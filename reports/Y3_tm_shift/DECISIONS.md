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
