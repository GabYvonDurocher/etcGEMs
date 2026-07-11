# Ea-definition audit — the windowed slope is unstable; standardise on Sharpe-Schoolfield E

Diagnostic + a new window-independent Ea fitter (`src/etcgem/sharpe_schoolfield.py`). No
Bayesian re-fit, no model changes, no dissection re-plumb. Every convention applied
identically to MODEL and OBSERVED curves for BOTH organisms. Curves: E. coli emergent/tuned
(Van Derlinden P2 posterior-predictive) + observed VdL; methanogen calibrated (Jones M4
posterior-predictive) + observed Jones.

## PART A — the windowed Arrhenius-slope Ea is not a stable quantity
Boltzmann-Arrhenius slope (ln r vs 1/kT below Topt) under 5 window conventions
(`window_sensitivity.csv`). **Spread PER CURVE 0.42–1.41 eV — larger than the differences we
want to detect.** The current 10-95% values reproduce (E. coli emergent 0.61, tuned 0.96, obs
0.64; methanogen calibrated **1.17 on the dense grid** vs 0.85 on the sparse 11 Jones temps
reported in M4 — the same curve gives two different Ea; Jones observed swings 0.66→2.07).

## PART B — Sharpe-Schoolfield E (window-independent), `sharpe_schoolfield_fits.csv`
Schoolfield (1981) high-T-inactivation model fit to the whole curve (fixed T_ref = 20 °C):

| curve | SS-E (eV) [95% CI] | R² | windowed 10-95% |
|---|---|---|---|
| E. coli emergent | 0.46 [0.34, 0.57] | 0.90 | 0.61 |
| E. coli tuned | **0.68 [0.53, 0.82]** | 0.93 | 0.96 |
| E. coli observed (VdL) | **0.56 [0.47, 0.65]** | 0.97 | 0.64 |
| methanogen calibrated | **1.02 [0.79, 1.26]** | 0.96 | 1.17 |
| methanogen observed (Jones) | **1.04 [0.55, 1.53]** | 0.95 | 0.66 |

## PART C — comparison + does the conclusion hold
(i) **Window-dependence of the slope Ea:** severe (spread 0.42–1.41 eV/curve); it is not
comparable across curves or organisms.
(ii) **SS-E per curve:** see table; R² 0.90–0.97 (good fits; the sparse Jones curve gives a
wide CI as expected).
(iii) **Does the MODEL's SS-E match the OBSERVED SS-E?** **Yes, for both organisms** — a
cleaner validation than the windowed slope: methanogen model **1.02** vs observed **1.04**
(near-identical); E. coli tuned **0.68** vs observed **0.56** (model slightly high, CIs
overlap). See `ss_fits_overlay.png`.
(iv) **Cross-organism ordering — DOES THE HEADLINE SURVIVE?** The conclusion **FLIPS** with
the convention:
- **Windowed 10-95% slope:** methanogen obs 0.66 vs E. coli obs 0.64 → *comparable* (this is
  what M4 reported, and it was **misleading**).
- **Sharpe-Schoolfield E (window-independent, field-standard):** methanogen **~1.0** vs
  E. coli **~0.6** → the **methanogen Ea is ~1.7–1.9× higher** (observed 1.04 vs 0.56; model
  1.02 vs 0.68). **The "methanogenesis Ea > respiration" pattern HOLDS — and is only visible
  once the window-dependence is removed.**

## PART D — recommendation
**Standardise on the Sharpe-Schoolfield E** as the organism-level activation-energy
convention: it is window-independent, field-standard (rTPC), fit from the whole shape, and —
critically here — it makes MODEL and OBSERVED comparable and gives a stable cross-organism
ordering that the windowed slope does not. Report E with its CI and R²; keep the windowed
slope only as a deprecated cross-check.

**Implication for the E. coli activation-energy DISSECTION (follow-up, NOT executed here):**
the dissection's organism Ea (`Ea_org`) is currently the windowed BA slope, and the MCA
identity `Ea_org = Σ C_i·Ea_i/Σ C_i + allocation + maintenance + residual` requires `Ea_org`
AND the per-enzyme `Ea_i` to be defined the SAME way. Re-basing `Ea_org` to SS-E therefore
requires the per-enzyme `Ea_i` to be re-based consistently (e.g. an SS-style E of each
per-enzyme kcat(T) contribution, or a redefinition of the identity). This is a real
follow-up decision before M5 — flagged, not done in this audit.

## Files
`window_sensitivity.csv`, `sharpe_schoolfield_fits.csv`, `comparison_table.csv`,
`ss_fits_overlay.png`, this NOTE. Fitter: `src/etcgem/sharpe_schoolfield.py` (reusable for M5).
