#!/usr/bin/env python3
"""task3b_membrane_retest.py -- K5 TASK 3b: re-test the ETC membrane-area constraint on a model
that can actually respire, under a carbon budget.

WHY K4's NULL RESULT DOES NOT SETTLE THE QUESTION. K4 swept A_ETC and found that no budget,
including zero, could put a relative below detection at 40 C. It ran on models with TWO escape
routes, and both are now known:

  * the proton leak K5 TASK 2 repairs -- the chain carried 0.04-0.05 % of the load, so
    constraining the area of complexes carrying no flux could not do anything; and
  * FERMENTATION with no carbon cap. Measured here: as A_ETC tightens from non-binding to zero,
    C. auris' carbon uptake TRIPLES, 12.0 -> 35.9 mmol C/gDW/h, while growth falls by two
    thirds. The cell buys its way out of the area budget with carbon. P4 found the same in
    E. coli on M9 and fixed it with a carbon cap.

THE CARBON CAP, and why this value. c_max = 12.0 mmol C/gDW/h: the carbon the CALIBRATION strain
(C. auris) actually consumes at 40 C with no area constraint. It is therefore the tightest cap
that does not itself reduce base growth, which is P4's criterion -- cap the escape, do not
impose a new limitation. One shared value across the four species, deliberately: a per-species
cap would encode a species difference that nothing measured supports. Swept 8 / 12 / 20 as a
sensitivity.

THE PARAMETER CAVEAT IS UNCHANGED AND IS NOT SOFTENED BY ANY OF THIS. Zero of twenty area and
turnover values in strains/*/etc/complexes.csv are measured in any Candida; all four species
carry identical tables. A constraint with undifferentiated parameters cannot EXPLAIN a species
difference however it now behaves. This script reports what the mechanism DOES.

Run from the project root:

    python3 reports/K5_respire/task3b_membrane_retest.py

Writes task3b_sweep.csv, task3b_counterfactual.csv and task3b_flatness.json beside this file.
"""
from __future__ import annotations

import json
import logging
import os
import sys

import numpy as np
import pandas as pd

logging.getLogger("cobra").setLevel(logging.ERROR)
sys.path.insert(0, "src")

from etcgem import etc_area as ea                                          # noqa: E402
from etcgem.config import build_provider, resolve, strain_dir              # noqa: E402
from etcgem.enzyme_cost import Perturbation                                # noqa: E402
from etcgem.gasflux import (add_total_carbon_constraint,                   # noqa: E402
                            remove_total_carbon_constraint)
from etcgem.sectors import plateau_width                                   # noqa: E402
from etcgem.tpc import TPC, apply_state                                    # noqa: E402
from etcgem.transfer import load_measured_tpc                              # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
EXPERIMENT = "candida_B5_respire"          # the REPAIRED model
CALIBRATE_ON = "cauris_iRV973"
PREDICT = ["chaemulonii_draft", "cduobushaemulonii_draft", "cparapsilosis_iDC1003"]
STRAINS = [CALIBRATE_ON] + PREDICT
DETECTION_FLOOR, FAIL_T, PERMISSIVE_T, PERM_FRAC = 0.05, 40.0, 34.0, 0.7
CRIT_FRAC = 0.05
GRID = dict(start_C=15.0, stop_C=75.0, n=121)
LEVELS = [np.inf, 2.0, 1.0, 0.7, 0.5, 0.35, 0.2, 0.1, 0.05, 0.0]
C_MAX = {"no carbon cap": None, "c_max 12": 12.0, "c_max 8": 8.0, "c_max 20": 20.0}


def build(s):
    pm = build_provider(resolve(s, EXPERIMENT))
    return pm, pm.ec.model


def growth(pm, temps):
    out = np.zeros(len(temps))
    for i, T in enumerate(temps):
        apply_state(pm.ec, float(T), Perturbation())
        g = pm.ec.model.slim_optimize()
        out[i] = 0.0 if (g is None or not np.isfinite(g) or g < 1e-6) else g
    return out


def main():
    temps = np.linspace(GRID["start_C"], GRID["stop_C"], int(GRID["n"]))
    pms, models, tables = {}, {}, {}
    for s in STRAINS:
        pms[s], models[s] = build(s)
        tables[s] = ea.load_etc_table("etc/complexes.csv", strain_dir(s))

    apply_state(pms[CALIBRATE_ON].ec, 30.0, Perturbation())
    models[CALIBRATE_ON].slim_optimize()
    a_star = ea.etc_area_value(models[CALIBRATE_ON], tables[CALIBRATE_ON])["total"]
    print(f"[k5] A* (repaired C. auris, unconstrained, 30 C) = {a_star:.6g} nm^2/gDW", flush=True)

    measured = load_measured_tpc(CALIBRATE_ON, resolve(CALIBRATE_ON, EXPERIMENT))
    meas_T = measured["T_C"].values.astype(float)
    meas_mu = measured["mu"].values.astype(float)

    rows, cf_rows, flat = [], [], {}
    for cap_label, c_max in C_MAX.items():
        for lvl in LEVELS:
            a_etc = np.inf if not np.isfinite(lvl) else a_star * lvl
            tag = "unconstrained" if not np.isfinite(lvl) else f"{lvl:g}xA*"
            for s in STRAINS:
                ea.remove_etc_area_constraint(pms[s])
                remove_total_carbon_constraint(pms[s])
                if np.isfinite(a_etc):
                    ea.add_etc_area_constraint(pms[s], tables[s], a_etc)
                if c_max is not None:
                    add_total_carbon_constraint(pms[s], c_max)
            g_cal = growth(pms[CALIBRATE_ON], meas_T)
            scale = float(meas_mu.max() / max(g_cal.max(), 1e-6))
            for s in STRAINS:
                g = growth(pms[s], temps)
                d = TPC(temps, g * scale).descriptors(CRIT_FRAC)
                lo1, hi1, w1 = plateau_width(temps, g, 0.01)
                _, _, w0 = plateau_width(temps, g, 1e-4)
                flat[f"{cap_label}::{tag}::{s}"] = dict(
                    carbon_cap=cap_label, A_ETC_level=tag, strain=s,
                    plateau_1pct_lo_C=lo1, plateau_1pct_hi_C=hi1,
                    plateau_1pct_width_C=w1, plateau_0p01pct_width_C=w0,
                    grid_span_C=float(temps.max() - temps.min()))
                apply_state(pms[s].ec, FAIL_T, Perturbation())
                mu40 = pms[s].ec.model.slim_optimize() or 0.0
                u = ea.etc_area_value(models[s], tables[s])
                i_peak = int(np.argmax(g))
                rows.append(dict(
                    carbon_cap=cap_label, c_max=c_max, A_ETC_level=tag,
                    A_ETC_over_Astar=(np.inf if not np.isfinite(lvl) else lvl),
                    A_ETC_nm2_per_gDW=(np.nan if not np.isfinite(a_etc) else a_etc),
                    strain=s, growth_scale=scale,
                    peak_mu_model=float(g.max()), peak_mu=float(g.max() * scale),
                    peak_T_C=float(temps[i_peak]), Topt_C=d.Topt_C, rmax=d.rmax,
                    CTmax_C=d.CTmax_C, Ea_eV=d.Ea_eV,
                    mu_40C_model=float(mu40), mu_40C=float(mu40 * scale),
                    area_used_40C=u["total"],
                    binds=bool(np.isfinite(a_etc) and u["total"] >= a_etc * 0.999),
                    plateau_1pct_width_C=w1))
            print(f"[k5] {cap_label:14s} {tag:14s} " + "  ".join(
                f"{s.split('_')[0][:9]}:{rows[-len(STRAINS)+i]['mu_40C']:.3f}"
                for i, s in enumerate(STRAINS)), flush=True)

    # ---- the counterfactual: what A_ETC ratio kills a relative at 40 C, with the cap on ----
    for cap_label, c_max in (("no carbon cap", None), ("c_max 12", 12.0)):
        for s in STRAINS:
            ea.remove_etc_area_constraint(pms[s])
            remove_total_carbon_constraint(pms[s])
            if c_max is not None:
                add_total_carbon_constraint(pms[s], c_max)
        g_cal = growth(pms[CALIBRATE_ON], meas_T)
        scale_free = float(meas_mu.max() / max(g_cal.max(), 1e-6))
        for s in PREDICT:
            def mu_at(T, a):
                ea.remove_etc_area_constraint(pms[s])
                if np.isfinite(a):
                    ea.add_etc_area_constraint(pms[s], tables[s], a)
                apply_state(pms[s].ec, float(T), Perturbation())
                v = pms[s].ec.model.slim_optimize()
                return (0.0 if v is None or not np.isfinite(v) else v) * scale_free

            base = mu_at(FAIL_T, np.inf)
            base_perm = mu_at(PERMISSIVE_T, np.inf)
            zero = mu_at(FAIL_T, 0.0)
            if base < DETECTION_FLOOR:
                req, note = a_star, "already below the floor unconstrained"
            elif zero >= DETECTION_FLOOR:
                req, note = None, ("cannot be pushed below the floor at 40 C by ANY A_ETC, "
                                   "including 0")
            else:
                lo, hi, note = 0.0, 10.0 * a_star, ""
                for _ in range(60):
                    mid = 0.5 * (lo + hi)
                    if mu_at(FAIL_T, mid) < DETECTION_FLOOR:
                        lo = mid
                    else:
                        hi = mid
                    if (hi - lo) / a_star < 1e-4:
                        break
                req = 0.5 * (lo + hi)
            perm = mu_at(PERMISSIVE_T, req) if req is not None else np.nan
            cf_rows.append(dict(
                carbon_cap=cap_label, strain=s, A_star=a_star,
                required_A_ETC=req,
                required_ratio_to_Astar=(None if req is None else req / a_star),
                required_fold_reduction=(None if req is None or req <= 0
                                         else a_star / req),
                mu40_unconstrained=base, mu40_at_zero_area=zero,
                detection_floor=DETECTION_FLOOR,
                permissive_mu=perm, permissive_baseline=base_perm,
                permissive_preserved=(None if req is None
                                      else bool(perm >= PERM_FRAC * base_perm)),
                note=note))
            print(f"[k5] counterfactual [{cap_label}] {s}: required A_ETC "
                  f"{'none' if req is None else f'{req:.4g}'} "
                  f"({'-' if req is None else f'{a_star/req:.2f}x smaller than A*' if req > 0 else 'zero'}); "
                  f"mu40 {base:.4f} -> {zero:.4f} at zero area, floor {DETECTION_FLOOR}. "
                  f"{note}", flush=True)
            ea.remove_etc_area_constraint(pms[s])

    pd.DataFrame(rows).to_csv(os.path.join(HERE, "task3b_sweep.csv"), index=False)
    pd.DataFrame(cf_rows).to_csv(os.path.join(HERE, "task3b_counterfactual.csv"), index=False)
    with open(os.path.join(HERE, "task3b_flatness.json"), "w") as fh:
        json.dump(flat, fh, indent=2)
    print("\n[k5] wrote task3b_sweep.csv, task3b_counterfactual.csv, task3b_flatness.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
