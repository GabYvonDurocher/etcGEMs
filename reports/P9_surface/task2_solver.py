#!/usr/bin/env python3
"""P9 TASK 2 -- is the roughness the solver? Re-scan the roughest three lines (from
task1_summary.csv, by max_jump_frac) under (a) the defaults, (b) tightened Gurobi tolerances,
(c) a fixed method (dual simplex, no concurrent/barrier); then at the three largest jumps of the
default scan, solve both ends at every temperature and report which variables changed basis
status, and how growth and O2 uptake moved. Characterises; adopts nothing. Writes
task2_lines.csv, task2_params.json, task2_basis.csv beside this file.
"""
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "reports", "P6_convergence"))
os.chdir(ROOT)
from etcgem.calibration_multi import _build_gasflux_ctx, gasflux_log_likelihood, build_gasflux_specs, to_pert  # noqa: E402
from etcgem.tpc import apply_state                                                                    # noqa: E402
from p6_fits import FITS                                                                              # noqa: E402
from task1_scan import build, ll_reset, STEPS                                                         # noqa: E402

TIGHT = {"FeasibilityTol": 1e-9, "OptimalityTol": 1e-9, "BarConvTol": 1e-12}
FIXED = {"Method": 1}          # dual simplex only


def gp(ctx):
    return ctx["pm"].ec.model.solver.problem


def set_params(ctx, params):
    before = {}
    m = gp(ctx)
    for k, v in params.items():
        before[k] = m.getParamInfo(k)[2]
        m.setParam(k, v)
    return before


def scan(ctx, sp, theta0, sd, v):
    return np.array([ll_reset(theta0 + s * sd * v, ctx, sp) for s in STEPS])


def stats(vals):
    d1 = np.diff(vals); sc = int(np.sum(np.sign(d1[1:]) * np.sign(d1[:-1]) < 0)); j = float(np.max(np.abs(d1))); r = float(vals.max() - vals.min())
    return sc, j, j / r if r > 0 else np.nan


def basis_snapshot(ctx, th, sp):
    """per temperature: growth, O2 uptake, and the tuple of VBasis over all variables"""
    m = ctx["pm"].ec.model; pert = to_pert(th, sp); out = []
    gasflux_log_likelihood(th, ctx, sp)            # installs the medium at this theta
    for T in ctx["T"]:
        apply_state(ctx["pm"].ec, float(T), pert)
        try: gp(ctx).reset()
        except Exception: pass
        g = m.slim_optimize()
        if g is None or not np.isfinite(g):
            out.append((float(T), np.nan, np.nan, None)); continue
        o2 = float(m.reactions.get_by_id("EX_o2_e_REV").flux - m.reactions.get_by_id("EX_o2_e").flux)
        vb = np.array([var.VBasis for var in gp(ctx).getVars()], int)
        out.append((float(T), float(g), o2, vb))
    return out


def main():
    fit = [f for f in FITS if f[0] == "D_NLDM"][0]
    meta = json.load(open(os.path.join(HERE, "task1_meta.json"))); theta0 = np.array(meta["theta0"]); sd = np.array(meta["sd"]); names = meta["names"]; D = len(names)
    summ = pd.read_csv(os.path.join(HERE, "task1_summary.csv")).sort_values("max_jump_frac", ascending=False)
    top = summ.line.head(3).tolist(); print(f"[solver] roughest three lines: {top}", flush=True)
    # rebuild the directions exactly as task1 did
    import emcee
    b = emcee.backends.HDFBackend(os.path.join(ROOT, "strains", "eciML1515", "outputs", "calibration_configD_NLDM_recipe_P7_w128", "chain.h5"), read_only=True)
    X = b.get_chain()[250:].reshape(-1, D); Z = (X - X.mean(0)) / X.std(0); ev, evecs = np.linalg.eigh(np.cov(Z, rowvar=False)); evecs = evecs[:, np.argsort(ev)[::-1]]
    rng = np.random.default_rng(11); rnd = []
    for k in range(3):
        v = rng.standard_normal(D); rnd.append(v / np.linalg.norm(v))
    def direction(lname):
        if lname.startswith("axis:"): e = np.zeros(D); e[names.index(lname[5:])] = 1.0; return e
        if lname.startswith("PC"): v = evecs[:, int(lname[2:]) - 1]; return v / np.linalg.norm(v)
        return rnd[int(lname[6:]) - 1]
    rows, params = [], {}
    for lname in top:
        v = direction(lname)
        ctx, sp = build(fit)
        params["defaults_read_back"] = {k: gp(ctx).getParamInfo(k)[2] for k in list(TIGHT) + list(FIXED)}
        vals_def = scan(ctx, sp, theta0, sd, v)
        before = set_params(ctx, TIGHT); vals_tight = scan(ctx, sp, theta0, sd, v); params["tight_before"] = before; params["tight_after"] = TIGHT
        for k, val in before.items(): gp(ctx).setParam(k, val)
        before2 = set_params(ctx, FIXED); vals_fixed = scan(ctx, sp, theta0, sd, v); params["fixed_before"] = before2; params["fixed_after"] = FIXED
        for k, val in before2.items(): gp(ctx).setParam(k, val)
        for kind, vals in (("defaults", vals_def), ("tight tolerances", vals_tight), ("dual simplex only", vals_fixed)):
            sc, j, jf = stats(vals)
            rows.append(dict(line=lname, setting=kind, sign_changes=sc, max_jump=j, max_jump_frac=jf, ll_at_map=float(vals[20]),
                             max_abs_diff_vs_defaults=float(np.max(np.abs(vals - vals_def)))))
            print(f"[solver] {lname:22s} {kind:18s} sign changes {sc:2d}  max jump {j:8.3f} ({100*jf:5.1f} %)  max |diff vs defaults| {np.max(np.abs(vals-vals_def)):.2e}", flush=True)
        pd.DataFrame(rows).to_csv(os.path.join(HERE, "task2_lines.csv"), index=False)
    json.dump(params, open(os.path.join(HERE, "task2_params.json"), "w"), indent=2, default=float)
    # basis changes at the three largest jumps (default scan, across all lines of task1)
    L = pd.read_csv(os.path.join(HERE, "task1_lines.csv")); jumps = []
    for lname, sub in L.groupby("line"):
        vals = sub.logL.to_numpy(); d1 = np.abs(np.diff(vals)); k = int(np.argmax(d1)); jumps.append((float(d1[k]), lname, k))
    jumps.sort(reverse=True); brows = []
    for jval, lname, k in jumps[:3]:
        v = direction(lname); ctx, sp = build(fit)
        a = basis_snapshot(ctx, theta0 + STEPS[k] * sd * v, sp); bb = basis_snapshot(ctx, theta0 + STEPS[k + 1] * sd * v, sp)
        nvar = len(a[0][3]) if a[0][3] is not None else 0
        for (T, ga, oa, va), (_, gb, ob, vb) in zip(a, bb):
            nchg = int(np.sum(va != vb)) if (va is not None and vb is not None) else -1
            brows.append(dict(line=lname, step_from=float(STEPS[k]), step_to=float(STEPS[k + 1]), jump_logL=jval, T_C=T,
                              growth_from=ga, growth_to=gb, d_growth=(gb - ga) if np.isfinite(ga) and np.isfinite(gb) else np.nan,
                              o2_from=oa, o2_to=ob, d_o2=(ob - oa) if np.isfinite(oa) and np.isfinite(ob) else np.nan,
                              n_vars=nvar, n_basis_changes=nchg))
        sub = pd.DataFrame([r for r in brows if r["line"] == lname])
        print(f"[solver] jump {jval:.3f} on {lname} between {STEPS[k]:+.2f} and {STEPS[k+1]:+.2f} sd: basis changes per T "
              f"{sub.n_basis_changes.tolist()} of {nvar} vars; max |d growth| {np.nanmax(np.abs(sub.d_growth)):.4f}; max |d O2| {np.nanmax(np.abs(sub.d_o2)):.3f}", flush=True)
    pd.DataFrame(brows).to_csv(os.path.join(HERE, "task2_basis.csv"), index=False)
    print("[solver] done", flush=True)


if __name__ == "__main__":
    main()
