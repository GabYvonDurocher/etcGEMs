#!/usr/bin/env python3
"""P16 TASKS 2-3 -- which parameter to fix, decided on measurement, and the synthetic check.

For BOTH candidates (dTm = 0, tm_scale = 1):
  * the synthetic reduction: drop that row/column from P15's live-point covariance and report the
    new smallest eigenvalue and condition number (the prompt stops the run above ~500);
  * the log-likelihood cost of fixing it at nominal at p38, everything else unchanged;
  * where the fixed choice puts the LOW TAIL of the meltome, which is Y3's invariant.
"""
import json, os, sys
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
for p in (os.path.join(ROOT, "reports", "P13_support"), os.path.join(ROOT, "reports", "P11_nested")):
    if p not in sys.path: sys.path.insert(0, p)
from common13 import build, SPECS, NAMES, p12_points, gasflux_log_likelihood   # noqa: E402
OUT15 = os.path.join(ROOT, "strains", "eciML1515", "outputs", "calibration_configD_NLDM_recipe_P15_nested")
CAND = {"dTm": 0.0, "tm_scale": 1.0}


def main():
    import dynesty
    s = dynesty.NestedSampler.restore(os.path.join(OUT15, "dynesty_run1.save"))
    U = np.asarray(s.live_u, float)
    C = np.cov(U, rowvar=False)
    ev0 = np.linalg.eigvalsh(C)
    print(f"[t3] FULL 16-D: smallest {ev0[0]:.4e}, largest {ev0[-1]:.4e}, condition {ev0[-1]/ev0[0]:.1f}")
    rows = []
    for name in CAND:
        k = NAMES.index(name)
        keep = [i for i in range(len(NAMES)) if i != k]
        Cs = C[np.ix_(keep, keep)]
        ev = np.linalg.eigvalsh(Cs)
        cond = float(ev[-1] / ev[0])
        rows.append(dict(fixed=name, new_smallest=float(ev[0]), new_largest=float(ev[-1]),
                         new_condition=cond, passes_500=bool(cond <= 500)))
        print(f"[t3] drop {name:9s} -> 15-D smallest {ev[0]:.4e}, largest {ev[-1]:.4e}, "
              f"condition {cond:7.1f}  {'PASS (<=500)' if cond <= 500 else '*** ABOVE 500 ***'}")
    # ---- log-likelihood cost of fixing, at p38 ----
    ctx, sp = build()
    pts, _ = p12_points(); th = np.array(pts["p38(b22)"], float)
    base = float(gasflux_log_likelihood(th, ctx, sp))
    print(f"\n[t2] p38 baseline log L = {base:.4f}")
    from etcgem.calibration_multi import to_natural
    nat0 = to_natural(th, SPECS)
    for name, nominal in CAND.items():
        k = NAMES.index(name); spk = SPECS[k]
        t2 = th.copy()
        # the sampled space: "add" is natural, "log" is log(natural/nominal)
        t2[k] = nominal if spk.space == "add" else float(np.log(nominal / float(spk.emergent)))
        v = float(gasflux_log_likelihood(t2, ctx, sp))
        rows[[r["fixed"] for r in rows].index(name)].update(
            p38_logl_fixed=v, cost=base - v, natural_at_p38=float(nat0[name]), nominal=nominal,
            space=spk.space)
        print(f"[t2] fix {name:9s} = {nominal:g} (p38 has {nat0[name]:+.4f}) -> log L {v:9.4f}  "
              f"COST {base - v:8.4f}")
    df = pd.DataFrame(rows); df.to_csv(os.path.join(HERE, "task23_choice.csv"), index=False)
    pd.set_option("display.width", 220)
    print("\n" + df.to_string(index=False))
    json.dump(rows, open(os.path.join(HERE, "task23_choice.json"), "w"), indent=1, default=float)
    print("\n[t23] done")


if __name__ == "__main__":
    main()
