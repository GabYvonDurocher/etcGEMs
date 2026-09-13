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
from etcgem.calibration_multi import gasflux_log_likelihood          # noqa: E402
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
        with deadline(300, label):
            ll_p = gasflux_log_likelihood(tg_p.expand(th_s), ctx_p, sp_p)
            d1 = pt_v(rng.random(tg_v.D))[-2:]; d2 = pt_v(rng.random(tg_v.D))[-2:]
            ll_v1 = gasflux_log_likelihood(tg_v.expand(np.concatenate([th_s, d1])), ctx_v, sp_v)
            ll_v2 = gasflux_log_likelihood(tg_v.expand(np.concatenate([th_s, d2])), ctx_v, sp_v)
        same = (ll_p == ll_v1 == ll_v2 == -np.inf) or (np.isfinite(ll_p) and abs(ll_v1 - ll_p) <= 1e-12 and abs(ll_v2 - ll_p) <= 1e-12)
        rows.append(dict(label=label, ll_production=ll_p, ll_validation_1=ll_v1, ll_validation_2=ll_v2, diag_1=list(map(float, d1)), diag_2=list(map(float, d2)),
                         max_diff=(max(abs(ll_v1 - ll_p), abs(ll_v2 - ll_p)) if np.isfinite(ll_p) else 0.0), inert=bool(same)))
        if len(rows) % 20 == 0: print(f"[diag] {len(rows)}/100 {label:22s} prod {ll_p} val {ll_v1:.10f} {ll_v2:.10f} inert={same}", flush=True)
    df = pd.DataFrame(rows); df.to_csv(os.path.join(HERE, "task3_diagnostics.csv"), index=False)
    summ = dict(n=len(df), n_inert=int(df.inert.sum()), n_finite=int(np.isfinite(df.ll_production).sum()), n_neg_inf=int((df.ll_production == -np.inf).sum()),
                max_diff=float(df.max_diff.max()), tolerance=1e-12, config_hash_production=tg_p.config_hash(), config_hash_validation=tg_v.config_hash(),
                sampled_production=tg_p.names, sampled_validation=tg_v.names, seed=17303, wall_min=round((time.time() - t0) / 60, 1))
    json.dump(summ, open(os.path.join(HERE, "task3_diagnostics.json"), "w"), indent=1); print("[diag] SUMMARY", json.dumps(summ), flush=True)


if __name__ == "__main__":
    main()
