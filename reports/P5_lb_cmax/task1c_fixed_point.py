#!/usr/bin/env python3
"""P5 TASK 1c -- the deterministic check the trapped chain could not give.

The P5 chain (run_lb_fit.py) was warm-started into a dead mode (zero growth at every
temperature, the growth discrepancy term absorbing the data) and never left it, so its R2 says
nothing about c_max. This script asks the question at FIXED parameter points instead, with no
sampler: the same parameter vector, scored the same way (P4's recipe: dense grid, interpolated
onto the observed temperatures), in our configuration-D LB model at c_max 120 and at 257.

Points:
  * Parsa's own configD_LB_full MAP (read from his chain under $PARSA_ROOT, READ ONLY; his
    C_max_LB_mult dropped because the cap is fixed here) -- the point P3's gate reproduced his
    0.90 at, with the cap at 256.7;
  * P4's D_LB MAP at c_max 120 (growth R2 0.196);
  * the P5 chain's MAP (the dead mode), for the record.
Then a local optimisation of the log-posterior (Powell) from his MAP and from P4's MAP, in each
context, so "the best growing-mode fit at each cap" is compared like for like without emcee.

Writes fixed_point_r2.csv beside this file.
"""
import json
import os
import sys
import time

import numpy as np
import pandas as pd
from scipy.optimize import minimize

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "reports", "P4_refit"))
sys.path.insert(0, os.path.join(ROOT, "reports", "P3_gate"))
os.chdir(ROOT)

from etcgem.calibration_multi import (_build_gasflux_ctx, gasflux_log_likelihood, log_prior,  # noqa: E402
                                      to_pert, to_natural)
from etcgem.gasflux import flux_tpc                                                          # noqa: E402
from run_fits import r2, DENSE                                                               # noqa: E402
from gate_def import read_points                                                             # noqa: E402

PARSA = os.environ.get("PARSA_ROOT", "/Users/g.yvon-durocher/Downloads/etcGEMs-main_3")
HIS_DIR = os.path.join(PARSA, "strains", "eciML1515", "outputs", "calibration_configD_LB_full")
P4_DIR = os.path.join(ROOT, "strains", "eciML1515", "outputs", "calibration_configD_LB_recipe_cmax120")
P5_DIR = os.path.join(ROOT, "strains", "eciML1515", "outputs", "calibration_configD_LB_recipe_cmax257")
TABLE = "respirometry/derived_R2A_LB_current.csv"
CAPS = (120.0, 257.0)
MAXFEV = int(os.environ.get("P5_MAXFEV", "600"))


def chain_map(d):
    ch, lp = np.load(os.path.join(d, "chain.npy")), np.load(os.path.join(d, "log_prob.npy"))
    i, j = np.unravel_index(np.nanargmax(lp), lp.shape)
    return ch[i, j]


def score_point(theta, ctx, specs):
    nat = to_natural(theta, specs)
    df = flux_tpc(ctx["pm"], DENSE, to_pert(theta, specs), metabolites=("o2", "co2", "ac"))
    g = df["growth"].to_numpy(float)
    rr = df["o2_uptake"].to_numpy(float) * ctx["o2_conv"] * float(nat["resp_scale"])
    return dict(growth_R2=r2(ctx["growth_obs"], ctx["T"], g, DENSE),
                resp_R2=r2(ctx["resp_obs"], ctx["T"], rr, DENSE),
                rmax=float(np.nanmax(g)), Topt_C=float(DENSE[int(np.nanargmax(g))]),
                logL=gasflux_log_likelihood(theta, ctx, specs),
                logpost=gasflux_log_likelihood(theta, ctx, specs) + log_prior(theta, specs),
                kcat_scale=nat["kcat_scale"], dTopt=nat["dTopt"], dTm=nat["dTm"],
                disc_growth=nat["disc_growth"])


def main():
    # his MAP, with C_max_LB_mult removed (our specs carry no cap parameter: the cap is fixed)
    meta = json.load(open(os.path.join(HIS_DIR, "meta.json")))
    his_names = meta["param_names"]
    th_his_full, th_his_med_full, _, _ = read_points(HIS_DIR)
    keep = [k for k, n in enumerate(his_names) if n != "C_max_LB_mult"]
    th_his = th_his_full[keep]
    his_cap = 230.0 * float(np.exp(th_his_full[his_names.index("C_max_LB_mult")]))
    th_p4, th_p5 = chain_map(P4_DIR), chain_map(P5_DIR)

    rows = []
    for cap in CAPS:
        ctx, specs = _build_gasflux_ctx(strain="eciML1515", medium="LB", experiment="gasflux_configD",
                                        table=TABLE, otu=2, c_max=cap, etc_table=None,
                                        apply_protons=False, fit_clearance=False)
        assert [s.name for s in specs] == [his_names[k] for k in keep], ([s.name for s in specs], his_names)
        for label, th in (("Parsa D_LB MAP (his cap %.1f)" % his_cap, th_his),
                          ("P4 D_LB MAP (cap 120)", th_p4),
                          ("P5 chain MAP (cap 257, dead mode)", th_p5)):
            sc = score_point(th, ctx, specs)
            rows.append(dict(c_max=cap, point=label, optimised=False, **sc))
            print(f"[fixed] cap {cap:g}  {label:36s} growth R2 {sc['growth_R2']:7.3f}  resp R2 {sc['resp_R2']:7.3f}  "
                  f"rmax {sc['rmax']:.3f}  logpost {sc['logpost']:.2f}", flush=True)
        # local optimisation of the log posterior from the two growing-mode starts
        for label, th0 in (("Powell from Parsa's MAP", th_his), ("Powell from P4's MAP", th_p4)):
            t0 = time.time()
            f = lambda th: -(gasflux_log_likelihood(th, ctx, specs) + log_prior(th, specs))
            res = minimize(f, th0, method="Powell", options=dict(maxfev=MAXFEV, xtol=1e-3, ftol=1e-3))
            sc = score_point(res.x, ctx, specs)
            rows.append(dict(c_max=cap, point=label, optimised=True, nfev=int(res.nfev), **sc))
            print(f"[opt]   cap {cap:g}  {label:36s} growth R2 {sc['growth_R2']:7.3f}  resp R2 {sc['resp_R2']:7.3f}  "
                  f"rmax {sc['rmax']:.3f}  logpost {sc['logpost']:.2f}  ({res.nfev} evals, {(time.time()-t0)/60:.1f} min)", flush=True)
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(HERE, "fixed_point_r2.csv"), index=False)
    pd.set_option("display.width", 220)
    print(df.round(3).to_string(index=False))
    print("[task1c] done", flush=True)


if __name__ == "__main__":
    main()
