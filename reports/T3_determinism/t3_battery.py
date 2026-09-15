#!/usr/bin/env python3
"""T3 TASK 1 -- one battery per invocation: --scheme ref | A | B | C | D | Cverify. FILE with a __main__ guard.
Every evaluation records value, wall-clock and per-temperature statuses. Protocol and budgets: DECISIONS D0."""
import os, sys, json, time, argparse, signal, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
for p in (os.path.join(ROOT, "src"), os.path.join(ROOT, "reports", "P6_convergence"), os.path.join(ROOT, "reports", "T2_validated_posterior"), HERE):
    if p not in sys.path: sys.path.insert(0, p)
os.chdir(ROOT)
from etcgem import calibration_multi as CM
from etcgem import gasflux as GF
from etcgem.calibration_multi import _gwinit, _set_default_solver, gasflux_log_likelihood
from t2_target import payload as d_payload
from alarm import deadline, Deadline, self_test
BUDGET_MIN = {"ref": 15, "A": 60, "B": 60, "C": 60, "D": 30, "Cverify": 15}
_LAST = {"statuses": None, "rows": None}
_ORIG = {}


# ---------------- worker-side ----------------
def _record_flux(*a, **k):
    df = _ORIG["flux_tpc"](*a, **k); _LAST["statuses"] = list(map(str, df["status"])); return df


def _init(pay, scheme):
    _gwinit(dict(pay, solver=_set_default_solver("gurobi")))
    _ORIG["flux_tpc"] = GF.flux_tpc; GF.flux_tpc = _record_flux            # record statuses; same path
    if scheme == "B":
        _ORIG["apply_state"] = GF.apply_state; _ORIG["tiebroken"] = GF._tiebroken_solve
        def apply_reset(ecm, Tc, pert):
            _ORIG["apply_state"](ecm, Tc, pert); ecm.model.solver.problem.reset()      # discard solution + basis before the growth solve
        def tiebroken_reset(m, g, tiebreak, growth_tol, **kw):
            m.solver.problem.reset(); return _ORIG["tiebroken"](m, g, tiebreak, growth_tol, **kw)   # and before the tie-break solve
        GF.apply_state = apply_reset; GF._tiebroken_solve = tiebroken_reset


def _eval(args):
    label, theta = args; t0 = time.time(); _LAST["statuses"] = None
    try:
        with deadline(300, label):
            ll = float(gasflux_log_likelihood(np.asarray(theta, float), CM._GCTX, CM._GSPECS))
        st = _LAST["statuses"]
    except GF.UnresolvedSolve as e:
        ll, st = float("nan"), [f"UNRESOLVED:{e}"]
    except Deadline as e:
        ll, st = float("nan"), [f"TIMEOUT:{e}"]
    return dict(label=label, value=ll, wall=time.time() - t0, statuses=st, pid=os.getpid())


def _eval_C(args):
    from lexi_tiebreak import lexi_loglike
    label, theta = args; t0 = time.time()
    try:
        with deadline(300, label):
            ll, rows = lexi_loglike(np.asarray(theta, float), CM._GCTX, CM._GSPECS)
    except Deadline as e:
        ll, rows = float("nan"), [dict(status=f"TIMEOUT:{e}")]
    return dict(label=label, value=float(ll), wall=time.time() - t0, statuses=[r["status"] for r in rows], growth=[r.get("growth") for r in rows], o2=[r.get("o2_uptake") for r in rows], pid=os.getpid())


def _eval_pfba_fresh_detail(args):
    """for Cverify: the current pFBA path's growth/O2 per temperature, fresh, no short-circuit"""
    label, theta = args
    from etcgem.calibration_multi import to_natural, to_pert
    ctx, specs = CM._GCTX, CM._GSPECS; nat = to_natural(theta, specs); pert = to_pert(theta, specs); pm = ctx["pm"]; resp = ctx["respiration"]
    if "clearance_mult" in nat:
        r = ctx["recipe"]; CM._prov.set_medium_recipe(pm, r["recipe_csv"], clearance_L_per_gDW_h=r["clearance"] * float(nat["clearance_mult"]), uptake_ub=r.get("uptake_ub", 1000.0), verbose=False) if hasattr(CM, "_prov") else None
    from etcgem import providers as _prov
    if "clearance_mult" in nat:
        r = ctx["recipe"]; _prov.set_medium_recipe(pm, r["recipe_csv"], clearance_L_per_gDW_h=r["clearance"] * float(nat["clearance_mult"]), uptake_ub=r.get("uptake_ub", 1000.0), verbose=False)
        if ctx.get("c_max") is not None: GF.add_total_carbon_constraint(pm, float(ctx["c_max"]))
    if "F_ETC_mult" in nat:
        from etcgem import etc_area as _ea
        _ea.add_etc_area_constraint(pm, ctx["etc_table"], _ea.budget_from_fraction(ctx["a_mem"], ctx["f_etc_nom"] * float(nat["F_ETC_mult"])))
    df = _ORIG["flux_tpc"](pm, ctx["T"], pert, metabolites=("o2",), tiebreak=str(resp.get("tiebreak", "none")), growth_tol=float(resp.get("growth_tol", 1e-6)), tiebreak_tol=float(resp.get("tiebreak_tol", 1e-9)))
    return dict(label=label, statuses=list(map(str, df["status"])), growth=df["growth"].tolist(), o2=df["o2_uptake"].tolist())


# ---------------- parent ----------------
def order(labels, rounds, seed=17403):
    rng = np.random.default_rng(seed); out = []
    for r in range(rounds):
        perm = rng.permutation(len(labels))
        if out and labels[perm[0]] == out[-1][1]: perm = np.roll(perm, 1)     # never the same input twice in succession
        out += [(r, labels[i]) for i in perm]
    return out


def run_battery(scheme, n):
    from multiprocessing import Pool
    inp = json.load(open(os.path.join(HERE, "inputs.json"))); items = inp["inputs"]; meta = inp["meta"]
    groups = {"D_NLDM_validation": (d_payload(True), [x for x in items if x["space"] == "D_NLDM_validation"]),
              "E_LB": (meta["E_LB_payload"], [x for x in items if x["space"] == "E_LB"])}
    fn = {"A": _eval, "B": _eval, "C": _eval_C, "D": _eval, "ref": _eval, "Cverify": _eval_pfba_fresh_detail}[scheme]
    results = []; t0 = time.time()
    for space, (pay, its) in groups.items():
        theta = {x["label"]: x["theta"] for x in its}; labels = [x["label"] for x in its]
        if scheme in ("ref", "D", "Cverify"):
            reps = {"ref": 2, "D": n, "Cverify": 1}[scheme]
            seq = [(r, l) for r in range(reps) for l in labels]
            pool_kw = dict(processes=1, initializer=_init, initargs=(pay, scheme), maxtasksperchild=1)   # a FRESH process (fresh model) per evaluation
        else:
            seq = order(labels, n)
            pool_kw = dict(processes=1, initializer=_init, initargs=(pay, scheme))                        # ONE persistent worker
        if scheme == "Cverify":
            # C in a fresh process per input, then pFBA in a fresh process per input
            with Pool(processes=1, initializer=_init, initargs=(pay, "C"), maxtasksperchild=1) as pool:
                c_res = pool.map(_eval_C, [(l, theta[l]) for l in labels], chunksize=1)
            with Pool(**pool_kw) as pool:
                p_res = pool.map(fn, [(l, theta[l]) for l in labels], chunksize=1)
            for c, p in zip(c_res, p_res): results.append(dict(space=space, label=c["label"], C=c, pfba=p))
            continue
        with Pool(**pool_kw) as pool:
            for k, res in enumerate(pool.imap(fn, [(l, theta[l]) for _, l in seq], chunksize=1)):
                res.update(space=space, scheme=scheme, round=seq[k][0], k=k); results.append(res)
                if k % 50 == 0 or k == len(seq) - 1:
                    print(f"[{scheme}] {space} {k+1}/{len(seq)} {res['label']:30s} {res['value']!s:>22} {res['wall']:.2f}s", flush=True)
                    json.dump(dict(scheme=scheme, n=n, results=results, elapsed_min=round((time.time() - t0) / 60, 2)), open(os.path.join(HERE, f"battery_{scheme}.json"), "w"))
    json.dump(dict(scheme=scheme, n=n, results=results, elapsed_min=round((time.time() - t0) / 60, 2), complete=True), open(os.path.join(HERE, f"battery_{scheme}.json"), "w"))
    print(f"[{scheme}] done: {len(results)} records in {(time.time() - t0) / 60:.1f} min", flush=True)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--scheme", required=True); ap.add_argument("--n", type=int, default=50); a = ap.parse_args()
    self_test()
    def _cap(*_): raise Deadline(f"battery {a.scheme} budget {BUDGET_MIN[a.scheme]} min")
    signal.signal(signal.SIGALRM, _cap); signal.alarm(int(BUDGET_MIN[a.scheme] * 60))
    try:
        run_battery(a.scheme, a.n)
    except Deadline as e:
        print(f"[{a.scheme}] BUDGET CAP: {e} -- partial results retained", flush=True); sys.exit(3)
    finally:
        signal.alarm(0)


if __name__ == "__main__":
    main()
