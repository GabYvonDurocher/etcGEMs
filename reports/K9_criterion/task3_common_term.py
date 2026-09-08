#!/usr/bin/env python3
"""task3_common_term.py -- K9 TASK 3: does the ~5.6 K common ceiling term generalise?

K8 found E. coli's Bayesian calibration pulls a MEASURED meltome down by 5.6 K to close its
ceiling gap. Measured Tm cannot carry predictor bias, so that is a component separate from the
Candida predictor artefact. Whether it generalises is open, and an earlier version of this claim
was asserted on two data points and turned out to be wrong.

For each of the seven strains this computes the TOTAL ceiling correction -- the uniform Tm shift
that brings predicted CT_max onto the observed limit -- and, where Tm are PREDICTED by Seq2Tm,
decomposes it into A1's measured predictor bias and a residual.

E. COLI IS READ FROM COMMITTED OUTPUTS, never re-run: P4 is active on that strain.

SYNECHOCYSTIS IS TAKEN FROM ITS COMMITTED CURVE, and its correction is NOT computed here.
Rebuilding the phototroph from `resolve("syn6803", "syn6803_ecmodel")` gives CT_max 55.5 C
against the committed 45.7. The committed curve is NOT truncated -- growth falls to 0.2 % of
peak by 50 C and 45.70 is a genuine 5 %-of-rmax crossing -- and applying the light-saturated
autotrophic medium its own script uses does not close the difference either. So the committed
row depends on configuration in `strains/syn6803/run_p2_thermal.py` that a plain strain build
does not reproduce, and reconciling that is outside K9's scope. Its gap is quoted from the
committed table and its total correction is left blank rather than guessed. Recorded as an open
item: a committed ceiling that a strain build does not reproduce is worth knowing about.

Run from the project root:

    python3 reports/K9_criterion/task3_common_term.py

Writes task3_seven_strain.csv beside this file.
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

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
A1_BIAS = 5.43
OFFSETS = np.array([0.0, 2.0, 4.0, 6.0, 9.0, 12.0, 15.0, 18.0])
GRID = np.linspace(20.0, 60.0, 121)

# strain, experiment, kcat_scale, observed limit, Tm provenance
STRAINS = [
    ("cauris_iRV973", "candida_B5_respire", 1.0, 44.0, "PREDICTED (Seq2Tm)"),
    ("chaemulonii_draft", "candida_B5_respire", 1.0, 38.0, "PREDICTED (Seq2Tm)"),
    ("cduobushaemulonii_draft", "candida_B5_respire", 1.0, 38.0, "PREDICTED (Seq2Tm)"),
    ("cparapsilosis_iDC1003", "candida_B5_respire", 1.0, 38.0, "PREDICTED (Seq2Tm)"),
    ("mmaripaludis", None, 7.223, 47.0, "PRIOR (mesophile N(55.6, 7.59), built on E. coli)"),

]
LABEL = {"cauris_iRV973": "C. auris", "chaemulonii_draft": "C. haemulonii",
         "cduobushaemulonii_draft": "C. duobushaemulonii",
         "cparapsilosis_iDC1003": "C. parapsilosis",
         "mmaripaludis": "M. maripaludis", "syn6803": "Synechocystis"}


def main():
    rows = []
    for strain, exp, ks, obs, prov in STRAINS:
        pm = build_provider(resolve(strain, exp))

        tms = np.array([e.Tm - 273.15 for e in pm.ec.table.entries
                        if e.Tm is not None and np.isfinite(e.Tm)])
        cs = []
        for off in OFFSETS:
            g = np.zeros(len(GRID))
            for i, T in enumerate(GRID):
                apply_state(pm.ec, float(T), Perturbation(dTm=-off, kcat_scale=ks))
                v = pm.ec.model.slim_optimize()
                g[i] = 0.0 if (v is None or not np.isfinite(v) or v < 1e-6) else v
            cs.append(TPC(GRID, g).descriptors(0.05).CTmax_C if g.max() > 0 else np.nan)
        cs = np.array(cs)
        ok = np.isfinite(cs)
        if ok.sum() >= 2 and cs[ok].min() <= obs <= cs[ok].max():
            idx = np.argsort(cs[ok])
            total = float(np.interp(obs, cs[ok][idx], OFFSETS[ok][idx]))
        else:
            total = float("nan")
        predictor = A1_BIAS if prov.startswith("PREDICTED") else 0.0
        rows.append(dict(
            strain=strain, species=LABEL[strain], Tm_provenance=prov,
            Tm_median_C=float(np.median(tms)), Tm_sd_C=float(np.std(tms)),
            n_enzymes=len(tms), CTmax_C=float(cs[0]), observed_limit_C=obs,
            gap_C=float(cs[0]) - obs, total_correction_C=total,
            predictor_component_C=predictor,
            residual_C=(total - predictor if np.isfinite(total) else np.nan),
            source="computed here"))
        print(f"[k9] {LABEL[strain]:22s} CTmax {cs[0]:6.2f}  obs {obs:4.1f}  "
              f"gap {cs[0]-obs:+6.2f}  total correction {total:5.2f}  "
              f"predictor {predictor:4.2f}  residual "
              f"{total-predictor if np.isfinite(total) else float('nan'):5.2f}", flush=True)

    # Synechocystis and E. coli: read from the committed ceiling table (see the header)
    ct0 = pd.read_csv(os.path.join(ROOT, "reports", "candida_thermal_limit",
                                   "ceiling_table_B4.csv"))
    sy = ct0[ct0.strain == "syn6803"].iloc[0]
    rows.append(dict(
        strain="syn6803", species="Synechocystis",
        Tm_provenance="PRIOR (mesophile N(55.6, 7.59), built on E. coli's meltome)",
        Tm_median_C=float(sy["median_enzyme_Tm_C"]), Tm_sd_C=np.nan, n_enzymes=np.nan,
        CTmax_C=float(sy["predicted_CTmax_C"]), observed_limit_C=float(sy["observed_limit_C"]),
        gap_C=float(sy["gap_C"]), total_correction_C=np.nan, predictor_component_C=0.0,
        residual_C=np.nan,
        source="committed ceiling_table_B4.csv; correction NOT computed -- a plain strain build "
               "gives CT_max 55.5 against the committed 45.7 and the difference is not the "
               "medium, so run_p2_thermal.py's configuration is not reproduced here"))
    print(f"[k9] {'Synechocystis':22s} CTmax {float(sy['predicted_CTmax_C']):6.2f}  "
          f"obs {float(sy['observed_limit_C']):4.1f}  gap {float(sy['gap_C']):+6.2f}  "
          f"total correction    -- (committed row; rebuild does not reproduce it)")

    # E. coli: read from the committed ceiling table, never re-run (P4 is active there)
    ct = pd.read_csv(os.path.join(ROOT, "reports", "candida_thermal_limit",
                                  "ceiling_table_B4.csv"))
    e = ct[(ct.strain == "eciML1515") & (ct.config == "emergent")].iloc[0]
    rows.append(dict(
        strain="eciML1515", species="E. coli", Tm_provenance="MEASURED meltome",
        Tm_median_C=float(e["median_enzyme_Tm_C"]), Tm_sd_C=np.nan, n_enzymes=np.nan,
        CTmax_C=float(e["predicted_CTmax_C"]), observed_limit_C=float(e["observed_limit_C"]),
        gap_C=float(e["gap_C"]), total_correction_C=5.6, predictor_component_C=0.0,
        residual_C=5.6,
        source="committed ceiling_table_B4.csv; the 5.6 K is the Bayesian posterior's own "
               "Tm correction, recorded in that table's tuned row (gap +5.875 -> -0.012)"))
    print(f"[k9] {'E. coli':22s} CTmax {float(e['predicted_CTmax_C']):6.2f}  "
          f"obs {float(e['observed_limit_C']):4.1f}  gap {float(e['gap_C']):+6.2f}  "
          f"total correction  5.60 (committed, not re-run)  predictor 0.00  residual  5.60")

    d = pd.DataFrame(rows)
    d.to_csv(os.path.join(HERE, "task3_seven_strain.csv"), index=False)
    print("\n=== the residual after removing A1's measured predictor bias ===")
    for _, r in d.iterrows():
        print(f"  {r['species']:22s} {r['Tm_provenance'][:34]:34s} "
              f"total {r['total_correction_C']:5.2f}  - predictor "
              f"{r['predictor_component_C']:4.2f}  = residual {r['residual_C']:5.2f} C")
    res = d["residual_C"].dropna()
    print(f"\n  residuals span {res.min():.2f} to {res.max():.2f} C")
    print("\n[k9] wrote task3_seven_strain.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
