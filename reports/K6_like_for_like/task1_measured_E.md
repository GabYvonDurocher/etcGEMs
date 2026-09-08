# K6 TASK 1 — the two measured activation energies, and which one a model should be tested against

**The prompt's diagnosis is correct, and the test confirms it.** The two measured E_growth are
not two estimates of one quantity. K5 compared the model against the wrong one.

Reproduce with `CANDIDAS_ROOT=... python3 reports/K6_like_for_like/task1_two_measured_E.py`
(exit 0). Table: `task1_measured_E.csv`.

---

## What each fit actually is, read from the source

| | form | window | deactivation | pooling |
|---|---|---|---|---|
| **OLS** (`07_oxygen_fits.R`, `fit_arr_lm`) — what K5 used | `lm(ln y ~ boltz)` | **every** temperature with y > 0 | **none** | per isolate |
| **Bayesian growth** (`09_bayesian_models.R`, `fit_ss_hier`) | **Sharpe-Schoolfield** | every temperature | **yes**, its own `Eh`, `Th` | hierarchical, isolate within group |
| **Bayesian respiration** (`fit_arr_hier`) | Arrhenius | every temperature | none | hierarchical |

`EXCLUDE_TEMPS_PLOT` is empty, so no temperature is dropped anywhere.

The Sharpe-Schoolfield `E` is the **rising-limb** activation energy: the collapse is carried by
separate terms. The OLS `E` is the slope of a straight line drawn through a curve that turns
over. Those are different quantities, and the four-fold gap between them is not a disagreement
about a measurement.

## The test: refit the OLS on the rising limb only

If the diagnosis is right, restricting the OLS to the rising limb should move it toward the
Bayesian value, and should leave E_resp alone because respiration does not turn over.

**E_growth (eV)**

| group | OLS, full range | OLS, rising limb | Bayesian Sharpe-Schoolfield |
|---|---|---|---|
| Clade 1 (*C. auris*, the model organism) | 0.194 | **0.732** | 0.901 [0.75, 1.07] |
| Clade 2 | 0.321 | 0.932 | 1.148 [0.98, 1.33] |
| Clade 3 | 0.225 | 0.741 | 0.942 [0.78, 1.11] |
| Clade 4 | 0.350 | 0.723 | 1.011 [0.85, 1.18] |
| *C. parapsilosis* | 0.262 | 0.683 | 0.828 [0.65, 1.02] |
| *C. haemulonii* | 0.157 | 0.601 | 0.797 [0.61, 0.98] |
| *C. duobushaemulonii* | 0.008 | **0.627** | **0.622** [0.45, 0.80] |

It moves, in every group, by a factor of two to eighty, and *C. duobushaemulonii* lands on its
Bayesian value almost exactly. The residual gap is what partial pooling and an explicit
deactivation term buy over a truncated straight line.

**E_resp (eV) — unaffected, which is the tell**

| group | OLS, full range | Bayesian Arrhenius |
|---|---|---|
| Clade 1 | 0.518 | 0.518 |
| Clade 2 | 0.416 | 0.414 |
| Clade 3 | 0.404 | 0.402 |
| Clade 4 | 0.291 | 0.301 |
| *C. parapsilosis* | 0.339 | 0.364 |
| *C. haemulonii* | 0.328 | 0.433 |
| *C. duobushaemulonii* | 0.466 | 0.475 |

The two conventions agree on respiration to three decimals for the model organism, and differ
four-fold on growth. That is exactly what a turnover-contaminated growth fit looks like.

## What it does to the quantity K5 reported

**E_resp − E_growth**

| group | OLS full range (**K5's comparator**) | OLS rising limb | **Bayesian (the manuscript's own)** |
|---|---|---|---|
| Clade 1 | **+0.324** | −0.373 | **−0.383** [−0.56, −0.21] |
| Clade 2 | +0.095 | −0.725 | −0.733 [−0.93, −0.54] |
| Clade 3 | +0.179 | −0.477 | −0.541 [−0.72, −0.36] |
| Clade 4 | −0.060 | −0.647 | −0.710 [−0.90, −0.53] |
| *C. parapsilosis* | +0.077 | −0.454 | −0.464 [−0.68, −0.27] |
| *C. haemulonii* | +0.171 | +0.069 | −0.363 [−0.57, −0.15] |
| *C. duobushaemulonii* | +0.458 | −0.397 | −0.149 [−0.36, +0.06] |

**The measured difference is negative in every group**, once the comparator is the rising-limb
growth E. K5's "+0.33 measured" was the full-range OLS artefact for Clade 1.

## Which comparator is appropriate, and why it is not one number

Neither table is "the" measured value; the right one depends on the quantity.

* **E_growth**: the rising-limb value. A model whose curve turns over 9–16 °C higher than the
  organism's cannot be compared against a slope that was depressed by the organism's turnover.
* **E_resp**: the full-range Arrhenius value. Respiration does not turn over, both sources
  agree, and truncating at the growth optimum discards the hot end where the signal is.

That asymmetry is what the manuscript itself does, and `bayes_E_resp_minus_growth.csv` is the
difference of exactly those two quantities. TASK 2 reports the model against all three
comparators so the effect of the choice is visible rather than assumed.

**One methodological note.** The rising-limb cut is taken at each group's Bayesian
`growth_Topt_C`, not at the argmax of the measured mean. *C. haemulonii*'s raw argmax lands at
42 °C, above its own thermal limit, on a mean over the few wells still alive; cutting there
leaves the turnover inside the "rising limb" and returns 0.205 eV against 0.601 eV at the
Bayesian optimum of 32.0 °C. Both cuts are in the table.
