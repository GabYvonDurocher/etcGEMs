#!/usr/bin/env python3
"""Figures for the gas-exchange deliverable (P1).

Replaces Parsa's per-configuration plotting scripts: it reads whatever
`etcgem gasflux --experiment <EXP>` wrote and draws the two panels every configuration needs
-- growth TPCs across media, and O2 / CO2 / RQ across media -- for each configuration given.

    python scripts/gasflux_figures.py --strain eciML1515 \
        --experiments gasflux_configA gasflux_configB gasflux_configC

Writes into reports/ecoli_gasflux/assets/figures/, the house report convention, NOT into the
strain's output tree.
"""
from __future__ import annotations

import argparse
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
FIGS = os.path.join(ROOT, "reports", "ecoli_gasflux", "assets", "figures")
COL = {"glucose_minimal": "#2ca02c", "NLDM": "#d62728", "NLDM_blanket": "#ff9896",
       "LB": "#2E5E8C", "BHI": "#9467bd"}
MASK = 0.05          # hide the collapsed tail, where fluxes are meaningless


def _figure(df, title, stem, gdw_per_cell=None):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from etcgem.tpc import TPC

    media = [m for m in df.medium.unique()]
    os.makedirs(FIGS, exist_ok=True)

    fig, ax = plt.subplots(figsize=(8.6, 5.6))
    for m in media:
        d = df[df.medium == m].sort_values("temp_C")
        desc = TPC(d.temp_C.to_numpy(float), d.growth.to_numpy(float)).descriptors()
        ax.plot(d.temp_C, d.growth, "-", lw=2.4, color=COL.get(m),
                label=f"{m} — r$_{{max}}$ {desc.rmax:.2f} @ {desc.Topt_C:.0f} °C")
    ax.set_xlabel("Temperature (°C)"); ax.set_ylabel("Growth rate (h$^{-1}$)")
    ax.set_title(title, fontsize=11); ax.grid(alpha=0.3); ax.legend(fontsize=8.5)
    fig.tight_layout(); fig.savefig(os.path.join(FIGS, f"{stem}_growth.png"), dpi=140)
    plt.close(fig)

    fig, axes = plt.subplots(1, 3, figsize=(16, 5.0))
    for m in media:
        d = df[df.medium == m].sort_values("temp_C")
        g = d.growth.to_numpy(float)
        keep = g >= MASK * np.nanmax(g) if np.nanmax(g) > 0 else np.zeros_like(g, bool)
        for ax, col in zip(axes, ["o2_uptake", "co2_release", "RQ"]):
            y = d[col].to_numpy(float).copy(); y[~keep] = np.nan
            ax.plot(d.temp_C, y, "-", lw=2.3, color=COL.get(m), label=m)
    axes[0].set_ylabel("O$_2$ consumption (mmol gDW$^{-1}$ h$^{-1}$)")
    axes[1].set_ylabel("CO$_2$ formation (mmol gDW$^{-1}$ h$^{-1}$)")
    axes[2].set_ylabel("RQ = CO$_2$/O$_2$")
    axes[2].axhline(1.0, color="k", ls=":", lw=0.8)
    axes[2].axhspan(0.8, 1.4, color="0.85", alpha=0.5, zorder=0)
    if gdw_per_cell:
        for ax in axes[:2]:
            tw = ax.twinx(); lo, hi = ax.get_ylim()
            tw.set_ylim(lo * gdw_per_cell * 1e12, hi * gdw_per_cell * 1e12)
            tw.set_ylabel("fmol cell$^{-1}$ h$^{-1}$", fontsize=9, color="0.35")
            tw.tick_params(labelsize=8, colors="0.35")
    for ax, t in zip(axes, ["O$_2$ consumption", "CO$_2$ formation", "Respiratory quotient"]):
        ax.set_xlabel("Temperature (°C)"); ax.grid(alpha=0.3); ax.legend(fontsize=8)
        ax.set_title(t, fontsize=11)
    fig.suptitle(f"{title} — gas exchange (collapsed tail masked)", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(os.path.join(FIGS, f"{stem}_gasflux.png"), dpi=140)
    plt.close(fig)
    return [f"{stem}_growth.png", f"{stem}_gasflux.png"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--strain", default="eciML1515")
    ap.add_argument("--experiments", nargs="+", required=True)
    args = ap.parse_args()
    import yaml
    gx_path = os.path.join(ROOT, "strains", args.strain, "gas_exchange.yaml")
    gdw = None
    if os.path.exists(gx_path):
        gdw = (yaml.safe_load(open(gx_path)) or {}).get("gas_exchange", {}).get("gdw_per_cell")
    made = []
    for exp in args.experiments:
        src = os.path.join(ROOT, "strains", args.strain, "outputs", exp, "gasflux.csv")
        if not os.path.exists(src):
            print(f"  - MISSING {src}; run `etcgem gasflux --experiment {exp}` first")
            continue
        made += _figure(pd.read_csv(src), exp.replace("gasflux_", "").replace("config", "Configuration "),
                        exp.replace("gasflux_", ""), gdw)
    print(f"wrote {len(made)} figure(s) to {os.path.relpath(FIGS, ROOT)}")
    for f in made:
        print("  +", f)


if __name__ == "__main__":
    main()
