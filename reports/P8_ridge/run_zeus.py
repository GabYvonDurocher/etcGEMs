#!/usr/bin/env python3
"""P8 TASK 2B -- configuration D NLDM under zeus, all sixteen parameters, everything else P6's.

Model, priors, data, c_max 120, 16 processes, seed 1, 40 walkers (zeus asks for >= 2 x ndim = 32;
40 keeps the emcee comparison at equal walkers), initialised from P4's final ensemble state.
Blocks of 250 with a per-block checkpoint (chain.npy / log_prob.npy); tau with emcee's
estimator at every checkpoint plus zeus's act / efficiency. No early stop on the 1500-step
diagnostic run (tau_factor huge); the rule in DECISIONS D3 is applied afterwards by
task2b_table.py.

    python reports/P8_ridge/run_zeus.py            # 1500 steps
    python reports/P8_ridge/run_zeus.py --extend   # resume to 2500 (PARTIAL case only)
    python reports/P8_ridge/run_zeus.py --target   # resume and run to the P6 target (MIXING case only)
"""
import argparse
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "reports", "P6_convergence"))
os.chdir(ROOT)
from etcgem.calibration_multi import run_gasflux_fit      # noqa: E402
from p6_fits import FITS, p4_dir_for                      # noqa: E402

OUT = os.path.join(ROOT, "strains", "eciML1515", "outputs", "calibration_configD_NLDM_recipe_P8_zeus")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--extend", action="store_true"); ap.add_argument("--target", action="store_true")
    a = ap.parse_args()
    label, cfg, medium, table, otu, c_max, etc, protons, fit_k = [f for f in FITS if f[0] == "D_NLDM"][0]
    init = np.load(os.path.join(ROOT, "strains", "eciML1515", "outputs", p4_dir_for(cfg, medium), "chain.npy"))[-1]
    resume = a.extend or a.target
    n_max = 2500 if a.extend else (12000 if a.target else 1500)
    res = run_gasflux_fit("eciML1515", OUT, medium=medium, table=table, otu=otu, experiment=f"gasflux_config{cfg}",
                          c_max=c_max, etc_table=etc, apply_protons=protons, fit_clearance=fit_k,
                          label="D_NLDM_zeus", n_walkers=40, n_steps_max=n_max, seed=1, n_proc=16, check_every=250,
                          tau_factor=(25 if a.target else 10 ** 6), target_neff=(600 if a.target else 10 ** 9),
                          warm_start=False, init_state=None if resume else init,
                          init_label="P4 D_NLDM final ensemble state", checkpoint=True, resume=resume, sampler_kind="zeus")
    s = res["sampler"]
    print(f"[p8] {s['n_steps']} steps x {s['n_walkers']} walkers, {s['wall_time_s']/60:.1f} min, "
          f"{s['wall_time_s']/max(1, s['n_steps']):.2f} s/step (this call), tau_max {s['autocorr_time_max']}, zeus {s['zeus'].get('checkpoints', [{}])[-1]}", flush=True)
    print("[p8] done", flush=True)


if __name__ == "__main__":
    main()
