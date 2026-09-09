#!/usr/bin/env python3
"""task_b_coupling_audit.py -- Y1 PART B: the coupling-ion audit (sink-audit class E) and
classes A-D, applied to Li et al.'s published yeast etcGEM.

    python3 reports/Y1_yeast_audit/task_b_coupling_audit.py --bayesiangem /path/to/BayesianGEM

FOUR STATES ARE AUDITED, because "does it fire" and "does it matter" are different questions.

  batch_pristine     `ecYeast7_v1.0_batch.mat` exactly as deposited. The plain GECKO batch model.
  aerobic_pristine   `ecYeast7_v1.0_batch_minimal_thermo.mat` exactly as deposited. This is the
                     model the paper's aerobic simulations run on (its anaerobic twin is the
                     same file with O2 uptake shut, which is how the correspondence to
                     `aerobic.pkl` / `anaerobic.pkl` is established -- see task_a_load.md).
  aerobic_etcpy_30C  the same model after THEIR OWN thermal layer has been applied at 30 C with
                     sigma = 0.5: `etc.map_fNT`, `etc.map_kcatT`, `etc.set_NGAMT`,
                     `etc.set_sigma`, run from the deposited `code/etcpy` against the deposited
                     `data/model_enzyme_params.csv`. This is PART B verification 3 -- whether
                     their code constrains the reactions our loading path sees unconstrained --
                     and it is also the only state at which "carries meaningful flux" means
                     anything, because it is the state their conclusions are drawn from.
  anaerobic_etcpy_30C  the anaerobic deposit under the same treatment, for contrast.

ONE COMPATIBILITY SHIM, and it changes no number. `etc.set_NGAMT` sets `NGAM.lower_bound` and
then `NGAM.upper_bound`; under cobra 0.15.3 that was legal, and under cobra 0.31 the
intermediate state lb > ub raises. The shim sets both at once to the same value their code
computes, via `etc.getNGAMT`, which is their function unaltered.

Writes task_b_budget.csv (one row per state, K5's columns), task_b_translocators.csv (every
ion-moving reaction, classified costed/uncosted x reversible/irreversible) and
task_b_classes_AD.csv. Nothing is written to the clone, which is read-only.
"""
from __future__ import annotations

import argparse
import logging
import os
import sys
import warnings

import numpy as np
import pandas as pd

logging.getLogger("cobra").setLevel(logging.ERROR)
warnings.filterwarnings("ignore")

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), "src"))

from etcgem.sink_audit import audit_coupling_ion, audit_sinks       # noqa: E402
from yeast_model import YeastPM, load                               # noqa: E402

AEROBIC = "ecYeast7_v1.0_batch_minimal_thermo.mat"
ANAEROBIC = "ecYeast7_v1.0_batch_minimal_thermo_anaerobic.mat"
BATCH = "ecYeast7_v1.0_batch.mat"


def load_etcpy(bg):
    """Their thermal layer, from the deposit, with the one bounds-order shim."""
    sys.path.insert(0, os.path.join(bg, "code"))
    from etcpy import etc

    def set_NGAMT(model, T):
        v = etc.getNGAMT(T)                      # their function, unaltered
        model.reactions.NGAM.bounds = (v, v)
    etc.set_NGAMT = set_NGAMT
    return etc


def apply_etcpy(model, etc, params, T_C, sigma):
    """Their thermal layer at one temperature, exactly as `etc.simulate_growth` applies it."""
    T = T_C + 273.15
    etc.map_fNT(model, T, params)
    etc.map_kcatT(model, T, params)
    etc.set_NGAMT(model, T)
    etc.set_sigma(model, sigma)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bayesiangem", required=True)
    ap.add_argument("--T", type=float, default=30.0, help="temperature for the etcpy states")
    ap.add_argument("--sigma", type=float, default=0.5, help="their enzyme saturation factor")
    args = ap.parse_args()
    bg = os.path.abspath(args.bayesiangem)
    etc = load_etcpy(bg)
    params = etc.calculate_thermal_params(
        pd.read_csv(os.path.join(bg, "data", "model_enzyme_params.csv"), index_col=0))

    states = [("batch_pristine", BATCH, False),
              ("aerobic_pristine", AEROBIC, False),
              ("aerobic_etcpy_30C", AEROBIC, True),
              ("anaerobic_etcpy_30C", ANAEROBIC, True)]

    budget_rows, rxn_rows, ad_rows = [], [], []
    for state, fn, treat in states:
        m, _ = load(os.path.join(bg, "models", fn))
        if treat:
            apply_etcpy(m, etc, params, args.T, args.sigma)
        pm = YeastPM(m)
        sol = m.optimize()

        ad = audit_sinks(pm)
        ad_rows.append(dict(state=state, model=fn, status=sol.status,
                            growth=float(sol.objective_value),
                            reactions=ad["n_reactions"], costed=ad["n_costed"],
                            uncosted=ad["n_uncosted"], A=ad["class_A_count"],
                            B=ad["class_B_count"], C=ad["class_C_count"],
                            D=ad["class_D_count"]))

        rep = audit_coupling_ion(pm, solution=sol)
        if rep.get("ion") is None:
            budget_rows.append(dict(state=state, model=fn, note=rep.get("note")))
            print(f"[y1b] {state}: {rep.get('note')}", flush=True)
            continue
        for r in rep.pop("reactions"):
            r.update(state=state, model=fn)
            rxn_rows.append(r)
        rep.update(state=state, model=fn, status=sol.status,
                   T_C=(args.T if treat else None), sigma=(args.sigma if treat else None))
        budget_rows.append(rep)
        print(f"[y1b] {state:22s} [{sol.status}] ion={rep['ion']:3s} "
              f"({rep['inner_compartment']}->{rep['outer_compartment']})  "
              f"mu={rep['growth']:.6f}  draw {rep['atp_synthase_draw']:8.3f} | "
              f"chain: translocated {rep['redox_translocated']:8.3f} + in-compartment "
              f"{rep['redox_in_compartment']:8.3f} | carriers {rep['carrier_translocated']:8.3f}"
              f"  ->  chain supplies {100*rep['chain_supplies_fraction']:7.2f} % translocated, "
              f"{100*rep['chain_supplies_fraction_incl_chemistry']:7.2f} % incl. chemistry  "
              f"[{rep['n_ion_reactions']} ion reactions, {rep['n_uncosted']} uncosted, "
              f"{rep['n_uncosted_reversible']} of those reversible]", flush=True)

    pd.DataFrame(budget_rows).to_csv(os.path.join(HERE, "task_b_budget.csv"), index=False)
    pd.DataFrame(rxn_rows).to_csv(os.path.join(HERE, "task_b_translocators.csv"), index=False)
    pd.DataFrame(ad_rows).to_csv(os.path.join(HERE, "task_b_classes_AD.csv"), index=False)
    print(f"[y1b] wrote task_b_budget.csv ({len(budget_rows)}), "
          f"task_b_translocators.csv ({len(rxn_rows)}), task_b_classes_AD.csv ({len(ad_rows)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
