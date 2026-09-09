#!/usr/bin/env python3
"""task_b2_verifications.py -- Y1 PART B, the three verifications and two stress tests.

    python3 reports/Y1_yeast_audit/task_b2_verifications.py --bayesiangem /path/to/BayesianGEM

WHAT THIS ADDS TO task_b_coupling_audit.py.

(1) THE RESPIRATORY STATE. The batch states in task_b are FERMENTATIVE -- on unlimited glucose
    under a protein-pool cap the model does what the Crabtree effect says it should, and ATP
    synthase carries no flux at all, so the coupling budget is undefined there (0/0). The state
    at which the proton circuit actually bears load is the chemostat, which is where the paper's
    respiratory conclusions come from (Fig 4). Their `etc.simulate_chomostat` runs the model
    inside `with model:` blocks and returns only a Solution, so the state cannot be audited from
    outside it; `chemostat_state` performs THEIR OWN sequence of calls, in their order, in
    place, and `--verify-chemostat` checks it reproduces `etc.simulate_chomostat`'s solution.

(2) THE DIRECTIONALITY CENSUS. Every reaction that moves a proton between the mitochondrion and
    the cytosol, with its enzyme-cost status and its DIRECTION. GECKO writes every reaction
    irreversibly and supplies a `_REV` twin where the reconstruction allowed both directions, so
    "reversible" in a GECKO model is not `lb < 0 < ub` -- it is the existence of an uncosted
    twin. K5's criterion has to be applied that way or it is vacuous on any GECKO model,
    eciML1515 included.

(3) THE COUNTERFACTUAL. Block every COSTED proton-translocating reaction that delivers protons
    to the energised compartment -- the respiratory chain -- and re-solve. If ATP synthase can
    still run, something uncosted is supplying its protons and the circuit is shorted. If it
    cannot, the circuit is closed through the chain, which is the negative result stated with
    evidence rather than asserted.

Writes task_b2_mito_proton_census.csv, task_b2_chemostat_budget.csv,
task_b2_chemostat_translocators.csv and task_b2_counterfactual.csv beside this file.
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

from etcgem.sink_audit import _ion_of, audit_coupling_ion, find_atp_synthase   # noqa: E402
from task_b_coupling_audit import AEROBIC, apply_etcpy, load_etcpy             # noqa: E402
from yeast_model import YeastPM, load                                          # noqa: E402

GROWTH, GLC, POOL = "r_2111", "r_1714_REV", "prot_pool_exchange"


def chemostat_state(model, etc, params, dilu, T_C, sigma):
    """Their `simulate_chomostat` steps, applied IN PLACE so the state can be audited.

    Their code is called for every step that touches the model; nothing here re-implements it."""
    T = T_C + 273.15
    model.reactions.get_by_id(GROWTH).lower_bound = dilu
    model.objective = GLC
    model.objective.direction = "min"
    etc.map_fNT(model, T, params)
    etc.map_kcatT(model, T, params)
    etc.set_NGAMT(model, T)
    etc.set_sigma(model, sigma)
    s1 = model.optimize()
    model.reactions.get_by_id(GLC).upper_bound = s1.objective_value * 1.001
    model.objective = POOL
    model.objective.direction = "min"
    return model.optimize()


def mito_proton_census(model, costed, inner, outer):
    """Every reaction moving a proton between the energised compartment and the other side."""
    ids = {r.id for r in model.reactions}
    rows = []
    for r in model.reactions:
        bycomp = {}
        for m_, c in r.metabolites.items():
            if _ion_of(m_) == "H+":
                bycomp[m_.compartment] = bycomp.get(m_.compartment, 0.0) + float(c)
        bycomp = {k: v for k, v in bycomp.items() if abs(v) > 1e-12}
        if inner not in bycomp or outer not in bycomp:
            continue
        twin = r.id[:-4] if r.id.endswith("_REV") else r.id + "_REV"
        rows.append(dict(
            reaction=r.id, name=r.name, costed=r.id in costed,
            lb=float(r.lower_bound), ub=float(r.upper_bound),
            h_inner=bycomp[inner], h_outer=bycomp[outer],
            direction=("to_energised" if bycomp[outer] > 0 else "from_energised"),
            twin=twin if twin in ids else "",
            twin_costed=(twin in costed) if twin in ids else "",
            reaction_string=r.reaction[:220]))
    return pd.DataFrame(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bayesiangem", required=True)
    ap.add_argument("--T", type=float, default=30.0)
    ap.add_argument("--sigma", type=float, default=0.5)
    ap.add_argument("--dilu", type=float, default=0.1)
    ap.add_argument("--verify-chemostat", action="store_true", default=True)
    args = ap.parse_args()
    bg = os.path.abspath(args.bayesiangem)
    etc = load_etcpy(bg)
    raw = pd.read_csv(os.path.join(bg, "data", "model_enzyme_params.csv"), index_col=0)
    params = etc.calculate_thermal_params(raw)
    path = os.path.join(bg, "models", AEROBIC)

    # --- (1) the respiratory state ------------------------------------------------------
    m, _ = load(path)
    sol = chemostat_state(m, etc, params, args.dilu, args.T, args.sigma)
    pm = YeastPM(m)
    print(f"[y1b2] chemostat D={args.dilu} T={args.T}C sigma={args.sigma}: [{sol.status}] "
          f"glc={sol.fluxes[GLC]:.4f} O2={sol.fluxes.get('r_1992_REV', float('nan')):.4f} "
          f"pool={sol.objective_value:.6f}", flush=True)

    if args.verify_chemostat:
        m2, _ = load(path)
        their = etc.simulate_chomostat(m2, args.dilu, raw, [args.T + 273.15], args.sigma,
                                       GROWTH, GLC, POOL)
        ours, theirs = float(sol.objective_value), float(their[0].objective_value)
        print(f"[y1b2] verify: their simulate_chomostat pool={theirs:.10f} vs inlined "
              f"{ours:.10f}  |diff|={abs(ours - theirs):.3e}", flush=True)

    rep = audit_coupling_ion(pm, solution=sol)
    inner, outer = rep["inner_compartment"], rep["outer_compartment"]
    rxns = rep.pop("reactions")
    rep.update(state="aerobic_chemostat", model=AEROBIC, T_C=args.T, sigma=args.sigma,
               dilution=args.dilu, status=sol.status)
    pd.DataFrame([rep]).to_csv(os.path.join(HERE, "task_b2_chemostat_budget.csv"), index=False)
    pd.DataFrame(rxns).to_csv(os.path.join(HERE, "task_b2_chemostat_translocators.csv"),
                              index=False)
    print(f"[y1b2] chemostat budget: ion={rep['ion']} ({inner}->{outer}) "
          f"draw={rep['atp_synthase_draw']:.3f} redox_translocated="
          f"{rep['redox_translocated']:.3f} carriers={rep['carrier_translocated']:.3f} "
          f"-> chain supplies {100*rep['chain_supplies_fraction']:.2f} % "
          f"[{rep['n_uncosted']} uncosted ion movers, {rep['n_uncosted_reversible']} reversible]",
          flush=True)

    # --- (2) the directionality census --------------------------------------------------
    census = mito_proton_census(pm.ec.model, pm.costed_ids, inner, outer)
    census["flux"] = [float(sol.fluxes.get(r, 0.0)) for r in census.reaction]
    census.to_csv(os.path.join(HERE, "task_b2_mito_proton_census.csv"), index=False)
    free_in = census[(~census.costed) & (census.direction == "to_energised")]
    print(f"[y1b2] census: {len(census)} reactions move H+ across the {inner}/{outer} membrane; "
          f"{(~census.costed).sum()} uncosted; {len(free_in)} of those deliver H+ TO the "
          f"energised side ({outer}); uncosted with an uncosted twin: "
          f"{int(((~census.costed) & (census.twin_costed == False)).sum())}", flush=True)  # noqa: E712

    # --- (3) the counterfactual ---------------------------------------------------------
    rows = []
    syn, ion, _ = find_atp_synthase(pm.ec.model, fluxes=sol.fluxes)
    syn_ids = {r.id for members in syn.values() for r in members}
    chain = census[(census.costed) & (census.direction == "to_energised")
                   & (~census.reaction.isin(syn_ids))]
    with pm.ec.model as mm:
        for rid in chain.reaction:
            mm.reactions.get_by_id(rid).upper_bound = 0.0
        cf = mm.optimize()
        cf_syn = sum(abs(float(cf.fluxes.get(r, 0.0))) for r in syn_ids) if cf.status == "optimal" else float("nan")
    base_syn = sum(abs(float(sol.fluxes.get(r, 0.0))) for r in syn_ids)
    rows.append(dict(test="chemostat, block costed chain proton translocators",
                     n_blocked=len(chain), blocked=" ".join(sorted(chain.reaction)),
                     status=cf.status,
                     atp_synthase_flux_before=base_syn, atp_synthase_flux_after=cf_syn,
                     objective_before=float(sol.objective_value),
                     objective_after=(float(cf.objective_value) if cf.status == "optimal" else float("nan"))))
    print(f"[y1b2] counterfactual A (chemostat): blocked {len(chain)} costed chain "
          f"translocators -> [{cf.status}] ATP synthase flux {base_syn:.4f} -> {cf_syn:.4f}",
          flush=True)

    # The chemostat pins growth at the dilution rate, so blocking the chain can only come back
    # INFEASIBLE -- informative, but blunt. The sharper question is: with growth free and the
    # chain shut, how much ATP synthase flux can ANY combination of the remaining reactions
    # support? If the answer is zero, nothing uncosted supplies the energised compartment.
    m3, _ = load(path)
    apply_etcpy(m3, etc, params, args.T, args.sigma)
    pm3 = YeastPM(m3)
    base3 = m3.optimize()
    syn3, _, _ = find_atp_synthase(m3, fluxes=base3.fluxes)
    syn3_ids = sorted({r.id for members in syn3.values() for r in members})
    census3 = mito_proton_census(m3, pm3.costed_ids, inner, outer)
    chain3 = census3[(census3.costed) & (census3.direction == "to_energised")
                     & (~census3.reaction.isin(syn3_ids))]
    for label, block in (("max ATP synthase, chain intact", []),
                         ("max ATP synthase, costed chain blocked", list(chain3.reaction))):
        with m3 as mm:
            for rid in block:
                mm.reactions.get_by_id(rid).upper_bound = 0.0
            mm.objective = {mm.reactions.get_by_id(r): 1.0 for r in syn3_ids
                            if not r.startswith("arm_")}
            mm.objective.direction = "max"
            r3 = mm.optimize()
            val = float(r3.objective_value) if r3.status == "optimal" else float("nan")
        rows.append(dict(test=label, n_blocked=len(block), blocked=" ".join(sorted(block)),
                         status=r3.status, atp_synthase_flux_before=float("nan"),
                         atp_synthase_flux_after=val, objective_before=float("nan"),
                         objective_after=val))
        print(f"[y1b2] counterfactual B ({label}): [{r3.status}] max ATP synthase flux "
              f"= {val:.6f}", flush=True)
    # --- (3b) every free reversible proton mover, anywhere in the model -------------------
    # The census above covers the energised membrane. This covers the whole model: any
    # H+-moving reaction that is uncosted AND has an uncosted `_REV` twin -- K5's criterion in
    # the form GECKO forces it to take. It is the nearest thing to a hit in this model, so it
    # is reported explicitly rather than left implied by an absence.
    ids = {r.id for r in pm.ec.model.reactions}
    free_pairs = []
    for r in pm.ec.model.reactions:
        bycomp = {}
        for m_, c in r.metabolites.items():
            if _ion_of(m_) == "H+":
                bycomp[m_.compartment] = bycomp.get(m_.compartment, 0.0) + float(c)
        bycomp = {k: v for k, v in bycomp.items() if abs(v) > 1e-12}
        if len(bycomp) < 2 or r.id in pm.costed_ids:
            continue
        twin = r.id[:-4] if r.id.endswith("_REV") else r.id + "_REV"
        if twin not in ids or twin in pm.costed_ids:
            continue
        free_pairs.append(dict(reaction=r.id, twin=twin, name=r.name,
                               compartments=" ".join(sorted(bycomp)),
                               touches_energised=(outer in bycomp and inner in bycomp),
                               h=" ".join(f"{k}:{v:+g}" for k, v in sorted(bycomp.items())),
                               flux=float(sol.fluxes.get(r.id, 0.0)),
                               reaction_string=r.reaction[:200]))
    fp = pd.DataFrame(free_pairs)
    fp.to_csv(os.path.join(HERE, "task_b2_free_proton_pairs.csv"), index=False)
    print(f"[y1b2] free reversible proton movers anywhere in the model: {len(fp)}; "
          f"touching the {inner}/{outer} membrane: "
          f"{int(fp.touches_energised.sum()) if len(fp) else 0}", flush=True)

    # --- (4) the energy-generating-cycle test -------------------------------------------
    # The sharpest form of the question. Shut every exchange except the protein pool -- no
    # glucose, no oxygen, no secretion -- and ask the model to make ATP anyway. Enzyme is not a
    # free-energy source, so the pool stays open; anything that still runs is running on
    # nothing. A model with an uncosted free-energy shortcut answers with a positive number.
    for label, target in (("ATP synthase", None), ("NGAM (ATP hydrolysis)", "NGAM")):
        with m3 as mm:
            for r in mm.reactions:
                if r.boundary and r.id != POOL:
                    r.bounds = (0.0, 0.0)
            # NGAM is PINNED (lb = ub) by their set_NGAMT, so with no substrate the LP is
            # infeasible for reasons that have nothing to do with the question. Release it.
            mm.reactions.NGAM.bounds = (0.0, 1000.0)
            if target is None:
                mm.objective = {mm.reactions.get_by_id(r): 1.0 for r in syn3_ids
                                if not r.startswith("arm_")}
            else:
                mm.objective = mm.reactions.get_by_id(target)
            mm.objective.direction = "max"
            r4 = mm.optimize()
            val = float(r4.objective_value) if r4.status == "optimal" else float("nan")
        rows.append(dict(test=f"all exchanges closed, max {label}", n_blocked=-1, blocked="",
                         status=r4.status, atp_synthase_flux_before=float("nan"),
                         atp_synthase_flux_after=val, objective_before=float("nan"),
                         objective_after=val))
        print(f"[y1b2] energy-generating-cycle test, max {label} with every exchange shut: "
              f"[{r4.status}] {val:.10g}", flush=True)

    pd.DataFrame(rows).to_csv(os.path.join(HERE, "task_b2_counterfactual.csv"), index=False)
    print("[y1b2] wrote task_b2_*.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
