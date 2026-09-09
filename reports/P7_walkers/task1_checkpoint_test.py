#!/usr/bin/env python3
"""P7 TASK 1 -- checkpointing must change nothing, and must resume exactly.

Three short runs of configuration D NLDM (P6's definition), 40 walkers from P4's final ensemble
state, 100 steps, seed 1, 16 processes, no warm start:
  A  checkpoint=False                                   (the driver as P6 ran it, plus the seeded RNG)
  B  checkpoint=True                                    (HDF5 backend, written every step)
  C  checkpoint=True, halted at 50 steps, then resume=True to 100
Pass: chain(A) == chain(B) exactly and chain(B) == chain(C) exactly. Scratch dirs; not committed.
Writes task1_checkpoint_test.json beside this file.
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
                  etc_table=etc, apply_protons=protons, fit_clearance=fit_k, seed=1, n_proc=16,
                  warm_start=False, init_state=init, init_label="P4 D_NLDM final ensemble state",
                  tau_factor=10 ** 6, check_every=50)
    out = {}
    for name in ("A", "B", "C"):
        d = os.path.join(SCR, f"ckpt_{name}"); shutil.rmtree(d, ignore_errors=True)
        if name == "A":
            run_gasflux_fit("eciML1515", d, label="ckpt_A", n_steps_max=100, checkpoint=False, **common)
        elif name == "B":
            run_gasflux_fit("eciML1515", d, label="ckpt_B", n_steps_max=100, checkpoint=True, **common)
        else:
            run_gasflux_fit("eciML1515", d, label="ckpt_C1", n_steps_max=50, checkpoint=True, **common)
            run_gasflux_fit("eciML1515", d, label="ckpt_C2", n_steps_max=100, checkpoint=True, resume=True, **common)
        out[name] = np.load(os.path.join(d, "chain.npy"))
        print(f"[ckpt-test] {name}: chain {out[name].shape}", flush=True)
    res = dict(A_shape=list(out["A"].shape), B_shape=list(out["B"].shape), C_shape=list(out["C"].shape),
               A_equals_B=bool(np.array_equal(out["A"], out["B"])),
               B_equals_C=bool(np.array_equal(out["B"], out["C"])),
               max_abs_diff_AB=float(np.max(np.abs(out["A"] - out["B"]))) if out["A"].shape == out["B"].shape else None,
               max_abs_diff_BC=float(np.max(np.abs(out["B"] - out["C"]))) if out["B"].shape == out["C"].shape else None)
    json.dump(res, open(os.path.join(HERE, "task1_checkpoint_test.json"), "w"), indent=2)
    print(f"[ckpt-test] {res}", flush=True)
    print("[ckpt-test] done", flush=True)


if __name__ == "__main__":
    main()
