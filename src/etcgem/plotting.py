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


def plot_all(result, out_dir: str):
    os.makedirs(out_dir, exist_ok=True)
    return [
        plot_ensemble(result, out_dir),
        plot_descriptor_hist(result, out_dir),
        plot_sensitivity(result, out_dir),
    ]
