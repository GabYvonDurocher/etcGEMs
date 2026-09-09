#!/usr/bin/env python3
"""P9 TASK 2 (mechanism) -- at the temperature that carries each of the three largest jumps, is
the O2 uptake at optimal growth a face (FVA range) on fresh models at both ends of the step?
Writes task2_fva_at_jump.csv beside this file."""
import json, os, sys
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src")); sys.path.insert(0, os.path.join(ROOT, "reports", "P6_convergence")); sys.path.insert(0, HERE); os.chdir(ROOT)
from etcgem.calibration_multi import gasflux_log_likelihood, to_pert   # noqa: E402
from etcgem.tpc import apply_state                                       # noqa: E402
from p6_fits import FITS                                                 # noqa: E402
from task1_scan import build, STEPS                                      # noqa: E402
from task2_solver import direction_factory                               # noqa: E402
sys.path.insert(0, os.path.join(ROOT, "reports", "P6_convergence"))
from state_vs_identifiability import o2_fva_at                           # noqa: E402

JUMPS = [("axis:dCp_scale", 18, 25.0), ("random1", 19, 20.0), ("PC2", 0, 20.0)]   # k index of the step start; the carrying temperature
fit = [f for f in FITS if f[0] == "D_NLDM"][0]
meta = json.load(open(os.path.join(HERE, "task1_meta.json"))); theta0 = np.array(meta["theta0"]); sd = np.array(meta["sd"]); direction = direction_factory(meta["names"])
rows = []
for lname, k, T in JUMPS:
    v = direction(lname)
    for tag, s in (("from", STEPS[k]), ("to", STEPS[k + 1])):
        ctx, sp = build(fit); th = theta0 + s * sd * v
        gasflux_log_likelihood(th, ctx, sp)           # medium + cap installed at theta
        lo, hi, g = o2_fva_at(ctx, th, sp, T)
        rows.append(dict(line=lname, end=tag, step_sd=float(s), T_C=T, growth=g, o2_fva_min=lo, o2_fva_max=hi, width=hi - lo))
        print(f"[fva] {lname} {tag} ({s:+.2f} sd) at {T:.0f} C: growth {g:.4f}, O2 at fixed optimum in [{lo:.3f}, {hi:.3f}] (width {hi-lo:.3f})", flush=True)
pd.DataFrame(rows).to_csv(os.path.join(HERE, "task2_fva_at_jump.csv"), index=False); print("[fva] done")
