#!/usr/bin/env python3
"""P10 TASK 5 -- ONE fit: D NLDM with both halves ON (through the strain config, which the
likelihood reads), everything else P4's/P6's -- data, priors (disc_resp's unchanged), c_max 120,
the ORIGINAL sampler (stretch move, 40 walkers, 16 processes), P7's driver with the HDF5
checkpoint every step and tau logged every 250, initialised from P4's final ensemble state.
No early stop on the 1500-step diagnostic; --extend resumes to 2500 (PARTIAL only); --target
resumes and runs to the P6 target (MIXING only).
"""
import argparse, json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src")); sys.path.insert(0, os.path.join(ROOT, "reports", "P6_convergence")); os.chdir(ROOT)
from etcgem.calibration_multi import run_gasflux_fit, _build_gasflux_ctx   # noqa: E402
from p6_fits import FITS, p4_dir_for                                       # noqa: E402
OUT = os.path.join(ROOT, "strains", "eciML1515", "outputs", "calibration_configD_NLDM_recipe_P10")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--extend", action="store_true"); ap.add_argument("--target", action="store_true"); a = ap.parse_args()
    label, cfg, medium, table, otu, c_max, etc, protons, fit_k = [f for f in FITS if f[0] == "D_NLDM"][0]
    init = np.load(os.path.join(ROOT, "strains", "eciML1515", "outputs", p4_dir_for(cfg, medium), "chain.npy"))[-1]
    ctx, _ = _build_gasflux_ctx(strain="eciML1515", medium=medium, experiment=f"gasflux_config{cfg}", table=table, otu=otu, c_max=c_max, etc_table=etc, apply_protons=protons, fit_clearance=fit_k)
    print(f"[p10] respiration options read from the strain config: {ctx['respiration']}", flush=True)
    assert ctx["respiration"].get("tiebreak") == "pfba" and float(ctx["respiration"].get("log_o2_floor", 0)) > 0, "both halves must be ON"
    resume = a.extend or a.target
    res = run_gasflux_fit("eciML1515", OUT, medium=medium, table=table, otu=otu, experiment=f"gasflux_config{cfg}", c_max=c_max, etc_table=etc,
                          apply_protons=protons, fit_clearance=fit_k, label="D_NLDM_P10", n_walkers=40,
                          n_steps_max=(2500 if a.extend else (12000 if a.target else 1500)), seed=1, n_proc=16, check_every=250,
                          tau_factor=(25 if a.target else 10 ** 6), target_neff=(600 if a.target else 10 ** 9),
                          warm_start=False, init_state=None if resume else init, init_label="P4 D_NLDM final ensemble state",
                          checkpoint=True, resume=resume)
    s = res["sampler"]; print(f"[p10] {s['n_steps']} steps, {s['wall_time_s']/60:.1f} min, tau_max {s['autocorr_time_max']}, accept {s['acceptance_fraction']}", flush=True); print("[p10] done", flush=True)


if __name__ == "__main__":
    main()
