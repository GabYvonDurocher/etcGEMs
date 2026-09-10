#!/usr/bin/env python3
"""P13 TASK 1 (continued) -- the two tests that decide between the schemes.

TEST A -- the D3a instrument, which is how P10 gated the tie-break: evaluate each point twice,
once after evaluating ITSELF and once after evaluating a DIFFERENT point, and report the
difference. P10's rule was that every cell must be 0.0000; a scheme whose value depends on what
the solver did last is not a likelihood.

TEST B -- the continuity scan the prompt asks for: 41 points along a direction carrying the model
from living to dead (p38 -> b3), plus a fine scan through the crossing, reporting the largest
single step in the RESPIRATION term. The prompt's rule: a step above 1 log-likelihood unit means
imputation is a mask in disguise.
"""
import json, os, sys
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from common13 import build, SPECS, p12_points, decompose, gasflux_log_likelihood, _MASK_G  # noqa: E402

SCHEMES = {"current": {}, "clamp": {"support": "clamp", "weight_floor": 1.0},
           "impute": {"support": "impute", "o2_epsilon": 1e-9}}
NCOARSE, NFINE = 41, 61


def main():
    ctx, _sp = build(); base = dict(ctx.get("respiration") or {})
    pts, _ = p12_points()
    p38, b3 = pts["p38(b22)"], pts["B(b3)"]

    def sc(th, name):
        ctx["respiration"] = dict(base, **SCHEMES[name])
        return float(gasflux_log_likelihood(th, ctx, SPECS))

    # ---------- TEST A ----------
    print("=== TEST A: the D3a instrument -- does the value depend on the previous solve? ===", flush=True)
    rows = []
    for k, th in pts.items():
        other = b3 if k != "B(b3)" else p38
        r = dict(key=k)
        for name in SCHEMES:
            sc(th, name); a = sc(th, name)          # after itself
            sc(other, name); b = sc(th, name)       # after a different point
            r[f"{name}_self"] = a; r[f"{name}_other"] = b; r[f"{name}_diff"] = abs(a - b)
        rows.append(r)
        print(f"[A] {k:20s} " + "  ".join(f"{n} |d|={r[f'{n}_diff']:9.4f}" for n in SCHEMES), flush=True)
    A = pd.DataFrame(rows); A.to_csv(os.path.join(HERE, "task1b_state.csv"), index=False)
    print("\n[A] worst |difference| per scheme (P10's rule: must be 0.0000)")
    worst = {n: float(A[f"{n}_diff"].max()) for n in SCHEMES}
    for n, v in worst.items():
        print(f"[A]   {n:8s}: {v:10.4f}   {'PASS' if v < 1e-4 else '*** FAIL ***'}")

    # ---------- TEST B ----------
    print("\n=== TEST B: continuity through the death threshold, p38 -> b3 ===", flush=True)
    def scan(ts):
        out = []
        for t in ts:
            th = p38 + t * (b3 - p38)
            ctx["respiration"] = dict(base)
            d = decompose(th, ctx, SPECS)
            gt = float(np.sum(d["growth_term"]))
            g = np.asarray(d["growth"], float); o2 = np.asarray(d["o2"], float)
            row = dict(t=float(t), growth_term=gt, min_growth=float(g.min()),
                       n_below_thresh=int((g < _MASK_G).sum()),
                       n_o2_nan=int((~np.isfinite(o2)).sum()))
            for n in SCHEMES:
                row[f"resp_{n}"] = sc(th, n) - gt
            out.append(row); print(f"[B]   t={t:.4f} done", flush=True)
        return pd.DataFrame(out)

    B = scan(np.linspace(0, 1, NCOARSE))
    B.to_csv(os.path.join(HERE, "task1b_continuity_coarse.csv"), index=False)
    steps = {}
    print("\n[B] largest single step in the RESPIRATION term, 41-point coarse scan")
    for n in SCHEMES:
        s = np.abs(np.diff(B[f"resp_{n}"].to_numpy()))
        steps[n] = float(s.max())
        i = int(np.argmax(s))
        print(f"[B]   {n:8s}: {s.max():10.4f}  between t={B.t.iloc[i]:.3f} and t={B.t.iloc[i+1]:.3f}"
              f"   {'PASS (<1)' if s.max() < 1.0 else '*** FAIL (>1) ***'}")
    # fine scan across the coarse interval carrying the biggest impute step
    si = int(np.argmax(np.abs(np.diff(B["resp_impute"].to_numpy()))))
    lo, hi = float(B.t.iloc[si]), float(B.t.iloc[si + 1])
    print(f"\n[B] fine scan across t in [{lo:.4f}, {hi:.4f}] ({NFINE} points)", flush=True)
    F = scan(np.linspace(lo, hi, NFINE))
    F.to_csv(os.path.join(HERE, "task1b_continuity_fine.csv"), index=False)
    fsteps = {}
    for n in SCHEMES:
        s = np.abs(np.diff(F[f"resp_{n}"].to_numpy())); fsteps[n] = float(s.max())
        print(f"[B]   fine {n:8s}: {s.max():10.4f}")
    json.dump(dict(state_worst=worst, coarse_max_step=steps, fine_max_step=fsteps,
                   fine_window=[lo, hi]),
              open(os.path.join(HERE, "task1b_summary.json"), "w"), indent=1)
    print("\n[B] done", flush=True)


if __name__ == "__main__":
    main()
