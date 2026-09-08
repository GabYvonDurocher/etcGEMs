# `reports/ecoli_gasflux/` — the gas-exchange deliverable

> ## ✅ CONFIGURATIONS D, E AND F ARE NOW GATED AGAINST EXPERIMENT
>
> Parsa's respirometry arrived on 2026-09-08 and is ingested at
> `strains/eciML1515/respirometry/`. **All ten R² values his reports print reproduce here, the
> worst to 0.009** (P3 TASK 3, `reports/P3_gate/gate.md`):
>
> | | his growth R² | port | his respiration R² | port |
> |---|---|---|---|---|
> | **D** NLDM / LB | 0.71 / 0.90 | **0.707 / 0.896** | — | — |
> | **E** NLDM / LB | 0.85 / 0.83 | **0.849 / 0.828** | 0.72 / 0.81 | **0.721 / 0.801** |
> | **F** NLDM / LB | 0.91 / 0.88 | **0.905 / 0.881** | 0.96 / 0.85 | **0.964 / 0.852** |
>
> plus his fitted `C_max ≈ 510` on LB (port **509.9**) and `F_ETC ≈ 0.28–0.32` (port
> **0.282 / 0.284**). Configurations **A, B and C** remain gated at 60/60
> (`reports/P1_parsa_port/gate.md`). **So every configuration A–F is now reproduced here.**
>
> Four things had to be established before any of it matched, and each is a named cause in the
> gate table: the blanket NLDM medium his fits used, his O2-sink closure order (which matters
> once an ETC area constraint is present, where it did not for A–C), the parameter point
> (configuration D quotes the posterior median, E and F the MAP), and which of his similarly
> named runs each number came from. A fifth was a correction to P1: **his configuration F is
> configuration E's ETC table plus a non-electrogenic bd-II**, not the Bekker-turnover table
> P1 wired.
>
> Gated against the **pre-boundaryfix** data, which is what his figures used. Against the
> current data the R² values move by ≤ 0.021, all of it an improvement in NLDM growth.

> ### NLDM: the recipe medium is the baseline; the blanket medium is a sensitivity
>
> `NLDM` in these runs applies **recipe-proportional uptake ceilings** (each carbon component
> capped at `clearance × concentration`). That is canonical. `NLDM_blanket` — every component
> open at one generous bound — is a **labelled sensitivity**, kept only because Parsa's
> committed NLDM figures were produced with it before he changed his own code and did not
> re-run. Quote `NLDM`, not `NLDM_blanket`.
>
> It matters: on the canonical medium configuration C's NLDM respiratory quotient is **1.04**,
> not the ≈ 7–9 his report gives, so the high RQ was the unlimited medium and not the absent
> carbon cap. Full table in `reports/P2_settle/TASK2_nldm.md`. Provisional pending his
> confirmation.


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
