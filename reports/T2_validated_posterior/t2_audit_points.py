#!/usr/bin/env python3
"""T2 -- T1's 876 registered audit points, built EXACTLY as reports/T1_target_revision/task2_classify.py
builds them (16-D old-target theta), with T1's class per label and T1's old log L where T1 recorded one."""
import os, sys, json, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
ARCH = os.path.abspath(os.path.join(ROOT, "..", "etcGEMs-p17-archive"))
for p in (os.path.join(ROOT, "src"), os.path.join(ROOT, "reports", "P6_convergence"), os.path.join(ROOT, "reports", "P11_nested"),
          os.path.join(ROOT, "reports", "P16_reduced"), HERE):
    if p not in sys.path: sys.path.insert(0, p)
from prior_transform import transform_factory        # noqa: E402  (P11's, for the 15-D cube points)
from reduced import FULL_SPECS, FREE_SPECS, expand    # noqa: E402  (P16's 16-D old target incl. f_metab)
OLD_NAMES = [s.name for s in FULL_SPECS]; F_METAB_IDX = OLD_NAMES.index("f_metab")
T1 = os.path.join(ROOT, "reports", "T1_target_revision")


def points():
    pt15 = transform_factory(FREE_SPECS); pts = []
    for e in json.load(open(os.path.join(ROOT, "reports/P17_inactive_prior/real_curvature_probe/evaluations.json"))):
        pts.append(("D44:" + e["label"], expand(pt15(np.asarray(e["u"], float)))))
    for st in json.load(open(os.path.join(ROOT, "reports/P17_inactive_prior/stratum_probe.json"))):
        pts.append((f"stratum:{st['tag']}:{st['stored_index']}", expand(pt15(np.asarray(st["start"], float)))))
    z = np.load(os.path.join(ARCH, "reports/P17_inactive_prior/validated_live_input.npz"))
    for i in range(z["theta"].shape[0]):
        pts.append((f"red2_6800:{i}", expand(np.asarray(z["theta"][i], float))))
    d = pd.read_csv(os.path.join(ROOT, "reports/P12_modes/task2c_converged.csv"))
    for _, r in d.iterrows():
        pts.append(("P12:" + r.key, r[[f"x_{n}" for n in OLD_NAMES]].to_numpy(float)))
    return pts


def drop_f_metab(th16):
    """old 16-D theta -> the revised target's 15-D full theta (f_metab removed; order otherwise identical)."""
    return np.delete(np.asarray(th16, float), F_METAB_IDX)


def t1_classes():
    """label -> (n_structural_zero, n_unresolved) from T1's audited merge (rows in file order; stratum labels repeat)."""
    d = pd.read_csv(os.path.join(T1, "task2_classify_all.csv"))
    return d


def t1_old_logl():
    """label -> T1's old log L: task1_invariant.csv `old` (870) + the six stratum totals from task2_datum_totals.csv."""
    inv = pd.read_csv(os.path.join(T1, "task1_invariant.csv")); out = dict(zip(inv.label, inv.old))
    tot = pd.read_csv(os.path.join(T1, "task2_datum_totals.csv"))
    strat = tot[tot.point.str.startswith("stratum")]
    return out, list(zip(strat.point, strat.logl_code))
