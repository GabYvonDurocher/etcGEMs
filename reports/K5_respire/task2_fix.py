#!/usr/bin/env python3
"""task2_fix.py -- K5 TASK 2: repair the Candida proton circuit, least invasive first.

Three candidate fixes are tried IN ORDER and the cheapest that works is the one adopted. Each
is scored the same way: the class-E proton budget before and after, and the cost in predicted
growth.

  (a) COST THE TRANSPORT.  Config A's mechanism (MMRT-costed membrane carriers), gated on
      E. coli by P3. If free proton pumping stops being free, the solver may prefer the chain
      on its own. Tried first because it is a mechanism this project already has and has
      validated elsewhere, and because it adds no new assumption about direction.

  (b) IRREVERSIBILITY, reaction by reaction, ITERATIVELY, with the justification recorded per
      reaction. Iteration is required and is itself a finding: constrain the one carrier that
      is leaking and in some models the solver simply picks up another. The loop closes the
      route, not one reaction.
      A mitochondrial H+-coupled symporter is not wrong to be reversible in general. It is
      wrong for it to run in the direction that CREATES proton-motive force for free, because
      that direction is uphill against the very gradient the model is trying to build. This
      constrains the direction, not the reaction.

  (c) EXPLICIT BOUNDS, named and documented, as a last resort.

Nothing is deleted. These carriers are real biology; the defect is that they are free.

Run from the project root:

    python3 reports/K5_respire/task2_fix.py

Writes task2_fix_comparison.csv and task2_reaction_justification.csv beside this file.
"""
from __future__ import annotations

import logging
import os
import sys

import numpy as np
import pandas as pd

logging.getLogger("cobra").setLevel(logging.ERROR)
sys.path.insert(0, "src")

from etcgem.config import build_provider, resolve            # noqa: E402
from etcgem.enzyme_cost import Perturbation                  # noqa: E402
from etcgem.gasflux import add_transport_costs               # noqa: E402
from etcgem.sink_audit import audit_coupling_ion, _ion_of    # noqa: E402
from etcgem.tpc import apply_state                           # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
EXPERIMENT = "candida_B3_ngamT"
TEMPS = (30.0, 40.0)
CANDIDA = ["cauris_iRV973", "chaemulonii_draft", "cduobushaemulonii_draft",
           "cparapsilosis_iDC1003"]
# the mitochondrial inner membrane in these models
MITO, CYTO = "C_00003", "C_00002"

# Generic mitochondrial carrier parameters. Same convention as eciML1515's
# gas_exchange.yaml transport_carrier block, whose kcat P2 settled by reproduction.
CARRIER = dict(kcat=300.0, mw_kDa=35.0, length_aa=320.0)


def build(strain):
    pm = build_provider(resolve(strain, EXPERIMENT))
    return pm, pm.ec.model


def budget(pm, T):
    apply_state(pm.ec, float(T), Perturbation())
    sol = pm.ec.model.optimize()
    rep = audit_coupling_ion(pm, solution=sol)
    rep["status"] = sol.status
    return rep


def leaking_carriers(pm, T):
    """The uncosted reversible carriers that deliver protons to the cytosolic side at the
    solved state -- i.e. the ones actually running the wrong way, not merely able to."""
    rep = budget(pm, T)
    out = []
    for r in rep.get("reactions", []):
        if (not r["costed"] and r["reversible"] and r["translocates"]
                and r["ion_to_outer"] > 1e-9 and not r["is_atp_synthase"]):
            out.append(r)
    return out, rep


def fix_a_cost_transport(pm):
    """(a) give every mito/cyto carrier an enzyme cost."""
    added = add_transport_costs(pm, compartments=frozenset({MITO, CYTO}),
                                only_carbon=False, verbose=False, group="mito_transport",
                                **CARRIER)
    return added


def fix_b_direction_iterative(pm, T, max_rounds: int = 12, verbose: bool = True):
    """(b) applied until the leak is closed, not once.

    Constraining the single carrier that leaks is not enough: in C. duobushaemulonii the
    solver answers by routing the same free proton export through a different carrier. Each
    round re-solves, finds whatever is now delivering protons to the cytosol for free, and
    constrains that. Returns the accumulated list of changes."""
    changed, seen = [], set()
    for rnd in range(max_rounds):
        leaks, rep = leaking_carriers(pm, T)
        ids = [r["reaction"] for r in leaks if r["reaction"] not in seen]
        if not ids:
            if verbose:
                print(f"      round {rnd}: no uncosted reversible carrier is exporting "
                      f"protons; chain supplies "
                      f"{100*rep['chain_supplies_fraction']:.2f} %", flush=True)
            break
        seen.update(ids)
        new = fix_b_direction(pm, ids)
        for c in new:
            c["round"] = rnd
        changed.extend(new)
        if verbose:
            print(f"      round {rnd}: constrained {len(new)} "
                  f"({', '.join(i[:34] for i in ids[:3])}{'...' if len(ids) > 3 else ''})",
                  flush=True)
    return changed


def fix_b_direction(pm, rxn_ids):
    """(b) forbid the PMF-CREATING direction of each named carrier, keeping the other.

    For each reaction, the sign of the cytosolic-proton coefficient says which direction
    exports protons to the cytosol. That direction is bounded to zero; the physiological
    direction, protons flowing down the gradient into the matrix, is left open."""
    model = pm.ec.model
    changed = []
    for rid in rxn_ids:
        if rid not in model.reactions:
            continue
        r = model.reactions.get_by_id(rid)
        h_cyto = sum(c for m_, c in r.metabolites.items()
                     if _ion_of(m_) == "H+" and m_.compartment == CYTO)
        if abs(h_cyto) < 1e-12:
            continue
        old = r.bounds
        if h_cyto > 0:        # forward direction exports H+ to cytosol -> forbid forward
            r.bounds = (min(old[0], 0.0), 0.0)
        else:                 # reverse direction exports H+ to cytosol -> forbid reverse
            r.bounds = (0.0, max(old[1], 0.0))
        changed.append(dict(reaction=rid, old_lb=old[0], old_ub=old[1],
                            new_lb=r.bounds[0], new_ub=r.bounds[1],
                            h_cyto_coeff=h_cyto,
                            justification=(
                                "H+-coupled mitochondrial carrier. The direction bounded away "
                                "is the one that moves protons OUT of the matrix into the "
                                "cytosol, i.e. that CREATES proton-motive force. A symporter "
                                "cannot build the gradient it is driven by; run that way it is "
                                "a free proton pump. The physiological direction, protons "
                                "flowing down the gradient into the matrix, is left open.")))
    model.solver.update()
    return changed


def main():
    rows, just_rows = [], []
    for strain in CANDIDA:
        # ---------- before ----------
        pm, model = build(strain)
        for T in TEMPS:
            b0 = budget(pm, T)
            rows.append(dict(strain=strain, T_C=T, fix="none", **_slim(b0)))
        leaks40, _ = leaking_carriers(pm, 40.0)
        leak_ids = [r["reaction"] for r in leaks40]
        print(f"\n### {strain}: {len(leak_ids)} uncosted reversible carriers deliver protons "
              f"to the cytosol at 40 C", flush=True)
        for r in leaks40[:6]:
            print(f"      {r['ion_to_outer']:+9.3f}  {r['reaction']:36s} {r['name'][:52]}")

        # ---------- (a) cost the transport ----------
        pm_a, _ = build(strain)
        added = fix_a_cost_transport(pm_a)
        for T in TEMPS:
            ba = budget(pm_a, T)
            rows.append(dict(strain=strain, T_C=T, fix="a_cost_transport",
                             n_changed=len(added), **_slim(ba)))
        a40 = budget(pm_a, 40.0)
        print(f"  (a) costed {len(added)} mito/cyto carriers -> chain supplies "
              f"{100*a40['chain_supplies_fraction']:.2f} %, mu {a40['growth']:.6f}", flush=True)

        # ---------- (b) direction ----------
        pm_b, _ = build(strain)
        changed = fix_b_direction_iterative(pm_b, 40.0)
        for T in TEMPS:
            bb = budget(pm_b, T)
            rows.append(dict(strain=strain, T_C=T, fix="b_direction",
                             n_changed=len(changed), **_slim(bb)))
        b40 = budget(pm_b, 40.0)
        print(f"  (b) constrained {len(changed)} carrier directions -> chain supplies "
              f"{100*b40['chain_supplies_fraction']:.2f} %, mu {b40['growth']:.6f}", flush=True)
        for c in changed:
            c.update(strain=strain)
            just_rows.append(c)

        # ---------- (a)+(b) together, for completeness ----------
        pm_ab, _ = build(strain)
        fix_a_cost_transport(pm_ab)
        fix_b_direction_iterative(pm_ab, 40.0, verbose=False)
        for T in TEMPS:
            bab = budget(pm_ab, T)
            rows.append(dict(strain=strain, T_C=T, fix="ab_both", **_slim(bab)))

    d = pd.DataFrame(rows)
    d.to_csv(os.path.join(HERE, "task2_fix_comparison.csv"), index=False)
    pd.DataFrame(just_rows).to_csv(
        os.path.join(HERE, "task2_reaction_justification.csv"), index=False)
    print("\n=== chain supplies (%) and growth, at 40 C ===")
    x = d[d.T_C == 40.0].pivot_table(index="strain", columns="fix",
                                     values="chain_supplies_fraction")
    print((100 * x).round(2).to_string())
    g = d[d.T_C == 40.0].pivot_table(index="strain", columns="fix", values="growth")
    print("\n=== growth (model units) at 40 C ===")
    print(g.round(6).to_string())
    print("\n[k5] wrote task2_fix_comparison.csv and task2_reaction_justification.csv")
    return 0


def _slim(rep):
    keys = ("status", "growth", "atp_synthase_draw", "redox_translocated",
            "redox_in_compartment", "carrier_translocated", "chain_supplies_fraction",
            "chain_supplies_fraction_incl_chemistry", "n_ion_reactions", "n_uncosted",
            "n_uncosted_reversible")
    return {k: rep.get(k, np.nan) for k in keys}


if __name__ == "__main__":
    sys.exit(main())
