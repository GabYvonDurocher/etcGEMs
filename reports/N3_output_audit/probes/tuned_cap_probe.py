"""N3 TASK 2: does the translation cap bind at T_opt at the DECOMPOSITION's operating point?

Rebuilds the tuned rich-BHI point exactly as calibration_multi._build_pm_rich does, applies
the tuned medians recorded in the committed decompose_summary.json, and sweeps the
decomposition's own temperature grid (recast_temps_C.npy). One TPC's worth of solves; no
posterior draws, no grids, no dissection.
"""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.join(os.getcwd(), "src"))
from etcgem.calibration_multi import _build_pm_rich
from etcgem.dissect import LEVERS, LEVER_ATTR
from etcgem.enzyme_cost import Perturbation

D = "strains/eciML1515/outputs/decompose_tuned"
summ = json.load(open(f"{D}/decompose_summary.json"))
med = summ["tuned_medians"]
pert = Perturbation(**{LEVER_ATTR[lv]: float(med[lv]) for lv in LEVERS if lv in med})
temps = np.load(f"{D}/recast_temps_C.npy")
base = np.load(f"{D}/recast_base_curve.npy")

pm = _build_pm_rich("eciML1515")
ec = pm.ec
CAP, POOL = "proteome_biosynthesis", getattr(ec, "POOL", "enzyme_pool")
rows = []
for Tc in temps:
    ec.set_temperature(float(Tc) + 273.15, pert)
    if pert.uses_allocation():
        # kappa_scale / sigma_sat MUST be passed: sigma_sat rescales both sector caps by
        # sigma_sat/sigma_nom (0.8669/0.45 = 1.93 at the tuned point). Omitting them is
        # what made an earlier version of this probe report rmax 1.114 instead of 2.161.
        ec.set_allocation(pert.f_metab, pert.f_maint,
                          kappa_scale=pert.kappa_scale, sigma_sat=pert.sigma_sat)
    else:
        ec.set_budget(pert.budget if pert.budget is not None else ec.default_budget,
                      pert.group_alloc)
    g = ec.model.slim_optimize()
    g = 0.0 if (g is None or not np.isfinite(g) or g < 1e-6) else float(g)
    r = {"temp_C": float(Tc), "growth": g}
    for key, cname in (("cap", CAP), ("pool", POOL)):
        c = ec.model.constraints.get(cname)
        if c is None:
            r[f"{key}_lhs"] = r[f"{key}_ub"] = float("nan"); continue
        try: r[f"{key}_lhs"] = float(c.primal)
        except Exception: r[f"{key}_lhs"] = float("nan")
        r[f"{key}_ub"] = float(c.ub) if c.ub is not None else float("nan")
    rows.append(r)

import csv
out = sys.argv[1]
with open(out, "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
g = np.array([r["growth"] for r in rows])
print(f"alloc_from_data at the tuned point: {ec._alloc_from_data!r}")
print(f"reproduces recast_base_curve.npy: max|d|={np.max(np.abs(g-base)):.3e} "
      f"max rel={np.nanmax(np.abs(g-base)/np.where(base!=0,np.abs(base),np.nan)):.3e}")
i = int(np.argmax(g)); j = int(np.argmax(base))
print(f"probe  Topt={temps[i]:.1f} rmax={g[i]:.6f}")
print(f"commit Topt={temps[j]:.1f} rmax={base[j]:.6f}")
for k in (i,):
    r = rows[k]
    print(f"at Topt: cap lhs={r['cap_lhs']:.6g} ub={r['cap_ub']:.6g} slack={r['cap_ub']-r['cap_lhs']:.3g}"
          f" | pool lhs={r['pool_lhs']:.6g} ub={r['pool_ub']:.6g} slack={r['pool_ub']-r['pool_lhs']:.3g}")
capb = np.array([abs(r["cap_ub"]-r["cap_lhs"])/max(abs(r["cap_ub"]),1e-30) < 1e-6 for r in rows])
poolb = np.array([abs(r["pool_ub"]-r["pool_lhs"])/max(abs(r["pool_ub"]),1e-30) < 1e-6 for r in rows])
live = g > 0
print(f"cap binds at {int((capb&live).sum())}/{int(live.sum())} live temperatures"
      + (f", {temps[capb&live].min():.0f}-{temps[capb&live].max():.0f} C" if (capb&live).any() else ""))
print(f"pool binds at {int((poolb&live).sum())}/{int(live.sum())} live temperatures"
      + (f", {temps[poolb&live].min():.0f}-{temps[poolb&live].max():.0f} C" if (poolb&live).any() else ""))
