# K6 TASK 2 — the comparison, redone like for like

**Under both valid comparators the sign agrees with measurement in all four species.** K5's
"wrong sign in all four species" was an artefact of the comparator. A **magnitude** gap
survives: the model's E_resp − E_growth is two to two and a half times more negative than
measured, and lies outside the measured 95 % credible interval in all four.

Reproduce with `CANDIDAS_ROOT=... python3 reports/K6_like_for_like/task2_like_for_like.py`
(exit 0). Tables: `task2_panels.csv`, `task2_ratio.csv`, `task2_model_curves.csv`.

---

## The three panels

Every panel fits **both sides with the same functional form** — the measured pipeline's own
`lm(ln y ~ boltz)`. What differs is the window. The repaired model (B5) is shown; `before (B3)`
and the complex III sensitivity are in the table.

### E_resp − E_growth

| species | **(a) rising limb, organism's window** | | **(b) full window (K5's)** | | **(c) manuscript convention** | |
|---|---|---|---|---|---|---|
| | model | measured | model | measured | model | measured [95 % CI] |
| *C. auris* (clade I) | **−0.917** | **−0.347** | −0.329 | **+0.341** | **−0.969** | **−0.383** [−0.56, −0.21] |
| *C. haemulonii* | −1.174 | −0.426 | −0.360 | +0.156 | −1.388 | −0.363 [−0.57, −0.15] |
| *C. duobushaemulonii* | −0.803 | −0.338 | −0.079 | +0.482 | −0.757 | −0.149 [−0.36, +0.06] |
| *C. parapsilosis* | −0.785 | −0.412 | −0.416 | +0.191 | −1.018 | −0.464 [−0.68, −0.27] |
| **sign agrees?** | **yes, 4 / 4** | | **no, 0 / 4** | | **yes, 4 / 4** | |
| **inside the 95 % CI?** | — | | — | | **no, 0 / 4** | |

Panel (b) is the only one in which the sign disagrees, and it is the only one in which the
window contains the organism's collapse but not the model's. The models over-predict the
thermal limit by 9.6 to 15.8 °C (K4, §4), so over 22–44 °C the organism turns over and the model
does not. Fitting a straight line to both depresses the measured E_growth and leaves the model's
alone. That is the whole of K5's discrepancy.

### The components, panel (c), repaired model

| species | model E_growth | measured | model E_resp | measured |
|---|---|---|---|---|
| *C. auris* | 1.200 | 0.901 | **0.231** | **0.518** |
| *C. haemulonii* | 1.759 | 0.797 | 0.371 | 0.433 |
| *C. duobushaemulonii* | 0.934 | 0.622 | 0.177 | 0.475 |
| *C. parapsilosis* | 1.023 | 0.828 | 0.004 | 0.364 |

The surviving gap is not one thing. The model's growth is too steep (1.2–1.8 against 0.6–0.9)
**and** its respiration too shallow (0.00–0.37 against 0.36–0.52), and the two errors add in the
difference. Correcting complex III raises *C. auris*' model E_resp from 0.231 to 0.371 and moves
the difference from −0.969 to −0.879.

## The other two rows K5 reported, restricted to where the organism grows

K5 compared at 44 °C, where three of the four species are dead and *C. auris* is at a fifth of
its peak. Restricting to temperatures at which the organism actually grows, and taking each
species' own upper limit:

| species | cut | level: model | measured | fold | rise to the cut: model | measured |
|---|---|---|---|---|---|---|
| *C. auris* | 40 °C | 2.99 | 0.85 | 3.5× | 1.03 | **1.57** |
| *C. haemulonii* | 40 °C | 3.63 | 0.82 | 4.4× | 0.88 | 1.73 |
| *C. duobushaemulonii* | 38 °C | 2.31 | 0.83 | 2.8× | 1.17 | 7.18 |
| *C. parapsilosis* | 40 °C | 2.55 | 0.60 | 4.3× | 0.57 | 2.69 |

With complex III also corrected the level falls to 1.34, 1.69 and 1.35, i.e. 1.6–2.1× measured
rather than 2.8–4.4×.

**K5 reported the rise as 4.70× measured against 1.20× model.** Within the organism's growing
range it is **1.57× against 1.03×** for *C. auris* — the same direction, a third of the size.
*C. duobushaemulonii*'s 7.18× is not a steady respiration rise but its collapse at 38 °C, where
measured growth falls to 0.209 while respiration is still 0.669.

## Verdict on the sign, panel by panel

* **(a) rising limb, both sides, organism's window** — sign agrees, 4 of 4.
* **(b) full window, both sides** — sign disagrees, 0 of 4. This is K5's panel and it is not a
  valid comparison.
* **(c) manuscript convention against the paper's own Bayesian values** — sign agrees, 4 of 4;
  magnitude outside the credible interval, 4 of 4.
