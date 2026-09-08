# `reports/ecoli_gasflux/` — the gas-exchange deliverable

> ## ⚠ CONFIGURATIONS D, E AND F ARE PORTED BUT **NOT VALIDATED AGAINST EXPERIMENT**
>
> **Ported ≠ verified.** Configurations **A, B and C** are gated: they reproduce Parsa's
> committed numbers in 60 of 60 comparisons, T_opt exactly and everything else within
> 1 × 10⁻³ relative (`reports/P1_parsa_port/gate.md`). **Configurations D, E and F have been
> ported and they run, and nothing about their fit to data has been checked here.** The growth
> and respiration R² values his report quotes for them — D 0.71/0.90, E 0.85/0.83 and
> 0.72/0.81, F 0.91/0.88 and 0.96/0.85, and the fitted F_ETC ≈ 0.28–0.32 and LB C_max ≈ 510 —
> are **his numbers, not reproduced here**, and must not be quoted as though they were.
>
> **What is missing:** `derived_N0_R_results_with_carbon.csv`, the E. coli R2A / LB growth and
> per-cell respirometry from `Presense_Analysis/Ecoli_R2A_LB`. Every D/E/F likelihood and every
> "vs experiment" figure reads it from `C:\Users\Parsa\Desktop\...`; it exists only on
> Parsa Amirmoeini's machine and a search of the whole 1.0 GB snapshot he supplied finds no copy.
> It has been requested.
>
> **What will be run when it lands:** a joint growth + per-cell-respiration fit per medium
> using `calibration_multi.build_overflow_specs()` (the v3 lever set plus the fitted
> `C_max_mult`), `build_pm_medium()` for the medium, and `gasflux.overflow_threshold()` for the
> overflow term — all three already in place, so no second calibrator is needed. Cost, from his
> own `summary.json` for the v3 run of the same shape: 60 walkers × 6000 steps, ≈ 4 h 28 min on
> 10 processes, per fit. The result then goes through `reports/P1_parsa_port/gate.py` beside
> configurations A–C.
>
> Until then: **A, B, C — gated. D, E, F — ported, ungated.**


A new deliverable directory in the house convention (`reports/<organism>_<topic>/`), created by
P1 for Parsa's gas-exchange and overflow work on *E. coli*.

**Status: assets only.** P1 ported the mechanisms, the configurations and the gate; it did not
write the paper. What is here is the figure builder's output plus the gate that says which of
the source numbers reproduce.

* `assets/figures/` — built by `python scripts/gasflux_figures.py --strain eciML1515
  --experiments gasflux_configA gasflux_configB gasflux_configC` from the runs of
  `etcgem gasflux --strain eciML1515 --experiment gasflux_config{A..F}`.
* the port, the gate and what does and does not reproduce: `reports/P1_parsa_port/`.
* Parsa's own prose for configurations A–F is in
  `$PARSA_ROOT/outputs_reports/etcgem3_configuration_summary.pdf`; it is the source text for
  this report when it is written. His `outputs_reports/` (and its sixteen `.bak` Word files)
  is deliberately not imported — see P1 PART G.

When the report is written it follows the convention: `report.qmd` + `assemble.py`, rendering
from committed outputs under `strains/eciML1515/outputs/gasflux_*`.
