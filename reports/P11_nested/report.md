# P11 — the last wall, an absolute smoothness rule, and a sampler matched to a piecewise surface

| task | status | one line |
|---|---|---|
| **0** — the floor and the absolute rule | **DONE — SAMPLEABLE** | floor 0.76 → 1.42 (the largest measured vertex jump); all twelve of P9's lines under 5 log-likelihood units, largest 3.53; P9's relative rule would still read ROUGH, which is why the rule changed |
| **1** — dynesty wired | **DONE** | prior transform proven to 3.5e-14; pool path exact; toy log Z within 0.93 sigma; checkpoint restore reproduces log Z to 0.005 |
| **2** — the run | **CONVERGED** | dlogz **0.100**, n_eff **4,052**, log Z **−22.886 ± 0.164**, 7,118 iterations, 111,420 evaluations, **4.8 h** — stopped on its own criterion, 4 h inside the budget |
| **3** — the posterior | **DONE** | no median outside P4's invalid intervals; 10 narrower, 6 wider; **11 gradient-determined, 0 wall-bounded, 5 flat**; growth R² 0.900 against P4's 0.854, respiration 0.626 against 0.795 |
| **4** — the rest, costed | **DONE** | ≈ 33 h for seven fits; F LB held |
| **5** — the record | **DONE** | 1.12 and 1.15 closed, two PI items, the absolute-rule hazard, four evidence rows, the synthesis note |
| — second seed | **INCOMPLETE** | started 04:04 at nlive 250; had not converged by the morning; outstanding as a PI item |

Detail: [DECISIONS.md](DECISIONS.md) (D0–D6). Scripts beside this file:
`prior_transform.py`, `task1_prove_transform.py`, `toy.py`, `task1_pool_check.py`,
`task1_checkpoint.py`, `run_nested.py`, `task0_two_rules.py`, `task3_posterior.py`,
`task3_identifiability.py`, `task3_r2.py`, `task4_costs.py`.

---

## TASK 0 — the floor, the rule, and the surface under both readings

PR #25 merged → `97411f1`; `p11/nested`; gates with the options OFF **79/79 and 60/60**, seven
strains byte-identical.

**The floor: 0.76 → 1.42.** P10 set it from the largest jump at the *modal* cliff temperature
(20 °C: 0.759). The largest measured vertex jump anywhere in that scan is **1.4216**, on the
`dCp_scale` line between +0.90 and +0.95 sd, carried by **25 °C** — the step that still cost 7.8
units and left the surface rough. The cost is stated rather than hidden (D0): the respiration
sd is now at least 1.42 in log at every temperature, a factor-4 band on O2, and the three cold
points whose measured relative sd is 0.06–0.09 lose most. The growth term is untouched.

**The absolute rule, written before the re-scan** (D0, verbatim): *a line is SAMPLEABLE if no
single 0.05 sd step exceeds 5 log-likelihood units; the surface is SAMPLEABLE if every line is.*
What decides whether a sampler can cross a step is the likelihood ratio across it: e^−30 is a
wall, e^−2 is a kink. A relative rule was the right instrument while the cliffs were 13–72 units
and the ranges 15–137; the floor shrinks the ranges along with the cliffs, so a relative rule
then flags kinks that are not obstacles.

**P9's twelve lines under the new floor, both readings** (`task0_two_rules.csv`; ±1 sd at
0.05 sd, fresh model per evaluation, 54 min):

| line | before P10 | floor 0.76 | **floor 1.42** | % of range | range | ≤ 5 units? |
|---|---|---|---|---|---|---|
| dCp_scale | 71.78 | 7.83 | **3.53** | 16.3 | 21.70 | yes |
| topt_scale | 19.95 | 3.21 | **3.20** | 20.3 | 15.75 | yes |
| kcat_scale | 12.64 | 1.61 | **1.50** | 8.5 | 17.76 | yes |
| random1 | 35.73 | 2.45 | **1.21** | 8.5 | 14.24 | yes |
| random2 | 13.58 | 0.90 | **0.87** | 9.0 | 9.70 | yes |
| PC2 | 22.79 | 2.18 | **0.83** | 23.2 | 3.59 | yes |
| PC1 | 18.46 | 0.88 | **0.71** | 10.7 | 6.61 | yes |
| PC3 | 11.81 | 0.68 | **0.65** | 7.9 | 8.33 | yes |
| random3 | 14.75 | 0.37 | **0.25** | 8.0 | 3.12 | yes |
| ngam_scale | 18.40 | 0.38 | **0.22** | 10.3 | 2.13 | yes |
| clearance_mult | 16.71 | 0.14 | **0.10** | 9.5 | 0.99 | yes |
| f_maint | 18.19 | 0.10 | **0.06** | 9.1 | 0.71 | yes |

**SAMPLEABLE: 12 of 12**, largest step **3.53 units**. Median sign changes 1. **P9's relative
rule on the same data still reads ROUGH** — two lines (PC2 23.2 %, topt_scale 20.3 %) exceed
20 % of ranges that are now 3.6 and 15.8 units — which is precisely why the rule changed.

The two largest remaining steps are the ones the two decisions predicted: `dCp_scale`'s 3.53 is
the single O2 vertex jump the floor is now sized on, and `topt_scale`'s 3.20 is **entirely a
growth-term kink** (P10 attributed it: growth 0.189 → 0.146 across one step at 25 °C), unchanged
from floor 0.76 because no respiration change touches it. Both are reported, not fixed.

## TASK 1 — dynesty behind the same likelihood

**dynesty 3.1.0**, added to `requirements.lock.txt`. One thing went into the core: `_gwloglike`,
the gas-flux log-likelihood on a worker's own ctx without the prior — the callable a sampler
that handles the prior itself needs, beside the `_gwlogprob` the MCMC runs used. Everything
else (the transform, the runner, the checks) lives in `reports/P11_nested/`, because
`src/etcgem/` is the seven-strain core and a sampler used by one report is not core
infrastructure until a second report needs it; the worker callable had to be core because a
process pool imports it from an installed module (D1).

**The prior transform** is the inverse CDF of each of P4's priors, truncated to its hard
support, in the space `log_prior` scores: the natural value for `normal`, its log for
`lognormal`, and for `halfnormal` inverted in the natural value and returned as its log — whose
Jacobian is exactly the `+theta` term `log_prior` adds. Proven two ways:

* **10,000 draws** against `scipy.stats.truncnorm`: every marginal mean within **1.58**
  Monte-Carlo standard errors, worst quantile error 0.127 (on dTopt, whose prior spans 30);
* **a 200-point grid per parameter**: the difference between `log_prior`'s contribution and the
  transform's implied log-density is constant to **3.6e-14** for all sixteen.

The first version of that second check disagreed by exactly 8.0 and 10.8 on the two
half-normals — the range of their log-Jacobian — which was the check comparing spaces, not the
transform being wrong. Recorded because it is the kind of error that looks like a bug in the
thing being tested.

**The pool path is exact.** `_gwloglike` through a 16-worker pool against a single-process
evaluation on a freshly built provider, at three points: **max |difference| 0.0e+00**, i.e.
identical, well inside the 1e-4 P7 measured. Throughput **0.141 s per evaluation of wall
clock** (32 evaluations over 16 workers in 4.5 s).

**The toy.** A 16-dimensional correlated Gaussian with P8's covariance (condition number 50)
under a uniform prior on a 12-sd box, log Z analytic: dynesty returns
**-72.90 ± 0.30 against -73.18** — 0.93 sigma — with the posterior means within
2.8 Monte-Carlo errors and a median relative covariance error of 0.055. 20760 iterations,
1,913,532 calls.

**Checkpointing.** A run halted at 301 iterations, restored from disk and continued to
602, reaches log Z -313.056 ± 2.357 against an uninterrupted run's -313.051 ± 2.356 —
a difference of **0.005, 0.00 combined sigma**. (dynesty's `maxiter` counts per call, not
cumulatively; the first attempt at this proof ran the restored sampler 601 iterations *past* the
checkpoint and compared 902 iterations against 601. Recorded for the same reason as above.)

## TASK 2 — the run

**Settings, pre-registered in D2 and unchanged throughout:** nlive **400**, `bound="multi"`,
`sample="rslice"`, `slices=3`, `queue_size=16`, dlogz 0.1, seed 1, 16 processes, initialised from
the prior through the transform. The wall-clock budget was raised from 4 h to 08:00 on the
user's instruction at 23:04 (D5); nothing else changed, and the run continued from its
checkpoint (**resume 1**, at iteration 1,585 / 17,354 evaluations).

*A reporting caveat, stated because the file says otherwise:* `summary_main.json` records
`"nlive": 500` and `"hours_cap": 4.0`. Those are the **argument defaults of the resume
invocation**, not the run: the sampler was restored from the checkpoint, so its nlive is the
400 the original process created — verified directly on the restored object — and the deadline
in force was 08:00.

**The stopping rule, quoted from D2 before the run:** *CONVERGED if dynesty reaches dlogz < 0.1
within the cap and the posterior n_eff is ≥ 600; STALLED if the cap is hit first.*

**Result: CONVERGED.** dynesty stopped on its own criterion at **03:53**, 4 h 11 m before the
deadline.

| | |
|---|---|
| iterations | **7,117** |
| likelihood evaluations | **111,420** |
| wall clock | **4.81 h** |
| evaluations per second across the pool | 6.43 |
| calls per iteration | 15.7 |
| sampling efficiency | 6.75 % |
| final dlogz | **0.100** (target 0.1) |
| **log Z** | **-22.886 ± 0.164** |
| **posterior n_eff** | **4,052** (target ≥ 600) |

Both conditions are met. The run's own information measure ended at **H = 9.22 nats**, and the
standard estimate nlive × (H + 3√H) = 7,334 iterations against the 7,118 actually taken — the
projection in D6 (4,000–6,000 iterations from H = 4.13, revised upward as H grew) was the right
order and low, because H kept climbing.

**The trajectory** (`run.log`, one line per 250 iterations): dlogz fell 10.15 → 8.46 → 6.88 →
5.67 → 6.40 → 5.59 → 5.56 → 4.81 → 4.62 → 4.53 → 3.69 → 3.13 → 2.56 → 1.84 → 1.36 → 1.09 →
0.68 → 0.65 → 0.38 → 0.22 → 0.19 → 0.10. It is not monotone in the short run — the rise at
iteration 2,840 is the live points finding a better maximum — but it falls throughout, which is
the property that makes extending a nested run legitimate where extending an MCMC chain is not
(D5).

**Throughput and what it cost.** The first ~1,250 iterations ran on **one core** and took 62
minutes: dynesty samples uniformly from the prior until efficiency drops below 10 %, and only
then engages the pool (D4). Measured after the switch: **8.5 of 16 cores**, with the main
process at **0.0** — so bound updates and bootstrap are not the bottleneck and `queue_size` was
already 16; the shortfall is the straggler effect of mapping sixteen variable-length slice
chains. No setting was changed mid-run. **For a future run, `first_update={'min_eff': 30}` is
the first thing to change**, and it would have saved most of an hour.

**Reproducibility.** The prompt's second-seed run (nlive 250, seed 2) was started at 04:04 and
@@SEED2@@

Beside it, the check dynesty makes available from the run itself: the prior-volume shrinkage at
each iteration is random, and resampling it 200 times (`task2_jitter.py`) gives
**log Z = -22.925 ± 0.149** against the reported -22.913 ± 0.152, with the posterior
medians stable to between 0.0004 and 0.05 in natural units. That is not an independent seed — it
re-rolls the volumes, not the sampling — and is reported as what it is.

## TASK 3 — the posterior

**How it is summarised.** dynesty's importance weights w = exp(logwt − log Z) are resampled to
equal weight (`resample_equal`, seed 42), so every median and 5/95 interval below is an ordinary
sample quantile of an equally weighted draw of 7,517 points.

| parameter | P4 median | **P11 median** | shift | P4 90 % width | P11 90 % width | ratio | P11 width / prior | identifiability |
|---|---|---|---|---|---|---|---|---|
| dTopt | 3.182 | **1.514** | -1.67 | 11.2 | 14.4 | 1.28 | 0.48 | Gradient |
| topt_scale | 0.9273 | **0.894** | -0.0333 | 0.565 | 0.487 | 0.86 | 0.65 | Gradient |
| dCp_scale | 1.529 | **2.205** | +0.675 | 2.61 | 2.51 | 0.96 | 0.67 | Gradient |
| dTm | -3.682 | **-3.92** | -0.238 | 8.58 | 6.31 | 0.73 | 0.21 | Gradient |
| tm_scale | 1.008 | **1.001** | -0.00635 | 0.483 | 0.422 | 0.88 | 0.23 | Gradient |
| kcat_scale | 1.441 | **1.323** | -0.118 | 3.14 | 1.39 | 0.44 | 0.12 | Gradient |
| kappa_scale | 1.033 | **1.057** | +0.0241 | 2.06 | 1.36 | 0.66 | 0.12 | Flat |
| sigma | 0.7302 | **0.8454** | +0.115 | 0.476 | 0.643 | 1.35 | 0.68 | Gradient |
| f_metab | 0.292 | **0.2886** | -0.00343 | 0.103 | 0.0754 | 0.74 | 0.25 | Flat |
| f_maint | 0.3545 | **0.3652** | +0.0107 | 0.0893 | 0.064 | 0.72 | 0.21 | Flat |
| ngam_scale | 1.313 | **1.483** | +0.17 | 1.81 | 1.96 | 1.08 | 0.33 | Gradient |
| ngam_steepness | 0.8832 | **0.751** | -0.132 | 1.85 | 1.31 | 0.71 | 0.22 | Flat |
| clearance_mult | 0.9551 | **0.7786** | -0.176 | 0.927 | 0.749 | 0.81 | 0.47 | Flat |
| resp_scale | 3.927 | **3.509** | -0.418 | 3.43 | 5.41 | 1.58 | 0.11 | Gradient |
| disc_resp | 0.3493 | **0.3132** | -0.0361 | 0.445 | 0.605 | 1.36 | 0.20 | Gradient |
| disc_growth | 0.2349 | **0.1766** | -0.0583 | 0.501 | 0.951 | 1.90 | 0.19 | Gradient |

**Which medians moved outside P4's intervals: none — 0 of 16.** That is worth stating plainly,
because P4's intervals were invalid (chains at ~9 autocorrelation times on a cliffed surface) and
the honest prior expectation was that some would move. They did not: the under-converged medians
were, in the event, close to the converged ones. **Ten intervals are narrower and six wider.**
The six that widened are exactly the ones the new likelihood loosens — `disc_growth` (×1.90),
`resp_scale` (×1.58), `disc_resp` (×1.36), `sigma` (×1.35), `dTopt` (×1.28), `ngam_scale`
(×1.08) — and the sharpest narrowing is `kcat_scale` (×0.44).

**Identifiability, by the rule written before the posterior existed** (D3; one line scan per
parameter through the new median, ±1 *posterior* sd, fresh model per evaluation):

* **GRADIENT-DETERMINED (11)** — `dTopt`, `topt_scale`, `dCp_scale`, `dTm`, `tm_scale`, `kcat_scale`, `sigma`, `ngam_scale`, `resp_scale`, `disc_resp`, `disc_growth`. The likelihood is a
  curve over the posterior's own width and no step exceeds 25 % of the range; these are credible
  intervals in the ordinary sense.
* **WALL-BOUNDED (0)** — **none**. This is the headline of the classification: after the
  tie-break and the floor, not one of the sixteen has its interval set by a step in the
  likelihood. Before P10 every line through the MAP had cliffs of 13–72 units.
* **FLAT (5)** — `kappa_scale`, `f_metab`, `f_maint`, `ngam_steepness`, `clearance_mult`. The log-likelihood ranges by less
  than 1 unit over ±1 posterior sd (`kappa_scale` and `f_metab` by **exactly 0.000**), so the
  data do not distinguish these locally at all: their posteriors are their priors, shaped only
  by correlation with the rest. `clearance_mult` being here is the sharpest form of the standing
  finding that the medium ceiling K is a prior choice (OPEN_ITEMS 1.12, P4's 0.57–0.64 width
  ratio); it is now not merely weakly identified but locally flat.

**The respiration scale.** `disc_resp` = 0.313 (90 % 0.052–0.657), on top of a
floor of 1.42 and measured relative sds of 0.06–0.38. So the model's respiration precision, as
the posterior sees it, is dominated by the floor: total sd = sqrt(rel² + 0.31² + 1.42²) ≈ 1.45–1.50
in log O2, a factor of about 4.3. The fitted discrepancy adds ~2 % to that in quadrature. The
posterior is not being asked to believe the model predicts respiration better than a factor of
four, and it does not.

**R² at the posterior median** (P4's scorer, dense grid, interpolated onto the observed
temperatures):

| point | scored under | growth R² | respiration R² | r_max | T_opt | sigma |
|---|---|---|---|---|---|---|
| **P11 nested median** | the new likelihood | **0.8997** | **0.6258** | 1.624 | 39.5 | 0.845 |
| P11 nested median | P4's scoring (no tie-break) | 0.8997 | 0.6261 | 1.624 | 39.5 | |
| P4 median | the new likelihood | 0.8544 | 0.7951 | 1.561 | 41.0 | 0.723 |
| P4 median | P4's scoring (no tie-break) | 0.8544 | 0.7952 | 1.561 | 41.0 | |

The converged median fits **growth better** (0.900 against 0.854) and **respiration worse**
(0.626 against 0.795) than P4's. That is the floor doing exactly what it was built to do: with
respiration granted a factor-4 band, the posterior stops paying for respiration residuals and
buys growth instead. Anyone quoting a respiration R² from this fit must quote the floor beside
it. The tie-break changes nothing here (0.6258 against 0.6261) because configuration D's O2 was
already unique — as predicted.

**Where sigma sits.** P4 observed sigma landing near the literature 0.45–0.50 on M9 and railing
toward ~0.7 on rich media. Converged on NLDM it is **0.845** (90 % 0.338–0.980), against
P4's under-converged 0.723 — further from the literature value, not closer, and pressed
against its prior's upper bound of 1.0. It is GRADIENT-DETERMINED, so this is the data speaking
and not a wall: on the recipe NLDM medium this model wants a saturation fraction the literature
does not support, and converging the posterior sharpens that disagreement rather than resolving
it.

## TASK 4 — what the rest would cost

From this run's measured **111,420 evaluations in 4.81 h** — 0.155 s per evaluation of wall
clock across 16 processes — scaled by P10's per-fit tie-break cost (`task1_cost.csv`), assuming
each fit needs a comparable number of evaluations. Nothing was run.

| fit | status | relative cost per evaluation | projected hours | note |
|---|---|---|---|---|
| D_NLDM | MEASURED (this run) | 1.00 | 4.8 |  |
| D_LB | projected | 0.94 | 4.5 |  |
| D_M9 | projected | 1.00 | 4.8 |  |
| E_NLDM | projected | 0.98 | 4.7 |  |
| E_LB | projected | 1.03 | 5.0 |  |
| E_M9 | projected | 1.00 | 4.8 |  |
| F_NLDM | projected | 0.99 | 4.8 |  |
| F_M9 | projected | 1.00 | 4.8 |  |
| F_LB | HELD | 1.03 | — | no tie-break at 1e-9 (P10 D1): its likelihood is still not a function of theta |

**The seven not yet run come to ≈ 33 h**, and F LB is **HELD** — P10 D1 found its tie-break is
still not exact at 1e-9, so its likelihood is not yet a function of its parameters and no
sampler should be pointed at it. Two caveats on the projection: it assumes the same iteration
count, and the iteration count scales with each fit's own information H, which is not measured
for the other eight; and about an hour of this run was the single-core unit-cube phase, which
`first_update` would remove.

## TASK 5 — the record

* **`docs/OPEN_ITEMS.md`**: **1.12 closed** with the verdict — the first converged posterior in
  this family, and the statement that the convergence problem was never a sampling budget;
  **1.15 closed** with the route taken and the two decisions executed; **1.13 and 3.21** stand as
  P10 left them (F LB still held). Two new PI items: **run the remaining eight fits (≈ 33 h) or
  not**, and **finish the second-seed check**. New standing hazard in §4: *a smoothness rule must
  be absolute in log-likelihood units; a relative rule flags kinks once the cliffs are gone.*
* **`reports/synthesis/evidence.csv`**: rows **P11a** (the floor), **P11b** (the sampleability
  verdict under both rules), **P11c** (the converged run), **P11d** (the identifiability
  classification).
* **`reports/synthesis/README.md`**: the correction note now says section 7 needs *rewriting*
  rather than annotating — the convergence finding was a cliffed likelihood, not a step budget —
  and names what resolved it and where the numbers that were waiting on P6 now come from.
* Stamps regenerated; `report_status.yaml` gains `P11_nested`.

## Verification

| check | result |
|---|---|
| TASK 0: #25 merged; gates; the floor old/new with its source; the absolute rule quoted from before the scan; the two-rule table; SAMPLEABLE | `97411f1`; **79/79 and 60/60** with the options OFF; 0.76 → **1.42** from `task2_jumps.csv` (dCp_scale, +0.90→+0.95 sd, 25 °C); rule quoted in D0 and above; twelve lines tabulated; **12 of 12 pass**, largest 3.53 units |
| TASK 1: dynesty version; transform proven on 10,000 draws; pool == single process at the MAP; toy log Z and moments; checkpoint resume proven | **3.1.0**; means within 1.6 MC errors and log-density constant to **3.5e-14**; **0.00e+00** difference at three points; log Z −72.90 ± 0.30 vs −73.18 analytic (**0.93 sigma**), means within 2.8 MC errors; restore reproduces log Z to **0.005** |
| TASK 2: settings and stopping rule quoted from before the run; iterations, evaluations, wall clock, dlogz, log Z ± error, n_eff; verdict; second seed | D2 quoted; 7,118 / 111,420 / 4.81 h / **0.100** / **−22.886 ± 0.164** / **4,052**; **CONVERGED**; second seed **incomplete**, with dynesty's 200-realisation volume check reported in its place |
| TASK 3: the sixteen-parameter table; width ratios; GRADIENT / WALL / FLAT; the respiration scale; the R² table; sigma | all above; **11 / 0 / 5**; `disc_resp` 0.313 on a floor of 1.42, so ≈ a factor 4.3 in O2; R² table given; sigma **0.845**, further from the literature 0.45–0.50 than P4's 0.723 and gradient-determined |
| TASK 4: the cost table | above; ≈ 33 h for seven, F LB held |
| TASK 5: OPEN_ITEMS; the hazard; evidence rows; README note; stamps | done |
| `git diff main --stat` | one floor value in `strains/eciML1515/gas_exchange.yaml`; `_gwloglike` in `src/etcgem/calibration_multi.py` (the pool needs an importable callable — the runner itself is in `reports/P11_nested/`, D1); `requirements.lock.txt` (dynesty 3.1.0); `reports/P11_nested/`; `docs/OPEN_ITEMS.md`; `reports/synthesis/{evidence.csv,README.md}`; `reports/report_status.yaml`; stamps; one run output directory. **No prior changed. No growth-term change.** |
