#!/usr/bin/env python3
"""ceiling_table.py -- K2 PART C2: the unfolding ceiling across all seven strains.

By how much does the model's unfolding-based upper thermal limit exceed the observed one?
docs/CANDIDA_DISCUSSION_2026-09-07.md section 4 suggests a consistent over-prediction of
+6 to +14 C in E. coli and in Candida, with MEASURED and PREDICTED Tm alike. That is a
statement about the model class, and it is only checkable once the strains share a code
base -- which is what K1 and K2 are for.

The three existing strains are read from their COMMITTED outputs; nothing is re-run for
them, and no number here is recomputed from a model. The Candida strains are read from the
K2 ladder's final rung. The table states what it shows and nothing more.

    python3 reports/candida_thermal_limit/ceiling_table.py [--rung B4]
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
FLOOR = 0.05          # h^-1, the detection floor used throughout this project

# The three existing strains: where the committed predicted CTmax comes from, what the
# observed limit is and where it was measured, and the per-enzyme Tm table.
# The three existing strains, read from their COMMITTED outputs. Each is taken at its
# EMERGENT operating point -- the a-priori model with nothing fitted to the growth curve --
# because that is the like-for-like comparison with the Candida strains from ladder rung B2
# on, which have no fitted parameter either. Where a TUNED value also exists it is carried
# as a second, labelled row rather than substituted.
EXISTING = [
    dict(strain="eciML1515", organism="Escherichia coli K-12 MG1655", kind="emergent",
         pred_file="strains/eciML1515/outputs/calibration_vanderlinden/summary.json",
         pred_path=("descriptors", "emergent_prior", "CTmax_C"),
         pred_topt=("descriptors", "emergent_prior", "Topt_C"),
         pred_source="outputs/calibration_vanderlinden/ descriptors.emergent_prior",
         observed_C=45.945,
         observed_source="Van Derlinden 2012, MG1655 in BHI, assayed 7-46 C "
                         "(descriptors.observed in the same file)",
         tm_file="strains/eciML1515/thermal/BestParamsTopt.csv",
         tm_kind="MEASURED meltome (Leuenberger 2017 / Li-Engqvist)"),
    dict(strain="eciML1515", organism="Escherichia coli K-12 MG1655", kind="tuned",
         pred_file="strains/eciML1515/outputs/calibration_vanderlinden/summary.json",
         pred_path=("descriptors", "posterior_median", "CTmax_C"),
         pred_topt=("descriptors", "posterior_median", "Topt_C"),
         pred_source="outputs/calibration_vanderlinden/ descriptors.posterior_median "
                     "(Bayesian tuning; the posterior pulls Tm down by 5.6 K)",
         observed_C=45.945,
         observed_source="as above",
         tm_file="strains/eciML1515/thermal/BestParamsTopt.csv",
         tm_kind="MEASURED meltome, corrected by the posterior"),
    dict(strain="eciML1515", organism="Escherichia coli K-12 MG1655", kind="nominal",
         pred_file="strains/eciML1515/outputs/tpc/descriptors.json",
         pred_path=("CTmax_C",), pred_topt=("Topt_C",),
         pred_source="outputs/tpc/ (nominal glucose-minimal, strain defaults)",
         observed_C=46.0,
         observed_source="Van Derlinden 2012 (rich BHI; the nominal run is "
                         "glucose-minimal, so this row is not like-for-like)",
         tm_file="strains/eciML1515/thermal/BestParamsTopt.csv",
         tm_kind="MEASURED meltome (Leuenberger 2017 / Li-Engqvist)"),
    dict(strain="mmaripaludis", organism="Methanococcus maripaludis S2", kind="emergent",
         pred_file="strains/mmaripaludis/outputs/M3_thermal/descriptors.json",
         pred_path=("shape", "CTmax_C"), pred_topt=("shape", "Topt_C"),
         pred_source="outputs/M3_thermal/ (M3 emergent thermal layer, shape)",
         observed_C=47.0,
         observed_source="Jones, Paynter & Gupta 1983, growth range 18-47 C",
         tm_file="strains/mmaripaludis/thermal/enzyme_thermal_params.csv",
         tm_kind="PREDICTED (mesophile Topt prior + Tm)"),
    dict(strain="syn6803", organism="Synechocystis sp. PCC 6803", kind="emergent",
         pred_file="strains/syn6803/outputs/P2_thermal/descriptors.json",
         pred_path=("emergent_growth", "CTmax_C"), pred_topt=("emergent_growth", "Topt_C"),
         pred_source="outputs/P2_thermal/ (P2 emergent thermal layer)",
         observed_C=44.0,
         observed_source="Zavrel 2015 (recorded in the same file: zavrel2015.CTmax_C)",
         tm_file="strains/syn6803/thermal/enzyme_thermal_params.csv",
         tm_kind="PREDICTED (mesophile Topt + Tm prior)"),
]
CANDIDA = {"cauris_iRV973": "Candidozyma auris",
           "chaemulonii_draft": "C. haemulonii (DRAFT)",
           "cduobushaemulonii_draft": "C. duobushaemulonii (DRAFT)",
           "cparapsilosis_iDC1003": "Candida parapsilosis"}
RUNG_EXP = {"B0": "outputs/transfer_candida", "B1": "outputs/transfer_candida_B1_unfolding",
            "B2": "outputs/transfer_candida_B2_grounded_budget",
            "B3": "outputs/transfer_candida_B3_ngamT",
            "B4": "outputs/transfer_candida_B4_sectors",
            "B1s": "outputs/transfer_candida_B1s_fit_dTm"}


def _dig(d, path):
    for k in path:
        d = d[k]
    return float(d)


def median_tm_C(path):
    d = pd.read_csv(path)
    col = "Tm" if "Tm" in d.columns else None
    if col is None:
        return float("nan")
    v = pd.to_numeric(d[col], errors="coerce").dropna()
    return float(v.median()) - 273.15 if len(v) else float("nan")


def observed_limit_from_measured(strain):
    """Highest ASSAYED temperature at which the measured curve still reaches the detection
    floor -- the same definition the model's own thermal limit uses. Right-censored where
    the species still grew at the top of the assay range (44 C)."""
    p = f"strains/{strain}/thermal/measured_tpc.csv"
    d = pd.read_csv(p)
    ok = d[d.mu >= FLOOR]
    if not len(ok):
        return float("nan"), False
    hi = float(ok.T_C.max())
    return hi, bool(hi >= float(d.T_C.max()))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--rung", default="B4", choices=sorted(RUNG_EXP))
    a = ap.parse_args(argv)

    rows = []
    for e in EXISTING:
        j = json.load(open(e["pred_file"]))
        pred = _dig(j, e["pred_path"])
        rows.append(dict(
            strain=e["strain"], organism=e["organism"], group="existing",
            config=e["kind"],
            predicted_Topt_C=_dig(j, e["pred_topt"]),
            predicted_CTmax_C=pred, observed_limit_C=e["observed_C"],
            gap_C=pred - e["observed_C"], censored=False,
            median_enzyme_Tm_C=median_tm_C(e["tm_file"]), Tm_kind=e["tm_kind"],
            source=e["pred_source"], observed_source=e["observed_source"]))

    d = RUNG_EXP[a.rung]
    s = pd.read_csv(os.path.join(d, "summary.csv")).set_index("strain")
    for st, org in CANDIDA.items():
        obs, cens = observed_limit_from_measured(st)
        pred = float(s.loc[st, "thermal_limit_C"])
        rows.append(dict(
            strain=st, organism=org, group=f"Candida (K2 rung {a.rung})",
            config=("emergent" if a.rung in ("B2", "B3", "B4") else "fitted globals"),
            predicted_Topt_C=float(s.loc[st, "descr_Topt_C"]),
            predicted_CTmax_C=pred, observed_limit_C=obs, gap_C=pred - obs, censored=cens,
            median_enzyme_Tm_C=median_tm_C(f"strains/{st}/thermal/enzyme_thermal_params.csv"),
            Tm_kind="PREDICTED (Seq2Tm from sequence)",
            source=f"{d}/summary.csv",
            observed_source="thermal/measured_tpc.csv, highest assayed T with mu >= 0.05 /h"))

    T = pd.DataFrame(rows)
    out = os.path.join(HERE, f"ceiling_table_{a.rung}.csv")
    T.to_csv(out, index=False)
    show = ["strain", "config", "predicted_Topt_C", "predicted_CTmax_C",
            "observed_limit_C", "gap_C", "censored", "median_enzyme_Tm_C", "Tm_kind"]
    with pd.option_context("display.width", 250, "display.max_colwidth", 40):
        print(T[show].round(2).to_string(index=False))
    E = T[T.config == "emergent"]
    print(f"\nemergent rows only ({len(E)} strains): median over-prediction "
          f"{E.gap_C.median():+.1f} C, range {E.gap_C.min():+.1f} to {E.gap_C.max():+.1f}")
    print("wrote", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
