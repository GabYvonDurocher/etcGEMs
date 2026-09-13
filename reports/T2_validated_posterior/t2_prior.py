#!/usr/bin/env python3
"""T2 -- the unit-cube prior transform: P11's exactly for normal / lognormal / halfnormal (the inverse
CDF of each truncated form, in the space the likelihood takes), plus ONE new kind for the validation
configuration's positive control:

  * ``beta31``  -- Beta(3,1) on [0, 1]: CDF x^3, so the transform is x = u^(1/3) in "add" space.

Module-level class so it pickles for a process pool. ``inverse`` is the exact inverse, used by the
audit to recover unit-cube positions from saved samples (check (f))."""
import numpy as np
from scipy.stats import norm


class PriorTransformT2:
    def __init__(self, loc, scale, Pa, Pb, take_log, is_beta31):
        self.loc, self.scale, self.Pa, self.Pb = loc, scale, Pa, Pb
        self.take_log, self.is_beta31 = take_log, is_beta31

    def __call__(self, u):
        u = np.asarray(u, float)
        x = self.loc + self.scale * norm.ppf(self.Pa + u * (self.Pb - self.Pa))
        if self.take_log.any():
            x = np.where(self.take_log, np.log(np.maximum(x, 1e-300)), x)
        if self.is_beta31.any():
            x = np.where(self.is_beta31, np.cbrt(np.clip(u, 0.0, 1.0)), x)
        return x

    def inverse(self, x):
        """sampled-space vector (or n x D array) -> unit cube."""
        x = np.asarray(x, float)
        v = np.where(self.take_log, np.exp(x), x)
        u = (norm.cdf((v - self.loc) / self.scale) - self.Pa) / (self.Pb - self.Pa)
        if self.is_beta31.any():
            u = np.where(self.is_beta31, np.clip(x, 0.0, 1.0) ** 3, u)
        return u


def transform_factory(specs):
    lo_z, hi_z, loc, scale, kind = [], [], [], [], []
    for s in specs:
        if s.prior == "normal":
            l, h, c, sc = s.lo, s.hi, s.loc, s.scale
        elif s.prior == "lognormal":
            l, h, c, sc = np.log(s.lo), np.log(s.hi), s.log_center, s.scale
        elif s.prior == "halfnormal":
            l, h, c, sc = s.lo, s.hi, 0.0, s.scale
        elif s.prior == "beta31":
            l, h, c, sc = -1.0, 1.0, 0.0, 1.0          # placeholders; overridden by the beta branch
        else:
            raise ValueError(s.prior)
        loc.append(c); scale.append(sc); lo_z.append((l - c) / sc); hi_z.append((h - c) / sc); kind.append(s.prior)
    loc, scale = np.array(loc), np.array(scale)
    return PriorTransformT2(loc, scale, norm.cdf(np.array(lo_z)), norm.cdf(np.array(hi_z)),
                            np.array([k == "halfnormal" for k in kind]), np.array([k == "beta31" for k in kind]))


def prior_cdf(specs, x):
    """the exact prior CDF of each coordinate at sampled-space value x (n x D) -- for checks (a), (b), (c)."""
    return transform_factory(specs).inverse(x)
