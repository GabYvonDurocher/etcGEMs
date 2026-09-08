#!/usr/bin/env python3
"""task1_coupling_audit.py -- K5 TASK 1: run the new coupling-ion audit (sink-audit class E)
on all seven strains.

WHY THIS CLASS EXISTS. Classes A-D of `etcgem audit-sinks` watch chemical free-energy carriers
-- ATP, NAD(P)H, quinol, ferredoxin -- and terminal electron acceptors. None of them watches
the ION that ATP synthase actually runs on. So a model can close its proton circuit through
free metabolite/H+ symporters and every one of those reactions passes the audit clean. K4 found
exactly that in three Candida models, which report 44-47 class-A hits while the chain supplied
0.02-0.03 % of the protons ATP synthase consumed.

The ion is INFERRED from each strain's own ATP synthase, not assumed to be the proton:
M. maripaludis' ATP synthase in this project is sodium-driven (4 Na+ per ATP).

READ-ONLY WHERE P4 IS ACTIVE. Every strain is built in-process and nothing is written under
`strains/`; all output goes to this directory. eciML1515 is audited and never modified.

Run from the project root:

    python3 reports/K5_respire/task1_coupling_audit.py

Writes task1_budget.csv (one row per strain) and task1_translocators.csv (every
ion-translocating reaction, classified) beside this file.
"""
from __future__ import annotations

import logging
import os
import sys

import pandas as pd

logging.getLogger("cobra").setLevel(logging.ERROR)
sys.path.insert(0, "src")

from etcgem.config import build_provider, resolve          # noqa: E402
from etcgem.enzyme_cost import Perturbation                # noqa: E402
from etcgem.sink_audit import audit_coupling_ion           # noqa: E402
from etcgem.tpc import apply_state                         # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))

# strain, experiment, temperature, kcat_scale. The Candida strains are audited under the K2
# configuration K4 used, so the numbers are directly comparable with K4's.
#
# M. maripaludis is audited at its CALIBRATED operating point (kcat_scale 7.223, its
# strain.yaml's `nominal_kcat_scale`). At the a-priori point its LP is infeasible -- the
# maintenance-crushed state K2 documented, where its predicted TPC is identically zero -- so an
# audit there reads fluxes from a failed solve. The status is recorded either way.
STRAINS = [
    ("cauris_iRV973", "candida_B3_ngamT", 40.0, 1.0),
    ("chaemulonii_draft", "candida_B3_ngamT", 40.0, 1.0),
    ("cduobushaemulonii_draft", "candida_B3_ngamT", 40.0, 1.0),
    ("cparapsilosis_iDC1003", "candida_B3_ngamT", 40.0, 1.0),
    ("eciML1515", None, 37.0, 1.0),
    ("mmaripaludis", None, 37.0, 7.223),
    ("syn6803", "syn6803_ecmodel", 30.0, 1.0),
]


def main():
    budget_rows, rxn_rows = [], []
    for strain, exp, T, kscale in STRAINS:
        try:
            pm = build_provider(resolve(strain, exp))
        except Exception as e:                                  # noqa: BLE001
            print(f"[k5] {strain}: BUILD FAILED ({type(e).__name__}: {e})")
            budget_rows.append(dict(strain=strain, experiment=exp, error=str(e)))
            continue
        try:
            apply_state(pm.ec, float(T), Perturbation(kcat_scale=float(kscale)))
        except Exception:                                        # noqa: BLE001
            pass
        sol = pm.ec.model.optimize()
        rep = audit_coupling_ion(pm, solution=sol)
        if rep.get("ion") is None:
            print(f"[k5] {strain}: {rep.get('note')}")
            budget_rows.append(dict(strain=strain, experiment=exp, T_C=T,
                                    kcat_scale=kscale, note=rep.get("note")))
            continue
        for r in rep.pop("reactions"):
            r.update(strain=strain, T_C=T, kcat_scale=kscale)
            rxn_rows.append(r)
        rep.update(strain=strain, experiment=exp, T_C=T, kcat_scale=kscale,
                   status=sol.status)
        budget_rows.append(rep)
        print(f"[k5] {strain:24s} T={T:.0f}C [{sol.status}] ion={rep['ion']:3s} "
              f"({rep['inner_compartment']}->{rep['outer_compartment']})  "
              f"mu={rep['growth']:.6f}  draw {rep['atp_synthase_draw']:8.3f} | "
              f"chain: translocated {rep['redox_translocated']:8.3f} + in-compartment "
              f"{rep['redox_in_compartment']:8.3f} | carriers {rep['carrier_translocated']:8.3f}"
              f"  ->  chain supplies {100*rep['chain_supplies_fraction']:7.2f} % translocated, "
              f"{100*rep['chain_supplies_fraction_incl_chemistry']:7.2f} % incl. chemistry  "
              f"[{rep['n_ion_reactions']} ion reactions, {rep['n_uncosted']} uncosted, "
              f"{rep['n_uncosted_reversible']} of those reversible]", flush=True)

    b = pd.DataFrame(budget_rows)
    b.to_csv(os.path.join(HERE, "task1_budget.csv"), index=False)
    pd.DataFrame(rxn_rows).to_csv(os.path.join(HERE, "task1_translocators.csv"), index=False)
    print(f"\n[k5] wrote task1_budget.csv ({len(b)}) and "
          f"task1_translocators.csv ({len(rxn_rows)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
