#!/usr/bin/env python3
"""task1_is_it_arithmetic.py -- K9 TASK 1: is the ~5 C ceiling-criterion requirement a model
constraint, or a restatement of the observed thermal limits?

THE WORRY, and it gates everything downstream. The four Candida models predict near-identical
CT_max. If so, the uniform Tm offset each species needs to bring its CT_max onto its OBSERVED
limit is just (model CT_max - observed limit), and the DIFFERENCE between species is then
(observed limit_i - observed limit_j) plus whatever small spread the model has. If the model's
CT_max spread is negligible against the observed spread, the "required interspecies difference"
is arithmetic and not a model-derived requirement at all, and must not be quoted as one.

THE TEST. An arithmetic identity does not care what the model is. A model constraint does. So
the required offset per species is recomputed under several model states that move the ceiling,
and the question is whether the DIFFERENCES between species move with them:

  * B3, the model before the K5 proton repair
  * B5, the repaired model
  * B5 with the carbon cap that K5 TASK 3b introduced
  * B5 with the curvature prior at -3.0 (K7's reconciling value) and at -6.0

If the required differences are the same to within a fraction of a degree across all of these
while the absolute requirements move, the answer is: arithmetic.

Run from the project root:

    python3 reports/K9_criterion/task1_is_it_arithmetic.py

Writes task1_offsets_by_model.csv beside this file.
"""
from __future__ import annotations

import logging
import os
import sys

import numpy as np
import pandas as pd

logging.getLogger("cobra").setLevel(logging.ERROR)
sys.path.insert(0, "src")

from etcgem.config import build_provider, resolve            # noqa: E402
from etcgem.enzyme_cost import Perturbation                  # noqa: E402
from etcgem.gasflux import add_total_carbon_constraint       # noqa: E402
from etcgem.tpc import TPC, apply_state                      # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
WIDE = np.linspace(20.0, 60.0, 81)           # 0.5 C steps over the range that
                                             # can contain CT_max; TASK 2 reports
                                             # the grid-resolution sensitivity
CRIT = 0.05
OBSERVED = {"cauris_iRV973": 44.0, "chaemulonii_draft": 38.0,
            "cduobushaemulonii_draft": 38.0, "cparapsilosis_iDC1003": 38.0}
LABEL = {"cauris_iRV973": "C. auris", "chaemulonii_draft": "C. haemulonii",
         "cduobushaemulonii_draft": "C. duobushaemulonii",
         "cparapsilosis_iDC1003": "C. parapsilosis"}
# label -> (experiment, carbon cap, dCp_scale)
STATES = {
    "B3 (before the K5 repair)": ("candida_B3_ngamT", None, 1.0),
    "B5 (repaired)": ("candida_B5_respire", None, 1.0),
    "B5 + carbon cap 12": ("candida_B5_respire", 12.0, 1.0),
    "B5, dCp -3.0 (K7's value)": ("candida_B5_respire", None, 0.75),
    "B5, dCp -6.0": ("candida_B5_respire", None, 1.5),
}


def ctmax(pm, pert):
    g = np.zeros(len(WIDE))
    for i, T in enumerate(WIDE):
        apply_state(pm.ec, float(T), pert)
        v = pm.ec.model.slim_optimize()
        g[i] = 0.0 if (v is None or not np.isfinite(v) or v < 1e-6) else v
    if g.max() <= 0:
        return float("nan")
    return TPC(WIDE, g).descriptors(CRIT).CTmax_C


OFFSETS = np.array([0.0, 3.0, 6.0, 9.0, 12.0, 15.0, 18.0])


def required_offset(pm, dcp, target):
    """The uniform Tm offset that brings CT_max onto the observed limit.

    CT_max falls smoothly and near-linearly with a uniform Tm shift (K8 measured
    dCT_max/dTm = 0.75-0.94), so it is evaluated on a short ladder of offsets and the crossing
    is interpolated. That is a few evaluations instead of a bisection's dozen, and the curve is
    written out so the linearity can be checked rather than assumed."""
    cs = np.array([ctmax(pm, Perturbation(dTm=-o, dCp_scale=dcp)) for o in OFFSETS])
    ok = np.isfinite(cs)
    if ok.sum() < 2:
        return float("nan"), cs
    o, c = OFFSETS[ok], cs[ok]
    if c.min() > target or c.max() < target:
        return float("nan"), cs
    # c decreases with o; interpolate o as a function of c
    idx = np.argsort(c)
    return float(np.interp(target, c[idx], o[idx])), cs


def main():
    rows = []
    for label, (exp, cmax, dcp) in STATES.items():
        for s, obs in OBSERVED.items():
            pm = build_provider(resolve(s, exp))
            if cmax is not None:
                add_total_carbon_constraint(pm, cmax)
            base = ctmax(pm, Perturbation(dCp_scale=dcp))
            off, curve = required_offset(pm, dcp, obs)
            rows.append(dict(model_state=label, strain=s, species=LABEL[s],
                             CTmax_uncorrected_C=base, observed_limit_C=obs,
                             gap_C=base - obs, required_offset_C=off,
                             **{f"CTmax_at_offset_{o:g}": float(c)
                                for o, c in zip(OFFSETS, curve)}))
            print(f"[k9] {label:26s} {LABEL[s]:22s} CTmax {base:6.2f}  obs {obs:4.1f}  "
                  f"gap {base-obs:+5.2f}  required offset {off:5.2f}", flush=True)

    d = pd.DataFrame(rows)
    d.to_csv(os.path.join(HERE, "task1_offsets_by_model.csv"), index=False)

    print("\n=== THE TEST: does the required DIFFERENCE move when the model moves? ===")
    print(f"{'model state':28s} {'CTmax spread':>13s} {'offset spread':>14s} "
          f"{'auris - relatives':>18s}")
    obs_spread = max(OBSERVED.values()) - min(OBSERVED.values())
    for label in STATES:
        x = d[d.model_state == label]
        cs = x["CTmax_uncorrected_C"].max() - x["CTmax_uncorrected_C"].min()
        os_ = x["required_offset_C"].max() - x["required_offset_C"].min()
        a = float(x[x.strain == "cauris_iRV973"]["required_offset_C"].iloc[0])
        r = float(x[x.strain != "cauris_iRV973"]["required_offset_C"].mean())
        print(f"{label:28s} {cs:12.2f} C {os_:13.2f} C {a-r:17.2f} C")
    print(f"\n  observed thermal-limit spread across the four species: {obs_spread:.2f} C")
    print("  If the offset spread equals the observed spread minus the model's own CTmax")
    print("  spread, and does not move as the model moves, the requirement is arithmetic.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
