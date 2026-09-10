#!/usr/bin/env python3
"""P12 TASK 1 -- the log-likelihood along the straight lines between the fixed points.

61 points per line: 41 spanning theta_1 -> theta_2 plus 25 % extension beyond each end, i.e.
t in [-0.25, 1.25]. Lines: A->B (the prompt's), P4->A, P4->B, and A->B* where B* is the seed-2
run's maximum-likelihood sample (D1: theta_B is that run's MEDIAN and the model is nearly dead
there, so B alone may not represent the mode).

Evaluated on the 16-process pool. P11 proved the pool path returns exactly the single-process
fresh-model value for this fit (max |difference| 0.00e+00 at three points); that check is
repeated here on two points of each line before the scan is trusted.
Writes task1_profiles.csv and task1_valleys.json beside this file.
"""
import json, os, sys, time
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from common import build, fixed_points, PAYLOAD, SPECS, NAMES, ROOT, NEST                    # noqa: E402
from etcgem.calibration_multi import _gwinit, _gwloglike, _set_default_solver, gasflux_log_likelihood  # noqa: E402

T_GRID = np.round(np.linspace(-0.25, 1.25, 61), 5)


def seed2_map():
    s = np.load(os.path.join(NEST, "samples_seed2.npy")); ll = np.load(os.path.join(NEST, "logl_seed2.npy"))
    return s[int(np.nanargmax(ll))]


def main():
    fp = fixed_points(); fp["Bstar"] = seed2_map()
    lines = [("A->B", fp["A"], fp["B"]), ("P4->A", fp["P4"], fp["A"]),
             ("P4->B", fp["P4"], fp["B"]), ("A->Bstar", fp["A"], fp["Bstar"])]
    pts, meta = [], []
    for name, a, b in lines:
        for t in T_GRID:
            pts.append(a + t * (b - a)); meta.append((name, float(t)))
    solver = _set_default_solver("gurobi")
    from multiprocessing import Pool
    t0 = time.time()
    with Pool(16, initializer=_gwinit, initargs=(dict(PAYLOAD, solver=solver),)) as pool:
        vals = pool.map(_gwloglike, pts)
    wall = time.time() - t0
    # the pool-vs-fresh check, on two points of each line
    checks = []
    for name, a, b in lines:
        for t in (0.0, 0.5):
            th = a + t * (b - a); ctx, sp = build()
            fresh = float(gasflux_log_likelihood(th, ctx, sp))
            k = meta.index((name, float(np.round(t, 5))))
            checks.append(dict(line=name, t=t, pooled=vals[k], fresh=fresh, diff=abs(vals[k] - fresh)))
    md = max(c["diff"] for c in checks)
    print(f"[t1] pool vs fresh single-process on 8 points: max |difference| {md:.2e} "
          f"-> {'exact' if md < 1e-4 else 'MISMATCH'}", flush=True)
    df = pd.DataFrame([dict(line=m[0], t=m[1], logl=v) for m, v in zip(meta, vals)])
    df.to_csv(os.path.join(HERE, "task1_profiles.csv"), index=False)
    out = {"pool_vs_fresh_max_diff": md, "wall_s": round(wall, 1), "n_points": len(pts), "lines": {}}
    for name, _, _ in lines:
        d = df[df.line == name].sort_values("t"); y = d.logl.to_numpy(); x = d.t.to_numpy()
        i0 = int(np.argmin(np.abs(x - 0.0))); i1 = int(np.argmin(np.abs(x - 1.0)))
        inner = slice(min(i0, i1), max(i0, i1) + 1)
        yi, xi = y[inner], x[inner]
        kmin = int(np.argmin(yi)); ends = max(yi[0], yi[-1]); lo = min(yi[0], yi[-1])
        depth_vs_lower_end = lo - yi[kmin]      # >0 means a genuine dip below BOTH ends
        out["lines"][name] = dict(
            logl_at_start=float(y[i0]), logl_at_end=float(y[i1]), best_on_line=float(np.max(y)),
            t_of_best=float(x[int(np.argmax(y))]), min_between=float(yi[kmin]), t_of_min=float(xi[kmin]),
            valley_depth_below_lower_end=float(depth_vs_lower_end),
            monotone_between=bool(np.all(np.diff(yi) >= -1e-9) or np.all(np.diff(yi) <= 1e-9)),
            beyond_start_best=float(np.max(y[:i0 + 1])) if i0 > 0 else float(y[i0]),
            beyond_end_best=float(np.max(y[i1:])) if i1 < len(y) - 1 else float(y[i1]))
        o = out["lines"][name]
        verdict = ("VALLEY between them" if depth_vs_lower_end > 0.5 else
                   "monotone / shoulder (no dip below the lower end)")
        print(f"[t1] {name:9s} logL {o['logl_at_start']:8.2f} -> {o['logl_at_end']:8.2f}; "
              f"minimum between {o['min_between']:8.2f} at t={o['t_of_min']:.2f}; "
              f"dip below the lower end {depth_vs_lower_end:+7.2f} -> {verdict}; "
              f"best on the extended line {o['best_on_line']:.2f} at t={o['t_of_best']:.2f}", flush=True)
    json.dump(out, open(os.path.join(HERE, "task1_valleys.json"), "w"), indent=1)
    print(f"[t1] {len(pts)} evaluations in {wall/60:.1f} min on 16 processes", flush=True)
    print("[t1] done", flush=True)


if __name__ == "__main__":
    main()
