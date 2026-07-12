# P3 — Bayesian calibration to the Zavrel 2015 light-saturated growth TPC (shape-first)

Additive-inverse calibration of the P2 thermal ecModel (iSynCJ816_STAR, unfolding kcat(T)+f_N(T)
+ NGAM(T), **single sMOMENT pool, growth-law/allocation OFF**) to the digitised **Zavrel 2015**
light-saturated growth TPC, reusing `calibration_multi.py` (emcee, provenance priors, Gaussian
discrepancy likelihood on raw absolute rates) — the same machinery as the E. coli and methanogen
fits. **Emergent vs calibrated kept distinct.** Solver **Gurobi**; fit under the light-saturated
autotrophic medium (photon shadow price = 0 across the range — in-mechanism holds). Entry point:
`strains/syn6803/run_p3_calibration.py`. No Ea dissection (P4); no allocation layer (P3b).

## PART A — target curve + operating point
- **Zavrel 2015** growth TPC: 6 points, 23–38 °C, Topt 35.0 °C, rmax 0.0972 /h. Fit on raw absolute
  rate (1/h). Observed **SS-E = 0.435 eV** (fit sd 0.023, R² 0.999) — BUT see the fragility caveat.
- Model = P2 thermal ecModel, single pool (budget 0.26), NGAM(T) on ATPM (Touloupakis 2015). Preflight:
  rmax(35 °C)=0.067, **photon shadow price 0** (light-saturated / carbon-fixation-limited holds).
- **Observed SS-E fragility (critical).** With only 6 points over a narrow window (peak at the 5th),
  the Sharpe–Schoolfield E is poorly identified: under ±5 % rate noise the 6-point SS-E has median
  0.45 but a **90 % CI of [0.32, 1.00]** — the curve-fit sd (0.023) is a gross under-statement. So
  "0.435" should be read as "≈0.4–0.5, loosely pinned". This bounds how hard P3 should push (and it
  means the robust Ea comparator is the well-sampled Inoue flux curve, below).

## PART B — free set (SHAPE-FIRST, single-pool)
Unified set as for the methanogen single-pool fit (sector levers f_metab/f_maint/sigma are **no-ops**
without the P3b allocation layer and are excluded): `kcat_scale` (LogNormal **centred on 1**, not the
Davidi 4× — the a-priori magnitude is already realistic; doubles as the borrowed-pool check), the
envelope `{dTopt, topt_scale, dCp_scale (broad — the prime Ea lever), dTm, tm_scale}`, maintenance
`{ngam_scale, ngam_steepness}` (Touloupakis-anchored), and `sigma_disc`. P_total fixed.

## PART C — fit (emcee)
Gurobi; 50 walkers; 4000 steps (n_eff **725** ≥ 400; acceptance 0.30; autocorr τ≈242; warm-started
at the DE mode; wall 19 min). Fit the Zavrel curve on absolute rates with the Gaussian discrepancy
likelihood.

## PART D — results, the Ea-lever diagnostic, cross-checks

### The fit reaches Zavrel (rates, rmax, Topt)
Posterior median passes through all 6 points (residuals ≤ 8 %): **rmax 0.094** (obs 0.097), **Topt
35.0 °C** (obs 35), CTmax 46.8 °C (Inoue ~44, prior-driven — Zavrel has no falling limb).
`prior_vs_posterior_tpc.png`.

### Demanded corrections — all MODEST and PLAUSIBLE
| param | posterior median | 90 % CI | reading |
|---|---|---|---|
| **kcat_scale** | **×1.22** | [1.10, 1.39] | small magnitude lift; the borrowed 0.26 pool budget is ~right |
| **dCp_scale** | **×0.85** | [0.43, 1.30] | curvature −3.39 kJ/mol/K (prior −4); a **modest** shallowing, **NOT railed** to the floor |
| dTopt | +0.1 K | [−1.9, +1.5] | Topt already right |
| topt_scale | ×0.88 | [0.68, 1.09] | ~neutral (high topt_scale collapses growth — not used) |
| dTm, tm_scale, ngam_* | ≈ prior | wide | unconstrained by the rising-limb-only Zavrel curve |

Only **kcat_scale** and **dCp_scale** are curve-constrained. Magnitude stayed near 1 (shape-first
confirmed); the maintenance multipliers stayed at the Touloupakis anchor.

### The Ea-lever diagnostic (the P4 setup) — headline
The window-independent **calibrated full-range (5–50 °C) growth SS-E = 0.563 eV**, achieved with the
envelope knobs at **plausible values** (dCp_scale 0.85 ≈ prior curvature; **not** pushed to an
implausible flat floor; no allocation buffer). So:

- **The low phototroph Ea is genuinely shallow carbon-fixation kcat(T)** — an in-mechanism,
  enzyme-kinetic result. The envelope reproduces it at essentially the literature MMRT curvature; it
  does **not** need an implausible dCp, and it does **not** need the allocation buffer. (Contrast the
  concern going in: the envelope alone *can* do it here, plausibly.)
- **Three-way ordering reproduced** (all full-range growth SS-E, consistent method): **phototroph 0.56
  < E. coli 0.68 < methanogen 1.06** — i.e. **photosynthesis < respiration < methanogenesis**, exactly
  the Yvon-Durocher 2014 ordering. The phototroph is the low-Ea point, for the right (kcat(T)) reason.
- Over the *narrow* 23–38 °C Zavrel window the model SS-E is 0.85 (window-inflated near the peak) vs
  the fragile observed 0.44; both lie within the observed SS-E's true [0.32, 1.00] band, so this is
  agreement within the data's (large) uncertainty, not a miss. The window-independent 0.56 is the
  quantity to report.

### Independent flux cross-check (Yvon-Durocher 2014 comparison) — matches
The calibrated **carbon-fixation-flux** (RuBisCO) SS-E = **0.563 eV** matches the **Inoue 2001
O₂-evolution** photosynthesis-flux SS-E = **0.52 ± 0.12 eV** (9 points, 25–52 °C, well-sampled,
NOT fit) — a solid, independent confirmation of the low photosynthesis-flux Ea. (The O₂-flux **Topt**
~42 °C runs warmer than the growth Topt ~35 °C — gross photosynthesis optima exceed growth optima, a
real feature; the **activation energy** is the matched quantity.) `inoue_crosschecks.png`.

### Validation overlay — the light-limitation gap (Discussion point)
Over the **Inoue 2001 light-LIMITED** growth curve the model (light-saturated) sits higher and peaks
later: Inoue light-limited Topt ≈ 25 °C vs the light-saturated 35 °C. Under light limitation, photon
capture (temperature-insensitive) co-limits and pulls Topt down and Ea further down — the regime the
user chose NOT to model (it would need the light-supply layer). This overlay makes the light-saturated
scope explicit and is a Discussion caveat, not a fit target.

## GO / NO-GO
- **P3b (cyanobacterial allocation layer): OPTIONAL, not required for the low-Ea result.** The
  envelope already delivers a plausibly-low, flux-validated Ea (0.56) without allocation. P3b (the
  analog of the methanogen M6 — Zavrel 2019 / Jahn 2018 / the 2021 temperature-growth-law) would test
  whether the cyano growth law lowers the growth Ea *further* toward the fragile 0.44 and would make
  the three-way *allocation* comparison symmetric, but it is a refinement, not a fix. **Recommend: do
  a light P3b for symmetry with the other two organisms, then P4.**
- **P4 (Ea dissection + three-way comparison): GO.** The calibrated phototroph is ready. P4 will
  attribute the 0.56 across the control-weighted terms and place it against E. coli / methanogen; the
  clean expectation from P3 is that the phototroph's low Ea is dominated by genuinely shallow
  Calvin-cycle kcat(T) (naive-mean/enzyme term), with allocation a minor contributor.

**Carry-forward caveats (honest):**
1. **Zavrel 6-point SS-E is fragile** ([0.32, 1.00]); the robust Ea anchor is the Inoue flux (0.52) —
   report the window-independent model SS-E (0.56), not the narrow-window 0.85 or the fragile 0.44.
2. **Falling-limb knobs (dTm/tm_scale) unconstrained** by Zavrel; CTmax (46.8) leans on the P2 prior —
   Inoue Fig-6 PSII denaturation is held in reserve to sanity-check Tm.
3. **Topt & Tm are still mesophile priors** (P2) — the calibration corrects them only slightly.
4. **Allocation OFF** — its Ea contribution is a P4 finding, not baked in here.
5. **Light-limited regime not modelled** (by design) — the Inoue light-limited overlay shows the gap.

## VERIFY (all reported)
0. solver=gurobi (preflight passed); fit under light-saturated medium (photon shadow price 0);
   NGAM(T) on; growth-law/allocation OFF (single pool). ✅
1. Unified free set + SHAPE-FIRST (magnitude ×1.22 near 1; envelope lowers the Ea); provenance priors;
   P_total fixed; observed Zavrel SS-E + its (fragile) CI reported. ✅
2. Posterior reaches Zavrel rmax (0.094/0.097), Topt (35.0/35), CTmax (46.8); window-independent
   calibrated growth SS-E 0.56 within the observed SS-E band [0.32, 1.00]; converged (n_eff 725). ✅
3. Ea-lever diagnostic: **dCp_scale** is the lever, demanded value **plausible (×0.85, not railed)** →
   **genuinely shallow Calvin kcat(T); allocation NOT required** — the explicit P4/P3b verdict. ✅
4. Secondary flux SS-E 0.56 vs Inoue O₂-evol 0.52 reported; Inoue light-limited + O₂-flux overlays
   saved; `calibration_zavrel/` outputs written; emergent vs calibrated distinct; GO for P4 (P3b
   optional-for-symmetry). ✅
