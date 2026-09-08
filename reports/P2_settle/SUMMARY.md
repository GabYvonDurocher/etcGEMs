# P2 — summary

| task | status | one line |
|---|---|---|
| **0** — merge P1, D/E/F marked ungated | **DONE** | Merged `bb25be5`; the ungated notice is at the top of the report and on the three overlays |
| **1** — the transporter k_cat | **DONE (provisional)** | 300 s⁻¹ reproduces his figure, 30 does not; 300 set in the strain data |
| **2** — NLDM under recipe ceilings | **DONE (provisional)** | The 1.2 % is the medium, to machine precision; and one of his claims changes |
| **3** — c_max provenance | **DONE** | No justification for 60 anywhere; 60 sits past the steepest part of the slope |
| **4** — provenance stamps | **DONE** | Nine reports stamped, generated not hand-written, `--check` enforced |
| **5** — the three owed annotations | **DONE** | All three in `reports/ecoli_tpc/`, plus the general rule in `docs/` |

Detail: [TASK2_nldm.md](TASK2_nldm.md), [TASK3_cmax.md](TASK3_cmax.md),
[DECISIONS.md](DECISIONS.md) (D0–D5). **TASKS 1 and 2 are PROVISIONAL pending Parsa's
confirmation** — they establish what his committed figures were made with, which is not the
same as what he intends.

---

## TASK 0 — merged, and the ungated status made impossible to miss

Merge commit **`bb25be5`** on `main` (`--no-ff`), then **`cd9ef9b`** adding the notice; pushed;
PR #4 closed as merged; branch deleted.

The notice sits at the **top** of `reports/ecoli_gasflux/README.md` and as a five-line banner on
`gasflux_config{D,E,F}.yaml`:

> **A, B, C — gated. D, E, F — ported, ungated.** … The growth and respiration R² values his
> report quotes for them … are **his numbers, not reproduced here**, and must not be quoted as
> though they were. **What is missing:** `derived_N0_R_results_with_carbon.csv` … it exists only
> on Parsa Amirmoeini's machine and a search of the whole 1.0 GB snapshot he supplied finds no
> copy. It has been requested.

**Verified after the merge, exit codes checked explicitly and never chained with `&&`:**

| check | result |
|---|---|
| Candida gate, `$CANDIDAS_ROOT` unset | rc=0, **79 comparisons, 79 PASS, 0 FAIL** |
| eciML1515 / mmaripaludis / syn6803 TPCs | rc=0, **byte-identical** |
| the four Candida `transfer_candida` runs | rc=0, **byte-identical** |

## TASK 1 — the transporter turnover is 300 s⁻¹ (provisional)

| k_cat | T_opt exact in all four media | worst optimum-quantity difference | worst curve \|Δgrowth\|/r_max | verdict |
|---|---|---|---|---|
| **300 s⁻¹** | **yes** | **7.4 × 10⁻⁴** | **6.0 × 10⁻⁴** | **reproduces his figure** |
| 30 s⁻¹ | no — 0.5 °C out in three media | r_max 5.5–5.8 % low | 1.4 × 10⁻¹ | does not |

Set as `gas_exchange.transport_carrier.kcat_s: 300.0` in `strains/eciML1515/gas_exchange.yaml`
— **strain data, not core code** — with the discrepancy and the test recorded in the comment,
and the now-redundant override removed from `gasflux_configA.yaml`. One committed output
changed and it carries no numbers: `gasflux_configA/resolved_config.yaml` loses one line;
`gasflux.csv` and `summary.csv` are byte-identical.

## TASK 2 — the 1.2 % is the medium, exactly

r_max at the NLDM optimum, configuration B — the run in which the discrepancy was seen:

| | Parsa | blanket (his medium) | recipe (canonical) |
|---|---|---|---|
| r_max | 0.965755 | **0.965755** (rel 2.1 × 10⁻¹⁵) | 0.954407 (rel 1.18 × 10⁻²) |

**Nothing is left over**: O₂, CO₂ and RQ agree to the same order. The ≤ 5.9 × 10⁻⁴ residual in
configurations A and C is the repository-wide residual P1 already isolated and attributed by
demonstration (his own code at his own fork point reproduces the port exactly), not a residual
of this task — reported, not stopped on (D2).

Recipe ceilings are now canonical; `NLDM_blanket` is a labelled sensitivity, and the gas-flux
README says which to quote. **What moves at the NLDM optimum:** A — r_max −9.9 %, O₂ −60.6 %,
CO₂ −79.1 %, RQ 2.036 → 1.082, acetate 0 → 25.14; B — T_opt 34.5 → 32.5 °C, r_max −1.2 %;
C — r_max −15.6 %, CO₂ −83.5 %, **RQ 7.375 → 1.044**.

**One of his claims changes.** His report says configuration C shows that "because no carbon cap
is imposed the RQ is not forced toward 1 … NLDM RQ ≈ 7–9". On the canonical medium it is
**1.04**: the high RQ was the blanket medium's unlimited carbon, not the absent cap. Reported,
not adjudicated.

## TASK 3 — c_max = 60 sits past the steepest part of the slope

**Provenance: no literature citation for any c_max exists anywhere in his folder.** What does
exist argues against 60 — his own report calls the cap "a boundary condition (a sweep), not a
fitted likelihood"; his own sweep table calls the growth shape at 60 a "flat plateau" and his
key finding is "**C_max ≈ 100–120 is the sweet spot**"; 60 appears only as the representative
run in his later configuration summary, and his driver's own default is `--caps 80 100`. In
configuration D the same name means a *fitted* multiplier of 230.

**Sensitivity** (two media, cap off → 40, 95 temperatures):

| c_max | glucose T_opt | NLDM T_opt | NLDM E_a | CT_max (either) |
|---|---|---|---|---|
| ∞ … 150 | 38.0 °C, flat | 39.0 °C, flat | 0.949 → 0.964 | ≤0.06 % |
| 120 / 100 | 38.0 | 39.5 | 0.952 / 0.981 | ≤0.27 % |
| 80 | 38.0 | 39.0 | **1.075** | ≤0.45 % |
| **60** | **37.5** | **32.5** | **1.230 (+29.6 %)** | ≤0.66 % |
| 50 / 40 | 36.5 / 35.5 | 30.5 / 29.5 | 1.307 / 1.374 | ≤0.91 % |

T_opt is flat to ≈150, stirs between 120 and 80, and falls 6.5 °C between 80 and 60. **CT_max is
insensitive throughout.** Two further observations: at c_max = 60 there is **no acetate overflow
at all** on either medium — the cap used for the configuration-B figures suppresses the very
mechanism configuration D exists to produce — and r_max moves continuously from the first
binding cap, so no value leaves growth alone. **c_max was not changed and no conclusion about
whether it is fitted was drawn.**

## TASK 4 — every report stamped

`scripts/stamp_reports.py` writes `reports/<name>/PROVENANCE.md` for all nine directories:
the commit the report was last written at, every committed input directory with the commit each
was last written at, and a one-line status. `--check` exits 1 if any is stale.

**The status is not inferred from dates** — N3 found counterexamples in both directions — so it
lives in `reports/report_status.yaml` **with its evidence**, and an unestablished report is
stamped UNKNOWN:

| status | reports |
|---|---|
| **CURRENT** | `candida_thermal_limit` (gate 79/79 today), `ecoli_gasflux` (gate 60/60; D/E/F flagged ungated in the same breath), `P1_parsa_port`, `P2_settle` |
| **HISTORICAL** | `ecoli_tpc` (N3's audit: 3 of 11 inputs reproduce, 8 do not), `N1_overnight`, `N2_followups`, `predictor_calibration` |
| **UNKNOWN** | `activation_energy` — not audited; settling it means re-running the dissections, so it is claimed neither way |

HISTORICAL is not a criticism and the stamp says so in as many words. `README.md` carries the
convention so the next report is stamped at birth. The stamp's own self-reference bug was caught
by running `--check` immediately after committing, and fixed.

## TASK 5 — the three annotations, in the files a reader reaches

1. **Two model states** — `reports/ecoli_tpc/report.qmd`, immediately before the dissection's
   conclusion: the control analysis is on the O2-closed model and the decomposition and
   elasticity are not; r_max 2.1609 vs 2.1558 (−0.235 %), B₈₀ −4.5 %, T_opt and CT_max
   unchanged; the cost of fixing it (re-running both, hours of solver time, not a calibration)
   stated and the deferral said out loud.
2. **The 37–44 °C shoulder** — in the passage that presents the measured sector allocation,
   because the measurement's temperature range is the cause: the curve is bit-identical across
   eight grid points at 0.524757 h⁻¹, the model answering the same question eight times, and
   the flat-top guard cannot see it because the shoulder sits below the maximum.
3. **T_opt is regime-determined** — one sentence in "Interpretation and caveats", plus the
   general rule in `docs/QUOTING_DESCRIPTORS.md` with all three measurements tabulated and the
   mechanism stated: CT_max is where the unfolding envelope reaches zero and no capacity
   constraint moves that; T_opt is wherever the binding constraint's ceiling peaks or crosses
   the rising branch, so it moves when *which* constraint binds changes.

## Verification

| check | result |
|---|---|
| Candida gate, `$CANDIDAS_ROOT` unset | rc=0, **79/79 PASS** |
| P1 gate (configurations A/B/C) | rc=0, **60/60 PASS** |
| eciML1515 / mmaripaludis / syn6803 TPCs | rc=0, **byte-identical** |
| the four Candida `transfer_candida` runs | rc=0, **byte-identical** |
| `python scripts/stamp_reports.py --check` | rc=0, every stamp up to date |
| committed outputs changed | **one line of one `resolved_config.yaml`**, numbers byte-identical |
| scientific conclusions altered | **none** — TASK 2 and TASK 3 report what changes; neither adjudicates |
| `$PARSA_ROOT` / `$CANDIDAS_ROOT` | read only; untouched |

## For Parsa — the three questions, with what is now known

1. **c_max.** No justification for 60 exists in the folder; your own sweep recommends 100–120
   and calls 60 a flat plateau; at 60 there is no acetate overflow and T_opt has already fallen
   6.5 °C on NLDM. Which value is intended, and is the cap swept (config B) or fitted (config D)?
2. **NLDM.** Your committed CSVs used the blanket medium; your code now uses recipe ceilings and
   was edited three days after the CSV. Recipe is taken as canonical here. Confirm — and note
   that under it configuration C's NLDM RQ is 1.04, not 7–9.
3. **Transporter k_cat.** 300 reproduces your figure and 30 does not, so 300 is set. Confirm
   that 30 in `gasflux.py` was a stale default.

And the standing request: **`derived_N0_R_results_with_carbon.csv`**. Until it arrives,
configurations D, E and F stay ported and ungated.
