#!/usr/bin/env python3
"""P9 TASK 2 (attribution) -- at the three largest jumps of the fresh-build scan, rebuild a fresh
model at each end (exactly as the scan did) and decompose the log-likelihood per temperature
into its growth and respiration terms, with the LP status, so the jump is attributed to a
named temperature and a named term. Writes task2_attribution.csv beside this file.
"""
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "reports", "P6_convergence"))
sys.path.insert(0, HERE)
os.chdir(ROOT)
from etcgem.calibration_multi import gasflux_log_likelihood, to_natural, to_pert, _MASK_G   # noqa: E402
from etcgem.gasflux import flux_tpc                                                       # noqa: E402
from etcgem import providers as _prov                                                     # noqa: E402
from etcgem.gasflux import add_total_carbon_constraint                                    # noqa: E402
from p6_fits import FITS                                                                  # noqa: E402
from task1_scan import build, STEPS                                                       # noqa: E402
from task2_solver import direction_factory                                                # noqa: E402


def terms(th, ctx, sp):
    """the likelihood's own arithmetic, per temperature"""
    nat = to_natural(th, sp); pert = to_pert(th, sp); pm = ctx["pm"]
    r = ctx["recipe"]; _prov.set_medium_recipe(pm, r["recipe_csv"], clearance_L_per_gDW_h=r["clearance"] * float(nat["clearance_mult"]), uptake_ub=r.get("uptake_ub", 1000.0), verbose=False)
    add_total_carbon_constraint(pm, float(ctx["c_max"]))
    df = flux_tpc(pm, ctx["T"], pert, metabolites=("o2",))
    g = df["growth"].to_numpy(float); o2 = df["o2_uptake"].to_numpy(float); st = df["status"].tolist()
    dg = float(nat["disc_growth"]); var = ctx["growth_sd"] ** 2 + dg ** 2
    gterm = -0.5 * ((ctx["growth_obs"] - g) ** 2 / var + np.log(2 * np.pi * var))
    keep = (g >= _MASK_G) & (o2 > 0); dr = float(nat["disc_resp"]); rs = float(nat["resp_scale"])
    rterm = np.zeros_like(g)
    if keep.any():
        pred = np.log(o2[keep] * ctx["o2_conv"] * rs); obsl = np.log(ctx["resp_obs"][keep]); rel = ctx["resp_sd"][keep] / ctx["resp_obs"][keep]; varr = rel ** 2 + dr ** 2
        rterm[keep] = -0.5 * ((obsl - pred) ** 2 / varr + np.log(2 * np.pi * varr))
    return g, o2, st, keep, gterm, rterm, float(gterm.sum() + rterm.sum()), float(gasflux_log_likelihood(th, ctx, sp))


def main():
    fit = [f for f in FITS if f[0] == "D_NLDM"][0]
    meta = json.load(open(os.path.join(HERE, "task1_meta.json"))); theta0 = np.array(meta["theta0"]); sd = np.array(meta["sd"])
    direction = direction_factory(meta["names"])
    L = pd.read_csv(os.path.join(HERE, "task1_lines.csv")); jumps = []
    for lname, sub in L.groupby("line"):
        vals = sub.logL.to_numpy(); d1 = np.abs(np.diff(vals)); k = int(np.argmax(d1)); jumps.append((float(d1[k]), lname, k, float(vals[k]), float(vals[k + 1])))
    jumps.sort(reverse=True); rows = []
    for jval, lname, k, la, lb in jumps[:3]:
        v = direction(lname)
        ca, sa = build(fit); A = terms(theta0 + STEPS[k] * sd * v, ca, sa)
        cb, sb = build(fit); B = terms(theta0 + STEPS[k + 1] * sd * v, cb, sb)
        print(f"[attr] {lname} {STEPS[k]:+.2f} -> {STEPS[k+1]:+.2f} sd: scan logL {la:.2f} -> {lb:.2f} (jump {jval:.2f}); recomputed {A[7]:.2f} -> {B[7]:.2f} (terms sum {A[6]:.2f} -> {B[6]:.2f})", flush=True)
        for i, T in enumerate(ca["T"]):
            dgt = B[4][i] - A[4][i]; drt = B[5][i] - A[5][i]
            rows.append(dict(line=lname, step_from=float(STEPS[k]), step_to=float(STEPS[k + 1]), T_C=float(T), status_from=A[2][i], status_to=B[2][i],
                             growth_from=A[0][i], growth_to=B[0][i], o2_from=A[1][i], o2_to=B[1][i], alive_from=bool(A[3][i]), alive_to=bool(B[3][i]),
                             growth_term_from=A[4][i], growth_term_to=B[4][i], d_growth_term=dgt, resp_term_from=A[5][i], resp_term_to=B[5][i], d_resp_term=drt))
            if abs(dgt) + abs(drt) > 0.5:
                print(f"[attr]    {T:4.0f} C  status {A[2][i]}->{B[2][i]}  growth {A[0][i]:.4f}->{B[0][i]:.4f}  O2 {A[1][i]:.3f}->{B[1][i]:.3f}  alive {A[3][i]}->{B[3][i]}  d growth term {dgt:+.2f}  d resp term {drt:+.2f}", flush=True)
    pd.DataFrame(rows).to_csv(os.path.join(HERE, "task2_attribution.csv"), index=False)
    print("[attr] done", flush=True)


if __name__ == "__main__":
    main()
