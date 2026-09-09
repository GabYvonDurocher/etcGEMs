#!/usr/bin/env python3
"""task_c_regime_test.py -- Y1 PART C: does T_opt move under a capacity constraint while CT_max
does not, in the PUBLISHED yeast etcGEM, run with the PUBLISHED thermal layer?

    python3 reports/Y1_yeast_audit/task_c_regime_test.py --bayesiangem /path/to/BayesianGEM

THE CLAIM UNDER TEST, from this project's own work on E. coli, three Candida species, a
methanogen and a phototroph: T_opt is REGIME-DETERMINED -- it moves when you change which
constraint binds -- while CT_max is STABILITY-DETERMINED and barely moves at all. That was shown
in one codebase. Testing it in someone else's, on someone else's organism, is the
generalisation.

NOTHING IS RE-IMPLEMENTED. Growth at each temperature comes from `etc.simulate_growth`, their
function, on their model, with their `data/model_enzyme_params.csv`. The only shim is the
bounds-order one in `set_NGAMT` (DECISIONS.md 7).

TWO CAPACITY LEVERS, both theirs.
  sigma   the enzyme saturation factor. `etc.set_sigma` sets the protein pool upper bound to
          0.17866*sigma, so this is the enzyme-capacity constraint in its purest form. Their
          calibrated value is 0.5.
  glucose the upper bound on `r_1714_REV`. In the deposited aerobic model this is unbounded --
          growth is protein-limited, which is what makes the model Crabtree-positive -- so
          capping it substitutes a substrate-uptake limit for the enzyme limit and changes
          WHICH constraint binds. That is the regime change the claim is about.

READOUTS. T_opt is the argmax of the curve, refined by a parabola through the three points
around the maximum. CT_max is where the falling limb crosses 1 % of THAT curve's own maximum,
linearly interpolated -- a relative threshold, because a capacity cut scales the whole curve and
an absolute threshold would move for that reason alone. The absolute crossing of 0.01 h^-1 is
recorded beside it so the choice can be checked.

Writes task_c_curves.csv (every point) and task_c_summary.csv (one row per setting).
"""
from __future__ import annotations

import argparse
import logging
import os
import sys
import warnings

import numpy as np
import pandas as pd

logging.getLogger("cobra").setLevel(logging.ERROR)
warnings.filterwarnings("ignore")

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from task_b_coupling_audit import AEROBIC, load_etcpy      # noqa: E402
from yeast_model import load                               # noqa: E402

GLC = "r_1714_REV"


def refine_topt(T, mu):
    """argmax, refined by a parabola through the three points around the discrete maximum."""
    i = int(np.nanargmax(mu))
    if i in (0, len(T) - 1):
        return float(T[i]), True
    x0, x1, x2 = T[i - 1], T[i], T[i + 1]
    y0, y1, y2 = mu[i - 1], mu[i], mu[i + 1]
    denom = (y0 - 2 * y1 + y2)
    if abs(denom) < 1e-15:
        return float(x1), False
    return float(x1 - 0.5 * (x2 - x0) * (y2 - y0) / (2 * denom) / 2), False


def crossing(T, mu, level):
    """Temperature at which the falling limb crosses `level`, linearly interpolated."""
    i = int(np.nanargmax(mu))
    for j in range(i, len(T) - 1):
        if mu[j] >= level > mu[j + 1]:
            f = (mu[j] - level) / (mu[j] - mu[j + 1])
            return float(T[j] + f * (T[j + 1] - T[j]))
    return float("nan")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bayesiangem", required=True)
    ap.add_argument("--tmin", type=float, default=20.0)
    ap.add_argument("--tmax", type=float, default=50.0)
    ap.add_argument("--step", type=float, default=0.5)
    args = ap.parse_args()
    bg = os.path.abspath(args.bayesiangem)
    etc = load_etcpy(bg)
    params = etc.calculate_thermal_params(
        pd.read_csv(os.path.join(bg, "data", "model_enzyme_params.csv"), index_col=0))
    Ts = np.arange(args.tmin, args.tmax + 1e-9, args.step)

    settings = [("sigma", 0.5, None), ("sigma", 0.4, None), ("sigma", 0.3, None),
                ("sigma", 0.2, None), ("sigma", 0.1, None),
                ("glucose_cap", 0.5, 10.0), ("glucose_cap", 0.5, 4.0),
                ("glucose_cap", 0.5, 2.0), ("glucose_cap", 0.5, 1.0)]

    curves, rows = [], []
    for lever, sigma, glc in settings:
        m, _ = load(os.path.join(bg, "models", AEROBIC))
        if glc is not None:
            m.reactions.get_by_id(GLC).upper_bound = glc
        mu = np.array(etc.simulate_growth(m, Ts + 273.15, sigma, params), dtype=float)
        mu = np.where(np.isfinite(mu), mu, 0.0)
        label = f"{lever}={sigma if lever == 'sigma' else glc}"
        for t, v in zip(Ts, mu):
            curves.append(dict(lever=lever, sigma=sigma, glucose_cap=glc, label=label,
                               T_C=float(t), mu=float(v)))
        topt, edge = refine_topt(Ts, mu)
        mx = float(np.nanmax(mu))
        rows.append(dict(lever=lever, sigma=sigma, glucose_cap=glc, label=label,
                         mu_max=mx, T_opt=topt, T_opt_at_edge=edge,
                         CT_max_rel_1pct=crossing(Ts, mu, 0.01 * mx),
                         CT_max_rel_10pct=crossing(Ts, mu, 0.10 * mx),
                         CT_max_abs_0p01=crossing(Ts, mu, 0.01)))
        print(f"[y1c] {label:18s} mu_max={mx:.4f}  T_opt={topt:6.2f} C  "
              f"CT_max(1% rel)={rows[-1]['CT_max_rel_1pct']:6.2f} C  "
              f"CT_max(10% rel)={rows[-1]['CT_max_rel_10pct']:6.2f} C  "
              f"CT_max(0.01 abs)={rows[-1]['CT_max_abs_0p01']:6.2f} C", flush=True)

    pd.DataFrame(curves).to_csv(os.path.join(HERE, "task_c_curves.csv"), index=False)
    s = pd.DataFrame(rows)
    s.to_csv(os.path.join(HERE, "task_c_summary.csv"), index=False)
    for lever in ("sigma", "glucose_cap"):
        sub = s[s.lever == lever]
        print(f"[y1c] {lever}: mu_max spans {sub.mu_max.min():.4f}-{sub.mu_max.max():.4f} "
              f"({sub.mu_max.max()/sub.mu_max.min():.2f}x); T_opt range "
              f"{sub.T_opt.max()-sub.T_opt.min():.2f} C; CT_max(1%) range "
              f"{sub.CT_max_rel_1pct.max()-sub.CT_max_rel_1pct.min():.2f} C", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
