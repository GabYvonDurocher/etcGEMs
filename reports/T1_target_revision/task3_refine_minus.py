#!/usr/bin/env python3
"""T1 TASK 3 -- the minus-side refinement series registered in DECISIONS D9 (task3_trace.py stepped
only +h). Same instrument: h, h/2, h/4, h/8 with h = 0.04 SD, fresh evaluation each, alarm per solve,
appended to task3_trace.json as `refinements_minus`. Nothing else in the JSON is touched."""
import os, sys, json, time, numpy as np
sys.argv = [sys.argv[0]]
import task3_trace as t
rec = json.load(open(t.OUT)); t0 = time.time()
plan = json.load(open("reports/P17_inactive_prior/real_curvature_probe/plan.json"))
scale = np.asarray(plan["scale"], float); u0 = np.asarray(plan["parent"], float); pt15 = t.transform_factory(t.FREE_SPECS)
base = [r for r in rec["evaluations"] if r.get("label") == "baseline_start"][0]
rec["refinements_minus"] = []
for ax in t.AXES:
    j = t.FREE.index(ax); ser = []
    for h in (0.04, 0.02, 0.01, 0.005):
        u = u0.copy(); u[j] = u0[j] - h * scale[j]
        try:
            with t.deadline(t.SOLVE_S, f"refine- {ax} {h}"): r = t.evaluate(t.expand(pt15(u)))
            ser.append(dict(h=h, logl=r["logl"], delta=r["logl"] - base["logl"], clipped_low=[x["clipped_low"] for x in r["enzyme_state"]], status=r["status"], growth_term=r["growth_term"], resp_term=r["resp_term"]))
        except t.Deadline as ex:
            ser.append(dict(h=h, status="UNRESOLVED_TIMEOUT", note=str(ex)))
    rec["refinements_minus"].append(dict(axis=ax, side="minus", series=ser)); json.dump(rec, open(t.OUT, "w"))
    print(f"[t3-] refine {ax} (minus): " + " -> ".join(f"{s.get('delta', float('nan')):+.4f}" for s in ser), flush=True)
print(f"[t3-] done in {(time.time() - t0) / 60:.1f} min", flush=True)
