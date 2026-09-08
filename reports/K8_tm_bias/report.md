# K8 — is the Candida ceiling over-prediction a Seq2Tm artefact?

_2026-09-08. Branched from `main` at **028e908**, the K7 merge. **P4 had not landed**, so
*E. coli* is read from committed outputs and never re-run. **No default is changed.**_

**Partly. And the part that is left over is the interesting one.**

At exactly the bias A1 measured — nobody tuned it — the ceiling gaps close by a third to a half,
the fit improves in all four species, and the rising limb does not move at all. But full closure
needs 1.8 to 2.8 times that bias, and the amount each species needs differs by 5 °C, which no
uniform predictor bias can produce.

Reproduce with:

```bash
python3 reports/K8_tm_bias/task1_premise.py
CANDIDAS_ROOT=... python3 reports/K8_tm_bias/task2_apply_correction.py
CANDIDAS_ROOT=... python3 reports/K8_tm_bias/task3_offset_sweep.py
etcgem transfer --experiment candida_B5_tm_bias_corrected     # the correction, through the CLI
```

---

## 1. The premise, checked before anything was applied

**The bias is not uniform.** A1's +5.43 °C is a mean over a bias that rises **1.06 °C per °C of
predicted Tm** — from +2.44 °C in the lowest predicted octile to **+12.78 °C** in the highest.
The cause is A1's own headline: measured Tm barely responds to the prediction (slope −0.061), so
almost all of the predicted spread is error and the error grows with the prediction.

A flat offset therefore corrects the **location** of the Tm distribution and not its **shape**.
Both corrections were run.

**The ceiling tracks the upper quartile** of the Tm distribution (r = +0.939) rather than the
median (r = +0.824), though over a 0.7–1.4 °C range on four species that is indicative only.

**More important, and easy to miss:** the model's CT_max spans just **1.6 °C** across the four
species while the **observed** limits span **6 °C**. The variation in the gap is almost entirely
observational, so **no uniform correction can differentially fix the gaps** — only their average.

**The prediction, recorded in `DECISIONS.md` D4 before the sweep ran:** dCT_max/dTm ≈ 1.0, so a
−5.43 °C correction should move CT_max by about −5.4 °C. Damping possible; amplification would
falsify the mechanism.

## 2. What happened

| species | CT_max before | after −5.43 | shift | dCT_max/dTm |
|---|---|---|---|---|
| *C. auris* | 53.03 | 48.23 | −4.80 | 0.88 |
| *C. haemulonii* | 51.83 | 47.47 | −4.36 | 0.80 |
| *C. duobushaemulonii* | 51.67 | 47.59 | −4.08 | 0.75 |
| *C. parapsilosis* | 53.29 | 48.17 | −5.12 | 0.94 |

**Confirmed, and damped as the prediction allowed.**

**The mechanism claim holds exactly.** E_growth is unchanged to four significant figures in all
four species (1.200 → 1.200, 1.759 → 1.759, 0.934 → 0.934, 1.023 → 1.023) and T_opt does not move
at all. K7 showed the curvature prior cannot address the ceiling without worsening the rising
limb; **a Tm offset is the orthogonal lever that requirement calls for.**

| species | gap before | gap after | vs *E. coli*'s +5.9 |
|---|---|---|---|
| *C. auris* | +9.0 | **+4.2** | below |
| *C. haemulonii* | +13.8 | +9.5 | above |
| *C. duobushaemulonii* | +13.7 | +9.6 | above |
| *C. parapsilosis* | +15.3 | +10.2 | above |

**The correction A1's data actually supports**, `Tm = 52.60 − 0.061 × Tm_pred`, collapses the
Tm spread from sd 2.2–2.9 °C to **0.14–0.18 °C** and **improves the fit more than the flat offset
in every species** — *C. auris* R² 0.518 → **0.687**, *C. haemulonii* −1.270 → **−0.515** — while
also moving E_growth toward measurement (1.200 → 0.661). **The model's per-enzyme Tm spread is
carrying error rather than signal**, which is A1's finding arriving in the model's behaviour.

## 3. Is 5.43 special?

| species | offset that closes the gap | distance from 5.43 | offset that maximises fit |
|---|---|---|---|
| *C. auris* | **10.0 °C** | 4.6 | 8.0 (R² 0.753) |
| *C. haemulonii* | **15.0 °C** | 9.6 | 15.0 (R² 0.451) |
| *C. duobushaemulonii* | **15.0 °C** | 9.6 | 15.0 (R² 0.947) |
| *C. parapsilosis* | **15.0 °C** | 9.6 | 15.0 (R² 0.920) |

**Three statements, all true, and not summarised into one:**

1. At exactly the measured 5.43 °C the gaps close **32–53 %**, the fit improves in all four, and
   the rising limb does not move. That is a real predictor component found at a value nobody
   tuned.
2. Full closure needs **1.8 to 2.8 times** the measured bias. The predictor bias is **not the
   whole explanation**.
3. The species need offsets differing by **5 °C**, and a predictor bias is a property of the
   predictor, common to all four by construction. **No uniform predictor correction can produce a
   species-specific residual**, so what remains after the measured bias is removed is precisely
   the interspecies divergence this project exists to explain.

E_growth is flat across the whole sweep to 15 °C (1.200 → 1.180), confirming the lever stays
orthogonal throughout; only at 20 °C does the model break down.

## 4. The cross-organism check

**The strongest evidence was already committed.** `ceiling_table_B4.csv` records that
*E. coli*'s Bayesian calibration **pulls Tm down by 5.6 K**, taking its gap from **+5.875 to
−0.012 °C**. *E. coli*'s Tm are a **measured meltome**, so that 5.6 K cannot be predictor bias.

**So the ceiling has at least two components**, and the arithmetic works:

| component | size | where it appears |
|---|---|---|
| common, present even with measured Tm | ≈ **5.6 K** | *E. coli* and Candida |
| predictor, Seq2Tm's measured bias | ≈ **5.4 K** | Candida only |
| **sum** | **≈ 11 K** | against *C. auris*' required 10 °C |

That leaves about 4 °C unexplained for the three relatives — the species-specific residual of §3.

**The methanogen and phototroph support this only weakly, and the caveats matter.** Both draw Tm
from a **mesophile prior**, `N(55.6, 7.59)` — the *E. coli* meltome mean and spread — **not** from
Seq2Tm, and their gaps are −0.2 and +1.7 °C. Consistent with the hypothesis, but: their median Tm
(55.9, 56.9) are **higher** than Candida's, so the gap is a difference of two quantities that both
differ; **the methanogen runs at a calibrated `kcat_scale` of 7.223**, so a gap may have been
absorbed there; and a generic prior does not test a Tm distribution the way an organism-specific
predictor does.

## 5. What this licenses

**Licensed.**

* A predictor component in the Candida ceiling is real, is about 5 K, and shows up at the
  independently measured value without tuning.
* A Tm offset moves the ceiling without touching the rising limb — the orthogonal lever K7's
  result requires, and the curvature prior is not it.
* The ceiling has **at least two causes**: E. coli's measured-Tm gap of 5.9 K cannot be predictor
  bias.
* Applying A1's measured *relationship* rather than its mean improves the fit in all four species
  and moves both failures toward measurement, which says the per-enzyme Tm spread is error.

**Not licensed.**

* That the ceiling is "explained". At the measured bias, a third to a half closes; the rest does
  not, and the remainder is species-specific in a way no predictor bias can be.
* Adopting any offset. −5.43 is a test with a stated prediction; 10 and 15 are the values that
  happen to close the gap and are **not** the hypothesis. Nothing is adopted and no default moves.
* Reading the relatives' excellent fit at a 15 °C offset (R² up to 0.947) as support. That is
  nearly three times the measured bias and is a fit, not a test.

## Verification

| check | result |
|---|---|
| K1 gate, `$CANDIDAS_ROOT` unset | **79/79 PASS, exit 0** |
| `stamp_reports.py --check` | exit 0 |
| all three K8 scripts re-run | exit 0, tables regenerate |
| defaults changed | **none** |
| `strains/eciML1515/`, `reports/ecoli_*` | untouched; P4 had not landed |
