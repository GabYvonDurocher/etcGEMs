# Q1 — Is the N₀ / cell-carbon conversion imprinting itself on the respiration data?

**Verdict: no, and the reason is more specific than the all-clear.** The quantity the respiration
likelihood compares against does not contain `cell_carbon_fg` at all, so the 350-vs-2120.58 fg
discrepancy cannot reach it. What that quantity *does* contain is `N₀`, and `N₀` enters as an exact
multiplicative constant — a uniform error, fully absorbable by the fitted `resp_scale`, with no
effect on temperature dependence. The empirical test for the one mechanism that *could* have
distorted the temperature axis — a growth-rate-dependent cell size — finds nothing, in a comparison
that was powered to see a literature-magnitude effect at 3–5× the residual scatter.

**One thing does move materially: CUE.** It is not linear in the conversion constant, so its shape
moves and not just its level. The deck's CUE slide needs a caveat.

Arithmetic on committed tables only. No solves, no fits, no data altered, no conversion changed.
`docs/OPEN_ITEMS.md` 1.9 remains Parsa's to resolve; this run draws the consequence and stops.

---

## TASK 0 — the conversion chain, derived from the columns

Derived from `derived_R2A_LB_current.csv` and `derived_M9_current.csv` by reproducing each column
from its inputs, not from the README's summary. Every column below was reproduced to
**≤ 8.5 × 10⁻¹⁴** relative deviation on all 113 growing R2A/LB rows and 59 M9 rows
(`task2_sensitivity.py` asserts this, so the chain is checked on every run):

```
R_O2_mg_cell_min      = C_tot_O2_mg_per_L / biomass_integral_cells_min_per_L
biomass_integral…     = N0_cells_per_L * (exp(r * T_end_min) - 1) / r        [D5]
growth_C_per_C_h      = r * 60
growth_fgC_h          = r * 60 * cell_carbon_fg
respiration_fgC_h     = R_O2_mg_cell_min * 60 * 1e12 * (12.011 / 31.998)
respiration_C_per_C_h = respiration_fgC_h / cell_carbon_fg
CUE                   = growth_fgC_h / (growth_fgC_h + respiration_fgC_h)
resp_over_growth      = respiration_C_per_C_h / growth_C_per_C_h
```

**Where the constants enter.** `N0_cells_per_L` = 4 × 10⁸ in every row of both media, and enters
*only* through the biomass integral — hence `R_O2_mg_cell_min` and everything below it.
`cell_carbon_fg` = 350 everywhere (2 µm³ × 175 fg µm⁻³) and enters `growth_fgC_h`,
`respiration_C_per_C_h`, `CUE` and `resp_over_growth`. **`cell_volume_um3` enters no derived column
at all** — it is carried but unused. `growth_C_per_C_h = r × 60` is immune to both.

**What the likelihood compares against.** Read from `gate_def.py`: `load_obs(csv, OTU[medium],
"R_O2_mg_cell_min")`, replicate-averaged by `groupby("T").mean()`. So the respiration observable is
`R_O2_mg_cell_min` — which **contains `N₀` but not `cell_carbon_fg`.**

**Disagreement with the README, and it matters.** `strains/eciML1515/respirometry/README.md` and
OPEN_ITEMS 1.9 both frame the ~6× cell-carbon discrepancy as putting "respiration R²" at risk
alongside CUE and absolute per-cell rates. On the chain above it cannot: the fitted respiration
observable has **factor exactly 1.0000** under the alternative conversion (verified to 4 × 10⁻¹⁶).
The risk to the respiration likelihood, such as it is, comes from `N₀` — a different constant, which
1.9 names but does not connect to the respiration term.

**A second disagreement, smaller.** 1.9 describes the two conversions as "~6× apart". They are
6.0588× apart *on carbon per cell*, but they disagree on **both** constants: 2 µm³ vs 21.21 µm³ is
**10.61×**, while the implied carbon density is **175 vs 100 fg C µm⁻³** (0.57×). These partly
cancel. Two independent constants disagreeing makes a single typo an unlikely explanation.

---

## TASK 1 — the residual: does it trend, and with growth rate or temperature?

`fit_predictions.csv` (configurations D, E, F at Parsa's gated parameters, committed by E4) joined
to the derived tables on medium and temperature; residual `r = log(measured O₂ / modelled O₂)`;
**72 points** = 3 configurations × 2 media × 12 temperatures.

**Replicates** are the mean per (medium, temperature), because that is exactly what
`gate_def.load_obs` gives the likelihood. Per-replicate `sd` and `n` are carried in
`task1_residuals.csv` but do not weight the regressions — the likelihood does not weight them
either (D1). The model curve is on a 1.5 °C dense grid and is linearly interpolated onto the
measured temperatures (D2).

### The marginal regressions — mixed, and unable to separate the two

| config | medium | against | slope | 95 % CI | p | R² |
|---|---|---|---|---|---|---|
| D | NLDM | temperature | **+0.0268** | [+0.0121, +0.0414] | **0.0022** | 0.62 |
| D | NLDM | growth rate | **+0.331** | [+0.023, +0.638] | **0.038** | 0.36 |
| D | LB | temperature | +0.0094 | [−0.0028, +0.0216] | 0.116 | 0.23 |
| D | LB | growth rate | +0.032 | [−0.107, +0.170] | 0.620 | 0.03 |
| E | NLDM | temperature | −0.0105 | [−0.0357, +0.0147] | 0.375 | 0.08 |
| E | NLDM | growth rate | −0.084 | [−0.504, +0.336] | 0.667 | 0.02 |
| E | LB | temperature | +0.0154 | [−0.0008, +0.0317] | 0.061 | 0.31 |
| E | LB | growth rate | +0.085 | [−0.103, +0.273] | 0.339 | 0.09 |
| F | NLDM | temperature | −0.0103 | [−0.0249, +0.0043] | 0.149 | 0.20 |
| F | NLDM | growth rate | +0.040 | [−0.222, +0.301] | 0.742 | 0.01 |
| F | LB | temperature | +0.0014 | [−0.0135, +0.0162] | 0.842 | 0.00 |
| F | LB | growth rate | +0.007 | [−0.143, +0.158] | 0.917 | 0.00 |

Only configuration D's NLDM residual trends significantly, and it trends on *both* axes — which is
what collinearity along a TPC produces. Nothing here separates a conversion artefact from a model
failure, and the fact that the trend appears in one configuration of three already points away from
the data and towards that model.

### The decisive comparison — temperature held exactly, growth rate varying

At all 12 temperatures both media have data, and they grow at different rates. `resp_scale` is
fitted **per medium** (D: 3.336/3.369, E: 10.230/5.325, F: 11.041/4.705 for NLDM/LB), so a constant
offset between media is already absorbed; the test is therefore a **slope** test with a free
intercept (D3). Configuration D shown; E and F are in `task1_paired_media.csv`.

| T (°C) | µ NLDM | µ LB | Δµ | resid NLDM | resid LB | Δresid |
|---|---|---|---|---|---|---|
| 15 | 0.094 | 0.126 | 0.032 | −0.662 | +0.064 | **+0.725** |
| 20 | 0.256 | 0.324 | 0.068 | −0.773 | −0.052 | **+0.720** |
| 25 | 0.585 | 0.750 | 0.164 | −0.222 | +0.211 | +0.433 |
| 27 | 0.726 | 0.946 | 0.220 | −0.220 | −0.266 | −0.046 |
| 30 | 1.055 | 1.376 | 0.322 | −0.050 | −0.162 | −0.112 |
| 35 | 1.563 | 2.156 | 0.593 | +0.175 | −0.223 | −0.398 |
| 37 | 1.853 | 2.398 | 0.545 | +0.228 | −0.099 | −0.327 |
| 40 | 2.076 | 2.944 | 0.868 | −0.031 | −0.017 | +0.015 |
| 43 | 1.594 | 2.945 | **1.351** | +0.386 | +0.371 | −0.015 |
| 45 | 0.915 | 2.915 | **2.000** | +0.500 | +0.336 | −0.163 |
| 47 | 0.457 | 1.796 | **1.339** | −0.042 | +0.217 | +0.259 |
| 50 | 0.094 | 0.134 | 0.039 | +0.013 | +0.242 | +0.229 |

**Δresidual does not track Δgrowth-rate in any configuration:**

| config | slope of Δresid on Δµ | 95 % CI | p | R² |
|---|---|---|---|---|
| D | **−0.252** | [−0.622, +0.118] | 0.160 | 0.19 |
| E | **−0.020** | [−0.524, +0.485] | 0.933 | 0.00 |
| F | **+0.006** | [−0.273, +0.284] | 0.965 | 0.00 |

The largest Δresiduals (+0.72 at 15 and 20 °C) occur where Δµ is *smallest* (0.03–0.07 h⁻¹), and the
largest Δµ (2.00 h⁻¹ at 45 °C) has Δresid −0.16. The sign in D is **opposite** to the artefact's
prediction. **This is a null result** (D4), and it is conversion-independent: TASK 1's two inputs
both have factor exactly 1.0000 under the alternative constants.

Figure: `task1_residuals.png` (`task1_figure.py`) — residual against temperature, against growth
rate, and the paired difference with the artefact's expected band shaded.

---

## TASK 2 — sensitivity to the conversion

Whole chain recomputed under 2120.58 fg against 350 fg, after first reproducing all seven columns
from the table's own constants (the check on TASK 0's derivation — it passes):

| quantity | factor | constant? | temperature dependence |
|---|---|---|---|
| `R_O2_mg_cell_min` — **the likelihood's observable** | **1.0000** | yes | **unmoved** |
| `growth_C_per_C_h` | **1.0000** | yes | **unmoved** |
| `respiration_fgC_h` | **1.0000** | yes | **unmoved** |
| `growth_fgC_h` | 6.0588 | yes | unmoved — scale only |
| `respiration_C_per_C_h` | 0.1650 | yes | unmoved — scale only |
| `resp_over_growth` | 0.1650 | yes | unmoved — scale only |
| `CUE` | **1.2344 – 6.0576** | **NO** | **MOVED** |

**The three scale-invariant quantities do not move**, exactly as the TASK 0 derivation predicted —
that is the numerical check on the derivation, and it passes. Three move by an exactly constant
factor, so only their level changes and `d log q / dT` is identical to machine precision: absorbable
by a scale parameter.

### CUE moves, and its shape moves

CUE is `growthC / (growthC + respC)` — not linear in the constant.

| | table (350 fg) | config.R (2120.58 fg) |
|---|---|---|
| R2A/LB CUE range | 0.072 – 0.664 | 0.241 – 0.922 |
| spread across temperature | 0.591 | 0.680 |
| `d log CUE / dT`, NLDM | −0.0587 | **−0.0436** |
| `d log CUE / dT`, LB | −0.0476 | **−0.0362** |
| `d log CUE / dT`, M9 | −0.1646 | **−0.1461** |

Per-temperature values in `task2_cue.csv`. This is material: at 15 °C LB CUE goes 0.40 → 0.80, and
the temperature dependence weakens by ~25 %. **`reports/ecoli_deck/fig_cue.png` needs a caveat**;
noted in the deck's `DECISIONS.md` without touching the deck, which is E5's branch.

---

## TASK 3 — what a growth-rate-dependent cell size would do

**The repository cites nothing for this**, so the band is sourced externally and said to be:
`Basan2015` and `Scott2010` are proteome allocation against growth rate, not cell size;
`Mairet2021` is the temperature dependence of growth laws; and `Cooper2007` is, despite its key,
Cooper, Bennett & Lenski **2001**, *Evolution* **55**:889–896, on the evolution of thermal
dependence.

**The relation.** Schaechter, Maaløe & Kjeldgaard 1958, *J. Gen. Microbiol.* **19**:592–606 — mean
cell mass rises exponentially with growth rate, `M(µ) = M₀ exp(k µ)`. Through the Donachie/Cooper
replication-plus-division period, `k = (C + D) ln 2` with `C + D` ≈ 40–70 min, giving
**k = 0.45–0.80 h**.

**Schaechter et al.'s result is itself the reason the paired test is the right one.** Cell size
tracks growth rate when growth rate is set by **medium composition**, and is very nearly
**invariant** when it is set by **temperature** at fixed medium. The axis on which a constant
fg C cell⁻¹ is genuinely in danger is therefore the medium axis — which is exactly the axis the
paired comparison isolates. The marginal growth-rate regression was never the right question.

**Was the test powered?** The artefact predicts `residual = k µ + const`, so the paired slope
estimates `k` *directly*. Against the band:

| config | slope | 95 % CI | excludes the whole band? |
|---|---|---|---|
| D | −0.252 | [−0.622, **+0.118**] | **yes** |
| E | −0.020 | [−0.524, +0.485] | no — interval too wide |
| F | +0.006 | [−0.273, **+0.284**] | **yes** |

**2 of 3, not 3 of 3.** In magnitude: the largest between-media growth-rate difference is 2.00 h⁻¹
(45 °C), so a size effect at k = 0.45–0.80 would displace the paired residual by **+0.90 to +1.60 in
log — a factor of 2.5 to 5.0** — against a residual scatter of sd 0.22–0.42 (0.31 pooled). That is
**2.9 to 5.2× the noise.** Had the effect been there at literature magnitude, it would have been
plainly visible.

**The fraction it could account for** — order of magnitude, from a literature band, not a fit. Along
the temperature axis a size effect must follow `µ(T)`, which is hump-shaped, so it cannot produce a
monotone trend; `µ` is only weakly *linear* in T (R² = 0.09 NLDM, 0.31 LB). Propagating the band
through `dµ/dT`:

| config / medium | observed `dr/dT` | artefact `dr/dT` | fraction |
|---|---|---|---|
| D / NLDM | +0.0268 | +0.0085 … +0.0151 | **0.32 – 0.56** |
| D / LB | +0.0094 | +0.0249 … +0.0442 | 2.6 – 4.7 |
| E / NLDM | −0.0105 | +0.0085 … +0.0151 | wrong sign |
| E / LB | +0.0154 | +0.0249 … +0.0442 | 1.6 – 2.9 |
| F / NLDM | −0.0103 | +0.0085 … +0.0151 | wrong sign |
| F / LB | +0.0014 | +0.0249 … +0.0442 | 18 – 32 |

One cell of six lies in (0, 1): size could account for **roughly a third to a half** of
configuration D's NLDM trend — the one significant marginal trend. In the other five the artefact
predicts the wrong sign, or a trend 1.6–32× larger than observed. The data are, if anything, *less*
consistent with a size effect than with none.

**What would settle it:** per-condition cell size or dry mass measured alongside the respirometry —
sizing-channel counts, or dry weight per cell — at each temperature on each medium, replacing both
constants with a measured `fg C cell⁻¹(medium, T)`. The fitted `K` cannot substitute: it is in
OD-like units (8.1 × 10⁻⁶ – 2.2 × 10⁻²), not a cell count. **Whether such data exist is Parsa's to
answer; this run does not assume either way.**

---

## TASK 4 — what it means for P16: an all-clear, with one caveat that is not about cell carbon

**The all-clear.** On current evidence the respiration likelihood is safe from the 1.9 discrepancy:

1. Its observable, `R_O2_mg_cell_min`, **does not contain `cell_carbon_fg`** — factor exactly
   1.0000 under the alternative conversion. The 350-vs-2120.58 fg question cannot reach the
   respiration term at all.
2. `N₀` *does* reach it, but the biomass integral is **exactly linear in `N₀`** (D5, verified to
   7 × 10⁻¹⁴ on all 183 growing rows), and `N₀` is one global constant. So an `N₀` error is a
   **uniform multiplicative error**, absorbed by `resp_scale` with **no effect on the temperature
   dependence** — and the temperature dependence is what the thermal parameters read.
3. The one mechanism that could have made the error non-uniform along the temperature axis — a
   growth-rate-dependent cell size — is **not detectable** in a test with 2.9–5.2× the power needed
   to see it at literature magnitude.

**The caveat that remains, stated as a caveat.** `resp_scale` is a fitted observation parameter that
absorbs whatever uniform scale error the conversion carries, so **its posterior should not be read
as physiology.** As fitted it already ranges 3.34–11.04 across configurations and media (a 3.3×
spread) — far more variation than physiology alone would explain — so this is not a new warning so
much as a quantified one. The point for P16 is the division: `resp_scale`'s *level* is
uninterpretable, while the respiration term's *temperature dependence*, and therefore the thermal
parameters, carry no imprint from this.

**Two further things, recorded rather than pursued.** (a) The biomass integral is **exponential** —
`K` is fitted and reported but never used downstream. The fit window is temperature-adapted so that
`r · T_end` stays near-constant at ~3.0–3.3 through the mid-range (a comparable ~20–28× fold-change
at every temperature), so this introduces no hidden temperature dependence; it falls away only at
15 and 50 °C where growth barely happens. (b) Because the integral contains `r`, the respiration
observable is `C_tot_O2` divided by a function of the **fitted growth rate**, so the respiration and
growth observables are **not statistically independent** — the likelihood treats them as though they
were. That is the pipeline's design and outside Q1's question, but it belongs in OPEN_ITEMS.

**Nothing was changed.** No data, no conversion, no config. 1.9 remains Parsa's to resolve.

---

## Reproducing

```
python3 reports/Q1_n0_check/task1_residuals.py     # residuals, regressions, paired-media test
python3 reports/Q1_n0_check/task1_figure.py        # task1_residuals.png
python3 reports/Q1_n0_check/task2_sensitivity.py   # chain check + sensitivity + CUE
python3 reports/Q1_n0_check/task3_size_growth.py   # power against the literature band
```

Inputs, all committed: `strains/eciML1515/respirometry/derived_{R2A_LB,M9}_current.csv`,
`reports/ecoli_deck/fit_predictions.csv`. Judgement calls in `DECISIONS.md` (D0–D8).
