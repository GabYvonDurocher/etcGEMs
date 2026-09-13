#!/usr/bin/env python3
"""task1_residuals.py -- Q1 TASK 1: does the respiration residual trend with growth rate at fixed
temperature, or only with temperature?

    python3 reports/Q1_n0_check/task1_residuals.py

Arithmetic on committed tables only; no solves.

THE QUESTION. If a constant carbon-per-cell / N0 conversion is imprinting itself on the
temperature dependence of per-cell respiration, the residual between measured and modelled O2
should track GROWTH RATE. But growth rate and temperature are strongly correlated along a TPC, so
a residual trending with growth rate could equally be the model failing with temperature.

THE SEPARATION. The two media grow at DIFFERENT RATES AT THE SAME TEMPERATURE. So at each shared
temperature, ask whether the difference in residual between media is predicted by the difference
in their growth rates. Temperature is held exactly; only growth rate varies. That is the decisive
test and it is `paired_media` below -- the marginal regressions are reported first because they
are what a reader expects, and they cannot separate the two on their own.

REPLICATES. The model comparison uses the replicate MEAN per (medium, temperature) --
`gate_def.load_obs` does `groupby("T")[col].mean()` -- so the residual is formed on the same
means, one point per (medium, temperature). The per-replicate spread is reported beside it as
`sd` and `n` so the weight behind each point is visible, but it is not used to weight the fits:
the likelihood does not weight them either.

Writes task1_residuals.csv, task1_regressions.csv, task1_paired_media.csv and task1_meta.json.
"""
from __future__ import annotations

import json
import os

import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
RESP = os.path.join(ROOT, "strains", "eciML1515", "respirometry")
DECK = os.path.join(ROOT, "reports", "ecoli_deck")
OTU = {"NLDM": 1, "LB": 2}          # gate_def.OTU: R2A -> the model's NLDM, LB -> LB


def measured():
    """Replicate mean, sd and n per (medium, temperature), as the likelihood forms them."""
    d = pd.read_csv(os.path.join(RESP, "derived_R2A_LB_current.csv"))
    out = []
    for medium, otu in OTU.items():
        s = d[d.OTU == otu]
        g = s.groupby("T").agg(
            o2_meas=("R_O2_mg_cell_min", "mean"), o2_sd=("R_O2_mg_cell_min", "std"),
            growth_meas=("growth_C_per_C_h", "mean"), growth_sd=("growth_C_per_C_h", "std"),
            n=("R_O2_mg_cell_min", "size")).reset_index()
        g["medium"] = medium
        out.append(g)
    return pd.concat(out, ignore_index=True)


def reg(x, y):
    k = np.isfinite(x) & np.isfinite(y)
    x, y = np.asarray(x)[k], np.asarray(y)[k]
    if len(x) < 3:
        return dict(n=int(len(x)))
    r = stats.linregress(x, y)
    tcrit = stats.t.ppf(0.975, len(x) - 2)
    return dict(n=int(len(x)), slope=float(r.slope),
                ci_lo=float(r.slope - tcrit * r.stderr), ci_hi=float(r.slope + tcrit * r.stderr),
                p=float(r.pvalue), r2=float(r.rvalue ** 2), intercept=float(r.intercept))


def main():
    m = measured()
    p = pd.read_csv(os.path.join(DECK, "fit_predictions.csv"))
    rows = []
    for conf in ("D", "E", "F"):
        for medium in OTU:
            q = p[(p.config == conf) & (p.medium == medium)].sort_values("T_C")
            mm = m[m.medium == medium]
            pred = np.interp(mm["T"], q.T_C, q.o2_pred_per_cell)
            for (_, o), pr in zip(mm.iterrows(), pred):
                rows.append(dict(config=conf, medium=medium, T_C=float(o["T"]),
                                 n=int(o["n"]), o2_meas=float(o.o2_meas),
                                 o2_sd=float(o.o2_sd) if np.isfinite(o.o2_sd) else np.nan,
                                 o2_pred=float(pr),
                                 growth_meas=float(o.growth_meas),
                                 resid=float(np.log(o.o2_meas / pr))
                                 if (o.o2_meas > 0 and pr > 0) else np.nan))
    r = pd.DataFrame(rows)
    r.to_csv(os.path.join(HERE, "task1_residuals.csv"), index=False)
    print(f"[q1t1] {len(r)} residual points: 3 configurations x 2 media x "
          f"{r.T_C.nunique()} temperatures; residual = log(measured O2 / modelled O2)\n")

    # --- the marginal regressions, which cannot separate the two ---------------------------
    regs = []
    print(f"{'config':7s} {'medium':7s} {'against':14s} {'n':>3s} {'slope':>10s} "
          f"{'95% CI':>22s} {'p':>8s} {'R2':>6s}")
    for conf in ("D", "E", "F"):
        for medium in OTU:
            s = r[(r.config == conf) & (r.medium == medium)].dropna(subset=["resid"])
            for lab, x in (("temperature", s.T_C), ("growth rate", s.growth_meas)):
                v = reg(x, s.resid)
                regs.append(dict(config=conf, medium=medium, against=lab, **v))
                print(f"{conf:7s} {medium:7s} {lab:14s} {v['n']:3d} {v['slope']:10.4f} "
                      f"[{v['ci_lo']:9.4f},{v['ci_hi']:9.4f}] {v['p']:8.4f} {v['r2']:6.3f}")
    pd.DataFrame(regs).to_csv(os.path.join(HERE, "task1_regressions.csv"), index=False)

    # --- the decisive test: same temperature, different growth rate ------------------------
    print("\n[q1t1] PAIRED-MEDIA TEST -- temperature held exactly, growth rate varying")
    pairs = []
    for conf in ("D", "E", "F"):
        s = r[r.config == conf].dropna(subset=["resid"])
        piv = s.pivot(index="T_C", columns="medium", values=["resid", "growth_meas"]).dropna()
        for T, row in piv.iterrows():
            pairs.append(dict(config=conf, T_C=float(T),
                              growth_NLDM=float(row[("growth_meas", "NLDM")]),
                              growth_LB=float(row[("growth_meas", "LB")]),
                              resid_NLDM=float(row[("resid", "NLDM")]),
                              resid_LB=float(row[("resid", "LB")]),
                              d_growth=float(row[("growth_meas", "LB")] - row[("growth_meas", "NLDM")]),
                              d_resid=float(row[("resid", "LB")] - row[("resid", "NLDM")])))
    pr = pd.DataFrame(pairs)
    pr.to_csv(os.path.join(HERE, "task1_paired_media.csv"), index=False)
    print(pr[pr.config == "D"][["T_C", "growth_NLDM", "growth_LB", "d_growth",
                                "resid_NLDM", "resid_LB", "d_resid"]].round(4).to_string(index=False))
    paired = {}
    for conf in ("D", "E", "F"):
        s = pr[pr.config == conf]
        v = reg(s.d_growth, s.d_resid)
        paired[conf] = v
        print(f"\n[q1t1] {conf}: d_resid vs d_growth  n={v['n']}  slope {v['slope']:+.4f} "
              f"[{v['ci_lo']:+.4f}, {v['ci_hi']:+.4f}]  p={v['p']:.4f}  R2={v['r2']:.3f}")

    json.dump(dict(n_points=int(len(r)), regressions=regs, paired=paired,
                   temperatures=sorted(r.T_C.unique().tolist()),
                   note="residual = log(measured R_O2_mg_cell_min / modelled per-cell O2, "
                        "the latter already including the fitted resp_scale)"),
              open(os.path.join(HERE, "task1_meta.json"), "w"), indent=2)
    print("\n[q1t1] wrote task1_residuals.csv, task1_regressions.csv, task1_paired_media.csv, "
          "task1_meta.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
