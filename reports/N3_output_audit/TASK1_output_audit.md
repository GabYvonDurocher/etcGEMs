# N3 TASK 1 — is every output `reports/ecoli_tpc/assemble.py` reads consistent with the code that wrote it?

Cheap checks only; **nothing was re-run in this task** and nothing was fixed.

---

## 1. What the report actually reads (authoritative, from `assemble.py`)

`assemble.py` defines eleven run keys under `strains/eciML1515/outputs/`, and reads
**43 committed files** from them (20 figures, 20 tables, 1 `resolved_config.yaml` chosen by
`PROVENANCE_ORDER`, plus two files reached through `annotate_enzymes`). Every one of the 43
exists and is tracked; none is missing.

| run key | directory | files read | what the report gets from it |
|---|---|---|---|
| `sweep` | `sweep_default/` | 7 | TPC ensemble, sensitivity heatmap, descriptor distributions; `descriptors.csv`, `sensitivity_spearman.csv`, `summary.json` |
| `dltkcat` | `sweep_dltkcat_ext/` | 1 | `tpc_ensemble.png` (DLTKcat variant) |
| `calibrated` | `sweep_calibrated/` | 1 | **`resolved_config.yaml` only** — this is `PROVENANCE_ORDER[0]`, i.e. the config the supplementary prints |
| `proteome` | `proteome_sectors/` | 6 | sector fractions vs T (fig + csv), predicted-vs-measured usage and sector figures, `validation_correlations.csv` |
| `ablation` | `outputs/` (root) | 2 | `ablation_comparison.png`, `ablation_summary.csv` |
| `anatomy` | `anatomy/` | 4 | reference TPC, enzyme-parameter densities, example kcat(T), `resolved_config.yaml` |
| `valid_trust` | `validation/` | 3 | Van Derlinden validation curves, table, summary |
| `calibration_v3` | `calibration_vanderlinden/` | 4 | prior-vs-posterior TPC, corner plot, `demanded_corrections.csv`, `summary.json` |
| `elasticity_tuned` | `elasticity_tuned/` | 5 | tornado plots (rmax, CTmax), heatmap, `elasticity_table.csv`, `elasticity_bands.json` |
| `decompose_tuned` | `decompose_tuned/` | 5 | **the envelope/magnitude decomposition** — IQR bands, variance figure, `decomposition_variance.csv`, `decomposition_iqr_magnitude.csv`, `decompose_summary.json` |
| `control_tuned` | `control_tuned/` | 6 | thermal control + identifiability tables (raw and annotated), top enzymes, control bar figure |

**`assemble.py` also writes back into a committed strain output directory.** It imports and
runs `annotate_enzymes.main()`, which reads `control_tuned/thermal_control.csv` and
`identifiability.csv` plus the model SBML and `proteomics/tem_proteomic.csv`, and **writes**
`control_tuned/thermal_control_annotated.csv`, `identifiability_annotated.csv` and
`control_coefficient_bar.png` — three of the files `assemble.py` then reads. Assembling the
report therefore regenerates three committed files. It is a local identity join (gene /
protein names), not a model solve, but it means "assemble the report" is not a read-only act.

---

## 2. The two changes that date everything

| commit | date | what it changed |
|---|---|---|
| `a416fd1` | **2026-07-02 22:32** | medium-dependent sector allocation. Strain nominal re-grounded: **f_metab 0.285 → 0.483, f_maint 0.374 → 0.326**, `allocation_from_data` wired. N2 showed this moves eciML1515 T_opt 37 → 30 °C. |
| `8085036` | **2026-07-11 18:18** | closes four uncosted O2-sink reactions **by default**. Self-documented effect: "~−0.3 % growth; TPC essentially unchanged". Adds the key `close_free_o2_sinks`. |

Between them, three further commits change the model that produced these outputs:
`7ec248f` (2026-07-09, reconcile the two redundant enzyme pools into one budget),
`922e13d` (2026-07-09, coupled growth-law partition) and `2b6e8b4` (2026-07-09, free σ knob
scaling both sector caps).

---

## 3. Config validity — checked directly against the current config model

Six directories carry a `resolved_config.yaml`; **five carry none at all**, and no
`summary.json` in this tree embeds a config or provenance block, so for those five the only
provenance that exists is the git commit.

Committed config vs what `config.resolve("eciML1515")` produces today:

| directory | `f_metab` / `f_maint` | `allocation_from_data` | keys the current model has that it lacks | keys it sets that no longer exist |
|---|---|---|---|---|
| `sweep_default` | **0.285 / 0.374** | `null` | `close_free_o2_sinks`, `biosynthesis_growth_law`, `growth_law_slope`, `growth_law_f_bio0`, `default_medium_proteome` | `kind`, `sensitivity.*` (run-scoped, harmless) |
| `sweep_dltkcat_ext` | **0.285 / 0.374** | `null` | as above **+** `provider.dcp_from`, `dcp_prior_kJ`, `p_total`, `sigma` | as above |
| `sweep_calibrated` | **0.285 / 0.374** | set | as `sweep_dltkcat_ext` | as above **+** `envelope_sampling.*` |
| `proteome_sectors` | **0.285 / 0.374** | absolute path | as `sweep_dltkcat_ext` | none |
| `anatomy` | 0.483 / 0.326 | `proteomics/tem_proteomic.csv` | **`close_free_o2_sinks` only** | none |
| `validation`, `calibration_vanderlinden`, `elasticity_tuned`, `decompose_tuned`, `control_tuned` | — | — | **no `resolved_config.yaml`** | — |

Two further values differ from today's defaults in the four 2026-07-02 configs:
`provider.default_dCp` **−3.398 vs −4.0** and `provider.pool_scale` **0.9 vs 1.0**
(`sweep_default` keeps 1.0).

---

## 4. Classification

| directory | last content write | vs `a416fd1` | vs O2 closure `8085036` | `resolved_config` | **class** |
|---|---|---|---|---|---|
| `sweep_default` | `0957b33` 2026-07-02 | **BEFORE** | BEFORE | present, f_metab 0.285, allocation `null` | **SUSPECT** |
| `sweep_dltkcat_ext` | `5d6ce87` 2026-07-02 | **BEFORE** | BEFORE | present, 0.285 | **SUSPECT** |
| `sweep_calibrated` | `5d6ce87` 2026-07-02 | **BEFORE** | BEFORE | present, 0.285 | **SUSPECT — and it is the config the supplementary prints** |
| `proteome_sectors` | `aa2ef9f`/`ab7e9d9` 2026-07-02 | **BEFORE** | BEFORE | present, 0.285 | **SUSPECT** |
| `ablation_*` + `ablation_summary.csv` | `bdb9475`/`502b711` 2026-07-02 | **BEFORE** | BEFORE | **none** | **SUSPECT** |
| `anatomy` | `8ef4eaf` 2026-07-09 | AFTER | **BEFORE** | present, current grounding | **SUSPECT** (only the O2 closure separates it) |
| `validation` | `04c1ce4` 2026-07-09 (renamed at `8e6b703`) | AFTER | **BEFORE** | **none** | **SUSPECT** |
| `calibration_vanderlinden` | `8061dc9` 2026-07-09 (renamed at `8e6b703`) | AFTER | **BEFORE** | **none** | **SUSPECT / UNKNOWN** (emcee posterior; not cheaply testable) |
| `elasticity_tuned` | `17305e8` 2026-07-09 | AFTER | **BEFORE** | **none** | **SUSPECT** |
| `decompose_tuned` | `17305e8` 2026-07-09 | AFTER | **BEFORE** | **none** | **SUSPECT** |
| `control_tuned` | `b62fa25` 2026-07-11 20:15 | AFTER | **AFTER** | **none** | **UNKNOWN** — post-dates every known change, but records no config |

Nine of eleven directories predate at least one committed change that moves their numbers.
**`control_tuned` is the only directory written after every model change identified here**,
and it was regenerated for exactly that reason: `b62fa25` is titled "regenerate enzyme-control
analysis on the corrected (O2-closed) model", two hours after `8085036`.

That is the sharpest single finding in this table. **`decompose_tuned` and `elasticity_tuned`
were not regenerated at the same time**, although they sit at the same operating point
(`decompose_summary.json`: "rich (BHI), growth law ON, reconciled single pool; TUNED (v3
medians)") and share `17305e8` with the pre-regeneration control run. The numbers say the same:
`decompose_tuned` baseline `rmax` = 2.1609, `elasticity_tuned` median `rmax` = 2.1609,
`control_tuned` nominal `rmax` = 2.1558 — a −0.24 % offset, matching the O2 closure's
self-documented "~−0.3 % growth". So the control analysis is on the corrected model and the
decomposition and elasticity beside it in the report are on the uncorrected one.

**Not decided here:** whether that 0.24 % matters to any claim. It does not obviously move
T_opt (39 °C in all three) or CT_max (45.95 vs 45.97). The point of this task is that the
directories are *not from the same model state*, and nothing in the outputs says so.

## 5. What could not be established cheaply

* The five directories with no `resolved_config.yaml` cannot be validated by inspection at
  all — their configuration is not recorded anywhere. This is a **process gap**, not a
  finding about any specific number: `sweep`, `proteome-sectors` and `anatomy` write a
  resolved config; `validate`, `calibrate`, `elasticity`, `decompose` and `control` do not.
* Several commits after `a416fd1` touch shared modules while building other organisms
  (`3f45c94`, `c508e27`, `b55fa1f`, `0dcf9a1`, and the K1/K2 Candida work). Each was gated at
  the time ("mmrt gate: toy byte-identical" and similar), but whether any of them moved
  eciML1515 is not decidable by reading; only by re-running. That is TASK 3's job.
