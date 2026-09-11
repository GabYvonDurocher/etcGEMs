# Q1 — decisions and judgement calls

---

## D0. The conversion chain, derived from the columns rather than from the README

The respirometry pipeline's scripts are deliberately not copied into this repository (they live at
`$ECOLI_R2A` / `$ECOLI_M9`, read-only), so the chain is **reconstructed from the derived tables
themselves** and each link checked numerically on all 113 growing rows of `derived_R2A_LB_current.csv`
and all 59 of `derived_M9_current.csv`. Every relation below holds to floating-point exactness
(max relative deviation quoted).

| link | relation | checked |
|:--|:--|--:|
| per-cell O₂ rate | `R_O2_mg_cell_min` = `C_tot_O2_mg_per_L` / `biomass_integral_cells_min_per_L` | 4.0e-16 |
| growth, scale-free | `growth_C_per_C_h` = `r` × 60 | 4.9e-14 |
| growth, absolute | `growth_fgC_h` = `r` × 60 × **`cell_carbon_fg`** | 5.0e-14 |
| respiration, absolute | `respiration_fgC_h` = `R_O2_mg_cell_min` × 60 × **1e12** × (12.011/31.998) | 3.6e-16 |
| respiration, per carbon | `respiration_C_per_C_h` = `respiration_fgC_h` / **`cell_carbon_fg`** | 7.2e-16 |
| efficiency | `CUE` = `growth_C_per_C_h` / (`growth_C_per_C_h` + `respiration_C_per_C_h`) | 4.3e-14 |
| ratio | `resp_over_growth` = `respiration_C_per_C_h` / `growth_C_per_C_h` | 1.8e-15 |

**Where each constant enters.**

* **`N0_cells_per_L` = 4 × 10⁸ for every row of both media** (one unique value; equal to
  `N_inoculation_cells_per_L`, with `delta_Ninoc_to_N0_min` = 0). It enters **only** through
  `biomass_integral_cells_min_per_L`, and therefore through `R_O2_mg_cell_min` and everything
  downstream of it.
* **`cell_carbon_fg` = 350 for every row** (= `cell_volume_um3` 2 × `carbon_density_fg_per_um3` 175,
  per `otu_cell_sizes_*.csv`, identical for both OTUs). It enters **`growth_fgC_h`** and
  **`respiration_C_per_C_h`**, and hence `CUE` and `resp_over_growth`.
* **`cell_volume_um3` enters no derived column in these tables.** It is carried as provenance; the
  product has already been taken in `cell_carbon_fg`.

**So, affected or not:**

| quantity | `N0` | `cell_carbon_fg` |
|:--|:--:|:--:|
| `growth_C_per_C_h` — **the growth observable** | **no** | **no** |
| `R_O2_mg_cell_min` — **the respiration observable** | **yes** | **no** |
| `respiration_fgC_h` | yes | no |
| `growth_fgC_h` | no | **yes** |
| `respiration_C_per_C_h` | yes | **yes** |
| `CUE`, `resp_over_growth` | yes | **yes** |

**What the likelihood compares against.** Read from `reports/P3_gate/gate_def.py`: `load_obs(csv,
OTU[medium], "growth_C_per_C_h")` and `load_obs(csv, OTU[medium], "R_O2_mg_cell_min")`, the
replicate **mean per temperature**, against `flux_tpc` growth and `o2_uptake × O2_CONV ×
resp_scale`. So the respiration term sees **`R_O2_mg_cell_min`** and nothing else.

### Where this agrees with the README, and where it does not

**Agrees:** growth R² and scale-free quantities are immune — `growth_C_per_C_h` = `r` × 60 contains
neither constant. CUE and `resp_over_growth` are affected. Absolute per-cell rates are affected.

**Disagrees, and it matters for what follows.** `docs/OPEN_ITEMS.md` 1.9 names
"`cell_volume_um3`/`cell_carbon_fg`" and the ~6× discrepancy as the threat to "respiration R², CUE
and absolute per-cell rates". **The respiration observable the likelihood actually uses,
`R_O2_mg_cell_min`, does not contain `cell_carbon_fg` at all** — it is mg O₂ per cell per minute,
and the carbon conversion is applied only *downstream* of it, in columns the model never sees. So
the 350-vs-2120.58 fg discrepancy **cannot touch the respiration likelihood**. What the respiration
likelihood *does* depend on is **`N0`**, through the biomass integral — a different constant, with a
different and unquantified provenance, and one that 1.9 mentions only in passing.

**Two things this reconstruction cannot settle, and they are stated rather than assumed.** How `N0`
propagates into `biomass_integral_cells_min_per_L` is not recoverable from these columns —
`K` ranges 8.1e-6 to 2.2e-2, which is not a cell count, so the integral is built from the logistic
fit in units this table does not expose. Whether an `N0` error therefore scales
`R_O2_mg_cell_min` uniformly, or non-uniformly along the temperature axis, **cannot be derived
here**; it is decided empirically in TASK 1 instead. And the mg-O₂→fg-C step assumes **one carbon
per O₂** (a respiratory quotient of 1), which is a modelling choice in the pipeline, not a
measurement.

## D1 — replicates are the mean per (medium, temperature), because that is what the likelihood sees

`gate_def.load_obs` does `groupby("T")[col].mean()`, so the fit compares the model against the
replicate mean. The residual is formed on the same means — one point per (medium, temperature), 12
temperatures per medium. Per-replicate `sd` and `n` are carried in `task1_residuals.csv` so the
weight behind each point is visible, but they do **not** weight the regressions: the likelihood does
not weight them either, and weighting here would measure something the fit never optimised.

## D2 — the residual is computed for all three configurations D, E and F

One configuration cannot distinguish "the conversion imprints itself on the data" from "this
particular model is wrong". A trend present in D, E and F alike points at the data; a trend in one
points at that model. Cost is nil — the predictions are all in the committed
`reports/ecoli_deck/fit_predictions.csv`. `fit_predictions.csv` is on a 1.5 °C dense grid and the
measurements are not, so the model curve is linearly interpolated onto the measured temperatures;
the grid is fine enough (1.5 °C) that interpolation error is far below the residual scale.

## D3 — the paired-media regression carries a free intercept, and that is not a concession

Read from `make_fit_figures.py`: the model's per-cell rate is `mmol gDW⁻¹ h⁻¹ × gdw_per_cell ×
resp_scale`, where `gdw_per_cell = 2.8e-13` is a **single constant** in
`strains/eciML1515/gas_exchange.yaml` — no growth-rate dependence anywhere in the conversion. That
is precisely the configuration in which a Schaechter-type size/growth relation would surface as a
residual tracking growth rate.

But `resp_scale` is fitted **separately per (config, medium)** — D: 3.336 / 3.369, E: 10.230 /
5.325, F: 11.041 / 4.705 for NLDM / LB. So any *constant* offset in per-cell scale between the two
media has already been absorbed into `resp_scale` and cannot appear in the residual. The paired test
therefore regresses Δresidual on Δgrowth-rate **with a free intercept**: the intercept absorbs the
absorbed offset, and the slope — which `resp_scale` cannot absorb, because it is one number per
medium and the growth-rate difference varies across temperatures — is the informative quantity.
This is the reason the test is a slope test and not a comparison of residual levels.

## D4 — TASK 1 verdict: no growth-rate imprint at fixed temperature

The marginal regressions are mixed and configuration-specific: in configuration D the NLDM residual
trends with temperature (slope +0.0268 per °C, 95 % CI [+0.0121, +0.0414], p = 0.0022, R² = 0.62)
and, confoundedly, with growth rate (+0.331 [+0.023, +0.638], p = 0.038, R² = 0.36); in E and F
nothing reaches p < 0.05 on either axis in either medium. That mixture is what the confound
predicts and it settles nothing on its own.

The paired-media test — temperature held exactly, growth rate varying by up to 2.0 h⁻¹ between
media — finds no relation in any configuration: D slope −0.252 [−0.622, +0.118] p = 0.16, E −0.020
[−0.524, +0.485] p = 0.93, F +0.006 [−0.273, +0.284] p = 0.96. The sign in D is *opposite* to the
artefact's prediction. TASK 3 sources the literature band as k = 0.45-0.80 h and finds that D's and
F's intervals exclude it entirely while E's is too wide to (upper bound +0.485 against a band
starting at 0.45); the band quoted in an earlier draft of this entry, 0.35-0.75, was provisional
and is superseded by D7's sourced value. This is a null result and is reported as such.

## D5 — the biomass integral is exponential and exactly proportional to N0, which closes what D0 left open

D0 left open "whether an N0 error scales the observable uniformly", because `K` ranges
8.1e-6–2.2e-2 and is plainly not a cell count, so the integral's construction could not be read off
the columns. It can be reproduced from them. On **all 183 growing rows of both media**:

    biomass_integral_cells_min_per_L == N0_cells_per_L * (exp(r * T_end_min) - 1) / r

to `max|ratio - 1| = 6.9e-14` (R2A/LB, n = 117) and `7.1e-14` (M9, n = 66). Two consequences:

1. **The integral is exponential, not logistic — `K` does not enter it at all.** `K` is fitted and
   reported but is not used downstream. Reassuringly, the fit window is temperature-adapted
   (mean `T_end` 1262 min at 15 °C down to 86 min at 37 °C) such that `r·T_end` is near-constant at
   ~3.0–3.3 through the mid-range, i.e. a comparable fold-change (~20–28×) at every temperature.
   The window was chosen to sit in exponential phase, and it does so consistently across
   temperature, so this introduces no hidden temperature dependence. It falls away only at the
   extremes where growth barely happens (`r·T_end` 2.3 at 15 °C, 0.25 at 50 °C).
2. **The integral is exactly linear in `N0`,** hence `R_O2_mg_cell_min = C_tot_O2 / integral` is
   exactly inversely proportional to `N0`. Since `N0 = 4e8` is one global constant, an N0 error is a
   **uniform multiplicative error in the likelihood's respiration observable** — fully absorbable by
   the fitted `resp_scale`, with **no effect on temperature dependence**. D0's open question is
   answered: uniform.

One observation, recorded rather than pursued: because the integral contains `r`, the respiration
observable is `C_tot_O2` divided by a function of the fitted growth rate, so it is not statistically
independent of the growth observable. That is the pipeline's design and is outside Q1's question,
but it belongs in OPEN_ITEMS.

## D6 — TASK 2: the likelihood's observable does not move at all; CUE moves and changes shape

The conversions differ in **both** constants, not one: 2 µm³ vs 21.21 µm³ is **10.61×**, while the
implied carbon density is **175 vs 100 fg C µm⁻³** (0.57×). These partly cancel to the 6.0588× in
carbon per cell that 1.9 records. So 1.9's "~6× apart" is right about carbon per cell but
understates the disagreement: two independent constants disagree, which makes a single typo an
unlikely explanation.

Recomputing the whole chain under each, all 7 columns first reproduced from the table's own
constants to ≤ 8.5e-14 (the check on D0's derivation):

| quantity | factor | constant? | temperature dependence |
|---|---|---|---|
| `R_O2_mg_cell_min` (**the likelihood's observable**) | **1.0000** | yes | unmoved |
| `growth_C_per_C_h` | **1.0000** | yes | unmoved |
| `respiration_fgC_h` | **1.0000** | yes | unmoved |
| `growth_fgC_h` | 6.0588 | yes | unmoved (scale only) |
| `respiration_C_per_C_h` | 0.1650 | yes | unmoved (scale only) |
| `resp_over_growth` | 0.1650 | yes | unmoved (scale only) |
| `CUE` | **1.2344–6.0576** | **NO** | **moved** |

Three quantities do not move at all, exactly as D0's derivation predicted — that is the numerical
check on the derivation, and it passes. Three move by an exactly constant factor, so only their
level changes and `d log q / dT` is identical to machine precision: absorbable by a scale parameter.

**CUE is the exception and it matters.** It is `growthC / (growthC + respC)`, not linear in the
constant, so its *shape* moves: R2A/LB CUE goes from 0.072–0.664 to 0.241–0.922, and
`d log CUE / dT` from −0.0587 to −0.0436 (NLDM) and −0.0476 to −0.0362 (LB). M9 likewise
(−0.1646 → −0.1461). This is material and the deck's `fig_cue.png` needs a caveat (TASK 5).

TASK 1's residual is built from `R_O2_mg_cell_min` and `growth_C_per_C_h`, both factor exactly
1.0000 (verified to 0 relative deviation), so **every slope, CI, p and R² in TASK 1 is unchanged by
the conversion**. The null result is conversion-independent.

## D7 — the size/growth band, and the fact that the repository cites nothing for it

**The repository cites no cell-size/growth-rate reference.** `references.bib` (identical in
`ecoli_deck/`, `ecoli_tpc/` and `activation_energy/`) has `Basan2015` and `Scott2010` — proteome
allocation against growth rate, not cell size — and `Mairet2021` on the temperature dependence of
growth laws. `Cooper2007` is not a cell-size paper: despite the key it is Cooper, Bennett & Lenski
**2001**, *Evolution* **55**:889–896, on the evolution of thermal dependence. So this band is
sourced from outside the repository and that is stated in the report rather than hidden behind a
citation key.

**The band.** The nutrient growth law — Schaechter, Maaløe & Kjeldgaard 1958, *J. Gen. Microbiol.*
**19**:592–606 — has mean cell mass rising exponentially with growth rate,
`M(µ) = M₀ exp(k µ)`. Reading `k` through the Donachie/Cooper replication-plus-division period,
`k = (C + D) ln 2` with `C + D` ≈ 40–70 min in E. coli, gives **k = 0.45–0.80 h**. An earlier draft
of D4 used a provisional 0.35–0.75 before this was sourced; 0.45–0.80 supersedes it and
`task1_figure.py`'s band was regenerated to match.

**Why the paired-media test is the right test and not merely a convenient one.** Schaechter et
al.'s own central result is that cell size tracks growth rate when growth rate is set by **medium
composition**, and is very nearly **invariant** when growth rate is set by **temperature** at fixed
medium. So the axis on which a constant fg-C-per-cell is genuinely in danger is the medium axis —
which is exactly the axis the paired comparison isolates with temperature held. This makes the
paired test not a workaround for the confound but the directly appropriate measurement, and it also
means the marginal growth-rate regression was never the right question.

## D8 — TASK 3: the test was powered, and the artefact's signature is the wrong shape anyway

**Power.** The artefact predicts `residual = k µ + const`, so the paired regression's slope
estimates `k` *directly* — no conversion needed. Against the band 0.45–0.80: configuration **D**
excludes it entirely (CI upper bound +0.118) and so does **F** (+0.284); **E** does not (+0.485,
against a band beginning at 0.45), because E's residuals are the noisiest. **2 of 3 configurations
exclude the entire literature band at 95 %** — reported as 2 of 3, not 3 of 3.

**Shape.** Along the temperature axis a size effect must be proportional to `µ(T)`, which is
hump-shaped, so it cannot produce a clean monotone trend; growth rate is only weakly *linear* in
temperature over the full series (µ-vs-T R² = 0.09 for NLDM, 0.31 for LB). Propagating the band
through `dµ/dT` gives the induced `dr/dT` against the observed:

| config / medium | observed dr/dT | artefact dr/dT (band) | fraction |
|---|---|---|---|
| D / NLDM | +0.0268 | +0.0085 .. +0.0151 | **0.32–0.56** |
| D / LB | +0.0094 | +0.0249 .. +0.0442 | 2.6–4.7 |
| E / NLDM | −0.0105 | +0.0085 .. +0.0151 | opposite sign |
| E / LB | +0.0154 | +0.0249 .. +0.0442 | 1.6–2.9 |
| F / NLDM | −0.0103 | +0.0085 .. +0.0151 | opposite sign |
| F / LB | +0.0014 | +0.0249 .. +0.0442 | 18–32 |

Only one of six cells sits in `(0, 1)`: a literature-magnitude size effect could account for
**roughly a third to a half** of configuration D's NLDM temperature trend — the one marginal trend
that was significant. In the other five it predicts the wrong sign or a trend 1.6–32× larger than
observed. So the data are, if anything, *less* consistent with a size effect than with none. These
are order-of-magnitude estimates from a literature band, not fits, and are labelled as such.

**The measurement that would settle it.** Per-condition cell size or dry mass measured alongside
the respirometry — cell counts with a sizing channel, or dry weight per cell — at each temperature
and on each medium, which would replace both constants with a measured `fg C cell⁻¹ (medium, T)`.
The fitted `K` in the derived tables is in OD-like units (8.1e-6–2.2e-2) and is not a cell count, so
it cannot substitute. **Whether such data exist is Parsa's to answer; this run does not assume
either way.**
