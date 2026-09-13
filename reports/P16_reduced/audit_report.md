# P16 completed-run audit — 12 September 2026

**Verdict: both runs converged by the stopping rule, but DISAGREED by P16 D3. The reduced
posterior is not independently reproduced. The addendum's inferred geometry is also not stable
between seeds. No second parameter was fixed and no new sampler or fit was launched.**

**Scope of every table and number:** dTm is fixed at zero. This posterior assumes the measured
meltome mean is exactly right; any uniform error must be absorbed by tm_scale and catalytic
parameters. These are diagnostics of two disagreeing runs, not a validated full-model posterior.

## 1. The pre-registered agreement rule

D3 requires log Z within combined reported error **AND** no marginal median separated by more
than two Monte-Carlo errors. Both conditions matter. The evidence difference is **0.022486**,
combined error **0.147777**, or **0.1522** errors: PASS. **14/15 medians FAIL**, so the overall
verdict is **DISAGREED**, not a successful posterior with an optional caveat.

| diagnostic | seed 1 | seed 2 |
|---|---:|---:|
| free dimensions / fixed parameter | 15 / dTm=0 | 15 / dTm=0 |
| iterations | 14,088 | 12,495 |
| likelihood calls | 221,781 | 197,844 |
| wall time, h | 9.585 | 7.966 |
| log Z | -26.029894 | -26.052380 |
| reported log Z error | 0.109358 | 0.099392 |
| actual final dlogz | 0.09999335 | 0.09995762 |
| importance-weight ESS | 5,987.56 | 3,252.25 |
| best saved log L | -10.704111 | -12.704332 |

Settings match: 800 live points, rslice/3 slices, multi bound, 16 processes, 16-hour cap,
checkpoint every 30 minutes. The saved runner fixes first_update min_eff=30.
No crash occurred, so the crash-specific instruction to stop after diagnosing a new direction
was not triggered. The agreement failure nonetheless blocks promoting TASK 5's interpretation.

The runner's **dlogz_final field is wrong in both summaries**: it contains logzerr. The actual
stopping quantities above come from trace_red1/trace_red2. Both pass despite that reporting bug.

### Fifteen medians and the implemented agreement test

The natural-unit medians below are individual marginal summaries, never a joint fitted vector.
The errors column is calculated in the sampled coordinates, matching P16's implementation.

| parameter | median_seed1 | median_seed2 | mc_errors | passes |
|---|---|---|---|---|
| dTopt | 12.0791 | 12.1683 | 1.5635 | True |
| topt_scale | 1.09505 | 1.22762 | 55.5938 | False |
| dCp_scale | 1.50573 | 1.29556 | 13.4175 | False |
| tm_scale | 1.06884 | 0.956216 | 25.5988 | False |
| kcat_scale | 0.950925 | 0.788178 | 30.9746 | False |
| kappa_scale | 0.916997 | 0.849746 | 11.6232 | False |
| sigma | 0.595299 | 0.217787 | 103.907 | False |
| f_metab | 0.259147 | 0.269411 | 31.6951 | False |
| f_maint | 0.36626 | 0.37503 | 37.2108 | False |
| ngam_scale | 1.52539 | 1.33878 | 24.8509 | False |
| ngam_steepness | 1.30169 | 1.0123 | 55.9705 | False |
| clearance_mult | 1.03949 | 0.995928 | 14.6078 | False |
| resp_scale | 2.90803 | 0.682274 | 195.672 | False |
| disc_resp | 0.374811 | 0.58677 | 53.6948 | False |
| disc_growth | 0.844972 | 1.0021 | 40.1888 | False |

P16's existing `mc` method resamples independent points from fixed posterior weights, using
200 replicates of length equal to the stored sample count. It estimates resampling variation
conditional on this run, **not the full uncertainty of nested sampling**; the quoted scores of
up to 196 errors should not be treated as calibrated Gaussian significance.

As a supplementary check, dynesty.utils.resample_run bootstrapped 100 sets of complete nested
sampling strands per seed, with no likelihood calls. **The same 14 medians fail**. Examples:
sigma 33.6 errors, resp_scale 86.7, tm_scale 10.2, f_metab 15.7. This is not a replacement rule
chosen to rescue the result. Bootstrap procedures also cannot account for regions never explored.

## 2. Addendum 1: eigendecomposition alongside marginals

The prior transform maps independent priors to a uniform 15-dimensional unit cube. The audit
uses that cube, exactly as D4 specifies. Covariances use importance weights and the existing
finite-weight correction 1/(1-sum(w^2)); widths are sqrt(12*eigenvalue).
D4 classifications: CONSTRAINED <0.5, PRIOR-DOMINATED >0.8, intermediate otherwise.

| classification | seed 1 | seed 2 |
|---|---:|---:|
| CONSTRAINED | 4 | 6 |
| INTERMEDIATE | 6 | 6 |
| PRIOR-DOMINATED | 5 | 3 |

These are per-run classifications, **not an established count of biologically identified
combinations**. Directions can rotate between seeds; equal rank does not mean equal loadings.
An eigenvalue-derived width above 0.8 is the registered category name, not proof of equality
to the prior distribution (some widths exceed 1 substantially).

| direction | eigenvalue_seed1 | width_ratio_seed1 | eigenvalue_seed2 | width_ratio_seed2 |
|---|---|---|---|---|
| 1 | 0.00298868 | 0.189378 | 0.00213626 | 0.16011 |
| 2 | 0.00781249 | 0.306186 | 0.00488984 | 0.242236 |
| 3 | 0.0150463 | 0.424918 | 0.0100442 | 0.347175 |
| 4 | 0.0187393 | 0.474206 | 0.0125482 | 0.388044 |
| 5 | 0.0248791 | 0.546397 | 0.0179321 | 0.46388 |
| 6 | 0.025783 | 0.556234 | 0.0181039 | 0.466098 |
| 7 | 0.0305476 | 0.605451 | 0.0234994 | 0.531029 |
| 8 | 0.0336431 | 0.635388 | 0.026327 | 0.562071 |
| 9 | 0.0387512 | 0.68192 | 0.0297381 | 0.597375 |
| 10 | 0.0501196 | 0.775523 | 0.0328057 | 0.62743 |
| 11 | 0.0599533 | 0.848198 | 0.0446804 | 0.732233 |
| 12 | 0.0783591 | 0.969695 | 0.0497868 | 0.772943 |
| 13 | 0.0919993 | 1.05071 | 0.0782365 | 0.968937 |
| 14 | 0.126309 | 1.23114 | 0.181506 | 1.47583 |
| 15 | 0.446449 | 2.3146 | 0.324352 | 1.97287 |

**All fifteen loadings for every direction in each seed:** `audit_eigendecomposition.csv`.
Full covariance matrices: `audit_covariance_red1.csv`, `audit_covariance_red2.csv`.
All marginal medians, 5/95 intervals and prior width comparisons: `audit_marginals.csv`.
Thus the requested eigendecomposition accompanies, rather than replaces, the marginals.

## 3. Addendum 2: the pair prediction does not reproduce

First, the original `task5_posterior.py:144` computes unweighted correlations, despite its
weighted covariance. Those correlations mix nested samples without their posterior weights.
D5 copied them. The corrected values are:

| seed | pair | P15_correlation | weighted_correlation | narrow_pair_width | broad_pair_width |
|---|---|---|---|---|---|
| red1 | sigma~kcat_scale | -0.857 | 0.370371 | 0.808741 | 1.27873 |
| red1 | dCp_scale~dTopt | -0.853 | -0.639407 | 0.557938 | 1.21175 |
| red1 | kappa_scale~tm_scale | 0.804 | 0.2982 | 0.787489 | 1.24965 |
| red2 | sigma~kcat_scale | -0.857 | 0.307026 | 0.64515 | 1.0767 |
| red2 | dCp_scale~dTopt | -0.853 | -0.392932 | 0.609512 | 1.06641 |
| red2 | kappa_scale~tm_scale | 0.804 | -0.0400165 | 0.852452 | 0.970521 |

The last two columns are supplementary eigen-widths **within each two-parameter subspace**,
using the same unit-cube scale. Each broad direction exceeds 0.8, but **none of the narrow
orthogonal directions reaches <0.5**. Thus the specific picture of a broad pair direction with
a tightly constrained orthogonal complement is not observed in these runs. Globally, the full
15-variable covariance contains narrower combinations; those involve additional parameters.

Crucially, failure of that prediction **does not imply that the parameters are individually
identified**. Their individual cube-width ratios are mostly near or above 0.8, and the two runs
do not agree. Choosing the global eigenvector with the largest pair loading and calling the pair
identified is insufficient: that vector also contains other parameters.

D5 therefore needs qualification: the quoted correlations were wrong, and the statement that
the data constrain these parameters individually is not established. What survives is that
P15's live-point geometry did not predict these sampled distributions. Late nested live points
occupy a likelihood-constrained region, not the full posterior (nor literally a single exact
iso-likelihood shell). Fixing dTm also changes the model, so the discrepancy cannot be attributed
to live-point weighting alone. No confirmed posterior exists here to settle that extrapolation.

A numerical slip in the addendum: only two listed absolute correlations exceed 0.831; 0.804
is smaller. All three requested pairs were nevertheless tested.

## 4. Addendum 3: no tm_scale railing, but no stable tail inference

Prior bounds **[0.4,2.2]**, dTm fixed at 0 in both runs.

| tm_scale marginal | seed 1 | seed 2 |
|---|---:|---:|
| median | 1.068839 | 0.956216 |
| 5th percentile | 0.793060 | 0.782855 |
| 95th percentile | 1.515456 | 1.228116 |
| posterior weight at tm_scale >=2.09 | 0 | 0 |

Neither shows mass piled at the upper boundary, under D4's definition. **This excludes that
particular warning sign in the saved runs; it does not establish that the reduction solved
posterior exploration.** The second seed's 95th percentile is below the 1.32--1.62 range the
TASK 2 calculation associated with the 4--6 K tail shift.

Using the previously recorded mean-to-quantile distances (task5_tail.csv) and the code's
mean-centred tm_scale definition, the shifts below are relative to the measured meltome.
Negative means lower Tm. No model build or solve is needed for this arithmetic.

| seed | percentile | median_shift_K | lo5_shift_K | hi95_shift_K |
|---|---|---|---|---|
| red1 | 1 | -0.85823 | -6.42629 | 2.57997 |
| red1 | 2 | -0.814712 | -6.10044 | 2.44914 |
| red1 | 5 | -0.667778 | -5.00022 | 2.00744 |
| red2 | 1 | 0.545863 | -2.84396 | 2.70719 |
| red2 | 2 | 0.518184 | -2.69976 | 2.56992 |
| red2 | 5 | 0.424729 | -2.21285 | 2.10643 |

The seed-2 interval does not reach a 4 K downward shift for any of these three quantiles.
Because R1 fails, this does **not** refute Y3's result about selected growing fits. It shows
that a statement about those fits cannot be promoted to the whole posterior on this evidence.

## 5. Addenda 4 and 5

The meltome-mean assumption appears at the top and applies to every displayed table. Neither
run is a posterior over the original 16-parameter model. No second parameter was fixed and
no replacement sampler was launched. There was no repeat crash to diagnose.

## 6. A stronger diagnostic from the inactive parameter

The current growth-law code ignores sampled f_metab (enzyme_cost.set_allocation). Its support
[0.15,0.45] and f_maint support [0.20,0.50] also make the simplex guard non-binding throughout.
With independent priors, its exact marginal should therefore equal its truncated prior.
In unit-cube coordinates that is Uniform(0,1), with mean 0.5 and SD 0.288675.

| seed | f_metab_unit_mean | expected_mean | f_metab_unit_sd | expected_sd | weighted_KS_to_uniform | logz_strand_sd |
|---|---|---|---|---|---|---|
| red1 | 0.31912 | 0.5 | 0.259033 | 0.288675 | 0.290878 | 0.086119 |
| red2 | 0.393715 | 0.5 | 0.22228 | 0.288675 | 0.216146 | 0.0855648 |

The substantial departures cannot represent information the biological likelihood learned
about f_metab. They are a practical null test for the computational inference. Restored samples
match saved arrays, weight sums are one to ~1e-13, ESS values reproduce, and an independent
inverse-CDF calculation matches saved unit-cube positions to floating-point precision. Those
checks rule out simple row/weight/coordinate misalignment in this audit.

This warrants an investigation of constrained-prior exploration and sampling correlations,
using inactive coordinates as controls. It does not by itself prove whether slice mixing,
bounding, numerical likelihood behaviour or another implementation issue is responsible.
Removing the inactive parameter is sensible housekeeping; fixing another active parameter to
make these results agree would not be justified.

## 7. Original prompt aims: what is complete and what remains open

| task | evidence and audit verdict |
|---|---|
| 0: inherited state | Existing log records 79/79 and 60/60, state JSON ten-evaluation spread 0. Those checks were not rerun in this audit. |
| 1: full P15 spectrum | Stored 16 eigenvalues/loadings, 1e-3 relative threshold, exactly one qualifying direction. Its live-point interpretation needs the qualification above. |
| 2: choice | dTm=0, mean-centred tm_scale, hidden mean uncertainty recorded. Rotation considered in the existing decisions. |
| 3: synthetic check | Stored condition 458.05 versus 708.17 if tm_scale fixed. Fixing dTm alone at p38 costs 50.32 logL units; the much smaller Y3 cost required other parameters to compensate. |
| 4: runs | Both stop successfully; agreement FAILS. No new run authorised by this success criterion. |
| 5: posterior | Per-seed diagnostic marginals/eigenspectra/tails now supplied. A validated posterior interpretation is BLOCKED by agreement. Existing script lacks requested line scans and the two carried predictions. |
| 6: reconciliation | This audit and dated decision/OPEN_ITEMS notes correct the conclusion. No claim that the remaining D/E/F programme is unblocked. |

The two original predictive checks remain **unassessed**: mass within 1% of _MASK_G compared
with P11, and posterior-predictive growth at 15 C compared with P11. The stored TASK 5 code
implements neither; audit_pairs.csv concerns the separate addendum's geometry prediction.
Also outstanding: line-scan GRADIENT/WALL/FLAT classification, the MAP/predictive R2 reporting
required by D6, and seed-2 replication of the low-growth predictive fraction. D6's 300-draw
seed-1 result is not evidence that seed 2 has the same fraction, and D6's claim that sampling
failure has been ruled out is now too strong.

No fresh predictive solves were undertaken to dress a failed agreement gate as completed
TASK 5. No sampler changes, parameter fixes, core edits, merges or changes to the deck.

**R1 is not closed. R2 is clarified by detecting inactive-parameter sampling and unstable
geometry, not by certifying identified directions. R3's stability/mechanism interpretation
remains provisional. R4 predictive validation was not advanced.**

## Reproduce

Run in the project virtual environment:

```sh
python reports/P16_reduced/audit_completed_runs.py
python reports/P16_reduced/audit_sampling_uncertainty.py
```

Original run outputs, checkpoints and previous TASK 5 tables remain unchanged. Audit files
have separate names. The Monte-Carlo bootstrap supplements the original rule and does not
replace it. `audit_inputs.json` hashes the principal run arrays and summaries used here.
