# K8 — decisions

Standing rules carry over. `$CANDIDAS_ROOT` is READ ONLY. Branched from `main` at **028e908**,
the K7 merge. **P4 had not landed** (D1), so `strains/eciML1515/` and `reports/ecoli_*` are read
only, never written. **No default is changed anywhere in K8.**

_Opened at the first judgement call._

---

## D0 — TASK 0: the K7 merge verified

PR #10 merged as `028e908`, branch deleted local and remote. Exit codes checked explicitly:

| check | result |
|---|---|
| Candida gate, `$CANDIDAS_ROOT` unset | **79/79 PASS, exit 0** |
| `stamp_reports.py --check` | **exit 0** |
| `transfer_candida`, `candida_B3_ngamT`, `candida_B5_respire` re-run | exit 0, no numerical output changed |
| working tree | clean |

## D1 — P4 had NOT landed

`p4/refit` at `51327b1`, **five** commits ahead of `main`, unmerged, writing under
`strains/eciML1515/outputs/` within the previous ninety minutes. *E. coli* is therefore read
from committed outputs only (TASK 4), never re-run.

## D2 — the bias is NOT uniform, so the prompt's flat offset is tested alongside the correct one

**Where:** TASK 1, check 1. **This is the first judgement call and it changes what TASK 2 does.**

A1's +5.43 °C is a mean over a bias that is strongly dependent on the predicted value. Regressing
on A1's own 1947 paired points:

    bias = -52.60 + 1.061 x predicted Tm

The bias rises **1.06 °C per °C of predicted Tm**, from +2.44 °C in the lowest predicted octile
to **+12.78 °C** in the highest — a five-fold range. The reason is A1's own headline: the
measured value barely moves with the prediction (slope −0.061), so almost all of the predicted
spread is error, and the error therefore grows with the prediction.

**A flat offset is consequently the wrong correction in principle.** The correction A1's data
actually supports is the regression itself,

    Tm_corrected = 52.60 - 0.061 x Tm_predicted

which not only lowers the mean by about 4.4 °C but **collapses the between-enzyme spread almost
to a constant** — and that spread is the only channel through which this model gives enzymes
different thermal fates.

**Decided:** test both, and report them side by side.
* **(a) the flat −5.43 °C offset** — what the hypothesis literally proposes, kept because the
  prompt asks for it and because it isolates the *location* of the Tm distribution from its
  *shape*;
* **(b) the regression correction** — what A1's data supports, which changes location and shape
  together.
If (a) fixes the ceiling and (b) destroys the model, that is a statement about how much the
model depends on Tm spread, and it is worth having.

## D3 — the ceiling tracks the upper quartile, not the median, but the evidence is weak and the gap spread is observational

**Where:** TASK 1, check 2.

Ilgaz's claim is that the limit tracks median enzyme Tm. In our code, across the four Candida
strains, CT_max correlates best with the **q75** of the Tm distribution (r = +0.939) rather than
the median (r = +0.824). With four species over a quantile range of 0.7–1.4 °C, that ordering is
indicative and not decisive, and it is reported as such.

**The more important observation is one the correlation obscures.** The model's CT_max spans only
**51.67–53.29 °C** across the four species — 1.6 °C — while the observed limits span **38–44 °C**,
6 °C. So the *variation in the gap* between species is almost entirely a variation in the
**observed** limits, not in the model. **A uniform Tm correction shifts all four CT_max by the
same amount and therefore cannot differentially fix the gaps**; it can only move their average.

**Decided:** report the average gap and the spread of gaps separately, and state at the outset
that no uniform correction can address the second.

## D4 — the expected shift, recorded BEFORE the sweep was run

**Where:** TASK 1, check 3. Committed in this file before TASK 2 executed.

The unfolding form sets the falling limb through each enzyme's own Tm: the native fraction
collapses above Tm, and a uniform shift of every Tm translates that collapse along the
temperature axis without changing its shape.

> **PREDICTION: dCT_max / dTm ≈ 1.0.** A −5.43 °C correction should move CT_max by about
> −5.4 °C, taking the Candida gaps from +9.0 … +15.4 °C to about **+3.6 … +10.0 °C**.
> Damping is possible — if the proteome pool or maintenance binds before unfolding does, the
> shift will be **less** than one-for-one. **Amplification is not expected** and would falsify
> this reading of the mechanism.

## D5 — the sweep's verdict is PARTIAL and is reported as three separate statements

**Where:** TASK 3.

The result does not fall cleanly into either branch the prompt anticipated, and forcing it into
one would misreport it. Three things are true at once:

* At **exactly** A1's independently measured 5.43 °C the gaps close by **32–53 %**, the fit
  improves in all four species, and the rising limb does not move at all. That is a real
  predictor component, found at a value nobody tuned.
* Full closure needs **10 °C** (*C. auris*) and **15 °C** (all three relatives) — 1.8× to 2.8×
  the measured bias. So the predictor bias is **not the whole explanation**.
* The offsets the four species need differ by **5 °C**, and a predictor bias is a property of the
  predictor, common to all four by construction. **No uniform predictor correction can produce a
  species-specific residual**, so what is left over after the measured bias is removed is exactly
  the interspecies divergence this project exists to explain.

**Decided:** report all three, in that order, and do not summarise them into a verdict word.

## D6 — E. coli's own tuned row is the strongest cross-organism evidence, and it was already committed

**Where:** TASK 4.

`reports/candida_thermal_limit/ceiling_table_B4.csv` records that *E. coli*'s Bayesian
calibration **pulls Tm down by 5.6 K** and that this takes its ceiling gap from **+5.875 to
−0.012 °C**. *E. coli*'s Tm are a **measured meltome**, so that 5.6 K cannot be predictor bias.

Set beside A1's +5.43 °C predictor bias, the arithmetic of a two-component ceiling works:
a common ≈5.6 K term that appears even with measured Tm, plus a ≈5.4 K predictor term that
appears only where Seq2Tm is used, sums to ≈11 K — which is close to the 10 °C *C. auris*
needs and about 4 °C short of the 15 °C the relatives need.

**Decided:** treat this as the central cross-organism result rather than the methanogen and
phototroph rows, which are weaker evidence for the reason in D7.

## D7 — the methanogen and phototroph support the hypothesis only weakly, and the caveats are stated

**Where:** TASK 4.

Both draw Tm from a **mesophile prior**, `N(55.6, 7.59)`, which is the *E. coli* meltome mean and
spread — **not** from Seq2Tm (`strains/syn6803/thermal/gen_thermal_params.py`, and the same route
for the methanogen). Their gaps are −0.2 and +1.7 °C.

That is consistent with the hypothesis — no predictor, no predictor-driven excess — but it is
weak evidence, for three reasons, all recorded rather than glossed:

1. Their median Tm (55.9, 56.9 °C) are **higher** than Candida's (53.5–54.2), so if the ceiling
   tracked Tm alone they should sit higher, not closer. Their observed limits are also higher
   (47, 44 °C). The gap is a difference of two quantities and both differ.
2. **The methanogen runs at a calibrated `kcat_scale` of 7.223**, so its analyses are not at an
   a-priori operating point and a gap may have been absorbed there. The prompt flags this and it
   is correct to.
3. A generic prior is not an organism-specific estimate, so neither strain tests a Tm
   *distribution* in the way the Candida strains do.
