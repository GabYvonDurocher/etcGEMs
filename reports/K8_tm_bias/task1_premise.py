#!/usr/bin/env python3
"""task1_premise.py -- K8 TASK 1: three checks that could kill the hypothesis before any sweep.

The hypothesis: the Candida ceiling over-prediction (+9.6 to +15.8 C) is largely a Seq2Tm
artefact, because A1 measured the predictor's bias at +5.43 C and Ilgaz showed the predicted
limit tracks median enzyme Tm.

  1. IS THE BIAS UNIFORM, or does it depend on the predicted Tm? A1's +5.43 C is a mean. If the
     bias varies with predicted Tm a flat offset is the wrong correction, and the right one has
     to be stated.
  2. WHAT SETS THE CEILING in THIS model? Ilgaz's claim is confirmed in our own code rather than
     cited: which quantile of each species' Tm distribution does CT_max track?
  3. DOES THE ARITHMETIC WORK IN PRINCIPLE? The expected CT_max shift is computed from the
     model's own structure and RECORDED IN DECISIONS.md BEFORE the sweep is run.

Run from the project root:

    python3 reports/K8_tm_bias/task1_premise.py

Writes task1_bias.csv and task1_ceiling_vs_tm.csv beside this file.
"""
from __future__ import annotations

import logging
import os
import sys

import numpy as np
import pandas as pd

logging.getLogger("cobra").setLevel(logging.ERROR)
sys.path.insert(0, "src")

from etcgem.config import build_provider, resolve            # noqa: E402
from etcgem.enzyme_cost import Perturbation                  # noqa: E402
from etcgem.tpc import TPC, apply_state                      # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
WIDE = np.linspace(15.0, 75.0, 121)
EXP = "candida_B5_respire"
STRAINS = ["cauris_iRV973", "chaemulonii_draft", "cduobushaemulonii_draft",
           "cparapsilosis_iDC1003"]
OBSERVED_LIMIT = {"cauris_iRV973": 44.0, "chaemulonii_draft": 38.0,
                  "cduobushaemulonii_draft": 38.0, "cparapsilosis_iDC1003": 38.0}
QUANTILES = [0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95]


def check1_bias():
    """Is A1's +5.43 C bias uniform across the predicted Tm range?"""
    p = os.path.join(ROOT, "reports", "predictor_calibration",
                     "partAB_measured_vs_predicted.csv")
    d = pd.read_csv(p).dropna(subset=["meltingPoint", "pred"])
    d["bias"] = d["pred"] - d["meltingPoint"]
    print(f"=== CHECK 1: is the bias uniform?  (A1's data, n = {len(d)}) ===")
    print(f"  mean bias {d['bias'].mean():+.2f} C   median {d['bias'].median():+.2f}   "
          f"sd {d['bias'].std():.2f}")
    # bias against PREDICTED Tm -- predicted is what we have for Candida, so this is the
    # regression that decides whether a flat offset is right
    sp, ip = np.polyfit(d["pred"], d["bias"], 1)
    sm, im = np.polyfit(d["pred"], d["meltingPoint"], 1)
    print(f"  bias      = {ip:+.2f} {sp:+.3f} x predicted Tm")
    print(f"  measured  = {im:+.2f} {sm:+.3f} x predicted Tm   "
          f"(A1 reports this slope as -0.061 +- 0.029)")
    print(f"  -> the bias rises {sp:.3f} C per C of predicted Tm, because the predictor "
          f"carries almost no signal")
    rows = []
    d["bin"] = pd.qcut(d["pred"], 8, duplicates="drop")
    for b, g in d.groupby("bin", observed=True):
        rows.append(dict(pred_bin=str(b), n=len(g), pred_mean=g["pred"].mean(),
                         measured_mean=g["meltingPoint"].mean(), bias_mean=g["bias"].mean()))
        print(f"    predicted {g['pred'].mean():5.1f} C  ->  measured "
              f"{g['meltingPoint'].mean():5.1f} C   bias {g['bias'].mean():+6.2f} C  "
              f"(n={len(g)})")
    return pd.DataFrame(rows), float(sp), float(sm), float(d["bias"].mean())


def check2_ceiling():
    """Which quantile of the Tm distribution does the model's CT_max track?"""
    rows = []
    print("\n=== CHECK 2: what sets the ceiling in this model? ===")
    for s in STRAINS:
        pm = build_provider(resolve(s, EXP))
        tms = np.array([e.Tm - 273.15 for e in pm.ec.table.entries
                        if e.Tm is not None and np.isfinite(e.Tm)])
        g = np.zeros(len(WIDE))
        for i, T in enumerate(WIDE):
            apply_state(pm.ec, float(T), Perturbation())
            v = pm.ec.model.slim_optimize()
            g[i] = 0.0 if (v is None or not np.isfinite(v) or v < 1e-6) else v
        d = TPC(WIDE, g).descriptors(0.05)
        row = dict(strain=s, CTmax_C=d.CTmax_C, Topt_C=d.Topt_C,
                   observed_limit_C=OBSERVED_LIMIT[s],
                   gap_C=d.CTmax_C - OBSERVED_LIMIT[s], n_enzymes=len(tms))
        for q in QUANTILES:
            row[f"Tm_q{int(q*100):02d}"] = float(np.quantile(tms, q))
        rows.append(row)
        print(f"  {s:24s} CTmax {d.CTmax_C:6.2f}  gap {row['gap_C']:+5.1f}  "
              f"Tm median {row['Tm_q50']:5.2f}  Tm q95 {row['Tm_q95']:5.2f}")
    df = pd.DataFrame(rows)
    print("\n  correlation of CT_max with each Tm quantile across the four species:")
    best, best_r = None, -2
    for q in QUANTILES:
        c = f"Tm_q{int(q*100):02d}"
        r = float(np.corrcoef(df[c], df["CTmax_C"])[0, 1])
        span = df[c].max() - df[c].min()
        print(f"    q{int(q*100):02d}  r = {r:+.3f}   (that quantile spans "
              f"{span:.2f} C across the four species)")
        if r > best_r:
            best, best_r = q, r
    print(f"  -> CT_max tracks the q{int(best*100):02d} of the Tm distribution most closely "
          f"(r = {best_r:+.3f}); with only four species this is indicative, not decisive.")
    return df


def main():
    bias_df, slope_pred, slope_meas, mean_bias = check1_bias()
    bias_df.to_csv(os.path.join(HERE, "task1_bias.csv"), index=False)
    ceil = check2_ceiling()
    ceil.to_csv(os.path.join(HERE, "task1_ceiling_vs_tm.csv"), index=False)

    print("\n=== CHECK 3: the expected CT_max shift, stated BEFORE the sweep ===")
    print("  The unfolding form sets the falling limb through each enzyme's own Tm: the native")
    print("  fraction f_N(T) collapses above Tm, and a UNIFORM shift of every Tm translates that")
    print("  collapse along the temperature axis without changing its shape. So on the model's")
    print("  own structure the expectation is a ONE-FOR-ONE shift:")
    print(f"     predicted  dCT_max / dTm  ~  1.0")
    print(f"     so a -{mean_bias:.2f} C correction should move CT_max by about "
          f"-{mean_bias:.2f} C,")
    print(f"     taking the Candida gaps from +9.0 .. +15.4 C to about "
          f"+{9.0-mean_bias:.1f} .. +{15.4-mean_bias:.1f} C.")
    print("  Damping is possible: if another constraint (the proteome pool, maintenance) binds")
    print("  before unfolding does, the shift will be LESS than one-for-one. Amplification is")
    print("  not expected and would falsify this reading of the mechanism.")
    print("\n[k8] wrote task1_bias.csv and task1_ceiling_vs_tm.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
