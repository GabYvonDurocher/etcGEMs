#!/usr/bin/env python3
"""T2 TASK 2 -- the invariant at all 876 audit points under the REVISED target (f_metab removed,
infeasibility -> -inf), read from the strain config exactly as the sampler will read it.
Prediction (D0): every point T1 classified feasible at all 12 T reproduces its old log L to 1e-6;
every point with a STRUCTURAL_ZERO at any T is exactly -inf. Any feasible point that moves or any
infeasible point not at -inf STOPS. Single process, one ctx (warm state; P10 D3a), 120 s alarm/eval."""
import os, sys, json, time, hashlib, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from t2_audit_points import points, drop_f_metab, t1_classes, t1_old_logl, ROOT   # noqa: E402
os.chdir(ROOT)
from t2_target import build                                                        # noqa: E402
from etcgem.calibration_multi import gasflux_log_likelihood                        # noqa: E402
from etcgem.gasflux import UnresolvedSolve                                         # noqa: E402
from alarm import deadline, Deadline, self_test                                    # noqa: E402
TOL = 1e-6


def main():
    self_test(); t0 = time.time()
    ctx, specs = build(validation=False)
    resp = ctx["respiration"]; assert resp.get("infeasible") == "zero_lik", resp
    assert "f_metab" not in [s.name for s in specs] and len(specs) == 15, [s.name for s in specs]
    cls = t1_classes(); old, strat_old = t1_old_logl()
    # T1's stratum labels repeat (2 stored x 3 seeds, D8); match by order within label
    strat_iter = {}
    rows = []
    for k, (label, th16) in enumerate(points()):
        c = cls[cls.label == label]
        if label.startswith("stratum:"):
            j = strat_iter.get(label, 0); strat_iter[label] = j + 1
            n_sz = int(c.iloc[j].n_structural_zero); ll_old = float([v for (p, v) in strat_old if p == label][j])
        else:
            n_sz = int(c.iloc[0].n_structural_zero); ll_old = float(old[label])
        expected = "NEG_INF" if n_sz > 0 else "UNCHANGED"
        th = drop_f_metab(th16); row = dict(label=label, t1_n_structural_zero=n_sz, expected=expected, ll_old=ll_old)
        try:
            with deadline(120, label):
                ll = gasflux_log_likelihood(th, ctx, specs)
            row["ll_new"] = float(ll)
            if expected == "NEG_INF":
                row["verdict"] = "OK" if ll == -np.inf else "STOP:infeasible point not at -inf"
                row["diff"] = float("nan")
            else:
                row["diff"] = float(abs(ll - ll_old)) if np.isfinite(ll) else float("inf")
                row["verdict"] = "OK" if row["diff"] <= TOL else "STOP:feasible point moved"
        except UnresolvedSolve as e:
            row.update(ll_new=float("nan"), diff=float("nan"), verdict=f"UNRESOLVED:{e}")
        except Deadline as e:
            row.update(ll_new=float("nan"), diff=float("nan"), verdict=f"UNRESOLVED_TIMEOUT:{e}")
        rows.append(row)
        if (k + 1) % 100 == 0 or row["verdict"] != "OK":
            print(f"[inv] {k+1:4d}/876 {label:26s} {expected:9s} new {row['ll_new']} old {ll_old:.6f} diff {row['diff']} {row['verdict']}", flush=True)
            pd.DataFrame(rows).to_csv(os.path.join(HERE, "task2_invariant.csv"), index=False)
    df = pd.DataFrame(rows); df.to_csv(os.path.join(HERE, "task2_invariant.csv"), index=False)
    feas = df[df.expected == "UNCHANGED"]; inf_ = df[df.expected == "NEG_INF"]
    summ = dict(n=len(df), n_expected_unchanged=len(feas), n_expected_neg_inf=len(inf_),
                n_unchanged_ok=int((feas.verdict == "OK").sum()), max_feasible_diff=float(feas["diff"].max()),
                n_neg_inf_ok=int((inf_.verdict == "OK").sum()), n_stop=int(df.verdict.str.startswith("STOP").sum()),
                n_unresolved=int(df.verdict.str.startswith("UNRESOLVED").sum()), tolerance=TOL, wall_min=round((time.time() - t0) / 60, 1),
                sha256_csv=hashlib.sha256(open(os.path.join(HERE, "task2_invariant.csv"), "rb").read()).hexdigest())
    json.dump(summ, open(os.path.join(HERE, "task2_invariant.json"), "w"), indent=1)
    print("[inv] SUMMARY", json.dumps(summ), flush=True)


if __name__ == "__main__":
    main()
