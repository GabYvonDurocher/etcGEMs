"""Gas-exchange read-out: exchange-flux TPCs and the constraints that make them determinate.

Ported from Parsa's ``gasflux.py`` (P1) and made organism-independent: nothing here names a
reaction, a footprint or a measured value. Every identifier and number comes from the caller,
which in practice means ``strains/<name>/strain.yaml`` and a ``configs/experiments/`` overlay.

An enzyme-constrained TPC fixes the growth rate but not, on its own, the internal flux
distribution, so O2 and CO2 exchange are under-determined. Three ways to pin them are provided,
each opt-in and off by default:

* **transport costing** (:func:`add_transport_costs`) -- give the uncosted inner-membrane
  carriers the same MMRT/unfolding envelope every metabolic enzyme has, so uptake acquires a
  temperature-dependent ceiling.
* **a total-carbon cap** (:func:`add_total_carbon_constraint`) -- ``sum_i nC_i * v_uptake_i <=
  c_max``, a medium-independent carbon budget.
* **an empirical overflow line** (:func:`add_acetate_line`) -- a threshold-linear floor on net
  overflow-product excretion as a function of growth rate.

A fourth, mechanistic, route lives in :mod:`etcgem.etc_area` (the ETC membrane-area budget).

NOT here, deliberately: closing uncosted O2-sink reactions. The provider does that by default
(``close_free_o2_sinks`` in ``configs/defaults.yaml``, commit 8085036, from Parsa's own audit),
and a second mechanism doing the same job at a different point in the build is exactly how two
implementations drift apart. If a run needs the sinks OPEN, set ``close_free_o2_sinks: false``.
"""
from __future__ import annotations

from typing import Optional, Sequence

import numpy as np
import pandas as pd

from .enzyme_cost import Perturbation
from .tpc import apply_state


# ---------------------------------------------------------------------------
# exchange-flux TPC
# ---------------------------------------------------------------------------
def _flux(m, rid):
    return float(m.reactions.get_by_id(rid).flux) if rid in m.reactions else 0.0


TIEBREAKS = ("none", "pfba", "min_o2", "max_o2")


def _tiebroken_solve(m, g, tiebreak, growth_tol, o2_fwd="EX_o2_e", o2_rev="EX_o2_e_REV"):
    """(P10) Re-solve with growth held at its optimum and a second objective, so the exchange
    fluxes read off the vertex are a FUNCTION of the model and not of the solver's path:
    ``pfba`` minimises total absolute flux (cobra's add_pfba); ``min_o2`` / ``max_o2`` minimise /
    maximise the net O2 uptake (the ends of the face; for reporting). Runs inside a cobra
    context so the objective and the added constraint are reverted afterwards. Returns the
    solver status; the fluxes are read by the caller while the context is open, so it is the
    caller that opens it -- see flux_tpc."""
    from optlang.symbolics import Zero
    fix = m.problem.Constraint(m.objective.expression, lb=float(g) * (1.0 - growth_tol), name="_etcgem_fix_growth")
    m.add_cons_vars([fix])

    if tiebreak == "pfba":
        # cobra's add_pfba re-optimises growth and pins it at EXACTLY the re-solved optimum
        # (fraction 1.0, no tolerance); on the LB models that second pin is numerically fragile
        # and whether it solves depends on the basis -- which is the state-dependence a
        # tie-break exists to remove. So the parsimonious objective is built here directly:
        # minimise the sum of every reaction's forward and reverse variable (all >= 0 in
        # cobra's split formulation), with growth held by the tolerance constraint above.
        m.objective = m.problem.Objective(Zero, direction="min")
        m.objective.set_linear_coefficients({v: 1.0 for r in m.reactions for v in (r.forward_variable, r.reverse_variable)})
    else:
        rev = m.reactions.get_by_id(o2_rev).flux_expression if o2_rev in m.reactions else 0
        fwd = m.reactions.get_by_id(o2_fwd).flux_expression if o2_fwd in m.reactions else 0
        m.objective = m.problem.Objective(rev - fwd, direction="min" if tiebreak == "min_o2" else "max")
    m.slim_optimize()
    return str(m.solver.status)


def flux_tpc(pm, temps_C: Sequence[float], pert: Optional[Perturbation] = None,
             metabolites: Sequence[str] = ("o2", "co2"),
             exchange_fmt: str = "EX_{met}_e",
             min_growth: float = 1e-6,
             tiebreak: str = "none", growth_tol: float = 1e-6, tiebreak_tol: float = 1e-9) -> pd.DataFrame:
    """Growth **and exchange fluxes** vs temperature.

    Identical model states to :func:`etcgem.tpc.compute_tpc` -- both call
    :func:`etcgem.tpc.apply_state` -- but the LP solution is kept, so exchange fluxes can be
    read off. ``metabolites`` are base metabolite ids (``o2``, ``co2``, ``ac`` ...); the
    forward/reverse exchange pair is found with ``exchange_fmt`` and its ``_REV`` partner, the
    GECKO convention. Returns one row per temperature with ``<met>_uptake`` and
    ``<met>_release`` (uptake positive), plus the solver status.

    ``tiebreak`` (P10, default ``"none"`` = the single growth-objective solve every earlier run
    used): ``"pfba"`` re-solves with growth held at its optimum (to ``growth_tol``, relative) and
    total absolute flux minimised, and reads the exchange fluxes off THAT vertex, so O2 at the
    optimum is a function of the model rather than of the solver's path; ``"min_o2"`` /
    ``"max_o2"`` give the two ends of the face instead (reporting only).
    """
    if tiebreak not in TIEBREAKS:
        raise ValueError(f"tiebreak must be one of {TIEBREAKS}, got {tiebreak!r}")
    # With a tie-break on, EVERY solve in this call (the growth solve and the tie-break solve)
    # runs at ``tiebreak_tol`` optimality/feasibility tolerance, restored on exit. Measured
    # (P10 TASK 1): on the LB models the parsimonious optimum is nearly flat in the O2
    # direction, and at Gurobi's default 1e-7 vertices within tolerance differ two- to
    # four-fold in O2 depending on the basis history; tightening the tie-break solve alone is
    # not enough, because the growth optimum it pins is then itself tolerance-level
    # history-dependent. At 1e-9 for both, the E-configuration cells reproduce to 0.0000.
    _restored = {}
    if tiebreak != "none":
        try:
            gp = pm.ec.model.solver.problem
            for name in ("OptimalityTol", "FeasibilityTol"):
                _restored[name] = gp.getParamInfo(name)[2]
                gp.setParam(name, float(tiebreak_tol))
        except Exception:
            _restored = {}
    try:
        return _flux_tpc_body(pm, temps_C, pert, metabolites, exchange_fmt, min_growth, tiebreak, growth_tol)
    finally:
        try:
            for name, val in _restored.items():
                pm.ec.model.solver.problem.setParam(name, val)
        except Exception:
            pass


def _flux_tpc_body(pm, temps_C, pert, metabolites, exchange_fmt, min_growth, tiebreak, growth_tol):
    pert = pert or Perturbation()
    ecm = pm.ec
    m = ecm.model
    temps_C = np.asarray(temps_C, dtype=float)
    rows = []
    for Tc in temps_C:
        apply_state(ecm, float(Tc), pert)
        g = m.slim_optimize()
        feasible = (str(m.solver.status) == "optimal") and (g is not None) and np.isfinite(g)
        row = {"temp_C": float(Tc),
               "growth": float(g) if (feasible and g >= min_growth) else 0.0,
               "status": str(m.solver.status)}
        if feasible and tiebreak != "none" and g >= min_growth:
            with m:
                st2 = _tiebroken_solve(m, g, tiebreak, growth_tol)
                row["tiebreak_status"] = st2
                ok = st2 == "optimal"
                for met in metabolites:
                    fwd = exchange_fmt.format(met=met)
                    up = (_flux(m, f"{fwd}_REV") - _flux(m, fwd)) if ok else np.nan
                    row[f"{met}_uptake"] = up
                    row[f"{met}_release"] = -up
            rows.append(row)
            continue
        for met in metabolites:
            fwd = exchange_fmt.format(met=met)
            if feasible:
                up = _flux(m, f"{fwd}_REV") - _flux(m, fwd)
                row[f"{met}_uptake"] = up
                row[f"{met}_release"] = -up
            else:
                row[f"{met}_uptake"] = np.nan
                row[f"{met}_release"] = np.nan
        rows.append(row)
    return pd.DataFrame(rows)


def respiratory_quotient(df, o2_col="o2_uptake", co2_col="co2_release"):
    """RQ = CO2 released / O2 consumed, NaN where O2 uptake is ~0."""
    o2 = df[o2_col].to_numpy(float)
    co2 = df[co2_col].to_numpy(float)
    with np.errstate(divide="ignore", invalid="ignore"):
        rq = np.where(np.abs(o2) > 1e-9, co2 / o2, np.nan)
    return pd.Series(rq, index=df.index, name="RQ")


def per_cell(flux_mmol_gdw_h, gdw_per_cell: float):
    """Convert mmol gDW^-1 h^-1 to fmol cell^-1 h^-1 given the strain's gDW per cell."""
    return np.asarray(flux_mmol_gdw_h, float) * float(gdw_per_cell) * 1e12


# ---------------------------------------------------------------------------
# (1) total-carbon uptake cap
# ---------------------------------------------------------------------------
def add_total_carbon_constraint(pm, c_max: float, exclude=("co2", "hco3"),
                                name: str = "total_carbon_uptake"):
    """``sum_i (nC_i * v_uptake_i) <= c_max`` over every OPEN carbon uptake.

    Carbon counts come from the model's own metabolite formulae, so this is medium- and
    organism-independent: it constrains whatever carbon sources the current medium leaves open.
    ``exclude`` names inorganic-carbon bases that should not be charged to the budget.
    Returns the constraint (with ``_n_carbon_sources`` attached) or None if nothing matched.

    TWO EXCHANGE ENCODINGS (K5). A GECKO model splits every exchange into a forward and a
    ``_e_REV`` reverse half, and uptake is the REV half's flux -- that is the eciML1515 case and
    the only one this function handled. A plain SBML GEM keeps one reversible exchange with a
    negative lower bound, and uptake is its REVERSE VARIABLE; that is the Candida and methanogen
    case, in which the GECKO pattern matches nothing at all and the cap was silently a no-op.
    The plain-exchange branch is a FALLBACK, used only when the GECKO pattern finds nothing, so
    no eciML1515 run can change behaviour.
    """
    m = pm.ec.model if hasattr(pm, "ec") else pm
    if name in m.constraints:
        m.remove_cons_vars([m.constraints[name]])
    terms, n = [], 0
    for r in m.reactions:
        if not (r.id.startswith("EX_") and r.id.endswith("_e_REV")) or r.upper_bound <= 0:
            continue
        if r.id[3:-6] in exclude:
            continue
        mets = list(r.metabolites)
        if len(mets) == 1:
            nC = mets[0].elements.get("C", 0)
            if nC > 0:
                terms.append(nC * r.flux_expression)
                n += 1
    if not terms:
        # plain SBML exchanges: uptake is the reverse variable of a reaction with lb < 0
        for r in m.reactions:
            if not r.id.startswith("EX_") or r.lower_bound >= 0:
                continue
            mets = list(r.metabolites)
            if len(mets) != 1:
                continue
            mid = mets[0].id.lower()
            if any(x in mid for x in exclude) or mets[0].id.startswith(("C00011", "C00288")):
                continue
            nC = (mets[0].elements or {}).get("C", 0)
            if nC > 0:
                terms.append(nC * r.reverse_variable)
                n += 1
    if not terms:
        return None
    c = m.problem.Constraint(sum(terms), lb=0, ub=float(c_max), name=name)
    m.add_cons_vars([c])
    m.solver.update()
    c._n_carbon_sources = n
    return c


def remove_total_carbon_constraint(pm, name: str = "total_carbon_uptake"):
    m = pm.ec.model if hasattr(pm, "ec") else pm
    if name in m.constraints:
        m.remove_cons_vars([m.constraints[name]])
        m.solver.update()


# ---------------------------------------------------------------------------
# (2) empirical threshold-linear overflow line
# ---------------------------------------------------------------------------
def add_acetate_line(pm, slope: float, threshold: float, exchange_rxn: str,
                     biomass_rxn: Optional[str] = None, name: str = "overflow_line"):
    """Impose a threshold-linear overflow floor  ``J >= slope * (mu - threshold)``.

    ``J`` is NET excretion through ``exchange_rxn`` (forward minus its ``_REV`` partner) and
    ``mu`` is the biomass flux. Below ``threshold`` the right-hand side is negative, so the
    constraint is slack and excretion may be zero -- the empirical law's threshold behaviour.

    Nothing about the law is organism-specific in this function: the slope, the threshold and
    the reaction come from the strain's configuration -- ``gas_exchange.overflow_line`` in
    ``strains/<name>/gas_exchange.yaml``, where the measurement's citation is recorded.
    """
    m = pm.ec.model if hasattr(pm, "ec") else pm
    if name in m.constraints:
        m.remove_cons_vars([m.constraints[name]])
    if biomass_rxn is None:
        biomass_rxn = getattr(pm, "biomass_rxn", None)
    if biomass_rxn is None:
        raise ValueError("add_acetate_line needs a biomass reaction id "
                         "(pass biomass_rxn= or use a ProvidedModel that carries one)")
    fwd = m.reactions.get_by_id(exchange_rxn)
    rev = m.reactions.get_by_id(f"{exchange_rxn}_REV") if f"{exchange_rxn}_REV" in m.reactions else None
    bio = m.reactions.get_by_id(biomass_rxn)
    net = fwd.flux_expression - (rev.flux_expression if rev is not None else 0)
    c = m.problem.Constraint(net - float(slope) * bio.flux_expression,
                             lb=-float(slope) * float(threshold), name=name)
    m.add_cons_vars([c])
    m.solver.update()
    c._slope = float(slope)
    c._threshold = float(threshold)
    return c


# ---------------------------------------------------------------------------
# (3) MMRT-costed membrane transport
# ---------------------------------------------------------------------------
def add_transport_costs(pm, kcat: float, mw_kDa: float, length_aa: float,
                        dcp_prior_kJ: float = -4.0, only_carbon: bool = True,
                        compartments=frozenset({"c", "p"}), skip_suffixes=("tex",),
                        group: str = "transport", verbose: bool = True):
    """Give the uncosted membrane carriers an enzyme cost, so uptake carries a thermal envelope.

    Any reaction that (a) has no cost entry yet, (b) is not an exchange / arm / protein
    pseudo-reaction, (c) spans exactly ``compartments`` and (d) -- with ``only_carbon`` --
    touches a carbon-bearing metabolite, is added to the enzyme table with the given generic
    carrier parameters and the dataset-mean Topt / Tm, so its Vmax follows kcat(T) * f_N(T)
    like every other enzyme. Reactions whose id ends in one of ``skip_suffixes`` are left free
    (outer-membrane porins are diffusive, not catalytic).

    The carrier parameters are arguments, not constants: a generic transporter's molecular
    weight, turnover and length are properties of the organism being modelled and belong in its
    ``strain.yaml``. Note the model's own ``kcat_scale`` also multiplies these.
    Returns the list of reaction ids that were costed.
    """
    from .enzyme_cost import EnzymeEntry
    ecm = pm.ec
    model = ecm.model
    ents = ecm.table.entries
    costed = {e.rxn_id for e in ents}
    Topt_mean = float(np.mean([e.Topt for e in ents]))
    Tm_vals = [e.Tm for e in ents if e.Tm is not None and np.isfinite(e.Tm)]
    Tm_mean = float(np.mean(Tm_vals)) if Tm_vals else None
    T0 = float(np.median([e.T0 for e in ents]))
    added = []
    for r in model.reactions:
        if r.id in costed or r.id.startswith(("EX_", "arm_", "prot_")):
            continue
        if any(r.id.endswith(sfx) or f"{sfx}_" in r.id for sfx in skip_suffixes):
            continue
        if {mm.compartment for mm in r.metabolites} != compartments:
            continue
        if only_carbon and not any(mm.elements.get("C", 0) > 0 for mm in r.metabolites):
            continue
        ents.append(EnzymeEntry(rxn_id=r.id, mw=float(mw_kDa), kcat_ref=float(kcat),
                                Topt=Topt_mean, dCp=float(dcp_prior_kJ), T0=T0,
                                group=group, Tm=Tm_mean, length=float(length_aa)))
        added.append(r.id)
    if not added:
        return []
    rxns = [model.reactions.get_by_id(e.rxn_id) for e in ents]
    ecm._fwd = [r.forward_variable for r in rxns]
    ecm._rev = [r.reverse_variable for r in rxns]
    ecm._group_pos = {g: np.array([i for i, e in enumerate(ents) if e.group == g])
                      for g in {e.group for e in ents}}
    ecm.refresh_params()
    if verbose:
        tm = "dataset mean" if Tm_mean is None else f"{Tm_mean - 273.15:.1f}C"
        print(f"[transport] costed {len(added)} membrane carriers "
              f"(MW={mw_kDa} kDa, kcat={kcat}/s, {length_aa} aa; "
              f"Topt={Topt_mean - 273.15:.1f}C, Tm={tm})")
    return added


# ---------------------------------------------------------------------------
# overflow threshold (a diagnostic, and a likelihood term for a calibration)
# ---------------------------------------------------------------------------
def overflow_threshold(pm, pert, T_C: float, uptake_rxn: str, exchange_rxn: str,
                       ub_lo: float = 3.0, ub_hi: float = 26.0, n_bisect: int = 9,
                       tol: float = 1e-3) -> float:
    """The growth rate at which EMERGENT overflow switches on, by bisection (~11 LP solves).

    At fixed temperature, sweep the substrate-uptake ceiling ``uptake_rxn`` and find where net
    excretion through ``exchange_rxn`` first becomes positive; return the growth rate there.
    This is the model's own analogue of an empirical overflow threshold, so it can be compared
    with one (or scored in a likelihood) without imposing the empirical line.

    Returns NaN when the model never overflows in the bracket, or already overflows at its
    bottom -- both of which are informative and must not be silently read as zero.
    """
    from .tpc import apply_state
    apply_state(pm.ec, float(T_C), pert)
    m = pm.ec.model
    up = m.reactions.get_by_id(uptake_rxn)
    ub0 = up.upper_bound

    def probe(ub):
        up.upper_bound = float(ub)
        g = m.slim_optimize()
        if str(m.solver.status) != "optimal" or g is None or not np.isfinite(g):
            return None, None
        ex = _flux(m, exchange_rxn) - _flux(m, f"{exchange_rxn}_REV")
        return float(g), float(ex)

    try:
        g_hi, ex_hi = probe(ub_hi)
        if ex_hi is None or ex_hi <= tol:
            return float("nan")
        g_lo, ex_lo = probe(ub_lo)
        if ex_lo is None or ex_lo > tol:
            return float("nan")
        lo, hi = ub_lo, ub_hi
        for _ in range(n_bisect):
            mid = 0.5 * (lo + hi)
            g, ex = probe(mid)
            if g is None:
                return float("nan")
            if ex > tol:
                hi, g_hi = mid, g
            else:
                lo, g_lo = mid, g
        return 0.5 * (g_lo + g_hi)
    finally:
        up.upper_bound = ub0
        m.solver.update()
