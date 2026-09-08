#!/usr/bin/env python3
"""task3_sweep.py -- K4 TASK 3: apply the ETC membrane-area constraint to the four Candida
strains and sweep A_ETC from non-binding to strongly binding.

CONFIGURATION. The K2 configuration (`candida_B3_ngamT`): the core's `unfolding` thermal form,
the grounded proteome budget, and the corrected temperature-dependent maintenance. Nothing is
fitted. The transfer convention is followed exactly -- one growth scale, computed on the
CALIBRATION strain (C. auris) at each A_ETC level, frozen, and applied to all four -- so these
numbers sit beside K2's ladder rather than on a different footing.

THE SWEEP AXIS. A_ETC is the single free knob (see the table headers in strains/*/etc/). Its
absolute value cannot be sourced for these species, so the sweep is expressed as a multiple of
a REFERENCE area A*, defined once as the area C. auris' unconstrained solution uses at 30 degC.
The absolute nm^2/gDW is reported in every row so that a reader who later has a measured fungal
value can locate it on the axis.

THE SAME A_ETC IS APPLIED TO ALL FOUR SPECIES. That is deliberate and is the point: an
undifferentiated parameter cannot explain a difference between species, and this run measures
what it does instead of assuming.

THE COUNTERFACTUAL, the analogue of K2's 13.8 degC. For each predicted strain: by what factor
must ITS A_ETC be reduced, relative to the value C. auris carries, before the model puts it
below the 0.05 h^-1 detection floor at 40 degC while still growing at the permissive
temperature? Reported as a ratio, which is the form a membrane-area difference is measurable in.

FLATNESS. The core's guard (src/etcgem/sectors.record_flatness) only fires when proteome
sectors are enabled without temperature-dependent allocation, which is not this configuration,
so it writes nothing here. The same quantity is therefore computed directly with the same
function (sectors.plateau_width) and written to task3_flatness.json, so a constraint that
flattens the curve is visible rather than inferred.

Run from the project root:

    python3 reports/K4_membrane/task3_sweep.py            # the full sweep
    python3 reports/K4_membrane/task3_sweep.py --quick    # 3 A_ETC levels, coarse grid

Writes task3_sweep.csv, task3_binding.csv, task3_counterfactual.csv and task3_flatness.json
beside this file.
"""
from __future__ import annotations

import argparse
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
from etcgem.sectors import plateau_width                                   # noqa: E402
from etcgem.tpc import TPC, apply_state                                    # noqa: E402
from etcgem.transfer import load_measured_tpc                              # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
EXPERIMENT = "candida_B3_ngamT"
CALIBRATE_ON = "cauris_iRV973"
PREDICT = ["chaemulonii_draft", "cduobushaemulonii_draft", "cparapsilosis_iDC1003"]
STRAINS = [CALIBRATE_ON] + PREDICT

DETECTION_FLOOR = 0.05      # h^-1, the project's floor
FAIL_T, PERMISSIVE_T = 40.0, 34.0
PERMISSIVE_FRAC = 0.7
CRIT_FRAC = 0.05
GRID = dict(start_C=15.0, stop_C=75.0, n=121)       # the K2 descriptor grid
GRID_QUICK = dict(start_C=20.0, stop_C=60.0, n=41)

# A_ETC levels, as multiples of the reference area A*
LEVELS = [np.inf, 3.0, 2.0, 1.0, 0.7, 0.5, 0.35, 0.2, 0.1, 0.05, 0.0]
LEVELS_QUICK = [np.inf, 0.5, 0.1, 0.0]

# Two tables are swept. "full" is the E. coli convention -- ATP synthase is a member of the
# area budget, as it is in strains/eciML1515/etc/complexes.csv. "chain_only" drops it, leaving
# complexes I-IV. The pair separates what the budget does to RESPIRATION from what it does to
# ATP SYNTHESIS, which TASK 1 showed are different things in three of these four models.
VARIANTS = ("full", "chain_only")


def table_for(strain, variant="full"):
    df = ea.load_etc_table("etc/complexes.csv", strain_dir(strain))
    if variant == "chain_only":
        df = df[~df["complex"].str.contains("ATP synthase", case=False)].reset_index(drop=True)
    return df


def build(strain):
    pm = build_provider(resolve(strain, EXPERIMENT))
    return pm, pm.ec.model


def growth(pm, temps, a_etc=None, df=None):
    """TPC at this A_ETC. The constraint is (re)applied before every solve, because
    set_temperature rebuilds the enzyme layer; verified to survive, and re-checked here."""
    out = np.zeros(len(temps))
    for i, T in enumerate(temps):
        apply_state(pm.ec, float(T), Perturbation())
        g = pm.ec.model.slim_optimize()
        out[i] = 0.0 if (g is None or not np.isfinite(g) or g < 1e-6) else g
    return out


def area_used(model, df):
    return ea.etc_area_value(model, df)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    args = ap.parse_args()
    grid = GRID_QUICK if args.quick else GRID
    levels = LEVELS_QUICK if args.quick else LEVELS
    temps = np.linspace(grid["start_C"], grid["stop_C"], int(grid["n"]))

    pms, models, tables = {}, {}, {}
    for s in STRAINS:
        pms[s], models[s] = build(s)
        tables[s] = {v: table_for(s, v) for v in VARIANTS}
        print(f"[k4] {s}: table {len(tables[s]['full'])} complexes, reactions present "
              f"{ {k: len(v) for k, v in ea.present_reactions(models[s], tables[s]['full']).items()} }",
              flush=True)

    # the reference area A*: C. auris, unconstrained, 30 C
    apply_state(pms[CALIBRATE_ON].ec, 30.0, Perturbation())
    models[CALIBRATE_ON].slim_optimize()
    a_star = area_used(models[CALIBRATE_ON], tables[CALIBRATE_ON]["full"])["total"]
    print(f"[k4] reference A* (C. auris, unconstrained, 30 C) = {a_star:.6g} nm^2/gDW", flush=True)

    measured = load_measured_tpc(CALIBRATE_ON, resolve(CALIBRATE_ON, EXPERIMENT))
    meas_T = measured["T_C"].values.astype(float)
    meas_mu = measured["mu"].values.astype(float)

    rows, bind_rows, cf_rows, flat = [], [], [], {}
    for variant in VARIANTS:
     for lvl in levels:
        a_etc = np.inf if not np.isfinite(lvl) else a_star * lvl
        tag = "unconstrained" if not np.isfinite(lvl) else f"{lvl:g}xA*"
        vtag = f"{variant}:{tag}"
        # apply to every strain
        for s in STRAINS:
            ea.remove_etc_area_constraint(pms[s])
            if np.isfinite(a_etc):
                ea.add_etc_area_constraint(pms[s], tables[s][variant], a_etc)
        # the frozen growth scale, from the calibration strain, as `transfer` does it
        g_cal_meas = growth(pms[CALIBRATE_ON], meas_T)
        scale = float(meas_mu.max() / max(g_cal_meas.max(), 1e-6))

        for s in STRAINS:
            g = growth(pms[s], temps)
            d = TPC(temps, g * scale).descriptors(CRIT_FRAC)
            lo1, hi1, w1 = plateau_width(temps, g, 0.01)
            _, _, w0 = plateau_width(temps, g, 1e-4)
            flat[f"{vtag}::{s}"] = dict(
                variant=variant, A_ETC_level=tag, A_ETC_nm2_per_gDW=(None if not np.isfinite(a_etc) else a_etc),
                plateau_1pct_lo_C=lo1, plateau_1pct_hi_C=hi1, plateau_1pct_width_C=w1,
                plateau_0p01pct_width_C=w0, grid_span_C=float(temps.max() - temps.min()),
                note="computed with sectors.plateau_width; the core's own guard does not fire "
                     "in this configuration because proteome sectors are off (K2 rung B3).")
            # growth at 40 C, and whether the constraint binds at each temperature
            mu40 = float(np.interp(FAIL_T, temps, g) * scale)
            for T in (22.0, 26.0, 30.0, 34.0, 38.0, 40.0, 44.0):
                apply_state(pms[s].ec, T, Perturbation())
                mu = pms[s].ec.model.slim_optimize()
                u = area_used(models[s], tables[s][variant])
                bind_rows.append(dict(
                    variant=variant, A_ETC_level=tag, A_ETC_nm2_per_gDW=(np.nan if not np.isfinite(a_etc) else a_etc),
                    strain=s, T_C=T, mu_model=float(mu or 0.0), mu_scaled=float((mu or 0.0) * scale),
                    area_used=u["total"],
                    binds=bool(np.isfinite(a_etc) and u["total"] >= a_etc - abs(a_etc) * 1e-3
                               - (1e-6 if a_etc == 0 else 0.0)),
                    frac_of_budget=(u["total"] / a_etc if (np.isfinite(a_etc) and a_etc > 0) else np.nan),
                    **{f"area::{k}": v for k, v in u.items() if k != "total"}))
            # thermal limit, bisected above the peak, as transfer.thermal_limit does
            i_peak = int(np.argmax(g))
            lo, hi = float(temps[i_peak]), 90.0

            def mu_at(T):
                apply_state(pms[s].ec, float(T), Perturbation())
                v = pms[s].ec.model.slim_optimize()
                return (0.0 if v is None or not np.isfinite(v) else v) * scale

            if mu_at(lo) < DETECTION_FLOOR:
                limit = float("nan")
            elif mu_at(hi) >= DETECTION_FLOOR:
                limit = float("inf")
            else:
                a, b = lo, hi
                while b - a > 0.02:
                    mid = 0.5 * (a + b)
                    if mu_at(mid) >= DETECTION_FLOOR:
                        a = mid
                    else:
                        b = mid
                limit = 0.5 * (a + b)
            # fit R2 against this strain's own measured curve
            try:
                mm = load_measured_tpc(s, resolve(s, EXPERIMENT))
                pred = np.interp(mm["T_C"].values.astype(float), temps, g) * scale
                obs = mm["mu"].values.astype(float)
                ss_res = float(np.sum((obs - pred) ** 2))
                ss_tot = float(np.sum((obs - obs.mean()) ** 2))
                r2 = float("nan") if ss_tot <= 0 else 1.0 - ss_res / ss_tot
            except Exception:
                r2 = float("nan")
            rows.append(dict(
                variant=variant, A_ETC_level=tag, A_ETC_over_Astar=(np.inf if not np.isfinite(lvl) else lvl),
                A_ETC_nm2_per_gDW=(np.nan if not np.isfinite(a_etc) else a_etc),
                strain=s, role=("calibrate_on" if s == CALIBRATE_ON else "predict"),
                growth_scale=scale, peak_mu_model=float(g.max()), peak_mu=float(g.max() * scale),
                peak_T_C=float(temps[i_peak]), Topt_C=d.Topt_C, rmax=d.rmax,
                CTmax_C=d.CTmax_C, CTmin_C=d.CTmin_C, Ea_eV=d.Ea_eV,
                thermal_limit_C=limit, mu_40C=mu40, fit_r2=r2,
                plateau_1pct_width_C=w1, plateau_0p01pct_width_C=w0))
            print(f"[k4] {vtag:26s} {s:24s} peak {g.max()*scale:.4f}/h at {temps[i_peak]:.1f}C  "
                  f"Topt {d.Topt_C:.1f}  CTmax {d.CTmax_C:.2f}  limit {limit:.2f}  "
                  f"mu(40C) {mu40:.4f}  R2 {r2:.3f}  plateau1% {w1:.1f}C", flush=True)

    # ---- the counterfactual: what A_ETC ratio would push a relative below detection at 40 C
    for s in STRAINS:
        ea.remove_etc_area_constraint(pms[s])
    g_cal = growth(pms[CALIBRATE_ON], meas_T)
    scale_free = float(meas_mu.max() / max(g_cal.max(), 1e-6))
    for variant in VARIANTS:
     for s in PREDICT:
        def mu_at_T(T, a):
            ea.remove_etc_area_constraint(pms[s])
            if np.isfinite(a):
                ea.add_etc_area_constraint(pms[s], tables[s][variant], a)
            apply_state(pms[s].ec, float(T), Perturbation())
            v = pms[s].ec.model.slim_optimize()
            return (0.0 if v is None or not np.isfinite(v) else v) * scale_free

        base_fail = mu_at_T(FAIL_T, np.inf)
        base_perm = mu_at_T(PERMISSIVE_T, np.inf)
        # THE LIMITING CASE. A_ETC = 0 is NOT a clean "chain off": etc_area_expr sums SIGNED
        # flux (flux_expression = forward - reverse), so a REVERSIBLE complex can contribute
        # NEGATIVE area and offset another complex's usage. Succinate dehydrogenase is
        # reversible in these models and does exactly that, so at A_ETC = 0 the budget is met
        # by running SDH backwards while ATP synthase still turns over. The unambiguous
        # limiting case is therefore reaction DELETION, which is what is reported.
        zero_fail = mu_at_T(FAIL_T, 0.0)
        ea.remove_etc_area_constraint(pms[s])
        keep = {}
        for rid in [r for r in tables[s][variant]["reactions"].sum() if r in models[s].reactions]:
            rr = models[s].reactions.get_by_id(rid)
            keep[rid] = rr.bounds
            rr.bounds = (0.0, 0.0)
        models[s].solver.update()
        apply_state(pms[s].ec, FAIL_T, Perturbation())
        v = pms[s].ec.model.slim_optimize()
        deleted_fail = (0.0 if v is None or not np.isfinite(v) else v) * scale_free
        for rid, b in keep.items():
            models[s].reactions.get_by_id(rid).bounds = b
        models[s].solver.update()
        if base_fail < DETECTION_FLOOR:
            req, note = 1.0, "already below the floor with no area constraint"
        else:
            lo, hi = 0.0, 10.0 * a_star
            if mu_at_T(FAIL_T, lo) >= DETECTION_FLOOR:
                req, note = None, ("cannot be pushed below the floor at 40 C by ANY A_ETC, "
                                   "INCLUDING A_ETC = 0")
            else:
                note = ""
                for _ in range(60):
                    mid = 0.5 * (lo + hi)
                    if mu_at_T(FAIL_T, mid) < DETECTION_FLOOR:
                        lo = mid
                    else:
                        hi = mid
                    if (hi - lo) / a_star < 1e-4:
                        break
                req = 0.5 * (lo + hi)
        perm = mu_at_T(PERMISSIVE_T, req) if req not in (None, 1.0) else base_perm
        cf_rows.append(dict(
            variant=variant, strain=s, A_star_nm2_per_gDW=a_star,
            required_A_ETC_nm2_per_gDW=req,
            required_ratio_to_Astar=(None if req is None else req / a_star),
            required_fold_reduction=(None if req is None else a_star / req if req > 0 else None),
            baseline_mu_40C=base_fail, mu_40C_at_zero_area=zero_fail,
            mu_40C_complexes_deleted=deleted_fail, detection_floor_h=DETECTION_FLOOR,
            permissive_mu=perm, permissive_baseline=base_perm,
            permissive_preserved=(None if req is None else bool(perm >= PERMISSIVE_FRAC * base_perm)),
            note=note))
        print(f"[k4] counterfactual [{variant}] {s}: required A_ETC = "
              f"{'none' if req is None else f'{req:.4g}'} nm^2/gDW "
              f"({'-' if req is None else f'{a_star/req:.2f}x smaller than A*'}); "
              f"mu(40C) unconstrained {base_fail:.4f}, at A_ETC=0 {zero_fail:.4f}, "
              f"with these complexes DELETED {deleted_fail:.4f}, floor {DETECTION_FLOOR}. "
              f"{note}", flush=True)
        ea.remove_etc_area_constraint(pms[s])

    pd.DataFrame(rows).to_csv(os.path.join(HERE, "task3_sweep.csv"), index=False)
    pd.DataFrame(bind_rows).to_csv(os.path.join(HERE, "task3_binding.csv"), index=False)
    pd.DataFrame(cf_rows).to_csv(os.path.join(HERE, "task3_counterfactual.csv"), index=False)
    with open(os.path.join(HERE, "task3_flatness.json"), "w") as fh:
        json.dump(flat, fh, indent=2)
    print(f"\n[k4] wrote task3_sweep.csv ({len(rows)}), task3_binding.csv ({len(bind_rows)}), "
          f"task3_counterfactual.csv ({len(cf_rows)}), task3_flatness.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
