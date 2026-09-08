# P4 TASK 4 — M9, first light

M9 has never been fitted by anyone. These are the first results, and they are reported as a
first result, not as a comparison. **The same caveat governs them as everything else in P4: the
chains are not converged** (τ 146–202, chain/τ 7–10), so the numbers below are indicative.

## What was fitted

M9 is glucose + salts, so it is mapped to the model's `glucose_minimal` medium — there is no
recipe and therefore no clearance K to sample, and the carbon cap (120) is the only carbon
limitation. Configurations E and F carry the cap here too, unlike their NLDM counterparts, for
that reason (pre-flight finding, DECISIONS D2). Data: `derived_M9_current.csv`, **OTU 1
(`Ecoli_M9`)**, 59 rows, 12 temperatures, 4–5 replicates each.

## The measured curve, and the fits

Measured M9 (OTU 1): a clean TPC peaking at **0.717 h⁻¹ at 40 °C**, collapsing to 0.050 at
45 °C and 0.0001 at 50 °C.

| fit | growth R² (MAP) | resp R² (MAP) | r_max | T_opt | acetate @37 °C | RQ @37 °C | resp_scale |
|---|---|---|---|---|---|---|---|
| **D M9** | **0.959** | 0.541 | 0.637 | 39.5 °C | 3.75 | 0.26 | 5.20 |
| **E M9** | **0.987** | 0.160 | 0.691 | 41.0 °C | 19.4 | 1.13 | 3.04 |
| **F M9** | **0.982** | 0.499 | 0.691 | 41.0 °C | 21.8 | 1.12 | 4.08 |

**The growth fits are the best in the whole exercise** — R² 0.96–0.99, r_max 0.637–0.691 against
a measured 0.717, T_opt 39.5–41 °C against a measured 40 °C. A minimal defined medium is exactly
the case an enzyme-constrained model should handle best: one carbon source, no amino-acid
shortcut, and the carbon cap doing work it can actually do.

**The respiration fits are the worst** — 0.16–0.54, against 0.56–0.92 on NLDM and LB. That is
worth flagging rather than explaining: on a minimal medium the per-cell respiration data are
smallest in absolute terms and most exposed to the N₀ and fg-C-per-cell constants (see
`strains/eciML1515/respirometry/README.md`), and configuration D's RQ of 0.26 at 37 °C says its
solution there is fermentative, not respiratory.

## How the posterior differs from NLDM and LB

| parameter | M9 (D / E / F) | NLDM (D / E) | LB (D) |
|---|---|---|---|
| `kcat_scale` | 0.84 / 0.92 / 0.93 | 1.44 / 1.74 | 1.69 |
| `sigma` (in-vivo saturation) | 0.49 / 0.50 / 0.47 | 0.73 / 0.64 | 0.73 |
| `dTopt` | 5.99 / 3.20 / 7.01 | 3.18 / 1.85 | 4.36 |
| `resp_scale` | 2.35 / 3.39 / 1.62 | 3.93 / 3.60 | 4.96 |
| `f_metab`, `f_maint` | ≈0.28, ≈0.36 | ≈0.28, ≈0.36 | ≈0.29, ≈0.35 |

The consistent difference is **capacity**: on M9 the fit wants `kcat_scale` ≈ 0.9 and
`sigma` ≈ 0.48, against ≈1.5–1.7 and ≈0.7 on the rich media. That is the expected direction — a
minimal medium reaches a lower peak (0.72 h⁻¹ against ~2 h⁻¹) and needs less catalytic capacity
to explain it, and σ ≈ 0.48 sits on the literature value of 0.45–0.5 rather than railing toward
1 as the rich fits do. The **allocation** parameters are indistinguishable across all three
media, which is what one expects of measured sector fractions that were never fitted per medium.

## Data-quality flags — checked, not assumed

1. **OTU 2 (`M9`) is not fittable and was not fitted.** Seven rows at four temperatures, with
   growth 0.0001 (25 °C), 0.324 (30), 0.020 (37), 0.302 (45) — non-monotonic, no collapse limb,
   1–3 replicates. Against OTU 1's clean 59-row curve this reads as a control or a
   partially-failed condition, not a second biological series. Only OTU 1 was used.
2. **The 25 °C no-growth series P3 found is in OTU 2, not OTU 1** — it is the `(25, 2, 'R2')`
   row the boundary fix added, with `K` = 8.4e-6. So it never entered these fits. OTU 1's 25 °C
   mean (0.173 h⁻¹, n = 4) is clean.
3. **The 45–47 °C replicate spread is large**: at 45 °C the mean is 0.050 with an SD of 0.077 —
   larger than the mean — and at 47 °C 0.011 ± 0.021. Those are the temperatures where the
   boundary fix added rows, i.e. where some replicates grew and others did not. The likelihood
   floors the SD rather than letting it dominate, but **the collapse limb on M9 is the least
   determined part of the curve**, and any statement about CT_max from these fits inherits that.
4. `Skipped_Series_Log.csv` for M9 is empty apart from its header: nothing was dropped by the
   pipeline. The rows that exist are the rows it kept.

None of these is a model problem. (1) and (2) are dataset structure; (3) is genuine biological
variability at the thermal limit.
