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
    E. THE COUPLING-ION CIRCUIT -- whether the ion gradient ATP synthase runs on is actually
       supplied by the respiratory chain, or leaks in around it. Classes A-D all watch
       CHEMICAL free-energy carriers (ATP, NAD(P)H, quinol, ferredoxin) and a terminal
       acceptor. None of them watches the ION, so a model can close its proton circuit
       through free metabolite/H+ symporters and every one of those reactions passes the
       audit clean. K4 found exactly that in three Candida models -- the chain supplied
       0.02-0.03 % of the protons ATP synthase consumed -- with 44-47 class-A hits reported
       and this defect invisible. Class E is a BUDGET rather than a list: see
       :func:`audit_coupling_ion`.

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


def _search(met, pats) -> bool:
    """Match a metabolite against the patterns: its id, its NAME ON ITS OWN, and the two joined.

    The name has to be tested as its own string. Every pattern in this module is anchored at
    `^`, and the models here split into two naming conventions: BiGG and ModelSEED put the
    chemistry in the id (`atp_c`, `cpd00002_c0`) and a description in the name, while
    Yeast7-derived SBML puts an OPAQUE id (`s_0437`) beside a plain chemical name (`ATP`).
    Searching only the id and the joined `"s_0437 ATP"` sees the first convention and is blind
    to the second, because an anchored pattern cannot match a joined string from the left.

    Found in Y1 on Li et al.'s deposited ecYeast7, where it made the entire audit read clean:
    zero hits in classes A-D and no ATP synthase found at all, on a model that has one carrying
    flux. It is a defect in THIS audit, not in that model.
    """
    name = getattr(met, "name", "") or ""
    joined = f"{met.id} {name}"
    return any(p.search(met.id) or p.search(name) or p.search(joined) for p in pats)


def _acceptor(met) -> Optional[str]:
    for name, pats in _ACCEPTORS.items():
        if _search(met, pats):
            return name
    return None


def _carrier(met) -> Optional[str]:
    for carrier, pats in _COMPILED.items():
        if _search(met, pats):
            return carrier
    return None


# ---------------------------------------------------------------------------
# class E -- the coupling-ion circuit
# ---------------------------------------------------------------------------
# The ion an ATP synthase runs on is NOT always the proton: M. maripaludis' ATP synthase in
# this project is SODIUM-driven (4 Na+ per ATP). So the ion is inferred from the strain's own
# ATP synthase rather than assumed, which is why this class is named for the coupling ion.
COUPLING_ION_PATTERNS = {
    "H+":  [r"^h(_|\[|$)", r"^C00080(__|$)", r"^cpd00067(_|$)"],
    "Na+": [r"^na1?(_|\[|$)", r"^C01330(__|$)", r"^cpd00971(_|$)"],
}
_IONS = {k: [re.compile(p, re.I) for p in v] for k, v in COUPLING_ION_PATTERNS.items()}

# A reaction is REDOX-COUPLED -- i.e. part of the electron-transport chain rather than a
# metabolite carrier -- if it handles one of these alongside the ion.
REDOX_PATTERNS = [
    r"quinol", r"quinone", r"^q8", r"^mql8", r"^mqn", r"C01967", r"^M84[0-9]{2}",
    r"cytochrome", r"^focy", r"^ficy", r"C00125", r"C00126", r"C00996", r"C00999",
    r"C00997", r"C01000",
    r"^nadh(_|\[|$)", r"^nad(_|\[|$)", r"C00003", r"C00004", r"cpd00003", r"cpd00004",
    r"^nadph(_|\[|$)", r"^nadp(_|\[|$)", r"C00005", r"C00006",
    r"^fadh2", r"^fad(_|\[|$)", r"ferredoxin", r"^fdx",
    r"^o2(_|\[|$)", r"C00007", r"cpd00007", r"^oxygen$",
    r"^pq(_|\[|$)", r"plastoquin", r"^pheo", r"photosystem",
]
_REDOX = [re.compile(p, re.I) for p in REDOX_PATTERNS]
_ATP_RE = [re.compile(p, re.I) for p in (r"^atp(_|\[|$)", r"^C00002(__|$)", r"^cpd00002(_|$)")]
_WATER_RE = [re.compile(p, re.I) for p in (r"^h2o(_|\[|$)", r"^C00001(__|$)", r"^cpd00001(_|$)")]


def _matches(met, pats) -> bool:
    return _search(met, pats)


def _ion_of(met) -> Optional[str]:
    """Which coupling ion is this metabolite, if any. Chemistry first, then id/name.

    Chemistry alone is not enough: syn6803's protons carry no formula at all, so a
    formula-only test finds zero proton metabolites in a model with two ATP synthases."""
    el = getattr(met, "elements", {}) or {}
    charge = getattr(met, "charge", None)
    if el == {"H": 1} and (charge is None or float(charge) == 1.0):
        return "H+"
    if el == {"Na": 1}:
        return "Na+"
    for ion, pats in _IONS.items():
        if any(p.search(met.id) for p in pats):
            return ion
        nm = (getattr(met, "name", "") or "").strip().lower()
        if ion == "H+" and nm in ("h+", "proton", "h"):
            return "H+"
        if ion == "Na+" and nm in ("na+", "sodium", "na"):
            return "Na+"
    return None


def _is_redox(rxn) -> bool:
    if any(_matches(m_, _REDOX) for m_ in rxn.metabolites):
        return True
    ec = str(rxn.annotation.get("ec-code", "") or "")
    return bool(re.search(r"(^|[^\d])(1\.|7\.1\.)", ec))


# Methanogen and phototroph redox carriers, so "is this reaction part of the energy-conserving
# chain" is not silently a bacterial/mitochondrial question. M. maripaludis conserves energy at
# a sodium-translocating methyltransferase, which handles none of the carriers above.
REDOX_PATTERNS_EXTRA = [
    r"coenzyme[ -]?m\b", r"\bcom\b", r"cpd02246", r"cpd00126",       # CoM / CoM-S-S-CoB
    r"coenzyme[ -]?b\b", r"cpd02248",
    r"tetrahydromethanopterin", r"h4mpt", r"cpd0264[0-9]",
    r"methanophenazine", r"coenzyme[ -]?f420", r"cpd00558", r"f420",
    r"cpd11620", r"cpd11621",                                          # reduced/oxidised F420
]
_REDOX += [re.compile(p, re.I) for p in REDOX_PATTERNS_EXTRA]

_PMET_RE = re.compile(r"^pmet_", re.I)


def _gecko_groups(model):
    """Contract GECKO arm/isozyme splits into one logical reaction each.

    GECKO splits a reaction into `arm_<R>` (which carries the real metabolites) and
    `<R>No<k>` (which carries the enzyme cost), joined by a pseudo-metabolite `pmet_<R>`.
    The two halves of ATP synthase therefore live in DIFFERENT reactions -- `arm_ATPS4rpp`
    consumes 4 periplasmic protons and `ATPS4rppNo1` produces the ATP and 3 cytosolic
    protons -- so a test that wants both in one reaction finds no ATP synthase in eciML1515
    at all. Returns {representative_reaction_id: [member reactions]}.
    """
    parent = {r.id: r.id for r in model.reactions}

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for met in model.metabolites:
        if not _PMET_RE.match(met.id):
            continue
        rs = [r.id for r in met.reactions]
        for other in rs[1:]:
            union(rs[0], other)
    groups = {}
    for r in model.reactions:
        groups.setdefault(find(r.id), []).append(r)
    # Key each group by its lexicographically smallest member. Union-find's own
    # representative comes from `met.reactions`, a set of objects hashed by identity, so it
    # varies between processes: two runs of the same audit on eciML1515 label ATP synthase
    # 'ATPS4rpp_REVNo1' and 'ATPS4rpp_REVNo2'. The membership, and therefore every number, is
    # identical either way -- but a report should not change its labels when re-run.
    return {min(r.id for r in members): sorted(members, key=lambda r: r.id)
            for members in groups.values()}


def _group_ion_by_compartment(members, ion):
    """Net coefficient of `ion` per compartment, summed over a contracted group, ignoring the
    pseudo-metabolites that only exist to join the group."""
    out = {}
    for r in members:
        for m_, c in r.metabolites.items():
            if _PMET_RE.match(m_.id):
                continue
            if _ion_of(m_) == ion:
                out[m_.compartment] = out.get(m_.compartment, 0.0) + float(c)
    return {k: v for k, v in out.items() if abs(v) > 1e-12}


def _group_flux(members, fluxes):
    """One flux for a contracted group: the largest |flux| among its members. GECKO's arm and
    isozyme reactions carry the same flux by construction, so this is that flux."""
    best = 0.0
    for r in members:
        v = float(fluxes.get(r.id, 0.0) or 0.0)
        if abs(v) > abs(best):
            best = v
    return best


def find_atp_synthase(model, fluxes=None, ion_hint: Optional[str] = None):
    """The strain's ATP synthase, found by chemistry rather than by name, after contracting
    GECKO arm/isozyme splits.

    Returns (groups, ion, (inner, outer)) where `groups` maps a representative reaction id to
    its member reactions. `outer` is the compartment ATP synthase DRAWS the ion from when it
    makes ATP -- the energised side. Everything downstream is expressed as ions delivered TO
    that side.

    WHICH membrane, when a model has more than one. syn6803 has two ATP synthases, one on the
    plasma membrane and one on the thylakoid. The energising membrane is taken to be the one
    that actually carries the ATP-synthesis flux at the solved state, which is a statement
    about the model's behaviour rather than about its topology.
    """
    fluxes = {} if fluxes is None else fluxes
    groups = _gecko_groups(model)
    cands = []
    for rep, members in groups.items():
        if all(_is_exchange_or_biomass(r) for r in members):
            continue
        makes_atp = any(_matches(m_, _ATP_RE) for r in members for m_ in r.metabolites
                        if not _PMET_RE.match(m_.id))
        if not makes_atp:
            continue
        for ion in (["H+", "Na+"] if ion_hint is None else [ion_hint]):
            bycomp = _group_ion_by_compartment(members, ion)
            if len(bycomp) < 2:
                continue
            v = _group_flux(members, fluxes)
            # ATP-synthesis direction: the sign that makes ATP a product
            atp_sign = 0.0
            for r in members:
                for m_, c in r.metabolites.items():
                    if _PMET_RE.match(m_.id) or not _matches(m_, _ATP_RE):
                        continue
                    atp_sign = 1.0 if c > 0 else -1.0
                    break
                if atp_sign:
                    break
            atp_sign = atp_sign or 1.0
            drawn = {k: val * atp_sign for k, val in bycomp.items()}
            outer = min(drawn, key=lambda k: drawn[k])
            inner = max(drawn, key=lambda k: drawn[k])
            # how many ions this group actually moved, which is what ranks the candidates
            moved = abs(bycomp[outer] * v)
            cands.append(dict(rep=rep, members=members, ion=ion, inner=inner, outer=outer,
                              moved=moved, per_flux=abs(bycomp[outer])))
    if not cands:
        return {}, None, (None, None)
    # rank: the membrane that carries flux wins; with no flux anywhere, the biggest
    # stoichiometry wins, which is the ATP synthase rather than a P-type ATPase
    cands.sort(key=lambda d: (d["moved"], d["per_flux"]), reverse=True)
    top = cands[0]
    chosen = {c["rep"]: c["members"] for c in cands
              if c["ion"] == top["ion"] and c["inner"] == top["inner"]
              and c["outer"] == top["outer"]}
    return chosen, top["ion"], (top["inner"], top["outer"])


def audit_coupling_ion(pm, solution=None, tol: float = 1e-9) -> Dict[str, object]:
    """Class E: does the respiratory chain actually supply the ion gradient ATP synthase uses?

    Needs a SOLVED state, because the question is about flux and not topology: a free proton
    carrier that exists but carries nothing is not a defect. Pass ``solution``, or one is
    computed by optimising the model as configured.

    THE ION CAN ENTER THE ENERGISED COMPARTMENT TWO WAYS, and a metric that counts only one of
    them mis-reads whole organisms. It can be TRANSLOCATED across the membrane -- the
    mitochondrial and bacterial case -- or RELEASED CHEMICALLY inside that compartment, which
    is what photosynthetic water splitting and the cytochrome b6f complex do into a thylakoid
    lumen. Counting translocation alone scores Synechocystis at 19 % when its chain in fact
    supplies all of it. So the budget is reported as a full decomposition, redox against
    carrier and translocated against in-compartment, and the caller reads the cell that matters
    for the organism at hand.

    One asymmetry the caller must keep in view: in a two-compartment mitochondrial model the
    energised side is the CYTOSOL, which is also where bulk metabolism happens, so
    in-compartment production there is ordinary chemistry rather than the chain. In a thylakoid
    or a periplasm it is not. `chain_supplies_fraction` is therefore the TRANSLOCATION
    fraction, which is the quantity K4 measured and the one comparable across the mitochondrial
    strains; `chain_supplies_fraction_incl_chemistry` is the other reading.
    """
    model = pm.ec.model
    costed = {e.rxn_id for e in pm.ec.table}
    if solution is None:
        solution = model.optimize()
    fluxes = getattr(solution, "fluxes", {})

    synthases, ion, (inner, outer) = find_atp_synthase(model, fluxes=fluxes)
    if ion is None:
        return dict(ion=None, note="no ATP synthase moving a coupling ion was found; "
                                   "class E cannot be evaluated for this model")

    groups = _gecko_groups(model)
    rows = []
    for rep, members in groups.items():
        if all(_is_exchange_or_biomass(r) for r in members):
            continue
        bycomp = _group_ion_by_compartment(members, ion)
        if outer not in bycomp:
            continue
        v = _group_flux(members, fluxes)
        to_outer = bycomp[outer] * v            # >0 puts the ion into the energised side
        if abs(to_outer) <= tol:
            continue
        is_syn = rep in synthases
        translocates = len(bycomp) >= 2
        carries_other = any(
            (_ion_of(m_) is None and not _matches(m_, _WATER_RE) and not _PMET_RE.match(m_.id))
            for r in members for m_ in r.metabolites)
        rows.append(dict(
            reaction=rep, members=" ".join(sorted(r.id for r in members)),
            name=(getattr(members[0], "name", "") or "")[:90],
            costed=any(r.id in costed for r in members),
            reversible=any(r.lower_bound < 0 < r.upper_bound for r in members),
            is_atp_synthase=is_syn, translocates=translocates,
            kind=("atp_synthase" if is_syn
                  else "redox" if any(_is_redox(r) for r in members)
                  else "carrier" if carries_other else "pure_ion_transport"),
            ion_per_flux_to_outer=bycomp[outer], flux=v, ion_to_outer=to_outer,
            reaction_string=" ; ".join(r.reaction for r in members)[:300]))

    def _sum(pred):
        return sum(abs(x["ion_to_outer"]) for x in rows if pred(x))

    draw = _sum(lambda x: x["is_atp_synthase"] and x["ion_to_outer"] < -tol)
    sup = lambda k, t: _sum(                                             # noqa: E731
        lambda x: (x["kind"] == k and x["translocates"] is t
                   and x["ion_to_outer"] > tol))
    redox_tl, redox_chem = sup("redox", True), sup("redox", False)
    carrier_tl, carrier_chem = sup("carrier", True), sup("carrier", False)
    pure_tl = sup("pure_ion_transport", True)
    other_chem = _sum(lambda x: (not x["translocates"] and not x["is_atp_synthase"]
                                 and x["kind"] not in ("redox", "carrier")
                                 and x["ion_to_outer"] > tol))
    frac = (lambda n: n / draw if draw > tol else float("nan"))
    return dict(
        ion=ion, inner_compartment=inner, outer_compartment=outer,
        atp_synthase=sorted(synthases),
        growth=float(getattr(solution, "objective_value", float("nan")) or float("nan")),
        n_ion_reactions=len(rows),
        n_translocating=sum(1 for x in rows if x["translocates"]),
        n_uncosted=sum(1 for x in rows if not x["costed"]),
        n_uncosted_reversible=sum(1 for x in rows if not x["costed"] and x["reversible"]),
        atp_synthase_draw=draw,
        redox_translocated=redox_tl, redox_in_compartment=redox_chem,
        carrier_translocated=carrier_tl, carrier_in_compartment=carrier_chem,
        pure_ion_translocated=pure_tl, other_in_compartment=other_chem,
        chain_supplies_fraction=frac(redox_tl),
        chain_supplies_fraction_incl_chemistry=frac(redox_tl + redox_chem),
        carrier_supplies_fraction=frac(carrier_tl),
        reactions=sorted(rows, key=lambda x: -abs(x["ion_to_outer"])),
    )


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
