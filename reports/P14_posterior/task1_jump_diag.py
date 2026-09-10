#!/usr/bin/env python3
"""P14 TASK 1 -- what the four residual JUMPs ARE.

For each line that tested JUMP, bisect to the finest interval reached and decompose the persistent
step: growth term vs respiration term, and the per-temperature O2 across it. A jump with the same
support set and unchanged growth, carried by O2 changing vertex, is the LP tie-break phenomenon
P9/P10 measured -- now small because the 1.42 floor is doing its job.
"""
import json, os, sys
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
for p in (os.path.join(ROOT, "reports", "P13_support"), os.path.join(ROOT, "reports", "P9_surface")):
    if p not in sys.path: sys.path.insert(0, p)
from common13 import build, SPECS, p12_points, decompose, gasflux_log_likelihood   # noqa: E402
from task2_solver import direction_factory                                         # noqa: E402

JUMPY = ["axis:dCp_scale", "PC1", "PC2", "random1"]
NLEV = 8


def main():
    meta = json.load(open(os.path.join(ROOT, "reports", "P9_surface", "task1_meta.json")))
    sd = np.array(meta["sd"]); names = meta["names"]
    pts, _ = p12_points(); th0 = pts["p38(b22)"]
    scan = pd.read_csv(os.path.join(ROOT, "reports", "P13_support", "task3_lines.csv"))
    scan = scan[scan.scheme == "clamp"]
    dirf = direction_factory(list(names))
    out = []
    for lname in JUMPY:
        d = scan[scan.line == lname].sort_values("step_sd").reset_index(drop=True)
        y = d.logL.to_numpy(); x = d.step_sd.to_numpy(); nsup = 12 - d.n_infeasible.to_numpy()
        cand = np.where(np.diff(nsup) == 0, np.abs(np.diff(y)), -np.inf)
        k = int(np.argmax(cand)); a, b = float(x[k]), float(x[k + 1])
        v = dirf(lname)

        def L(s):
            ctx, sp = build()
            return float(gasflux_log_likelihood(th0 + s * sd * v, ctx, sp))
        la, lb = L(a), L(b)
        for _ in range(NLEV):
            m = 0.5 * (a + b); lm = L(m)
            if abs(lm - la) >= abs(lb - lm): b, lb = m, lm
            else: a, la = m, lm
        ctx, sp = build()
        dA = decompose(th0 + a * sd * v, ctx, SPECS)
        ctx, sp = build()
        dB = decompose(th0 + b * sd * v, ctx, SPECS)
        gA, gB = float(np.sum(dA["growth_term"])), float(np.sum(dB["growth_term"]))
        rA, rB = float(np.sum(dA["resp_term"])), float(np.sum(dB["resp_term"]))
        o2A, o2B = np.asarray(dA["o2"], float), np.asarray(dB["o2"], float)
        grA, grB = np.asarray(dA["growth"], float), np.asarray(dB["growth"], float)
        ratio = np.where(np.isfinite(o2A) & (o2A > 0), o2B / o2A, np.nan)
        j = int(np.nanargmax(np.abs(np.log(np.where(np.isfinite(ratio) & (ratio > 0), ratio, 1.0)))))
        rec = dict(line=lname, interval_sd=b - a, step=abs((gB + rB) - (gA + rA)),
                   d_growth_term=gB - gA, d_resp_term=rB - rA,
                   pct_growth=100 * abs(gB - gA) / max(abs(gB - gA) + abs(rB - rA), 1e-12),
                   T_max_o2_change=float(np.asarray(dA["T"], float)[j]),
                   o2_before=float(o2A[j]), o2_after=float(o2B[j]), o2_ratio=float(ratio[j]),
                   growth_before=float(grA[j]), growth_after=float(grB[j]),
                   max_rel_growth_change=float(np.nanmax(np.abs(grB - grA) / np.maximum(grA, 1e-9))))
        out.append(rec)
        print(f"[jd] {lname:18s} interval {b-a:.3e} sd  step {rec['step']:.4f}  "
              f"growth {rec['d_growth_term']:+.4f} resp {rec['d_resp_term']:+.4f} "
              f"({rec['pct_growth']:.0f} % growth)", flush=True)
        print(f"[jd] {'':18s} biggest O2 move at {rec['T_max_o2_change']:.0f} C: "
              f"{rec['o2_before']:.3f} -> {rec['o2_after']:.3f} ({rec['o2_ratio']:.3f}x); "
              f"growth there {rec['growth_before']:.5f} -> {rec['growth_after']:.5f}", flush=True)
    df = pd.DataFrame(out); df.to_csv(os.path.join(HERE, "task1_jump_diag.csv"), index=False)
    print("\n[jd] done")


if __name__ == "__main__":
    main()
