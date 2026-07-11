"""Cross-organism decomposition figure in SIGNED-CONTRIBUTION style (NOT a waterfall): each of
the 4 named terms as a horizontal +/- deviation from the naive enzyme-E mean, sign-coloured
and value-labelled, both organisms side by side. Mirrors the E. coli dissection figure design.

  python reports/activation_energy/gen_fig_signed_decomp.py
"""
import json, os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

POS, NEG = "#199e70", "#d85a30"
OUT = "outputs/ea_cross_organism/cross_organism_signed_contributions.png"


def panel(ax, title, base, org_E, obs_E, terms):
    labels = [t[0] for t in terms]
    vals = [t[1] for t in terms]
    y = np.arange(len(terms))[::-1]
    colors = [POS if v >= 0 else NEG for v in vals]
    ax.barh(y, vals, color=colors, height=0.6, zorder=3)
    ax.axvline(0, color="k", lw=0.9, zorder=2)
    for yi, v in zip(y, vals):
        ax.text(v + (0.006 if v >= 0 else -0.006), yi, f"{'+' if v >= 0 else '−'}{abs(v):.2f}",
                va="center", ha="left" if v >= 0 else "right", fontsize=9.5,
                color=(POS if v >= 0 else NEG), fontweight="bold")
    ax.set_yticks(y); ax.set_yticklabels(labels, fontsize=9.5)
    span = max(abs(min(vals)), abs(max(vals)))
    ax.set_xlim(-span * 1.7, span * 1.7)
    ax.set_xlabel(f"Δ$E_a$ from enzyme mean ({base:.2f})  →  organism $E_a$ = {org_E:.2f} eV "
                  f"(obs {obs_E:.2f})", fontsize=9)
    ax.set_title(title, fontsize=10.5)
    for sp in ("top", "right", "left"):
        ax.spines[sp].set_visible(False)
    ax.tick_params(left=False)


def main():
    ec = json.load(open("strains/eciML1515/outputs/ea_dissection_ss/decomposition_ss.json"))["BHI"]
    mm = json.load(open("strains/mmaripaludis/outputs/ea_dissection_ss/decomposition_ss.json"))
    comp = json.load(open("outputs/ea_cross_organism/comparison.json"))
    ecn, mmn = ec["named_terms_eV"], mm["named_terms_eV"]
    order = [("control weighting", "control_weighting"),
             ("allocation (growth law)", "allocation"),
             ("maintenance NGAM(T)", "maintenance"),
             ("aggregation", "aggregation")]
    fig, ax = plt.subplots(1, 2, figsize=(12.5, 3.5), sharex=False)
    panel(ax[0], "E. coli respiration — broad control, allocation-buffered",
          ec["unweighted_mean_kcat_E"], ec["Ea_org_SS_E"], comp["ecoli"]["obs_SS_E"],
          [(lab, ecn[k]) for lab, k in order])
    panel(ax[1], "M. maripaludis methanogenesis — backbone control, no buffer",
          mm["unweighted_mean_kcat_E"], mm["Ea_org_SS_E"], comp["methanogen"]["obs_SS_E"],
          [(lab.replace("(growth law)", "(flat, Müller)") if k == "allocation" else lab, mmn[k])
           for lab, k in order])
    fig.suptitle("What moves the organism $E_a$ from the naive enzyme mean "
                 "(Sharpe–Schoolfield $E$; both organisms sectored)", fontsize=11)
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(OUT, dpi=200); plt.close(fig)
    print("wrote", OUT)
    print(f"  E. coli: naive {ec['unweighted_mean_kcat_E']} control {ecn['control_weighting']:+} "
          f"alloc {ecn['allocation']:+} -> {ec['Ea_org_SS_E']}")
    print(f"  methan : naive {mm['unweighted_mean_kcat_E']} control {mmn['control_weighting']:+} "
          f"alloc {mmn['allocation']:+} -> {mm['Ea_org_SS_E']}")


if __name__ == "__main__":
    main()
