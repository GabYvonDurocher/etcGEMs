# Y1 PART D — what their Bayesian calibration did to the enzyme thermal parameters

Read from the paper and its supplementary, cited by figure number. Li G. *et al.* (2021)
*Bayesian genome scale modelling identifies thermal determinants of yeast metabolism.* **Nature
Communications 12:190.** No re-analysis of their posterior; the one place where their **deposited
prior** is read directly (`data/model_enzyme_params.csv`) is marked as such in §4.

---

## 1. Where the priors came from — and one correction to the framing of this task

| parameter | prior | uncertainty |
|---|---|---|
| **Tm** | measured, for **266 of 764** enzymes, from the Leuenberger *et al.* yeast meltome; the remaining ~500 assigned the population mean **51.9 °C** | N(Tm_i, **3.4 °C**) measured; N(51.9, **5.9 °C**) assigned |
| **Topt** | **all 764 predicted from sequence** by **Tome v1.0**, an ML method with test-set R² = 0.5 | N(Topt_i, **13.0 °C**), the RMSE implied by that R² |
| **ΔCp‡** | assumed | sampled |

Methods, "Melting temperatures" and "Enzyme optimal temperature".

**The correction.** The task framing says Li used curated per-enzyme parameters rather than a
sequence predictor, so our Seq2Tm finding cannot apply to them. Half of that is right and half is
not. **Tm** is measured or a population mean — no predictor. But **every Topt in the model is a
sequence prediction**, from Tome v1.0, with a stated RMSE of 13.0 °C.

What they did with it is the point, and it is a methodological answer to our own concern rather
than an instance of the problem: the predictor's output was used as a **wide prior**, its RMSE
carried explicitly as the prior standard deviation, and the calibration was then asked to shrink
it. They did not treat a sequence prediction as a measurement. That distinction — predictor as
prior, not as point estimate — is worth stating plainly in any methods paper, and it belongs to
them, not to us.

## 2. What the calibration moved: Topt, not Tm

> "we observed that the approach tended to change the enzyme Topt rather than its Tm and ΔCp‡
> parameters (Fig. 2e)."

* **Topt** — significant *variance* reduction in **59 % (449/764)** of enzymes; significant *mean*
  change in **26 % (200/764)** (Fig. 2e; Šidák-adjusted one-tailed F-test and Welch's t-test,
  p < 0.01).
* A random-forest importance analysis puts the **largest contribution to the improved posterior
  performance on Topt**, of the three parameter categories (Fig. 2f).
* Average parameter standard deviation, prior → posterior (Supplementary Fig. 7):
  **Topt 10.9 → 7.1 °C**, **Tm 4.9 → 4.0 °C**, **ΔCp‡ 2.0 → 1.8 kJ/mol/K**. Topt shrank most; Tm
  barely moved.

## 3. Did the posterior pull stability DOWN? No.

This is the question PART D exists to answer, and the answer is clean.

> "the parity plot comparing the Tm in the Posterior models and experimental values used in the
> Prior showed that the Posterior mean values were strongly correlated with the experimental ones
> (Pearson's r = 0.97, p value < 1e−32) (Fig. 2g). This indicated that the parameter values
> returned by the SMC-ABC approach ... were not very different from the experimentally measured
> values."

By contrast the posterior Topt correlates only weakly with the fourteen BRENDA measurements that
could be mapped (**r = 0.49, p = 0.075**, Fig. 2h) — the calibration moved Topt away from its
prior and left Tm where the meltome put it.

The paper reports **counts and correlation, not a signed shift**, so the direction of the small Tm
movement is not stated and is not inferred here.

## 4. The nine unstable enzymes were unstable in the PRIOR, not made so by the calibration

The paper's mechanism at the growth limit rests on a short list:

> "in the Posterior etcGEMs, only 9 enzymes (1%) with a mean melting temperature below 42 °C were
> present (ERG1, ATP1, ALA1, KRS1, SER1, HEM1, PDB1, ADH1, and TRP3) (Supplementary Fig. 8), of
> which three (ATP1, HEM1, and PDB1) are located in the mitochondria."

Their deposited prior (`data/model_enzyme_params.csv`, read directly — this is the one place this
section touches data rather than text):

| gene | UniProt | **prior** Tm (°C) | source | prior Topt (°C) |
|---|---|---|---|---|
| ERG1 | P32476 | **40.46** | measured | 34.00 |
| ADH1 | P00330 | 41.32 | measured | 41.00 |
| TRP3 | P00937 | 41.60 | measured | 33.00 |
| PDB1 | P32473 | 42.09 | measured | 35.00 |
| SER1 | P33330 | 42.42 | measured | 35.00 |
| KRS1 | P15180 | 42.49 | measured | 35.00 |
| ALA1 | P40825 | 42.69 | measured | 35.00 |
| HEM1 | P09950 | 43.15 | measured | 34.00 |
| ATP1 | P07251 | 43.80 | measured | 32.00 |

**Every one of the nine has a MEASURED prior Tm, and every one is already at or within 2 °C of
42 °C before any calibration.** ERG1 — the headline enzyme — has the second-lowest measured
melting temperature in the whole model.

Across the 764: prior Tm mean **51.36 °C**, minimum **40.22 °C**, and **7 enzymes** already below
42 °C in the prior against **9** in the posterior. The calibration moved two enzymes across that
line. It did not manufacture instability; it inherited it.

## 5. Against our own result

E. coli, in this project, needed **ΔTm = −5.6 K applied to a measured meltome** to bring CT_max
onto the observed thermal limit. Li *et al.* faced the same tension and did not resolve it that
way. They state it explicitly:

> "recent high throughput measurements of melting temperatures (Tm) for 707 S. cerevisiae proteins
> revealed a Tm distribution with a mean value of 52 °C and a minimum of 40 °C, which suggests
> that protein denaturation alone might not be sufficient to explain the decline of yeast cell
> growth between 30 °C (OGT) and 42 °C (lethal temperature point)."

and

> "experimentally measured enzyme melting temperatures (Tm) are on average 20 °C higher than
> enzyme Topts collected from BRENDA (Fig. 3b), protein denaturation alone seems to be
> insufficient to explain the thermal mechanism underlying enzyme Topts."

**So the mismatch is common to both studies: measured melting temperatures are too high to account
for where growth actually stops.** The two resolved it differently.

* **Ours:** move stability down — ΔTm = −5.6 K on the measured meltome — so denaturation reaches
  the growth limit.
* **Theirs:** leave stability at the measured values (Fig. 2g, r = 0.97) and put the decline on
  **kcat degeneration** instead, through MMRT's negative ΔCp‡ (Fig. 3c, 3e, 3f), with the *final*
  termination at 42 °C still carried by the handful of genuinely low-Tm enzymes (Fig. 3a, 3d;
  Supplementary Fig. 8).

**This is the answer PART D was after, and it is not the one that would have been most convenient.
Their calibration did NOT pull stability down substantially, so it is not independent support for
a common over-prediction of stability.** What it *is* independent support for is the underlying
tension — that a measured meltome sits too high to explain an organism's thermal limit on its own
— and for the fact that a calibration will resolve that tension through whichever term the
formulation leaves free. Ours left stability free; theirs put the weight on catalysis. Neither
result adjudicates which is right.

## 6. The headline, and what none of this touches

ERG1 (squalene epoxidase) has the highest median flux-sensitivity coefficient of any enzyme at
40 °C by an order of magnitude (Fig. 5a); removing its temperature constraint raises simulated
growth from 0.09 to 0.14 h⁻¹ (Fig. 5b); and replacing ScERG1 with the *K. marxianus* orthologue
gave significantly better growth after two passages at 40 °C (Fig. 5c). Of the 24 enzymes
predicted by more than 10 % of posterior models to be growth-limiting at 42 °C, three are in
sterol biosynthesis — ERG1, HMG1, HMG2 (Fig. 5d, e).

Nothing in Y1 bears on that result. It rests on flux control and on an experimental validation,
not on the coupling circuit PART B audited, and PART B found that circuit sound in any case.
