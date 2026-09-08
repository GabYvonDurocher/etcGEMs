# N3 TASK 3 — escalating what TASK 1 flagged, cheaply

Every SUSPECT/UNKNOWN directory from TASK 1, the cheapest test that would settle it, and the
outcome. **Nothing was regenerated.** Two tests had to run a command that writes into the
strain's output tree; in both cases the tree was restored immediately afterwards and verified
clean against `git status` (D7).

## The tests

| test | what it does | writes |
|---|---|---|
| **config replay** (`probes/replay_config.py`) | loads a directory's own committed `resolved_config.yaml`, builds the provider with **today's** code, computes the nominal TPC on the config's own grid, compares with the `nominal_tpc.csv` committed beside it | nothing |
| **tuned-point rebuild** (`probes/tuned_cap_probe.py`, TASK 2) | rebuilds `calibration_multi._build_pm_rich` with the tuned medians recorded in `decompose_summary.json` | nothing |
| **command re-run + restore** | runs the actual CLI verb, diffs, then `git checkout --` | restored |
| **recompute in-process** | calls the module function directly | nothing |

## Outcomes

| directory | test | outcome |
|---|---|---|
| `control_tuned` | tuned-point rebuild | **REPRODUCES.** Committed nominal `rmax` 2.1557849 = rebuilt 2.1557849, seven decimal places. **CONSISTENT** |
| `proteome_sectors` — `sector_fractions_vs_T.csv` / `.png` | recompute in-process | **REPRODUCES.** Max abs difference 0.0 (5.6e-17 before rounding). This table is a pure function of the proteomics file and the model's protein list; no model change can touch it |
| `anatomy` — `resolved_config.yaml` | config replay | **REPRODUCES today's model exactly**: `rmax` 0.5429018962625, T_opt 31.0 — identical to the strain's current committed `outputs/tpc` |
| `anatomy` — the three figures | dated, not re-rendered | **STALE.** Rendered 2026-07-09 (`8ef4eaf`), before the O2 closure `8085036`. Per N2's bisection the nominal `rmax` at that state was 0.5511 against today's 0.5429, so `reference_tpc.png` plots a curve ~1.5 % high |
| `validation` | `etcgem validate` (writes to `validation_trusted/`, which the rename at `8e6b703` left as a *different* directory from the committed `validation/`) | **DOES NOT REPRODUCE, marginally.** `abs_R2` 0.265 → 0.258, RMSE 0.705 → 0.708, `pred_rmax` 1.037 → 1.035, `pred_Ea` 0.630 → 0.642. T_opt (40.5) and CT_max (51.5) unchanged |
| `proteome_sectors` — `validation_correlations.csv` | command re-run + restore | **DOES NOT REPRODUCE.** The matched enzyme count changes (16 °C: n 178 → 191; 43 °C: 213 → 189) and the log-Pearson R² changes by 2–20×: 25 °C **0.0018 → 0.0847**, 30 °C **0.0055 → 0.1273**, 16 °C 0.0442 → 0.1036. Spearman ρ moves little (≤ 0.06) |
| `decompose_tuned` | tuned-point rebuild | **DOES NOT REPRODUCE.** Baseline `rmax` 2.1608622 committed vs 2.1557849 today (**−0.235 %**); `CTmin` 13.899 → 14.160 °C, niche 32.070 → 31.809 °C, `B80` 13.697 → 13.076 (**−4.5 %**), skewness −0.5048 → −0.5268. T_opt (39.0) and CT_max (45.969) unchanged. Cause established: the O2-sink closure `8085036`, whose own commit message predicts "~−0.3 % growth" |
| `elasticity_tuned` | same rebuild (its `median_descriptors` are the same baseline: `rmax` 2.1608622) | **DOES NOT REPRODUCE**, same offset, same cause |
| `sweep_default` — nominal | config replay | **DOES NOT REPRODUCE.** `rmax` 0.323608 → 0.317942 (−1.75 %), `CTmin` 10.521 → 10.702, `Ea` 0.9981 → 1.0056. T_opt 31.0 unchanged |
| `sweep_dltkcat_ext` — nominal | config replay | **DOES NOT REPRODUCE, and the headline descriptor moves: T_opt 37.0 → 31.0 °C.** `rmax` 0.4306 → 0.4134 (−4.0 %) |
| `sweep_calibrated` — nominal | config replay | **DOES NOT REPRODUCE, badly. T_opt 37.0 → 30.0 °C, `rmax` 0.4542 → 0.2314 (−49 %)**, `CTmin` 8.54 → 5.0, niche 38.30 → 42.21. This is the directory whose `resolved_config.yaml` `PROVENANCE_ORDER` selects for the supplementary |
| `ablation_complete` | committed values vs today's complete model | **DOES NOT REPRODUCE.** Committed T_opt 37.0 / `rmax` 0.454; today's complete model is 31.0 / 0.5429. The committed value carries the pre-`a416fd1` T_opt-37 signature |
| `ablation_mmrt`, `ablation_sectors_off`, `ablation_sectors_Tindep` | — | **NOT CHEAPLY TESTABLE.** No config is recorded for any of them and no ablation harness is committed (`bdb9475` changed only experiment YAMLs). All three carry the same 2026-07-02 date and the same T_opt 37/40 signature |
| `sweep_default` / `sweep_dltkcat_ext` — the **120-sample ensembles** (the figures and tables the report actually shows: `tpc_ensemble.png`, `descriptor_distributions.png`, `sensitivity_heatmap.png`, `descriptors.csv`, `sensitivity_spearman.csv`) | — | **NOT CHEAPLY TESTABLE.** 120 LHS samples × 56 temperatures ≈ 2 h single-process each. The nominal member of each ensemble was tested instead and fails, above |
| `calibration_vanderlinden` | — | **STOPPED — for a human.** Settling it means re-running the emcee calibration. The committed `summary.json` records the cost exactly: 60 walkers × 6000 steps, **wall time 16 118 s = 4 h 28 min on 10 processes**, acceptance 0.295, autocorr 321, n_eff 1000. That is not a decision to take unattended |

## Tally

**Reproduces: 3** — `control_tuned`; `proteome_sectors/sector_fractions_vs_T`; the `anatomy`
config. **Does not reproduce: 8** — `decompose_tuned`, `elasticity_tuned`, `validation`,
`proteome_sectors/validation_correlations`, `sweep_default`, `sweep_dltkcat_ext`,
`sweep_calibrated`, `ablation_complete` (plus the `anatomy` figures, stale by date).
**Not cheaply testable: 3** — the two sweep ensembles, the three other ablation variants.
**Stopped for a human: 1** — `calibration_vanderlinden`, 4 h 28 min of emcee.

Nothing has been regenerated. Every failing directory is listed with its evidence, and the
cause is established for the two largest groups: `a416fd1` (the 2026-07-02 directories, T_opt
37 → 30/31) and `8085036` (the 2026-07-09 directories, −0.235 % on r_max).
