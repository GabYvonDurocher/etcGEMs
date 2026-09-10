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
