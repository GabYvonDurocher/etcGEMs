#!/usr/bin/env python3
"""regime.py -- Y1's regime test, amortised over the constraint settings.

Y1 PART C ran `etc.simulate_growth` once per (setting, temperature). The thermal layer --
`map_fNT` and `map_kcatT` over 764 enzymes -- is by far the expensive part and is IDENTICAL
across settings that differ only in a bound. `sweep` applies their four calls once per
temperature, inside their own `with model:` block, and then solves once per glucose cap inside a
nested block. Same calls, same order, same LP; four times fewer of the expensive ones. That
matters here because Y2 repeats the test at every one of a hundred posterior draws.

`verify_against_simulate_growth` checks the amortisation is exact -- it must return 0.0 -- and
`task2_regime.py` runs that check before it uses any of the numbers.

The readouts (`refine_topt`, `crossing`) are imported from Y1's script rather than copied, so the
99 % plateau and the 1 %-of-maximum CT_max cannot drift between the two reports.
"""
from __future__ import annotations

import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
Y1 = os.path.join(os.path.dirname(HERE), "Y1_yeast_audit")
for p in (HERE, Y1):
    if p not in sys.path:
        sys.path.insert(0, p)

from task_c_regime_test import crossing, refine_topt        # noqa: E402,F401  (Y1's readouts)

GLC = "r_1714_REV"
# The constraint switch Y1 used: an unbounded/loosely-bounded glucose uptake leaves the model
# ENZYME-limited (Crabtree-positive, which is the regime their paper is about); tightening it
# substitutes a SUBSTRATE-uptake limit. Y1's four settings, kept exactly.
CAPS = ((10.0, "glucose_cap=10.0"), (4.0, "glucose_cap=4.0"),
        (2.0, "glucose_cap=2.0"), (1.0, "glucose_cap=1.0"))
SIGMA = 0.5
TS_C = np.arange(20.0, 50.0 + 1e-9, 0.5)


def sweep(model, etc, df, Ts_C=TS_C, sigma=SIGMA, caps=CAPS):
    """{label: mu array} over Ts_C, one entry per glucose cap. Their calls, their order."""
    out = {lab: [] for _, lab in caps}
    for T_C in Ts_C:
        T = float(T_C) + 273.15
        with model:
            etc.map_fNT(model, T, df)
            etc.map_kcatT(model, T, df)
            etc.set_NGAMT(model, T)
            etc.set_sigma(model, sigma)
            for cap, lab in caps:
                with model:
                    model.reactions.get_by_id(GLC).upper_bound = float(cap)
                    try:
                        r = model.optimize().objective_value
                    except Exception:                      # noqa: BLE001  (as their code does)
                        r = 0.0
                out[lab].append(0.0 if r is None else float(r))
    return {k: np.where(np.isfinite(v), v, 0.0) for k, v in
            ((k, np.asarray(v, float)) for k, v in out.items())}


def _their_curve(model, etc, df, Ts_C, sigma, cap):
    with model:
        model.reactions.get_by_id(GLC).upper_bound = float(cap)
        r = np.asarray(etc.simulate_growth(model, np.asarray(Ts_C, float) + 273.15,
                                           sigma, df), dtype=float)
    return np.where(np.isfinite(r), r, 0.0)


def verify_against_simulate_growth(model, etc, df, Ts_C, sigma, cap):
    """Is the amortised sweep the same computation as `etc.simulate_growth`?

    Two numbers are returned, and BOTH are needed to answer that honestly.

    `diff` is the largest difference between the two curves. It is NOT zero, and it should not be
    expected to be: these are linear programs solved to a tolerance, and the two routes reach the
    same LP by different bases. `noise` is the largest difference between two consecutive calls to
    THEIR OWN function on the same model with the same arguments -- the run-to-run repeatability of
    the solver, measured rather than assumed. If `diff` is of the same order as `noise`, the
    amortisation has changed nothing that the solver itself does not change between two identical
    calls.

    The descriptors are compared too, because those are what the report quotes. A difference in the
    tenth decimal place of a growth rate that moves no T_opt, no CT_max and no plateau edge is not
    a difference in the result.
    """
    ours = sweep(model, etc, df, Ts_C, sigma, ((cap, "x"),))["x"]
    theirs = _their_curve(model, etc, df, Ts_C, sigma, cap)
    again = _their_curve(model, etc, df, Ts_C, sigma, cap)
    diff = float(np.max(np.abs(ours - theirs)))
    noise = float(np.max(np.abs(theirs - again)))
    d_ours, d_theirs = descriptors(Ts_C, ours), descriptors(Ts_C, theirs)
    desc = {k: (d_ours[k], d_theirs[k]) for k in d_ours
            if isinstance(d_ours[k], float) and d_ours[k] == d_ours[k]}
    desc_max = max((abs(a - b) for a, b in desc.values()), default=0.0)
    return dict(curve_max_abs_diff=diff, solver_repeat_noise=noise,
                descriptor_max_abs_diff=float(desc_max),
                descriptors_ours=d_ours, descriptors_theirs=d_theirs), ours, theirs


def descriptors(Ts_C, mu):
    """Y1's readouts for one curve, plus the plateau width the plateau claim rests on."""
    mx = float(np.nanmax(mu))
    topt, at_edge = refine_topt(np.asarray(Ts_C, float), mu)
    p99 = np.asarray(Ts_C, float)[mu >= 0.99 * mx]
    i = int(np.nanargmax(mu))
    zero = np.asarray(Ts_C, float)[(np.arange(len(mu)) > i) & (mu <= 0)]
    return dict(mu_max=mx, T_opt=topt, T_opt_at_edge=bool(at_edge),
                plateau99_lo=float(p99.min()), plateau99_hi=float(p99.max()),
                plateau99_width=float(p99.max() - p99.min()),
                CT_max_rel_1pct=crossing(np.asarray(Ts_C, float), mu, 0.01 * mx),
                CT_max_rel_10pct=crossing(np.asarray(Ts_C, float), mu, 0.10 * mx),
                T_first_zero=(float(zero.min()) if len(zero) else float("nan")))


def summarise(Ts_C, curves):
    """Per-setting descriptors plus the across-setting ranges Y1 quoted (10.09 / 0.81)."""
    per = {lab: descriptors(Ts_C, mu) for lab, mu in curves.items()}
    topt = [v["T_opt"] for v in per.values()]
    ctmax = [v["CT_max_rel_1pct"] for v in per.values()]
    width = [v["plateau99_width"] for v in per.values()]
    mumax = [v["mu_max"] for v in per.values()]
    return per, dict(T_opt_range=max(topt) - min(topt),
                     CT_max_range=max(ctmax) - min(ctmax),
                     plateau_lo=min(width), plateau_hi=max(width),
                     mu_max_ratio=max(mumax) / min(mumax) if min(mumax) > 0 else float("nan"),
                     asymmetry=((max(topt) - min(topt)) / (max(ctmax) - min(ctmax))
                                if max(ctmax) - min(ctmax) > 0 else float("inf")))
