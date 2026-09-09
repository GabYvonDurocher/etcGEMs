#!/usr/bin/env python3
"""task_b4_what_etcpy_constrains.py -- Y1 PART B verification 3: does THEIR code constrain the
reactions our loading path sees unconstrained?

    python3 reports/Y1_yeast_audit/task_b4_what_etcpy_constrains.py --bayesiangem /path/...

The concern the prompt raises is real and specific: a thermal layer may bound things the raw
model does not, and an audit that reads only the deposited file would then be auditing a model
nobody ever solves. This answers it by DIFFING the model against itself -- every bound and every
stoichiometric coefficient, before and after `etc.map_fNT`, `etc.map_kcatT`, `etc.set_NGAMT` and
`etc.set_sigma` are applied at 30 C with sigma = 0.5.

Writes task_b4_etcpy_diff.csv (every reaction their layer changes) and prints the summary.
"""
from __future__ import annotations

import argparse
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

from etcgem.sink_audit import _ion_of                                     # noqa: E402
from task_b_coupling_audit import AEROBIC, apply_etcpy, load_etcpy        # noqa: E402
from yeast_model import YeastPM, load                                     # noqa: E402


def snapshot(model):
    return {r.id: (float(r.lower_bound), float(r.upper_bound),
                   tuple(sorted((m_.id, float(c)) for m_, c in r.metabolites.items())))
            for r in model.reactions}


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
    pm = YeastPM(m)
    before = snapshot(m)
    apply_etcpy(m, etc, params, args.T, args.sigma)
    after = snapshot(m)

    rows = []
    for rid, (lb0, ub0, s0) in before.items():
        lb1, ub1, s1 = after[rid]
        if (lb0, ub0) == (lb1, ub1) and s0 == s1:
            continue
        moves_h = any(_ion_of(x) == "H+" for x in m.reactions.get_by_id(rid).metabolites)
        rows.append(dict(reaction=rid, name=m.reactions.get_by_id(rid).name,
                         bounds_changed=(lb0, ub0) != (lb1, ub1),
                         stoich_changed=s0 != s1, lb_before=lb0, lb_after=lb1,
                         ub_before=ub0, ub_after=ub1,
                         costed=rid in pm.costed_ids, moves_proton=moves_h))
    d = pd.DataFrame(rows)
    d.to_csv(os.path.join(HERE, "task_b4_etcpy_diff.csv"), index=False)
    nb = int(d.bounds_changed.sum()) if len(d) else 0
    ns = int(d.stoich_changed.sum()) if len(d) else 0
    print(f"[y1b4] their thermal layer changes {len(d)} of {len(before)} reactions: "
          f"{nb} bound changes, {ns} stoichiometry changes", flush=True)
    if nb:
        print("[y1b4] every bound their layer changes:")
        print(d[d.bounds_changed][["reaction", "name", "lb_before", "lb_after",
                                   "ub_before", "ub_after"]].to_string(index=False))
    uncosted_h = d[(~d.costed) & d.moves_proton] if len(d) else d
    print(f"[y1b4] of the changes, UNCOSTED proton-moving reactions touched: {len(uncosted_h)}",
          flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
