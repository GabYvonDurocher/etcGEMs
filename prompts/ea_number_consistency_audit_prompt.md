# Claude Code prompt — enforce ONE consistent pair of SS-E (Ea) numbers per organism across the whole activation-energy paper: E_a(observed) and E_a(model), identical in every figure, table, caption and sentence (autonomous)

Run from the project root (`.../MICROADAPT/etcGEMs`). CONSISTENCY AUDIT + STANDARDISATION of reports/activation_energy/.
The phototroph (and, to a lesser extent, the other two) currently show DIFFERENT SS-E/Ea numbers in the figures vs the
text vs the tables. Establish exactly TWO canonical numbers per organism — E_a(observed) [fit to the empirical calibration
data] and E_a(model) [SS-E of the calibrated model TPC] — from a SINGLE source of truth, and make every figure, table,
caption and inline mention use them. Light re-computation only (re-fitting SS-E to observed data points, reusing saved
model outputs/posteriors). NO model re-runs, NO re-calibration, NO changes to the mechanism/decomposition conclusions.

NOTE TO USER: launch in an auto-approving mode. Needs quarto to re-render.

THE DRIFT TO FIX (diagnosed):
- MODEL number appears as 0.563 (P3 single-pool), 0.573 (P3b sectored), 0.57 (P4 table) AND 0.64 (Fig 1 violin). 0.64 is
  the MEDIAN OF THE SS-E POSTERIOR; 0.57 is the SS-E of the calibrated model TPC (and the decomposition target). Pick ONE.
- OBSERVED number appears as 0.435 (fragile 6-point Zavrel GROWTH fit), 0.52 (Inoue FLUX fit) and 0.56 (a window-
  independent value). The Fig 1 "observed" marker at ~0.52 looks like the Inoue FLUX number, not the Zavrel GROWTH fit the
  model was calibrated to. Two different curves are being conflated under "observed".

---

```
Work AUTONOMOUSLY; commit in parts; print a summary + the final canonical table. Read first: reports/activation_energy/
{report.qmd, supplementary.qmd, assemble.py} and the Fig 1 + decomposition figure code;
src/etcgem/sharpe_schoolfield.py; the calibration + dissection artifacts strains/{mmaripaludis,eciML1515,syn6803}/
outputs/{calibration_*, ea_dissection_ss/}; outputs/ea_cross_organism/{comparison_table_3way.csv, NOTE_3way.md}; and the
digitised observed TPCs (methanogen Jones; E. coli Van Derlinden; phototroph Zavrel growth + the Inoue cross-check curves).
Gurobi only if a saved value must be recomputed from the model; prefer reusing saved TPCs/posteriors.

PART A - define the SINGLE SOURCE OF TRUTH (two numbers per organism, one procedure)
Compute/collect, with ONE identical SS-E fitting procedure (same sharpe_schoolfield.py settings, same T-handling, f_N
separation as the decomposition) for all three organisms:
- E_a(observed) := SS-E fit to the OBSERVED CALIBRATION data points (methanogen Jones; E. coli Van Derlinden; phototroph
  ZAVREL GROWTH — the curve the model was calibrated to), ALWAYS reported WITH its resampling/bootstrap CI. This is "the fit
  to the empirical data". CRITICAL for the phototroph: the Zavrel growth SS-E is 0.435 but ESSENTIALLY UNIDENTIFIED (90% CI
  [0.32, 1.00] under +/-5% rate noise), so it must NEVER appear as a bare number — always show it with its CI, so the
  model's 0.57 reads as SITTING INSIDE the observed interval (consistent), NOT as an overshoot/discrepancy. For the
  phototroph, ALSO compute the Inoue light-saturated FLUX SS-E separately (~0.52, well-identified, 9 points) and label it as
  an INDEPENDENT CROSS-CHECK (E_a(Inoue flux)) — the headline empirical Ea stays the Zavrel-growth value (symmetric with the
  other two), with Inoue as corroboration.
- FIT QUALITY (so the obs-vs-model descriptor difference is not misread as a misfit): for each organism ALSO report the
  rate-space fit of the calibrated model to the observed points (e.g. residuals / RMSE / R2; the phototroph passes through
  all 6 Zavrel points with residuals <=8%). State explicitly that the model REPRODUCES the observed TPC, and that any
  E_a(observed)-vs-E_a(model) difference is a small-sample descriptor-estimation effect (few rising-limb points), not a
  failure to fit — largest/least-identified for the phototroph (wide CI), a small genuine offset for E. coli (0.56 vs 0.68),
  and negligible for the methanogen (1.04 vs 1.06).
- E_a(model) := SS-E of the CALIBRATED (sectored, posterior-median-parameter) model TPC — the SAME value the control-
  weighted decomposition sums to (methanogen 1.06; respiration 0.68; photosynthesis 0.57). This is "the fit to the modelled
  data". Confirm each organism's decomposition (naive+control+allocation+maintenance+aggregation) sums to THIS number.
- Reconcile the Fig 1 posterior: the violin should be computed on the SAME calibrated sectored model + SAME SS-E settings,
  so its distribution is consistent with E_a(model). If the posterior MEDIAN differs from the point E_a(model) (as the
  0.64 vs 0.57 gap suggests), the CANONICAL quoted value is the point E_a(model) (the decomposition target); report the
  posterior median + CI only in the caption as the spread, and mark the POINT value on the violin (not a separate posterior-
  median line). Investigate + state briefly WHY they differ (skew of the SS-E posterior) so it is understood, not hidden.
- Write these to ONE source-of-truth file: outputs/ea_cross_organism/ss_e_canonical.{csv,json} with columns organism,
  E_a_observed, E_a_observed_CI, E_a_model, E_a_model_posteriorCI, and (phototroph) E_a_Inoue_flux. Every figure/table/text
  number must trace to this file.

PART B - propagate to ALL text, tables and captions
- Grep the paper for EVERY SS-E/Ea number (e.g. 0.435, 0.44, 0.51, 0.52, 0.56, 0.563, 0.573, 0.57, 0.64, 0.68, 0.69, 0.87,
  1.04, 1.06, and the "~0.65 benchmark") in report.qmd + supplementary.qmd + assemble.py + figure code + NOTE files that
  feed the paper. For each, replace with the canonical E_a(observed) or E_a(model) from PART A, keeping observed vs model
  explicitly distinguished in the prose ("the model predicts E_a = 0.57 eV, versus 0.44 eV [95% CI ...] fit to the observed
  growth data, and 0.52 eV from the independent light-saturated flux curve"). Fix the three-way comparison table and the
  descriptor table to the canonical pair. Do NOT alter the decomposition term values (they sum to E_a(model)).
- Make sure the ORDERING sentences (methanogenesis > respiration > photosynthesis) use E_a(model) consistently.

PART C - fix the FIGURES (Fig 1 panel D + any SS-E figure)
- Fig 1 panel D violins: the marked central value + numeric label per organism = E_a(model) (1.06 / 0.68 / 0.57), matching
  the table and decomposition. The observed reference marker = E_a(observed) (Jones ~1.04 / Van Derlinden ~0.56 / ZAVREL
  GROWTH ~0.44 — NOT the Inoue 0.52). CRITICAL: draw the observed marker WITH AN ERROR BAR spanning its CI — especially the
  phototroph's [0.32, 1.00] — so a bare 0.44 dash next to the 0.57 violin does NOT invent a visual discrepancy; the wide bar
  should make clear the model value lies within the observed interval. If the Inoue flux value is shown, mark it as a
  SEPARATE, clearly-labelled cross-check point, not the observed dash. Keep the earlier panel-D text-overlap fixes (rotated
  x labels, benchmark clear of the medians).
- Any other figure that prints an SS-E value must read from ss_e_canonical.

PART D - build + verify
- Re-run assemble.py; quarto render report + supplement; build clean. Print the FINAL canonical table (the two numbers +
  CIs per organism, + the phototroph Inoue cross-check) and confirm every figure/table/text now matches it.

VERIFY (report all)
1. ss_e_canonical.{csv,json} written; E_a(observed) [+CI] and E_a(model) computed by ONE procedure for all three; the
   phototroph's Zavrel-growth observed vs Inoue-flux cross-check kept DISTINCT.
2. Each organism's decomposition sums to E_a(model); the Fig 1 point marker = E_a(model); the point-vs-posterior-median
   gap (0.57 vs 0.64) explained + the canonical point value used everywhere.
3. Every SS-E number in report.qmd + supplementary.qmd + figures traces to ss_e_canonical (no stray 0.435/0.52/0.563/0.573/
   0.64 used inconsistently); observed vs model distinguished in the prose; ordering sentences use E_a(model).
4. Fig 1 observed marker for the phototroph is the Zavrel-growth value (not Inoue); Inoue shown only as a labelled cross-
   check; panel-D text still non-overlapping.
5. report + supplement build (page count); final canonical table printed.

CONSTRAINTS
- Consistency + light SS-E re-fit only; reuse saved model TPCs/posteriors; NO model re-runs, NO re-calibration, NO change to
  the decomposition terms or the mechanistic conclusions. SS-E throughout. Two numbers per organism, one source of truth.
- Autonomous; commit in parts: "paper(activation_energy): single source of truth for E_a(observed) vs E_a(model) per organism (ss_e_canonical)",
  "paper(activation_energy): propagate canonical E_a numbers to all text/tables/captions + Fig 1 markers; render".
```
