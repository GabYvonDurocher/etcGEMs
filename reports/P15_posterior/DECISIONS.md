# P15 — decisions, from the first judgement call

## D0 — the 1.23 resolution: the discontinuity conjunct is lifted, and why that is a correction rather than an accommodation

**The PI has resolved OPEN_ITEMS 1.23: the discontinuity conjunct of P14's sampleability criterion
is lifted.** This entry records the reasoning before anything is run, because the distinction
between *correcting a criterion* and *moving a threshold to suit inconvenient data* is the whole
point, and this series has now refused the latter three times.

### The conjunct was wrong when it was written, on an argument that predates any data

The criterion required **(a)** no discontinuity **and** **(b)** no plateau. The addendum that
specified it **named plateaus as nested sampling's failure mode and then required no-jumps as
well**. Those are different objects, and the argument separating them needed no measurement:

Nested sampling estimates **Z = ∫ L dX**, where **X(λ)** is the prior volume on which L > λ. Its
one structural requirement is that **L have no atoms under the prior**. An atom makes **X(λ) jump**,
and that voids the shrinkage estimate **X_i ≈ exp(−i/nlive)**, which assumes the live points are
uniformly distributed in X. **A plateau — a set of positive prior volume on which L is exactly
constant — creates exactly that atom.**

A **jump discontinuity in L(θ) does not.** It leaves a **gap in the support of L**: X(λ) is flat
over an interval of λ that carries **no prior mass**. No live point ever falls in that interval,
nothing is estimated there, and **Z = Σ L_i w_i remains a valid Riemann sum in X**. The estimator
is a function of the distribution of L under the prior, not of the geometry of L in θ — which is
the same invariance that makes nested sampling indifferent to any monotone reparameterisation of
the likelihood, and therefore to gradient magnitude.

So (a) tested a property the sampler does not require. That was true before P14 ran.

### What the measurements then showed

- **The test that matters passes perfectly.** P14 counted **0 of 480 adjacent evaluations exactly
  equal**, across all twelve lines: longest plateau run **0 intervals**, against a 10 % rule. **There
  are no atoms.**
- **The four real jumps are 0.145–0.885 log-likelihood units**, and all four are one mechanism —
  97–100 % respiration term, growth unchanged to five decimal places, **O₂ moving 0.57–1.86× at a
  single cold temperature**. That is the residue of P9's LP vertex switch, **two orders of magnitude
  below its diagnosis** (13–72 units).
- **They are not the binding constraint on this likelihood.** The **growth-term kinks P11 accepted
  as irreducible are 1–3 units**, and P10 established that no respiration change touches them. So
  even implementing 1.22 — the lexicographic tie-break, which would remove the O₂ jumps — would
  leave **larger** discontinuities in place from a different term. 1.22 is therefore a **cost
  optimisation for the remaining eight fits, not a correctness fix**.

### The distinction, stated plainly

**This is a criterion corrected on an argument available before the data, not a threshold moved to
accommodate it.** The evidence did not change what the sampler needs; it confirmed that the surface
supplies it. Had P14's plateau census found atoms, the conjunct would have been irrelevant — the run
would stop on (b), which is the test that names the actual failure mode.

**P14 was right to refuse to lift it itself.** The criterion was P14's own, its data had been seen,
and a run that moves its own goalposts after a failing result is worth nothing regardless of whether
the new position is defensible. The correction required someone who was not holding the pen.

### What P15 inherits as established

- **The refinement test is a proper instrument.** `axis:topt_scale` refines 8.5517 → 4.3325 →
  2.2295 → 1.1236, ratios 0.507 / 0.515 / 0.504 — textbook linear scaling in h, hence **pure
  steepness**.
- **The old absolute rule ranked all twelve lines backwards**: the 8.55-unit step is smooth, while
  steps of 0.05–0.59 that do not shrink are the genuine discontinuities.
- **The flat directions are R2, not R1.** {L = c} along such an axis is codimension-1 extruded, with
  **zero 16-dimensional volume**, so it is not an atom; dynesty returns the parameter's **prior** as
  its marginal. TASK 2 reports any such marginal as **the model being unidentified in that direction
  given this data**, never as a sampling failure.

## D0b — which of R1–R4 this run moves

**R1 only** — a posterior two independent runs agree on.

- **R2 (identified): not moved, and reported honestly rather than improved.** P11 found five flat
  parameters; P12 found `f_metab` pinned at 0.28000 and `f_maint` at ~0.35 from twelve independent
  starts; **Y3 added `dTm`/`tm_scale` as not jointly identified**. A posterior *measures* this. Any
  marginal that returns its prior is an R2 statement.
- **R3 (right for the right reason): not moved.** Y3 settled that `dTm`'s **value** is a
  parameterisation artefact and that what survives is a **per-enzyme tail requirement**. P15 reports
  where the posterior puts that tail; it does not discriminate mechanism.
- **R4 (predictive): not moved.** Nothing is held out.

**Stated before the runs:** if they AGREE, that establishes the posterior is **reproducible**, not
**right**. A reproducible posterior over a model with six or more unidentified parameters and an
unexplained low-tail stability requirement is still a model with a problem, and the agreement
verdict must not be quoted as if it settled more than it does.

## D1 — the settings, the agreement rule, and the two predictions, ALL written before either run starts

Committed before any sampler was launched. None of it is revised afterwards.

### Settings

| | |
|---|---|
| sampler | `dynesty.NestedSampler`, P11's wiring unchanged |
| nlive | **800** |
| sample / bound | **`rslice`**, slices 3 / `multi` |
| stopping | **dlogz < 0.1** |
| `first_update` | **`{'min_eff': 30}`** (P11 D4: ~1 h of single-core unit-cube phase without it) |
| runs | **two, SEQUENTIAL, different seeds** (1 and 2) |
| checkpoint | every 30 min; wall-clock cap **16 h each** |
| processes | 16, `queue_size` 16 |
| likelihood | P10's with clamp (P13), asserted from the strain config at start-up |

**If run 1 hits the 16 h cap**: checkpoint cleanly, report **STALLED** with a projection, and **do
not start run 2** — a second stalled run answers nothing.

### The agreement rule

> **AGREED** if the two log Z agree within their combined reported error **AND** no posterior median
> differs by more than two Monte-Carlo errors.
> **DISAGREED** otherwise, reported with the same table P11 produced.

### The two predictions, orphaned by P13 and P14 and now evaluable

Both follow from D4 of P13: the growth mask at `_MASK_G = 1e-4` is an **attractor**, and **four of
twelve independent optimisations parked a temperature on it exactly**, worth ~2.8 log-likelihood
units of unscored 15 °C respiration. That was measured on an **optimiser**. Under clamp the
advantage is gone, because the 15 °C prediction is scored whatever the growth is.

> **(i)** The clamp posterior **moves AWAY** from parameter values placing any temperature within
> **1 % of `_MASK_G`**. Reported as the **fraction of posterior samples** with at least one
> temperature in that band, against **P11's posterior** (`samples_main.npy`, importance-weighted the
> same way) as comparator.
>
> **(ii)** The 15 °C growth residual becomes more expensive to ignore, so the fit should trade
> **toward growing at the cold end**. Reported as **posterior-predictive growth at 15 °C** under both
> posteriors, against the measured **0.0937 /h**.

**If (i) holds, the attractor is confirmed by a second and independent route — a sampler as well as
an optimiser. If it does not, the attractor was optimiser-specific and P12's dated qualification of
its ceiling test narrows accordingly.** Either way it is reported against this text as written.

**Neither prediction is a criterion for anything.** They are diagnostics of the support change; the
agreement rule above is independent of them.

### One thing that will NOT be read as a failure

If a marginal comes back equal to its prior, that is **R2 unidentifiability surfacing honestly**, not
an R1 sampling failure. P14 established that a flat direction has **zero 16-dimensional volume** and
so is not an atom: dynesty is behaving correctly by returning the prior. Any such parameter is
reported that way in TASK 2.

## D2 — run 1 CRASHED at 9.9 h. It did not converge and it did not hit the cap, and those are three different outcomes.

At **08:04 on 2026-09-11**, after **~9.9 h** and **11,547 iterations**, run 1 died with:

```
RuntimeError: Slice sampler has failed to find a valid point.
nstep_left: -5.4e-323   nstep_right: 5e-323   nstep_hat: 1.04e-322
u_prop == u   (bit-identical)
loglstar: -14.169843617724203
```

Those step sizes are **denormal doubles — numerically zero**. The slice bracket collapsed, and the
proposed point was bit-identical to the current one. **No summary, samples or weights were written**;
the only artefact is the 07:15 checkpoint at iteration 11,547, dlogz **2.168**, log Z **−25.730**.

**This is reported as CRASHED, not STALLED.** D1's rule covers a run that hits the 16 h cap; this
one did neither that nor converge. Calling it "stalled" would make a software failure sound like a
budget finding, and the two license different next steps.

### The cause, diagnosed from the checkpoint's own live points

`task1_crash_diag.py` restores the checkpoint and takes the covariance of the 800 live points **in
the unit cube**, which is the space `rslice` actually works in:

| smallest eigenvalues | λ | √λ | dominant loadings |
|---|---|---|---|
| 1 | **1.947e-04** | 1.395e-02 | **`dTm` +0.903**, `sigma` +0.274, **`tm_scale` −0.217** |
| 2 | 6.305e-04 | 2.511e-02 | `dTopt` −0.625, `resp_scale` −0.560 |
| 3 | 7.880e-04 | 2.807e-02 | `sigma` −0.816, `kcat_scale` −0.313 |

Largest eigenvalue 2.835e-01; **condition number 1,457**.

**`corr(dTm, tm_scale) = +0.831` among the live points**, with that 2×2 block conditioned at 49.3.

**This is Y3's non-identified pair, confirmed by an independent route.** Y3 found `dTm` and
`tm_scale` not jointly identified by profiling the likelihood; here the *sampler's own live points*
collapse onto that correlation as the constraint tightens. It also explains the **1,124
divide-by-zero warnings** dynesty emitted from `bounding.py:273` (`1./l1` with a zero eigenvalue) —
the bounding ellipsoid was singular for hours before the slice sampler finally failed.

Note what this is **not**: `dTm` is the *most tightly constrained* parameter (live sd 0.0506 in the
unit cube against the prior's 0.289), not a flat one. The pathology is a **thin, correlated ridge**,
not a plateau — consistent with P14's census, which found no plateaus at all.

For the record, the same table shows three parameters sitting essentially **at their priors** —
`f_metab` 0.273, `dCp_scale` 0.266, `f_maint` 0.265 against 0.289 — which is **R2 unidentifiability
surfacing exactly as D1 said it would be read.**

### What was done about it, and what was not

**Resumed from the checkpoint with identical settings.** The prompt provides `--resume`, the restore
was proven in TASK 1, and the question worth answering first is whether the failure is
*deterministic*. It is not: the resume picked up at iteration 11,546 and continued. So the crash is
a **numerical fragility of `rslice` on this geometry**, hit stochastically, not a wall the run
cannot pass.

**What was NOT done, deliberately:** the sampler was not changed. Switching `rslice` → `rwalk` would
very likely avoid the failure, but it is a setting fixed in D1, it would break comparability with
P11's runs, and choosing it after a crash is the pattern this series has refused three times. If the
resumed run crashes again, that is reported and the choice is the PI's.

**The wall-clock envelope is honoured rather than reset:** the resume was given **5.8 h**, so the
total stays inside the original 16 h from 22:07, which ends at **14:07**.
