#!/usr/bin/env python3
"""P11 TASK 1 -- prove the prior transform two ways.

(1) 10,000 draws through the transform: marginal mean and the 5/25/50/75/95 % quantiles of the
    NATURAL value against the analytic truncated distribution (scipy.stats.truncnorm) each
    parameter's prior is.
(2) The stronger check: on a grid of 200 points per parameter, the difference between that
    parameter's contribution to calibration_multi.log_prior and the log-density implied by the
    transform must be CONSTANT (the truncation normaliser). Its spread over the grid is
    reported; anything above 1e-9 is a mismatch.
Writes task1_transform.csv and task1_transform.json beside this file.
"""
import json, os, sys
import numpy as np, pandas as pd
from scipy.stats import norm, truncnorm
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src")); sys.path.insert(0, HERE); os.chdir(ROOT)
from etcgem.calibration_multi import build_gasflux_specs, log_prior     # noqa: E402
from prior_transform import transform_factory                          # noqa: E402

specs = build_gasflux_specs({"use_etc": False, "fit_clearance": True}); D = len(specs)
pt = transform_factory(specs)
rng = np.random.default_rng(0); U = rng.random((10000, D))
TH = np.array([pt(u) for u in U])
NAT = np.array([[np.exp(TH[i, j]) if s.space == "log" else TH[i, j] for j, s in enumerate(specs)] for i in range(len(TH))])
QS = [5, 25, 50, 75, 95]
rows = []
for j, s in enumerate(specs):
    if s.prior == "normal":   c, sc, l, h = s.loc, s.scale, s.lo, s.hi
    elif s.prior == "lognormal": c, sc, l, h = s.log_center, s.scale, np.log(s.lo), np.log(s.hi)
    else:                     c, sc, l, h = 0.0, s.scale, s.lo, s.hi
    rv = truncnorm((l - c) / sc, (h - c) / sc, loc=c, scale=sc)
    emp = NAT[:, j] if s.prior != "lognormal" else np.log(NAT[:, j])
    r = dict(param=s.name, prior=s.prior, space=("v" if s.prior != "lognormal" else "log v"),
             mean_draws=float(emp.mean()), mean_analytic=float(rv.mean()), d_mean=float(emp.mean() - rv.mean()))
    for q in QS:
        r[f"q{q}_draws"] = float(np.percentile(emp, q)); r[f"q{q}_analytic"] = float(rv.ppf(q / 100))
    r["max_abs_quantile_error"] = max(abs(r[f"q{q}_draws"] - r[f"q{q}_analytic"]) for q in QS)
    r["mc_se_of_mean"] = float(emp.std() / np.sqrt(len(emp)))
    # (2) density consistency on a grid
    grid_v = np.linspace(l + 1e-6 * (h - l), h - 1e-6 * (h - l), 200)
    # the density the transform induces, IN THE SPACE log_prior scores (theta). For `normal`
    # and `lognormal` the inversion is already in that space. For `halfnormal` the inversion is
    # in v while theta = log v, so the induced theta-density carries the Jacobian +log v --
    # which is exactly the "+ theta" term log_prior adds.
    logdens_transform = norm.logpdf(grid_v, loc=c, scale=sc)          # up to the truncation constant
    if s.prior == "halfnormal":
        logdens_transform = logdens_transform + np.log(grid_v)
    diffs = []
    base = np.array([0.0] * D)
    for j2, s2 in enumerate(specs):     # a valid theta to fill the other coordinates
        base[j2] = np.log(np.sqrt(s2.lo * s2.hi)) if s2.space == "log" else 0.5 * (s2.lo + s2.hi)
    for gv, ld in zip(grid_v, logdens_transform):
        th = base.copy()
        th[j] = gv if s.prior != "halfnormal" else np.log(gv)
        # this parameter's contribution: log_prior(theta) - log_prior(theta with j at the base)
        full = log_prior(th, specs); ref = log_prior(base, specs)
        # the reference contribution of j, computed analytically, cancels in the spread
        diffs.append(full - ref - ld)
    d = np.array(diffs); d = d[np.isfinite(d)]
    r["density_check_spread"] = float(d.max() - d.min()); r["density_check_n"] = int(len(d))
    rows.append(r)
    print(f"[pt] {s.name:16s} {s.prior:11s} mean draws {r['mean_draws']:9.4f} vs analytic {r['mean_analytic']:9.4f} "
          f"(MC se {r['mc_se_of_mean']:.4f}); max |quantile err| {r['max_abs_quantile_error']:.4f}; "
          f"log-density spread over 200 grid points {r['density_check_spread']:.2e}", flush=True)
df = pd.DataFrame(rows); df.to_csv(os.path.join(HERE, "task1_transform.csv"), index=False)
ok = bool((df.density_check_spread < 1e-9).all())
json.dump(dict(n_draws=10000, all_densities_consistent=ok, max_density_spread=float(df.density_check_spread.max()),
               max_quantile_error=float(df.max_abs_quantile_error.max()),
               worst_mean_z=float((np.abs(df.d_mean) / df.mc_se_of_mean).max())), open(os.path.join(HERE, "task1_transform.json"), "w"), indent=1)
print(f"[pt] density consistent for every parameter: {ok} (max spread {df.density_check_spread.max():.2e}); "
      f"largest |mean - analytic| in MC se: {(np.abs(df.d_mean)/df.mc_se_of_mean).max():.2f}", flush=True)
print("[pt] done")
