# P14 — decisions, from the first judgement call

## D0 — what this run moves under §0a

**Moves R1 only** — *a posterior two independent runs agree on.* P14 corrects the sampleability
test that stopped P13 and, if it passes, runs two nested samplers at nlive 800 with different
seeds.

**Does NOT move:**

- **R2 (identified).** P11 found five flat parameters; P12 found `f_metab` pinned at 0.28000 and
  `f_maint` at ~0.35 from twelve independent starts; **Y3 added that `dTm` and `tm_scale` are not
  jointly identified**, which makes it six or more. A posterior *measures* this; it does not fix it.
- **R3 (right for the right reason).** Y3 settled that `dTm`'s **value** is a parameterisation
  artefact and what survives is a **per-enzyme tail requirement**. P14 reports where the posterior
  puts that tail; it does not discriminate the mechanism.
- **R4 (predictive).** Nothing is held out.

**Stated in advance:** if the two runs AGREE, that establishes the posterior is **reproducible**,
not that it is **right**. A reproducible posterior over a model with six unidentified parameters
and an unexplained low-tail stability requirement is still a model with a problem.

## D1 — the corrected sampleability criterion, WRITTEN BEFORE IT IS APPLIED

The old rule — *no 0.05 sd step above 5 log-likelihood units* — is retired. The user's diagnosis is
recorded as the reason, and P13's own evidence supports it: **the rule was a proxy for
discontinuity that in fact measured steepness**, and it was **centre-dependent** — the same line,
instrument and likelihood give **3.20 at θ_A and 8.55 at p38**, differing only in where they were
measured. It cost a run slot. It is replaced, not patched.

The replacement tests the two things that actually break the sampler.

### (a) DISCONTINUITY, by grid refinement

At the **largest step of each of the twelve lines** under clamp, centred at **p38**, evaluate the
step across spacings **h, h/2, h/4, h/8**, where h = 0.05 sd, with a **fresh model per evaluation,
single process**.

For a function with a bounded derivative, |Δ| falls in proportion to h. For a genuine jump, |Δ|
converges to the jump height.

> **SMOOTH** if the ratio |Δ(h/2)| / |Δ(h)| lies in **[0.35, 0.65]** at every one of the three
> halvings (0.5 is exact linear scaling; the window admits curvature and the ~0.02-unit evaluation
> jitter P5 measured).
> **JUMP** if any ratio exceeds **0.80**, i.e. the step stops shrinking.
> **AMBIGUOUS** in between, and an ambiguous line is treated as a JUMP for the purpose of stopping.

### (b) PLATEAUS, which is what nested sampling actually requires

Nested sampling depends only on the **ordering** of likelihood values and is invariant to any
monotone transformation of them, so **gradient magnitude is irrelevant to it**. What voids the
volume-shrinkage estimate is a **plateau**: a set of *positive prior volume* on which the
likelihood is *exactly* constant (Fowlie, Handley & Su 2021, flagged in P11).

On all twelve lines under clamp: count exactly-equal adjacent log-likelihood values, report the
longest run and the fraction of all evaluations lying on any plateau.

> **PASS** if no plateau run spans more than **10 % of a line** — 4 of the 40 intervals, i.e. 0.2 sd
> of the 2 sd scanned.

### (c) FEASIBILITY BOUNDARIES do not disqualify

Where a line crosses into infeasibility the model makes no claim: the likelihood is genuinely
undefined, not discontinuous. Nested sampling proposes there, receives −inf and discards, exactly
as it treats a prior bound. These are **reported with their location relative to ±1 sd of p38 and
passed over**. Nothing is smoothed, floored or softened.

### The criterion

> **SAMPLEABLE if every line's largest step tests SMOOTH under (a) AND no plateau under (b) spans
> more than 10 % of a line. Steepness alone does not disqualify. Feasibility boundaries do not
> disqualify.**

If any line tests JUMP or AMBIGUOUS, TASK 2 does not start and the line, its location and its
refinement series are reported.

**The twelve lines are reported under the old rule and the new one side by side**, so the change is
auditable rather than asserted.

### On the exactly-flat parameters — a prediction of what (b) will show, and why

P11 found five parameters flat and P12 found `f_metab` and `f_maint` pinned from every start. **A
flat *direction* is not a plateau in the sense that breaks nested sampling**, and the distinction
matters. If the likelihood does not depend on `kappa_scale`, the level set {L = c} is a
codimension-1 surface extruded along that axis: it still has **zero** 16-dimensional volume, so the
shrinkage estimate is unaffected. dynesty samples such a direction uniformly from its prior inside
the constrained region, and its posterior marginal simply equals its prior — which is what
"unidentified" means and is an **R2** statement, not an R1 one. A harmful plateau needs L exactly
constant on a set of **positive** 16-D volume, which is what (b) looks for. Neither
`kappa_scale` nor `f_metab` is among the twelve lines (P9 excluded them as exactly flat), so this
is stated as a prediction and checked against (b)'s counts.
