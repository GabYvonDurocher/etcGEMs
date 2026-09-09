#!/usr/bin/env python3
"""P10 TASK 1 -- why pfba does not reach 0.0000 on E LB / F LB. On one reused model at P4's MAP:
per-temperature O2 and growth on the first and second pfba call; the O2 range with growth fixed
at its optimum AND total absolute flux fixed at its pfba minimum (is the pfba vertex itself a
face in O2?); and the same with growth_tol 1e-9. Writes task1_why_lb.csv beside this file."""
import json, os, sys
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src")); sys.path.insert(0, os.path.join(ROOT, "reports", "P6_convergence")); os.chdir(ROOT)
from etcgem.calibration_multi import gasflux_log_likelihood, to_pert   # noqa: E402
from etcgem.gasflux import flux_tpc                                     # noqa: E402
from etcgem.tpc import apply_state                                      # noqa: E402
from cobra.flux_analysis.parsimonious import add_pfba                   # noqa: E402
from p6_fits import FITS                                                # noqa: E402
from state_vs_identifiability import build, points                      # noqa: E402


def o2_range_at_pfba_optimum(m, g, tol):
    rev, fwd = m.reactions.get_by_id("EX_o2_e_REV"), m.reactions.get_by_id("EX_o2_e"); obj = m.objective.expression; out = {}
    with m:
        from optlang.symbolics import Zero
        m.add_cons_vars([m.problem.Constraint(obj, lb=g * (1 - tol), name="_fixg")])
        m.objective = m.problem.Objective(Zero, direction="min")
        m.objective.set_linear_coefficients({v: 1.0 for r in m.reactions for v in (r.forward_variable, r.reverse_variable)})
        fmin = m.slim_optimize(); pf_expr = m.objective.expression
        m.add_cons_vars([m.problem.Constraint(pf_expr, ub=fmin * (1 + 1e-9), name="_fixpf")])
        for sense in ("min", "max"):
            m.objective = m.problem.Objective(rev.flux_expression - fwd.flux_expression, direction=sense); v = m.slim_optimize(); out[sense] = float(v) if v is not None else np.nan
    return fmin, out["min"], out["max"]


rows = []
for want in ("E_LB", "F_LB"):
    fit = [f for f in FITS if f[0] == want][0]; th, th2 = points(fit)
    ctx, sp = build(fit); ctx["respiration"] = {"tiebreak": "pfba"}; pert = to_pert(th, sp)
    L1 = gasflux_log_likelihood(th, ctx, sp); d1 = flux_tpc(ctx["pm"], ctx["T"], pert, metabolites=("o2",), tiebreak="pfba")
    L2 = gasflux_log_likelihood(th, ctx, sp); d2 = flux_tpc(ctx["pm"], ctx["T"], pert, metabolites=("o2",), tiebreak="pfba")
    gasflux_log_likelihood(th2, ctx, sp); L3 = gasflux_log_likelihood(th, ctx, sp); d3 = flux_tpc(ctx["pm"], ctx["T"], pert, metabolites=("o2",), tiebreak="pfba")
    print(f"[why] {want}: logL calls {L1:.4f} {L2:.4f} {L3:.4f}", flush=True)
    m = ctx["pm"].ec.model
    for i, T in enumerate(ctx["T"]):
        o = (d1.o2_uptake[i], d2.o2_uptake[i], d3.o2_uptake[i]); g = (d1.growth[i], d2.growth[i], d3.growth[i]); st = (d1.get("tiebreak_status", [None]*12)[i], d2.get("tiebreak_status", [None]*12)[i], d3.get("tiebreak_status", [None]*12)[i])
        moved = np.nanmax(o) - np.nanmin(o) > 1e-3 if np.isfinite(o).all() else True
        fmin = lo = hi = lo9 = hi9 = np.nan
        if moved and np.isfinite(g[0]) and g[0] > 1e-4:
            apply_state(ctx["pm"].ec, float(T), pert); gg = m.slim_optimize()
            fmin, lo, hi = o2_range_at_pfba_optimum(m, gg, 1e-6); _, lo9, hi9 = o2_range_at_pfba_optimum(m, gg, 1e-9)
            print(f"[why]   {T:4.0f} C: O2 over the three calls {np.round(o,3).tolist()} (growth {np.round(g,4).tolist()}, statuses {st}); at the pfba optimum (total flux {fmin:.2f}) O2 in [{lo:.3f}, {hi:.3f}] (tol 1e-6) / [{lo9:.3f}, {hi9:.3f}] (tol 1e-9)", flush=True)
        rows.append(dict(fit=want, T_C=float(T), o2_call1=o[0], o2_call2=o[1], o2_call3=o[2], growth=g[0], moved=bool(moved), pfba_total_flux=fmin, o2_min_at_pfba=lo, o2_max_at_pfba=hi, o2_min_tol9=lo9, o2_max_tol9=hi9))
pd.DataFrame(rows).to_csv(os.path.join(HERE, "task1_why_lb.csv"), index=False); print("[why] done", flush=True)
