"""P4 PART A+B: dissect the calibrated, SECTORED Synechocystis 6803 SS-E (same method as
E. coli + methanogen), with the aggregation term computed DIRECTLY and named, the MEASURED
allocation (P3b) used, and the Calvin / carbon-fixation backbone attribution (test the
shallow-Calvin-kinetics hypothesis). Reuses ea_dissection + sharpe_schoolfield. Gurobi.

Nested switch-off decomposition (closes exactly to the sectored Ea_org):
  maintenance = Ea_org - SS(ngam off);  allocation = SS(ngam off) - SS(ngam off, growth-law off);
  aggregation = SS_backbone - cw;  control = cw - naive;
  Ea_org = naive + control + allocation + maintenance + aggregation.

  python strains/syn6803/run_p4_dissection.py
"""
import json, logging, os, sys, warnings
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
logging.getLogger("cobra").setLevel(logging.CRITICAL); warnings.filterwarnings("ignore")
import numpy as np, pandas as pd

# Calvin-Benson-Bassham / carbon-fixation backbone (reaction base -> label)
CALVIN = {
    "RBPC_1": "RuBisCO", "CBBM": "RuBisCO", "PRUK": "PRK", "PRUK_1": "PRK",
    "GAPD": "GAPDH", "GAP2": "GAPDH", "GAPDH": "GAPDH", "PGK": "PGK",
    "FBA": "FBA", "FBA3": "FBA", "TPI": "TPI", "FBP": "FBPase", "SBP": "SBPase",
    "SBP3": "SBPase", "TKT1": "TKT", "TKT2": "TKT", "TALA": "TAL", "RPE": "RPE", "RPI": "RPI",
}


def tuned_pert_syn6803(sectored=True):
    from src.etcgem import calibration_multi as C
    from src.etcgem.enzyme_cost import Perturbation
    specs = C.build_syn6803_specs()
    f = np.load("strains/syn6803/outputs/calibration_zavrel/chain_flat.npy")
    med = [np.median(f[:, j]) for j in range(len(specs))]
    nat = {s.name: (float(np.exp(med[j])) if s.space == "log" else float(med[j])) for j, s in enumerate(specs)}
    kw = {s.pert: nat[s.name] for s in specs if s.pert is not None}
    return kw, {k: round(v, 4) for k, v in nat.items()}


def main():
    import cobra; cobra.Configuration().solver = "gurobi"
    from src.etcgem import ea_dissection as EA, calibration_multi as C
    from src.etcgem.enzyme_cost import Perturbation
    OUT = "strains/syn6803/outputs/ea_dissection_ss"; os.makedirs(OUT, exist_ok=True)
    grid = np.linspace(5, 50, 46)
    kw, med = tuned_pert_syn6803()

    # sectored (growth law ON) provider + pert with the nominal sector split
    pm = C._build_pm_syn6803_sectored("syn6803"); s = pm.ec._sectors
    try: pm.ec.model.solver.configuration.timeout = 30
    except Exception: pass
    pert = Perturbation(**kw, f_metab=s["f_metab_nom"], f_maint=s["f_maint_nom"])

    SS_tuned, ssfit, _ = EA.ea_org_ss(pm, pert, grid)
    slope, window, _ = EA.ea_org(pm, pert, grid)
    T_ctrl = float(window[int(0.7 * (len(window) - 1))])
    print(f"[syn6803] sectored SS-E={SS_tuned:.4f} (slope {slope:.4f}); window {window[0]:.0f}-{window[-1]:.0f}C; C_i at {T_ctrl:.1f}C")

    ea_i = EA.enzyme_ea(pm, pert, window)
    ci = EA.control_coeffs(pm, pert, T_ctrl, progress=True)
    m = ci.merge(ea_i, on=["rxn_id", "enzyme_id"], how="left")
    m["contrib"] = m["C_i"] * m["Ea_kcat_eV"]

    sumC = float(m["C_i"].sum())
    cw = float((m["C_i"] * m["Ea_kcat_eV"]).sum()) / sumC
    cw_fN = float((m["C_i"] * m["Ea_fN_eV"]).sum()) / sumC
    unweighted = float(m["Ea_kcat_eV"].dropna().mean())
    mass = m["flux"].clip(lower=0)
    mass_mean = float(np.average(m["Ea_kcat_eV"].fillna(unweighted), weights=mass)) if mass.sum() > 0 else np.nan

    # --- nested switch-off (closes exactly): allocation outermost (ngam ON, matching P3b +
    # E. coli's method), then maintenance (growth law off), then aggregation directly. ---
    # growth-law OFF (slope 0) sectored model at the same pert
    cfg0 = dict(C.SYN6803_SECTOR_CFG); cfg0["growth_law_slope"] = 0.0; cfg0["growth_law_f_bio0"] = s["f_bio_nom"]
    pm0 = C._build_pm_syn6803_sectored("syn6803", cfg0)
    pert0 = Perturbation(**kw, f_metab=s["f_metab_nom"], f_maint=s["f_maint_nom"])
    SS_gloff_ngamon, _, _ = EA.ea_org_ss(pm0, pert0, grid)     # GL OFF, ngam ON
    pm0.ec.ngam_temperature = False
    SS_backbone, _, _ = EA.ea_org_ss(pm0, pert0, grid)         # GL OFF, ngam OFF -> kinetic backbone
    pm0.ec.ngam_temperature = True
    allocation = SS_tuned - SS_gloff_ngamon                    # growth-law buffer (ngam ON; ~ P3b -0.019)
    maintenance = SS_gloff_ngamon - SS_backbone               # maintenance (growth law off)
    aggregation = SS_backbone - cw                            # heterogeneity flattening (DIRECT)
    control = cw - unweighted
    SS_no_maint = SS_tuned - maintenance
    allocation_ngam_on = allocation
    closure = unweighted + control + allocation + maintenance + aggregation

    # --- Calvin / carbon-fixation backbone attribution ---
    import re
    def base_of(rid):
        b = re.sub(r"(_TG)?(_reverse)?$", "", rid)   # AUTOPACMEN arm-reaction suffixes
        return re.sub(r"(No\d+)?(_REV)?$", "", b)
    m["base"] = m["rxn_id"].map(base_of)
    m["calvin"] = m["base"].map(lambda b: CALVIN.get(b, ""))
    m = m.sort_values("contrib", key=lambda x: x.abs(), ascending=False)
    m.to_csv(f"{OUT}/ea_per_enzyme.csv", index=False)
    cb = m[m["calvin"] != ""]
    total_contrib = float(m["contrib"].sum()); cb_contrib = float(cb["contrib"].sum())

    dec = {
        "organism": "Synechocystis sp. PCC 6803",
        "operating_point": "calibrated (P3 medians) + SECTORED (P3b, Jahn 2018), light-saturated autotrophy",
        "tuned_medians": med, "Ea_org_SS_E": round(SS_tuned, 4), "SS_fit_r2": round(ssfit.r2, 4),
        "SS_Eh_eV": round(ssfit.E_h, 3), "SS_Th_C": round(ssfit.T_h_C, 2),
        "windowed_slope_crosscheck": round(slope, 4), "window_C": [float(window[0]), float(window[-1])],
        "T_control_C": round(T_ctrl, 2), "sum_C_i": round(sumC, 3), "n_flux_enzymes": int(len(m)),
        "unweighted_mean_kcat_E": round(unweighted, 4), "mass_weighted_mean_kcat_E": round(mass_mean, 4),
        "control_weighted_mean_kcat_E": round(cw, 4), "  fN_contribution": round(cw_fN, 4),
        "SS_kinetic_backbone": round(SS_backbone, 4), "SS_no_maint": round(SS_no_maint, 4),
        "named_terms_eV": {"control_weighting": round(control, 4), "allocation": round(allocation, 4),
                           "maintenance": round(maintenance, 4), "aggregation": round(aggregation, 4)},
        "closure_check": round(closure, 4),
        "allocation_note": (f"MEASURED {allocation:+.4f} on the sectored model (Jahn 2018 shallow RIB "
                            f"growth law; ngam-off isolation); P3b ngam-on cross-check {allocation_ngam_on:+.4f}. "
                            f"Small, between E. coli's -0.130 (Scott) and the methanogen's 0.000 (Muller-flat)."),
        "calvin_backbone_attribution": {
            "calvin_contrib_sum": round(cb_contrib, 4), "total_contrib_sum": round(total_contrib, 4),
            "calvin_fraction_of_control": round(cb_contrib / total_contrib, 3) if total_contrib else None,
            "proteome_mean_kcat_E": round(unweighted, 4),
            "calvin_enzymes": [{"label": r["calvin"], "rxn": r["base"], "C_i": round(r["C_i"], 4),
                                "Ea_kcat_E": round(r["Ea_kcat_eV"], 4), "contrib": round(r["contrib"], 4),
                                "E_vs_proteome_mean": round(r["Ea_kcat_eV"] - unweighted, 4)}
                               for _, r in cb.sort_values("contrib", ascending=False).iterrows()],
        },
        "top_contributors": [{"rxn": r["base"], "calvin": r["calvin"], "C_i": round(r["C_i"], 4),
                              "Ea_kcat_E": round(r["Ea_kcat_eV"], 4), "contrib": round(r["contrib"], 4)}
                             for _, r in m.head(15).iterrows()],
        # split of the low Ea: (i) low controlling-enzyme E (control term), (ii) globally shallow
        # naive mean vs the ~0.65 benchmark, (iii) aggregation
        "low_Ea_split": {"naive_mean_vs_0.65": round(unweighted - 0.65, 4),
                         "control_weighting": round(control, 4), "aggregation": round(aggregation, 4)},
    }
    json.dump(dec, open(f"{OUT}/decomposition_ss.json", "w"), indent=2, default=str)
    print(f"[syn6803] naive {unweighted:.3f} + control {control:+.3f} + alloc {allocation:+.3f} "
          f"+ maint {maintenance:+.3f} + aggregation {aggregation:+.3f} = {closure:.3f} (SS-E {SS_tuned:.3f})")
    print(f"[syn6803] Calvin backbone carries {cb_contrib/total_contrib*100:.0f}% of control; "
          f"Calvin mean E {cb['Ea_kcat_eV'].mean():.3f} vs proteome mean {unweighted:.3f} "
          f"({'LOW-E' if cb['Ea_kcat_eV'].mean()<unweighted else 'high-E'} backbone)")
    print(f"  top: {[(r['base'], r['calvin'], round(r['contrib'],3)) for _,r in m.head(8).iterrows()]}")
    print("wrote", f"{OUT}/decomposition_ss.json + ea_per_enzyme.csv")


if __name__ == "__main__":
    main()
