#!/usr/bin/env python3
"""T2 TASK 3 -- prove the two diagnostic coordinates enter nothing: 100 registered physical points (the 13
audit points T1 classified feasible everywhere, then prior draws with seed 17303 -- D0 -- until 100), each
evaluated under the PRODUCTION specs and under the VALIDATION specs with two independent diagnostic draws.
log L identical to 1e-12 (or -inf in all three). Records both configuration hashes."""
import os, sys, json, time, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from t2_audit_points import points, drop_f_metab, t1_classes, ROOT     # noqa: E402
os.chdir(ROOT)
from t2_target import build, Target                                  # noqa: E402
from t2_prior import transform_factory                               # noqa: E402
from etcgem.calibration_multi import gasflux_log_likelihood, to_pert  # noqa: E402
from alarm import deadline, self_test                                # noqa: E402


def main():
    self_test(); t0 = time.time()
    ctx_p, sp_p = build(validation=False); tg_p = Target(sp_p)
    ctx_v, sp_v = build(validation=True); tg_v = Target(sp_v)
    assert tg_v.names[:tg_p.D] == tg_p.names and tg_v.D == tg_p.D + 2
    cls = t1_classes(); feasible = cls[cls.n_structural_zero == 0].label.tolist()
    pts = [(l, tg_p.reduce(drop_f_metab(th))) for l, th in points() if l in feasible]
    rng = np.random.default_rng(17303); pt_p = transform_factory(tg_p.sampled); pt_v = transform_factory(tg_v.sampled)
    k = 0
    while len(pts) < 100:
        pts.append((f"prior17303:{k}", pt_p(rng.random(tg_p.D)))); k += 1
    rows = []
    for label, th_s in pts:
        with deadline(600, label):
            pert_p = to_pert(tg_p.expand(th_s), sp_p)
            ll_p = gasflux_log_likelihood(tg_p.expand(th_s), ctx_p, sp_p)               # production, instance A
            d1 = pt_v(rng.random(tg_v.D))[-2:]; d2 = pt_v(rng.random(tg_v.D))[-2:]
            th_v1 = tg_v.expand(np.concatenate([th_s, d1])); th_v2 = tg_v.expand(np.concatenate([th_s, d2]))
            pert_same = (to_pert(th_v1, sp_v) == pert_p) and (to_pert(th_v2, sp_v) == pert_p)   # EXACT: what the model receives
            ll_v1 = gasflux_log_likelihood(th_v1, ctx_p, sp_v)                           # validation specs, SAME instance A
            ll_v2 = gasflux_log_likelihood(th_v2, ctx_p, sp_v)
            ll_p2 = gasflux_log_likelihood(tg_p.expand(th_s), ctx_p, sp_p)              # production repeat, instance A
        if ll_p == -np.inf:
            inert12 = (ll_v1 == ll_v2 == ll_p2 == -np.inf); dmax = 0.0; floor = 0.0
        else:
            dmax = max(abs(ll_v1 - ll_p), abs(ll_v2 - ll_p)); floor = abs(ll_p2 - ll_p); inert12 = bool(dmax <= 1e-12)
        rows.append(dict(label=label, ll_production=ll_p, ll_validation_1=ll_v1, ll_validation_2=ll_v2, ll_production_repeat=ll_p2, diag_1=list(map(float, d1)), diag_2=list(map(float, d2)),
                         perturbation_identical=bool(pert_same), max_diff_same_instance=float(dmax), repeat_floor=float(floor), inert_1e12=bool(inert12),
                         within_repeat_floor=bool(dmax <= max(1e-12, floor))))
        if len(rows) % 20 == 0: print(f"[diag] {len(rows)}/100 {label:22s} prod {ll_p} val {ll_v1} {ll_v2} repeat {ll_p2} pert_same={pert_same} dmax={dmax:.2e} floor={floor:.2e}", flush=True)
    df = pd.DataFrame(rows); df.to_csv(os.path.join(HERE, "task3_diagnostics.csv"), index=False)
    fin = df[np.isfinite(df.ll_production)]
    summ = dict(n=len(df), n_perturbation_identical=int(df.perturbation_identical.sum()), n_inert_1e12=int(df.inert_1e12.sum()), n_within_repeat_floor=int(df.within_repeat_floor.sum()),
                n_finite=len(fin), n_neg_inf=int((df.ll_production == -np.inf).sum()), max_diff_same_instance=float(df.max_diff_same_instance.max()), max_repeat_floor=float(df.repeat_floor.max()),
                median_repeat_floor=float(fin.repeat_floor.median()) if len(fin) else 0.0, tolerance=1e-12, config_hash_production=tg_p.config_hash(), config_hash_validation=tg_v.config_hash(),
                sampled_production=tg_p.names, sampled_validation=tg_v.names, seed=17303, wall_min=round((time.time() - t0) / 60, 1))
    json.dump(summ, open(os.path.join(HERE, "task3_diagnostics.json"), "w"), indent=1); print("[diag] SUMMARY", json.dumps(summ), flush=True)


if __name__ == "__main__":
    main()
