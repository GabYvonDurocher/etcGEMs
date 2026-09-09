#!/usr/bin/env python3
"""P6 TASK 0 -- does the warm start work, and does its mode GROW? Two short runs (50 steps), in
scratch directories that are not committed:

  * configuration D on NLDM -- the fit TASK 0b benchmarks;
  * configuration D on LB at c_max 450 -- the family of the P5 chain the warm start killed.

For each, run_gasflux_fit's warm start is exercised with the growth check D1 added: the DE mode's
predicted peak growth against the measured peak, accepted at >= 10 %, otherwise rejected in favour
of the emergent-point ball. The printed [warm-start] line and summary.json's sampler.init are the
result. Writes warmstart_test.json beside this file.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, HERE)
os.chdir(ROOT)
from etcgem.calibration_multi import run_gasflux_fit      # noqa: E402
from p6_fits import FITS                                  # noqa: E402



def main():
    SCRATCH = os.environ.get("P6_SCRATCH", os.path.join(ROOT, "reports", "P6_convergence", "_scratch"))
    out = {}
    for label, cfg, medium, table, otu, c_max, etc, protons, fit_k in FITS:
        if label not in ("D_NLDM", "D_LB"):
            continue
        d = os.path.join(SCRATCH, f"warmstart_{label}")
        res = run_gasflux_fit("eciML1515", d, medium=medium, table=table, otu=otu, experiment=f"gasflux_config{cfg}",
                              c_max=c_max, etc_table=etc, apply_protons=protons, fit_clearance=fit_k,
                              label=f"ws_{label}", n_walkers=36, n_steps_max=50, seed=1, warm_start=True)
        s = res["sampler"]
        out[label] = {k: s[k] for k in ("init", "warm_started", "warm_start_rejected", "n_walkers", "n_steps", "acceptance_fraction")}
        print(f"[ws-test] {label}: {out[label]}", flush=True)
    json.dump(out, open(os.path.join(HERE, "warmstart_test.json"), "w"), indent=2)
    print("[ws-test] done", flush=True)


if __name__ == "__main__":
    main()
