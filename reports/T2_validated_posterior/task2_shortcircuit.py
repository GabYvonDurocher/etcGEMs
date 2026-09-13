#!/usr/bin/env python3
"""T2 TASK 2 -- the short-circuit: 50 registered prior draws (seed 17301), each solved with and without
stop_on_infeasible; identical verdicts required; solves saved counted."""
import os, sys, json, time, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from t2_audit_points import ROOT     # noqa: E402
os.chdir(ROOT)
from t2_target import build, Target  # noqa: E402
from t2_prior import transform_factory   # noqa: E402
from etcgem.calibration_multi import to_pert, to_natural   # noqa: E402
from etcgem.gasflux import flux_tpc, add_total_carbon_constraint   # noqa: E402
from etcgem import providers as _prov   # noqa: E402
from alarm import deadline, self_test   # noqa: E402


def solve(ctx, specs, th, stop):
    resp = ctx["respiration"]; nat = to_natural(th, specs); pert = to_pert(th, specs); pm = ctx["pm"]
    if "clearance_mult" in nat:
        r = ctx["recipe"]; _prov.set_medium_recipe(pm, r["recipe_csv"], clearance_L_per_gDW_h=r["clearance"] * float(nat["clearance_mult"]), uptake_ub=r.get("uptake_ub", 1000.0), verbose=False)
        if ctx.get("c_max") is not None: add_total_carbon_constraint(pm, float(ctx["c_max"]))
    df = flux_tpc(pm, ctx["T"], pert, metabolites=("o2",), tiebreak=str(resp.get("tiebreak", "none")), growth_tol=float(resp.get("growth_tol", 1e-6)),
                  tiebreak_tol=float(resp.get("tiebreak_tol", 1e-9)), stop_on_infeasible=stop, retry_ladder=True)
    st = list(map(str, df["status"])); return ("infeasible" in st), len(df), (df.attrs.get("infeasible_at")), st


def main():
    self_test(); ctx, specs = build(validation=False); tg = Target(specs); pt = transform_factory(tg.sampled)
    rng = np.random.default_rng(17301); U = rng.random((50, tg.D)); rows = []; t0 = time.time()
    for i, u in enumerate(U):
        th = tg.expand(pt(u))
        with deadline(600, f"draw {i}"):
            ta = time.time(); v1, n1, at1, st1 = solve(ctx, specs, th, True); ta = time.time() - ta
            tb = time.time(); v2, n2, at2, st2 = solve(ctx, specs, th, False); tb = time.time() - tb
        rows.append(dict(draw=i, infeasible_short=v1, infeasible_full=v2, solves_short=n1, solves_full=n2, first_infeasible_T=at1,
                         full_first_infeasible_T=(next((ctx["T"][k] for k, s in enumerate(st2) if s == "infeasible"), None)), agree=(v1 == v2), s_short=round(ta, 2), s_full=round(tb, 2)))
    import pandas as pd; df = pd.DataFrame(rows); df.to_csv(os.path.join(HERE, "task2_shortcircuit.csv"), index=False)
    summ = dict(n=50, seed=17301, agree=int(df.agree.sum()), n_infeasible=int(df.infeasible_full.sum()), solves_short=int(df.solves_short.sum()), solves_full=int(df.solves_full.sum()),
                first_T_agrees=int((df.first_infeasible_T.fillna(-1) == df.full_first_infeasible_T.fillna(-1)).sum()), wall_s_short=float(df.s_short.sum()), wall_s_full=float(df.s_full.sum()), wall_min=round((time.time() - t0) / 60, 1))
    json.dump(summ, open(os.path.join(HERE, "task2_shortcircuit.json"), "w"), indent=1); print("[sc] SUMMARY", json.dumps(summ), flush=True)


if __name__ == "__main__":
    main()
