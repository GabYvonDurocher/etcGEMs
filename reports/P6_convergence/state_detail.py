#!/usr/bin/env python3
"""P6 addendum 5, second pass -- WHICH term moves between the first and second evaluation of
the same theta on one model, temperature by temperature (growth, O2, solver status), and at
every temperature that moves, the O2 range at fixed optimal growth (FVA) and the growth optimum
re-solved after a basis reset. Diagnosis only. Writes state_detail.json beside this file.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, HERE)
os.chdir(ROOT)
from etcgem.calibration_multi import _build_gasflux_ctx, gasflux_log_likelihood, to_pert, _MASK_G  # noqa: E402
from etcgem.gasflux import flux_tpc                                                        # noqa: E402
from etcgem.tpc import apply_state                                                         # noqa: E402
from p6_fits import FITS, p4_dir_for                                                       # noqa: E402
from state_vs_identifiability import build, points, o2_fva_at                             # noqa: E402

out = {}
for fit in FITS:
    label = fit[0]
    if label not in ("E_NLDM", "E_LB", "F_NLDM", "F_LB", "D_LB"):
        continue
    th, _ = points(fit)
    ctx, specs = build(fit)
    pert = to_pert(th, specs)
    recs = []
    for k in range(3):
        L = gasflux_log_likelihood(th, ctx, specs)
        df = flux_tpc(ctx["pm"], ctx["T"], pert, metabolites=("o2",))
        recs.append(dict(L=L, g=df["growth"].to_numpy(float), o2=df["o2_uptake"].to_numpy(float), st=df["status"].tolist()))
    T = ctx["T"]
    moved = [i for i in range(len(T)) if (abs(recs[0]["g"][i] - recs[1]["g"][i]) > 1e-6
                                          or (np.nan_to_num(recs[0]["o2"][i], nan=-1) != np.nan_to_num(recs[1]["o2"][i], nan=-1)
                                              and abs(np.nan_to_num(recs[0]["o2"][i], nan=-1) - np.nan_to_num(recs[1]["o2"][i], nan=-1)) > 1e-4))]
    print(f"[detail] {label}: L first {recs[0]['L']:.4f}, second {recs[1]['L']:.4f}, third {recs[2]['L']:.4f}", flush=True)
    per_T = []
    for i in moved:
        lo, hi, gstar = o2_fva_at(ctx, th, specs, T[i])     # on the model in its current (post-3rd-call) state
        m = ctx["pm"].ec.model
        try:
            m.solver.problem.reset()
        except Exception:
            pass
        apply_state(ctx["pm"].ec, float(T[i]), pert); g_reset = m.slim_optimize()
        per_T.append(dict(T=float(T[i]), g_first=float(recs[0]["g"][i]), g_second=float(recs[1]["g"][i]),
                          o2_first=float(recs[0]["o2"][i]), o2_second=float(recs[1]["o2"][i]),
                          status_first=recs[0]["st"][i], status_second=recs[1]["st"][i],
                          fva_o2_lo=lo, fva_o2_hi=hi, g_star_fva=gstar, g_after_basis_reset=float(g_reset) if g_reset is not None else None,
                          alive_first=bool(recs[0]["g"][i] >= _MASK_G), alive_second=bool(recs[1]["g"][i] >= _MASK_G)))
        print(f"[detail]   {T[i]:4.0f}C  growth {recs[0]['g'][i]:.5f} -> {recs[1]['g'][i]:.5f} ({recs[0]['st'][i]}/{recs[1]['st'][i]})  "
              f"O2 {recs[0]['o2'][i]:.3f} -> {recs[1]['o2'][i]:.3f}  FVA O2 at g* [{lo:.3f}, {hi:.3f}] (g*={gstar:.5f}); g after basis reset {g_reset:.5f}", flush=True)
    out[label] = dict(L=[r["L"] for r in recs], T=T.tolist(), g_first=recs[0]["g"].tolist(), g_second=recs[1]["g"].tolist(),
                      o2_first=recs[0]["o2"].tolist(), o2_second=recs[1]["o2"].tolist(), moved=per_T)
json.dump(out, open(os.path.join(HERE, "state_detail.json"), "w"), indent=1)
print("[detail] done", flush=True)
