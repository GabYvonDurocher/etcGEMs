#!/usr/bin/env python3
"""P13 TASK 3 -- the SAMPLEABLE verdict under D6's refined rule.

A step above 5 log-likelihood units disqualifies a scheme ONLY between two FEASIBLE points. A step
across a feasible/infeasible transition is the boundary of the model's feasible set: the model
makes no claim past it, the likelihood is undefined there, and nested sampling handles such a wall
natively. So the verdict is decided on the largest step between adjacent points whose SUPPORT SET
IS UNCHANGED, and every feasibility transition is reported separately with its location in sd.
"""
import json, os, sys
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
RULE, COLD = 5.0, 25.0
df = pd.read_csv(os.path.join(HERE, "task3_lines.csv"))
p11 = pd.read_csv(os.path.join(HERE, "..", "P11_nested", "lines_p11floor_summary.csv"))
p11m = dict(zip(p11.line, p11.max_jump))
rows, trans = [], []
for s in sorted(df.scheme.unique()):
    for l in sorted(df.line.unique()):
        d = df[(df.scheme == s) & (df.line == l)].sort_values("step_sd").reset_index(drop=True)
        y = d.logL.to_numpy(); x = d.step_sd.to_numpy()
        # the support set size the scheme actually scores
        nsup = (12 - d.n_infeasible.to_numpy()) if s == "clamp" else \
               (12 - np.maximum(d.n_infeasible.to_numpy(), d.n_below_mask.to_numpy()))
        step = np.abs(np.diff(y))
        same = np.diff(nsup) == 0                      # adjacent pair with an unchanged support set
        feas_step = step.copy(); feas_step[~same] = np.nan
        i = int(np.nanargmax(feas_step)) if np.any(same) else -1
        for k in np.where(~same)[0]:
            trans.append(dict(scheme=s, line=l, at_step_sd=float(x[k]), to_step_sd=float(x[k + 1]),
                              n_scored_before=int(nsup[k]), n_scored_after=int(nsup[k + 1]),
                              step=float(step[k]), T_min_growth=float(d.T_min_growth.iloc[k])))
        rows.append(dict(scheme=s, line=l,
                         max_step_feasible=float(np.nanmax(feas_step)) if np.any(same) else float("nan"),
                         at_step_sd=float(x[i]) if i >= 0 else float("nan"),
                         max_step_any=float(step.max()),
                         n_transitions=int((~same).sum()),
                         T_at_max=float(d.T_min_growth.iloc[i]) if i >= 0 else float("nan"),
                         rng=float(y.max() - y.min()),
                         p11_at_thetaA=float(p11m.get(l, np.nan)),
                         sampleable=bool(np.nanmax(feas_step) <= RULE) if np.any(same) else False))
S = pd.DataFrame(rows); S.to_csv(os.path.join(HERE, "task3_verdict.csv"), index=False)
T = pd.DataFrame(trans); T.to_csv(os.path.join(HERE, "task3_transitions.csv"), index=False)
pd.set_option("display.width", 240)
out = {}
for s in sorted(df.scheme.unique()):
    d = S[S.scheme == s]
    print(f"\n=== {s.upper()} at p38 — step BETWEEN FEASIBLE POINTS decides ===")
    print(d[["line", "max_step_feasible", "at_step_sd", "max_step_any", "n_transitions",
             "T_at_max", "rng", "p11_at_thetaA", "sampleable"]].round(4).to_string(index=False))
    bad = d[~d.sampleable]
    ok = bool(len(bad) == 0)
    print(f"{s}: largest FEASIBLE-to-FEASIBLE step {d.max_step_feasible.max():.4f} (rule {RULE})"
          f"  ->  {'SAMPLEABLE' if ok else '*** NOT SAMPLEABLE: ' + ','.join(bad.line) + ' ***'}")
    cold = d[d.T_at_max <= COLD]
    print(f"{s}: lines whose largest feasible step is carried at <= {COLD:.0f} C: {len(cold)} of {len(d)}"
          + (f", largest {cold.max_step_feasible.max():.4f}" if len(cold) else ""))
    tt = T[T.scheme == s]
    print(f"{s}: feasibility transitions: {len(tt)}"
          + (f"; |step_sd| range {tt.at_step_sd.abs().min():.2f}-{tt.at_step_sd.abs().max():.2f} sd, "
             f"largest step {tt.step.max():.3f}" if len(tt) else " (none within +/-1 sd of p38)"))
    out[s] = dict(max_feasible_step=float(d.max_step_feasible.max()), sampleable=ok,
                  n_transitions=int(len(tt)),
                  transition_sd_min=float(tt.at_step_sd.abs().min()) if len(tt) else None)
if len(T):
    print("\n=== every feasibility transition (NOT smoothed; reported and passed over) ===")
    print(T.round(4).to_string(index=False))
json.dump(dict(rule=RULE, refined="step between FEASIBLE points only (D6)", schemes=out),
          open(os.path.join(HERE, "task3_verdict.json"), "w"), indent=1)
print("\n[t3v] done")
