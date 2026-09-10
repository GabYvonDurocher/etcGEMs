# P12 — decisions

Standing rules carry over. Branch `p12/modes` from `main` after the P11 merge; no push to `main`;
end in a PR that is not merged. Interpreter `../etcGEMs-venv`. The likelihood is P10's with both
options ON for eciML1515 (tie-break pfba at 1e-9, log-O2 floor 1.42, continuous support 0.01),
read from the strain config; **nothing about the likelihood or the priors changes here**. No
sampler is run. Exit codes checked explicitly.

---

## D0 — which of R1–R4 this run can move, and the first thing the decomposition says

PR #26 merged server-side → `9af3184`; `p12/modes` branched; gates with the options OFF
recorded in the report. **The user's uncommitted edit to `docs/OPEN_ITEMS.md` — sections 0a
(R1–R4), 0b (the sequence) and 0c (the reconciliation rule) — was present in the working tree and
is committed as this branch's first commit, untouched**, before any analysis. This run appends
to those sections; it does not rewrite them.

**Against R1–R4, read from 0a before running anything:**

* **R1 (statistically reliable)** — this run **moves it**, and only in the sense 0a already
  allows: it supplies the basin map that decides *what kind* of sampling is needed. It cannot by
  itself produce a posterior two runs agree on, because it runs no sampler. Its deliverable is
  the licence for the next run, with a cost.
* **R3 (right for the right reason)** — this run **informs it** and cannot close it. If the
  basins are what 0a suspects — "shift enzyme optima **or** shift stability, differently
  compensated" — then the map states the alternatives in the model's own parameters and says how
  far apart they are. Discriminating them needs the per-enzyme data 0a names (temperature-dependent
  kcat on the Topt side; the meltome is already held on the Tm side). A basin with `dTm` near zero
  would bear directly on 0b's step 2, the dTm decision, and that is the single most valuable thing
  this map could contain.
* **R2 (identified)** — **untouched.** The five flat parameters are flat because the data do not
  constrain them; a basin map does not add data. If a parameter that P11 called flat turns out to
  separate basins, that is a statement about the *surface*, not about identifiability, and will be
  said that way.
* **R4 (predictively reliable)** — **untouched.** No holdout is involved.

## D1 — theta_B is the seed-2 *median*, and at that point the model is nearly dead; the seed-2 MAP is carried alongside it

**Where:** TASK 0, on reading the decomposition.

The prompt defines theta_B as P11's seed-2 posterior median, and that is what is used. But the
decomposition shows what that point is: **at theta_B the model barely grows at any temperature**
— predicted growth 0.000–0.163 h⁻¹ against measured 0.094–2.076 — and its log-likelihood is
−34.96 against theta_A's −10.42. The seed-2 run's *best* sample is −9.11 (P11), so its posterior
contains good points; its **median** does not sit near them. A median is a coordinate-wise
summary and in a spread or skewed posterior it need not lie in a region of high density at all.

That matters for TASK 1: a line from A to B may be a line from a good point to a poor one rather
than a line between two basins, and a valley on it would prove nothing about mode structure.
**Decided:** report the prompt's A→B line as specified, and carry **theta_B\*, the seed-2 run's
maximum-likelihood sample**, as a second representative of that run, with the same three profiles.
The basin map in TASK 2 is what actually settles the question, and it includes A, B, B\* and P4 as
starts.

Recorded also because it qualifies P11's own comparison: the fifteen-of-sixteen median
disagreement is real, but "the medians differ" and "the modes differ" are not the same statement,
and TASK 2 is what distinguishes them.

## D2 — the evaluation profile inverts Pettersen & Almaas's, so their 8.5× route does not apply here

**Where:** TASK 0.

One evaluation of this likelihood is **2.06 s**, split **92 % LP solve / 8 % model preparation**
(growth LP 1.07 s, tie-break LP 0.81 s, `apply_state` 0.16 s, medium 0.003 s, carbon cap 0.007 s,
flux reads 0.001 s). Pettersen & Almaas measured the reverse — 0.8 % of their time in
optimisation, the rest in COBRApy model preparation — and got 8.5× by moving to ReFramed
(their Table 1). **That lever is worth at most 8 % here and is not recommended.** The lever that
exists is the LP itself: the pfba tie-break is a second LP costing 0.81 s, 39 % of the total, and
it is the price of a likelihood that is a function of its parameters (P10). Recommendations,
not acted on: warm-start the tie-break LP from the growth solve's basis rather than re-solving
from scratch; or solve the two objectives lexicographically in one Gurobi call, which is exactly
what Pettersen & Almaas propose for their chemostat instability. Both are changes to the
evaluation path and belong in their own run with their own verification.

## D3 — the line profiles say A and B are separated by a valley, but A and B* are not

TASK 1's six line scans (`task1_profiles.csv`, `task1_valleys.json`) put a genuine barrier between
theta_A and theta_B: the log-likelihood dips to -35.58 at t=0.88, +0.62 below the lower endpoint,
and P4->B dips +1.10 below its lower end. Those are VALLEYS by the rule written before the scan
(a dip strictly below the lower endpoint by more than the 0.02 evaluation jitter P5 measured).

But A -> B* — the second seed's MAP rather than its median — is MONOTONE, with no dip at all, and
B* is *better* than A (-9.11 against -10.42; -9.07 at t=0.93 on the extended line). So along this
one line the two seeds' best points are not separated by anything.

Judgement: this does not settle whether the seeds found different modes, and TASK 1 is not the
instrument that can settle it. A single straight line finding no barrier is weak evidence of a
shared basin: two basins can be connected along one chord and separated along another, and a
monotone chord is exactly what a long curved ridge would also produce. The claim "seed 2's mode
lies inside seed 1's basin" therefore waits for TASK 2, whose local optimisations follow the
surface rather than a chord, and whose clustering is the actual test. What TASK 1 establishes is
narrower and still worth having: the seed-2 MEDIAN sits in a region separated from A by a real
barrier, which is why the two runs' medians disagreed on 15 of 16 parameters, and the seed-2
MEDIAN is not a good point of the posterior at all (-34.96, nearly dead). A median between two
modes is a point in neither.

Consequence for the report: the 6.8-sigma log Z disagreement in P11 is not necessarily two
different modes. It may be one mode explored to different depths. TASK 2 decides.

## D4 — the support weight: what it is, and the counterfactual (addendum 1, characterisation only)

Nothing was changed. The likelihood, the weight, the floor and the tie-break are as P11 left them.

### 1. The exact form, quoted

`src/etcgem/calibration_multi.py:282` and `:294-301`:

```python
keep = (g >= _MASK_G) & (o2 > 0)          # _MASK_G = 1e-4  (line 144)
...
        # P10: the support of the term. The hard mask above switches a whole temperature in or
        # out of the term as growth crosses 1e-4, which is a discontinuity by construction --
        # half of P9's cliffs were this, not O2 (P10 D2). With ``alive_soft_growth`` = g_s set,
        # a temperature's contribution is weighted by min(1, g / g_s), continuous in theta and
        # equal to 1 wherever the model grows faster than g_s. Default None = the hard mask.
        gs = resp.get("alive_soft_growth")
        w = np.minimum(1.0, g[keep] / float(gs)) if gs else np.ones(int(keep.sum()))
        ll += float(-0.5 * np.sum(w * ((obsl - pred) ** 2 / varr + np.log(2 * np.pi * varr))))
```

- **A function of** the model's PREDICTED growth `g` at each temperature, not of the observation.
  The addendum reads this correctly.
- **Multiplies the RESPIRATION term only.** It does not touch growth. The growth term is
  `calibration_multi.py:279-281`, and it is on a **LINEAR** scale:
  `-0.5 * ((growth_obs - g)**2 / var + log(2*pi*var))`. So the addendum's premise that "a model
  that predicts no growth has its own growth penalty discounted" is **not what the code does**:
  at theta_B the growth penalty is paid in full, and it is -20.109, the largest single term in
  the decomposition. What is discounted is the model's RESPIRATION penalty.
- **How it enters:** a multiplier on the whole per-temperature respiration term, outside the
  variance. It scales the term, it does not widen the error bar.
- **P10's intent,** from the comment above and P10 D2: the pre-existing HARD mask at g >= 1e-4
  switched an entire temperature in or out as growth crossed a threshold, which is a step
  discontinuity by construction, and P10 attributed half of P9's measured cliffs to it. The soft
  weight makes the support continuous in theta. That is a real defect being fixed, and the weight
  is on record as a reasonable response to it before anything below is said.

Note the hard mask is still applied (`keep`); the weight operates on top of it. At the mask
boundary g = 1e-4 the weight is 0.01, so the residual step is 1 % of the term rather than 100 %.
That is the smoothing, and it works.

### 2. The arithmetic reconciled

Per-scheme totals (`addendum1_schemes.csv`), all from ONE LP solve per point, re-scored:

| point | growth term | resp term (as is) | TOTAL (i) | P11's best sample |
|---|---|---|---|---|
| theta_A     | +2.951  | -13.373 | **-10.422** | main run best -7.40 |
| theta_B     | -20.109 | -14.848 | **-34.957** | seed 2 best -9.11 |
| theta_B*    | +4.212  | -13.317 | **-9.106**  | = seed 2's best sample |
| theta_P4    | -0.060  | -14.770 | **-14.830** | — |

The columns combine as growth + respiration, both already summed over the twelve temperatures.

theta_B at -34.96 is **25.9 units worse than seed 2's own best sample** at -9.11. The addendum's
test is therefore met: **theta_B is a MEDIAN ARTEFACT**, not a mode. This was already caught in
D1 and acted on before the addendum arrived — theta_B* (seed 2's best sample) was carried as B's
representative from TASK 0 onward, and TASK 1 already ran the A -> B* line, which is the extra
line the addendum asks for. Both lines are reported (D3). **theta_B* is B's representative from
here on**; theta_B is retained only as the object whose artefactual status is being demonstrated.

### 3. The counterfactual

The addendum's schemes (ii) and (iii) are both premised on the growth term being log-scale with a
zero-prediction problem. It is linear, so:

- **(ii) as written is a no-op.** Flooring the growth PREDICTION at 1e-3 before scoring moves the
  total by 0.002 units at theta_A and 0.001 at theta_B. Computed and reported for the record:
  A - B = +24.537 against +24.535. It answers nothing, through no fault of the reasoning — the
  term simply was not where the hazard was.
- **(iii) as written cannot return -inf from the growth term** for the same reason.

So the counterfactual that actually answers "does the weight BOUND the penalty or DISCOUNT it"
was restated to act where the weight acts:

- **(ii') no discount** — hard mask kept, `w == 1`: the respiration penalty paid in full wherever
  it is scored.
- **(iii') no support handling** — no mask, `w == 1`, every temperature scored.

| gap | (i) as is | (ii) addendum floor | (ii') no discount |
|---|---|---|---|
| A - B      | +24.535 | +24.537 | **+39.967** |
| A - B*     | -1.316  | -1.317  | -1.464 |

Units the weight hands back (resp term as is, minus resp term at w == 1):

| theta_A | theta_B | theta_B* | theta_P4 |
|---|---|---|---|
| 1.263 | **16.696** | 1.115 | 1.234 |

**The weight DISCOUNTS; it does not bound.** It is worth ~1.2 units to every live point and
**16.7 units to theta_B**, and removing it widens the A - B gap by 15.4 units. The addendum's
inference is correct in its conclusion even though its mechanism was the wrong term: the weight
is what keeps theta_B's score respectable.

**But theta_B was already established as a median artefact, and the weight does not prop up
theta_B*.** At B* the discount is 1.115 units, the same as at A, and B* stays better than A under
both schemes (-1.316 as is, -1.464 with no discount). So the weight is not manufacturing the
seed-2 result. It flatters one point that was never a mode.

**(iii') is UNDEFINED at every good point, and that is the finding.** At 15 C the model does not
grow at theta_A, theta_B* or theta_P4, and `flux_tpc` returns **NaN** for O2 there -- there is no
prediction to score, not a zero whose log is large. Scoring every temperature is therefore not
merely harsh at these points, it is impossible, and (iii') returns NaN for A, B* and P4.

It is finite only at **theta_B**, at -53.780, and for a revealing reason: theta_B is alive-but-
negligible at 15 C rather than dead, so O2 is defined there. The scheme that pays the full penalty
everywhere can be evaluated at the dead-model point and NOT at the three live ones.

So some support handling is structurally required, which is on record as the addendum asked, and
it strengthens rather than weakens P10's position: the question was only ever WHICH handling, and
the answer "none" is not available.

### 4. Deadness

Peak predicted growth against the observed peak (2.076 /h):

| theta_A | theta_B | theta_B* | theta_P4 |
|---|---|---|---|
| 1.627 (78 %) | **0.163 (7.8 %)** | 1.648 (79 %) | 1.558 (75 %) |

theta_B is a DEAD-MODEL point by the addendum's own criterion (peak below half the observed
peak). A, B* and P4 are not, and all three sit near 75-80 %.

TASK 2 will carry this: every basin gets its peak predicted growth reported beside its
log-likelihood, any basin below 50 % of the observed peak is flagged **DEAD-MODEL** and is not
presented as an alternative explanation of the thermal curve, and every basin centre is re-scored
under (ii') so the reader sees which basins survive a full-strength respiration penalty.

### 5. Scope of what this does and does not touch

P11's twelve smoothness lines and both nested runs were measured on the weighted likelihood. The
**floor and the tie-break are unaffected** by this question: they act on the respiration variance
and on the LP's choice of vertex, neither of which involves the weight. The **sampleability
verdict on the cold lines (15-25 C) is not independent of it** — those are exactly the
temperatures where predicted growth is small and the weight is below 1, so a change to the weight
would change those lines and they would need re-scanning. Not re-scanned here.

### 6. Consequence — recorded, not acted on

The weight discounts rather than bounds. Under section 0c that is a new PI item under 1.15 with
the numbers above beneath it, and the sequence in section 0b gains a step before per-basin
sampling: decide the support handling. **No change is made in P12.**

### 7. Reconciliation against section 0c

This bears on **R1** (the posterior). It **qualifies P11's framing of the seed disagreement as
multimodality**: the disagreement in MEDIANS is now partly explained without invoking two modes at
all, because one of the two medians is a dead point that the weight flatters and that neither run
would have visited as a mode. It does not touch R2 or R4. P11's numbers are not edited; a dated
note is added to P11's report pointing here. Whether two modes exist remains TASK 2's question,
and TASK 1 has already shown there is no barrier between A and B*.
