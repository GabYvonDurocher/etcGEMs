#!/usr/bin/env python3
"""P12 TASK 2 -- the per-start local optimiser, in its own module so the pool's workers can
import it (a function defined in a run script is re-imported by every spawned worker).

Powell on the negative log-POSTERIOR, using the worker's own ctx (set by `_gwinit`, the same
initialiser every pooled run in this series has used). Powell rather than Nelder-Mead: it is
derivative-free, it does line searches along conjugate directions, and on a piecewise-smooth
surface with single-digit kinks (P10/P11) a direction-set method is less prone to collapsing
its simplex on a kink than Nelder-Mead is. maxfev is a hard cap; xtol/ftol are stated in the
report and recorded in the output.
"""
import os
import numpy as np

MAXFEV = int(os.environ.get("P12_MAXFEV", "600"))
XTOL = float(os.environ.get("P12_XTOL", "1e-3"))
FTOL = float(os.environ.get("P12_FTOL", "1e-3"))


def optimise(arg):
    """arg = (index, x0). Returns a dict; never raises, so one bad start cannot kill the pool."""
    import time
    from scipy.optimize import minimize
    from etcgem.calibration_multi import _gwnegpost, _gwlogprob, _GSPECS, gasflux_log_likelihood, _GCTX
    i, x0 = arg
    t0 = time.time()
    try:
        f0 = float(_gwnegpost(np.asarray(x0, float)))
        res = minimize(_gwnegpost, np.asarray(x0, float), method="Powell",
                       options=dict(maxfev=MAXFEV, xtol=XTOL, ftol=FTOL))
        x = np.asarray(res.x, float)
        lp = float(_gwlogprob(x))
        ll = float(gasflux_log_likelihood(x, _GCTX, _GSPECS))
        return dict(i=int(i), ok=True, x=x.tolist(), x0=list(map(float, x0)),
                    logpost_start=-f0, logpost=lp, logl=ll, nfev=int(res.nfev),
                    success=bool(res.success), wall_s=round(time.time() - t0, 1))
    except Exception as e:
        return dict(i=int(i), ok=False, error=f"{type(e).__name__}: {e}", x=list(map(float, x0)),
                    x0=list(map(float, x0)), logpost=float("-inf"), logl=float("-inf"),
                    nfev=0, success=False, wall_s=round(time.time() - t0, 1))
