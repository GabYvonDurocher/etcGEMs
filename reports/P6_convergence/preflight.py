#!/usr/bin/env python3
"""P6 TASK 0 pre-flight. Three things, each read back rather than assumed.

1. SETTINGS: for each of the nine fits, build the provider config exactly as the runner will and
   read c_max, the ETC table, proton stoichiometry, medium and clearance sampling back OUT of the
   resolved config. The three LB fits must show c_max 450 (P5), not the scalar 120.
2. TAU: re-measure the integrated autocorrelation time on P4's nine committed chains with the
   same estimator, and from it the steps needed for chain/tau >= 25 (the adopted target, TASK 0c)
   and >= 40 (the stricter one), with a wall-clock estimate from P4's own measured s/step.
3. JITTER: the likelihood is re-evaluated at one fixed parameter vector (P4's MAP) six times,
   alternating with a second vector, per configuration; the spread is the non-determinism emcee
   is being asked to sample through (user addendum 3; P5 saw 0.02 for configuration E).

Writes preflight_settings.csv, preflight_tau.csv, preflight_jitter.csv beside this file.
"""
import json
import os
import sys
import time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, HERE)
os.chdir(ROOT)

import emcee                                                                              # noqa: E402
from etcgem.calibration_multi import build_gasflux_pm, _build_gasflux_ctx, gasflux_log_likelihood  # noqa: E402
from p6_fits import FITS, p4_dir_for, LB_CMAX                                            # noqa: E402

OUTS = os.path.join(ROOT, "strains", "eciML1515", "outputs")


def settings():
    rows = []
    for label, cfg_name, medium, table, otu, c_max, etc_table, protons, fit_k in FITS:
        _, cfg = build_gasflux_pm("eciML1515", medium, f"gasflux_config{cfg_name}", c_max=c_max,
                                  etc_table=etc_table)
        gf = cfg["gasflux"]
        cc = gf.get("total_carbon_cap") or {}
        ea = gf.get("etc_area") or {}
        rows.append(dict(fit=label, config=cfg_name, medium=gf.get("medium"), media=str(gf.get("media")),
                         cap_enabled=bool(cc.get("enabled")), c_max_resolved=cc.get("c_max") if cc.get("enabled") else None,
                         c_max_requested=c_max, etc_enabled=bool(ea.get("enabled")), etc_table=ea.get("table"),
                         protons_config=bool(ea.get("apply_proton_stoichiometry")), protons_requested=protons,
                         fit_clearance=fit_k, data_table=table, otu=otu,
                         growth_law=cfg.get("proteome_sectors", {}).get("biosynthesis_growth_law"),
                         allocation_from_data=cfg.get("allocation_from_data")))
        r = rows[-1]
        ok = (r["c_max_resolved"] == c_max) if c_max is not None else (not r["cap_enabled"])
        print(f"[settings] {label:7s} medium={r['medium']:16s} cap={'ON ' if r['cap_enabled'] else 'off'} "
              f"c_max={r['c_max_resolved']}  etc={r['etc_table']}  protons(cfg)={r['protons_config']} "
              f"clearance_sampled={fit_k}  {'OK' if ok else 'MISMATCH'}", flush=True)
        if not ok:
            raise SystemExit(f"[settings] {label}: resolved c_max {r['c_max_resolved']} != requested {c_max}")
        if medium == "LB" and r["c_max_resolved"] != LB_CMAX:
            raise SystemExit(f"[settings] {label}: LB c_max is {r['c_max_resolved']}, not P5's {LB_CMAX}")
    pd.DataFrame(rows).to_csv(os.path.join(HERE, "preflight_settings.csv"), index=False)


def tau_targets():
    rows = []
    for label, cfg_name, medium, *_ in FITS:
        d = os.path.join(OUTS, p4_dir_for(cfg_name, medium))
        ch = np.load(os.path.join(d, "chain.npy"))
        s = json.load(open(os.path.join(d, "summary.json")))["sampler"]
        tau = emcee.autocorr.integrated_time(ch, tol=0)
        tmax = float(np.max(tau)); steps, nw = ch.shape[0], ch.shape[1]
        s_per_step = s["wall_time_s"] / s["n_steps"]
        rows.append(dict(fit=label, p4_steps=steps, walkers=nw, tau_max_remeasured=round(tmax, 1),
                         tau_max_p4=s["autocorr_time_max"], chain_over_tau_p4=round(steps / tmax, 1),
                         n_eff_p4_walkers_steps_over_tau=round(nw * steps / tmax),
                         steps_for_25tau=int(np.ceil(25 * tmax)), steps_for_40tau=int(np.ceil(40 * tmax)),
                         s_per_step_p4=round(s_per_step, 2),
                         hours_25tau_fresh=round(25 * tmax * s_per_step / 3600, 2),
                         hours_40tau_fresh=round(40 * tmax * s_per_step / 3600, 2)))
        print(f"[tau] {label:7s} tau {tmax:6.1f} (P4 {s['autocorr_time_max']})  chain/tau {steps/tmax:4.1f}  "
              f"25tau={25*tmax:.0f} steps ({25*tmax*s_per_step/3600:.1f} h)  40tau={40*tmax:.0f} ({40*tmax*s_per_step/3600:.1f} h)", flush=True)
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(HERE, "preflight_tau.csv"), index=False)
    print(f"[tau] TOTAL fresh, stretch move at P4's rates: 25tau {df.hours_25tau_fresh.sum():.1f} h, 40tau {df.hours_40tau_fresh.sum():.1f} h", flush=True)


def jitter():
    rows = []
    for label, cfg_name, medium, table, otu, c_max, etc_table, protons, fit_k in FITS:
        ctx, specs = _build_gasflux_ctx(strain="eciML1515", medium=medium, experiment=f"gasflux_config{cfg_name}",
                                        table=table, otu=otu, c_max=c_max, etc_table=etc_table,
                                        apply_protons=protons, fit_clearance=fit_k)
        d = os.path.join(OUTS, p4_dir_for(cfg_name, medium))
        ch = np.load(os.path.join(d, "chain.npy")); lp = np.load(os.path.join(d, "log_prob.npy"))
        i, j = np.unravel_index(np.nanargmax(lp), lp.shape)
        th0 = ch[i, j]; th1 = ch[-1, 0]          # the MAP, and one final-state walker
        vals0, vals1, t0 = [], [], time.time()
        for _ in range(6):
            vals0.append(gasflux_log_likelihood(th0, ctx, specs))
            vals1.append(gasflux_log_likelihood(th1, ctx, specs))
        ms = (time.time() - t0) * 1000 / 12
        j0, j1 = float(np.ptp(vals0)), float(np.ptp(vals1))
        rows.append(dict(fit=label, logL_MAP_first=vals0[0], jitter_MAP=j0, logL_other_first=vals1[0], jitter_other=j1,
                         max_jitter=max(j0, j1), ms_per_eval=round(ms, 0),
                         reapplies=("clearance" if fit_k else "") + ("+ETC" if etc_table else "")))
        print(f"[jitter] {label:7s} logL(MAP) {vals0[0]:9.3f}  spread {j0:.4f}   other {vals1[0]:9.3f} spread {j1:.4f}   "
              f"({ms:.0f} ms/eval; re-applies: {rows[-1]['reapplies'] or 'nothing'})", flush=True)
    pd.DataFrame(rows).to_csv(os.path.join(HERE, "preflight_jitter.csv"), index=False)


if __name__ == "__main__":
    settings()
    tau_targets()
    jitter()
    print("[preflight] done", flush=True)
