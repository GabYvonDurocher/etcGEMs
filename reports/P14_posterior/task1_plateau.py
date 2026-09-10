#!/usr/bin/env python3
"""P14 TASK 1 (b) and (c) -- plateaus, and feasibility boundaries.

Both read P13's committed clamp scan at p38 (twelve lines, 41 points each at 0.05 sd, fresh model
per evaluation), which is exactly the data these tests need.

(b) A PLATEAU in the sense that breaks nested sampling is a set of POSITIVE PRIOR VOLUME on which
    the likelihood is EXACTLY constant -- it voids the volume-shrinkage estimate (Fowlie, Handley
    & Su 2021). Counted here as runs of exactly-equal adjacent log-likelihood values. D1's rule:
    PASS if no run spans more than 10 % of a line (4 of the 40 intervals = 0.2 of the 2 sd scanned).

(c) FEASIBILITY BOUNDARIES are reported with their location and passed over; the model makes no
    claim beyond them and nested sampling discards there. Nothing is smoothed.
"""
import json, os, sys
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
FRAC = 0.10
scan = pd.read_csv(os.path.join(ROOT, "reports", "P13_support", "task3_lines.csv"))
old = pd.read_csv(os.path.join(ROOT, "reports", "P13_support", "task3_verdict.csv"))
rows, cross = [], []
for l in sorted(scan.line.unique()):
    d = scan[(scan.scheme == "clamp") & (scan.line == l)].sort_values("step_sd").reset_index(drop=True)
    y = d.logL.to_numpy(); x = d.step_sd.to_numpy()
    eq = np.diff(y) == 0.0                       # EXACTLY equal, not "close"
    runs, cur = [], 0
    for e in eq:
        cur = cur + 1 if e else 0
        runs.append(cur)
    longest = int(max(runs)) if len(runs) else 0
    nsup = 12 - d.n_infeasible.to_numpy()
    tr = np.where(np.diff(nsup) != 0)[0]
    for k in tr:
        cross.append(dict(line=l, from_sd=float(x[k]), to_sd=float(x[k + 1]),
                          n_scored_before=int(nsup[k]), n_scored_after=int(nsup[k + 1])))
    rows.append(dict(line=l, n_intervals=int(len(eq)), n_equal=int(eq.sum()),
                     longest_plateau_intervals=longest,
                     longest_plateau_sd=float(longest * 0.05),
                     frac_of_line=float(longest / len(eq)),
                     n_feasibility_crossings=int(len(tr)),
                     crossing_sd=";".join(f"{x[k]:+.2f}" for k in tr) if len(tr) else "",
                     plateau_pass=bool(longest / len(eq) <= FRAC)))
P = pd.DataFrame(rows); P.to_csv(os.path.join(HERE, "task1_plateau.csv"), index=False)
C = pd.DataFrame(cross); C.to_csv(os.path.join(HERE, "task1_feasibility.csv"), index=False)
pd.set_option("display.width", 240)
print("=== (b) PLATEAUS: runs of EXACTLY equal adjacent log-likelihood ===")
print(P[["line", "n_intervals", "n_equal", "longest_plateau_intervals", "longest_plateau_sd",
         "frac_of_line", "plateau_pass"]].round(4).to_string(index=False))
tot_eq = int(P.n_equal.sum()); tot_iv = int(P.n_intervals.sum())
print(f"\nfraction of ALL evaluations lying on any plateau: {tot_eq}/{tot_iv} = {100*tot_eq/tot_iv:.2f} %")
print(f"longest plateau anywhere: {int(P.longest_plateau_intervals.max())} intervals "
      f"= {P.longest_plateau_sd.max():.2f} sd = {100*P.frac_of_line.max():.1f} % of a line "
      f"-> {'PASS' if P.plateau_pass.all() else '*** FAIL ***'} (rule: <= 10 %)")
print("\n=== (c) FEASIBILITY CROSSINGS (reported, NOT smoothed) ===")
print(C.round(3).to_string(index=False) if len(C) else "none within +/-1 sd of p38")
if len(C):
    print(f"\nall {len(C)} crossings lie at |step_sd| in [{C[['from_sd','to_sd']].abs().min().min():.2f}, "
          f"{C[['from_sd','to_sd']].abs().max().max():.2f}] sd of p38")
json.dump(dict(rule_frac=FRAC, longest_plateau_intervals=int(P.longest_plateau_intervals.max()),
               frac_all_on_plateau=tot_eq / tot_iv, plateau_pass=bool(P.plateau_pass.all()),
               n_crossings=int(len(C))),
          open(os.path.join(HERE, "task1_plateau.json"), "w"), indent=1)
print("\n[t1bc] done")
