# Y3 — is the −4 K stability shift biology, or is it having 16 global parameters instead of 2 292?

**Verdict: PARAMETERISATION, by the rule — but the rule's own arms point at a narrower thing than
the question asked, and the narrower thing is the useful result.**

The −4 K `dTm` is **not uniquely required**. An equally good, equally living fit exists at
`dTm` = 0. But the parameter that pays for it is **`tm_scale`**, which stretches the *spread* of
the melting-temperature distribution — not a catalytic parameter. Both solutions buy the **same
low tail of Tm**: about 4–6 °C below the measured meltome at the 1st–5th percentile. So the −4 K
*shift* is an artefact of the global parameterisation, and the *contradiction with the meltome* is
not. **What the fit needs is the least-stable few per cent of enzymes to be less stable in vivo
than in vitro** — a per-enzyme *stability* question, not a per-enzyme *catalysis* one.

That has a direct consequence for the decision this screen exists to inform: **the DLTKcat route
is not the route.** And a committed claim needs correcting — OPEN_ITEMS 1.20 says the
meltome-honouring region of parameter space contains no growing model. It contains one.

The rule was written and committed before any number was computed (`306da82`, DECISIONS.md §D1);
every judgement call since is in `DECISIONS.md`.

---

## 0. What this screens, and what it does not

**R3 only, and only as a screen** (`DECISIONS.md` §D0). Not R1 — no sampler, no posterior, and
P12's basin map is unchanged. Not R2 — no prior is changed and no flat parameter is fixed, though
§4 below is a further non-identification and is recorded as one. Not R4 — nothing out of sample.

**It licenses nothing about the Candida models.** Their Tm is *predicted*, not measured, and A1
measured that predictor's bias at **+5.43 °C**, rising 1.06 °C per °C of predicted Tm (K8 §1). A
predictor bias and an in-vitro/in-vivo gap are different problems with different fixes.

## 1. The decision rule, as fixed before the data

> **PARAMETERISATION** if `dTm` is strongly traded against the catalytic parameters — a partial
> correlation with `dCp_scale`, `kcat_scale` or `dTopt` across the live endpoints above **|0.6|**,
> **AND** a compensating direction exists along which log L changes by less than **2 units** while
> `dTm` moves at least **2 K**.
> **BIOLOGY** if `dTm` is close to orthogonal to all of them — no partial correlation above
> **|0.3|** — and no such compensating direction exists.
> **AMBIGUOUS** otherwise.

with "a compensating direction exists" closed in advance to require the model to **still grow**
there — peak predicted growth ≥ 1.038 h⁻¹, half the observed 2.076.

## 2. TASK 1 — the existing endpoints, and why they cannot carry the verdict

**Live endpoints.** P12 TASK 3 computed peak predicted growth per *basin*, so it was computed here
per *endpoint* with P12's own `common.decompose` (`DECISIONS.md` §D2). Two of twelve fall below
1.038 h⁻¹ and are excluded: **`B(b3)` at 0.0001** and **`worst(b5)` at 0.970**.
**`big(b6,n=2)` peaks at 1.282 and is therefore live by the stated rule and is kept** (§D5), though
its log L is −23.79 and OPEN_ITEMS 1.20 calls it weight-propped. Ten endpoints remain.

**The correlations, over those ten:**

| parameter | Pearson | Spearman | **partial** | partial, dropping `big(b6,n=2)` |
|---|---|---|---|---|
| `dCp_scale` | 0.208 | 0.248 | **+0.661** | +0.299 |
| `kcat_scale` | 0.239 | −0.103 | −0.533 | **−0.964** |
| `dTopt` | 0.278 | −0.212 | **+0.696** | −0.277 |
| `topt_scale` | −0.128 | 0.212 | **+0.663** | −0.084 |
| `tm_scale` | 0.379 | 0.418 | +0.204 | **+0.997** |

**The rule's correlation arm fires** — three partials above |0.6|, two of them among the three the
rule names. **It should not be believed.** Removing one endpoint inverts it. The correlation
matrix's condition number is **233 on n = 10** and **1 188 on n = 9**; the catalytic parameters are
near-collinear among themselves (`dTopt` vs `topt_scale` = −0.986, `dCp_scale` vs `topt_scale` =
−0.962); every raw Pearson correlation is |r| ≤ 0.38 and the Spearman ones change sign between
subsets. These are ten optima chosen by an optimiser, not ten posterior draws: a partial
correlation over them describes the set the optimiser returned, not the geometry of the
likelihood. The rule is not revised; the arm is reported and given no weight (§D4).

**`dTm` against log L:** Pearson **0.921**, Spearman 0.673 — the better optima need *less* shift.
That too is carried by `big(b6,n=2)`: without it, 0.224 and 0.550.

## 3. TASK 2 — the profile, which is decisive

From **p38**, the best converged endpoint (log L −7.186, `dTm` −4.021 K), `dTm` walked to 0 in
eleven steps with `dCp_scale`, `kcat_scale`, `dTopt`, `topt_scale`, `tm_scale` re-optimised at each
step by Powell (300 evaluations, the prompt's figure). Eleven steps rather than twenty-one because
one likelihood evaluation costs 1.87 s measured (§D3).

| `dTm` (K) | log L | log post | peak growth (h⁻¹) | alive | `dCp_scale` | `kcat_scale` | `dTopt` | `topt_scale` | **`tm_scale`** |
|---|---|---|---|---|---|---|---|---|---|
| −4.021 | −7.185 | −16.710 | 1.713 | ✓ | 1.985 | 1.329 | 1.913 | 0.955 | **0.990** |
| −3.619 | −6.954 | −16.556 | 1.741 | ✓ | 1.984 | 1.425 | 2.095 | 0.956 | 1.051 |
| −3.217 | −7.079 | −16.711 | 1.712 | ✓ | 1.985 | 1.328 | 1.909 | 0.955 | 1.096 |
| −2.815 | −6.841 | −16.780 | 1.742 | ✓ | 1.984 | 1.431 | 2.137 | 0.954 | 1.153 |
| −2.413 | −6.867 | −17.081 | 1.742 | ✓ | 1.984 | 1.432 | 2.068 | 0.959 | 1.204 |
| −2.011 | −6.862 | −17.407 | 1.742 | ✓ | 1.990 | 1.432 | 2.033 | 0.959 | 1.250 |
| −1.609 | −6.911 | −17.808 | 1.736 | ✓ | 2.014 | 1.409 | 1.853 | 0.964 | 1.294 |
| −1.206 | −7.028 | −18.380 | 1.739 | ✓ | 2.056 | 1.414 | 1.679 | 0.963 | 1.338 |
| −0.804 | −7.422 | −19.166 | 1.700 | ✓ | 2.255 | 1.265 | 0.498 | 0.960 | 1.361 |
| −0.402 | −7.450 | −19.773 | 1.714 | ✓ | 2.303 | 1.309 | 0.485 | 0.965 | 1.408 |
| **0.000** | **−7.263** | −20.072 | **1.739** | **✓** | 2.135 | 1.406 | 1.388 | 0.961 | **1.467** |

**The profile is flat and the model never dies.** Over the whole 4.02 K, log L stays between
−6.84 and −7.45. **At `dTm` = 0 the cost is 0.077 log L units and peak growth is 1.739 h⁻¹**,
indistinguishable from p38's 1.713. The rule's compensating-direction condition is met from
`dTm` = −2.011 onwards.

Every fit hit the 300-evaluation cap and none converged, so **every log L here is a lower bound
and every cost an upper bound** (§D7) — conservative in the direction that matters: more
evaluations could only flatten the profile further.

## 4. What actually pays for it — and it is not catalysis

`tm_scale` is not a catalytic parameter. It multiplies each enzyme's `(Tm − mean Tm)` about the
distribution mean; it is a property of the **Tm distribution**. Along the profile it is the
parameter that moves most — **0.990 → 1.467, monotonically** — while `kcat_scale` stays 1.33–1.43
and `topt_scale` 0.954–0.965. So the compensation may be the melting-temperature distribution being
*stretched*, not catalysis being retuned (§D6). Four fits separate them:

| | `dTm` | `tm_scale` | log L | peak growth | alive | cost vs A |
|---|---|---|---|---|---|---|
| **A** | −4.021 | free → 0.990 | −7.185 | 1.713 | ✓ | — |
| **B** | **0** | free → **1.467** | −7.263 | 1.739 | ✓ | **+0.079** |
| **C** | **0** | **1.000** | **−17.049** (capped) | 1.618 | ✓ | +9.864 |
| **C′** | **0** | **1.000** | **−14.786** (converged) | **1.659** | **✓** | **+7.600** |
| **D** | −4.021 | **1.000** | −7.032 | 1.742 | ✓ | **−0.153** |

**D is the control and it is decisive:** pinning `tm_scale` to the meltome's own spread while
keeping the shift costs *nothing* — it is very slightly better. `tm_scale` is doing no work at p38.
It becomes load-bearing only when `dTm` is forced to zero. **The compensation is stability-borne,
not catalysis-borne.**

**And the two solutions buy the same thing.** On the model's own 2 560 measured melting
temperatures (mean 55.02 °C, sd 6.13):

| | mean Tm | sd | 1st pct | 5th pct | 10th pct |
|---|---|---|---|---|---|
| the meltome as measured | 55.02 | 6.13 | 42.55 | 45.32 | 47.44 |
| p38: `dTm` −4.02, `tm_scale` 0.990 | 51.00 | 6.07 | **38.67** | **41.40** | 43.50 |
| `dTm` 0, `tm_scale` 1.467 | 55.02 | 8.99 | **36.74** | **40.79** | 43.90 |

Honouring the mean while stretching the spread by 47 % reaches the *same* — in fact a slightly
lower — low tail. **The fit does not need the meltome moved down. It needs the least-stable few
per cent of enzymes several degrees less stable than measured**, and `dTm` and `tm_scale` are two
global ways of buying that.

**Case C was rerun to convergence** (C′: 1 000 evaluations then a restart converging in 167).
**log L −14.786, peak growth 1.659 h⁻¹, alive — a cost of 7.60 units against p38, and a real
optimum rather than a capped pass.**

**And it is boxed into the corner of the prior.** C′ returns `dCp_scale` = **4.0** against a bound
of 4.0 and `topt_scale` = **1.35** against a bound of 1.35, with `dTopt` = −8.66 against p38's
+1.91: two of its four free parameters are pressed against the edge (§D8). So 7.60 units is a
converged upper bound **partly set by the prior** — the meltome-honouring fit is asking for more
thermal curvature and more spread of enzyme optima than the prior allows. Widening those two
priors is a one-line experiment, named as a follow-up and not run: changing a prior is what this
screen was told not to do.

## 5. TASK 3 — the comparison with Li et al., stated precisely

**Their parameterisation.** Tm measured for 266 of 764 enzymes (the yeast meltome) and set to the
population mean 51.9 °C for the rest; Topt predicted for all 764 by Tome v1.0 and carried as
N(Topt, 13.0 °C); ΔCp‡ sampled. Their calibration moved **Topt** (average per-enzyme SD 10.9 →
7.1 °C) and left **Tm** at the meltome (posterior vs experiment r = 0.97, Fig. 2g). Their nine
limit-carrying enzymes had *measured* prior Tm of 40.5–43.8 °C, and Y2 measured what the
calibration did to them: seven of the nine moved **down** (ATP1 −6.30 °C, ERG1 −3.66 °C) against a
proteome whose Tm moved **up** by +1.33 °C on average.

**The structural difference in one paragraph.** They had per-enzyme freedom on both the catalytic
side (2 292 parameters, ~764 of them Topt) and, through the same sampler, on Tm; we have one global
`dTm` and one global `tm_scale` on top of a fixed per-enzyme meltome. With per-enzyme freedom you
can degrade the specific enzymes that limit growth; with global scalars you can only translate the
whole distribution or stretch it about its mean. **Y2's measurement is that Li's calibration used
exactly that freedom in exactly that way** — it left the proteome's Tm alone and pulled down the
handful of enzymes that set the limit.

**What TASK 2's profile implies about that difference — and what it does not.** It implies that our
−4 K is not a fact about *E. coli*: the same fit is available at `dTm` = 0, so the shift is one of
two interchangeable global descriptions and its *value* carries no biological content. It does
**not** imply that per-enzyme catalysis would remove the tension. The tension survives every
catalytic reparameterisation we can apply: with both moments of the meltome held, the four
catalytic parameters cannot recover the fit, and the one that can is a stability parameter. **The
honest reading is that Li's per-enzyme freedom would help on the side where they used it — Tm's low
tail — and not on the catalytic side the expensive route proposes to buy.**

**And the alternative is not excluded.** Yeast and *E. coli* may genuinely differ: the yeast
meltome's low tail already reaches 40–42 °C against a 42 °C lethal point, while *E. coli*'s
1st percentile sits at 42.6 °C against a growth limit near 47 °C. Nothing here separates "our
parameterisation is too coarse" from "*E. coli*'s in-vivo stability really is lower than its
in-vitro meltome". §7 says what would.

## 6. TASK 4 — the costing and the recommendation

In full in `task4_cost.md`. In short:

* **DLTKcat has already been run on this proteome** — 1 149 reactions, 5–55 °C in 11 steps. Fitting
  MMRT to its predictions gives an interior optimum for **36 of 1 149**; 736 rail at 80 °C, 377 at
  0 °C, and only 169 have the negative ΔCp‡ a peak requires. **DLTKcat's kcat(T) is essentially
  monotone over the biological range for these enzymes, so there is no per-enzyme Topt in it to
  extract.** Thirteen enzymes of 2 560 currently pass the quality test and are applied.
* **The thermal layer is already per-enzyme in its data.** `enzyme_cost.py` holds per-enzyme
  `Topt` and `Tm` arrays and applies the global scalars as vectorised transforms of them, and
  `dltkcat.apply_fits_to_provider` already overrides them from a fits csv. Swapping in a better
  per-enzyme table is **~0 half-days of core work**; making the *free parameters* per-enzyme is a
  **6–10 half-day** change in the calibration and sampler, not in the thermal layer.
* **Re-verification, at minimum:** the seven-strain sink-audit gate, P1's 60/60 and 10/10 gate, and
  every committed `resolved_config.yaml`.

**Recommendation: do not start the DLTKcat route.** Its input does not exist (§6, first bullet) and
TASK 2 says the catalytic side is not where the tension is (§4). **Recommended instead, and it is
half a day:** the meltome is per-protein, so name the enzymes that carry this model's thermal
limit and compare their measured Tm against what the fit needs of them. That decides
biology-versus-parameterisation properly rather than screening it. *Not decided here.*

## 7. What this retracts, qualifies, and does not license

**Retracts, in part:** OPEN_ITEMS 1.20 states that "**the meltome-honouring region of parameter
space contains no growing model**". **It contains one.** With `dTm` = 0 and `tm_scale` = 1 both
held and the four catalytic parameters re-optimised to convergence, the model grows at
**1.659 h⁻¹** — comfortably alive — for a log L cost of **7.60 units** against p38, itself partly
set by two prior ceilings (§4). P12's inference was sound for what P12 did: its only `dTm` ≈ 0 point was an *unconstrained*
optimum of the 16-dimensional log posterior, which is a different object from a *constrained*
optimum with `dTm` and `tm_scale` pinned. The claim is corrected by dated note; P12's numbers are
not edited.

**Qualifies:** 1.20's framing that "either the meltome is not the right constraint, or the model
cannot fit these data without contradicting it". A third option is now on the table and is the one
the evidence supports: the model can fit these data while honouring the meltome's *mean*, and what
it cannot do is honour its *low tail*.

**Does not license:**

* any statement about the Candida models (§0);
* "per-enzyme parameters would remove the −4 K" — §4 shows catalysis cannot pay for it;
* "the meltome is compatible with these data" — the fit exists and lives, but 7.60 log L units
  worse and pressed against two prior bounds;
* any conclusion about which of the two global descriptions is *right*. Both contradict the
  measured low tail by 4–6 °C. That is the finding.

**Moves R3 as a screen, and nothing else.** It also records a further non-identification for R2's
list: **`dTm` and `tm_scale` are not jointly identified** — 4 K of one trades against 47 % of the
other for 0.08 log L units.

---

## Verdict

**PARAMETERISATION**, by the rule as written: the correlation arm fires (partials +0.696, +0.663,
+0.661) and the compensating-direction arm fires decisively (4.02 K of `dTm` for 0.077 log L units,
alive throughout).

**And the rule's verdict is narrower than its label.** What is a parameterisation artefact is the
**−4 K number**, not the contradiction with the meltome: the trade is against another *stability*
parameter, and both descriptions put the least-stable few per cent of enzymes 4–6 °C below
measurement. Per-enzyme *catalysis* — the resolution the expensive route would buy — cannot pay
for it. If the question is "is the −4 K a fact about *E. coli*?", the answer is no. If it is "is
the meltome compatible with this model?", this screen does not answer it, and §6 says what would.
