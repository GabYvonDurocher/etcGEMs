"""Coarse-grained proteome-sector allocation (Basan 2015 / Scott 2010).

The single scalar proteome pool is refined into three sectors of the total
proteome mass fraction ``P_total`` that sum to 1:

    f_metab : metabolic enzymes      -> the existing pool bound = f_metab * P_total
    f_bio   : biosynthesis/ribosomes -> a translation cap on growth
    f_maint : maintenance/housekeeping -> proteome overhead + maintenance ATP

This is the natural coordinate for a maintenance->biosynthesis reallocation and
makes the baseline rate B0 an explicit allocation trade-off with an interior
optimum (too little metabolic pool starves enzymes; too little biosynthesis caps
translation). Opt-in and backward compatible: unless a strain enables it, nothing
is wired and behaviour is exactly the scalar-pool model.

Growth-law translation cap (Scott/Basan):  translation_coeff * v_biomass <=
f_bio * P_total. ``translation_coeff`` is auto-calibrated at build time so that
at the nominal split and T0 the translation cap and the metabolic pool are
co-limiting (both just bind) -- so enabling sectors at the nominal point does not
move the nominal growth, it only opens the allocation axis.
"""
from __future__ import annotations

from typing import Optional

from .enzyme_cost import Perturbation


def add_proteome_sectors(pm, cfg: dict) -> dict:
    """Wire the three-sector partition onto an already-built ProvidedModel.

    cfg keys (from strain.yaml `proteome_sectors`): P_total (or null -> backed out
    from the model's pool bound), f_metab, f_maint, atpm_reaction, translation_coeff
    ('auto' or a number). Returns the sector state dict (also stored on pm.ec).
    """
    ec = pm.ec
    model = ec.model
    f_metab_nom = float(cfg.get("f_metab", 0.5))
    f_maint_nom = float(cfg.get("f_maint", 0.15))
    f_bio_nom = 1.0 - f_metab_nom - f_maint_nom
    if f_bio_nom <= 0:
        raise ValueError(f"f_metab+f_maint must be <1 (got {f_metab_nom}+{f_maint_nom})")

    # P_total: back out from the metabolic pool bound so the nominal metabolic
    # pool (f_metab_nom * P_total) equals the existing default_budget exactly.
    P_total = cfg.get("P_total")
    if P_total in (None, "null", "auto"):
        P_total = ec.default_budget / f_metab_nom
    P_total = float(P_total)

    ec._pool.ub = f_metab_nom * P_total   # == default_budget at nominal

    # nominal growth at T0 with only the metabolic pool binding
    ec.set_temperature(pm.T0, Perturbation())
    ec.set_budget(f_metab_nom * P_total)
    mu = model.slim_optimize()
    if mu is None or mu <= 0:
        raise RuntimeError("model does not grow at T0; cannot calibrate sectors")

    tc = cfg.get("translation_coeff", "auto")
    if tc in (None, "auto"):
        translation_coeff = f_bio_nom * P_total / mu   # cap binds exactly at mu*
    else:
        translation_coeff = float(tc)

    biomass = model.reactions.get_by_id(pm.biomass_rxn)
    bio_con = model.problem.Constraint(
        translation_coeff * biomass.flux_expression,
        lb=0, ub=f_bio_nom * P_total, name="proteome_biosynthesis")
    model.add_cons_vars([bio_con])
    model.solver.update()

    atpm_rxn = None
    atpm_nom_lb = 0.0
    aid = cfg.get("atpm_reaction")
    for c in ([aid] if aid else ["ATPM", "NGAM"]):
        if c and c in model.reactions:
            atpm_rxn = model.reactions.get_by_id(c)
            atpm_nom_lb = float(atpm_rxn.lower_bound)
            break

    ec._sectors = {
        "P_total": P_total, "f_metab_nom": f_metab_nom, "f_maint_nom": f_maint_nom,
        "f_bio_nom": f_bio_nom, "bio_constraint": bio_con,
        "translation_coeff": translation_coeff, "atpm_rxn": atpm_rxn,
        "atpm_nom_lb": atpm_nom_lb, "mu_nominal": float(mu),
    }
    print(f"[sectors] P_total={P_total:.4g}  f=(metab {f_metab_nom}, bio "
          f"{f_bio_nom:.2f}, maint {f_maint_nom})  translation_coeff="
          f"{translation_coeff:.4g} (mu*={mu:.4g})  "
          f"atpm={atpm_rxn.id if atpm_rxn else None}")
    return ec._sectors
