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

## D2 — the first pass of (a) tested the wrong step on eight lines, and the fix is D1(c), not a new rule

The refinement in `task1_refine.py` was applied to each line's **largest step overall**. On **eight
of twelve lines that step is the feasibility transition itself**, which D1(c) exempts in advance.
The identification is exact rather than inferred: for `axis:f_maint`, `axis:ngam_scale`,
`axis:clearance_mult`, `PC1`, `PC2`, `PC3`, `random2` and `random3`, the location (`at_sd`) and the
size (`step_h`) of the refined step **equal P13's committed feasibility-transition table to the
digit** — e.g. `clearance_mult` −0.05 / 1.5717 in both, `PC1` 0.00 / 1.6367 in both. They converge
to ≈1.56 because that is the size of the term a temperature contributes when it enters or leaves
the scored set, which is the same quantity on every line.

**Those eight JUMP verdicts are therefore not findings; they are the test pointed at the one thing
D1 said not to point it at.** A boundary of the feasible set *is* a jump — the model makes no claim
past it and nested sampling discards there — which is exactly why (c) exempts it.

**The fix, and it is not a relaxation.** (a) is re-run on each line's largest step **between two
points whose support set is unchanged**, which is what the criterion always meant. Two additions,
both tightening rather than loosening:

1. **The support set is recorded at every refinement evaluation**, not just on the 0.05 sd grid.
   P13's scan located feasibility crossings only to 0.05 sd; a crossing can lie *inside* a refined
   interval and would otherwise present as a spurious persistent step. Any interval that turns out
   to contain a crossing is reported as a crossing and exempted under (c) — with its location — not
   silently passed.
2. **The refinement is extended to h/16 and h/32 for any line that reads AMBIGUOUS.** This is
   **more resolution of the same test, not a wider window**: the SMOOTH band stays [0.35, 0.65] and
   the JUMP threshold stays 0.80. The three-level cap in D1 was my own arbitrary choice, and an
   indeterminate verdict produced by too few levels is a limitation of the instrument, not a
   property of the surface. The window is not moved; if the ratios trend to 1.0 the line is a JUMP
   and TASK 2 stops.

### Standing after the first pass

- **`axis:topt_scale` — the line that stopped P13 — tests SMOOTH**: 8.5517 → 4.3325 → 2.2295 →
  1.1236, ratios **0.507, 0.515, 0.504**. Textbook linear scaling in h. **The 8.55 units are pure
  steepness**, and the user's diagnosis of the old rule is confirmed by direct measurement rather
  than by argument.
- **`axis:kcat_scale` SMOOTH**: ratios 0.507, 0.502, 0.502.
- **`axis:dCp_scale` AMBIGUOUS** at +0.95 sd (not a transition; its crossings are at 0.00 and
  0.75): 4.8156 → 3.7087 → 2.4065 → 1.6404, ratios 0.770, 0.649, 0.682 — falling, but not halving.
- **`random1` JUMP** at +0.80 sd (its crossing is at 0.00): 2.5010 → 1.4430 → 1.0535 → 0.8849,
  ratios 0.577, 0.730, 0.840 — falling but decelerating, which is what a smooth part plus a jump,
  **or** an unresolved feasibility crossing inside the interval, both look like.

Those two are the run's real question and are settled by the second pass, not by argument.

## D3 — the corrected test: (b) passes perfectly, (a) fails on four lines, and TASK 2 does not start

### Results

**(b) PLATEAUS — PASS, emphatically.** Across all twelve lines and **480 evaluations there is not a
single pair of exactly-equal adjacent log-likelihood values**: 0/480, longest plateau run 0
intervals, 0.00 % of every line, against D1's 10 % rule. **The property that actually voids nested
sampling's volume-shrinkage estimate is absent.**

**(c) FEASIBILITY — 13 crossings**, all reported with location, none smoothed, all within
|0.00–0.80| sd of p38. Eight of them are the *largest* step on their line, which is why D2's second
pass was needed.

**(a) DISCONTINUITY — 8 of 12 SMOOTH, 4 JUMP.**

| line | series (h → h/2 → …) | last ratio | verdict |
|---|---|---|---|
| `axis:topt_scale` | 8.5517 → 4.3325 → 2.2295 → 1.1236 | 0.504 | **SMOOTH** |
| `axis:kcat_scale` | 2.7260 → 1.3808 → 0.6938 → 0.3484 | 0.502 | SMOOTH |
| `PC3` | 0.7895 → 0.3974 → 0.1991 → 0.0996 | 0.500 | SMOOTH |
| `random2` | 1.1993 → 0.6041 → 0.3032 → 0.1519 | 0.501 | SMOOTH |
| `random3`, `f_maint`, `ngam_scale`, `clearance_mult` | all halve | 0.50–0.52 | SMOOTH |
| `axis:dCp_scale` | 4.8156 → … → 0.6662 → 0.3791 (8 levels) | 0.569 | **JUMP** |
| `PC1` | 0.7111 → … → 0.1472 → 0.1453 (8 levels) | 0.987 | **JUMP** |
| `PC2` | 0.6839 → 0.5672 → 0.5073 → 0.4672 | 0.921 | **JUMP** |
| `random1` | 2.5010 → 1.4430 → 1.0535 → 0.8849 | 0.840 | **JUMP** |

**`axis:topt_scale` — the line that stopped P13 at 8.55 units — tests SMOOTH, with ratios 0.507,
0.515, 0.504.** The old rule's verdict was steepness, measured. That is now demonstrated rather
than argued.

### What the four jumps ARE — one mechanism, and it is the known one

Bisected to intervals of 1.95e-04 sd and decomposed:

| line | step | growth term | respiration term | % growth | biggest O₂ move |
|---|---|---|---|---|---|
| `axis:dCp_scale` | 0.3791 | −0.0090 | **−0.3702** | 2 % | 25 °C, 0.278 → 0.228 (**0.82×**) |
| `PC1` | 0.0525 | +0.0017 | **+0.0508** | 3 % | 15 °C, 1.153 → 1.452 (**1.26×**) |
| `PC2` | 0.4007 | +0.0010 | **+0.3997** | 0 % | 20 °C, 1.462 → 2.718 (**1.86×**) |
| `random1` | 0.5886 | −0.0052 | **−0.5834** | 1 % | 20 °C, 1.174 → 0.665 (**0.57×**) |

**97–100 % respiration term in every case, with growth unchanged to five decimal places**
(0.10412 → 0.10408; 0.00353 → 0.00353; 0.07634 → 0.07634; 0.02282 → 0.02280) while **O₂ moves by a
factor of 0.57–1.86 at a single cold temperature**.

That is **precisely P9's diagnosis**: the LP's optimal O₂ switching vertex at cold temperatures
while growth barely moves. P10's tie-break made it *deterministic* — P13 and P14 both measure
state-independence at 0.0000000000 — and the 1.42 floor cut its cost from **13–72 log-likelihood
units to 0.05–0.59**. It is the LP being an LP, it is two orders of magnitude smaller than when it
was diagnosed, and removing it entirely would need the lexicographic tie-break, which is item 1.22
and is **excluded from this prompt by name**.

### The verdict, and the argument I am NOT using to override it

**TASK 2 does not start.** The prompt is explicit — *"If any line tests JUMP: STOP and report which,
where, and its refinement series. Do not start TASK 2."* — four lines test JUMP, so the run stops
and no posterior is quoted.

**The case for proceeding is put to the user rather than acted on, because acting on it would be
the fourth time this series moved a criterion after seeing its data.** It is this:

1. **(b), the test the prompt itself identifies as decisive, passes perfectly.** The prompt's own
   rationale: *"Nested sampling depends only on the ordering of likelihood values … What genuinely
   breaks it is plateaus … Steepness is not a problem. Flatness is."*
2. **A jump is not a plateau, and nested sampling is insensitive to it.** The estimator depends on
   X(L) = the prior mass with likelihood above L. A discontinuity in L(θ) leaves an *interval of
   likelihood values carrying no prior mass* — X is flat there, no live point ever lands in it, and
   nothing is estimated wrongly. A **plateau** puts an **atom** in the distribution of L, which is
   what breaks the shrinkage argument. The two are different objects and only one is fatal.
3. **The jumps are 0.05–0.59 units** — below the 1–3 unit LP kink scale P9/P10 measured and P11
   accepted as irreducible, and far below the 5-unit scale anything in this series has treated as
   material.
4. **They are not removable within this prompt's constraints**: their mechanism is the pFBA
   vertex, and the lexicographic tie-break is excluded by name.

So D1's conjunction — SMOOTH under (a) **and** no plateau under (b) — is, on this evidence,
**over-strict in its first conjunct**: it requires a property the sampler does not need. That is a
statement about the criterion, and the criterion was mine. It is recorded, not exercised.
