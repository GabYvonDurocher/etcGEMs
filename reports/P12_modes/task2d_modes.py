#!/usr/bin/env python3
"""P12 TASK 2d -- the mode count, under D7's rule, on TASK 2c's CONVERGED endpoints.

D7 (written before 2c reported): two endpoints are SEPARATE BASINS only if the barrier on their
chord exceeds the threshold AND both are local optima by 2c's termination reason (Powell stopped
on tolerance, not on the 3,000-evaluation cap). 1-5 units is sub-structure of one basin -- the
kink scale P9/P10 measured. Below 1 is noise. Counted at 3, 5 and 8; headline 5.

Also, per addendum 2: the ceiling test against P11's main-run best sample (-7.3964), and every
endpoint's peak predicted growth against the observed 2.076 /h plus its no-discount (ii') score.
"""
import json, os, sys, time
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from common import PAYLOAD, NAMES, build, SPECS, decompose                    # noqa: E402
from etcgem.calibration_multi import _gwinit, _gwloglike, _set_default_solver  # noqa: E402
from addendum1_weight import schemes                                           # noqa: E402

NPTS = 41
THRESHOLDS = (3.0, 5.0, 8.0)
HEADLINE = 5.0
P11_MAIN_BEST = -7.3964
PEAK_OBS = 2.076


def _evalone(arg):
    k, x = arg
    return k, float(_gwloglike(np.asarray(x, float)))


def components(keys, res, thresh, eligible):
    """union-find over pairs that are NOT separated at `thresh`. Only endpoints that are
    demonstrated local optima (`eligible`) can found a basin; the rest are attached to whichever
    basin they are monotonically downhill of, and reported separately."""
    parent = {k: k for k in keys}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    for _, r in res.iterrows():
        if r.depth_below_lower_end <= thresh:
            a, b = find(r.a), find(r.b)
            if a != b:
                parent[a] = b
    comp = {}
    for k in keys:
        comp.setdefault(find(k), []).append(k)
    return list(comp.values())


def main():
    c = pd.read_csv(os.path.join(HERE, "task2c_converged.csv"))
    xc = [f"x_{n}" for n in NAMES]
    keys = c.key.tolist()
    X = {r.key: r[xc].to_numpy(float) for _, r in c.iterrows()}
    capped = dict(zip(c.key, c.capped))
    print(f"[t2d] {len(keys)} converged endpoints; local optima (not capped): "
          f"{int((~c.capped).sum())} of {len(c)}", flush=True)

    # ---- barrier scan on the converged points ----
    pairs = [(keys[i], keys[j]) for i in range(len(keys)) for j in range(i + 1, len(keys))]
    grid = np.linspace(0.0, 1.0, NPTS)
    pts, meta = [], []
    for a, b in pairs:
        for t in grid:
            pts.append(X[a] + t * (X[b] - X[a])); meta.append((a, b, float(t)))
    print(f"[t2d] {len(pairs)} pairs x {NPTS} = {len(pts)} evaluations", flush=True)
    solver = _set_default_solver("gurobi")
    from multiprocessing import Pool
    t0 = time.time(); vals = [None] * len(pts); done = 0
    with Pool(16, initializer=_gwinit, initargs=(dict(PAYLOAD, solver=solver),)) as pool:
        for k, v in pool.imap_unordered(_evalone, list(enumerate(pts)), chunksize=4):
            vals[k] = v; done += 1
            if done % 400 == 0:
                print(f"[t2d]   {done}/{len(pts)} ({(time.time()-t0)/60:.1f} min)", flush=True)
    df = pd.DataFrame([dict(a=m[0], b=m[1], t=m[2], logl=v) for m, v in zip(meta, vals)])
    df.to_csv(os.path.join(HERE, "task2d_points.csv"), index=False)
    rows = []
    for a, b in pairs:
        d = df[(df.a == a) & (df.b == b)].sort_values("t"); y = d.logl.to_numpy()
        lo = min(y[0], y[-1]); depth = lo - y.min()
        monotone_end = bool(abs(depth) < 1e-9 and np.argmin(y) in (0, len(y) - 1))
        rows.append(dict(a=a, b=b, logl_a=y[0], logl_b=y[-1], min_between=float(y.min()),
                         t_of_min=float(d.t.to_numpy()[int(np.argmin(y))]),
                         depth_below_lower_end=float(depth), monotone_to_lower=monotone_end))
    res = pd.DataFrame(rows); res.to_csv(os.path.join(HERE, "task2d_barriers.csv"), index=False)

    # ---- D7 rule ----
    eligible = [k for k in keys if not capped[k]]
    print(f"\n[t2d] endpoints eligible to FOUND a basin (local optima by termination reason): "
          f"{eligible if eligible else 'NONE'}", flush=True)
    counts = {}
    for th in THRESHOLDS:
        comps = components(keys, res, th, eligible)
        founded = [g for g in comps if any(k in eligible for k in g)]
        counts[th] = dict(n_components=len(comps), n_with_optimum=len(founded),
                          components=[sorted(g) for g in comps])
        print(f"[t2d] threshold {th:.0f}: {len(comps)} components, {len(founded)} containing a "
              f"demonstrated local optimum", flush=True)
        for n, g in enumerate(comps, 1):
            print(f"[t2d]     {n}: {sorted(g)}", flush=True)

    # ---- addendum 2 items 3 and 4 ----
    print(f"\n[t2d] CEILING TEST against P11 main-run best sample {P11_MAIN_BEST:+.4f}")
    best = c.loc[c.logl.idxmax()]
    print(f"[t2d]   best 2c endpoint: {best.key} at {best.logl:+.4f}  "
          f"({'REACHES/BEATS' if best.logl >= P11_MAIN_BEST else 'BELOW'} it by "
          f"{abs(best.logl - P11_MAIN_BEST):.4f})")
    print(f"[t2d]   endpoints reaching -7.40: {int((c.logl >= P11_MAIN_BEST).sum())} of {len(c)}")

    ctx, _sp = build()
    sc = []
    for _, r in c.iterrows():
        th = r[xc].to_numpy(float)
        s = schemes(th, ctx, SPECS); d = decompose(th, ctx, SPECS)
        pk = float(np.max(d["growth"]))
        sc.append(dict(key=r.key, logl=r.logl, capped=bool(r.capped), nfev=int(r.nfev),
                       peak_growth=pk, peak_frac=pk / PEAK_OBS, dead_model=bool(pk / PEAK_OBS < 0.5),
                       logl_nodiscount=s["total_iiprime"],
                       discount_credit=s["resp_i"] - s["resp_nodiscount"],
                       growth_term=s["growth_term"], resp_term=s["resp_i"],
                       dTm=float(r[f"x_dTm"]) if f"x_dTm" in r else float("nan"),
                       dTopt=float(r[f"x_dTopt"]) if f"x_dTopt" in r else float("nan")))
        print(f"[t2d]   scored {r.key}", flush=True)
    s = pd.DataFrame(sc).sort_values("logl", ascending=False)
    s.to_csv(os.path.join(HERE, "task2d_endpoint_scores.csv"), index=False)
    pd.set_option("display.width", 240)
    print("\n[t2d] per endpoint: deadness, the no-discount rescore, and dTm")
    print(s[["key", "logl", "capped", "nfev", "peak_growth", "peak_frac", "dead_model",
             "logl_nodiscount", "discount_credit", "dTm", "dTopt"]].round(3).to_string(index=False))
    dead = s[s.dead_model].key.tolist()
    print(f"\n[t2d] DEAD-MODEL endpoints (peak predicted growth < 50 % of {PEAK_OBS}): "
          f"{dead if dead else 'none'}")
    json.dump(dict(thresholds={str(k): v for k, v in counts.items()}, headline=HEADLINE,
                   n_eligible=len(eligible), eligible=eligible,
                   p11_main_best=P11_MAIN_BEST, best_2c=float(c.logl.max()),
                   best_2c_key=str(best.key), n_reaching=int((c.logl >= P11_MAIN_BEST).sum()),
                   dead_endpoints=dead, wall_min=round((time.time() - t0) / 60, 1)),
              open(os.path.join(HERE, "task2d_summary.json"), "w"), indent=1)
    print("[t2d] done", flush=True)


if __name__ == "__main__":
    main()
