#!/usr/bin/env python3
"""P11 TASK 1 -- the prior transform from the unit cube to P4's priors, and its proof.

Every parameter of the gas-flux fit is one of three forms (calibration_multi.log_prior), each
TRUNCATED to a hard support [lo, hi]:

  * ``normal``      theta = the natural value v; density N(v; loc, scale) on [lo, hi].
  * ``lognormal``   theta = log v; density N(theta; log_center, scale) on [log lo, log hi].
  * ``halfnormal``  theta = log v; density HalfNormal(v; scale) on [lo, hi] -- log_prior adds
                    the +theta log-Jacobian, so the density in v is what is inverted here.

The transform is the inverse CDF of each of those truncated distributions, evaluated in the
space log_prior scores (v for ``normal``, log v for the other two), so the sampled vector is
exactly the theta the likelihood takes. Truncated-normal inverse CDF:
    x = loc + scale * Phi^-1( Phi(a) + u * (Phi(b) - Phi(a)) ),  a=(lo-loc)/scale, b=(hi-loc)/scale.
"""
import numpy as np
from scipy.stats import norm


def transform_factory(specs):
    lo_z, hi_z, loc, scale, kind = [], [], [], [], []
    for s in specs:
        if s.prior == "normal":                 # in v
            l, h, c, sc = s.lo, s.hi, s.loc, s.scale
        elif s.prior == "lognormal":            # in log v
            l, h, c, sc = np.log(s.lo), np.log(s.hi), s.log_center, s.scale
        elif s.prior == "halfnormal":           # in v, half-normal at 0 -> truncated normal(0, scale)
            l, h, c, sc = s.lo, s.hi, 0.0, s.scale
        else:
            raise ValueError(s.prior)
        loc.append(c); scale.append(sc); lo_z.append((l - c) / sc); hi_z.append((h - c) / sc); kind.append(s.prior)
    loc, scale = np.array(loc), np.array(scale)
    Pa, Pb = norm.cdf(np.array(lo_z)), norm.cdf(np.array(hi_z))
    take_log = np.array([k == "halfnormal" for k in kind])      # inverted in v, sampled in log v

    def prior_transform(u):
        x = loc + scale * norm.ppf(Pa + np.asarray(u) * (Pb - Pa))
        if take_log.any():
            x = np.where(take_log, np.log(np.maximum(x, 1e-300)), x)
        return x

    return prior_transform
