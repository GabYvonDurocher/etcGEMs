#!/usr/bin/env python3
"""task2_apply_correction.py -- K8 TASK 2: apply A1's measured Seq2Tm bias, two ways.

TWO CORRECTIONS, because TASK 1 found A1's bias is not uniform (it rises 1.06 C per C of
predicted Tm, from +2.44 C in the lowest predicted octile to +12.78 C in the highest).

  (a) FLAT OFFSET, -5.43 C on every enzyme. What the hypothesis literally proposes. It moves
      the LOCATION of the Tm distribution and leaves its SHAPE alone.
  (b) THE REGRESSION A1's DATA SUPPORTS, Tm_corrected = 52.60 - 0.061 x Tm_predicted, fitted on
      A1's own 1947 paired points. This moves location AND shape: because the predictor carries
      almost no within-proteome signal, the corrected distribution is nearly a constant.

Both are applied as tests, not fits. (a) is also available through the CLI as
`configs/experiments/candida_B5_tm_bias_corrected.yaml`, which pins it with `fixed_globals`.

THE STEEPNESS IS CHECKED, NOT ASSUMED. K7 established that the two envelope failures are
opposed under the curvature prior. A Tm offset should move the ceiling and leave the rising
limb alone; if it does not, the mechanism is not what the hypothesis claims. E_growth is
therefore reported before and after, fitted over the organism's rising limb on both sides.

NO DEFAULT IS CHANGED. (a) uses `Perturbation(dTm=...)`; (b) mutates the built cost table
in memory and calls `refresh_params()`.

Run from the project root, with $CANDIDAS_ROOT readable:

    python3 reports/K8_tm_bias/task2_apply_correction.py

Writes task2_corrections.csv beside this file.
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
from etcgem.transfer import load_measured_tpc                # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
K_EV = 8.617333262e-5
T_REF_K = 293.15
TEMPS = np.arange(22.0, 45.0, 2.0)
WIDE = np.linspace(15.0, 75.0, 121)
EXP = "candida_B5_respire"
A1_BIAS = 5.43                       # A1's measured mean bias, C
A1_INTERCEPT, A1_SLOPE = 52.60, -0.061   # measured = a + b * predicted, on A1's 1947 points
ECOLI_GAP = 5.9                      # K4 section 4, measured meltome

SPECIES = {
    "cauris_iRV973": dict(group="Clade1", otus=[1, 2, 3], label="C. auris (clade I)",
                          limit=44.0),
    "chaemulonii_draft": dict(group="Hae", otus=[19, 20, 21], label="C. haemulonii",
                              limit=38.0),
    "cduobushaemulonii_draft": dict(group="Duo", otus=[22, 23], label="C. duobushaemulonii",
                                    limit=38.0),
    "cparapsilosis_iDC1003": dict(group="para", otus=[16, 17, 18], label="C. parapsilosis",
                                  limit=38.0),
}


def candidas_root():
    r = os.environ.get("CANDIDAS_ROOT")
    if r and os.path.isdir(r):
        return r
    g = os.path.abspath(os.path.join(HERE, "..", "..", "..", "Candidas TPC", "Candidas"))
    return g if os.path.isdir(g) else None


def ols_E(T_C, y):
    T_C, y = np.asarray(T_C, float), np.asarray(y, float)
    ok = np.isfinite(T_C) & np.isfinite(y) & (y > 0)
    if ok.sum() < 3 or len(np.unique(T_C[ok])) < 2:
        return np.nan
    TK = T_C[ok] + 273.15
    return float(np.polyfit(1.0 / (K_EV * T_REF_K) - 1.0 / (K_EV * TK), np.log(y[ok]), 1)[0])


def evaluate(pm, meas, Topt_cut, pert=None):
    pert = pert or Perturbation()
    model = pm.ec.model
    o2 = next((r.id for r in model.reactions
               if r.id.startswith("EX_") and len(r.metabolites) == 1
               and list(r.metabolites)[0].id.startswith("C00007__")), None)
    mus, qs = [], []
    for T in TEMPS:
        apply_state(pm.ec, float(T), pert)
        sol = model.optimize()
        ok = sol.status == "optimal"
        mus.append(float(sol.objective_value or 0.0) if ok else 0.0)
        qs.append(abs(float(sol.fluxes.get(o2, 0.0))) if (ok and o2) else np.nan)
    gw = np.zeros(len(WIDE))
    for i, T in enumerate(WIDE):
        apply_state(pm.ec, float(T), pert)
        v = model.slim_optimize()
        gw[i] = 0.0 if (v is None or not np.isfinite(v) or v < 1e-6) else v
    scale = float(meas["mu"].max() / max(gw.max(), 1e-9))
    d = TPC(WIDE, gw * scale).descriptors(0.05)
    pred = np.interp(meas["T_C"].values.astype(float), WIDE, gw) * scale
    obs = meas["mu"].values.astype(float)
    ss_res = float(np.sum((obs - pred) ** 2))
    ss_tot = float(np.sum((obs - obs.mean()) ** 2))
    r2 = np.nan if ss_tot <= 0 else 1.0 - ss_res / ss_tot
    sel = TEMPS <= Topt_cut
    return dict(CTmax_C=d.CTmax_C, Topt_C=d.Topt_C, rmax=d.rmax, Ea_eV=d.Ea_eV,
                fit_r2=r2, peak_mu_model=float(gw.max()),
                E_growth=ols_E(TEMPS[sel], np.array(mus)[sel]),
                E_resp=ols_E(TEMPS, np.array(qs)))


def main():
    root = candidas_root()
    if root is None:
        print("[k8] CANDIDAS_ROOT not found")
        return 1
    bayes = pd.read_csv(os.path.join(root, "results", "tables",
                                     "bayes_clade_params.csv")).set_index("Group")
    rows = []
    for strain, spec in SPECIES.items():
        Topt_cut = float(bayes.loc[spec["group"], "growth_Topt_C"])
        meas = load_measured_tpc(strain, resolve(strain, EXP))

        # --- uncorrected, and (a) the flat offset: same provider, different perturbation ---
        pm = build_provider(resolve(strain, EXP))
        tm0 = np.array([e.Tm - 273.15 for e in pm.ec.table.entries
                        if e.Tm is not None and np.isfinite(e.Tm)])
        base = evaluate(pm, meas, Topt_cut)
        flat = evaluate(pm, meas, Topt_cut, Perturbation(dTm=-A1_BIAS))

        # --- (b) the regression correction: rebuild and mutate every Tm in place ---
        pm2 = build_provider(resolve(strain, EXP))
        for e in pm2.ec.table.entries:
            if e.Tm is not None and np.isfinite(e.Tm):
                e.Tm = (A1_INTERCEPT + A1_SLOPE * (e.Tm - 273.15)) + 273.15
        pm2.ec.refresh_params()
        tm1 = np.array([e.Tm - 273.15 for e in pm2.ec.table.entries
                        if e.Tm is not None and np.isfinite(e.Tm)])
        regr = evaluate(pm2, meas, Topt_cut)

        for lab, r, tms in (("uncorrected", base, tm0),
                            ("(a) flat -5.43 C", flat, tm0 - A1_BIAS),
                            ("(b) A1 regression", regr, tm1)):
            rows.append(dict(species=spec["label"], strain=strain, correction=lab,
                             observed_limit_C=spec["limit"],
                             gap_C=r["CTmax_C"] - spec["limit"],
                             Tm_median_C=float(np.median(tms)),
                             Tm_sd_C=float(np.std(tms)), **r))
        print(f"[k8] {spec['label']:22s}")
        for lab, r, tms in (("uncorrected", base, tm0),
                            ("(a) flat -5.43 C", flat, tm0 - A1_BIAS),
                            ("(b) A1 regression", regr, tm1)):
            print(f"       {lab:18s} CTmax {r['CTmax_C']:6.2f} (gap "
                  f"{r['CTmax_C']-spec['limit']:+5.1f})  Topt {r['Topt_C']:5.1f}  "
                  f"E_growth {r['E_growth']:6.3f}  rmax {r['rmax']:.4f}  "
                  f"R2 {r['fit_r2']:6.3f}  Tm med {np.median(tms):5.2f} "
                  f"sd {np.std(tms):5.2f}", flush=True)

    d = pd.DataFrame(rows)
    d.to_csv(os.path.join(HERE, "task2_corrections.csv"), index=False)

    print("\n=== the prediction, and what happened ===")
    b = d[d.correction == "uncorrected"].set_index("species")
    f = d[d.correction == "(a) flat -5.43 C"].set_index("species")
    print(f"  PREDICTED (DECISIONS D4, recorded before the run): dCT_max/dTm ~ 1.0, "
          f"so about -{A1_BIAS:.2f} C")
    for sp in b.index:
        sh = f.loc[sp, "CTmax_C"] - b.loc[sp, "CTmax_C"]
        print(f"    {sp:22s} CT_max {b.loc[sp,'CTmax_C']:6.2f} -> {f.loc[sp,'CTmax_C']:6.2f}  "
              f"= {sh:+5.2f} C   (dCT_max/dTm = {sh/-A1_BIAS:.2f})")
    print("\n=== steepness: did the rising limb move? ===")
    for sp in b.index:
        print(f"    {sp:22s} E_growth {b.loc[sp,'E_growth']:6.3f} -> "
              f"{f.loc[sp,'E_growth']:6.3f}  ({100*(f.loc[sp,'E_growth']/b.loc[sp,'E_growth']-1):+.1f} %)"
              f"   T_opt {b.loc[sp,'Topt_C']:5.1f} -> {f.loc[sp,'Topt_C']:5.1f}")
    print(f"\n=== convergence on E. coli's +{ECOLI_GAP} C gap (measured meltome) ===")
    for sp in b.index:
        print(f"    {sp:22s} gap {b.loc[sp,'gap_C']:+5.1f} -> {f.loc[sp,'gap_C']:+5.1f} C"
              f"   ({'below' if f.loc[sp,'gap_C'] < ECOLI_GAP else 'above'} E. coli)")
    print("\n[k8] wrote task2_corrections.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
