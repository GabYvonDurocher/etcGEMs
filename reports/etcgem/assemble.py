#!/usr/bin/env python3
"""Assemble the etcGEM report assets.

Copies the chosen pipeline run's figures and tables into
``reports/etcgem/assets/`` under STABLE names, so report.qmd / supplementary.qmd
reference fixed filenames regardless of which experiment/run-dir produced them.
Also generates two DERIVED figures (calibrated-vs-default descriptor comparison
and the sector trade-off) that the pipeline itself does not emit.

The document never re-runs the pipeline -- it only embeds these assets. Missing
sources are skipped with a warning (assembly never fails on a missing run), and a
summary of what was copied/generated is printed at the end.

Run from the project root:  ``python reports/etcgem/assemble.py``
"""
from __future__ import annotations

import json
import os
import shutil

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# --- locations (edit source run dirs here) ---------------------------------
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))          # project root
STRAIN = os.path.join(ROOT, "strains", "eciML1515", "outputs")

RUNS = {
    "sweep":      os.path.join(STRAIN, "default"),
    "dltkcat":    os.path.join(STRAIN, "dltkcat_ext"),
    "decompose":  os.path.join(STRAIN, "decompose_decomposition_quick"),
    "control":    os.path.join(STRAIN, "control_control_quick"),
    "calibrated": os.path.join(STRAIN, "sweep_calibrated"),      # M1.2
    "sectors":    os.path.join(STRAIN, "sweep_sectors"),         # optional
}

FIG_DIR = os.path.join(HERE, "assets", "figures")
TBL_DIR = os.path.join(HERE, "assets", "tables")

# (run_key, source_filename, stable_dest_name)
FIGURES = [
    ("sweep",      "tpc_ensemble.png",             "tpc_ensemble.png"),
    ("sweep",      "sensitivity_heatmap.png",      "sensitivity_heatmap.png"),
    ("sweep",      "descriptor_distributions.png", "descriptor_distributions.png"),
    ("decompose",  "achievable_ranges.png",        "decomp_achievable.png"),
    ("decompose",  "variance_partition.png",       "decomp_variance.png"),
    ("decompose",  "shapley_effects.png",          "decomp_shapley.png"),
    ("control",    "thermal_control_bar.png",      "control_thermal.png"),
    ("control",    "bottleneck_vs_temperature.png","control_bottleneck.png"),
    ("control",    "identifiability_hist.png",     "control_identifiability.png"),
    ("dltkcat",    "tpc_ensemble.png",             "dltkcat_ensemble.png"),
    ("calibrated", "tpc_ensemble.png",             "calibrated_ensemble.png"),
    ("sectors",    "sensitivity_heatmap.png",      "sectors_sensitivity.png"),
]

TABLES = [
    ("sweep",      "descriptors.csv",           "descriptors.csv"),
    ("sweep",      "sensitivity_spearman.csv",  "sensitivity_spearman.csv"),
    ("sweep",      "summary.json",              "summary.json"),
    ("decompose",  "decomposition_table.csv",   "decomposition_table.csv"),
    ("control",    "thermal_control.csv",       "thermal_control.csv"),
    ("control",    "identifiability.csv",       "identifiability.csv"),
    ("calibrated", "descriptors.csv",           "calibrated_descriptors.csv"),
    ("calibrated", "summary.json",              "calibrated_summary.json"),
    ("sectors",    "samples.csv",               "sectors_samples.csv"),
    ("sectors",    "descriptors.csv",           "sectors_descriptors.csv"),
]

# resolved_config.yaml for supplementary provenance: first available wins.
PROVENANCE_ORDER = ["calibrated", "sectors", "decompose", "control"]

KEY_DESCRIPTORS = ["Topt_C", "rmax", "CTmax_C", "niche_width_C"]


def _copy(src_dir, src_name, dest_dir, dest_name, copied, missing, tag):
    src = os.path.join(src_dir, src_name)
    if not os.path.exists(src):
        missing.append(f"{tag}:{src_name}  ({src})")
        return False
    os.makedirs(dest_dir, exist_ok=True)
    shutil.copy2(src, os.path.join(dest_dir, dest_name))
    copied.append(f"{dest_name}  <- {tag}/{src_name}")
    return True


def _derived_calibrated_vs_default(copied, missing):
    """Overlay the DEFAULT (hand-set LHS ranges) and CALIBRATED (correlated /
    DLTKcat-posterior per-enzyme) descriptor distributions -- the headline M1.2
    comparison of nominal vs calibrated uncertainty."""
    d_def = os.path.join(RUNS["sweep"], "descriptors.csv")
    d_cal = os.path.join(RUNS["calibrated"], "descriptors.csv")
    if not (os.path.exists(d_def) and os.path.exists(d_cal)):
        missing.append("derived:calibrated_vs_default.png (needs sweep + calibrated descriptors.csv)")
        return
    df_def = pd.read_csv(d_def)
    df_cal = pd.read_csv(d_cal)
    cols = [c for c in KEY_DESCRIPTORS if c in df_def.columns and c in df_cal.columns]
    fig, axes = plt.subplots(2, 2, figsize=(9, 7))
    for ax, c in zip(axes.ravel(), cols):
        a = df_def[c].replace([np.inf, -np.inf], np.nan).dropna()
        b = df_cal[c].replace([np.inf, -np.inf], np.nan).dropna()
        lo = float(min(a.min(), b.min()))
        hi = float(max(a.max(), b.max()))
        bins = np.linspace(lo, hi, 26) if hi > lo else 26
        ax.hist(a, bins=bins, density=True, color="0.6", alpha=0.6, label="default (hand-set)")
        ax.hist(b, bins=bins, density=True, color="tab:orange", alpha=0.55, label="calibrated")
        ax.set_title(c)
        ax.set_yticks([])
    for ax in axes.ravel()[len(cols):]:
        ax.axis("off")
    axes.ravel()[0].legend(frameon=False, fontsize=8)
    fig.suptitle("Nominal (hand-set) vs calibrated descriptor uncertainty (M1.2)")
    fig.tight_layout()
    out = os.path.join(FIG_DIR, "calibrated_vs_default.png")
    fig.savefig(out, dpi=150); plt.close(fig)
    copied.append("calibrated_vs_default.png  <- DERIVED (sweep vs calibrated)")


def _derived_sector_tradeoff(copied, missing):
    """Interior growth optimum from the sectors run: rmax / CTmax_C vs f_metab
    coloured by f_maint (metabolic vs biosynthesis co-limitation)."""
    s = os.path.join(RUNS["sectors"], "samples.csv")
    d = os.path.join(RUNS["sectors"], "descriptors.csv")
    if not (os.path.exists(s) and os.path.exists(d)):
        missing.append("derived:sector_tradeoff.png (needs sectors samples.csv + descriptors.csv)")
        return
    sm = pd.read_csv(s)
    de = pd.read_csv(d)
    if "f_metab" not in sm.columns:
        missing.append("derived:sector_tradeoff.png (sectors run has no f_metab column)")
        return
    fm = sm["f_metab"].values
    fmaint = sm["f_maint"].values if "f_maint" in sm.columns else np.zeros_like(fm)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    for ax, c in zip(axes, ["rmax", "CTmax_C"]):
        if c not in de.columns:
            ax.axis("off"); continue
        y = de[c].replace([np.inf, -np.inf], np.nan).values
        sc = ax.scatter(fm, y, c=fmaint, cmap="viridis", s=18, alpha=0.85)
        ax.set_xlabel("f_metab (metabolic sector)")
        ax.set_ylabel(c)
        ax.set_title(f"{c} vs metabolic allocation")
        fig.colorbar(sc, ax=ax, label="f_maint")
    fig.suptitle("Proteome-sector trade-off (interior growth optimum)")
    fig.tight_layout()
    out = os.path.join(FIG_DIR, "sector_tradeoff.png")
    fig.savefig(out, dpi=150); plt.close(fig)
    copied.append("sector_tradeoff.png  <- DERIVED (sectors)")


def main():
    copied, missing = [], []
    for key, src_name, dest in FIGURES:
        _copy(RUNS[key], src_name, FIG_DIR, dest, copied, missing, key)
    for key, src_name, dest in TABLES:
        _copy(RUNS[key], src_name, TBL_DIR, dest, copied, missing, key)

    # resolved_config.yaml for provenance (first available run)
    for key in PROVENANCE_ORDER:
        if _copy(RUNS[key], "resolved_config.yaml", TBL_DIR,
                 "resolved_config.yaml", copied, missing, key):
            break

    # derived figures
    _derived_calibrated_vs_default(copied, missing)
    _derived_sector_tradeoff(copied, missing)

    print("=" * 70)
    print(f"COPIED / GENERATED ({len(copied)}):")
    for c in copied:
        print("  +", c)
    if missing:
        print(f"\nSKIPPED / MISSING ({len(missing)}):")
        for m in missing:
            print("  - WARNING:", m)
    print("=" * 70)
    print(f"assets -> {os.path.relpath(os.path.join(HERE, 'assets'), ROOT)}")


if __name__ == "__main__":
    main()
