"""Cross-strain transfer: calibrate global parameters on ONE strain, freeze, predict others.

Every other command in this package runs one strain at a time. This is the multi-strain
experiment kind: an experiment names a strain to ``calibrate_on``, a list of strains to
``predict``, and the *global* (organism-independent, shared) parameters to fit. Those
parameters are fitted against the calibration strain's measured TPC, frozen, and the
whole set of strains is then swept with them. Anything that then differs between strains
comes only from their own per-enzyme parameters -- which is the point of the design.

    kind: transfer
    calibrate_on: cauris_iRV973
    predict: [chaemulonii_draft, ...]
    globals: [pheno_sigma, pheno_w, pool_budget]
    objective: measured_tpc
    optimizer: {method: nelder-mead, multistart: 4, starts: [[...], ...], options: {...}}
    detection_floor_h: 0.05

The sweep itself is ``tpc.compute_tpc`` -- there is no second solver loop here. The
fitted globals are carried as an ``enzyme_cost.Perturbation``, the same object the
sensitivity and calibration code uses, so a global is fittable here exactly when it is a
Perturbation field.

Growth scale. ``growth_scale: peak_match`` reproduces the standalone Candida etcGEM: the
model's absolute rate is not identified by the pool budget alone, so one scale factor
maps the model's peak onto the measured peak of the CALIBRATION strain. It is a profile
parameter -- recomputed inside every objective evaluation from the current prediction,
not a fifth fitted dimension -- and the frozen value is then applied to every strain.
``growth_scale: none`` leaves predictions in model units.
"""
from __future__ import annotations

import json
import os
from typing import Dict, List, Optional, Sequence

import numpy as np
import pandas as pd

from .config import (build_provider, dump_resolved, load_experiment, resolve,
                     strain_dir, temperature_grid)
from .enzyme_cost import Perturbation
from .tpc import compute_tpc

# global name -> the Perturbation field it sets. A global is fittable here exactly when
# it appears in this map; add a Perturbation field and one entry to add another.
GLOBAL_TO_PERT: Dict[str, str] = {
    "pheno_sigma": "pheno_sigma",     # phenomenological Gaussian peak width (K)
    "pheno_w": "pheno_w",             # phenomenological denaturation width (K)
    "pool_budget": "budget",          # total proteome pool P (g enzyme / gDW)
    "kcat_scale": "kcat_scale",       # global turnover level
    "dTopt": "dTopt",                 # uniform shift of every enzyme optimum (K)
    "dTm": "dTm",                     # uniform shift of every enzyme Tm (K)
    "sigma_sat": "sigma_sat",         # effective in-vivo saturation (sectors)
}


def _pert(globals_: Sequence[str], x: Sequence[float]) -> Perturbation:
    kw = {}
    for name, v in zip(globals_, x):
        if name not in GLOBAL_TO_PERT:
            raise ValueError(f"'{name}' is not a fittable global; known: "
                             f"{sorted(GLOBAL_TO_PERT)}")
        kw[GLOBAL_TO_PERT[name]] = float(v)
    return Perturbation(**kw)


def load_measured_tpc(strain: str, cfg: Dict) -> pd.DataFrame:
    """The strain's measured curve as (T_C, mu), dropping missing values.

    Path from ``measured.tpc`` in strain.yaml, resolved against the strain folder.
    Column names are taken as written by tools/reconstruction/to_strain_inputs.py
    (T_C, mu) with a couple of common aliases accepted."""
    rel = (cfg.get("measured") or {}).get("tpc")
    if not rel:
        raise ValueError(f"strain {strain} has no measured.tpc in strain.yaml; "
                         f"objective 'measured_tpc' needs one")
    path = rel if os.path.isabs(rel) else os.path.join(strain_dir(strain), rel)
    df = pd.read_csv(path)
    tcol = next((c for c in ("T_C", "T", "temp_C", "temperature_C") if c in df.columns), None)
    mcol = next((c for c in ("mu", "mu_honest", "growth", "mu_h") if c in df.columns), None)
    if tcol is None or mcol is None:
        raise ValueError(f"{path}: expected a temperature and a growth column, "
                         f"got {list(df.columns)}")
    out = df[[tcol, mcol]].rename(columns={tcol: "T_C", mcol: "mu"}).dropna()
    return out.sort_values("T_C").reset_index(drop=True)


def _growth(pm, temps_C, pert) -> np.ndarray:
    """Model growth at each temperature -- the shared TPC engine, nothing else."""
    return compute_tpc(pm, temps_C, pert).growth


def _scale(pred: np.ndarray, meas: np.ndarray, mode: str) -> float:
    if mode in (None, "none", False):
        return 1.0
    if mode != "peak_match":
        raise ValueError(f"unknown growth_scale {mode!r} (peak_match | none)")
    return float(meas.max() / max(pred.max(), 1e-6))


def thermal_limit(pm, pert, scale: float, floor: float,
                  lo: float = 20.0, hi: float = 90.0, tol: float = 0.02) -> float:
    """Highest temperature at which the scaled prediction still reaches the detection
    floor, by bisection. NaN if the model is already below the floor at ``lo``; inf if it
    is still above it at ``hi``. Same definition and defaults as the standalone's
    ``gem/22_thermal_sensitivity.py``."""
    def mu(T):
        return float(_growth(pm, [T], pert)[0]) * scale
    if mu(lo) < floor:
        return float("nan")
    if mu(hi) >= floor:
        return float("inf")
    a, b = lo, hi
    while b - a > tol:
        mid = 0.5 * (a + b)
        if mu(mid) >= floor:
            a = mid
        else:
            b = mid
    return 0.5 * (a + b)


def fit_globals(pm, measured: pd.DataFrame, globals_: Sequence[str], opt: Dict,
                growth_scale: str, lower_bounds: Dict[str, float],
                verbose: bool = True):
    """Multi-start Nelder-Mead on the calibration strain's measured curve.

    Returns (x, info). The loss is the mean squared error between the peak-matched
    prediction and the measurement at the measured temperatures; a start that violates a
    lower bound returns the standalone's flat penalty rather than an exception, so the
    simplex walks back into the feasible region instead of failing."""
    from scipy.optimize import minimize
    Ts = measured["T_C"].values.astype(float)
    mu = measured["mu"].values.astype(float)
    penalty = float(opt.get("penalty", 1e3))
    n_eval = [0]

    def loss(x):
        for name, v in zip(globals_, x):
            lb = lower_bounds.get(name)
            if lb is not None and v <= lb:
                return penalty
        pred = _growth(pm, Ts, _pert(globals_, x))
        sc = _scale(pred, mu, growth_scale)
        n_eval[0] += 1
        e = float(np.mean((pred * sc - mu) ** 2))
        if verbose and n_eval[0] % 25 == 0:
            print("  eval {:4d}  ".format(n_eval[0])
                  + " ".join(f"{k}={v:.4g}" for k, v in zip(globals_, x))
                  + f"  mse={e:.5f}", flush=True)
        return e

    starts = opt.get("starts")
    if not starts:
        raise ValueError("optimizer.starts must list the multi-start simplex origins")
    if opt.get("multistart") not in (None, len(starts)):
        raise ValueError(f"optimizer.multistart={opt['multistart']} but "
                         f"{len(starts)} starts are listed")
    method = opt.get("method", "nelder-mead")
    options = dict(opt.get("options") or {})
    best = None
    for x0 in starts:
        r = minimize(loss, np.asarray(x0, float), method=method, options=options)
        if verbose:
            print(f"  start {list(x0)} -> mse {r.fun:.6f} after {r.nfev} evaluations",
                  flush=True)
        if best is None or r.fun < best.fun:
            best = r
    info = dict(mse=float(best.fun), n_eval=int(n_eval[0]), method=method,
                starts=[list(map(float, s)) for s in starts], options=options)
    return np.asarray(best.x, float), info


def run_tag(experiment: str) -> str:
    """Output-folder name for a transfer run: ``transfer_<experiment>``, de-doubled when
    the experiment name already starts with the command (transfer_candida ->
    transfer_candida, not transfer_transfer_candida). Mirrors cli._run_tag."""
    return experiment if experiment.startswith("transfer") else f"transfer_{experiment}"


def run(experiment: str, out_root: str = "outputs", verbose: bool = True) -> str:
    """Run one transfer experiment. Returns the top-level output directory."""
    exp = load_experiment(experiment)
    if exp.get("kind") != "transfer":
        raise ValueError(f"experiment {experiment} is kind={exp.get('kind')!r}, "
                         f"not 'transfer'")
    cal = exp["calibrate_on"]
    predict: List[str] = list(exp.get("predict") or [])
    strains = [cal] + [s for s in predict if s != cal]
    globals_ = list(exp["globals"])
    objective = exp.get("objective", "measured_tpc")
    if objective != "measured_tpc":
        raise ValueError(f"unknown objective {objective!r} (measured_tpc)")
    growth_scale = exp.get("growth_scale", "peak_match")
    floor = float(exp.get("detection_floor_h", 0.05))
    lower_bounds = dict(exp.get("lower_bounds") or {})
    lim = dict(exp.get("thermal_limit") or {})

    # build every strain once; the same providers are reused for the fit and the sweep
    cfgs, pms = {}, {}
    for s in strains:
        cfgs[s] = resolve(s, experiment)
        pms[s] = build_provider(cfgs[s])
        try:
            pms[s].ec.model.solver.configuration.timeout = int(cfgs[s].get("solver_timeout", 10))
        except Exception:
            pass
        if verbose:
            print(f"[transfer] {s}: {len(pms[s].ec.table)} enzyme-costed reactions",
                  flush=True)

    measured = load_measured_tpc(cal, cfgs[cal])
    if verbose:
        print(f"[transfer] fitting {globals_} on {cal} against "
              f"{len(measured)} measured points", flush=True)
    x, info = fit_globals(pms[cal], measured, globals_, dict(exp.get("optimizer") or {}),
                          growth_scale, lower_bounds, verbose=verbose)
    fitted = {k: float(v) for k, v in zip(globals_, x)}
    pert = _pert(globals_, x)

    # the frozen growth scale, from the calibration strain at the fitted point
    pred_cal = _growth(pms[cal], measured["T_C"].values.astype(float), pert)
    scale = _scale(pred_cal, measured["mu"].values.astype(float), growth_scale)

    tag = run_tag(experiment)
    out_dir = os.path.join(out_root, tag)
    os.makedirs(out_dir, exist_ok=True)
    calib = dict(experiment=experiment, calibrate_on=cal, predict=predict,
                 globals=globals_, fitted=fitted, growth_scale=growth_scale,
                 scale=float(scale), detection_floor_h=floor, **info)
    with open(os.path.join(out_dir, "calibration.json"), "w") as fh:
        json.dump(calib, fh, indent=2)

    rows = []
    for s in strains:
        temps = temperature_grid(cfgs[s])
        g = _growth(pms[s], temps, pert)
        per = pd.DataFrame({"temp_C": temps, "growth": g, "mu_pred": g * scale})
        try:
            m = load_measured_tpc(s, cfgs[s]).set_index("T_C")["mu"]
            per["mu_measured"] = [float(m.get(round(float(t), 6), np.nan)) for t in temps]
        except Exception:
            per["mu_measured"] = np.nan
        s_out = os.path.join(strain_dir(s), "outputs", tag)
        os.makedirs(s_out, exist_ok=True)
        per.to_csv(os.path.join(s_out, "tpc.csv"), index=False)
        dump_resolved(cfgs[s], s_out)
        limit = thermal_limit(pms[s], pert, scale, floor,
                              lo=float(lim.get("lo_C", 20.0)),
                              hi=float(lim.get("hi_C", 90.0)),
                              tol=float(lim.get("tol_C", 0.02)))
        row = dict(strain=s, role=("calibrate_on" if s == cal else "predict"),
                   growth_scale=scale, thermal_limit_C=limit,
                   peak_mu=float(np.max(g) * scale),
                   peak_T_C=float(temps[int(np.argmax(g))]))
        row.update(fitted)
        for t, v in zip(temps, g * scale):
            row[f"mu_{t:g}C"] = float(v)
        rows.append(row)
        if verbose:
            print(f"[transfer] {s}: peak {row['peak_mu']:.4f}/h at {row['peak_T_C']:.0f}C, "
                  f"thermal limit {limit:.2f}C at mu>={floor}", flush=True)
    pd.DataFrame(rows).to_csv(os.path.join(out_dir, "summary.csv"), index=False)
    if verbose:
        print(f"[transfer] fitted {fitted}, scale {scale:.6f}, mse {info['mse']:.6f}")
        print(f"[transfer] wrote {out_dir}/summary.csv and per-strain "
              f"strains/*/outputs/{tag}/")
    return out_dir
