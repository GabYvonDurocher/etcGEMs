#!/usr/bin/env python3
"""task3_dcp_sweep.py -- K7 TASK 3: how much of the growth envelope's steepness is the dCp prior?

The kinetic envelope's curvature comes from a single shared literature prior,
`provider.dcp_prior_kJ = -4.0` kJ/mol/K, cited to Hobbs et al. 2013 (ACS Chem. Biol.) and never
tested against these organisms. K7 TASK 2 measured the consequence: the model's growth
activation energy is 1.24-2.29x the measured value in every species and every configuration,
and unlike the respiration error it barely moves between configurations.

THE RANGE, and its basis. This repository's own robustness analysis
(`strains/syn6803/run_p4_robustness.py`) takes the shared Hobbs-2013 prior as **-2 to
-6 kJ/mol/K**, with -4.0 the central value every strain uses. The sweep goes wider, -1 to -16,
so that a reconciling value can be found and then judged against that range rather than
constrained to lie inside it.

NO DEFAULT IS CHANGED. dCp is moved through `Perturbation.dCp_scale`, which multiplies the
transition-state dCp at solve time; `dCp_scale = 1.0` is the configured -4.0 kJ/mol/K. This is a
sensitivity analysis, and a value that fixes a fit is a finding rather than a parameter choice.

THE SECOND CONSEQUENCE, which is the point of asking. These models over-predict CT_max by +9.6
to +15.8 C (K4, section 4). If the dCp that reconciles the rising limb also pulls the ceiling
down, one parameter explains two failures; if it pushes the ceiling the wrong way, that is
equally worth knowing and rules the parameter out as an explanation.

Run from the project root, with $CANDIDAS_ROOT readable:

    python3 reports/K7_envelope/task3_dcp_sweep.py

Writes task3_dcp_sweep.csv beside this file.
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
from etcgem.tpc import TPC, apply_state                      # noqa: E402
from etcgem.transfer import load_measured_tpc                # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
K_EV = 8.617333262e-5
T_REF_K = 293.15
TEMPS = np.arange(22.0, 45.0, 2.0)
WIDE = np.linspace(15.0, 75.0, 121)          # the K2 descriptor grid, for CT_max
EXP = "candida_B5_respire"
DCP_BASE = -4.0                               # kJ/mol/K, the configured prior
LIT_LO, LIT_HI = -6.0, -2.0                   # Hobbs-2013 range as this repo uses it
SCALES = [0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 3.0, 4.0]

SPECIES = {
    "cauris_iRV973": dict(group="Clade1", otus=[1, 2, 3], label="C. auris (clade I)"),
    "chaemulonii_draft": dict(group="Hae", otus=[19, 20, 21], label="C. haemulonii"),
    "cduobushaemulonii_draft": dict(group="Duo", otus=[22, 23], label="C. duobushaemulonii"),
    "cparapsilosis_iDC1003": dict(group="para", otus=[16, 17, 18], label="C. parapsilosis"),
}
# observed upper thermal limits, as K2 PART C2 derives them
OBSERVED_LIMIT = {"cauris_iRV973": 44.0, "chaemulonii_draft": 38.0,
                  "cduobushaemulonii_draft": 38.0, "cparapsilosis_iDC1003": 38.0}


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
    return float(np.polyfit(1.0 / (K_EV * T_REF_K) - 1.0 / (K_EV * TK), np.log(y[ok]), 1)[0])


def main():
    root = candidas_root()
    if root is None:
        print("[k7] CANDIDAS_ROOT not found")
        return 1
    tab = os.path.join(root, "results", "tables")
    bayes = pd.read_csv(os.path.join(tab, "bayes_clade_params.csv")).set_index("Group")

    rows = []
    for strain, spec in SPECIES.items():
        grp = spec["group"]
        Topt_meas = float(bayes.loc[grp, "growth_Topt_C"])
        m_Eg = float(bayes.loc[grp, "growth_E_eV"])
        m_Er = float(bayes.loc[grp, "resp_E_eV"])
        pm = build_provider(resolve(strain, EXP))
        model = pm.ec.model
        o2 = next((r.id for r in model.reactions
                   if r.id.startswith("EX_") and len(r.metabolites) == 1
                   and list(r.metabolites)[0].id.startswith("C00007__")), None)
        meas = load_measured_tpc(strain, resolve(strain, EXP))
        for sc in SCALES:
            pert = Perturbation(dCp_scale=sc)
            mus, qs = [], []
            for T in TEMPS:
                apply_state(pm.ec, float(T), pert)
                sol = model.optimize()
                ok = sol.status == "optimal"
                mus.append(float(sol.objective_value or 0.0) if ok else 0.0)
                qs.append(abs(float(sol.fluxes.get(o2, 0.0))) if (ok and o2) else np.nan)
            mus, qs = np.array(mus), np.array(qs)
            gw = np.zeros(len(WIDE))
            for i, T in enumerate(WIDE):
                apply_state(pm.ec, float(T), pert)
                v = model.slim_optimize()
                gw[i] = 0.0 if (v is None or not np.isfinite(v) or v < 1e-6) else v
            scale = float(meas["mu"].max() / max(gw.max(), 1e-9))
            d = TPC(WIDE, gw * scale).descriptors(0.05)
            pred = np.interp(meas["T_C"].values.astype(float), WIDE, gw) * scale
            obs = meas["mu"].values.astype(float)
            ss_res = float(np.sum((obs - pred) ** 2))
            ss_tot = float(np.sum((obs - obs.mean()) ** 2))
            r2 = np.nan if ss_tot <= 0 else 1.0 - ss_res / ss_tot
            sel = TEMPS <= Topt_meas
            Eg, Er = ols_E(TEMPS[sel], mus[sel]), ols_E(TEMPS, qs)
            rows.append(dict(
                species=spec["label"], strain=strain, dCp_scale=sc,
                dCp_kJ=DCP_BASE * sc, in_literature_range=bool(LIT_LO <= DCP_BASE * sc <= LIT_HI),
                model_E_growth=Eg, measured_E_growth=m_Eg, steepness=Eg / m_Eg,
                model_E_resp=Er, measured_E_resp=m_Er, model_diff=Er - Eg,
                Topt_C=d.Topt_C, CTmax_C=d.CTmax_C,
                observed_limit_C=OBSERVED_LIMIT[strain],
                ceiling_gap_C=d.CTmax_C - OBSERVED_LIMIT[strain],
                fit_r2=r2, peak_mu_model=float(gw.max())))
            print(f"[k7] {spec['label']:22s} dCp {DCP_BASE*sc:7.2f} kJ/mol/K "
                  f"{'(lit)' if LIT_LO <= DCP_BASE*sc <= LIT_HI else '     '}  "
                  f"E_growth {Eg:6.3f} ({Eg/m_Eg:4.2f}x)  E_resp {Er:6.3f}  "
                  f"Topt {d.Topt_C:5.1f}  CTmax {d.CTmax_C:5.2f} "
                  f"(gap {d.CTmax_C-OBSERVED_LIMIT[strain]:+5.1f})  R2 {r2:6.3f}", flush=True)

    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(HERE, "task3_dcp_sweep.csv"), index=False)
    print("\n=== the dCp that best reconciles E_growth with measurement, per species ===")
    for s in df.species.unique():
        x = df[df.species == s].copy()
        x["err"] = (x["steepness"] - 1.0).abs()
        b = x.loc[x["err"].idxmin()]
        print(f"  {s:22s} dCp {b['dCp_kJ']:7.2f} kJ/mol/K  "
              f"{'INSIDE' if b['in_literature_range'] else 'OUTSIDE'} the -2..-6 range;  "
              f"steepness {b['steepness']:.2f}x, CTmax gap {b['ceiling_gap_C']:+.1f} C, "
              f"R2 {b['fit_r2']:.3f}")
    print("\n[k7] wrote task3_dcp_sweep.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
