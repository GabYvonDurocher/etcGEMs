#!/usr/bin/env python3
"""P10 TASK 3 -- decompose the largest remaining step of each of the twelve lines under (c),
per temperature and per term, on fresh models at both ends, the likelihood's own arithmetic
with both options on. Writes task3_attribution.csv beside this file."""
import json, os, sys
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src")); sys.path.insert(0, os.path.join(ROOT, "reports", "P6_convergence")); sys.path.insert(0, os.path.join(ROOT, "reports", "P9_surface")); os.chdir(ROOT)
from etcgem.calibration_multi import gasflux_log_likelihood, to_natural, to_pert, _MASK_G   # noqa: E402
from etcgem.gasflux import flux_tpc, add_total_carbon_constraint                            # noqa: E402
from etcgem import providers as _prov                                                      # noqa: E402
from p6_fits import FITS                                                                   # noqa: E402
from task1_scan import build, STEPS                                                        # noqa: E402
from task2_solver import direction_factory                                                 # noqa: E402
OPT = {"tiebreak": "pfba", "log_o2_floor": 0.76, "alive_soft_growth": 0.01}


def terms(th, ctx, sp):
    ctx["respiration"] = dict(OPT); nat = to_natural(th, sp); pert = to_pert(th, sp); pm = ctx["pm"]
    r = ctx["recipe"]; _prov.set_medium_recipe(pm, r["recipe_csv"], clearance_L_per_gDW_h=r["clearance"] * float(nat["clearance_mult"]), uptake_ub=r.get("uptake_ub", 1000.0), verbose=False)
    add_total_carbon_constraint(pm, float(ctx["c_max"]))
    df = flux_tpc(pm, ctx["T"], pert, metabolites=("o2",), tiebreak="pfba", tiebreak_tol=1e-9)
    g = df["growth"].to_numpy(float); o2 = df["o2_uptake"].to_numpy(float)
    dg = float(nat["disc_growth"]); var = ctx["growth_sd"] ** 2 + dg ** 2
    gterm = -0.5 * ((ctx["growth_obs"] - g) ** 2 / var + np.log(2 * np.pi * var))
    keep = (g >= _MASK_G) & (o2 > 0); dr = float(nat["disc_resp"]); rs = float(nat["resp_scale"]); rterm = np.zeros_like(g); w = np.zeros_like(g)
    if keep.any():
        pred = np.log(o2[keep] * ctx["o2_conv"] * rs); obsl = np.log(ctx["resp_obs"][keep]); rel = ctx["resp_sd"][keep] / ctx["resp_obs"][keep]; varr = rel ** 2 + dr ** 2 + 0.76 ** 2
        w[keep] = np.minimum(1.0, g[keep] / 0.01); rterm[keep] = -0.5 * w[keep] * ((obsl - pred) ** 2 / varr + np.log(2 * np.pi * varr))
    return g, o2, w, gterm, rterm, float(gterm.sum() + rterm.sum()), float(gasflux_log_likelihood(th, ctx, sp))


def main():
    fit = [f for f in FITS if f[0] == "D_NLDM"][0]
    meta = json.load(open(os.path.join(ROOT, "reports", "P9_surface", "task1_meta.json"))); theta0 = np.array(meta["theta0"]); sd = np.array(meta["sd"]); direction = direction_factory(meta["names"])
    L = pd.read_csv(os.path.join(HERE, "lines_both.csv")); rows = []
    for lname, sub in L.groupby("line"):
        pts = sub.drop_duplicates("step_sd").sort_values("step_sd"); vals = pts.logL.to_numpy(); steps = pts.step_sd.to_numpy(); d1 = np.abs(np.diff(vals)); k = int(np.argmax(d1))
        v = direction(lname); ca, sa = build(fit); A = terms(theta0 + steps[k] * sd * v, ca, sa); cb, sb = build(fit); B = terms(theta0 + steps[k + 1] * sd * v, cb, sb)
        print(f"[attr] {lname:22s} largest step {steps[k]:+.2f}->{steps[k+1]:+.2f} sd: {d1[k]:.2f} units (recomputed {B[6]-A[6]:+.2f})", flush=True)
        for i, T in enumerate(ca["T"]):
            dgt = B[3][i] - A[3][i]; drt = B[4][i] - A[4][i]
            rows.append(dict(line=lname, step_from=steps[k], step_to=steps[k + 1], step_logL=d1[k], T_C=float(T), growth_from=A[0][i], growth_to=B[0][i], o2_from=A[1][i], o2_to=B[1][i], w_from=A[2][i], w_to=B[2][i], d_growth_term=dgt, d_resp_term=drt))
            if abs(dgt) + abs(drt) > 0.5: print(f"[attr]    {T:4.0f} C growth {A[0][i]:.4f}->{B[0][i]:.4f} O2 {A[1][i]:.3f}->{B[1][i]:.3f} w {A[2][i]:.2f}->{B[2][i]:.2f}  d growth term {dgt:+.2f}  d resp term {drt:+.2f}", flush=True)
    pd.DataFrame(rows).to_csv(os.path.join(HERE, "task3_attribution.csv"), index=False); print("[attr] done", flush=True)


if __name__ == "__main__":
    main()
