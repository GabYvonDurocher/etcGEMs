#!/usr/bin/env python3
"""task1_etc_complement.py -- K4 TASK 1: can the four Candida models express an ETC
membrane-area constraint at all?

This is the GATE. It answers three questions and writes one table for each:

  1. WHICH ETC COMPLEXES ARE IN EACH MODEL, and is each one enzyme-costed?
     -> task1_inventory.csv
     The area constraint (src/etcgem/etc_area.py) binds on FLUX VARIABLES, so a reaction
     does not have to be enzyme-costed for the constraint to reach it. Cost membership is
     still reported, because an uncosted reaction is invisible to the proteome budget and
     so behaves differently under temperature.

  2. IS THE MODELLED CHAIN LOAD-BEARING? -> task1_coupling.csv, task1_fva.csv
     A constraint can only bind on something that carries flux. Each complex is knocked out
     in turn; the flux range at 99% of optimal growth is reported (so "carries no flux at
     the optimum" and "cannot carry flux" are distinguished); and the mitochondrial proton
     budget is traced, which is what actually decides the question.

  3. IF IT IS NOT LOAD-BEARING, WHAT IS IT FOR? -> task1_essentiality.csv, task1_quinol.csv
     Every combination of complexes I-IV is deleted, and the ubiquinol balance is traced at
     the optimum. The chain turns out to be essential only in combination, and for a
     BIOSYNTHETIC reason rather than a bioenergetic one.

  4. WHY IS IT BYPASSED? -> task1_proton_carriers.csv, task1_uncoupling.csv
     Two labelled diagnostics, neither of them adopted as a default: close the non-ETC
     proton carriers outright, and (surgically) strip only their proton coupling while
     keeping the metabolite transport.

Run from the project root:

    python3 reports/K4_membrane/task1_etc_complement.py

Reads only committed strain models and the K2 configuration (candida_B3_ngamT). Writes the
five CSVs beside this file. Changes nothing.
"""
from __future__ import annotations

import json
import logging
import os
import sys

import numpy as np
import pandas as pd

logging.getLogger("cobra").setLevel(logging.ERROR)
sys.path.insert(0, "src")

from cobra.flux_analysis import flux_variability_analysis as fva          # noqa: E402
from etcgem.config import build_provider, resolve, strain_dir             # noqa: E402
from etcgem.enzyme_cost import Perturbation                               # noqa: E402
from etcgem.tpc import apply_state                                        # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
EXPERIMENT = "candida_B3_ngamT"     # the K2 configuration: unfolding + grounded budget + NGAM(T)
TEMPS = (30.0, 40.0)                # a permissive temperature and the temperature the
                                    # counterfactual asks about

# The ETC complexes each model encodes, found by reading the SBML (see the report for how
# each was identified: KEGG reaction id, name, proton stoichiometry and the metabolites).
# `alt` is C. parapsilosis' plasma-membrane ("CYTMEM") NADH dehydrogenase and bc1, which the
# other three models do not have.
ETC_COMPLEXES = {
    "cauris_iRV973": {
        "complex I (NADH dehydrogenase)": ["R11945__mito", "R11945__cyto"],
        "complex II (succinate dehydrogenase)": ["R02164__mito"],
        "complex III (cytochrome bc1)": ["R02161__mito"],
        "complex IV (cytochrome c oxidase)": ["R00081__mito"],
        "complex V (ATP synthase)": ["T_ATP_synthase__mito"],
    },
    "chaemulonii_draft": {
        "complex I (NADH dehydrogenase)": ["R11945__mito", "R11945__cyto"],
        "complex II (succinate dehydrogenase)": ["R02164__mito"],
        "complex III (cytochrome bc1)": ["R02161__mito"],
        "complex IV (cytochrome c oxidase)": ["R00081__mito"],
        "complex V (ATP synthase)": ["T_ATP_synthase__mito"],
    },
    "cduobushaemulonii_draft": {
        "complex I (NADH dehydrogenase)": ["R11945__mito", "R11945__cyto"],
        "complex II (succinate dehydrogenase)": ["R02164__mito"],
        "complex III (cytochrome bc1)": ["R02161__mito"],
        "complex IV (cytochrome c oxidase)": ["R00081__mito"],
        "complex V (ATP synthase)": ["T_ATP_synthase__mito"],
    },
    "cparapsilosis_iDC1003": {
        "complex I (NADH dehydrogenase)": ["R11945__mito"],
        "complex II (succinate dehydrogenase)": ["R02164__mito"],
        "complex III (cytochrome bc1)": ["T02161__mito"],
        "complex IV (cytochrome c oxidase)": ["R00081__mito"],
        "complex V (ATP synthase)": ["T00485__cyto"],
        "alternative chain (plasma membrane)": ["TI6900005_CYTMEM__plas",
                                                "TI6900007_CYTMEM__plas"],
    },
}
STRAINS = list(ETC_COMPLEXES)
H_CYTO, H_MITO = "C00080__cyto", "C00080__mito"


def etc_reactions(strain):
    return [r for rids in ETC_COMPLEXES[strain].values() for r in rids]


def build(strain):
    cfg = resolve(strain, EXPERIMENT)
    pm = build_provider(cfg)
    return pm, pm.ec.model, {e.rxn_id for e in pm.ec.table.entries}


def h_transfer_to_cytosol(model, rid, flux):
    """Net protons this reaction delivers to the cytosolic side, at this flux."""
    if rid not in model.reactions or not np.isfinite(flux):
        return 0.0
    r = model.reactions.get_by_id(rid)
    return sum(c * flux for m_, c in r.metabolites.items() if m_.id == H_CYTO)


# ---------------------------------------------------------------------------
# 1. the inventory
# ---------------------------------------------------------------------------
def inventory():
    rows = []
    for s in STRAINS:
        pm, m, costed = build(s)
        kc = pd.read_csv(os.path.join(strain_dir(s), "dltkcat", "kcat_table.csv"))
        flux = {}
        for T in TEMPS:
            apply_state(pm.ec, T, Perturbation())
            sol = m.optimize()
            flux[T] = (sol.status, float(sol.objective_value or 0.0), sol.fluxes)
        for complex_name, rids in ETC_COMPLEXES[s].items():
            for rid in rids:
                if rid not in m.reactions:
                    rows.append(dict(strain=s, complex=complex_name, rxn=rid, in_model=False))
                    continue
                r = m.reactions.get_by_id(rid)
                krow = kc[kc["rxn_id"] == rid]
                rows.append(dict(
                    strain=s, complex=complex_name, rxn=rid, in_model=True,
                    name=r.name, ec_code=str(r.annotation.get("ec-code", "")),
                    lb=r.lower_bound, ub=r.upper_bound,
                    n_genes=len(r.genes), gpr=r.gene_reaction_rule,
                    enzyme_costed=(rid in costed),
                    kcat_s=(float(krow["kcat_s"].iloc[0]) if len(krow) else np.nan),
                    mw_kDa=(float(krow["mw_kDa"].iloc[0]) if len(krow) else np.nan),
                    kcat_source=(krow["source"].iloc[0] if len(krow) else ""),
                    h_cyto=sum(c for m_, c in r.metabolites.items() if m_.id == H_CYTO),
                    h_mito=sum(c for m_, c in r.metabolites.items() if m_.id == H_MITO),
                    equation=r.reaction,
                    **{f"flux_{int(T)}C": float(flux[T][2].get(rid, np.nan)) for T in TEMPS},
                ))
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# 2. is it load-bearing?
# ---------------------------------------------------------------------------
def coupling():
    rows = []
    for s in STRAINS:
        pm, m, _ = build(s)
        for T in TEMPS:
            apply_state(pm.ec, T, Perturbation())
            sol = m.optimize()
            base = float(sol.objective_value)
            row = dict(strain=s, T_C=T, mu_base=base)
            # protons the chain delivers to the cytosolic side, against what ATP synthase uses
            deliver = sum(h_transfer_to_cytosol(m, rid, float(sol.fluxes.get(rid, 0.0)))
                          for cx, rids in ETC_COMPLEXES[s].items() if "ATP synthase" not in cx
                          for rid in rids)
            use = -sum(h_transfer_to_cytosol(m, rid, float(sol.fluxes.get(rid, 0.0)))
                       for cx, rids in ETC_COMPLEXES[s].items() if "ATP synthase" in cx
                       for rid in rids)
            row["etc_H_to_cytosol"] = deliver
            row["atp_synthase_H_used"] = use
            row["chain_supplies_frac"] = (deliver / use) if use > 1e-9 else np.nan
            for cx, rids in ETC_COMPLEXES[s].items():
                keep = {}
                for rid in rids:
                    if rid in m.reactions:
                        r = m.reactions.get_by_id(rid)
                        keep[rid] = r.bounds
                        r.bounds = (0.0, 0.0)
                m.solver.update()
                mu = m.slim_optimize()
                row[f"mu_ko::{cx}"] = float(mu) if mu is not None and np.isfinite(mu) else 0.0
                for rid, b in keep.items():
                    m.reactions.get_by_id(rid).bounds = b
                m.solver.update()
            # oxygen: is it needed for respiration, or for biosynthesis?
            exO = [r for r in m.reactions if r.id.startswith("EX_") and len(r.metabolites) == 1
                   and list(r.metabolites)[0].id.startswith("C00007__")]
            row["o2_uptake"] = float(sum(abs(sol.fluxes.get(r.id, 0.0)) for r in exO))
            keep = [(r, r.bounds) for r in exO]
            for r, b in keep:
                r.bounds = (0.0, max(b[1], 0.0))
            m.solver.update()
            mu = m.slim_optimize()
            row["mu_anaerobic"] = float(mu) if mu is not None and np.isfinite(mu) else 0.0
            for r, b in keep:
                r.bounds = b
            m.solver.update()
            rows.append(row)
    return pd.DataFrame(rows)


def variability():
    rows = []
    for s in STRAINS:
        pm, m, _ = build(s)
        rids = [r for r in etc_reactions(s) if r in m.reactions]
        exO = [r.id for r in m.reactions if r.id.startswith("EX_") and len(r.metabolites) == 1
               and list(r.metabolites)[0].id.startswith("C00007__")]
        for T in TEMPS:
            apply_state(pm.ec, T, Perturbation())
            sol = m.optimize()
            f = fva(m, reaction_list=rids + exO, fraction_of_optimum=0.99, processes=1)
            for rid in f.index:
                rows.append(dict(strain=s, T_C=T, mu=float(sol.objective_value), rxn=rid,
                                 flux_at_optimum=float(sol.fluxes.get(rid, np.nan)),
                                 fva_min=float(f.loc[rid, "minimum"]),
                                 fva_max=float(f.loc[rid, "maximum"])))
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# 3. why not? -- the proton carriers
# ---------------------------------------------------------------------------
def proton_carriers(model, strain, costed):
    """Non-ETC reactions that move H+ between cytosol and mitochondrion."""
    out = []
    etc = set(etc_reactions(strain))
    for r in model.reactions:
        comps = {m_.compartment for m_ in r.metabolites if m_.id.startswith("C00080__")}
        if {"C_00002", "C_00003"} <= comps and r.id not in etc:
            out.append(r)
    return out


def shunts_and_uncoupling():
    shunt_rows, unc_rows = [], []
    for s in STRAINS:
        pm, m, costed = build(s)
        carriers = proton_carriers(m, s, costed)
        rids = [r for r in etc_reactions(s) if r in m.reactions]
        for r in carriers:
            shunt_rows.append(dict(strain=s, rxn=r.id, name=r.name,
                                   enzyme_costed=(r.id in costed),
                                   lb=r.lower_bound, ub=r.upper_bound, equation=r.reaction))
        uncosted = [r for r in carriers if r.id not in costed]
        for T in TEMPS:
            apply_state(pm.ec, T, Perturbation())
            sol = m.optimize()
            base = float(sol.objective_value)
            bf = {rid: float(sol.fluxes.get(rid, np.nan)) for rid in rids}

            # (a) close them outright
            keep = [(r, r.bounds) for r in carriers]
            for r, _ in keep:
                r.bounds = (0.0, 0.0)
            m.solver.update()
            s_closed = m.optimize()
            mu_closed = float(s_closed.objective_value) if s_closed.status == "optimal" else 0.0
            f_closed = {rid: (float(s_closed.fluxes.get(rid, np.nan))
                              if s_closed.status == "optimal" else np.nan) for rid in rids}
            for r, b in keep:
                r.bounds = b
            m.solver.update()

            # (b) strip only the proton coupling from the UNCOSTED carriers
            undo = []
            for r in uncosted:
                hm = {m_: c for m_, c in r.metabolites.items() if m_.id.startswith("C00080__")}
                r.add_metabolites({m_: -c for m_, c in hm.items()})
                undo.append((r, hm))
            m.solver.update()
            s_unc = m.optimize()
            mu_unc = float(s_unc.objective_value) if s_unc.status == "optimal" else 0.0
            f_unc = {rid: (float(s_unc.fluxes.get(rid, np.nan))
                           if s_unc.status == "optimal" else np.nan) for rid in rids}
            for r, hm in undo:
                r.add_metabolites(hm)
            m.solver.update()

            unc_rows.append(dict(
                strain=s, T_C=T, n_carriers=len(carriers), n_uncosted=len(uncosted),
                mu_base=base, mu_carriers_closed=mu_closed, mu_proton_uncoupled=mu_unc,
                **{f"base::{k}": v for k, v in bf.items()},
                **{f"closed::{k}": v for k, v in f_closed.items()},
                **{f"uncoupled::{k}": v for k, v in f_unc.items()}))
    return pd.DataFrame(shunt_rows), pd.DataFrame(unc_rows)


def essentiality_and_quinol():
    """Delete every combination of complexes I-IV, and trace the ubiquinol balance.

    Single knockouts are harmless in the three Candidozyma models and joint ones are lethal,
    which looks like redundancy in a respiratory chain. It is not: the chain's only essential
    job in these models is to RE-OXIDISE the ubiquinol that dihydroorotate dehydrogenase
    (pyrimidine biosynthesis) produces, so its flux is set by nucleotide demand and not by
    energy demand.
    """
    import itertools
    ess_rows, q_rows = [], []
    for s in STRAINS:
        pm, m, _ = build(s)
        groups = {k: v for k, v in ETC_COMPLEXES[s].items() if "ATP synthase" not in k
                  and "alternative" not in k}
        keys = list(groups)
        for T in TEMPS:
            apply_state(pm.ec, T, Perturbation())
            base = m.slim_optimize()
            base = 0.0 if base is None or not np.isfinite(base) else float(base)
            for k in range(1, len(keys) + 1):
                for combo in itertools.combinations(keys, k):
                    keep = {}
                    for cx in combo:
                        for rid in groups[cx]:
                            if rid in m.reactions:
                                r = m.reactions.get_by_id(rid)
                                keep[rid] = r.bounds
                                r.bounds = (0.0, 0.0)
                    m.solver.update()
                    apply_state(pm.ec, T, Perturbation())
                    v = m.slim_optimize()
                    mu = 0.0 if v is None or not np.isfinite(v) else float(v)
                    for rid, b in keep.items():
                        m.reactions.get_by_id(rid).bounds = b
                    m.solver.update()
                    ess_rows.append(dict(strain=s, T_C=T, deleted="+".join(combo),
                                         n_deleted=k, mu_base=base, mu=mu,
                                         frac_of_base=(mu / base if base > 0 else np.nan),
                                         lethal=bool(mu < 1e-6)))
            # ubiquinol balance
            apply_state(pm.ec, T, Perturbation())
            sol = m.optimize()
            for qid in ("M8428__mito", "M8416__mito"):
                if qid not in [x.id for x in m.metabolites]:
                    continue
                q = m.metabolites.get_by_id(qid)
                # sorted: Metabolite.reactions is a SET, so iteration order varies between
                # runs and the committed CSV would not be reproducible row-for-row.
                for r in sorted(q.reactions, key=lambda r_: r_.id):
                    v = float(sol.fluxes.get(r.id, 0.0))
                    c = float(r.metabolites[q])
                    if abs(v * c) > 1e-9:
                        q_rows.append(dict(strain=s, T_C=T, metabolite=qid, rxn=r.id,
                                           name=r.name, net_flux=v * c,
                                           role=("produces" if v * c > 0 else "consumes")))
    return pd.DataFrame(ess_rows), pd.DataFrame(q_rows)


def main():
    print("K4 TASK 1 -- the ETC complement of the four Candida models\n")
    inv = inventory()
    inv.to_csv(os.path.join(HERE, "task1_inventory.csv"), index=False)
    print(f"  task1_inventory.csv  {len(inv)} rows")
    cou = coupling()
    cou.to_csv(os.path.join(HERE, "task1_coupling.csv"), index=False)
    print(f"  task1_coupling.csv   {len(cou)} rows")
    var = variability()
    var.to_csv(os.path.join(HERE, "task1_fva.csv"), index=False)
    print(f"  task1_fva.csv        {len(var)} rows")
    sh, unc = shunts_and_uncoupling()
    sh.to_csv(os.path.join(HERE, "task1_proton_carriers.csv"), index=False)
    unc.to_csv(os.path.join(HERE, "task1_uncoupling.csv"), index=False)
    print(f"  task1_proton_carriers.csv {len(sh)} rows")
    print(f"  task1_uncoupling.csv      {len(unc)} rows")
    ess, quin = essentiality_and_quinol()
    ess.to_csv(os.path.join(HERE, "task1_essentiality.csv"), index=False)
    quin.to_csv(os.path.join(HERE, "task1_quinol.csv"), index=False)
    print(f"  task1_essentiality.csv    {len(ess)} rows")
    print(f"  task1_quinol.csv          {len(quin)} rows")

    print("\nWHAT THE CHAIN IS FOR -- lethal deletion combinations at 40 C:")
    for s_ in STRAINS:
        x = ess[(ess.strain == s_) & (ess.T_C == 40.0)]
        lethal = sorted(x[x.lethal]["deleted"], key=len)
        print(f"  {s_:26s} lethal: {', '.join(lethal) if lethal else 'none'}")

    print("\nHEADLINE -- fraction of ATP synthase's protons the respiratory chain supplies:")
    for _, r in cou.iterrows():
        print(f"  {r['strain']:26s} {r['T_C']:.0f} C   "
              f"chain delivers {r['etc_H_to_cytosol']:8.3f}, ATP synthase uses "
              f"{r['atp_synthase_H_used']:8.3f}  -> {100*r['chain_supplies_frac']:7.2f} %")
    return 0


if __name__ == "__main__":
    sys.exit(main())
