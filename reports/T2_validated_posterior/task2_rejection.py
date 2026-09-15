#!/usr/bin/env python3
"""T2 TASK 2 -- the prior rejection rate (item 1.33's number): 2,000 registered prior draws (seed 17302)
through a 16-process pool; the fraction returning -inf, its Wilson 95 % interval, and the temperature at
which rejection first fires in the registered order. FILE with a __main__ guard (OPEN_ITEMS section 4).
Also usable by the driver for check (d): `rejection(seed_sequence, n, nproc)`."""
import os, sys, json, time, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from t2_audit_points import ROOT     # noqa: E402
os.chdir(ROOT)
from t2_target import payload, Target   # noqa: E402
from t2_prior import transform_factory  # noqa: E402
from etcgem import calibration_multi as CM   # noqa: E402
from etcgem.calibration_multi import _gwinit, _set_default_solver, to_pert, to_natural   # noqa: E402
from etcgem.gasflux import flux_tpc, add_total_carbon_constraint, UnresolvedSolve   # noqa: E402
from etcgem import providers as _prov   # noqa: E402

_TG = None


def _verdict(u):
    """worker: -inf?, first infeasible T, peak growth (feasible only), n solves"""
    global _TG
    if _TG is None: _TG = Target(CM._GSPECS)
    pt = transform_factory(_TG.sampled); th = _TG.expand(pt(np.asarray(u, float)))
    ctx, specs = CM._GCTX, CM._GSPECS; resp = ctx["respiration"]; nat = to_natural(th, specs); pert = to_pert(th, specs); pm = ctx["pm"]
    if "clearance_mult" in nat:
        r = ctx["recipe"]; _prov.set_medium_recipe(pm, r["recipe_csv"], clearance_L_per_gDW_h=r["clearance"] * float(nat["clearance_mult"]), uptake_ub=r.get("uptake_ub", 1000.0), verbose=False)
        if ctx.get("c_max") is not None: add_total_carbon_constraint(pm, float(ctx["c_max"]))
    try:
        df = flux_tpc(pm, ctx["T"], pert, metabolites=("o2",), tiebreak=str(resp.get("tiebreak", "none")), growth_tol=float(resp.get("growth_tol", 1e-6)),
                      tiebreak_tol=float(resp.get("tiebreak_tol", 1e-9)), stop_on_infeasible=True, retry_ladder=True)
    except UnresolvedSolve as e:
        return dict(unresolved=True, msg=str(e))
    at = df.attrs.get("infeasible_at")
    return dict(unresolved=False, rejected=(at is not None), first_T=at, n_solves=int(len(df)), peak_growth=(float(np.nanmax(df["growth"])) if at is None else None))


def rejection(seed, n, nproc=16, validation=False):
    from multiprocessing import Pool
    solver = _set_default_solver("gurobi")
    ctx0, specs0 = None, None
    from t2_target import build
    ctx0, specs0 = build(validation); tg = Target(specs0)
    rng = np.random.default_rng(seed); U = rng.random((n, tg.D)); t0 = time.time()
    with Pool(nproc, initializer=_gwinit, initargs=(dict(payload(validation), solver=solver),)) as pool:
        out = pool.map(_verdict, list(U), chunksize=8)
    wall = time.time() - t0
    unres = [o for o in out if o["unresolved"]]; ok = [o for o in out if not o["unresolved"]]
    k = sum(o["rejected"] for o in ok); m = len(ok); p = k / m
    z = 1.959964; den = 1 + z * z / m; c = (p + z * z / (2 * m)) / den; h = z * np.sqrt(p * (1 - p) / m + z * z / (4 * m * m)) / den
    firstT = {}
    for o in ok:
        if o["rejected"]: firstT[o["first_T"]] = firstT.get(o["first_T"], 0) + 1
    feas = [o for o in ok if not o["rejected"]]; living = sum(1 for o in feas if o["peak_growth"] >= 0.5 * 2.0761)
    return dict(seed=(seed if isinstance(seed, int) else list(seed)), n=n, n_unresolved=len(unres), n_rejected=k, n_evaluated=m, fraction=p, wilson95=[c - h, c + h],
                first_infeasible_T_counts={str(t): v for t, v in sorted(firstT.items())}, n_feasible=len(feas), n_living_of_feasible=living,
                solves_total=int(sum(o["n_solves"] for o in ok)), wall_s=round(wall, 1), unresolved=unres[:5])


if __name__ == "__main__":
    res = rejection(17302, 2000, 16, validation=False)
    json.dump(res, open(os.path.join(HERE, "task2_rejection.json"), "w"), indent=1)
    print("[rej] SUMMARY", json.dumps(res), flush=True)
