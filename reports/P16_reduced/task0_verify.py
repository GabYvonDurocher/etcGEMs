#!/usr/bin/env python3
"""P14 TASK 0 -- re-confirm P13's state-independence result survived the Y3/P13 merge.

Ten evaluations at p38 under the clamp support read from the strain config, FRESH MODEL each.
The spread must be 0.0000000000; anything else means something did not survive the merge.
"""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
P13 = os.path.abspath(os.path.join(HERE, "..", "P13_support"))
if P13 not in sys.path: sys.path.insert(0, P13)
from common13 import build, p12_points, gasflux_log_likelihood, NAMES   # noqa: E402


def main():
    pts, _ = p12_points(); th = pts["p38(b22)"]
    vals = []
    for i in range(10):
        ctx, sp = build()
        r = ctx.get("respiration") or {}
        if i == 0:
            print(f"[t0] config in force: support={r.get('support')!r} "
                  f"weight_floor={r.get('weight_floor')!r} tiebreak={r.get('tiebreak')!r} "
                  f"log_o2_floor={r.get('log_o2_floor')!r} alive_soft_growth={r.get('alive_soft_growth')!r}",
                  flush=True)
        v = float(gasflux_log_likelihood(th, ctx, sp)); vals.append(v)
        print(f"[t0]   fresh build {i+1:2d}: {v:.10f}", flush=True)
    a = np.array(vals); spread = float(a.max() - a.min())
    print(f"[t0] spread = {spread:.10f}   {'PASS' if spread < 1e-9 else '*** FAIL ***'}")
    print(f"[t0] value  = {a[0]:.4f}  (P13 measured -9.9894)")
    json.dump(dict(values=vals, spread=spread, expected=-9.9894),
              open(os.path.join(HERE, "task0_state.json"), "w"), indent=1)
    print("[t0] done", flush=True)


if __name__ == "__main__":
    main()
