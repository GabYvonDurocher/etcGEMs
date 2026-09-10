# Y3 — decisions and judgement calls

Kept from the first judgement call. **§D0 and §D1 were written and committed BEFORE any number
was computed**, per the prompt; the commit that adds them touches nothing else, so the ordering is
checkable in the history rather than asserted here.

---

## D0. What this screens, against §0a

**R3 only — "right for the right reason" — and only as a screen.** Y3 asks whether the −3 to
−4.5 K `dTm` every live endpoint requires is a statement about biology (in-vitro melting
temperature is not in-vivo functional inactivation) or an artefact of resolution (one global
`dTm` where Li *et al.* had 2 292 per-enzyme parameters). That is R3's question: is the mechanism
discriminated, or merely fitted.

It does **not** move:

* **R1 (statistically reliable).** Y3 runs no sampler, produces no posterior, and its TASK 2
  profile is a sequence of optimisations, not draws. The basin structure P12 mapped is unchanged.
* **R2 (identified).** Y3 changes no prior and fixes no flat parameter. If anything it bears on
  R2 obliquely — a strong `dTm`↔catalysis trade would be a further non-identification — but that
  would be a *consequence* to record, not a result Y3 establishes, and it is reported as such.
* **R4 (predictively reliable).** Nothing here is tested out of sample.

It also **does not license any statement about the Candida models**. Their `Tm` is *predicted*,
not measured, and A1 measured that predictor's bias at **+5.43 °C** — a different problem with a
different fix, and one this screen says nothing about.

## D1. The decision rule, fixed before the data

Verbatim from the prompt, with the two thresholds it names, and not revised after seeing anything:

> **PARAMETERISATION** if `dTm` is strongly traded against the catalytic parameters — a partial
> correlation with `dCp_scale`, `kcat_scale` or `dTopt` across the live endpoints above **|0.6|**,
> **AND** a compensating direction exists along which log L changes by less than **2 units** while
> `dTm` moves at least **2 K**.
>
> **BIOLOGY** if `dTm` is close to orthogonal to all of them — no partial correlation above
> **|0.3|** — and no such compensating direction exists.
>
> **AMBIGUOUS** otherwise, which is a legitimate outcome and is reported as such.

Two readings of the rule were possible and the choice is made here, before the data, so it cannot
be made to suit the answer:

* **"A compensating direction exists"** is read as: somewhere on TASK 2's profile of `dTm` with
  the five catalytic parameters re-optimised, there is a step at least 2 K from p38's `dTm` whose
  re-optimised log L is within 2 units of p38's −7.186 **and whose model still grows** — peak
  predicted growth at or above half the observed 2.076 h⁻¹, i.e. **≥ 1.038**. A direction that
  keeps log L only by killing the organism is not a compensating direction; P12's b3 is exactly
  that and it is the reason the growth condition is written in.
* **The correlation arm** is evaluated on the partial correlations, as the rule says, with Pearson
  and Spearman reported beside them. The rule's two arms can disagree; if they do, the verdict is
  AMBIGUOUS and both are reported.

## D2. Which endpoints count as live

The rule needs "the live endpoints", and P12's TASK 3 computed peak predicted growth per **basin**
(at its best endpoint), not per endpoint — so the exclusion cannot be read off a committed file
for the ten remaining points.

**Decision: compute peak predicted growth for each of the twelve endpoints, with P12's own
`common.decompose`, and apply the prompt's threshold (half of the observed 2.076 h⁻¹ = 1.038).**
Twelve twelve-temperature sweeps, a few minutes, and it makes the exclusion evidential rather than
inherited. The numbers and the excluded set are in the report.

---

_Everything below was written after the corresponding computation._

## D3. Eleven profile steps, not twenty-one

One likelihood evaluation costs **1.87 s**, measured (five calls at p38, which also reproduces
P12's committed log L of −7.185975 to 1e-11). Twenty-one steps at the 300-evaluation cap is
therefore up to **3.3 hours of solving**; on eight workers that is ~28 minutes of wall-clock with
eight cores held, against a screen budget of ~15 minutes and P13 owning the primary tree.

**Decision: eleven steps — the prompt's own stated fallback — at the 300-evaluation cap, on eight
workers, and say so.** The grid still lands exactly on p38's dTm and on dTm = 0, which are the two
points the verdict turns on, and the spacing is 0.402 K.

## D4. The correlation arm is uninformative, and the report says so rather than leaning on it

The rule's correlation arm fires: over the ten live endpoints, `dTm`'s partial correlations are
+0.696 (`dTopt`), +0.663 (`topt_scale`), +0.661 (`dCp_scale`) — three above |0.6|.

**It should not be believed, and the reason is in the numbers rather than in a general worry about
small n.** Removing a single endpoint — `big(b6,n=2)`, the one live point with `dTm` = −10.18
against the others' −3.07 to −4.50 — moves those partials to +0.299, −0.084 and −0.277, and moves
`kcat_scale` from −0.533 to −0.964 and `tm_scale` from +0.204 to +0.997. The correlation matrix's
condition number is **233 on n = 10** and **1188 on n = 9**, and the catalytic parameters are
near-collinear among themselves (`dTopt` vs `topt_scale` = −0.986, `dCp_scale` vs `topt_scale` =
−0.962). The raw Pearson correlations are all small (|r| ≤ 0.38) and the Spearman ones change sign
between subsets.

**Decision: report the arm as the rule requires, report the sensitivity beside it, and rest the
verdict on TASK 2.** These are ten optima chosen by an optimiser, not ten posterior draws; a
partial correlation over them estimates the shape of the set the optimiser happened to return, not
the geometry of the likelihood. The prompt anticipated this — "correlation across optima is
suggestive; a direct scan is decisive" — and the sensitivity confirms it empirically. The rule is
not revised; its correlation arm is simply reported as not load-bearing.

## D5. `big(b6,n=2)` is live by the stated rule and is kept

The prompt's exclusion is peak predicted growth below half the observed 2.076 h⁻¹. Computed per
endpoint: `worst(b5)` peaks at **0.970** and is excluded; `B(b3)` at **0.0001** and is excluded;
`big(b6,n=2)` peaks at **1.282** and is therefore **live**, though its log L is −23.79 against
p38's −7.19 and OPEN_ITEMS 1.20 describes it as weight-propped.

**Decision: apply the rule as written and keep it, rather than adding a log-L criterion after
seeing that it is the point driving the correlations.** Adding an exclusion at that moment would
be exactly the revision the prompt forbids. Its influence is instead quantified in D4 and reported.

## D6. `tm_scale` is not catalytic, and the profile forced a follow-up the prompt did not anticipate

TASK 2 holds a **living** model at `dTm` = 0 for **0.077 log L units**, which reads as "catalysis
compensates". But the five parameters the prompt names as catalytic include **`tm_scale`**, and
`tm_scale` is a property of the **Tm distribution**, not of catalysis: it multiplies each enzyme's
`(Tm − mean Tm)` about the distribution mean. Along the profile it is the parameter that moves
most — **0.990 at `dTm` = −4.02 rising monotonically to 1.467 at `dTm` = 0** — while `dCp_scale`
moves 1.98 → 2.14, `kcat_scale` stays 1.33–1.43 and `topt_scale` 0.954–0.965.

A measured meltome fixes **both moments** of Tm. Honouring the mean (`dTm` = 0) while stretching
the spread by 47 % contradicts the measurement just as surely, in a different moment.

**Decision: add `task2b`, four fits separating the two — `dTm` = 0 with `tm_scale` free, `dTm` = 0
with `tm_scale` = 1 (both moments honoured), and the two reference points at p38's `dTm`.** This is
the configuration §0b step 2 was actually asking about, and without it the screen would report
"catalysis can do it" when the profile shows the work being done by a second stability parameter.
The rule is not changed; this sharpens what its profile arm is measuring.

## D7. Every Powell fit hit the 300-evaluation cap

All eleven profile steps and all four follow-up fits report `nfev = 300` and
`success = False` ("Maximum number of function evaluations has been exceeded"). Powell had not
converged at any of them.

**Decision: report the values as LOWER BOUNDS on the achievable log L, and let the direction of
the bias do the arguing.** More evaluations can only raise each step's log L, so a profile that is
already flat would only get flatter — the compensability conclusion is conservative. The converse
would not be true: had the profile collapsed, the cap would have been a candidate explanation and
the fits would have had to be rerun. The cap is the prompt's own figure ("300 evaluations is enough
for five parameters"); it is not, and that is recorded rather than quietly raised.

## D8. The meltome-honouring fit is boxed into the corner of the prior, and that is part of the answer

`task2b` case C (`dTm` = 0, `tm_scale` = 1, four catalytic parameters free) hit the 300-evaluation
cap at log L −17.05, so it was rerun to convergence: **1 000 evaluations, then a restart that
converged in 167 — log L −14.7856, peak growth 1.6592 h⁻¹, ALIVE.** Cost against p38: **7.60 log L
units**, and this one is a real optimum rather than a capped pass.

It sits on **two prior ceilings**: `dCp_scale` = **4.0** against a bound of 4.0, and `topt_scale` =
**1.35** against a bound of 1.35, with `dTopt` = −8.66 against p38's +1.91. Two of its four free
parameters are pressed against the edge of the box.

**Decision: report 7.60 units as a converged UPPER bound that is partly set by the prior, and name
which bounds.** The constrained fit is asking for more thermal curvature and more spread of enzyme
optima than the prior allows, which is a statement about the prior as much as about the data.
Widening `dCp_scale` and `topt_scale` is a one-line experiment; it is named as a follow-up rather
than run, because changing a prior is exactly what this screen was told not to do.

## D9. Total solving time overran the screen's budget, deliberately and once

The prompt budgeted ~15 minutes of solving and ~2 hours overall. TASK 2's profile took 19 minutes
on eight workers, `task2b` 10 minutes on four, and `task2c` 31 minutes on one.

**Decision: spend the extra half-hour on `task2c` only, and say so.** It is the one run that bounds
a **retraction of a committed claim** — OPEN_ITEMS 1.20's "the meltome-honouring region contains no
growing model" — and reporting that retraction on a capped, unconverged fit would have been worse
than reporting it late. P13 was not running at any point (no Python process in the primary tree,
load average 5–12 throughout), so nothing was slowed. Everything else stayed inside the budget.
