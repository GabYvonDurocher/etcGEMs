"""Unified command-line interface for etcgem.

Two tiers of commands over the defaults/strain/experiment config model
(see etcgem.config):

Strain-only (no experiment needed -- a strain is runnable on its own):
    etcgem build --strain NAME                 # build provider; print+save summary
    etcgem tpc   --strain NAME [--fits [PATH]]  # nominal TPC + descriptors + plot
    etcgem fba   --strain NAME --temp C [--fits [PATH]]   # single solve at C
    etcgem dltkcat prep|parse --strain NAME ... # DLTKcat tooling (strain-aware)

Strain + experiment (method overlay from experiments/EXP.yaml):
    etcgem sweep     --strain NAME --experiment EXP [--fits [PATH]] [--resume] [--seconds N] [--no-plots]
    etcgem decompose --strain NAME --experiment EXP [--no-plots]
    etcgem sweep     --config PATH ...          # ad-hoc self-contained config escape hatch

Every run writes into strains/NAME/outputs/<tag>/ and dumps the exact merged
config there as resolved_config.yaml. No scientific/numerical code changes --
provider construction (config.build_provider) is byte-for-byte unchanged.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

import numpy as np
import pandas as pd

from . import config
from .config import (build_provider, temperature_grid, resolve, dump_resolved,
                     load_config, strain_dir)
from .enzyme_cost import Perturbation
from .sensitivity import (SensitivityResult, run_sensitivity, _lhs,
                          _make_perturbation, _spearman_matrix)
from .tpc import TPC, compute_tpc

_FITS_DEFAULT = "\0default"   # `--fits` given without an explicit path


# ---------------------------------------------------------------------------
# shared helpers
# ---------------------------------------------------------------------------
def _out_dir(strain, tag):
    return os.path.join(strain_dir(strain), "outputs", tag)


def _fits_path(strain, fits_arg):
    """Resolve the --fits value: None -> no fits; sentinel -> strain default."""
    if fits_arg is None:
        return None
    if fits_arg == _FITS_DEFAULT:
        return os.path.join(strain_dir(strain), "dltkcat", "fits.csv")
    return fits_arg


def _build_pm(cfg, fits_path=None, key="rxn_id"):
    """Build the provider, cap the LP solver, and optionally apply DLTKcat fits
    (Topt/dCp only; kcat/base costs untouched -- the old run_with_fits behaviour)."""
    pm = build_provider(cfg)
    try:
        pm.ec.model.solver.configuration.timeout = int(cfg.get("solver_timeout", 10))
    except Exception:
        pass
    if fits_path:
        from .dltkcat import apply_fits_to_provider
        apply_fits_to_provider(pm, pd.read_csv(fits_path), key=key)
    return pm


def _plot_curve(temps_C, growth, out_dir, title, fname="nominal_tpc.png"):
    try:
        from .plotting import _mpl
        plt = _mpl()
        fig, ax = plt.subplots(figsize=(7, 5))
        ax.plot(temps_C, growth, "k-", lw=2)
        ax.set_xlabel("Temperature (°C)")
        ax.set_ylabel("Growth rate (1/h)")
        ax.set_title(title)
        fig.tight_layout()
        p = os.path.join(out_dir, fname)
        fig.savefig(p, dpi=150)
        plt.close(fig)
        return p
    except Exception as e:
        print(f"[tpc] plotting skipped ({e})")
        return None


# ---------------------------------------------------------------------------
# strain-only commands
# ---------------------------------------------------------------------------
def cmd_build(args):
    cfg = resolve(args.strain)
    out_dir = _out_dir(args.strain, "build")
    os.makedirs(out_dir, exist_ok=True)
    pm = _build_pm(cfg)
    temps = temperature_grid(cfg)
    summary = {
        "strain": args.strain,
        "model": pm.name,
        "provider_type": cfg["provider"]["type"],
        "n_enzymes": len(pm.ec.table),
        "default_budget": pm.ec.default_budget,
        "T0_C": cfg.get("T0_C", 30.0),
        "temperature_grid_C": [float(temps[0]), float(temps[-1]), int(len(temps))],
    }
    with open(os.path.join(out_dir, "model_summary.json"), "w") as fh:
        json.dump(summary, fh, indent=2)
    dump_resolved(cfg, out_dir)
    print(f"[build] strain={args.strain} model={pm.name}")
    print(f"[build] enzymes={len(pm.ec.table)} budget={pm.ec.default_budget:.4g} "
          f"T0={summary['T0_C']}C grid={temps[0]:.0f}-{temps[-1]:.0f}C n={len(temps)}")
    print(f"[build] wrote {out_dir}/model_summary.json")
    return out_dir


def cmd_tpc(args):
    cfg = resolve(args.strain)
    out_dir = _out_dir(args.strain, "tpc")
    os.makedirs(out_dir, exist_ok=True)
    fits = _fits_path(args.strain, args.fits)
    pm = _build_pm(cfg, fits)
    temps = temperature_grid(cfg)
    tpc = compute_tpc(pm, temps, Perturbation())
    desc = tpc.descriptors(cfg.get("crit_frac", 0.05))
    pd.DataFrame({"temp_C": temps, "growth": tpc.growth}).to_csv(
        os.path.join(out_dir, "nominal_tpc.csv"), index=False)
    with open(os.path.join(out_dir, "descriptors.json"), "w") as fh:
        json.dump(desc.as_dict(), fh, indent=2)
    dump_resolved(cfg, out_dir)
    print(f"[tpc] strain={args.strain}" + (f" +fits {os.path.basename(fits)}" if fits else ""))
    print(f"[tpc] Topt={desc.Topt_C:.1f}°C rmax={desc.rmax:.3f}/h "
          f"CTmax={desc.CTmax_C:.1f}°C niche={desc.niche_width_C:.1f}°C Ea={desc.Ea_eV:.2f}eV")
    if not args.no_plots:
        _plot_curve(temps, tpc.growth, out_dir, f"Nominal TPC — {args.strain}")
    print(f"[tpc] wrote {out_dir}")
    return out_dir


def cmd_fba(args):
    cfg = resolve(args.strain)
    out_dir = _out_dir(args.strain, "fba")
    os.makedirs(out_dir, exist_ok=True)
    fits = _fits_path(args.strain, args.fits)
    pm = _build_pm(cfg, fits)
    tpc = compute_tpc(pm, [args.temp], Perturbation())
    growth = float(tpc.growth[0])
    result = {"strain": args.strain, "temp_C": args.temp, "growth": growth,
              "fits": os.path.basename(fits) if fits else None}
    with open(os.path.join(out_dir, "fba_result.json"), "w") as fh:
        json.dump(result, fh, indent=2)
    dump_resolved(cfg, out_dir)
    print(f"[fba] strain={args.strain} T={args.temp}°C -> growth={growth:.5f} /h")
    print(f"[fba] wrote {out_dir}/fba_result.json")
    return out_dir


# ---------------------------------------------------------------------------
# sweep (strain + experiment, or --config escape hatch)
# ---------------------------------------------------------------------------
def _sweep_cfg_out(args):
    """Return (cfg, out_dir) for a sweep, from either --config or strain+experiment."""
    if args.config:
        cfg = load_config(args.config)
        cfg.setdefault("output_dir", "outputs/run")
        return cfg, cfg["output_dir"]
    if not (args.strain and args.experiment):
        raise SystemExit("sweep needs --strain NAME --experiment EXP (or --config PATH)")
    cfg = resolve(args.strain, args.experiment)
    if "sensitivity" not in cfg:
        raise SystemExit(f"experiment '{args.experiment}' defines no `sensitivity` block")
    return cfg, _out_dir(args.strain, f"sweep_{args.experiment}")


def _finalize_sweep(cfg, out_dir, pm, result, no_plots, tag="run"):
    result.save(out_dir)
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
    dump_resolved(cfg, out_dir)
    print(f"[{tag}] nominal TPC: Topt={nom.Topt_C:.1f}°C rmax={nom.rmax:.3f}/h "
          f"CTmax={nom.CTmax_C:.1f}°C Ea={nom.Ea_eV:.2f}eV -> {out_dir}")
    if not no_plots:
        try:
            from .plotting import plot_all
            plot_all(result, out_dir)
            print(f"[{tag}] figures written")
        except Exception as e:
            print(f"[{tag}] plotting skipped ({e})")


def _run_oneshot(cfg, out_dir, fits_path, key, no_plots):
    print(f"[run] building provider: {cfg['provider']['type']}"
          + (f"  (+fits {os.path.basename(fits_path)})" if fits_path else ""))
    pm = _build_pm(cfg, fits_path, key)
    temps = temperature_grid(cfg)
    print(f"[run] model={pm.name}  enzymes={len(pm.ec.table)}  "
          f"budget={pm.ec.default_budget:.4g}  T grid={temps[0]:.0f}-{temps[-1]:.0f}°C")
    s = cfg["sensitivity"]
    from .decomposition import build_envelope_samples
    env_samples = build_envelope_samples(pm, cfg, s.get("n_samples", 200), s.get("seed", 1))
    if env_samples is not None:
        print(f"[run] envelope sampling: {cfg['envelope_sampling'].get('mode')} "
              f"(rho={cfg['envelope_sampling'].get('shared_fraction', 0.7)})")
    result = run_sensitivity(
        pm, temps, {k: tuple(v) for k, v in s["parameters"].items()},
        n_samples=s.get("n_samples", 200), seed=s.get("seed", 1),
        group_names=s.get("groups", []), crit_frac=cfg.get("crit_frac", 0.05),
        envelope_samples=env_samples,
    )
    _finalize_sweep(cfg, out_dir, pm, result, no_plots, "run")
    return out_dir


def _run_resume(cfg, out_dir, seconds, fits_path, key, no_plots):
    ckpt = os.path.join(out_dir, "_checkpoint.npz")
    s = cfg["sensitivity"]
    ranges = {k: tuple(v) for k, v in s["parameters"].items()}
    n, seed = int(s.get("n_samples", 200)), int(s.get("seed", 1))
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
            curves = np.full((n, len(temps)), np.nan); done = np.zeros(n, bool)
    else:
        curves = np.full((n, len(temps)), np.nan); done = np.zeros(n, bool)

    todo = np.where(~done)[0]
    if len(todo):
        print(f"[resume] building provider ({cfg['provider']['type']}) ...")
        pm = _build_pm(cfg, fits_path, key)
        default_budget = pm.ec.default_budget
        t0, n_run = time.time(), 0
        for i in todo:
            row = {k: float(samples_df.iloc[i][k]) for k in names}
            pert = _make_perturbation(row, default_budget, groups)
            curves[i] = compute_tpc(pm, temps, pert).growth
            done[i] = True; n_run += 1
            if time.time() - t0 > seconds:
                break
        np.savez(ckpt, curves=curves, done=done)
        n_done = int(done.sum())
        print(f"[resume] ran {n_run} this call; {n_done}/{n} done")
        if n_done < n:
            print(f"[resume] PARTIAL {n_done}/{n} -- call again")
            return out_dir
    else:
        print(f"[resume] all {n} samples already done -> finalizing")

    desc_df = pd.DataFrame(
        [TPC(temps, curves[i]).descriptors(cfg.get("crit_frac", 0.05)).as_dict()
         for i in range(curves.shape[0])])
    sens = _spearman_matrix(samples_df, desc_df)
    pm = _build_pm(cfg, fits_path, key)
    nominal = compute_tpc(pm, temps, Perturbation())
    res = SensitivityResult(np.asarray(temps), curves, samples_df, desc_df, sens, nominal)
    _finalize_sweep(cfg, out_dir, pm, res, no_plots, "resume")
    if os.path.exists(ckpt):
        os.remove(ckpt)
    print("[resume] ALL DONE")
    return out_dir


def cmd_sweep(args):
    cfg, out_dir = _sweep_cfg_out(args)
    os.makedirs(out_dir, exist_ok=True)
    fits = None if args.config else _fits_path(args.strain, args.fits)
    if args.config and args.fits not in (None, _FITS_DEFAULT):
        fits = args.fits
    if args.resume:
        return _run_resume(cfg, out_dir, args.seconds, fits, args.key, args.no_plots)
    return _run_oneshot(cfg, out_dir, fits, args.key, args.no_plots)


# ---------------------------------------------------------------------------
# decompose (strain + experiment) -- dispatches to a decomposition module
# ---------------------------------------------------------------------------
def cmd_decompose(args):
    if not (args.strain and args.experiment):
        raise SystemExit("decompose needs --strain NAME --experiment EXP")
    cfg = resolve(args.strain, args.experiment)
    out_dir = _out_dir(args.strain, f"decompose_{args.experiment}")
    try:
        from . import decomposition  # noqa: F401
    except Exception:
        print("decomposition module not installed yet")
        return sys.exit(1)
    os.makedirs(out_dir, exist_ok=True)
    dump_resolved(cfg, out_dir)
    return decomposition.run(cfg, out_dir, no_plots=args.no_plots)


# ---------------------------------------------------------------------------
# control (strain-level diagnostic; experiment optional for the control block)
# ---------------------------------------------------------------------------
def cmd_control(args):
    if not args.strain:
        raise SystemExit("control needs --strain NAME")
    cfg = resolve(args.strain, args.experiment)
    tag = f"control_{args.experiment}" if args.experiment else "control"
    out_dir = _out_dir(args.strain, tag)
    os.makedirs(out_dir, exist_ok=True)
    dump_resolved(cfg, out_dir)
    from . import control
    return control.run(cfg, out_dir, no_plots=args.no_plots)


# ---------------------------------------------------------------------------
# dltkcat tooling
# ---------------------------------------------------------------------------
def cmd_dltkcat(args):
    from . import dltkcat as dk
    if args.dcmd == "prep":
        if args.strain:
            cfg = resolve(args.strain)
            model = cfg["provider"]["model_path"]
            out = args.out or os.path.join(strain_dir(args.strain), "dltkcat", "input.csv")
            t0 = args.t0 if args.t0 is not None else cfg.get("T0_C", 30.0)
        else:
            model, out, t0 = args.model, args.out, (args.t0 or 30.0)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        dk.build_dltkcat_input(model, out, args.tmin, args.tmax, args.n, t0)

    elif args.dcmd == "parse":
        if args.strain:
            d = os.path.join(strain_dir(args.strain), "dltkcat")
            pred = args.pred or os.path.join(d, "output.csv")
            out = args.out or os.path.join(d, "fits.csv")
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
        description="Enzyme/temperature-constrained GEM thermal-performance tools.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    # --- strain-only ---
    b = sub.add_parser("build", help="build a strain's provider; print+save summary")
    b.add_argument("--strain", required=True)
    b.set_defaults(func=cmd_build)

    t = sub.add_parser("tpc", help="nominal TPC + descriptors for a strain")
    t.add_argument("--strain", required=True)
    t.add_argument("--fits", nargs="?", const=_FITS_DEFAULT, default=None)
    t.add_argument("--key", default="rxn_id", choices=["rxn_id", "enzyme_id"])
    t.add_argument("--no-plots", action="store_true")
    t.set_defaults(func=cmd_tpc)

    fb = sub.add_parser("fba", help="single enzyme-constrained solve at one temperature")
    fb.add_argument("--strain", required=True)
    fb.add_argument("--temp", type=float, required=True, help="temperature in °C")
    fb.add_argument("--fits", nargs="?", const=_FITS_DEFAULT, default=None)
    fb.add_argument("--key", default="rxn_id", choices=["rxn_id", "enzyme_id"])
    fb.set_defaults(func=cmd_fba)

    # --- strain + experiment ---
    sw = sub.add_parser("sweep", help="TPC sensitivity sweep (strain + experiment)")
    sw.add_argument("--strain")
    sw.add_argument("--experiment")
    sw.add_argument("--config", help="ad-hoc self-contained config (escape hatch)")
    sw.add_argument("--fits", nargs="?", const=_FITS_DEFAULT, default=None)
    sw.add_argument("--key", default="rxn_id", choices=["rxn_id", "enzyme_id"])
    sw.add_argument("--resume", action="store_true")
    sw.add_argument("--seconds", type=float, default=35.0)
    sw.add_argument("--no-plots", action="store_true")
    sw.set_defaults(func=cmd_sweep)

    dc = sub.add_parser("decompose", help="variance decomposition (strain + experiment)")
    dc.add_argument("--strain")
    dc.add_argument("--experiment")
    dc.add_argument("--no-plots", action="store_true")
    dc.set_defaults(func=cmd_decompose)

    ct = sub.add_parser("control", help="per-enzyme thermal control + identifiability (strain)")
    ct.add_argument("--strain")
    ct.add_argument("--experiment", help="experiment carrying the control: block (optional)")
    ct.add_argument("--no-plots", action="store_true")
    ct.set_defaults(func=cmd_control)

    # --- dltkcat tooling ---
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
    pr.add_argument("--kcat-col", default="kcat"); pr.add_argument("--key", default="rxn_id")
    pr.add_argument("--temp-col", default="Temp_C"); pr.add_argument("--t0", type=float, default=None)
    pr.add_argument("--no-log10", action="store_true")
    f = dsub.add_parser("fit", help="fit MMRT to a filled prediction table")
    f.add_argument("--pred", required=True); f.add_argument("--out", required=True)
    f.add_argument("--key", default="rxn_id"); f.add_argument("--t0", type=float, default=None)
    c = dsub.add_parser("csv", help="fit + write a from_kcat_csv provider table")
    c.add_argument("--pred", required=True); c.add_argument("--model", required=True)
    c.add_argument("--out", required=True)
    c.add_argument("--key", default="rxn_id"); c.add_argument("--t0", type=float, default=None)
    tg = dsub.add_parser("targets", help="export a prediction template")
    tg.add_argument("--model", required=True); tg.add_argument("--out", required=True)
    tg.add_argument("--tmin", type=float, default=5.0); tg.add_argument("--tmax", type=float, default=55.0)
    tg.add_argument("--n", type=int, default=11); tg.add_argument("--t0", type=float, default=None)
    dl.set_defaults(func=cmd_dltkcat)

    return ap


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    main()
