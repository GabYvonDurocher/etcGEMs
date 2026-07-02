"""Allocation vs envelope variance decomposition of the TPC (hypothesis H1.3).

A single genome can generate a *range* of thermal performance curves by (a)
reshaping the per-enzyme thermal envelope (genome-set params: dTopt, topt_scale,
dCp_scale) and (b) reallocating its proteome (allocation-set params:
budget_scale, per-group allocations). H1.3 says these separate: the envelope
sets the *shape/position* of the TPC, allocation sets its *magnitude*.

This module quantifies that split with a two-group functional-ANOVA / Shapley
variance decomposition on a **crossed** design, reusing the existing engine
(`Perturbation`, `compute_tpc`, `TPC.descriptors`, `sensitivity._lhs`) unchanged.

Design
------
Draw M allocation samples (envelope held at nominal) and N envelope samples
(allocation at nominal) by Latin hypercube, then evaluate every crossed pair
(allocation_i, envelope_j) -> one Perturbation -> one TPC -> its descriptors.
That gives an M x N matrix ``f_ij`` per descriptor.

Decomposition (per descriptor, over finite cells)
-------------------------------------------------
    mu   = mean(f_ij)
    a_i  = mean_j f_ij - mu                 # allocation main effect
    e_j  = mean_i f_ij - mu                 # envelope main effect
    g_ij = f_ij - mu - a_i - e_j            # interaction
    V_A  = mean_i a_i^2 ; V_E = mean_j e_j^2 ; V_AE = mean_ij g_ij^2
    V    = V_A + V_E + V_AE
    S_A, S_E, S_AE = V_A/V, V_E/V, V_AE/V           # grouped Sobol fractions (sum 1)
    T_A, T_E       = S_A + S_AE, S_E + S_AE          # total-effect indices
    phi_A, phi_E   = S_A + S_AE/2, S_E + S_AE/2      # Shapley (exact for 2 groups)

The fractions are relative to the chosen input distributions (uniform over the
configured ranges) -- a structural, in-silico decomposition of what the model
*can* generate, not a claim about real cells.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence

import numpy as np
import pandas as pd

from .enzyme_cost import Perturbation
from .sensitivity import _lhs, _make_perturbation
from .tpc import compute_tpc

# Descriptors decomposed (magnitude: rmax; temperature/shape: the rest).
DESCRIPTORS = ["Topt_C", "rmax", "CTmin_C", "CTmax_C", "niche_width_C",
               "B80_C", "Ea_eV", "skewness"]
KEY_DESCRIPTORS = ["Topt_C", "rmax", "CTmax_C", "niche_width_C", "Ea_eV"]


# ---------------------------------------------------------------------------
# core math
# ---------------------------------------------------------------------------
def decompose_grid(F: np.ndarray) -> Dict[str, float]:
    """Two-group functional-ANOVA / Shapley split of an M x N descriptor grid.

    Drops fully-NaN rows/columns, then works over the remaining finite cells.
    Fractions sum to 1 by construction; returns NaNs if there is no variance.
    """
    F = np.asarray(F, float)
    keep_r = ~np.all(np.isnan(F), axis=1)
    keep_c = ~np.all(np.isnan(F), axis=0)
    F = F[np.ix_(keep_r, keep_c)]
    n_valid = int(np.isfinite(F).sum())
    out = dict(V_A=np.nan, V_E=np.nan, V_AE=np.nan, V=np.nan,
               S_A=np.nan, S_E=np.nan, S_AE=np.nan, T_A=np.nan, T_E=np.nan,
               phi_A=np.nan, phi_E=np.nan, n_valid=n_valid,
               n_alloc=int(F.shape[0]) if F.ndim == 2 else 0,
               n_env=int(F.shape[1]) if F.ndim == 2 else 0)
    if F.size == 0 or n_valid == 0:
        return out
    mu = float(np.nanmean(F))
    a = np.nanmean(F, axis=1) - mu
    e = np.nanmean(F, axis=0) - mu
    g = F - mu - a[:, None] - e[None, :]
    V_A = float(np.nanmean(a ** 2))
    V_E = float(np.nanmean(e ** 2))
    V_AE = float(np.nanmean(g ** 2))
    V = V_A + V_E + V_AE
    out.update(V_A=V_A, V_E=V_E, V_AE=V_AE, V=V)
    if V <= 0:
        return out
    S_A, S_E, S_AE = V_A / V, V_E / V, V_AE / V
    out.update(S_A=S_A, S_E=S_E, S_AE=S_AE,
               T_A=S_A + S_AE, T_E=S_E + S_AE,
               phi_A=S_A + S_AE / 2.0, phi_E=S_E + S_AE / 2.0)
    return out


def _lhs_table(ranges: Dict[str, Sequence[float]], n: int, seed: int) -> pd.DataFrame:
    names = list(ranges)
    U = _lhs(n, len(names), seed)
    cols = {nm: ranges[nm][0] + U[:, k] * (ranges[nm][1] - ranges[nm][0])
            for k, nm in enumerate(names)}
    return pd.DataFrame(cols, columns=names)


def _group_names(allocation_ranges: Dict[str, Sequence[float]]) -> List[str]:
    """Per-group allocation multipliers are named alloc_<grp>."""
    return [n[len("alloc_"):] for n in allocation_ranges if n.startswith("alloc_")]


# ---------------------------------------------------------------------------
# result container
# ---------------------------------------------------------------------------
@dataclass
class DecompositionResult:
    temps_C: np.ndarray
    alloc_samples: pd.DataFrame
    env_samples: pd.DataFrame
    grids: Dict[str, np.ndarray]              # descriptor -> (M, N)
    table: pd.DataFrame                       # one row per descriptor
    alloc_only_curves: np.ndarray             # (M, n_temps), envelope nominal
    env_only_curves: np.ndarray               # (N, n_temps), allocation nominal
    nominal_curve: np.ndarray                 # (n_temps,)

    # -- summary --------------------------------------------------------------
    def summary(self) -> Dict[str, dict]:
        out = {}
        for d, row in self.table.iterrows():
            phi_a, phi_e = row["phi_A"], row["phi_E"]
            dom = ("allocation" if phi_a > phi_e else "envelope") \
                if np.isfinite(phi_a) and np.isfinite(phi_e) else "undetermined"
            out[d] = {"dominant_axis": dom,
                      "S_allocation": _f(row["S_A"]), "S_envelope": _f(row["S_E"]),
                      "S_interaction": _f(row["S_AE"]),
                      "phi_allocation": _f(phi_a), "phi_envelope": _f(phi_e),
                      "n_valid": int(row["n_valid"])}
        return out

    # -- persistence ----------------------------------------------------------
    def save(self, out_dir: str, no_plots: bool = False) -> List[str]:
        os.makedirs(out_dir, exist_ok=True)
        written = []
        p = os.path.join(out_dir, "decomposition_table.csv")
        self.table.to_csv(p, index_label="descriptor")
        written.append(p)

        npz = os.path.join(out_dir, "grids.npz")
        payload = {f"grid_{d}": g for d, g in self.grids.items()}
        payload["allocation_samples"] = self.alloc_samples.to_numpy()
        payload["allocation_names"] = np.array(list(self.alloc_samples.columns))
        payload["envelope_samples"] = self.env_samples.to_numpy()
        payload["envelope_names"] = np.array(list(self.env_samples.columns))
        np.savez(npz, **payload)
        written.append(npz)

        np.save(os.path.join(out_dir, "allocation_only_curves.npy"), self.alloc_only_curves)
        np.save(os.path.join(out_dir, "envelope_only_curves.npy"), self.env_only_curves)
        np.save(os.path.join(out_dir, "temps_C.npy"), self.temps_C)

        summ = os.path.join(out_dir, "summary.json")
        with open(summ, "w") as fh:
            json.dump(self.summary(), fh, indent=2)
        written.append(summ)

        if not no_plots:
            try:
                written += plot_all(self, out_dir)
            except Exception as e:
                print(f"[decompose] plotting skipped ({e})")
        return written


def _f(x):
    return None if x is None or not np.isfinite(x) else float(x)


# ---------------------------------------------------------------------------
# runner
# ---------------------------------------------------------------------------
def run_decomposition(pm, temps_C, allocation_ranges, envelope_ranges,
                      n_alloc: int, n_env: int, seed: int = 1,
                      crit_frac: float = 0.05,
                      descriptors: Sequence[str] = DESCRIPTORS,
                      progress: bool = True) -> DecompositionResult:
    """Crossed allocation x envelope evaluation + per-descriptor decomposition.

    Reuses Perturbation / compute_tpc / TPC.descriptors unchanged; the descriptor
    table it feeds the ANOVA is generic, so it can later target respiration/CUE
    curves instead of growth without touching the math.
    """
    temps_C = np.asarray(temps_C, float)
    default_budget = pm.ec.default_budget
    group_names = _group_names(allocation_ranges)

    alloc = _lhs_table(allocation_ranges, n_alloc, seed)
    env = _lhs_table(envelope_ranges, n_env, seed + 1)
    a_names, e_names = list(alloc.columns), list(env.columns)

    grids = {d: np.full((n_alloc, n_env), np.nan) for d in descriptors}
    total = n_alloc * n_env
    for i in range(n_alloc):
        ai = {k: float(alloc.iloc[i][k]) for k in a_names}
        for j in range(n_env):
            ej = {k: float(env.iloc[j][k]) for k in e_names}
            pert = _make_perturbation({**ai, **ej}, default_budget, group_names)
            desc = compute_tpc(pm, temps_C, pert).descriptors(crit_frac).as_dict()
            for d in descriptors:
                grids[d][i, j] = desc.get(d, np.nan)
        if progress and (i + 1) % max(1, n_alloc // 8) == 0:
            print(f"[decompose] crossed grid {(i + 1) * n_env}/{total}")

    # marginal ensembles (envelope nominal / allocation nominal)
    alloc_only = np.vstack([
        compute_tpc(pm, temps_C,
                    _make_perturbation({k: float(alloc.iloc[i][k]) for k in a_names},
                                       default_budget, group_names)).growth
        for i in range(n_alloc)])
    env_only = np.vstack([
        compute_tpc(pm, temps_C,
                    _make_perturbation({k: float(env.iloc[j][k]) for k in e_names},
                                       default_budget, group_names)).growth
        for j in range(n_env)])
    nominal = compute_tpc(pm, temps_C, Perturbation()).growth

    table = pd.DataFrame({d: decompose_grid(grids[d]) for d in descriptors}).T
    table = table[["V_A", "V_E", "V_AE", "V", "S_A", "S_E", "S_AE",
                   "T_A", "T_E", "phi_A", "phi_E", "n_valid", "n_alloc", "n_env"]]
    return DecompositionResult(temps_C, alloc, env, grids, table,
                               alloc_only, env_only, nominal)


# ---------------------------------------------------------------------------
# plots (match plotting.py: Agg, dpi 150)
# ---------------------------------------------------------------------------
def _mpl():
    from .plotting import _mpl as m
    return m()


def plot_achievable_ranges(res, out_dir, fname="achievable_ranges.png"):
    plt = _mpl()
    T = res.temps_C
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=True)
    for ax, C, title in ((axes[0], res.alloc_only_curves, "Allocation-only (envelope nominal)"),
                         (axes[1], res.env_only_curves, "Envelope-only (allocation nominal)")):
        for row in C:
            ax.plot(T, row, color="0.7", lw=0.4, alpha=0.4)
        med = np.median(C, axis=0)
        q1, q3 = np.percentile(C, [25, 75], axis=0)
        ax.fill_between(T, q1, q3, color="tab:blue", alpha=0.25, label="IQR")
        ax.plot(T, med, color="tab:blue", lw=2, label="median")
        ax.plot(T, res.nominal_curve, "k--", lw=2, label="nominal")
        ax.set_xlabel("Temperature (°C)")
        ax.set_title(title)
        ax.legend(frameon=False)
    axes[0].set_ylabel("Growth rate (1/h)")
    fig.suptitle("H1.3 achievable TPC ranges: allocation vs envelope")
    fig.tight_layout()
    p = os.path.join(out_dir, fname)
    fig.savefig(p, dpi=150)
    plt.close(fig)
    return p


def plot_variance_partition(res, out_dir, fname="variance_partition.png"):
    plt = _mpl()
    descs = [d for d in KEY_DESCRIPTORS if d in res.table.index]
    S_A = res.table.loc[descs, "S_A"].astype(float).values
    S_E = res.table.loc[descs, "S_E"].astype(float).values
    S_AE = res.table.loc[descs, "S_AE"].astype(float).values
    x = np.arange(len(descs))
    fig, ax = plt.subplots(figsize=(1.4 * len(descs) + 2, 5))
    ax.bar(x, S_A, label="allocation (S_A)", color="tab:orange")
    ax.bar(x, S_E, bottom=S_A, label="envelope (S_E)", color="tab:blue")
    ax.bar(x, S_AE, bottom=S_A + S_E, label="interaction (S_AE)", color="0.6")
    ax.set_xticks(x)
    ax.set_xticklabels(descs, rotation=30, ha="right")
    ax.set_ylabel("variance fraction")
    ax.set_ylim(0, 1)
    ax.set_title("Grouped Sobol variance partition per descriptor")
    ax.legend(frameon=False)
    fig.tight_layout()
    p = os.path.join(out_dir, fname)
    fig.savefig(p, dpi=150)
    plt.close(fig)
    return p


def plot_shapley_effects(res, out_dir, fname="shapley_effects.png"):
    plt = _mpl()
    descs = [d for d in res.table.index if np.isfinite(res.table.loc[d, "phi_A"])]
    phi_A = res.table.loc[descs, "phi_A"].astype(float).values
    phi_E = res.table.loc[descs, "phi_E"].astype(float).values
    x = np.arange(len(descs))
    w = 0.4
    fig, ax = plt.subplots(figsize=(1.4 * len(descs) + 2, 5))
    ax.bar(x - w / 2, phi_A, w, label="allocation (φ_A)", color="tab:orange")
    ax.bar(x + w / 2, phi_E, w, label="envelope (φ_E)", color="tab:blue")
    ax.set_xticks(x)
    ax.set_xticklabels(descs, rotation=30, ha="right")
    ax.set_ylabel("Shapley effect (φ_A + φ_E = 1)")
    ax.set_ylim(0, 1)
    ax.set_title("Shapley variance attribution per descriptor")
    ax.legend(frameon=False)
    fig.tight_layout()
    p = os.path.join(out_dir, fname)
    fig.savefig(p, dpi=150)
    plt.close(fig)
    return p


def plot_all(res, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    return [plot_achievable_ranges(res, out_dir),
            plot_variance_partition(res, out_dir),
            plot_shapley_effects(res, out_dir)]


# ---------------------------------------------------------------------------
# CLI entry (called by cli.cmd_decompose)
# ---------------------------------------------------------------------------
def run(cfg: Dict, out_dir: str, no_plots: bool = False):
    """Build the provider from a resolved config and run the decomposition."""
    from .config import build_provider, temperature_grid
    if "decomposition" not in cfg:
        raise SystemExit("config has no `decomposition:` block "
                         "(use an experiment of kind: decompose)")
    d = cfg["decomposition"]
    pm = build_provider(cfg)
    try:
        pm.ec.model.solver.configuration.timeout = int(cfg.get("solver_timeout", 10))
    except Exception:
        pass
    temps = temperature_grid(cfg)
    print(f"[decompose] model={pm.name} grid={temps[0]:.0f}-{temps[-1]:.0f}°C "
          f"M={d.get('n_allocation', 24)} N={d.get('n_envelope', 24)}")
    res = run_decomposition(
        pm, temps, d["allocation_params"], d["envelope_params"],
        n_alloc=int(d.get("n_allocation", 24)), n_env=int(d.get("n_envelope", 24)),
        seed=int(d.get("seed", 1)), crit_frac=cfg.get("crit_frac", 0.05))
    res.save(out_dir, no_plots=no_plots)
    for desc, info in res.summary().items():
        if desc in KEY_DESCRIPTORS:
            print(f"[decompose] {desc:14s} dominant={info['dominant_axis']:11s} "
                  f"phi_A={info['phi_allocation']} phi_E={info['phi_envelope']}")
    print(f"[decompose] wrote {out_dir}")
    return out_dir
