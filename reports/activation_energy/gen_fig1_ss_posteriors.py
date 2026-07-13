"""Figure-1 (the ONE allowed light analysis): the THREE-organism scene-setter.

(1) Propagate the phototroph calibration draws through the Sharpe-Schoolfield fitter to get its
SS-E posterior (E. coli + methanogen posteriors are REUSED from the existing ss_e_posteriors.json,
no re-computation). (2) Build the three-panel scene-setter: the three calibrated Bayesian TPCs
(posterior-predictive band + median + observed) with the three SS-E posteriors overlaid, showing
they are separated and correctly ordered (methanogenesis ~1.06 > respiration ~0.68 > photosynthesis
~0.57). Reuses saved chains + posterior_predictive.npz + sharpe_schoolfield.py; no re-calibration.

  python reports/activation_energy/gen_fig1_ss_posteriors.py
"""
import json, logging, os, sys, warnings
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
logging.getLogger("cobra").setLevel(logging.CRITICAL); warnings.filterwarnings("ignore")
import numpy as np

OUT = "reports/activation_energy/assets/fig1"
N_DRAWS = 200
PP = {  # posterior-predictive TPC bands (built by the calibrations)
    "methanogen": "strains/mmaripaludis/outputs/calibration_jones/posterior_predictive.npz",
    "ecoli": "strains/eciML1515/outputs/calibration_vanderlinden/posterior_predictive.npz",
    "phototroph": "strains/syn6803/outputs/calibration_zavrel/posterior_predictive.npz",
}
META = {
    "methanogen": dict(title="Methanogenesis", sub="M. maripaludis (H₂/CO₂)", color="#b35806",
                       study="Jones 1983"),
    "ecoli": dict(title="Respiration", sub="E. coli (rich BHI)", color="#1b7837",
                  study="Van Derlinden 2012"),
    "phototroph": dict(title="Photosynthesis", sub="Synechocystis 6803 (light-sat.)", color="#2166ac",
                       study="Zavrel 2015"),
}


def phototroph_ss_posterior():
    import cobra; cobra.Configuration().solver = "gurobi"
    from src.etcgem.tpc import compute_tpc
    from src.etcgem.sharpe_schoolfield import fit_sharpe_schoolfield
    from src.etcgem import calibration_multi as CM
    rng = np.random.default_rng(0); grid = np.linspace(5, 52, 32)
    pm = CM._build_pm_syn6803("syn6803")
    try: pm.ec.model.solver.configuration.timeout = 15
    except Exception: pass
    specs = CM.build_syn6803_specs()
    f = np.load("strains/syn6803/outputs/calibration_zavrel/chain_flat.npy")
    idx = rng.choice(f.shape[0], size=min(N_DRAWS, f.shape[0]), replace=False)
    Es = []
    for i in idx:
        E = fit_sharpe_schoolfield(grid, compute_tpc(pm, grid, CM.to_pert(f[i], specs)).growth, T_ref_C=20.0).E
        if np.isfinite(E) and E > 0: Es.append(float(E))
    return Es


def main():
    os.makedirs(OUT, exist_ok=True)
    jpath = f"{OUT}/ss_e_posteriors.json"
    post = json.load(open(jpath)) if os.path.exists(jpath) else {}
    if "phototroph" not in post or not post["phototroph"].get("SS_E_draws"):
        Es = phototroph_ss_posterior()
        post["phototroph"] = {"SS_E_draws": Es, "median": float(np.median(Es)),
                              "ci90": [float(np.percentile(Es, 5)), float(np.percentile(Es, 95))]}
        print(f"phototroph SS-E posterior: median {np.median(Es):.3f} "
              f"90%CI [{np.percentile(Es,5):.3f},{np.percentile(Es,95):.3f}] (n={len(Es)})")
    for k in ("methanogen", "ecoli", "phototroph"):
        m = post[k]; print(f"  {k}: median {m['median']:.3f} CI {m['ci90']}")
    json.dump(post, open(jpath, "w"), indent=2)

    # --- scene-setter figure: 3 TPC panels + 1 SS-E posterior panel ---
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    order = ["methanogen", "ecoli", "phototroph"]
    # canonical numbers (single source of truth): mark E_a(model) point; observed marker + CI error bar
    CAN = {r["organism"]: r for r in json.load(open("outputs/ea_cross_organism/ss_e_canonical.json"))["rows"]}
    fig = plt.figure(figsize=(15.5, 4.4))
    gs = fig.add_gridspec(1, 4, width_ratios=[1, 1, 1, 1.35], wspace=0.34)
    for j, k in enumerate(order):
        ax = fig.add_subplot(gs[0, j]); d = np.load(PP[k]); mt = META[k]
        # data-bounded x-range: start near the lowest observed T, end just beyond the highest
        obsT = d["obs_T"]; xlo = float(obsT.min()) - 1.0; xhi = float(obsT.max()) + 2.5
        T = d["temps_C"]; m = (T >= xlo) & (T <= xhi)   # drop extrapolated model tails
        ax.fill_between(T[m], d["lo"][m], d["hi"][m], color=mt["color"], alpha=0.20, lw=0)
        ax.plot(T[m], d["med"][m], color=mt["color"], lw=2, label="posterior median")
        ax.plot(obsT, d["obs"], "o", color="k", ms=4.5, label=f"observed ({mt['study']})")
        ax.set_xlabel("temperature (°C)"); ax.set_xlim(xlo, xhi)
        ax.set_ylabel("growth rate (1/h)")
        ax.set_title(f"{mt['title']}\n{mt['sub']}", fontsize=10)
        ax.legend(fontsize=6.5, loc="upper left", frameon=False)
        for sp in ("top", "right"): ax.spines[sp].set_visible(False)
    # SS-E posterior panel — VIOLINS on a shared Ea axis (Ea on y so the ordering is obvious)
    axp = fig.add_subplot(gs[0, 3])
    data = [np.array(post[k]["SS_E_draws"]) for k in order]
    pos = np.arange(1, len(order) + 1)
    vp = axp.violinplot(data, positions=pos, showextrema=False, widths=0.8)
    for body, k in zip(vp["bodies"], order):
        body.set_facecolor(META[k]["color"]); body.set_alpha(0.55); body.set_edgecolor(META[k]["color"])
    for x, k in zip(pos, order):
        c = CAN[k]
        # canonical E_a(model) point = the marked central value + label (matches table + decomposition)
        emod = c["E_a_model"]
        axp.hlines(emod, x - 0.34, x + 0.34, color=META[k]["color"], lw=2.6, zorder=4)
        axp.text(x + 0.40, emod, f"{emod:.2f}", ha="left", va="center", fontsize=8.5,
                 color=META[k]["color"], fontweight="bold")
        # observed E_a with a CI error bar (esp. the phototroph's wide [0.34,1.01] — so the model
        # point reads as lying INSIDE the observed interval, not as a discrepancy)
        eobs = c["E_a_observed"]; lo, hi = c["E_a_observed_CI90_lo"], c["E_a_observed_CI90_hi"]
        axp.errorbar(x - 0.42, eobs, yerr=[[eobs - lo], [hi - eobs]], fmt="_", color="k",
                     ms=13, mew=2, elinewidth=1.3, capsize=3, zorder=5)
        # phototroph: Inoue light-saturated FLUX SS-E as a separate, labelled cross-check
        if "E_a_Inoue_flux_crosscheck" in c:
            axp.plot(x - 0.42, c["E_a_Inoue_flux_crosscheck"], "D", color="0.35", ms=4.5, zorder=6)
            axp.annotate("Inoue\nflux", (x - 0.42, c["E_a_Inoue_flux_crosscheck"]),
                         textcoords="offset points", xytext=(-16, -2), fontsize=5.8, color="0.35",
                         ha="right", va="center")
    axp.axhline(0.65, color="0.5", ls=":", lw=1.2)
    axp.text(0.45, 0.655, "~0.65 eV benchmark", fontsize=6.5, color="0.5", va="bottom", ha="left")
    axp.set_xticks(pos)
    axp.set_xticklabels([META[k]["title"] for k in order], fontsize=8, rotation=32, ha="right")
    axp.set_ylabel("Sharpe–Schoolfield $E_a$ (eV)")
    axp.set_title("Activation-energy: model (violins;\n— model $E_a$) vs observed (− with 90% CI)", fontsize=9.5)
    axp.set_xlim(0.25, pos[-1] + 1.0)
    for sp in ("top", "right"): axp.spines[sp].set_visible(False)
    fig.suptitle("Three metabolic strategies reproduce the Yvon-Durocher 2014 ordering at the cellular scale: "
                 "methanogenesis > respiration > photosynthesis", fontsize=11.5, y=1.02)
    fig.savefig(f"{OUT}/fig1_scene_setter.png", dpi=150, bbox_inches="tight"); plt.close(fig)

    # separation check
    order_ok = post["methanogen"]["median"] > post["ecoli"]["median"] > post["phototroph"]["median"]
    print(f"ordering methanogen>ecoli>phototroph: {order_ok}")
    print("wrote", jpath, "+ fig1_scene_setter.png")


if __name__ == "__main__":
    main()
