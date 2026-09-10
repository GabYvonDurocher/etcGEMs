#!/usr/bin/env python3
"""P13 addendum 1 -- why clamp is right, the knife-edge, and state-independence at the boundary.

1. At every temperature where growth <= _MASK_G, is the LP INFEASIBLE (O2 undefined) or
   FEASIBLE-NOT-GROWING (O2 finite)? If most are feasible with finite O2, the mask was discarding
   real predictions and clamp is right because it SCORES them.
2. The knife-edge: how many of P12's twelve converged endpoints park a temperature within 1 % of
   _MASK_G? If several do, the mask is an attractor.
3. Ten evaluations at p38 under the chosen scheme, FRESH MODEL each. Must be 0.0000.
"""
import json, os, sys
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from common13 import build, SPECS, p12_points, decompose, gasflux_log_likelihood, _MASK_G  # noqa: E402

CLAMP = {"support": "clamp", "weight_floor": 1.0}
NEAR = 0.01          # "within 1 % of _MASK_G"


def main():
    ctx, _sp = build(); base = dict(ctx.get("respiration") or {})
    pts, _ = p12_points()

    # ---------- 1 + 2 ----------
    rows, per_T = [], []
    for k, th in pts.items():
        ctx["respiration"] = dict(base)
        d = decompose(th, ctx, SPECS)
        g = np.asarray(d["growth"], float); o2 = np.asarray(d["o2"], float)
        dead = g <= _MASK_G
        infeas = dead & ~np.isfinite(o2)
        feas_ng = dead & np.isfinite(o2) & (o2 > 0)
        near = np.abs(g - _MASK_G) <= NEAR * _MASK_G
        for T, gg, oo, dd in zip(d["T"], g, o2, dead):
            if dd:
                per_T.append(dict(key=k, T=float(T), growth=float(gg), o2=float(oo),
                                  status="INFEASIBLE" if not np.isfinite(oo) else "FEASIBLE-NOT-GROWING"))
        rows.append(dict(key=k, n_dead=int(dead.sum()), n_infeasible=int(infeas.sum()),
                         n_feasible_not_growing=int(feas_ng.sum()),
                         o2_at_feasible_not_growing=";".join(f"{v:.3f}" for v in o2[feas_ng]),
                         n_within_1pct_of_mask=int(near.sum()),
                         min_rel_dist_to_mask=float(np.min(np.abs(g - _MASK_G)) / _MASK_G)))
        print(f"[a1] {k:20s} dead {rows[-1]['n_dead']:2d}  infeasible {rows[-1]['n_infeasible']:2d}  "
              f"feasible-not-growing {rows[-1]['n_feasible_not_growing']:2d}  "
              f"within 1% of mask {rows[-1]['n_within_1pct_of_mask']:2d}", flush=True)
    R = pd.DataFrame(rows); R.to_csv(os.path.join(HERE, "addendum1_support_status.csv"), index=False)
    P = pd.DataFrame(per_T); P.to_csv(os.path.join(HERE, "addendum1_dead_temperatures.csv"), index=False)
    pd.set_option("display.width", 240)
    print("\n[a1] every temperature with growth <= _MASK_G, classified")
    print(P.round(6).to_string(index=False))
    tot_d, tot_i, tot_f = int(R.n_dead.sum()), int(R.n_infeasible.sum()), int(R.n_feasible_not_growing.sum())
    print(f"\n[a1] TOTALS across the twelve endpoints: {tot_d} dead temperatures = "
          f"{tot_i} INFEASIBLE + {tot_f} FEASIBLE-NOT-GROWING "
          f"({100*tot_f/max(tot_d,1):.0f} % carry a real O2 prediction the mask discarded)")
    nk = int((R.n_within_1pct_of_mask > 0).sum())
    print(f"[a1] KNIFE-EDGE: {nk} of {len(R)} endpoints park a temperature within 1 % of _MASK_G")
    print(R[["key", "n_within_1pct_of_mask", "min_rel_dist_to_mask"]]
          .sort_values("min_rel_dist_to_mask").round(6).to_string(index=False))

    # ---------- 3 ----------
    print("\n[a1] state-independence at the boundary: ten FRESH-MODEL evaluations at p38 under clamp",
          flush=True)
    vals = []
    for i in range(10):
        c2, s2 = build()
        c2["respiration"] = dict(dict(c2.get("respiration") or {}), **CLAMP)
        v = float(gasflux_log_likelihood(pts["p38(b22)"], c2, s2))
        vals.append(v); print(f"[a1]   fresh build {i+1:2d}: {v:.10f}", flush=True)
    vals = np.array(vals)
    spread = float(vals.max() - vals.min())
    print(f"[a1]   spread = {spread:.10f}   {'PASS (0.0000)' if spread < 1e-4 else '*** FAIL ***'}")
    json.dump(dict(n_dead=tot_d, n_infeasible=tot_i, n_feasible_not_growing=tot_f,
                   frac_feasible=tot_f / max(tot_d, 1), n_endpoints_on_knife_edge=nk,
                   clamp_fresh_values=vals.tolist(), clamp_fresh_spread=spread),
              open(os.path.join(HERE, "addendum1_summary.json"), "w"), indent=1)
    print("[a1] done", flush=True)


if __name__ == "__main__":
    main()
