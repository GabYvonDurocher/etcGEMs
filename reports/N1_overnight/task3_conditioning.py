#!/usr/bin/env python3
"""task3_conditioning.py -- N1 TASK 3: the pool row's conditioning, and what rescaling fixes.

K2 PART D established that the pool constraint's coefficients span ~8e8 at the cold end,
that GLPK returns a growth rate ~0.5% wrong there, and that rescaling to a mathematically
identical well-conditioned LP makes GLPK agree with Gurobi exactly. This measures the
conditioning per strain and per temperature, and demonstrates the fix.

    python3 reports/N1_overnight/task3_conditioning.py

Writes task3_conditioning.csv and task3_rescaled_comparison.csv beside this file. It builds
providers and solves; it changes no committed output.
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "src"))

STRAINS = ["cauris_iRV973", "chaemulonii_draft", "cduobushaemulonii_draft",
           "cparapsilosis_iDC1003"]
# B0 is the standalone's form (the gate's configuration); B3 is the ladder's last rung
# without sectors, which is as far as the rescaling can be exercised (see the RuntimeError
# in set_temperature: the sector layer writes the pool bound in places this does not reach).
EXPERIMENTS = ["transfer_candida", "candida_B3_ngamT"]
TEMPS = [22.0, 26.0, 30.0, 34.0, 38.0, 44.0]


def run(strain, experiment, solver, rescale):
    import cobra
    cobra.Configuration().solver = solver
    from etcgem.config import resolve, build_provider
    from etcgem.enzyme_cost import Perturbation
    from etcgem.tpc import compute_tpc
    cfg = resolve(strain, experiment)
    cfg["solver"] = solver
    cfg["provider"]["rescale_pool_row"] = rescale
    pm = build_provider(cfg)
    out = []
    for T in TEMPS:
        g = float(compute_tpc(pm, [T], Perturbation()).growth[0])
        out.append(dict(strain=strain, experiment=experiment, solver=solver,
                        rescaled=rescale, temp_C=T, growth=g,
                        row_condition=pm.ec._row_cond, row_scale=pm.ec._row_scale))
    return out


def main():
    rows = []
    for exp in EXPERIMENTS:
        for st in STRAINS:
            for solver in ("gurobi", "glpk"):
                for rescale in (False, True):
                    rows.extend(run(st, exp, solver, rescale))
                    print(f"  {exp:22s} {st:24s} {solver:7s} rescale={rescale}", flush=True)
    D = pd.DataFrame(rows)
    D.to_csv(os.path.join(HERE, "task3_conditioning.csv"), index=False)

    # conditioning, which does not depend on solver or on the rescaling (it is a property
    # of the cost vector, measured before any rescaling is applied)
    C = (D[(D.solver == "gurobi") & (~D.rescaled)]
         .pivot_table(index=["experiment", "strain"], columns="temp_C",
                      values="row_condition"))
    print("\nPOOL-ROW CONDITION NUMBER (max/min coefficient), per strain and temperature")
    with pd.option_context("display.width", 200):
        print(C.map(lambda v: f"{v:.2e}").to_string())

    # what moves
    key = ["experiment", "strain", "temp_C"]
    g0 = D[(D.solver == "gurobi") & (~D.rescaled)].set_index(key).growth
    g1 = D[(D.solver == "gurobi") & (D.rescaled)].set_index(key).growth
    l0 = D[(D.solver == "glpk") & (~D.rescaled)].set_index(key).growth
    l1 = D[(D.solver == "glpk") & (D.rescaled)].set_index(key).growth
    cmp_ = pd.DataFrame(dict(gurobi=g0, gurobi_rescaled=g1, glpk=l0, glpk_rescaled=l1))
    cmp_["glpk_minus_gurobi"] = cmp_.glpk - cmp_.gurobi
    cmp_["glpk_rescaled_minus_gurobi"] = cmp_.glpk_rescaled - cmp_.gurobi
    cmp_["gurobi_rescaled_minus_gurobi"] = cmp_.gurobi_rescaled - cmp_.gurobi
    cmp_ = cmp_.reset_index()
    cmp_.to_csv(os.path.join(HERE, "task3_rescaled_comparison.csv"), index=False)
    print("\nWHAT MOVES (growth in model units)")
    bad = cmp_[cmp_.glpk_minus_gurobi.abs() > 1e-9]
    with pd.option_context("display.width", 220):
        print(bad.round(9).to_string(index=False) if len(bad)
              else "  (no GLPK/Gurobi disagreement above 1e-9 at these temperatures)")
    print(f"\nsummary over {len(cmp_)} (experiment, strain, temperature) points:")
    print(f"  |GLPK - Gurobi|           max {cmp_.glpk_minus_gurobi.abs().max():.3e}  "
          f"n>1e-9 {int((cmp_.glpk_minus_gurobi.abs() > 1e-9).sum())}")
    print(f"  |GLPK_rescaled - Gurobi|  max {cmp_.glpk_rescaled_minus_gurobi.abs().max():.3e}  "
          f"n>1e-9 {int((cmp_.glpk_rescaled_minus_gurobi.abs() > 1e-9).sum())}")
    print(f"  |Gurobi_rescaled - Gurobi| max {cmp_.gurobi_rescaled_minus_gurobi.abs().max():.3e}  "
          f"n>1e-9 {int((cmp_.gurobi_rescaled_minus_gurobi.abs() > 1e-9).sum())}")
    print("\nwrote task3_conditioning.csv, task3_rescaled_comparison.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
