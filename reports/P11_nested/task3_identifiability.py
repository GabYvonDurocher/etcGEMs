#!/usr/bin/env python3
"""P11 TASK 3 -- one line scan per parameter through the NEW posterior median, +/- 1 POSTERIOR
sd at 0.05 sd, fresh model per evaluation, single process; classified FLAT / WALL-BOUNDED /
GRADIENT-DETERMINED by the rule in DECISIONS D3 (written before the posterior existed).
Writes task3_identifiability.csv and task3_lines.csv beside this file."""
import json, os, sys, time
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src")); sys.path.insert(0, os.path.join(ROOT, "reports", "P6_convergence")); sys.path.insert(0, os.path.join(ROOT, "reports", "P9_surface")); sys.path.insert(0, HERE); os.chdir(ROOT)
from etcgem.calibration_multi import gasflux_log_likelihood, build_gasflux_specs   # noqa: E402
from p6_fits import FITS                                                          # noqa: E402
from task1_scan import build, STEPS                                               # noqa: E402
from task3_posterior import equal_weight                                          # noqa: E402
FLAT_RANGE, WALL_FRAC = 1.0, 0.25       # D3


def main(tag="main"):
    fit = [f for f in FITS if f[0] == "D_NLDM"][0]
    specs = build_gasflux_specs({"use_etc": False, "fit_clearance": True}); names = [s.name for s in specs]
    post, summ, _ = equal_weight(tag)
    centre = np.median(post, axis=0); psd = post.std(axis=0)      # posterior sd in sampled space
    rows, pts = [], []
    for j, s in enumerate(specs):
        vals = []; t0 = time.time()
        for st in STEPS:
            ctx, sp = build(fit); th = centre.copy(); th[j] = centre[j] + st * psd[j]
            v = gasflux_log_likelihood(th, ctx, sp); vals.append(v)
            pts.append(dict(param=s.name, step_posterior_sd=float(st), logL=float(v)))
        vals = np.array(vals); fin = np.isfinite(vals); d1 = np.diff(vals[fin])
        rng_ = float(vals[fin].max() - vals[fin].min()); jump = float(np.max(np.abs(d1))) if len(d1) else np.nan
        frac = jump / rng_ if rng_ > 0 else np.nan
        cls = "FLAT" if rng_ < FLAT_RANGE else ("WALL-BOUNDED" if frac > WALL_FRAC else "GRADIENT-DETERMINED")
        rows.append(dict(param=s.name, posterior_sd_sampled=float(psd[j]), range_logL=rng_, max_step=jump,
                         max_step_frac=frac, sign_changes=int(np.sum(np.sign(d1[1:]) * np.sign(d1[:-1]) < 0)) if len(d1) > 1 else 0,
                         classification=cls, s_per_eval=round((time.time() - t0) / len(STEPS), 2)))
        print(f"[ident] {s.name:16s} posterior sd {psd[j]:8.4f}  range {rng_:8.3f}  largest step {jump:7.3f} ({100*frac if rng_>0 else float('nan'):5.1f} %)  -> {cls}", flush=True)
    df = pd.DataFrame(rows); df.to_csv(os.path.join(HERE, "task3_identifiability.csv"), index=False)
    pd.DataFrame(pts).to_csv(os.path.join(HERE, "task3_lines.csv"), index=False)
    for c in ("GRADIENT-DETERMINED", "WALL-BOUNDED", "FLAT"):
        print(f"[ident] {c}: {df[df.classification==c].param.tolist()}", flush=True)
    print("[ident] done", flush=True)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "main")
