"""Membrane real-estate: a surface-area budget on the electron-transport chain.

One mechanism, driven entirely by a per-strain table. This is Parsa's configurations E and F
collapsed (P1): E is the area budget, F is E plus a corrected proton stoichiometry for one
oxidase. Two modules with a near-duplicate constant dict cannot be kept in step, and neither
could ever describe a second organism, so both become **rows and a column** of one table:

    complex,area_nm2,kcat_s,reactions,h_p_target,notes
    <label>,<nm^2>,<s^-1>,<isozyme reaction ids>,<blank>,proton-pumping
    <label>,<nm^2>,<s^-1>,<isozyme reaction ids>,0,non-electrogenic

The footprints, turnovers, reaction ids and the electrogenicity flag are measurements of a
particular organism and its model encoding, so they live in ``strains/<name>/etc/*.csv`` with
their citations; none of them appears here.

Mechanism (a GECKO-style budget in AREA rather than protein MASS), after Szenk, Dill & de
Graff (2017), Cell Systems 5:95-104:

    sum_i (A_i / kcat_i) * v_i  <=  A_ETC          [nm^2 gDW^-1]

* ``A_i``  physical membrane footprint of one complex (nm^2)
* ``kcat_i`` turnover (s^-1), so ``A_i/kcat_i`` is area cost per unit flux
* ``v_i``  summed flux through that complex's isozyme reactions (an LP variable)
* ``A_ETC`` the available inner-membrane area (nm^2 gDW^-1) -- the single budget knob

Respiration is then limited by the area the ETC can physically occupy, so overflow can emerge
instead of being imposed. Where the terminal-oxidase split is left free, the LP chooses it, and
because the oxidases differ in BOTH footprint and proton stoichiometry the choice sets how much
ATP the area budget buys.

No reaction id, footprint, turnover or membrane area appears in this module.
"""
from __future__ import annotations

import os
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

# molecules per (mmol gDW^-1 h^-1), expressed as reactions s^-1 gDW^-1:
#   v[mmol/gDW/h] * 1e-3 mol/mmol * N_A /mol / 3600 s/h
_CONV = 6.02214076e23 * 1e-3 / 3600.0            # = 1.6728e17

CONS_NAME = "etc_membrane_area"
REQUIRED_COLUMNS = ("complex", "area_nm2", "kcat_s", "reactions")


def _model(pm):
    return pm.ec.model if hasattr(pm, "ec") else pm


# ---------------------------------------------------------------------------
# the table
# ---------------------------------------------------------------------------
def load_etc_table(path: str, strain_dir: Optional[str] = None) -> pd.DataFrame:
    """Read a strain's ETC-complex table.

    Columns: ``complex`` (label), ``area_nm2``, ``kcat_s``, ``reactions`` (whitespace- or
    semicolon-separated reaction ids), optional ``h_p_target`` (target coefficient of the
    translocated proton in each of those reactions; blank = leave the model as encoded) and
    optional ``notes``. Comment lines beginning ``#`` carry the provenance and are ignored.
    """
    if strain_dir and not os.path.isabs(path):
        cand = os.path.join(strain_dir, path)
        if os.path.exists(cand):
            path = cand
    df = pd.read_csv(path, comment="#")
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"ETC table {path} is missing column(s): {missing}")
    df["reactions"] = df["reactions"].fillna("").map(
        lambda s: [r for r in str(s).replace(";", " ").split() if r])
    if "h_p_target" not in df.columns:
        df["h_p_target"] = np.nan
    return df


def area_weights(df: pd.DataFrame) -> Dict[str, float]:
    """``w_i = A_i * _CONV / kcat_i``  [nm^2 gDW^-1 per (mmol gDW^-1 h^-1)]."""
    return {row["complex"]: float(row["area_nm2"]) * _CONV / float(row["kcat_s"])
            for _, row in df.iterrows()}


def present_reactions(model, df: pd.DataFrame) -> Dict[str, List[str]]:
    """Per complex, the table reactions this model actually has."""
    return {row["complex"]: [r for r in row["reactions"] if r in model.reactions]
            for _, row in df.iterrows()}


def etc_area_expr(model, df: pd.DataFrame):
    """The linear area-usage expression ``sum_i w_i * v_i`` (nm^2 gDW^-1)."""
    w = area_weights(df)
    out = 0
    for name, rids in present_reactions(model, df).items():
        if rids:
            out = out + w[name] * sum(model.reactions.get_by_id(r).flux_expression
                                      for r in rids)
    return out


def etc_area_value(model, df: pd.DataFrame) -> Dict[str, float]:
    """Area usage (nm^2 gDW^-1) per complex and in total, at the current LP solution."""
    w = area_weights(df)
    out = {}
    for name, rids in present_reactions(model, df).items():
        v = sum(float(model.reactions.get_by_id(r).flux) for r in rids)
        out[name] = w[name] * v
    out["total"] = float(sum(out.values()))
    return out


# ---------------------------------------------------------------------------
# the constraint
# ---------------------------------------------------------------------------
def add_etc_area_constraint(pm, df: pd.DataFrame, a_etc: float, name: str = CONS_NAME):
    """Add ``sum_i (A_i/kcat_i) v_i <= a_etc``."""
    m = _model(pm)
    if name in m.constraints:
        m.remove_cons_vars([m.constraints[name]])
    c = m.problem.Constraint(etc_area_expr(m, df), lb=0.0, ub=float(a_etc), name=name)
    m.add_cons_vars([c])
    m.solver.update()
    c._a_etc = float(a_etc)
    return c


def remove_etc_area_constraint(pm, name: str = CONS_NAME):
    m = _model(pm)
    if name in m.constraints:
        m.remove_cons_vars([m.constraints[name]])
        m.solver.update()


def budget_from_fraction(a_mem_per_gdw: float, f_etc: float) -> float:
    """``A_ETC = A_mem * f_etc`` -- the first-principles budget.

    ``a_mem_per_gdw`` (nm^2 gDW^-1) is a strain property: surface-to-volume ratio divided by
    dry-cell density. Both belong in ``strain.yaml``, not here.
    """
    return float(a_mem_per_gdw) * float(f_etc)


def membrane_area_per_gdw(sv_um2_per_fL: float, dcw_pg_per_fL: float) -> float:
    """A_mem [nm^2 gDW^-1] from surface-to-volume ratio and dry-cell density."""
    return (float(sv_um2_per_fL) * 1e6) / (float(dcw_pg_per_fL) * 1e-12)


def calibrate_budget_to_flux(pm, df: pd.DataFrame, pert, target_flux: float,
                             uptake_rxn: str, T_ref_C: float) -> float:
    """Calibrate ``A_ETC`` so that the maximum flux through ``uptake_rxn`` at ``T_ref_C``
    equals ``target_flux``: bound that uptake, solve, and read off the area used.

    Anchors the absolute budget to a measured respiratory ceiling while keeping the table's
    RELATIVE areas, which are what drive the internal allocation.
    """
    from .tpc import apply_state
    m = _model(pm)
    apply_state(pm.ec, float(T_ref_C), pert)
    r = m.reactions.get_by_id(uptake_rxn)
    ub0 = r.upper_bound
    r.upper_bound = float(target_flux)
    g = m.slim_optimize()
    if str(m.solver.status) != "optimal" or g is None or not np.isfinite(g):
        r.upper_bound = ub0
        m.solver.update()
        raise RuntimeError("ETC-area calibration reference solve infeasible")
    a_etc = etc_area_value(m, df)["total"]
    r.upper_bound = ub0
    m.solver.update()
    return float(a_etc)


# ---------------------------------------------------------------------------
# proton stoichiometry (what used to be a whole second module)
# ---------------------------------------------------------------------------
def _is_proton(mm):
    el = getattr(mm, "elements", {}) or {}
    return el == {"H": 1} and float(getattr(mm, "charge", 1) or 1) == 1.0


def _proton(reaction, compartment, model=None):
    """The proton metabolite of ``compartment``, found by chemistry, not by id.

    Prefer one the reaction already carries; otherwise fall back to the model's proton in that
    compartment. The fallback matters: in a GECKO arm/isozyme split the internal proton often
    sits on the ARM reaction while the translocated proton sits on the isozyme, so an isozyme
    can have ``h_p`` and no ``h_c`` at all. Without the fallback such a reaction is silently
    skipped -- which is a wrong answer, not a safe one, since it leaves exactly the isozyme
    the table is trying to correct untouched.
    """
    for mm in reaction.metabolites:
        if mm.compartment == compartment and _is_proton(mm):
            return mm
    if model is not None:
        for mm in model.metabolites:
            if mm.compartment == compartment and _is_proton(mm):
                return mm
    return None


def set_proton_stoichiometry(pm, df: pd.DataFrame, translocated_compartment: str = "p",
                             internal_compartment: str = "c", verbose: bool = True):
    """Apply each row's ``h_p_target`` to its reactions, mass- and charge-balanced.

    For a row that sets ``h_p_target``, every one of its reactions has the coefficient of the
    translocated (e.g. periplasmic) proton set to that value, and the difference moved to the
    internal proton so the reaction stays balanced. ``h_p_target = 0`` makes a complex
    non-electrogenic: it still turns over, but translocates nothing and so conserves no energy.
    Rows with a blank ``h_p_target`` are left exactly as the model encodes them.

    Returns the list of (reaction, old, new) triples actually changed.
    """
    m = _model(pm)
    changed = []
    for _, row in df.iterrows():
        target = row.get("h_p_target", np.nan)
        if target is None or (isinstance(target, float) and not np.isfinite(target)):
            continue
        target = float(target)
        for rid in row["reactions"]:
            if rid not in m.reactions:
                continue
            r = m.reactions.get_by_id(rid)
            hp = _proton(r, translocated_compartment, m)
            hc = _proton(r, internal_compartment, m)
            if hp is None or hc is None:
                continue
            cur = float(r.metabolites.get(hp, 0.0))
            if cur == target:
                continue
            delta = target - cur
            r.add_metabolites({hp: delta, hc: -delta})
            changed.append((rid, cur, target))
    if changed:
        m.solver.update()
        if verbose:
            for rid, old, new in changed:
                print(f"[etc-area] {rid}: translocated H+ {old:g} -> {new:g}")
    return changed
