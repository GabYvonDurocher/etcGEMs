#!/usr/bin/env python3
"""task1_correlations.py -- Y3 TASK 1: what P12's converged endpoints already say about whether
dTm is traded against the catalytic parameters.

    python3 reports/Y3_tm_shift/task1_correlations.py

Two steps and no fitting.

1. WHICH ENDPOINTS ARE LIVE. P12 TASK 3 computed peak predicted growth per BASIN, at its best
   endpoint, so the prompt's exclusion -- "any point whose peak predicted growth is below half the
   observed 2.076" -- cannot be read off a committed file for the other ten. It is computed here
   with P12's own `common.decompose`, twelve temperatures per endpoint.

2. THE CORRELATIONS. Pearson, Spearman and PARTIAL correlation of dTm with each of dCp_scale,
   kcat_scale, dTopt, topt_scale and tm_scale, the partial controlling for the other four. Partial
   correlation is computed from the inverse of the correlation matrix over those six columns:
   r_ij.rest = -P_ij / sqrt(P_ii P_jj). With n around ten that matrix is barely invertible, so the
   condition number is reported beside the numbers and the report says what they do not support.

Writes task1_endpoints.csv, task1_corr.csv, task1_partial.csv and task1_meta.json.
"""
from __future__ import annotations

import json
import os
import sys
import time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "reports", "P12_modes"))

OBS_PEAK = 2.076          # the observed peak growth, from the prompt
LIVE_FRAC = 0.5           # "below half the observed" is dead, per the prompt
CATALYTIC = ["dCp_scale", "kcat_scale", "dTopt", "topt_scale", "tm_scale"]


def partial_matrix(df):
    """Partial correlations from the precision matrix; NaN if it is not invertible."""
    C = np.corrcoef(df.to_numpy(float).T)
    cond = float(np.linalg.cond(C))
    try:
        P = np.linalg.inv(C)
    except np.linalg.LinAlgError:
        return pd.DataFrame(np.nan, index=df.columns, columns=df.columns), cond
    d = np.sqrt(np.diag(P))
    R = -P / np.outer(d, d)
    np.fill_diagonal(R, 1.0)
    return pd.DataFrame(R, index=df.columns, columns=df.columns), cond


def main():
    import common                                                   # noqa: E402
    from scipy.stats import spearmanr                               # noqa: E402

    src = os.path.join(ROOT, "reports", "P12_modes", "task2c_converged.csv")
    d = pd.read_csv(src)
    cols = {c: c[2:] for c in d.columns if c.startswith("x_")}
    d = d.rename(columns=cols)
    names = list(cols.values())
    print(f"[y3t1] {len(d)} endpoints, {len(names)} parameters, from {os.path.relpath(src, ROOT)}",
          flush=True)

    ctx, sp = common.build()          # build() returns (ctx, specs), as P12's own scripts use it
    t0 = time.time()
    peaks, rows = [], []
    for _, r in d.iterrows():
        th = np.array([float(r[n]) for n in common.NAMES], float)
        dec = common.decompose(th, ctx, sp)
        g = np.asarray(dec["growth"], float)
        peaks.append(float(np.nanmax(g)))
        rows.append(dict(key=r["key"], logl=float(r["logl"]), logpost=float(r["logpost"]),
                         peak_growth=peaks[-1], dTm=float(r["dTm"]),
                         **{n: float(r[n]) for n in CATALYTIC}))
        print(f"[y3t1] {r['key']:16s} logl {float(r['logl']):9.3f}  dTm {float(r['dTm']):8.3f} K  "
              f"peak growth {peaks[-1]:7.4f} /h  "
              f"{'LIVE' if peaks[-1] >= LIVE_FRAC * OBS_PEAK else 'dead'}", flush=True)
    d["peak_growth"] = peaks
    d["live"] = d.peak_growth >= LIVE_FRAC * OBS_PEAK
    e = pd.DataFrame(rows)
    e["live"] = d.live.to_numpy()
    e.to_csv(os.path.join(HERE, "task1_endpoints.csv"), index=False)
    print(f"[y3t1] live threshold {LIVE_FRAC*OBS_PEAK:.3f} /h ; "
          f"{int(d.live.sum())} live, {int((~d.live).sum())} excluded "
          f"({', '.join(d.loc[~d.live, 'key'])})  [{time.time()-t0:.0f}s]", flush=True)

    live = d[d.live]
    sub = live[["dTm"] + CATALYTIC]
    pear = sub.corr(method="pearson")
    spear = pd.DataFrame(spearmanr(sub.to_numpy(float)).statistic,
                         index=sub.columns, columns=sub.columns)
    part, cond = partial_matrix(sub)
    pear.to_csv(os.path.join(HERE, "task1_corr.csv"))
    part.to_csv(os.path.join(HERE, "task1_partial.csv"))

    print(f"\n[y3t1] dTm against the catalytic parameters, over {len(live)} live endpoints:")
    print(f"{'parameter':12s} {'Pearson':>9s} {'Spearman':>9s} {'partial':>9s}")
    out = {}
    for c in CATALYTIC:
        out[c] = dict(pearson=float(pear.loc["dTm", c]), spearman=float(spear.loc["dTm", c]),
                      partial=float(part.loc["dTm", c]))
        print(f"{c:12s} {out[c]['pearson']:9.3f} {out[c]['spearman']:9.3f} "
              f"{out[c]['partial']:9.3f}")
    print(f"[y3t1] correlation-matrix condition number {cond:.1f} on n={len(live)}")

    q = live[["dTm", "logl"]].corr().loc["dTm", "logl"]
    qs = float(spearmanr(live.dTm.to_numpy(float), live.logl.to_numpy(float)).statistic)
    print(f"[y3t1] dTm vs log L over live endpoints: Pearson {q:.3f}, Spearman {qs:.3f}  "
          f"(dTm range {live.dTm.min():.3f} to {live.dTm.max():.3f} K, "
          f"log L {live.logl.min():.3f} to {live.logl.max():.3f})", flush=True)

    # the whole matrix over all sixteen, for the record
    allp = live[common.NAMES].corr()
    allp.to_csv(os.path.join(HERE, "task1_corr_all16.csv"))

    json.dump(dict(n_endpoints=int(len(d)), n_live=int(d.live.sum()),
                   excluded=list(d.loc[~d.live, "key"]),
                   live_threshold=LIVE_FRAC * OBS_PEAK, obs_peak=OBS_PEAK,
                   dTm_vs=out, corr_condition_number=cond,
                   dTm_vs_logl=dict(pearson=float(q), spearman=qs),
                   dTm_min=float(live.dTm.min()), dTm_max=float(live.dTm.max()),
                   wall_s=time.time() - t0),
              open(os.path.join(HERE, "task1_meta.json"), "w"), indent=2)
    print("[y3t1] wrote task1_endpoints.csv, task1_corr.csv, task1_partial.csv, "
          "task1_corr_all16.csv, task1_meta.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
