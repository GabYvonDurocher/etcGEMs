#!/usr/bin/env python3
"""P6 TASK 1 -- run the scoped fits to the adopted convergence target, committing after each.

What runs: p6_fits.RUN -- configuration D on NLDM, LB and M9 (E and F are stopped, DECISIONS
D3). What is fixed: everything P4 fitted, except the three things the prompt allows to change:
  * chain length      -- n_steps_max = 1.2 x (25 x tau_P4) per fit, so a fit either reaches the
                         target or is reported NOT CONVERGED at the target length;
  * sampler config    -- move set and process count from sampler_config.json (TASK 0b);
  * LB's c_max        -- 450, from the strain data (P5), read back by preflight.py.
Target (TASK 0c): n_eff >= 600 AND chain/tau >= 25, checked every 250 steps; the driver stops the
fit there. chain/tau >= 40 is reported alongside, never required.

Initialisation: P4's final ensemble state for the same fit (DECISIONS D2); tau, n_eff and the
posterior are computed on the new chain only. No warm start.

Resumable: a fit whose summary.json exists is scored and skipped.

    python reports/P6_convergence/run_fits.py [--only D_NLDM,D_LB] [--no-commit]
"""
import argparse
import json
import os
import subprocess
import sys
import time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "reports", "P4_refit"))
os.chdir(ROOT)

import emcee                                                     # noqa: E402
from etcgem.calibration_multi import run_gasflux_fit             # noqa: E402
from run_fits import score                                       # noqa: E402  (P4's scorer, unchanged)
from p6_fits import RUN, out_dir_for, p4_dir_for                 # noqa: E402

OUTS = os.path.join(ROOT, "strains", "eciML1515", "outputs")
TARGET_NEFF, TAU_FACTOR, STRICT = 600, 25, 40
TABLE = os.path.join(HERE, "fits_table.csv")


def git(*args):
    return subprocess.run(["git", "-C", ROOT, *args], capture_output=True, text=True)


def sampler_config():
    p = os.path.join(HERE, "sampler_config.json")
    c = json.load(open(p))
    moves = None
    if c.get("moves") == "DE+Snooker":
        moves = [(emcee.moves.DEMove(), 0.8), (emcee.moves.DESnookerMove(), 0.2)]
    return moves, int(c["n_proc"]), c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default=None)
    ap.add_argument("--no-commit", action="store_true")
    args = ap.parse_args()
    want = set(args.only.split(",")) if args.only else None
    moves, n_proc, sc = sampler_config()
    tau_p4 = pd.read_csv(os.path.join(HERE, "preflight_tau.csv")).set_index("fit")
    print(f"[p6] sampler: moves={sc.get('moves')} n_proc={n_proc} ({sc.get('reason', '')})", flush=True)
    t_all = time.time()
    for label, cfg, medium, table, otu, c_max, etc_table, protons, fit_k in RUN:
        if want and label not in want:
            continue
        rel = os.path.join("strains", "eciML1515", "outputs", out_dir_for(cfg, medium))
        out_dir = os.path.join(ROOT, rel)
        p4 = os.path.join(OUTS, p4_dir_for(cfg, medium))
        init = np.load(os.path.join(p4, "chain.npy"))[-1]
        n_max = int(np.ceil(1.2 * tau_p4.loc[label, "steps_for_25tau"] / 250.0) * 250)
        t0 = time.time()
        if os.path.exists(os.path.join(out_dir, "summary.json")):
            print(f"[p6] {label}: summary.json exists, scoring only", flush=True)
        else:
            print(f"\n{'=' * 70}\n[p6] {label} ({cfg} on {medium}, c_max {c_max}) -> {rel}; n_steps_max {n_max} "
                  f"(1.2 x 25 x tau_P4 {tau_p4.loc[label, 'tau_max_remeasured']})\n{'=' * 70}", flush=True)
            try:
                run_gasflux_fit("eciML1515", out_dir, medium=medium, table=table, otu=otu,
                                experiment=f"gasflux_config{cfg}", c_max=c_max, etc_table=etc_table,
                                apply_protons=protons, fit_clearance=fit_k, label=label,
                                n_walkers=init.shape[0], n_steps_max=n_max, seed=1, n_proc=n_proc,
                                check_every=250, target_neff=TARGET_NEFF, tau_factor=TAU_FACTOR,
                                moves=moves, init_state=init, warm_start=False,
                                init_label=f"P4 final ensemble state ({p4_dir_for(cfg, medium)})")
            except SystemExit as e:
                print(f"[p6] {label}: STOPPED -- {e}", flush=True); continue
            except Exception as e:
                print(f"[p6] {label}: FAILED -- {type(e).__name__}: {e}", flush=True); continue
        s = json.load(open(os.path.join(out_dir, "summary.json")))["sampler"]
        ch = np.load(os.path.join(out_dir, "chain.npy"))
        tau = float(np.max(emcee.autocorr.integrated_time(ch, tol=0)))
        steps, nw = ch.shape[0], ch.shape[1]
        n_eff_simple = nw * steps / tau
        n_eff_driver = s["n_eff"]
        met_adopted = (n_eff_driver >= TARGET_NEFF) and (steps / tau >= TAU_FACTOR)
        met_strict = steps / tau >= STRICT
        sc_r2 = score(out_dir, label, cfg, medium, table, otu, c_max, etc_table, protons, fit_k)
        point = "posterior median" if label == "D_NLDM" else "MAP"     # P3's convention per configuration
        row = dict(fit=label, config=cfg, medium=medium, c_max=c_max, init=s["init"], moves=sc.get("moves"),
                   n_proc=n_proc, steps=steps, walkers=nw, n_steps_max=n_max, tau_max=round(tau, 1),
                   chain_over_tau=round(steps / tau, 1), n_eff_driver=round(n_eff_driver),
                   n_eff_walkers_steps_over_tau=round(n_eff_simple), accept=s["acceptance_fraction"],
                   converged_adopted=met_adopted, converged_40tau=met_strict,
                   steps_needed_25tau=int(np.ceil(25 * tau)), steps_needed_40tau=int(np.ceil(40 * tau)),
                   stop_reason=s["stop_reason"], wall_min=round(s["wall_time_s"] / 60, 1),
                   score_point=point, growth_R2=round(sc_r2[point]["growth_R2"], 4),
                   resp_R2=round(sc_r2[point]["resp_R2"], 4), rmax=round(sc_r2[point]["rmax"], 4),
                   Topt_C=sc_r2[point]["Topt_C"])
        df = pd.read_csv(TABLE) if os.path.exists(TABLE) else pd.DataFrame()
        df = pd.concat([df[df.fit != label] if len(df) else df, pd.DataFrame([row])], ignore_index=True)
        df.to_csv(TABLE, index=False)
        print(f"[p6] {label}: {steps} steps, tau {tau:.1f}, chain/tau {steps/tau:.1f}, n_eff {n_eff_driver:.0f}, "
              f"accept {s['acceptance_fraction']}, adopted target {'MET' if met_adopted else 'NOT MET'}, "
              f"40tau {'MET' if met_strict else 'NOT MET'}; growth R2 {row['growth_R2']} resp R2 {row['resp_R2']} "
              f"({(time.time()-t0)/60:.0f} min)", flush=True)
        if not args.no_commit:
            git("add", rel, os.path.relpath(TABLE, ROOT))
            msg = (f"P6: {label} to the adopted target -- {steps} steps, tau {tau:.1f}, chain/tau {steps/tau:.1f}, "
                   f"n_eff {n_eff_driver:.0f}, {'CONVERGED' if met_adopted else 'NOT CONVERGED'} "
                   f"(n_eff>={TARGET_NEFF} and chain/tau>={TAU_FACTOR}); chain/tau>=40 {'met' if met_strict else 'not met'}\n\n"
                   f"{s['stop_reason']}; init {s['init']}; moves {sc.get('moves')}; n_proc {n_proc}; "
                   f"{s['wall_time_s']/60:.0f} min.\n\n"
                   f"Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>\n"
                   f"Claude-Session: https://claude.ai/code/session_01UdkbgJfuK4HUYeCMhtVito\n")
            r = git("commit", "-m", msg)
            print(f"[p6] {label}: committed rc={r.returncode}", flush=True)
    print(f"\n[p6] ALL DONE in {(time.time() - t_all) / 60:.1f} min", flush=True)


if __name__ == "__main__":
    main()
