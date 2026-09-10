#!/usr/bin/env python3
"""P14 TASK 1 (a) -- the DISCONTINUITY test by grid refinement, per D1.

At each of P11's twelve lines, take the interval carrying the largest step under clamp at p38
(from P13's committed scan) and BISECT INTO THE LARGER HALF three times, so the refinement always
follows whatever is producing the step:

    level 0:  |L(s1) - L(s0)|                       spacing h    = 0.05 sd
    level 1:  the larger of the two half-increments spacing h/2
    level 2:  ... of that half                      spacing h/4
    level 3:  ... of that half                      spacing h/8

For a function with bounded derivative the tracked increment halves each level. For a genuine jump
it converges to the jump height, because the sub-interval containing the jump keeps all of it.
Following the LARGER half is what makes this a test: a jump cannot hide in the half we stop looking
at. Fresh model per evaluation, single process.
"""
import json, os, sys, time
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
for p in (os.path.join(ROOT, "reports", "P13_support"), os.path.join(ROOT, "reports", "P9_surface")):
    if p not in sys.path: sys.path.insert(0, p)
from common13 import build, SPECS, p12_points, gasflux_log_likelihood     # noqa: E402
from task2_solver import direction_factory                                # noqa: E402

LINES = ["axis:topt_scale", "axis:dCp_scale", "axis:kcat_scale", "axis:f_maint", "axis:ngam_scale",
         "axis:clearance_mult", "PC1", "PC2", "PC3", "random1", "random2", "random3"]
LO, HI, JUMP = 0.35, 0.65, 0.80          # D1's windows, fixed before this ran
P13 = os.path.join(ROOT, "reports", "P13_support", "task3_lines.csv")


def main():
    meta = json.load(open(os.path.join(ROOT, "reports", "P9_surface", "task1_meta.json")))
    sd = np.array(meta["sd"]); names = meta["names"]
    pts, _ = p12_points(); th0 = pts["p38(b22)"]
    scan = pd.read_csv(P13); scan = scan[scan.scheme == "clamp"]
    dirf = direction_factory(list(names))

    def L(s, v):
        ctx, sp = build()                       # FRESH model
        return float(gasflux_log_likelihood(th0 + s * sd * v, ctx, sp))

    rows, t0 = [], time.time()
    for lname in LINES:
        d = scan[scan.line == lname].sort_values("step_sd")
        y = d.logL.to_numpy(); x = d.step_sd.to_numpy()
        k = int(np.argmax(np.abs(np.diff(y))))
        a, b = float(x[k]), float(x[k + 1])
        v = dirf(lname)
        la, lb = L(a, v), L(b, v)
        series = [dict(level=0, spacing=b - a, lo=a, hi=b, delta=abs(lb - la))]
        for lev in (1, 2, 3):
            m = 0.5 * (a + b); lm = L(m, v)
            if abs(lm - la) >= abs(lb - lm):     # follow the LARGER half
                b, lb = m, lm
            else:
                a, la = m, lm
            series.append(dict(level=lev, spacing=b - a, lo=a, hi=b, delta=abs(lb - la)))
        r = [s["delta"] for s in series]
        ratios = [r[i + 1] / r[i] if r[i] > 0 else float("nan") for i in range(3)]
        if all(np.isfinite(q) and LO <= q <= HI for q in ratios):
            verdict = "SMOOTH"
        elif any(np.isfinite(q) and q > JUMP for q in ratios):
            verdict = "JUMP"
        else:
            verdict = "AMBIGUOUS"
        rows.append(dict(line=lname, at_sd=float(x[k]), step_h=r[0], d_h2=r[1], d_h4=r[2], d_h8=r[3],
                         ratio1=ratios[0], ratio2=ratios[1], ratio3=ratios[2], verdict=verdict))
        print(f"[t1a] {lname:22s} |d| {r[0]:8.4f} -> {r[1]:8.4f} -> {r[2]:8.4f} -> {r[3]:8.4f}   "
              f"ratios {ratios[0]:.3f} {ratios[1]:.3f} {ratios[2]:.3f}   {verdict}", flush=True)
    df = pd.DataFrame(rows); df.to_csv(os.path.join(HERE, "task1_refine.csv"), index=False)
    bad = df[df.verdict != "SMOOTH"]
    print(f"\n[t1a] {int((df.verdict == 'SMOOTH').sum())} of {len(df)} lines SMOOTH; "
          + ("all smooth" if len(bad) == 0 else "NOT SMOOTH: " + ", ".join(f"{r.line}({r.verdict})" for _, r in bad.iterrows())))
    json.dump(dict(windows=dict(smooth=[LO, HI], jump=JUMP), n_smooth=int((df.verdict == "SMOOTH").sum()),
                   n_lines=len(df), not_smooth=bad.line.tolist(), wall_min=round((time.time()-t0)/60, 1)),
              open(os.path.join(HERE, "task1_refine.json"), "w"), indent=1)
    print("[t1a] done", flush=True)


if __name__ == "__main__":
    main()
