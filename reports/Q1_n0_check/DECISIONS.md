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
