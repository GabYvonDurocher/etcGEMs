#!/usr/bin/env python3
"""P4 TASK 3 -- what moved, and why.

One table per configuration and medium: the blanket-medium R² P3 gated against the recipe
refit, and the posterior median of every shared parameter. Plus the two questions the prompt
singles out -- is the medium clearance K identified, and do the RQ figures in circulation agree.

    python reports/P4_refit/compare.py
"""
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, HERE)
os.chdir(ROOT)

from fits import FITS, out_dir_for                                        # noqa: E402

# What P3 gated, against the blanket medium and his own chains.
P3 = {("D", "NLDM"): dict(growth=0.7066, resp=0.7246, point="posterior median"),
      ("D", "LB"):   dict(growth=0.8964, resp=0.7931, point="MAP"),
      ("E", "NLDM"): dict(growth=0.8492, resp=0.7214, point="MAP"),
      ("E", "LB"):   dict(growth=0.8284, resp=0.8014, point="MAP"),
      ("F", "NLDM"): dict(growth=0.9051, resp=0.9636, point="MAP"),
      ("F", "LB"):   dict(growth=0.8809, resp=0.8524, point="MAP")}
HIS = {("D", "NLDM"): (0.71, None), ("D", "LB"): (0.90, None),
       ("E", "NLDM"): (0.85, 0.72), ("E", "LB"): (0.83, 0.81),
       ("F", "NLDM"): (0.91, 0.96), ("F", "LB"): (0.88, 0.85)}

rows, params, k_rows = [], [], []
for label, cfg, medium, table, otu, c_max, etc, protons, fit_k in FITS:
    d = os.path.join("strains", "eciML1515", "outputs", out_dir_for(label, cfg, medium))
    sj, cj = os.path.join(d, "summary.json"), os.path.join(d, "scores.json")
    if not (os.path.exists(sj) and os.path.exists(cj)):
        rows.append({"fit": label, "status": "NOT RUN"})
        continue
    summ, sc = json.load(open(sj)), json.load(open(cj))
    point = P3.get((cfg, medium), {}).get("point", "MAP")
    s = sc[point]
    conv = summ["sampler"]["converged"]
    row = {"fit": label, "config": cfg, "medium": medium, "point": point,
           "converged": conv,
           "steps": summ["sampler"]["n_steps"], "accept": summ["sampler"]["acceptance_fraction"],
           "tau": summ["sampler"]["autocorr_time_max"], "n_eff": summ["sampler"]["n_eff"],
           "wall_min": round(summ["sampler"]["wall_time_s"] / 60, 1),
           "growth_R2_refit": round(s["growth_R2"], 4),
           "resp_R2_refit": round(s["resp_R2"], 4),
           "rmax": round(s["rmax"], 4), "Topt_C": s["Topt_C"],
           "acetate_37C": round(s["acetate_37C"], 4), "RQ_37C": round(s["RQ_37C"], 4),
           "resp_scale": round(s["resp_scale"], 3)}
    if (cfg, medium) in P3:
        row["growth_R2_blanket"] = P3[(cfg, medium)]["growth"]
        row["resp_R2_blanket"] = P3[(cfg, medium)]["resp"]
        row["d_growth"] = round(s["growth_R2"] - P3[(cfg, medium)]["growth"], 4)
        row["d_resp"] = round(s["resp_R2"] - P3[(cfg, medium)]["resp"], 4)
        row["his_growth"], row["his_resp"] = HIS[(cfg, medium)]
    rows.append(row)
    for name, p in summ["posterior"].items():
        params.append({"fit": label, "param": name, "median": p["posterior_median"],
                       "ci90_lo": p["ci90"][0], "ci90_hi": p["ci90"][1],
                       "width_ratio_vs_prior": p["width_ratio_vs_prior"]})
        if name == "clearance_mult":
            k_rows.append({"fit": label,
                           "K_median": 5.0 * p["posterior_median"],
                           "K_ci90": [5.0 * p["ci90"][0], 5.0 * p["ci90"][1]],
                           "width_ratio_vs_prior": p["width_ratio_vs_prior"],
                           "identified": p["width_ratio_vs_prior"] < 0.5})

t = pd.DataFrame(rows)
t.to_csv(os.path.join(HERE, "refit_comparison.csv"), index=False)
pd.DataFrame(params).to_csv(os.path.join(HERE, "refit_posteriors.csv"), index=False)
with pd.option_context("display.width", 250, "display.max_columns", 30):
    print(t.to_string(index=False))
print("\n--- the medium clearance K: identified, or a prior choice? ---")
if k_rows:
    for r in k_rows:
        print(f"  {r['fit']:8s} K = {r['K_median']:.2f} L/gDW/h  90% CI "
              f"[{r['K_ci90'][0]:.2f}, {r['K_ci90'][1]:.2f}]  "
              f"posterior/prior width = {r['width_ratio_vs_prior']:.2f}  -> "
              f"{'IDENTIFIED' if r['identified'] else 'NOT identified: the ceiling is a PRIOR CHOICE'}")
else:
    print("  (no fit sampled the clearance)")
