#!/usr/bin/env python3
"""task1_two_measured_E.py -- K6 TASK 1: what ARE the two measured activation energies?

The repository holds two measured E_growth for the same organisms, about fourfold apart. K5
compared the model against one of them and reported the project's sharpest discrepancy. This
establishes what each one is before anything is concluded from either.

WHAT THE SOURCE CODE SAYS (read, not assumed; $CANDIDAS_ROOT is READ ONLY):

  OLS, `scripts/07_oxygen_fits.R`, function `fit_arr_lm`
      lm(ln y ~ boltz) over EVERY temperature with y > 0. No deactivation term, no
      rising-limb restriction, EXCLUDE_TEMPS_PLOT is empty. One fit per isolate.
      -> a straight Arrhenius line through a curve that turns over.

  Bayesian growth, `scripts/09_bayesian_models.R`, `fit_ss_hier`
      hierarchical SHARPE-SCHOOLFIELD,
          y ~ lnB0 - E*11604.5*(1/TK - 1/293.15) - log(1 + exp(Eh*11604.5*(1/Th - 1/TK)))
      so the high-temperature collapse is carried by its OWN terms (Eh, Th) and E is the
      RISING-LIMB activation energy. Partial pooling over isolates within group.

  Bayesian respiration, `fit_arr_hier`
      hierarchical ARRHENIUS, y ~ alpha + E*boltz_shift. No deactivation term -- respiration
      rises monotonically, so none is needed.

So the two E_growth are NOT two estimates of one quantity. One is the slope of a line through a
peaked curve; the other is the rising-limb parameter of a peaked model. The two E_resp agree
because respiration does not turn over, which is exactly the tell.

THE EMPIRICAL TEST. If that diagnosis is right, refitting the OLS to growth on the RISING LIMB
ONLY -- at or below each isolate's own optimum -- should move it toward the Bayesian value. If
it does not, the diagnosis is wrong and this report has to say so.

Run from the project root, with $CANDIDAS_ROOT readable:

    python3 reports/K6_like_for_like/task1_two_measured_E.py

Writes task1_measured_E.csv beside this file.
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
K_EV = 8.617333262e-5
T_REF_K = 293.15                      # the 20 C reference the R code uses

GROUPS = {
    "Clade1": [1, 2, 3], "Clade2": [4, 5, 6], "Clade3": [7, 8, 9], "Clade4": [10, 11, 12],
    "para": [16, 17, 18], "Hae": [19, 20, 21], "Duo": [22, 23],
}
MODEL_OF = {"Clade1": "cauris_iRV973 (C. auris clade I)",
            "Hae": "chaemulonii_draft", "Duo": "cduobushaemulonii_draft",
            "para": "cparapsilosis_iDC1003"}


def candidas_root():
    r = os.environ.get("CANDIDAS_ROOT")
    if r and os.path.isdir(r):
        return r
    guess = os.path.abspath(os.path.join(HERE, "..", "..", "..", "Candidas TPC", "Candidas"))
    return guess if os.path.isdir(guess) else None


def ols_E(T_C, y):
    """The R code's fit, transcribed: lm(ln y ~ boltz), boltz = 1/(k*Tref) - 1/(k*TK)."""
    T_C = np.asarray(T_C, float)
    y = np.asarray(y, float)
    ok = np.isfinite(T_C) & np.isfinite(y) & (y > 0)
    if ok.sum() < 3 or len(np.unique(T_C[ok])) < 2:
        return np.nan, np.nan, int(ok.sum())
    TK = T_C[ok] + 273.15
    boltz = 1.0 / (K_EV * T_REF_K) - 1.0 / (K_EV * TK)
    ln_y = np.log(y[ok])
    slope, intercept = np.polyfit(boltz, ln_y, 1)
    yhat = slope * boltz + intercept
    ss_res = float(np.sum((ln_y - yhat) ** 2))
    ss_tot = float(np.sum((ln_y - ln_y.mean()) ** 2))
    r2 = np.nan if ss_tot <= 0 else 1.0 - ss_res / ss_tot
    return float(slope), float(r2), int(ok.sum())


def main():
    root = candidas_root()
    if root is None:
        print("[k6] CANDIDAS_ROOT not found")
        return 1
    tab = os.path.join(root, "results", "tables")
    meas = pd.read_csv(os.path.join(tab, "derived_N0_R_results_with_carbon.csv"))
    meas = meas[(meas.keep) & (meas.fit_valid)]
    ols_g = pd.read_csv(os.path.join(tab, "arrhenius_growth_fgC_h_coefs.csv"))
    ols_r = pd.read_csv(os.path.join(tab, "arrhenius_respiration_fgC_h_coefs.csv"))
    bayes = pd.read_csv(os.path.join(tab, "bayes_clade_params.csv")).set_index("Group")
    bdiff = pd.read_csv(os.path.join(tab, "bayes_E_resp_minus_growth.csv")).set_index("Group")

    rows = []
    for grp, otus in GROUPS.items():
        x = meas[meas.OTU.isin(otus)]
        # the group's own optimum, from the measured growth curve
        gmean = x.groupby("T")["growth_fgC_h"].mean()
        Topt_measured = float(gmean.idxmax())
        Topt_bayes = float(bayes.loc[grp, "growth_Topt_C"]) if grp in bayes.index else np.nan

        # (i) OLS as published: every temperature
        E_full, r2_full, n_full = ols_E(x["T"], x["growth_fgC_h"])
        Er_full, r2r_full, _ = ols_E(x["T"], x["respiration_fgC_h"])
        # (ii) OLS on the rising limb only, cut at the measured optimum
        rise = x[x["T"] <= Topt_measured]
        E_rise, r2_rise, n_rise = ols_E(rise["T"], rise["growth_fgC_h"])
        Er_rise, _, _ = ols_E(rise["T"], rise["respiration_fgC_h"])
        # (iii) rising limb cut at the BAYESIAN optimum, as a sensitivity to the cut
        rise_b = x[x["T"] <= Topt_bayes] if np.isfinite(Topt_bayes) else rise
        E_rise_b, _, n_rise_b = ols_E(rise_b["T"], rise_b["growth_fgC_h"])
        Er_rise_b, _, _ = ols_E(rise_b["T"], rise_b["respiration_fgC_h"])

        rows.append(dict(
            group=grp, model=MODEL_OF.get(grp, ""), n_isolates=len(otus),
            Topt_measured_C=Topt_measured, Topt_bayes_C=Topt_bayes,
            OLS_full_E_growth=E_full, OLS_full_r2_growth=r2_full, n_full=n_full,
            OLS_full_E_resp=Er_full,
            OLS_rise_E_growth=E_rise, OLS_rise_r2_growth=r2_rise, n_rise=n_rise,
            OLS_rise_E_resp=Er_rise,
            OLS_riseBayesCut_E_growth=E_rise_b, OLS_riseBayesCut_E_resp=Er_rise_b,
            published_OLS_E_growth_mean=float(ols_g[ols_g.OTU.isin(otus)]["E_eV"].mean()),
            published_OLS_E_resp_mean=float(ols_r[ols_r.OTU.isin(otus)]["E_eV"].mean()),
            bayes_E_growth=(float(bayes.loc[grp, "growth_E_eV"]) if grp in bayes.index else np.nan),
            bayes_E_growth_lo=(float(bayes.loc[grp, "growth_E_lo"]) if grp in bayes.index else np.nan),
            bayes_E_growth_hi=(float(bayes.loc[grp, "growth_E_hi"]) if grp in bayes.index else np.nan),
            bayes_E_resp=(float(bayes.loc[grp, "resp_E_eV"]) if grp in bayes.index else np.nan),
            bayes_E_resp_minus_growth=(float(bdiff.loc[grp, "E_resp_minus_growth"])
                                       if grp in bdiff.index else np.nan),
            bayes_diff_lo=(float(bdiff.loc[grp, "lo"]) if grp in bdiff.index else np.nan),
            bayes_diff_hi=(float(bdiff.loc[grp, "hi"]) if grp in bdiff.index else np.nan)))

    d = pd.DataFrame(rows)
    d.to_csv(os.path.join(HERE, "task1_measured_E.csv"), index=False)

    print("=== E_growth (eV): does the OLS move toward the Bayesian value on the rising limb? ===")
    print(f"{'group':8s} {'Topt(meas)':>10s} {'OLS full':>9s} {'OLS rise':>9s} "
          f"{'OLS rise(B)':>11s} {'Bayes SS':>9s} {'Bayes 95%':>18s}")
    for _, r in d.iterrows():
        print(f"{r['group']:8s} {r['Topt_measured_C']:10.0f} {r['OLS_full_E_growth']:9.3f} "
              f"{r['OLS_rise_E_growth']:9.3f} {r['OLS_riseBayesCut_E_growth']:11.3f} "
              f"{r['bayes_E_growth']:9.3f}  [{r['bayes_E_growth_lo']:.2f},"
              f"{r['bayes_E_growth_hi']:.2f}]")
    print("\n=== E_resp (eV): unaffected, because respiration does not turn over ===")
    print(f"{'group':8s} {'OLS full':>9s} {'OLS rise':>9s} {'Bayes Arr':>10s}")
    for _, r in d.iterrows():
        print(f"{r['group']:8s} {r['OLS_full_E_resp']:9.3f} {r['OLS_rise_E_resp']:9.3f} "
              f"{r['bayes_E_resp']:10.3f}")
    print("\n=== E_resp - E_growth, by comparator ===")
    print(f"{'group':8s} {'OLS full':>9s} {'OLS rise':>9s} {'Bayesian':>9s} {'Bayes 95%':>18s}")
    for _, r in d.iterrows():
        print(f"{r['group']:8s} {r['OLS_full_E_resp']-r['OLS_full_E_growth']:9.3f} "
              f"{r['OLS_rise_E_resp']-r['OLS_rise_E_growth']:9.3f} "
              f"{r['bayes_E_resp_minus_growth']:9.3f}  "
              f"[{r['bayes_diff_lo']:.2f},{r['bayes_diff_hi']:.2f}]")
    print("\n[k6] wrote task1_measured_E.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
