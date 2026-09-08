#!/usr/bin/env python3
"""task3_maintenance_test.py -- K6 TASK 3: does the maintenance layer close the magnitude gap?

K5 concluded that its discrepancy "points at the maintenance layer, not the ETC". K6 TASK 2
shows the SIGN part of that discrepancy was a comparator artefact, but a magnitude gap survives:
under the manuscript's own convention the model's E_resp - E_growth is 2 to 2.5 times more
negative than measured, and the gap is driven mainly by the model's respiration activation
energy being too shallow.

K5's claim is testable and cheap, so it is tested rather than repeated. NGAM(T) is scaled
through `provider.ngam_base_scale` -- the anchor that sets maintenance ATP demand at 30 C --
and E_resp, E_growth and their difference are re-measured each time, fitted exactly as TASK 2
fits them (growth on the organism's rising limb, respiration over the full range, same OLS form
on both sides).

NOTHING IS TUNED. The scan reports how far maintenance can move the quantity and at what cost
to the rest of the fit; it does not adopt a value.

Run from the project root, with $CANDIDAS_ROOT readable:

    python3 reports/K6_like_for_like/task3_maintenance_test.py

Writes task3_maintenance_scan.csv beside this file.
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
EXP = "candida_B5_respire"
SCALES = [0.0, 1.0, 2.0, 5.0, 10.0, 20.0]

SPECIES = {
    "cauris_iRV973": dict(group="Clade1", label="C. auris (clade I)"),
    "chaemulonii_draft": dict(group="Hae", label="C. haemulonii"),
    "cduobushaemulonii_draft": dict(group="Duo", label="C. duobushaemulonii"),
    "cparapsilosis_iDC1003": dict(group="para", label="C. parapsilosis"),
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
    boltz = 1.0 / (K_EV * T_REF_K) - 1.0 / (K_EV * TK)
    return float(np.polyfit(boltz, np.log(y[ok]), 1)[0])


def main():
    root = candidas_root()
    if root is None:
        print("[k6] CANDIDAS_ROOT not found")
        return 1
    tab = os.path.join(root, "results", "tables")
    bayes = pd.read_csv(os.path.join(tab, "bayes_clade_params.csv")).set_index("Group")
    bdiff = pd.read_csv(os.path.join(tab, "bayes_E_resp_minus_growth.csv")).set_index("Group")

    rows = []
    for strain, spec in SPECIES.items():
        grp = spec["group"]
        Topt = float(bayes.loc[grp, "growth_Topt_C"])
        m_diff = float(bdiff.loc[grp, "E_resp_minus_growth"])
        lo, hi = float(bdiff.loc[grp, "lo"]), float(bdiff.loc[grp, "hi"])
        base_scale = None
        for sc in SCALES:
            cfg = resolve(strain, EXP)
            if base_scale is None:
                base_scale = float(cfg["provider"].get("ngam_base_scale", 1.0))
            cfg["provider"]["ngam_base_scale"] = base_scale * sc
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
                species=spec["label"], strain=strain, ngam_scale=sc,
                ngam_base_scale=base_scale * sc,
                model_E_growth=Eg, model_E_resp=Er, model_diff=Er - Eg,
                measured_diff=m_diff, measured_lo=lo, measured_hi=hi,
                gap=(Er - Eg) - m_diff,
                within_CI=bool(lo <= (Er - Eg) <= hi),
                peak_mu=float(np.nanmax(mus)),
                peak_T_C=float(TEMPS[int(np.nanargmax(mus))]) if np.isfinite(mus).any() else np.nan))
            print(f"[k6] {spec['label']:22s} NGAM x{sc:5.1f}  E_growth {Eg:6.3f}  "
                  f"E_resp {Er:6.3f}  diff {Er-Eg:7.3f}  (measured {m_diff:6.3f} "
                  f"[{lo:.2f},{hi:.2f}])  peak mu {np.nanmax(mus):.4f} at "
                  f"{TEMPS[int(np.nanargmax(mus))]:.0f} C", flush=True)
    d = pd.DataFrame(rows)
    d.to_csv(os.path.join(HERE, "task3_maintenance_scan.csv"), index=False)
    print("\n[k6] wrote task3_maintenance_scan.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
