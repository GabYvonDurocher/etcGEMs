"""M5 PART C: Mcr-kcat sensitivity sweep. Repeats the methanogen SS-E + control attribution
across the Mcr kcat uncertainty range (3-294/s; M2b), to test whether the
methanogen>>E.coli ordering and the backbone-control finding are robust or hinge on Mcr.

  python strains/mmaripaludis/run_mcr_sweep_m5.py
"""
import json, logging, os, sys, warnings
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
logging.getLogger("cobra").setLevel(logging.CRITICAL); warnings.filterwarnings("ignore")
import numpy as np, pandas as pd


def main():
    import cobra; cobra.Configuration().solver = "gurobi"
    from src.etcgem import ea_dissection as EA
    from src.etcgem.config import resolve, build_provider
    from run_ea_dissection_m5 import tuned_pert_methanogen, BACKBONE
    import importlib.util
    # import helper from the sibling script
    spec = importlib.util.spec_from_file_location("m5", os.path.join(os.path.dirname(__file__), "run_ea_dissection_m5.py"))
    m5 = importlib.util.module_from_spec(spec); spec.loader.exec_module(m5)

    OUT = "strains/mmaripaludis/outputs/ea_dissection_ss"
    grid = np.linspace(5, 55, 51)
    pert, _ = m5.tuned_pert_methanogen()
    MCR_BASE = "rxn03127"
    MCR_KCATS = [3.0, 10.0, 30.0, 58.9, 100.0, 294.0]   # M2b range (58.9 = the pinned value)

    pm = build_provider(resolve("mmaripaludis"))
    try: pm.ec.model.solver.configuration.timeout = 30
    except Exception: pass
    ec = pm.ec
    # locate the Mcr entry + its MW (base_cost = MW/(kcat*3600))
    mcr = next(e for e in ec.table.entries if e.rxn_id.startswith(MCR_BASE))
    mw = mcr.mw

    rows = []
    for kc in MCR_KCATS:
        mcr.kcat_ref = kc; mcr.base_cost = mw / (kc * 3600.0)
        ec.refresh_params()
        SS, ssfit, _ = EA.ea_org_ss(pm, pert, grid)
        slope, window, _ = EA.ea_org(pm, pert, grid)
        T_ctrl = float(window[int(0.7 * (len(window) - 1))])
        ci = EA.control_coeffs(pm, pert, T_ctrl, progress=False)
        ea_i = EA.enzyme_ea(pm, pert, window)
        m = ci.merge(ea_i, on=["rxn_id", "enzyme_id"], how="left")
        m["contrib"] = m["C_i"] * m["Ea_kcat_eV"]
        m["base"] = m["rxn_id"].str.replace(r"_LSQBKT.*$", "", regex=True)
        m["backbone"] = m["base"].map(lambda b: BACKBONE.get(b, ""))
        tot = float(m["contrib"].sum()); bb = float(m[m["backbone"] != ""]["contrib"].sum())
        top = m.reindex(m["contrib"].abs().sort_values(ascending=False).index).head(3)
        mcr_row = m[m["base"] == MCR_BASE]
        rows.append({"Mcr_kcat": kc, "SS_E": round(SS, 4), "slope": round(slope, 4),
                     "backbone_frac_of_control": round(bb / tot, 3) if tot else None,
                     "top3": ";".join(f"{r['backbone'] or r['base']}({r['contrib']:.3f})" for _, r in top.iterrows()),
                     "Mcr_C_i": round(float(mcr_row["C_i"].iloc[0]), 4) if len(mcr_row) else None,
                     "Mcr_contrib": round(float(mcr_row["contrib"].iloc[0]), 4) if len(mcr_row) else None})
        print(f"  Mcr={kc:6.1f}/s  SS-E={SS:.3f}  backbone={bb/tot*100:4.0f}%  top: {rows[-1]['top3']}")

    df = pd.DataFrame(rows); df.to_csv(f"{OUT}/mcr_sweep.csv", index=False)
    ss = df["SS_E"].values
    verdict = {"mcr_kcat_range": [MCR_KCATS[0], MCR_KCATS[-1]], "SS_E_range": [float(ss.min()), float(ss.max())],
               "SS_E_min_vs_ecoli_0.68": "methanogen SS-E stays above E. coli 0.68 across the whole Mcr range"
                                          if ss.min() > 0.68 else "SS-E DIPS to/below E. coli at some Mcr value",
               "backbone_frac_range": [float(df["backbone_frac_of_control"].min()), float(df["backbone_frac_of_control"].max())]}
    json.dump({"sweep": rows, "verdict": verdict}, open(f"{OUT}/mcr_sweep.json", "w"), indent=2)
    print(f"\nSS-E across Mcr 3-294/s: {ss.min():.3f}-{ss.max():.3f} (E. coli 0.68). "
          f"backbone {df['backbone_frac_of_control'].min()*100:.0f}-{df['backbone_frac_of_control'].max()*100:.0f}% of control.")
    print("wrote", f"{OUT}/mcr_sweep.csv + mcr_sweep.json")


if __name__ == "__main__":
    main()
