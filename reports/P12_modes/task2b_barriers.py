#!/usr/bin/env python3
"""P12 TASK 2b -- barrier tests between representative endpoints (D5).

A basin is defined by the absence of a barrier between two points, not by a clustering threshold.
This test therefore measures basin identity DIRECTLY, and unlike the clustering it does not
require the endpoints to be converged: a hump between two points separates them whatever their
provenance. Conversely a straight chord finding no hump is only WEAK evidence of one basin (D3),
so "connected" here means "not separated along the straight line", and is reported as such.

41 points per pair on t in [0, 1]. Barrier if the interior minimum falls more than 0.5
log-likelihood units below the LOWER of the two endpoints -- TASK 1's rule, unchanged.

Uses imap_unordered with incremental writes (D5): the run is resumable and a straggler can be
dropped without losing the rest.
"""
import json, os, sys, time
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from common import PAYLOAD, NAMES                                              # noqa: E402
from etcgem.calibration_multi import _gwinit, _gwloglike, _set_default_solver  # noqa: E402

NPTS = 41
BARRIER = 0.5
OUT = os.path.join(HERE, "task2b_points.csv")


def representatives():
    d = pd.read_csv(os.path.join(HERE, "task2_endpoints_clustered.csv"))
    xc = [f"x_{n}" for n in NAMES]
    reps = {}
    # the six best endpoints overall
    for _, r in d.nlargest(6, "logl").iterrows():
        tag = r.kind if r.kind != "prior" else f"p{int(r.idx)}"
        reps[f"{tag}(b{int(r.basin)})"] = r[xc].to_numpy(float)
    # the biggest cluster, the two fixed-point basins not already in, and the worst basin
    d10 = d[d.basin == 10]; reps[f"big(b10,n={len(d10)})"] = d10.loc[d10.logl.idxmax(), xc].to_numpy(float)
    for b in sorted(d.basin.unique()):
        g = d[d.basin == b]
        holds = set(g.kind) - {"prior"}
        if holds and not any(h in k for k in reps for h in holds):
            reps[f"{'/'.join(sorted(holds))}(b{b})"] = g.loc[g.logl.idxmax(), xc].to_numpy(float)
    worst = d.loc[d.logl.idxmin()]
    reps[f"worst(b{int(worst.basin)})"] = worst[xc].to_numpy(float)
    return reps


def main():
    reps = representatives()
    keys = list(reps)
    print(f"[t2b] {len(keys)} representatives: {keys}", flush=True)
    pairs = [(i, j) for i in range(len(keys)) for j in range(i + 1, len(keys))]
    grid = np.linspace(0.0, 1.0, NPTS)
    pts, meta = [], []
    for i, j in pairs:
        a, b = reps[keys[i]], reps[keys[j]]
        for t in grid:
            pts.append(a + t * (b - a)); meta.append((i, j, float(t)))
    print(f"[t2b] {len(pairs)} pairs x {NPTS} points = {len(pts)} evaluations", flush=True)
    solver = _set_default_solver("gurobi")
    from multiprocessing import Pool
    t0 = time.time(); vals = [None] * len(pts); done = 0
    with Pool(16, initializer=_gwinit, initargs=(dict(PAYLOAD, solver=solver),)) as pool:
        for k, v in pool.imap_unordered(_evalone, list(enumerate(pts)), chunksize=4):
            vals[k] = v; done += 1
            if done % 200 == 0:
                pd.DataFrame([dict(i=m[0], j=m[1], t=m[2], logl=x) for m, x in zip(meta, vals)
                              if x is not None]).to_csv(OUT, index=False)
                print(f"[t2b]   {done}/{len(pts)} ({(time.time()-t0)/60:.1f} min)", flush=True)
    wall = time.time() - t0
    df = pd.DataFrame([dict(i=m[0], j=m[1], t=m[2], logl=v) for m, v in zip(meta, vals)])
    df.to_csv(OUT, index=False)
    rows = []
    import itertools
    parent = list(range(len(keys)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x

    for i, j in pairs:
        d = df[(df.i == i) & (df.j == j)].sort_values("t")
        y = d.logl.to_numpy()
        lo = min(y[0], y[-1]); depth = lo - y.min()
        sep = depth > BARRIER
        rows.append(dict(a=keys[i], b=keys[j], logl_a=y[0], logl_b=y[-1], min_between=y.min(),
                         t_of_min=float(d.t.to_numpy()[int(np.argmin(y))]),
                         depth_below_lower_end=depth, separated=sep))
        if not sep:
            pi, pj = find(i), find(j)
            if pi != pj:
                parent[pi] = pj
    res = pd.DataFrame(rows)
    res.to_csv(os.path.join(HERE, "task2b_barriers.csv"), index=False)
    pd.set_option("display.width", 220)
    print("\n[t2b] pairs SEPARATED by a barrier (> %.1f units below the lower end):" % BARRIER)
    s = res[res.separated].sort_values("depth_below_lower_end", ascending=False)
    print(s.round(3).to_string(index=False) if len(s) else "   NONE")
    print(f"\n[t2b] {int(res.separated.sum())} of {len(res)} pairs separated")
    comp = {}
    for k in range(len(keys)):
        comp.setdefault(find(k), []).append(keys[k])
    print(f"\n[t2b] CONNECTED COMPONENTS under the straight-line test: {len(comp)}")
    for n, (_, members) in enumerate(comp.items(), 1):
        print(f"[t2b]   component {n}: {members}")
    json.dump(dict(n_representatives=len(keys), keys=keys, barrier_units=BARRIER, npts=NPTS,
                   n_pairs=len(pairs), n_separated=int(res.separated.sum()),
                   n_components=len(comp), components=[v for v in comp.values()],
                   wall_min=round(wall / 60, 1)),
              open(os.path.join(HERE, "task2b_summary.json"), "w"), indent=1)
    print(f"\n[t2b] {len(pts)} evaluations in {wall/60:.1f} min")
    print("[t2b] done", flush=True)


def _evalone(arg):
    k, x = arg
    return k, float(_gwloglike(np.asarray(x, float)))


if __name__ == "__main__":
    main()
