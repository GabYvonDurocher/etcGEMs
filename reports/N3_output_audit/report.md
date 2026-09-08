# N3 — the committed outputs the E. coli report renders from

**What this is.** N2 established that this repository can commit an output its own code does
not produce: `strains/eciML1515/outputs/tpc/descriptors.json` was already stale at the moment
it was committed. That file is read by no report. The eleven directories
`reports/ecoli_tpc/assemble.py` renders the paper from had never been checked. They have now.

**The result is not clean.** Of the eleven, **three reproduce, eight do not, three are not
cheaply testable, and one was stopped and costed for a human.** Nothing has been regenerated;
every failure is listed with its evidence and, for the two large groups, its cause.

Detail: [TASK1_output_audit.md](TASK1_output_audit.md) (what is read, and its provenance),
[TASK2_cap_regime.md](TASK2_cap_regime.md) (the cap-regime test),
[TASK3_escalation.md](TASK3_escalation.md) (the reproduction tests),
[DECISIONS.md](DECISIONS.md) (every judgement call). Probes and their outputs are in
[`probes/`](probes/).

---

## 1. What the report reads

`assemble.py` reads **43 committed files from 11 directories** under
`strains/eciML1515/outputs/`. All 43 exist and are tracked; none is missing. It is also not
read-only: it runs `annotate_enzymes.main()`, which **writes** three of the files it then
reads (`control_tuned/thermal_control_annotated.csv`, `identifiability_annotated.csv`,
`control_coefficient_bar.png`).

## 2. The audit, in one table

| directory | what the report takes | reproduces today? | evidence |
|---|---|---|---|
| `control_tuned` | thermal control + identifiability tables, control bar figure | **YES** | rebuilt nominal `rmax` 2.1557849 = committed, 7 d.p. |
| `proteome_sectors` → `sector_fractions_vs_T` | sector-fraction figure + table | **YES** | max abs diff 0.0 |
| `anatomy` → `resolved_config.yaml` | supplementary provenance | **YES** (config) | replays to the strain's current TPC exactly |
| `anatomy` → 3 figures | reference TPC, enzyme densities, example kcat(T) | **no** (by date) | rendered `8ef4eaf` 2026-07-09, before `8085036`; plots `rmax` ≈ 0.5511 vs today's 0.5429 |
| `validation` | Van Derlinden curves, table, summary | **no**, marginally | `abs_R2` 0.265 → 0.258, `pred_Ea` 0.630 → 0.642 |
| `proteome_sectors` → `validation_correlations.csv` | predicted-vs-measured usage correlations | **no** | log-Pearson R² 0.0018 → 0.0847 (25 °C), 0.0055 → 0.1273 (30 °C); n 178 → 191 |
| `decompose_tuned` | **the envelope/magnitude decomposition** | **no** | baseline `rmax` −0.235 %, `B80` −4.5 %, `CTmin` +0.26 °C |
| `elasticity_tuned` | tornado plots, elasticity table | **no** | same baseline, same offset |
| `sweep_default` | TPC ensemble, sensitivity heatmap, descriptor tables | **no** (nominal tested) | `rmax` 0.3236 → 0.3179 |
| `sweep_dltkcat_ext` | DLTKcat ensemble figure | **no** (nominal tested) | **T_opt 37.0 → 31.0 °C** |
| `sweep_calibrated` | **the `resolved_config.yaml` the supplementary prints** | **no** (nominal tested) | **T_opt 37.0 → 30.0 °C, `rmax` −49 %** |
| `ablation_*` | ablation figure + summary table | **no** (`complete` tested) | committed T_opt 37.0 / 0.454 vs today's 31.0 / 0.5429 |
| `calibration_vanderlinden` | prior-vs-posterior, corner, corrections | **STOPPED** | settling it = 4 h 28 min of emcee |

## 3. The two causes

**`a416fd1` (2026-07-02 22:32) — the sector re-grounding.** `f_metab` 0.285 → 0.483,
`f_maint` 0.374 → 0.326, medium-matched allocation wired. Five directories were written
*before* it and still record the old fractions in their own `resolved_config.yaml`:
`sweep_default`, `sweep_dltkcat_ext`, `sweep_calibrated`, `proteome_sectors`, and the
`ablation_*` set. This is the change N2 traced T_opt 37 → 30 °C to, and it is visible in the
replays above.

**`8085036` (2026-07-11 18:18) — the O2-sink closure.** Four uncosted O2-consuming reactions
closed by default; the commit predicts "~−0.3 % growth; TPC essentially unchanged". Four
directories were written on 2026-07-09, before it: `anatomy`, `validation`,
`calibration_vanderlinden`, `elasticity_tuned`, `decompose_tuned`.

**The sharpest single fact in the audit.** `control_tuned` was regenerated for that closure
two hours later (`b62fa25`, "regenerate enzyme-control analysis on the corrected (O2-closed)
model"). `decompose_tuned` and `elasticity_tuned`, at the *same* operating point and
previously written by the *same* commit, were not. The numbers confirm it exactly: rebuilding
the tuned point today gives `rmax` 2.1557849 — `control_tuned`'s committed value to seven
decimal places, and 0.235 % below the 2.1608622 that `decompose_tuned` and `elasticity_tuned`
both record. **The decomposition and the control analysis printed beside each other in the
report are from different model states, and nothing in the outputs says so.**

## 4. The provenance gap underneath all of this

**Five of the eleven directories carry no `resolved_config.yaml`**, and no `summary.json` in
this tree embeds a config: `validation`, `calibration_vanderlinden`, `elasticity_tuned`,
`decompose_tuned`, `control_tuned`. Their configuration exists only as a git commit. `sweep`,
`proteome-sectors` and `anatomy` write one; `validate`, `calibrate`, `elasticity`,
`decompose`, `control` and `dissect` do not. That is why `decompose_tuned` had to be
reconstructed from `calibration_multi._build_pm_rich` plus the medians incidentally recorded
in `decompose_summary.json`, rather than simply replayed.

Two commands have also drifted away from the directories they made: `etcgem validate` writes
to `outputs/validation_trusted/` while the report reads `outputs/validation/`, and `etcgem
dissect` still looks for `outputs/calibration_vanderlinden_v3/` — both renamed at `8e6b703`
without updating the code. `dissect` therefore does not run at all on a fresh clone.

## 5. The cap-regime question

Tested directly (TASK 2). The hypothesis — that the old T_opt of 37 °C was a cap-limited
plateau edge — **is wrong**: the plateau was 1.0 °C wide, and the cap binds at T_opt in the
current state too. What is true is sharper. In **both** nominal states growth over the
cap-binding range equals `cap_ub / translation_coeff` to five digits, so the top of the
nominal curve is allocation-determined: before, T_opt 37 °C is the *argmax* of the measured
f_bio(T) ceiling; now, T_opt 31 °C is the *crossover* where the rising envelope-limited branch
meets the falling ceiling. The 7 °C shift is a change in which feature of the allocation curve
sets the optimum — a regime change a local ±20 % decomposition cannot see.

The report's φ_envelope = 0.999 for T_opt is measured at neither of those points: at the tuned
rich operating point the cap has slack at **every one of 48 temperatures** and the metabolic
pool binds instead, so that attribution is already in the cap-free regime. It is still
regime-*conditional*, and the report did not say so; one caveat sentence has been added to
`reports/ecoli_tpc/report.qmd`. The decomposition itself has not been restated or recomputed.
`report.qmd` has **not** been re-rendered, so `report.tex` / the PDF are one sentence behind.

A new artefact was found on the way and is recorded, not fixed: the Glucose proteome has
measurements at 25/30/37 °C only, so the allocation — and with it the cap — is constant outside
that range. Current nominal growth is **exactly** 0.524757 /h from 37 to 44 °C, an 8 °C
dead-flat shoulder at 96.7 % of r_max, produced by the data table running out. N1's
`sector_cap_risk()` does not fire on it (it asks whether `allocation_from_data` is *absent*),
and at the tuned point that guard *does* fire while the cap never binds. The guard's condition
is neither necessary nor sufficient; the direct test is whether the cap binds and whether its
ceiling is flat where it does.

## 6. What a reader of `reports/ecoli_tpc/` should currently believe

**The report's qualitative structure is not in question here, and nothing in this audit
contradicts a scientific claim.** T_opt, CT_max and the shape of the curve are stable across
every reproduction test: T_opt is 39.0 °C at the tuned point in both the committed and the
rebuilt curve, CT_max 45.969 in both, and where descriptors move they move by fractions of a
degree or a few per cent. What has changed underneath is the model's *height* and its cold
limb.

Concretely, a reader should believe:

* **The tuned-model analyses** (decomposition, elasticity, control) describe the model at
  T_opt 39 °C, and the control analysis is on the current model while the decomposition and
  elasticity are 0.235 % of r_max behind it, with `B80` 4.5 % out. The Shapley *shares* are
  not measured here and are not claimed to have moved.
* **The a-priori sweep results, the ablation table and the proteome usage correlations** are
  from the pre-`a416fd1` model. Their headline T_opt of 37 °C is **not** what this model
  produces today; today it is 31 °C. Anything that leans on the 37 °C figure or on the
  ablation R² ordering should be re-derived before publication.
* **The sector-fraction figure and table** are measurement, not model output, and are exact.
* **The supplementary's `resolved_config.yaml`** describes `sweep_calibrated` — a 2026-07-02
  run that today reproduces neither its T_opt (37 → 30 °C) nor its r_max (−49 %) — and so does
  not describe most of the figures printed beside it.
* **The calibration posterior** is untested. It defines the tuned operating point, so if it
  has moved, all three tuned analyses inherit that independently of the O2 closure. Settling it
  costs 4 h 28 min of emcee and is a human's call.

## 7. What was changed by N3

Documentation and one caveat sentence, as the prompt allowed:

* `reports/ecoli_tpc/report.qmd` — one caveat sentence on the φ_envelope = 0.999 bullet.
* `README.md` — the "default on means default on where it works" limitation promoted out of
  N2's decision log; and the now-false claim that `strains/eciML1515/outputs/tpc/` "no longer
  reproduces" corrected, since N2 regenerated it and TASK 0 verified it.
* `reports/N3_output_audit/` — this report and its supporting notes and probes.

Plus one code hotfix on `main`, before the merge was pushed, recorded in DECISIONS D1–D3: the
N2 rescaling default broke `etcgem tpc` outright for every gecko-provider strain with sectors,
and `cli.main` returned the output path into `sys.exit()` so every successful run exited 1.
Neither moves a committed number; both are verified byte-identical against what was committed.

**No committed output was regenerated. No scientific conclusion was altered.**
