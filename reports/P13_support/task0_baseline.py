#!/usr/bin/env python3
"""P13 TASK 0 -- the baseline under the CURRENT likelihood, single process, fresh model.

Every later comparison in P13 is against these numbers, so they are measured here once, from
P12's committed converged endpoints, and committed.
"""
import json, os, sys
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from common13 import build, SPECS, NAMES, decompose, p12_points   # noqa: E402


def main():
    ctx, _sp = build()
    pts, meta = p12_points()
    rows = []
    for k, th in pts.items():
        d = decompose(th, ctx, SPECS)
        g = np.asarray(d["growth"], float)
        rows.append(dict(key=k, logl=float(d["logl"]),
                         growth_term=float(np.sum(d["growth_term"])),
                         resp_term=float(np.sum(d["resp_term"])),
                         peak_growth=float(g.max()),
                         n_scored=int((np.asarray(d["weight"], float) > 0).sum()),
                         mean_weight=float(np.asarray(d["weight"], float)[np.asarray(d["weight"], float) > 0].mean())
                         if (np.asarray(d["weight"], float) > 0).any() else float("nan"),
                         dTm=float(dict(zip(NAMES, th))["dTm"]),
                         dTopt=float(dict(zip(NAMES, th))["dTopt"])))
        print(f"[t0] {k:16s} logL {rows[-1]['logl']:9.3f}  growth {rows[-1]['growth_term']:9.3f}  "
              f"resp {rows[-1]['resp_term']:9.3f}  peak growth {rows[-1]['peak_growth']:.3f}", flush=True)
    df = pd.DataFrame(rows).sort_values("logl", ascending=False)
    df.to_csv(os.path.join(HERE, "task0_baseline.csv"), index=False)
    best = df.iloc[0]; dead = df[df.key == "B(b3)"].iloc[0]
    gap = float(best.logl - dead.logl)
    print(f"\n[t0] live basin best: {best.key} at {best.logl:.3f}")
    print(f"[t0] dead basin b3  : {dead.logl:.3f}")
    print(f"[t0] LIVE-DEAD GAP under CURRENT = {gap:.3f}")
    json.dump(dict(best_key=str(best.key), best_logl=float(best.logl), b3_logl=float(dead.logl),
                   live_dead_gap=gap,
                   p38=float(df[df.key == "p38(b22)"].logl.iloc[0]),
                   A=float(df[df.key == "A(b20)"].logl.iloc[0])),
              open(os.path.join(HERE, "task0_baseline.json"), "w"), indent=1)
    print("[t0] done", flush=True)


if __name__ == "__main__":
    main()
