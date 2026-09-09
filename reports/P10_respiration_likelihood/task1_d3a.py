#!/usr/bin/env python3
"""P10 TASK 1 -- the D3a instrument (P6) re-run under the tie-break: for each of the six
NLDM/LB fits, at P4's MAP theta and a second vector theta', the log-likelihood on one reused
model (theta, theta again; theta, theta', theta) and on models rebuilt fresh, under
tiebreak=none and tiebreak=pfba. Every pfba cell must be 0.0000. Also: O2 at Parsa's E LB
theta (P3's gate point) at 37/40/45/50 C under none / pfba / min_o2 / max_o2, so the reader
sees where on the face pfba lands. And the cost per evaluation, none vs pfba, per fit.
Writes task1_d3a.csv, task1_elb_face.csv, task1_cost.csv beside this file.
"""
import json, os, sys, time
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src")); sys.path.insert(0, os.path.join(ROOT, "reports", "P6_convergence")); sys.path.insert(0, os.path.join(ROOT, "reports", "P3_gate")); os.chdir(ROOT)
from etcgem.calibration_multi import _build_gasflux_ctx, gasflux_log_likelihood, to_pert   # noqa: E402
from etcgem.gasflux import flux_tpc                                                       # noqa: E402
from etcgem.tpc import apply_state                                                        # noqa: E402
from p6_fits import FITS, p4_dir_for                                                      # noqa: E402
from state_vs_identifiability import build, points                                        # noqa: E402
import gate_def as G                                                                      # noqa: E402

WANT = ("D_NLDM", "D_LB", "E_NLDM", "E_LB", "F_NLDM", "F_LB")


BOTH = "--both" in sys.argv


def ll(th, ctx, sp, tb):
    ctx["respiration"] = ({"tiebreak": tb, "log_o2_floor": 0.76, "alive_soft_growth": 0.01} if BOTH else {"tiebreak": tb})
    return gasflux_log_likelihood(th, ctx, sp)


def main():
    rows, cost = [], []
    for fit in FITS:
        label = fit[0]
        if label not in WANT: continue
        th, th2 = points(fit)
        for tb in ("none", "pfba"):
            ctx, sp = build(fit)
            t0 = time.time(); L1 = ll(th, ctx, sp, tb); dt = time.time() - t0
            L1b = ll(th, ctx, sp, tb); ll(th2, ctx, sp, tb); L3 = ll(th, ctx, sp, tb)
            cA, sA = build(fit); R1 = ll(th, cA, sA, tb); cB, sB = build(fit); R2 = ll(th, cB, sB, tb)
            cC, sC = build(fit); ll(th2, cC, sC, tb); R3 = ll(th, cC, sC, tb)
            rows.append(dict(fit=label, tiebreak=tb, reuse_consecutive=abs(L1 - L1b), reuse_after_other=abs(L3 - L1), rebuild_twice=abs(R1 - R2),
                             rebuild_then_history=abs(R3 - R1), fresh_vs_reused_first=abs(R1 - L1), logL=L1))
            cost.append(dict(fit=label, tiebreak=tb, s_per_eval=round(dt, 3)))
            print(f"[d3a] {label:7s} {tb:5s} reuse: consecutive {abs(L1-L1b):.4f} after-theta' {abs(L3-L1):.4f} | rebuild: twice {abs(R1-R2):.4f} history {abs(R3-R1):.4f} | fresh-vs-reused {abs(R1-L1):.4f} | {dt:.2f} s/eval", flush=True)
    pd.DataFrame(rows).to_csv(os.path.join(HERE, "task3_d3a_both.csv" if BOTH else "task1_d3a.csv"), index=False)
    pd.DataFrame(cost).to_csv(os.path.join(HERE, "task3_cost_both.csv" if BOTH else "task1_cost.csv"), index=False)
    if BOTH:
        print("[d3a] done", flush=True); return
    # E LB at Parsa's theta: the face under the four tie-breaks at 37/40/45/50 C
    fit = [f for f in FITS if f[0] == "E_LB"][0]
    cdir = os.path.join(os.environ.get("PARSA_ROOT", "/Users/g.yvon-durocher/Downloads/etcGEMs-main_3"), "strains", "eciML1515", "outputs", "calibration_configE_LB_freecmax")
    from task1e_reoptimise import his_theta_in_our_specs  # noqa
    face = []
    for tb in ("none", "pfba", "min_o2", "max_o2"):
        ctx, sp = build(fit); th_his, his_cap = his_theta_in_our_specs(cdir, sp)
        ctx["respiration"] = {"tiebreak": tb}; gasflux_log_likelihood(th_his, ctx, sp)
        df = flux_tpc(ctx["pm"], np.array([37.0, 40.0, 45.0, 50.0]), to_pert(th_his, sp), metabolites=("o2",), tiebreak=tb)
        for T, g, o2 in zip(df.temp_C, df.growth, df.o2_uptake):
            face.append(dict(tiebreak=tb, T_C=float(T), growth=float(g), o2=float(o2)))
        print(f"[d3a] E LB at Parsa's theta, {tb:6s}: O2 at 37/40/45/50 C = {np.round(df.o2_uptake.to_numpy(), 3).tolist()} (growth {np.round(df.growth.to_numpy(), 4).tolist()})", flush=True)
    pd.DataFrame(face).to_csv(os.path.join(HERE, "task1_elb_face.csv"), index=False)
    print("[d3a] done", flush=True)


if __name__ == "__main__":
    sys.path.insert(0, os.path.join(ROOT, "reports", "P5_lb_cmax"))
    main()
