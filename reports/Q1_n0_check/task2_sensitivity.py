#!/usr/bin/env python3
"""task2_sensitivity.py -- Q1 TASK 2: recompute every affected derived quantity under Parsa's
config.R conversion (21.21 um3 / 2120.58 fg C per cell) in place of the typed table constants
(2 um3 / 350 fg), and separate a change of SCALE from a change of TEMPERATURE DEPENDENCE.

    python3 reports/Q1_n0_check/task2_sensitivity.py

Nothing is written back to the respirometry tables. This recomputes into new columns for
comparison only; `strains/` is not touched.

WHY SCALE AND SHAPE MUST BE SEPARATED. The conversion constant is the same at every temperature,
so for any quantity that is LINEAR in it, only the scale moves and the temperature dependence is
bit-identical -- a change absorbed by a fitted scale parameter. CUE is NOT linear in it: it is
growthC / (growthC + respC), so multiplying growthC by ~6 changes the SHAPE of CUE against
temperature, not just its level. That distinction is the whole content of this task.

Writes task2_sensitivity.csv (per-quantity summary) and task2_cue.csv (CUE per medium/temperature
under both conversions).
"""
from __future__ import annotations

import json
import os

import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
RESP = os.path.join(ROOT, "strains", "eciML1515", "respirometry")
OTU = {"NLDM": 1, "LB": 2}     # gate_def.OTU for the R2A/LB set
OTU_M9 = {"M9": 1}

TABLE_VOL, TABLE_C = 2.0, 350.0            # typed in every row of both derived tables
CONFIG_VOL, CONFIG_C = 21.21, 2120.58      # printed by Parsa's config.R log
MW_C, MW_O2 = 12.011, 31.998


def recompute(d: pd.DataFrame, cell_c: float) -> pd.DataFrame:
    """The derived chain of TASK 0's D0, with cell_carbon_fg as the free constant.

    R_O2_mg_cell_min and growth_C_per_C_h are reproduced from their own inputs rather than read
    back, so that the claim 'these do not contain cell_carbon_fg' is demonstrated and not asserted.
    """
    o = pd.DataFrame(index=d.index)
    o["R_O2_mg_cell_min"] = d.C_tot_O2_mg_per_L / d.biomass_integral_cells_min_per_L
    o["growth_C_per_C_h"] = d.r * 60.0
    o["growth_fgC_h"] = d.r * 60.0 * cell_c
    o["respiration_fgC_h"] = o.R_O2_mg_cell_min * 60.0 * 1e12 * (MW_C / MW_O2)
    o["respiration_C_per_C_h"] = o.respiration_fgC_h / cell_c
    o["CUE"] = o.growth_fgC_h / (o.growth_fgC_h + o.respiration_fgC_h)
    o["resp_over_growth"] = o.respiration_C_per_C_h / o.growth_C_per_C_h
    return o


def slope(x, y):
    k = np.isfinite(x) & np.isfinite(y)
    if k.sum() < 3:
        return np.nan
    return float(stats.linregress(np.asarray(x)[k], np.asarray(y)[k]).slope)


def main():
    print(f"[q1t2] table constants   : {TABLE_VOL} um3, {TABLE_C} fg C  "
          f"-> implied density {TABLE_C/TABLE_VOL:.1f} fg C um^-3")
    print(f"[q1t2] config.R constants : {CONFIG_VOL} um3, {CONFIG_C} fg C  "
          f"-> implied density {CONFIG_C/CONFIG_VOL:.1f} fg C um^-3")
    print(f"[q1t2] the two differ in BOTH volume ({CONFIG_VOL/TABLE_VOL:.2f}x) and carbon density "
          f"({(CONFIG_C/CONFIG_VOL)/(TABLE_C/TABLE_VOL):.2f}x); carbon per cell ratio "
          f"{CONFIG_C/TABLE_C:.4f}x\n")

    rows, cue_rows = [], []
    for tag, f in (("R2A_LB", "derived_R2A_LB_current.csv"), ("M9", "derived_M9_current.csv")):
        d = pd.read_csv(os.path.join(RESP, f))
        d = d[(d.r > 0) & d.biomass_integral_cells_min_per_L.notna()].copy()
        a = recompute(d, TABLE_C)       # as published
        b = recompute(d, CONFIG_C)      # under config.R
        # the check on TASK 0's derivation: reproduced columns must match the table's own
        for c in ("R_O2_mg_cell_min", "growth_C_per_C_h", "growth_fgC_h",
                  "respiration_fgC_h", "respiration_C_per_C_h", "CUE", "resp_over_growth"):
            rel = np.abs(a[c] / d[c] - 1.0)
            assert np.nanmax(rel) < 1e-9, (tag, c, np.nanmax(rel))
        print(f"[q1t2] {tag}: all 7 derived columns reproduced from the table constants "
              f"(max rel dev {max(np.nanmax(np.abs(a[c]/d[c]-1)) for c in a.columns):.2e}) -- "
              f"TASK 0's chain is confirmed against the committed values")

        for c in a.columns:
            ratio = b[c] / a[c]
            # Temperature dependence, as d log(q) / dT per medium under each conversion. NOTE
            # `d["T"]`, not `d.T` -- the latter is pandas' transpose property, not the column.
            sl = {}
            for medium, otu in (OTU if tag == "R2A_LB" else OTU_M9).items():
                m = d.OTU == otu
                if not m.any():
                    continue
                ya, yb = a[c][m], b[c][m]
                sl[medium] = (slope(d["T"][m], np.log(ya.where(ya > 0))),
                              slope(d["T"][m], np.log(yb.where(yb > 0))))
            for medium, (sa, sb) in sl.items():
                rows.append(dict(
                    dataset=tag, medium=medium, quantity=c,
                    ratio_min=float(np.nanmin(ratio)), ratio_max=float(np.nanmax(ratio)),
                    constant_factor=bool(
                        np.nanmax(np.abs(ratio / np.nanmedian(ratio) - 1)) < 1e-9),
                    dlog_dT_table=sa, dlog_dT_config=sb,
                    dlog_dT_moved=bool(np.isfinite(sa) and np.isfinite(sb)
                                       and abs(sa - sb) > 1e-9 * max(1.0, abs(sa)))))
        if tag == "R2A_LB":
            for medium, otu in OTU.items():
                s = d[d.OTU == otu]
                ga, gb = recompute(s, TABLE_C), recompute(s, CONFIG_C)
                for T, ca, cb in zip(s["T"].values, ga.CUE.values, gb.CUE.values):
                    cue_rows.append(dict(medium=medium, T_C=float(T), CUE_table=float(ca),
                                         CUE_config=float(cb)))

    r = pd.DataFrame(rows)
    r.to_csv(os.path.join(HERE, "task2_sensitivity.csv"), index=False)
    print("\n[q1t2] SENSITIVITY -- factor by which each quantity moves, and whether the factor is "
          "constant\n")
    print(f"{'dataset':8s} {'medium':7s} {'quantity':24s} {'factor (min..max)':>22s} "
          f"{'const?':>7s} {'dlog/dT tbl':>12s} {'dlog/dT cfg':>12s} {'shape moved?':>13s}")
    for _, q in r.iterrows():
        fac = (f"{q.ratio_min:.4f}" if abs(q.ratio_min - q.ratio_max) < 1e-9
               else f"{q.ratio_min:.4f}..{q.ratio_max:.4f}")
        print(f"{q.dataset:8s} {q.medium:7s} {q.quantity:24s} {fac:>22s} "
              f"{'yes' if q.constant_factor else 'NO':>7s} "
              f"{q.dlog_dT_table:12.5f} {q.dlog_dT_config:12.5f} "
              f"{'YES' if q.dlog_dT_moved else 'no':>13s}")

    c = pd.DataFrame(cue_rows)
    cg = c.groupby(["medium", "T_C"]).mean().reset_index()
    cg.to_csv(os.path.join(HERE, "task2_cue.csv"), index=False)
    print("\n[q1t2] CUE under both conversions (R2A/LB, replicate means)\n")
    print(cg.round(4).to_string(index=False))
    print(f"\n[q1t2] CUE range: table {cg.CUE_table.min():.3f}-{cg.CUE_table.max():.3f}  "
          f"config.R {cg.CUE_config.min():.3f}-{cg.CUE_config.max():.3f}")
    print(f"[q1t2] CUE spread across temperature (max-min): table "
          f"{cg.CUE_table.max()-cg.CUE_table.min():.3f}  config.R "
          f"{cg.CUE_config.max()-cg.CUE_config.min():.3f}  -- CUE is NOT linear in the constant, "
          f"so its SHAPE moves, not only its level")

    json.dump(dict(table=dict(vol=TABLE_VOL, c=TABLE_C),
                   config_r=dict(vol=CONFIG_VOL, c=CONFIG_C),
                   carbon_ratio=CONFIG_C / TABLE_C,
                   density_table=TABLE_C / TABLE_VOL, density_config=CONFIG_C / CONFIG_VOL,
                   cue_table=[float(cg.CUE_table.min()), float(cg.CUE_table.max())],
                   cue_config=[float(cg.CUE_config.min()), float(cg.CUE_config.max())]),
              open(os.path.join(HERE, "task2_meta.json"), "w"), indent=2)
    print("\n[q1t2] wrote task2_sensitivity.csv, task2_cue.csv, task2_meta.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
