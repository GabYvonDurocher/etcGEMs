#!/usr/bin/env python3
"""P10 TASK 1 -- functional check of the tie-break on D NLDM at P4's MAP: O2 per temperature
under none / pfba / min_o2 / max_o2, statuses, repeat determinism on one reused model, and the
cost per likelihood evaluation. Writes task1_check.json beside this file."""
import json, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src")); sys.path.insert(0, os.path.join(ROOT, "reports", "P6_convergence")); sys.path.insert(0, os.path.join(ROOT, "reports", "P9_surface")); os.chdir(ROOT)
from etcgem.calibration_multi import gasflux_log_likelihood, to_pert   # noqa: E402
from etcgem.gasflux import flux_tpc                                     # noqa: E402
from p6_fits import FITS                                                # noqa: E402
from task1_scan import build                                            # noqa: E402
fit = [f for f in FITS if f[0] == "D_NLDM"][0]
theta = np.array(json.load(open(os.path.join(ROOT, "reports", "P9_surface", "task1_meta.json")))["theta0"])
out = {}
ctx, sp = build(fit); gasflux_log_likelihood(theta, ctx, sp); pert = to_pert(theta, sp)
for tb in ("none", "pfba", "min_o2", "max_o2"):
    t0 = time.time(); df = flux_tpc(ctx["pm"], ctx["T"], pert, metabolites=("o2",), tiebreak=tb); dt = time.time() - t0
    out[tb] = dict(o2=df["o2_uptake"].round(4).tolist(), growth=df["growth"].round(5).tolist(), status=df["status"].tolist(),
                   tiebreak_status=df["tiebreak_status"].tolist() if "tiebreak_status" in df else None, seconds=round(dt, 2))
    print(f"[check] {tb:7s} {dt:5.2f} s  O2: {np.round(df['o2_uptake'].to_numpy(), 3).tolist()}", flush=True)
# repeat determinism under pfba on one reused model (theta, theta', theta)
ctx2, sp2 = build(fit); ctx2["respiration"] = {"tiebreak": "pfba"}
th2 = theta.copy(); th2[0] += 0.3
L = [gasflux_log_likelihood(theta, ctx2, sp2), gasflux_log_likelihood(theta, ctx2, sp2), gasflux_log_likelihood(th2, ctx2, sp2), gasflux_log_likelihood(theta, ctx2, sp2)]
out["pfba_reuse_logL"] = L; out["pfba_reuse_spread"] = float(max(L[0], L[1], L[3]) - min(L[0], L[1], L[3]))
ctx3, sp3 = build(fit); t0 = time.time(); l_none = gasflux_log_likelihood(theta, ctx3, sp3); t_none = time.time() - t0
ctx3["respiration"] = {"tiebreak": "pfba"}; t0 = time.time(); l_pfba = gasflux_log_likelihood(theta, ctx3, sp3); t_pfba = time.time() - t0
out["cost_s_per_eval"] = dict(none=round(t_none, 3), pfba=round(t_pfba, 3)); out["logL_none_vs_pfba_at_MAP"] = [l_none, l_pfba]
print(f"[check] pfba reuse: theta, theta, theta', theta -> {np.round(L,4).tolist()} spread {out['pfba_reuse_spread']:.4f}")
print(f"[check] cost per likelihood evaluation: none {t_none:.2f} s, pfba {t_pfba:.2f} s; logL at MAP none {l_none:.3f} pfba {l_pfba:.3f}")
json.dump(out, open(os.path.join(HERE, "task1_check.json"), "w"), indent=1); print("[check] done")
