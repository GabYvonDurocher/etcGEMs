#!/usr/bin/env python3
"""P12 TASK 2c -- continue the representative endpoints to ACTUAL convergence (D5).

The screen gave every start ~one Powell sweep (600 evaluations, 96/100 capped), so its endpoints
are not local minima. This continues a representative set, warm-started from the endpoints
already paid for, with a 3,000-evaluation cap and tighter tolerances, and RECORDS THE TERMINATION
REASON so "converged" is a measurement rather than an assumption.

Representatives are chosen by basin, with the b3 fix: the screen's picker tested `"B" in key`,
which matched "Bstar", so theta_B's own basin was silently omitted from the barrier test.

imap_unordered with incremental writes (D5), so a straggler cannot cost the rest.
"""
import json, os, sys, time
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from common import PAYLOAD, NAMES                                        # noqa: E402
from etcgem.calibration_multi import _gwinit, _set_default_solver        # noqa: E402

MAXFEV = 3000
XTOL = FTOL = 1e-4
OUT = os.path.join(HERE, "task2c_converged.csv")


def _run(arg):
    key, x0 = arg
    import numpy as _np
    from scipy.optimize import minimize
    from etcgem.calibration_multi import _gwnegpost, _gwlogprob, _GSPECS, gasflux_log_likelihood, _GCTX
    t0 = time.time()
    try:
        res = minimize(_gwnegpost, _np.asarray(x0, float), method="Powell",
                       options=dict(maxfev=MAXFEV, xtol=XTOL, ftol=FTOL))
        x = _np.asarray(res.x, float)
        return dict(key=key, ok=True, x=x.tolist(), logpost=float(_gwlogprob(x)),
                    logl=float(gasflux_log_likelihood(x, _GCTX, _GSPECS)), nfev=int(res.nfev),
                    success=bool(res.success), message=str(res.message)[:90],
                    capped=bool(res.nfev >= MAXFEV), wall_s=round(time.time() - t0, 1))
    except Exception as e:
        return dict(key=key, ok=False, x=list(map(float, x0)), logpost=float("-inf"),
                    logl=float("-inf"), nfev=0, success=False, message=f"{type(e).__name__}: {e}"[:90],
                    capped=False, wall_s=round(time.time() - t0, 1))


def representatives():
    d = pd.read_csv(os.path.join(HERE, "task2_endpoints_clustered.csv"))
    xc = [f"x_{n}" for n in NAMES]
    reps, seen = {}, set()

    def add(key, row):
        if int(row.basin) in seen:
            return
        seen.add(int(row.basin)); reps[key] = row[xc].to_numpy(float)

    for _, r in d.nlargest(6, "logl").iterrows():
        tag = r.kind if r.kind != "prior" else f"p{int(r.idx)}"
        add(f"{tag}(b{int(r.basin)})", r)
    # every basin holding a named fixed point -- exact match, not substring (the b3 fix)
    for b in sorted(d.basin.unique()):
        g = d[d.basin == b]
        holds = sorted(set(g.kind) - {"prior"})
        if holds:
            add(f"{'/'.join(holds)}(b{b})", g.loc[g.logl.idxmax()])
    # the largest basins by membership, then the worst endpoint
    for b, _ in d.basin.value_counts().head(4).items():
        g = d[d.basin == b]
        add(f"big(b{b},n={len(g)})", g.loc[g.logl.idxmax()])
    add(f"worst(b{int(d.loc[d.logl.idxmin()].basin)})", d.loc[d.logl.idxmin()])
    return reps


def main():
    reps = representatives()
    keys = list(reps)
    print(f"[t2c] {len(keys)} representatives, Powell maxfev {MAXFEV}, xtol/ftol {XTOL}", flush=True)
    for k in keys:
        print(f"[t2c]   {k}", flush=True)
    solver = _set_default_solver("gurobi")
    from multiprocessing import Pool
    t0 = time.time(); rows = []
    with Pool(min(16, len(keys)), initializer=_gwinit, initargs=(dict(PAYLOAD, solver=solver),)) as pool:
        for r in pool.imap_unordered(_run, [(k, reps[k]) for k in keys]):
            rows.append(r)
            pd.DataFrame(rows).to_csv(OUT, index=False)
            print(f"[t2c] {r['key']:22s} logL {r['logl']:9.3f}  nfev {r['nfev']:5d}  "
                  f"{'CAPPED' if r['capped'] else 'converged'}  ({r['wall_s']/60:.1f} min)  "
                  f"[{len(rows)}/{len(keys)}]", flush=True)
    df = pd.DataFrame(rows)
    for n, c in zip(NAMES, range(len(NAMES))):
        df[f"x_{n}"] = [r["x"][c] for r in rows]
    df.drop(columns=["x"]).to_csv(OUT, index=False)
    scr = pd.read_csv(os.path.join(HERE, "task2_endpoints_clustered.csv"))
    pd.set_option("display.width", 220)
    print("\n[t2c] converged representatives")
    print(df[["key", "logl", "nfev", "success", "capped", "wall_s"]].sort_values("logl", ascending=False)
          .round(3).to_string(index=False))
    print(f"\n[t2c] converged (not capped): {int((~df.capped).sum())} of {len(df)}")
    json.dump(dict(maxfev=MAXFEV, xtol=XTOL, n=len(df), n_converged=int((~df.capped).sum()),
                   wall_h=round((time.time() - t0) / 3600, 2)),
              open(os.path.join(HERE, "task2c_meta.json"), "w"), indent=1)
    print(f"[t2c] {(time.time()-t0)/3600:.2f} h")
    print("[t2c] done", flush=True)


if __name__ == "__main__":
    main()
