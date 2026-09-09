#!/usr/bin/env python3
"""P5 TASK 1a -- what c_max did Parsa's own LB fits actually use? Read at source.

Reads his committed chains under $PARSA_ROOT (READ ONLY): meta.json for the parameter list
and cfg, chain.h5 for the MAP and posterior-median point. c_max on LB is his fitted
multiplier `C_max_LB_mult` times his nominal cap (CAP_NOM 230 for configuration D, CAP_NOM_E
450 for E and F -- both from his calibration_configD_full.py), or, where he pinned it,
cfg.cmax_fixed.LB. Nothing is sampled; a chain is read.

Writes parsa_lb_cmax.csv beside this file.
"""
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "reports", "P3_gate"))
from gate_def import read_points                       # noqa: E402  (import-safe: main guard)

PARSA = os.environ.get("PARSA_ROOT", "/Users/g.yvon-durocher/Downloads/etcGEMs-main_3")
OUT = os.path.join(PARSA, "strains", "eciML1515", "outputs")
CAP_NOM, CAP_NOM_E = 230.0, 450.0      # his calibration_configD_full.py lines 38 and 42

# every LB directory he committed, gated or not
RUNS = [("D", "calibration_configD_LB_full",        "gated: his D LB 0.90 (P3)"),
        ("D", "calibration_configD_LB_growthonly",  "no cap; growth only"),
        ("E", "calibration_configE_LB_freecmax",    "gated: his E LB 0.83 / 0.81 (P3)"),
        ("E", "calibration_configE_LB",             "c_max pinned at 459 (from freecmax)"),
        ("F", "calibration_configF_LB",             "gated: his F LB 0.88 / 0.85 (P3)"),
        ("F", "calibration_configF_LB_combined",    "not gated")]

rows = []
for cfg_name, run, note in RUNS:
    d = os.path.join(OUT, run)
    meta = json.load(open(os.path.join(d, "meta.json")))
    cfg = meta.get("cfg") or {}
    names = meta["param_names"]
    th_map, th_med, it, walkers = read_points(d)
    # C_max_LB_mult is sampled in log space in every one of his fits (his build_specs_full:
    # PSpec(..., "log", "lognormal", 0.40, ...)); natural value = exp(theta). Located by name
    # in his own param_names so the growth-only run (no respiration terms) reads too.
    def mult_of(theta):
        return float(np.exp(theta[names.index("C_max_LB_mult")])) if "C_max_LB_mult" in names else None
    nat_map, nat_med = {"C_max_LB_mult": mult_of(th_map)}, {"C_max_LB_mult": mult_of(th_med)}
    nom = CAP_NOM_E if cfg.get("use_etc") else CAP_NOM
    fixed = (cfg.get("cmax_fixed") or {}).get("LB")
    if "C_max_LB_mult" in names:
        c_map, c_med = nom * nat_map["C_max_LB_mult"], nom * nat_med["C_max_LB_mult"]
        how = f"fitted: {nom:g} x C_max_LB_mult"
    elif fixed is not None:
        c_map = c_med = float(fixed); how = "pinned: cfg.cmax_fixed.LB"
    else:
        c_map = c_med = float("nan"); how = "no cap (use_cap=%s)" % cfg.get("use_cap")
    rows.append(dict(config=cfg_name, run=run, use_cap=cfg.get("use_cap"), use_etc=cfg.get("use_etc"),
                     nominal=nom if "C_max_LB_mult" in names else "", how=how,
                     mult_MAP=nat_map["C_max_LB_mult"] or "", mult_median=nat_med["C_max_LB_mult"] or "",
                     c_max_MAP=round(c_map, 1), c_max_median=round(c_med, 1),
                     chain_iterations=it, walkers=walkers, meta_n_steps=meta.get("n_steps"), note=note))
df = pd.DataFrame(rows)
df.to_csv(os.path.join(HERE, "parsa_lb_cmax.csv"), index=False)
pd.set_option("display.width", 200)
print(df[["config", "run", "how", "mult_MAP", "c_max_MAP", "c_max_median", "chain_iterations", "note"]].to_string(index=False))
