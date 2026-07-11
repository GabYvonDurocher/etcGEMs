"""M5 PART A+B: dissect the calibrated M. maripaludis SS-E (same method as E. coli), with the
aggregation term computed DIRECTLY and named, and the methanogenesis-backbone attribution.
Single sMOMENT pool (allocation ~ 0, grounded in slow growth). Reuses ea_dissection +
sharpe_schoolfield. The methanogen model is small, so the per-enzyme control coefficients are
minutes, not hours.

  python strains/mmaripaludis/run_ea_dissection_m5.py
"""
import json, logging, os, sys, warnings
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
logging.getLogger("cobra").setLevel(logging.CRITICAL); warnings.filterwarnings("ignore")
import numpy as np, pandas as pd

BACKBONE = {  # methanogenesis / energy backbone reaction bases -> label
    "rxn03127": "Mcr", "rxn03020": "Mtr", "rxn11938": "Fwd", "rxn02431": "Ftr",
    "rxn02480": "Mch", "rxn06696": "Hmd", "rxn03085": "Mer", "rxn06299": "Frh/Vhu",
    "HdrABC": "Hdr", "Fdh": "Fdh", "ATPS": "ATPsyn",
}


def tuned_pert_methanogen():
    from src.etcgem.calibration_multi import build_methanogen_specs, to_natural
    from src.etcgem.enzyme_cost import Perturbation
    f = np.load("strains/mmaripaludis/outputs/calibration_jones/chain_flat.npy")
    specs = build_methanogen_specs()
    nat = to_natural([np.median(f[:, j]) for j in range(len(specs))], specs)
    kw = {s.pert: nat[s.name] for s in specs if s.pert is not None}
    return Perturbation(**kw), {k: round(v, 4) for k, v in nat.items()}


def main():
    import cobra; cobra.Configuration().solver = "gurobi"
    from src.etcgem import ea_dissection as EA
    from src.etcgem.config import resolve, build_provider

    OUT = "strains/mmaripaludis/outputs/ea_dissection_ss"; os.makedirs(OUT, exist_ok=True)
    grid = np.linspace(5, 55, 51)
    pert, med = tuned_pert_methanogen()
    pm = build_provider(resolve("mmaripaludis"))
    try: pm.ec.model.solver.configuration.timeout = 30
    except Exception: pass

    # organism Ea = SS-E; the rising-limb window (for the per-enzyme kcat Arrhenius E_i)
    SS_tuned, ssfit, _ = EA.ea_org_ss(pm, pert, grid)
    slope, window, _ = EA.ea_org(pm, pert, grid)
    T_ctrl = float(window[int(0.7 * (len(window) - 1))])
    print(f"[methanogen] SS-E={SS_tuned:.4f} (slope {slope:.4f}); window {window[0]:.0f}-{window[-1]:.0f}C; C_i at {T_ctrl:.1f}C")

    ea_i = EA.enzyme_ea(pm, pert, window)                 # Ea_kcat_eV (rising-limb kcat E), Ea_fN_eV
    ci = EA.control_coeffs(pm, pert, T_ctrl, progress=True)
    m = ci.merge(ea_i, on=["rxn_id", "enzyme_id"], how="left")
    m["contrib"] = m["C_i"] * m["Ea_kcat_eV"]

    sumC = float(m["C_i"].sum())
    cw = float((m["C_i"] * m["Ea_kcat_eV"]).sum()) / sumC
    cw_fN = float((m["C_i"] * m["Ea_fN_eV"]).sum()) / sumC
    unweighted = float(m["Ea_kcat_eV"].dropna().mean())
    mass = m["flux"].clip(lower=0)
    mass_mean = float(np.average(m["Ea_kcat_eV"].fillna(unweighted), weights=mass)) if mass.sum() > 0 else np.nan

    # named terms (single pool: allocation = 0). maintenance = SS_tuned - SS(ngam flat);
    # kinetic backbone = SS(ngam flat) -> aggregation = SS_backbone - cw (heterogeneity flattening).
    ec = pm.ec; saved = ec.ngam_temperature
    ec.ngam_temperature = False
    SS_backbone, _, _ = EA.ea_org_ss(pm, pert, grid)     # no maintenance, no allocation (single pool)
    ec.ngam_temperature = saved
    maintenance = SS_tuned - SS_backbone
    aggregation = SS_backbone - cw
    allocation = 0.0
    control = cw - unweighted
    closure = unweighted + control + allocation + maintenance + aggregation

    dec = {"organism": "M. maripaludis", "operating_point": "calibrated (M4 medians), H2/CO2, single sMOMENT pool, no growth law",
           "tuned_medians": med, "Ea_org_SS_E": round(SS_tuned, 4), "SS_fit_r2": round(ssfit.r2, 4),
           "SS_Eh_eV": round(ssfit.E_h, 3), "SS_Th_C": round(ssfit.T_h_C, 2),
           "windowed_slope_crosscheck": round(slope, 4), "window_C": [float(window[0]), float(window[-1])],
           "T_control_C": round(T_ctrl, 2), "sum_C_i": round(sumC, 3), "n_flux_enzymes": int(len(m)),
           "unweighted_mean_kcat_E": round(unweighted, 4), "mass_weighted_mean_kcat_E": round(mass_mean, 4),
           "control_weighted_mean_kcat_E": round(cw, 4), "  fN_contribution": round(cw_fN, 4),
           "SS_kinetic_backbone": round(SS_backbone, 4),
           "named_terms_eV": {"control_weighting": round(control, 4), "allocation": round(allocation, 4),
                              "maintenance": round(maintenance, 4), "aggregation": round(aggregation, 4)},
           "closure_check": round(closure, 4),
           "allocation_note": "0 by the single sMOMENT pool (no growth law / sectors). Grounded in slow "
                              "growth (~10x slower than E. coli): the Scott growth-law buffer is weak; a "
                              "sector layer would make the comparison exactly symmetric (deferred)."}

    # backbone attribution
    def base_of(rid):
        import re; return re.sub(r"_LSQBKT.*$", "", rid)
    m["base"] = m["rxn_id"].map(base_of)
    m["backbone"] = m["base"].map(lambda b: BACKBONE.get(b, ""))
    m.sort_values("contrib", key=lambda s: s.abs(), ascending=False).to_csv(f"{OUT}/ea_per_enzyme.csv", index=False)
    bb = m[m["backbone"] != ""]
    total_contrib = float(m["contrib"].sum())
    bb_contrib = float(bb["contrib"].sum())
    proteome_mean_E = unweighted
    dec["backbone_attribution"] = {
        "backbone_contrib_sum": round(bb_contrib, 4), "total_contrib_sum": round(total_contrib, 4),
        "backbone_fraction_of_control_term": round(bb_contrib / total_contrib, 3) if total_contrib else None,
        "backbone_enzymes": [{"label": r["backbone"], "gene_rxn": r["base"], "C_i": round(r["C_i"], 4),
                              "Ea_kcat_E": round(r["Ea_kcat_eV"], 4), "contrib": round(r["contrib"], 4),
                              "E_above_proteome_mean": round(r["Ea_kcat_eV"] - proteome_mean_E, 4)}
                             for _, r in bb.sort_values("contrib", ascending=False).iterrows()],
        "proteome_mean_kcat_E": round(proteome_mean_E, 4)}
    top = m.reindex(m["contrib"].abs().sort_values(ascending=False).index).head(12)
    dec["top_contributors"] = [{"rxn": r["base"], "backbone": r["backbone"], "C_i": round(r["C_i"], 4),
                                "Ea_kcat_E": round(r["Ea_kcat_eV"], 4), "contrib": round(r["contrib"], 4)}
                               for _, r in top.iterrows()]

    json.dump(dec, open(f"{OUT}/decomposition_ss.json", "w"), indent=2, default=str)
    print(f"[methanogen] unweighted {unweighted:.3f} + control {control:+.3f} + alloc {allocation:+.3f} "
          f"+ maint {maintenance:+.3f} + aggregation {aggregation:+.3f} = {closure:.3f} (SS-E {SS_tuned:.3f})")
    print(f"[methanogen] backbone carries {bb_contrib/total_contrib*100:.0f}% of the control term; "
          f"backbone E {bb['Ea_kcat_eV'].mean():.3f} vs proteome mean {proteome_mean_E:.3f}")
    print(f"  top: {[(r['base'], r['backbone'], round(r['contrib'],3)) for _,r in top.head(6).iterrows()]}")
    print("wrote", f"{OUT}/decomposition_ss.json + ea_per_enzyme.csv")


if __name__ == "__main__":
    main()
