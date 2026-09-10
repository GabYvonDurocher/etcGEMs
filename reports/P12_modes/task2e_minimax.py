#!/usr/bin/env python3
"""P12 TASK 2e -- the BOTTLENECK (minimax) barrier between every pair. Pure arithmetic on
task2d_barriers.csv; no new likelihood evaluations.

Why this and not the straight chord: two points are in one basin if SOME path between them stays
above the level, not if the straight line does (D3). The bottleneck barrier -- the minimum over
paths of the maximum barrier on the path -- is the right statistic, and the threshold components
D7 asks for are exactly its sub-level sets. Computed from the maximum spanning tree of the
negated chord barriers.

Because a straight chord is only a SUFFICIENT witness of connection, curved paths can merge
further but never split: the component count is an UPPER BOUND on the number of basins.
"""
import json, os, sys
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
b = pd.read_csv(os.path.join(HERE, "task2d_barriers.csv"))
s = pd.read_csv(os.path.join(HERE, "task2d_endpoint_scores.csv"))
keys = sorted(set(b.a) | set(b.b))
idx = {k: i for i, k in enumerate(keys)}
n = len(keys)
D = np.full((n, n), np.inf); np.fill_diagonal(D, 0.0)
for _, r in b.iterrows():
    D[idx[r.a], idx[r.b]] = D[idx[r.b], idx[r.a]] = r.depth_below_lower_end
# minimax closure (Floyd-Warshall with max-min)
M = D.copy()
for k in range(n):
    M = np.minimum(M, np.maximum(M[:, [k]], M[[k], :]))
mm = pd.DataFrame(M, index=keys, columns=keys)
mm.round(3).to_csv(os.path.join(HERE, "task2e_minimax.csv"))
pd.set_option("display.width", 260)
print("=== bottleneck (minimax) barrier between endpoints ===")
print(mm.round(2).to_string())
capped = dict(zip(s.key, s.capped)); logl = dict(zip(s.key, s.logl))
print("\n=== pairs by bottleneck barrier, D7 classification ===")
rows = []
for i in range(n):
    for j in range(i + 1, n):
        v = M[i, j]
        cls = ("SEPARATE BASINS" if v > 5 else "sub-structure of one basin" if v > 1 else "noise")
        both_opt = (not capped[keys[i]]) and (not capped[keys[j]])
        rows.append(dict(a=keys[i], b=keys[j], bottleneck=v, both_local_optima=both_opt,
                         classification=cls if both_opt or v <= 5 else "SEPARATE (but one is CAPPED -> not a basin)"))
r = pd.DataFrame(rows).sort_values("bottleneck", ascending=False)
print(r.round(3).to_string(index=False))
for th in (3.0, 5.0, 8.0):
    lab = {}
    par = list(range(n))
    def f(x):
        while par[x] != x:
            par[x] = par[par[x]]; x = par[x]
        return x
    for i in range(n):
        for j in range(n):
            if M[i, j] <= th:
                a, c = f(i), f(j)
                if a != c: par[a] = c
    comp = {}
    for i in range(n): comp.setdefault(f(i), []).append(keys[i])
    print(f"\nthreshold {th:.0f}: {len(comp)} components -> at most {len(comp)} basins")
    for m, g in enumerate(comp.values(), 1):
        best = max(g, key=lambda k: logl[k])
        print(f"   {m}: best {best} logL {logl[best]:+.3f}  members {sorted(g)}")
json.dump(dict(keys=keys, minimax=M.tolist()), open(os.path.join(HERE, "task2e_minimax.json"), "w"), indent=1)
print("\n[t2e] done")
