#!/usr/bin/env python3
"""T1 TASK 2 -- independent audit of the two classification batches BY HASH and by recomputation
(RIGOUR rule 7), then the merge. Nothing here solves an LP. Every count below is recomputed from the
per-temperature rung columns, never copied from the classify script's own n_* tallies; the two are
then compared and any disagreement is printed, not silenced. Labels registered (D1/D5) but reached by
neither batch are listed as UNEVALUATED with their count -- never as zero.
"""
import os, sys, json, hashlib
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))

def sha(p):
    h = hashlib.sha256(); h.update(open(p, "rb").read()); return h.hexdigest()

def classify_row(r):
    """recompute the per-temperature classes from rung1/rung2/rung3 exactly as task2_classify.py:102-103 states."""
    if r.status != "OK": return None
    r1, r2, r3 = (str(r.rung1).split(";"), str(r.rung2).split(";"), str(r.rung3).split(";"))
    out = []
    for i, s1 in enumerate(r1):
        if s1 == "optimal": continue
        trio = (s1, r2[i], r3[i])
        out.append("STRUCTURAL_ZERO" if all(s == "infeasible" for s in trio) else ("RESOLVED_ON_RETRY" if "optimal" in trio else "UNRESOLVED"))
    return out

def main():
    # --- the registered label set (D1 + D5): 800 red2_6800 + 58 D44 + 6 stratum + 12 P12 = 876 ---
    p12 = pd.read_csv(os.path.join(HERE, "..", "P12_modes", "task2c_converged.csv")).key.tolist()   # the registered P12 set, read from its source
    b1p, b2p = os.path.join(HERE, "task2_classify.csv"), os.path.join(HERE, "task2_classify_batch2.csv")
    print(f"[audit] batch1 sha256 {sha(b1p)}"); print(f"[audit] batch2 sha256 {sha(b2p)}")
    b1 = pd.read_csv(b1p); b2 = pd.read_csv(b2p)
    print(f"[audit] batch1 rows {len(b1)} status {b1.status.value_counts().to_dict()}")
    print(f"[audit] batch2 rows {len(b2)} status {b2.status.value_counts().to_dict()}")
    dup = set(b1.label) & set(b2.label)
    print(f"[audit] labels in BOTH batches: {len(dup)} {sorted(dup)[:5]}")
    allrows = pd.concat([b1, b2], ignore_index=True)
    assert allrows.label.is_unique or len(dup) == 0, "duplicate labels across batches -- STOP"
    by_set = allrows.label.str.split(":").str[0].value_counts().to_dict(); print(f"[audit] coverage by set: {by_set}")
    # registered labels the batches never reached:
    red2_missing = sorted(set(range(800)) - {int(l.split(":")[1]) for l in allrows.label if l.startswith("red2_6800:")})
    p12_missing = [k for k in p12 if f"P12:{k}" not in set(allrows.label)]
    print(f"[audit] UNEVALUATED: red2_6800 {len(red2_missing)} {red2_missing[:10]}{'...' if len(red2_missing) > 10 else ''}; P12 {len(p12_missing)} {p12_missing}")
    n_reg = 876; n_eval = int((allrows.status == "OK").sum()); n_timeout = int((allrows.status != "OK").sum())
    # --- recomputed counts (independent of the n_* columns) ---
    rec = {"STRUCTURAL_ZERO": 0, "UNRESOLVED": 0, "RESOLVED_ON_RETRY": 0}; disagree = 0; any_nonopt = 0
    per_set = {}
    for _, r in allrows.iterrows():
        c = classify_row(r)
        if c is None: continue
        s = r.label.split(":")[0]; ps = per_set.setdefault(s, {"points": 0, "STRUCTURAL_ZERO": 0, "UNRESOLVED": 0, "RESOLVED_ON_RETRY": 0, "temps": 0})
        ps["points"] += 1; ps["temps"] += len(str(r.rung1).split(";"))
        for k in rec: rec[k] += c.count(k); ps[k] += c.count(k)
        any_nonopt += int(len(c) > 0)
        if (c.count("STRUCTURAL_ZERO"), c.count("UNRESOLVED"), c.count("RESOLVED_ON_RETRY")) != (int(r.n_structural_zero), int(r.n_unresolved), int(r.n_resolved_on_retry)):
            disagree += 1; print(f"[audit] DISAGREEMENT at {r.label}: recomputed {c} vs script {r.n_structural_zero},{r.n_unresolved},{r.n_resolved_on_retry}")
    print(f"[audit] recomputed: {rec} over {n_eval} evaluated points ({any_nonopt} with any non-optimal T); script-vs-recomputed disagreements: {disagree}")
    print(f"[audit] per set: {json.dumps(per_set)}")
    ok = allrows[allrows.status == "OK"]
    agree = int((ok.agrees_with_saved == True).sum()); cmp_ = int(ok.agrees_with_saved.notna().sum())
    print(f"[audit] saved-status agreement (where a saved status exists): {agree} of {cmp_}")
    # the stratum (P17's -18.68 stratum, 6 states): what fraction of its missing predictions is STRUCTURAL_ZERO
    st = per_set.get("stratum", {}); st_missing = st.get("STRUCTURAL_ZERO", 0) + st.get("UNRESOLVED", 0) + st.get("RESOLVED_ON_RETRY", 0)
    print(f"[audit] stratum: {st.get('points', 0)} states, {st_missing} missing predictions, STRUCTURAL_ZERO {st.get('STRUCTURAL_ZERO', 0)}, UNRESOLVED {st.get('UNRESOLVED', 0)}")
    # timeouts, listed
    to = allrows[allrows.status != "OK"]
    if len(to): print(f"[audit] UNRESOLVED_TIMEOUT rows: {to.label.tolist()}")
    # --- merge ---
    outp = os.path.join(HERE, "task2_classify_all.csv"); allrows.to_csv(outp, index=False)
    summ = dict(n_registered=n_reg, n_evaluated_OK=n_eval, n_timeout=n_timeout,
                n_unevaluated=len(red2_missing) + len(p12_missing), unevaluated_red2_indices=red2_missing, unevaluated_P12=p12_missing,
                temps_structural_zero=rec["STRUCTURAL_ZERO"], temps_unresolved=rec["UNRESOLVED"], temps_resolved_on_retry=rec["RESOLVED_ON_RETRY"],
                points_with_any_nonoptimal=any_nonopt, per_set=per_set, saved_status_agreement=agree, saved_status_compared=cmp_,
                script_vs_recomputed_disagreements=disagree, sha_batch1=sha(b1p), sha_batch2=sha(b2p), sha_merged=sha(outp),
                batch1_wall_min=json.load(open(os.path.join(HERE, "task2_classify.json"))).get("wall_min"),
                batch2_wall_min=(json.load(open(os.path.join(HERE, "task2_classify_batch2.json"))).get("wall_min") if os.path.exists(os.path.join(HERE, "task2_classify_batch2.json")) else None))
    json.dump(summ, open(os.path.join(HERE, "task2_classify_all.json"), "w"), indent=1)
    print(f"[audit] merged -> task2_classify_all.csv sha256 {summ['sha_merged']}; summary -> task2_classify_all.json")

if __name__ == "__main__":
    main()
