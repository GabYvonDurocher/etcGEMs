"""Unified multi-parameter Bayesian tuning of the etc-GEM (P2+).

Generalises the single-lever Phase-1 calibration to the full canonical free set the
sensitivity/decomposition will also use, fit at a chosen operating point (here the
rich BHI medium) against one measured absolute-rate TPC (Van Derlinden, K-12
MG1655). Spec-driven so the same machinery serves later joint/per-curve fits.

Method (unchanged): deterministic simulator (theta -> TPC), exact Gaussian
discrepancy likelihood on raw absolute rate, gradient-free ensemble MCMC (emcee).
Positive-only parameters are sampled in log space; sector fractions and additive
shifts in natural space. Priors are provenance-based (see build_vdl_specs).
"""
from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

from .enzyme_cost import Perturbation
from .tpc import TPC, compute_tpc


@dataclass
class PSpec:
    name: str            # natural-space parameter name
    space: str           # "add" (theta = natural) | "log" (theta = log natural)
    prior: str           # "normal" | "lognormal" | "halfnormal"
    scale: float         # prior scale (add: natural units; log: sd on log)
    loc: float = 0.0     # prior centre (natural units); for lognormal the log is centred at log(loc) if loc>0 else 0
    lo: float = -1e9     # hard support bound (natural)
    hi: float = 1e9
    pert: Optional[str] = None   # Perturbation attribute to set (None -> nuisance sigma_disc)
    emergent: Optional[float] = 0.0   # emergent/reference value for reporting

    @property
    def log_center(self) -> float:
        """Centre of the LogNormal in log space (0 -> median 1; log(loc) -> median loc)."""
        return float(np.log(self.loc)) if (self.prior == "lognormal" and self.loc and self.loc > 0) else 0.0


def build_vdl_specs(f_metab_meas=0.280, f_maint_meas=0.360, sigma_nom=0.45) -> List[PSpec]:
    """Canonical free set for the rich Van Derlinden fit (the SAME set P3 uses).
    Measured (rich/LB) sector fractions get TIGHT priors (measurement wiggle only);
    the in-vivo magnitude levers get their physical priors: kcat_scale/kappa_scale
    broad LogNormals about 1, and the in-vivo saturation ``sigma`` a broad Normal on
    the literature ~0.45 BOUNDED to (0,1) -- with the reconciled single pool sigma is
    the EFFECTIVE budget lever (kcat saturates once metabolic enzymes are cheap and the
    ribosome cap binds; sigma raises both caps). The envelope shape (incl. tm_scale)
    and the borrowed maintenance (ngam_scale/ngam_steepness) get moderate/broad priors;
    sigma_disc is a free discrepancy term (Van Derlinden has no measured SD).
    NOTE: sigma_disc MUST stay last (nuisance index + emergent-theta rely on it)."""
    return [
        PSpec("dTopt",         "add", "normal",     4.25, 0.0, -12.0, 12.0, "dTopt", 0.0),
        PSpec("topt_scale",    "log", "lognormal",  0.12, 0.0, 0.5, 2.0, "topt_scale", 1.0),
        PSpec("dCp_scale",     "log", "lognormal",  0.30, 0.0, 0.25, 4.0, "dCp_scale", 1.0),
        PSpec("dTm",           "add", "normal",     6.13, 0.0, -15.0, 15.0, "dTm", 0.0),
        PSpec("tm_scale",      "log", "lognormal",  0.15, 0.0, 0.4, 2.2, "tm_scale", 1.0),
        PSpec("kcat_scale",    "log", "lognormal",  0.60, 0.0, 0.2, 12.0, "kcat_scale", 1.0),
        PSpec("kappa_scale",   "log", "lognormal",  0.60, 0.0, 0.2, 12.0, "kappa_scale", 1.0),
        PSpec("sigma",         "add", "normal",     0.20, sigma_nom, 0.05, 1.0, "sigma_sat", sigma_nom),
        PSpec("f_metab",       "add", "normal",     0.03, f_metab_meas, 0.15, 0.45, "f_metab", f_metab_meas),
        PSpec("f_maint",       "add", "normal",     0.03, f_maint_meas, 0.20, 0.50, "f_maint", f_maint_meas),
        PSpec("ngam_scale",    "log", "lognormal",  0.50, 0.0, 0.1, 6.0, "ngam_scale", 1.0),
        PSpec("ngam_steepness","log", "lognormal",  0.50, 0.0, 0.1, 6.0, "ngam_steepness", 1.0),
        PSpec("sigma_disc",    "log", "halfnormal", 0.50, 0.0, 1e-4, 5.0, None, None),
    ]


# --- overflow / gas-exchange fits (P1: Parsa's configuration D and later) ------------------
# Widened thermal-envelope priors, opt-in. In his capped fit the dCp_scale posterior ran to
# 2.18 at p95 while its prior only reached 1.64 -- the data was pushing against the prior --
# so Topt shift and spread are freed alongside it and the peak SHAPE, POSITION and WIDTH can
# move together. topt_scale's upper bound is TIGHTENED 2.0 -> 1.35 in the same breath: above
# ~1.4 every enzyme sits far above its inflated Topt and the whole TPC collapses to zero
# growth (measured), so a wider prior there only scatters walkers into a dead region.
WIDE_ENVELOPE_SPECS = {
    "dTopt":      PSpec("dTopt",      "add", "normal",    8.00, 0.0, -15.0, 15.0, "dTopt", 0.0),
    "topt_scale": PSpec("topt_scale", "log", "lognormal", 0.25, 0.0, 0.60, 1.35, "topt_scale", 1.0),
    "dCp_scale":  PSpec("dCp_scale",  "log", "lognormal", 0.50, 0.0, 0.25, 4.00, "dCp_scale", 1.0),
}


def build_overflow_specs(f_metab_meas=0.280, f_maint_meas=0.360, sigma_nom=0.45,
                         fit_carbon_cap=True, wide_envelope=False) -> List[PSpec]:
    """The Van Derlinden free set, as a CONFIGURATION for an overflow / gas-exchange fit.

    This is the whole of what used to be a second calibrator: the same twelve physical levers
    with the same priors and provenance, optionally (a) widened envelope priors and (b) one
    extra dimension, ``C_max_mult``, a multiplier on the strain's nominal total-carbon cap so
    the cap is fitted rather than swept. ``sigma_disc`` stays LAST -- the nuisance index and
    the emergent-theta helper rely on it.

    Adding a third top-level calibrator was the alternative and was rejected (P1 DECISIONS
    D4): three sampling code paths cannot be kept in step, and everything that differs here is
    a parameter set, not an algorithm.
    """
    base = build_vdl_specs(f_metab_meas, f_maint_meas, sigma_nom)
    phys = [s for s in base if s.name != "sigma_disc"]
    if wide_envelope:
        phys = [WIDE_ENVELOPE_SPECS.get(s.name, s) for s in phys]
    disc = next(s for s in base if s.name == "sigma_disc")
    cap = ([PSpec("C_max_mult", "log", "lognormal", 0.40, 0.0, 0.25, 3.0, None, 1.0)]
           if fit_carbon_cap else [])
    return phys + cap + [disc]


def build_pm_medium(strain, medium=None, experiment=None, cfg=None, timeout=10):
    """Provider at a chosen GROWTH MEDIUM and the calibration operating point.

    The generalisation of :func:`_build_pm_rich` over media: same coupled growth law, same
    static sectors (``allocation_from_data`` off, so the fitted f_metab/f_maint drive the
    split), but the medium -- and any gas-exchange mechanism -- comes from a
    ``configs/experiments/gasflux_*.yaml`` overlay rather than from code. Pass ``medium`` to
    override the overlay's choice for one call, which is what a per-medium likelihood term
    needs.
    """
    import copy
    from .config import resolve, build_provider
    cfg = copy.deepcopy(cfg) if cfg is not None else resolve(strain, experiment)
    cfg.setdefault("proteome_sectors", {})["biosynthesis_growth_law"] = True
    cfg["allocation_from_data"] = None
    if medium is not None:
        cfg.setdefault("gasflux", {})["enabled"] = True
        cfg["gasflux"]["medium"] = medium
    pm = build_provider(cfg)
    try:
        pm.ec.model.solver.configuration.timeout = int(timeout)
    except Exception:
        pass
    pm.ec._alloc_from_data = None
    return pm


# ---------------------------------------------------------------------------
# overflow / gas-exchange fits against measured growth + per-cell respiration (P4)
# ---------------------------------------------------------------------------
OVERFLOW_MEDIUM_OTU = {"NLDM": 1, "LB": 2, "glucose_minimal": 1}
_MW_O2 = 32.0
_MASK_G = 1e-4          # growth below this is "dead"; respiration there is not scored


def build_gasflux_specs(cfg) -> List[PSpec]:
    """Free set for a gas-exchange fit, assembled from ``cfg`` -- not a new spec system.

    Starts from :func:`build_overflow_specs` (the v3 twelve with the widened envelope priors)
    and adds only what the configuration needs:

    * ``fit_clearance``  -- the medium's volumetric clearance K, as a multiplier of the strain's
      nominal (prior [0.4, 2.0] -> K in [2, 10] L gDW^-1 h^-1). This is the recipe medium's one
      physical scale factor, and P4 samples it rather than fixing it.
    * ``use_etc``        -- the ETC membrane fraction F_ETC, as a multiplier of the nominal.
    * ``resp_scale``     -- the per-cell respiration scale, plus its discrepancy term.
    * ``disc_growth``    -- the growth discrepancy term, LAST as the nuisance index requires.

    The total-carbon cap is NOT a free parameter here: P4 adopts c_max from Parsa's own sweep
    rather than fitting it, so it is a fixed model setting, not a dimension.
    """
    specs = [s for s in build_overflow_specs(fit_carbon_cap=False, wide_envelope=True)
             if s.name != "sigma_disc"]
    if cfg.get("use_etc"):
        specs += [PSpec("F_ETC_mult", "log", "lognormal", 0.35, 0.0, 0.3, 2.0, None, 1.0)]
    if cfg.get("fit_clearance"):
        specs += [PSpec("clearance_mult", "log", "lognormal", 0.35, 0.0, 0.4, 2.0, None, 1.0)]
    specs += [PSpec("resp_scale", "log", "lognormal", 1.00, 0.0, 0.02, 50.0, None, 1.0),
              PSpec("disc_resp", "log", "halfnormal", 0.50, 0.0, 1e-3, 3.0, None, None),
              PSpec("disc_growth", "log", "halfnormal", 0.50, 0.0, 1e-4, 5.0, None, None)]
    return specs


def load_respirometry(strain, table, otu, temps=None):
    """(T, growth mean/sd, respiration mean/sd) from a committed respirometry table.

    ``growth_C_per_C_h`` is a specific rate (h^-1) and ``R_O2_mg_cell_min`` is per cell; both
    are averaged over replicates per temperature. SDs are floored the way his likelihood floors
    them -- 2 % of the mean for growth, 30 % for respiration where the SD is missing -- so a
    single-replicate temperature cannot dominate.
    """
    import pandas as pd
    from .config import strain_dir
    path = table if os.path.isabs(table) else os.path.join(strain_dir(strain), table)
    d = pd.read_csv(path)
    d = d[d["OTU"] == otu]
    if temps is not None:
        d = d[d["T"].isin(list(temps))]
    g = d.groupby("T")["growth_C_per_C_h"].agg(["mean", "std", "count"]).reset_index()
    r = d.groupby("T")["R_O2_mg_cell_min"].agg(["mean", "std"]).reset_index()
    T = g["T"].to_numpy(float)
    og = g["mean"].to_numpy(float)
    sg = np.maximum(np.nan_to_num(g["std"].to_numpy(float), nan=0.0),
                    0.02 * np.maximum(og, 1e-6))
    orr = r["mean"].to_numpy(float)
    sr = np.where(np.isfinite(r["std"].to_numpy(float)), r["std"].to_numpy(float), 0.30 * orr)
    meta = {"table": os.path.basename(path), "otu": int(otu), "n_per_T": g["count"].astype(int).tolist(),
            "temps_C": T.tolist(), "growth_obs": og.tolist(), "growth_sd": sg.tolist(),
            "resp_obs": orr.tolist(), "resp_sd": sr.tolist()}
    return T, og, sg, orr, sr, meta


def build_gasflux_pm(strain, medium, experiment, c_max=None, etc_table=None, timeout=30):
    """Provider for a gas-exchange fit, built through the ordinary config path.

    Everything the configuration needs is set here ONCE and read back from the resolved config
    by the caller, so a setting cannot arrive by accident from an overlay (P3 found exactly that
    failure: configuration D's cap leaking into E and F).
    """
    import copy
    from .config import resolve, build_provider
    cfg = resolve(strain, experiment)
    cfg.setdefault("proteome_sectors", {})["biosynthesis_growth_law"] = True
    cfg["allocation_from_data"] = None
    gf = cfg.setdefault("gasflux", {})
    gf["enabled"] = True
    gf["medium"] = medium
    gf["media"] = [medium]
    cc = gf.setdefault("total_carbon_cap", {})
    cc["enabled"] = c_max is not None
    if c_max is not None:
        cc["c_max"] = float(c_max)
    ea = gf.setdefault("etc_area", {})
    if etc_table is not None:
        ea["enabled"] = True
        ea["table"] = etc_table
        ea["apply_proton_stoichiometry"] = bool(ea.get("apply_proton_stoichiometry"))
    else:
        ea["enabled"] = False
    pm = build_provider(cfg)
    try:
        pm.ec.model.solver.configuration.timeout = float(timeout)
    except Exception:
        pass
    pm.ec._alloc_from_data = None
    return pm, cfg


def gasflux_log_likelihood(theta, ctx, specs) -> float:
    """Growth TPC + per-cell respiration TPC, the two terms his fits used.

    Growth is scored on a linear scale against the measured specific growth rate; respiration
    on a LOG scale against the measured per-cell rate, over the temperatures where the model is
    alive and consuming O2. ``resp_scale`` carries the per-cell unit conversion, which is why it
    is fitted rather than asserted -- see strains/<strain>/respirometry/README.md for what that
    absorbs.
    """
    nat = to_natural(theta, specs)
    pert = to_pert(theta, specs)
    pm = ctx["pm"]
    if "clearance_mult" in nat:
        from . import providers as _prov
        r = ctx["recipe"]
        _prov.set_medium_recipe(pm, r["recipe_csv"],
                                clearance_L_per_gDW_h=r["clearance"] * float(nat["clearance_mult"]),
                                uptake_ub=r.get("uptake_ub", 1000.0), verbose=False)
        if ctx.get("c_max") is not None:
            from .gasflux import add_total_carbon_constraint
            add_total_carbon_constraint(pm, float(ctx["c_max"]))
    if "F_ETC_mult" in nat:
        from . import etc_area as _ea
        _ea.add_etc_area_constraint(
            pm, ctx["etc_table"],
            _ea.budget_from_fraction(ctx["a_mem"], ctx["f_etc_nom"] * float(nat["F_ETC_mult"])))
    from .gasflux import flux_tpc
    resp = ctx.get("respiration") or {}          # P10: strain-config options, default inert
    try:
        df = flux_tpc(pm, ctx["T"], pert, metabolites=("o2",),
                      tiebreak=str(resp.get("tiebreak", "none")),
                      growth_tol=float(resp.get("growth_tol", 1e-6)),
                      tiebreak_tol=float(resp.get("tiebreak_tol", 1e-9)))
    except Exception:
        return -np.inf
    g = df["growth"].to_numpy(float)
    o2 = df["o2_uptake"].to_numpy(float)
    if not np.all(np.isfinite(g)):
        return -np.inf
    dg = float(nat["disc_growth"])
    var = ctx["growth_sd"] ** 2 + dg ** 2
    ll = float(-0.5 * np.sum((ctx["growth_obs"] - g) ** 2 / var + np.log(2 * np.pi * var)))
    keep = (g >= _MASK_G) & (o2 > 0)
    if keep.sum() >= 1:
        dr = float(nat["disc_resp"])
        rs = float(nat["resp_scale"])
        pred = np.log(o2[keep] * ctx["o2_conv"] * rs)
        obsl = np.log(ctx["resp_obs"][keep])
        rel = ctx["resp_sd"][keep] / ctx["resp_obs"][keep]
        # P10: a floor on the log-O2 sd, in quadrature -- the model's own vertex granularity
        # (how far O2 at the optimum jumps between adjacent LP vertices), fixed from
        # measurement of the surface (reports/P10_respiration_likelihood), default 0 = off.
        floor = float(resp.get("log_o2_floor", 0.0))
        varr = rel ** 2 + dr ** 2 + floor ** 2
        # P10: the support of the term. The hard mask above switches a whole temperature in or
        # out of the term as growth crosses 1e-4, which is a discontinuity by construction --
        # half of P9's cliffs were this, not O2 (P10 D2). With ``alive_soft_growth`` = g_s set,
        # a temperature's contribution is weighted by min(1, g / g_s), continuous in theta and
        # equal to 1 wherever the model grows faster than g_s. Default None = the hard mask.
        gs = resp.get("alive_soft_growth")
        w = np.minimum(1.0, g[keep] / float(gs)) if gs else np.ones(int(keep.sum()))
        ll += float(-0.5 * np.sum(w * ((obsl - pred) ** 2 / varr + np.log(2 * np.pi * varr))))
    return ll


_GCTX = None
_GSPECS = None


def _gwinit(payload):
    global _GCTX, _GSPECS
    _set_default_solver(payload.pop("solver", "gurobi"))
    _GCTX, _GSPECS = _build_gasflux_ctx(**payload)


def _gwlogprob(theta):
    lp = log_prior(theta, _GSPECS)
    if not np.isfinite(lp):
        return -np.inf
    ll = gasflux_log_likelihood(theta, _GCTX, _GSPECS)
    return lp + ll if np.isfinite(ll) else -np.inf


def _gwnegpost(theta):
    v = _gwlogprob(theta)
    return 1e12 if not np.isfinite(v) else -v


def _gwloglike(theta):
    """(P11) The gas-flux LOG-LIKELIHOOD alone, on the worker's own ctx -- the callable a
    sampler that handles the prior itself (nested sampling) needs. Same ctx, same specs and
    same pool initialiser (:func:`_gwinit`) as :func:`_gwlogprob`; the only difference is that
    no log-prior is added. Bounds are the prior transform's business, so an out-of-support
    theta cannot arrive here; a non-finite likelihood is returned as a large negative number
    because dynesty requires a finite ordering."""
    ll = gasflux_log_likelihood(theta, _GCTX, _GSPECS)
    return float(ll) if np.isfinite(ll) else -1e100


def _build_gasflux_ctx(strain, medium, experiment, table, otu, c_max, etc_table,
                       apply_protons, fit_clearance, timeout=30):
    import yaml
    from . import etc_area as _ea
    pm, cfg = build_gasflux_pm(strain, medium, experiment, c_max=c_max,
                               etc_table=etc_table, timeout=timeout)
    gx = cfg.get("gas_exchange") or {}
    T, og, sg, orr, sr, meta = load_respirometry(strain, table, otu)
    ctx = {"pm": pm, "T": T, "growth_obs": og, "growth_sd": sg,
           "resp_obs": orr, "resp_sd": sr, "meta": meta, "c_max": c_max,
           "o2_conv": float(gx["gdw_per_cell"]) * _MW_O2 / 60.0,
           # P10: the strain's respiration-likelihood options (gas_exchange.respiration):
           # tiebreak none|pfba|min_o2|max_o2 (default none), log_o2_floor (default 0).
           "respiration": dict(gx.get("respiration") or {})}
    if etc_table is not None:
        mem = gx.get("membrane") or {}
        from .config import strain_dir
        ctx["etc_table"] = _ea.load_etc_table(etc_table, strain_dir(strain))
        ctx["a_mem"] = _ea.membrane_area_per_gdw(mem["sv_um2_per_fL"], mem["dcw_pg_per_fL"])
        ctx["f_etc_nom"] = float(gx.get("f_etc_nom", 0.316))
    if fit_clearance:
        rec = ((gx.get("media") or {}).get(medium) or {})
        from .config import _strain_path
        ctx["recipe"] = {"recipe_csv": _strain_path(cfg, rec["recipe_csv"]),
                         "clearance": float(rec["clearance_L_per_gDW_h"]),
                         "uptake_ub": float(rec.get("uptake_ub", 1000.0))}
    return ctx, build_gasflux_specs({"use_etc": etc_table is not None,
                                     "fit_clearance": fit_clearance})


def run_zeus_blocks(logprob, p0, n_steps_max, check_every, pool, out_dir=None, label="",
                    prev=None, seed=1, tau_factor=25, target_neff=600, n_burn=200):
    """(P8) Run zeus in blocks of ``check_every`` steps -- the same loop, tau estimator and
    stopping rule as the emcee path of :func:`run_gasflux_fit` -- saving chain.npy /
    log_prob.npy after every block (the checkpoint) and quoting zeus's own diagnostics
    (``act``, ``efficiency``) beside emcee's tau at each checkpoint.

    ``prev`` = (chain, log_prob) of an earlier run to continue from (positions only: zeus
    cannot restore its random state, so a resumed chain is the same ensemble with fresh
    proposals). Returns (chain, log_prob, n_steps, tau_max, stop_reason, info)."""
    import zeus
    import emcee
    n_walkers, ndim = p0.shape
    np.random.seed(seed)
    sampler = zeus.EnsembleSampler(n_walkers, ndim, logprob, pool=pool, verbose=False)
    state = p0; done = 0; tau_max = float("nan")
    stop_reason = f"n_steps_max ({n_steps_max})"
    info = {"ncall": 0, "checkpoints": []}
    while done < n_steps_max:
        n = min(check_every, n_steps_max - done)
        t0 = time.time()
        sampler.run_mcmc(state, n, progress=False)
        state = sampler.get_last_sample()
        done += n
        chain = sampler.get_chain(); lp = sampler.get_log_prob()
        if prev is not None:
            chain = np.concatenate([prev[0], chain], axis=0); lp = np.concatenate([prev[1], lp], axis=0)
        if out_dir:
            np.save(os.path.join(out_dir, "chain.npy"), chain)
            np.save(os.path.join(out_dir, "log_prob.npy"), lp)
        total = chain.shape[0]
        try:
            tau_max = float(np.nanmax(emcee.autocorr.integrated_time(chain, tol=0)))
        except Exception:
            tau_max = float("nan")
        try:
            z_act = float(np.max(sampler.act)); z_eff = float(sampler.efficiency); z_ess = float(sampler.ess)
        except Exception:
            z_act = z_eff = z_ess = float("nan")
        info["ncall"] = int(sampler.ncall)
        ck = dict(step=total, tau_max_emcee=tau_max, zeus_act_max=z_act, zeus_efficiency=z_eff, zeus_ess=z_ess,
                  ncall=int(sampler.ncall), block_wall_s=round(time.time() - t0, 1),
                  evals_per_walker_step=round(sampler.ncall / (n_walkers * (total - (prev[0].shape[0] if prev is not None else 0))), 2))
        info["checkpoints"].append(ck)
        if np.isfinite(tau_max) and tau_max > 0:
            burn_now = min(int(max(n_burn, 2 * tau_max)), total - 10)
            n_eff_min = n_walkers * (total - burn_now) / tau_max
            print(f"[zeus] {label} step {total}: tau_max={tau_max:.1f} (emcee estimator) chain/tau={total / tau_max:.1f} "
                  f"(need >{tau_factor}) min n_eff~{n_eff_min:.0f} (need >={target_neff}) | zeus act_max={z_act:.1f} "
                  f"efficiency={z_eff:.4f} ess={z_ess:.0f} evals/walker/step={ck['evals_per_walker_step']} "
                  f"block {ck['block_wall_s']} s", flush=True)
            if total > tau_factor * tau_max and n_eff_min >= target_neff:
                stop_reason = (f"converged: chain {total} > {tau_factor}*tau_max AND min n_eff {n_eff_min:.0f} >= {target_neff}")
                break
        else:
            print(f"[zeus] {label} step {total}: autocorr not yet estimable", flush=True)
    total = chain.shape[0]
    return chain, lp, total, tau_max, stop_reason, info


def run_gasflux_fit(strain, out_dir, *, medium, table, otu=None, experiment="gasflux_configD",
                    c_max=None, etc_table=None, apply_protons=False, fit_clearance=True,
                    label="", n_walkers=36, n_steps_max=2000, n_burn=200, seed=1, n_proc=0,
                    check_every=250, target_neff=200, tau_factor=40, allow_glpk=False,
                    warm_start=True, progress=False, moves=None, init_state=None,
                    init_label=None, warm_start_min_growth_frac=0.10,
                    checkpoint=False, resume=False, sampler_kind="emcee") -> Dict:
    """Emcee fit of one gas-exchange configuration to measured growth + per-cell respiration.

    The fourth entry point beside :func:`run`, :func:`run_syn6803` and :func:`run_methanogen`,
    on the same machinery (PSpec / to_pert / log_prior / warm start / autocorr early-stop). It
    is a configuration of that machinery, not a second calibrator.

    SAMPLER-ONLY options added by P6 (none of them touches the model, likelihood or priors):

    * ``moves``      -- passed straight to ``emcee.EnsembleSampler``; None keeps emcee's default
                        stretch move, which every earlier fit in this family used.
    * ``init_state`` -- an (n_walkers, ndim) array of starting positions, e.g. the final
                        ensemble state of an earlier chain for the same fit. Overrides the warm
                        start and the emergent-point ball; ``n_walkers`` is then taken from it.
                        ``init_label`` is recorded in summary.json so the provenance is visible.
    * ``warm_start_min_growth_frac`` -- the warm start is REJECTED, and the emergent-point ball
                        used instead, if the DE mode's predicted peak growth is below this
                        fraction of the measured peak. P5 found the mode-seeker can return a
                        zero-growth local optimum (the growth discrepancy term absorbing the
                        data) and seed every walker there, where they stay (OPEN_ITEMS 3.20).
                        A warm start into a dead mode is worse than none.
    * ``checkpoint``  -- (P7) keep the chain in emcee's HDF5 backend, ``<out_dir>/chain.h5``,
                        written every step, with the sampler's random state, so a halted run
                        loses at most the block in flight. ``resume=True`` continues a run from
                        that file (walkers, positions and random state come from it; the init
                        arguments are ignored). The sampler's RNG is seeded from ``seed`` either
                        way, so a checkpointed and an un-checkpointed run of the same seed give
                        IDENTICAL chains -- proven, not assumed (reports/P7_walkers TASK 1).
    * ``sampler_kind`` -- (P8) ``"emcee"`` (the default, everything above) or ``"zeus"``: the
                        ensemble slice sampler (zeus-mcmc), same log-probability, same pool, same
                        block loop and tau estimator, run through :func:`run_zeus_blocks`. Its
                        checkpoint is a per-block save of chain.npy / log_prob.npy (zeus has no
                        resumable backend); ``resume=True`` restarts from the saved last positions
                        and concatenates. Walkers are taken as given (zeus asks for >= 2 * ndim).
    """
    import emcee
    os.makedirs(out_dir, exist_ok=True)
    np.random.seed(seed)
    otu = OVERFLOW_MEDIUM_OTU[medium] if otu is None else int(otu)
    payload = dict(strain=strain, medium=medium, experiment=experiment, table=table, otu=otu,
                   c_max=c_max, etc_table=etc_table, apply_protons=apply_protons,
                   fit_clearance=fit_clearance)

    solver = _set_default_solver("gurobi")
    if solver != "gurobi" and not allow_glpk:
        raise SystemExit("[solver] Gurobi NOT active - stopping (set ALLOW_GLPK to override).")
    print(f"[solver] {solver}")

    ctx, specs = _build_gasflux_ctx(**payload)
    ndim = len(specs)
    _, cfg = build_gasflux_pm(strain, medium, experiment, c_max=c_max, etc_table=etc_table)
    from .config import dump_resolved
    dump_resolved(cfg, out_dir)

    t_pf = time.time()
    lp0 = gasflux_log_likelihood(init_walkers(specs, 1, np.random.default_rng(seed))[0], ctx, specs)
    pf_ms = (time.time() - t_pf) * 1000
    if not np.isfinite(lp0):
        raise SystemExit(f"[preflight] {label}: the likelihood is not finite at a prior draw.")
    print(f"[preflight] {label}: one likelihood evaluation = {pf_ms:.0f} ms over "
          f"{len(ctx['T'])} temperatures; logL={lp0:.1f}")

    n_proc = n_proc or max(1, min(10, (os.cpu_count() or 2) - 2))
    backend = None
    resuming = False
    if checkpoint:
        backend = emcee.backends.HDFBackend(os.path.join(out_dir, "chain.h5"))
        if resume and os.path.exists(os.path.join(out_dir, "chain.h5")) and backend.iteration > 0:
            resuming = True
            n_walkers = int(backend.shape[0])
            print(f"[ckpt] {label}: resuming from chain.h5 at iteration {backend.iteration} "
                  f"({n_walkers} walkers)", flush=True)
    if resuming:
        pass
    elif init_state is not None:
        init_state = np.asarray(init_state, float)
        if init_state.ndim != 2 or init_state.shape[1] != ndim:
            raise SystemExit(f"[init] {label}: init_state has shape {init_state.shape}, "
                             f"need (n_walkers, {ndim})")
        n_walkers = int(init_state.shape[0])
    else:
        n_walkers = int(np.ceil(max(n_walkers, 2 * ndim + 2) / n_proc)) * n_proc

    from multiprocessing import Pool
    pool = Pool(processes=n_proc, initializer=_gwinit, initargs=(dict(payload, solver=solver),))
    t0 = time.time()
    warm_rejected = False
    try:
        if resuming:
            p0, mode = None, None
            init_kind = f"resumed from chain.h5 at iteration {backend.iteration}"
        elif init_state is not None:
            p0, mode = init_state, None
            init_kind = init_label or "init_state"
            print(f"[init] {label}: {n_walkers} walkers from {init_kind}", flush=True)
        elif warm_start:
            p0, mode = _warm_start(specs, n_walkers, seed, pool, progress,
                                   negpost=_gwnegpost, logprob=_gwlogprob)
            init_kind = "warm-start (DE mode ball)"
            if mode is not None:
                # P6 / OPEN_ITEMS 3.20: does the mode GROW? A zero-growth mode is a local
                # optimum of this posterior and every walker seeded there stays there.
                from .gasflux import flux_tpc as _ftpc
                try:
                    _g = _ftpc(ctx["pm"], ctx["T"], to_pert(mode, specs),
                               metabolites=("o2",))["growth"].to_numpy(float)
                    gmax = float(np.nanmax(_g))
                except Exception:
                    gmax = 0.0
                peak = float(np.nanmax(ctx["growth_obs"]))
                if not (gmax >= warm_start_min_growth_frac * peak):
                    print(f"[warm-start] {label}: REJECTED -- the DE mode predicts peak growth "
                          f"{gmax:.4f} h^-1 against a measured {peak:.3f} (floor "
                          f"{warm_start_min_growth_frac:.0%}); using emergent-point init",
                          flush=True)
                    p0, mode = init_walkers(specs, n_walkers, np.random.default_rng(seed)), None
                    warm_rejected = True
                    init_kind = "emergent-point ball (warm start rejected: dead mode)"
                else:
                    print(f"[warm-start] {label}: mode predicts peak growth {gmax:.3f} h^-1 "
                          f"against a measured {peak:.3f} -- accepted", flush=True)
            else:
                init_kind = "emergent-point ball (warm start found no mode)"
        else:
            p0, mode = init_walkers(specs, n_walkers, np.random.default_rng(seed)), None
            init_kind = "emergent-point ball"
        if sampler_kind == "zeus":
            prev = None
            if resume and os.path.exists(os.path.join(out_dir, "chain.npy")):
                prev = (np.load(os.path.join(out_dir, "chain.npy")), np.load(os.path.join(out_dir, "log_prob.npy")))
                p0 = prev[0][-1]; n_walkers = int(p0.shape[0])
                init_kind = f"resumed (zeus) from chain.npy at step {prev[0].shape[0]}"
                print(f"[ckpt] {label}: {init_kind}", flush=True)
            zres = run_zeus_blocks(_gwlogprob, np.asarray(p0, float), n_steps_max, check_every, pool,
                                   out_dir=out_dir, label=label, prev=prev, seed=seed,
                                   tau_factor=tau_factor, target_neff=target_neff, n_burn=n_burn)
            chain, lp_all, done, tau_max, stop_reason, zinfo = zres
            sampler = None
        else:
          if backend is not None and not resuming:
            backend.reset(n_walkers, ndim)
          sampler = emcee.EnsembleSampler(n_walkers, ndim, _gwlogprob, pool=pool, moves=moves,
                                        backend=backend)
          if not resuming:
            # seed the sampler's OWN RNG (emcee 3 does not read numpy's global seed), so the
            # same seed gives the same chain with or without a backend; on resume the backend
            # restores the random state it saved.
            sampler.random_state = np.random.RandomState(seed).get_state()
          state = p0; done = int(backend.iteration) if resuming else 0; tau_max = float("nan")
          stop_reason = f"n_steps_max ({n_steps_max})"
          zinfo = {}
          while done < n_steps_max:
              n = min(check_every, n_steps_max - done)
              state = sampler.run_mcmc(state, n, progress=progress)
              done += n
              if backend is not None:
                  print(f"[ckpt] {label}: chain.h5 holds {backend.iteration} steps", flush=True)
              try:
                  tau_max = float(np.nanmax(sampler.get_autocorr_time(tol=0)))
              except Exception:
                  tau_max = float("nan")
              if np.isfinite(tau_max) and tau_max > 0:
                  burn_now = min(int(max(n_burn, 2 * tau_max)), done - 10)
                  n_eff_min = n_walkers * (done - burn_now) / tau_max
                  print(f"[emcee] {label} step {done}: tau_max={tau_max:.1f} "
                        f"chain/tau={done / tau_max:.1f} (need >{tau_factor}) "
                        f"min n_eff~{n_eff_min:.0f} (need >={target_neff})", flush=True)
                  if done > tau_factor * tau_max and n_eff_min >= target_neff:
                      stop_reason = (f"converged: chain {done} > {tau_factor}*tau_max "
                                     f"AND min n_eff {n_eff_min:.0f} >= {target_neff}")
                      break
              else:
                  print(f"[emcee] {label} step {done}: autocorr not yet estimable", flush=True)
    finally:
        pool.close(); pool.join()
    wall = time.time() - t0

    burn = min(int(n_burn if not np.isfinite(tau_max) else max(n_burn, 2 * tau_max)), done - 10)
    thin = max(1, int(tau_max / 2)) if np.isfinite(tau_max) else 1
    if sampler is not None:
        chain = sampler.get_chain()
        lp_all = sampler.get_log_prob()
        accept = float(np.mean(sampler.acceptance_fraction))
    else:
        accept = float("nan")          # a slice sampler has no acceptance fraction
    flat = chain[burn::thin].reshape(-1, chain.shape[2])
    lpf = lp_all[burn::thin].reshape(-1)
    i, j = np.unravel_index(np.nanargmax(lp_all), lp_all.shape)
    n_eff = flat.shape[0] if not np.isfinite(tau_max) else float(n_walkers * (done - burn) / tau_max)
    converged = stop_reason.startswith("converged")

    np.save(os.path.join(out_dir, "chain.npy"), chain)
    np.save(os.path.join(out_dir, "log_prob.npy"), lp_all)
    np.save(os.path.join(out_dir, "flat.npy"), flat)

    names = [s.name for s in specs]
    nat_med = to_natural(np.median(flat, axis=0), specs)
    nat_map = to_natural(chain[i, j], specs)
    post = {}
    for k, nm in enumerate(names):
        col = np.array([to_natural(t, specs)[nm] for t in flat[::max(1, len(flat) // 400)]])
        lo, md, hi = np.percentile(col, [5, 50, 95])
        post[nm] = {"posterior_median": float(md), "ci90": [float(lo), float(hi)],
                    "map": float(nat_map[nm]),
                    "prior_lo": float(specs[k].lo), "prior_hi": float(specs[k].hi),
                    "width_ratio_vs_prior": float((hi - lo) / (specs[k].hi - specs[k].lo))}
    result = {
        "strain": strain, "label": label, "medium": medium, "otu": otu,
        "settings": {"c_max": c_max, "etc_table": etc_table,
                     "apply_proton_stoichiometry": bool(apply_protons),
                     "fit_clearance": bool(fit_clearance), "experiment": experiment},
        "data": ctx["meta"], "solver": solver,
        "preflight_single_eval_ms": round(pf_ms, 1),
        "sampler": {"n_walkers": n_walkers, "n_steps": done, "n_steps_max": n_steps_max,
                    "burn": burn, "thin": thin, "warm_started": bool(mode is not None),
                    "init": init_kind, "warm_start_rejected": bool(warm_rejected),
                    "moves": None if moves is None else str(moves),
                    "checkpoint": bool(checkpoint), "resumed": bool(resuming),
                    "sampler_kind": sampler_kind, "zeus": zinfo,
                    "target": {"tau_factor": tau_factor, "target_neff": target_neff},
                    "stop_reason": stop_reason, "converged": bool(converged),
                    "acceptance_fraction": round(accept, 3),
                    "autocorr_time_max": None if not np.isfinite(tau_max) else round(tau_max, 1),
                    "n_eff": round(float(n_eff), 1), "wall_time_s": round(wall, 1),
                    "n_proc": n_proc, "seed": seed},
        "posterior": post,
        "param_names": names,
    }
    with open(os.path.join(out_dir, "summary.json"), "w") as fh:
        json.dump(result, fh, indent=2)
    print(f"[fit] {label}: {done} steps x {n_walkers} walkers, {wall / 60:.1f} min, "
          f"accept {accept:.3f}, tau {tau_max:.1f}, "
          f"{'CONVERGED' if converged else 'NOT CONVERGED'} -> {out_dir}", flush=True)
    return result


def build_methanogen_specs() -> List[PSpec]:
    """Free set for the M. maripaludis Jones-1983 fit (M4). The methanogen ecModel is a
    SINGLE sMOMENT pool with NGAM(T) and NO sectors/growth-law (per M3), so the E. coli
    allocation levers (f_metab/f_maint/sigma_sat) have NO independent effect -- magnitude
    collapses onto ``kcat_scale`` (which absorbs the in-vitro->in-vivo gap, the residual
    archaeal-kcat underprediction, AND the pool/saturation/f_metab magnitude uncertainty).
    MAGNITUDE-FIRST: kcat_scale gets a LogNormal centred on the Davidi ~4x in-vitro->in-vivo
    median (broad) so walkers start where growth clears the measured maintenance. Envelope
    shape knobs correct the a-priori Topt (+5 C) and steep Ea (1.72 eV); the maintenance
    multipliers stay near 1 (Goyal 2015 NGAM is measured). sigma_disc MUST stay last."""
    return [
        PSpec("kcat_scale",    "log", "lognormal", 0.60, 4.0,  0.5, 25.0, "kcat_scale", 1.0),
        PSpec("dTopt",         "add", "normal",    5.0,  0.0, -15.0, 15.0, "dTopt", 0.0),
        PSpec("topt_scale",    "log", "lognormal", 0.15, 0.0,  0.4, 2.2, "topt_scale", 1.0),
        PSpec("dCp_scale",     "log", "lognormal", 0.45, 0.0,  0.2, 4.0, "dCp_scale", 1.0),
        PSpec("dTm",           "add", "normal",    4.0,  0.0, -12.0, 12.0, "dTm", 0.0),
        PSpec("tm_scale",      "log", "lognormal", 0.15, 0.0,  0.4, 2.2, "tm_scale", 1.0),
        PSpec("ngam_scale",    "log", "lognormal", 0.30, 0.0,  0.3, 3.0, "ngam_scale", 1.0),
        PSpec("ngam_steepness","log", "lognormal", 0.40, 0.0,  0.2, 4.0, "ngam_steepness", 1.0),
        PSpec("sigma_disc",    "log", "halfnormal", 0.50, 0.0, 1e-4, 5.0, None, None),
    ]


def build_syn6803_specs() -> List[PSpec]:
    """Free set for the Synechocystis 6803 Zavrel-2015 fit (P3). The P2 phototroph ecModel
    is a SINGLE sMOMENT pool (iSynCJ816_STAR) with NGAM(T) and NO sectors/growth-law, so —
    exactly as for the methanogen — the E. coli allocation levers (f_metab/f_maint/sigma_sat)
    have NO independent effect and are EXCLUDED (they become real levers only in P3b, the
    cyanobacterial allocation layer). SHAPE-FIRST (the opposite of the methanogen): the
    a-priori magnitude is already realistic (emergent rmax 0.067 vs Zavrel 0.097), so
    ``kcat_scale`` is a LogNormal centred on 1 (NOT the Davidi 4x) — it doubles as the
    'borrowed ecModel pool budget' check. The ENVELOPE knobs do the work of lowering the
    rising-limb SS-E 0.77 -> ~0.44: ``dCp_scale`` gets a BROAD LogNormal about 1 (the prime
    Ea lever — flatter MMRT curvature -> shallower rising limb) and ``topt_scale`` a moderate
    one (per-enzyme Topt heterogeneity, a legitimate aggregation route). dTopt/dTm are small
    (Topt 36->35, CTmax 45.7->44). Maintenance multipliers stay near 1 (Touloupakis 2015
    anchored). sigma_disc MUST stay last."""
    return [
        PSpec("kcat_scale",    "log", "lognormal", 0.40, 1.0,  0.3, 4.0, "kcat_scale", 1.0),
        PSpec("dTopt",         "add", "normal",    4.0,  0.0, -12.0, 12.0, "dTopt", 0.0),
        PSpec("topt_scale",    "log", "lognormal", 0.20, 0.0,  0.4, 2.2, "topt_scale", 1.0),
        PSpec("dCp_scale",     "log", "lognormal", 0.55, 0.0,  0.2, 4.0, "dCp_scale", 1.0),
        PSpec("dTm",           "add", "normal",    4.0,  0.0, -12.0, 12.0, "dTm", 0.0),
        PSpec("tm_scale",      "log", "lognormal", 0.15, 0.0,  0.4, 2.2, "tm_scale", 1.0),
        PSpec("ngam_scale",    "log", "lognormal", 0.30, 0.0,  0.3, 3.0, "ngam_scale", 1.0),
        PSpec("ngam_steepness","log", "lognormal", 0.40, 0.0,  0.2, 4.0, "ngam_steepness", 1.0),
        PSpec("sigma_disc",    "log", "halfnormal", 0.50, 0.0, 1e-4, 5.0, None, None),
    ]


def _syn6803_light_saturated_medium(model):
    """P1/P2 medium: photon non-limiting (light-saturated), inorganic C available,
    organic C closed -> carbon fixation limits, photon stays slack (in-mechanism)."""
    ids = {r.id for r in model.reactions}
    if "EX_glc__D_e" in ids:
        model.reactions.get_by_id("EX_glc__D_e").lower_bound = 0.0
    for oc in ("EX_ac_e", "EX_pyr_e", "EX_succ_e", "EX_glcglyc_e"):
        if oc in ids:
            model.reactions.get_by_id(oc).lower_bound = 0.0
    model.reactions.get_by_id("EX_co2_e").lower_bound = -1000.0
    model.reactions.get_by_id("EX_photon_e").lower_bound = -999999.0
    model.objective = "BIOMASS_Ec_SynAuto_1"


def _build_pm_syn6803(strain):
    """Provider at the Synechocystis 6803 light-saturated autotrophic operating point: the
    P2 thermal ecModel (from_gecko route-B on iSynCJ816_STAR, unfolding kcat(T)+f_N(T),
    NGAM(T) anchored on Touloupakis 2015), single sMOMENT pool (budget 0.26), NO sectors/
    growth law. Mirrors strains/syn6803/run_p2_thermal.py so calibration fits the same model."""
    from .providers import from_gecko
    from . import unfolding as U
    base = os.path.join("strains", strain)
    star = os.path.join(base, "model", "ecmodel_iSynCJ816_STAR", "iSynCJ816_STAR.xml")
    params = os.path.join(base, "thermal", "enzyme_thermal_params.csv")
    ngam_base_scale = 3.12 / U.ngam_T(273.15 + 35.0, scale=1.0)   # Touloupakis 2015 anchor
    pm = from_gecko(
        star, T0=273.15 + 35.0, thermal_model="unfolding",
        enzyme_params=params, enzyme_params_key="rxn_id", budget_override=0.26,
        ngam_temperature=True, ngam_rxn="ATPM", ngam_base_scale=ngam_base_scale,
        dcp_prior_kJ=-4.0, close_free_o2_sinks=False,
        prot_prefix="prot_", pool_id="prot_pool", biomass_rxn="BIOMASS_Ec_SynAuto_1")
    _syn6803_light_saturated_medium(pm.ec.model)
    try:
        pm.ec.model.solver.configuration.timeout = 2
    except Exception:
        pass
    return pm


# Synechocystis 6803 proteome-sector / allocation layer (P3b). Grounded in the organism's
# OWN allocation physiology (Jahn et al. 2018, Cell Reports 25:478; Zavrel et al. 2019, eLife
# 8:e42508; Faizi et al. 2018 framework; Suzuki et al. 2006 heat-shock for the maintenance-T
# note) -- NOT the bacterial Scott law, NOT the methanogen's flat law. From Jahn 2018 Fig 2A
# (seven sectors vs mu over 0.016-0.106/h): MAI ~33% (maintenance/regulation/hypothetical),
# RIB 16.5-16.9% (ribosome/translation, INCREASING with mu = the coupling slope), and the
# flux-carrying LHC(~15-19.6%)+PSET(~13%)+CBM(~14%)+GLM+LPB ~50% (light-harvesting -> metabolic
# mapping). Total cellular protein is invariant across growth (Jahn/Du/Touloupakis).
SYN6803_SECTOR_CFG = {
    "enabled": True,
    "P_total": None,          # back out from the P3 metabolic budget (0.26/0.50=0.52 g/gDW);
                              # Zavrel 2019 measured total protein ~0.402 g/gDW (corroboration)
    "f_metab": 0.50,          # LHC+PSET+CBM+GLM+LPB (Jahn 2018 Fig 2A; light-harvesting->metabolic)
    "f_maint": 0.33,          # MAI (Jahn 2018; "did not exceed 33%")
    "sigma_nom": 0.45,
    "atpm_reaction": "ATPM",
    "biosynthesis_growth_law": True,
    "growth_law_slope": 0.39,  # RIB rising limb, Jahn 2018 Fig 2A (per 1/h). Comparable per-mu to
                               # E. coli, but SMALL in absolute terms over the phototroph's tiny mu
                               # range (<=0.11/h) -> a small allocation buffer (to be measured).
    "growth_law_f_bio0": 0.133,  # RIB intercept = f_bio_nom(0.17) - slope*mu_op(~0.094)
    "nominal_kcat_scale": 1.22,  # P3 posterior-median kcat_scale (sector co-limit at operating point)
    "translation_coeff": 0.9,    # ribosome cap PINNED non-binding (as M6): Jahn's RIB is nearly
                                 # constant (16.5->16.9%), so the metabolic pool stays the binding
                                 # constraint (kcat(T)-limited, preserving Topt/the P3 fit) and the
                                 # small allocation buffer comes from the metabolic-sector shrinkage
                                 # (the +slope*P*v_bio growth-law term), not a clipping ribosome cap.
}


def _build_pm_syn6803_sectored(strain, cfg=None):
    """Phototroph provider (as _build_pm_syn6803) with the P3b cyanobacterial proteome-sector +
    coupled growth-law layer attached (reuses sectors.add_proteome_sectors; no fork). The
    metabolic pool stays at the P3-calibrated budget (P_total backed out), so the layer is
    additive; the RIB growth-law slope introduces the (small) allocation buffer."""
    from .sectors import add_proteome_sectors
    pm = _build_pm_syn6803(strain)
    add_proteome_sectors(pm, cfg or SYN6803_SECTOR_CFG)
    return pm


def load_zavrel(strain):
    """Load the digitised Zavrel 2015 light-saturated growth TPC, raw absolute rate (1/h)."""
    path = os.path.join("strains", strain, "thermal", "zavrel2015_tpc.csv")
    df = pd.read_csv(path, comment="#").sort_values("temperature_c")
    temps = df["temperature_c"].to_numpy(float)
    rates = df["growth_h"].to_numpy(float)
    meta = {"curve_id": "Zavrel2015_6803_lightsat", "study": "Zavrel et al. 2015 (Eng. Life Sci. 15:122)",
            "strain": "Synechocystis sp. PCC 6803 (GT)", "medium": "photoautotrophic, light-saturated",
            "n": int(len(df)), "temp_min_C": float(temps.min()), "temp_max_C": float(temps.max()),
            "obs_rmax": float(rates.max()), "obs_Topt_C": float(temps[int(np.argmax(rates))]),
            "units": "1/h", "has_sd": False}
    return temps, rates, meta


def _winit_syn6803(strain, solver_pref="gurobi", timeout=30.0):
    global _PM, _T, _OBS, _SPECS
    _set_default_solver(solver_pref)
    _PM = _build_pm_syn6803(strain)
    try:
        _PM.ec.model.solver.configuration.timeout = timeout
    except Exception:
        pass
    _T, _OBS, _ = load_zavrel(strain)
    _SPECS = build_syn6803_specs()


def run_syn6803(strain, out_dir, *, n_walkers=40, n_steps_max=6000, n_burn=150, seed=1,
                n_proc=0, check_every=200, target_neff=400, tau_factor=50,
                allow_glpk=False, warm_start=True, progress=True) -> Dict:
    """Emcee calibration of the Synechocystis 6803 thermal ecModel to the Zavrel 2015
    light-saturated growth TPC (single pool + NGAM(T), growth law OFF). SHAPE-FIRST. Same
    machinery as run_methanogen (warm-start, autocorr early-stop) at the phototroph
    operating point / curve / free set."""
    import emcee
    os.makedirs(out_dir, exist_ok=True)
    np.random.seed(seed)
    specs = build_syn6803_specs()
    ndim = len(specs)

    solver = _set_default_solver("gurobi")
    if solver != "gurobi":
        if not allow_glpk:
            raise SystemExit("[solver] Gurobi NOT active - stopping (set ALLOW_GLPK to override).")
        print("[solver] GLPK - slow; install gurobipy + academic licence (ALLOW_GLPK override)")
    else:
        print("[solver] gurobi")

    pm = _build_pm_syn6803(strain)
    try:
        pm.ec.model.solver.configuration.timeout = 30.0
    except Exception:
        pass
    temps, obs, meta = load_zavrel(strain)

    # pre-flight: the emergent point must grow and stay light-saturated (photon non-binding)
    pm.ec.set_temperature(35 + 273.15, Perturbation())
    t_pf = time.time(); g_pf = pm.ec.model.slim_optimize(); pf_ms = (time.time() - t_pf) * 1000
    status = getattr(pm.ec.model.solver, "status", "?")
    if g_pf is None or not np.isfinite(g_pf) or status != "optimal" or g_pf <= 0:
        raise SystemExit(f"[preflight] syn6803 ecModel did not grow at emergent point "
                         f"(status={status}, g={g_pf}).")
    sol = pm.ec.model.optimize()
    ph_shadow = abs(sol.reduced_costs.get("EX_photon_e", 0.0))
    print(f"[preflight] solve OK on {solver}: rmax(35C)={g_pf:.4f}, single-solve={pf_ms:.1f} ms; "
          f"photon shadow price={ph_shadow:.2e} (~0 => light-saturated / in-mechanism)")

    n_proc = n_proc or max(1, min(10, (os.cpu_count() or 2) - 2))
    n_walkers = int(np.ceil(max(n_walkers, 2 * ndim + 2) / n_proc)) * n_proc

    from multiprocessing import Pool
    pool = Pool(processes=n_proc, initializer=_winit_syn6803, initargs=(strain, solver, 30.0))
    t0 = time.time()
    try:
        if warm_start:
            p0, mode = _warm_start(specs, n_walkers, seed, pool, progress)
        else:
            p0, mode = init_walkers(specs, n_walkers, np.random.default_rng(seed)), None
        sampler = emcee.EnsembleSampler(n_walkers, ndim, _wlogprob, pool=pool)
        state = p0; done = 0; tau_max = float("nan")
        stop_reason = f"n_steps_max ({n_steps_max})"
        while done < n_steps_max:
            n = min(check_every, n_steps_max - done)
            state = sampler.run_mcmc(state, n, progress=progress)
            done += n
            try:
                tau = sampler.get_autocorr_time(tol=0); tau_max = float(np.nanmax(tau))
            except Exception:
                tau_max = float("nan")
            if np.isfinite(tau_max) and tau_max > 0:
                burn_now = min(int(max(n_burn, 2 * tau_max)), done - 10)
                n_eff_min = n_walkers * (done - burn_now) / tau_max
                need = tau_factor * tau_max
                print(f"[emcee] step {done}: tau_max={tau_max:.1f} chain/tau={done/tau_max:.1f} "
                      f"(need >{tau_factor}) min n_eff~{n_eff_min:.0f} (need >={target_neff})")
                if done > need and n_eff_min >= target_neff:
                    stop_reason = (f"converged: chain {done} > {tau_factor}*tau_max={need:.0f} "
                                   f"AND min n_eff {n_eff_min:.0f} >= {target_neff}")
                    break
            else:
                print(f"[emcee] step {done}: autocorr not yet estimable")
    finally:
        pool.close(); pool.join()
    wall = time.time() - t0

    burn = min(int(n_burn if not np.isfinite(tau_max) else max(n_burn, 2 * tau_max)), done - 10)
    thin = max(1, int(tau_max / 2)) if np.isfinite(tau_max) else 1
    flat = sampler.get_chain(discard=burn, thin=thin, flat=True)
    accept = float(np.mean(sampler.acceptance_fraction))
    n_eff = flat.shape[0] if not np.isfinite(tau_max) else float(n_walkers * (done - burn) / tau_max)

    result = {
        "strain": strain, "curve": meta, "medium": "photoautotrophic light-saturated",
        "operating_point": "syn6803 light-saturated autotrophy, thermal ecModel (unfolding+NGAM(T)), single sMOMENT pool, growth law OFF",
        "solver": solver, "preflight_single_solve_ms": round(pf_ms, 1),
        "preflight_photon_shadow_price": round(float(ph_shadow), 6),
        "sampler": {"n_walkers": n_walkers, "n_steps": done, "n_steps_max": n_steps_max,
                    "burn": burn, "thin": thin, "warm_started": bool(mode is not None),
                    "stop_reason": stop_reason, "acceptance_fraction": round(accept, 3),
                    "autocorr_time_max": None if not np.isfinite(tau_max) else round(tau_max, 1),
                    "n_eff": round(float(n_eff), 1), "wall_time_s": round(wall, 1),
                    "n_proc": n_proc, "seed": seed},
    }
    _finalise(out_dir, flat, pm, temps, obs, meta, specs, result)
    return result


def _build_pm_methanogen(strain):
    """Provider at the methanogen H2/CO2 operating point: the M3 thermal ecModel (unfolding
    kcat(T)+f_N(T), NGAM(T) anchored on Goyal 2015), single sMOMENT pool, NO sectors/growth
    law. The defined H2/CO2 medium is baked into the curated SBML, so no set_medium call."""
    from .config import resolve, build_provider
    pm = build_provider(resolve(strain))
    try:
        pm.ec.model.solver.configuration.timeout = 2
    except Exception:
        pass
    return pm


def load_jones(strain):
    """Load the digitised Jones 1983 growth TPC (H2/CO2), raw absolute rate (1/h)."""
    path = os.path.join("strains", strain, "thermal", "mmaripaludis_tpc_curves.csv")
    df = pd.read_csv(path, comment="#").sort_values("temp_C")
    temps = df["temp_C"].to_numpy(float)
    rates = df["mu_per_h"].to_numpy(float)
    meta = {"curve_id": "Jones1983_JJ_H2CO2", "study": "Jones, Paynter & Gupta 1983",
            "strain": "M. maripaludis (type strain JJ)", "medium": "H2/CO2 defined",
            "n": int(len(df)), "temp_min_C": float(temps.min()), "temp_max_C": float(temps.max()),
            "obs_rmax": float(rates.max()), "obs_Topt_C": float(temps[int(np.argmax(rates))]),
            "units": "1/h", "has_sd": False}
    return temps, rates, meta


def _winit_methanogen(strain, solver_pref="gurobi", timeout=30.0):
    global _PM, _T, _OBS, _SPECS
    _set_default_solver(solver_pref)
    _PM = _build_pm_methanogen(strain)
    try:
        _PM.ec.model.solver.configuration.timeout = timeout
    except Exception:
        pass
    _T, _OBS, _ = load_jones(strain)
    _SPECS = build_methanogen_specs()


def run_methanogen(strain, out_dir, *, n_walkers=40, n_steps_max=6000, n_burn=150, seed=1,
                   n_proc=0, check_every=200, target_neff=400, tau_factor=50,
                   allow_glpk=False, warm_start=True, progress=True) -> Dict:
    """Emcee calibration of the M. maripaludis thermal ecModel to the Jones 1983 TPC
    (H2/CO2, single pool + NGAM(T), growth law OFF). Same machinery as run() (warm-start,
    autocorr early-stop) but the methanogen operating point / curve / free set."""
    import emcee
    os.makedirs(out_dir, exist_ok=True)
    np.random.seed(seed)
    specs = build_methanogen_specs()
    ndim = len(specs)

    solver = _set_default_solver("gurobi")
    if solver != "gurobi":
        if not allow_glpk:
            raise SystemExit("[solver] Gurobi NOT active - stopping (set ALLOW_GLPK to override).")
        print("[solver] GLPK - slow; install gurobipy + academic licence (ALLOW_GLPK override)")
    else:
        print("[solver] gurobi")

    pm = _build_pm_methanogen(strain)
    try:
        pm.ec.model.solver.configuration.timeout = 30.0
    except Exception:
        pass
    temps, obs, meta = load_jones(strain)

    # pre-flight: at the Davidi kcat_scale prior centre the model must grow (clears NGAM)
    pm.ec.set_temperature(38 + 273.15, Perturbation(kcat_scale=4.0))
    t_pf = time.time(); g_pf = pm.ec.model.slim_optimize(); pf_ms = (time.time() - t_pf) * 1000
    status = getattr(pm.ec.model.solver, "status", "?")
    if g_pf is None or not np.isfinite(g_pf) or status != "optimal" or g_pf <= 0:
        raise SystemExit(f"[preflight] methanogen ecModel did not grow at kcat_scale=4 "
                         f"(status={status}, g={g_pf}); the magnitude-first init region is empty.")
    print(f"[preflight] solve OK on {solver}: rmax(38C, kcat_scale=4)={g_pf:.4f}, single-solve={pf_ms:.1f} ms")

    n_proc = n_proc or max(1, min(10, (os.cpu_count() or 2) - 2))
    n_walkers = int(np.ceil(max(n_walkers, 2 * ndim + 2) / n_proc)) * n_proc

    from multiprocessing import Pool
    pool = Pool(processes=n_proc, initializer=_winit_methanogen, initargs=(strain, solver, 30.0))
    t0 = time.time()
    try:
        if warm_start:
            p0, mode = _warm_start(specs, n_walkers, seed, pool, progress)
        else:
            p0, mode = init_walkers(specs, n_walkers, np.random.default_rng(seed)), None
        sampler = emcee.EnsembleSampler(n_walkers, ndim, _wlogprob, pool=pool)
        state = p0; done = 0; tau_max = float("nan")
        stop_reason = f"n_steps_max ({n_steps_max})"
        while done < n_steps_max:
            n = min(check_every, n_steps_max - done)
            state = sampler.run_mcmc(state, n, progress=progress)
            done += n
            try:
                tau = sampler.get_autocorr_time(tol=0); tau_max = float(np.nanmax(tau))
            except Exception:
                tau_max = float("nan")
            if np.isfinite(tau_max) and tau_max > 0:
                burn_now = min(int(max(n_burn, 2 * tau_max)), done - 10)
                n_eff_min = n_walkers * (done - burn_now) / tau_max
                need = tau_factor * tau_max
                print(f"[emcee] step {done}: tau_max={tau_max:.1f} chain/tau={done/tau_max:.1f} "
                      f"(need >{tau_factor}) min n_eff~{n_eff_min:.0f} (need >={target_neff})")
                if done > need and n_eff_min >= target_neff:
                    stop_reason = (f"converged: chain {done} > {tau_factor}*tau_max={need:.0f} "
                                   f"AND min n_eff {n_eff_min:.0f} >= {target_neff}")
                    break
            else:
                print(f"[emcee] step {done}: autocorr not yet estimable")
    finally:
        pool.close(); pool.join()
    wall = time.time() - t0

    burn = min(int(n_burn if not np.isfinite(tau_max) else max(n_burn, 2 * tau_max)), done - 10)
    thin = max(1, int(tau_max / 2)) if np.isfinite(tau_max) else 1
    flat = sampler.get_chain(discard=burn, thin=thin, flat=True)
    accept = float(np.mean(sampler.acceptance_fraction))
    n_eff = flat.shape[0] if not np.isfinite(tau_max) else float(n_walkers * (done - burn) / tau_max)

    result = {
        "strain": strain, "curve": meta, "medium": "H2/CO2",
        "operating_point": "methanogen H2/CO2, thermal ecModel (unfolding+NGAM(T)), single sMOMENT pool, growth law OFF",
        "solver": solver, "preflight_single_solve_ms": round(pf_ms, 1),
        "sampler": {"n_walkers": n_walkers, "n_steps": done, "n_steps_max": n_steps_max,
                    "burn": burn, "thin": thin, "warm_started": bool(mode is not None),
                    "stop_reason": stop_reason, "acceptance_fraction": round(accept, 3),
                    "autocorr_time_max": None if not np.isfinite(tau_max) else round(tau_max, 1),
                    "n_eff": round(float(n_eff), 1), "wall_time_s": round(wall, 1),
                    "n_proc": n_proc, "seed": seed},
    }
    _finalise(out_dir, flat, pm, temps, obs, meta, specs, result)
    return result


# ---------------------------------------------------------------------------
def to_natural(theta, specs) -> Dict[str, float]:
    out = {}
    for j, s in enumerate(specs):
        out[s.name] = float(np.exp(theta[j])) if s.space == "log" else float(theta[j])
    return out


def to_pert(theta, specs) -> Perturbation:
    nat = to_natural(theta, specs)
    kw = {s.pert: nat[s.name] for s in specs if s.pert is not None}
    return Perturbation(**kw)


def _nuisance_index(specs):
    for j, s in enumerate(specs):
        if s.pert is None:
            return j
    return len(specs) - 1


def log_prior(theta, specs) -> float:
    nat = to_natural(theta, specs)
    lp = 0.0
    for j, s in enumerate(specs):
        v = nat[s.name]
        if not (s.lo <= v <= s.hi):
            return -np.inf
        if s.prior == "normal":            # add-space Normal(loc, scale) on natural
            lp += -0.5 * ((v - s.loc) / s.scale) ** 2 - np.log(s.scale * np.sqrt(2 * np.pi))
        elif s.prior == "lognormal":       # Normal(log_center, scale) on the sampled log param
            lp += -0.5 * ((theta[j] - s.log_center) / s.scale) ** 2 - np.log(s.scale * np.sqrt(2 * np.pi))
        elif s.prior == "halfnormal":      # HalfNormal(scale) on natural + log-Jacobian
            lp += (-0.5 * (v / s.scale) ** 2 + np.log(np.sqrt(2 / np.pi) / s.scale)) + theta[j]
    return float(lp)


def log_likelihood(theta, pm, temps, obs, specs) -> float:
    sigma = float(np.exp(theta[_nuisance_index(specs)]))
    pred = compute_tpc(pm, temps, to_pert(theta, specs)).growth
    if not np.all(np.isfinite(pred)):
        return -np.inf
    r = obs - pred
    n = len(obs)
    return float(-0.5 * np.sum((r / sigma) ** 2) - n * np.log(sigma * np.sqrt(2 * np.pi)))


def init_walkers(specs, n_walkers, rng):
    cols = []
    for s in specs:
        if s.space == "log":
            cols.append(s.log_center + 0.6 * s.scale * rng.standard_normal(n_walkers) if s.prior == "lognormal"
                        else np.log(s.scale) + 0.2 * rng.standard_normal(n_walkers))
        else:  # add-space: centre on prior loc, 0.6x prior width
            cols.append(np.clip(s.loc + 0.6 * s.scale * rng.standard_normal(n_walkers), s.lo, s.hi))
    return np.column_stack(cols)


# ---------------------------------------------------------------------------
# operating point + curve
# ---------------------------------------------------------------------------
def _build_pm_rich(strain):
    """Provider at the RICH (BHI) operating point with the coupled growth law ON and
    a STATIC rich sector allocation (allocation_from_data disabled) so the fit's
    f_metab/f_maint drive the split. With the growth law ON the biosynthesis cap
    relaxes and the coupled metabolic sector binds, so kcat_scale is the effective
    magnitude lever."""
    from .config import resolve, build_provider
    from .providers import set_medium
    cfg = resolve(strain)
    cfg.setdefault("proteome_sectors", {})["biosynthesis_growth_law"] = True
    pm = build_provider(cfg)
    try:
        pm.ec.model.solver.configuration.timeout = 2
    except Exception:
        pass
    set_medium(pm, "BHI", bhi_media_csv=os.path.join("strains", strain, "media", "BHI_media.csv"))
    pm.ec._alloc_from_data = None   # static sectors -> pert.f_metab/f_maint are used
    return pm


def load_vanderlinden(strain):
    from . import validation as V
    spec = next(s for s in V.CURVES if s.key == "vanderlinden_bhi")
    cv = V.load_curve(strain, spec)
    meta = {"curve_id": "VanDerlinden2012_MG1655_BHI", "study": cv["study"],
            "strain": cv["strain"], "medium": "BHI", "n": int(len(cv["temps_C"])),
            "temp_min_C": float(cv["temps_C"].min()), "temp_max_C": float(cv["temps_C"].max()),
            "obs_rmax": float(cv["obs_rmax"]), "obs_Topt_C": float(cv["obs_Topt_C"]),
            "units": "1/h", "has_sd": False}
    return cv["temps_C"], cv["rate"], meta


# --- fast LP solver (PART A0a): Gurobi with graceful fallback ---
def _set_default_solver(pref="gurobi"):
    """Make cobra build new models on `pref`. Set BEFORE building the provider so
    the enzyme/sector constraint handles live on the fast interface (switching after
    build would leave stale optlang references). Returns the interface actually set."""
    import cobra
    try:
        cobra.Configuration().solver = pref
        return pref
    except Exception:
        try:
            cobra.Configuration().solver = "glpk"
        except Exception:
            pass
        return "glpk"


# --- multiprocessing globals ---
_PM = None
_T = None
_OBS = None
_SPECS = None


def _winit(strain, solver_pref="gurobi", timeout=30.0):
    global _PM, _T, _OBS, _SPECS
    _set_default_solver(solver_pref)   # spawn workers re-import fresh -> set here
    _PM = _build_pm_rich(strain)
    try:
        _PM.ec.model.solver.configuration.timeout = timeout
    except Exception:
        pass
    _T, _OBS, _ = load_vanderlinden(strain)
    _SPECS = build_vdl_specs()


def _wlogprob(theta):
    lp = log_prior(theta, _SPECS)
    if not np.isfinite(lp):
        return -np.inf
    return lp + log_likelihood(theta, _PM, _T, _OBS, _SPECS)


def _wnegpost(theta):
    """Negative log-posterior for the warm-start optimiser (finite penalty off-support)."""
    v = _wlogprob(theta)
    return 1e12 if not np.isfinite(v) else -float(v)


# --- warm start (PART A0c): DE to the mode, then a tight walker ball ---
def _theta_bounds(specs):
    return [(np.log(s.lo), np.log(s.hi)) if s.space == "log" else (s.lo, s.hi) for s in specs]


def _warm_start(specs, n_walkers, seed, pool, progress, negpost=None, logprob=None):
    """Return (p0, mode_theta_or_None). Run a short differential_evolution to the
    posterior mode over the process pool, then seed walkers in a tight ball around it
    (falls back to the emergent-point ball if the optimiser fails).

    ``negpost`` / ``logprob`` name the worker-side callables. They default to the ``run()``
    family's, which is what every earlier caller wants -- but a pool initialised for a
    DIFFERENT entry point has different globals, and calling the wrong pair makes every worker
    raise, which scipy surfaces as an opaque "map-like callable" error and the warm start then
    silently degrades to the emergent-point ball. P4's first run lost its warm start exactly
    that way (P4 DECISIONS D3).
    """
    negpost = negpost or _wnegpost
    logprob = logprob or _wlogprob
    ndim = len(specs)
    rng = np.random.default_rng(seed)
    mode = None
    try:
        from scipy.optimize import differential_evolution
        t0 = time.time()
        res = differential_evolution(
            negpost, _theta_bounds(specs), workers=pool.map, updating="deferred",
            maxiter=12, popsize=4, tol=0.03, mutation=(0.4, 1.0), recombination=0.8,
            init="sobol", polish=False, seed=seed)
        if np.isfinite(res.fun) and res.fun < 1e11:
            mode = np.asarray(res.x, float)
            print(f"[warm-start] DE mode found in {time.time()-t0:.0f}s "
                  f"(-logpost={res.fun:.1f}, {res.nit} gens)")
        else:
            print("[warm-start] DE did not find a finite mode; using emergent-point init")
    except Exception as e:
        print(f"[warm-start] optimiser failed ({e!r}); using emergent-point init")

    if mode is None:
        return init_walkers(specs, n_walkers, rng), None

    # tight ball around the mode; per-param width = 5% of the prior scale, clipped
    widths = np.array([0.05 * (s.scale if s.space == "log" else s.scale) for s in specs])
    lo = np.array([np.log(s.lo) if s.space == "log" else s.lo for s in specs])
    hi = np.array([np.log(s.hi) if s.space == "log" else s.hi for s in specs])
    p0 = np.clip(mode + widths * rng.standard_normal((n_walkers, ndim)), lo + 1e-6, hi - 1e-6)
    # guarantee every walker starts at finite log-prob (resample stragglers wider)
    lps = np.array(pool.map(logprob, [p0[i] for i in range(n_walkers)]))
    for i in np.where(~np.isfinite(lps))[0]:
        for _ in range(50):
            cand = np.clip(mode + 3 * widths * rng.standard_normal(ndim), lo + 1e-6, hi - 1e-6)
            if np.isfinite(_wlogprob_local(cand, specs)):
                p0[i] = cand
                break
    return p0, mode


def _wlogprob_local(theta, specs):
    # parent-process log-prior check (cheap; likelihood not needed for finiteness of prior)
    return log_prior(theta, specs)


# ---------------------------------------------------------------------------
def run(strain, out_dir, *, n_walkers=52, n_steps_max=6000, n_burn=150, seed=1,
        n_proc=0, check_every=200, target_neff=400, tau_factor=50,
        allow_glpk=False, warm_start=True, progress=True) -> Dict:
    """Emcee tuning at the rich BHI operating point (growth law ON, reconciled pool).
    Gurobi solver with stop-and-flag (A0a), warm-started at the DE mode (A0c) and run
    to an autocorrelation-based early stop (A0b: chain > tau_factor*max(tau) AND min
    n_eff >= target_neff), capped at n_steps_max. These only change speed, not the
    model / likelihood / priors / target posterior."""
    import emcee
    os.makedirs(out_dir, exist_ok=True)
    np.random.seed(seed)
    specs = build_vdl_specs()
    ndim = len(specs)

    # --- PART A0a: fast solver + stop-and-flag ---
    solver = _set_default_solver("gurobi")
    if solver != "gurobi":
        msg = ("[solver] Gurobi NOT active - the venv running this job is not seeing "
               "Gurobi. Expected [solver] gurobi. Stopping so you can fix the environment "
               "(activate the venv with gurobipy + ~/gurobi.lic) rather than run ~3 h on GLPK.")
        if not allow_glpk:
            raise SystemExit(msg)
        print("[solver] GLPK - slow; install gurobipy + academic licence (ALLOW_GLPK override set)")
    else:
        print("[solver] gurobi")

    pm = _build_pm_rich(strain)
    try:
        pm.ec.model.solver.configuration.timeout = 30.0
    except Exception:
        pass
    temps, obs, meta = load_vanderlinden(strain)

    # --- PART A0a: pre-flight full-size solve (fail on a licence/size problem NOW) ---
    pm.ec.set_temperature(40 + 273.15, Perturbation(f_metab=0.28, f_maint=0.36))
    pm.ec.set_allocation(0.28, 0.36)
    t_pf = time.time()
    g_pf = pm.ec.model.slim_optimize()
    pf_ms = (time.time() - t_pf) * 1000
    status = getattr(pm.ec.model.solver, "status", "?")
    if g_pf is None or not np.isfinite(g_pf) or status != "optimal":
        raise SystemExit(f"[preflight] full-size ecModel did NOT solve to optimality "
                         f"(status={status}). On Gurobi this indicates a size-limited (trial) "
                         f"licence rejecting the ~7,700-reaction model - install the free "
                         f"academic licence.")
    print(f"[preflight] full-size solve OK on {solver}: rmax(40C)={g_pf:.4f}, "
          f"single-solve={pf_ms:.1f} ms (GLPK is ~1,000-30,000 ms on degenerate theta)")

    n_proc = n_proc or max(1, min(10, (os.cpu_count() or 2) - 2))
    # keep n_walkers a multiple of the pool size and > 2*ndim (emcee requirement)
    n_walkers = int(np.ceil(max(n_walkers, 2 * ndim + 2) / n_proc)) * n_proc

    from multiprocessing import Pool
    pool = Pool(processes=n_proc, initializer=_winit, initargs=(strain, solver, 30.0))
    t0 = time.time()
    try:
        # --- PART A0c: warm start ---
        if warm_start:
            p0, mode = _warm_start(specs, n_walkers, seed, pool, progress)
        else:
            p0, mode = init_walkers(specs, n_walkers, np.random.default_rng(seed)), None

        sampler = emcee.EnsembleSampler(n_walkers, ndim, _wlogprob, pool=pool)

        # --- PART A0b: convergence-based early stop ---
        state = p0
        done = 0
        tau_max = float("nan")
        stop_reason = f"n_steps_max ({n_steps_max})"
        while done < n_steps_max:
            n = min(check_every, n_steps_max - done)
            state = sampler.run_mcmc(state, n, progress=progress)
            done += n
            try:
                tau = sampler.get_autocorr_time(tol=0)
                tau_max = float(np.nanmax(tau))
            except Exception:
                tau_max = float("nan")
            if np.isfinite(tau_max) and tau_max > 0:
                burn_now = min(int(max(n_burn, 2 * tau_max)), done - 10)
                n_eff_min = n_walkers * (done - burn_now) / tau_max
                need = tau_factor * tau_max
                print(f"[emcee] step {done}: tau_max={tau_max:.1f}  chain/tau={done/tau_max:.1f} "
                      f"(need >{tau_factor})  min n_eff~{n_eff_min:.0f} (need >={target_neff})")
                if done > need and n_eff_min >= target_neff:
                    stop_reason = (f"converged: chain {done} > {tau_factor}*tau_max={need:.0f} "
                                   f"AND min n_eff {n_eff_min:.0f} >= {target_neff}")
                    break
            else:
                print(f"[emcee] step {done}: autocorr not yet estimable")
    finally:
        pool.close(); pool.join()
    wall = time.time() - t0

    burn = min(int(n_burn if not np.isfinite(tau_max) else max(n_burn, 2 * tau_max)), done - 10)
    thin = max(1, int(tau_max / 2)) if np.isfinite(tau_max) else 1
    flat = sampler.get_chain(discard=burn, thin=thin, flat=True)
    accept = float(np.mean(sampler.acceptance_fraction))
    n_eff = flat.shape[0] if not np.isfinite(tau_max) else float(n_walkers * (done - burn) / tau_max)

    result = {
        "strain": strain, "curve": meta, "medium": "BHI",
        "operating_point": "rich (BHI), growth law ON, reconciled single pool (v3)",
        "solver": solver, "preflight_single_solve_ms": round(pf_ms, 1),
        "sampler": {"n_walkers": n_walkers, "n_steps": done, "n_steps_max": n_steps_max,
                    "burn": burn, "thin": thin, "warm_started": bool(mode is not None),
                    "stop_reason": stop_reason,
                    "acceptance_fraction": round(accept, 3),
                    "autocorr_time_max": None if not np.isfinite(tau_max) else round(tau_max, 1),
                    "n_eff": round(float(n_eff), 1), "wall_time_s": round(wall, 1),
                    "n_proc": n_proc, "seed": seed},
    }
    _finalise(out_dir, flat, pm, temps, obs, meta, specs, result)
    return result


# ---------------------------------------------------------------------------
def _ci(x, q=(5, 50, 95)):
    return [float(v) for v in np.percentile(x, q)]


def _finalise(out_dir, flat, pm, temps, obs, meta, specs, result):
    np.save(os.path.join(out_dir, "chain_flat.npy"), flat)
    names = [s.name for s in specs]
    nat = np.column_stack([np.exp(flat[:, j]) if s.space == "log" else flat[:, j]
                           for j, s in enumerate(specs)])

    rows, summary = [], {}
    for j, s in enumerate(specs):
        lo, med, hi = _ci(nat[:, j])
        # constrained if the posterior 90% CI is materially tighter than the prior
        if s.prior == "lognormal":
            prior_w = 2 * 1.645 * s.scale
            post_w = np.log(max(hi, 1e-9)) - np.log(max(lo, 1e-9))
        else:
            prior_w = 2 * 1.645 * s.scale
            post_w = hi - lo
        constrained = bool(post_w < 0.7 * prior_w)
        if s.space == "log":
            corr = f"x{med:.2f}"
        elif s.name in ("f_metab", "f_maint"):
            corr = f"{med:.3f} (meas {s.emergent:.3f})"
        elif s.name == "sigma":
            corr = f"{med:.3f} (nom {s.emergent:.3f}, lit 0.4-0.5)"
        elif s.pert is None:
            corr = f"{med:.3f} 1/h"
        else:
            corr = f"{med:+.1f} K"
        summary[s.name] = {"emergent": s.emergent, "posterior_median": round(med, 4),
                           "posterior_90CI": [round(lo, 4), round(hi, 4)],
                           "demanded_correction": corr,
                           "constrained_by_curve": None if s.pert is None else constrained}
        rows.append({"parameter": s.name, "emergent": s.emergent,
                     "posterior_median": round(med, 4), "ci5": round(lo, 4), "ci95": round(hi, 4),
                     "demanded_correction": corr,
                     "constrained_by_curve": (None if s.pert is None else constrained)})
    pd.DataFrame(rows).to_csv(os.path.join(out_dir, "demanded_corrections.csv"), index=False)
    result["posterior"] = summary

    # descriptors: prior (emergent) vs posterior-median vs observed
    dense = np.linspace(min(float(temps.min()), 5.0), max(float(temps.max()), 52.0),
                        int(round((max(float(temps.max()), 52.0) - min(float(temps.min()), 5.0)) / 1.5)) + 1)
    emergent_theta = np.array([np.log(s.emergent) if s.space == "log" else s.emergent
                               for s in specs[:-1]] + [np.log(0.3)])
    prior_curve = compute_tpc(pm, dense, to_pert(emergent_theta, specs)).growth
    med_theta = np.array([np.median(flat[:, j]) for j in range(len(specs))])
    post_curve = compute_tpc(pm, dense, to_pert(med_theta, specs)).growth
    d_obs = TPC(temps, obs).descriptors(0.05)
    d_pri = TPC(dense, prior_curve).descriptors(0.05)
    d_post = TPC(dense, post_curve).descriptors(0.05)
    result["descriptors"] = {
        "observed": {k: round(getattr(d_obs, a), 3) for k, a in
                     [("rmax", "rmax"), ("Topt_C", "Topt_C"), ("Ea_eV", "Ea_eV"), ("CTmax_C", "CTmax_C")]},
        "emergent_prior": {k: round(getattr(d_pri, a), 3) for k, a in
                           [("rmax", "rmax"), ("Topt_C", "Topt_C"), ("Ea_eV", "Ea_eV"), ("CTmax_C", "CTmax_C")]},
        "posterior_median": {k: round(getattr(d_post, a), 3) for k, a in
                             [("rmax", "rmax"), ("Topt_C", "Topt_C"), ("Ea_eV", "Ea_eV"), ("CTmax_C", "CTmax_C")]},
    }

    # posterior-predictive band
    rng = np.random.default_rng(0)
    n_pp = min(150, flat.shape[0])
    pick = rng.choice(flat.shape[0], size=n_pp, replace=False)
    pp = np.vstack([compute_tpc(pm, dense, to_pert(flat[i], specs)).growth for i in pick])
    lo, md, hi = np.percentile(pp, [5, 50, 95], axis=0)
    np.savez(os.path.join(out_dir, "posterior_predictive.npz"), temps_C=dense,
             lo=lo, med=md, hi=hi, prior=prior_curve, obs_T=temps, obs=obs)
    with open(os.path.join(out_dir, "summary.json"), "w") as fh:
        json.dump(result, fh, indent=2)

    _plot_prior_vs_posterior(out_dir, dense, prior_curve, lo, md, hi, temps, obs, meta)
    _plot_corner(out_dir, nat, names, specs)


def _plot_prior_vs_posterior(out_dir, T, prior, lo, med, hi, obsT, obs, meta):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.fill_between(T, lo, hi, color="tab:orange", alpha=0.25, label="posterior predictive 90% CI")
    ax.plot(T, med, color="tab:orange", lw=2, label="posterior median")
    ax.plot(T, prior, color="tab:blue", lw=2, ls="--", label="emergent prior")
    ax.plot(obsT, obs, "o", color="k", ms=5, label=f"data ({meta['study'][:24]}…, digitized)")
    ax.set_xlabel("Temperature (°C)"); ax.set_ylabel("Growth rate (1/h)")
    _med = meta.get("medium", meta.get("medium_class", ""))
    ax.set_title(f"Prior vs posterior — {meta['study'][:30]} ({_med}), n={meta['n']}")
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    fig.tight_layout()
    p = os.path.join(out_dir, "prior_vs_posterior_tpc.png")
    fig.savefig(p, dpi=150); plt.close(fig)
    return p


def _plot_corner(out_dir, nat, names, specs):
    import matplotlib
    matplotlib.use("Agg")
    import corner
    import matplotlib.pyplot as plt
    truths = [s.emergent for s in specs]
    fig = corner.corner(nat, labels=names, show_titles=True, title_fmt=".2f",
                        quantiles=[0.05, 0.5, 0.95], truths=truths)
    p = os.path.join(out_dir, "corner.png")
    fig.savefig(p, dpi=130); plt.close(fig)
    return p
