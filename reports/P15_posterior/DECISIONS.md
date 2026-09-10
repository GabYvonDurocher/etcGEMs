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
