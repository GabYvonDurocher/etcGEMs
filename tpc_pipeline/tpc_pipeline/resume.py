"""Checkpointed sensitivity sweep for large models / time-limited runners.

Runs the same LHS sweep as ``sensitivity.run_sensitivity`` but persists a
checkpoint after every sample and exits after a wall-time budget, so it can be
invoked repeatedly until complete:

    python -m tpc_pipeline.resume --config configs/eciML1515.yaml --seconds 35

When all samples are done it writes the final outputs (csvs, summary, figures),
identical to the one-shot CLI.
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
from .sensitivity import SensitivityResult, _lhs, _make_perturbation, _spearman_matrix
from .tpc import TPC, compute_tpc


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--seconds", type=float, default=35.0)
    ap.add_argument("--no-plots", action="store_true")
    args = ap.parse_args(argv)

    cfg = load_config(args.config)
    out_dir = cfg.get("output_dir", "outputs/run")
    os.makedirs(out_dir, exist_ok=True)
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

    # load / init checkpoint
    if os.path.exists(ckpt):
        z = np.load(ckpt)
        curves = z["curves"]
        done = z["done"]
        if curves.shape != (n, len(temps)):
            curves = np.full((n, len(temps)), np.nan)
            done = np.zeros(n, bool)
    else:
        curves = np.full((n, len(temps)), np.nan)
        done = np.zeros(n, bool)

    todo = np.where(~done)[0]
    if len(todo) == 0:
        print(f"[resume] all {n} samples already done -> finalizing")
        return _finalize(cfg, out_dir, temps, curves, samples_df, names, groups,
                         args.no_plots)

    print(f"[resume] building provider ({cfg['provider']['type']}) ...")
    pm = build_provider(cfg)
    default_budget = pm.ec.default_budget
    # Cap any single LP so one hard (tightly-constrained) sample can't blow the
    # wall-time budget and get the runner killed mid-solve.
    try:
        pm.ec.model.solver.configuration.timeout = int(cfg.get("solver_timeout", 6))
    except Exception:
        pass

    t0 = time.time()
    n_run = 0
    for i in todo:
        row = {k: float(samples_df.iloc[i][k]) for k in names}
        pert = _make_perturbation(row, default_budget, groups)
        curves[i] = compute_tpc(pm, temps, pert).growth
        done[i] = True
        n_run += 1
        if time.time() - t0 > args.seconds:
            break
    np.savez(ckpt, curves=curves, done=done)
    n_done = int(done.sum())
    print(f"[resume] ran {n_run} this call; {n_done}/{n} done")

    if n_done < n:
        print(f"[resume] PARTIAL {n_done}/{n} -- call again")
        return out_dir
    print("[resume] all samples complete -> finalizing")
    return _finalize(cfg, out_dir, temps, curves, samples_df, names, groups,
                     args.no_plots)


def _finalize(cfg, out_dir, temps, curves, samples_df, names, groups, no_plots):
    # descriptors from stored curves (no LP needed)
    desc_rows = [TPC(temps, curves[i]).descriptors(cfg.get("crit_frac", 0.05)).as_dict()
                 for i in range(curves.shape[0])]
    desc_df = pd.DataFrame(desc_rows)
    sens = _spearman_matrix(samples_df, desc_df)

    # nominal curve needs the model
    pm = build_provider(cfg)
    nominal = compute_tpc(pm, temps, Perturbation())
    res = SensitivityResult(np.asarray(temps), curves, samples_df, desc_df, sens, nominal)
    res.save(out_dir)

    nom = nominal.descriptors()
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
    print(f"[resume] nominal Topt={nom.Topt_C:.1f}C rmax={nom.rmax:.3f} "
          f"CTmax={nom.CTmax_C:.1f}C Ea={nom.Ea_eV:.2f}eV")

    if not no_plots:
        try:
            from .plotting import plot_all
            plot_all(res, out_dir)
            print("[resume] figures written")
        except Exception as e:
            print(f"[resume] plotting skipped ({e})")
    # clean up checkpoint
    c = os.path.join(out_dir, "_checkpoint.npz")
    if os.path.exists(c):
        os.remove(c)
    print("[resume] ALL DONE")
    return out_dir


if __name__ == "__main__":
    main()
