# T3 — the four determinism schemes, measured: only a fresh model per evaluation is deterministic, at 3.2× the cost

_2026-09-15 → 2026-09-16, branch `t3/determinism` from main `b5b06c6` (the merge of T2's #41),
worktree `../etcGEMs-t3`. Decisions D0–D4. **Measurement only: no core change, no default changed,
no option enabled, no fit, no sampler run, no reserved seed consumed.** The remedy is the PI's to
register (OPEN_ITEMS 1.34, 1.35)._

## What was registered before anything ran (D0, committed alone at `ac7e821`)

**The fixed input set** — `inputs.json`, sha256 `8aef2dfd9d61db83255add520e13e2ee831a9b188881da5249b01cb95900f27e`,
22 vectors each hashed, built by rule from the T2 checkpoints (themselves hashed):
(i) run 3's crashing live point 654; (ii) its three +1.28 siblings (791, 297, 105); (iii) the five
largest-offset live points of each of runs 1 and 2; (iv) five prior draws (seed 17401), three
feasible and two infeasible; (v) Parsa's E LB MAP θ, the historical face case, with two E LB prior
draws (seed 17402) as interleaving companions.

**The protocol:** N = 50 evaluations of every input in **one persistent worker**, in a registered
interleaved order (50 rounds, each a fresh permutation by `default_rng(17403)`, never the same
input twice in succession), against a **fresh-process reference** evaluated twice. Scheme D at
N = 5, its cost being what was needed from it. **The statistic:** max |value − fresh reference|.
**The rule, not revised:** DETERMINISTIC if every input's max deviation ≤ 1e-9; MARGINAL if
≤ 1e-6; FAILS otherwise; among deterministic schemes recommend the cheapest by measured
wall-clock; if none, recommend nothing.

## The reference, and two caveats it exposed (D1)

All 22 inputs are **bit-identical** across two fresh-process evaluations. Two things worth the
record: the crash point's fresh value on the worker path is −19.760854155863385 against T2's
in-process −19.760854009581777, a **1.5e-7** difference between two construction paths (the rule
uses the worker path, the one the runs use); and T2's "exhaustive fresh audit" ran its 800 points
per checkpoint in a **persistent 16-process pool**, so its ≤ 5e-3 offsets for runs 1–2 were
themselves measured with the defect present. Its four +1.28 points stand — this battery reproduces
them — but its small offsets were never a clean measurement. T3's reference is.

## Scheme A reproduced the defect, so the instrument is valid

Max deviation **1.815**; 16 of 22 inputs above 1e-9; four above one full unit. Solver statuses
never varied, and the two −∞ draws were −∞ in all 50 evaluations (the short-circuit is
deterministic).

## The table (D3)

| scheme | end-to-end s/eval | D NLDM max dev | E LB max dev | inputs > 1e-9 | unresolved | verdict |
|---|---:|---:|---:|---:|---:|---|
| **A** current | 1.79 | 1.280 | 1.815 | 16 / 22 | 0 | **FAILS** |
| **B** solver reset per call | 2.91 | 1.578 | **23.277** | 18 / 22 | 0 | **FAILS** |
| **C** lexicographic tie-break | 1.49 | 0.223 | **∞** | 20 / 22 | **111** | **FAILS** (and a different model) |
| **D** fresh model per evaluation | **5.70** | **0.000** | **0.000** | **0 / 22** | 0 | **DETERMINISTIC** |

**B is worse than doing nothing** — 23.28 against A's 1.82, at 63 % more cost, and it spreads the
damage from 3 evaluations on run 3's siblings to order-1 excursions on 13 of the 19 D-NLDM inputs
including the crash point. The reading is mechanical: a reset discards the basis but not the
**degeneracy**, so each solve re-enters a flat face from a different start. P6 D3a saw a reset
return E LB to its fresh value once; P17 D2 already found it did not remove the 0.088 event. T3
settles it: **a basis reset is not a remedy.**

**C is disqualified before its verdict.** D0 required it to return the same vertex as pFBA first.
It does not, at any input: O₂ differs by up to **4.58** on D NLDM and **8.40** on E LB (96 %
relative), growth by up to **2.27** /h on E LB; 111 of its 150 E LB evaluations returned `numeric`.
A different tie-break is a different model. Whether a *correct* single-solve tie-break could be
built is a separate question this measurement does not answer.

**D returned exactly the reference value at every one of its 110 evaluations**, both spaces,
including the −∞ draws.

**Recommendation, by the registered rule: scheme D, at a measured 3.2× the current cost.** D's
overhead is the process spawn and model build, which the in-worker timer hides; the honest basis
is each battery's own elapsed time per evaluation, and on that basis D is 5.70 s against A's 1.79.
T2's 4–5× estimate was pessimistic.

## Two mechanisms, reported separately (addendum 1)

**The corruption attaches to the evaluation, not to θ.** Under A the crash point was *clean* over
50 evaluations (6.9e-8) while its siblings carried the +1.28 that crashed run 3. Which θ is hit
depends on what the worker evaluated before it, so **no θ can be certified clean by a spot check**.

**The E LB inputs are a second, larger magnitude.** 1.538 at Parsa's MAP with 12 of 50 evaluations
above one unit, 1.815 at a prior draw, 23.28 under B — an order of magnitude above D NLDM's, and
E LB is exactly the configuration whose O₂ at optimal growth is a **face**: P6 D3a measured its
FVA range as [5.8, 114.5] at 37 °C and [0, 190] at 45–50 °C, and P10 D1 held F LB for the same
reason. D NLDM's O₂ is unique at most temperatures, which is why its defect is mostly a 1e-8 haze
with rare order-1 excursions. Plausibly one cause — face degeneracy — at two widths. **An E or F
run would be far worse than the D runs T2 attempted**, which bears directly on 1.17.

## What it implies for runs 1 and 2 (D4)

The **20 highest-weight posterior samples of each run, re-evaluated fresh, are clean**: max
2.02e-08 (run 1) and 5.16e-09 (run 2), nothing above 1e-6. **The defect is therefore not a
candidate explanation for their disagreement.** Something else is also wrong — and P17's
analytical controls, which failed with no LP present at all, are where that has to be looked for.
Limitation, stated plainly: the top 20 cover only **0.3–0.4 %** of the posterior weight, so this
establishes that the dominant samples are clean, not that the bulk is.

The accumulation argument, for scale only: at scheme A's measured D-NLDM rates (49.1 % of
evaluations above 1e-9, 6.6 % above 1e-6, 0.32 % above 1e-3 — and those 0.32 % are all above one
unit), one run's ≈ 221,000 evaluations expects **≈ 14,650** deviations above 1e-6 and **≈ 700
above one unit**. The error is not symmetric: **42.9 %** of deviating evaluations are *inflated*,
and an inflated live point is never replaced until the threshold passes its true value. Run 3
crashed carrying four such points in 800. Assumptions (rates transfer; evaluations independent —
they are not) are stated in D4. **Neither run is corrected, recomputed or re-run.**

## The reach backwards, and its limit (D2)

P6 D3a (2026-09-09, *"which point of that face the solver returns is set by its basis history"*),
P15's deterministic crash at dlogz 2.168, P17's 0.088 event with *"zero canonical LP
coefficient/bound/objective differences"*, T2 D6's 0.028, T2 D11's crash and T3's +1.28 and +1.54
are **one phenomenon at different magnitudes**.

**The limit:** P17's **analytical** controls failed with **no LP present at all** — narrow-mixture
active probability 0.084 / 0.785 / 0.231 against the exact 0.30437 — so a genuine sampler weakness
exists independently, and nothing here touches that finding. What may need revisiting is P17's
attribution of its **real-path** observations, in particular the living-group ancestry collapse
(454 live / 30 ancestors, correlation 0.99556), which is also what one would get mechanically if
inflated points stay above threshold longer than they should. **Stated as a hypothesis with its
test** (D2), not as a retraction: re-evaluate the dominant ancestors fresh; if they carry inflated
stored values while the non-dominant ones do not, P17's attribution needs a dated qualification;
if they are clean to 1e-9, the collapse is the sampler's own. P17's numbers are not edited; a
dated note in its report points here.

## What this licenses

A recommendation for the PI to register (1.35), and nothing else. **No scheme was implemented, no
option enabled, no fit launched.** R1 stays open. The reserved seeds 17904–17905 remain unused;
17901–17903 are spent.

## Reconciliation (§0c and RIGOUR)

**Which of R1–R4 this moves:** none directly. **R1 stays OPEN** and its blocker is now measured
rather than inferred; T3 supplies the evidence for the remedy decision (1.35) and takes none.
R2, R3 and R4 are untouched.

**What it retracts or qualifies, by dated note with numbers unedited:** T2's "exhaustive fresh
audit" is qualified — it ran in a persistent pool, so its ≤ 5e-3 offsets for runs 1–2 were
measured with the defect present (its four +1.28 points stand and are reproduced here). T2's
estimate of a fresh-model remedy at 4–5× is corrected to a measured **3.2×**. OPEN_ITEMS **1.22**
is restated from a cost optimisation to a correctness question that the measurement answers
negatively. **P17 is qualified by a dated note in its report and by nothing else**; its numbers
are not edited, its analytical-control finding is untouched, and the ancestry point is recorded as
a hypothesis with its test.

**What this does NOT license:** adopting any scheme (that is 1.35, the PI's); any statement about
E, F, M9 or another organism beyond the observation that E LB's face degeneracy is an order of
magnitude worse than D NLDM's; any correction, recomputation or re-run of T2's runs; any claim
that runs 1 and 2's disagreement is explained — it is not.

**RIGOUR by number.** 1 — D0 was committed alone (`ac7e821`) with the input set hashed, the
protocol, the statistic, the rule and the budgets, before any battery ran; the batteries' raw
outputs were committed before interpretation (`7696d8e`). 2 — the decision rule was not revised:
scheme C is reported FAILS on the rule *and* disqualified on the vertex check registered in D0,
and the 1e-9 bar was not relaxed for the 1e-8 haze. 3 — every outcome retained, including the
failed first TASK 2 attempt (`task2_highweight_attempt1.log`) and all four batteries in full.
4 — the T2 audit and 4–5× estimate qualified by dated addition; P17 by dated note. 5 — scheme D
passing this bar is necessary, not sufficient: it makes the likelihood a function of θ, and says
nothing about whether the sampler then agrees across seeds (D4 shows it may not). 6 — reserved
seeds 17904–17905 untouched; T3 used development seeds 17401–17403. 7 — the reference is an
independent fresh-process measurement, not a re-reading of T2's summaries, and it caught the
qualification in the previous sentence. 8 — every battery under a registered SIGALRM budget, one
at a time, none extended. 9 — no likelihood, prior, parameter, medium or default changed: the
lexicographic module is a scratch file outside the core. 10 — the blocker is measured and the
remedy recorded as the PI's decision, not manufactured into a fix. 11 — #41's base read before
merging.
