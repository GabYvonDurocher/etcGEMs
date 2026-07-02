"""Sensitivity analysis: sweep proteome allocation and kcat(T) responses.

Draws a Latin-hypercube sample over the perturbation parameters, computes a TPC
for each point, and reduces the ensemble to descriptor distributions plus
Spearman sensitivity indices (a PRCC-style measure of how strongly each input
moves each TPC feature).

Perturbation parameters (any subset can be swept):
    dTopt        shift (K) applied to every enzyme optimum
    topt_scale   scales the spread of enzyme optima about T0 (heterogeneity)
    dCp_scale    scales heat capacity of activation (curvature / breadth)
    budget_scale multiplies the total proteome pool (global allocation)
    alloc_<grp>  multiplies a group's sub-budget (allocation between pathways)
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Dict, List, Sequence, Tuple

import numpy as np
import pandas as pd

from .enzyme_cost import Perturbation
from .tpc import TPC, compute_tpc


def _lhs(n: int, d: int, seed: int) -> np.ndarray:
    """Latin-hypercube sample in the unit cube (scipy if present, else numpy)."""
    try:
        from scipy.stats.qmc import LatinHypercube
        return LatinHypercube(d=d, seed=seed).random(n)
    except Exception:
        rng = np.random.default_rng(seed)
        cut = (np.arange(n)[:, None] + rng.random((n, d))) / n
        return np.take_along_axis(cut, rng.random((n, d)).argsort(0), 0)


def _make_perturbation(sample: Dict[str, float], default_budget: float,
                       group_names: Sequence[str]) -> Perturbation:
    p = Perturbation(
        dTopt=sample.get("dTopt", 0.0),
        topt_scale=sample.get("topt_scale", 1.0),
        dCp_scale=sample.get("dCp_scale", 1.0),
    )
    if "budget_scale" in sample:
        p.budget = default_budget * sample["budget_scale"]
    for g in group_names:
        key = f"alloc_{g}"
        if key in sample:
            p.group_alloc[g] = sample[key]
    # proteome-sector allocation (opt-in; only used when sectors are wired)
    if "f_metab" in sample:
        p.f_metab = sample["f_metab"]
    if "f_maint" in sample:
        p.f_maint = sample["f_maint"]
    if "maint_to_bio" in sample:
        p.maint_to_bio = sample["maint_to_bio"]
    return p


@dataclass
class SensitivityResult:
    temps_C: np.ndarray
    curves: np.ndarray                 # (n_samples, n_temps)
    samples: pd.DataFrame              # sampled inputs
    descriptors: pd.DataFrame          # one row per sample
    sensitivity: pd.DataFrame          # Spearman rho, inputs x descriptors
    nominal: TPC                       # unperturbed reference curve

    def save(self, out_dir: str):
        os.makedirs(out_dir, exist_ok=True)
        np.save(os.path.join(out_dir, "temps_C.npy"), self.temps_C)
        np.save(os.path.join(out_dir, "curves.npy"), self.curves)
        self.samples.to_csv(os.path.join(out_dir, "samples.csv"), index=False)
        self.descriptors.to_csv(os.path.join(out_dir, "descriptors.csv"), index=False)
        self.sensitivity.to_csv(os.path.join(out_dir, "sensitivity_spearman.csv"))
        pd.DataFrame({"temp_C": self.nominal.temps_C,
                      "growth": self.nominal.growth}).to_csv(
            os.path.join(out_dir, "nominal_tpc.csv"), index=False)


def run_sensitivity(pm, temps_C: Sequence[float],
                    param_ranges: Dict[str, Tuple[float, float]],
                    n_samples: int = 200, seed: int = 1,
                    group_names: Sequence[str] = (),
                    crit_frac: float = 0.05,
                    envelope_samples=None,
                    progress: bool = True) -> SensitivityResult:
    """LHS sweep over param_ranges.

    ``envelope_samples`` (optional): a list of n_samples per-enzyme thermal draws
    (thermal_sampling.sample_thermal). When given, each sample's per-enzyme
    Topt/dCp is applied (mutating entries) before its TPC instead of the
    dTopt/topt_scale/dCp_scale knobs; the shared latent Z is recorded as a
    sensitivity input. When None, behaviour is exactly as before.
    """
    temps_C = np.asarray(temps_C, float)
    default_budget = pm.ec.default_budget
    names = list(param_ranges.keys())
    U = _lhs(n_samples, len(names), seed)

    # scale unit cube to parameter ranges
    sampled = {}
    for j, name in enumerate(names):
        lo, hi = param_ranges[name]
        sampled[name] = lo + U[:, j] * (hi - lo)
    samples_df = pd.DataFrame(sampled)

    use_env = envelope_samples is not None
    if use_env:
        from .thermal_sampling import (nominal_thermal, apply_thermal_sample,
                                        restore_thermal)
        nomT, nomC = nominal_thermal(pm)
        samples_df = samples_df.copy()
        samples_df["thermal_Z"] = [envelope_samples[i]["Z"] for i in range(n_samples)]

    curves = np.zeros((n_samples, len(temps_C)))
    desc_rows: List[dict] = []
    for i in range(n_samples):
        row = {k: float(samples_df.iloc[i][k]) for k in names}
        pert = _make_perturbation(row, default_budget, group_names)
        if use_env:
            apply_thermal_sample(pm, envelope_samples[i])
        tpc = compute_tpc(pm, temps_C, pert)
        curves[i] = tpc.growth
        desc_rows.append(tpc.descriptors(crit_frac).as_dict())
        if progress and (i + 1) % max(1, n_samples // 10) == 0:
            print(f"[sensitivity] {i + 1}/{n_samples}")
    if use_env:
        restore_thermal(pm, nomT, nomC)
    desc_df = pd.DataFrame(desc_rows)

    nominal = compute_tpc(pm, temps_C, Perturbation())
    sens = _spearman_matrix(samples_df, desc_df)
    return SensitivityResult(temps_C, curves, samples_df, desc_df, sens, nominal)


def _spearman_matrix(inputs: pd.DataFrame, outputs: pd.DataFrame) -> pd.DataFrame:
    from scipy.stats import spearmanr
    out = pd.DataFrame(index=inputs.columns, columns=outputs.columns, dtype=float)
    for a in inputs.columns:
        for b in outputs.columns:
            y = outputs[b].values
            m = np.isfinite(y)
            if m.sum() < 3 or np.nanstd(y[m]) == 0:
                out.loc[a, b] = np.nan
            else:
                out.loc[a, b] = spearmanr(inputs[a].values[m], y[m]).correlation
    return out
