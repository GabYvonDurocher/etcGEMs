"""Model providers: turn a genome-scale model into (cobra model, cost table).

Three routes, all returning a ``ProvidedModel``:

* ``toy_ecoli_core``  -- self-contained, no downloads. e_coli_core (ships with
  cobrapy) plus synthetic MW / kcat / Topt / dCp per reaction. Use it to smoke-
  test the whole pipeline and to develop new analyses offline.

* ``from_gecko``      -- read a real GECKO enzyme-constrained model (SBML/.mat/
  .json) and extract per-reaction kcats from its protein-usage stoichiometry.
  Assigns MMRT knobs (Topt, dCp) from defaults you can override per enzyme.

* ``from_kcat_csv``   -- attach a table of kcats (e.g. DLKcat / DLTKcat output)
  to any base GEM. Columns: rxn_id, mw, kcat[, Topt, dCp, group, T0].

The GECKO and CSV routes are the ones you point at ecYeastGEM on your machine;
the toy route is what the sandbox tests run on.
"""
from __future__ import annotations

import csv
import os
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import numpy as np

from .enzyme_cost import EnzymeConstrainedModel, EnzymeCostTable, EnzymeEntry


@dataclass
class ProvidedModel:
    ec: EnzymeConstrainedModel
    T0: float                     # reference temperature (K) of the kcats
    biomass_rxn: str
    name: str
    closed_free_o2_sinks: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Model-quality correction: uncosted free-energy (O2) sink reactions
# ---------------------------------------------------------------------------
# Base reaction IDs (GECKO adds No<n> isozyme and _REV suffixes) of O2-consuming
# side reactions that carry ~zero enzyme cost and short-circuit the electron
# transport chain, creating a futile O2 cycle (Parsa's gas-flux audit: at LB/40 C,
# ~75% of gross O2 turnover was this cycle). Closing them routes O2 through the
# genuine, enzyme-costed cytochrome oxidase (CYTBO3) at ~-0.3% growth. NB: catalase
# (CATNo1) and superoxide dismutase (SPODMNo1) are REAL enzymes (kcat 1e5-1e9/s) and
# are deliberately NOT in this list. Extend per-organism as other models are audited.
FREE_O2_SINK_REACTIONS = [
    "QMO2",    # 2 O2 + ubiquinol -> 2 superoxide + ubiquinone      (ygiN / P0ADU2; ~free)
    "QMO3",    # 2 O2 + menaquinol -> 2 superoxide + menaquinone    (same enzyme; ~free)
    "MOX",     # malate + O2 -> H2O2 + oxaloacetate                 (no enzyme-cost entry)
    "CU1Opp",  # 4 Cu+ + O2 -> 4 Cu2+ + 2 H2O                       (no enzyme-cost entry)
]


def close_free_energy_sinks(model, bases: Optional[List[str]] = None) -> List[str]:
    """Close uncosted O2-sink reactions (Parsa's audit) so flux routes through the
    genuine enzyme-costed respiratory chain. Matches each base ID plus any GECKO
    ``No<n>`` isozyme / ``_REV`` suffix, and sets the forward (and reverse, if the
    reaction is reversible) bound to 0. Returns the list of closed reaction IDs.
    Reusable/auditable: pass ``bases`` to close a different set per organism. Does
    NOT touch catalase / SOD (real kcat)."""
    bases = list(bases) if bases is not None else FREE_O2_SINK_REACTIONS
    pat = re.compile(r"^(" + "|".join(re.escape(b) for b in bases) + r")(No\d+)?(_REV(No\d+)?)?$")
    closed = []
    for r in model.reactions:
        if pat.match(r.id):
            if r.upper_bound > 0.0:
                r.upper_bound = 0.0
            if r.lower_bound < 0.0:
                r.lower_bound = 0.0
            closed.append(r.id)
    return closed


# ---------------------------------------------------------------------------
# Budget calibration
# ---------------------------------------------------------------------------
def calibrate_budget(model, table: EnzymeCostTable, T0: float, biomass_rxn: str,
                     target_fraction: float = 0.6) -> float:
    """Pick a pool budget so constrained growth at T0 is ~target_fraction of the
    unconstrained optimum (guarantees the enzyme constraint actually binds).

    Bisection on the budget; cheap because each step is one LP.
    """
    with model:
        model.objective = biomass_rxn
        uncon = model.slim_optimize()
    if not uncon or uncon <= 0 or not np.isfinite(uncon):
        raise RuntimeError("Unconstrained model does not grow; check biomass reaction.")
    target = target_fraction * uncon

    # An upper bound on useful budget: cost if every enzyme ran at unit flux.
    hi = sum(e.cost(T0) for e in table) or 1.0
    lo = 0.0
    # Calibrate on a disposable copy so we don't leave a pool constraint behind.
    ecm = EnzymeConstrainedModel(model.copy(), table, default_budget=hi)
    ecm.model.objective = biomass_rxn
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        ecm.set_budget(mid)
        ecm.set_temperature(T0)
        g = ecm.model.slim_optimize()
        g = 0.0 if (g is None or not np.isfinite(g)) else g
        if g < target:
            lo = mid
        else:
            hi = mid
    return hi


# ---------------------------------------------------------------------------
# Toy provider (offline)
# ---------------------------------------------------------------------------
def toy_ecoli_core(T0: float = 303.15, seed: int = 0,
                   topt_mean_offset: float = 8.0, topt_sd: float = 6.0,
                   dCp_mean: float = -8.0, dCp_sd: float = 2.0,
                   n_groups: int = 4, target_fraction: float = 0.6) -> ProvidedModel:
    """E. coli core with synthetic enzyme kinetics. Deterministic given seed.

    Enzyme optima are drawn a little above T0 with spread ``topt_sd`` so the
    organismal TPC (which folds in the proteome budget) peaks below the mean
    enzyme Topt -- the usual empirical pattern.
    """
    from cobra.io import load_model
    rng = np.random.default_rng(seed)
    model = load_model("textbook")
    biomass = str(model.objective.expression).split()[0]  # fallback below
    biomass = _find_biomass(model)

    entries = []
    for rxn in model.reactions:
        if rxn.id.startswith("EX_") or rxn.id == biomass:
            continue
        if rxn.id in ("ATPM",):
            continue
        if not rxn.metabolites:
            continue
        mw = float(np.clip(rng.lognormal(mean=np.log(40), sigma=0.5), 10, 150))     # kDa
        kcat = float(np.clip(rng.lognormal(mean=np.log(50), sigma=1.0), 1, 800))    # 1/s
        Topt = T0 + topt_mean_offset + rng.normal(0, topt_sd)
        dCp = float(np.clip(rng.normal(dCp_mean, dCp_sd), -20, -2))
        group = f"grp{rng.integers(0, n_groups)}"
        entries.append(EnzymeEntry(rxn.id, mw, kcat, Topt, dCp, T0, group))
    table = EnzymeCostTable(entries)

    budget = calibrate_budget(model, table, T0, biomass, target_fraction)
    group_budgets = _group_budgets_from_reference(table, T0, budget)
    ec = EnzymeConstrainedModel(model, table, default_budget=budget,
                                group_budgets=group_budgets)
    ec.model.objective = biomass
    return ProvidedModel(ec=ec, T0=T0, biomass_rxn=biomass, name="toy_ecoli_core")


def _group_budgets_from_reference(table, T0, total_budget, slack=1.5):
    """Per-group sub-budgets, set generous (slack x each group's proportional
    share) so group caps only bind when a sweep tightens allocation."""
    per_group = {}
    for g, ents in table.by_group().items():
        share = sum(e.cost(T0) for e in ents)
        per_group[g] = share
    tot = sum(per_group.values()) or 1.0
    return {g: slack * total_budget * v / tot for g, v in per_group.items()}


def _find_biomass(model) -> str:
    # objective reaction name is most reliable
    for r in model.reactions:
        if r.objective_coefficient != 0:
            return r.id
    for r in model.reactions:
        if "biomass" in r.id.lower():
            return r.id
    raise RuntimeError("Could not identify biomass reaction.")


# ---------------------------------------------------------------------------
# GECKO ecModel extractor
# ---------------------------------------------------------------------------
def load_enzyme_thermal_params(path: str):
    """Read a per-enzyme thermal parameter table (MRes / Li 2021 format) indexed
    by UniProt id, with columns Topt, Tm (K), Length, T90, dCpt (J/mol/K).

    Returns a DataFrame indexed by UniProt id. The first (unnamed) column is the
    UniProt id in the MRes tables."""
    import pandas as pd
    df = pd.read_csv(path)
    idcol = df.columns[0]
    df = df.set_index(df[idcol].astype(str))
    return df


def apply_thermal_params(table, params_df, key: str = "enzyme_id",
                         use_dCpt: bool = True):
    """Set each entry's grounded Topt/Tm/T90/length/dCpt from a params table,
    joined by UniProt id. Topt/Tm are converted to K assumption already met (the
    MRes tables store K). ``use_dCpt=False`` leaves dCpt unset (the emergent model
    uses an independent literature MMRT dCp prior instead of the table's tuned
    per-enzyme values). Returns (n_matched, n_total) coverage."""
    import numpy as np
    n_matched = 0
    for e in table.entries:
        uid = getattr(e, key, None)
        if uid is None or uid not in params_df.index:
            continue
        row = params_df.loc[uid]
        if hasattr(row, "iloc") and getattr(row, "ndim", 1) > 1:
            row = row.iloc[0]   # duplicate ids -> take first
        def _get(col):
            v = row.get(col) if hasattr(row, "get") else None
            return float(v) if v is not None and np.isfinite(v) else None
        topt = _get("Topt")
        if topt is not None:
            e.Topt = topt
        e.Tm = _get("Tm")
        e.T90 = _get("T90")
        e.length = _get("Length")
        if use_dCpt:
            e.dCpt = _get("dCpt")
        n_matched += 1
    return n_matched, len(table.entries)


def from_gecko(model_path: str, T0: float = 303.15,
               default_Topt_offset: float = 7.0, default_dCp: float = -12.0,
               prot_prefix: str = "prot_", pool_id: str = "prot_pool",
               biomass_rxn: Optional[str] = None,
               target_fraction: Optional[float] = None,
               pool_scale: float = 1.0,
               thermal_model: str = "mmrt", ngam_temperature: bool = False,
               ngam_rxn: Optional[str] = None, ngam_base_scale: float = 1.0,
               enzyme_params: Optional[str] = None,
               enzyme_params_key: str = "enzyme_id",
               budget_override: Optional[float] = None,
               enzyme_params_use_dCpt: bool = True,
               dcp_prior_kJ: float = -4.0,
               close_free_o2_sinks: bool = True,
               rescale_pool_row: bool = True) -> ProvidedModel:
    """Extract an enzyme cost table from a GECKO-style ecModel.

    Handles two encodings:
      (A) 'full' GECKO: draw reactions convert `prot_pool` -> `prot_<id>` with
          coefficient = MW; metabolic reactions consume `prot_<id>` with
          coefficient = 1/kcat. We recover MW and kcat per reaction.
      (B) 'short'/sMOMENT: reactions consume `prot_pool` directly with
          coefficient MW/kcat. We keep that as base_cost (temperature scaling is
          invariant to the MW/kcat split).

    Topt/dCp are not stored in GECKO models, so we assign defaults; override them
    afterwards via the returned table (e.g. from DLTKcat predictions).
    """
    import cobra

    model = _load_any(model_path)
    # Model-quality correction (default ON): close the uncosted O2-sink reactions
    # (Parsa's audit) so O2 routes through the real respiratory chain, not a futile cycle.
    closed_sinks = []
    if close_free_o2_sinks:
        closed_sinks = close_free_energy_sinks(model)
        if closed_sinks:
            print(f"[from_gecko] closed {len(closed_sinks)} uncosted O2-sink reaction(s) "
                  f"(Parsa's audit): {closed_sinks}")
    if biomass_rxn is None:
        biomass_rxn = _find_biomass(model)

    # Auto-detect the pool metabolite id (GECKO adds a compartment suffix, e.g.
    # 'prot_pool[c]', so the bare 'prot_pool' won't match get_by_id).
    all_met_ids = {m.id for m in model.metabolites}
    if pool_id not in all_met_ids:
        cand = [i for i in all_met_ids if "prot_pool" in i or i.startswith(pool_id)]
        if cand:
            pool_id = sorted(cand, key=len)[0]
    # Enzyme pseudo-metabolites = prot_ prefix, excluding the pool itself.
    prot_mets = {m.id for m in model.metabolites
                 if m.id.startswith(prot_prefix) and m.id != pool_id}

    # MW per enzyme from draw reactions (route A: pool -> single enzyme).
    mw_of: Dict[str, float] = {}
    draw_rxns = set()
    for rxn in model.reactions:
        prods = [m for m in rxn.metabolites if m.id in prot_mets and rxn.metabolites[m] > 0]
        cons_pool = any(m.id == pool_id and rxn.metabolites[m] < 0 for m in rxn.metabolites)
        if cons_pool and len(prods) == 1:
            draw_rxns.add(rxn.id)
            enz = prods[0].id
            for m, c in rxn.metabolites.items():
                if m.id == pool_id:
                    mw_of[enz] = abs(c)   # |pool coeff| == MW (kDa)

    pool_met = model.metabolites.get_by_id(pool_id) if pool_id in all_met_ids else None
    entries = []
    for rxn in model.reactions:
        if rxn.id == biomass_rxn or rxn.id.startswith("EX_") or rxn.id in draw_rxns:
            continue
        enz_consumed = {m.id: -rxn.metabolites[m] for m in rxn.metabolites
                        if m.id in prot_mets and rxn.metabolites[m] < 0}
        pool_consumed = rxn.metabolites.get(pool_met, 0.0) if pool_met is not None else 0.0

        if enz_consumed:  # route A: coefficient == 1/kcat[1/h]
            # if a complex, use the limiting (largest coefficient == smallest kcat)
            enz_id, inv_kcat_h = max(enz_consumed.items(), key=lambda kv: kv[1])
            kcat_s = 1.0 / (inv_kcat_h * 3600.0) if inv_kcat_h > 0 else 50.0
            mw = mw_of.get(enz_id, 40.0)
            entries.append(EnzymeEntry(rxn.id, mw, kcat_s,
                                       T0 + default_Topt_offset, default_dCp, T0,
                                       group=_subsystem(rxn),
                                       enzyme_id=_clean_uniprot(enz_id, prot_prefix)))
        elif pool_consumed < 0:  # route B: base_cost = MW/kcat directly
            entries.append(EnzymeEntry(rxn.id, mw=40.0, kcat_ref=50.0,
                                       Topt=T0 + default_Topt_offset, dCp=default_dCp,
                                       T0=T0, group=_subsystem(rxn),
                                       base_cost=abs(pool_consumed)))
    if not entries:
        raise RuntimeError(
            "No enzyme-linked reactions found. Check prot_prefix/pool_id match "
            "this model's naming (inspect metabolite ids).")

    table = EnzymeCostTable(entries)
    # Budget: reuse the model's existing pool bound if present, else calibrate.
    if budget_override is not None:
        # EMERGENT magnitude: the pool budget is derived from independent data
        # (P_total x f_metab x sigma), NOT the growth-calibrated GECKO bound.
        budget = float(budget_override)
    else:
        budget = _existing_pool_bound(model, pool_id)
        if budget is None:
            if target_fraction is None:
                target_fraction = 0.6
            budget = calibrate_budget(model, table, T0, biomass_rxn, target_fraction)
        # DEPRECATED knob: pool_scale<1 tuned the pool to make peak growth respond.
        # For the emergent model pool_scale=1.0 (nothing tuned to the growth curve).
        budget *= pool_scale
    group_budgets = _group_budgets_from_reference(table, T0, budget)

    # Unfolding mode: overlay grounded per-enzyme Topt/Tm/dCpt/length before the
    # model precomputes its unfolding thermodynamics; report coverage.
    if thermal_model == "unfolding" and enzyme_params:
        params_df = load_enzyme_thermal_params(enzyme_params)
        n_match, n_tot = apply_thermal_params(table, params_df, key=enzyme_params_key,
                                              use_dCpt=enzyme_params_use_dCpt)
        print(f"[from_gecko] unfolding mode: matched grounded Topt/Tm for "
              f"{n_match}/{n_tot} enzymes ({100*n_match/max(1,n_tot):.1f}%); "
              f"the rest use dataset-mean fallbacks")

    ec = EnzymeConstrainedModel(model, table, default_budget=budget,
                                group_budgets=group_budgets,
                                thermal_model=thermal_model,
                                ngam_temperature=ngam_temperature, ngam_rxn=ngam_rxn,
                                ngam_base_scale=ngam_base_scale,
                                unfold_means={"dCpt": dcp_prior_kJ * 1000.0},
                                rescale_pool_row=rescale_pool_row)
    ec.model.objective = biomass_rxn
    # P1c: reconcile the two redundant enzyme-mass pools into ONE proteome budget.
    # The etcgem sMOMENT/sector pool (P_total x f_metab x sigma, medium- & growth-law-
    # aware, scaled by kcat_scale) is the sole proteome accounting; relax the leftover
    # GECKO base pool supply (prot_pool_exchange) so it can no longer cap growth
    # independently (the magnitude levers kcat_scale/sigma/P_total do not touch it).
    _relax_base_protein_pool(ec.model, pool_id)
    return ProvidedModel(ec=ec, T0=T0, biomass_rxn=biomass_rxn,
                         name=f"gecko:{model.id}", closed_free_o2_sinks=closed_sinks)


# A GEM-compatible LB (rich) medium: amino acids, nucleosides/bases, vitamins,
# ions and glucose. Component EX_ ids from the MResProject data/media.csv definition
# (reused; consistent with the Machado et al. 2018 LB composition).
_CARBON_BASES = ["glc__D", "ac", "glyc", "succ", "lac__D", "lac__L", "xyl__D",
                 "gal", "fru", "man", "malt", "sucr", "pyr", "etoh", "cit"]
LB_COMPONENTS = [
    "adn", "ala__L", "amp", "arg__L", "aso3", "asp__L", "ca2", "cbl1", "cd2", "cl",
    "cmp", "cobalt2", "cro4", "cu2", "cys__L", "dad_2", "dcyt", "fe2", "fe3", "fol",
    "glc__D", "glu__L", "gly", "gmp", "gsn", "h2o", "h2s", "h", "hg2", "his__L",
    "hxan", "ile__L", "ins", "k", "leu__L", "lipoate", "lys__L", "met__L", "mg2",
    "mn2", "mobd", "na1", "nac", "nh4", "ni2", "o2", "phe__L", "pheme", "pi",
    "pnto__R", "pro__L", "pydx", "ribflv", "ser__L", "so4", "thm", "thr__L",
    "thymd", "trp__L", "tyr__L", "ump", "ura", "uri", "val__L", "zn2"]


def apply_exchange_medium(model, csv_path: str, open_lb: float = -1000.0,
                          fit_lb: float = -10.0, aa_pool_lb: float = -3.0):
    """Apply a medium given as an exchange-reaction table to a PLAIN (unsplit) GEM.

    The GECKO/sMOMENT ``set_medium`` above works on split ``EX_<met>_e_REV`` uptake
    reactions; a plain SBML GEM has signed exchanges instead, so availability is set
    by the exchange lower bound. This is the Candida route and applies the medium
    exactly as the standalone does (Candidas ``gem/18_build_etcgem_tpc.py``
    ``setup_pool``):

    1. close every exchange (``EX_*`` / ``Drain*`` / cobra boundary) to uptake
       (``lower_bound = 0``), so nothing is available that the medium does not list;
    2. ``setting=OPEN``    -> lower_bound = -1000  (non-limiting availability)
       ``setting=FIT``     -> lower_bound = -10    (the carbon source's fitted scale)
       ``setting=AA_POOL`` -> lower_bound = -3     (the pooled amino-acid budget)
    Rows whose ``exchange_id`` is not an exchange in this model are ignored (the
    medium file records the ones absent from a given reconstruction).

    Returns (n_opened, n_missing)."""
    import pandas as pd
    med = pd.read_csv(csv_path)
    EX = {r.id for r in model.reactions
          if r.id.startswith(("EX_", "Drain")) or r.boundary}
    for r in model.reactions:
        if r.id in EX:
            r.lower_bound = 0.0
    opened = missing = 0
    for _, row in med.iterrows():
        rid = str(row["exchange_id"])
        if rid not in EX:
            missing += 1
            continue
        setting = str(row.get("setting", "")).strip()
        if setting == "OPEN":
            model.reactions.get_by_id(rid).lower_bound = open_lb
        elif setting == "FIT":
            model.reactions.get_by_id(rid).lower_bound = fit_lb
        elif setting == "AA_POOL":
            model.reactions.get_by_id(rid).lower_bound = aa_pool_lb
        else:
            continue
        opened += 1
    model.solver.update()
    return opened, missing


def pin_reactions_at_ub(model, rxn_ids):
    """Fix each listed reaction at |upper_bound| in both directions.

    The Candida route's maintenance fix: *C. parapsilosis*' iDC1003 leaves its ATP
    maintenance reaction reversible (bounds -3.9, 3.9), so the LP may run it BACKWARDS
    and generate free ATP. Pinning it at its own upper bound makes maintenance an
    obligate, fixed drain -- the standalone applies this in
    ``gem/22_thermal_sensitivity.py`` (and the later audits) but NOT in
    ``gem/18_build_etcgem_tpc.py``, so it is opt-in here and OFF in the strain
    defaults, which reproduce 18. Returns the list of (id, value) actually pinned."""
    done = []
    for rid in (rxn_ids or []):
        if rid in model.reactions:
            r = model.reactions.get_by_id(rid)
            v = abs(r.upper_bound)
            r.bounds = (v, v)
            done.append((rid, v))
    if done:
        model.solver.update()
    return done


def set_medium(pm, medium="glucose_minimal", carbon="glc__D", aerobic=True,
               uptake_ub=1000.0, lb_media_csv=None, bhi_media_csv=None):
    """Set the growth medium as AVAILABILITY, not pinned uptake rates: open the
    `EX_<met>_e_REV` uptakes for the medium's components and close other carbon
    sources; the enzyme-constrained model then determines actual uptake.

    medium="glucose_minimal" (default): a single carbon source (+ O2 if aerobic)
    on top of the model's minimal-salt defaults. medium="LB"/"BHI": a rich medium
    opening the amino-acid / nucleoside / vitamin / ion component uptakes
    (:data:`LB_COMPONENTS`, or the given ``lb_media_csv`` / ``bhi_media_csv``).
    BHI is not encoded in silico in the literature (even the Rothia GEM used
    LB/TSB as defined rich stand-ins), so it is approximated by a curated rich
    component list and mapped to the LB medium-matched sector allocation.
    Returns (n_opened, n_missing)."""
    model = pm.ec.model if hasattr(pm, "ec") else pm
    # switch the medium-matched sector allocation, if wired. BHI has no measured
    # proteome (DeyuWang is LB/Glucose/Glycerol), so it uses the LB (rich) curve.
    sector_medium = "LB" if medium == "BHI" else medium
    alloc = getattr(getattr(pm, "ec", None), "_alloc_from_data", None)
    if alloc is not None and hasattr(alloc, "set_active_medium"):
        alloc.set_active_medium(sector_medium)
    if medium in ("LB", "BHI"):
        comps = LB_COMPONENTS
        csv = bhi_media_csv if medium == "BHI" else lb_media_csv
        if csv:
            import pandas as pd
            df = pd.read_csv(csv)
            comps = [str(n)[3:-2] for n in df["Name"] if str(n).startswith("EX_")]
        # close non-medium carbon sources, then open every component uptake present
        rich_set = set(comps)
        for base in _CARBON_BASES:
            rev = f"EX_{base}_e_REV"
            if rev in model.reactions and base not in rich_set:
                model.reactions.get_by_id(rev).upper_bound = 0.0
        opened, missing = 0, 0
        for base in comps:
            rev = f"EX_{base}_e_REV"
            if rev in model.reactions:
                model.reactions.get_by_id(rev).upper_bound = uptake_ub
                opened += 1
            else:
                missing += 1
        model.solver.update()
        return opened, missing
    # glucose_minimal (single carbon source)
    for base in _CARBON_BASES:
        rev = f"EX_{base}_e_REV"
        if rev in model.reactions:
            model.reactions.get_by_id(rev).upper_bound = uptake_ub if base == carbon else 0.0
    o2 = "EX_o2_e_REV"
    if o2 in model.reactions:
        model.reactions.get_by_id(o2).upper_bound = uptake_ub if aerobic else 0.0
    model.solver.update()
    return 1 + int(aerobic), 0


def set_medium_recipe(pm, recipe_csv, clearance_L_per_gDW_h: Optional[float],
                      uptake_ub: float = 1000.0, aerobic: bool = True,
                      o2_rxn: str = "EX_o2_e_REV", verbose: bool = True):
    """Set a DEFINED medium from a recipe of per-component concentrations.

    A rich medium given as an open/closed component list says which substrates exist but not
    how much of each, so a dilute defined medium looks as rich as LB. A recipe fixes that with
    one physical scale factor -- a volumetric clearance:

        ub_i [mmol gDW^-1 h^-1]  =  clearance [L gDW^-1 h^-1] * C_i [mM]

    applied to every CARBON-bearing component; non-carbon components (salts, trace minerals)
    and O2 keep the generous ``uptake_ub``, since they are not the limiting resource. Carbon
    sources absent from the recipe are closed.

    ``recipe_csv`` has columns ``base`` (the exchange metabolite base id, e.g. ``glc__D``) and
    ``conc_mM``; ``#`` comment lines carry the provenance. Generic: the recipe, the clearance
    and the citation live with the strain, not here.
    Returns (n_opened, n_missing).
    """
    import pandas as pd
    model = pm.ec.model if hasattr(pm, "ec") else pm
    df = pd.read_csv(recipe_csv, comment="#")
    for col in ("base", "conc_mM"):
        if col not in df.columns:
            raise ValueError(f"medium recipe {recipe_csv} needs a '{col}' column")
    conc = {str(b): float(c) for b, c in zip(df["base"], df["conc_mM"])}
    comps = set(conc)
    # close every carbon source the recipe does not list
    for base in _CARBON_BASES:
        rev = f"EX_{base}_e_REV"
        if rev in model.reactions and base not in comps:
            model.reactions.get_by_id(rev).upper_bound = 0.0
    opened, missing, carbon = 0, 0, 0
    for base, c in conc.items():
        rev = f"EX_{base}_e_REV"
        if rev not in model.reactions:
            missing += 1
            continue
        r = model.reactions.get_by_id(rev)
        mets = list(r.metabolites)
        is_c = bool(mets) and any(mm.elements.get("C", 0) > 0 for mm in mets)
        if clearance_L_per_gDW_h is None:
            # BLANKET mode: the medium says which components exist but not how much of each.
            # Kept because it is what Parsa's committed gas-flux CSVs were produced with,
            # before he introduced the recipe-proportional ceilings (P1 gate, DECISIONS D5).
            is_c = False
        if is_c and np.isfinite(c) and c > 0:
            r.upper_bound = float(clearance_L_per_gDW_h) * c
            carbon += 1
        else:
            r.upper_bound = float(uptake_ub)
        opened += 1
    if o2_rxn in model.reactions:
        model.reactions.get_by_id(o2_rxn).upper_bound = float(uptake_ub) if aerobic else 0.0
    model.solver.update()
    if verbose and clearance_L_per_gDW_h is None:
        print(f"[medium] recipe {os.path.basename(str(recipe_csv))} in BLANKET mode: "
              f"{opened} components open at ub={uptake_ub:g} (no per-component ceilings), "
              f"{missing} not in the model")
    elif verbose:
        total_c = sum(clearance_L_per_gDW_h * conc[b] *
                      max([mm.elements.get("C", 0)
                           for mm in model.reactions.get_by_id(f"EX_{b}_e_REV").metabolites]
                          or [0])
                      for b in conc if f"EX_{b}_e_REV" in model.reactions
                      and np.isfinite(conc[b]))
        print(f"[medium] recipe {os.path.basename(str(recipe_csv))}: {opened} components open "
              f"({carbon} carbon-limited at clearance {clearance_L_per_gDW_h:g} L/gDW/h "
              f"-> {total_c:.0f} mmol C/gDW/h ceiling), {missing} not in the model")
    return opened, missing


def _existing_pool_bound(model, pool_id):
    for rxn in model.reactions:
        # the pool exchange/supply reaction produces prot_pool
        prod = [m for m in rxn.metabolites if m.id == pool_id and rxn.metabolites[m] > 0]
        if prod and rxn.upper_bound < 1e6:
            return float(rxn.upper_bound)
    return None


def _relax_base_protein_pool(model, pool_id, big=1e6):
    """Relax the GECKO base protein-pool supply reaction (which produces the pool
    metabolite with a finite upper bound) so it no longer independently caps growth.
    The etcgem sMOMENT/sector pool becomes the sole enzyme-mass constraint. Returns
    the original bound that was relaxed (or None)."""
    for rxn in model.reactions:
        prod = [m for m in rxn.metabolites if m.id == pool_id and rxn.metabolites[m] > 0]
        if prod and rxn.upper_bound < 1e6:
            old = float(rxn.upper_bound)
            rxn.upper_bound = float(big)
            model.solver.update()
            print(f"[from_gecko] reconciled proteome pools: relaxed base pool supply "
                  f"'{rxn.id}' ({old:.4g} -> inf); the etcgem sMOMENT/sector pool is now "
                  f"the sole enzyme-mass budget.")
            return old
    return None


def _subsystem(rxn) -> str:
    s = getattr(rxn, "subsystem", None)
    return s if s else "default"


def _clean_uniprot(prot_met_id: str, prot_prefix: str) -> str:
    """'prot_P0A8F4[c]' -> 'P0A8F4'."""
    s = prot_met_id
    if s.startswith(prot_prefix):
        s = s[len(prot_prefix):]
    return s.split("[")[0].strip()


# ---------------------------------------------------------------------------
# CSV kcat loader (DLKcat / DLTKcat)
# ---------------------------------------------------------------------------
def from_kcat_csv(model_path: str, csv_path: str, T0: float = 303.15,
                  default_Topt_offset: float = 8.0, default_dCp: float = -8.0,
                  biomass_rxn: Optional[str] = None,
                  target_fraction: float = 0.6) -> ProvidedModel:
    """Attach a kcat table to a plain GEM.

    CSV columns (header required): rxn_id, mw, kcat  and optionally
    Topt, dCp, group, T0. Missing optional columns fall back to defaults.
    """
    model = _load_any(model_path)
    if biomass_rxn is None:
        biomass_rxn = _find_biomass(model)
    entries = []
    with open(csv_path, newline="") as fh:
        for row in csv.DictReader(fh):
            rid = row["rxn_id"].strip()
            if rid not in model.reactions:
                continue
            t0 = float(row.get("T0") or T0)
            entries.append(EnzymeEntry(
                rxn_id=rid,
                mw=float(row.get("mw") or 40.0),
                kcat_ref=float(row["kcat"]),
                Topt=float(row.get("Topt") or (t0 + default_Topt_offset)),
                dCp=float(row.get("dCp") or default_dCp),
                T0=t0,
                group=(row.get("group") or "default").strip() or "default",
            ))
    if not entries:
        raise RuntimeError("No CSV rows matched reactions in the model.")
    table = EnzymeCostTable(entries)
    budget = calibrate_budget(model, table, T0, biomass_rxn, target_fraction)
    group_budgets = _group_budgets_from_reference(table, T0, budget)
    ec = EnzymeConstrainedModel(model, table, default_budget=budget,
                                group_budgets=group_budgets)
    ec.model.objective = biomass_rxn
    return ProvidedModel(ec=ec, T0=T0, biomass_rxn=biomass_rxn,
                         name=f"csv:{model.id}")


def from_gem_smoment(model_path: str, kcat_csv: str, T0: float = 310.15,
                     budget_override: Optional[float] = None,
                     target_fraction: float = 0.6,
                     biomass_rxn: Optional[str] = None,
                     default_kcat: float = 25.0, default_mw: float = 40.0,
                     close_free_sinks: Optional[List[str]] = None,
                     relax_pinned: Optional[List[str]] = None,
                     thermal_model: str = "mmrt",
                     enzyme_params: Optional[str] = None,
                     enzyme_params_key: str = "rxn_id",
                     ngam_temperature: bool = False, ngam_rxn: Optional[str] = None,
                     ngam_base_scale: float = 1.0,
                     dcp_prior_kJ: float = -4.0,
                     medium_csv: Optional[str] = None,
                     pin_at_ub: Optional[List[str]] = None,
                     pheno_sigma: float = 10.0,
                     pheno_w: float = 5.0,
                     topt_tm_min_gap: Optional[float] = None,
                     rescale_pool_row: bool = True) -> ProvidedModel:
    """Attach a temperature-INDEPENDENT sMOMENT total-protein pool to a plain GEM.

    This is the methanogen route: the base GEM (iMR539_curated) carries no GECKO
    protein layer, so we build the enzyme cost table from an external
    (rxn_id, mw_kDa, kcat_s[, group, source]) CSV -- one entry per enzymatic
    reaction, costing ``MW/(kcat*3600)`` g protein per unit flux from a shared pool
    (enzyme_cost.EnzymeConstrainedModel). Reactions absent from the CSV (no GPR:
    transport/spontaneous) carry no cost (free), exactly as in a GECKO ecModel.

    Temperature-independent by construction: every entry's Topt is pinned to T0, so
    the peak-normalised MMRT shape is flat (cost == base_cost at the reference T).
    The thermal layer (M3) overrides Topt/Tm/dCp per enzyme to introduce kcat(T).

    ``budget_override`` sets the grounded proteome pool P_total*f_metab*sigma
    (emergent: NOT calibrated to growth). If None, ``calibrate_budget`` is used as a
    fallback so the pool at least binds. ``close_free_sinks`` optionally closes
    listed (uncosted) energy side-reactions before building (the methanogen analogue
    of the E. coli O2-sink fix); returns them on the ProvidedModel.

    ``medium_csv`` (Candida route) applies an exchange-table medium to the plain GEM
    before the pool is built (see ``apply_exchange_medium``); the methanogen's medium
    is baked into its curated SBML, so it leaves this None. ``pin_at_ub`` fixes listed
    reactions at their own upper bound (the parapsilosis maintenance fix).
    ``pheno_sigma``/``pheno_w`` are the two global shape parameters of the
    ``phenomenological`` thermal form; they are inert under ``mmrt``/``unfolding``.
    ``topt_tm_min_gap`` (K) is the unfolding form's admissibility floor on Tm - Topt; see
    ``EnzymeConstrainedModel._build_unfolding``. None (default) leaves it off.
    ``rescale_pool_row`` divides the pool row and its bound by the same constant -- a
    mathematically identical, better-conditioned LP. Default True since N2; the one
    configuration that switches it off is K1's gate, whose job is to reproduce the standalone
    including its solver's error. See ``EnzymeConstrainedModel.set_temperature``."""
    model = _load_any(model_path)
    if biomass_rxn is None:
        biomass_rxn = _find_biomass(model)
    closed_sinks: List[str] = []
    if medium_csv:
        n_open, n_missing = apply_exchange_medium(model, medium_csv)
        print(f"[smoment_gem] medium {os.path.basename(medium_csv)}: opened {n_open} "
              f"exchange(s); {n_missing} listed component(s) absent from this model")
    for rid, val in pin_reactions_at_ub(model, pin_at_ub):
        print(f"[smoment_gem] pinned {rid} at {val:.4g} (obligate maintenance drain)")
    if close_free_sinks:
        closed_sinks = close_free_energy_sinks(model, bases=close_free_sinks)
        if closed_sinks:
            print(f"[smoment_gem] closed {len(closed_sinks)} uncosted energy side-reaction(s): {closed_sinks}")
    # Enzyme-cost artefact audit (PART D): relax any hard-PINNED, uncosted ATP/maintenance
    # drain (e.g. iMR539's rxn00062 protein-secreting ATPase, fixed at 5.12 mmol/gDW/h) to a
    # 0-floor. A *fixed* uncosted ATP sink dominates the enzyme-limited energy budget and is
    # non-physiological in the base ecModel; measured maintenance NGAM(T) is the M3 layer.
    # Documented + reversible (reaction kept, only its forced lower bound is released).
    for rid in (relax_pinned or []):
        if rid in model.reactions:
            r = model.reactions.get_by_id(rid)
            if r.lower_bound > 0.0:
                print(f"[smoment_gem] relaxed pinned uncosted reaction {rid} "
                      f"(lb {r.lower_bound:.4g} -> 0; ub {r.upper_bound:.4g} -> 1000); "
                      f"maintenance is the M3 NGAM(T) layer.")
                r.lower_bound = 0.0
                r.upper_bound = max(r.upper_bound, 1000.0)  # headroom for the NGAM(T) lower bound
                closed_sinks.append(f"{rid}(lb->0)")
    entries = []
    with open(kcat_csv, newline="") as fh:
        for row in csv.DictReader(fh):
            rid = (row.get("rxn_id") or "").strip()
            if rid not in model.reactions:
                continue
            mw = float(row.get("mw_kDa") or row.get("mw") or default_mw)
            kcat = float(row.get("kcat_s") or row.get("kcat") or default_kcat)
            if kcat <= 0:
                kcat = default_kcat
            entries.append(EnzymeEntry(
                rxn_id=rid, mw=mw, kcat_ref=kcat,
                Topt=T0, dCp=-4.0, T0=T0,          # Topt=T0 -> flat (temperature-independent)
                group=(row.get("group") or _subsystem(model.reactions.get_by_id(rid))),
                enzyme_id=(row.get("enzyme_id") or row.get("enz") or None),
            ))
    if not entries:
        raise RuntimeError("No kcat CSV rows matched reactions in the GEM.")
    table = EnzymeCostTable(entries)
    if budget_override is not None:
        budget = float(budget_override)
    else:
        budget = calibrate_budget(model, table, T0, biomass_rxn, target_fraction)
    # M3 thermal envelope: overlay grounded per-enzyme Topt/Tm/length/dCpt (unfolding mode)
    # before the model precomputes its two-state thermodynamics. Keyed by rxn_id (each
    # methanogen reaction has one representative UniProt); report coverage.
    if thermal_model in ("unfolding", "phenomenological") and enzyme_params:
        params_df = load_enzyme_thermal_params(enzyme_params)
        n_match, n_tot = apply_thermal_params(table, params_df, key=enzyme_params_key)
        print(f"[smoment_gem] {thermal_model}: matched grounded Topt/Tm for "
              f"{n_match}/{n_tot} enzymes ({100*n_match/max(1,n_tot):.0f}%); rest at dataset means")
    # Single total-protein pool only (no allocation sub-budgets -- that is the sector layer;
    # group labels are kept on the entries for diagnostics).
    ec = EnzymeConstrainedModel(model, table, default_budget=budget,
                                thermal_model=thermal_model,
                                ngam_temperature=ngam_temperature, ngam_rxn=ngam_rxn,
                                ngam_base_scale=ngam_base_scale,
                                unfold_means={"dCpt": dcp_prior_kJ * 1000.0},
                                pheno_sigma=pheno_sigma, pheno_w=pheno_w,
                                topt_tm_min_gap=topt_tm_min_gap,
                                rescale_pool_row=rescale_pool_row)
    ec.model.objective = biomass_rxn
    return ProvidedModel(ec=ec, T0=T0, biomass_rxn=biomass_rxn,
                         name=f"smoment_gem:{model.id}", closed_free_o2_sinks=closed_sinks)


def _read_sbml_safe(path: str):
    """Read an SBML model, sanitising COBRA id-encodings that break the LP
    backend. GECKO SBML encodes spaces as ``__32__`` which cobra decodes to a
    literal space in the id (e.g. 'protein pseudoreaction'); optlang/GLPK reject
    whitespace in variable names. We decode normally then replace spaces."""
    import cobra
    from cobra.io.sbml import F_REPLACE, F_REACTION, F_SPECIE, F_GENE
    base = dict(F_REPLACE)
    _wrap = lambda f: (lambda s: f(s).replace(" ", "_"))
    fr = dict(base)
    for key in (F_REACTION, F_SPECIE, F_GENE):
        if key in fr:
            fr[key] = _wrap(base[key])
    return cobra.io.read_sbml_model(path, f_replace=fr)


def _load_any(path: str):
    import cobra
    p = path.lower()
    if p.endswith((".xml", ".sbml", ".xml.gz")):
        return _read_sbml_safe(path)
    if p.endswith(".json"):
        return cobra.io.load_json_model(path)
    if p.endswith(".mat"):
        return cobra.io.load_matlab_model(path)
    if p.endswith(".yml") or p.endswith(".yaml"):
        return cobra.io.load_yaml_model(path)
    raise ValueError(f"Unsupported model format: {path}")
