#!/usr/bin/env python3
"""S1 TASK 3 — the one figure this document generates.

The Candida requirement arithmetic as a single figure: what Figure 4's claim rests on at each
stage, and how far the model is from the only measured congeneric benchmark there is.

EVERY number is read from a committed table or report; nothing is recomputed and no model is
solved. Sources, per value:

  32.54 C, 0.411 C, 79x, 34x, 5.4x [2.5, 10.3], 2.56 C, 1.60 C, 0.151 C, 91x, 13.77 C
        reports/predictor_calibration/report.md, PART F table
  13.64 C (B3, this repository's recompute), 13.57 C (B5, after the K5 repair)
        reports/K7_envelope/task1_conventions.csv  (MEDIAN rows, zeros convention)

    python reports/synthesis/fig_requirement_arithmetic.py
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(HERE, "assets", "figures", "requirement_arithmetic.png")

# --- read the two numbers that come from a table (the rest are quoted in A1's PART F) -------
conv = pd.read_csv(os.path.join(ROOT, "reports/K7_envelope/task1_conventions.csv"))
med = conv[(conv.strain == "MEDIAN") & (conv.convention.str.startswith("zeros"))]
REQ_B3 = float(med[med.config.str.startswith("B3")].required_dTm.iloc[0])
REQ_B5 = float(med[med.config.str.startswith("B5")].required_dTm.iloc[0])

# A1 PART F, verbatim
REQ_PUB, AVAIL_PUB = 32.54, 0.411
REQ_K2 = 13.77
AVAIL_A1, AVAIL_A1_LO, AVAIL_A1_HI = 2.56, 1.33, 5.56
AVAIL_MEASURED = 1.60           # Walunjkar 2025, 827 ortholog pairs, the only measured benchmark
FOLD = {"as published": 79.0, "K2 requirement": 34.0, "K2 + A1": 5.4}
FOLD_CI = (2.5, 10.3)

fig, axes = plt.subplots(1, 2, figsize=(11.2, 4.6))

# --- left: the requirement in degrees, as the model states have changed it -----------------
ax = axes[0]
stages = ["as published\n(standalone)", "K2\n(core thermal form)", "K2 recompute\n(B3, this repo)",
          "B5\n(after the K5 repair)"]
vals = [REQ_PUB, REQ_K2, REQ_B3, REQ_B5]
cols = ["#7f7f7f", "#2E5E8C", "#2E5E8C", "#1b7837"]
ax.bar(range(4), vals, color=cols, width=0.62)
for i, v in enumerate(vals):
    ax.text(i, v + 0.7, f"{v:.2f}", ha="center", fontsize=10, fontweight="bold")
ax.axhline(AVAIL_MEASURED, color="#d62728", ls="--", lw=1.8)
ax.text(3.45, AVAIL_MEASURED + 0.8, f"measured congeneric\ndifference {AVAIL_MEASURED:.1f} °C",
        ha="right", va="bottom", fontsize=8.5, color="#d62728")
ax.set_xticks(range(4)); ax.set_xticklabels(stages, fontsize=8.5)
ax.set_ylabel("required ΔT$_m$ between relatives (°C)")
ax.set_title("A)  what the model requires", fontsize=11, loc="left")
ax.set_ylim(0, 36); ax.grid(axis="y", alpha=0.3)

# --- right: the fold gap, which is the claim ------------------------------------------------
ax = axes[1]
names = list(FOLD)
y = np.arange(len(names))[::-1]
ax.barh(y, [FOLD[n] for n in names], color=["#7f7f7f", "#2E5E8C", "#1b7837"], height=0.55)
ax.errorbar(FOLD["K2 + A1"], y[-1], xerr=[[FOLD["K2 + A1"] - FOLD_CI[0]], [FOLD_CI[1] - FOLD["K2 + A1"]]],
            fmt="none", ecolor="k", elinewidth=1.6, capsize=5, zorder=5)
for yy, n in zip(y, names):
    v = FOLD[n]
    lab = f"{v:.0f}×" if v >= 10 else f"{v:.1f}× [{FOLD_CI[0]}, {FOLD_CI[1]}]"
    ax.text(v + 1.5, yy, lab, va="center", fontsize=10, fontweight="bold")
ax.axvline(1.0, color="#d62728", ls="--", lw=1.8)
ax.text(1.8, y[0] + 0.42, "parity: the model would need\nno more than measurement provides",
        fontsize=8.5, color="#d62728", va="top")
ax.set_yticks(y); ax.set_yticklabels(
    ["as published\n32.54 / 0.411 °C", "K2 requirement\n13.77 / 0.411 °C",
     "K2 + A1 correction\n13.77 / 2.56 °C"], fontsize=8.5)
ax.set_xlabel("fold gap = required ΔT$_m$ ÷ available ΔT$_m$")
ax.set_title("B)  the claim, and its two corrections", fontsize=11, loc="left")
ax.set_xlim(0, 95); ax.grid(axis="x", alpha=0.3)

fig.suptitle("Figure 4's arithmetic, stage by stage — every value read from a committed table",
             fontsize=11.5)
fig.tight_layout(rect=(0, 0, 1, 0.94))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
fig.savefig(OUT, dpi=170)
print(f"wrote {os.path.relpath(OUT, ROOT)}")
print(f"  B3 requirement (recomputed by K7): {REQ_B3} C")
print(f"  B5 requirement (after K5 repair):  {REQ_B5} C")
