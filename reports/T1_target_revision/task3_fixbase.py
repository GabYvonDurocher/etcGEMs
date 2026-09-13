#!/usr/bin/env python3
"""T1 TASK 3 -- correction of one script defect, recorded in DECISIONS D9: task3_trace.py evaluated the
BASE of p38 and P4_MAP at their stored 16-D theta (dTm = -4.02 and -5.12) while every stencil is
at dTm = 0, as D1 registered for all five points. This re-evaluates those two bases at dTm = 0
(two fresh evaluations under the same alarm) and stores them as `base`; the as-stored evaluations
are RETAINED under `base_as_stored_16D` (RIGOUR 3). Nothing else in the JSON is touched."""
import os, sys, json, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.argv = [sys.argv[0]]
import task3_trace as t
from reduced import FIXED_IDX, expand
rec = json.load(open(t.OUT))
for d in rec["diverse"]:
    if d["point"] not in ("p38", "P4_MAP") or "base" not in d: continue
    dp, _, _ = t.diverse_points(); th = [x for x in dp if x[0] == d["point"]][0][1]
    assert t.sha(th) == d["sha_theta"], "theta mismatch"
    th0 = expand(np.delete(np.asarray(th, float), FIXED_IDX))
    with t.deadline(t.SOLVE_S, f"fixbase {d['point']}"): b0 = t.evaluate(th0)
    d["base_as_stored_16D"] = dict(d["base"], note=f"evaluated at stored dTm={float(th[FIXED_IDX]):.4f}; NOT the registered point")
    d["base"] = dict(b0, note="re-evaluated at dTm=0 (D1's registration) by task3_fixbase.py"); d["sha_theta_dTm0"] = t.sha(th0)
    print(f"[fix] {d['point']}: stored dTm {float(th[FIXED_IDX]):+.4f} logL {d['base_as_stored_16D']['logl']:.4f} -> dTm=0 logL {b0['logl']:.4f} status[15C] {b0['status'][0]}", flush=True)
json.dump(rec, open(t.OUT, "w")); print("[fix] written", flush=True)
