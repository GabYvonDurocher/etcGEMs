# P13 — replace the support discount with a bounded penalty, and try to earn the posterior

_Run 2026-09-10 on `../etcGEMs-venv`, branch `p13/support`, from main after PR #27 (P12) merged._

**Outcome in one line: the support form was chosen on measurement and adopted, and the posterior
was NOT earned — TASK 3's stop condition failed, so the two nested runs were not started.** The
blocker is not the support handling; it predates P13 and is unchanged by it.

---

## TASK 0 — baseline, and what this run moves

Merged #27; gates with the options OFF: **Candida 79/79, P1 60/60**, all three `tpc` runs rc=0.

**D0 — this run moves R1 only.** R2 is untouched (a support rule cannot change what the data say
about five flat parameters); R3 is untouched (`dTm` was to be *reported*, not interpreted); R4 is
untouched. A caveat was entered in advance: had the two runs agreed, that would have established
the posterior is *reproducible*, not that it is *right*.

Baseline under the current likelihood, single process, fresh model, at P12's committed points:

| point | log L |
|---|---|
| p38(b22) — the live basin's best | **−7.186** |
| A(b20) | −7.197 |
| B(b3) — the dead basin | −18.877 |
| **live−dead gap** | **11.691** |

## TASK 1 — three schemes tested; the recommended one withdrawn

Implemented as **one core option**, `respiration.support` ∈ {`current`, `clamp`, `impute`},
**default `current` and proven inert** (the baseline reproduces to the digit).

### The premise that failed, and the physiology behind it

The prompt recommended **imputing O₂ = 0** where the model does not grow, arguing that "O₂ falls to
zero continuously as growth does". **It does not: a non-growing cell still respires for
maintenance.** Measured at every temperature with growth ≤ `_MASK_G` across P12's twelve converged
endpoints:

| endpoint | T (°C) | growth | O₂ | status |
|---|---|---|---|---|
| A(b20) | 15 | 1.00e-4 | **1.570** | FEASIBLE-NOT-GROWING |
| Bstar(b8) | 15 | 1.00e-4 | **0.525** | FEASIBLE-NOT-GROWING |
| p81(b7) | 15 | 1.00e-4 | **2.237** | FEASIBLE-NOT-GROWING |
| worst(b5) | 50 | 4.7e-5 | **5.674** | FEASIBLE-NOT-GROWING |
| B(b3) | 11 temperatures | 0.000 | NaN | INFEASIBLE |

**15 dead temperatures: 11 INFEASIBLE — every one of them the dead basin — and 4
FEASIBLE-NOT-GROWING. Among the eleven LIVE endpoints it is 4 of 4.** So for any model that grows
at all, the growth mask was discarding *real predictions*.

### Why `impute` was withdrawn

Imputing O₂ := 1e-9 where the true prediction is 0.5–5.7 is a factor of ~1e9, ~21 in log, ~110
log-likelihood units. Three measurements, any one of them disqualifying:

- **It fails P10's own D3a gate** — the instrument the tie-break had to pass — at b3, with
  **|Δ| = 119.1447** between an evaluation after itself and after a different point. `clamp` is
  **0.0000** at all twelve.
- Its continuity step is **2,300 log-likelihood units per 0.05 sd**.
- **Its live−dead gap is the epsilon, not the evidence**: 774 / 1,553 / 2,511 at ε = 1e-6 / 1e-9 /
  1e-12.

There is also no "existing ε" to inherit. The 1.42 floor is on the **sd of log O₂**, added in
quadrature — it widens the error bar and never touches the predicted value — and the only `1e-9`
constants in the module are solver tolerances and one guard in an RQ helper the likelihood never
calls.

### The knife-edge: the mask is an ATTRACTOR

| endpoint | temperatures within 1 % of `_MASK_G` | relative distance |
|---|---|---|
| **B(b3), A(b20), Bstar(b8), p38(b22)** | 1 each | **0.000000** |
| p81(b7) | 1 | 0.004320 |
| the other seven | 0 | 0.53 – 13.4 |

**Five of twelve endpoints park a temperature within 1 % of the threshold; four sit on it exactly.**
p38's 15 °C growth is 9.999999859874725e-05 — **1.4e-12 below 1e-4**. Independent optimisations
from unrelated prior draws do not land on the same knife-edge by chance: the optimiser parks a
temperature on the mask to escape the 15 °C respiration penalty, worth ~2.8 units.

**`current` is itself state-dependent there**: it fails P10's 0.0000 rule at p38 with
**|Δ| = 0.0157**, the knife-edge showing through the ramp's 0.01 floor — in the likelihood P11's
two nested runs were computed on.

### The choice: `clamp`

`clamp`'s mask is `keep = isfinite(o2) & (o2 > 0)` — it drops the growth mask entirely and **scores
feasible-not-growing points at full weight**, masking only genuine infeasibility. It is adopted
because **it scores real predictions the mask was discarding**, which is a stronger justification
than "it removes a discount", and because:

- **state-independence at the boundary: ten evaluations at p38, fresh model each →
  −9.9893897954 ten times, spread 0.0000000000**;
- it removes the discount item 1.21 was raised for.

**Cost, stated:** p38 loses **2.8 units** (−7.186 → −9.989) because its 15 °C prediction is now
scored, and the live−dead gap moves **11.691 → 11.245**. The gap barely moves, and the reason is
worth recording: the discount was never the dead basin's main protection — **the NaN mask is**, and
that is irreducible, because a model that is infeasible has no O₂ prediction to score.

## TASK 2 — gated, then turned on

- Seven-strain gate with the option **OFF**: **79/79, 60/60**, `tpc` rc=0 — plumbing inert.
- **ON for eciML1515 only**, verified read from the config (p38 = −9.9894).
- **P3 gate re-run: `gate_def_table.csv` is BYTE-IDENTICAL.** Growth R² at Parsa's θ unchanged in
  all ten comparisons; configuration D's respiration R² unchanged (MAP 0.7039 / 0.7062, posterior
  median 0.7246 / 0.7268). The reason is structural: `gate_def.py` calls `flux_tpc` directly and
  never reads `ctx["respiration"]`. Dated note added to `reports/P3_gate/README.md`; the gate's
  history is not rewritten.

## TASK 3 — the surface. **STOP.**

Twelve lines re-scanned **at p38** (not θ_A), 41 points at 0.05 sd over ±1 sd, fresh model per
evaluation, under both schemes. Judged by the refined rule: **the largest step between two FEASIBLE
points decides**; a step across a feasibility transition is the boundary of the model's feasible
set, is reported separately, and is not smoothed.

| scheme | largest feasible-to-feasible step | line | at | verdict |
|---|---|---|---|---|
| current | **8.5519** | `axis:topt_scale` | +0.90 → +0.95 sd | **NOT SAMPLEABLE** |
| clamp | **8.5517** | `axis:topt_scale` | +0.90 → +0.95 sd | **NOT SAMPLEABLE** |

Every other line passes under both; next largest `axis:dCp_scale` 4.82, `axis:kcat_scale` 2.73.
**The two numbers differ by 0.0002 — the support handling is not the cause.** 13 feasibility
transitions were found per scheme, all within |0.00–0.75| sd, largest step 1.64 (clamp) / 1.73
(current); all are at 15 °C entering or leaving the feasible set, and none is smoothed.

### What the step is

96 % **growth term** (−8.1775) against 4 % respiration (−0.3743), spread over the cold end: 27 °C
−3.40 (growth 0.2224 → 0.1512), 30 °C −2.97 (0.6226 → 0.5185), 25 °C −1.66 (0.0861 → 0.0539). This
is the LP growth response P11 deliberately left unfloored, and no support rule touches it.

### And it is curvature, not a cliff — reported, not used to override the rule

Steps along `axis:topt_scale` from +0.40 sd:

`−0.71, −0.83, −1.11, −1.18, −1.44, −1.83, −2.39, −3.05, −4.15, −5.63, −7.25, −8.55, −8.46`

Monotone, smoothly increasing, small second differences, at a log-likelihood of **−47.8 — some 40
units below p38**, a region with essentially no posterior mass. A cliff is an isolated jump among
small steps (P9's were `0.1, 0.1, 70, 0.1`). **This is not overridden on that basis**: inventing a
curvature criterion after seeing the data is precisely the error recorded in P12 D5/D7, and the
rule was fixed in advance. The evidence is reported so the decision can be taken on it.

### A finding about P11

P11 verified SAMPLEABLE **at θ_A only**, where this line's largest step was **3.20**. At **p38** —
the better optimum, which beats P11's own best sample — the same line, instrument and rule give
**8.55**. **P11's sampleability verdict is centre-dependent and was established at a single point.**
That does not invalidate its runs and does not explain their disagreement (P12 settled that as one
basin explored to two depths), but the claim is weaker than it read. Qualified by dated note,
numbers unedited.

## TASKS 4 and 5 — NOT RUN

By the stop condition, fixed in advance and reaffirmed by the user: *"If a line does have a >5-unit
step between two feasible points, the original stop stands."* **The two nested runs were not
started. No posterior, no log Z, no agreement verdict, no `dTm` interval is quoted, because none
was computed.**

The two predictions pre-registered in D6 — that the clamp posterior moves away from the mask
knife-edge, and that posterior-predictive growth at 15 °C rises — **cannot be evaluated**, since
both require the clamp posterior. They stand as written for whoever runs it.

## Reconciliation against §0c

- **Which of R1–R4 moved:** **none, in the sense of being closed.** R1 was the target and is
  *advanced but not closed*: the likelihood is better posed (the discount is gone, the term scores
  real predictions, and the evaluation is now state-independent where it was not), but no posterior
  was earned. R2, R3 and R4 are untouched, as D0 said in advance.
- **What is retracted or qualified, by dated note, numbers unedited:**
  - **P11's SAMPLEABLE verdict** — centre-dependent, established at θ_A only; 3.20 there against
    8.55 at p38.
  - **P12's ceiling test** — p38 and A beat the sampler's best *partly by exploiting the mask*:
    both sit exactly on the threshold and both lose ~2.8 units once their 15 °C prediction is
    scored. P12's basin count (13.868 against 1.785) is untouched.
  - **The prompt's recommended support form** — withdrawn on physiology and measurement.
- **What this does NOT license:** it does not license quoting any posterior; it does not license
  the remaining eight fits (1.17 stays blocked); and it does not license the claim that the
  likelihood is now sampleable — one line says otherwise, at p38, under both schemes.
