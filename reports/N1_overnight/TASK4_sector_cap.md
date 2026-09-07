# TASK 4 — the sector translation cap

_N1 TASK 4. K2 rung B4 found that with proteome sectors on and literature (non-temperature-
dependent) allocation, the translation cap removes the growth optimum rather than shifting
it. This establishes why, adds a guard, and does **not** change the model._

## The hypothesis, and the run that tests it

`docs/CANDIDA_DISCUSSION_2026-09-07.md` §6b notes that *E. coli*'s model carries **measured,
temperature- and medium-dependent** sector fractions, while Candida has none and gets
literature constants. The hypothesis: E. coli escapes the flattening only because
`allocation_from_data` makes its translation cap temperature-dependent.

Tested by running eciML1515 with `allocation_from_data` disabled and **nothing else
changed** (`configs/experiments/eci_sectors_no_alloc_data.yaml`), into a new output
directory. eciML1515's committed outputs are untouched.

| eciML1515 | T_opt | rmax | CTmax | **plateau within 1% of max** | within 0.01% |
|---|---|---|---|---|---|
| with `allocation_from_data` (as it runs) | 31.0 °C | 0.5429 | 46.88 °C | **2.0 °C** | 0.0 °C |
| **without it**, sectors still on | 31.0 °C | 0.5462 | 46.88 °C | **14.0 °C** | 13.0 °C |

**The hypothesis is confirmed.** E. coli flattens too. Its plateau goes from 2.0 °C to
14.0 °C on that one change, which is the same order as the 12.5–20.5 °C K2 measured in the
four Candida strains. **The flattening is a property of a temperature-independent
translation cap, not a property of the Candida strains.**

Note what does *not* move: T_opt (31.0 °C in both, because the plateau's low edge happens to
sit there) and CTmax (46.88 °C in both). The falling limb is still owned by the enzyme layer;
only the top is destroyed.

Outputs: `strains/eciML1515/outputs/n1_task4_sectors_no_alloc/{summary.json,tpc_*.csv}`.

## The mechanism, in one paragraph

The biosynthesis cap is `translation_coeff × v_biomass ≤ f_bio × P_total`. Every term is
temperature-independent unless the sector fractions themselves vary with temperature. So
once the cap binds, growth is pinned at exactly `f_bio × P_total / translation_coeff` over
the whole range in which the metabolic pool can supply that rate — a horizontal line, not a
peak. T_opt is then the argmax of a tie, which is also why K2 PART D found the two LP solvers
disagreeing about B4's T_opt by up to 8.5 °C while agreeing on growth to 2 × 10⁻⁵.

## The guard (implemented)

**A guard, not a modelling change.** Nothing about how any model runs has changed.

1. **A warning at build time**, `sectors.warn_sector_cap`, fires when
   `proteome_sectors.enabled` is true and `allocation_from_data` is absent. It names the
   risk, quotes the measured plateau widths, and says that any T_opt from the run is the
   argmax of a tie.
2. **The flatness is recorded**, `sectors.record_flatness` → `sector_flatness.json` in the
   run's own output folder: the width of the region within 1% and within 0.01% of the
   maximum, and the span of the grid it was measured on. It is written by both `etcgem tpc`
   and `etcgem transfer`, and **only when the risk applies**, so it is a new file and never
   an edit to an existing one.

Verified to fire exactly where it should:

| run | sectors | temperature-dependent allocation | guard |
|---|---|---|---|
| `candida_B4_sectors` (all four strains) | on | no | **fires**; plateau 14.0 °C recorded for *C. auris* |
| `transfer_candida` (B0), `candida_B3_ngamT` | off | — | silent |
| `etcgem tpc --strain eciML1515` | on | **yes** | silent |
| `etcgem tpc --strain mmaripaludis` | on | no | **fires** |

The *M. maripaludis* case is worth noting: it has sectors on with a fixed
`translation_coeff` and no allocation data, so it is in the at-risk class. Its plateau comes
back `NaN` because its bare TPC is identically zero at the a-priori `kcat_scale` — the
maintenance-crushed state its own `strain.yaml` documents — so the guard reports NaN rather
than inventing a number.

Every committed output is unchanged: eciML1515 and mmaripaludis TPCs byte-identical in all
three files each, and K1's gate 79/79.

## What I would propose, and why I did not do it

**Not done, deliberately.** Making the translation cap temperature-dependent is a modelling
decision with literature implications for every strain in the project, and it needs a human.

**The proposal, for that human.** The cap's temperature dependence should come from the same
place its magnitude does — measurement — and should be *explicit* rather than a side effect
of whether a strain happens to have proteomics attached. Three options, in the order I would
consider them:

1. **Make the absence of temperature dependence a declared choice rather than a default.**
   Today a strain gets a temperature-independent cap by *omitting* `allocation_from_data`,
   which is exactly the failure mode where the flattening is invisible. A required key —
   `proteome_sectors.cap_temperature_dependence: measured | none` — would make the
   configuration state which it is, and `none` would carry the guard's warning by
   construction. This is the cheapest change and the one I would do first. It is a schema
   change, not a modelling change, and no number moves.

2. **Ground the temperature dependence for yeast from measurement, when measurement
   exists.** `docs/CANDIDA_DISCUSSION_2026-09-07.md` §7 records that temperature-dependent
   yeast proteome allocation is thin — the closest dataset is anaerobic, and the 2025
   absolute-quantitative atlas is organised by growth rate rather than temperature. So this
   is currently blocked on data, and saying so is more useful than interpolating.

3. **A generic, literature-grounded ribosome temperature response**, applied to every strain
   that has no measured allocation. This is the option I would argue *against* without more
   evidence: it would put a fitted-in-spirit temperature dependence into the one layer of
   the model whose whole justification is that it is measured, and it would change
   *E. coli*'s and *M. maripaludis*' results as a side effect of a Candida problem.

**One thing that should be decided either way**, independent of the above: K2's rung B4
reports a `T_opt` that is the low edge of a plateau. Any descriptor read off a flat-topped
curve — T_opt, and the skewness and B80 that depend on the peak's position — should either
be suppressed or flagged in the outputs, not just in the report. The guard now records the
flatness beside the run; making the descriptor itself refuse to report a tie is a small
follow-up and would prevent the number being quoted.
