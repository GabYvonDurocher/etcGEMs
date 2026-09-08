# P1 PART A — inventory of Parsa's snapshot, and the fork point

`$PARSA_ROOT` = `/Users/g.yvon-durocher/Downloads/etcGEMs-main_3` (1.0 GB, a plain directory,
not a git repository). Read only throughout; nothing in it was modified.

---

## 1. The fork point — verified, and narrower than assumed

Every `.py` in his `src/etcgem` that also exists here was hashed and searched against this
repository's whole history. **All 21 shared modules are exact ancestors** — he modified no core
module. The prompt's five stated matches are confirmed, and the other sixteen resolve too:

| module | last commit that produced his content |
|---|---|
| `config.py`, `enzyme_cost.py`, `sectors.py`, `tpc.py` | `2b6e8b4` 2026-07-09 |
| `calibration_multi.py` | `4620c9f` 2026-07-09 |
| `providers.py` | `7ec248f` 2026-07-09 |
| `cli.py`, `dissect.py` | `e67b4c0` 2026-07-09 |
| `control.py` | `f1caa66` | `unfolding.py` | `cf9db9c` | `validation.py` | `04c1ce4` |
| `plotting.py` `5f4f195`, `calibration.py` `5e7f98a`, `decomposition.py` `b164d29`, `sensitivity.py` `2e27335`, `proteome_alloc.py` `27cafef`, `dltkcat.py` `cf1994f`, `thermal_sampling.py`/`__init__.py` `f5c9456`, `mmrt.py`/`__main__.py` `502b075` | |

Rather than infer the fork point from the newest module, I checked which commits on `main`
have a `src/etcgem` tree **byte-identical to his**. There are exactly eleven, consecutively:

* **first** `e67b4c0` — 2026-07-09 21:00:51
* **last** `8c2c30f` — 2026-07-10 21:55:56
* **first divergence** `99eab16` — 2026-07-10 21:58:06 (the config consolidation)

So his fork point lies in that 25-hour window. He recalls 7 July; the content says **on or
after the evening of 9 July, and before 21:58 on 10 July** — most likely 10 July, since his
tree also carries `configs/example_gecko.yaml` and `configs/toy.yaml`, added in that window.
He is missing four modules added since (`transfer.py`, `sink_audit.py`, `ea_dissection.py`,
`sharpe_schoolfield.py`).

### One correction to the prompt's premises

The prompt says his baseline "predates `a416fd1` (the sector re-grounding that moved E. coli's
nominal T_opt 37 → 30 °C)". **It does not.** `a416fd1` is 2026-07-02, a week before his fork,
and **his `strains/eciML1515/strain.yaml` is byte-identical to ours today**, `f_metab: 0.483`
included. Every file under `strains/eciML1515/{dltkcat,media,model,proteomics,thermal}` is
byte-identical to ours as well. So `a416fd1` cannot explain any movement in his numbers, and
it is struck from the attribution list before the gate is run. The reconciliations that do
apply are `99eab16` (layout), `8e6b703` (output-directory renames) and `8085036` (the O2-sink
closure) — plus everything on `main` since 10 July.

**His v3 posterior is our v3 posterior, exactly.** All thirteen posterior medians in his
`calibration_vanderlinden_v3/summary.json` match our `calibration_vanderlinden/summary.json`
to every stored digit, same sampler settings, same wall time (16 118 s). The gate can therefore
use our committed posterior and any movement is attributable to code, not to a different fit.

### The one place his snapshot still differs structurally

* `strains/eciML1515/config.yaml` — the per-strain config `99eab16` deleted. It is dead in his
  tree too (his `config.py` reads `strain.yaml`), but it records different values (`pool_scale:
  0.9`, grid 8–60 °C n=53) from the live `strain.yaml` (1.0, 5–60 n=56). Anything that reads it
  would be wrong; nothing does.
* his root `defaults.yaml` = our `configs/defaults.yaml` **minus `close_free_o2_sinks: true`** —
  the direct evidence that his runs predate `8085036` and used his own closure.

---

## 2. What he adds

### 2.1 Five new source modules

| module | what it is |
|---|---|
| `gasflux.py` | exchange-flux TPCs (`flux_tpc`), `add_total_carbon_constraint`, `add_acetate_line`, `respiratory_quotient`, `add_transport_costs`, **and `block_free_o2_sinks` + `FREE_O2_SINKS`** — the duplicate of `8085036` |
| `configE.py` | the ETC membrane-area constraint, with `ETC_COMPLEXES` (Szenk-2017 footprints, turnovers, eciML1515 reaction IDs) as a module constant |
| `configF.py` | imports `configE`, redefines the same dict as `ETC_COMPLEXES_F` with the bd oxidases split and measured turnovers, plus `set_bdII_nonelectrogenic` and `BDII_RXNS` |
| `calibration_configD.py` | joint Bayesian fit: R2A growth TPC + Basan's overflow threshold, on `calibration_multi`'s `PSpec`/`to_pert`/`log_prior`/`init_walkers` |
| `calibration_configD_full.py` | the same, extended to joint growth **+ per-cell respiration** over media |

### 2.2 Scripts — 72, classified

| class | n | what |
|---|---|---|
| **PORT** | 8 | the canonical driver of each configuration (below) |
| **ONE-OFF / SCRATCH** | 47 | 9 `scratchpad_*.py` + 38 `scripts_*` that are diagnostics, forward-tests, re-plots or figure variants |
| **REPORT-BUILDER** | 17 | every `scripts/*.py`; all of them edit a Word `.docx` with `python-docx` |

**PORT (8).** `scripts_posterior_multimedia_tpc.py` (the shared operating point: `build_pm`,
`posterior_pert`, and the NLDM recipe), `scripts_posterior_tpc.py` (posterior TPC vs the
measured curve), `scripts_posterior_mmrt_transport.py` (**A**),
`scripts_transport_kcat_sweep.py` (A's kcat choice), `scripts_posterior_carboncap_gasflux.py`
(**B**), `scripts_posterior_configC_acetate.py` (**C**), `scripts_configC_bd_bo3_sweep.py` (C's
oxidase sweep), `scripts_configE_build.py` (**E**).

**REPORT-BUILDER (17), all dropped.** `scripts/add_*.py` (13), `scripts/build_config_summary.py`,
`scripts/build_posterior_report.py`, `scripts/label_configAB.py`,
`scripts/rework_configF_section.py`. Each opens `outputs_reports/*.docx` and splices a section
into it. This repository's convention is Quarto (`report.qmd` + `assemble.py`), so they are
replaced rather than ported; his prose is the source for the new report's text.

**ONE-OFF / SCRATCH (47), dropped, one line each** — see `PARTD_scripts.md`.

### 2.3 A blocking data gap

`calibration_configD.py` reads
`C:\Users\Parsa\Desktop\Presense_Analysis\Ecoli_R2A_LB\tables\derived_N0_R_results_with_carbon.csv`,
and eight further scripts read the same path. **That file is not in the snapshot** — a search
of the whole 1.0 GB tree finds no R2A / Presense / derived_N0 data. Every configuration-D, E
and F *fit* and every "vs experiment" figure therefore depends on measurements we do not hold.
Consequence for the gate: **their R² values cannot be reproduced here at all**, independently
of the no-emcee rule.

Conversely, **every input file his configs need that does exist is already in this
repository**, byte-identical. Nothing needs importing from his tree (PART G).

---

## 3. The gate list — the numbers his own reports print

From `outputs_reports/etcgem3_configuration_summary.pdf` (text extracted with `pdftotext`) and,
where a figure quotes a computed value, from the CSV behind it in
`strains/eciML1515/outputs/<dir>/`.

| # | quantity | his value | source | cheap to check? |
|---|---|---|---|---|
| 1 | baseline growth R² vs the reference TPC | 0.96 | summary PDF, "The baseline model" | calibration — no |
| 2 | **A**: transporter turnover used | k_cat = 300 s⁻¹ | summary PDF, Config A | yes (a run setting) |
| 3 | **A**: respiratory quotient | RQ ≈ 0 (fermentative) | summary PDF + `posterior_mmrt_transport/mmrt_transport_kcat300.csv` | **yes** |
| 4 | **A**: glucose CO₂ FVA span | ≈ 9 mmol gDW⁻¹ h⁻¹ | summary PDF, Config A | yes (one FVA) |
| 5 | **B**: RQ at each medium's optimum, C_max = 60 | glucose **1.07**, NLDM **0.90**, LB **0.99**, BHI **1.00** | summary PDF Fig. B2 + `posterior_carboncap/gasflux_C60.csv` | **yes** |
| 6 | **B**: growth at the cap | ≈ 90 % of the uncapped optimum | summary PDF, Config B | **yes** |
| 7 | **C**: Basan line parameters | s_ac = 21 mmol gDW⁻¹ h⁻¹, λ_ac = 0.76 h⁻¹ | `gasflux.add_acetate_line` defaults; Basan 2015 Fig. 1 | inputs, not outputs |
| 8 | **C**: r_max under the acetate line | NLDM **2.27** h⁻¹; LB/BHI **2.13** h⁻¹ | summary PDF, Config C | **yes** |
| 9 | **C**: RQ under the acetate line | NLDM ≈ 7–9, glucose ≈ 0 | summary PDF + `posterior_configC/configC_acetate.csv` | **yes** |
| 10 | **D**: NLDM growth R² / respiration scale | 0.71 / ≈ 3.4 | summary PDF, Config D | emcee **and** missing data — no |
| 11 | **D**: LB growth R² / respiration scale | 0.90 / ≈ 3.6 | summary PDF, Config D | no |
| 12 | **E**: NLDM growth R² / respiration R² | 0.85 / 0.72 | summary PDF, Config E | no |
| 13 | **E**: LB growth R² / respiration R² | 0.83 / 0.81 | summary PDF, Config E | no |
| 14 | **E**: fitted membrane fraction | F_ETC ≈ 0.28–0.32 (Szenk's measured 0.316) | summary PDF, Config E | no (fit); the *nominal* 0.316 budget is checkable |
| 15 | **F**: NLDM growth R² / respiration R² | 0.91 / 0.96 | summary PDF, Config F | no |
| 16 | **F**: LB growth R² / respiration R² | 0.88 / 0.85 | summary PDF, Config F | no |
| 17 | **F**: LB fitted carbon cap | C_max ≈ 510 | summary PDF, Config F | no |
| 18 | posterior multimedia r_max / T_opt per medium | `posterior_multimedia/posterior_multimedia.csv` (91 × 4) | his own CSV | **yes** |

Items 2–9 and 18 are the PART E gate. Items 1 and 10–17 are listed with their cost in
`gate.md` and left for a human.
