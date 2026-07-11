"""Generate the SS-E report assets (figures + summary.json + no-carrier tables + SS
robustness) into strains/eciML1515/outputs/ea_dissection_ss/, reusing the ea_dissection
plot helpers. Reuses saved per-enzyme C_i / Ea_kcat; rebuilds only the BHI tuned provider
for the SS robustness sweep.

  python strains/eciML1515/gen_ea_ss_assets.py
"""
import json, logging, os, sys, warnings
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
logging.getLogger("cobra").setLevel(logging.CRITICAL); warnings.filterwarnings("ignore")
import numpy as np, pandas as pd

ACP = "P0A6A8"   # acyl-carrier protein hub (excluded in the 'no_carrier' robust attribution)


def main():
    import cobra; cobra.Configuration().solver = "gurobi"
    from src.etcgem import ea_dissection as EA
    OUT = "strains/eciML1515/outputs/ea_dissection_ss"
    SLOPE = "strains/eciML1515/outputs/ea_dissection"
    os.makedirs(OUT, exist_ok=True)
    D = json.load(open(f"{OUT}/decomposition_ss.json"))
    b = D["BHI"]

    # per-enzyme frames with SS contribution (C_i * Ea_kcat); no-carrier = acpP excluded
    frames = {}
    for med, csv in [("BHI", "ea_per_enzyme_BHI.csv"), ("glucose", "ea_per_enzyme_glucose.csv")]:
        df = pd.read_csv(f"{SLOPE}/{csv}")
        df["contrib"] = df["C_i"] * df["Ea_kcat_eV"]   # SS backbone uses kcat-only E_i
        frames[med] = df
        nc = df[df["enzyme_id"] != ACP]
        nc.groupby(["cog", "cog_category"])["contrib"].sum().sort_values(ascending=False)\
          .to_csv(f"{OUT}/ea_by_cog_{med}_no_carrier.csv")
        df.sort_values("contrib", key=lambda s: s.abs(), ascending=False)\
          .to_csv(f"{OUT}/ea_per_enzyme_{med}.csv", index=False)
    mB, mG = frames["BHI"], frames["glucose"]
    mB_nc = mB[mB["enzyme_id"] != ACP]

    # mass-weighted mean (SS/kcat basis) for the departure panel
    mass = mB["flux"].clip(lower=0)
    mass_mean = float(np.average(mB["Ea_kcat_eV"], weights=mass)) if mass.sum() > 0 else np.nan

    # SS-compatible summary.json (headline_BHI structure the report's Table code reads)
    base = b["unweighted_mean_kcat_E"]; cw = b["control_weighted_mean_kcat_E"]
    dep = {"unweighted_mean_Ea_i": base, "mass_weighted_mean_Ea_i": round(mass_mean, 4),
           "control_weighted_mean_Ea_i": cw,
           "attribution": {"control_concentration": round(cw - base, 4),
                           "allocation": b["allocation_growth_law_SS"], "maintenance": b["maintenance_NGAM_SS"]}}
    decomp = {"kinetic_control_weighted_mean_Ea_i": cw,
              "allocation_growth_law": b["allocation_growth_law_SS"],
              "maintenance_NGAM": b["maintenance_NGAM_SS"],
              "residual_nonlinear": b["residual_nonlinear_SS"], "actual_Ea_org": b["Ea_org_SS_E"]}
    headline = {"Ea_org_eV": b["Ea_org_SS_E"], "medium": "BHI", "sum_C_i": b["sum_C_i"],
                "decomposition_eV": decomp, "departure_from_naive_mean_eV": dep,
                "convention": "Sharpe-Schoolfield E (window-independent)"}

    # SS robustness: homogenise / spread sweep on SS-E (rebuild BHI tuned pm)
    pert, _ = EA.tuned_pert()
    pm, _ = EA.build_pm("eciML1515", "BHI", growth_law=True, close_o2=True)
    grid = np.linspace(5, 52, 48)
    ec = pm.ec; Topt0, uCpt0 = ec._Topt.copy(), ec._uCpt.copy()
    tm, cm = float(Topt0.mean()), float(uCpt0.mean())
    def ss_with(Topt, uCpt):
        s = (ec._Topt.copy(), ec._uCpt.copy()); ec._Topt, ec._uCpt = Topt, uCpt
        try: E, _, _ = EA.ea_org_ss(pm, pert, grid)
        finally: ec._Topt, ec._uCpt = s
        return round(float(E), 4)
    rob = {"homogenised_Ea_org": ss_with(np.full_like(Topt0, tm), np.full_like(uCpt0, cm)),
           "spread_sweep": {f"spread_x{s}": ss_with(tm + s*(Topt0-tm), cm + s*(uCpt0-cm))
                            for s in (0.0, 0.5, 0.75, 1.0, 1.25)},
           "note": "SS-E; spread_x1.0 = actual heterogeneity; x0.0 = homogenised"}

    summary = {"headline_BHI": headline,
               "medium_comparison": {"Ea_org_BHI": b["Ea_org_SS_E"],
                                     "Ea_org_glucose": D["glucose_minimal"]["Ea_org_SS_E"]},
               "robustness_BHI": rob,
               "emergent_vs_tuned": {"Ea_org_emergent": D["emergent_BHI_SS_E"]},
               "observed_VdL_SS_E": D["observed_VdL_SS_E"],
               "convention": D["meta"]["convention"]}
    json.dump(summary, open(f"{OUT}/summary.json", "w"), indent=2, default=str)

    # figures (standard names in the _ss dir)
    dec_fig = {"Ea_org_eV": b["Ea_org_SS_E"], "medium": "BHI",
               "decomposition_eV": decomp, "departure_from_naive_mean_eV": dep}
    EA.plot_ea_signed_contributions(dec_fig, f"{OUT}/ea_signed_contributions.png")
    EA._plot_departure(dep, OUT)                       # -> ea_departure.png
    mB_nc2 = mB_nc.copy(); EA._plot_top_enzymes(mB_nc2, OUT)   # -> ea_top_enzymes.png (acpP-excluded)
    os.replace(f"{OUT}/ea_top_enzymes.png", f"{OUT}/ea_top_enzymes_no_carrier.png")
    EA._plot_by_cog(mB_nc2, OUT)                        # -> ea_by_cog.png
    EA._plot_robustness(rob, OUT)                       # -> ea_robustness.png

    print(f"SS-E assets -> {OUT}")
    print(f"  Ea_org(SS)={b['Ea_org_SS_E']} base={base} cw={cw} mass={mass_mean:.3f} "
          f"alloc={decomp['allocation_growth_law']} maint={decomp['maintenance_NGAM']} "
          f"resid={decomp['residual_nonlinear']}")
    print(f"  robustness SS spread_sweep: {rob['spread_sweep']}")
    lip = mB_nc.groupby('cog_category')['contrib'].sum()
    print(f"  no-carrier by-cog: lipid={lip.get('lipid metab',0):.3f} glyco={lip.get('carbohydrate/glycolysis',0):.3f}")


if __name__ == "__main__":
    main()
