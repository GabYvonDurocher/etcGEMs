#!/usr/bin/env python3
"""P4 TASK 2 -- run the nine scoped refits, in order, committing after each.

Long-running and unattended by design. Ordered so that a partial run still answers the most
important question first (configuration D, where the medium change bites hardest). Each fit
writes to a NEW directory named for its settings; Parsa's ported outputs are never touched,
because they are the comparison.

Resumable: a fit whose summary.json already exists is skipped.

    python reports/P4_refit/run_fits.py [--only D_NLDM,D_LB] [--no-commit]
"""
import argparse
import json
import os
import subprocess
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, HERE)
os.chdir(ROOT)

from etcgem.calibration_multi import run_gasflux_fit, to_natural, to_pert   # noqa: E402
from fits import FITS, out_dir_for                                          # noqa: E402

# Parsa's own sampler settings, per configuration, from his chain files.
STEPS = {"D": 2000, "E": 1500, "F": 1500}
WALKERS = 36
DENSE = np.arange(8.0, 55.01, 1.5)


def git(*args):
    return subprocess.run(["git", "-C", ROOT, *args], capture_output=True, text=True)


def r2(obs, Tobs, pred, Tpred):
    p = np.interp(Tobs, Tpred, pred)
    k = np.isfinite(p) & np.isfinite(obs)
    o, pp = np.asarray(obs)[k], p[k]
    ss = float(np.sum((o - pp) ** 2))
    return 1.0 - ss / float(np.sum((o - o.mean()) ** 2))


def score(out_dir, label, cfg, medium, table, otu, c_max, etc_table, protons, fit_k):
    """R2 the way his figure script does it: one point from the chain (median for D, MAP for
    E and F -- P3 established which), on the dense grid, interpolated onto the observed T."""
    from etcgem.calibration_multi import _build_gasflux_ctx
    from etcgem.gasflux import flux_tpc
    ctx, specs = _build_gasflux_ctx(strain="eciML1515", medium=medium,
                                    experiment=f"gasflux_config{cfg}", table=table, otu=otu,
                                    c_max=c_max, etc_table=etc_table, apply_protons=protons,
                                    fit_clearance=fit_k)
    flat = np.load(os.path.join(out_dir, "flat.npy"))
    chain = np.load(os.path.join(out_dir, "chain.npy"))
    lp = np.load(os.path.join(out_dir, "log_prob.npy"))
    i, j = np.unravel_index(np.nanargmax(lp), lp.shape)
    points = {"posterior median": np.median(flat, axis=0), "MAP": chain[i, j]}
    out = {}
    for name, theta in points.items():
        nat = to_natural(theta, specs)
        if "clearance_mult" in nat:
            from etcgem import providers as _prov
            r = ctx["recipe"]
            _prov.set_medium_recipe(ctx["pm"], r["recipe_csv"],
                                    clearance_L_per_gDW_h=r["clearance"] * float(nat["clearance_mult"]),
                                    uptake_ub=r.get("uptake_ub", 1000.0), verbose=False)
            if ctx.get("c_max") is not None:
                from etcgem.gasflux import add_total_carbon_constraint
                add_total_carbon_constraint(ctx["pm"], float(ctx["c_max"]))
        if "F_ETC_mult" in nat:
            from etcgem import etc_area as _ea
            _ea.add_etc_area_constraint(
                ctx["pm"], ctx["etc_table"],
                _ea.budget_from_fraction(ctx["a_mem"], ctx["f_etc_nom"] * float(nat["F_ETC_mult"])))
        df = flux_tpc(ctx["pm"], DENSE, to_pert(theta, specs), metabolites=("o2", "co2", "ac"))
        g = df["growth"].to_numpy(float)
        rr = df["o2_uptake"].to_numpy(float) * ctx["o2_conv"] * float(nat["resp_scale"])
        i37 = int(np.argmin(np.abs(DENSE - 37.0)))
        with np.errstate(divide="ignore", invalid="ignore"):
            rq = float(df["co2_release"][i37] / df["o2_uptake"][i37]) if df["o2_uptake"][i37] else float("nan")
        out[name] = {"growth_R2": r2(ctx["growth_obs"], ctx["T"], g, DENSE),
                     "resp_R2": r2(ctx["resp_obs"], ctx["T"], rr, DENSE),
                     "rmax": float(np.nanmax(g)), "Topt_C": float(DENSE[int(np.nanargmax(g))]),
                     "acetate_37C": float(df["ac_release"][i37]), "RQ_37C": rq,
                     "resp_scale": float(nat["resp_scale"])}
    with open(os.path.join(out_dir, "scores.json"), "w") as fh:
        json.dump(out, fh, indent=2)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default=None)
    ap.add_argument("--no-commit", action="store_true")
    args = ap.parse_args()
    want = set(args.only.split(",")) if args.only else None

    t_all = time.time()
    for label, cfg, medium, table, otu, c_max, etc_table, protons, fit_k in FITS:
        if want and label not in want:
            continue
        rel = os.path.join("strains", "eciML1515", "outputs", out_dir_for(label, cfg, medium))
        out_dir = os.path.join(ROOT, rel)
        if os.path.exists(os.path.join(out_dir, "summary.json")):
            print(f"[run] {label}: already done, skipping", flush=True)
            continue
        print(f"\n{'=' * 70}\n[run] {label}  ({cfg} on {medium})  -> {rel}\n{'=' * 70}", flush=True)
        t0 = time.time()
        try:
            res = run_gasflux_fit("eciML1515", out_dir, medium=medium, table=table, otu=otu,
                                  experiment=f"gasflux_config{cfg}", c_max=c_max,
                                  etc_table=etc_table, apply_protons=protons,
                                  fit_clearance=fit_k, label=label,
                                  n_walkers=WALKERS, n_steps_max=STEPS[cfg], seed=1)
            sc = score(out_dir, label, cfg, medium, table, otu, c_max, etc_table, protons, fit_k)
            print(f"[run] {label}: growth R2 {sc['posterior median']['growth_R2']:.3f} (median) / "
                  f"{sc['MAP']['growth_R2']:.3f} (MAP); resp R2 "
                  f"{sc['posterior median']['resp_R2']:.3f} / {sc['MAP']['resp_R2']:.3f}", flush=True)
        except SystemExit as e:
            print(f"[run] {label}: STOPPED -- {e}", flush=True)
            continue
        except Exception as e:
            print(f"[run] {label}: FAILED -- {type(e).__name__}: {e}", flush=True)
            continue
        if not args.no_commit:
            # stage ONLY this fit's directory: K4 is running in parallel under strains/c*/
            git("add", rel)
            msg = (f"P4 TASK 2: refit {label} under the canonical settings\n\n"
                   f"{res['sampler']['n_steps']} steps x {res['sampler']['n_walkers']} walkers, "
                   f"{res['sampler']['wall_time_s'] / 60:.1f} min, accept "
                   f"{res['sampler']['acceptance_fraction']}, tau "
                   f"{res['sampler']['autocorr_time_max']}, "
                   f"{'CONVERGED' if res['sampler']['converged'] else 'NOT CONVERGED'}.\n"
                   f"{res['sampler']['stop_reason']}\n\n"
                   f"Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>\n"
                   f"Claude-Session: https://claude.ai/code/session_01YQYJ13QULcrKdLubPkCeRN\n")
            r = git("commit", "-m", msg)
            print(f"[run] {label}: committed ({r.returncode}) in {(time.time() - t0) / 60:.1f} min",
                  flush=True)
    print(f"\n[run] ALL DONE in {(time.time() - t_all) / 60:.1f} min", flush=True)


if __name__ == "__main__":
    main()
