"""CLI entry point:  python -m tpc_pipeline --config configs/example.yaml"""
from __future__ import annotations

import argparse
import json
import os

from .config import build_provider, load_config, temperature_grid
from .sensitivity import run_sensitivity


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Sensitivity of an enzyme/temperature-constrained GEM's TPC "
                    "to proteome allocation and kcat(T) responses.")
    ap.add_argument("--config", required=True, help="YAML/JSON config file")
    ap.add_argument("--no-plots", action="store_true", help="skip matplotlib figures")
    args = ap.parse_args(argv)

    cfg = load_config(args.config)
    out_dir = cfg.get("output_dir", "outputs/run")
    os.makedirs(out_dir, exist_ok=True)

    print(f"[run] building provider: {cfg['provider']['type']}")
    pm = build_provider(cfg)
    try:
        pm.ec.model.solver.configuration.timeout = int(cfg.get("solver_timeout", 10))
    except Exception:
        pass
    temps = temperature_grid(cfg)
    print(f"[run] model={pm.name}  enzymes={len(pm.ec.table)}  "
          f"budget={pm.ec.default_budget:.4g}  T grid={temps[0]:.0f}-{temps[-1]:.0f}°C")

    s = cfg["sensitivity"]
    ranges = {k: tuple(v) for k, v in s["parameters"].items()}
    result = run_sensitivity(
        pm, temps, ranges,
        n_samples=s.get("n_samples", 200),
        seed=s.get("seed", 1),
        group_names=s.get("groups", []),
        crit_frac=cfg.get("crit_frac", 0.05),
    )
    result.save(out_dir)
    print(f"[run] saved data to {out_dir}")

    # summary of nominal curve + descriptor medians
    nom = result.nominal.descriptors()
    summary = {
        "model": pm.name,
        "n_enzymes": len(pm.ec.table),
        "default_budget": pm.ec.default_budget,
        "nominal": nom.as_dict(),
        "descriptor_medians": result.descriptors.median(numeric_only=True).to_dict(),
        "descriptor_iqr": (result.descriptors.quantile(0.75)
                           - result.descriptors.quantile(0.25)).to_dict(),
    }
    with open(os.path.join(out_dir, "summary.json"), "w") as fh:
        json.dump(summary, fh, indent=2)
    print("[run] nominal TPC:",
          f"Topt={nom.Topt_C:.1f}°C  rmax={nom.rmax:.3f}/h  "
          f"CTmax={nom.CTmax_C:.1f}°C  Ea={nom.Ea_eV:.2f} eV")

    if not args.no_plots:
        try:
            from .plotting import plot_all
            figs = plot_all(result, out_dir)
            print("[run] figures:", ", ".join(os.path.basename(f) for f in figs))
        except Exception as e:
            print(f"[run] plotting skipped ({e})")

    return out_dir


if __name__ == "__main__":
    main()
