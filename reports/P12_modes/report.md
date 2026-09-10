# P12 — map the modes: how many basins, how deep, how big, and what separates them

> **Dated note, 2026-09-10 (P13): the CEILING TEST is qualified. The basin count is not. No number
> below is edited.**
>
> TASK 2's ceiling test reported that **p38 (−7.186) and A (−7.213) beat P11's main-run best sample
> (−7.3964)** and concluded that Powell reaches the top of the basin the sampler found. P13 measured
> why, and the margin is **partly an artefact of the growth mask**.
>
> The mask at `_MASK_G = 1e-4` is an **attractor**: **5 of these 12 converged endpoints park a
> temperature within 1 % of it, and 4 sit on it exactly** — p38's 15 °C growth is
> 9.999999859874725e-05, **1.4e-12 below the threshold**. Sitting there means the 15 °C respiration
> prediction is never scored, which is worth **~2.8 log-likelihood units**. Score it, as P13's
> adopted `clamp` support does, and p38 falls from −7.186 to **−9.989**.
>
> So the optimiser exploited a discontinuity the sampler did not, and the comparison is **not
> like-for-like**. The qualification is to the ceiling test only. **The basin count is untouched** —
> it rests on bottleneck barriers of 13.868 against a maximum of 1.785 elsewhere, which no support
> rule affects — and so are the retraction of the multimodality reading and the identification of
> basin 2 as a dead model. See `reports/P13_support/` D4.


_Run 2026-09-10 on `../etcGEMs-venv`, branch `p12/modes`, from main after PR #26 (P11) merged._

**What this run moves, under §0c.** It moves **R1** (a posterior two runs agree on) by establishing
what the posterior's *shape* is before any more sampling is spent on it, and it informs **R3** (right
for the right reason) through each basin's `dTm` and `dTopt`. It **cannot** touch R2 (identification
needs data, not sampling) or R4 (holdout needs a posterior first). No sampler was run.

---

## The question P11 left, stated precisely

P11 ran dynesty twice to its own convergence criterion and the two runs disagreed: log Z by 6.8
combined standard errors, 15 of 16 posterior medians by more than two Monte-Carlo errors. The
natural reading was multimodality — two runs finding two different optima. **That reading is now
qualified, and the qualification came from measuring the points rather than the runs.**

---

## TASK 0 — the fixed points, and what the likelihood is made of there

Three points were taken as fixed references: **θ_A**, P11's main-run posterior median; **θ_B**,
P11's seed-2 posterior median; **θ_P4**, P4's median. A fourth, **θ_B\***, was added as the first
judgement call of this run (D1) and it turned out to matter more than any other decision here.

| point | growth term | respiration term | **total log-likelihood** |
|---|---|---|---|
| θ_A  | **+2.951**  | −13.373 | **−10.422** |
| θ_B  | **−20.109** | −14.848 | **−34.957** |
| θ_B\* | **+4.212**  | −13.317 | **−9.106** |
| θ_P4 | −0.060      | −14.770 | −14.830 |

**θ_A beats θ_B by +24.53, and +23.06 of that is the growth term.** At θ_B the model is nearly
dead: predicted growth spans 0.000–0.163 /h against measured 0.094–2.076, a peak at **7.8 %** of the
observed peak.

### D1 — θ_B is a median, not a mode

θ_B's log-likelihood of −34.96 is **25.9 units worse than seed 2's own best sample** (−9.11). A
median that falls between modes is a point in neither, so θ_B is a **median artefact** and is the
wrong representative of the second run. **θ_B\*, seed 2's best sample, was carried alongside it from
TASK 0 onward** and is B's representative from here. θ_B is retained only as the object whose
artefactual status is being demonstrated.

### The evaluation profile — and why the precedent's speedup does not transfer

One likelihood evaluation costs **2.06 s**, of which **92 % is LP solving** (growth LP 1.07 s,
tie-break LP 0.81 s) and **8 % is preparation**. Pettersen & Almaas report the inverse — 80 %
preparation, 19.7 % optimisation after their COBRApy→ReFramed switch, which bought them 8.5×. Here
the same switch could address at most the 8 %. **The route worth taking is fewer or cheaper LP
solves** — warm-starting the tie-break from the growth solve, or a single lexicographic objective
instead of two sequential solves. Recorded as D2; not acted on.

---

## TASK 1 — the lines between the fixed points

41 points per line on the **log-likelihood** (the prior kept out, so the surface is the model's),
through the same process pool, which was first proved exact: pool against fresh single-process
agrees to **1.18e-09** on eight points.

Rule, written before the scan: a line shows a **VALLEY** if its minimum dips strictly below the
lower endpoint by more than the 0.02-unit evaluation jitter P5 measured.

| line | endpoints | minimum | dip below lower end | verdict |
|---|---|---|---|---|
| θ_A → θ_B  | −10.42 → −34.96 | −35.58 at t = 0.88 | **+0.62** | **VALLEY** |
| θ_P4 → θ_A | −14.83 → −10.42 | −14.83 at t = 0.00 | +0.00 | monotone / shoulder |
| θ_P4 → θ_B | −14.83 → −34.96 | −36.06 at t = 0.82 | **+1.10** | **VALLEY** |
| θ_A → θ_B\* | −10.42 → **−9.11** | −10.42 at t = 0.00 | +0.00 | **monotone**; best −9.07 at t = 0.93 |

244 evaluations, 0.9 min on 16 processes.

**The barrier is between θ_A and the seed-2 MEDIAN. There is no barrier between θ_A and the seed-2
MODE, and the mode is the better of the two.**

### D3 — what a monotone chord does and does not prove

A single straight line finding no barrier is weak evidence of a shared basin: two basins can be
connected along one chord and separated along another, and a monotone chord is also what a long
curved ridge gives. So "seed 2's mode lies inside seed 1's basin" waits for TASK 2, whose local
optimisations follow the surface rather than a chord. What TASK 1 does establish is narrower and
still worth having: **the disagreement in medians is partly an artefact of comparing a point that
neither run visited as a mode.**

---

## Addendum 1 — what the support weight is doing

Raised by the user mid-run, before the basin map was interpreted, on the observation that the
TASK 0 decomposition shows a weight varying with the PREDICTION rather than the observation.
Characterisation only: **nothing was changed.** Full record in DECISIONS D4.

### The exact form, and one correction to the premise

`calibration_multi.py:299–301`:

```python
gs = resp.get("alive_soft_growth")
w = np.minimum(1.0, g[keep] / float(gs)) if gs else np.ones(int(keep.sum()))
ll += float(-0.5 * np.sum(w * ((obsl - pred) ** 2 / varr + np.log(2 * np.pi * varr))))
```

The weight is a function of **predicted growth**, and it multiplies the **respiration term only**.
It does not touch growth. The growth term (`:279–281`) is on a **linear** scale, so a model that
predicts no growth **pays its growth penalty in full** — at θ_B that penalty is −20.109, the largest
single term in the decomposition. The addendum's premise about the growth term is therefore not what
the code does; its conclusion about the weight is nonetheless right, in the term where the weight
actually acts.

**P10's reason, on record before any criticism:** the pre-existing hard mask at `g ≥ 1e-4` switched
an entire temperature in or out of the term as growth crossed a threshold — a step discontinuity by
construction, and P10 D2 attributed half of P9's measured cliffs to it. The weight makes the support
continuous in θ. At the mask boundary the weight is 0.01, so the residual step is 1 % of the term
rather than 100 %. That is a real defect being properly fixed.

### The counterfactual

The addendum's schemes (ii) and (iii) both assume a log-scale growth term. Since it is linear,
**(ii) is a no-op** — flooring the growth prediction at 1e-3 moves the total by 0.002 units — and
(iii) cannot return −inf from growth. Restated to act where the weight acts:

- **(ii′) no discount** — hard mask kept, `w ≡ 1`.
- **(iii′) no support handling** — no mask, `w ≡ 1`, every temperature scored.

| gap | (i) as is | (ii) addendum's floor | **(ii′) no discount** |
|---|---|---|---|
| θ_A − θ_B  | +24.535 | +24.537 | **+39.967** |
| θ_A − θ_B\* | −1.316  | −1.317  | −1.464 |

Units the weight hands back:

| θ_A | θ_B | θ_B\* | θ_P4 |
|---|---|---|---|
| 1.263 | **16.696** | 1.115 | 1.234 |

**The weight discounts; it does not bound.** It is worth ~1.2 units to every live point and **16.7
units to θ_B**, and removing it widens the A−B gap by 15.4 units.

**But it is not manufacturing the seed disagreement.** θ_B was already established as a median
artefact before this addendum arrived, and at θ_B\* the discount is 1.115 units — the same as at
θ_A — with B\* still better than A under both schemes. The weight flatters a point that was never a
mode.

**(iii′) is UNDEFINED at every good point, and that is the finding.** At 15 °C the model does not
grow at θ_A, θ_B\* or θ_P4, and `flux_tpc` returns **NaN** for O₂ — there is no prediction to score,
not a zero whose log is large. It is finite only at θ_B (−53.780), which is alive-but-negligible at
15 °C rather than dead. **The scheme that pays the full penalty everywhere can be evaluated at the
dead-model point and not at the three live ones.** Support handling is structurally required; the
open question is only which BOUNDED form replaces a discount.

### Scope

The **floor and the tie-break are unaffected** — they act on the respiration variance and on the
LP's choice of vertex, neither of which involves the weight. P11's **sampleability verdict on the
cold lines (15–25 °C) is not independent of it**: those are exactly the temperatures where predicted
growth is small and `w < 1`, so a change to the support would require re-scanning them. Not
re-scanned here. Recorded as OPEN_ITEMS **1.21**, with a new step 4 in the §0b sequence placing this
decision **before** per-basin sampling.

---

## TASK 2 — the basin map, in four stages, because the first one did not answer the question

### Stage 1: the screen (100 optimisations, 2.92 h) — and why it is only a screen

96 prior draws through P11's proven transform (seed 21) plus θ_A, θ_B, θ_B\* and θ_P4; Powell on
the log-posterior, 16 processes, 600-evaluation cap; 0 failures.

**96 of the 100 starts hit the cap** (nfev min 433, median 600, max 600 — no overshoot). In sixteen
dimensions one Powell sweep is sixteen Brent line searches, roughly 400–600 evaluations, so the cap
bought about **one sweep per start** and no endpoint is a local minimum. The output says so without
needing to be argued:

| single-linkage threshold | 1.0 | 2.0 | 4.0 |
|---|---|---|---|
| clusters | 76 | 23 | 10 |

A factor of 7.6 across a factor of 4 — **the stability check the prompt itself asks for, failed.**
16 of the 23 clusters at threshold 2.0 hold one endpoint, and the six best endpoints are mutually
2.87–9.79 apart at nearly equal likelihood.

The 600 cap came from the prompt. It is the one place the task as specified cannot deliver what it
asks, and the honest response is to say so rather than report a budget artefact as a mode count
(**D5**). The screen is kept: it cost 2.92 h and it bounds the answer, since descent can only merge
endpoints, never split them.

### Stage 2: barriers, not clustering

A basin is the absence of a barrier, not a distance threshold, and unlike clustering the test does
not need converged endpoints — a hump between two points separates them whatever their provenance.
Nine representatives, 36 chords, 41 points each, 1,476 evaluations, 4.8 min.

**My first reduction of that table was wrong and is retracted in D6 before it reached any
conclusion.** Union-find over "no barrier" gave three components — but six of the ten unseparated
pairs have depth **exactly 0.000 with the minimum at an endpoint**, which is a *monotone descent*
and means the lower point is not a local optimum at all. That is the opposite of "same basin", and
it merged A and B\* — separated by 0.532 — through P4, a point downhill from both. Two claims died
with it, both of which the screen alone would have supported:

- **the 64-endpoint cluster carrying 66.7 % of prior volume is not a mode** — it lies 0.178 below
  B\* on their chord;
- the four best points were not "four candidate modes"; under D7's scale they are one basin.

### Stage 3: the threshold, fixed before the data (D7, on the user's addendum 2)

The 0.5-unit threshold was inherited from TASK 1, where it was calibrated against the **0.02-unit
evaluation jitter** — the wrong scale for this question. The right scale is the **kink** scale:
P9/P10 measured the growth term's LP kinks at **1–3 units** and P11's sampleability rule accepts
**5**. A dip of that size is what one piecewise basin floor looks like where a chord crosses a
basis change.

> **Separate basins** only if the barrier exceeds **5.0** units **and both endpoints are local
> optima by the termination reason** — a capped endpoint cannot found a basin. **1.0–5.0 is
> sub-structure** of one basin. **Below 1.0 is noise.** Counted at 3, 5 and 8; headline 5.

Written into DECISIONS.md and committed while `task2c_run.log` still held **zero** result lines.

### Stage 4: convergence, and the bottleneck barrier

Twelve representatives continued from the endpoints already paid for, 3,000-evaluation cap,
xtol/ftol 1e-4, termination reason recorded (1.73 h). **11 of 12 terminated on tolerance** and are
demonstrated local optima; p83 capped and is therefore ineligible to found a basin. The barrier
test was re-run on the converged points (66 chords, 2,706 evaluations) and reduced to **bottleneck
(minimax) barriers** — the minimum over paths of the maximum barrier — because a straight chord is
only a *sufficient* witness of connection (D3). Chord-connectivity therefore gives an **upper
bound** on the basin count: curved paths can merge further, never split.

**The bottleneck matrix is sharply bimodal, and that is the entire result.**

| | value |
|---|---|
| B(b3) to every other endpoint | **13.868**, identically |
| every other pair, maximum | **1.785** |

Nothing lies between. **Any threshold from 1.79 to 13.87 returns two components** — a factor of
7.8 — so 3, 5 and 8 all give **2**. This is the stability the screen's clustering could not
provide.

## TASK 2 — the answer

**TWO basins.**

| | basin 1 — LIVE | basin 2 — DEAD |
|---|---|---|
| members | A, B\*, P4, p38, p50, p81, p83, big(b10, n=64), big(b9), big(b6), worst(b5) | B(b3) alone |
| best log L | **−7.186** (p38) | −18.877 |
| growth term | **+6.363** | −18.860 |
| respiration term | −13.549 | **−0.017** |
| peak predicted growth | **1.713 /h (82 %** of the observed 2.076) | **0.000 /h (0 %)** |
| dTm | −3.07 to −4.50 | **0.000** |
| internal bottleneck barriers | 0.00–1.785 (noise + kink-scale sub-structure) | — |

**Prior-volume fractions** come from the screen and are labelled as such: the live basin takes
essentially all of it — the single 64-endpoint cluster alone is 66.7 % — and θ_B's region draws
10.4 % (10 of 96 prior starts reached basin 3 in one sweep). These are basins-of-one-sweep and are
an **upper bound** on the number of true basins.

### What this retracts

**P11's seed disagreement is not evidence of multimodality among live models. P12 retracts that
reading rather than qualifying it.** θ_A and θ_B\* — the two runs' best points — have a bottleneck
barrier of **0.266**, which is *noise* by D7's bands. They are the same basin. The two nested runs
explored **one** basin to different depths and disagreed because dlogz stopped them at different
places, which is exactly P11's own "necessary and not sufficient" conclusion — with the mode
question now closed rather than open.

The one genuinely separated basin is reachable only by a model that does not grow, and **addendum 1
showed that the support weight is what lets such points score at all**. The two threads meet: *the
only multimodality in this posterior is an artefact the likelihood's support handling keeps alive.*

### The ceiling test — passed

**Two continuations beat P11's main-run best sample of −7.3964: p38 at −7.186 and A at −7.213.** So
a derivative-free optimiser with a real budget reaches the top of the basin the sampler found and
passes it by 0.21 — and the sampler was not sitting at the optimum either. The caveat D7
provisionally attached to height comparisons is **lifted**.

The optimiser targets the log-**posterior**, so small negative moves in log-likelihood
(B\* −8.300 → −8.311) are not failures; both columns are in `task2c_converged.csv`. Repeated
evaluation of one point differs by ~0.02 (P5), which is why A appears as −7.213 and −7.197 in
different tables.

### Deadness and the weight, per endpoint

DEAD-MODEL by the addendum's criterion (peak growth below half the observed): **B(b3)** at 0 % and
**worst(b5)** at 47 %. Every live endpoint of interest sits at **79–84 %**. The discount credit
separates them just as cleanly — **1.05–1.24 units** for every good live endpoint against **8.10**
for big(b6) and **9.15** for worst(b5). *The weight most flatters the two worst models in the set.*

## TASK 3 — what each basin is

### The thermal curve

| T (°C) | measured | basin 1 | basin 2 |
|---|---|---|---|
| 15 | 0.094 | 0.000 | 0.000 |
| 20 | 0.256 | 0.124 | 0.000 |
| 25 | 0.585 | 0.500 | 0.000 |
| 30 | 1.055 | 1.169 | 0.000 |
| 35 | 1.563 | 1.564 | 0.000 |
| 37 | 1.853 | 1.661 | 0.000 |
| **40** | **2.076** | **1.713** | 0.000 |
| 43 | 1.594 | 1.663 | 0.000 |
| 45 | 0.915 | 1.211 | 0.000 |
| 47 | 0.457 | 0.433 | 0.000 |
| 50 | 0.094 | 0.001 | 0.000 |

Basin 1 reproduces the curve's shape and its optimum at 40 °C, underestimating the peak by 17 %
and the cold tail at 15–20 °C. Basin 2 is flat zero.

### The O2 face — the Pettersen & Almaas reproduction, and it does NOT reproduce

At optimal growth, min and max O2 uptake through P10's own `min_o2`/`max_o2` tie-breaks:

| basin 1 | value |
|---|---|
| face width, mean over live temperatures | **0.009 mmol/gDW/h** |
| face width, max | **0.021** |
| as a fraction of the pFBA O2 | **0.001 %–0.28 %** |

**The face has essentially collapsed.** Pettersen & Almaas found equally-fit particles differing
widely in cytochrome-oxidase flux; in this model, at the optimum, under P10's pFBA tie-break, O2 is
pinned to within a quarter of a percent. That is the tie-break doing exactly what 1.13 adopted it
for, measured here for the first time across the whole curve rather than at four temperatures.

Basin 2's face is the opposite and is diagnostic: O2 is **NaN at 11 of the 12 temperatures** (no
growth, so no solution to read O2 from), and at 50 °C alone it spans **4.355 to 8.710 — a 100 %
face**. Its respiration term is therefore **−0.017**: a model that grows nowhere is charged
essentially nothing for respiration, against basin 1's −13.549. This is the support-weight artefact
of addendum 1 shown at the level of the fit rather than the arithmetic.

### dTm — reported prominently, as the prompt requires

**The only endpoint with dTm at or near zero is B(b3), the dead basin: dTm = 0.000 exactly, with
dTopt = 13.873.** Every live endpoint requires **dTm between −3.07 and −4.50** (A −3.81, p38 −4.02,
B\* −4.08, p81 −4.08, P4 −4.07, p50 −3.07, p83 −4.50); the two weight-propped poor endpoints go
further still (big(b6) −10.18, worst(b5) −13.07).

**This sharpens §0b step 2 decisively, and not in the direction it hoped.** Fitting these data with
this model requires shifting the melting temperature 3–4.5 K below a **measured** meltome, and the
one place in parameter space where the meltome is honoured is a model that does not grow. So
constraining dTm to zero would not merely "collapse the multimodality" — on this evidence it
removes the fit, and the shift becomes **a model failure to explain rather than a nuisance
parameter to fix**. That is the PI's decision, now with numbers under it.

## TASK 4 — the recommendation

**(c) ONE DOMINANT BASIN** — with the qualification that the second is not a scientific alternative
at all, and that this is stronger than (c) as the prompt framed it.

Among models that grow, there is **one** basin. The second basin is a model with zero predicted
growth at every measured temperature, separated by 13.9 units, which survives scoring only because
the respiration term's support weight charges it −0.017 instead of a full penalty. It is not an
alternative explanation of the thermal curve and must not be presented as one.

**What this licenses, and what it does not.** Per-basin sampling on restricted priors (§0b step 5)
is **not needed**: there is one live basin, so a single well-converged run on it is the posterior.
But that run should not be started until **1.21** is settled, because as the likelihood stands a
sampler can spend real mass on the dead region — that is what the second nested seed did. The
cheapest sound sequence is: settle the support handling, then one nested run at nlive ≥ 800 with a
second seed for agreement (1.19), on the live basin only. Estimated **10–12 h each**, unchanged
from P11's costing.

**Is P8's "unimodal, isotropic" reading retracted, qualified or intact?** **Intact, and
vindicated.** P8 found the chains' ensemble unimodal with no ridge (PC1 16.5 %, τ 110–121 on every
component); P12 finds one live basin containing every point those chains and both nested runs ever
occupied. What was wrong in that era was never the unimodality — it was the *explanation* for
τ ∝ N, which P9 corrected to a cliffed likelihood and P10 fixed. P8's geometric reading survives
P12 unchanged.

## TASK 5 — against the precedent, and the record

### Pettersen & Almaas 2023, and why the comparison inverts

The precedent for this whole exercise is Pettersen & Almaas's finding that Li et al.'s yeast
etcGEM, calibrated by SMC-ABC over **2,292 per-enzyme parameters**, is seed-unstable and
multimodal. P11's seed disagreement in a **16-parameter** reformulation looked like the same
disease in a smaller body, and the project recorded the conclusion that **"the multimodality is in
the thermal formulation, not the parameter count"** (§0c).

**P12 tested that claim directly and it does not survive.** With endpoints actually converged and
basins defined by bottleneck barriers rather than by a clustering threshold, this posterior has
**one live basin**. The two nested runs' best samples are **0.266** apart — noise. The one
separated basin contains only models that do not grow, and it is kept scoring by the likelihood's
support weight rather than by the data. So the multimodality is **not** intrinsic to the thermal
formulation, at least not at 16 parameters with gas-exchange data; the sentence is withdrawn in
§0c by dated note.

Two further inversions of the precedent are worth recording, because both cut against reusing
their solutions here:

- **Their cost route does not transfer.** Their 8.5× speedup came from replacing COBRApy with
  ReFramed, because **80 % of their time was model preparation** and 19.7 % optimisation. Here the
  split is the mirror image — **92 % LP solving, 8 % preparation** (growth LP 1.07 s, tie-break LP
  0.81 s, of 2.06 s total) — so the same change could buy at most 8 %. The route worth taking here
  is *fewer or cheaper LP solves*: warm-starting the tie-break from the growth solve, or one
  lexicographic objective instead of two sequential ones (D2, not acted on).
- **Their central diagnostic does not fire.** Their FVA on equally-fit particles found wide
  variation in cytochrome-oxidase flux. Under P10's pFBA tie-break, measured here across all twelve
  temperatures, the O2 face at optimal growth is **0.001 %–0.28 %** of the pFBA value. The
  degeneracy they diagnosed is, in this model, already closed.

What does carry over is their **method**, and it is what produced this report: local optimisation
from prior draws, hierarchical clustering of endpoints, and testing equally-fit points rather than
trusting a sampler's summary.

### The record

- **`docs/OPEN_ITEMS.md`**: **1.19 restated** (two agreeing runs still close R1, but they no longer
  arbitrate between modes, and must not start before 1.21); **1.20 added** — the `dTm` decision,
  filling §0b step 2's forward reference with numbers; **1.21 added** (addendum 1) — decide the
  respiration term's support, a bounded penalty rather than a discount; **1.22 added** — per-basin
  sampling is unnecessary and §0b step 5 should be struck. A **§4b note** and a **§0c note**
  withdrawing one sentence.
- **Dated notes, no numbers edited**: `reports/P8_ridge/report.md` (intact and vindicated),
  `reports/Y2_regime_posterior/report.md` and `reports/Y1_yeast_audit/report.md` (their own results
  unaffected; the inference to *our* posterior withdrawn), `reports/P11_nested/report.md`
  (multimodality framing qualified, then retracted by D8).
- **`reports/synthesis/evidence.csv`**: rows **P12a–P12g**, one of them typed `retraction`.
- **A new standing hazard** in §4: `multiprocessing` from stdin respawns forever — found as a
  13.6-hour orphan during this run, the second occurrence.

### Verification

| # | item | result |
|---|---|---|
| 1 | TASK 0 fixed points and decomposition | θ_A −10.422, θ_B −34.957, θ_B\* −9.106, θ_P4 −14.830; A−B = +24.53 of which +23.06 is growth |
| 2 | evaluation profile | 2.06 s, 92 % LP / 8 % preparation — inverts the precedent |
| 3 | TASK 1 lines | 4 lines, 244 evaluations, pool exact to 1.18e-09; VALLEY to θ_B, monotone to θ_B\* |
| 4 | addendum 1 | weight multiplies respiration only; growth term linear; credit 1.26/16.70/1.12/1.23; (iii′) undefined at every live point |
| 5 | TASK 2 screen | 100 optimisations, 0 failures, 2.92 h; **96/100 capped**; clustering unstable 76/23/10 |
| 6 | TASK 2c convergence | 12 continued, **11/12 terminated on tolerance**, 1.73 h |
| 7 | TASK 2d/2e barriers | 66 chords, 2,706 evaluations; bottleneck 13.868 vs max 1.785 |
| 8 | basin count at 3, 5, 8 | **2, 2, 2** — stable over any threshold in 1.79–13.87 |
| 9 | ceiling test | **passed** — p38 −7.186 and A −7.213 beat P11's −7.3964 |
| 10 | deadness | basin 2 peak growth 0.000 (0 %); basin 1 82 % |
| 11 | O2 face | 0.001 %–0.28 % — the precedent's diagnostic does not fire |
| 12 | dTm | live −3.07 to −4.50; **dTm = 0 only in the dead basin** |
| 13 | stamps | see below |
| 14 | PR | opened, **not merged** |
