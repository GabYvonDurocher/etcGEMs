#!/usr/bin/env python3
"""P13 TASK 3 -- one (line, scheme) scan, in its own module so pool workers can import it.

P9's instrument exactly -- 41 points at 0.05 sd over +/- 1 posterior sd, FRESH MODEL PER
EVALUATION, so no solver state carries between points -- but centred on p38 rather than P4's MAP,
and with the P13 support option applied through ctx["respiration"].
"""
import os, sys, time
import numpy as np
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
for p in (os.path.join(ROOT, "src"), os.path.join(ROOT, "reports", "P6_convergence"),
          os.path.join(ROOT, "reports", "P9_surface")):
    if p not in sys.path: sys.path.insert(0, p)

SCHEMES = {"current": {}, "clamp": {"support": "clamp", "weight_floor": 1.0}}


def scan(arg):
    """arg = (line_name, scheme, theta0, sd, names). Returns per-point rows."""
    lname, scheme, theta0, sd, names = arg
    os.chdir(ROOT)
    from etcgem.calibration_multi import gasflux_log_likelihood, to_pert
    from etcgem.gasflux import flux_tpc
    from p6_fits import FITS
    from task1_scan import build, STEPS
    from task2_solver import direction_factory
    fit = [f for f in FITS if f[0] == "D_NLDM"][0]
    v = direction_factory(list(names))(lname)
    theta0 = np.asarray(theta0, float); sd = np.asarray(sd, float)
    out, t0 = [], time.time()
    for s in STEPS:
        ctx, sp = build(fit)                       # FRESH model for this point
        base = dict(ctx.get("respiration") or {})
        ctx["respiration"] = dict(base, **SCHEMES[scheme])
        th = theta0 + s * sd * v
        ll = float(gasflux_log_likelihood(th, ctx, sp))
        resp = ctx["respiration"]
        df = flux_tpc(ctx["pm"], ctx["T"], to_pert(th, sp), metabolites=("o2",),
                      tiebreak=str(resp.get("tiebreak", "none")),
                      growth_tol=float(resp.get("growth_tol", 1e-6)),
                      tiebreak_tol=float(resp.get("tiebreak_tol", 1e-9)))
        g = df["growth"].to_numpy(float); o2 = df["o2_uptake"].to_numpy(float)
        out.append(dict(line=lname, scheme=scheme, step_sd=float(s), logL=ll,
                        min_growth=float(np.nanmin(g)), n_infeasible=int((~np.isfinite(o2)).sum()),
                        n_below_mask=int((g < 1e-4).sum()),
                        T_min_growth=float(np.asarray(ctx["T"], float)[int(np.nanargmin(g))])))
    return lname, scheme, out, round(time.time() - t0, 1)
