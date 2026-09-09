#!/usr/bin/env python3
"""P10 -- P9's line-scan instrument, generalised: the same 41-point lines through P4's MAP, a
fresh model per evaluation, single process, but recording per-temperature growth and O2 as
well as the log-likelihood, and taking the two P10 options as arguments so the surface can be
read under (a) tie-break only, (b) variance only, (c) both, (0) neither.

    python reports/P10_respiration_likelihood/lines.py --tag baseline
    python reports/P10_respiration_likelihood/lines.py --tag tiebreak --tiebreak pfba
    python reports/P10_respiration_likelihood/lines.py --tag variance --floor 0.7
    python reports/P10_respiration_likelihood/lines.py --tag both --tiebreak pfba --floor 0.7

The options are passed to the likelihood through ctx["respiration"], which the core reads once
P10's options exist; with neither given the run is P9's instrument exactly. Writes
lines_<tag>.csv (per point: logL, per-T growth and O2), lines_<tag>_summary.csv.
"""
import argparse
import json
import os
import sys
import time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "reports", "P6_convergence"))
sys.path.insert(0, os.path.join(ROOT, "reports", "P9_surface"))
os.chdir(ROOT)
from etcgem.calibration_multi import gasflux_log_likelihood, to_pert, to_natural   # noqa: E402
from etcgem.gasflux import flux_tpc                                                # noqa: E402
from p6_fits import FITS                                                           # noqa: E402
from task1_scan import build, STEPS                                                # noqa: E402
from task2_solver import direction_factory                                         # noqa: E402

P9 = os.path.join(ROOT, "reports", "P9_surface")
ROUGH = ["axis:topt_scale", "axis:dCp_scale", "axis:kcat_scale", "axis:f_maint", "axis:ngam_scale", "axis:clearance_mult",
         "PC1", "PC2", "PC3", "random1", "random2", "random3"]      # the twelve lines P9 read ROUGH (step > 20 % of range)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--tag", required=True); ap.add_argument("--tiebreak", default=None)
    ap.add_argument("--floor", type=float, default=None); ap.add_argument("--lines", default=None); a = ap.parse_args()
    lines = a.lines.split(",") if a.lines else ROUGH
    fit = [f for f in FITS if f[0] == "D_NLDM"][0]
    meta = json.load(open(os.path.join(P9, "task1_meta.json"))); theta0 = np.array(meta["theta0"]); sd = np.array(meta["sd"]); names = meta["names"]
    direction = direction_factory(names)
    rows, summ, t_all = [], [], time.time()
    for li, lname in enumerate(lines):
        v = direction(lname); vals = []; t0 = time.time()
        for s in STEPS:
            ctx, sp = build(fit)
            if a.tiebreak or a.floor is not None:
                ctx["respiration"] = {"tiebreak": a.tiebreak or "none", "log_o2_floor": a.floor or 0.0}
            th = theta0 + s * sd * v
            ll = gasflux_log_likelihood(th, ctx, sp)
            # the O2 the likelihood saw: recompute through the same path (state installed by the call above)
            df = flux_tpc(ctx["pm"], ctx["T"], to_pert(th, sp), metabolites=("o2",), tiebreak=(ctx.get("respiration") or {}).get("tiebreak", "none")) \
                if "tiebreak" in flux_tpc.__code__.co_varnames else flux_tpc(ctx["pm"], ctx["T"], to_pert(th, sp), metabolites=("o2",))
            vals.append(ll)
            for T, g, o2 in zip(ctx["T"], df["growth"].to_numpy(float), df["o2_uptake"].to_numpy(float)):
                rows.append(dict(line=lname, step_sd=float(s), logL=float(ll), T_C=float(T), growth=float(g), o2=float(o2)))
        vals = np.array(vals); fin = np.isfinite(vals); d1 = np.diff(vals[fin]); sc = int(np.sum(np.sign(d1[1:]) * np.sign(d1[:-1]) < 0))
        jump = float(np.max(np.abs(d1))); rng_ = float(vals[fin].max() - vals[fin].min())
        summ.append(dict(tag=a.tag, line=lname, sign_changes=sc, max_jump=jump, max_jump_frac=jump / rng_ if rng_ > 0 else np.nan, range=rng_,
                         ll_at_map=float(vals[20]), s_per_eval=round((time.time() - t0) / len(STEPS), 2)))
        print(f"[lines:{a.tag}] {li+1:2d}/{len(lines)} {lname:22s} sign changes {sc:2d}  max jump {jump:8.3f} ({100*jump/rng_ if rng_>0 else float('nan'):5.1f} % of {rng_:.2f})  {(time.time()-t0)/len(STEPS):.2f} s/eval", flush=True)
        pd.DataFrame(rows).to_csv(os.path.join(HERE, f"lines_{a.tag}.csv"), index=False)
        pd.DataFrame(summ).to_csv(os.path.join(HERE, f"lines_{a.tag}_summary.csv"), index=False)
    df = pd.DataFrame(summ)
    print(f"[lines:{a.tag}] SUMMARY: sign changes median {df.sign_changes.median():.0f} max {df.sign_changes.max()}; jump median {df.max_jump.median():.2f} max {df.max_jump.max():.2f}; "
          f"frac median {100*df.max_jump_frac.median():.1f} % max {100*df.max_jump_frac.max():.1f} %; lines > 20 %: {int((df.max_jump_frac>0.2).sum())}; > 5 %: {int((df.max_jump_frac>0.05).sum())}; wall {(time.time()-t_all)/60:.1f} min", flush=True)
    print(f"[lines:{a.tag}] done", flush=True)


if __name__ == "__main__":
    main()
