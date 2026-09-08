#!/usr/bin/env python3
"""task3_respiration_test.py -- K5 TASK 3: does the repaired model respire like the organism?

THIS COMPARISON HAS NEVER BEEN MADE. The Candida models have been fitted and tested against
measured GROWTH throughout; the measured O2 assay has never been put beside what they predict
for respiration.

SCALE-FREE BY CONSTRUCTION. Absolute per-cell O2 depends on the cell-mass conversion, and that
conversion is unreliable: the derived tables carry 2 um^3 / 350 fg (8 / 1320 for most isolates)
typed as constants while the pipeline's own config.R logs 21.21 um^3 / 2120.58 fg, about 6x
apart (OPEN_ITEMS 1.9). So the conclusions rest on three quantities in which that factor
cancels:

  1. RESPIRATION-TO-GROWTH RATIO. Measured `resp_over_growth` is carbon per carbon. The model
     predicts both, and the model's qO2/mu differs from it only by the carbon content of
     biomass -- a per-species constant, and the SAME constant for the three iRV973-derived
     models, which share a biomass reaction. So the between-species ordering and the
     temperature dependence are both directly comparable; the absolute level is not, and is
     not used.
  2. ACTIVATION ENERGY of respiration, and of growth, fitted the same way on both sides:
     ln(rate) against 1/kT over the twelve assayed temperatures. A slope is scale-free.
     E_resp - E_growth is scale-free twice over and is the sharpest single number here.
  3. THE SHAPE of the respiration curve against the growth curve -- where each peaks, and
     whether respiration keeps rising after growth turns over.

Absolute per-cell respiration is reported and LABELLED as carrying the cell-mass assumption.
Nothing is concluded from it.

Run from the project root, with the measured tables readable:

    CANDIDAS_ROOT=/path/to/Candidas python3 reports/K5_respire/task3_respiration_test.py

Writes task3_curves.csv, task3_activation_energies.csv, task3_ratio.csv and
task3_absolute_labelled.csv beside this file.
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

# model strain -> the measured OTUs it corresponds to.
# C. auris clade I (B8441) is the model organism, so clade 1 is the primary comparator and all
# twelve auris isolates are carried as a sensitivity.
SPECIES = {
    "cauris_iRV973": dict(primary=[1, 2, 3], all_isolates=list(range(1, 13)),
                          label="C. auris (clade I)"),
    "chaemulonii_draft": dict(primary=[19, 20, 21], all_isolates=[19, 20, 21],
                              label="C. haemulonii"),
    "cduobushaemulonii_draft": dict(primary=[22, 23], all_isolates=[22, 23],
                                    label="C. duobushaemulonii"),
    "cparapsilosis_iDC1003": dict(primary=[16, 17, 18], all_isolates=[16, 17, 18],
                                  label="C. parapsilosis"),
}
CONFIGS = {"before (B3)": "candida_B3_ngamT", "after (B5, repaired)": "candida_B5_respire"}
# A LABELLED SENSITIVITY, not an adopted configuration. K4 found, and K5 TASK 2 quantified,
# that complex III in the three iRV973-derived models is encoded with its 1.5 protons moving
# cytosol->matrix, the opposite direction to a mitochondrion, so it SPENDS proton-motive force
# and eats exactly half of what cytochrome c oxidase pumps. This flips it back, on top of the
# B5 repair, to ask whether that second defect is what stands between the repaired model and
# the measurement. It is a second change to the reconstruction and is reported separately for
# that reason.
COMPLEX_III = {"cauris_iRV973": "R02161__mito", "chaemulonii_draft": "R02161__mito",
               "cduobushaemulonii_draft": "R02161__mito"}
SENSITIVITY = "B5 + complex III direction (sensitivity)"
TEMPS = np.arange(22.0, 45.0, 2.0)          # the twelve assayed temperatures
GDW_PER_CELL = 2.8e-13                      # g/cell, the E. coli value; LABELLED, see below


def candidas_root():
    r = os.environ.get("CANDIDAS_ROOT")
    if r and os.path.isdir(r):
        return r
    guess = os.path.abspath(os.path.join(
        os.path.dirname(HERE), "..", "..", "..", "Candidas TPC", "Candidas"))
    return guess if os.path.isdir(guess) else None


def o2_exchange(model):
    for r in model.reactions:
        if r.id.startswith("EX_") and len(r.metabolites) == 1:
            m_ = list(r.metabolites)[0]
            if m_.id.startswith("C00007__") or "oxygen" in (m_.name or "").lower():
                return r.id
    return None


def co2_exchange(model):
    for r in model.reactions:
        if r.id.startswith("EX_") and len(r.metabolites) == 1:
            m_ = list(r.metabolites)[0]
            if m_.id.startswith("C00011__") or (m_.name or "").strip().lower() == "co2":
                return r.id
    return None


def arrhenius_E(temps_C, rates, mask=None):
    """Boltzmann-Arrhenius slope, ln(rate) against 1/kT, over the given points.

    Fitted exactly as the measured coefficients were: over ALL assayed temperatures, not over
    a hand-picked rising limb, so the two sides are comparable."""
    t = np.asarray(temps_C, float)
    r = np.asarray(rates, float)
    ok = np.isfinite(r) & (r > 0)
    if mask is not None:
        ok &= mask
    if ok.sum() < 3:
        return np.nan, np.nan, np.nan
    x = 1.0 / (K_EV * (t[ok] + 273.15))
    y = np.log(r[ok])
    slope, intercept = np.polyfit(x, y, 1)
    yhat = slope * x + intercept
    ss_res = float(np.sum((y - yhat) ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    r2 = np.nan if ss_tot <= 0 else 1.0 - ss_res / ss_tot
    return float(-slope), float(intercept), float(r2)


def main():
    root = candidas_root()
    if root is None:
        print("[k5] CANDIDAS_ROOT not found; cannot run the measured comparison")
        return 1
    tab = os.path.join(root, "results", "tables")
    meas = pd.read_csv(os.path.join(tab, "derived_N0_R_results_with_carbon.csv"))
    meas = meas[(meas.keep) & (meas.fit_valid)]
    ar = pd.read_csv(os.path.join(tab, "arrhenius_respiration_fgC_h_coefs.csv"))
    ag = pd.read_csv(os.path.join(tab, "arrhenius_growth_fgC_h_coefs.csv"))

    curve_rows, ea_rows, ratio_rows, abs_rows = [], [], [], []
    for strain, spec in SPECIES.items():
        runs = [(k, v, False) for k, v in CONFIGS.items()]
        if strain in COMPLEX_III:
            runs.append((SENSITIVITY, "candida_B5_respire", True))
        for cfg_label, exp, flip_ciii in runs:
            pm = build_provider(resolve(strain, exp))
            model = pm.ec.model
            if flip_ciii:
                r3 = model.reactions.get_by_id(COMPLEX_III[strain])
                delta = {}
                for m_, c in list(r3.metabolites.items()):
                    if m_.id == "C00080__cyto":
                        delta[m_] = -2.0 * c
                    elif m_.id == "C00080__mito":
                        delta[m_] = -2.0 * c
                r3.add_metabolites(delta)
                model.solver.update()
            o2, co2 = o2_exchange(model), co2_exchange(model)
            mus, qo2s, qco2s = [], [], []
            for T in TEMPS:
                apply_state(pm.ec, float(T), Perturbation())
                sol = model.optimize()
                mu = float(sol.objective_value or 0.0) if sol.status == "optimal" else 0.0
                q = abs(float(sol.fluxes.get(o2, 0.0))) if (o2 and sol.status == "optimal") else np.nan
                qc = abs(float(sol.fluxes.get(co2, 0.0))) if (co2 and sol.status == "optimal") else np.nan
                mus.append(mu); qo2s.append(q); qco2s.append(qc)
                curve_rows.append(dict(strain=strain, species=spec["label"], config=cfg_label,
                                       T_C=T, mu=mu, qO2=q, qCO2=qc,
                                       qO2_over_mu=(q / mu if mu > 1e-9 else np.nan)))
            mus, qo2s = np.array(mus), np.array(qo2s)
            E_r, _, r2r = arrhenius_E(TEMPS, qo2s)
            E_g, _, r2g = arrhenius_E(TEMPS, mus)
            # measured, for the same species
            m_r = ar[ar.OTU.isin(spec["primary"])]["E_eV"]
            m_g = ag[ag.OTU.isin(spec["primary"])]["E_eV"]
            ea_rows.append(dict(
                strain=strain, species=spec["label"], config=cfg_label,
                model_E_resp_eV=E_r, model_E_growth_eV=E_g,
                model_E_resp_minus_growth=E_r - E_g,
                model_r2_resp=r2r, model_r2_growth=r2g,
                measured_E_resp_eV=m_r.mean(), measured_E_resp_sd=m_r.std(),
                measured_E_growth_eV=m_g.mean(), measured_E_growth_sd=m_g.std(),
                measured_E_resp_minus_growth=m_r.mean() - m_g.mean(),
                n_isolates=len(m_r)))
            # peaks
            i_g = int(np.nanargmax(mus)) if np.isfinite(mus).any() else -1
            i_r = int(np.nanargmax(qo2s)) if np.isfinite(qo2s).any() else -1
            mm = meas[meas.OTU.isin(spec["primary"])].groupby("T")[
                ["growth_C_per_C_h", "respiration_C_per_C_h", "resp_over_growth"]].mean()
            ea_rows[-1].update(
                model_growth_peak_C=(TEMPS[i_g] if i_g >= 0 else np.nan),
                model_resp_peak_C=(TEMPS[i_r] if i_r >= 0 else np.nan),
                measured_growth_peak_C=float(mm["growth_C_per_C_h"].idxmax()),
                measured_resp_peak_C=float(mm["respiration_C_per_C_h"].idxmax()))
            # the ratio, per temperature, model against measurement
            for T in TEMPS:
                j = int(np.where(TEMPS == T)[0][0])
                mrow = mm.loc[T] if T in mm.index else None
                ratio_rows.append(dict(
                    strain=strain, species=spec["label"], config=cfg_label, T_C=T,
                    model_qO2_over_mu=(qo2s[j] / mus[j] if mus[j] > 1e-9 else np.nan),
                    measured_resp_over_growth=(float(mrow["resp_over_growth"])
                                               if mrow is not None else np.nan)))
                abs_rows.append(dict(
                    strain=strain, species=spec["label"], config=cfg_label, T_C=T,
                    model_qO2_mmol_gDW_h=qo2s[j],
                    model_O2_fmol_per_cell_h=qo2s[j] * GDW_PER_CELL * 1e12,
                    LABEL="carries the cell-mass assumption; not concluded from"))
            print(f"[k5] {spec['label']:22s} {cfg_label:22s} "
                  f"E_resp {E_r:5.3f} (measured {m_r.mean():5.3f}), "
                  f"E_growth {E_g:6.3f} (measured {m_g.mean():6.3f}), "
                  f"E_resp-E_growth {E_r - E_g:6.3f} (measured "
                  f"{m_r.mean() - m_g.mean():6.3f}); peaks: growth "
                  f"{TEMPS[i_g]:.0f}/{mm['growth_C_per_C_h'].idxmax():.0f} C, resp "
                  f"{TEMPS[i_r]:.0f}/{mm['respiration_C_per_C_h'].idxmax():.0f} C", flush=True)

    pd.DataFrame(curve_rows).to_csv(os.path.join(HERE, "task3_curves.csv"), index=False)
    pd.DataFrame(ea_rows).to_csv(os.path.join(HERE, "task3_activation_energies.csv"),
                                 index=False)
    pd.DataFrame(ratio_rows).to_csv(os.path.join(HERE, "task3_ratio.csv"), index=False)
    pd.DataFrame(abs_rows).to_csv(os.path.join(HERE, "task3_absolute_labelled.csv"),
                                  index=False)
    print("\n[k5] wrote task3_curves.csv, task3_activation_energies.csv, task3_ratio.csv, "
          "task3_absolute_labelled.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
