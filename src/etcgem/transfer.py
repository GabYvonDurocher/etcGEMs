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
    fixed_globals: {dTm: -5.43}      # PINNED, not fitted -- see below
    objective: measured_tpc
    optimizer: {method: nelder-mead, multistart: 4, starts: [[...], ...], options: {...}}
    detection_floor_h: 0.05

``fixed_globals`` pins a global at a stated value instead of fitting it (K8). It is the same
Perturbation vocabulary as ``globals`` and the two must not name the same parameter. It exists
so that a MEASURED correction can be applied and reported as an experiment -- K8 applies A1's
measured Seq2Tm bias this way -- without either fitting it or editing a strain default. A pinned
value is recorded in the run's ``calibration.json`` under ``fixed`` so it cannot be mistaken for
a fitted one.

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
from .tpc import TPC, compute_tpc

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
    ``gem/22_thermal_sensitivity.py``.

    ``lo`` must be a temperature at which the model is still above the floor, i.e. the
    bracket has to start on the warm side of the rising limb. The caller passes the strain's
    own peak temperature for that reason: the standalone's fixed 20 C works for a Gaussian
    rising limb but not for the unfolding form, whose cold limb is Arrhenius and can be
    below the detection floor at 20 C while the curve peaks perfectly well at 36 C. Starting
    from the peak gives the same answer wherever both brackets are valid (growth is monotone
    above the peak) and a valid one where the fixed bracket is not."""
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


def pool_binds(pm, pert, T_C: float, slack: float = 1000.0):
    """Does the proteome pool actually constrain growth at this temperature?

    Solve as configured, then with the metabolic pool budget multiplied by ``slack`` (i.e.
    effectively removed), then with every enzyme-mass cap removed. Returns
    (mu_configured, mu_pool_free, mu_all_caps_free, pool_binds). A eukaryote given a
    literature-grounded budget may leave the pool slack, in which case the model has
    collapsed to a plain GEM and says so here rather than silently; and once sectors are
    wired, the pool may be slack because the TRANSLATION CAP binds instead, which the third
    value distinguishes."""
    mu_cfg = float(_growth(pm, [T_C], pert)[0])
    budget = pert.budget if pert.budget is not None else pm.ec.default_budget
    mu_free = float(_growth(pm, [T_C], _replace(pert, budget=float(budget) * slack))[0])
    # With proteome sectors wired, the metabolic pool is not the only enzyme-mass
    # constraint: the biosynthesis/translation cap can bind instead (and by construction
    # does, when translation_coeff is auto-calibrated to co-limit at the nominal point).
    # Relax it too, so "nothing binds" and "something else binds" are distinguishable.
    mu_all = mu_free
    sect = getattr(pm.ec, "_sectors", None)
    if sect is not None and sect.get("bio_constraint") is not None:
        bio = sect["bio_constraint"]
        keep = bio.ub
        try:
            bio.ub = keep * slack
            mu_all = float(_growth(pm, [T_C], _replace(pert, budget=float(budget) * slack))[0])
        finally:
            bio.ub = keep
            pm.ec.model.solver.update()
    return mu_cfg, mu_free, mu_all, bool(mu_free > mu_cfg * (1.0 + 1e-6))


def _replace(pert: Perturbation, **kw) -> Perturbation:
    import dataclasses
    return dataclasses.replace(pert, **kw)


def fit_r2(pred: np.ndarray, meas: np.ndarray) -> float:
    """Coefficient of determination of the prediction against the measured curve,
    1 - SS_res/SS_tot -- the same quantity the E. coli work reports as 'fit R^2'. Negative
    values mean the prediction is worse than the measured mean, which is informative and is
    not clipped."""
    meas = np.asarray(meas, float)
    pred = np.asarray(pred, float)
    ok = np.isfinite(meas) & np.isfinite(pred)
    if ok.sum() < 2:
        return float("nan")
    ss_res = float(np.sum((meas[ok] - pred[ok]) ** 2))
    ss_tot = float(np.sum((meas[ok] - meas[ok].mean()) ** 2))
    return float("nan") if ss_tot <= 0 else 1.0 - ss_res / ss_tot


def required_separation(pm, pert, scale: float, param: str, T_fail: float,
                        T_perm: float, threshold: float, perm_frac: float,
                        lo: float = -35.0, tol: float = 0.1):
    """The uniform downward shift of one thermal parameter that a strain's enzymes need
    before the model puts it below the detection threshold at ``T_fail``.

    This is the counterfactual behind Figure 4 of the Candida work
    (gem/19_etcgem_counterfactual.py), expressed against the core's own perturbation
    vocabulary so it can be asked of any thermal form: ``param`` is a Perturbation field
    (dTm or dTopt), applied uniformly to every enzyme of this strain only.

    Returns a dict with the required separation (= -shift, positive degrees), whether the
    strain still grows at the permissive temperature under that shift, and both growth
    rates. ``required=None`` means the strain cannot be pushed below the threshold at all
    within ``lo``, which is itself a result."""
    def mu_at(T, d):
        return float(_growth(pm, [T], _replace(pert, **{param: d}))[0]) * scale

    base_fail = mu_at(T_fail, 0.0)
    base_perm = mu_at(T_perm, 0.0)
    if base_fail < threshold:
        shift = 0.0
    elif mu_at(T_fail, lo) >= threshold:
        return dict(required=None, note=f"cannot fall below {threshold} at {T_fail} C "
                                        f"within {lo} C of {param}",
                    baseline_fail=round(base_fail, 4), baseline_permissive=round(base_perm, 4))
    else:
        a, b = lo, 0.0
        for _ in range(40):
            mid = 0.5 * (a + b)
            if mu_at(T_fail, mid) < threshold:
                a = mid
            else:
                b = mid
            if b - a < tol:
                break
        shift = 0.5 * (a + b)
    perm = mu_at(T_perm, shift)
    return dict(required=round(-shift, 2), permissive_growth=round(perm, 4),
                permissive_baseline=round(base_perm, 4),
                permissive_preserved=bool(perm >= perm_frac * base_perm),
                baseline_fail=round(base_fail, 4))


def run_tag(experiment: str) -> str:
    """Output-folder name for a transfer run: ``transfer_<experiment>``, de-doubled when
    the experiment name already starts with the command (transfer_candida ->
    transfer_candida, not transfer_transfer_candida). Mirrors cli._run_tag."""
    return experiment if experiment.startswith("transfer") else f"transfer_{experiment}"


def run(experiment: str, out_root: str = "outputs", verbose: bool = True,
        solver: Optional[str] = None, tag: Optional[str] = None) -> str:
    """Run one transfer experiment. Returns the top-level output directory.

    ``solver`` overrides the LP solver for this run only (the same experiment can then be
    run under two solvers and the answers compared, rather than the choice being pinned and
    forgotten). ``tag`` overrides the output-folder name, so those two runs do not overwrite
    each other."""
    exp = load_experiment(experiment)
    if exp.get("kind") != "transfer":
        raise ValueError(f"experiment {experiment} is kind={exp.get('kind')!r}, "
                         f"not 'transfer'")
    cal = exp["calibrate_on"]
    predict: List[str] = list(exp.get("predict") or [])
    strains = [cal] + [s for s in predict if s != cal]
    globals_ = list(exp["globals"])
    fixed = dict(exp.get("fixed_globals") or {})
    clash = set(fixed) & set(globals_)
    if clash:
        raise ValueError(f"fixed_globals and globals both name {sorted(clash)}; a parameter "
                         f"is either pinned or fitted, not both")
    for k in fixed:
        if k not in GLOBAL_TO_PERT:
            raise ValueError(f"'{k}' is not a fittable global; known: {sorted(GLOBAL_TO_PERT)}")
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
        if solver:
            cfgs[s]["solver"] = str(solver)
        pms[s] = build_provider(cfgs[s])
        try:
            pms[s].ec.model.solver.configuration.timeout = int(cfgs[s].get("solver_timeout", 10))
        except Exception:
            pass
        if verbose:
            print(f"[transfer] {s}: {len(pms[s].ec.table)} enzyme-costed reactions",
                  flush=True)

    measured = load_measured_tpc(cal, cfgs[cal])
    if globals_:
        if verbose:
            print(f"[transfer] fitting {globals_} on {cal} against "
                  f"{len(measured)} measured points", flush=True)
        x, info = fit_globals(pms[cal], measured, globals_,
                              dict(exp.get("optimizer") or {}),
                              growth_scale, lower_bounds, verbose=verbose)
    else:
        # No free globals: every parameter is grounded, so there is nothing to fit and the
        # curve is an a-priori PREDICTION. Reported, not worked around -- it is the point of
        # the later rungs of the K2 ladder.
        if verbose:
            print(f"[transfer] no free globals: {cal} is predicted, not fitted", flush=True)
        x, info = np.zeros(0), dict(mse=float("nan"), n_eval=0, method="none",
                                    starts=[], options={})
    fitted = {k: float(v) for k, v in zip(globals_, x)}
    # pinned values are applied exactly like fitted ones, and recorded separately so the two
    # can never be confused in a committed output
    pert = _pert(list(globals_) + list(fixed), list(x) + [float(v) for v in fixed.values()])
    if fixed:
        print(f"[transfer] pinned (not fitted): {fixed}", flush=True)

    # the frozen growth scale, from the calibration strain at the fitted point
    pred_cal = _growth(pms[cal], measured["T_C"].values.astype(float), pert)
    scale = _scale(pred_cal, measured["mu"].values.astype(float), growth_scale)

    tag = tag or run_tag(experiment)
    out_dir = os.path.join(out_root, tag)
    os.makedirs(out_dir, exist_ok=True)
    calib = dict(experiment=experiment, calibrate_on=cal, predict=predict,
                 globals=globals_, fitted=fitted, growth_scale=growth_scale,
                 scale=float(scale), detection_floor_h=floor, **info)
    # `fixed` is written ONLY when something is pinned. Writing it unconditionally added an
    # empty key to every run's calibration.json and so made every committed transfer output
    # stale on re-run -- the exact stale-at-commit hazard docs/OPEN_ITEMS.md section 4 lists.
    # Caught by K9 TASK 0's byte-identity check; introduced by K8.
    if fixed:
        calib["fixed"] = fixed
    with open(os.path.join(out_dir, "calibration.json"), "w") as fh:
        json.dump(calib, fh, indent=2)

    dgrid = exp.get("descriptor_grid")
    crit = float(exp.get("crit_frac", 0.05))
    cf = dict(exp.get("counterfactual") or {})
    rows, cf_rows = [], []
    for s in strains:
        temps = temperature_grid(cfgs[s])
        g = _growth(pms[s], temps, pert)
        per = pd.DataFrame({"temp_C": temps, "growth": g, "mu_pred": g * scale})
        meas_col = np.full(len(temps), np.nan)
        try:
            m = load_measured_tpc(s, cfgs[s]).set_index("T_C")["mu"]
            meas_col = np.array([float(m.get(round(float(t), 6), np.nan)) for t in temps])
        except Exception:
            pass
        per["mu_measured"] = meas_col
        s_out = os.path.join(strain_dir(s), "outputs", tag)
        os.makedirs(s_out, exist_ok=True)
        per.to_csv(os.path.join(s_out, "tpc.csv"), index=False)
        from .sectors import record_flatness
        record_flatness(cfgs[s], temps, g, s_out, label=f"{experiment}:{s}")
        dump_resolved(cfgs[s], s_out)
        i_peak = int(np.argmax(g))
        peak_T = float(temps[i_peak])
        limit = thermal_limit(pms[s], pert, scale, floor,
                              lo=max(float(lim.get("lo_C", 20.0)), peak_T),
                              hi=float(lim.get("hi_C", 90.0)),
                              tol=float(lim.get("tol_C", 0.02)))
        # does the pool still bind, at this strain's own peak?
        mu_cfg, mu_free, mu_all, binds = pool_binds(pms[s], pert, peak_T)
        row = dict(strain=s, role=("calibrate_on" if s == cal else "predict"),
                   growth_scale=scale, thermal_limit_C=limit,
                   peak_mu=float(np.max(g) * scale), peak_T_C=peak_T,
                   peak_mu_model=float(np.max(g)),
                   pool_binds=binds,
                   mu_pool_free_model=float(mu_free),
                   pool_binding_ratio=(float(mu_free / mu_cfg) if mu_cfg > 0 else float("inf")),
                   mu_all_caps_free_model=float(mu_all),
                   all_caps_ratio=(float(mu_all / mu_cfg) if mu_cfg > 0 else float("inf")),
                   fit_r2=fit_r2(g * scale, meas_col))
        # descriptors on a wider grid, when one is configured: the strain grid stops at the
        # top of the ASSAY range (44 C), well below any model CTmax, so Topt/rmax/CTmax read
        # off it would be truncated.
        if dgrid:
            wide = np.linspace(dgrid["start_C"], dgrid["stop_C"], int(dgrid["n"]))
            gw = _growth(pms[s], wide, pert)
            d = TPC(wide, gw * scale).descriptors(crit)
            pd.DataFrame({"temp_C": wide, "growth": gw, "mu_pred": gw * scale}).to_csv(
                os.path.join(s_out, "tpc_wide.csv"), index=False)
            row.update(descr_Topt_C=d.Topt_C, descr_rmax=d.rmax, descr_CTmax_C=d.CTmax_C,
                       descr_CTmin_C=d.CTmin_C, descr_Ea_eV=d.Ea_eV)
        # median enzyme Tm actually carried by this strain's cost table (K)
        tms = [e.Tm for e in pms[s].ec.table if e.Tm is not None and np.isfinite(e.Tm)]
        row["median_enzyme_Tm_C"] = (float(np.median(tms)) - 273.15) if tms else float("nan")
        row.update(fitted)
        for t, v in zip(temps, g * scale):
            row[f"mu_{t:g}C"] = float(v)
        for t, v in zip(temps, g):
            row[f"model_mu_{t:g}C"] = float(v)
        rows.append(row)
        if verbose:
            print(f"[transfer] {s}: peak {row['peak_mu']:.4f}/h at {peak_T:.0f}C "
                  f"(model units {row['peak_mu_model']:.4f}), thermal limit {limit:.2f}C at "
                  f"mu>={floor}, pool binds={binds} (x{row['pool_binding_ratio']:.2f} pool-free, "
                  f"x{row['all_caps_ratio']:.2f} all-caps-free), "
                  f"R2={row['fit_r2']:.3f}", flush=True)
        # the Figure-4 counterfactual, on the predicted strains only
        if cf and s != cal:
            for param in cf.get("params", ["dTm", "dTopt"]):
                r = required_separation(
                    pms[s], pert, scale, param,
                    T_fail=float(cf.get("fail_T_C", 40.0)),
                    T_perm=float(cf.get("permissive_T_C", 34.0)),
                    threshold=float(cf.get("threshold_h", floor)),
                    perm_frac=float(cf.get("permissive_frac", 0.7)),
                    lo=float(cf.get("lo", -35.0)), tol=float(cf.get("tol", 0.1)))
                r.update(strain=s, param=param, experiment=experiment)
                cf_rows.append(r)
                if verbose:
                    print(f"[transfer]   counterfactual {s} {param}: required "
                          f"{r.get('required')} C, permissive preserved="
                          f"{r.get('permissive_preserved')}", flush=True)
    pd.DataFrame(rows).to_csv(os.path.join(out_dir, "summary.csv"), index=False)
    if cf_rows:
        cols = ["experiment", "strain", "param", "required", "permissive_preserved",
                "permissive_growth", "permissive_baseline", "baseline_fail", "note"]
        d = pd.DataFrame(cf_rows)
        d = d[[c for c in cols if c in d.columns]]
        d.to_csv(os.path.join(out_dir, "counterfactual.csv"), index=False)
    if verbose:
        print(f"[transfer] fitted {fitted}, scale {scale:.6f}, mse {info['mse']:.6f}")
        print(f"[transfer] wrote {out_dir}/summary.csv and per-strain "
              f"strains/*/outputs/{tag}/")
    return out_dir
