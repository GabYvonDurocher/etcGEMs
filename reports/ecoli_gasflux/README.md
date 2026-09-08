# `reports/ecoli_gasflux/` — the gas-exchange deliverable

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
