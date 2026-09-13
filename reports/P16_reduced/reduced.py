#!/usr/bin/env python3
"""P16 -- the 15-parameter reduction: dTm pinned at 0.0 (D2).

Module level, so pool workers can import it. The workers are still initialised with the FULL
payload by `_gwinit`, so `_GSPECS` there is the full 16-parameter spec list and `_gwloglike`
expects a 16-vector; this module inserts the fixed value at dTm's index before calling it. Nothing
in src/ changes.
"""
import os, sys
import numpy as np
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
for p in (os.path.join(ROOT, "src"), os.path.join(ROOT, "reports", "P6_convergence")):
    if p not in sys.path: sys.path.insert(0, p)
from etcgem.calibration_multi import build_gasflux_specs, _gwloglike   # noqa: E402
from p6_fits import FITS                                               # noqa: E402

FIT = [f for f in FITS if f[0] == "D_NLDM"][0]
FULL_SPECS = build_gasflux_specs({"use_etc": FIT[6] is not None, "fit_clearance": FIT[8]})
FULL_NAMES = [s.name for s in FULL_SPECS]

FIXED_NAME = "dTm"
FIXED_IDX = FULL_NAMES.index(FIXED_NAME)
# dTm has space "add", so the sampled-space value equals the natural value
FIXED_SAMPLED = 0.0
FREE_SPECS = [s for i, s in enumerate(FULL_SPECS) if i != FIXED_IDX]
FREE_NAMES = [s.name for s in FREE_SPECS]


def expand(theta15):
    """15 free parameters -> the full 16-vector the core likelihood expects."""
    t = np.empty(len(FULL_NAMES), float)
    t[:FIXED_IDX] = theta15[:FIXED_IDX]
    t[FIXED_IDX] = FIXED_SAMPLED
    t[FIXED_IDX + 1:] = theta15[FIXED_IDX:]
    return t


def loglike15(theta15):
    return _gwloglike(expand(np.asarray(theta15, float)))
