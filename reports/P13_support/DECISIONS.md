# P13 — decisions, from the first judgement call

## D0 — what this run moves under §0a, and what it must not claim

**Moves R1 only** — *statistically reliable: a posterior two independent runs agree on.* P13
changes how the respiration term scores a model that does not grow, then runs two nested samplers
at nlive 800 with different seeds. Both halves are about getting a posterior that reproduces.

**Does NOT move:**

- **R2 (identified).** Five parameters are flat because the data do not constrain them
  (P11 TASK 3; P12 found `f_metab` pinned at 0.28000 and `f_maint` at ~0.35 from every one of
  twelve starting points). Nothing in a support rule changes what the data say. TASK 5 reports
  whether the posterior still calls them flat, which is a *measurement of R2*, not progress on it.
- **R3 (right for the right reason).** P13 reports `dTm`'s credible interval because item 1.20
  turns on it, and the prompt is explicit: **report it, do not interpret it.** Discriminating the
  mechanism needs per-enzyme data, not a better posterior.
- **R4 (predictive).** Nothing is held out here.

**A caveat entered in advance, because the temptation will be to widen the claim.** If the two runs
AGREE, that establishes the posterior is *reproducible*, not that it is *right*. R2's five flat
parameters and R3's unexplained 3–4.5 K `dTm` shift are untouched by it, and a reproducible
posterior over a model that needs a 4 K shift against a measured meltome is still a model with a
problem. If findings later suggest this run moved more than R1, that will be stated explicitly
rather than absorbed.

## D1 — the death threshold is read from the code; the epsilon does not exist and is chosen here

The prompt asks for the death threshold from the existing support handling rather than invented.
It is:

```python
_MASK_G = 1e-4          # growth below this is "dead"; respiration there is not scored
...
keep = (g >= _MASK_G) & (o2 > 0)
```
`src/etcgem/calibration_multi.py:144,282`. **Death threshold = 1e-4 /h**, used unchanged.

**The epsilon is a different matter and the prompt's premise does not hold.** It speaks of
"the existing ε" and of flooring O₂ "exactly as the 1.42 floor already handles small values". Two
corrections, from reading the code:

1. **The 1.42 floor is not on O₂.** It is a floor on the *standard deviation of log O₂*, added in
   quadrature (`varr = rel**2 + dr**2 + floor**2`, `:293`). It widens the error bar; it never
   touches the predicted value. So it is not a precedent for flooring O₂ itself.
2. **No epsilon on O₂ exists anywhere in the likelihood.** The only `1e-9` values in
   `gasflux.py`/`calibration_multi.py` are solver tolerances (`tiebreak_tol`, `growth_tol`) and one
   guard in the RQ helper (`gasflux.py:167`, `np.abs(o2) > 1e-9 → NaN`), which is a different
   quantity in a different function and is not consumed by the likelihood.

So an epsilon has to be **chosen**, and because the imputed penalty scales with `log(ε)` the choice
is not cosmetic — it sets how large "large and finite" is. Chosen: **ε = 1e-9 mmol/gDW/h**, the
same numerical-zero scale `gasflux.py:167` already uses for O₂, so the constant is at least the
module's own and not a new invention. **Its sensitivity is reported in TASK 1 rather than
asserted**, at ε = 1e-6, 1e-9 and 1e-12, so the reader can see how much of any live–dead gap is the
epsilon rather than the evidence.

## D2 — a structural doubt about scheme (i), recorded BEFORE it is tested

The prompt's argument for imputation is that "**O₂ falls to zero continuously as growth does, so
there is no step for a cliff to form on**". **The committed P12 data appear to contradict that**, and
it is recorded here before the test so the test cannot be read as fitting the conclusion.

From P12's per-temperature decomposition at θ_A (`reports/P12_modes/`, TASK 0):

| T (°C) | predicted growth | O₂ uptake |
|---|---|---|
| 15 | 0.00000 | **NaN** (LP infeasible) |
| 50 | **0.00086** | **8.17** |

At 50 °C the model grows at 0.00086 /h — a factor of 8.6 above the death threshold, and
effectively zero against a measured peak of 2.076 — while consuming **8.17 mmol O₂/gDW/h**. That is
not a defect; it is **maintenance respiration**: ATP demand (NGAM) does not vanish when growth
does, so O₂ uptake does not either. Growth and O₂ decouple exactly in the region the support rule
governs.

If that holds generally, then imputing O₂ := ε at the threshold replaces a value of order 8 with a
value of order 1e-9 — a step of ~23 in log O₂, which at `varr ≈ 1.42²` is an enormous jump in the
respiration term. **Imputation would then be the hard mask again, wearing different clothes**, and
the prompt anticipates exactly this outcome: *"If imputation introduces a step above 1
log-likelihood unit, it is a mask in disguise; say so and prefer (ii)."*

This is a prediction, not a verdict. TASK 1's continuity scan measures it.
