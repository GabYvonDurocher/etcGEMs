"""M5 PART D: E. coli vs M. maripaludis cross-organism SS-E comparison. Reads both
decomposition_ss.json + the Mcr sweep + observed SS-E, builds the side-by-side decomposition
table + comparison figure into outputs/ea_cross_organism/.

  python strains/mmaripaludis/gen_cross_organism_m5.py
"""
import json, logging, os, sys, warnings
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
logging.getLogger("cobra").setLevel(logging.CRITICAL); warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt


def main():
    from src.etcgem.tpc import TPC
    from src.etcgem.sharpe_schoolfield import fit_sharpe_schoolfield
    OUT = "outputs/ea_cross_organism"; os.makedirs(OUT, exist_ok=True)

    ec = json.load(open("strains/eciML1515/outputs/ea_dissection_ss/decomposition_ss.json"))["BHI"]
    mm = json.load(open("strains/mmaripaludis/outputs/ea_dissection_ss/decomposition_ss.json"))
    ze = np.load("strains/eciML1515/outputs/calibration_vanderlinden/posterior_predictive.npz")
    zm = np.load("strains/mmaripaludis/outputs/calibration_jones/posterior_predictive.npz")

    # descriptors (Topt, CTmax) + observed SS-E from the posterior-predictive curves
    def desc(z):
        d = TPC(z["temps_C"], z["med"]).descriptors(0.05)
        obs = fit_sharpe_schoolfield(z["obs_T"], z["obs"], T_ref_C=20.0)
        return round(d.Topt_C, 1), round(d.CTmax_C, 1), round(obs.E, 3)
    ec_topt, ec_ctmax, ec_obsE = desc(ze)
    mm_topt, mm_ctmax, mm_obsE = desc(zm)

    ecn = ec["named_terms_eV"]; mmn = mm["named_terms_eV"]
    rows = [
        ("SS-E organism Ea (eV)", ec["Ea_org_SS_E"], mm["Ea_org_SS_E"]),
        ("observed SS-E (eV)", ec_obsE, mm_obsE),
        ("Topt (C)", ec_topt, mm_topt),
        ("CTmax (C)", ec_ctmax, mm_ctmax),
        ("— naive (unweighted) enzyme-E mean", ec["unweighted_mean_kcat_E"], mm["unweighted_mean_kcat_E"]),
        ("+ control weighting", ecn["control_weighting"], mmn["control_weighting"]),
        ("+ allocation (growth law)", ecn["allocation"], mmn["allocation"]),
        ("+ maintenance NGAM(T)", ecn["maintenance"], mmn["maintenance"]),
        ("+ aggregation (heterogeneity/flattening)", ecn["aggregation"], mmn["aggregation"]),
        ("control-weighted enzyme-E mean", ec["control_weighted_mean_kcat_E"], mm["control_weighted_mean_kcat_E"]),
        ("sum C_i", ec["sum_C_i"], mm["sum_C_i"]),
    ]
    df = pd.DataFrame(rows, columns=["term", "E. coli (rich BHI)", "M. maripaludis (H2/CO2)"])
    df["difference (methanogen - E. coli)"] = [
        (round(m - e, 4) if isinstance(e, (int, float)) and isinstance(m, (int, float)) else "")
        for _, e, m in rows]
    df.to_csv(f"{OUT}/comparison_table.csv", index=False)
    print(df.to_string(index=False))

    # figure: side-by-side signed decomposition (from the naive mean to the organism SS-E)
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.6))
    for a, (org, dd, dn, col) in zip(ax, [("E. coli (0.68)", ec, ecn, "#2c7fb8"),
                                          ("M. maripaludis (1.06)", mm, mmn, "#199e70")]):
        base = dd["unweighted_mean_kcat_E"]
        comps = [("control", dn["control_weighting"]), ("allocation", dn["allocation"]),
                 ("maintenance", dn["maintenance"]), ("aggregation", dn["aggregation"])]
        labels = ["naive mean"] + [c[0] for c in comps] + ["organism Ea"]
        run = base; xs = [base]
        for _, v in comps:
            run += v; xs.append(run)
        y = np.arange(len(labels))[::-1]
        vals = [base] + [c[1] for c in comps] + [dd["Ea_org_SS_E"]]
        colors = ["0.5"] + ["#199e70" if c[1] >= 0 else "#d85a30" for c in comps] + ["k"]
        a.barh(y[1:-1], [c[1] for c in comps], left=[xs[i] - (comps[i][1] if comps[i][1] < 0 else 0) for i in range(4)],
               color=colors[1:-1], height=0.6, zorder=3)
        a.barh([y[0]], [base], color="0.5", height=0.6)
        a.barh([y[-1]], [dd["Ea_org_SS_E"]], color="k", height=0.6)
        for yi, lab, v in zip(y, labels, vals):
            a.text(0.02, yi, f"{lab}", va="center", fontsize=8)
        a.set_yticks([]); a.axvline(0, color="k", lw=0.6)
        a.set_xlim(0, 1.25); a.set_xlabel("E_a (eV)"); a.set_title(f"{org}: SS-E decomposition", fontsize=10)
    plt.tight_layout(); plt.savefig(f"{OUT}/cross_organism_decomposition.png", dpi=140); plt.close()
    print(f"\nwrote {OUT}/comparison_table.csv + cross_organism_decomposition.png")

    # bundle a machine-readable comparison
    json.dump({"ecoli": {"SS_E": ec["Ea_org_SS_E"], "obs_SS_E": ec_obsE, "Topt_C": ec_topt, "CTmax_C": ec_ctmax,
                         "named_terms": ecn, "unweighted": ec["unweighted_mean_kcat_E"], "sum_C_i": ec["sum_C_i"]},
               "methanogen": {"SS_E": mm["Ea_org_SS_E"], "obs_SS_E": mm_obsE, "Topt_C": mm_topt, "CTmax_C": mm_ctmax,
                              "named_terms": mmn, "unweighted": mm["unweighted_mean_kcat_E"], "sum_C_i": mm["sum_C_i"],
                              "backbone_fraction_of_control": mm["backbone_attribution"]["backbone_fraction_of_control_term"]}},
              open(f"{OUT}/comparison.json", "w"), indent=2, default=str)


if __name__ == "__main__":
    main()
