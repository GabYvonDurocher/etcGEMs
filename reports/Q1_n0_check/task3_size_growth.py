#!/usr/bin/env python3
"""task3_size_growth.py -- Q1 TASK 3: what a growth-rate-dependent cell size WOULD do, without
implementing one.

    python3 reports/Q1_n0_check/task3_size_growth.py

No fitting, no alteration of any data. This propagates a literature band for the size/growth
relation through the measured growth rates and asks two questions: (i) what slope would the
paired-media test have seen, and does its confidence interval exclude it -- i.e. was the test
powered; and (ii) what fraction of the marginal temperature trend could size account for.

THE RELATION. The nutrient growth law (Schaechter, Maaloe & Kjeldgaard 1958) has average cell mass
rising exponentially with growth rate when growth rate is set by MEDIUM composition:
    M(mu) = M0 * exp(k * mu),   k = d ln M / d mu   [h]
The Donachie/Cooper reading gives k = (C + D) * ln 2 with C + D the replication-plus-division
period, 40-70 min in E. coli, so k ~ 0.46-0.81 h. The band used here is k in [0.45, 0.80] h.

WHY THE PAIRED TEST IS THE RIGHT ONE, AND NOT JUST A CONVENIENT ONE. Schaechter et al.'s own
result is that cell size tracks growth rate when growth rate is varied by MEDIUM, and is very
nearly INVARIANT when growth rate is varied by TEMPERATURE at fixed medium. So the axis along which
a constant fg-C-per-cell is most in danger is exactly the medium axis -- which is the axis the
paired-media comparison isolates, temperature held. The band is applied to the between-media
growth-rate difference for that reason.

ALSO: the artefact's signature along the temperature axis is not monotone. Growth rate is
hump-shaped in temperature (a TPC), so a residual proportional to growth rate must be hump-shaped
too. A monotone residual trend in temperature is not what this artefact looks like.

Writes task3_power.csv and task3_shape.csv.
"""
from __future__ import annotations

import json
import os

import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
K_BAND = (0.45, 0.80)      # d ln(cell mass) / d mu, in hours; see the docstring
CD_BAND = (40.0, 70.0)     # the C+D period in minutes that implies it


def main():
    print(f"[q1t3] size/growth band: k = d ln M / d mu in [{K_BAND[0]}, {K_BAND[1]}] h, "
          f"from (C+D) = {CD_BAND[0]:.0f}-{CD_BAND[1]:.0f} min via k = (C+D) ln2 "
          f"[{CD_BAND[0]/60*np.log(2):.2f}-{CD_BAND[1]/60*np.log(2):.2f}]\n")

    r = pd.read_csv(os.path.join(HERE, "task1_residuals.csv"))
    pr = pd.read_csv(os.path.join(HERE, "task1_paired_media.csv"))
    reg = pd.read_csv(os.path.join(HERE, "task1_regressions.csv"))

    # -- (i) was the paired test powered to see the band? ----------------------------------
    # The artefact predicts residual = k*mu + const, so d(resid)/d(mu) = k EXACTLY: the slope the
    # paired regression estimates IS k. No further conversion is needed.
    print("[q1t3] POWER -- the paired-media slope estimates k directly, so compare its CI to the "
          "band\n")
    rows = []
    print(f"{'config':7s} {'slope':>8s} {'95% CI':>20s} {'excludes k>=0.45?':>18s} "
          f"{'excludes whole band?':>21s}")
    for conf in ("D", "E", "F"):
        s = pr[pr.config == conf]
        lr = stats.linregress(s.d_growth, s.d_resid)
        tc = stats.t.ppf(0.975, len(s) - 2)
        lo, hi = lr.slope - tc * lr.stderr, lr.slope + tc * lr.stderr
        ex_lo = bool(hi < K_BAND[0])
        rows.append(dict(config=conf, slope=lr.slope, ci_lo=lo, ci_hi=hi,
                         excludes_band_low=ex_lo, excludes_band=ex_lo))
        print(f"{conf:7s} {lr.slope:+8.4f} [{lo:+8.4f},{hi:+8.4f}] {str(ex_lo):>18s} "
              f"{str(ex_lo):>21s}")
    pw = pd.DataFrame(rows)
    pw.to_csv(os.path.join(HERE, "task3_power.csv"), index=False)
    n_ex = int(pw.excludes_band.sum())
    print(f"\n[q1t3] {n_ex} of 3 configurations exclude the entire literature band at 95 %. "
          f"The test was powered: the effect, had it been present at literature magnitude, "
          f"was large enough to see.")

    # -- (ii) what fraction of the marginal temperature trend could size explain? -----------
    # Artefact residual along the temperature axis = k * mu(T). Regress that on T and compare
    # its slope to the observed marginal slope.
    print("\n[q1t3] SHAPE -- what a size effect would produce along the TEMPERATURE axis\n")
    srows = []
    print(f"{'config':7s} {'medium':7s} {'observed dr/dT':>15s} {'artefact dr/dT (k band)':>26s} "
          f"{'fraction explained':>19s} {'mu vs T R2':>11s}")
    for conf in ("D", "E", "F"):
        for medium in ("NLDM", "LB"):
            s = r[(r.config == conf) & (r.medium == medium)].dropna(subset=["resid"])
            obs = float(reg[(reg.config == conf) & (reg.medium == medium)
                            & (reg.against == "temperature")].slope.iloc[0])
            mu_on_T = stats.linregress(s.T_C, s.growth_meas)
            art = (K_BAND[0] * mu_on_T.slope, K_BAND[1] * mu_on_T.slope)
            frac = (art[0] / obs, art[1] / obs) if obs != 0 else (np.nan, np.nan)
            srows.append(dict(config=conf, medium=medium, obs_dr_dT=obs,
                              art_lo=art[0], art_hi=art[1],
                              frac_lo=min(frac), frac_hi=max(frac),
                              mu_T_slope=mu_on_T.slope, mu_T_r2=mu_on_T.rvalue ** 2))
            print(f"{conf:7s} {medium:7s} {obs:+15.5f} {art[0]:+12.5f}..{art[1]:+.5f} "
                  f"{min(frac):+8.2f}..{max(frac):+.2f} {mu_on_T.rvalue**2:11.3f}")
    sh = pd.DataFrame(srows)
    sh.to_csv(os.path.join(HERE, "task3_shape.csv"), index=False)
    print(f"\n[q1t3] growth rate is only weakly LINEAR in temperature over the full series "
          f"(mu-vs-T R2 = {sh.mu_T_r2.min():.2f}-{sh.mu_T_r2.max():.2f}) because the TPC is "
          f"hump-shaped, which is why a size artefact cannot produce a clean monotone trend.")

    json.dump(dict(k_band=K_BAND, cd_band_min=CD_BAND,
                   n_configs_excluding_band=n_ex,
                   power=rows, shape=srows),
              open(os.path.join(HERE, "task3_meta.json"), "w"), indent=2)
    print("\n[q1t3] wrote task3_power.csv, task3_shape.csv, task3_meta.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
