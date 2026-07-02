"""Plots for TPC ensembles and sensitivity results. matplotlib only."""
from __future__ import annotations

import os

import numpy as np


def _mpl():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    return plt


def plot_ensemble(result, out_dir: str, fname: str = "tpc_ensemble.png"):
    """Spaghetti of all sampled TPCs, median +/- IQR band, nominal curve."""
    plt = _mpl()
    T, C = result.temps_C, result.curves
    fig, ax = plt.subplots(figsize=(7, 5))
    for row in C:
        ax.plot(T, row, color="0.7", lw=0.4, alpha=0.4)
    med = np.median(C, axis=0)
    q1, q3 = np.percentile(C, [25, 75], axis=0)
    ax.fill_between(T, q1, q3, color="tab:blue", alpha=0.25, label="IQR")
    ax.plot(T, med, color="tab:blue", lw=2, label="median")
    ax.plot(result.nominal.temps_C, result.nominal.growth, "k--", lw=2, label="nominal")
    ax.set_xlabel("Temperature (°C)")
    ax.set_ylabel("Growth rate (1/h)")
    ax.set_title("TPC ensemble across proteome allocation & kcat(T)")
    ax.legend(frameon=False)
    fig.tight_layout()
    p = os.path.join(out_dir, fname)
    fig.savefig(p, dpi=150)
    plt.close(fig)
    return p


def plot_descriptor_hist(result, out_dir: str, fname: str = "descriptor_distributions.png"):
    plt = _mpl()
    cols = ["Topt_C", "rmax", "CTmax_C", "niche_width_C", "B80_C", "Ea_eV"]
    cols = [c for c in cols if c in result.descriptors.columns]
    n = len(cols)
    ncol = 3
    nrow = int(np.ceil(n / ncol))
    fig, axes = plt.subplots(nrow, ncol, figsize=(4 * ncol, 3 * nrow))
    axes = np.atleast_1d(axes).ravel()
    for ax, c in zip(axes, cols):
        vals = result.descriptors[c].replace([np.inf, -np.inf], np.nan).dropna()
        ax.hist(vals, bins=25, color="tab:blue", alpha=0.8)
        ax.set_title(c)
    for ax in axes[n:]:
        ax.axis("off")
    fig.suptitle("TPC descriptor distributions")
    fig.tight_layout()
    p = os.path.join(out_dir, fname)
    fig.savefig(p, dpi=150)
    plt.close(fig)
    return p


def plot_sensitivity(result, out_dir: str, fname: str = "sensitivity_heatmap.png"):
    plt = _mpl()
    S = result.sensitivity.astype(float)
    fig, ax = plt.subplots(figsize=(1.2 * S.shape[1] + 2, 0.7 * S.shape[0] + 2))
    im = ax.imshow(S.values, cmap="RdBu_r", vmin=-1, vmax=1, aspect="auto")
    ax.set_xticks(range(S.shape[1]))
    ax.set_xticklabels(S.columns, rotation=45, ha="right")
    ax.set_yticks(range(S.shape[0]))
    ax.set_yticklabels(S.index)
    for i in range(S.shape[0]):
        for j in range(S.shape[1]):
            v = S.values[i, j]
            if np.isfinite(v):
                ax.text(j, i, f"{v:.2f}", ha="center", va="center",
                        color="white" if abs(v) > 0.5 else "black", fontsize=8)
    ax.set_title("Spearman sensitivity (input × TPC descriptor)")
    fig.colorbar(im, ax=ax, label="rho")
    fig.tight_layout()
    p = os.path.join(out_dir, fname)
    fig.savefig(p, dpi=150)
    plt.close(fig)
    return p


def plot_descriptor_intervals(result, out_dir: str,
                              fname: str = "descriptor_intervals.png"):
    """Headline calibrated-uncertainty view: per-descriptor median with the
    2.5-97.5 percentile interval. One panel per descriptor (independent scales)
    drawn as a horizontal point-interval. Works for any sweep."""
    plt = _mpl()
    cols = ["Topt_C", "rmax", "CTmax_C", "niche_width_C", "Ea_eV"]
    cols = [c for c in cols if c in result.descriptors.columns]
    if not cols:
        return None
    n = len(cols)
    fig, axes = plt.subplots(n, 1, figsize=(6, 0.9 * n + 1.2))
    axes = np.atleast_1d(axes).ravel()
    for ax, c in zip(axes, cols):
        vals = result.descriptors[c].replace([np.inf, -np.inf], np.nan).dropna()
        lo, med, hi = np.percentile(vals, [2.5, 50, 97.5])
        ax.plot([lo, hi], [0, 0], color="tab:blue", lw=3, alpha=0.4,
                solid_capstyle="round")
        ax.plot([med], [0], "o", color="tab:blue", ms=8, zorder=3)
        ax.annotate(f"{med:.3g}  [{lo:.3g}, {hi:.3g}]",
                    xy=(med, 0), xytext=(0, 8), textcoords="offset points",
                    ha="center", va="bottom", fontsize=8)
        ax.set_yticks([])
        ax.set_ylabel(c, rotation=0, ha="right", va="center", fontsize=10)
        ax.margins(x=0.15)
        ax.margins(y=0.6)
    fig.suptitle("Calibrated descriptor intervals (median, 2.5–97.5%)")
    fig.tight_layout()
    p = os.path.join(out_dir, fname)
    fig.savefig(p, dpi=150)
    plt.close(fig)
    return p


def plot_sector_tradeoff(result, out_dir: str, fname: str = "sector_tradeoff.png"):
    """Interior growth optimum from metabolic<->biosynthesis co-limitation.
    Only meaningful when the proteome-sector split was swept: returns None (and
    writes nothing) unless ``f_metab`` is a column of result.samples."""
    if "f_metab" not in result.samples.columns:
        return None
    plt = _mpl()
    fm = result.samples["f_metab"].values
    fmaint = (result.samples["f_maint"].values
              if "f_maint" in result.samples.columns
              else np.zeros_like(fm))
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    for ax, c in zip(axes, ["rmax", "CTmax_C"]):
        if c not in result.descriptors.columns:
            ax.axis("off")
            continue
        y = result.descriptors[c].replace([np.inf, -np.inf], np.nan).values
        sc = ax.scatter(fm, y, c=fmaint, cmap="viridis", s=18, alpha=0.85)
        ax.set_xlabel("f_metab (metabolic sector)")
        ax.set_ylabel(c)
        ax.set_title(f"{c} vs metabolic allocation")
        fig.colorbar(sc, ax=ax, label="f_maint")
    fig.suptitle("Proteome-sector trade-off (interior optimum)")
    fig.tight_layout()
    p = os.path.join(out_dir, fname)
    fig.savefig(p, dpi=150)
    plt.close(fig)
    return p


def plot_all(result, out_dir: str):
    os.makedirs(out_dir, exist_ok=True)
    figs = [
        plot_ensemble(result, out_dir),
        plot_descriptor_hist(result, out_dir),
        plot_sensitivity(result, out_dir),
        plot_descriptor_intervals(result, out_dir),
    ]
    samples = getattr(result, "samples", None)
    if samples is not None and "f_metab" in samples.columns:
        figs.append(plot_sector_tradeoff(result, out_dir))
    return figs
