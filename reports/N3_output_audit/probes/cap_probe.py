"""N3 TASK 2 probe: TPC + translation-cap binding, per temperature.

Runs UNCHANGED in the current tree and in a pre-a416fd1 worktree: it only uses
config.resolve / build_provider / ec.set_temperature / ec.set_allocation, which have the
same signatures in both. Writes a CSV; decides nothing.
"""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.join(os.getcwd(), "src"))
from etcgem.config import resolve, build_provider, temperature_grid
from etcgem.enzyme_cost import Perturbation

out = sys.argv[1]
cfg = resolve("eciML1515")
pm = build_provider(cfg)
ec = pm.ec
temps = np.asarray(temperature_grid(cfg), float)
pert = Perturbation()
CAP = "proteome_biosynthesis"
POOL = getattr(ec, "POOL", "enzyme_pool")
rows = []
for Tc in temps:
    ec.set_temperature(Tc + 273.15, pert)
    if getattr(ec, "_alloc_from_data", None) is not None and ec._sectors is not None:
        fm, fmaint = ec._alloc_from_data.model_alloc(float(Tc))
        ec.set_allocation(fm, fmaint)
    else:
        ec.set_budget(pert.budget if pert.budget is not None else ec.default_budget,
                      pert.group_alloc)
    g = ec.model.slim_optimize()
    g = 0.0 if (g is None or not np.isfinite(g) or g < 1e-6) else float(g)
    r = {"temp_C": float(Tc), "growth": g}
    for key, cname in (("cap", CAP), ("pool", POOL)):
        c = ec.model.constraints.get(cname)
        if c is None:
            r[f"{key}_lhs"] = r[f"{key}_ub"] = r[f"{key}_slack"] = float("nan")
            continue
        try:
            lhs = float(c.primal)
        except Exception:
            lhs = float("nan")
        ub = float(c.ub) if c.ub is not None else float("nan")
        r[f"{key}_lhs"] = lhs
        r[f"{key}_ub"] = ub
        r[f"{key}_slack"] = ub - lhs
    rows.append(r)

import csv
os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
with open(out, "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
meta = {"cwd": os.getcwd(),
        "f_metab_cfg": (cfg.get("proteome_sectors") or {}).get("f_metab"),
        "f_maint_cfg": (cfg.get("proteome_sectors") or {}).get("f_maint"),
        "allocation_from_data": cfg.get("allocation_from_data"),
        "sectors": {k: (v if isinstance(v, (int, float, str, type(None))) else str(v))
                    for k, v in (ec._sectors or {}).items()},
        "n_temps": len(rows)}
with open(out.replace(".csv", "_meta.json"), "w") as fh:
    json.dump(meta, fh, indent=2, default=str)
print("wrote", out)
