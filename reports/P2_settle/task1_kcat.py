#!/usr/bin/env python3
"""P2 TASK 1 -- settle the transporter turnover by experiment.

Parsa's `gasflux.py` sets TRANSPORT_KCAT = 30 s^-1; his configuration-A figure, its CSV
filename (`mmrt_transport_kcat300.csv`) and his report all say 300 s^-1. Rather than ask, run
configuration A at BOTH values and see which reproduces his committed output.

Reads his CSV read-only from $PARSA_ROOT (default the P1 location). Writes
task1_kcat_table.csv beside this file. Changes nothing.
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

PARSA = os.environ.get("PARSA_ROOT", "/Users/g.yvon-durocher/Downloads/etcGEMs-main_3")
REF = os.path.join(PARSA, "strains", "eciML1515", "outputs",
                   "posterior_mmrt_transport", "mmrt_transport_kcat300.csv")
KCATS = [30.0, 300.0]
# His configuration-A CSV is dated 2026-07-10, before he replaced the blanket NLDM medium with
# recipe ceilings (P1 DECISIONS D5), so NLDM is compared against NLDM_blanket.
MEDIA = {"glucose_minimal": "glucose_minimal", "NLDM": "NLDM_blanket", "LB": "LB", "BHI": "BHI"}
TEMPS = np.linspace(5, 50, 91)
METS = ("o2", "co2", "glc__D", "ac")
QUANTITIES = ["growth", "o2_uptake", "co2_release", "RQ"]

if not os.path.exists(REF):
    sys.exit(f"$PARSA_ROOT reference not found: {REF}")
his = pd.read_csv(REF)
pert, _ = tuned_pert_from_v3("strains/eciML1515/outputs/calibration_vanderlinden")

rows = []
for kcat in KCATS:
    for his_med, port_med in MEDIA.items():
        cfg = resolve("eciML1515", "gasflux_configA")
        cfg["gasflux"]["medium"] = port_med
        cfg["gasflux"]["media"] = [port_med]
        cfg["gasflux"]["transport_costs"]["kcat_s"] = kcat
        pm = build_provider(cfg)
        try:
            pm.ec.model.solver.configuration.timeout = 20
        except Exception:
            pass
        got = flux_tpc(pm, TEMPS, pert, metabolites=METS)
        got["RQ"] = respiratory_quotient(got)
        a = his[his.medium == his_med].sort_values("temp_C").reset_index(drop=True)
        b = got.sort_values("temp_C").reset_index(drop=True)
        ia, ib = int(np.nanargmax(a.growth.to_numpy())), int(np.nanargmax(b.growth.to_numpy()))
        # Curve agreement is measured as the largest ABSOLUTE growth difference scaled by
        # r_max. A plain relative difference is meaningless in the cold tail, where growth is
        # ~1e-3 and a 1e-4 absolute difference reads as 10%.
        d_abs = float(np.nanmax((b.growth - a.growth).abs()))
        row = {"kcat_s": kcat, "medium": his_med, "his_Topt": float(a.temp_C[ia]),
               "port_Topt": float(b.temp_C[ib]),
               "curve_max_abs_growth_diff": d_abs,
               "curve_max_abs_diff_over_rmax": d_abs / float(a.growth[ia])}
        for q in QUANTITIES:
            row[f"his_{q}"] = float(a[q][ia])
            row[f"port_{q}"] = float(b[q][ib])
        rows.append(row)
        print(f"[task1] kcat={kcat:5g}  {his_med:16s} "
              f"Topt his {a.temp_C[ia]:.1f} / port {b.temp_C[ib]:.1f}   "
              f"rmax his {a.growth[ia]:.5f} / port {b.growth[ib]:.5f}   "
              f"max |dgrowth|/rmax {d_abs / float(a.growth[ia]):.3e}")

out = pd.DataFrame(rows)
out.to_csv(os.path.join(HERE, "task1_kcat_table.csv"), index=False)
print()
# Verdict on the SAME criterion the P1 gate uses: T_opt exact, and every quantity at the
# optimum within 1e-3 relative -- plus the whole curve within 1e-3 of r_max.
for kcat in KCATS:
    d = out[out.kcat_s == kcat]
    topt_ok = bool((d.his_Topt == d.port_Topt).all())
    q_rel = max(float(np.nanmax(np.abs(d[f"port_{q}"].to_numpy() - d[f"his_{q}"].to_numpy())
                                / np.abs(d[f"his_{q}"].to_numpy()).clip(1e-12)))
                for q in QUANTITIES)
    curve = d.curve_max_abs_diff_over_rmax.max()
    ok = topt_ok and q_rel < 1e-3 and curve < 1e-3
    print(f"kcat = {kcat:g} s^-1: T_opt exact in all media = {topt_ok}; "
          f"worst optimum-quantity relative difference = {q_rel:.3e}; "
          f"worst curve |dgrowth|/rmax = {curve:.3e}  ->  "
          f"{'REPRODUCES his figure' if ok else 'does NOT reproduce it'}")
