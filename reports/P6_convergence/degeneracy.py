#!/usr/bin/env python3
"""P6 TASK 0d -- WHY is the E/F respiration likelihood degenerate? (diagnosis; nothing fitted,
nothing changed)

gasflux.py's docstring says the total-carbon cap "pins the flux distribution (O2/CO2 unique)".
So either the cap is not binding at the fitted parameters, or the ETC area constraint changes
which optimum is selected, or O2 uptake is degenerate at fixed growth regardless. For each of
the nine fits, at P4's MAP and at five temperatures:

  * grow: apply the state, optimise growth -> g*;
  * the cap: is it present, and is it ACTIVE (primal at its bound) at the solution?
  * FVA on the net O2 uptake (EX_o2_e_REV - EX_o2_e) with growth fixed at g* (to 1e-6):
    min and max -> the width is the degeneracy the likelihood samples through;
  * the same FVA with the ETC area constraint REMOVED (E/F only), to see whether the constraint
    creates the degeneracy or merely changes which vertex the solver lands on;
  * the O2 value flux_tpc actually returned, for reference.

Writes degeneracy.csv beside this file.
"""
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, HERE)
os.chdir(ROOT)

from etcgem import etc_area as EA                                                          # noqa: E402
from etcgem.calibration_multi import _build_gasflux_ctx, gasflux_log_likelihood, to_pert   # noqa: E402
from etcgem.tpc import apply_state                                                         # noqa: E402
from p6_fits import FITS, p4_dir_for                                                       # noqa: E402

TEMPS = (25.0, 30.0, 37.0, 40.0, 44.0)
CAP = "total_carbon_uptake"


def o2_fva(m, g_star):
    """min / max net O2 uptake with growth held at g_star."""
    rev, fwd = m.reactions.get_by_id("EX_o2_e_REV"), m.reactions.get_by_id("EX_o2_e")
    obj_expr = m.objective.expression
    fix = m.problem.Constraint(obj_expr, lb=g_star * (1 - 1e-6), name="_p6_fix_growth")
    m.add_cons_vars([fix])
    net = rev.flux_expression - fwd.flux_expression
    out = {}
    try:
        for sense in ("min", "max"):
            m.objective = m.problem.Objective(net, direction=sense)
            v = m.slim_optimize()
            out[sense] = float(v) if v is not None and np.isfinite(v) else np.nan
    finally:
        m.remove_cons_vars([fix])
        m.objective = m.problem.Objective(obj_expr, direction="max")
        m.solver.update()
    return out["min"], out["max"]


def cap_state(m):
    if CAP not in m.constraints:
        return None, np.nan, np.nan
    c = m.constraints[CAP]
    return True, float(c.primal), float(c.ub)


def main():
    rows = []
    for label, cfg, medium, table, otu, c_max, etc, protons, fit_k in FITS:
        ctx, specs = _build_gasflux_ctx(strain="eciML1515", medium=medium, experiment=f"gasflux_config{cfg}",
                                        table=table, otu=otu, c_max=c_max, etc_table=etc,
                                        apply_protons=protons, fit_clearance=fit_k)
        d = os.path.join(ROOT, "strains", "eciML1515", "outputs", p4_dir_for(cfg, medium))
        ch = np.load(os.path.join(d, "chain.npy")); lp = np.load(os.path.join(d, "log_prob.npy"))
        i, j = np.unravel_index(np.nanargmax(lp), lp.shape); th = ch[i, j]
        gasflux_log_likelihood(th, ctx, specs)      # installs clearance / ETC constraint at theta
        pert = to_pert(th, specs)
        m = ctx["pm"].ec.model
        for T in TEMPS:
            apply_state(ctx["pm"].ec, T, pert)
            g = m.slim_optimize()
            if g is None or not np.isfinite(g) or g < 1e-4:
                rows.append(dict(fit=label, T_C=T, growth=0.0, note="no growth")); continue
            present, cap_primal, cap_ub = cap_state(m)
            o2_solver = float(m.reactions.get_by_id("EX_o2_e_REV").flux - m.reactions.get_by_id("EX_o2_e").flux)
            lo, hi = o2_fva(m, g)
            row = dict(fit=label, config=cfg, medium=medium, T_C=T, growth=round(float(g), 4),
                       cap_present=bool(present), cap_c_max=c_max,
                       cap_primal=round(cap_primal, 2) if present else np.nan,
                       cap_active=(present and abs(cap_ub - cap_primal) < 1e-3 * max(1.0, cap_ub)) if present else False,
                       o2_solver=round(o2_solver, 3), o2_fva_min=round(lo, 3), o2_fva_max=round(hi, 3),
                       o2_fva_width=round(hi - lo, 3),
                       o2_width_over_o2=round((hi - lo) / o2_solver, 3) if o2_solver else np.nan)
            if etc is not None:
                EA.remove_etc_area_constraint(ctx["pm"])
                apply_state(ctx["pm"].ec, T, pert)
                g2 = m.slim_optimize()
                lo2, hi2 = o2_fva(m, g2) if g2 and np.isfinite(g2) else (np.nan, np.nan)
                row.update(growth_no_etc=round(float(g2), 4), o2_fva_min_no_etc=round(lo2, 3),
                           o2_fva_max_no_etc=round(hi2, 3), o2_fva_width_no_etc=round(hi2 - lo2, 3))
                gasflux_log_likelihood(th, ctx, specs)   # re-install the ETC constraint
            rows.append(row)
            print(f"[degen] {label:7s} {T:4.0f}C g={g:.3f} cap={'none' if not present else ('ACTIVE' if row['cap_active'] else f'slack ({cap_primal:.0f}/{cap_ub:.0f})')} "
                  f"O2 solver {o2_solver:.2f}  FVA [{lo:.2f}, {hi:.2f}] width {hi-lo:.2f}"
                  + (f"  | no ETC: FVA [{row.get('o2_fva_min_no_etc')}, {row.get('o2_fva_max_no_etc')}]" if etc else ""), flush=True)
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(HERE, "degeneracy.csv"), index=False)
    print("[degen] done", flush=True)


if __name__ == "__main__":
    main()
