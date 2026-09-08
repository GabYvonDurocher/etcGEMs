#!/usr/bin/env python3
"""task2_like_for_like.py -- K6 TASK 2: redo K5's model-vs-measurement comparison like for like.

THREE PANELS, so the effect of the comparator is visible rather than assumed:

  (a) RISING LIMB, BOTH SIDES, THE ORGANISM'S WINDOW. Model and measurement fitted with the same
      OLS Arrhenius over the same temperatures -- at or below the organism's Bayesian growth
      optimum. This is the only panel in which both sides are treated identically AND the window
      is chosen by the data rather than by the model.

  (b) FULL WINDOW, BOTH SIDES. What K5 did, retained for continuity, with the caveat stated:
      the model does not turn over where the organism does (K4/section 4 puts the model's
      thermal limit 9.6-15.8 C too high), so this window contains the organism's collapse and
      not the model's.

  (c) AGAINST THE MANUSCRIPT'S BAYESIAN VALUES, which are what the paper quotes. To match that
      quantity the model is fitted the way the manuscript fits: growth on its rising limb,
      respiration over the full range.

The same treatment is applied to the other two rows K5 reported -- the respiration-to-growth
level and the 44/30 ratio -- restricted to temperatures where the organism is actually growing.

Run from the project root, with $CANDIDAS_ROOT readable:

    python3 reports/K6_like_for_like/task2_like_for_like.py

Writes task2_panels.csv, task2_ratio.csv and task2_model_curves.csv beside this file.
"""
from __future__ import annotations

import logging
import os
import sys

import numpy as np
import pandas as pd

logging.getLogger("cobra").setLevel(logging.ERROR)
sys.path.insert(0, "src")

from etcgem.config import build_provider, resolve            # noqa: E402
from etcgem.enzyme_cost import Perturbation                  # noqa: E402
from etcgem.tpc import apply_state                           # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
K_EV = 8.617333262e-5
T_REF_K = 293.15
TEMPS = np.arange(22.0, 45.0, 2.0)
C_BIOMASS = 37.5      # mmol C/gDW at 45 % carbon by dry mass; NOMINAL, and labelled

SPECIES = {
    "cauris_iRV973": dict(group="Clade1", otus=[1, 2, 3], label="C. auris (clade I)"),
    "chaemulonii_draft": dict(group="Hae", otus=[19, 20, 21], label="C. haemulonii"),
    "cduobushaemulonii_draft": dict(group="Duo", otus=[22, 23], label="C. duobushaemulonii"),
    "cparapsilosis_iDC1003": dict(group="para", otus=[16, 17, 18], label="C. parapsilosis"),
}
CONFIGS = {"before (B3)": "candida_B3_ngamT", "repaired (B5)": "candida_B5_respire"}
COMPLEX_III = {"cauris_iRV973": "R02161__mito", "chaemulonii_draft": "R02161__mito",
               "cduobushaemulonii_draft": "R02161__mito"}
SENS = "repaired + complex III"


def candidas_root():
    r = os.environ.get("CANDIDAS_ROOT")
    if r and os.path.isdir(r):
        return r
    g = os.path.abspath(os.path.join(HERE, "..", "..", "..", "Candidas TPC", "Candidas"))
    return g if os.path.isdir(g) else None


def ols_E(T_C, y):
    """The measured pipeline's own fit: lm(ln y ~ boltz). Used on BOTH sides, always."""
    T_C, y = np.asarray(T_C, float), np.asarray(y, float)
    ok = np.isfinite(T_C) & np.isfinite(y) & (y > 0)
    if ok.sum() < 3 or len(np.unique(T_C[ok])) < 2:
        return np.nan
    TK = T_C[ok] + 273.15
    boltz = 1.0 / (K_EV * T_REF_K) - 1.0 / (K_EV * TK)
    return float(np.polyfit(boltz, np.log(y[ok]), 1)[0])


def exch(model, prefix, names=()):
    for r in model.reactions:
        if r.id.startswith("EX_") and len(r.metabolites) == 1:
            m_ = list(r.metabolites)[0]
            if m_.id.startswith(prefix) or (m_.name or "").strip().lower() in names:
                return r.id
    return None


def model_curves(strain, exp, flip_ciii=False):
    pm = build_provider(resolve(strain, exp))
    model = pm.ec.model
    if flip_ciii and strain in COMPLEX_III:
        r3 = model.reactions.get_by_id(COMPLEX_III[strain])
        r3.add_metabolites({m_: -2.0 * c for m_, c in list(r3.metabolites.items())
                            if m_.id in ("C00080__cyto", "C00080__mito")})
        model.solver.update()
    o2 = exch(model, "C00007__", ("o2", "oxygen"))
    mus, qs = [], []
    for T in TEMPS:
        apply_state(pm.ec, float(T), Perturbation())
        sol = model.optimize()
        ok = sol.status == "optimal"
        mus.append(float(sol.objective_value or 0.0) if ok else 0.0)
        qs.append(abs(float(sol.fluxes.get(o2, 0.0))) if (ok and o2) else np.nan)
    return np.array(mus), np.array(qs)


def main():
    root = candidas_root()
    if root is None:
        print("[k6] CANDIDAS_ROOT not found")
        return 1
    tab = os.path.join(root, "results", "tables")
    meas = pd.read_csv(os.path.join(tab, "derived_N0_R_results_with_carbon.csv"))
    meas = meas[(meas.keep) & (meas.fit_valid)]
    bayes = pd.read_csv(os.path.join(tab, "bayes_clade_params.csv")).set_index("Group")
    bdiff = pd.read_csv(os.path.join(tab, "bayes_E_resp_minus_growth.csv")).set_index("Group")

    rows, ratio_rows, curve_rows = [], [], []
    for strain, spec in SPECIES.items():
        grp = spec["group"]
        Topt = float(bayes.loc[grp, "growth_Topt_C"])
        mx = meas[meas.OTU.isin(spec["otus"])]
        mg = mx.groupby("T")["growth_fgC_h"].mean()
        mr = mx.groupby("T")["respiration_fgC_h"].mean()
        rise_T = np.array([t for t in mg.index if t <= Topt], float)

        # measured, the three ways
        m_Eg_rise = ols_E(rise_T, mg.reindex(rise_T).values)
        m_Er_rise = ols_E(rise_T, mr.reindex(rise_T).values)
        m_Eg_full = ols_E(mg.index.values, mg.values)
        m_Er_full = ols_E(mr.index.values, mr.values)
        m_Eg_bayes = float(bayes.loc[grp, "growth_E_eV"])
        m_Er_bayes = float(bayes.loc[grp, "resp_E_eV"])
        m_diff_bayes = float(bdiff.loc[grp, "E_resp_minus_growth"])
        lo_b, hi_b = float(bdiff.loc[grp, "lo"]), float(bdiff.loc[grp, "hi"])

        runs = [(k, v, False) for k, v in CONFIGS.items()]
        if strain in COMPLEX_III:
            runs.append((SENS, "candida_B5_respire", True))
        for cfg, exp, flip in runs:
            mu, q = model_curves(strain, exp, flip)
            for i, T in enumerate(TEMPS):
                curve_rows.append(dict(strain=strain, species=spec["label"], config=cfg,
                                       T_C=T, mu=mu[i], qO2=q[i]))
            sel = TEMPS <= Topt
            # (a) rising limb, organism's window, both sides same form
            a_Eg, a_Er = ols_E(TEMPS[sel], mu[sel]), ols_E(TEMPS[sel], q[sel])
            # (b) full window, both sides
            b_Eg, b_Er = ols_E(TEMPS, mu), ols_E(TEMPS, q)
            # (c) the manuscript's convention: growth rising limb, respiration full range
            c_Eg, c_Er = a_Eg, b_Er
            for panel, (eg, er, meg, mer, mdiff, lo, hi) in {
                "(a) rising limb, organism's window, both sides":
                    (a_Eg, a_Er, m_Eg_rise, m_Er_rise,
                     m_Er_rise - m_Eg_rise, np.nan, np.nan),
                "(b) full window, both sides (K5's)":
                    (b_Eg, b_Er, m_Eg_full, m_Er_full,
                     m_Er_full - m_Eg_full, np.nan, np.nan),
                "(c) manuscript convention vs Bayesian":
                    (c_Eg, c_Er, m_Eg_bayes, m_Er_bayes, m_diff_bayes, lo_b, hi_b),
            }.items():
                rows.append(dict(
                    panel=panel, species=spec["label"], group=grp, strain=strain, config=cfg,
                    Topt_cut_C=Topt,
                    model_E_growth=eg, model_E_resp=er, model_diff=er - eg,
                    measured_E_growth=meg, measured_E_resp=mer, measured_diff=mdiff,
                    measured_diff_lo=lo, measured_diff_hi=hi,
                    sign_agrees=bool(np.sign(er - eg) == np.sign(mdiff)),
                    within_measured_CI=(bool(lo <= (er - eg) <= hi)
                                        if np.isfinite(lo) else None)))
            # the ratio rows, restricted to where the organism actually grows
            growing = [t for t in mg.index if mg.loc[t] > 0 and t <= 40]
            sel_g = np.isin(TEMPS, growing)
            with np.errstate(divide="ignore", invalid="ignore"):
                model_ratio = np.where(mu > 1e-9, q / mu, np.nan) / C_BIOMASS
            meas_ratio = (mr / mg).reindex(TEMPS).values
            ratio_rows.append(dict(
                species=spec["label"], config=cfg,
                window="organism growing (<=40 C, mu>0)",
                model_mean=float(np.nanmean(model_ratio[sel_g])),
                measured_mean=float(np.nanmean(meas_ratio[sel_g])),
                fold=float(np.nanmean(model_ratio[sel_g]) / np.nanmean(meas_ratio[sel_g])),
                model_44_over_30=float(model_ratio[TEMPS == 44][0] / model_ratio[TEMPS == 30][0]),
                measured_44_over_30=float(meas_ratio[TEMPS == 44][0] / meas_ratio[TEMPS == 30][0])
                if np.isfinite(meas_ratio[TEMPS == 44][0]) else np.nan,
                model_Tcut_over_30=float(model_ratio[TEMPS == max(growing)][0]
                                         / model_ratio[TEMPS == 30][0]),
                measured_Tcut_over_30=float(meas_ratio[TEMPS == max(growing)][0]
                                            / meas_ratio[TEMPS == 30][0]),
                T_cut=max(growing)))
        print(f"[k6] {spec['label']} done", flush=True)

    d = pd.DataFrame(rows)
    d.to_csv(os.path.join(HERE, "task2_panels.csv"), index=False)
    pd.DataFrame(ratio_rows).to_csv(os.path.join(HERE, "task2_ratio.csv"), index=False)
    pd.DataFrame(curve_rows).to_csv(os.path.join(HERE, "task2_model_curves.csv"), index=False)

    for panel in d.panel.unique():
        print(f"\n===== {panel}")
        x = d[(d.panel == panel) & (d.config == "repaired (B5)")]
        print(f"{'species':22s} {'model diff':>10s} {'measured':>10s} "
              f"{'sign agrees':>12s} {'in 95% CI':>10s}")
        for _, r in x.iterrows():
            ci = "-" if r["within_measured_CI"] is None else ("yes" if r["within_measured_CI"] else "no")
            print(f"{r['species']:22s} {r['model_diff']:10.3f} {r['measured_diff']:10.3f} "
                  f"{str(r['sign_agrees']):>12s} {ci:>10s}")
    print("\n[k6] wrote task2_panels.csv, task2_ratio.csv, task2_model_curves.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
