#!/usr/bin/env python3
"""task4_required_separation.py -- K5 TASK 4: recompute Figure 4's required interspecies Tm
separation on a model that respires, with and without a carbon budget.

WHY IT MIGHT MOVE. K2's 13.8 C was computed on a model with at least two escape routes: free
protons, and fermentation. K4 put it plainly -- "no budget, including zero, puts any relative
below detection, because the models can ferment". A model with fewer escape routes should be
easier to kill, so the requirement may FALL. If it does not, that is worth knowing too.

WHAT IS COMPUTED. Exactly K2's counterfactual, via the same function the transfer command uses
(transfer.required_separation): the uniform downward shift of every enzyme's Tm, applied to ONE
predicted strain, that first puts it below the 0.05 h^-1 detection floor at 40 C, with its
permissive-temperature growth checked afterwards. Reported as the median over the three
relatives, as K2 reports it.

Run from the project root:

    python3 reports/K5_respire/task4_required_separation.py

Writes task4_required_separation.csv beside this file.
"""
from __future__ import annotations

import logging
import os
import sys

import numpy as np
import pandas as pd

logging.getLogger("cobra").setLevel(logging.ERROR)
sys.path.insert(0, "src")

from etcgem.config import build_provider, resolve                          # noqa: E402
from etcgem.gasflux import (add_total_carbon_constraint,                   # noqa: E402
                            remove_total_carbon_constraint)
from etcgem.transfer import (load_measured_tpc, required_separation)       # noqa: E402
from etcgem.enzyme_cost import Perturbation                                # noqa: E402
from etcgem.tpc import compute_tpc                                         # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
CALIBRATE_ON = "cauris_iRV973"
PREDICT = ["chaemulonii_draft", "cduobushaemulonii_draft", "cparapsilosis_iDC1003"]
FLOOR, FAIL_T, PERM_T, PERM_FRAC = 0.05, 40.0, 34.0, 0.7

# label -> (experiment, carbon cap or None)
RUNS = {
    "B3 before repair, no cap (K2's condition)": ("candida_B3_ngamT", None),
    "B5 repaired, no cap": ("candida_B5_respire", None),
    "B5 repaired + carbon cap 12": ("candida_B5_respire", 12.0),
    "B3 before repair + carbon cap 12": ("candida_B3_ngamT", 12.0),
}


def main():
    rows = []
    for label, (exp, c_max) in RUNS.items():
        pms = {}
        for s in [CALIBRATE_ON] + PREDICT:
            pms[s] = build_provider(resolve(s, exp))
            if c_max is not None:
                add_total_carbon_constraint(pms[s], c_max)
        meas = load_measured_tpc(CALIBRATE_ON, resolve(CALIBRATE_ON, exp))
        Ts = meas["T_C"].values.astype(float)
        mu = meas["mu"].values.astype(float)
        pred = compute_tpc(pms[CALIBRATE_ON], Ts, Perturbation()).growth
        scale = float(mu.max() / max(pred.max(), 1e-6))
        reqs = []
        for s in PREDICT:
            r = required_separation(pms[s], Perturbation(), scale, "dTm",
                                    T_fail=FAIL_T, T_perm=PERM_T, threshold=FLOOR,
                                    perm_frac=PERM_FRAC, lo=-35.0, tol=0.1)
            r.update(config=label, experiment=exp, c_max=c_max, strain=s,
                     growth_scale=scale)
            rows.append(r)
            if r.get("required") is not None:
                reqs.append(r["required"])
            print(f"[k5] {label:42s} {s:24s} required dTm = "
                  f"{r.get('required')} C  (permissive preserved="
                  f"{r.get('permissive_preserved')})", flush=True)
        med = float(np.median(reqs)) if reqs else float("nan")
        print(f"[k5] {label:42s} MEDIAN over the three relatives = {med:.2f} C\n", flush=True)
        rows.append(dict(config=label, experiment=exp, c_max=c_max, strain="MEDIAN",
                         required=med, growth_scale=scale))
    pd.DataFrame(rows).to_csv(os.path.join(HERE, "task4_required_separation.csv"), index=False)
    print("[k5] wrote task4_required_separation.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
