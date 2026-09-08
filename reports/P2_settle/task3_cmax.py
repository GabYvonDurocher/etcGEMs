#!/usr/bin/env python3
"""P2 TASK 3 -- the c_max sensitivity, done properly.

At which total-carbon cap do the THERMAL descriptors start to move, and does c_max = 60 sit in
a flat region or on a slope? Sweeps the cap from off to strongly binding on two media and
tabulates the thermal descriptors beside the carbon read-out.

Gathers and reports. It does NOT change c_max and does NOT conclude whether the cap is fitted.
Writes task3_cmax_table.csv beside this file.
"""
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
os.chdir(ROOT)

from etcgem.config import resolve, build_provider           # noqa: E402
from etcgem.dissect import tuned_pert_from_v3               # noqa: E402
from etcgem.gasflux import flux_tpc, respiratory_quotient   # noqa: E402
from etcgem.tpc import TPC                                  # noqa: E402

MEDIA = ["glucose_minimal", "NLDM"]          # NLDM = the canonical recipe medium (P2 TASK 2)
CAPS = [None, 230.0, 180.0, 150.0, 120.0, 100.0, 80.0, 60.0, 50.0, 40.0]
TEMPS = np.linspace(5, 52, 95)
METS = ("o2", "co2", "glc__D", "ac")
THERMAL = ["Topt_C", "CTmax_C", "CTmin_C", "niche_width_C", "Ea_eV", "rmax"]

pert, _ = tuned_pert_from_v3("strains/eciML1515/outputs/calibration_vanderlinden")
rows = []
for medium in MEDIA:
    for cap in CAPS:
        cfg = resolve("eciML1515", "gasflux_configD")
        cfg["gasflux"]["medium"] = medium
        cfg["gasflux"]["media"] = [medium]
        cfg["gasflux"]["total_carbon_cap"]["enabled"] = cap is not None
        if cap is not None:
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
        rows.append({"medium": medium, "c_max": np.inf if cap is None else float(cap),
                     **{k: d[k] for k in THERMAL},
                     "o2_at_Topt": float(df.o2_uptake[i]),
                     "co2_at_Topt": float(df.co2_release[i]),
                     "acetate_at_Topt": float(df.ac_release[i]),
                     "RQ_at_Topt": float(df.RQ[i])})
        print(f"[task3] {medium:16s} c_max {'off  ' if cap is None else f'{cap:<5g}'}  "
              f"Topt {d['Topt_C']:5.1f}  rmax {d['rmax']:7.4f}  CTmax {d['CTmax_C']:6.2f}  "
              f"Ea {d['Ea_eV']:6.3f}  acetate {float(df.ac_release[i]):7.3f}  "
              f"RQ {float(df.RQ[i]):6.3f}")

out = pd.DataFrame(rows)
out.to_csv(os.path.join(HERE, "task3_cmax_table.csv"), index=False)
print()
with pd.option_context("display.width", 240, "display.max_columns", 24):
    print(out.to_string(index=False, float_format=lambda x: f"{x:.5g}"))

print("\n--- where do the thermal descriptors start to move? (against the uncapped run) ---")
for medium in MEDIA:
    ref = out[(out.medium == medium) & (~np.isfinite(out.c_max))].iloc[0]
    print(f"  {medium}")
    for _, r in out[(out.medium == medium) & np.isfinite(out.c_max)].iterrows():
        parts = []
        for k in ["Topt_C", "CTmax_C", "Ea_eV", "rmax"]:
            rel = abs(r[k] - ref[k]) / abs(ref[k]) if ref[k] else float("nan")
            parts.append(f"{k} {rel*100:6.2f}%")
        print(f"    c_max {r.c_max:6.0f}:  " + "  ".join(parts))
