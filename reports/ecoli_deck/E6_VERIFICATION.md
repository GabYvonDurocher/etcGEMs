# E6 verification — 2026-09-11 snapshot

## 1. Premise and scope

- Worktree: `etcGEMs-work`. Branch: `e2/deck`, continued from `bc356e3`.
- Initial worktree was clean on `q1/n0-check`; returned to e2/deck without merging Q1.
- Interpreter: sibling `etcGEMs-venv/bin/python`, Python 3.9.6. Quarto/LuaLaTeX Beamer.
- Baseline render: exit 0, **49 source frames, 52 PDF pages**, frame check 0 missing.
- P16 seed 2 independently confirmed running by an approved read-only process check,
  PID 57126, `run_reduced.py --tag red2 --seed 2`. No seed-2 results quoted.
- E5 errors **1, 3** and jobs **4, 5, 6** carried forward. ERROR 2 superseded.
- E5 had already run, despite E6's premise. E1 register absent in both worktrees and
  available Git history. No duplicate E5 execution and no return to the P15-only conclusion.
- No solves, fits, changes to src/ or strains/, push, merge, or primary working-file writes.
  Switching/committing a worktree necessarily updates shared Git metadata in primary .git.

## 2. E5 carry-forward checks

**Stopping rule:** P16 D3: dynesty, 800 live points, rslice (3 slices), multi bounds,
dlogz < 0.1. Agreement requires log Z within combined reported error AND no parameter
median differing by more than two Monte-Carlo errors. The current posterior slides state
these rules. Older-MCMC narrative remains explicitly historical with ESS >=600; no
nested run is described using autocorrelation times or walkers. The generic methods slide
now records the move from ensemble MCMC to nested sampling.

**Identifiability:** the worked pair distinguishes compensating stability parameters from
a flat lever. Removed the claim that failed-run live-point spread proves dTm's posterior
precision. P16 D5 itself corrects that extrapolation. No unweighted P16 correlation values
are quoted. This does not invalidate the documented numerical crash diagnosis.

**Holdout:** `reports/ecoli_tpc/report.qmd:563,570,580` says the emergent prediction was
nothing-fit-to-growth, peak 1.04 vs measured 2.40 h^-1 (about 2.3-fold low), with shape
agreement. That curve was subsequently used for calibration; calibrated holdout remains
outstanding. The deck retains E5's accurate standalone holdout slide. R4 was already fixed
on the deck branch. The new 0d repeats the corrected distinction.

**Line scan:** P9 report verifies 22 directions, 41 points per line (40 steps), 902 builds;
step 0.05 prior SD across +/-1 SD; 12/22 with a largest jump >20% of the entire line's
range, median 39%, maximum 99%, two flat axes. The preceding slide explains transects,
step size, range and why abrupt changes impede local fitting. It does not claim every
algorithm is mathematically unable to cross a discontinuity.

Figure 12 already had its own enlarged slide after E5. E6 baseline and final: **82% height,
234.3 pt calculated rendered width**, about **233.6 pt** from pdfimages' rounded 524 dpi.
The E5 historical before/after was about **188.6 -> 234.3 pt**, a 24% enlargement.
E6 does not claim a second enlargement. All 13 figure paths resolve; no borrowed image
was changed. The eight prior legibility failures remain disclosed; figure 12's estimated
tick size is 1.9 pt. It is a pattern overview, and its full meaning is explained in text.

**Basins:** the final P12 D7 rule is barrier >5 units and locally optimal endpoints, with
1--5 substructure and <1 noise. The 0.02 figure in E5 was the earlier jitter criterion,
not the final basin rule. P12 pre-registered the final rule before continuation results.
100 starts comprised 96 random points plus four anchors; 12 continuations, 11 converged.
The map is stable at 3/5/8 and its chord connectivity gives an upper bound on basin count.
Dead is a finite statistical score with negligible growth, not a feasible flux solution.
P13 explicitly retains the infeasibility mask: gap 11.691 -> 11.245 under clamp.

**Retractions:** no retraction framing retained. Original -4 K slide is byte-identical to
E6 baseline. Its adjacent slide preserves **0.079** units with one lever pinned versus
**7.600** with both pinned, peak **1.659 h^-1**, two prior bounds (Y3 task2b_meta.json and
task2c_bound.json). Synthesis prose predates these claims and contains neither dTm nor
basins; later evidence rows contain the corrected statements. No external correction
is implied beyond what the local records establish.

## 3. P16 numerical source ledger

P16 sources read at commit **191b4b0**, without merging or changing the primary worktree.

| deck statement | source and value |
|---|---|
| dTm fixed 0, 15 free | P16 D2/D3; summary_red1.json |
| Iterations / evaluations / wall time | summary_red1: 14,088 / 221,781 / 9.585 h |
| log evidence / uncertainty / ESS | summary_red1: -26.0298936831 / 0.1093582543 / 5987.5599 |
| Actual stopping statistic | trace_red1 final: 0.09999335448 |
| At previous crash iteration 11,547 | trace_red1: dlogz 0.665766, ncall 179,064; P15 recorded dlogz 2.168 |
| tm_scale marginal | task5_summary: 1.068839, 5/95 [0.793060,1.515456], near-bound mass 0 |
| tm_scale prior | P16 D4 and task5_posterior.py: [0.4,2.2] |
| MAP | D6: logL -10.704, peak 1.7255 h^-1 |
| Median vector | D6: logL -30.558; task5_r2.csv peak 0.0043073, growth R2 -2.01113 |
| Measured peak | task5_r2.csv: 2.076066941 h^-1 |
| Predictive draws | D6: 300 weighted draws, peak median 0.0016, 5/95 [0,1.7106], 50.7% below half measurement |

The summary JSON mislabels evidence uncertainty as dlogz_final; the slide uses the actual
trace stopping value. Quantile 1.515456 rounds to **1.515**, correcting the prompt's 1.516.
All P16 findings are labelled seed-1/provisional, and the full meltome-mean assumption is
on the slide. Absence of railing is an observation, not proof of global identifiability.
The 300 predictive draws were not re-solved: D6 is the source record. Their per-draw
solver statuses are not supplied, so 50.7% cannot establish the infeasible mass fraction.

## 4. Diagnosis, with the distinction preserved

P12 TASK 2's historical decomposition: live growth +6.363, respiration -13.549; dead
growth -18.860, respiration -0.017. Eleven of twelve dead temperatures are infeasible.
Current clamp excludes missing/non-positive O2. The slides label this as a diagnosis
under test, not a property of the model class and not a failed sampler run.

The gap ~11.7 gives exp(-11.7)=8.29e-6. Its fifteenth root is 0.4584: a rectangular
prior-volume illustration, not a measured basin volume or proof of the cause.
Separate marginal medians can fall far from likely joint combinations; the deck uses
the MAP and weighted predictions, showing the median vector only as a failed summary.

Q1 was read at **b163bad**. Contrary to E6's wording, Q1 diagnoses the conversion chain,
not the infeasible basin. It confirms the likelihood's per-cell O2 observable is invariant
to carbon-per-cell conversion, while CUE changes shape and level. CUE slide caveated.
Cooper's local bibliography entry is year 2001; its misleading 2007 key was corrected.

## 5. Next steps

The list has **33 words**, five bullets in the specified order, directly before the three
closing questions. Two preceding slides explain M9 and the three competing mechanisms.
The questions now ask about mechanistic discrimination, defensible infeasibility scoring,
and an external predictive test. Exactly three retained.

## 6. Render and layout verification

- Final artifact: `reports/ecoli_deck/_output/deck.pdf`.
- **56 source frames, 59 PDF pages**, versus baseline 49 / 52. Three reference pages.
- Quarto render exit 0; no overfull, unresolved-citation or missing-file warnings.
- Frame check exit 0: no source-frame tail missing from its page.
- All 59 pages rendered to PNG and inspected in contact sheets; revised evidence slides
  also inspected individually. Existing theme, aspect ratio, figures and hierarchy retained.
- Visual inspection caught unsupported Unicode superscript minus and oxygen subscripts;
  replaced with LaTeX math, then re-rendered and checked text extraction for missing glyphs.
- Figure check intentionally remains exit 1: the same eight borrowed figures fail the
  pre-existing tick-label threshold. All five locally generated figures pass.
- Report metadata and README updated to avoid their stale 20/40-page and P15-only claims.
- Provenance generated after content commits, then checked again after its own commit.

## 7. Change scope

The E6 diff from **bc356e3** is limited to docs/OPEN_ITEMS.md, reports/ecoli_deck/ and
reports/report_status.yaml. No E6 src/ or strains/ changes. The complete `git diff main
--stat` additionally contains inherited E4 Parsa-attribution corrections in two strain
text files and P2_settle; those precede E6 and were not reverted or enlarged. The PR stays
unmerged and no branch is pushed.

## Exact slide text and R4 reconciliation

### R4 on main before E5

| **R4** | **Predictively reliable** — holds out of sample | **Nothing has ever been tested against data it was not fit to** | Cooper 2007 (`refs/`): TPCs of *E. coli* lines after 20,000 generations. Predicting how a curve *shifts* under evolution is the real test of a temperature-dependence framework | ~1 day once R1 holds |

### R4 retained after E5/E6

| **R4** | **Predictively reliable** — holds out of sample | **Corrected 2026-09-11 (E5): one a priori test WAS run, and it half-succeeded.** `reports/ecoli_tpc/report.qmd` §563–570: the **uncalibrated** model predicts the exact-strain Van Derlinden curve with *"Nothing is fit to growth"* — it tracks the **shape** (T_opt, E_a) and under-predicts the peak **~2.3-fold** (1.04 against 2.40 h⁻¹). So shape held and magnitude did not. **What has no holdout is the CALIBRATED model**, because the calibration was then fitted to that same curve. The earlier wording — "nothing has ever been tested against data it was not fit to" — was wrong and undersold the work. | Cooper 2007 (`refs/`): TPCs of *E. coli* lines after 20,000 generations. Predicting how a curve *shifts* under evolution is the real test of a temperature-dependence framework, and it is the holdout the calibrated model still lacks | ~1 day once R1 holds |

### What a line scan is, and what it found

- **A transect through parameter space.** Start at the best fit, choose a parameter or combination, and step along it. Rebuild and solve the whole model at each point, recording fit quality
- **22 directions, 41 points each: 902 model builds.** Each step is 0.05 prior standard deviations. Each line spans $-1$ to $+1$ standard deviation
- **12 of 22 directions have a cliff.** One small step changes fit quality by more than one fifth of its total change along the whole line. Median largest jump: 39 % of that line's range, worst: 99 %
- Small parameter changes can therefore give abruptly worse fits and impede local searches. Two directions are flat. The next slide shows all 22 transects

### How many answers are there? First, what a basin is

- **A basin is a valley of the fitting problem.** Nearby starting parameters lead an optimiser towards the same good fit
- **A live basin predicts growth. A dead basin predicts essentially none**, although its parameters still receive a finite statistical score
- We screened **100 starts**, then continued 12 representative endpoints. **11 converged**. We scanned paths between endpoints to look for barriers in fit quality
- **The final rule was fixed before those results:** separate basins require a barrier above **5 log-likelihood units** and locally optimal endpoints. Barriers of 1--5 are substructure, below 1 is noise

### How many answers are there? The result

- **The map found one live and one dead region.** The result holds at barrier thresholds of 3, 5 and 8 units. Straight-line paths give an upper bound on the number of basins
- The dead region predicts peak growth **0.000 h$^{-1}$**, against a measured **2.076 h$^{-1}$**
- **Eleven of its twelve temperatures are infeasible:** the metabolic constraints admit no flux solution. Those temperatures receive no respiration score
- **The dead region survives the current support rule.** The live--dead likelihood gap changed only from 11.69 to 11.25 units. Infeasibility remains exempted from respiration scoring

### The reduced posterior: run 1 converged

- We fixed the uniform melting-temperature shift **$dT_m=0$**, leaving **15 free parameters**. Configuration D on the NLDM recipe, with the current respiration likelihood
- **The first clean nested run in this family:** 14,088 iterations, 221,781 likelihood evaluations, **9.585 hours**, no crash
- **Log evidence $\log Z=-26.030\pm0.109$**, effective sample size **5,988**. The recorded stopping statistic reached **0.09999**, below 0.1
- At the previous run's failure point, **iteration 11,547**, dlogz was **0.666 versus 2.168**, at a comparable evaluation count
- **Seed 2 is in flight. Independent confirmation is pending.** All posterior numbers shown here come from seed 1 alone

### The stopping and reproducibility rules

- **Pre-registered sampler:** `dynesty`, 800 live points, random-direction slice sampling (`rslice`, 3 slices), multiple ellipsoidal bounds
- **Stopping rule:** estimated remaining change in log evidence, **dlogz $<0.1$**. Evidence uncertainty is a separate quantity
- **Agreement requires both:** the two log evidences agree within their combined reported errors **and** no parameter median differs by more than two Monte-Carlo errors
- Seed 1 meets its stopping rule. **The two-seed agreement test has no result yet.** Sampler convergence alone does not establish useful biological predictions

### What the reduction assumes

- **`tm_scale` does not pile up at its upper bound:** median **1.069**, 5th--95th percentiles **[0.793, 1.515]**, prior bounds **[0.4, 2.2]**
- **0.00% of seed 1's posterior weight** lies within 5% of that upper bound. There is no observed boundary pile-up in this run
- The failed 16-parameter run identified a numerical difficulty in its remaining sampling points. **That geometry cannot be treated as the full posterior**
- **Fixing $dT_m$ assumes the meltome's mean is right.** Any uniform error in measured melting temperatures must now be absorbed by `tm_scale` and the catalytic parameters

### Run 1 assigns about half its weight to very low growth

Measured peak: **2.0761 h$^{-1}$**. Results below are provisional, from seed 1.

| summary | log likelihood | peak growth, h$^{-1}$ |
|:--|--:|--:|
| Best posterior sample (MAP) | **−10.704** | **1.7255** |
| Separate median of each parameter | −30.558 | 0.0043 |

- The MAP reaches **83% of the measured peak**
- **300 draws sampled using posterior weights:** median peak **0.0016 h$^{-1}$**, 5th--95th percentiles **[0.0000, 1.7106]**
- **50.7% of these draws grow below half the measured peak.** This estimates low-growth posterior mass, not the fraction proven infeasible

### Why separate parameter medians give a misleading model

- Correlated parameters work in combinations. Taking each parameter's median separately can put the resulting vector far from combinations that jointly fit well
- Here that vector predicts peak growth **0.0043 h$^{-1}$**, against **1.7255 h$^{-1}$** at the best posterior sample
- Its growth $R^2=-2.01$ describes this unrepresentative vector. It cannot summarise the predictive performance of the full posterior
- **Report the MAP alongside predictions drawn from the weighted joint posterior.** The median vector appears here only to show why it is unusable

### The infeasibility exemption: a diagnosis under test

Earlier basin-map scores, before the current support rule:

| log-likelihood contribution | live region | dead region |
|:--|--:|--:|
| Growth | +6.363 | −18.860 |
| Respiration | −13.549 | −0.017 |

- **The dead region gains about 13.5 units on respiration** because 11 of 12 temperatures have no feasible flux solution and receive no respiration score
- The current clamp still skips missing or non-positive oxygen uptake. It addresses feasible low growth, but leaves this exemption
- **Test now:** quantify infeasibility among low-growth posterior predictions and its contribution to their statistical weight. The basin example identifies a mechanism, not its share of the full posterior

### Why a converged posterior can favour poor predictions

- The earlier live--dead gap is about **11.7 log-likelihood units**, a **dead-to-live likelihood ratio of roughly $8\times10^{-6}$**
- Posterior mass also depends on **how much prior volume each region occupies**. A sufficiently larger dead region can outweigh that fit disadvantage
- Illustration only: in 15 dimensions, a live region occupying **46% of prior width per axis** has volume about $8\times10^{-6}$ of the full box. The actual regions need not be rectangular
- **The cause remains under test.** Seed 1 converged, but convergence does not validate the likelihood. This finding concerns this model and scoring rule, not enzyme-constrained models in general

### What happens next

- Confirm seed reproducibility against the pre-registered rule.
- Resolve the infeasibility exemption before further fits.
- Test D on fully defined M9.
- Compare D/E/F evidences on one medium.
- Measure glucose proteome allocation above 37 °C.

### Three questions for the group

1. **Which respiratory mechanism should the data distinguish?** A carbon cap, a membrane-area limit, or altered respiratory coupling? What independent measurement would make the evidence comparison convincing?

2. **How should infeasible predictions be scored?** We can identify the exemption. What observation model would make a model with no feasible flux solution appropriately unlikely?

3. **What would count as a strong external test?** Predicting thermal-curve shifts after 20,000 generations [@Cooper2001], or another held-out experiment? Glucose proteome measurements above 37 °C would constrain the uncertain allocation layer

