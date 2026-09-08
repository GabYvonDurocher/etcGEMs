#!/usr/bin/env python3
"""task2_envelope.py -- K7 TASK 2: is the model's growth envelope too steep? Measure it.

K6 attributed 88 % of the residual model-data discrepancy to this, by subtraction. This tests it
directly and decomposes the difference into its two parts, so neither is quoted as a single
number.

THE RULE, from K6 and now standing: same window, same functional form, both sides. The window is
the ORGANISM's rising limb -- at or below each group's Bayesian `growth_Topt_C` -- and the form
is the measured pipeline's own `lm(ln y ~ boltz)`, applied identically to model and measurement.

TWO MEASURED COMPARATORS are reported for growth, because K6 established there is no single
measured E_growth:
  * the hierarchical Sharpe-Schoolfield value the manuscript quotes (0.62-1.15 eV), and
  * K6's refit of the OLS to the rising limb (0.21-0.93 eV),
which bracket the honest range. Respiration has one: the full-range Arrhenius, on which the OLS
and the Bayesian fit agree, because respiration does not turn over.

Configurations: the repaired model (B5), the model before the repair (B3), and B5 with NGAM(T)
switched off -- K6 found respiration lands on measurement when maintenance is removed, and this
confirms which side of the difference carries the error.

Run from the project root, with $CANDIDAS_ROOT readable:

    python3 reports/K7_envelope/task2_envelope.py

Writes task2_envelope.csv beside this file.
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

SPECIES = {
    "cauris_iRV973": dict(group="Clade1", otus=[1, 2, 3], label="C. auris (clade I)"),
    "chaemulonii_draft": dict(group="Hae", otus=[19, 20, 21], label="C. haemulonii"),
    "cduobushaemulonii_draft": dict(group="Duo", otus=[22, 23], label="C. duobushaemulonii"),
    "cparapsilosis_iDC1003": dict(group="para", otus=[16, 17, 18], label="C. parapsilosis"),
}
# label -> (experiment, ngam multiplier)
RUNS = {"B3 (before the repair)": ("candida_B3_ngamT", 1.0),
        "B5 (repaired)": ("candida_B5_respire", 1.0),
        "B5, NGAM(T) off": ("candida_B5_respire", 0.0)}


def candidas_root():
    r = os.environ.get("CANDIDAS_ROOT")
    if r and os.path.isdir(r):
        return r
    g = os.path.abspath(os.path.join(HERE, "..", "..", "..", "Candidas TPC", "Candidas"))
    return g if os.path.isdir(g) else None


def ols_E(T_C, y):
    T_C, y = np.asarray(T_C, float), np.asarray(y, float)
    ok = np.isfinite(T_C) & np.isfinite(y) & (y > 0)
    if ok.sum() < 3 or len(np.unique(T_C[ok])) < 2:
        return np.nan
    TK = T_C[ok] + 273.15
    boltz = 1.0 / (K_EV * T_REF_K) - 1.0 / (K_EV * TK)
    return float(np.polyfit(boltz, np.log(y[ok]), 1)[0])


def main():
    root = candidas_root()
    if root is None:
        print("[k7] CANDIDAS_ROOT not found")
        return 1
    tab = os.path.join(root, "results", "tables")
    meas = pd.read_csv(os.path.join(tab, "derived_N0_R_results_with_carbon.csv"))
    meas = meas[(meas.keep) & (meas.fit_valid)]
    bayes = pd.read_csv(os.path.join(tab, "bayes_clade_params.csv")).set_index("Group")

    rows = []
    for strain, spec in SPECIES.items():
        grp = spec["group"]
        Topt = float(bayes.loc[grp, "growth_Topt_C"])
        mx = meas[meas.OTU.isin(spec["otus"])]
        mg = mx.groupby("T")["growth_fgC_h"].mean()
        mr = mx.groupby("T")["respiration_fgC_h"].mean()
        rise_T = np.array([t for t in mg.index if t <= Topt], float)
        m_Eg_rise = ols_E(rise_T, mg.reindex(rise_T).values)
        m_Eg_bayes = float(bayes.loc[grp, "growth_E_eV"])
        m_Er_full = ols_E(mr.index.values, mr.values)
        m_Er_bayes = float(bayes.loc[grp, "resp_E_eV"])

        for label, (exp, ng) in RUNS.items():
            cfg = resolve(strain, exp)
            cfg["provider"]["ngam_base_scale"] = \
                float(cfg["provider"].get("ngam_base_scale", 1.0)) * ng
            pm = build_provider(cfg)
            model = pm.ec.model
            o2 = next((r.id for r in model.reactions
                       if r.id.startswith("EX_") and len(r.metabolites) == 1
                       and list(r.metabolites)[0].id.startswith("C00007__")), None)
            mus, qs = [], []
            for T in TEMPS:
                apply_state(pm.ec, float(T), Perturbation())
                sol = model.optimize()
                ok = sol.status == "optimal"
                mus.append(float(sol.objective_value or 0.0) if ok else 0.0)
                qs.append(abs(float(sol.fluxes.get(o2, 0.0))) if (ok and o2) else np.nan)
            mus, qs = np.array(mus), np.array(qs)
            sel = TEMPS <= Topt
            Eg, Er = ols_E(TEMPS[sel], mus[sel]), ols_E(TEMPS, qs)
            rows.append(dict(
                species=spec["label"], strain=strain, config=label, Topt_cut_C=Topt,
                model_E_growth=Eg, model_E_resp=Er, model_diff=Er - Eg,
                measured_E_growth_bayes=m_Eg_bayes, measured_E_growth_riseOLS=m_Eg_rise,
                measured_E_resp_bayes=m_Er_bayes, measured_E_resp_OLS=m_Er_full,
                growth_steepness_vs_bayes=Eg / m_Eg_bayes,
                growth_steepness_vs_riseOLS=Eg / m_Eg_rise,
                resp_ratio_vs_bayes=Er / m_Er_bayes,
                growth_excess_eV=Eg - m_Eg_bayes, resp_deficit_eV=Er - m_Er_bayes))
            print(f"[k7] {spec['label']:22s} {label:22s} "
                  f"E_growth {Eg:6.3f} (measured {m_Eg_bayes:5.3f} Bayes / "
                  f"{m_Eg_rise:5.3f} riseOLS) = {Eg/m_Eg_bayes:4.2f}x ; "
                  f"E_resp {Er:6.3f} (measured {m_Er_bayes:5.3f}) = "
                  f"{Er/m_Er_bayes:4.2f}x", flush=True)

    d = pd.DataFrame(rows)
    d.to_csv(os.path.join(HERE, "task2_envelope.csv"), index=False)
    print("\n=== VERDICT: is the model's growth envelope too steep? ===")
    for cfg in RUNS:
        x = d[d.config == cfg]
        print(f"\n  {cfg}")
        print(f"    growth steepness vs the Bayesian value: "
              f"{x['growth_steepness_vs_bayes'].min():.2f}-"
              f"{x['growth_steepness_vs_bayes'].max():.2f}x "
              f"(median {x['growth_steepness_vs_bayes'].median():.2f}x)")
        print(f"    respiration        vs the Bayesian value: "
              f"{x['resp_ratio_vs_bayes'].min():.2f}-{x['resp_ratio_vs_bayes'].max():.2f}x "
              f"(median {x['resp_ratio_vs_bayes'].median():.2f}x)")
        print(f"    excess in growth {x['growth_excess_eV'].median():+.3f} eV, "
              f"deficit in respiration {x['resp_deficit_eV'].median():+.3f} eV")
    print("\n[k7] wrote task2_envelope.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
