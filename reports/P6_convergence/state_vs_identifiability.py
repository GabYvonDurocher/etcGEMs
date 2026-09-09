#!/usr/bin/env python3
"""P6 addendum 5 -- is the E/F likelihood jitter STATE (the second call sees a model the first
one modified) or IDENTIFIABILITY (alternate optima in O2 at fixed growth)? Diagnosis only:
repeated likelihood evaluations and FVA, nothing fitted, nothing changed.

Per fit (D as the negative control), at one fixed theta (P4's MAP) and one other vector theta'
(a final-state walker):

  REUSE   one model, evaluated:  theta, theta  (consecutive)      -> spread_consecutive
                                  theta, theta', theta             -> |L(theta) - L(theta after theta')|
  REBUILD a model rebuilt from scratch before each evaluation of theta, twice
                                                                    -> spread_rebuild
  REBUILD+HISTORY  rebuild, evaluate theta' then theta              -> against the fresh value
  RESET   reuse, theta' then Gurobi basis reset then theta          -> does discarding the solver
                                                                       basis alone restore the fresh value?
  FVA     at the temperature where the O2 differs between the fresh and the after-theta'
          evaluation (per temperature O2 is recorded), the O2 range at growth held to its
          optimum, on the model in the after-theta' state -> is the O2 there a face or a vertex?
  MODEL DIFF  after theta' then theta: the ETC constraint ub, the carbon cap ub, the number of
          constraints and the medium's open exchange bounds, against a fresh model at theta
                                                                    -> is the model DATA identical?

Writes state_vs_identifiability.csv and .json beside this file.
"""
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, HERE)
os.chdir(ROOT)

from etcgem.calibration_multi import _build_gasflux_ctx, gasflux_log_likelihood, to_pert   # noqa: E402
from etcgem.gasflux import flux_tpc                                                        # noqa: E402
from etcgem.tpc import apply_state                                                         # noqa: E402
from p6_fits import FITS, p4_dir_for                                                       # noqa: E402

WANT = ("D_NLDM", "D_LB", "E_NLDM", "E_LB", "F_NLDM", "F_LB")


def build(fit):
    label, cfg, medium, table, otu, c_max, etc, protons, fit_k = fit
    return _build_gasflux_ctx(strain="eciML1515", medium=medium, experiment=f"gasflux_config{cfg}",
                              table=table, otu=otu, c_max=c_max, etc_table=etc,
                              apply_protons=protons, fit_clearance=fit_k)


def points(fit):
    label, cfg, medium = fit[0], fit[1], fit[2]
    d = os.path.join(ROOT, "strains", "eciML1515", "outputs", p4_dir_for(cfg, medium))
    ch = np.load(os.path.join(d, "chain.npy")); lp = np.load(os.path.join(d, "log_prob.npy"))
    i, j = np.unravel_index(np.nanargmax(lp), lp.shape)
    return ch[i, j], ch[-1, 0]


def ll_and_o2(th, ctx, specs):
    ll = gasflux_log_likelihood(th, ctx, specs)
    df = flux_tpc(ctx["pm"], ctx["T"], to_pert(th, specs), metabolites=("o2",))
    return ll, df["growth"].to_numpy(float), df["o2_uptake"].to_numpy(float)


def o2_fva_at(ctx, th, specs, T):
    m = ctx["pm"].ec.model
    apply_state(ctx["pm"].ec, float(T), to_pert(th, specs))
    g = m.slim_optimize()
    if g is None or not np.isfinite(g) or g < 1e-4:
        return np.nan, np.nan, float(g) if g is not None else np.nan
    rev, fwd = m.reactions.get_by_id("EX_o2_e_REV"), m.reactions.get_by_id("EX_o2_e")
    obj = m.objective.expression
    fix = m.problem.Constraint(obj, lb=g * (1 - 1e-6), name="_p6_fix")
    m.add_cons_vars([fix])
    out = {}
    try:
        for sense in ("min", "max"):
            m.objective = m.problem.Objective(rev.flux_expression - fwd.flux_expression, direction=sense)
            v = m.slim_optimize(); out[sense] = float(v) if v is not None else np.nan
    finally:
        m.remove_cons_vars([fix]); m.objective = m.problem.Objective(obj, direction="max"); m.solver.update()
    return out["min"], out["max"], float(g)


def model_fingerprint(ctx):
    m = ctx["pm"].ec.model
    fp = {"n_constraints": len(m.constraints), "n_variables": len(m.variables)}
    for name in ("etc_membrane_area", "total_carbon_uptake"):
        fp[name + "_ub"] = float(m.constraints[name].ub) if name in m.constraints else None
    ex = sorted((r.id, r.lower_bound, r.upper_bound) for r in m.exchanges)
    fp["exchange_bounds_hash"] = hash(tuple(ex))
    return fp


def main():
    rows, detail = [], {}
    for fit in FITS:
        label = fit[0]
        if label not in WANT:
            continue
        th, th2 = points(fit)
        # --- REUSE
        ctx, specs = build(fit)
        L1, g1, o1 = ll_and_o2(th, ctx, specs)
        L1b, _, _ = ll_and_o2(th, ctx, specs)
        ll_and_o2(th2, ctx, specs)
        L_after, g_after, o_after = ll_and_o2(th, ctx, specs)
        fp_after = model_fingerprint(ctx)
        # RESET: theta' then basis reset then theta, on the same reused model
        ll_and_o2(th2, ctx, specs)
        try:
            ctx["pm"].ec.model.solver.problem.reset(); reset_ok = True
        except Exception as e:
            reset_ok = False; print(f"[state] {label}: basis reset unavailable ({e!r})")
        L_reset, _, _ = ll_and_o2(th, ctx, specs)
        # FVA at the temperature where O2 differs most between fresh and after-theta'
        dO2 = np.nan_to_num(np.abs(o_after - o1), nan=0.0)
        kT = int(np.argmax(dO2)); T_star = float(ctx["T"][kT])
        # put the model back in the after-theta' state for the FVA (theta' then theta), then FVA at T*
        ll_and_o2(th2, ctx, specs); ll_and_o2(th, ctx, specs)
        fva_lo, fva_hi, g_star = o2_fva_at(ctx, th, specs, T_star)
        # --- REBUILD
        ctxA, specsA = build(fit); R1, gR1, oR1 = ll_and_o2(th, ctxA, specsA); fp_fresh = model_fingerprint(ctxA)
        ctxB, specsB = build(fit); R2, _, _ = ll_and_o2(th, ctxB, specsB)
        ctxC, specsC = build(fit); ll_and_o2(th2, ctxC, specsC); R3, _, oR3 = ll_and_o2(th, ctxC, specsC)
        fva_fresh_lo, fva_fresh_hi, _ = o2_fva_at(ctxA, th, specsA, T_star)
        row = dict(fit=label,
                   reuse_consecutive_spread=abs(L1 - L1b),
                   reuse_after_other_theta_delta=L_after - L1,
                   rebuild_spread=abs(R1 - R2),
                   rebuild_then_history_delta=R3 - R1,
                   reuse_reset_delta=(L_reset - L1) if reset_ok else np.nan,
                   fresh_vs_reused_first=R1 - L1,
                   T_of_max_o2_change=T_star, o2_fresh_at_T=float(o1[kT]), o2_after_at_T=float(o_after[kT]),
                   growth_fresh_at_T=float(g1[kT]), growth_after_at_T=float(g_after[kT]),
                   fva_o2_at_T_after_state=(fva_lo, fva_hi), fva_o2_at_T_fresh=(fva_fresh_lo, fva_fresh_hi),
                   model_data_identical=(fp_after == fp_fresh))
        rows.append(row)
        detail[label] = dict(T=ctx["T"].tolist(), o2_fresh=o1.tolist(), o2_after=o_after.tolist(),
                             o2_rebuild_history=oR3.tolist(), fp_after=fp_after, fp_fresh=fp_fresh,
                             L=dict(fresh=L1, fresh_repeat=L1b, after_other=L_after, reset=L_reset if reset_ok else None,
                                    rebuild1=R1, rebuild2=R2, rebuild_history=R3))
        print(f"[state] {label:7s} reuse: consecutive {abs(L1-L1b):.4f}, after theta' {L_after-L1:+.3f}, after theta'+reset {(L_reset-L1) if reset_ok else float('nan'):+.3f} | "
              f"rebuild: twice {abs(R1-R2):.4f}, rebuild+history {R3-R1:+.3f} | model data identical after theta': {fp_after == fp_fresh} | "
              f"T*={T_star:g}C O2 fresh {o1[kT]:.3f} after {o_after[kT]:.3f}; FVA at T* (after-state) [{fva_lo:.3f}, {fva_hi:.3f}], (fresh) [{fva_fresh_lo:.3f}, {fva_fresh_hi:.3f}]", flush=True)
    pd.DataFrame(rows).to_csv(os.path.join(HERE, "state_vs_identifiability.csv"), index=False)
    json.dump(detail, open(os.path.join(HERE, "state_vs_identifiability.json"), "w"), indent=1)
    print("[state] done", flush=True)


if __name__ == "__main__":
    main()
