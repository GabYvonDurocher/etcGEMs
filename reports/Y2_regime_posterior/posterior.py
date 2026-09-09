#!/usr/bin/env python3
"""posterior.py -- Li et al.'s SMC-ABC prior and posterior particles, as their own code stores them.

Y2. The posterior is the file, not the figures. `results.tar.gz` on Zenodo (10.5281/zenodo.3996543,
version 2.0) contains `results/smcabc_gem_three_conditions_save_all_particles.pkl`, a pickle of
their `abc_etc.SMCABC` object, and two of its attributes are the two populations the paper plots:

    .population_t0   the FIRST generation, n = 128  -- "Prior" in Fig. 2a-c, 2d, 2e
    .population      the final population,  n = 100 -- "Posterior"

Both are lists of particles, and a particle is a plain dict keyed `"<uniprot>_<Tm|Topt|dCpt>"` in
the SAME units as `data/model_enzyme_params.csv` (Tm, Topt in K; dCpt in J/mol/K). So the
prior -> posterior mapping is a field rename and nothing else; `task1_posterior.py` shows it exact
on one enzyme before it is applied to 764.

TWO SHIMS, both needed to import THEIR code rather than re-implement it.

1. `sklearn` is not in this project's environment. `GEMS.py` imports `mean_squared_error` and
   `r2_score` at module level and uses them only to print fit statistics inside `aerobic()`,
   `anaerobic()` and `chemostat()` -- none of which Y2 calls. A two-function stub is installed so
   `GEMS` imports; the stub's own functions are the real formulas, and if anything ever calls them
   the numbers are right.
2. Unpickling the SMCABC object needs `abc_etc` and `GEMS` importable, because the object holds a
   reference to `GEMS.simulate_at_three_conditions_2` as its simulator. Their `code/` directory
   goes on the path.

The particle -> thermal-parameter conversion is **their** `GEMS.format_input`, unaltered: it copies
the prior table, overwrites Tm/Topt/dCpt from the particle, shifts T90 by the same amount Tm moved,
and calls `etc.calculate_thermal_params`.
"""
from __future__ import annotations

import logging
import os
import pickle
import sys
import types
import warnings

import numpy as np
import pandas as pd

logging.getLogger("cobra").setLevel(logging.ERROR)
warnings.filterwarnings("ignore")

PICKLE = "results/smcabc_gem_three_conditions_save_all_particles.pkl"
FIELDS = ("Tm", "Topt", "dCpt")


def _install_sklearn_stub():
    """Let GEMS.py import. Its two sklearn functions are never on any path Y2 takes."""
    if "sklearn.metrics" in sys.modules:
        return
    metrics = types.ModuleType("sklearn.metrics")

    def mean_squared_error(y_true, y_pred):
        y_true, y_pred = np.asarray(y_true, float), np.asarray(y_pred, float)
        return float(np.mean((y_true - y_pred) ** 2))

    def r2_score(y_true, y_pred):
        y_true, y_pred = np.asarray(y_true, float), np.asarray(y_pred, float)
        ss_res = float(np.sum((y_true - y_pred) ** 2))
        ss_tot = float(np.sum((y_true - np.mean(y_true)) ** 2))
        return 1.0 - ss_res / ss_tot if ss_tot else float("nan")

    metrics.mean_squared_error = mean_squared_error
    metrics.r2_score = r2_score
    sk = types.ModuleType("sklearn")
    sk.metrics = metrics
    sys.modules["sklearn"] = sk
    sys.modules["sklearn.metrics"] = metrics


def import_their_code(bg):
    """Their `code/` on the path, with GEMS importable. Returns (etc, GEMS)."""
    _install_sklearn_stub()
    code = os.path.join(bg, "code")
    if code not in sys.path:
        sys.path.insert(0, code)
    from etcpy import etc                                  # noqa: E402
    import GEMS                                            # noqa: E402

    def set_NGAMT(model, T):                               # the Y1 bounds-order shim
        v = etc.getNGAMT(T)
        model.reactions.NGAM.bounds = (v, v)
    etc.set_NGAMT = set_NGAMT
    return etc, GEMS


def load_populations(results_root, bg):
    """(prior particles, posterior particles) from their deposited SMC-ABC object."""
    import_their_code(bg)
    path = os.path.join(results_root, PICKLE)
    with open(path, "rb") as fh:
        smc = pickle.load(fh)
    return list(smc.population_t0), list(smc.population), smc


def particles_frame(particles):
    """n_particles x n_parameters DataFrame, columns `<uniprot>_<field>`."""
    return pd.DataFrame([dict(p) for p in particles])


def per_enzyme(particles, field):
    """n_particles x n_enzymes DataFrame for one field, columns = uniprot ids."""
    df = particles_frame(particles)
    cols = [c for c in df.columns if c.endswith("_" + field)]
    out = df[cols].copy()
    out.columns = [c[: -(len(field) + 1)] for c in cols]
    return out


def median_particle(particles):
    """The enzyme-by-enzyme median across a population, as a particle dict."""
    df = particles_frame(particles)
    return {c: float(np.median(df[c].values)) for c in df.columns}
