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
    df = pd.DataFrame(rows)
    # D0's input set (v) is a DIFFERENT MODEL (E LB) with a known LP face (P6 D3a, P10 D1). Report the two
    # spaces separately as well as together (T3 addendum 1): a single number would hide which mechanism is which.
    inp = json.load(open(os.path.join(HERE, "inputs.json")))
    space = {x["label"]: x["space"] for x in inp["inputs"]}
    df["space"] = df.input.map(space)
    df.to_csv(os.path.join(HERE, "task1_table.csv"), index=False)
    def block(d):
        return dict(max_dev=float(d.max_dev.max()), mean_s_per_eval=float(d.s_per_eval.mean()), n_inputs=len(d),
                    n_inputs_gt_1e9=int((d.max_dev > 1e-9).sum()), n_inputs_gt_1e6=int((d.max_dev > 1e-6).sum()),
                    n_inputs_gt_1e3=int((d.max_dev > 1e-3).sum()), n_inputs_gt_1=int((d.max_dev > 1.0).sum()),
                    n_evals_gt_1e9=int(d.n_gt_1e9.sum()), n_evals=int(d.n.sum()), n_unresolved=int(d.n_unresolved_or_timeout.sum()))
    summ = {}
    for s in ("A", "B", "C", "D"):
        d = df[df.scheme == s]
        if not len(d): summ[s] = dict(verdict=verdicts[s]); continue
        summ[s] = dict(verdict=verdicts[s], **block(d),
                       D_NLDM=block(d[d.space == "D_NLDM_validation"]),
                       E_LB=block(d[d.space != "D_NLDM_validation"]),
                       verdict_D_NLDM_only=("DETERMINISTIC" if d[d.space == "D_NLDM_validation"].max_dev.max() <= 1e-9 else "MARGINAL" if d[d.space == "D_NLDM_validation"].max_dev.max() <= 1e-6 else "FAILS"))
    det = [s for s in ("A", "B", "C", "D") if verdicts[s] == "DETERMINISTIC"]
    summ["recommendation"] = (min(det, key=lambda s: summ[s]["mean_s_per_eval"]) if det else "NONE: no scheme is deterministic by the registered rule")
    det_d = [s for s in ("A", "B", "C", "D") if summ.get(s, {}).get("verdict_D_NLDM_only") == "DETERMINISTIC"]
    summ["recommendation_D_NLDM_only"] = (min(det_d, key=lambda s: summ[s]["D_NLDM"]["mean_s_per_eval"]) if det_d else "NONE on the D NLDM inputs either")
    json.dump(summ, open(os.path.join(HERE, "task1_verdicts.json"), "w"), indent=1)
    pd.set_option("display.width", 250)
    print(df[["scheme", "space", "input", "n", "max_dev", "spread", "n_gt_1e9", "n_gt_1e6", "n_gt_1e3", "n_gt_1", "n_unresolved_or_timeout", "s_per_eval"]].to_string(index=False))
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
