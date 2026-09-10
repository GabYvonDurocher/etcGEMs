#!/usr/bin/env python3
"""P13 TASK 3 -- decompose the 8.55-unit step on axis:topt_scale at p38, P9-style.

It is identical under `current` (8.5519) and `clamp` (8.5517), so the support handling is not the
cause. This asks what is: which temperature carries it, and what the LP does across it.
"""
import os, sys, json
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "reports", "P9_surface"))
from common13 import build, SPECS, NAMES, decompose, gasflux_log_likelihood   # noqa: E402
from task2_solver import direction_factory                                     # noqa: E402
from common13 import p12_points                                                # noqa: E402

SCHEMES = {"current": {}, "clamp": {"support": "clamp", "weight_floor": 1.0}}


def main():
    meta = json.load(open(os.path.join(ROOT, "reports", "P9_surface", "task1_meta.json")))
    sd = np.array(meta["sd"]); names = meta["names"]
    v = direction_factory(list(names))("axis:topt_scale")
    pts, _ = p12_points(); th0 = pts["p38(b22)"]
    ctx, sp = build(); base = dict(ctx.get("respiration") or {})
    A, B = th0 + 0.90 * sd * v, th0 + 0.95 * sd * v
    print(f"[dec] axis:topt_scale, step 0.90 -> 0.95 sd at p38")
    print(f"[dec] topt_scale (sampled) {dict(zip(NAMES, A))['topt_scale']:.6f} -> "
          f"{dict(zip(NAMES, B))['topt_scale']:.6f}")
    for name, over in SCHEMES.items():
        ctx["respiration"] = dict(base, **over)
        la, lb = (float(gasflux_log_likelihood(x, ctx, sp)) for x in (A, B))
        print(f"[dec] {name:8s}: logL {la:9.3f} -> {lb:9.3f}   step {lb-la:+9.4f}")
    ctx["respiration"] = dict(base)
    dA, dB = decompose(A, ctx, SPECS), decompose(B, ctx, SPECS)
    t = pd.DataFrame(dict(T=dA["T"],
                          growth_A=dA["growth"], growth_B=dB["growth"],
                          o2_A=dA["o2"], o2_B=dB["o2"],
                          gterm_A=dA["growth_term"], gterm_B=dB["growth_term"],
                          rterm_A=dA["resp_term"], rterm_B=dB["resp_term"]))
    t["d_growth_term"] = t.gterm_B - t.gterm_A
    t["d_resp_term"] = t.rterm_B - t.rterm_A
    t["d_total"] = t.d_growth_term + t.d_resp_term
    t["o2_ratio"] = t.o2_B / t.o2_A
    pd.set_option("display.width", 250)
    print("\n[dec] per temperature, A (0.90 sd) -> B (0.95 sd)")
    print(t[["T", "growth_A", "growth_B", "o2_A", "o2_B", "o2_ratio",
             "d_growth_term", "d_resp_term", "d_total"]].round(4).to_string(index=False))
    print(f"\n[dec] TOTAL   growth term {t.d_growth_term.sum():+.4f}   "
          f"respiration term {t.d_resp_term.sum():+.4f}   sum {t.d_total.sum():+.4f}")
    k = int(t.d_total.abs().idxmax())
    Tk = float(t["T"].iloc[k])
    print(f"[dec] carried by T = {Tk:.0f} C: growth {t.growth_A.iloc[k]:.4f} -> "
          f"{t.growth_B.iloc[k]:.4f}, O2 {t.o2_A.iloc[k]:.3f} -> {t.o2_B.iloc[k]:.3f} "
          f"({t.o2_ratio.iloc[k]:.2f}x), contributing {t.d_total.iloc[k]:+.4f}")
    gsum, rsum = t.d_growth_term.sum(), t.d_resp_term.sum()
    print(f"[dec] VERDICT: the step is "
          f"{'GROWTH-TERM dominated' if abs(gsum) > abs(rsum) else 'RESPIRATION-TERM dominated'} "
          f"({100*abs(gsum)/(abs(gsum)+abs(rsum)):.0f} % growth / "
          f"{100*abs(rsum)/(abs(gsum)+abs(rsum)):.0f} % respiration)")
    t.to_csv(os.path.join(HERE, "task3_step_decomposition.csv"), index=False)
    print("[dec] done")


if __name__ == "__main__":
    main()
