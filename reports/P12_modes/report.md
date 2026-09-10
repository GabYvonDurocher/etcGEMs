# P12 — map the modes: how many basins, how deep, how big, and what separates them

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

