#!/usr/bin/env python3
"""P5 TASK 1e -- can each configuration be re-tuned to the OTHER cap? (deterministic, no emcee)

task1d held Parsa's parameters fixed and moved the cap; that favours the cap each point was
fitted under. Here the parameters are re-optimised (Powell on the log-posterior, 600
evaluations, from his MAP) at a cap the point was NOT fitted under: D at 450, E and F at 257,
plus each at its own cap as the control. Same model construction as P4's refits
(_build_gasflux_ctx; E with its ETC table, F with E's areas plus non-electrogenic bd-II).

Reads his chains under $PARSA_ROOT (READ ONLY). Writes reoptimise.csv beside this file.
"""
import json
import os
import sys
import time

import numpy as np
import pandas as pd
from scipy.optimize import minimize

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "reports", "P4_refit"))
sys.path.insert(0, os.path.join(ROOT, "reports", "P3_gate"))
os.chdir(ROOT)

from etcgem.calibration_multi import (_build_gasflux_ctx, gasflux_log_likelihood, log_prior,  # noqa: E402
                                      to_pert, to_natural)
from etcgem.gasflux import flux_tpc                                                          # noqa: E402
from run_fits import r2, DENSE                                                               # noqa: E402
from fits import E_TABLE, F_TABLE, R2A_LB                                                    # noqa: E402
import gate_def as G                                                                         # noqa: E402

PARSA = os.environ.get("PARSA_ROOT", "/Users/g.yvon-durocher/Downloads/etcGEMs-main_3")
CHAINS = os.path.join(PARSA, "strains", "eciML1515", "outputs")
# config, his run, our etc table, protons, caps to re-optimise at
JOBS = [("D", "calibration_configD_LB_full",     None,    False, (257.0, 450.0)),
        ("E", "calibration_configE_LB_freecmax", E_TABLE, False, (257.0, 450.0)),
        ("F", "calibration_configF_LB",          F_TABLE, True,  (257.0, 450.0))]
MAXFEV = int(os.environ.get("P5_MAXFEV", "600"))
RENAME = {"F_ETC_LB_mult": "F_ETC_mult"}


def his_theta_in_our_specs(cdir, specs):
    cfg = json.load(open(os.path.join(cdir, "meta.json"))).get("cfg") or {}
    his_specs = G.build_specs("LB", cfg)
    th_map, _, _, _ = G.read_points(cdir)
    nat = {RENAME.get(s.name, s.name): float(th_map[j]) for j, s in enumerate(his_specs)}   # sampled-space values
    k = [s.name for s in his_specs].index("C_max_LB_mult")
    his_cap = (G.CAP_NOM_E["LB"] if cfg.get("use_etc") else G.CAP_NOM["LB"]) * float(np.exp(th_map[k]))
    ours = [s.name for s in specs]
    missing = [n for n in ours if n not in nat]
    assert not missing, (missing, list(nat))
    return np.array([nat[n] for n in ours], float), his_cap


def score_point(theta, ctx, specs):
    nat = to_natural(theta, specs)
    df = flux_tpc(ctx["pm"], DENSE, to_pert(theta, specs), metabolites=("o2",))
    g = df["growth"].to_numpy(float)
    rr = df["o2_uptake"].to_numpy(float) * ctx["o2_conv"] * float(nat["resp_scale"])
    ll = gasflux_log_likelihood(theta, ctx, specs)
    return dict(growth_R2=r2(ctx["growth_obs"], ctx["T"], g, DENSE), resp_R2=r2(ctx["resp_obs"], ctx["T"], rr, DENSE),
                rmax=float(np.nanmax(g)), Topt_C=float(DENSE[int(np.nanargmax(g))]), logL=ll,
                logpost=ll + log_prior(theta, specs), kcat_scale=nat["kcat_scale"])


def main():
    rows = []
    for conf, run, etc, protons, caps in JOBS:
        cdir = os.path.join(CHAINS, run)
        for cap in caps:
            ctx, specs = _build_gasflux_ctx(strain="eciML1515", medium="LB", experiment=f"gasflux_config{conf}",
                                            table=R2A_LB, otu=2, c_max=cap, etc_table=etc,
                                            apply_protons=protons, fit_clearance=False)
            th0, his_cap = his_theta_in_our_specs(cdir, specs)
            s0 = score_point(th0, ctx, specs)
            rows.append(dict(config=conf, c_max=cap, his_cap=round(his_cap, 1), stage="his MAP, fixed", **s0))
            print(f"[reopt] {conf} cap {cap:g}  his MAP fixed      growth R2 {s0['growth_R2']:7.3f}  resp R2 {s0['resp_R2']:7.3f}  rmax {s0['rmax']:.3f}  logpost {s0['logpost']:.2f}", flush=True)
            t0 = time.time()
            f = lambda th: -(gasflux_log_likelihood(th, ctx, specs) + log_prior(th, specs))
            res = minimize(f, th0, method="Powell", options=dict(maxfev=MAXFEV, xtol=1e-3, ftol=1e-3))
            s1 = score_point(res.x, ctx, specs)
            rows.append(dict(config=conf, c_max=cap, his_cap=round(his_cap, 1), stage="Powell from his MAP", nfev=int(res.nfev), **s1))
            print(f"[reopt] {conf} cap {cap:g}  Powell re-optimised growth R2 {s1['growth_R2']:7.3f}  resp R2 {s1['resp_R2']:7.3f}  rmax {s1['rmax']:.3f}  logpost {s1['logpost']:.2f}  ({res.nfev} evals, {(time.time()-t0)/60:.1f} min)", flush=True)
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(HERE, "reoptimise.csv"), index=False)
    pd.set_option("display.width", 220)
    print(df.round(3).to_string(index=False))
    print("[reopt] done", flush=True)


if __name__ == "__main__":
    main()
