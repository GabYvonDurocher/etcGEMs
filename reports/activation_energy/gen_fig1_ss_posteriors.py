"""Figure-1 data (the ONE allowed light analysis): propagate the calibration posterior draws
of each organism through the Sharpe-Schoolfield fitter to get the SS-E POSTERIOR distribution,
so Figure 1 can show the two SS-E posteriors are separated (methanogen ~1.0 vs E. coli ~0.6).
Reuses saved chains + sharpe_schoolfield.py; no re-calibration.

  python reports/activation_energy/gen_fig1_ss_posteriors.py
"""
import json, logging, os, sys, warnings
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
logging.getLogger("cobra").setLevel(logging.CRITICAL); warnings.filterwarnings("ignore")
import numpy as np

OUT = "reports/activation_energy/assets/fig1"
N_DRAWS = 200


def main():
    import cobra; cobra.Configuration().solver = "gurobi"
    from src.etcgem.tpc import compute_tpc
    from src.etcgem.sharpe_schoolfield import fit_sharpe_schoolfield
    from src.etcgem import calibration_multi as CM
    os.makedirs(OUT, exist_ok=True)
    rng = np.random.default_rng(0)
    grid = np.linspace(5, 52, 32)

    out = {}
    # --- methanogen (sectored model, fast) ---
    from src.etcgem.config import resolve, build_provider
    pm_m = build_provider(resolve("mmaripaludis"))
    try: pm_m.ec.model.solver.configuration.timeout = 15
    except Exception: pass
    specs_m = CM.build_methanogen_specs()
    fm = np.load("strains/mmaripaludis/outputs/calibration_jones/chain_flat.npy")
    idx = rng.choice(fm.shape[0], size=min(N_DRAWS, fm.shape[0]), replace=False)
    Es = []
    for k, i in enumerate(idx):
        pert = CM.to_pert(fm[i], specs_m)
        E = fit_sharpe_schoolfield(grid, compute_tpc(pm_m, grid, pert).growth, T_ref_C=20.0).E
        if np.isfinite(E): Es.append(float(E))
    out["methanogen"] = {"SS_E_draws": Es, "median": float(np.median(Es)),
                         "ci90": [float(np.percentile(Es, 5)), float(np.percentile(Es, 95))]}
    print(f"methanogen SS-E posterior: median {np.median(Es):.3f} 90%CI [{np.percentile(Es,5):.3f},{np.percentile(Es,95):.3f}] (n={len(Es)})")

    # --- E. coli (rich BHI, GECKO; slower) ---
    pm_e = CM._build_pm_rich("eciML1515")
    try: pm_e.ec.model.solver.configuration.timeout = 20
    except Exception: pass
    specs_e = CM.build_vdl_specs()
    fe = np.load("strains/eciML1515/outputs/calibration_vanderlinden/chain_flat.npy")
    idxe = rng.choice(fe.shape[0], size=min(N_DRAWS, fe.shape[0]), replace=False)
    Ese = []
    for k, i in enumerate(idxe):
        pert = CM.to_pert(fe[i], specs_e)
        E = fit_sharpe_schoolfield(grid, compute_tpc(pm_e, grid, pert).growth, T_ref_C=20.0).E
        if np.isfinite(E): Ese.append(float(E))
        if (k + 1) % 50 == 0: print(f"  ecoli {k+1}/{len(idxe)}")
    out["ecoli"] = {"SS_E_draws": Ese, "median": float(np.median(Ese)),
                    "ci90": [float(np.percentile(Ese, 5)), float(np.percentile(Ese, 95))]}
    print(f"ecoli SS-E posterior: median {np.median(Ese):.3f} 90%CI [{np.percentile(Ese,5):.3f},{np.percentile(Ese,95):.3f}] (n={len(Ese)})")

    # separation
    sep = np.percentile(out["methanogen"]["SS_E_draws"], 5) - np.percentile(out["ecoli"]["SS_E_draws"], 95)
    out["separation_methanogen5_minus_ecoli95"] = float(sep)
    out["separated"] = bool(sep > 0)
    print(f"SS-E posteriors SEPARATED (methan p5 - ecoli p95 = {sep:+.3f}): {sep>0}")
    json.dump(out, open(f"{OUT}/ss_e_posteriors.json", "w"), indent=2)
    print("wrote", f"{OUT}/ss_e_posteriors.json")


if __name__ == "__main__":
    main()
