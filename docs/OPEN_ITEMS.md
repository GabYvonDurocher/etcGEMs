# Open items — the running list

_Started 2026-09-08 while P2 was running; last updated 2026-09-08 by P3._ This is the standing list of what is outstanding across
the whole project, so nothing is lost between sessions. Update it when something lands; do not let
it become a second decision log — decisions live in each prompt's `reports/*/DECISIONS.md`, this is
only what is NOT yet done and who or what it waits on._

Status: **BLOCKED** (waiting on something external) · **READY** (can start now) · **PENDING P2**
(depends on the run in flight) · **DEFERRED** (deliberately not now, with a trigger)

---

## 1. Waiting on people

| # | Item | Waiting on | Why it matters |
|---|---|---|---|
| ~~1.1~~ | ~~**E. coli respirometry**~~ | — | **CLOSED 2026-09-08 (P3).** Arrived as two full pipeline runs (R2A/LB and M9), ingested at `strains/eciML1515/respirometry/`. Configs D, E and F are now **gated**: all ten R² values reproduce, worst 0.009. |
| ~~1.2~~ | ~~**`c_max = 60`: grounded or fitted?**~~ | — | **CLOSED 2026-09-08 (P3 TASK 4)** — on his own evidence rather than by asking. His report calls the cap a swept boundary condition, not a fit, and his sweep concludes "C_max ≈ 100–120 is the sweet spot". **120 adopted** (the only value in his range at which acetate overflow is non-zero on both media); 60 kept as a labelled sensitivity. |
| ~~1.3~~ | ~~**Confirm recipe ceilings supersede blanket medium**~~ | — | **ACTED ON 2026-09-08/09 (P4).** All nine configurations refitted under recipe ceilings with the clearance K sampled. NLDM is unchanged to better; LB collapses, and the cause is `c_max`, not the medium (1.11). A one-line confirmation from Parsa is still welcome; nothing waits on it. |
| ~~1.4~~ | ~~**Confirm transporter kcat 30 vs 300**~~ | — | **SETTLED 2026-09-08 (P2 TASK 1)** by reproduction: 300 reproduces his figure, 30 does not. Set in the strain data. A one-line confirmation from Parsa would close it formally; nothing waits on it. |
| 1.8 | **Which configuration-F ETC table is intended?** | Parsa | P3 found his fits use configuration **E's** areas and turnovers plus a non-electrogenic bd-II, while the Bekker-turnover table in his `configF.py` was never used for a reported number. The port now matches what he fitted; whether the Bekker table is the intended future form is his call. |
| 1.9 | **Per-cell respiration: N₀ and fg C per cell** | Parsa | The inoculum back-projection is off in every row of both media sets, `cell_volume_um3`/`cell_carbon_fg` are typed constants (2 µm³ / 350 fg), and his own `config.R` log prints 21.21 µm³ / 2120.58 fg — ~6× apart. Growth R² and every scale-free quantity are immune; **respiration R², CUE and absolute per-cell rates are not.** Reported in `strains/eciML1515/respirometry/README.md`, not adjudicated. |
| ~~1.10~~ | ~~**M9: fit or not?**~~ | — | **CLOSED 2026-09-09 (P4 TASK 4).** Fitted for all three configurations — the best growth fits in the exercise (R² 0.96–0.99). OTU 2 (`M9`, 7 non-monotonic rows) was excluded as a control, not a series. |
| 1.11 | **`c_max` on LB** | us, then Parsa | P4 applied the canonical 120 to LB and all three LB growth R² collapsed (0.83–0.90 → 0.16–0.20). His own LB fits chose **257 / 459 / 510**. 120 comes from a glucose/NLDM sweep and no LB sensitivity has ever been run. **One fit settles it: configuration D on LB at c_max ≈ 260, ~45 min.** |
| 1.12 | **Chain length: every fit in this family is under-converged** | us | All nine P4 refits AND all six of Parsa's committed chains run ~9 autocorrelation times (chain/τ 6–12 against ≥40). Reaching the criterion is ~8 000 steps, ≈ 40 h for all nine. Until then no R² from either family is a converged posterior. The warm-start defect that lengthened P4's burn-in is fixed but untested at scale. |
| 1.5 | **`common_network.py` result** — does the optimum still compress on a common scaffold? | Ilgaz | Never recorded in `gem/notes/`. Note the K1 finding that makes it partly moot: the two draft models ARE the *auris* network with genes reassigned, so the control is near a no-op for them and informative only for *C. parapsilosis*. |
| 1.6 | **Did any Candida audit touch lipid or membrane pathways?** | Ilgaz | Bears on §6a. `allocation_and_trehalose.py` suggests compatible solutes were looked at; membranes unknown. |
| 1.7 | **`15_run_seq2tm.py` truncation bug** — truncates at 1022 aa citing a non-existent ESM-2 positional limit; committed predictions are untruncated, so the script cannot reproduce the data beside it (up to 2.6 °C) | Ilgaz — **told, not yet fixed** | A live reproducibility break in his repository. |

## 2. Ready to start

| # | Item | Notes |
|---|---|---|
| 2.1 | **A3 follow-through: gene content → mechanism** | A3 measured that models see only ~2–5 % of the gene-content difference (0–15 genes in-model vs 122–647 in proteome), and that AOX and the glutaredoxins are in NO model. Nothing has been done with that. |
| 2.2 | **Membrane-area constraint on Candida** | P1's collapse of Configs E+F into one table-driven ETC mechanism makes this possible for the first time. It is the leading candidate on §6a and now costs a strain data file, not a modelling project. **This is the highest-value scientific item on the list**, and P3 strengthens it: the mechanism is now gated against experiment on *E. coli* (configuration E respiration R² 0.72, configuration F 0.96), so it is a validated mechanism being carried to a new organism rather than an untested one. |
| 2.3 | **K3 — retire the Candidas fork** | N1 prepared the patch (unapplied, `git apply --check` clean) and confirmed nothing in etcGEMs needs `$CANDIDAS_ROOT` at run time now the gate has a fixture. Needs a human to apply it in Ilgaz's repository. |
| 2.4 | **`_toy/resolved_config.yaml`** structurally stale (numbers fine, 6.2e-15) | Listed by N2, not fixed. Trivial. |

## 3. Deferred, with triggers

| # | Item | Trigger to act |
|---|---|---|
| 3.1 | **Re-run `decompose_tuned` + `elasticity_tuned`** to match `control_tuned`'s model state | When that dissection material is used in a paper. Until then P2 TASK 5 annotates it. |
| 3.2 | **`calibration_vanderlinden`** (4 h 28 min emcee) | When a specific number from it is needed and must be current. |
| 3.3 | **Full E. coli regeneration** | Paper time, and then only the directories that paper uses. Reports are logs; provenance stamps (P2 TASK 4) are the standing fix. |
| 3.4 | **Extend the E. coli proteome above 37 °C** | This is a measurement, not a modelling job. Until then the 37–44 °C bit-identical shoulder is documented as a limitation (P2 TASK 5). |
| 3.5 | **DLTKcat on the four Candida proteomes** | A1 recommended against for now: wrong half of the curve, no benchmark, ~50,000 predictions. Revisit only if the kinetic envelope becomes load-bearing. |
| 3.6 | **Per-protein *S. cerevisiae*/*S. uvarum* Tm from the authors** | Would allow A1's strongest test (correlation of measured against predicted *differences*), currently impossible — only the summary statistic is published. |
| 3.7 | **A measured meltome for any *Candida*** | None exists. Would replace the load-bearing literature benchmark with own data. |

## 4. Standing hazards — not tasks, but re-read before trusting a result

- **Never verify with `cmd && check`.** The `cli.main` exit-code defect made one such check vacuous
  and produced a false PASS. Check exit codes explicitly. (Fixed in `a467d23`, but the habit is the
  hazard.)
- **Stale-at-commit has happened three times in three codebases by three people** — `outputs/tpc`
  committed with numbers its own code did not produce; `control_tuned` diverging from
  `decompose_tuned`; Parsa's NLDM CSV predating its own `build_pm`. Assume it until checked.
- **T_opt is regime-determined.** Three constraints relocate it (sector re-grounding `a416fd1`, the
  translation cap, Parsa's carbon cap); CT_max has been insensitive to all three. Quote T_opt with
  its binding constraint named; CT_max may be quoted plainly.
- **A variance decomposition can only attribute to mechanisms the model contains.** φ_envelope
  = 0.999 for T_opt is a local measure inside one regime, not a statement about what sets T_opt.
- **The two Candida draft models are the *auris* network with genes reassigned** (2,863 reactions,
  ~1,312 costed, differing by 2–4). Network differences cannot explain their behaviour — and cannot
  be tested there either.
- **Sectors without temperature-dependent allocation flatten the curve.** Confirmed on E. coli:
  plateau 2.0 → 14.0 °C with `allocation_from_data` off. N1's guard warns; it cannot see a shoulder
  *below* the maximum (the 37–44 °C case).

---

## 5. What to do with P2's outcome — the checklist to run against its report

_Written before P2 finished, so the reaction is not shaped by the result._

**Verify, in this order:**

1. **The merge held.** Gate 79/79 with `$CANDIDAS_ROOT` unset, exit codes checked explicitly not
   chained; all seven strains byte-identical. If either failed, nothing below matters.
2. **The ungated notice is at the top of the config report**, not buried. A reader must not be able
   to mistake ported for verified. Quote it and check.
3. **TASK 1 (kcat).** If neither 30 nor 300 reproduces his figure → that is a finding, not a
   failure, and it goes to Parsa as a fourth question. If one does → record as provisional, and
   expect his reply to ratify.
4. **TASK 2 (NLDM).** The 1.2 % must be **fully** explained by the medium. A residual means
   something else moved and is a stop condition — chase it before merging.
5. **TASK 3 (c_max) — read this one hardest.** The question is whether 60 sits in a flat region or
   on a slope.
   - *Flat region* → the thermal claims are safe whatever Parsa says about provenance, and 1.2
     downgrades from blocking to housekeeping.
   - *On a slope* → every T_opt and E_a number in the new paper depends on a constant whose
     justification is unknown, and that becomes the most urgent item on the list.
   - Either way, do NOT let a tidy sensitivity table substitute for the provenance question.
6. **TASK 4 (stamps).** Check the stamp is generated by a script, not hand-written — a hand-written
   stamp is the next thing to go stale. Check HISTORICAL is phrased neutrally.
7. **TASK 5 (annotations).** All three must be in files a reader reaches, not in decision logs.
   Verify by opening the file, not by trusting the report.

**Then update this document:**

- Move anything P2 closed out of §2 and into a struck-through line or delete it.
- Add anything P2 discovered — expect at least one; every run so far has produced a finding the
  prompt did not anticipate (K1: the draft-model construction; K2: the reversible ATP reaction;
  A1: the predictor's absent validity; N1: the E. coli allocation cliff; N2: stale-at-commit;
  N3: the exit-code defect; P1: the missing respirometry).
- Re-rank §2. If TASK 3 says c_max is on a slope, 1.2 outranks everything.

**Then the next prompt is one of:**

- **P3** — gate D/E/F, if Parsa's data has arrived. Highest value when possible.
- **K4** — the membrane-area constraint on Candida (2.2). Highest value when it has not, and it does
  not depend on anything outstanding.
- A short corrective run, if P2 raised a stop condition.
