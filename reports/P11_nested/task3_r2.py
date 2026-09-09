#!/usr/bin/env python3
"""P11 TASK 3 -- growth and respiration R2 at the new posterior median, beside P4's at its
median and Parsa's at his, and where sigma sits. P4's scorer's recipe: the dense grid
np.arange(8, 55.01, 1.5), prediction interpolated onto the observed temperatures.
Writes task3_r2.csv beside this file."""
import json, os, sys
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src")); sys.path.insert(0, os.path.join(ROOT, "reports", "P6_convergence")); sys.path.insert(0, os.path.join(ROOT, "reports", "P4_refit")); sys.path.insert(0, HERE); os.chdir(ROOT)
from etcgem.calibration_multi import _build_gasflux_ctx, gasflux_log_likelihood, to_natural, to_pert, build_gasflux_specs  # noqa: E402
from etcgem.gasflux import flux_tpc                                                    # noqa: E402
from run_fits import r2, DENSE                                                         # noqa: E402
from p6_fits import FITS                                                               # noqa: E402
from task3_posterior import equal_weight                                               # noqa: E402
P4 = os.path.join(ROOT, "strains", "eciML1515", "outputs", "calibration_configD_NLDM_recipe_cmax120")
FIT = [f for f in FITS if f[0] == "D_NLDM"][0]


def score(th, ctx, sp, tiebreak):
    nat = to_natural(th, sp)
    gasflux_log_likelihood(th, ctx, sp)      # installs the medium at this theta
    df = flux_tpc(ctx["pm"], DENSE, to_pert(th, sp), metabolites=("o2",), tiebreak=tiebreak)
    g = df["growth"].to_numpy(float); rr = df["o2_uptake"].to_numpy(float) * ctx["o2_conv"] * float(nat["resp_scale"])
    return dict(growth_R2=r2(ctx["growth_obs"], ctx["T"], g, DENSE), resp_R2=r2(ctx["resp_obs"], ctx["T"], rr, DENSE),
                rmax=float(np.nanmax(g)), Topt_C=float(DENSE[int(np.nanargmax(g))]), sigma=float(nat["sigma"]),
                disc_resp=float(nat["disc_resp"]), disc_growth=float(nat["disc_growth"]), resp_scale=float(nat["resp_scale"]))


def main(tag="main"):
    label, cfg, medium, table, otu, c_max, etc, protons, fit_k = FIT
    specs = build_gasflux_specs({"use_etc": False, "fit_clearance": fit_k})
    post, summ, _ = equal_weight(tag); th_new = np.median(post, axis=0)
    ch = np.load(os.path.join(P4, "chain.npy")); burn = int(2 * 244.7)
    th_p4 = np.median(ch[burn:].reshape(-1, ch.shape[2]), axis=0)
    rows = []
    ctx, sp = _build_gasflux_ctx(strain="eciML1515", medium=medium, experiment=f"gasflux_config{cfg}", table=table,
                                 otu=otu, c_max=c_max, etc_table=etc, apply_protons=protons, fit_clearance=fit_k)
    tb = ctx["respiration"].get("tiebreak", "none")
    for name, th in (("P11 nested posterior median", th_new), ("P4 posterior median", th_p4)):
        for scoring, t in ((f"new likelihood (tiebreak {tb}, floor {ctx['respiration']['log_o2_floor']})", tb), ("P4's scoring (no tiebreak)", "none")):
            c2, s2 = _build_gasflux_ctx(strain="eciML1515", medium=medium, experiment=f"gasflux_config{cfg}", table=table,
                                        otu=otu, c_max=c_max, etc_table=etc, apply_protons=protons, fit_clearance=fit_k)
            if t == "none": c2["respiration"] = {"tiebreak": "none", "log_o2_floor": 0.0}
            sc = score(th, c2, s2, t)
            rows.append(dict(point=name, scored_under=scoring, **sc))
            print(f"[r2] {name:30s} | {scoring:52s} growth R2 {sc['growth_R2']:.4f}  resp R2 {sc['resp_R2']:.4f}  rmax {sc['rmax']:.3f}  T_opt {sc['Topt_C']:.1f}  sigma {sc['sigma']:.3f}  disc_resp {sc['disc_resp']:.3f}", flush=True)
    pd.DataFrame(rows).to_csv(os.path.join(HERE, "task3_r2.csv"), index=False)
    print("[r2] done", flush=True)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "main")
