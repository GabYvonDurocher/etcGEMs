# Parsa's medium-dependent carbon / cell-number constants (item 1.9), assessed — a decision for the PI

_2026-09-16 (H1 TASK 3). **Nothing here is applied.** No derived table is altered, no constant is
propagated, no fit is re-run. The recommendation is the last section; the decision is the PI's._

**The files, copied unmodified into `reports/H1_handover/parsa_1_9/` with their hashes:**

| file | sha256 | size |
|---|---|---:|
| `09_medium_constants.R` | `3affc1c40abe8fdb03a8327a63093317cecead149ca2a7456d1c53b641384975` | 11,691 B |
| `METHODS_carbon_conversions.md` | `64c55688045d8d209e4386d949f1b24489a99df413def8d9571908f59963f3bf` | 4,991 B |

## 1. What he did

Both size-dependent constants are derived from **one per-medium input, the cell volume**, by fixed
formulas, so every medium is processed identically.

- **Cells per OD600 → N₀.** Volkmer & Heinemann (2011): *E. coli* K-12 packs a constant
  3.6 µL of cell volume per mL of culture at OD600 = 1. With an inoculum of OD600 = 0.0005,
  `N_inoc [cells L⁻¹] = 3.6 × 0.0005 × 1e9 × 1e3 / V = 1.8e9 / V`.
- **Carbon per cell.** A fixed carbon *density* times the medium's volume:
  `cell_carbon_fg = 180 × V`, the density taken as the mid-range of three independent direct
  measurements, with carbon as 47 % of dry weight measured on the exact strain (MG1655, Folsom &
  Carlson 2015).
- **Volumes** (Volkmer & Heinemann's growth-rate range ~1.5–4.4 µm³): LB 4.4, R2A 3.8,
  M9-glucose 2.2 µm³.

This **replaces** an earlier route that read per-cell dry mass off a growth-rate relationship and
had to be extrapolated past its calibration ceiling for LB and R2A. The direct-measurement route
is the better-founded of the two and the change is, in that respect, an improvement.

### His arithmetic reproduces his table — verified

| medium | V (µm³) | N₀ = 1.8e9/V | his table | carbon = 180 V | his table |
|---|---:|---:|---:|---:|---:|
| LB | 4.4 | 4.091 × 10⁸ | 4.09 × 10⁸ ✓ | 792 | 792 ✓ |
| R2A | 3.8 | 4.737 × 10⁸ | 4.74 × 10⁸ ✓ | 684 | 684 ✓ |
| M9-glucose | 2.2 | 8.182 × 10⁸ | 8.18 × 10⁸ ✓ | 396 | 396 ✓ |

The 1.8e9 constant also checks: 3.6 × 0.0005 × 1e9 × 1e3 = 1.8e9 exactly.

**Two immaterial wrinkles, recorded for completeness, neither an error in the result.** (i) The
METHODS calls 180 the *"midpoint"* of 132–204; the range midpoint is 168 and the **mean** of
(200, 204, 132) is 178.7, which rounds to 180 — it is the mean, not the midpoint. (ii) The R
script and the METHODS give slightly different values for the same three sources (script: 200,
200, ~140 with carbon at 50 %; METHODS: 200, 204, 132 with carbon at 47 %); the script's three
average to exactly 180. The two documents should be reconciled to one set before publication. The
±20 % spread he states across methods is the honest uncertainty either way.

## 2. The thing that needs a decision

His METHODS says the change *"does not alter the derived table the calibration likelihood consumes,
so no fit changes."* **That is true of his SCRIPT and not of his CONSTANTS**, and the distinction
is the whole of this assessment.

- **The script is safe.** `09_medium_constants.R` reads the finished derived table and writes only
  to `figures/medium_constants/` (`derived_medium_constants.csv`, `medium_constants_used.csv` and
  PNGs) — *"all NEW, nothing overwritten"*, verified by reading it. Nothing the likelihood reads is
  touched.
- **The constants are not.** **Q1 established** (`reports/Q1_n0_check/report.md:27–45`) that the
  likelihood's respiration observable is `R_O2_mg_cell_min`, that
  `R_O2_mg_cell_min = C_tot_O2_mg_per_L / biomass_integral`, that
  `biomass_integral = N0_cells_per_L × (exp(r·T_end) − 1)/r`, and therefore that the observable
  **contains N₀** (it does not contain `cell_carbon_fg`). Every committed derived table carries
  `N0_cells_per_L = 4.0 × 10⁸` in **every** row of both files. His N₀ is per-medium and different.

### How much the likelihood's observable would move, from the committed tables

`R_O2_mg_cell_min ∝ 1/N₀`, and N₀ is a single constant within a medium, so the movement is an
**exact multiplicative shift per medium** — a constant offset on the log scale the respiration
term uses:

| fits affected | table / OTU | N₀ now | N₀ proposed | observable × | change | log shift |
|---|---|---:|---:|---:|---:|---:|
| D/E/F **NLDM** (fit against R2A) | `derived_R2A_LB_current.csv`, OTU 1 | 4.00e8 | 4.74e8 | 0.8439 | **−15.6 %** | −0.170 |
| D/E/F **LB** | same file, OTU 2 | 4.00e8 | 4.09e8 | 0.9780 | −2.2 % | −0.022 |
| D/E/F **M9** | `derived_M9_current.csv` | 4.00e8 | 8.18e8 | 0.4890 | **−51.1 %** | −0.715 |

**M9's observable would halve.** That is the +105 % move in N₀ seen from the other side.

### Why R² is protected and what is not

The respiration term is Normal in **log O₂** with the model's prediction scaled by the fitted
`resp_scale`, and every fit is per-medium. A constant factor `c` on the observable shifts
`log y` by `log c` and is absorbed **exactly** by `resp_scale → resp_scale × 1/c`. The required
moves (×1.185 NLDM, ×1.023 LB, ×2.045 M9) sit well inside `resp_scale`'s prior support
[0.02, 50] — T2's fitted D-NLDM medians were 3.606 and 3.824 — so **R², the curve shapes, T_opt,
CT_max and the growth term are all untouched**, and so is the D/E/F evidence comparison, which is
within one medium.

**What is not protected:** `resp_scale`'s absolute value and its interpretation (it carries the
per-cell unit conversion, which is exactly what these constants are); any **cross-medium**
comparison of respiration level or of `resp_scale`; the CUE curves, which Q1 already found change
*shape* and not merely level under an alternative conversion; and any posterior already computed —
T2's runs were fitted against the current table.

**Conclusion: this is a LIKELIHOOD change, not a figures update.** It alters a number the
likelihood consumes, for six of the nine registered fits, by up to a factor of two. Under
RIGOUR.md it therefore needs a **new target identifier**, a **re-gate** (the P3 port-fidelity gate
reads the same respirometry tables) and its own registration — not a quiet substitution.

## 3. Two smaller points, recorded

1. **One volume per medium still ignores within-curve variation.** Cell volume varies with growth
   rate, and growth rate varies by an order of magnitude across a thermal performance curve, so a
   single volume per medium is applied at 15 °C and at 40 °C alike. His own header anticipates the
   objection (*"E. coli size ~invariant 15–30 °C"*, nutrient modulation ≠ temperature modulation),
   and **Q1's paired-media test found no growth-rate imprint in the residuals**
   (d(resid)/d(Δgrowth) = −0.252 [−0.622, +0.118], p = 0.16 for D; −0.020 and +0.006 for E and F,
   at 2.9–5.2× the power needed), so the neglected variation is empirically small. Worth stating
   as a limitation rather than fixing.
2. **Two routes to N₀ are proposed in one paragraph.** §4 of his METHODS says cells-per-OD600 will
   be measured directly (microscopy / flow cytometry) *and* elsewhere Ilgaz's Bayesian pipeline is
   the route; those are different estimators of the same quantity and the project should commit to
   one before either is propagated, or state explicitly which supersedes which.

## 4. Recommendation — not a decision

1. **Accept the derivation.** The density × volume route is better founded than the growth-rate
   extrapolation it replaces, the arithmetic is correct, and the provenance is properly documented.
2. **Do not propagate it into the pipeline as a figures update.** Register it as a **new target
   identifier** with its own gate, exactly as the f_metab removal and the infeasibility rule were
   handled (T1/T2): a core-level option, default OFF, gated 79/79 and 60/60, turned on per strain,
   with the invariant re-checked — here the check is that `resp_scale` absorbs the shift and every
   R² is unchanged, which is predicted above and should be *measured*.
3. **Sequence it after item 1.35.** Nothing is gained by re-fitting under new constants while the
   likelihood is still not a deterministic function of its parameters; and because the shift is
   exactly absorbable, waiting costs nothing scientifically.
4. **Reconcile the two documents** (the 180 provenance) and **pick one route to N₀** before either
   is published.
5. **Publish the figures now if wanted** — the script is safe and self-contained, and its outputs
   go to a new directory.

**Opened as OPEN_ITEMS 1.36 for the PI. Nothing was applied, and no derived table was altered.**
