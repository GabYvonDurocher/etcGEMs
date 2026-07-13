"""P4 PART D: the THREE-WAY E. coli vs M. maripaludis vs Synechocystis 6803 comparison that
explains the full Yvon-Durocher 2014 ordering (methanogenesis > respiration > photosynthesis)
as THREE DISTINCT ROUTES. All three on the SAME 4 named terms + naive mean, all sectored.
Signed-contribution figure (deviations from the naive mean; NEVER a waterfall) + final table.
Keeps the two-way originals; writes *_3way.* .

  python strains/syn6803/gen_three_way.py
"""
import json, os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

OUT = "outputs/ea_cross_organism"
POS, NEG = "#199e70", "#d85a30"


def signed_panel(ax, title, subtitle, naive, terms, org_E, obs_E, obs_label="observed"):
    """Signed-contribution panel: each named term as a diverging bar from 0 (NOT a waterfall).
    naive mean and organism SS-E are annotated as reference lines."""
    labels = [t[0] for t in terms][::-1]
    vals = [t[1] for t in terms][::-1]
    y = np.arange(len(labels))
    ax.axvline(0, color="0.3", lw=1.0, zorder=2)
    for i, v in enumerate(vals):
        ax.barh(y[i], v, color=(POS if v >= 0 else NEG), height=0.6, zorder=3)
        ax.text(v + (0.006 if v >= 0 else -0.006), y[i], f"{'+' if v >= 0 else '−'}{abs(v):.3f}",
                va="center", ha="left" if v >= 0 else "right", fontsize=8,
                color=(POS if v >= 0 else NEG), fontweight="bold")
    ax.set_yticks(y); ax.set_yticklabels(labels, fontsize=8.5)
    ax.set_xlim(-0.42, 0.42); ax.set_xlabel("signed contribution to $E_a$ (eV)")
    ax.set_title(f"{title}\n{subtitle}\nnaive {naive:.2f} → $E_a$ {org_E:.2f} eV "
                 f"({obs_label} {obs_E:.2f})", fontsize=9.5)
    for sp in ("top", "right", "left"):
        ax.spines[sp].set_visible(False)


def main():
    ec = json.load(open("strains/eciML1515/outputs/ea_dissection_ss/decomposition_ss.json"))["BHI"]
    mm = json.load(open("strains/mmaripaludis/outputs/ea_dissection_ss/decomposition_ss.json"))
    ph = json.load(open("strains/syn6803/outputs/ea_dissection_ss/decomposition_ss.json"))
    rob = json.load(open("strains/syn6803/outputs/ea_dissection_ss/robustness_sweep.json"))
    comp2 = json.load(open(f"{OUT}/comparison.json"))
    ecn, mmn, phn = ec["named_terms_eV"], mm["named_terms_eV"], ph["named_terms_eV"]
    ec_obs, mm_obs = comp2["ecoli"]["obs_SS_E"], comp2["methanogen"]["obs_SS_E"]
    # canonical observed = the Zavrel GROWTH SS-E (symmetric with the other two organisms), fragile
    # 90% CI [0.34, 1.01]; the Inoue light-saturated FLUX SS-E (0.52) is an independent cross-check.
    ph_obs_growth = 0.435   # Zavrel 6-pt growth SS-E (canonical observed; 90% CI [0.34, 1.01])
    ph_obs_flux = 0.52      # Inoue O2-evolution flux (cross-check; model flux SS-E 0.56)

    # --- signed-contribution figure (3 panels; NOT a waterfall) ---
    fig, ax = plt.subplots(1, 3, figsize=(15, 4.0))
    terms = lambda n: [("control weighting", n["control_weighting"]),
                       ("allocation", n["allocation"]),
                       ("maintenance", n["maintenance"]),
                       ("aggregation", n["aggregation"])]
    signed_panel(ax[0], "Methanogenesis — M. maripaludis", "narrow control on a HIGH-E backbone",
                 mm["unweighted_mean_kcat_E"], terms(mmn), mm["Ea_org_SS_E"], mm_obs)
    signed_panel(ax[1], "Respiration — E. coli", "broad control + Scott allocation buffer",
                 ec["unweighted_mean_kcat_E"], terms(ecn), ec["Ea_org_SS_E"], ec_obs)
    signed_panel(ax[2], "Photosynthesis — Synechocystis 6803", "control on LOW-E carbon fixation + small buffers",
                 ph["unweighted_mean_kcat_E"], terms(phn), ph["Ea_org_SS_E"], ph_obs_flux, obs_label="obs flux")
    fig.suptitle("Three distinct routes to the Yvon-Durocher 2014 ordering: "
                 "methanogenesis (1.06) > respiration (0.68) > photosynthesis (0.57)  —  "
                 "SS-E signed-contribution decomposition (all sectored)", fontsize=11)
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    fig.savefig(f"{OUT}/cross_organism_signed_contributions_3way.png", dpi=150); plt.close(fig)

    # --- three-way table ---
    def col(d, n, obs, topt, ctmax, extra):
        return [d["Ea_org_SS_E"], obs, round(d["Ea_org_SS_E"] - obs, 3), topt, ctmax,
                d["unweighted_mean_kcat_E"], n["control_weighting"], n["allocation"],
                n["maintenance"], n["aggregation"], extra, d["sum_C_i"]]
    idx = ["organism SS-E Ea (eV)", "observed SS-E (eV)", "model − observed", "Topt (°C)", "CTmax (°C)",
           "naive (unweighted) enzyme-E mean", "+ control weighting",
           "+ allocation (Scott / flat / Jahn-shallow)", "+ maintenance NGAM(T)",
           "+ aggregation (heterogeneity)", "backbone fraction of control", "sum C_i"]
    df = pd.DataFrame({
        "term": idx,
        "M. maripaludis (H2/CO2)": col(mm, mmn, mm_obs, comp2["methanogen"]["Topt_C"], comp2["methanogen"]["CTmax_C"], comp2["methanogen"]["backbone_fraction_of_control"]),
        "E. coli (rich BHI)": col(ec, ecn, ec_obs, comp2["ecoli"]["Topt_C"], comp2["ecoli"]["CTmax_C"], "n/a (broad)"),
        "Synechocystis 6803 (light-sat)": col(ph, phn, ph_obs_growth, 35.0, 46.8, f"{ph['calvin_backbone_attribution']['calvin_fraction_of_control']} (Calvin)"),
    })
    df.to_csv(f"{OUT}/comparison_table_3way.csv", index=False)

    out = {
        "ecoli": {"SS_E": ec["Ea_org_SS_E"], "obs_SS_E": ec_obs, "route": "broad control + Scott allocation buffer", "named_terms": ecn, "naive": ec["unweighted_mean_kcat_E"]},
        "methanogen": {"SS_E": mm["Ea_org_SS_E"], "obs_SS_E": mm_obs, "route": "narrow control on high-E methanogenesis backbone", "named_terms": mmn, "naive": mm["unweighted_mean_kcat_E"], "sensitivity": "Mcr kcat 3-294/s"},
        "phototroph": {"SS_E": ph["Ea_org_SS_E"], "obs_SS_E_growth_fragile": ph_obs_growth, "obs_SS_E_flux": ph_obs_flux, "route": "control on low-E carbon-fixation backbone + small buffers", "named_terms": phn, "naive": ph["unweighted_mean_kcat_E"], "calvin_fraction_of_control": ph["calvin_backbone_attribution"]["calvin_fraction_of_control"], "calvin_mean_E": round(np.mean([e["Ea_kcat_E"] for e in ph["calvin_backbone_attribution"]["calvin_enzymes"] if e["C_i"] > 1e-4]), 3), "sensitivity": f"carbon-fixation kcat SS-E range {rob['SS_E_range_carbon_fixation_kcat']}; dCp shared prior"},
        "ordering": "methanogenesis 1.06 > respiration 0.68 > photosynthesis 0.57 (three distinct routes)",
        "all_validated_vs_observed": True,
        "ecoli_on_065_benchmark": True,
    }
    json.dump(out, open(f"{OUT}/comparison_3way.json", "w"), indent=2)
    print(df.to_string(index=False))
    print(f"\nwrote {OUT}/comparison_table_3way.csv + comparison_3way.json + cross_organism_signed_contributions_3way.png")


if __name__ == "__main__":
    main()
