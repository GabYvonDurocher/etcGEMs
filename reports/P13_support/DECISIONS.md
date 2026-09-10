# P13 — decisions, from the first judgement call

## D0 — what this run moves under §0a, and what it must not claim

**Moves R1 only** — *statistically reliable: a posterior two independent runs agree on.* P13
changes how the respiration term scores a model that does not grow, then runs two nested samplers
at nlive 800 with different seeds. Both halves are about getting a posterior that reproduces.

**Does NOT move:**

- **R2 (identified).** Five parameters are flat because the data do not constrain them
  (P11 TASK 3; P12 found `f_metab` pinned at 0.28000 and `f_maint` at ~0.35 from every one of
  twelve starting points). Nothing in a support rule changes what the data say. TASK 5 reports
  whether the posterior still calls them flat, which is a *measurement of R2*, not progress on it.
- **R3 (right for the right reason).** P13 reports `dTm`'s credible interval because item 1.20
  turns on it, and the prompt is explicit: **report it, do not interpret it.** Discriminating the
  mechanism needs per-enzyme data, not a better posterior.
- **R4 (predictive).** Nothing is held out here.

**A caveat entered in advance, because the temptation will be to widen the claim.** If the two runs
AGREE, that establishes the posterior is *reproducible*, not that it is *right*. R2's five flat
parameters and R3's unexplained 3–4.5 K `dTm` shift are untouched by it, and a reproducible
posterior over a model that needs a 4 K shift against a measured meltome is still a model with a
problem. If findings later suggest this run moved more than R1, that will be stated explicitly
rather than absorbed.

## D1 — the death threshold is read from the code; the epsilon does not exist and is chosen here

The prompt asks for the death threshold from the existing support handling rather than invented.
It is:

```python
_MASK_G = 1e-4          # growth below this is "dead"; respiration there is not scored
...
keep = (g >= _MASK_G) & (o2 > 0)
```
`src/etcgem/calibration_multi.py:144,282`. **Death threshold = 1e-4 /h**, used unchanged.

**The epsilon is a different matter and the prompt's premise does not hold.** It speaks of
"the existing ε" and of flooring O₂ "exactly as the 1.42 floor already handles small values". Two
corrections, from reading the code:

1. **The 1.42 floor is not on O₂.** It is a floor on the *standard deviation of log O₂*, added in
   quadrature (`varr = rel**2 + dr**2 + floor**2`, `:293`). It widens the error bar; it never
   touches the predicted value. So it is not a precedent for flooring O₂ itself.
2. **No epsilon on O₂ exists anywhere in the likelihood.** The only `1e-9` values in
   `gasflux.py`/`calibration_multi.py` are solver tolerances (`tiebreak_tol`, `growth_tol`) and one
   guard in the RQ helper (`gasflux.py:167`, `np.abs(o2) > 1e-9 → NaN`), which is a different
   quantity in a different function and is not consumed by the likelihood.

So an epsilon has to be **chosen**, and because the imputed penalty scales with `log(ε)` the choice
is not cosmetic — it sets how large "large and finite" is. Chosen: **ε = 1e-9 mmol/gDW/h**, the
same numerical-zero scale `gasflux.py:167` already uses for O₂, so the constant is at least the
module's own and not a new invention. **Its sensitivity is reported in TASK 1 rather than
asserted**, at ε = 1e-6, 1e-9 and 1e-12, so the reader can see how much of any live–dead gap is the
epsilon rather than the evidence.

## D2 — a structural doubt about scheme (i), recorded BEFORE it is tested

The prompt's argument for imputation is that "**O₂ falls to zero continuously as growth does, so
there is no step for a cliff to form on**". **The committed P12 data appear to contradict that**, and
it is recorded here before the test so the test cannot be read as fitting the conclusion.

From P12's per-temperature decomposition at θ_A (`reports/P12_modes/`, TASK 0):

| T (°C) | predicted growth | O₂ uptake |
|---|---|---|
| 15 | 0.00000 | **NaN** (LP infeasible) |
| 50 | **0.00086** | **8.17** |

At 50 °C the model grows at 0.00086 /h — a factor of 8.6 above the death threshold, and
effectively zero against a measured peak of 2.076 — while consuming **8.17 mmol O₂/gDW/h**. That is
not a defect; it is **maintenance respiration**: ATP demand (NGAM) does not vanish when growth
does, so O₂ uptake does not either. Growth and O₂ decouple exactly in the region the support rule
governs.

If that holds generally, then imputing O₂ := ε at the threshold replaces a value of order 8 with a
value of order 1e-9 — a step of ~23 in log O₂, which at `varr ≈ 1.42²` is an enormous jump in the
respiration term. **Imputation would then be the hard mask again, wearing different clothes**, and
the prompt anticipates exactly this outcome: *"If imputation introduces a step above 1
log-likelihood unit, it is a mask in disguise; say so and prefer (ii)."*

This is a prediction, not a verdict. TASK 1's continuity scan measures it.

## D3 — `impute` is withdrawn, on evidence, and the physiology is the reason

The user withdrew the recommended scheme mid-run (addendum 1) on the physiology; the measurements
had independently reached the same place, and both are recorded.

**The premise that failed.** The prompt argued O₂ falls to zero continuously as growth does. It
does not, because a non-growing cell still respires for maintenance. Measured at the twelve
converged endpoints, at every temperature with growth ≤ `_MASK_G`:

| endpoint | T (°C) | growth | O₂ | status |
|---|---|---|---|---|
| A(b20) | 15 | 1.00e-4 | **1.570** | FEASIBLE-NOT-GROWING |
| Bstar(b8) | 15 | 1.00e-4 | **0.525** | FEASIBLE-NOT-GROWING |
| p81(b7) | 15 | 1.00e-4 | **2.237** | FEASIBLE-NOT-GROWING |
| worst(b5) | 50 | 4.7e-5 | **5.674** | FEASIBLE-NOT-GROWING |
| B(b3) | 11 temperatures | 0.000 | NaN | INFEASIBLE |

**Imputing O₂ := 1e-9 where the true prediction is 0.5–5.7 is a factor of ~1e9, i.e. ~21 in log**,
which at `varr ≈ 1.42²` costs ~110 log-likelihood units. Measured:

- **P10's D3a instrument, the gate the tie-break had to pass: `impute` FAILS at b3 with
  |Δ| = 119.1447** between an evaluation after itself and after a different point. `clamp` is
  0.0000 at all twelve.
- The continuity scan gives `impute` a step of **2,300 log-likelihood units per 0.05 sd**.
- The gap it produces is **the epsilon, not the evidence**: live−dead is 774 / 1,553 / 2,511 at
  ε = 1e-6 / 1e-9 / 1e-12.

Withdrawn. It is the hard mask in different clothes, exactly as the prompt's own fallback clause
anticipated.

## D4 — the mask is an ATTRACTOR, and it qualifies P12's ceiling test

The user asked whether p38's 15 °C growth landing on 1.000e-4 is coincidence. **It is not.**

| endpoint | temperatures within 1 % of `_MASK_G` | relative distance to the threshold |
|---|---|---|
| **B(b3)** | 1 | **0.000000** |
| **A(b20)** | 1 | **0.000000** |
| **Bstar(b8)** | 1 | **0.000000** |
| **p38(b22)** | 1 | **0.000000** |
| p81(b7) | 1 | 0.004320 |
| the other seven | 0 | 0.53 – 13.4 |

**Five of twelve converged endpoints park a temperature within 1 % of the threshold, and four sit
on it exactly** — p38's 15 °C growth is 9.999999859874725e-05, 1.4e-12 below 1e-4. Independent
optimisations from unrelated prior draws do not land on the same knife-edge by chance. **The
optimiser is parking a temperature on the mask to escape the 15 °C respiration penalty**, which is
a free −2.8 units at p38 (its clamp score is −9.989 against −7.186).

**Consequence, recorded as a dated qualification of P12 and NOT as an edit to its numbers.** P12's
ceiling test reported that p38 (−7.186) and A (−7.213) beat P11's main-run best sample (−7.396) and
concluded that Powell reaches the top of the basin the sampler found. **That margin is partly an
artefact of the mask**: both winning points sit exactly on the threshold, and both lose ~2.8 units
once their 15 °C prediction is actually scored. The qualification is that the *optimiser exploited
a discontinuity the sampler did not*, so the comparison is not like-for-like. P12's basin count,
which rests on bottleneck barriers of 13.868 against 1.785, is untouched by this.

**And the current likelihood is itself state-dependent there.** TEST A: `current` FAILS P10's
0.0000 rule at p38 with **|Δ| = 0.0157** — small, but non-zero, and it is the same knife-edge
showing through the ramp at its 0.01 floor. Every other endpoint is 0.0000. This is a property of
the likelihood P11's two nested runs were computed on.

## D5 — `clamp` wins on scoring, passes state-independence, and has ONE unresolved problem

**Why clamp is right, stated the strong way the user asked for.** `clamp`'s mask is
`keep = isfinite(o2) & (o2 > 0)`: it drops the growth mask entirely and **scores feasible-not-
growing points at full weight**. It is therefore already the variant the addendum proposed —
"scores every finite O2 and masks only genuine infeasibility" — and no separate test is needed.

Across the twelve endpoints there are 15 dead temperatures: **11 INFEASIBLE (all of them b3, the
dead basin) and 4 FEASIBLE-NOT-GROWING**. Among the **eleven live endpoints, 4 of 4 dead
temperatures are feasible with a finite O₂ prediction**. So for every model that grows at all,
**the mask was discarding real predictions, and clamp is right because it scores them** — not
merely because it removes a discount. That is the justification of record.

**State-independence at the boundary (addendum item 3): PASS.** Ten evaluations at p38, fresh
model built each time, under clamp: **−9.9893897954 ten times, spread 0.0000000000.**

**The unresolved problem, stated plainly.** Clamp scores a feasible-not-growing temperature at
**full** weight and then drops it **entirely** when the LP tips infeasible. That is a hard on/off at
the *feasibility* boundary, and the fine continuity scan measures it: **4.14 log-likelihood units
across 0.0032 sd = 64 units per 0.05 sd**, against the SAMPLEABLE rule's 5. Calibrated against the
same rule, `current` is 0.80 and `impute` 2,300.

So clamp has not removed the discontinuity; it has **relocated it from the growth threshold to the
feasibility threshold**, which is the same class of defect P10 fixed. P10's ramp is, structurally,
the right answer to *this* boundary — as growth → 0 the weight → 0.01, so the term is only 1 % of
itself when it vanishes — and its defect is only that its floor is a discount and its threshold is
an attractor.

**This is the third discontinuity found at the cold end, and the user's instruction is explicit:
do not proceed to TASK 4 until the chosen scheme is state-independent AND sampleable on the cold
lines.** State-independence is proven. Sampleability is not, and the cliff above is measured on the
road to the dead basin (t ≈ 0.9 of p38 → b3), not necessarily inside the posterior's own region.
**TASK 3 decides it** with P11's twelve lines at ±1 sd of p38, cold lines called out. TASK 4 does
not start unless every line, cold ones included, is under 5 units per 0.05 sd.
