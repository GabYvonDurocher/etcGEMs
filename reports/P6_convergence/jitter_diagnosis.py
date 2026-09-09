#!/usr/bin/env python3
"""P6 TASK 0 -- where does the E/F likelihood jitter come from? (diagnosis only; nothing changed)

preflight.py found repeated evaluations of gasflux_log_likelihood at ONE parameter vector spread
by 0.5-7.5 log-likelihood units for every configuration-E and -F fit, and by <= 0.0004 for every
configuration-D fit. The E/F likelihood removes and re-adds the ETC area constraint on each call.
Four measurements on configuration E, NLDM, at P4's MAP:

  (1) the likelihood as written, 5x                      -> the jitter as sampled by P4 / Parsa
  (2) flux_tpc alone, constraint left untouched, 5x      -> is the LP solution itself unique?
  (3) the same, but the constraint's ub updated IN PLACE instead of remove+add, 5x
      (a monkeypatch inside this script only)            -> is the trigger the remove/add?
  (4) growth and O2 uptake per temperature across the repeats of (1) -> which term jitters

Writes jitter_diagnosis.json beside this file.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, HERE)
os.chdir(ROOT)

from etcgem import etc_area as EA                                                          # noqa: E402
from etcgem.calibration_multi import _build_gasflux_ctx, gasflux_log_likelihood, to_pert   # noqa: E402
from etcgem.gasflux import flux_tpc                                                        # noqa: E402
from p6_fits import FITS, p4_dir_for                                                       # noqa: E402

out = {}
for want in ("E_NLDM", "F_LB"):
    label, cfg, medium, table, otu, c_max, etc, protons, fit_k = [f for f in FITS if f[0] == want][0]
    ctx, specs = _build_gasflux_ctx(strain="eciML1515", medium=medium, experiment=f"gasflux_config{cfg}",
                                    table=table, otu=otu, c_max=c_max, etc_table=etc,
                                    apply_protons=protons, fit_clearance=fit_k)
    d = os.path.join(ROOT, "strains", "eciML1515", "outputs", p4_dir_for(cfg, medium))
    ch = np.load(os.path.join(d, "chain.npy")); lp = np.load(os.path.join(d, "log_prob.npy"))
    i, j = np.unravel_index(np.nanargmax(lp), lp.shape); th = ch[i, j]
    pert = to_pert(th, specs)
    r = {}
    # (1) + (4)
    ll, G, O = [], [], []
    for _ in range(5):
        ll.append(gasflux_log_likelihood(th, ctx, specs))
        df = flux_tpc(ctx["pm"], ctx["T"], pert, metabolites=("o2",))
        G.append(df["growth"].to_numpy(float)); O.append(df["o2_uptake"].to_numpy(float))
    G, O = np.array(G), np.array(O)
    r["as_written_logL"] = ll; r["as_written_spread"] = float(np.ptp(ll))
    r["growth_ptp_per_T"] = np.ptp(G, axis=0).round(5).tolist()
    r["o2_ptp_per_T"] = np.ptp(O, axis=0).round(4).tolist()
    r["o2_mean_per_T"] = O.mean(axis=0).round(3).tolist()
    print(f"[diag] {label} (1) as written: logL {np.round(ll,3)}  spread {np.ptp(ll):.3f}", flush=True)
    print(f"[diag] {label} (4) growth ptp/T max {np.ptp(G,axis=0).max():.2e}; O2 ptp/T max {np.ptp(O,axis=0).max():.3f} of mean {O.mean():.2f}", flush=True)
    # (2) constraint untouched: evaluate flux_tpc alone
    gg, oo = [], []
    for _ in range(5):
        df = flux_tpc(ctx["pm"], ctx["T"], pert, metabolites=("o2",))
        gg.append(df["growth"].to_numpy(float)); oo.append(df["o2_uptake"].to_numpy(float))
    r["untouched_growth_ptp_max"] = float(np.ptp(np.array(gg), axis=0).max())
    r["untouched_o2_ptp_max"] = float(np.ptp(np.array(oo), axis=0).max())
    print(f"[diag] {label} (2) constraint untouched: growth ptp max {r['untouched_growth_ptp_max']:.2e}, O2 ptp max {r['untouched_o2_ptp_max']:.4f}", flush=True)
    # (3) in-place ub update instead of remove+add (monkeypatch, this process only)
    _orig = EA.add_etc_area_constraint
    def _inplace(pm, df, a_etc, name=EA.CONS_NAME):
        m = EA._model(pm)
        if name in m.constraints:
            c = m.constraints[name]; c.ub = float(a_etc); m.solver.update(); c._a_etc = float(a_etc); return c
        return _orig(pm, df, a_etc, name)
    EA.add_etc_area_constraint = _inplace
    ll3 = [gasflux_log_likelihood(th, ctx, specs) for _ in range(5)]
    EA.add_etc_area_constraint = _orig
    r["inplace_logL"] = ll3; r["inplace_spread"] = float(np.ptp(ll3))
    print(f"[diag] {label} (3) in-place ub update: logL {np.round(ll3,3)}  spread {np.ptp(ll3):.3f}", flush=True)
    out[label] = r
json.dump(out, open(os.path.join(HERE, "jitter_diagnosis.json"), "w"), indent=2)
print("[diag] done", flush=True)
