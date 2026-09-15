#!/usr/bin/env python3
"""T3 TASK 1 -- the scheme x input table and the verdict by D0's rule, from battery_*.json against battery_ref.json."""
import os, json, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
THR = [1e-9, 1e-6, 1e-3, 1.0]


def dev(v, ref):
    if v == ref: return 0.0
    if not np.isfinite(v) or not np.isfinite(ref): return float("inf")
    return abs(v - ref)


def main():
    ref = json.load(open(os.path.join(HERE, "battery_ref.json")))
    R = {}
    for r in ref["results"]: R.setdefault(r["label"], []).append(r["value"])
    fresh_spread = {l: (0.0 if v[0] == v[1] else abs(v[0] - v[1])) for l, v in R.items()}
    rows = []; verdicts = {}
    for scheme in ("A", "B", "C", "D"):
        p = os.path.join(HERE, f"battery_{scheme}.json")
        if not os.path.exists(p): verdicts[scheme] = "NOT RUN"; continue
        b = json.load(open(p)); by = {}
        for r in b["results"]: by.setdefault(r["label"], []).append(r)
        maxdev_all = 0.0
        for l, rs in by.items():
            ref_v = R[l][0]; vals = [x["value"] for x in rs]; d = [dev(v, ref_v) for v in vals]
            fin = [v for v in vals if np.isfinite(v)]; spread = (max(fin) - min(fin)) if len(fin) > 1 else 0.0
            nunres = sum(1 for x in rs if not np.isfinite(x["value"]) and np.isfinite(ref_v))
            rows.append(dict(scheme=scheme, input=l, n=len(rs), reference=ref_v, max_dev=max(d), spread=spread, n_gt_1e9=sum(x > THR[0] for x in d), n_gt_1e6=sum(x > THR[1] for x in d),
                             n_gt_1e3=sum(x > THR[2] for x in d), n_gt_1=sum(x > THR[3] for x in d), n_unresolved_or_timeout=nunres, s_per_eval=float(np.mean([x["wall"] for x in rs])),
                             fresh_vs_fresh=fresh_spread[l], first_value=vals[0], statuses_vary=len({tuple(x["statuses"] or []) for x in rs}) > 1))
            maxdev_all = max(maxdev_all, max(d))
        verdicts[scheme] = ("DETERMINISTIC" if maxdev_all <= 1e-9 else "MARGINAL" if maxdev_all <= 1e-6 else "FAILS") + (" (partial battery)" if not b.get("complete") else "")
    df = pd.DataFrame(rows); df.to_csv(os.path.join(HERE, "task1_table.csv"), index=False)
    summ = {s: dict(verdict=verdicts[s], max_dev=float(df[df.scheme == s].max_dev.max()) if s in set(df.scheme) else None,
                    mean_s_per_eval=float(df[df.scheme == s].s_per_eval.mean()) if s in set(df.scheme) else None,
                    n_inputs_gt_1e9=int((df[df.scheme == s].max_dev > 1e-9).sum()) if s in set(df.scheme) else None,
                    n_inputs_gt_1=int((df[df.scheme == s].max_dev > 1.0).sum()) if s in set(df.scheme) else None) for s in ("A", "B", "C", "D")}
    det = [s for s in ("A", "B", "C", "D") if verdicts[s] == "DETERMINISTIC"]
    summ["recommendation"] = (min(det, key=lambda s: summ[s]["mean_s_per_eval"]) if det else "NONE: no scheme is deterministic by the registered rule")
    json.dump(summ, open(os.path.join(HERE, "task1_verdicts.json"), "w"), indent=1)
    pd.set_option("display.width", 250)
    print(df[["scheme", "input", "n", "max_dev", "spread", "n_gt_1e9", "n_gt_1e6", "n_gt_1e3", "n_gt_1", "n_unresolved_or_timeout", "s_per_eval", "statuses_vary"]].to_string(index=False))
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
