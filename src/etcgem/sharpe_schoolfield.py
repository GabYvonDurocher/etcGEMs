"""Sharpe-Schoolfield thermal-performance model -- a window-INDEPENDENT activation
energy E for TPCs.

The Boltzmann-Arrhenius *slope* over a rising-limb window is window-dependent because
the limb is curved (MMRT / enzyme kinetics), so the "rising-limb Ea" is not a stable,
comparable quantity (see outputs/ea_definition_audit/window_sensitivity.csv). The
Schoolfield (1981) high-temperature-inactivation model instead fits the WHOLE curve with
a single activation energy E for the rising portion and a deactivation term (E_h, T_h)
for the high-T collapse, so E is read from the full shape, not a chosen window.

Model (rTPC ``sharpeschoolhigh_1981`` form; high-T inactivation only -- the cold-end
low-T term is added only if a curve's rise demands it):

    rate(T) = r_Tref * exp( (E/k_B) (1/T_ref - 1/T) )
                       / ( 1 + exp( (E_h/k_B) (1/T_h - 1/T) ) )

T, T_ref, T_h in KELVIN; k_B = 8.617333e-5 eV/K; E, E_h in eV. r_Tref is the rate at the
(fixed, documented) reference temperature T_ref. E is the window-independent activation
energy; E_h/T_h describe the deactivation (T_h is the temperature at which the inactivation
term is half, near CTmax).
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, Optional

import numpy as np

KB_EV = 8.617333e-5   # Boltzmann constant, eV/K


def sharpeschoolhigh(T_K, r_tref, E, E_h, T_h, T_ref_K):
    """Schoolfield 1981 high-T-inactivation rate at temperature T_K (Kelvin, array ok)."""
    T_K = np.asarray(T_K, float)
    rise = np.exp((E / KB_EV) * (1.0 / T_ref_K - 1.0 / T_K))
    deact = 1.0 + np.exp((E_h / KB_EV) * (1.0 / T_h - 1.0 / T_K))
    return r_tref * rise / deact


@dataclass
class SSFit:
    r_tref: float
    E: float           # eV, window-independent activation energy
    E_h: float         # eV, deactivation energy
    T_h_C: float       # deg C, half-inactivation temperature
    T_ref_C: float
    E_sd: float
    E_h_sd: float
    T_h_sd_C: float
    r2: float
    n: int
    ok: bool

    def as_row(self) -> Dict:
        return asdict(self)


def fit_sharpe_schoolfield(temps_C, rates, T_ref_C: float = 20.0,
                           E0: float = 0.7, Eh0: float = 3.0,
                           Th0_C: Optional[float] = None,
                           bounds_E=(0.05, 4.0), bounds_Eh=(0.3, 10.0),
                           maxfev: int = 20000) -> SSFit:
    """Fit the Schoolfield high-T model to (temps_C, rates) by nonlinear least squares.

    ``T_ref_C`` is FIXED (documented, consistent across curves) so E/E_h/T_h are the only
    shape parameters compared. Returns an SSFit with parameter SDs (from the covariance,
    1 sigma) and R^2. ``ok`` is False on a failed/implausible fit.
    """
    from scipy.optimize import curve_fit
    T = np.asarray(temps_C, float); r = np.asarray(rates, float)
    m = np.isfinite(T) & np.isfinite(r) & (r > 0)
    T, r = T[m], r[m]
    n = int(T.size)
    T_ref_K = T_ref_C + 273.15
    bad = SSFit(np.nan, np.nan, np.nan, np.nan, T_ref_C, np.nan, np.nan, np.nan, np.nan, n, False)
    if n < 5:
        return bad
    T_K = T + 273.15
    ip = int(np.argmax(r)); Topt_K = T_K[ip]
    if Th0_C is None:
        Th0_C = (Topt_K + 4.0) - 273.15          # a few K above the peak
    r_tref0 = float(np.interp(T_ref_K, T_K, r)) or max(r.min(), 1e-4)

    def _f(TK, r_tref, E, E_h, T_h):
        return sharpeschoolhigh(TK, r_tref, E, E_h, T_h, T_ref_K)

    p0 = [max(r_tref0, 1e-4), E0, Eh0, Th0_C + 273.15]
    lb = [1e-6, bounds_E[0], bounds_Eh[0], Topt_K - 5.0]
    ub = [10 * r.max() + 1e-3, bounds_E[1], bounds_Eh[1], Topt_K + 30.0]
    p0 = [min(max(p0[i], lb[i] * 1.001), ub[i] * 0.999) for i in range(4)]
    try:
        popt, pcov = curve_fit(_f, T_K, r, p0=p0, bounds=(lb, ub), maxfev=maxfev)
    except Exception:
        return bad
    sd = np.sqrt(np.diag(pcov)) if np.all(np.isfinite(pcov)) else np.full(4, np.nan)
    pred = _f(T_K, *popt)
    ss_res = float(np.sum((r - pred) ** 2)); ss_tot = float(np.sum((r - r.mean()) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else np.nan
    r_tref, E, E_h, T_h = popt
    return SSFit(float(r_tref), float(E), float(E_h), float(T_h - 273.15), T_ref_C,
                 float(sd[1]), float(sd[2]), float(sd[3]), float(r2), n,
                 ok=bool(np.isfinite(r2) and r2 > 0.9 and E > 0))
