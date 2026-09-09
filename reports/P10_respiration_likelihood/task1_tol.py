#!/usr/bin/env python3
"""P10 TASK 1 -- does tightening Gurobi's optimality/feasibility tolerances make the pfba
tie-break reproducible on E LB and F LB? The D3a reuse test (theta, theta again, theta after
theta') under pfba with tolerances 1e-7 (default) and 1e-9. Characterises; adopts nothing.
Writes task1_tol.csv beside this file."""
import os, sys
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src")); sys.path.insert(0, os.path.join(ROOT, "reports", "P6_convergence")); os.chdir(ROOT)
from etcgem.calibration_multi import gasflux_log_likelihood   # noqa: E402
from p6_fits import FITS                                      # noqa: E402
from state_vs_identifiability import build, points            # noqa: E402
rows = []
for want in ("E_LB", "F_LB", "E_NLDM"):
    fit = [f for f in FITS if f[0] == want][0]; th, th2 = points(fit)
    for tol in (1e-7, 1e-9):
        ctx, sp = build(fit); ctx["respiration"] = {"tiebreak": "pfba"}; gp = ctx["pm"].ec.model.solver.problem
        gp.setParam("OptimalityTol", tol); gp.setParam("FeasibilityTol", tol)
        L1 = gasflux_log_likelihood(th, ctx, sp); L2 = gasflux_log_likelihood(th, ctx, sp); gasflux_log_likelihood(th2, ctx, sp); L3 = gasflux_log_likelihood(th, ctx, sp)
        rows.append(dict(fit=want, tol=tol, consecutive=abs(L1 - L2), after_other=abs(L3 - L1), logL=L1))
        print(f"[tol] {want:7s} tol {tol:g}: consecutive {abs(L1-L2):.4f} after-theta' {abs(L3-L1):.4f} (logL {L1:.3f})", flush=True)
pd.DataFrame(rows).to_csv(os.path.join(HERE, "task1_tol.csv"), index=False); print("[tol] done")
