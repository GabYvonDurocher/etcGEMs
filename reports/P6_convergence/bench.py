#!/usr/bin/env python3
"""P6 TASK 0b -- benchmark before spending the night. ONE fit (configuration D on NLDM), every
run initialised from P4's final ensemble state (40 walkers, so no burn-in to pay), short chains:

  (a) baseline: emcee's default stretch move, n_proc 10 (P4's setting)        -- 500 steps
  (b) DEMove (0.8) + DESnookerMove (0.2), n_proc 10                             -- 500 steps
  (c) stretch move at n_proc 10 / 12 / 16 / 20                                  -- 150 steps each
      (timing only; tau needs the longer chains). NOTE the walker arithmetic: P4's chains hold
      40 walkers, not the prompt's 36, so emcee's halves are 20 -- 10 processes is two FULL
      rounds already; 12 and 16 leave the second round part-empty; 20 is one round on more
      processes than there are performance cores.
  (d) DE moves at the best process count from (c), if it differs from 10       -- 150 steps

Reports tau_max, acceptance and wall-clock per 500 steps for each, and for the two 500-step
runs the posterior medians and 90 % interval widths per parameter, so "same posterior, faster"
can be checked rather than assumed. Scratch directories only; nothing committed but the CSVs.
"""
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
os.chdir(ROOT)

import emcee                                                     # noqa: E402
from etcgem.calibration_multi import run_gasflux_fit, to_natural, build_gasflux_specs  # noqa: E402
from p6_fits import FITS, p4_dir_for                             # noqa: E402

SCRATCH = os.path.join(HERE, "_scratch")
FIT = [f for f in FITS if f[0] == "D_NLDM"][0]
label, cfg, medium, table, otu, c_max, etc, protons, fit_k = FIT
P4 = os.path.join(ROOT, "strains", "eciML1515", "outputs", p4_dir_for(cfg, medium))
INIT = np.load(os.path.join(P4, "chain.npy"))[-1]        # (40, ndim): P4's final ensemble state

DE = [(emcee.moves.DEMove(), 0.8), (emcee.moves.DESnookerMove(), 0.2)]
RUNS = [("stretch_p10", None, 10, 500),
        ("DE_p10", DE, 10, 500),
        ("stretch_p12", None, 12, 150),
        ("stretch_p16", None, 16, 150),
        ("stretch_p20", None, 20, 150)]


def run_one(name, moves, n_proc, steps):
    d = os.path.join(SCRATCH, f"bench_{name}")
    if os.path.exists(os.path.join(d, "summary.json")):
        print(f"[bench] {name}: exists, reusing", flush=True)
    else:
        run_gasflux_fit("eciML1515", d, medium=medium, table=table, otu=otu, experiment=f"gasflux_config{cfg}",
                        c_max=c_max, etc_table=etc, apply_protons=protons, fit_clearance=fit_k,
                        label=f"bench_{name}", n_steps_max=steps, seed=1, n_proc=n_proc, check_every=steps,
                        moves=moves, init_state=INIT, init_label="P4 D_NLDM final ensemble state",
                        tau_factor=10 ** 6)     # never early-stop a benchmark
    s = json.load(open(os.path.join(d, "summary.json")))["sampler"]
    ch = np.load(os.path.join(d, "chain.npy"))
    try:
        tau = float(np.max(emcee.autocorr.integrated_time(ch, tol=0)))
    except Exception:
        tau = float("nan")
    return d, dict(run=name, moves="DE+Snooker" if moves else "stretch", n_proc=n_proc, steps=s["n_steps"],
                   walkers=s["n_walkers"], wall_s=s["wall_time_s"], s_per_step=round(s["wall_time_s"] / s["n_steps"], 2),
                   wall_per_500_min=round(500 * s["wall_time_s"] / s["n_steps"] / 60, 1),
                   tau_max=round(tau, 1), chain_over_tau=round(s["n_steps"] / tau, 1) if np.isfinite(tau) else None,
                   accept=s["acceptance_fraction"])


def posterior_table(d, name, discard=100):
    ch = np.load(os.path.join(d, "chain.npy"))[discard:]
    specs = build_gasflux_specs({"use_etc": etc is not None, "fit_clearance": fit_k})
    flat = ch.reshape(-1, ch.shape[2])
    rows = []
    for k, s in enumerate(specs):
        col = np.array([to_natural(t, specs)[s.name] for t in flat[::max(1, len(flat) // 2000)]])
        lo, md, hi = np.percentile(col, [5, 50, 95])
        rows.append(dict(run=name, param=s.name, median=md, ci90_lo=lo, ci90_hi=hi, width=hi - lo))
    return rows


def main():
    cores = subprocess.run(["sysctl", "-n", "hw.perflevel0.physicalcpu", "hw.physicalcpu", "hw.logicalcpu"],
                           capture_output=True, text=True).stdout.split()
    print(f"[bench] machine: performance cores {cores[0]}, physical {cores[1]}, logical {cores[2]}; "
          f"walkers {INIT.shape[0]} -> emcee halves of {INIT.shape[0] // 2}", flush=True)
    rows, post = [], []
    for name, moves, n_proc, steps in RUNS:
        t0 = time.time()
        d, r = run_one(name, moves, n_proc, steps)
        rows.append(r)
        print(f"[bench] {name:12s} {r['steps']} steps  {r['s_per_step']} s/step  {r['wall_per_500_min']} min/500  "
              f"tau {r['tau_max']}  accept {r['accept']}", flush=True)
        if steps >= 500:
            post += posterior_table(d, name)
    df = pd.DataFrame(rows)
    # (d): DE at the fastest stretch process count, if it is not 10
    timing = df[df.moves == "stretch"].sort_values("s_per_step")
    best_p = int(timing.iloc[0].n_proc)
    if best_p != 10:
        d, r = run_one(f"DE_p{best_p}", DE, best_p, 150)
        df = pd.concat([df, pd.DataFrame([r])], ignore_index=True)
        print(f"[bench] DE_p{best_p}: {r['s_per_step']} s/step  {r['wall_per_500_min']} min/500", flush=True)
    df.to_csv(os.path.join(HERE, "bench.csv"), index=False)
    pt = pd.DataFrame(post)
    pt.to_csv(os.path.join(HERE, "bench_posteriors.csv"), index=False)
    if len(pt):
        w = pt.pivot(index="param", columns="run", values=["median", "width"])
        pd.set_option("display.width", 200)
        print(w.round(3).to_string())
    print(f"[bench] machine cores {cores}; fastest stretch process count {best_p}", flush=True)
    print("[bench] done", flush=True)


if __name__ == "__main__":
    main()
