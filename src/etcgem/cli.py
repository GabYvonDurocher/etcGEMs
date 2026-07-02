"""Unified command-line interface for etcgem.

Consolidates the previous package ``__main__`` (one-shot sweep),
``resume.py`` (checkpointed sweep) and ``run_with_fits.py`` (sweep with
DLTKcat-derived thermal params) into a single entry point, plus the DLTKcat
tooling. No scientific/algorithmic behaviour changes -- this only unifies the
entry points and adds per-strain path resolution.

    etcgem sweep  --strain NAME [--fits [PATH]] [--resume] [--seconds N] [--no-plots]
    etcgem sweep  --config PATH [--fits PATH] [--resume] [--seconds N] [--no-plots]
    etcgem dltkcat prep  --strain NAME [--tmin --tmax --n --t0]
    etcgem dltkcat parse --strain NAME [--pred PATH] [--key --temp-col --kcat-col --no-log10]
    etcgem dltkcat fit|csv|targets ...      # unchanged, explicit-path tools

A strain lives under ``strains/NAME/`` with ``config.yaml`` (carrying a
``provider.model_file`` name), ``model/<file>``, ``dltkcat/`` and ``outputs/``.
The CLI injects the resolved absolute ``provider.model_path`` and ``output_dir``
into the loaded config dict so ``config.py`` stays unchanged.
"""
from __future__ import annotations

import argparse
import json
import os
import time

import numpy as np
import pandas as pd

from .config import build_provider, load_config, temperature_grid
from .enzyme_cost import Perturbation
from .sensitivity import (SensitivityResult, run_sensitivity, _lhs,
                          _make_perturbation, _spearman_matrix)
from .tpc import TPC, compute_tpc

STRAINS_ROOT = "strains"
_FITS_DEFAULT = "\0default"   # sentinel for `--fits` given without a path


# ---------------------------------------------------------------------------
# strain / config resolution
# ---------------------------------------------------------------------------
def strain_root(name: str) -> str:
    return os.path.abspath(os.path.join(STRAINS_ROOT, name))


def load_strain_config(name: str):
    """Load strains/NAME/config.yaml and inject the absolute model path."""
    root = strain_root(name)
    cfg = load_config(os.path.join(root, "config.yaml"))
    model_file = cfg.get("provider", {}).get("model_file")
    if model_file:
        cfg["provider"]["model_path"] = os.path.join(root, "model", model_file)
    return cfg, root


def _resolve_sweep_paths(args):
    """Return (cfg, out_dir, fits_path). fits_path is None when no fits."""
    if args.strain:
        cfg, root = load_strain_config(args.strain)
        use_fits = args.fits is not None
        cfg["output_dir"] = os.path.join(root, "outputs",
                                         "dltkcat" if use_fits else "default")
        fits_path = None
        if use_fits:
            fits_path = (os.path.join(root, "dltkcat", "fits.csv")
                         if args.fits == _FITS_DEFAULT else args.fits)
    else:
        cfg = load_config(args.config)
        cfg.setdefault("output_dir", "outputs/run")
        fits_path = None if args.fits is None else (
            None if args.fits == _FITS_DEFAULT else args.fits)
        if args.fits == _FITS_DEFAULT:
            raise SystemExit("--fits needs an explicit PATH when using --config")
    return cfg, cfg["output_dir"], fits_path


def _build(cfg, fits_path, key):
    """Build the provider and (optionally) apply DLTKcat fits in place.

    kcat/base costs are left untouched; only Topt/dCp are overridden -- exactly
    the old run_with_fits behaviour."""
    pm = build_provider(cfg)
    try:
        pm.ec.model.solver.configuration.timeout = int(cfg.get("solver_timeout", 10))
    except Exception:
        pass
    if fits_path:
        from .dltkcat import apply_fits_to_provider
        apply_fits_to_provider(pm, pd.read_csv(fits_path), key=key)
    return pm


def _write_summary(out_dir, pm, nom, desc_df):
    summary = {
        "model": pm.name,
        "n_enzymes": len(pm.ec.table),
        "default_budget": pm.ec.default_budget,
        "nominal": nom.as_dict(),
        "descriptor_medians": desc_df.median(numeric_only=True).to_dict(),
        "descriptor_iqr": (desc_df.quantile(0.75) - desc_df.quantile(0.25)).to_dict(),
    }
    with open(os.path.join(out_dir, "summary.json"), "w") as fh:
        json.dump(summary, fh, indent=2)


def _maybe_plot(result, out_dir, no_plots, tag="run"):
    if no_plots:
        return
    try:
        from .plotting import plot_all
        figs = plot_all(result, out_dir)
        if figs:
            print(f"[{tag}] figures:", ", ".join(os.path.basename(f) for f in figs))
    except Exception as e:
        print(f"[{tag}] plotting skipped ({e})")


# ---------------------------------------------------------------------------
# one-shot sweep  (old __main__.py + run_with_fits.py)
# ---------------------------------------------------------------------------
def _run_oneshot(cfg, out_dir, fits_path, key, no_plots):
    print(f"[run] building provider: {cfg['provider']['type']}"
          + (f"  (+fits {os.path.basename(fits_path)})" if fits_path else ""))
    pm = _build(cfg, fits_path, key)
    temps = temperature_grid(cfg)
    print(f"[run] model={pm.name}  enzymes={len(pm.ec.table)}  "
          f"budget={pm.ec.default_budget:.4g}  T grid={temps[0]:.0f}-{temps[-1]:.0f}°C")
    s = cfg["sensitivity"]
    result = run_sensitivity(
        pm, temps, {k: tuple(v) for k, v in s["parameters"].items()},
        n_samples=s.get("n_samples", 200), seed=s.get("seed", 1),
        group_names=s.get("groups", []), crit_frac=cfg.get("crit_frac", 0.05),
    )
    result.save(out_dir)
    print(f"[run] saved data to {out_dir}")
    nom = result.nominal.descriptors()
    _write_summary(out_dir, pm, nom, result.descriptors)
    print("[run] nominal TPC:",
          f"Topt={nom.Topt_C:.1f}°C  rmax={nom.rmax:.3f}/h  "
          f"CTmax={nom.CTmax_C:.1f}°C  Ea={nom.Ea_eV:.2f} eV")
    _maybe_plot(result, out_dir, no_plots, "run")
    return out_dir


# ---------------------------------------------------------------------------
# checkpointed sweep  (old resume.py)
# ---------------------------------------------------------------------------
def _run_resume(cfg, out_dir, seconds, fits_path, key, no_plots):
    ckpt = os.path.join(out_dir, "_checkpoint.npz")
    s = cfg["sensitivity"]
    ranges = {k: tuple(v) for k, v in s["parameters"].items()}
    n = int(s.get("n_samples", 200))
    seed = int(s.get("seed", 1))
    groups = s.get("groups", [])
    names = list(ranges.keys())

    temps = temperature_grid(cfg)
    U = _lhs(n, len(names), seed)
    sampled = {nm: ranges[nm][0] + U[:, j] * (ranges[nm][1] - ranges[nm][0])
               for j, nm in enumerate(names)}
    samples_df = pd.DataFrame(sampled)

    if os.path.exists(ckpt):
        z = np.load(ckpt)
        curves, done = z["curves"], z["done"]
        if curves.shape != (n, len(temps)):
            curves = np.full((n, len(temps)), np.nan)
            done = np.zeros(n, bool)
    else:
        curves = np.full((n, len(temps)), np.nan)
        done = np.zeros(n, bool)

    todo = np.where(~done)[0]
    if len(todo) == 0:
        print(f"[resume] all {n} samples already done -> finalizing")
        return _finalize_resume(cfg, out_dir, temps, curves, samples_df, names,
                                groups, fits_path, key, no_plots)

    print(f"[resume] building provider ({cfg['provider']['type']}) ...")
    pm = _build(cfg, fits_path, key)
    default_budget = pm.ec.default_budget

    t0, n_run = time.time(), 0
    for i in todo:
        row = {k: float(samples_df.iloc[i][k]) for k in names}
        pert = _make_perturbation(row, default_budget, groups)
        curves[i] = compute_tpc(pm, temps, pert).growth
        done[i] = True
        n_run += 1
        if time.time() - t0 > seconds:
            break
    np.savez(ckpt, curves=curves, done=done)
    n_done = int(done.sum())
    print(f"[resume] ran {n_run} this call; {n_done}/{n} done")
    if n_done < n:
        print(f"[resume] PARTIAL {n_done}/{n} -- call again")
        return out_dir
    print("[resume] all samples complete -> finalizing")
    return _finalize_resume(cfg, out_dir, temps, curves, samples_df, names,
                            groups, fits_path, key, no_plots)


def _finalize_resume(cfg, out_dir, temps, curves, samples_df, names, groups,
                     fits_path, key, no_plots):
    desc_df = pd.DataFrame(
        [TPC(temps, curves[i]).descriptors(cfg.get("crit_frac", 0.05)).as_dict()
         for i in range(curves.shape[0])])
    sens = _spearman_matrix(samples_df, desc_df)
    pm = _build(cfg, fits_path, key)
    nominal = compute_tpc(pm, temps, Perturbation())
    res = SensitivityResult(np.asarray(temps), curves, samples_df, desc_df, sens, nominal)
    res.save(out_dir)
    nom = nominal.descriptors()
    _write_summary(out_dir, pm, nom, desc_df)
    print(f"[resume] nominal Topt={nom.Topt_C:.1f}C rmax={nom.rmax:.3f} "
          f"CTmax={nom.CTmax_C:.1f}C Ea={nom.Ea_eV:.2f}eV")
    _maybe_plot(res, out_dir, no_plots, "resume")
    if os.path.exists(os.path.join(out_dir, "_checkpoint.npz")):
        os.remove(os.path.join(out_dir, "_checkpoint.npz"))
    print("[resume] ALL DONE")
    return out_dir


def cmd_sweep(args):
    cfg, out_dir, fits_path = _resolve_sweep_paths(args)
    os.makedirs(out_dir, exist_ok=True)
    if args.resume:
        return _run_resume(cfg, out_dir, args.seconds, fits_path, args.key, args.no_plots)
    return _run_oneshot(cfg, out_dir, fits_path, args.key, args.no_plots)


# ---------------------------------------------------------------------------
# dltkcat tooling
# ---------------------------------------------------------------------------
def cmd_dltkcat(args):
    from . import dltkcat as dk
    if args.dcmd == "prep":
        if args.strain:
            cfg, root = load_strain_config(args.strain)
            model = cfg["provider"]["model_path"]
            out = args.out or os.path.join(root, "dltkcat", "input.csv")
            t0 = args.t0 if args.t0 is not None else cfg.get("T0_C", 30.0)
        else:
            model, out, t0 = args.model, args.out, (args.t0 or 30.0)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        dk.build_dltkcat_input(model, out, args.tmin, args.tmax, args.n, t0)

    elif args.dcmd == "parse":
        if args.strain:
            root = strain_root(args.strain)
            pred = args.pred or os.path.join(root, "dltkcat", "output.csv")
            out = args.out or os.path.join(root, "dltkcat", "fits.csv")
        else:
            pred, out = args.pred, args.out
        fits = dk.parse_dltkcat_output(pred, kcat_col=args.kcat_col, key=args.key,
                                       temp_col=args.temp_col, T0_C=args.t0 or 30.0,
                                       log10=not args.no_log10)
        fits.to_csv(out, index=False)
        print(f"[dltkcat] fitted {int(fits['ok'].sum())}/{len(fits)} usable -> {out}")

    elif args.dcmd == "fit":
        fits = dk.fit_predictions(pd.read_csv(args.pred), key=args.key, T0_C=args.t0 or 30.0)
        fits.to_csv(args.out, index=False)
        print(f"[dltkcat] fitted {int(fits['ok'].sum())}/{len(fits)} usable -> {args.out}")

    elif args.dcmd == "csv":
        fits = dk.fit_predictions(pd.read_csv(args.pred), key=args.key, T0_C=args.t0 or 30.0)
        dk.write_csv_table(fits, args.model, args.out, key=args.key, T0_C=args.t0 or 30.0)

    elif args.dcmd == "targets":
        dk.export_targets(args.model, args.out, args.tmin, args.tmax, args.n, args.t0 or 30.0)


# ---------------------------------------------------------------------------
# argument parser
# ---------------------------------------------------------------------------
def build_parser():
    ap = argparse.ArgumentParser(
        prog="etcgem",
        description="Enzyme/temperature-constrained GEM thermal-performance sweeps.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sw = sub.add_parser("sweep", help="run a TPC sensitivity sweep")
    g = sw.add_mutually_exclusive_group(required=True)
    g.add_argument("--strain", help="strain name under strains/")
    g.add_argument("--config", help="explicit YAML/JSON config (e.g. configs/toy.yaml)")
    sw.add_argument("--fits", nargs="?", const=_FITS_DEFAULT, default=None,
                    help="apply DLTKcat fits; with --strain and no PATH defaults "
                         "to strains/NAME/dltkcat/fits.csv")
    sw.add_argument("--key", default="rxn_id", choices=["rxn_id", "enzyme_id"])
    sw.add_argument("--resume", action="store_true", help="checkpointed, time-limited")
    sw.add_argument("--seconds", type=float, default=35.0, help="wall-time budget per --resume call")
    sw.add_argument("--no-plots", action="store_true")
    sw.set_defaults(func=cmd_sweep)

    dl = sub.add_parser("dltkcat", help="DLTKcat -> MMRT (Topt, dCp) tooling")
    dsub = dl.add_subparsers(dest="dcmd", required=True)

    p = dsub.add_parser("prep", help="write DLTKcat convert_input CSV (enz, sub, temp)")
    p.add_argument("--strain"); p.add_argument("--model"); p.add_argument("--out")
    p.add_argument("--tmin", type=float, default=5.0)
    p.add_argument("--tmax", type=float, default=55.0)
    p.add_argument("--n", type=int, default=11)
    p.add_argument("--t0", type=float, default=None)

    pr = dsub.add_parser("parse", help="fit MMRT from a DLTKcat prediction table")
    pr.add_argument("--strain"); pr.add_argument("--pred"); pr.add_argument("--out")
    pr.add_argument("--kcat-col", default="kcat")
    pr.add_argument("--key", default="rxn_id")
    pr.add_argument("--temp-col", default="Temp_C")
    pr.add_argument("--t0", type=float, default=None)
    pr.add_argument("--no-log10", action="store_true")

    f = dsub.add_parser("fit", help="fit MMRT to a filled prediction table")
    f.add_argument("--pred", required=True); f.add_argument("--out", required=True)
    f.add_argument("--key", default="rxn_id"); f.add_argument("--t0", type=float, default=None)

    c = dsub.add_parser("csv", help="fit + write a from_kcat_csv provider table")
    c.add_argument("--pred", required=True); c.add_argument("--model", required=True)
    c.add_argument("--out", required=True)
    c.add_argument("--key", default="rxn_id"); c.add_argument("--t0", type=float, default=None)

    t = dsub.add_parser("targets", help="export a prediction template")
    t.add_argument("--model", required=True); t.add_argument("--out", required=True)
    t.add_argument("--tmin", type=float, default=5.0)
    t.add_argument("--tmax", type=float, default=55.0)
    t.add_argument("--n", type=int, default=11)
    t.add_argument("--t0", type=float, default=None)
    dl.set_defaults(func=cmd_dltkcat)

    return ap


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    main()
