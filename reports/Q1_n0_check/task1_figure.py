#!/usr/bin/env python3
"""task1_figure.py -- Q1 TASK 1's scatter: the residual against temperature, against growth rate,
and the paired-media difference. Reads task1_residuals.csv / task1_paired_media.csv only.

    python3 reports/Q1_n0_check/task1_figure.py     ->  task1_residuals.png
"""
from __future__ import annotations

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
COL = {"NLDM": "#1b6ca8", "LB": "#c0392b"}
# Schaechter band: d(ln cell mass)/d(mu) in h^-1, the slope a constant-mass conversion would
# induce in the residual if cell mass followed the growth law. Sourced in TASK 3.
SCHAECHTER = (0.35, 0.75)


def fit_line(ax, x, y, c, ls="-"):
    k = np.isfinite(x) & np.isfinite(y)
    if k.sum() < 3:
        return
    r = stats.linregress(np.asarray(x)[k], np.asarray(y)[k])
    xs = np.linspace(np.nanmin(x), np.nanmax(x), 50)
    ax.plot(xs, r.intercept + r.slope * xs, ls, color=c, lw=1.2, alpha=0.85)
    return r


def main():
    r = pd.read_csv(os.path.join(HERE, "task1_residuals.csv"))
    pr = pd.read_csv(os.path.join(HERE, "task1_paired_media.csv"))
    confs = ["D", "E", "F"]
    fig, axes = plt.subplots(3, 3, figsize=(11.0, 9.2))

    for i, conf in enumerate(confs):
        s = r[r.config == conf]
        for j, (xcol, xlab) in enumerate((("T_C", "temperature (°C)"),
                                          ("growth_meas", "measured growth rate (h$^{-1}$)"))):
            ax = axes[i, j]
            for medium in ("NLDM", "LB"):
                q = s[s.medium == medium]
                ax.scatter(q[xcol], q.resid, s=26, color=COL[medium], label=medium, zorder=3)
                fit_line(ax, q[xcol], q.resid, COL[medium])
            ax.axhline(0.0, color="0.4", lw=0.8, zorder=1)
            ax.set_xlabel(xlab, fontsize=10)
            ax.set_ylabel(f"config {conf}\nresidual  log(meas/model)", fontsize=10)
            ax.tick_params(labelsize=9)
            if i == 0 and j == 0:
                ax.legend(fontsize=9, frameon=False, loc="upper left")

        # the decisive panel: temperature held exactly, growth rate varying
        ax = axes[i, 2]
        p = pr[pr.config == conf]
        ax.fill_between([0, p.d_growth.max() * 1.05],
                        [0, SCHAECHTER[0] * p.d_growth.max() * 1.05],
                        [0, SCHAECHTER[1] * p.d_growth.max() * 1.05],
                        color="0.75", alpha=0.45, zorder=1,
                        label="cell-size artefact\nwould lie here")
        ax.scatter(p.d_growth, p.d_resid, s=30, color="#7d3c98", zorder=3)
        for _, q in p.iterrows():
            ax.annotate(f"{q.T_C:.0f}", (q.d_growth, q.d_resid), fontsize=7,
                        textcoords="offset points", xytext=(4, 3), color="0.35")
        fit_line(ax, p.d_growth, p.d_resid, "#7d3c98")
        ax.axhline(0.0, color="0.4", lw=0.8, zorder=1)
        ax.set_xlabel("$\\Delta$ growth rate, LB $-$ NLDM (h$^{-1}$)", fontsize=10)
        ax.set_ylabel("$\\Delta$ residual, LB $-$ NLDM", fontsize=10)
        ax.tick_params(labelsize=9)
        if i == 0:
            ax.legend(fontsize=8, frameon=False, loc="upper left")

    axes[0, 0].set_title("against temperature", fontsize=11)
    axes[0, 1].set_title("against growth rate (confounded with T)", fontsize=11)
    axes[0, 2].set_title("paired media: T held, growth varying", fontsize=11)
    fig.suptitle("Q1 TASK 1  --  respiration residual; points labelled by °C in the right "
                 "column", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    out = os.path.join(HERE, "task1_residuals.png")
    fig.savefig(out, dpi=160)
    print(f"[q1t1fig] wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
