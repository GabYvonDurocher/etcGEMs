#!/usr/bin/env python3
"""P1 PART E -- the gate: does the port reproduce Parsa's numbers?

Compares, per configuration and per medium, the quantities his committed CSVs and reports
carry against what this repository's core produces. His values are transcribed in
`parsa_expected.json` so the gate runs without `$PARSA_ROOT` present -- the K1 precedent.

Run AFTER the three configurations, from the project root:

    etcgem gasflux --strain eciML1515 --experiment gasflux_configA
    etcgem gasflux --strain eciML1515 --experiment gasflux_configB
    etcgem gasflux --strain eciML1515 --experiment gasflux_configC
    python reports/P1_parsa_port/gate.py

Writes gate_table.csv beside this file and prints the table. Decides nothing: where a value
moves, the attribution column says WHY, and an unattributed movement is a FAIL.
"""
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(ROOT, "strains", "eciML1515", "outputs")
EXPECTED = json.load(open(os.path.join(HERE, "parsa_expected.json")))

# His NLDM references all predate his own switch to recipe-proportional uptake ceilings
# (P1 DECISIONS D5), so the medium to compare his NLDM numbers against is NLDM_blanket.
MEDIUM_FOR = {"glucose_minimal": "glucose_minimal", "NLDM": "NLDM_blanket",
              "LB": "LB", "BHI": "BHI"}
ATTR_BLANKET = ("his NLDM predates his recipe medium: CSV 2026-09-01, his set_medium_nldm "
                "2026-09-04 (D5)")
QUANTITIES = [("temp_C", "T_opt (C)", 0.0, "abs"),
              ("growth", "r_max (1/h)", 1e-3, "rel"),
              ("o2_uptake", "O2 uptake @T_opt", 1e-3, "rel"),
              ("co2_release", "CO2 release @T_opt", 1e-3, "rel"),
              ("RQ", "RQ @T_opt", 1e-3, "rel")]
CONFIGS = [("configA_kcat300", "gasflux_configA", "A -- MMRT-costed transport"),
           # C_max = 60 is now the labelled SENSITIVITY overlay, not the baseline (P3 TASK 4
           # adopted 120 on Parsa's own sweep). The gate compares his figure, so it reads the
           # run that reproduces his figure.
           ("configB_C60", "gasflux_configB_cmax60", "B -- total-carbon cap (C_max 60)"),
           ("configC_acetate", "gasflux_configC", "C -- Basan acetate line")]


def optimum(df, medium):
    a = df[df.medium == medium].sort_values("temp_C").reset_index(drop=True)
    if a.empty or not np.isfinite(a.growth.to_numpy()).any() or a.growth.max() <= 0:
        return None
    return a.iloc[int(np.nanargmax(a.growth.to_numpy()))]


def main():
    rows = []
    for key, exp, label in CONFIGS:
        path = os.path.join(OUT, exp, "gasflux.csv")
        if not os.path.exists(path):
            print(f"MISSING run: {path} -- run `etcgem gasflux --experiment {exp}` first")
            continue
        got = pd.read_csv(path)
        for his_med, port_med in MEDIUM_FOR.items():
            ref = EXPECTED[key].get(his_med)
            if ref is None:
                continue
            r = optimum(got, port_med)
            attribution = ATTR_BLANKET if port_med != his_med else ""
            for col, qlabel, tol, kind in QUANTITIES:
                if col not in ref or ref[col] is None:
                    continue
                a = float(ref[col])
                b = float("nan") if r is None else float(r[col])
                if kind == "abs":
                    d = abs(b - a)
                    ok = d <= tol + 1e-12
                    shown = f"{d:.3g}"
                else:
                    d = abs(b - a) / abs(a) if a else float("nan")
                    ok = np.isfinite(d) and d <= tol
                    shown = f"{d:.3g}"
                rows.append({"config": label, "medium": his_med, "quantity": qlabel,
                             "parsa": a, "port": b, "difference": shown,
                             "tolerance": (f"{tol} {kind}"),
                             "verdict": "PASS" if ok else "FAIL",
                             "attribution": attribution})
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(HERE, "gate_table.csv"), index=False)
    with pd.option_context("display.width", 200, "display.max_columns", 20):
        print(df.to_string(index=False, float_format=lambda x: f"{x:.6g}"))
    n, p = len(df), int((df.verdict == "PASS").sum())
    print(f"\n{n} comparisons, {p} PASS, {n - p} FAIL")
    return 0 if n == p else 1


if __name__ == "__main__":
    sys.exit(main())
