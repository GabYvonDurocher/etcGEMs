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
            # Is the "peak" a peak or a plateau? A temperature-INDEPENDENT constraint (the
            # sector translation cap, from B4 on) flattens the top of the curve, and then
            # Topt is the first index of a tie rather than an optimum -- which is also why
            # the two solvers disagree about it there. Measured on the wide grid as the
            # width of the region within 0.01% of the peak.
            plateau_lo = plateau_hi = float("nan")
            w = os.path.join("strains", r["strain"], "outputs",
                             ("transfer_" + exp) if not exp.startswith("transfer") else exp,
                             "tpc_wide.csv")
            if os.path.exists(w):
                tw = pd.read_csv(w)
                m = float(tw.growth.max())
                if m > 0:
                    flat = tw[tw.growth >= m * 0.9999]
                    plateau_lo, plateau_hi = float(flat.temp_C.min()), float(flat.temp_C.max())
            row = dict(rung=rung, experiment=exp, change=change,
                       species=SHORT.get(r["strain"], r["strain"]),
                       role=r["role"], growth_scale=cal["scale"],
                       fitted=";".join(f"{k}={v:.6g}" for k, v in cal["fitted"].items()) or "none")
            for c in COLS:
                row[c] = r.get(c)
            row["plateau_lo_C"] = plateau_lo
            row["plateau_hi_C"] = plateau_hi
            row["plateau_width_C"] = plateau_hi - plateau_lo
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
        # K2 PART C1. The separation the MODEL requires, against the separation that
        # actually exists. Two references, both from outside this model:
        #   0.52 C  the sequence-predicted paired ortholog dTm, C. auris minus
        #           C. haemulonii (95% CI 0.37-0.67), gem/24_paired_dedup_audit.py.
        #   1.6 C   MEASURED proteome-wide dTm between S. cerevisiae and S. uvarum, 827
        #           protein pairs, for an 8 C difference in growth limit (Walunjkar et al.
        #           2025, Mol Biol Evol 42:msaf137). The most generous real number available.
        C["fold_gap_vs_predicted_0.52C"] = C["required"] / 0.52
        C["fold_gap_vs_measured_1.6C"] = C["required"] / 1.6
        C.to_csv(os.path.join(HERE, "ladder_counterfactual.csv"), index=False)

    show = ["rung", "species", "peak_mu_model", "descr_Topt_C", "plateau_lo_C",
            "plateau_hi_C", "plateau_width_C", "descr_CTmax_C", "thermal_limit_C",
            "fit_r2", "pool_binds", "pool_binding_ratio", "all_caps_ratio"]
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
            print("\nPART C1 -- required separation and the fold gap, median over the "
                  "three relatives:")
            g = (C.groupby(["rung", "param"])[
                     ["required", "fold_gap_vs_predicted_0.52C", "fold_gap_vs_measured_1.6C"]]
                 .median().reset_index())
            g.columns = ["rung", "param", "required_C", "x vs predicted 0.52 C",
                         "x vs measured 1.6 C"]
            print(g.round(1).to_string(index=False))
    print("\nwrote", os.path.join(HERE, "ladder_table.csv"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
