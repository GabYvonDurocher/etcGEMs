#!/usr/bin/env python3
"""T1 TASK 2 (first part) -- classify every missing prediction by SOLVER STATUS, not by NaN.

At every registered audit point (D0) and every saved stratum state, each temperature's growth
solve is (a) an UNRESOLVED NUMERICAL SOLVE -- status not optimal for a reason other than
infeasibility (time_limit, numeric, suboptimal, ...), or a solve that is 'infeasible' on one rung
but not on all -- or (b) a STRUCTURAL ZERO -- 'infeasible' on the first solve AND on every rung of
the registered bounded retry ladder (D0): fresh model same tolerances; fresh model with
OptimalityTol/FeasibilityTol 1e-12; fresh model, dual simplex only. Each rung under a 60 s alarm,
three attempts max. A temperature failing all rungs for a non-infeasible reason is UNRESOLVED and
is reported as such, never treated as zero.

Reads statuses from flux_tpc's own 'status' column. Incremental CSV. One expensive job at a time.
"""
import os, sys, json, time, hashlib
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
ARCH = os.path.abspath(os.path.join(ROOT, "..", "etcGEMs-p17-archive"))
for p in (os.path.join(ROOT, "src"), os.path.join(ROOT, "reports", "P6_convergence"),
          os.path.join(ROOT, "reports", "P11_nested"), os.path.join(ROOT, "reports", "P16_reduced"), HERE):
    if p not in sys.path: sys.path.insert(0, p)
os.chdir(ROOT)
from etcgem.calibration_multi import _build_gasflux_ctx, to_pert, to_natural, _set_default_solver   # noqa: E402
from etcgem.gasflux import flux_tpc, add_total_carbon_constraint                                    # noqa: E402
from etcgem import providers as _prov                                                                # noqa: E402
from p6_fits import FITS                                                                             # noqa: E402
from prior_transform import transform_factory                                                        # noqa: E402
from reduced import FULL_SPECS, FREE_SPECS, expand                                                   # noqa: E402
from alarm import deadline, Deadline, self_test                                                      # noqa: E402

SOLVE_S, BATCH_S = 60, 2 * 3600
FIT = [f for f in FITS if f[0] == "D_NLDM"][0]
_, CFG, MEDIUM, TABLE, OTU, C_MAX, ETC, PROTONS, FIT_K = FIT
PAY = dict(strain="eciML1515", medium=MEDIUM, experiment=f"gasflux_config{CFG}", table=TABLE, otu=OTU,
           c_max=C_MAX, etc_table=ETC, apply_protons=PROTONS, fit_clearance=FIT_K)
NAMES = [s.name for s in FULL_SPECS]
OUT = os.path.join(HERE, "task2_classify.csv")
ONLY_MISSING = "--only-missing" in sys.argv
if ONLY_MISSING: OUT = os.path.join(HERE, "task2_classify_batch2.csv")


def points():
    pt15 = transform_factory(FREE_SPECS); pts = []
    for e in json.load(open("reports/P17_inactive_prior/real_curvature_probe/evaluations.json")):
        pts.append(("D44:" + e["label"], expand(pt15(np.asarray(e["u"], float))), e["flux"]["status"]))
    for k, st in enumerate(json.load(open("reports/P17_inactive_prior/stratum_probe.json"))):
        pts.append((f"stratum:{st['tag']}:{st['stored_index']}", expand(pt15(np.asarray(st["start"], float))),
                    st["initial_flux"]["status"]))
    z = np.load(os.path.join(ARCH, "reports/P17_inactive_prior/validated_live_input.npz"))
    for i in range(z["theta"].shape[0]):
        pts.append((f"red2_6800:{i}", expand(np.asarray(z["theta"][i], float)), None))
    d = pd.read_csv("reports/P12_modes/task2c_converged.csv")
    for _, r in d.iterrows():
        pts.append(("P12:" + r.key, r[[f"x_{n}" for n in NAMES]].to_numpy(float), None))
    return pts


def solve_statuses(th, rung):
    """fresh model per call; rung 1 = registered tolerances, 2 = 1e-12, 3 = dual simplex"""
    ctx, sp = _build_gasflux_ctx(**PAY)
    resp = ctx.get("respiration") or {}
    nat = to_natural(th, sp); pert = to_pert(th, sp); pm = ctx["pm"]
    if "clearance_mult" in nat:
        r = ctx["recipe"]
        _prov.set_medium_recipe(pm, r["recipe_csv"], clearance_L_per_gDW_h=r["clearance"] * float(nat["clearance_mult"]),
                                uptake_ub=r.get("uptake_ub", 1000.0), verbose=False)
        if ctx.get("c_max") is not None: add_total_carbon_constraint(pm, float(ctx["c_max"]))
    tol = float(resp.get("tiebreak_tol", 1e-9)) if rung < 2 else 1e-12
    if rung == 3:
        pm.ec.model.solver.problem.setParam("Method", 1)          # dual simplex only
    df = flux_tpc(pm, ctx["T"], pert, metabolites=("o2",), tiebreak=str(resp.get("tiebreak", "none")),
                  growth_tol=float(resp.get("growth_tol", 1e-6)), tiebreak_tol=tol)
    return list(map(str, df["status"])), df["growth"].to_numpy(float).tolist(), df["o2_uptake"].to_numpy(float).tolist()


def main():
    self_test(); pts = points()
    if ONLY_MISSING:
        done = set(pd.read_csv(os.path.join(HERE, "task2_classify.csv")).label)
        pts = [p for p in pts if p[0] not in done]
        print(f"[cls] BATCH 2: {len(pts)} labels not reached by batch 1 ({len(done)} done)", flush=True)
    print(f"[cls] {len(pts)} points", flush=True)
    rows = []; t0 = time.time()
    for k, (label, th, saved_status) in enumerate(pts):
        if time.time() - t0 > BATCH_S:
            print("[cls] BATCH DEADLINE -- stopping, partial retained", flush=True); break
        row = dict(label=label, saved_status=";".join(saved_status) if saved_status else "")
        try:
            with deadline(SOLVE_S * 3, label):
                st1, g1, o1 = solve_statuses(th, 1)
            row["rung1"] = ";".join(st1); row["growth"] = ";".join(f"{x:.4g}" for x in g1)
            bad = [i for i, s in enumerate(st1) if s != "optimal"]
            if bad:
                with deadline(SOLVE_S * 3, label + " rung2"):
                    st2, _, _ = solve_statuses(th, 2)
                with deadline(SOLVE_S * 3, label + " rung3"):
                    st3, _, _ = solve_statuses(th, 3)
                row["rung2"] = ";".join(st2); row["rung3"] = ";".join(st3)
                cls = []
                for i in bad:
                    trio = (st1[i], st2[i], st3[i])
                    cls.append("STRUCTURAL_ZERO" if all(s == "infeasible" for s in trio) else
                               ("RESOLVED_ON_RETRY" if "optimal" in trio else "UNRESOLVED"))
                row["nonoptimal_T"] = ";".join(str(i) for i in bad); row["classes"] = ";".join(cls)
                row["n_structural_zero"] = cls.count("STRUCTURAL_ZERO"); row["n_unresolved"] = cls.count("UNRESOLVED")
                row["n_resolved_on_retry"] = cls.count("RESOLVED_ON_RETRY")
            else:
                row.update(nonoptimal_T="", classes="", n_structural_zero=0, n_unresolved=0, n_resolved_on_retry=0)
            row["agrees_with_saved"] = (";".join(st1) == row["saved_status"]) if saved_status else None
            row["status"] = "OK"
        except Deadline as e:
            row.update(status="UNRESOLVED_TIMEOUT", note=str(e), n_unresolved=12)
        rows.append(row)
        if k % 25 == 0 or row.get("n_unresolved", 0) or row.get("n_resolved_on_retry", 0):
            print(f"[cls] {k+1:4d}/{len(pts)} {label:28s} sz={row.get('n_structural_zero',0)} unres={row.get('n_unresolved',0)} "
                  f"retry={row.get('n_resolved_on_retry',0)} {row['status']}", flush=True)
            pd.DataFrame(rows).to_csv(OUT, index=False)
    df = pd.DataFrame(rows); df.to_csv(OUT, index=False)
    strat = df[df.label.str.startswith("stratum:")]
    summ = dict(n_points=len(pts), n_evaluated=len(df),
                temps_structural_zero=int(df.n_structural_zero.sum()), temps_unresolved=int(df.n_unresolved.sum()),
                temps_resolved_on_retry=int(df.n_resolved_on_retry.sum()),
                points_with_any_nonoptimal=int((df.n_structural_zero + df.n_unresolved + df.n_resolved_on_retry > 0).sum()),
                stratum_points=len(strat), stratum_temps_structural_zero=int(strat.n_structural_zero.sum()) if len(strat) else 0,
                stratum_temps_unresolved=int(strat.n_unresolved.sum()) if len(strat) else 0,
                saved_status_agreement=int((df.agrees_with_saved == True).sum()), saved_status_compared=int(df.agrees_with_saved.notna().sum()),
                wall_min=round((time.time() - t0) / 60, 1))
    json.dump(summ, open(os.path.join(HERE, "task2_classify_batch2.json" if ONLY_MISSING else "task2_classify.json"), "w"), indent=1)
    print(f"[cls] SUMMARY {summ}", flush=True)


if __name__ == "__main__":
    main()
