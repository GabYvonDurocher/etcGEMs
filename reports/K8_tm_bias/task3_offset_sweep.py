#!/usr/bin/env python3
"""task3_offset_sweep.py -- K8 TASK 3: is 5.43 C special, or does any offset do?

A correction that works at the independently measured value is a test. One that needs a value
far from it is not the hypothesis, whatever it does to the fit. This sweeps the uniform Tm
offset from 0 to 20 C and reports where each species' ceiling gap is minimised, against A1's
measured +5.43 C.

The offset is applied through `Perturbation(dTm=...)`; no default is changed.

Run from the project root, with $CANDIDAS_ROOT readable:

    python3 reports/K8_tm_bias/task3_offset_sweep.py

Writes task3_offset_sweep.csv beside this file.
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
WIDE = np.linspace(15.0, 75.0, 121)
EXP = "candida_B5_respire"
A1_BIAS = 5.43
OFFSETS = [0.0, 2.0, 4.0, 5.43, 6.0, 8.0, 10.0, 12.0, 15.0, 20.0]

SPECIES = {
    "cauris_iRV973": dict(group="Clade1", label="C. auris (clade I)", limit=44.0),
    "chaemulonii_draft": dict(group="Hae", label="C. haemulonii", limit=38.0),
    "cduobushaemulonii_draft": dict(group="Duo", label="C. duobushaemulonii", limit=38.0),
    "cparapsilosis_iDC1003": dict(group="para", label="C. parapsilosis", limit=38.0),
}


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
        print("[k8] CANDIDAS_ROOT not found")
        return 1
    bayes = pd.read_csv(os.path.join(root, "results", "tables",
                                     "bayes_clade_params.csv")).set_index("Group")
    rows = []
    for strain, spec in SPECIES.items():
        Topt_cut = float(bayes.loc[spec["group"], "growth_Topt_C"])
        meas = load_measured_tpc(strain, resolve(strain, EXP))
        pm = build_provider(resolve(strain, EXP))
        model = pm.ec.model
        for off in OFFSETS:
            pert = Perturbation(dTm=-off)
            mus = []
            for T in TEMPS:
                apply_state(pm.ec, float(T), pert)
                v = model.slim_optimize()
                mus.append(0.0 if (v is None or not np.isfinite(v)) else v)
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
            sel = TEMPS <= Topt_cut
            rows.append(dict(species=spec["label"], strain=strain, offset_C=off,
                             CTmax_C=d.CTmax_C, gap_C=d.CTmax_C - spec["limit"],
                             abs_gap=abs(d.CTmax_C - spec["limit"]),
                             Topt_C=d.Topt_C, Ea_eV=d.Ea_eV, fit_r2=r2,
                             E_growth=ols_E(TEMPS[sel], np.array(mus)[sel])))
            print(f"[k8] {spec['label']:22s} offset -{off:5.2f}  CTmax {d.CTmax_C:6.2f}  "
                  f"gap {d.CTmax_C-spec['limit']:+6.2f}  Topt {d.Topt_C:5.1f}  "
                  f"E_growth {rows[-1]['E_growth']:6.3f}  R2 {r2:6.3f}", flush=True)

    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(HERE, "task3_offset_sweep.csv"), index=False)
    print("\n=== the offset that minimises the ceiling gap, per species, against A1's 5.43 C ===")
    for sp in df.species.unique():
        x = df[df.species == sp]
        b = x.loc[x["abs_gap"].idxmin()]
        bf = x.loc[x["fit_r2"].idxmax()]
        print(f"  {sp:22s} gap minimised at {b['offset_C']:5.2f} C "
              f"(gap {b['gap_C']:+.2f});  distance from 5.43 = "
              f"{abs(b['offset_C']-A1_BIAS):5.2f} C;  fit maximised at {bf['offset_C']:5.2f} C "
              f"(R2 {bf['fit_r2']:.3f})")
    print("\n[k8] wrote task3_offset_sweep.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
