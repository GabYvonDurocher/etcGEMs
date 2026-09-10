#!/usr/bin/env python3
"""P13 TASK 1 -- choose the bounded support form by testing three, not by assuming one.

Schemes, all on the RESPIRATION term only, selected by the new `respiration.support` core option
(default "current", inert):
  (i)   impute  -- every temperature scored; O2 imputed at `o2_epsilon` where the model is dead
                   (growth <= _MASK_G = 1e-4) or the LP returned none; full penalty.
  (ii)  clamp   -- the ramp's form kept but floored at `weight_floor` = 1.0, i.e. no discount;
                   mask retained for a missing O2 only.
  (iii) current -- as is.

The growth term is scheme-independent (it is linear and the weight never touches it), so it is
computed once per point and the respiration term is recovered exactly as total - growth.
"""
import json, os, sys
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from common13 import (build, SPECS, NAMES, decompose, p12_points, fixed_points,   # noqa: E402
                      gasflux_log_likelihood)

SCHEMES = {"current": {}, "clamp": {"support": "clamp", "weight_floor": 1.0},
           "impute": {"support": "impute", "o2_epsilon": 1e-9}}
EPSILONS = (1e-6, 1e-9, 1e-12)


def score(ctx, base, th, over):
    ctx["respiration"] = dict(base, **over)
    return float(gasflux_log_likelihood(th, ctx, SPECS))


def main():
    ctx, _sp = build()
    base = dict(ctx.get("respiration") or {})
    pts, _ = p12_points()
    pts["thetaA_P11median"] = fixed_points()["A"]          # the 13th point the prompt names
    rows = []
    for k, th in pts.items():
        ctx["respiration"] = dict(base)                      # growth term under the default path
        d = decompose(th, ctx, SPECS)
        gterm = float(np.sum(d["growth_term"]))
        r = dict(key=k, growth_term=gterm, peak_growth=float(np.max(d["growth"])))
        for name, over in SCHEMES.items():
            tot = score(ctx, base, th, over)
            r[f"logl_{name}"] = tot
            r[f"resp_{name}"] = tot - gterm
        r["d_clamp"] = r["logl_clamp"] - r["logl_current"]
        r["d_impute"] = r["logl_impute"] - r["logl_current"]
        rows.append(r)
        print(f"[t1] {k:20s} current {r['logl_current']:10.3f}  clamp {r['logl_clamp']:10.3f}  "
              f"impute {r['logl_impute']:12.3f}", flush=True)
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(HERE, "task1_schemes.csv"), index=False)
    pd.set_option("display.width", 250)
    print("\n[t1] totals and per-term, by scheme")
    print(df[["key", "peak_growth", "growth_term", "resp_current", "resp_clamp", "resp_impute",
              "logl_current", "logl_clamp", "logl_impute", "d_clamp", "d_impute"]]
          .sort_values("logl_current", ascending=False).round(3).to_string(index=False))

    # ---- the decisive number: the live-dead gap ----
    live = df[df.key != "B(b3)"]
    dead = df[df.key == "B(b3)"].iloc[0]
    print("\n[t1] LIVE-DEAD GAP (best live point minus b3)")
    gaps = {}
    for name in SCHEMES:
        best = live.loc[live[f"logl_{name}"].idxmax()]
        gaps[name] = float(best[f"logl_{name}"] - dead[f"logl_{name}"])
        print(f"[t1]   {name:8s}: best live {best.key} {best[f'logl_{name}']:10.3f}  "
              f"b3 {dead[f'logl_{name}']:12.3f}  GAP {gaps[name]:12.3f}")

    # ---- epsilon sensitivity for impute ----
    print("\n[t1] epsilon sensitivity of `impute` (how much of the gap is the constant?)")
    eps_rows = []
    for e in EPSILONS:
        b = score(ctx, base, pts["p38(b22)"], {"support": "impute", "o2_epsilon": e})
        d3 = score(ctx, base, pts["B(b3)"], {"support": "impute", "o2_epsilon": e})
        eps_rows.append(dict(epsilon=e, p38=b, b3=d3, gap=b - d3))
        print(f"[t1]   eps {e:.0e}: p38 {b:10.3f}  b3 {d3:14.3f}  gap {b - d3:14.3f}")
    pd.DataFrame(eps_rows).to_csv(os.path.join(HERE, "task1_epsilon.csv"), index=False)
    json.dump(dict(gaps=gaps, epsilon=eps_rows,
                   gap_current=gaps["current"], gap_clamp=gaps["clamp"], gap_impute=gaps["impute"]),
              open(os.path.join(HERE, "task1_gaps.json"), "w"), indent=1)
    print("\n[t1] done", flush=True)


if __name__ == "__main__":
    main()
