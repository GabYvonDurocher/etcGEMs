# P11 — the last wall, an absolute smoothness rule, and a sampler matched to a piecewise surface

@@STATUS@@

Detail: [DECISIONS.md](DECISIONS.md) (D0–@@DLAST@@). Scripts beside this file:
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

@@TASK2@@

## TASK 3 — the posterior

@@TASK3@@

## TASK 4 — what the rest would cost

@@TASK4@@

## TASK 5 — the record

@@TASK5@@

## Verification

@@VERIFY@@
