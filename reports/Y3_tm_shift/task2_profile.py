#!/usr/bin/env python3
"""task2_profile.py -- Y3 TASK 2: the profile likelihood of dTm with catalysis free to compensate.

    python3 reports/Y3_tm_shift/task2_profile.py --steps 11 --maxfev 300 --workers 8

THE DECISIVE TEST. Correlation across optima is suggestive and, at n = 10 with five near-collinear
catalytic parameters, barely estimable. A direct scan is not. From p38 -- the best converged
endpoint, log L -7.186, dTm -4.021 K -- dTm is walked to 0 and at every step the five CATALYTIC
parameters are re-optimised with everything else held at p38:

    dCp_scale, kcat_scale, dTopt, topt_scale, tm_scale

If catalysis can hold a LIVING model near the optimum at dTm = 0, the shift is compensable and the
finding leans PARAMETERISATION. If growth collapses however catalysis is retuned, no amount of
global catalytic freedom substitutes for the shift, and it leans BIOLOGY. "Living" is the rule's
own condition, fixed in DECISIONS.md D1 before any of this ran: peak predicted growth at or above
half the observed 2.076 h^-1.

WHAT IS OPTIMISED. log L, not the log posterior -- the rule is stated in log L units and this is a
profile likelihood. The prior still bounds the search: a theta outside the prior's support scores
a large penalty, so the profile stays inside the region the sampler could reach. log posterior is
reported beside log L at every step so the difference is visible.

ELEVEN STEPS, NOT TWENTY-ONE, and the prompt's own fallback. One likelihood evaluation costs
1.87 s measured, so 21 steps at the 300-evaluation cap is ~3.3 h of solving; 11 steps on eight
workers fits the screen's budget while P13 has the primary tree. Recorded in DECISIONS.md D3.

Writes task2_profile.csv and task2_meta.json.
"""
from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import os
import sys
import time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "reports", "P12_modes"))

FREE = ["dCp_scale", "kcat_scale", "dTopt", "topt_scale", "tm_scale"]
BASE_KEY = "p38(b22)"
OBS_PEAK, LIVE_FRAC = 2.076, 0.5
PENALTY = 1e6
_W = {}


def _init():
    import common
    from etcgem.calibration_multi import gasflux_log_likelihood, log_prior, to_natural
    ctx, sp = common.build()
    d = pd.read_csv(os.path.join(ROOT, "reports", "P12_modes", "task2c_converged.csv"))
    r = d[d.key == BASE_KEY].iloc[0]
    th0 = np.array([float(r["x_" + n]) for n in common.NAMES], float)
    _W.update(common=common, ctx=ctx, sp=sp, th0=th0, names=common.NAMES,
              logl=gasflux_log_likelihood, logprior=log_prior, to_natural=to_natural,
              idx=[common.NAMES.index(n) for n in FREE],
              i_dtm=common.NAMES.index("dTm"))


def _one(job):
    from scipy.optimize import minimize
    step, dtm = job
    th0, sp, ctx = _W["th0"], _W["sp"], _W["ctx"]
    idx, i_dtm = _W["idx"], _W["i_dtm"]
    calls = {"n": 0, "rejected": 0}

    def f(x5):
        th = th0.copy()
        th[i_dtm] = float(dtm)
        th[idx] = np.asarray(x5, float)
        calls["n"] += 1
        if not np.isfinite(_W["logprior"](th, sp)):
            calls["rejected"] += 1
            return PENALTY
        v = float(_W["logl"](th, ctx, sp))
        return PENALTY if not np.isfinite(v) else -v

    t0 = time.time()
    x0 = th0[idx].copy()
    res = minimize(f, x0, method="Powell",
                   options=dict(maxfev=int(_W["maxfev"]), xtol=1e-4, ftol=1e-4))
    th = th0.copy()
    th[i_dtm] = float(dtm)
    th[idx] = np.asarray(res.x, float)
    dec = _W["common"].decompose(th, ctx, sp)
    nat = _W["to_natural"](th, sp)
    g = np.asarray(dec["growth"], float)
    return dict(step=step, dTm=float(dtm), logl=float(dec["logl"]),
                logpost=float(dec["logl"] + dec["logprior"]), logprior=float(dec["logprior"]),
                peak_growth=float(np.nanmax(g)),
                alive=bool(np.nanmax(g) >= LIVE_FRAC * OBS_PEAK),
                nfev=int(res.nfev), success=bool(res.success),
                rejected_outside_prior=int(calls["rejected"]),
                wall_s=time.time() - t0,
                **{n: float(nat[n]) for n in FREE})


def _init_w(maxfev):
    _init()
    _W["maxfev"] = maxfev


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--steps", type=int, default=11)
    ap.add_argument("--maxfev", type=int, default=300)
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()

    d = pd.read_csv(os.path.join(ROOT, "reports", "P12_modes", "task2c_converged.csv"))
    r = d[d.key == BASE_KEY].iloc[0]
    dtm0 = float(r["x_dTm"])
    grid = np.linspace(dtm0, 0.0, args.steps)
    print(f"[y3t2] profile from {BASE_KEY}: dTm {dtm0:.4f} -> 0 in {args.steps} steps "
          f"(step {abs(grid[1]-grid[0]):.4f} K); re-optimising {FREE} with Powell, "
          f"maxfev {args.maxfev}, on {args.workers} workers", flush=True)

    t0 = time.time()
    ctx = mp.get_context("spawn")
    rows = []
    with ctx.Pool(args.workers, initializer=_init_w, initargs=(args.maxfev,)) as pool:
        for row in pool.imap_unordered(_one, list(enumerate(grid)), chunksize=1):
            rows.append(row)
            print(f"[y3t2] step {row['step']:2d}  dTm {row['dTm']:7.4f} K  log L {row['logl']:9.4f}  "
                  f"log post {row['logpost']:9.4f}  peak growth {row['peak_growth']:7.4f} /h  "
                  f"{'ALIVE' if row['alive'] else 'dead '}  nfev {row['nfev']:4d}"
                  f"{' (capped)' if not row['success'] else ''}  [{row['wall_s']:.0f}s]", flush=True)

    p = pd.DataFrame(rows).sort_values("step").reset_index(drop=True)
    p.to_csv(os.path.join(HERE, "task2_profile.csv"), index=False)
    base = float(r["logl"])
    at0 = p[p.dTm == 0.0].iloc[0] if (p.dTm == 0.0).any() else p.iloc[-1]
    comp = p[(p.dTm >= dtm0 + 2.0) & (p.logl >= base - 2.0) & p.alive]
    out = dict(base_key=BASE_KEY, base_dTm=dtm0, base_logl=base, steps=args.steps,
               maxfev=args.maxfev, workers=args.workers, wall_s=time.time() - t0,
               free=FREE, live_threshold=LIVE_FRAC * OBS_PEAK,
               at_dTm0=dict(logl=float(at0.logl), logpost=float(at0.logpost),
                            peak_growth=float(at0.peak_growth), alive=bool(at0.alive),
                            cost_logl=float(base - at0.logl)),
               compensating_direction_exists=bool(len(comp) > 0),
               compensating_steps=[float(x) for x in comp.dTm])
    json.dump(out, open(os.path.join(HERE, "task2_meta.json"), "w"), indent=2)
    print(f"\n[y3t2] at dTm = {at0.dTm:.4f}: log L {at0.logl:.4f} against {base:.4f} at p38 "
          f"-> COST {base - at0.logl:.4f} units; peak growth {at0.peak_growth:.4f} /h "
          f"({'ALIVE' if at0.alive else 'DEAD'}, threshold {LIVE_FRAC*OBS_PEAK:.3f})", flush=True)
    print(f"[y3t2] compensating direction (>=2 K from p38, within 2 log L, still alive): "
          f"{'YES at dTm = ' + ', '.join(f'{x:.3f}' for x in comp.dTm) if len(comp) else 'NONE'}",
          flush=True)
    print(f"[y3t2] wrote task2_profile.csv, task2_meta.json  [{time.time()-t0:.0f}s]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
