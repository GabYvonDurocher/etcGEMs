# K5 TASK 3 — does the repaired model respire like the organism?

**The repair fixes the level and not the temperature dependence.** Respiration per unit growth
goes from eight to twelve times too low to within about 30 % of measurement once both
reconstruction defects are corrected. The rise in respiration relative to growth at high
temperature — the decoupling the *Candida* work established from data — is still almost
entirely absent: measured 4.7-fold from 30 to 44 °C, model 1.2-fold.

This comparison has never been made before. The models have been tested against measured
growth throughout; the measured O₂ assay had never been put beside what they predict.

Reproduce with `CANDIDAS_ROOT=... python3 reports/K5_respire/task3_respiration_test.py`
(exit 0). Tables: `task3_curves.csv`, `task3_activation_energies.csv`, `task3_ratio.csv`,
`task3_absolute_labelled.csv`.

---

## Why every comparison here is scale-free

Absolute per-cell O₂ depends on the cell-mass conversion, and that conversion is unreliable:
the derived tables carry 8 µm³ / 1320 fg typed as constants while the pipeline's own
`config.R` logs 21.21 µm³ / 2120.58 fg, about six-fold apart (`OPEN_ITEMS` 1.9). So the
conclusions rest on ratios, slopes and peak positions, in all of which that factor cancels.
Absolute per-cell respiration is in `task3_absolute_labelled.csv`, labelled, and nothing is
concluded from it.

Measured comparators are *C. auris* clade I isolates for the clade I model, and the matching
isolates for each relative.

## 1. Respiration-to-growth ratio

**Before the repair there is no decoupling at all.** The model's qO₂/µ is constant to four
significant figures across the whole assayed range — 3.879 at 22 °C, 3.903 at 44 °C. Respiration
was not a separate process: the O₂ the model consumed was biosynthetic demand, chiefly sterol
synthesis, so it scaled with growth exactly. The measured ratio over the same range varies by a
factor of 7.8.

**Level**, averaged over 28–40 °C. The model's qO₂/µ is converted with a nominal biomass carbon
content of 37.5 mmol C/gDW, which is 45 % carbon by dry mass; that constant is the one thing
here that is not scale-free, and it is stated rather than fitted.

| species | measured | before | after (B5) | B5 + complex III |
|---|---|---|---|---|
| *C. auris* | 0.85 | 0.10 (**0.12×**) | 2.01 (2.35×) | 1.10 (**1.28×**) |
| *C. haemulonii* | 1.33 | 0.10 (0.08×) | 2.50 (1.88×) | 1.19 (**0.89×**) |
| *C. duobushaemulonii* | 1.05 | 0.10 (0.10×) | 1.85 (1.76×) | 1.23 (**1.18×**) |
| *C. parapsilosis* | 0.66 | 1.92 (2.91×) | 1.92 (2.91×) | — |

With both reconstruction defects corrected the three *Candidozyma* land within 0.9–1.3× of the
measured respiration-to-growth ratio, from 8–12× too low. *C. parapsilosis*, which needed no
repair, over-respires by 2.9× and is unchanged.

**Temperature dependence**, the ratio at 44 °C divided by the ratio at 30 °C, *C. auris*:

| | ratio(44 °C) / ratio(30 °C) |
|---|---|
| measured | **4.70×** |
| before (B3) | 1.01× |
| after (B5) | 1.20× |
| B5 + complex III | 0.90× |

The repair turns a flat ratio into a shallow U with its minimum near 34 °C, which is the right
shape and in the right place — the measured minimum is at 28 °C. The size of the hot-end rise
is wrong by about a factor of four.

## 2. Activation energies

Fitted the same way on both sides: ln(rate) against 1/kT over the twelve assayed temperatures,
which is how the measured coefficients were produced.

| species | | measured | before (B3) | after (B5) | B5 + complex III |
|---|---|---|---|---|---|
| *C. auris* | E_resp | 0.518 | 0.665 | 0.231 | 0.371 |
| | E_growth | 0.193 | 0.662 | 0.560 | 0.603 |
| | **E_resp − E_growth** | **+0.325** | +0.003 | **−0.329** | −0.233 |
| *C. haemulonii* | **E_resp − E_growth** | **+0.483** | +0.003 | −0.360 | −0.398 |
| *C. duobushaemulonii* | **E_resp − E_growth** | **+0.463** | −0.000 | −0.079 | −0.062 |
| *C. parapsilosis* | **E_resp − E_growth** | **+0.080** | −0.416 | −0.416 | — |

**The sign is wrong, and that is the sharpest failure here.** In every species the organism's
respiration rises faster with temperature than its growth. In the repaired model growth rises
faster than respiration. Correcting complex III as well does not change the sign.

Before the repair, E_resp and E_growth are *identical* to three decimal places in all three
*Candidozyma* — the arithmetic signature of respiration being slaved to growth.

## 3. Shape: where the two curves peak

| species | measured growth / respiration | before | after (B5) |
|---|---|---|---|
| *C. auris* | 34 / **44 °C** | 38 / 38 °C | 36 / **40 °C** |
| *C. haemulonii* | 42 / 44 °C | 40 / 40 °C | 38 / **42 °C** |
| *C. duobushaemulonii* | 32 / 38 °C | 36 / 36 °C | 34 / **42 °C** |

**This is where the repair succeeds qualitatively.** Before, growth and respiration peaked at
exactly the same temperature in all three models, because they were the same quantity up to a
constant. After, respiration peaks 4–8 °C above growth, and the organism's peaks 6–10 °C above.
Respiration continuing to rise while growth turns over is now something these models can
express, and it was not before.

## The verdict, stated plainly

**No, the repaired model does not respire like the organism** — but it fails in a much more
informative way than before.

* What the repair achieves: respiration becomes a **separate process** from growth. The
  decoupling has the right shape, the right sign in the peak positions, and, once complex III
  is corrected too, close to the right magnitude.
* What it does not achieve: the **temperature dependence** of the decoupling. The organism
  raises its respiration relative to growth 4.7-fold between 30 and 44 °C; the model raises it
  1.2-fold. The activation-energy difference has the wrong sign in all four species.

Nothing was tuned to fit. The complex III correction is a labelled sensitivity and is not
adopted; it is reported because it moves the level from 1.8–2.4× to 0.9–1.3× and so identifies
which of the two reconstruction defects the level error was coming from.

**What this points at.** The measured phenomenon is a cell that spends progressively more
carbon on respiration per unit growth as it heats up, which is what maintenance, futile
cycling, proton leak or protein turnover would each produce. The model has one of those,
NGAM(T), and it is evidently far too weak to generate a 4.7-fold swing. That is a statement
about the maintenance layer, not about the ETC, and it is the obvious next thing to test.
