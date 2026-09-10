#!/usr/bin/env python3
"""P13 -- shared pieces. Reuses P12's fit definition and context builder unchanged; adds the
thirteen committed points P13 compares schemes at (P12's twelve converged endpoints plus theta_A
as P11's main-run median, which is what every earlier report quotes)."""
import os, sys
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
P12 = os.path.abspath(os.path.join(HERE, "..", "P12_modes"))
if P12 not in sys.path: sys.path.insert(0, P12)
from common import (build, SPECS, NAMES, decompose, PAYLOAD, ROOT, NEST, P4DIR,   # noqa: E402,F401
                    fixed_points, to_natural, to_pert, flux_tpc, _prov, _MASK_G,
                    add_total_carbon_constraint, gasflux_log_likelihood, log_prior)

CONVERGED = os.path.join(P12, "task2c_converged.csv")


def p12_points():
    """P12's twelve converged endpoints, keyed by their P12 labels. These are the committed
    points every P13 comparison uses."""
    d = pd.read_csv(CONVERGED)
    xc = [f"x_{n}" for n in NAMES]
    return {r.key: r[xc].to_numpy(float) for _, r in d.iterrows()}, d


def key_points():
    """the three the prompt names: p38 (the live basin's best), theta_A, b3 (the dead basin)."""
    pts, _ = p12_points()
    return {"p38(b22)": pts["p38(b22)"], "A(b20)": pts["A(b20)"], "B(b3)": pts["B(b3)"]}
