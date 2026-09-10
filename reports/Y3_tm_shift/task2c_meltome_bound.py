#!/usr/bin/env python3
"""task2c_meltome_bound.py -- Y3 TASK 2, second follow-up: how expensive is the meltome-honouring
fit, really?

    python3 reports/Y3_tm_shift/task2c_meltome_bound.py --maxfev 1000 --restarts 2

WHY THIS ONE IS WORTH THE TIME. `task2b` case C -- `dTm` = 0 and `tm_scale` = 1, both moments of
the measured meltome honoured, the four catalytic parameters re-optimised -- comes back ALIVE at
1.618 h^-1 with log L -17.05. That contradicts a committed claim: OPEN_ITEMS 1.20 says "the
meltome-honouring region of parameter space contains no growing model". It does contain one.

But C hit the 300-evaluation Powell cap, so -17.05 is a LOWER BOUND on the achievable log L and
9.86 units is an UPPER BOUND on the cost. How large that cost really is decides whether the
meltome-honouring model is a serious candidate or a curiosity, so it is worth bounding better
than a capped first pass. This restarts Powell from C's own solution and lets it run 1000
evaluations, twice in sequence -- the standard way to continue Powell.

Writes task2c_bound.csv and task2c_bound.json.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "reports", "P12_modes"))

CATALYTIC4 = ["dCp_scale", "kcat_scale", "dTopt", "topt_scale"]
BASE_KEY = "p38(b22)"
OBS_PEAK, LIVE_FRAC = 2.076, 0.5
PENALTY = 1e6


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--maxfev", type=int, default=1000)
    ap.add_argument("--restarts", type=int, default=2)
    args = ap.parse_args()

    import common
    from scipy.optimize import minimize
    from etcgem.calibration_multi import gasflux_log_likelihood, log_prior, to_natural
    ctx, sp = common.build()
    N = common.NAMES
    d = pd.read_csv(os.path.join(ROOT, "reports", "P12_modes", "task2c_converged.csv"))
    r = d[d.key == BASE_KEY].iloc[0]
    th0 = np.array([float(r["x_" + n]) for n in N], float)
    th0[N.index("dTm")] = 0.0
    th0[N.index("tm_scale")] = 0.0            # exp(0) = 1: the meltome's own spread
    idx = [N.index(n) for n in CATALYTIC4]

    prev = pd.read_csv(os.path.join(HERE, "task2b_which_pays.csv"))
    c = prev[prev.label.str.startswith("C:")].iloc[0]
    x = np.array([np.log(c[k]) if k.endswith("_scale") else float(c[k]) for k in CATALYTIC4],
                 float)     # the *_scale parameters are exp-transformed; dTopt is not
    x[CATALYTIC4.index("dTopt")] = float(c["dTopt"])

    def f(v):
        th = th0.copy()
        th[idx] = np.asarray(v, float)
        if not np.isfinite(log_prior(th, sp)):
            return PENALTY
        y = float(gasflux_log_likelihood(th, ctx, sp))
        return PENALTY if not np.isfinite(y) else -y

    rows, t0 = [], time.time()
    print(f"[y3t2c] restarting Powell from task2b C (log L {float(c['logl']):.4f}), "
          f"maxfev {args.maxfev} x {args.restarts}, dTm = 0 and tm_scale = 1 both held", flush=True)
    for k in range(args.restarts):
        res = minimize(f, x, method="Powell",
                       options=dict(maxfev=args.maxfev, xtol=1e-6, ftol=1e-6))
        x = np.asarray(res.x, float)
        th = th0.copy()
        th[idx] = x
        dec = common.decompose(th, ctx, sp)
        nat = to_natural(th, sp)
        g = np.asarray(dec["growth"], float)
        rows.append(dict(restart=k, logl=float(dec["logl"]),
                         logpost=float(dec["logl"] + dec["logprior"]),
                         peak_growth=float(np.nanmax(g)),
                         alive=bool(np.nanmax(g) >= LIVE_FRAC * OBS_PEAK),
                         nfev=int(res.nfev), success=bool(res.success),
                         wall_s=time.time() - t0,
                         **{n: float(nat[n]) for n in CATALYTIC4 + ["dTm", "tm_scale"]}))
        print(f"[y3t2c] restart {k}: log L {rows[-1]['logl']:9.4f}  peak growth "
              f"{rows[-1]['peak_growth']:7.4f} /h  {'ALIVE' if rows[-1]['alive'] else 'DEAD'}  "
              f"nfev {res.nfev}{' (capped)' if not res.success else ''}  "
              f"[{time.time()-t0:.0f}s]", flush=True)

    p = pd.DataFrame(rows)
    p.to_csv(os.path.join(HERE, "task2c_bound.csv"), index=False)
    base = float(r["logl"])
    best = float(p.logl.max())
    json.dump(dict(base_logl=base, best_meltome_logl=best, cost_upper_bound=base - best,
                   alive=bool(p.iloc[int(p.logl.idxmax())].alive),
                   peak_growth=float(p.iloc[int(p.logl.idxmax())].peak_growth),
                   converged=bool(p.success.any()), wall_s=time.time() - t0),
              open(os.path.join(HERE, "task2c_bound.json"), "w"), indent=2)
    print(f"\n[y3t2c] meltome-honouring best log L {best:.4f} against p38's {base:.4f} "
          f"-> cost at most {base - best:.4f} units, model ALIVE at "
          f"{float(p.iloc[int(p.logl.idxmax())].peak_growth):.4f} /h", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
