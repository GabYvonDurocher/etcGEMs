"""M5b PART B: finalise the SYMMETRIC E. coli vs M. maripaludis cross-organism comparison
(both organisms sectored; same 4 named terms). Clean signed-contribution figure + final
table. Keeps the M5 originals; writes *_final.* .

  python strains/mmaripaludis/gen_cross_organism_final.py
"""
import json, os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

OUT = "outputs/ea_cross_organism"
POS, NEG, BASE, ORG = "#199e70", "#d85a30", "0.55", "k"


def signed_panel(ax, title, base, terms, org_E, obs_E):
    """terms: list of (label, value). Waterfall from the naive mean to the organism SS-E."""
    labels = ["naive enzyme-E mean"] + [t[0] for t in terms] + ["organism $E_a$ (SS-E)"]
    y = np.arange(len(labels))[::-1]
    run = base
    ax.barh(y[0], base, color=BASE, height=0.62, zorder=3)
    ax.text(base + 0.01, y[0], f"{base:.2f}", va="center", fontsize=8, color="0.3")
    for i, (lab, v) in enumerate(terms):
        left = run if v >= 0 else run + v
        ax.barh(y[i + 1], abs(v), left=left, color=(POS if v >= 0 else NEG), height=0.62, zorder=3)
        ax.text((run + max(v, 0)) + 0.01 if v >= 0 else (run + min(v, 0)) - 0.01, y[i + 1],
                f"{'+' if v >= 0 else '−'}{abs(v):.2f}", va="center",
                ha="left" if v >= 0 else "right", fontsize=8, color=(POS if v >= 0 else NEG), fontweight="bold")
        run += v
    ax.barh(y[-1], org_E, color=ORG, height=0.62, zorder=3)
    ax.text(org_E + 0.01, y[-1], f"{org_E:.2f}", va="center", fontsize=8, fontweight="bold")
    ax.axvline(obs_E, color="tab:blue", ls="--", lw=1.3, zorder=2)
    ax.text(obs_E, len(labels) - 0.4, f"observed {obs_E:.2f}", color="tab:blue", fontsize=7.5, ha="center")
    ax.set_yticks(y); ax.set_yticklabels(labels, fontsize=8.5)
    ax.set_xlim(0, 1.32); ax.set_xlabel("$E_a$ (eV)")
    ax.set_title(title, fontsize=10)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)


def main():
    ec = json.load(open("strains/eciML1515/outputs/ea_dissection_ss/decomposition_ss.json"))["BHI"]
    mm = json.load(open("strains/mmaripaludis/outputs/ea_dissection_ss/decomposition_ss.json"))
    comp = json.load(open(f"{OUT}/comparison.json"))
    ecn, mmn = ec["named_terms_eV"], mm["named_terms_eV"]
    ec_obs, mm_obs = comp["ecoli"]["obs_SS_E"], comp["methanogen"]["obs_SS_E"]

    fig, ax = plt.subplots(1, 2, figsize=(12.5, 3.9))
    signed_panel(ax[0], "E. coli (rich BHI) — broad control, allocation-buffered",
                 ec["unweighted_mean_kcat_E"],
                 [("control weighting", ecn["control_weighting"]),
                  ("allocation (growth law)", ecn["allocation"]),
                  ("maintenance", ecn["maintenance"]),
                  ("aggregation", ecn["aggregation"])], ec["Ea_org_SS_E"], ec_obs)
    signed_panel(ax[1], "M. maripaludis (H2/CO2) — backbone control, no allocation buffer",
                 mm["unweighted_mean_kcat_E"],
                 [("control weighting", mmn["control_weighting"]),
                  ("allocation (flat, Müller)", mmn["allocation"]),
                  ("maintenance", mmn["maintenance"]),
                  ("aggregation", mmn["aggregation"])], mm["Ea_org_SS_E"], mm_obs)
    fig.suptitle("Why methanogenesis $E_a$ > respiration: SS-E control-weighted decomposition "
                 "(both organisms sectored)", fontsize=11)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(f"{OUT}/cross_organism_decomposition_final.png", dpi=150); plt.close(fig)

    # final table
    rows = [
        ("organism SS-E $E_a$ (eV)", ec["Ea_org_SS_E"], mm["Ea_org_SS_E"]),
        ("observed SS-E (eV)", ec_obs, mm_obs),
        ("model − observed", round(ec["Ea_org_SS_E"] - ec_obs, 3), round(mm["Ea_org_SS_E"] - mm_obs, 3)),
        ("Topt (°C)", comp["ecoli"]["Topt_C"], comp["methanogen"]["Topt_C"]),
        ("CTmax (°C)", comp["ecoli"]["CTmax_C"], comp["methanogen"]["CTmax_C"]),
        ("naive (unweighted) enzyme-E mean", ec["unweighted_mean_kcat_E"], mm["unweighted_mean_kcat_E"]),
        ("+ control weighting", ecn["control_weighting"], mmn["control_weighting"]),
        ("+ allocation (measured; E. coli Scott / methanogen flat)", ecn["allocation"], mmn["allocation"]),
        ("+ maintenance NGAM(T)", ecn["maintenance"], mmn["maintenance"]),
        ("+ aggregation (heterogeneity/flattening)", ecn["aggregation"], mmn["aggregation"]),
        ("backbone fraction of control term", "n/a (broad)", comp["methanogen"]["backbone_fraction_of_control"]),
        ("sum C_i", ec["sum_C_i"], mm["sum_C_i"]),
    ]
    df = pd.DataFrame(rows, columns=["term", "E. coli (rich BHI)", "M. maripaludis (H2/CO2)"])
    df.to_csv(f"{OUT}/comparison_table_final.csv", index=False)
    print(df.to_string(index=False))
    print(f"\nwrote {OUT}/comparison_table_final.csv + cross_organism_decomposition_final.png")


if __name__ == "__main__":
    main()
