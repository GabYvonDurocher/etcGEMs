#!/usr/bin/env python3
"""P14 TASK 1 (a), second pass -- refinement at each line's largest FEASIBLE-to-FEASIBLE step.

Per D2: the first pass tested the largest step overall, which on eight lines is the feasibility
transition D1(c) exempts. This runs the same test on the largest step whose support set is
unchanged, records the support set at EVERY refinement evaluation so a crossing hiding inside a
refined interval is caught and exempted rather than read as a jump, and extends to h/16 and h/32
for any line that is still AMBIGUOUS. The SMOOTH window [0.35, 0.65] and the JUMP threshold 0.80
are unchanged.
"""
import json, os, sys, time
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
for p in (os.path.join(ROOT, "reports", "P13_support"), os.path.join(ROOT, "reports", "P9_surface")):
    if p not in sys.path: sys.path.insert(0, p)
from common13 import build, SPECS, p12_points, gasflux_log_likelihood, to_pert   # noqa: E402
from etcgem.gasflux import flux_tpc                                              # noqa: E402
from task2_solver import direction_factory                                       # noqa: E402

LINES = ["axis:topt_scale", "axis:dCp_scale", "axis:kcat_scale", "axis:f_maint", "axis:ngam_scale",
         "axis:clearance_mult", "PC1", "PC2", "PC3", "random1", "random2", "random3"]
LO, HI, JUMP = 0.35, 0.65, 0.80
MAXLEV, EXTRA = 3, 5


def main():
    meta = json.load(open(os.path.join(ROOT, "reports", "P9_surface", "task1_meta.json")))
    sd = np.array(meta["sd"]); names = meta["names"]
    pts, _ = p12_points(); th0 = pts["p38(b22)"]
    scan = pd.read_csv(os.path.join(ROOT, "reports", "P13_support", "task3_lines.csv"))
    scan = scan[scan.scheme == "clamp"]
    dirf = direction_factory(list(names))

    def ev(s, v):
        """log-likelihood AND the number of temperatures actually scored, fresh model."""
        ctx, sp = build()
        th = th0 + s * sd * v
        ll = float(gasflux_log_likelihood(th, ctx, sp))
        r = ctx.get("respiration") or {}
        df = flux_tpc(ctx["pm"], ctx["T"], to_pert(th, sp), metabolites=("o2",),
                      tiebreak=str(r.get("tiebreak", "none")),
                      growth_tol=float(r.get("growth_tol", 1e-6)),
                      tiebreak_tol=float(r.get("tiebreak_tol", 1e-9)))
        o2 = df["o2_uptake"].to_numpy(float)
        return ll, int((np.isfinite(o2) & (o2 > 0)).sum())

    rows, t0 = [], time.time()
    for lname in LINES:
        d = scan[scan.line == lname].sort_values("step_sd").reset_index(drop=True)
        y = d.logL.to_numpy(); x = d.step_sd.to_numpy(); nsup = 12 - d.n_infeasible.to_numpy()
        step = np.abs(np.diff(y)); same = np.diff(nsup) == 0
        cand = np.where(same, step, -np.inf)
        k = int(np.argmax(cand))
        a, b = float(x[k]), float(x[k + 1])
        v = dirf(lname)
        (la, na), (lb, nb) = ev(a, v), ev(b, v)
        series = [dict(level=0, spacing=b - a, delta=abs(lb - la), n_lo=na, n_hi=nb)]
        crossing = None
        nlev = MAXLEV
        lev = 1
        while lev <= nlev:
            m = 0.5 * (a + b); lm, nm = ev(m, v)
            if nm != na or nm != nb:
                crossing = dict(level=lev, at_sd=m, n_before=na, n_after=nm, n_hi=nb)
            if abs(lm - la) >= abs(lb - lm):
                b, lb, nb = m, lm, nm
            else:
                a, la, na = m, lm, nm
            series.append(dict(level=lev, spacing=b - a, delta=abs(lb - la), n_lo=na, n_hi=nb))
            r = [s["delta"] for s in series]
            ratios = [r[i + 1] / r[i] if r[i] > 0 else float("nan") for i in range(len(r) - 1)]
            if lev == MAXLEV:
                smooth = all(np.isfinite(q) and LO <= q <= HI for q in ratios)
                jumpy = any(np.isfinite(q) and q > JUMP for q in ratios[-2:])
                if not smooth and not jumpy:
                    nlev = MAXLEV + EXTRA        # AMBIGUOUS -> more resolution, same window
            lev += 1
        r = [s["delta"] for s in series]
        ratios = [r[i + 1] / r[i] if r[i] > 0 else float("nan") for i in range(len(r) - 1)]
        tail = ratios[-3:]
        if all(np.isfinite(q) and LO <= q <= HI for q in tail):
            verdict = "SMOOTH"
        elif any(np.isfinite(q) and q > JUMP for q in tail):
            verdict = "JUMP"
        else:
            verdict = "AMBIGUOUS"
        if crossing is not None:
            verdict += " (FEASIBILITY CROSSING inside -- exempt under D1(c))"
        rows.append(dict(line=lname, at_sd=a, levels=len(series) - 1,
                         deltas=";".join(f"{q:.4f}" for q in r),
                         ratios=";".join(f"{q:.3f}" for q in ratios),
                         last_ratio=float(ratios[-1]), verdict=verdict,
                         crossing_at=None if crossing is None else float(crossing["at_sd"])))
        print(f"[t1a2] {lname:22s} |d| {' -> '.join(f'{q:.4f}' for q in r)}", flush=True)
        print(f"[t1a2] {'':22s} ratios {' '.join(f'{q:.3f}' for q in ratios)}   {verdict}", flush=True)
    df = pd.DataFrame(rows); df.to_csv(os.path.join(HERE, "task1_refine2.csv"), index=False)
    ok = df[~df.verdict.str.startswith("SMOOTH") & ~df.verdict.str.contains("FEASIBILITY")]
    print(f"\n[t1a2] SMOOTH or exempt: {len(df) - len(ok)} of {len(df)}")
    if len(ok):
        print("[t1a2] *** NOT SMOOTH: " + ", ".join(f"{r.line} ({r.verdict})" for _, r in ok.iterrows()))
    json.dump(dict(n_lines=len(df), n_not_smooth=int(len(ok)), not_smooth=ok.line.tolist(),
                   windows=dict(smooth=[LO, HI], jump=JUMP), wall_min=round((time.time()-t0)/60, 1)),
              open(os.path.join(HERE, "task1_refine2.json"), "w"), indent=1)
    print("[t1a2] done", flush=True)


if __name__ == "__main__":
    main()
