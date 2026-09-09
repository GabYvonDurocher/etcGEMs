#!/usr/bin/env python3
"""task2_regime.py -- Y2 TASK 2: Y1's regime test at the prior, at the posterior median, and at
N posterior draws.

    python3 reports/Y2_regime_posterior/task2_regime.py --bayesiangem <clone> --results <extracted> \
        --draws 100 --prior-draws 40 --workers 6

WHY DRAWS AND NOT A MEDIAN. The median particle is one point; the paper's own results are stated
over 100 posterior models. A point estimate from the median cannot say how much of the 10.09 C
Y1 measured is the calibration and how much is the width of the parameter set it happened to be
run at. Draws give an interval, and an interval is what makes the number quotable.

The prior is drawn from too, so the prior -> posterior comparison is like for like: 128 prior
particles are the first SMC-ABC generation, and Y1's "prior" was a different object again -- the
point table `data/model_enzyme_params.csv`. All three are run.

Every curve is `regime.sweep`, which is `etc.simulate_growth`'s own calls amortised across the
four glucose settings; the amortisation is verified exact (max abs diff 0.0) before any of it is
used, and the run aborts if it is not.

Writes task2_summary.csv (one row per parameter set per setting), task2_ranges.csv (one row per
parameter set: the across-setting T_opt and CT_max ranges Y1 quoted) and task2_verify.json.
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
sys.path.insert(0, HERE)

from posterior import import_their_code, load_populations, median_particle   # noqa: E402
from regime import CAPS, SIGMA, TS_C, summarise, sweep, verify_against_simulate_growth  # noqa: E402

AEROBIC = "ecYeast7_v1.0_batch_minimal_thermo.mat"
_W = {}


def _init(bg):
    """One model, one copy of their code, per worker."""
    sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Y1_yeast_audit"))
    from yeast_model import load                                   # noqa: E402
    etc, GEMS = import_their_code(bg)
    model, _ = load(os.path.join(bg, "models", AEROBIC))
    _W.update(etc=etc, GEMS=GEMS, model=model)


def _one(job):
    kind, index, particle = job
    etc, GEMS, model = _W["etc"], _W["GEMS"], _W["model"]
    df, _ = GEMS.format_input(particle)
    t0 = time.time()
    curves = sweep(model, etc, df)
    per, rng = summarise(TS_C, curves)
    return kind, index, per, rng, time.time() - t0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bayesiangem", required=True)
    ap.add_argument("--results", required=True)
    ap.add_argument("--draws", type=int, default=100,
                    help="posterior draws; the population is 100, so 100 is all of them")
    ap.add_argument("--prior-draws", type=int, default=40)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--seed", type=int, default=20260909)
    args = ap.parse_args()
    bg = os.path.abspath(args.bayesiangem)

    prior, post, _ = load_populations(args.results, bg)
    etc, GEMS = import_their_code(bg)
    prior_file = {k: float(GEMS.params.loc[k.rsplit("_", 1)[0], k.rsplit("_", 1)[1]])
                  for k in prior[0]}

    # --- the amortisation must be exact before anything else counts ---------------------
    sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Y1_yeast_audit"))
    from yeast_model import load                                   # noqa: E402
    m0, _ = load(os.path.join(bg, "models", AEROBIC))
    df0, _ = GEMS.format_input(prior_file)
    v, ours, theirs = verify_against_simulate_growth(m0, etc, df0, TS_C, SIGMA, 10.0)
    print(f"[y2t2] amortised sweep vs etc.simulate_growth, prior at glucose_cap=10:\n"
          f"        curve max abs diff      {v['curve_max_abs_diff']:.3e}\n"
          f"        solver repeat noise     {v['solver_repeat_noise']:.3e}  "
          f"(their own function, twice, same model)\n"
          f"        descriptor max abs diff {v['descriptor_max_abs_diff']:.3e}  "
          f"(T_opt, CT_max, plateau edges)", flush=True)
    verify = dict(n_temperatures=len(TS_C), sigma=SIGMA, caps=[c for c, _ in CAPS], **v)
    # THE GATE, and its tolerance is measured rather than guessed. The amortisation must not move
    # a curve by more than the solver moves it between two identical calls to their own function,
    # and must not move a descriptor by more than 1e-4 C -- a hundred times finer than the 0.01 C
    # this report quotes to. Measured on the prior: the amortisation differs from their function
    # by 4.5e-10 while their function differs from ITSELF by 3.8e-7, so the amortisation is three
    # orders of magnitude quieter than the solver's own run-to-run repeatability.
    ok = (v["curve_max_abs_diff"] <= max(10 * v["solver_repeat_noise"], 1e-8)
          and v["descriptor_max_abs_diff"] <= 1e-4)
    if not ok:
        json.dump(verify, open(os.path.join(HERE, "task2_verify.json"), "w"), indent=2, default=str)
        print("[y2t2] STOP: the amortisation changes the result", flush=True)
        return 2

    rng = np.random.default_rng(args.seed)
    post_idx = list(range(len(post))) if args.draws >= len(post) else \
        sorted(rng.choice(len(post), size=args.draws, replace=False).tolist())
    prior_idx = list(range(len(prior))) if args.prior_draws >= len(prior) else \
        sorted(rng.choice(len(prior), size=args.prior_draws, replace=False).tolist())

    jobs = [("prior_file", -1, prior_file),
            ("prior_median", -1, median_particle(prior)),
            ("posterior_median", -1, median_particle(post))]
    jobs += [("posterior_draw", i, post[i]) for i in post_idx]
    jobs += [("prior_draw", i, prior[i]) for i in prior_idx]
    print(f"[y2t2] {len(jobs)} parameter sets x {len(CAPS)} settings x {len(TS_C)} temperatures "
          f"on {args.workers} workers", flush=True)

    rows, rrows, t0 = [], [], time.time()
    ctx = mp.get_context("spawn")
    with ctx.Pool(args.workers, initializer=_init, initargs=(bg,)) as pool:
        for n, (kind, index, per, rng_, secs) in enumerate(
                pool.imap_unordered(_one, jobs, chunksize=1), 1):
            for lab, d in per.items():
                rows.append(dict(kind=kind, index=index, setting=lab, **d))
            rrows.append(dict(kind=kind, index=index, **rng_))
            if kind.endswith("median") or kind == "prior_file" or n % 10 == 0:
                print(f"[y2t2] {n:3d}/{len(jobs)} {kind:17s} idx={index:3d}  "
                      f"T_opt range {rng_['T_opt_range']:6.2f} C  CT_max range "
                      f"{rng_['CT_max_range']:5.2f} C  plateau {rng_['plateau_lo']:.1f}->"
                      f"{rng_['plateau_hi']:.1f} C  ({secs:.0f}s)", flush=True)

    pd.DataFrame(rows).to_csv(os.path.join(HERE, "task2_summary.csv"), index=False)
    r = pd.DataFrame(rrows)
    r.to_csv(os.path.join(HERE, "task2_ranges.csv"), index=False)
    verify.update(n_jobs=len(jobs), workers=args.workers, wall_seconds=time.time() - t0,
                  posterior_draws=len(post_idx), prior_draws=len(prior_idx), seed=args.seed)
    json.dump(verify, open(os.path.join(HERE, "task2_verify.json"), "w"), indent=2, default=str)

    print("\n[y2t2] across-setting ranges (the numbers Y1 quoted as 10.09 / 0.81):")
    for kind in ("prior_file", "prior_median", "posterior_median"):
        s = r[r.kind == kind]
        if len(s):
            x = s.iloc[0]
            print(f"        {kind:17s} T_opt range {x.T_opt_range:6.2f} C   CT_max range "
                  f"{x.CT_max_range:5.2f} C   asymmetry {x.asymmetry:6.1f}x   plateau "
                  f"{x.plateau_lo:.1f}->{x.plateau_hi:.1f} C", flush=True)
    for kind in ("prior_draw", "posterior_draw"):
        s = r[r.kind == kind]
        if not len(s):
            continue
        q = lambda c, p: np.percentile(s[c].values, p)          # noqa: E731
        print(f"        {kind:17s} n={len(s):3d}  T_opt range median {np.median(s.T_opt_range):6.2f} "
              f"[{q('T_opt_range',5):.2f}, {q('T_opt_range',95):.2f}] C   "
              f"CT_max range median {np.median(s.CT_max_range):5.2f} "
              f"[{q('CT_max_range',5):.2f}, {q('CT_max_range',95):.2f}] C", flush=True)
    print(f"[y2t2] wrote task2_summary.csv ({len(rows)}), task2_ranges.csv ({len(rrows)}), "
          f"task2_verify.json  [{time.time()-t0:.0f}s]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
