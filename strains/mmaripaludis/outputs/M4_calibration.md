# M4 — Bayesian calibration to the Jones 1983 TPC (H2/CO2)

Additive-inverse Bayesian calibration of the M3 thermal ecModel to the digitised Jones 1983
growth TPC, reusing the P2/v3 emcee machinery (`calibration_multi.run_methanogen`). **Fit on
raw absolute rate (1/h).** No Ea dissection (M5). Operating point: methanogen H2/CO2, thermal
ecModel (unfolding kcat(T)+f_N(T), NGAM(T) anchored on Goyal 2015), **single sMOMENT pool,
growth-law/allocation OFF**. Solver: **Gurobi** (pre-flight passed).

Emergent (a-priori) and calibrated are kept distinct: the **emergent prior is mu ≈ 0**
(maintenance-dominated, M3) — the dashed flat line in the figure. Nothing is relabelled as a
prediction.

## Free set + magnitude-first (PART A/B)
The single sMOMENT pool (no sectors) collapses the E. coli allocation levers
(f_metab/f_maint/sigma_sat) — they have no independent effect — so magnitude rides on
**kcat_scale**, which absorbs the in-vitro→in-vivo gap, the residual archaeal-kcat
underprediction, and the pool/saturation/f_metab magnitude uncertainty (all degenerate here).
9 free params: `kcat_scale` (LogNormal centred on the Davidi ~4× median, broad),
`{dTopt, topt_scale, dCp_scale, dTm, tm_scale}` (envelope), `{ngam_scale, ngam_steepness}`
(LogNormal ~1; Goyal NGAM is measured), `sigma_disc`. Walkers warm-started (DE) at the mode;
pre-flight confirmed growth at kcat_scale = 4 (rmax(38 °C) = 0.052).

## Fit (PART C)
Gurobi, 40 walkers, 6000 steps (~31 min), acceptance 0.33, **n_eff ≈ 891** (> 400). Stopped
at n_steps_max: autocorr τ_max ≈ 247 so chain/τ ≈ 24 (< the strict 50), i.e. **slow mixing**
(kcat_scale↔envelope correlations) but the posterior is well-estimated (n_eff comfortable).

**The posterior reproduces the Jones curve across its whole range** (see
`prior_vs_posterior_tpc.png`): the median passes through essentially all 11 points; RMSE
**0.0047 /h**, max |resid| 0.010 /h.

## Posterior (`demanded_corrections.csv`, `summary.json`)
| param | posterior median [90% CI] | reading |
|---|---|---|
| **kcat_scale** | **7.22 [6.22, 8.54]** | the demanded magnitude: a **few-fold in-vivo/in-vitro correction** absorbing the archaeal-kcat underprediction + Mcr uncertainty + pool magnitude. Larger than E. coli's 1.25 (the methanogen carries the DLTKcat archaeal residual) but within the documented in-vitro→in-vivo range (Davidi median ~4×, up to ~100×). |
| dTopt | −2.7 K [−3.1, −2.3] | pulls the a-priori Topt 42 → ~37 (matches Jones). |
| dCp_scale | 1.29 [1.06, 1.54] | slightly steeper MMRT curvature. |
| dTm | +2.3 K [−0.7, +6.2] | small (CTmax already ~right). |
| topt_scale / tm_scale | 0.91 / 0.95 | ~unchanged (not curve-constrained). |
| **ngam_scale** | **1.24 [0.74, 2.0]** | **near 1** — the data do NOT demand a big maintenance change from the measured Goyal NGAM (good). |
| ngam_steepness | 1.02 [0.55, 1.98] | unchanged. |
| sigma_disc | 0.006 /h | tiny — the fit is very tight. |

## Calibrated descriptors (apples-to-apples, model at the 11 Jones temps)
| | observed (Jones) | emergent prior | calibrated |
|---|---|---|---|
| rmax (1/h) | 0.181 | ≈ 0 | **0.184** ✓ reaches the peak |
| Topt (°C) | 37.0 | — | **37.0** ✓ |
| CTmax (°C) | 51.1 | — | **51.1** ✓ |
| **rising-limb Ea (eV)** | **0.66** | 1.72 (a-priori) | **0.85** |

The calibration **reaches the Jones peak** (kcat_scale did the magnitude work) and lands Topt
and CTmax on the data. The rising-limb **Ea calibrates down from the a-priori 1.72 → 0.85 eV**
(consistent basis; the dense-grid value 1.16 in summary.json is window-sensitive, hence the
apples-to-apples number). The model Ea (0.85) is slightly **steeper** than the measured Jones
Ea (0.66) — the absolute-rate likelihood weights the peak and under-weights the low-rate
rising limb, so Ea is only weakly curve-constrained and carries real uncertainty.

## Headline for M5
- **Magnitude:** a **7× kcat_scale** closes the a-priori undershoot — plausible as a combined
  in-vitro→in-vivo + archaeal-underprediction + pool correction, but it lumps several
  degenerate levers (single pool), so it is not uniquely "the in-vivo kcat gap".
- **Ea:** calibrated **~0.85 eV**, vs measured Jones **0.66** and E. coli **~0.9**. So at the
  organism-growth level the methanogen Ea is **comparable to E. coli, not dramatically higher**
  — the digitised Jones Ea (0.66) is if anything slightly *lower*. This tempers the
  "methanogenesis Ea ≫ respiration" expectation and is exactly what the M5 control-weighted Ea
  dissection must test mechanistically (is Mcr/the methanogenesis backbone the control set?).
- **Mcr sensitivity (3–294/s) carried:** kcat_scale partly compensates for the Mcr kcat
  uncertainty, so the M5 Ea attribution must propagate it.

## GO / NO-GO for M5 (Ea dissection + E. coli comparison)
**GO.** The model now reproduces the Jones TPC (peak, Topt, CTmax) with a plausible magnitude
correction and a measured-maintenance-consistent NGAM. M5 can run the control-weighted Ea
decomposition and the E. coli comparison.

**Carry-forward caveats (honest):**
1. **kcat_scale 7× lumps degenerate levers** (in-vivo kcat, saturation, f_metab, archaeal
   residual) — the single pool cannot separate them; a sectored/allocation model (deferred) or
   the Xia proteome would help.
2. **Rising-limb Ea weakly constrained** (small absolute residuals on the low-rate limb); the
   calibrated 0.85 eV carries uncertainty — central to the E. coli comparison, so report it
   with the caveat.
3. **Mcr kcat 3–294/s** still the dominant single-parameter uncertainty for the M5 Ea.
4. **Growth-law/allocation OFF** — the E. coli Ea-buffering term is absent here; fold it in (or
   note the asymmetry) before over-interpreting the cross-organism Ea comparison.
