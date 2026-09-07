"""Uncosted free-energy sinks: a framework-wide audit, generalising three bespoke fixes.

Three strains in this project have needed the same kind of correction, each found by hand
and each fixed differently:

* *E. coli* (eciML1515): four uncosted O2-consuming side reactions short-circuit the
  electron transport chain with a futile O2 cycle -- ``providers.close_free_energy_sinks``.
* *M. maripaludis*: a hard-PINNED, uncosted "protein-secreting ATPase" fixed at
  5.12 mmol ATP/gDW/h dominates the enzyme-limited energy budget -- ``relax_pinned``.
* *C. parapsilosis* (iDC1003): its ATP maintenance reaction ships REVERSIBLE, so the solver
  runs maintenance backwards and makes ATP from ADP + Pi -- ``pin_at_ub`` (K1/K2).

All three are the same failure: a reaction that moves free energy WITHOUT paying enzyme
cost, so the proteome constraint does not see it. This module is the check every future
strain gets for free. It REPORTS; it fixes nothing.

Three classes:

    A. uncosted energy-producing reactions -- a reaction that can carry flux, is not in
       the enzyme cost table (so it is free), and produces ATP or reducing equivalents
       (NAD(P)H, reduced ferredoxin, quinol, proton-motive force carriers).
    B. reversible maintenance/ATPM reactions -- maintenance that the solver can run
       backwards, turning an obligate cost into a source.
    C. hard-pinned uncosted drains -- a reaction with a forced non-zero lower bound and no
       enzyme cost, which spends or supplies free energy the pool cannot account for.
    D. uncosted consumers of a terminal electron acceptor -- a free reaction that eats O2
       (or nitrate, or fumarate) and so bypasses the enzyme-costed respiratory chain. This
       is the E. coli case: four uncosted O2 sinks short-circuiting the ETC.

Class A is the broad, cheap screen and will list legitimate reactions too (transport,
spontaneous chemistry, the biomass and exchange reactions are excluded, but a genuine
uncosted transhydrogenase is a real hit and a real modelling gap). Classes B and C are
narrow and each hit is worth reading. Nothing here decides whether a hit is a defect.
"""
from __future__ import annotations

import re
from typing import Dict, List, Optional

# Metabolite-id fragments that mark a free-energy carrier, matched case-insensitively
# against the metabolite id and name. Deliberately generous: the models in this project
# span BiGG (atp_c), ModelSEED (cpd00002_c0) and KEGG (C00002__cyto) namespaces.
ENERGY_PATTERNS: Dict[str, List[str]] = {
    "ATP":  [r"^atp(_|\[|$)", r"\batp__?", r"C00002", r"cpd00002"],
    "GTP":  [r"^gtp(_|\[|$)", r"C00044", r"cpd00038"],
    "NADH": [r"^nadh(_|\[|$)", r"C00004", r"cpd00004"],
    "NADPH": [r"^nadph(_|\[|$)", r"C00005", r"cpd00005"],
    "FADH2": [r"^fadh2(_|\[|$)", r"C01352", r"cpd00982"],
    "QH2":  [r"^q8h2(_|\[|$)", r"^mql8(_|\[|$)", r"^ubiquinol", r"C00390"],
    "Fdred": [r"^fdxrd", r"^fdred", r"reduced ferredoxin"],
}
# Terminal electron acceptors. An UNCOSTED reaction that consumes one of these bypasses the
# enzyme-costed respiratory chain -- the E. coli case (four uncosted O2 sinks short-circuit
# the ETC with a futile O2 cycle), which is class D below.
ACCEPTOR_PATTERNS = {
    "O2": [r"^o2(_|\[|$)", r"C00007", r"cpd00007", r"^oxygen"],
    "NO3": [r"^no3(_|\[|$)", r"C00244"],
    "fumarate": [r"^fum(_|\[|$)", r"C00122"],
}
_ACCEPTORS = {k: [re.compile(x, re.I) for x in v] for k, v in ACCEPTOR_PATTERNS.items()}
_COMPILED = {k: [re.compile(p, re.I) for p in v] for k, v in ENERGY_PATTERNS.items()}

# Maintenance reactions, matched on the id and name. Anchored patterns, not bare
# substrings: "gam" alone matches gamma-glutamyl chemistry, which is not maintenance.
MAINTENANCE_RE = re.compile(
    r"(^|[^a-z])(atpm|ngam|gam)([^a-z]|$)|atp[_ -]?maintenance|maintenance[_ -]?atp"
    r"|non[- ]?growth[- ]?associated|\bmaintenance\b", re.I)


def _acceptor(met) -> Optional[str]:
    text = f"{met.id} {getattr(met, 'name', '') or ''}"
    for name, pats in _ACCEPTORS.items():
        if any(p.search(met.id) or p.search(text) for p in pats):
            return name
    return None


def _carrier(met) -> Optional[str]:
    text = f"{met.id} {getattr(met, 'name', '') or ''}"
    for carrier, pats in _COMPILED.items():
        if any(p.search(met.id) or p.search(text) for p in pats):
            return carrier
    return None


def _is_exchange_or_biomass(rxn) -> bool:
    return (rxn.boundary or rxn.id.startswith(("EX_", "DM_", "SK_", "Drain"))
            or "iomass" in rxn.id or "BIOMASS" in rxn.id.upper())


def audit_sinks(pm, max_report: int = 40) -> Dict[str, object]:
    """Audit one built ProvidedModel. Returns a dict of the three classes plus counts.

    ``pm`` is what ``config.build_provider`` returns, so the audit sees the model exactly
    as a run does: after the medium, after any closure or pinning a strain configures, and
    with the enzyme cost table that determines which reactions are free."""
    model = pm.ec.model
    costed = {e.rxn_id for e in pm.ec.table}

    free_energy, reversible_maint, pinned_uncosted, acceptor_sinks = [], [], [], []
    for r in model.reactions:
        if _is_exchange_or_biomass(r):
            continue
        is_costed = r.id in costed
        lo, hi = float(r.lower_bound), float(r.upper_bound)

        # --- class B: reversible maintenance -------------------------------------
        label = f"{r.id} {getattr(r, 'name', '') or ''}"
        if MAINTENANCE_RE.search(label) and lo < 0 < hi:
            reversible_maint.append(dict(reaction=r.id, name=getattr(r, "name", ""),
                                         lower_bound=lo, upper_bound=hi, costed=is_costed,
                                         reaction_string=r.reaction[:200]))
        # --- class C: hard-pinned uncosted drain ---------------------------------
        if not is_costed and (lo > 0 or hi < 0):
            pinned_uncosted.append(dict(reaction=r.id, name=getattr(r, "name", ""),
                                        lower_bound=lo, upper_bound=hi,
                                        fixed=bool(lo == hi),
                                        reaction_string=r.reaction[:200]))
        # --- class A: uncosted reaction that can produce a free-energy carrier ----
        if is_costed:
            continue
        # --- class D: uncosted consumer of a terminal electron acceptor ------------
        eaten = set()
        for met, coef in r.metabolites.items():
            acc = _acceptor(met)
            if acc is None:
                continue
            if (coef < 0 and hi > 0) or (coef > 0 and lo < 0):
                eaten.add(acc)
        if eaten:
            acceptor_sinks.append(dict(reaction=r.id, name=getattr(r, "name", ""),
                                       consumes="+".join(sorted(eaten)),
                                       lower_bound=lo, upper_bound=hi,
                                       has_gpr=bool(r.genes),
                                       reaction_string=r.reaction[:200]))
        produced = set()
        for met, coef in r.metabolites.items():
            c = _carrier(met)
            if c is None:
                continue
            if coef > 0 and hi > 0:
                produced.add(c)
            if coef < 0 and lo < 0:      # reversible: the reverse direction produces it
                produced.add(c)
        if produced:
            free_energy.append(dict(reaction=r.id, name=getattr(r, "name", ""),
                                    produces="+".join(sorted(produced)),
                                    lower_bound=lo, upper_bound=hi, has_gpr=bool(r.genes),
                                    reaction_string=r.reaction[:200]))

    return dict(
        model=pm.name, biomass=pm.biomass_rxn,
        n_reactions=len(model.reactions), n_costed=len(costed),
        n_uncosted=len(model.reactions) - len(costed),
        class_A_uncosted_energy_producing=free_energy[:max_report],
        class_A_count=len(free_energy),
        class_B_reversible_maintenance=reversible_maint,
        class_B_count=len(reversible_maint),
        class_C_pinned_uncosted=pinned_uncosted[:max_report],
        class_C_count=len(pinned_uncosted),
        class_D_uncosted_acceptor_sinks=acceptor_sinks[:max_report],
        class_D_count=len(acceptor_sinks),
    )
