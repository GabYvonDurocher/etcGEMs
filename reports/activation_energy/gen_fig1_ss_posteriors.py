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
    fig = plt.figure(figsize=(15, 4.2))
    gs = fig.add_gridspec(1, 4, width_ratios=[1, 1, 1, 1.05], wspace=0.32)
    for j, k in enumerate(order):
        ax = fig.add_subplot(gs[0, j]); d = np.load(PP[k]); mt = META[k]
        ax.fill_between(d["temps_C"], d["lo"], d["hi"], color=mt["color"], alpha=0.20, lw=0)
        ax.plot(d["temps_C"], d["med"], color=mt["color"], lw=2, label="posterior median")
        ax.plot(d["obs_T"], d["obs"], "o", color="k", ms=4.5, label=f"observed ({mt['study']})")
        ax.set_xlabel("temperature (°C)"); ax.set_xlim(5, 52)
        ax.set_ylabel("growth rate (1/h)")
        ax.set_title(f"{mt['title']}\n{mt['sub']}", fontsize=10)
        ax.legend(fontsize=6.5, loc="upper left", frameon=False)
        for sp in ("top", "right"): ax.spines[sp].set_visible(False)
    # SS-E posterior panel
    axp = fig.add_subplot(gs[0, 3])
    for k in order:
        mt = META[k]; draws = np.array(post[k]["SS_E_draws"])
        axp.hist(draws, bins=28, density=True, color=mt["color"], alpha=0.55,
                 label=f"{mt['title']} {post[k]['median']:.2f}")
        axp.axvline(post[k]["median"], color=mt["color"], lw=1.6)
    axp.axvline(0.65, color="0.4", ls=":", lw=1.2)
    axp.text(0.65, axp.get_ylim()[1] * 0.96, " ~0.65 eV\n benchmark", fontsize=6.5, color="0.4", va="top")
    axp.set_xlabel("Sharpe–Schoolfield $E_a$ (eV)"); axp.set_ylabel("posterior density")
    axp.set_title("Activation-energy posteriors\n(separated, correctly ordered)", fontsize=10)
    axp.legend(fontsize=7, frameon=False, loc="upper right")
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
