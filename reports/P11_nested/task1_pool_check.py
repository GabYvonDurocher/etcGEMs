#!/usr/bin/env python3
"""P11 TASK 1 -- the pool path returns the same number as a single-process fresh evaluation.
At P4's MAP and two other points, `_gwloglike` through a 16-worker pool (the path dynesty uses)
against `gasflux_log_likelihood` on a freshly built provider in this process. Writes
task1_pool_check.json beside this file."""
import json, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src")); sys.path.insert(0, HERE); os.chdir(ROOT)
from etcgem.calibration_multi import _gwinit, _gwloglike, _set_default_solver, gasflux_log_likelihood, _build_gasflux_ctx  # noqa: E402
from run_nested import PAYLOAD                                                                 # noqa: E402


def main():
    th0 = np.array(json.load(open(os.path.join(ROOT, "reports", "P9_surface", "task1_meta.json")))["theta0"])
    pts = [th0, th0 + 0.05, th0 - 0.10]
    single = []
    for th in pts:
        ctx, sp = _build_gasflux_ctx(**PAYLOAD)          # a fresh provider per evaluation
        single.append(float(gasflux_log_likelihood(th, ctx, sp)))
    solver = _set_default_solver("gurobi")
    from multiprocessing import Pool
    t0 = time.time()
    with Pool(16, initializer=_gwinit, initargs=(dict(PAYLOAD, solver=solver),)) as pool:
        pooled = list(pool.map(_gwloglike, pts))
        t1 = time.time(); many = list(pool.map(_gwloglike, [th0 + 0.01 * i for i in range(32)])); t_many = time.time() - t1
    d = [abs(a - b) for a, b in zip(single, pooled)]
    out = dict(single_process_fresh=single, pooled=pooled, abs_diff=d, max_abs_diff=max(d),
               within_1e_4=bool(max(d) < 1e-4), s_per_eval_pooled_wall=round(t_many / 32, 3),
               s_per_eval_effective_16proc=round(t_many / 32, 3), n_finite=int(np.isfinite(many).sum()))
    json.dump(out, open(os.path.join(HERE, "task1_pool_check.json"), "w"), indent=1)
    print(f"[pool] single-process fresh {np.round(single,4).tolist()} | pooled {np.round(pooled,4).tolist()} | "
          f"max |diff| {max(d):.2e} -> within the 1e-4 P7 measured: {max(d) < 1e-4}", flush=True)
    print(f"[pool] 32 evaluations over 16 workers in {t_many:.1f} s = {t_many/32:.3f} s per evaluation of wall clock", flush=True)
    print("[pool] done", flush=True)


if __name__ == "__main__":
    main()
