"""M4 runner: emcee calibration of the M. maripaludis thermal ecModel to the Jones 1983
TPC (H2/CO2). A real file (not stdin) is required for macOS multiprocessing spawn.

  python strains/mmaripaludis/run_calibration_jones.py            # full run
  python strains/mmaripaludis/run_calibration_jones.py --smoke    # fast pipeline check
"""
import argparse
import logging
import os
import sys
import warnings

# project root on sys.path (macOS multiprocessing spawn re-imports this file in a fresh
# interpreter whose sys.path[0] is this script's dir, not the repo root)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

logging.getLogger("cobra").setLevel(logging.CRITICAL)
warnings.filterwarnings("ignore")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="strains/mmaripaludis/outputs/calibration_jones")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--walkers", type=int, default=40)
    ap.add_argument("--steps", type=int, default=6000)
    ap.add_argument("--proc", type=int, default=0)
    a = ap.parse_args()

    from src.etcgem import calibration_multi as C
    if a.smoke:
        res = C.run_methanogen("mmaripaludis", a.out, n_walkers=20, n_steps_max=30, n_burn=5,
                               n_proc=4, check_every=15, target_neff=5, tau_factor=1,
                               warm_start=False, progress=False)
    else:
        res = C.run_methanogen("mmaripaludis", a.out, n_walkers=a.walkers, n_steps_max=a.steps,
                               n_burn=150, n_proc=a.proc, check_every=200, target_neff=400,
                               tau_factor=50, warm_start=True, progress=False)
    s = res["sampler"]
    print(f"DONE steps={s['n_steps']} accept={s['acceptance_fraction']} n_eff={s['n_eff']} "
          f"wall={s['wall_time_s']}s stop={s['stop_reason']}")
    print("posterior kcat_scale:", res["posterior"]["kcat_scale"]["posterior_median"],
          res["posterior"]["kcat_scale"]["posterior_90CI"])
    print("descriptors:", res["descriptors"])
    print("out:", os.path.abspath(a.out))


if __name__ == "__main__":
    main()
