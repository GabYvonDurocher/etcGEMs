# P11 — decisions

Standing rules carry over. Branch `p11/nested` from `main` after the P10 merge; no push to
`main`; end in a PR that is not merged. Interpreter `../etcGEMs-venv`. Two decisions are
**executed, not revisited**: the respiration floor moves to the largest measured vertex jump,
and the growth term is not floored. Exit codes checked explicitly.

---

## D0 — TASK 0: the floor moves 0.76 → 1.42, and the absolute smoothness rule, both written before the re-scan

PR #25 merged server-side clean → `97411f1`; `p11/nested` branched; gates on
`../etcGEMs-venv` with the options OFF recorded in the report.

**The floor.** P10 set `log_o2_floor` = **0.76** by a rule that took the largest |Δ log O2| at
the *modal* cliff temperature (20 °C, 14 of the 17 O2-carried cliff steps; largest there 0.759).
The largest measured vertex jump **anywhere** in that scan is **1.4216**, on the `axis:dCp_scale`
line between +0.90 and +0.95 sd, carried by **25 °C**, and it is the step that still cost 7.8
units under the 0.76 floor and left the surface ROUGH (P10 D5, `task2_jumps.csv`). The prompt's
first decision is to move the floor to that number: **`log_o2_floor` 0.76 → 1.42**. One value,
one commit. Its cost is stated rather than hidden: the respiration term's sd at every temperature
is now at least 1.42 in log, i.e. the model is granted a factor-4 band on O2 everywhere, which is
a real loss of information about respiration and is the price of a sampleable surface. The three
temperatures whose measured relative sd is 0.06–0.09 are the ones that lose most.

**The growth term is untouched** (the prompt's second decision, executed): its 1–3 unit kinks are
the growth LP's piecewise-linear response to θ, present in every enzyme-constrained model.
Flooring the primary data's variance to make a sampler comfortable would trade information for
convenience. They will appear in the re-scan and are **reported, not fixed**.

**The absolute smoothness rule, written now, before the re-scan exists:**

> A line is **SAMPLEABLE** if no single 0.05 sd step along it exceeds **5 log-likelihood units**.
> The surface is **SAMPLEABLE** if every one of P9's twelve lines is.

Why absolute rather than P9's relative rule: what decides whether a sampler can cross a step is
the likelihood ratio across it, e^{−Δ}. e^{−30} is a wall no random-walk proposal crosses;
e^{−2} is a kink any sampler steps over and a nested sampler does not even notice, since it uses
only the ordering of likelihood values. A relative rule (step > 20 % of the line's range) was the
right instrument while the cliffs were 13–72 units and the ranges 15–137; once the floor shrinks
the cliffs it shrinks the ranges with them, and the rule then flags kinks that are not obstacles.
Both readings are reported side by side. Five units is chosen as the threshold because it is the
same cliff threshold P10 used to *identify* the steps it fixed (`task2_floor.py`, CLIFF = 5.0),
so the rule and the diagnosis that produced the fix use one number; a step of 5 is a likelihood
ratio of 150 across 0.05 sd, which is a kink and not a wall.

If any line still exceeds 5 units after the floor move, TASK 0 STOPS and reports which.

## D1 — TASK 1: what had to be added to wire dynesty, and why the runner lives in the report directory

**Where:** TASK 1, before any nested run.

**In the core, one callable.** `_gwloglike` beside `_gwlogprob` in `calibration_multi.py`: the
gas-flux log-likelihood on the worker's own ctx, without the log-prior, because a sampler that
handles the prior itself needs the likelihood alone. Same pool initialiser, same ctx, same
specs. A non-finite value is returned as −1e100 rather than −inf, because nested sampling needs
a total ordering of likelihood values and −inf breaks it; the prior transform makes
out-of-support points unreachable, so this only catches a solver failure. Nothing else in the
core changed.

**Everything else is in `reports/P11_nested/`** — the transform, the runner, the checks. Reason:
`src/etcgem/` is the seven-strain core, gated on every change; a sampler used by one report is
not core infrastructure until a second report needs it. The one thing that had to be core is the
worker callable, because a process pool must import it from an installed module (a function
defined in a run script is re-imported by every spawned worker — the failure that produced this
session's runaway process).

**The prior transform** (`prior_transform.py`) is the inverse CDF of each of P4's priors, in the
space `log_prior` scores: `normal` in the natural value, `lognormal` in log, `halfnormal`
inverted in the natural value and returned as its log (whose Jacobian is exactly the `+theta`
term `log_prior` adds). Every one is truncated to its hard `[lo, hi]`. Proven two ways
(`task1_transform.csv`): 10,000 draws match `scipy.stats.truncnorm`'s analytic quantiles (worst
error 0.13 on dTopt, whose prior spans 30) and every marginal mean is within 1.6 Monte-Carlo
standard errors; and on a 200-point grid per parameter the difference between `log_prior`'s
contribution and the transform's implied log-density is **constant to 3.5e-14**. The first
version of that second check disagreed by exactly 8.0 and 10.8 on the two half-normals — the
range of their log-Jacobian — which was the check comparing spaces, not the transform being
wrong; recorded because it is the kind of error that looks like a bug in the thing being tested.

**The transform is a module-level callable object, not a closure**, because dynesty pickles it
to every worker.

**Proofs.** Pool path vs a single-process fresh evaluation at three points: **identical to
0.00e+00**, and 32 evaluations over 16 workers in 4.5 s = **0.141 s per evaluation of wall
clock**. Toy (16-d correlated Gaussian, P8's covariance, analytic log Z): dynesty recovers
log Z = −72.90 ± 0.30 against −73.18, **0.93 sigma**, means within 2.8 Monte-Carlo errors,
median relative covariance error 5.5 %. Checkpoint: a run halted at 301 iterations, restored
from disk and continued, reaches the same log Z as an uninterrupted run **to 0.005 (0.00
sigma)**. dynesty 3.1.0, added to `requirements.lock.txt`.

## D2 — TASK 2: the settings, the projection, and the stopping rule, all written before the run

**Where:** before the nested run starts.

**Settings.** `nlive = 400`, `bound = "multi"`, `sample = "rslice"`, `slices = 3`, `dlogz = 0.1`,
wall-clock cap **4 h**, checkpoint every 180 s, 16 processes, seed 1.

* **nlive 400, not the prompt's 500.** dynesty's guidance for multi-ellipsoid bounding is
  nlive ≳ 25 × D, which is exactly 400 in 16 dimensions. Cost scales linearly in nlive and the
  budget is the binding constraint, so 400 is the smallest value that keeps the bounding
  recommendation intact. Below it the ellipsoid decomposition degrades and log Z can bias.
* **rslice, not rwalk**, and this is the point of the run: slice sampling needs only the
  ordering of likelihood values, has no proposal scale to tune, and steps over a kink. A
  random-walk kernel inside nested sampling would reintroduce the proposal-scale dependence
  that defeated P6–P8, and a converged result would then be evidence about the kernel rather
  than about the surface. `slices = 3` rather than dynesty's default 5 halves the per-iteration
  cost and is dynesty's documented minimum for adequate decorrelation.

**The projection, stated before the run rather than after it.** The information is estimated
from P8's posterior/prior width ratios as H ≈ Σ log(1/ratio) ≈ 20 nats, and the new likelihood
is wider than the one those ratios came from, so H ≈ 15–20. Nested sampling needs about
nlive × H iterations, so 6,000–8,000, at an rslice cost of roughly 15–45 likelihood calls each:
**90,000–360,000 evaluations, or 3.5–14 h at the measured 0.141 s**. The 4 h cap therefore may
or may not be reached, and that is not a reason to weaken the settings: the run is
checkpointed, so a cap-stop is a resumable state and not a loss, and its trajectory is the first
measurement of what this posterior actually costs — which TASK 4 needs regardless of the verdict.

**The stopping rule, verbatim:** **CONVERGED** if dynesty reaches dlogz < 0.1 within the 4 h cap
**and** the posterior n_eff dynesty reports is ≥ 600. **STALLED** if the cap is hit first. Both
numbers are reported either way. A STALLED run is reported as STALLED, not extended past the
cap, and its posterior is not quoted as a result.

## D3 — TASK 3: the identifiability classification rule, written before the posterior exists

**Where:** before the nested run finishes.

Each of the sixteen parameters gets one line scan through the **new** posterior median, ±1
**posterior** sd (not prior sd) at 0.05 sd steps, log-likelihood only, fresh model per
evaluation — P9's instrument with a new centre and a new scale. Classified by a rule fixed now:

* **FLAT** — the log-likelihood ranges by **less than 1 unit** over ±1 posterior sd. The data do
  not distinguish the parameter locally at all; its posterior is its prior, reshaped by whatever
  correlations it has with the others.
* **WALL-BOUNDED** — not flat, and the largest single 0.05 sd step is **more than 25 % of the
  line's range**. The parameter's posterior width is set by where the likelihood falls off a
  step, not by curvature: an interval bounded by the model's piecewise structure.
* **GRADIENT-DETERMINED** — not flat, and no step exceeds 25 % of the range. The line is a
  curve and the interval is set by the data through the gradient, which is what a credible
  interval normally means.

Reported as three lists. This is the first time the identifiability of this model can be stated
per parameter, because it is the first posterior worth centring on.
