#!/usr/bin/env python3
"""ladder_table.py -- assemble the K2 ladder into one table (rung x species x descriptor).

Each rung of the K2 ladder is a separate `etcgem transfer` experiment applied cumulatively,
changing exactly one component from the rung before it. This reads their committed outputs
and writes the table the K2 report prints. It computes nothing: every number comes from a
run's own summary.csv / counterfactual.csv.

    python3 reports/candida_thermal_limit/ladder_table.py

Writes ladder_table.csv, ladder_counterfactual.csv and ladder_wide.csv beside this file.
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))

# rung -> (experiment, what changed from the rung before it)
RUNGS = [
    ("B0", "transfer_candida",
     "phenomenological form, fitted sigma/w/P, maintenance corrected (K2 PART A)"),
    ("B1", "candida_B1_unfolding",
     "thermal form: phenomenological -> unfolding"),
    ("B2", "candida_B2_grounded_budget",
     "budget: B0's fitted P -> grounded p_total x sigma x f_metab"),
    ("B3", "candida_B3_ngamT",
     "maintenance: constant -> NGAM(T)"),
    ("B4", "candida_B4_sectors",
     "proteome sectors: off -> on"),
]
SENSITIVITIES = [
    ("B1s", "candida_B1s_fit_dTm", "B1 with a uniform dTm free (E. coli's question)"),
    ("B0u", "transfer_candida_unpinned", "B0 without the maintenance correction (K1 gate)"),
]
SHORT = {"cauris_iRV973": "auris", "chaemulonii_draft": "haemulonii",
         "cduobushaemulonii_draft": "duobushaemulonii",
         "cparapsilosis_iDC1003": "parapsilosis"}
# measured thermal limit: the highest assayed temperature at which the species still grew
# (thermal/measured_tpc.csv, dead wells counted as zeros; the assay stops at 44 C, so
# C. auris's is right-censored).
OBSERVED_LIMIT_C = {"auris": 44.0, "haemulonii": 44.0,
                    "duobushaemulonii": 38.0, "parapsilosis": 40.0}

COLS = ["peak_mu", "peak_T_C", "peak_mu_model", "thermal_limit_C", "fit_r2",
        "descr_Topt_C", "descr_rmax", "descr_CTmax_C", "descr_Ea_eV",
        "pool_binds", "pool_binding_ratio", "all_caps_ratio", "median_enzyme_Tm_C"]


def load(tag_exp):
    exp = tag_exp
    d = f"outputs/transfer_{exp}" if not exp.startswith("transfer") else f"outputs/{exp}"
    return d


def main():
    rows, cfs, wide = [], [], []
    for rung, exp, change in RUNGS + SENSITIVITIES:
        d = load(exp)
        f = os.path.join(d, "summary.csv")
        if not os.path.exists(f):
            print(f"  (missing {f}; run `etcgem transfer --experiment {exp}`)", file=sys.stderr)
            continue
        s = pd.read_csv(f)
        import json
        cal = json.load(open(os.path.join(d, "calibration.json")))
        for _, r in s.iterrows():
            row = dict(rung=rung, experiment=exp, change=change,
                       species=SHORT.get(r["strain"], r["strain"]),
                       role=r["role"], growth_scale=cal["scale"],
                       fitted=";".join(f"{k}={v:.6g}" for k, v in cal["fitted"].items()) or "none")
            for c in COLS:
                row[c] = r.get(c)
            row["observed_limit_C"] = OBSERVED_LIMIT_C.get(row["species"], np.nan)
            row["ceiling_gap_C"] = row["thermal_limit_C"] - row["observed_limit_C"]
            rows.append(row)
            wide.append(dict(rung=rung, species=row["species"],
                             **{k: r[k] for k in s.columns if k.startswith("mu_")}))
        c = os.path.join(d, "counterfactual.csv")
        if os.path.exists(c):
            x = pd.read_csv(c)
            x.insert(0, "rung", rung)
            x["species"] = x.strain.map(SHORT)
            cfs.append(x)

    L = pd.DataFrame(rows)
    L.to_csv(os.path.join(HERE, "ladder_table.csv"), index=False)
    pd.DataFrame(wide).to_csv(os.path.join(HERE, "ladder_wide.csv"), index=False)
    C = pd.concat(cfs, ignore_index=True) if cfs else pd.DataFrame()
    if len(C):
        C.to_csv(os.path.join(HERE, "ladder_counterfactual.csv"), index=False)

    show = ["rung", "species", "peak_mu_model", "peak_T_C", "descr_Topt_C", "descr_rmax",
            "descr_CTmax_C", "thermal_limit_C", "fit_r2", "pool_binds",
            "pool_binding_ratio", "all_caps_ratio"]
    with pd.option_context("display.width", 250, "display.max_rows", 200):
        print(L[show].round(4).to_string(index=False))
        print("\ngrowth scale and fitted parameters per rung:")
        print(L.drop_duplicates("rung")[["rung", "change", "fitted", "growth_scale"]]
              .to_string(index=False))
        if len(C):
            print("\nrequired uniform separation to fall below detection at 40 C (C):")
            piv = C.pivot_table(index=["rung"], columns=["param", "species"],
                                values="required", dropna=False)
            print(piv.round(2).to_string())
            print("\nmedian over the three relatives:")
            m = (C.groupby(["rung", "param"])["required"].median().unstack())
            print(m.round(2).to_string())
    print("\nwrote", os.path.join(HERE, "ladder_table.csv"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
