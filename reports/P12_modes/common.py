#!/usr/bin/env python3
"""P12 -- shared pieces: the three fixed points, the likelihood in force, and a per-term
decomposition of it. The likelihood is P10's with both options ON for eciML1515 (tie-break pfba
at 1e-9, log-O2 floor 1.42, continuous support at 0.01), read from the strain config; nothing
here changes it."""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
for p in (os.path.join(ROOT, "src"), os.path.join(ROOT, "reports", "P6_convergence"),
          os.path.join(ROOT, "reports", "P11_nested"), os.path.join(ROOT, "reports", "P9_surface")):
    if p not in sys.path: sys.path.insert(0, p)
os.chdir(ROOT)
from etcgem.calibration_multi import (_build_gasflux_ctx, gasflux_log_likelihood, log_prior,   # noqa: E402
                                      to_natural, to_pert, build_gasflux_specs, _MASK_G)
from etcgem.gasflux import flux_tpc, add_total_carbon_constraint                               # noqa: E402
from etcgem import providers as _prov                                                          # noqa: E402
from p6_fits import FITS                                                                       # noqa: E402

FIT = [f for f in FITS if f[0] == "D_NLDM"][0]
LABEL, CFG, MEDIUM, TABLE, OTU, C_MAX, ETC, PROTONS, FIT_K = FIT
PAYLOAD = dict(strain="eciML1515", medium=MEDIUM, experiment=f"gasflux_config{CFG}", table=TABLE, otu=OTU,
               c_max=C_MAX, etc_table=ETC, apply_protons=PROTONS, fit_clearance=FIT_K)
SPECS = build_gasflux_specs({"use_etc": ETC is not None, "fit_clearance": FIT_K})
NAMES = [s.name for s in SPECS]
NEST = os.path.join(ROOT, "strains", "eciML1515", "outputs", "calibration_configD_NLDM_recipe_P11_nested")
P4DIR = os.path.join(ROOT, "strains", "eciML1515", "outputs", "calibration_configD_NLDM_recipe_cmax120")


def build():
    return _build_gasflux_ctx(**PAYLOAD)


def fixed_points():
    """theta_A (P11 main median), theta_B (P11 seed-2 median), theta_P4 (P4 median), sampled space."""
    from task3_posterior import equal_weight
    A, _, _ = equal_weight("main"); B, _, _ = equal_weight("seed2")
    ch = np.load(os.path.join(P4DIR, "chain.npy")); burn = int(2 * 244.7)
    return dict(A=np.median(A, axis=0), B=np.median(B, axis=0),
                P4=np.median(ch[burn:].reshape(-1, ch.shape[2]), axis=0))


def decompose(th, ctx, sp):
    """the likelihood's own arithmetic, per temperature and per term, at theta."""
    resp = ctx.get("respiration") or {}
    nat = to_natural(th, sp); pert = to_pert(th, sp); pm = ctx["pm"]
    if "clearance_mult" in nat:
        r = ctx["recipe"]
        _prov.set_medium_recipe(pm, r["recipe_csv"], clearance_L_per_gDW_h=r["clearance"] * float(nat["clearance_mult"]),
                                uptake_ub=r.get("uptake_ub", 1000.0), verbose=False)
        if ctx.get("c_max") is not None:
            add_total_carbon_constraint(pm, float(ctx["c_max"]))
    df = flux_tpc(pm, ctx["T"], pert, metabolites=("o2",), tiebreak=str(resp.get("tiebreak", "none")),
                  growth_tol=float(resp.get("growth_tol", 1e-6)), tiebreak_tol=float(resp.get("tiebreak_tol", 1e-9)))
    g = df["growth"].to_numpy(float); o2 = df["o2_uptake"].to_numpy(float)
    dg = float(nat["disc_growth"]); var = ctx["growth_sd"] ** 2 + dg ** 2
    gterm = -0.5 * ((ctx["growth_obs"] - g) ** 2 / var + np.log(2 * np.pi * var))
    keep = (g >= _MASK_G) & (o2 > 0); dr = float(nat["disc_resp"]); rs = float(nat["resp_scale"])
    floor = float(resp.get("log_o2_floor", 0.0)); gs = resp.get("alive_soft_growth")
    rterm = np.zeros_like(g); w = np.zeros_like(g)
    if keep.any():
        pred = np.log(o2[keep] * ctx["o2_conv"] * rs); obsl = np.log(ctx["resp_obs"][keep])
        rel = ctx["resp_sd"][keep] / ctx["resp_obs"][keep]; varr = rel ** 2 + dr ** 2 + floor ** 2
        w[keep] = np.minimum(1.0, g[keep] / float(gs)) if gs else 1.0
        rterm[keep] = -0.5 * w[keep] * ((obsl - pred) ** 2 / varr + np.log(2 * np.pi * varr))
    return dict(T=ctx["T"], growth=g, o2=o2, weight=w, growth_term=gterm, resp_term=rterm,
                growth_obs=ctx["growth_obs"], resp_obs=ctx["resp_obs"],
                total=float(gterm.sum() + rterm.sum()), logl=float(gasflux_log_likelihood(th, ctx, sp)),
                logprior=float(log_prior(th, SPECS)))
