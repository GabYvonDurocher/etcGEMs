#!/usr/bin/env python3
"""make_figures.py -- E2: the two figures the deck needs that no committed report provides.

    python3 reports/ecoli_deck/make_figures.py

Parsa's respirometry is committed as CSVs and has no committed figure anywhere in the repository,
so the deck cannot assemble it -- it has to draw it. Two figures, both from committed tables only,
against the prompt's cap of three:

  fig_respirometry.png   measured per-cell growth and respiration against temperature, by medium
  fig_cue.png            measured carbon-use efficiency against temperature, by medium

Sources, both under `strains/eciML1515/respirometry/`:
  derived_R2A_LB_current.csv   R2A (OTU 1) and LB (OTU 2), 12 temperatures, 117 replicate rows
  derived_M9_current.csv       M9 (OTU 1), 12 temperatures, 59 replicate rows

TWO THINGS THE FIGURES DO NOT SHOW, and the slides say so.

* **No acetate.** The prompt asked for O2 and acetate; the derived tables carry O2-based
  respiration, growth and CUE, and no acetate column. Acetate appears only as a model output in
  `reports/ecoli_gasflux/`'s committed figures, which are used as such.
* **No model curve.** There is no committed table giving the model's prediction on the same axes
  as these measurements, so the measurements are plotted alone. Model-against-measurement is left
  to `reports/ecoli_gasflux/assets/figures/configD_gasflux.png`, which is a committed figure and
  is labelled on its slide as mechanism, not interval.

`M9`'s OTU 2 (7 rows, non-monotonic) is the blank control that P4 TASK 4 excluded as a control
rather than a series; only OTU 1 is plotted for M9, and the exclusion is stated here rather than
made silently.
"""
from __future__ import annotations

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt          # noqa: E402
import numpy as np                       # noqa: E402
import pandas as pd                      # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
RESP = os.path.join(ROOT, "strains", "eciML1515", "respirometry")
OUT = os.path.join(HERE, "assets", "figures")
MEDIA = [("R2A", "derived_R2A_LB_current.csv", 1, "#1b6ca8"),
         ("LB", "derived_R2A_LB_current.csv", 2, "#c1440e"),
         ("M9", "derived_M9_current.csv", 1, "#2e7d32")]


def load():
    out = {}
    for label, fn, otu, colour in MEDIA:
        d = pd.read_csv(os.path.join(RESP, fn))
        d = d[d.OTU == otu].copy()
        out[label] = (d, colour)
    return out


def _panel(ax, data, col, ylab, title, logy=True):
    for label, (d, colour) in data.items():
        g = d.groupby("T")[col]
        m, s, n = g.mean(), g.std(), g.size()
        se = s / np.sqrt(n.clip(lower=1))
        ax.plot(d["T"], d[col], "o", ms=2.6, alpha=0.22, color=colour, zorder=1)
        ax.errorbar(m.index, m.values, yerr=se.values, fmt="o-", ms=5, lw=1.6,
                    color=colour, label=f"{label} (n={len(d)})", capsize=2.5, zorder=3)
    if logy:
        ax.set_yscale("log")
    ax.set_xlabel("temperature (°C)")
    ax.set_ylabel(ylab)
    ax.set_title(title, fontsize=10, loc="left")
    ax.grid(alpha=0.25, lw=0.5)


def main():
    os.makedirs(OUT, exist_ok=True)
    data = load()

    fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.9))
    _panel(axes[0], data, "growth_fgC_h", "growth (fg C cell$^{-1}$ h$^{-1}$)",
           "a  growth", logy=True)
    _panel(axes[1], data, "respiration_fgC_h", "respiration (fg C cell$^{-1}$ h$^{-1}$)",
           "b  respiration (from O$_2$)", logy=True)
    axes[0].legend(frameon=False, fontsize=8, loc="lower center")
    fig.tight_layout()
    p1 = os.path.join(OUT, "fig_respirometry.png")
    fig.savefig(p1, dpi=200)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(5.0, 3.9))
    _panel(ax, data, "CUE", "carbon-use efficiency", "measured CUE", logy=False)
    ax.set_ylim(0, 1)
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    p2 = os.path.join(OUT, "fig_cue.png")
    fig.savefig(p2, dpi=200)
    plt.close(fig)

    for label, (d, _) in data.items():
        g = d.groupby("T")["respiration_fgC_h"].mean()
        print(f"[e2fig] {label:4s} n={len(d):3d}  T {d['T'].min()}-{d['T'].max()} C  "
              f"respiration peak at {g.idxmax()} C  CUE {d.CUE.min():.2f}-{d.CUE.max():.2f}")
    print(f"[e2fig] wrote {os.path.relpath(p1, ROOT)} and {os.path.relpath(p2, ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
