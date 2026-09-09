#!/usr/bin/env python3
"""P7 TASK 1, second pass -- separate the checkpoint from the process pool.

The first pass found chain(A) != chain(B) at 16 processes. Two candidate causes: the checkpoint
(a bug) or the pool (multiprocessing assigns walkers to workers non-deterministically, each
worker's Gurobi model carries its own solve history, and the D likelihood reproduces only to
~1e-4 -- enough to flip a rare accept/reject). This pass decides:

  A2  checkpoint=False, n_proc=1, 20 steps      one worker, one history -> deterministic likelihood
  B2  checkpoint=True,  n_proc=1, 20 steps
  C2  checkpoint=True,  n_proc=1, 10 steps, then resume to 20
  A'  checkpoint=False, n_proc=16, 100 steps     a repeat of the first pass's A, to measure
                                                  run-to-run variability WITHOUT any checkpoint
Pass: A2 == B2 == C2 exactly (the checkpoint is a no-op and resumes exactly); A' vs A shows the
pool's variability, to be compared with A vs B from the first pass. Writes
task1_checkpoint_test2.json beside this file.
"""
import json
import os
import shutil
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "reports", "P6_convergence"))
os.chdir(ROOT)
from etcgem.calibration_multi import run_gasflux_fit          # noqa: E402
from p6_fits import FITS, p4_dir_for                          # noqa: E402

SCR = os.path.join(HERE, "_scratch")


def main():
    label, cfg, medium, table, otu, c_max, etc, protons, fit_k = [f for f in FITS if f[0] == "D_NLDM"][0]
    init = np.load(os.path.join(ROOT, "strains", "eciML1515", "outputs", p4_dir_for(cfg, medium), "chain.npy"))[-1]
    common = dict(medium=medium, table=table, otu=otu, experiment=f"gasflux_config{cfg}", c_max=c_max,
                  etc_table=etc, apply_protons=protons, fit_clearance=fit_k, seed=1,
                  warm_start=False, init_state=init, init_label="P4 D_NLDM final ensemble state",
                  tau_factor=10 ** 6, check_every=10)
    out = {}
    d = os.path.join(SCR, "ckpt_A2"); shutil.rmtree(d, ignore_errors=True)
    run_gasflux_fit("eciML1515", d, label="ckpt_A2", n_steps_max=20, n_proc=1, checkpoint=False, **common)
    out["A2"] = np.load(os.path.join(d, "chain.npy"))
    d = os.path.join(SCR, "ckpt_B2"); shutil.rmtree(d, ignore_errors=True)
    run_gasflux_fit("eciML1515", d, label="ckpt_B2", n_steps_max=20, n_proc=1, checkpoint=True, **common)
    out["B2"] = np.load(os.path.join(d, "chain.npy"))
    d = os.path.join(SCR, "ckpt_C2"); shutil.rmtree(d, ignore_errors=True)
    run_gasflux_fit("eciML1515", d, label="ckpt_C2a", n_steps_max=10, n_proc=1, checkpoint=True, **common)
    run_gasflux_fit("eciML1515", d, label="ckpt_C2b", n_steps_max=20, n_proc=1, checkpoint=True, resume=True, **common)
    out["C2"] = np.load(os.path.join(d, "chain.npy"))
    d = os.path.join(SCR, "ckpt_Aprime"); shutil.rmtree(d, ignore_errors=True)
    run_gasflux_fit("eciML1515", d, label="ckpt_Aprime", n_steps_max=100, n_proc=16, checkpoint=False, **dict(common, check_every=50))
    out["Ap"] = np.load(os.path.join(d, "chain.npy"))
    A = np.load(os.path.join(SCR, "ckpt_A", "chain.npy")); B = np.load(os.path.join(SCR, "ckpt_B", "chain.npy"))
    def first_diff(x, y):
        dif = np.any(x != y, axis=(1, 2)); return int(np.argmax(dif)) if dif.any() else None
    res = dict(A2_equals_B2=bool(np.array_equal(out["A2"], out["B2"])), B2_equals_C2=bool(np.array_equal(out["B2"], out["C2"])),
               A2_equals_C2=bool(np.array_equal(out["A2"], out["C2"])),
               pool16_A_vs_Aprime_equal=bool(np.array_equal(A, out["Ap"])), pool16_A_vs_Aprime_first_differing_step=first_diff(A, out["Ap"]),
               pool16_A_vs_B_first_differing_step=first_diff(A, B),
               pool16_A_vs_Aprime_frac_walkersteps_differing=float(np.mean(np.any(A != out["Ap"], axis=2))),
               pool16_A_vs_B_frac_walkersteps_differing=float(np.mean(np.any(A != B, axis=2))))
    json.dump(res, open(os.path.join(HERE, "task1_checkpoint_test2.json"), "w"), indent=2)
    print(f"[ckpt-test2] {res}", flush=True)
    print("[ckpt-test2] done", flush=True)


if __name__ == "__main__":
    main()
