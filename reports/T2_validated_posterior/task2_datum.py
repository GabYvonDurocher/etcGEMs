#!/usr/bin/env python3
"""T2 TASK 2 -- T1's 13 datum-table points under zero_lik: the seven stratum/D44 rows total -inf with
every positive measurement accounted for (the parameter set has zero likelihood; nothing escapes
because there is no score to escape from); the six feasible P12 rows unchanged to 1e-9."""
import os, sys, json, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from t2_audit_points import points, drop_f_metab, ROOT, T1     # noqa: E402
os.chdir(ROOT)
from t2_target import build                                    # noqa: E402
from etcgem.calibration_multi import gasflux_log_likelihood    # noqa: E402
from alarm import deadline, self_test                          # noqa: E402


def main():
    self_test(); ctx, specs = build(validation=False); assert ctx["respiration"].get("infeasible") == "zero_lik"
    tot = pd.read_csv(os.path.join(T1, "task2_datum_totals.csv")); tab = pd.read_csv(os.path.join(T1, "task2_datum_table.csv"))
    pts = dict(); order = []
    for label, th in points():
        if label == "D44:baseline_start" or label.startswith("stratum:") or label in ("P12:A(b20)", "P12:Bstar(b8)", "P12:p81(b7)", "P12:worst(b5)", "P12:p38(b22)", "P12:p50(b19)"):
            pts.setdefault(label, []).append(th); order.append(label) if label not in order else None
    rows = []; seen = {}
    for _, r in tot.iterrows():
        label = r.point; j = seen.get(label, 0); seen[label] = j + 1
        th = drop_f_metab(pts[label][j]); y = tab[tab.point == label].iloc[j * 12:(j + 1) * 12] if label.startswith("stratum") else tab[tab.point == label]
        with deadline(300, label): ll = float(gasflux_log_likelihood(th, ctx, specs))
        unscored_old = int(r.n_positive_measurements_unscored_OLD)
        if ll == -np.inf:
            verdict = "OK" if r.n_missing > 0 else "STOP:feasible row at -inf"
            accounted = f"all 12 measurements: zero likelihood ({unscored_old} were unscored under omission)"
        else:
            diff = abs(ll - float(r.logl_code)); verdict = "OK" if diff <= 1e-9 else f"STOP:changed by {diff:.2e}"
            accounted = "12 scored (unchanged)"
        rows.append(dict(point=label, logl_old=float(r.logl_code), n_missing_old=int(r.n_missing), unscored_positive_old=unscored_old,
                         logl_new=ll, diff=(abs(ll - float(r.logl_code)) if np.isfinite(ll) else float("inf")), accounted=accounted, verdict=verdict))
        print(f"[datum] {label:22s} old {r.logl_code:10.4f} new {ll!s:>12} {verdict} | {accounted}", flush=True)
    df = pd.DataFrame(rows); df.to_csv(os.path.join(HERE, "task2_datum.csv"), index=False)
    print("[datum] rows", len(df), "| -inf rows", int((df.logl_new == -np.inf).sum()), "| unchanged rows", int((df.verdict == "OK") & np.isfinite(df.logl_new)).sum(), "| STOP", int(df.verdict.str.startswith("STOP").sum()))


if __name__ == "__main__":
    main()
