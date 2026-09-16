#!/usr/bin/env python3
"""T3 scheme C -- SCRATCH module, measurement only, NOT part of the core (D0).

Gurobi's native hierarchical (lexicographic) objectives in ONE optimize(): objective 0 = growth
(priority 2, weight +1), objective 1 = total absolute flux over every variable (priority 1, weight -1
under MAXIMIZE), with ObjNRelTol = growth_tol on the growth objective so the growth degradation allowed
while minimising flux equals the current pFBA constraint growth >= g_opt (1 - growth_tol). There is no
second LP call from Python, so nothing to inherit a basis between the growth solve and the tie-break.
Reproduces gasflux_log_likelihood's arithmetic (zero_lik, clamp, floor) on the solved growth / O2."""
import numpy as np
import gurobipy as grb
from etcgem.calibration_multi import to_natural, to_pert
from etcgem.tpc import apply_state
from etcgem.gasflux import add_total_carbon_constraint
from etcgem import providers as _prov

_GROWTH_LIN = {}   # id(model) -> (LinExpr growth, LinExpr parsimony)


def _objectives(m):
    gp = m.solver.problem
    key = id(m)
    if key not in _GROWTH_LIN:
        lin = grb.LinExpr()
        for var, c in m.objective.get_linear_coefficients(m.objective.variables).items():
            lin.addTerms(float(c), gp.getVarByName(var.name))
        pars = grb.LinExpr()
        for v in gp.getVars(): pars.addTerms(1.0, v)
        _GROWTH_LIN[key] = (lin, pars)
    return gp, _GROWTH_LIN[key]


def lexi_flux(pm, temps_C, pert, growth_tol=1e-6, min_growth=1e-6, o2_fwd="EX_o2_e", o2_rev="EX_o2_e_REV", stop_on_infeasible=True):
    """one hierarchical solve per temperature; returns rows of (T, status, growth, o2_uptake)."""
    ecm = pm.ec; m = ecm.model; rows = []
    gp, (lin, pars) = _objectives(m)
    for Tc in np.asarray(temps_C, float):
        apply_state(ecm, float(Tc), pert); m.solver.update()
        gp.ModelSense = grb.GRB.MAXIMIZE; gp.NumObj = 2
        gp.setObjectiveN(lin, 0, priority=2, weight=1.0, reltol=float(growth_tol), name="growth")
        gp.setObjectiveN(pars, 1, priority=1, weight=-1.0, name="parsimony")
        gp.optimize()
        st = {2: "optimal", 3: "infeasible", 4: "infeasible_or_unbounded", 5: "unbounded", 9: "time_limit", 12: "numeric"}.get(int(gp.Status), f"gurobi_status_{gp.Status}")
        if st == "optimal":
            g = float(lin.getValue()); vr = gp.getVarByName(o2_rev); vf = gp.getVarByName(o2_fwd)
            o2 = float((vr.X if vr is not None else 0.0) - (vf.X if vf is not None else 0.0))
            rows.append(dict(temp_C=float(Tc), status=st, growth=(g if g >= min_growth else 0.0), o2_uptake=o2))
        else:
            rows.append(dict(temp_C=float(Tc), status=st, growth=0.0, o2_uptake=float("nan")))
            if stop_on_infeasible and st == "infeasible": break
    return rows


def lexi_loglike(theta, ctx, specs):
    """gasflux_log_likelihood's arithmetic on lexi_flux's solution (zero_lik; clamp; floor; weight floor)."""
    nat = to_natural(theta, specs); pert = to_pert(theta, specs); pm = ctx["pm"]; resp = ctx.get("respiration") or {}
    if "clearance_mult" in nat:
        r = ctx["recipe"]; _prov.set_medium_recipe(pm, r["recipe_csv"], clearance_L_per_gDW_h=r["clearance"] * float(nat["clearance_mult"]), uptake_ub=r.get("uptake_ub", 1000.0), verbose=False)
        if ctx.get("c_max") is not None: add_total_carbon_constraint(pm, float(ctx["c_max"]))
    if "F_ETC_mult" in nat:
        from etcgem import etc_area as _ea
        _ea.add_etc_area_constraint(pm, ctx["etc_table"], _ea.budget_from_fraction(ctx["a_mem"], ctx["f_etc_nom"] * float(nat["F_ETC_mult"])))
    _GROWTH_LIN.pop(id(pm.ec.model), None)          # constraints may have been re-added: rebuild the parsimony sum
    rows = lexi_flux(pm, ctx["T"], pert, growth_tol=float(resp.get("growth_tol", 1e-6)))
    st = [r["status"] for r in rows]
    if any(s == "infeasible" for s in st): return float("-inf"), rows
    if len(rows) != len(ctx["T"]) or any(s != "optimal" for s in st): return float("nan"), rows      # unresolved: reported, never a number
    g = np.array([r["growth"] for r in rows]); o2 = np.array([r["o2_uptake"] for r in rows])
    dg = float(nat["disc_growth"]); var = ctx["growth_sd"] ** 2 + dg ** 2
    ll = float(-0.5 * np.sum((ctx["growth_obs"] - g) ** 2 / var + np.log(2 * np.pi * var)))
    keep = np.isfinite(o2) & (o2 > 0)
    if keep.sum() >= 1:
        dr = float(nat["disc_resp"]); rs = float(nat["resp_scale"]); floor = float(resp.get("log_o2_floor", 0.0))
        pred = np.log(o2[keep] * ctx["o2_conv"] * rs); obsl = np.log(ctx["resp_obs"][keep]); rel = ctx["resp_sd"][keep] / ctx["resp_obs"][keep]
        varr = rel ** 2 + dr ** 2 + floor ** 2; gs = resp.get("alive_soft_growth"); wf = float(resp.get("weight_floor", 1.0))
        w = np.maximum(np.minimum(1.0, g[keep] / float(gs)), wf) if gs else np.ones(int(keep.sum()))
        ll += float(-0.5 * np.sum(w * ((obsl - pred) ** 2 / varr + np.log(2 * np.pi * varr))))
    return ll, rows
