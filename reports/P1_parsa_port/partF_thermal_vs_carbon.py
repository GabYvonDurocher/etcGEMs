#!/usr/bin/env python3
"""P1 PART F -- does configuration D's overflow move the THERMAL descriptors, or only the
carbon ones?

Configuration D differs from the plain calibrated model by ONE constraint: a total-carbon
uptake cap, under which acetate overflow emerges rather than being imposed. If the thermal
envelope is unmoved by it, the thermal work and the overflow work compose cleanly and can be
written up side by side. If T_opt or CT_max move, they cannot.

A handful of solves, not a calibration: two media x {cap off, cap on} on one temperature grid.
Writes partF_thermal_vs_carbon.csv beside this file. Reports the numbers; adjudicates nothing.
"""
import copy
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
os.chdir(ROOT)

from etcgem.config import resolve, build_provider              # noqa: E402
from etcgem.dissect import tuned_pert_from_v3                  # noqa: E402
from etcgem.gasflux import flux_tpc, respiratory_quotient      # noqa: E402
from etcgem.tpc import TPC                                     # noqa: E402

MEDIA = ["glucose_minimal", "NLDM"]
# Cap settings: OFF, his nominal NLDM cap (230), and a cap that certainly BINDS on both media
# (60, the value his configuration-B figures use). Without the binding case a medium whose
# nominal cap is slack would look like evidence that the cap does nothing.
CAPS = [None, 230.0, 60.0]
TEMPS = np.linspace(5, 55, 101)      # wider than the configs' 5-50 so CT_max is not censored
METS = ("o2", "co2", "glc__D", "ac")
DESCRIPTORS = ["Topt_C", "rmax", "CTmax_C", "CTmin_C", "niche_width_C", "Ea_eV"]

pert, _ = tuned_pert_from_v3("strains/eciML1515/outputs/calibration_vanderlinden")
rows = []
for medium in MEDIA:
    for cap in CAPS:
        cap_on = cap is not None
        cfg = resolve("eciML1515", "gasflux_configD")
        cfg["gasflux"]["medium"] = medium
        cfg["gasflux"]["media"] = [medium]
        cfg["gasflux"]["total_carbon_cap"]["enabled"] = bool(cap_on)
        if cap_on:
            cfg["gasflux"]["total_carbon_cap"]["c_max"] = float(cap)
        pm = build_provider(cfg)
        try:
            pm.ec.model.solver.configuration.timeout = 20
        except Exception:
            pass
        df = flux_tpc(pm, TEMPS, pert, metabolites=METS)
        df["RQ"] = respiratory_quotient(df)
        d = TPC(TEMPS, df.growth.to_numpy(float)).descriptors(cfg.get("crit_frac", 0.05)).as_dict()
        i = int(np.nanargmax(df.growth.to_numpy()))
        rows.append({"medium": medium,
                     "configD_cap": "OFF" if not cap_on else f"c_max={cap:g}",
                     **{k: d[k] for k in DESCRIPTORS},
                     "o2_uptake_at_Topt": float(df.o2_uptake[i]),
                     "co2_release_at_Topt": float(df.co2_release[i]),
                     "acetate_release_at_Topt": float(df.ac_release[i]),
                     "RQ_at_Topt": float(df.RQ[i])})
        print(f"[partF] {medium:16s} cap {'OFF     ' if not cap_on else f'c_max={cap:<4g}'}  "
              f"Topt {d['Topt_C']:.1f}  rmax {d['rmax']:.4f}  CTmax {d['CTmax_C']:.2f}  "
              f"Ea {d['Ea_eV']:.3f}  RQ {float(df.RQ[i]):.3f}")

out = pd.DataFrame(rows)
out.to_csv(os.path.join(HERE, "partF_thermal_vs_carbon.csv"), index=False)
print()
with pd.option_context("display.width", 220, "display.max_columns", 20):
    print(out.to_string(index=False, float_format=lambda x: f"{x:.5g}"))
print("\nCHANGE ON SWITCHING THE CAP ON (thermal descriptors first, then carbon):")
for medium in MEDIA:
    a = out[(out.medium == medium) & (out.configD_cap == "OFF")].iloc[0]
    for cap in CAPS[1:]:
        b = out[(out.medium == medium) & (out.configD_cap == f"c_max={cap:g}")].iloc[0]
        binds = "" if abs(b.rmax - a.rmax) > 1e-9 or abs(b.RQ_at_Topt - a.RQ_at_Topt) > 1e-9 \
            else "   [cap is SLACK on this medium -- an uninformative null]"
        print(f"  {medium}, cap {cap:g}:{binds}")
        for k in DESCRIPTORS + ["o2_uptake_at_Topt", "co2_release_at_Topt",
                                "acetate_release_at_Topt", "RQ_at_Topt"]:
            rel = (abs(b[k] - a[k]) / abs(a[k])) if a[k] else float("nan")
            print(f"    {k:24s} {a[k]:12.5g} -> {b[k]:12.5g}   ({rel*100:7.3f} %)")
