#!/usr/bin/env python3
"""P8 TASK 2B -- prove the zeus wiring on a toy before the E. coli model sees it.

A 16-dimensional correlated Gaussian with a known covariance (random SPD, condition number
~50, seed 0), sampled with the SAME block runner the driver uses (run_zeus_blocks: 40 walkers,
blocks of 100, a 4-process pool, per-block checkpoint to a scratch directory), 500 steps.
Pass: every posterior mean within 3 Monte-Carlo standard errors of the truth (SE = sd /
sqrt(n_eff), n_eff = walkers x steps / tau with emcee's estimator on the post-burn chain), every
marginal sd within 15 % of the truth, and the RMS error of the correlation matrix below 0.05.
Writes task2b_toy.json beside this file.
"""
import json
import os
import shutil
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
import emcee                                                     # noqa: E402
from etcgem.calibration_multi import run_zeus_blocks             # noqa: E402

D = 16
rng = np.random.default_rng(0)
A = rng.standard_normal((D, D)); COV = A @ A.T + 0.5 * np.eye(D)
w, V = np.linalg.eigh(COV); COV = (V * np.clip(w, w.max() / 50, None)) @ V.T      # condition number 50
MU = rng.standard_normal(D) * 3
PREC = np.linalg.inv(COV)


def logprob(x):
    d = x - MU
    return -0.5 * float(d @ PREC @ d)


def main():
    from multiprocessing import Pool
    scratch = os.path.join(HERE, "_scratch", "toy"); shutil.rmtree(scratch, ignore_errors=True); os.makedirs(scratch)
    p0 = MU + rng.standard_normal((40, D)) * np.sqrt(np.diag(COV)) * 0.5
    with Pool(4) as pool:
        chain, lp, n, tau_max, stop, info = run_zeus_blocks(logprob, p0, 500, 100, pool, out_dir=scratch, label="toy",
                                                          seed=1, tau_factor=10 ** 6, target_neff=10 ** 9)
    burn = int(min(3 * tau_max, n // 2)) if np.isfinite(tau_max) else n // 4
    post = chain[burn:].reshape(-1, D)
    tau = np.array(emcee.autocorr.integrated_time(chain[burn:], tol=0), float)
    n_eff = 40 * (n - burn) / tau
    mean, sd = post.mean(0), post.std(0)
    se = np.sqrt(np.diag(COV)) / np.sqrt(n_eff)
    z = (mean - MU) / se
    sd_err = sd / np.sqrt(np.diag(COV)) - 1
    corr_true = COV / np.sqrt(np.outer(np.diag(COV), np.diag(COV))); corr_est = np.corrcoef(post, rowvar=False)
    rms_corr = float(np.sqrt(np.mean((corr_est - corr_true)[np.triu_indices(D, 1)] ** 2)))
    res = dict(steps=n, walkers=40, tau_max_emcee=float(tau_max), tau_per_param=tau.round(1).tolist(), burn=burn,
               n_eff_min=float(n_eff.min()), max_abs_z_mean=float(np.abs(z).max()), max_abs_sd_err=float(np.abs(sd_err).max()),
               rms_corr_err=rms_corr, zeus_act_max=info["checkpoints"][-1]["zeus_act_max"], zeus_efficiency=info["checkpoints"][-1]["zeus_efficiency"],
               evals_per_walker_step=info["checkpoints"][-1]["evals_per_walker_step"], checkpoint_files=sorted(os.listdir(scratch)),
               passed=bool(np.abs(z).max() < 3 and np.abs(sd_err).max() < 0.15 and rms_corr < 0.05))
    json.dump(res, open(os.path.join(HERE, "task2b_toy.json"), "w"), indent=2)
    print(f"[toy] {res}")
    print("[toy] done")


if __name__ == "__main__":
    main()
