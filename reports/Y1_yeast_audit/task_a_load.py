#!/usr/bin/env python3
"""task_a_load.py -- Y1 PART A: can the published yeast etcGEM be loaded and solved?

Loads each of the three models deposited with Li et al. (2021), verifies the load shim is
inert against the raw MATLAB struct, solves each, and records which of them the paper's own
aerobic/anaerobic simulations use.

    python3 reports/Y1_yeast_audit/task_a_load.py --bayesiangem /path/to/BayesianGEM

Writes task_a_load.json beside this file. Nothing is written to the clone, which is read-only.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from yeast_model import DEPOSITED, YeastPM, load, verify_fidelity   # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bayesiangem", required=True, help="path to a clone of "
                    "SysBioChalmers/BayesianGEM (read-only)")
    args = ap.parse_args()

    out = {"source": {}, "models": {}}
    root = os.path.abspath(args.bayesiangem)
    out["source"]["clone"] = root

    for fn in DEPOSITED:
        path = os.path.join(root, "models", fn)
        rec = {"file": fn, "bytes": os.path.getsize(path)}
        m, st = load(path)
        rec["fidelity"] = verify_fidelity(m, st)
        rec["n_reactions"] = len(m.reactions)
        rec["n_metabolites"] = len(m.metabolites)
        rec["n_genes"] = len(m.genes)
        rec["compartments"] = m.compartments
        pm = YeastPM(m)
        rec["biomass"] = pm.biomass_rxn
        rec["n_costed"] = len(pm.costed_ids)
        rec["n_prot_metabolites"] = sum(1 for x in m.metabolites if x.id.startswith("prot_"))
        sol = m.optimize()
        rec["status"] = sol.status
        rec["growth"] = float(sol.objective_value)
        # the levers the paper's own code uses, if they are present
        for rid in ("prot_pool_exchange", "r_1714_REV", "r_1992_REV", "r_1714", "r_1992"):
            if rid in {r.id for r in m.reactions}:
                r = m.reactions.get_by_id(rid)
                rec.setdefault("levers", {})[rid] = dict(
                    lb=float(r.lower_bound), ub=float(r.upper_bound),
                    flux=float(sol.fluxes.get(rid, float("nan"))))
        out["models"][fn] = rec
        print(f"[y1a] {fn:52s} {rec['n_reactions']:5d} rxns  {rec['n_costed']:5d} costed  "
              f"[{rec['status']}] mu={rec['growth']:.6f}", flush=True)

    with open(os.path.join(HERE, "task_a_load.json"), "w") as fh:
        json.dump(out, fh, indent=2, default=str)
    print("[y1a] wrote task_a_load.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
