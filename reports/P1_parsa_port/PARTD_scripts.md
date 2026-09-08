# P1 PART D — what happened to each of Parsa's 72 scripts

The port's rule: a configuration is an **experiment overlay plus a CLI verb**, not a script.
`etcgem gasflux --strain eciML1515 --experiment gasflux_config{A..F}` replaces the six
per-configuration drivers outright, so most of the PORT-classified work became configuration
rather than code. What remains as a script is only what genuinely is one: the report builder.

## PORT (8 → 1 verb + 1 report builder)

| his script | what it did | where it went |
|---|---|---|
| `scripts_posterior_multimedia_tpc.py` | the shared operating point: `build_pm` (growth law on, static sectors, medium), `posterior_pert`, and the NLDM recipe | `calibration_multi.build_pm_medium`, `config.apply_gasflux`, `providers.set_medium_recipe`, `strains/eciML1515/media/NLDM_media.csv` |
| `scripts_posterior_mmrt_transport.py` | configuration A | `configs/experiments/gasflux_configA.yaml` + `gasflux.add_transport_costs` |
| `scripts_transport_kcat_sweep.py` | picked the carrier k_cat by sweeping 30/100/300 | the value is now `gas_exchange.transport_carrier.kcat_s` (strain) overridable per run; the sweep is a one-off and is not carried |
| `scripts_posterior_carboncap_gasflux.py` | configuration B | `gasflux_configB.yaml` + `gasflux.add_total_carbon_constraint` |
| `scripts_posterior_configC_acetate.py` | configuration C | `gasflux_configC.yaml` + `gasflux.add_acetate_line` |
| `scripts_configC_bd_bo3_sweep.py` | forced bd:bo3 ratios and swept them | not carried: the oxidase split is left FREE from configuration D on, which is the design the later configurations adopt |
| `scripts_configE_build.py` | built and demonstrated configuration E | `gasflux_configE.yaml` + `etc_area.py` + `strains/eciML1515/etc/complexes_szenk_merged_bd.csv` |
| `scripts_posterior_tpc.py` | posterior TPC vs the measured curve | already covered by `etcgem validate` / the existing report; not duplicated |

Figures for the new deliverable are built by **`scripts/gasflux_figures.py`**, writing into
`reports/ecoli_gasflux/assets/`, in the house Quarto convention.

## REPORT-BUILDER (17) — all dropped

Every `scripts/*.py` in his tree opens a Word `.docx` with `python-docx` and splices a section
into it: `add_bayesian_section`, `add_bd_bo3_section`, `add_configC`, `add_configD_capdesc`,
`add_configD_section`, `add_configE_bayesian`, `add_configE_section`, `add_configF_flatprior`,
`add_configF_section`, `add_growthonly_finale`, `add_methods_and_c180`,
`add_nldm_and_capdefence`, `add_o2sink_detail`, `build_config_summary`,
`build_posterior_report`, `label_configAB`, `rework_configF_section`.

Dropped as a class, not individually: this repository renders reports from `report.qmd` +
`assemble.py`, and a chain of seventeen scripts that mutate a binary document in place cannot
be reviewed, diffed or re-run from scratch — which is why his `outputs_reports/` carries
sixteen `.bak` copies of the same file. **His prose is the source for the new report's text**;
his tooling is not.

## ONE-OFF / SCRATCH (47) — dropped, with the reason

**`scratchpad_*.py` (9)** — session scratch, so labelled by his own manifest:
`band`, `capband`, `cmp_medium`, `feasible`, `fva`, `gasflux60`, `medium_check`,
`nldm_carbon`, `sens`. Two of them record findings worth keeping and they are kept as *facts*
in this report rather than as code: `scratchpad_fva.py` (the FVA determinacy check, whose
~9 mmol span is a gate quantity) and `scratchpad_cmp_medium.py` (blanket vs recipe medium —
the comparison that turned out to explain his NLDM numbers, DECISIONS D5).

**Configuration-D figure and diagnostic variants (12)** — `configD_2med_growth_fig`,
`configD_LB_full_fig`, `configD_NLDM_full_fig`, `configD_growth_fig_gen`,
`configD_nocap_growth_fig`, `configD_posterior_report`, `configD_prior_vs_posterior`,
`configD_replot`, `configD_uncapped_growth_2panel`, `configD_vs_experiment`,
`configD_vs_experiment_respiration`, `posterior_configD_recalib`. Each plots one calibration
run; nine of them read the R2A CSV that is not in the snapshot, so they cannot run at all here.

**Configuration-D model variants (3)** — `posterior_configD_capfit`,
`posterior_configD_multimedia`, `posterior_configD_proteome`: forward checks of the same
mechanism at different settings, now a matter of editing `c_max` in the overlay.

**Configuration-E diagnostics (7)** — `configE_capacity_diag`, `configE_cmax_compare`,
`configE_disc_slice`, `configE_fig`, `configE_plateau_test`, `configE_resp_growth`,
`configE_sigma_test`, `configE_tm_range_test`: forward tests and posterior figures around one
fit ("what caps LB growth?", "does raising sigma fix the plateau?"). Diagnostics of a
calibration we cannot reproduce; their questions are recorded in `gate.md`, their code is not.

**Configuration-F variants (12)** — `configF_acetate_calib`, `configF_acetate_fig`,
`configF_acetate_slope_sweep`, `configF_acetate_test`, `configF_flatprior_check`,
`configF_flatprior_combined`, `configF_lb_0Honly`, `configF_nldm_0Honly`,
`configF_nldm_condfit`, `configF_slope_corrected`, `configF_summary_fig`, `configF_test`:
conditional and profile fits, prior-independence checks and figure variants around the same
one-line correction that is now a table column.

**Growth-only figure scripts (2)** — `scripts_LB_growthonly_fig`, `scripts_NLDM_growthonly_fig`:
undocumented plot scripts reading the missing R2A CSV.

**Two structural findings from the dropped set are kept as findings**, in `gate.md`: that
configuration A is fermentative at his own carrier turnover (so the route was abandoned), and
that the acetate SLOPE is structurally unattainable in this model (~85–140 against Basan's 21)
— his `calibration_configD` docstring records this as shown exhaustively, and it is the reason
only the threshold is ever fitted.
