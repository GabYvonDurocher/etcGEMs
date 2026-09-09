#!/usr/bin/env python3
"""P9 TASK 1 -- line scans of the LOG-LIKELIHOOD through P4's MAP (D NLDM), single process, no
solver state carried between points (DECISIONS D1). Writes task1_lines.csv (41 values per line),
task1_summary.csv (per-line statistics), task1_spotcheck.json, task1_scan.png beside this file.
"""
import json
import os
import sys
import time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "reports", "P6_convergence"))
os.chdir(ROOT)
import emcee                                                                        # noqa: E402
from etcgem.calibration_multi import _build_gasflux_ctx, gasflux_log_likelihood, build_gasflux_specs  # noqa: E402
from p6_fits import FITS, p4_dir_for                                                # noqa: E402

OUTS = os.path.join(ROOT, "strains", "eciML1515", "outputs")
STEPS = np.arange(-20, 21) * 0.05            # 41 points, +/- 1 sd
SEED_RANDOM = 11


def build(fit):
    label, cfg, medium, table, otu, c_max, etc, protons, fit_k = fit
    return _build_gasflux_ctx(strain="eciML1515", medium=medium, experiment=f"gasflux_config{cfg}", table=table,
                              otu=otu, c_max=c_max, etc_table=etc, apply_protons=protons, fit_clearance=fit_k)


def ll_reset(th, ctx, specs):
    try:
        ctx["pm"].ec.model.solver.problem.reset()
    except Exception:
        pass
    return gasflux_log_likelihood(th, ctx, specs)


def main():
    fit = [f for f in FITS if f[0] == "D_NLDM"][0]
    specs = build_gasflux_specs({"use_etc": False, "fit_clearance": True}); names = [s.name for s in specs]; D = len(specs)
    p4 = os.path.join(OUTS, p4_dir_for(fit[1], fit[2]))
    ch4 = np.load(os.path.join(p4, "chain.npy")); lp4 = np.load(os.path.join(p4, "log_prob.npy"))
    i, j = np.unravel_index(np.nanargmax(lp4), lp4.shape); theta0 = ch4[i, j].copy()
    # scale: posterior sd per parameter, sampled space, P7 128w steps 250-1500 (P8's standardisation)
    b = emcee.backends.HDFBackend(os.path.join(OUTS, "calibration_configD_NLDM_recipe_P7_w128", "chain.h5"), read_only=True)
    X = b.get_chain()[250:].reshape(-1, D); mu, sd = X.mean(0), X.std(0)
    Z = (X - mu) / sd; evals_, evecs = np.linalg.eigh(np.cov(Z, rowvar=False)); order = np.argsort(evals_)[::-1]; evecs = evecs[:, order]
    dirs = []
    for k in range(D):
        e = np.zeros(D); e[k] = 1.0; dirs.append((f"axis:{names[k]}", e))
    for k in range(3):
        v = evecs[:, k]; v = v / np.linalg.norm(v); dirs.append((f"PC{k+1}", v))
    rng = np.random.default_rng(SEED_RANDOM)
    for k in range(3):
        v = rng.standard_normal(D); v /= np.linalg.norm(v); dirs.append((f"random{k+1}", v))
    # a unit direction in standardised space maps to sd * v in sampled space; +/- 1 sd of that direction
    rows, summ = [], []
    t_all = time.time(); spot = {}
    for li, (lname, v) in enumerate(dirs):
        # D2: a FRESH MODEL PER EVALUATION, exactly as the prompt and D3a's rebuild arm have it.
        # (A build is ~4 s, so 902 builds are affordable; the basis-reset shortcut D1 proposed
        # differed from a fresh build by 9e-2 on the first line and was abandoned.)
        t0 = time.time(); vals = []; t_builds = 0.0
        for s in STEPS:
            tb = time.time(); ctx, sp = build(fit); t_builds += time.time() - tb
            vals.append(gasflux_log_likelihood(theta0 + s * sd * v, ctx, sp))
        vals = np.array(vals); t_build = t_builds / len(STEPS); t_line = time.time() - t0 - t_builds
        if li == 0:
            # the comparison arm: the same five points on ONE reused model with a basis reset
            ctx, sp = build(fit); reset = {int(k): float(ll_reset(theta0 + STEPS[k] * sd * v, ctx, sp)) for k in (0, 10, 20, 30, 40)}
            spot = dict(line=lname, points=list(reset), fresh_values=[float(vals[k]) for k in reset], reset_values=list(reset.values()),
                        max_abs_diff=float(max(abs(vals[k] - reset[k]) for k in reset)))
            json.dump(spot, open(os.path.join(HERE, "task1_spotcheck.json"), "w"), indent=2)
            print(f"[scan] spot check on {lname}: fresh-vs-reset max |diff| {spot['max_abs_diff']:.2e}", flush=True)
        fin = np.isfinite(vals); d1 = np.diff(vals[fin]) if fin.sum() > 2 else np.array([])
        sc = int(np.sum(np.sign(d1[1:]) * np.sign(d1[:-1]) < 0)) if len(d1) > 1 else 0
        jump = float(np.max(np.abs(d1))) if len(d1) else np.nan
        rng_ = float(np.nanmax(vals) - np.nanmin(vals)) if fin.any() else np.nan
        summ.append(dict(line=lname, n_finite=int(fin.sum()), ll_at_map=float(vals[20]), ll_min=float(np.nanmin(vals)), ll_max=float(np.nanmax(vals)),
                         range=rng_, sign_changes=sc, max_jump=jump, max_jump_frac=(jump / rng_ if rng_ > 0 else np.nan),
                         argmax_step=float(STEPS[int(np.nanargmax(vals))]), build_s=round(t_build, 1), eval_s_mean=round(t_line / len(STEPS), 3)))
        for s, val in zip(STEPS, vals):
            rows.append(dict(line=lname, step_sd=float(s), logL=float(val)))
        print(f"[scan] {li+1:2d}/22 {lname:22s} build {t_build:5.1f}s  {t_line/len(STEPS):.2f} s/eval  sign changes {sc:2d}  max jump {jump:8.3f} ({100*jump/rng_ if rng_>0 else float('nan'):5.1f} % of range {rng_:.2f})", flush=True)
        pd.DataFrame(rows).to_csv(os.path.join(HERE, "task1_lines.csv"), index=False)
        pd.DataFrame(summ).to_csv(os.path.join(HERE, "task1_summary.csv"), index=False)
    wall = time.time() - t_all
    df = pd.DataFrame(summ)
    print(f"[scan] SUMMARY over {len(df)} lines: sign changes median {df.sign_changes.median():.0f} max {df.sign_changes.max()}; "
          f"max single-step jump median {df.max_jump.median():.3f} max {df.max_jump.max():.3f}; jump fraction median {100*df.max_jump_frac.median():.1f} % max {100*df.max_jump_frac.max():.1f} %; wall {wall/60:.1f} min", flush=True)
    json.dump(dict(theta0=theta0.tolist(), names=names, sd=sd.tolist(), wall_min=wall / 60, n_eval=len(df) * len(STEPS)),
              open(os.path.join(HERE, "task1_meta.json"), "w"), indent=1)
    try:
        import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
        L = pd.DataFrame(rows); fig, axes = plt.subplots(5, 5, figsize=(17, 15)); axes = axes.ravel()
        for k, (lname, _) in enumerate(dirs):
            sub = L[L.line == lname]; axes[k].plot(sub.step_sd, sub.logL, ".-", ms=3, lw=0.8); axes[k].set_title(lname, fontsize=8)
            axes[k].axvline(0, color="k", lw=0.4); axes[k].tick_params(labelsize=7)
        for k in range(len(dirs), 25): axes[k].axis("off")
        fig.suptitle("log-likelihood along 22 lines through P4's MAP, +/- 1 posterior sd (step 0.05 sd), D NLDM", fontsize=11)
        fig.tight_layout(); fig.savefig(os.path.join(HERE, "task1_scan.png"), dpi=100)
    except Exception as e:
        print(f"[scan] figure skipped: {e!r}")
    print("[scan] done", flush=True)


if __name__ == "__main__":
    main()
