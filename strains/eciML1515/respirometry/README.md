# *E. coli* respirometry — measured growth and per-cell respiration

The measured half of configurations D, E and F. Ingested in P3 TASK 1.

## Provenance

Parsa, two complete runs of the **Candida respirometry pipeline**
(`01_convert_xlsx.R` … `08_outlier_trends.R`, `config.R`, `run_all.R`) at a slightly different
revision. Everything established about that method applies to these numbers.

| file | source | rows | conditions |
|---|---|---|---|
| `derived_R2A_LB_current.csv` | `$ECOLI_R2A/tables/derived_N0_R_results_with_carbon.csv`, 2026-09-07 13:28 | 117 | OTU 1 = `Ecoli_R2A`, OTU 2 = `Ecoli_LB` |
| `derived_R2A_LB_20260907_prefix.csv` | `$ECOLI_R2A/_backup_before_boundaryfix_20260907_1326/tables/…` | 113 | as above |
| `derived_M9_current.csv` | `$ECOLI_M9/tables/derived_N0_R_results_with_carbon.csv`, 2026-09-07 13:19 | 66 | OTU 1 = `Ecoli_M9`, OTU 2 = `M9` |
| `derived_M9_20260907_prefix.csv` | `$ECOLI_M9/_backup_before_boundaryfix_20260907_1301/tables/…` | 54 | as above |
| `otu_cell_sizes_*.csv`, `otu_names_*.csv`, `replication_*.csv`, `activation_energy_*.csv` | the same `tables/` directories | — | provenance and the measured E_a |

Temperatures 15–50 °C in both sets; 1–5 replicates per (temperature, condition).

**Deliberately NOT copied**, because they belong to the respirometry repository and not here:
the raw and intermediate oxygen exports (`Oxygen_All_Long.csv`, `Oxygen_Data_Filtered.csv`,
`Oxygen_Data_Smoothed_Trimmed.csv` — 12–15 MB each), `figures/`, `models/`, `scripts/` and the
run logs. They are at `$ECOLI_R2A` and `$ECOLI_M9` (default
`~/Downloads/Ecoli_R2A_LB` and `~/Downloads/Ecoli_M9`), **read only**.

## Columns used downstream

| column | used for |
|---|---|
| `T` | temperature, °C |
| `OTU` | condition: R2A → the model's NLDM medium; LB → the model's LB |
| `growth_C_per_C_h` | **the growth observable** (= `r` × 60, h⁻¹); mean ± SD over replicates per T |
| `R_O2_mg_cell_min` | **the respiration observable**, per cell; mean ± SD over replicates per T |
| `r`, `K` | the logistic fit's parameters; `r` = 1e-6 marks a no-growth series (below) |
| `CUE`, `resp_over_growth`, `growth_fgC_h`, `respiration_fgC_h` | derived; not used by the model comparison |

## What the 2026-09-07 boundary fix changed

A one-hunk change to `06_oxygen_fits.R`, and its own comment states the intent:

> `r` pinned at its LOWER bound is not a fit failure: above CTmax the true growth rate really
> is ~0, so the optimiser correctly parks r on the floor. Vetoing it silently deleted the
> thermal-collapse limb (50 C here). Treat it as a valid "no measurable growth" result; K,
> O2_0, or r at its UPPER bound still veto.

So the added rows are **intended observations of no measurable growth**, not fitting failures.
The pipeline's own log says so per series — `[boundary] at bound: r  (r at lower bound ->
treated as zero growth, KEPT)` — and distinguishes them from series it still drops. Both
`Skipped_Series_Log.csv` files are empty apart from their header.

**Every row present before the fix is bit-identical after it.** The fix only adds rows:
**+4** in R2A/LB (all at 50 °C) and **+12** in M9 (five at 50 °C, three at 47, three at 45 and
**one at 25 °C**). The 25 °C addition is worth knowing about: it is a no-growth series at a
benign temperature (`K` = 8.4e-6, essentially no signal), not a thermal-collapse point, and it
enters the M9 mean at 25 °C.

Effect on the model comparison, measured (P3 TASK 3): **≤ 0.021 in R²**, and it *improves*
NLDM growth (D +0.021, E +0.015, F +0.013) while leaving LB and every respiration R² within
0.002.

## Method caveats these numbers inherit — established from the data, not asserted

His R² validation is against **per-cell respiration**, the quantity most exposed to the
assumptions the Candida work spent weeks characterising. Three, with the evidence:

1. **The inoculum back-projection is OFF, for every row of both media sets.**
   `delta_Ninoc_to_N0_min == 0` in **117/117** R2A/LB rows and **66/66** M9 rows, and
   `N0_cells_per_L == N_inoculation_cells_per_L` (4 × 10⁸ cells/L) in every row of both. So
   N₀ is the inoculum density as pipetted, with no lag-phase back-projection — not only in
   the new rows, but throughout.
2. **`cell_volume_um3` and `cell_carbon_fg` are typed constants, not measurements.** Both take
   exactly **one** value across every row of both files: 2 µm³ and 350 fg, from
   `otu_cell_sizes.csv`, which types them per OTU as 2 µm³ × 175 fg µm⁻³. They do not vary with
   temperature, medium or condition.
   **And the two sources disagree**: the pipeline's own run log prints
   `Cell volume: 21.21 um^3 | C/cell: 2120.58 fg` from `config.R`, about 6× the value the
   derived tables carry. Reported, not adjudicated — but any absolute per-cell number depends
   on which is right.
3. **The M9 project's `config.R` still carries the R2A/LB condition labels**: its log reads
   `conditions = {1, 2} (1=Ecoli_R2A, 2=Ecoli_LB)` while its `otu_names.csv` says
   `1=Ecoli_M9, 2=M9`. A labelling inconsistency, not a numerical one.

**Which reported quantities this touches, and which it does not.**

* **Immune** — anything scale-free: activation energies, the *shape* of a growth or respiration
  curve, ratios such as RQ or `resp_over_growth`, and the R² of growth (`growth_C_per_C_h` is a
  specific rate, independent of N₀ and of the carbon-per-cell constant).
* **Affected** — anything absolute per cell: `R_O2_mg_cell_min`, `CUE`, `growth_fgC_h`,
  `respiration_fgC_h`, and therefore **the respiration R² of configurations D, E and F**, which
  are computed against `R_O2_mg_cell_min`. The model's fitted `resp_scale` (4.7–11.0 across the
  six fits) absorbs a constant offset of exactly this kind, so a systematic error in N₀ or in
  fg C per cell is partly re-parameterised rather than exposed — which is why the respiration
  R² is a statement about *shape*, and the scale factor is not evidence that the absolute level
  is right.

This section reports the caveats. It does not revise his results.
