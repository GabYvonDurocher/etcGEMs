#!/usr/bin/env python3
"""P7 TASK 3 -- configuration D NLDM, 128 walkers, everything else P6's (D5).

Model, priors, data, c_max (120), stretch move, 16 processes, seed 1: exactly P6's D NLDM run.
The ONLY sampling change is 40 -> 128 walkers. Initialisation is DECISIONS D4: each of the 128
walkers is a P4 final walker drawn with replacement plus Gaussian jitter of 5 % of the prior
scale per parameter (sampled space), seed 7, clipped inside the bounds. Checkpointed every step
(chain.h5), tau logged every 250 steps by the driver; the per-parameter table is built afterwards
from chain.h5 by task3_table.py. No early stop (tau_factor huge): the tau(N) curve is the result.

    python reports/P7_walkers/run_walkers.py            # 1500 steps
    python reports/P7_walkers/run_walkers.py --extend   # resume to 2500 (TASK 2, partial case only)
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "reports", "P6_convergence"))
os.chdir(ROOT)
from etcgem.calibration_multi import run_gasflux_fit, build_gasflux_specs   # noqa: E402
from p6_fits import FITS, p4_dir_for                                        # noqa: E402

N_WALKERS, SEED_INIT, JITTER = 128, 7, 0.05
OUT = os.path.join(ROOT, "strains", "eciML1515", "outputs", "calibration_configD_NLDM_recipe_P7_w128")


def init_128(cfg, medium, specs):
    p4 = np.load(os.path.join(ROOT, "strains", "eciML1515", "outputs", p4_dir_for(cfg, medium), "chain.npy"))[-1]
    rng = np.random.default_rng(SEED_INIT)
    idx = rng.integers(0, p4.shape[0], N_WALKERS)
    widths = np.array([JITTER * s.scale for s in specs])
    lo = np.array([np.log(s.lo) if s.space == "log" else s.lo for s in specs])
    hi = np.array([np.log(s.hi) if s.space == "log" else s.hi for s in specs])
    p0 = np.clip(p4[idx] + widths * rng.standard_normal((N_WALKERS, p4.shape[1])), lo + 1e-6, hi - 1e-6)
    return p0, p4, idx


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--extend", action="store_true"); a = ap.parse_args()
    label, cfg, medium, table, otu, c_max, etc, protons, fit_k = [f for f in FITS if f[0] == "D_NLDM"][0]
    specs = build_gasflux_specs({"use_etc": etc is not None, "fit_clearance": fit_k})
    p0, p4, idx = init_128(cfg, medium, specs)
    if not a.extend:
        os.makedirs(OUT, exist_ok=True)
        json.dump(dict(rule="P4 final walker drawn with replacement + N(0, 0.05 x prior scale) jitter, clipped",
                       seed_init=SEED_INIT, jitter_frac=JITTER, n_walkers=N_WALKERS, source_walkers=int(p4.shape[0]),
                       draw_counts=np.bincount(idx, minlength=p4.shape[0]).tolist(),
                       spread_start_sd=p0.std(axis=0).tolist(), spread_p4_sd=p4.std(axis=0).tolist(),
                       params=[s.name for s in specs]), open(os.path.join(OUT, "init_128.json"), "w"), indent=1)
    res = run_gasflux_fit("eciML1515", OUT, medium=medium, table=table, otu=otu, experiment=f"gasflux_config{cfg}",
                          c_max=c_max, etc_table=etc, apply_protons=protons, fit_clearance=fit_k,
                          label="D_NLDM_w128", n_walkers=N_WALKERS, n_steps_max=2500 if a.extend else 1500,
                          seed=1, n_proc=16, check_every=250, tau_factor=10 ** 6, target_neff=10 ** 9,
                          warm_start=False, init_state=None if a.extend else p0,
                          init_label="128 from P4 D_NLDM final ensemble (D4 rule, seed 7)",
                          checkpoint=True, resume=a.extend)
    s = res["sampler"]
    print(f"[p7] {s['n_steps']} steps x {s['n_walkers']} walkers, {s['wall_time_s']/60:.1f} min, "
          f"{s['wall_time_s']/s['n_steps']:.2f} s/step, accept {s['acceptance_fraction']}, tau_max {s['autocorr_time_max']}", flush=True)
    print("[p7] done", flush=True)


if __name__ == "__main__":
    main()
