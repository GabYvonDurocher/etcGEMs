#!/usr/bin/env python3
"""P8 TASK 2B -- the cost of a zeus step on this likelihood, measured exactly on a short run
(D NLDM, 40 walkers from P4's final ensemble, 16 processes, blocks of 10, 30 steps): seconds
per step per block, zeus's own evaluation count (ncall) per walker-step, and the workers'
utilisation. Writes task2b_cost.json beside this file. Diagnostic only; scratch output.
"""
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "reports", "P6_convergence"))
os.chdir(ROOT)
from etcgem.calibration_multi import _build_gasflux_ctx, _gwinit, _gwlogprob, run_zeus_blocks, _set_default_solver  # noqa: E402
from p6_fits import FITS, p4_dir_for                      # noqa: E402


def main():
    label, cfg, medium, table, otu, c_max, etc, protons, fit_k = [f for f in FITS if f[0] == "D_NLDM"][0]
    init = np.load(os.path.join(ROOT, "strains", "eciML1515", "outputs", p4_dir_for(cfg, medium), "chain.npy"))[-1]
    payload = dict(strain="eciML1515", medium=medium, experiment=f"gasflux_config{cfg}", table=table, otu=otu,
                   c_max=c_max, etc_table=etc, apply_protons=protons, fit_clearance=fit_k)
    solver = _set_default_solver("gurobi")
    from multiprocessing import Pool
    scratch = os.path.join(HERE, "_scratch", "zeus_cost"); os.makedirs(scratch, exist_ok=True)
    t0 = time.time()
    with Pool(processes=16, initializer=_gwinit, initargs=(dict(payload, solver=solver),)) as pool:
        chain, lp, n, tau, stop, info = run_zeus_blocks(_gwlogprob, init, 30, 10, pool, out_dir=scratch, label="zeus_cost",
                                                      seed=1, tau_factor=10 ** 6, target_neff=10 ** 9)
    wall = time.time() - t0
    cks = info["checkpoints"]
    res = dict(steps=n, walkers=40, wall_s=round(wall, 1), s_per_step=round(wall / n, 1),
               block_wall_s=[c["block_wall_s"] for c in cks], ncall_total=cks[-1]["ncall"],
               evals_per_walker_step=round(cks[-1]["ncall"] / (40 * n), 2),
               emcee_40w_s_per_step=1.86, cost_ratio_vs_emcee=round(wall / n / 1.86, 1),
               single_eval_s=0.45, ideal_parallel_s_per_step=round(cks[-1]["ncall"] / n * 0.45 / 16, 1),
               utilisation=round((cks[-1]["ncall"] / n * 0.45 / 16) / (wall / n), 2))
    json.dump(res, open(os.path.join(HERE, "task2b_cost.json"), "w"), indent=2)
    print(f"[cost] {res}", flush=True); print("[cost] done", flush=True)


if __name__ == "__main__":
    main()
