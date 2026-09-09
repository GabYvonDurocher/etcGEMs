#!/usr/bin/env python3
"""P11 TASK 4 -- cost the remaining fits from THIS run's measured evaluations and wall clock.
Nothing is run. The per-evaluation cost differs by fit: the tie-break's parsimonious LP is the
expensive half and its cost scales with the model's size and the medium's openness, so the
per-evaluation times measured in P10's D3a table (none vs pfba, per fit) are used to scale
this run's measured rate. Writes task4_costs.csv beside this file."""
import json, os, sys
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
P10 = os.path.join(ROOT, "reports", "P10_respiration_likelihood")
OUT = os.path.join(ROOT, "strains", "eciML1515", "outputs", "calibration_configD_NLDM_recipe_P11_nested")
HELD = {"F_LB": "no tie-break at 1e-9 (P10 D1): its likelihood is still not a function of theta"}


def main(tag="main"):
    summ = json.load(open(os.path.join(OUT, f"summary_{tag}.json")))
    cost = pd.read_csv(os.path.join(P10, "task1_cost.csv"))
    pfba = cost[cost.tiebreak == "pfba"].set_index("fit").s_per_eval
    ref = float(pfba.loc["D_NLDM"])
    ncall, wall_h = int(summ["ncall"]), float(summ["wall_h"])
    per_call_h = wall_h / ncall
    rows = []
    for fit in ["D_NLDM", "D_LB", "D_M9", "E_NLDM", "E_LB", "E_M9", "F_NLDM", "F_M9", "F_LB"]:
        if fit in pfba.index:
            scale = float(pfba.loc[fit]) / ref; basis = f"P10 measured {pfba.loc[fit]:.2f} s/eval vs D_NLDM's {ref:.2f}"
        else:                                   # the M9 fits were not in P10's table
            scale = 1.0; basis = "assumed equal to its NLDM sibling (no P10 measurement)"
        h = ncall * per_call_h * scale
        rows.append(dict(fit=fit, held=fit in HELD, note=HELD.get(fit, ""), rel_cost_per_eval=round(scale, 2),
                         basis=basis, projected_evaluations=ncall,
                         projected_hours=(np.nan if fit in HELD else round(h, 1)),
                         status=("HELD" if fit in HELD else ("MEASURED (this run)" if fit == "D_NLDM" else "projected"))))
    df = pd.DataFrame(rows); df.to_csv(os.path.join(HERE, "task4_costs.csv"), index=False)
    tot = df[~df.held & (df.fit != "D_NLDM")].projected_hours.sum()
    print(df[["fit", "status", "rel_cost_per_eval", "projected_hours", "note"]].to_string(index=False), flush=True)
    print(f"\n[cost] this run: {ncall} evaluations in {wall_h:.2f} h ({per_call_h*3600:.3f} s per evaluation of wall clock across 16 processes)", flush=True)
    print(f"[cost] the eight not run: {tot:.1f} h in total if each needs the same number of evaluations; F_LB is HELD and not costed", flush=True)
    print("[cost] done", flush=True)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "main")
