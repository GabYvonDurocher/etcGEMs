"""Run a TPC sensitivity sweep with DLTKcat-derived thermal parameters applied.

    python run_with_fits.py --config configs/eciML1515.yaml --fits fits.csv

Builds the provider from the config, overrides each enzyme's Topt/dCp from the
fitted DLTKcat parameters (keeping the model's calibrated kcat costs), then runs
the same sweep as `python -m tpc_pipeline`.
"""
import argparse
import json
import os

import pandas as pd

from tpc_pipeline.config import build_provider, load_config, temperature_grid
from tpc_pipeline.dltkcat import apply_fits_to_provider
from tpc_pipeline.sensitivity import run_sensitivity


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--fits", required=True, help="fits.csv from `dltkcat parse`")
    ap.add_argument("--key", default="rxn_id", choices=["rxn_id", "enzyme_id"])
    ap.add_argument("--no-plots", action="store_true")
    args = ap.parse_args()

    cfg = load_config(args.config)
    out_dir = cfg.get("output_dir", "outputs/run") + "_dltkcat"
    os.makedirs(out_dir, exist_ok=True)

    pm = build_provider(cfg)
    try:
        pm.ec.model.solver.configuration.timeout = int(cfg.get("solver_timeout", 10))
    except Exception:
        pass
    apply_fits_to_provider(pm, pd.read_csv(args.fits), key=args.key)

    temps = temperature_grid(cfg)
    s = cfg["sensitivity"]
    result = run_sensitivity(
        pm, temps, {k: tuple(v) for k, v in s["parameters"].items()},
        n_samples=s.get("n_samples", 200), seed=s.get("seed", 1),
        group_names=s.get("groups", []), crit_frac=cfg.get("crit_frac", 0.05),
    )
    result.save(out_dir)
    nom = result.nominal.descriptors()
    json.dump({"model": pm.name, "nominal": nom.as_dict(),
               "descriptor_medians": result.descriptors.median(numeric_only=True).to_dict()},
              open(os.path.join(out_dir, "summary.json"), "w"), indent=2)
    print(f"[run_with_fits] nominal Topt={nom.Topt_C:.1f}C rmax={nom.rmax:.3f} "
          f"CTmax={nom.CTmax_C:.1f}C -> {out_dir}")
    if not args.no_plots:
        from tpc_pipeline.plotting import plot_all
        plot_all(result, out_dir)
        print("[run_with_fits] figures written")


if __name__ == "__main__":
    main()
