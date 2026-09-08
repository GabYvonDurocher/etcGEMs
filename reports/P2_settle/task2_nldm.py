#!/usr/bin/env python3
"""P2 TASK 2 -- NLDM under recipe ceilings, with the blanket medium as a labelled sensitivity.

P1 established that Parsa's committed NLDM numbers were produced with a BLANKET medium (every
component open at one generous bound) while his later code applies recipe-proportional uptake
ceilings, and that he never re-ran. This takes the recipe as canonical -- it is the more careful
construction and it post-dates his CSV -- and reports every number that moves.

Reads the committed gasflux runs (which already carry both media) and, read-only, his CSVs from
$PARSA_ROOT for the reproduction check. Writes task2_nldm_table.csv. Changes nothing.
"""
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
os.chdir(ROOT)
PARSA = os.environ.get("PARSA_ROOT", "/Users/g.yvon-durocher/Downloads/etcGEMs-main_3")
HIS = {"gasflux_configA": "posterior_mmrt_transport/mmrt_transport_kcat300.csv",
       "gasflux_configB": "posterior_carboncap/gasflux_C60.csv",
       "gasflux_configC": "posterior_configC/configC_acetate.csv"}
QUANTITIES = ["temp_C", "growth", "o2_uptake", "co2_release", "ac_release", "glc__D_uptake", "RQ"]


def optimum(df, medium):
    a = df[df.medium == medium].sort_values("temp_C").reset_index(drop=True)
    if a.empty or a.growth.max() <= 0:
        return None
    return a.iloc[int(np.nanargmax(a.growth.to_numpy()))]


rows = []
for exp, hisrel in HIS.items():
    got = pd.read_csv(os.path.join("strains", "eciML1515", "outputs", exp, "gasflux.csv"))
    rec, bla = optimum(got, "NLDM"), optimum(got, "NLDM_blanket")
    hispath = os.path.join(PARSA, "strains", "eciML1515", "outputs", hisrel)
    his = None
    if os.path.exists(hispath):
        h = pd.read_csv(hispath)
        his = optimum(h, "NLDM")
    for q in QUANTITIES:
        b = float(bla[q]); r = float(rec[q])
        row = {"config": exp.replace("gasflux_", ""), "quantity": q,
               "blanket (his medium)": b, "recipe (canonical)": r,
               "abs_change": r - b,
               "rel_change": (abs(r - b) / abs(b)) if b else float("nan")}
        if his is not None:
            hv = float(his[q])
            row["parsa"] = hv
            row["blanket_vs_parsa_rel"] = (abs(b - hv) / abs(hv)) if hv else float("nan")
            row["recipe_vs_parsa_rel"] = (abs(r - hv) / abs(hv)) if hv else float("nan")
        rows.append(row)

out = pd.DataFrame(rows)
out.to_csv(os.path.join(HERE, "task2_nldm_table.csv"), index=False)
with pd.option_context("display.width", 220, "display.max_columns", 20):
    print(out.to_string(index=False, float_format=lambda x: f"{x:.6g}"))

print("\n--- is the 1.2% fully explained by the medium? ---")
for exp in HIS:
    d = out[out.config == exp.replace("gasflux_", "")]
    if "blanket_vs_parsa_rel" not in d:
        continue
    g = d[d.quantity == "growth"].iloc[0]
    print(f"  {exp.replace('gasflux_',''):8s} r_max at the NLDM optimum: "
          f"his {g['parsa']:.6f} | blanket {g['blanket (his medium)']:.6f} "
          f"(rel {g['blanket_vs_parsa_rel']:.3e}) | recipe {g['recipe (canonical)']:.6f} "
          f"(rel {g['recipe_vs_parsa_rel']:.3e})")
