#!/usr/bin/env python3
"""task1_convention.py -- K7 TASK 1: which growth convention does Figure 4's requirement use,
and how much does the answer depend on it?

THE TRACE, followed through the code to the file on disk rather than inferred:

  transfer.run()
    line 324   measured = load_measured_tpc(cal, cfgs[cal])          <- cal = cauris_iRV973
    line 344   pred_cal = _growth(pms[cal], measured["T_C"], pert)
    line 345   scale    = _scale(pred_cal, measured["mu"], "peak_match")
                          = measured.mu.MAX() / predicted.MAX()      <- only the PEAK is used
    then       required_separation(pms[s], pert, scale, "dTm", T_fail=40, threshold=0.05)

  transfer.required_separation()
    mu_at(T, d) = model_growth(T, d) * scale ; compared against `threshold`
    -- it makes ZERO calls to load_measured_tpc. The PREDICTED strain's own measured curve
       never enters the counterfactual at all.

  load_measured_tpc -> strain.yaml `measured.tpc` -> strains/<name>/thermal/measured_tpc.csv,
  whose provenance block names gem/17_build_measured_tpc.py, i.e. the ZEROS convention
  (a dead well is an observed zero).

  The CALIBRATION target is the same call on the same file (line 324). For experiments with
  free globals the whole curve enters the loss at line 152; from K2 rung B2 on, `globals: []`,
  so nothing is fitted and only the scale survives.

So calibration and counterfactual read the SAME file -- the model is not fitted to one curve
and falsified against another -- and the counterfactual's ONLY measured input is the peak of
the C. auris curve, at 36 C, where C. auris is fully alive under either convention.

This script quantifies that: it rebuilds the C. auris curve under the survivors convention
from the derived table, and recomputes the required interspecies Tm separation under both.

Run from the project root, with $CANDIDAS_ROOT readable:

    python3 reports/K7_envelope/task1_convention.py

Writes task1_conventions.csv and task1_auris_curves.csv beside this file.
"""
from __future__ import annotations

import logging
import os
import sys

import numpy as np
import pandas as pd

logging.getLogger("cobra").setLevel(logging.ERROR)
sys.path.insert(0, "src")

from etcgem.config import build_provider, resolve                  # noqa: E402
from etcgem.enzyme_cost import Perturbation                        # noqa: E402
from etcgem.tpc import compute_tpc                                 # noqa: E402
from etcgem.transfer import load_measured_tpc, required_separation  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
CAL = "cauris_iRV973"
PREDICT = ["chaemulonii_draft", "cduobushaemulonii_draft", "cparapsilosis_iDC1003"]
AURIS_CLADE1 = [1, 2, 3]
FLOOR, FAIL_T, PERM_T, PERM_FRAC = 0.05, 40.0, 34.0, 0.7
RUNS = {"B3 (before the K5 repair)": "candida_B3_ngamT",
        "B5 (repaired)": "candida_B5_respire"}


def candidas_root():
    r = os.environ.get("CANDIDAS_ROOT")
    if r and os.path.isdir(r):
        return r
    g = os.path.abspath(os.path.join(HERE, "..", "..", "..", "Candidas TPC", "Candidas"))
    return g if os.path.isdir(g) else None


def main():
    root = candidas_root()
    if root is None:
        print("[k7] CANDIDAS_ROOT not found")
        return 1
    der = pd.read_csv(os.path.join(root, "results", "tables",
                                   "derived_N0_R_results_with_carbon.csv"))
    der = der[(der.keep) & (der.fit_valid) & der.OTU.isin(AURIS_CLADE1)]

    # convention A: what the repository uses -- dead wells are observed zeros, median
    zeros = load_measured_tpc(CAL, resolve(CAL, "candida_B3_ngamT")).set_index("T_C")["mu"]
    # convention B: survivors only, the table every activation-energy fit uses.
    # `r` is per MINUTE there (it is 1/59.5 of the zeros curve wherever both are non-zero),
    # so it is converted to per hour, and the median is taken as 17_build_measured_tpc does.
    surv = (der.groupby("T")["r"].median() * 60.0).rename("mu")

    curves = pd.DataFrame({"zeros_convention": zeros, "survivors_convention": surv})
    curves.to_csv(os.path.join(HERE, "task1_auris_curves.csv"))
    print("=== C. auris (clade I) measured growth, the two conventions (h^-1) ===")
    print(curves.round(4).to_string())
    print(f"\n  peak, zeros convention      {zeros.max():.4f} /h at {zeros.idxmax():.0f} C")
    print(f"  peak, survivors convention  {surv.max():.4f} /h at {surv.idxmax():.0f} C")
    print(f"  ratio of peaks              {surv.max()/zeros.max():.4f}")

    rows = []
    for label, exp in RUNS.items():
        pms = {s: build_provider(resolve(s, exp)) for s in [CAL] + PREDICT}
        Ts = zeros.index.values.astype(float)
        pred = compute_tpc(pms[CAL], Ts, Perturbation()).growth
        for conv, meas in (("zeros (as the repository does it)", zeros),
                           ("survivors", surv)):
            scale = float(meas.max() / max(pred.max(), 1e-6))
            reqs = []
            for s in PREDICT:
                r = required_separation(pms[s], Perturbation(), scale, "dTm",
                                        T_fail=FAIL_T, T_perm=PERM_T, threshold=FLOOR,
                                        perm_frac=PERM_FRAC, lo=-35.0, tol=0.1)
                rows.append(dict(config=label, experiment=exp, convention=conv,
                                 growth_scale=scale, strain=s,
                                 required_dTm=r.get("required"),
                                 permissive_preserved=r.get("permissive_preserved")))
                if r.get("required") is not None:
                    reqs.append(r["required"])
            med = float(np.median(reqs)) if reqs else float("nan")
            rows.append(dict(config=label, experiment=exp, convention=conv,
                             growth_scale=scale, strain="MEDIAN", required_dTm=med))
            print(f"[k7] {label:26s} {conv:34s} scale {scale:7.4f}  "
                  f"median required dTm = {med:6.2f} C", flush=True)

    pd.DataFrame(rows).to_csv(os.path.join(HERE, "task1_conventions.csv"), index=False)
    print("\n[k7] wrote task1_conventions.csv and task1_auris_curves.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
