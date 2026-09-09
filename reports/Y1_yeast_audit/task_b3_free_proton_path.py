#!/usr/bin/env python3
"""task_b3_free_proton_path.py -- Y1 PART B: is there a FREE PATH for a proton back into the
energised compartment, in one step or several?

    python3 reports/Y1_yeast_audit/task_b3_free_proton_path.py --bayesiangem /path/to/BayesianGEM

WHY A PATH AND NOT A LIST. The census in task_b2 is pairwise: it looks at reactions that move a
proton directly between the mitochondrion and the cytosol, and finds that every uncosted one runs
the dissipative way. That is not sufficient. This model has a `mm` compartment (mitochondrial
membrane) and an uncosted, reversible pair `r_3957`/`r_3957_REV` moving protons between `m` and
`mm`. If any uncosted reaction also moved protons between `mm` and `c`, the two together would be
a free bypass of the respiratory chain that no pairwise census would ever see.

So the test is reachability. Build a directed graph whose nodes are compartments and whose edges
are UNCOSTED reactions that move a proton from one compartment to another -- ATP synthase and the
costed chain excluded, since the question is what is free. Then ask for a path from the
de-energised side to the energised side.

A path found would be a LATENT HAZARD, not a defect: whether the model uses it is a separate
question, answered by the flux at a solved state and by the counterfactual in task_b2.

Writes task_b3_free_proton_path.json and task_b3_free_proton_edges.csv.
"""
from __future__ import annotations

import argparse
import collections
import json
import logging
import os
import sys
import warnings

import pandas as pd

logging.getLogger("cobra").setLevel(logging.ERROR)
warnings.filterwarnings("ignore")

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), "src"))

from etcgem.sink_audit import _ion_of, find_atp_synthase                  # noqa: E402
from task_b_coupling_audit import AEROBIC, apply_etcpy, load_etcpy        # noqa: E402
from yeast_model import YeastPM, load                                     # noqa: E402


def proton_edges(model, costed, exclude):
    """Directed edges (src -> dst) for every reaction that moves a proton, with cost status."""
    rows = []
    for r in model.reactions:
        if r.id in exclude:
            continue
        bycomp = {}
        for m_, c in r.metabolites.items():
            if _ion_of(m_) == "H+":
                bycomp[m_.compartment] = bycomp.get(m_.compartment, 0.0) + float(c)
        bycomp = {k: v for k, v in bycomp.items() if abs(v) > 1e-12}
        if len(bycomp) < 2:
            continue
        srcs = [k for k, v in bycomp.items() if v < 0]     # proton consumed here
        dsts = [k for k, v in bycomp.items() if v > 0]     # proton delivered here
        for a in srcs:
            for b in dsts:
                rows.append(dict(reaction=r.id, name=r.name, src=a, dst=b,
                                 costed=r.id in costed,
                                 h=" ".join(f"{k}:{v:+g}" for k, v in sorted(bycomp.items()))))
    return pd.DataFrame(rows)


def reachable(edges, start, goal):
    """Shortest free path start -> goal, as a list of (compartment, reaction) steps, or None."""
    adj = collections.defaultdict(list)
    for e in edges.itertuples():
        adj[e.src].append((e.dst, e.reaction))
    seen, q = {start: None}, collections.deque([start])
    while q:
        u = q.popleft()
        if u == goal:
            break
        for v, rid in adj[u]:
            if v not in seen:
                seen[v] = (u, rid)
                q.append(v)
    if goal not in seen:
        return None
    path, cur = [], goal
    while seen[cur] is not None:
        u, rid = seen[cur]
        path.append(dict(**{"from": u}, to=cur, reaction=rid))
        cur = u
    return list(reversed(path))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bayesiangem", required=True)
    ap.add_argument("--T", type=float, default=30.0)
    ap.add_argument("--sigma", type=float, default=0.5)
    args = ap.parse_args()
    bg = os.path.abspath(args.bayesiangem)
    etc = load_etcpy(bg)
    params = etc.calculate_thermal_params(
        pd.read_csv(os.path.join(bg, "data", "model_enzyme_params.csv"), index_col=0))
    m, _ = load(os.path.join(bg, "models", AEROBIC))
    apply_etcpy(m, etc, params, args.T, args.sigma)
    pm = YeastPM(m)
    sol = m.optimize()
    syn, ion, (inner, outer) = find_atp_synthase(m, fluxes=sol.fluxes)
    syn_ids = {r.id for members in syn.values() for r in members}

    edges = proton_edges(m, pm.costed_ids, exclude=syn_ids)
    edges.to_csv(os.path.join(HERE, "task_b3_free_proton_edges.csv"), index=False)
    free = edges[~edges.costed]

    out = dict(ion=ion, inner=inner, outer=outer,
               atp_synthase=sorted(syn_ids),
               n_proton_edges=len(edges), n_free_edges=len(free),
               compartments_with_free_proton_edges=sorted(set(free.src) | set(free.dst)))
    for label, sub in (("free_only", free), ("all_but_atp_synthase", edges)):
        p = reachable(sub, inner, outer)
        out[f"path_{inner}_to_{outer}__{label}"] = p
        print(f"[y1b3] path {inner} -> {outer} using {label}: "
              f"{'NONE' if p is None else ' -> '.join(x['reaction'] for x in p)}", flush=True)
    # and the direction that should exist: dissipation into the mitochondrion
    p = reachable(free, outer, inner)
    out[f"path_{outer}_to_{inner}__free_only"] = p
    print(f"[y1b3] path {outer} -> {inner} using free_only: "
          f"{'NONE' if p is None else ' -> '.join(x['reaction'] for x in p)}", flush=True)
    with open(os.path.join(HERE, "task_b3_free_proton_path.json"), "w") as fh:
        json.dump(out, fh, indent=2)
    print(f"[y1b3] {len(edges)} proton-moving edges, {len(free)} of them uncosted; wrote "
          f"task_b3_free_proton_path.json and task_b3_free_proton_edges.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
