#!/usr/bin/env python3
"""task2_criteria.py -- K9 TASK 2: both criteria as ranges, with their sensitivities.

Each criterion contains arbitrary choices, and a requirement that moves a lot with an arbitrary
threshold is weaker than one that does not. Both are therefore reported as ranges.

  DETECTION CRITERION (what Figure 4 uses). "The uniform downward Tm shift that first puts a
  relative below a detection floor at a fixed temperature." Two arbitrary choices: the floor
  (0.05 h^-1) and the temperature (40 C). Both are swept.

  CEILING CRITERION. "The uniform downward Tm shift that brings predicted CT_max onto the
  observed limit." Its arbitrary choices are the CT_max definition -- the fraction of rmax at
  which the falling limb is called (crit_frac, 0.05 by convention) -- and the temperature grid
  resolution. Both are swept.

TASK 1 established that the ceiling criterion's INTERSPECIES difference is a restatement of the
observed limits. Its PER-SPECIES requirement is still a model statement, and that is what is
reported here.

Run from the project root:

    python3 reports/K9_criterion/task2_criteria.py

Writes task2_detection_sensitivity.csv and task2_ceiling_sensitivity.csv beside this file.
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
from etcgem.transfer import load_measured_tpc, required_separation  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = "candida_B5_respire"
CAL = "cauris_iRV973"
PREDICT = ["chaemulonii_draft", "cduobushaemulonii_draft", "cparapsilosis_iDC1003"]
OBSERVED = {"cauris_iRV973": 44.0, "chaemulonii_draft": 38.0,
            "cduobushaemulonii_draft": 38.0, "cparapsilosis_iDC1003": 38.0}
LABEL = {"cauris_iRV973": "C. auris", "chaemulonii_draft": "C. haemulonii",
         "cduobushaemulonii_draft": "C. duobushaemulonii",
         "cparapsilosis_iDC1003": "C. parapsilosis"}
FLOORS = [0.01, 0.02, 0.05, 0.075, 0.10]
FAIL_TS = [38.0, 39.0, 40.0, 41.0, 42.0]
CRIT_FRACS = [0.01, 0.02, 0.05, 0.10]
GRIDS = {"0.25 C": 241, "0.5 C": 121, "1.0 C": 61}
OFFSETS = np.array([0.0, 3.0, 6.0, 9.0, 12.0, 15.0, 18.0])


def main():
    pms = {s: build_provider(resolve(s, EXP)) for s in [CAL] + PREDICT}
    meas = load_measured_tpc(CAL, resolve(CAL, EXP))
    Ts = meas["T_C"].values.astype(float)
    from etcgem.tpc import compute_tpc
    pred = compute_tpc(pms[CAL], Ts, Perturbation()).growth
    scale = float(meas["mu"].max() / max(pred.max(), 1e-6))

    # ---------------- detection criterion ----------------
    rows = []
    for floor in FLOORS:
        for T in FAIL_TS:
            reqs = []
            for s in PREDICT:
                r = required_separation(pms[s], Perturbation(), scale, "dTm",
                                        T_fail=T, T_perm=34.0, threshold=floor,
                                        perm_frac=0.7, lo=-40.0, tol=0.1)
                v = r.get("required")
                rows.append(dict(floor_h=floor, fail_T_C=T, species=LABEL[s],
                                 required_dTm=v))
                if v is not None:
                    reqs.append(v)
            med = float(np.median(reqs)) if reqs else float("nan")
            rows.append(dict(floor_h=floor, fail_T_C=T, species="MEDIAN",
                             required_dTm=med))
            print(f"[k9] detection  floor {floor:5.3f}  T {T:4.1f}  median required dTm "
                  f"= {med:6.2f} C", flush=True)
    det = pd.DataFrame(rows)
    det.to_csv(os.path.join(HERE, "task2_detection_sensitivity.csv"), index=False)

    # ---------------- ceiling criterion ----------------
    crows = []
    for gname, n in GRIDS.items():
        grid = np.linspace(20.0, 60.0, n)
        for cf in CRIT_FRACS:
            for s in [CAL] + PREDICT:
                cs = []
                for off in OFFSETS:
                    g = np.zeros(len(grid))
                    for i, T in enumerate(grid):
                        apply_state(pms[s].ec, float(T), Perturbation(dTm=-off))
                        v = pms[s].ec.model.slim_optimize()
                        g[i] = 0.0 if (v is None or not np.isfinite(v) or v < 1e-6) else v
                    cs.append(TPC(grid, g).descriptors(cf).CTmax_C if g.max() > 0 else np.nan)
                cs = np.array(cs)
                ok = np.isfinite(cs)
                tgt = OBSERVED[s]
                if ok.sum() >= 2 and cs[ok].min() <= tgt <= cs[ok].max():
                    idx = np.argsort(cs[ok])
                    req = float(np.interp(tgt, cs[ok][idx], OFFSETS[ok][idx]))
                else:
                    req = float("nan")
                crows.append(dict(grid=gname, crit_frac=cf, species=LABEL[s],
                                  CTmax_uncorrected_C=float(cs[0]),
                                  observed_limit_C=tgt, required_offset_C=req))
            print(f"[k9] ceiling  grid {gname}  crit_frac {cf:5.3f}  done", flush=True)
    cei = pd.DataFrame(crows)
    cei.to_csv(os.path.join(HERE, "task2_ceiling_sensitivity.csv"), index=False)

    print("\n=== DETECTION criterion: median required dTm (C) ===")
    print(det[det.species == "MEDIAN"].pivot_table(index="floor_h", columns="fail_T_C",
                                                   values="required_dTm").round(2).to_string())
    m = det[det.species == "MEDIAN"]["required_dTm"]
    print(f"  range across all floor x temperature combinations: "
          f"{m.min():.2f} - {m.max():.2f} C  (spread {m.max()-m.min():.2f})")
    print("\n=== CEILING criterion: required offset (C), C. auris ===")
    x = cei[cei.species == "C. auris"]
    print(x.pivot_table(index="grid", columns="crit_frac",
                        values="required_offset_C").round(2).to_string())
    print("\n  per-species range across grid x crit_frac:")
    for sp in cei.species.unique():
        y = cei[cei.species == sp]["required_offset_C"].dropna()
        print(f"    {sp:22s} {y.min():5.2f} - {y.max():5.2f} C  (spread {y.max()-y.min():.2f})")
    print("\n[k9] wrote task2_detection_sensitivity.csv and task2_ceiling_sensitivity.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
