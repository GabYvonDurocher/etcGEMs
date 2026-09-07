# Claude Code prompt — A1: calibrate the sequence predictors against measured truth — do Seq2Tm and Seq2Topt compress interspecies variance, and by how much? (autonomous)

Run from the project root (`.../MICROADAPT/etcGEMs`). This is not a modelling step. Every
species-specific input the Candida etcGEM has comes from three sequence predictors, and the entire
Figure 4 conclusion rests on one number one of them produced (0.52 °C). Nobody has asked whether
that predictor can resolve a difference of that size at all. This prompt asks it, against
measurements, on a eukaryote.

NOTE TO USER: launch in an auto-approving mode. It DOWNLOADS public data (a measured yeast meltome,
two yeast proteomes) and RUNS Seq2Tm / Seq2Topt — the predictors K1 wired into
`tools/reconstruction/` but never executed, so `fetch_external.sh` must be run first. Budget:
predictor inference over ~12,000 sequences, plus orthology. Hours, not minutes, and mostly GPU/CPU
inference. If any download is blocked, STOP and name the file you need rather than substituting.

REFERENCE, read first: `docs/CANDIDA_DISCUSSION_2026-09-07.md` (§1 as revised by K2, §3, and action
point A1 in §8), `reports/candida_thermal_limit/K2_core_thermal_form.md` (the model side of the
arithmetic is now settled: the required separation is **13.8 °C**, not 33 °C), and
`tools/reconstruction/` (how the predictors are invoked; `13_seq2topt_input.py`,
`14_run_seq2topt_seq2tm.sh`, `15_run_seq2tm.py`).

THE ARITHMETIC THIS PROMPT COMPLETES. Figure 4's claim is a ratio of two numbers. K2 fixed the
denominator: the model requires 13.8 °C, not the 33 °C the standalone reported. This prompt tests
the numerator: is 0.52 °C what the *proteomes* differ by, or what the *predictor can see*? If the
predictor compresses by ~8×, the corrected pair is roughly 4 °C against 13.8 °C — still a failure,
but ~3× rather than ~63×, which is a materially different sentence.

WHAT MAKES THIS ANSWERABLE. *S. cerevisiae* has a measured proteome-wide meltome (Meltome Atlas,
Jarzab 2020, PRIDE PXD011929; and Leuenberger 2017). So the predictor can be scored against
measurement on a yeast, three ways: absolute accuracy, variance compression, and a paired
interspecies difference against *S. uvarum* (measured mean ΔTm 1.6 °C over 827 proteins — the
benchmark already used in Figure 4C; take its exact provenance from
`$CANDIDAS_ROOT/gem/notes/FIG4_etcgem_caption.md`).

---

```
Work AUTONOMOUSLY; commit in parts; print a summary. Branch: `git switch -c a1/predictor-calibration
main`. Outputs go to `reports/predictor_calibration/` (framework-level, NOT under
candida_thermal_limit). Do NOT change any strain, model, experiment or committed output. Do NOT
touch $CANDIDAS_ROOT (read-only).

PART 0 - acquire, and be explicit about provenance
- Fetch the predictor weights via tools/reconstruction/fetch_external.sh.
- Obtain: (i) a measured S. cerevisiae meltome with per-protein Tm and a resolvable protein ID;
  (ii) the S. cerevisiae reference proteome; (iii) the S. uvarum reference proteome; (iv) the
  per-protein measured S. cerevisiae/S. uvarum comparison IF the source publishes one.
- Write reports/predictor_calibration/DATA_PROVENANCE.md: for each file, the accession/DOI/URL, the
  date, the number of entries, and the identifier namespace. If (iv) is only published as a summary
  statistic (mean 1.6 °C, n = 827) and not per protein, SAY SO — PART C then compares
  summary-to-summary and is weaker; do not silently substitute anything.

PART A - absolute accuracy: does Seq2Tm work on a yeast at all?
- Predict Tm for every S. cerevisiae protein with a measured value. Report n, Pearson and Spearman
  correlation, RMSE, and the bias (mean predicted - mean measured).
- Plot predicted vs measured with the 1:1 line.
- This is the precondition for everything else. If the correlation is weak, say so plainly and
  carry it forward into the interpretation rather than proceeding as if it were strong.

PART B - variance compression: the key test, and it needs only one species
- Compare the SPREAD of predicted Tm across the proteome with the spread of measured Tm: SD, IQR,
  and the 5-95 percentile range, predicted against measured, on the matched subset.
- Report the compression ratio SD_measured / SD_predicted.
- Also report it for the residual: regress measured on predicted and give the slope. A slope
  substantially above 1 means the predictor is shrinking real variation toward the mean, which is
  the failure mode that would make a 0.52 C interspecies estimate an underestimate.
- This is the strongest test available because the Meltome Atlas gives thousands of proteins in one
  species; it does not depend on orthology or on a second species.

PART C - the paired interspecies test
- Pair S. cerevisiae and S. uvarum orthologs (reciprocal best hits; reuse
  tools/reconstruction/07_rbh_orthologs.py, generalised if needed).
- Predict Tm for both, compute the paired mean difference and its CI over unique protein pairs
  (NOT over reactions - see gem/24_paired_dedup_audit.py for why that matters).
- Compare with the measured 1.6 C. Report the ratio measured/predicted. If per-protein measured
  values were obtained in PART 0, also report the paired correlation between measured and predicted
  DIFFERENCES, which is the quantity that actually matters and is stronger than comparing means.

PART D - the noise floor, and this is the control nobody has run
- The four C. auris clades are 99.4-100% identical at the proteome level; their true pairwise
  Tm difference is ~0. Their proteomes are at $CANDIDAS_ROOT/phylo/proteomes/auris_cladeI..IV.faa.
- Run Seq2Tm on all four, pair orthologs, and report the paired mean difference for each of the six
  clade pairs.
- Whatever that comes out at is the predictor's noise floor on this kind of comparison. Report the
  0.52 C auris-vs-haemulonii estimate as a multiple of it. If the floor is of the same order as
  0.52 C, that is a finding about the estimate's meaning, not about the biology.

PART E - Seq2Topt, the same treatment where data allow
- Repeat PARTs C and D for Seq2Topt (interspecies paired difference, and the clade noise floor).
- PARTs A and B require measured per-enzyme catalytic optima, which likely do not exist
  proteome-wide. If no measured benchmark can be obtained, say so and report the spread tests only.

PART F - what the correction does to Figure 4
- Using the compression factor from PART B (and PART C if per-protein data allowed it), give a
  CORRECTED estimate of the C. auris vs C. haemulonii paired Tm difference, with an interval, and
  state the assumption that makes the correction valid (that compression measured in one yeast pair
  transfers to another).
- Put it against K2's 13.8 C requirement and report the corrected fold-gap alongside the
  uncorrected one and the standalone's original ~63x. One table, three rows, so the arithmetic is
  visible.
- Do NOT conclude that the mechanism is or is not enzyme thermostability. Report the numbers.

PART G - DLTKcat: scope it, do not run it
- DLTKcat predicts kcat(T) for enzyme-SUBSTRATE pairs, so it cannot be benchmarked this way: there
  is no measured cross-species kcat(T) ortholog set, and substrate assignment needs a metabolic
  model, which S. uvarum does not have.
- Write half a page in the report: what running it on the four Candida proteomes would cost, what it
  would and would not test, and the fact that E. coli uses it as an OVERLAY on the same shared dCp
  prior that Candida already has - so Candida is missing a refinement, not a mechanism. Recommend
  for or against, with reasons. Do not run it.

PART H - the report
- reports/predictor_calibration/report.md: PARTs A-G, every figure and table with its producing
  script, and a short section "what this does and does not license us to say".
- Update docs/CANDIDA_DISCUSSION_2026-09-07.md §8 A1 with the outcome (a few lines, dated, pointing
  at the report - do not rewrite the section).
- Update prompts/README.md.

VERIFY (report all)
1. DATA_PROVENANCE.md complete; whether per-protein S. cerevisiae/S. uvarum data was obtained or
   only the summary statistic.
2. PART A: n, correlations, RMSE, bias; an explicit statement of whether the predictor is accurate
   enough on a yeast for the rest to mean anything.
3. PART B: predicted vs measured SD, IQR and 5-95 range; the compression ratio; the regression slope.
4. PART C: paired mean difference and CI over unique pairs; the ratio to the measured 1.6 C; the
   paired correlation if available.
5. PART D: all six auris clade-pair differences; the noise floor; 0.52 C expressed as a multiple.
6. PART E: Seq2Topt equivalents, and what could not be done for lack of a benchmark.
7. PART F: the three-row table (original / K2-corrected / K2+compression-corrected).
8. PART G: the DLTKcat recommendation with reasons.
9. `git diff main --stat`: reports/predictor_calibration/, tools/ (only if a script needed
   generalising), docs/, prompts/. No strain, model, experiment or committed output changed.

CONSTRAINTS
- Measurement is the reference throughout. Where no measurement exists, say so and stop - do not
  substitute a second prediction for a measurement.
- Pair over unique protein pairs, never over reactions. Report n honestly.
- The noise floor (PART D) is not optional. An interspecies estimate without a same-species control
  cannot be interpreted.
- Report numbers; do not adjudicate the biological mechanism. That is downstream of this prompt.
- If a predictor cannot be run (weights unavailable, sequence-length limits - Seq2* drops sequences
  >2000 aa, which K1 found affects 3-9 genes per Candida species), report the exclusions and their
  size rather than working around them silently.
- Autonomous; commit in parts:
  "A1: data acquisition + provenance",
  "A1: Seq2Tm absolute accuracy and variance compression vs the measured yeast meltome",
  "A1: paired interspecies test and the same-species noise floor",
  "A1: Seq2Topt; corrected Figure 4 arithmetic; DLTKcat scoping",
  "A1: report".
```
