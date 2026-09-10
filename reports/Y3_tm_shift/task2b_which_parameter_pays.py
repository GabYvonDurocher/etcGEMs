#!/usr/bin/env python3
"""task2b_which_parameter_pays.py -- Y3 TASK 2, follow-up: is the compensation CATALYTIC, or is it
another stability parameter?

    python3 reports/Y3_tm_shift/task2b_which_parameter_pays.py --maxfev 300 --workers 4

WHY THIS IS NEEDED, and it was not anticipated by the prompt. TASK 2's profile holds a living model
at dTm = 0 for 0.077 log L units, which reads as "catalysis compensates". But the five parameters
the prompt names as catalytic include **`tm_scale`**, and `tm_scale` is not catalytic: it multiplies
each enzyme's (Tm - mean Tm) about the distribution mean. Along the profile it is the parameter that
moves most -- 0.990 at dTm = -4.02 to 1.467 at dTm = 0 -- so the compensation may be the Tm
distribution being STRETCHED rather than catalysis being retuned.

That distinction decides what the screen licenses. A measured meltome fixes both the mean and the
spread of Tm; honouring the mean (dTm = 0) while stretching the spread by 47 % contradicts the
measurement just as surely, only in a different moment.

Four fits, all at the 300-evaluation Powell cap, all from p38:

  A  dTm = -4.021 (p38), tm_scale free      the profile's own left end, for reference
  B  dTm =  0.000,       tm_scale free      the profile's right end -- what TASK 2 reported
  C  dTm =  0.000,       tm_scale = 1.000   BOTH moments of the meltome honoured
  D  dTm = -4.021,       tm_scale = 1.000   the shift kept, the spread honoured

C is the configuration OPEN_ITEMS 0b step 2 was actually asking about. If C holds a living model
near the optimum, the meltome is compatible with these data and the shift is a parameterisation
artefact. If C collapses while B does not, the compensation is stability-borne and the screen says
something narrower than "catalysis can do it".

Writes task2b_which_pays.csv and task2b_meta.json.
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
sys.path.insert(0, HERE)

CATALYTIC4 = ["dCp_scale", "kcat_scale", "dTopt", "topt_scale"]
BASE_KEY = "p38(b22)"
OBS_PEAK, LIVE_FRAC = 2.076, 0.5
PENALTY = 1e6
_W = {}


def _init(maxfev):
    import common
    from etcgem.calibration_multi import gasflux_log_likelihood, log_prior, to_natural
    ctx, sp = common.build()
    d = pd.read_csv(os.path.join(ROOT, "reports", "P12_modes", "task2c_converged.csv"))
    r = d[d.key == BASE_KEY].iloc[0]
    th0 = np.array([float(r["x_" + n]) for n in common.NAMES], float)
    _W.update(common=common, ctx=ctx, sp=sp, th0=th0, names=common.NAMES, maxfev=maxfev,
              logl=gasflux_log_likelihood, logprior=log_prior, to_natural=to_natural,
              i_dtm=common.NAMES.index("dTm"), i_tms=common.NAMES.index("tm_scale"))


def _one(job):
    from scipy.optimize import minimize
    label, dtm, tm_scale_nat, free = job
    th0, sp, ctx = _W["th0"], _W["sp"], _W["ctx"]
    idx = [_W["names"].index(n) for n in free]
    th_fixed = th0.copy()
    th_fixed[_W["i_dtm"]] = float(dtm)
    if tm_scale_nat is not None:
        th_fixed[_W["i_tms"]] = float(np.log(tm_scale_nat))   # tm_scale is exp-transformed
    n = {"rejected": 0}

    def f(x):
        th = th_fixed.copy()
        th[idx] = np.asarray(x, float)
        if not np.isfinite(_W["logprior"](th, sp)):
            n["rejected"] += 1
            return PENALTY
        v = float(_W["logl"](th, ctx, sp))
        return PENALTY if not np.isfinite(v) else -v

    t0 = time.time()
    res = minimize(f, th_fixed[idx].copy(), method="Powell",
                   options=dict(maxfev=int(_W["maxfev"]), xtol=1e-4, ftol=1e-4))
    th = th_fixed.copy()
    th[idx] = np.asarray(res.x, float)
    dec = _W["common"].decompose(th, ctx, sp)
    nat = _W["to_natural"](th, sp)
    g = np.asarray(dec["growth"], float)
    return dict(label=label, dTm=float(dtm),
                tm_scale_fixed=(float(tm_scale_nat) if tm_scale_nat is not None else np.nan),
                free=" ".join(free), logl=float(dec["logl"]),
                logpost=float(dec["logl"] + dec["logprior"]),
                peak_growth=float(np.nanmax(g)),
                alive=bool(np.nanmax(g) >= LIVE_FRAC * OBS_PEAK),
                nfev=int(res.nfev), success=bool(res.success),
                rejected_outside_prior=int(n["rejected"]), wall_s=time.time() - t0,
                **{k: float(nat[k]) for k in
                   ("dCp_scale", "kcat_scale", "dTopt", "topt_scale", "tm_scale")})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--maxfev", type=int, default=300)
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()
    d = pd.read_csv(os.path.join(ROOT, "reports", "P12_modes", "task2c_converged.csv"))
    r = d[d.key == BASE_KEY].iloc[0]
    dtm0 = float(r["x_dTm"])
    five = CATALYTIC4 + ["tm_scale"]
    jobs = [("A: dTm=p38, tm_scale free", dtm0, None, five),
            ("B: dTm=0,   tm_scale free", 0.0, None, five),
            ("C: dTm=0,   tm_scale=1", 0.0, 1.0, CATALYTIC4),
            ("D: dTm=p38, tm_scale=1", dtm0, 1.0, CATALYTIC4)]
    print(f"[y3t2b] four fits from {BASE_KEY}, Powell maxfev {args.maxfev}, "
          f"{args.workers} workers", flush=True)
    t0 = time.time()
    ctx = mp.get_context("spawn")
    rows = []
    with ctx.Pool(args.workers, initializer=_init, initargs=(args.maxfev,)) as pool:
        for row in pool.imap_unordered(_one, jobs, chunksize=1):
            rows.append(row)
            print(f"[y3t2b] {row['label']:28s} log L {row['logl']:9.4f}  log post "
                  f"{row['logpost']:9.4f}  peak growth {row['peak_growth']:7.4f} /h  "
                  f"{'ALIVE' if row['alive'] else 'DEAD '}  tm_scale {row['tm_scale']:.4f}  "
                  f"nfev {row['nfev']}{' (capped)' if not row['success'] else ''}  "
                  f"[{row['wall_s']:.0f}s]", flush=True)
    p = pd.DataFrame(rows).sort_values("label").reset_index(drop=True)
    p.to_csv(os.path.join(HERE, "task2b_which_pays.csv"), index=False)
    g = {r["label"][0]: r for r in rows}
    out = dict(base_logl=float(r["logl"]), wall_s=time.time() - t0, maxfev=args.maxfev,
               cost_B_vs_A=float(g["A"]["logl"] - g["B"]["logl"]),
               cost_C_vs_A=float(g["A"]["logl"] - g["C"]["logl"]),
               cost_D_vs_A=float(g["A"]["logl"] - g["D"]["logl"]),
               C_alive=bool(g["C"]["alive"]), B_alive=bool(g["B"]["alive"]))
    json.dump(out, open(os.path.join(HERE, "task2b_meta.json"), "w"), indent=2)
    print(f"\n[y3t2b] cost of dTm=0 with tm_scale free  (B vs A): {out['cost_B_vs_A']:+.4f} log L, "
          f"{'alive' if out['B_alive'] else 'DEAD'}")
    print(f"[y3t2b] cost of dTm=0 with tm_scale=1     (C vs A): {out['cost_C_vs_A']:+.4f} log L, "
          f"{'alive' if out['C_alive'] else 'DEAD'}")
    print(f"[y3t2b] cost of tm_scale=1 alone          (D vs A): {out['cost_D_vs_A']:+.4f} log L")
    print(f"[y3t2b] wrote task2b_which_pays.csv, task2b_meta.json  [{time.time()-t0:.0f}s]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
