# N3 — summary

| task | status | one line |
|---|---|---|
| **TASK 0** — merge N2 | **DONE** (with a hotfix) | Merged `5714fb7`; verification caught a regression the merge introduced, fixed in `a467d23`, then pushed |
| **TASK 1** — audit the outputs the report reads | **DONE** | 43 files, 11 directories; 9 of 11 predate a change that moves their numbers; 5 record no config at all |
| **TASK 2** — the cap-regime hypothesis | **DONE** | Wrong as posed; what is true is sharper; caveat sentence added |
| **TASK 3** — escalate cheaply | **DONE** (1 item stopped, as instructed) | 3 reproduce, 8 do not, 3 not cheaply testable, `calibration_vanderlinden` costed for a human |
| **TASK 4** — record, close the loop on D5 | **DONE** | `report.md` written; D5 promoted to `README.md`; a false README claim corrected |

Full report: [report.md](report.md). Judgement calls: [DECISIONS.md](DECISIONS.md) (D0–D9).

---

## TASK 0 — merge N2

Merge commit **`5714fb7`** on `main` (`--no-ff`), then hotfix **`a467d23`**, then pushed;
PR #2 auto-closed as merged; branch `n2/followups` deleted locally and remotely;
`git config core.fileMode false` set in this clone (local config, not committed).

Verification, with `$CANDIDAS_ROOT` **unset** and exit codes checked:

| check | result |
|---|---|
| K1 gate | **79 comparisons, 79 PASS, 0 FAIL** |
| `eciML1515` `outputs/tpc` — the check that N2's fix took | **reproduces byte-identically** |
| `mmaripaludis` `outputs/tpc` | **byte-identical** |
| `syn6803` `outputs/tpc_syn6803_ecmodel` | **byte-identical** |

**Verification failed first, and that is the point of it.** `etcgem tpc --strain eciML1515`
and `etcgem tpc --strain syn6803 --experiment syn6803_ecmodel` both raised: N2's
`rescale_pool_row` default flip was guarded only in the `smoment_gem` branch of
`build_provider`, and both of those strains use `gecko` with sectors. A second defect hid it —
`cli.main` returned the output path into `sys.exit()`, so every successful run exited 1, and a
first pass using `etcgem … && cmp` skipped the run and compared each file against itself. Both
fixed in `a467d23`; the guard is now applied *before* the provider is built, because
`add_proteome_sectors` calibrates `translation_coeff` by solving the model and a post-hoc flip
reproduced the committed TPC only to 4.8e-13 (D2). Also recorded: N2's diff was wider than the
prompt expected — 32 Candida numeric files moved, largest relative change 2.5e-07 at 55.5 °C
in `tpc_wide.csv`, deep in the dead zone (D0).

## TASK 1 — the audit

`assemble.py` reads **43 committed files from 11 directories**; all exist and are tracked.
Classification: **9 of 11 predate at least one committed change that moves their numbers.**
Five (`sweep_default`, `sweep_dltkcat_ext`, `sweep_calibrated`, `proteome_sectors`,
`ablation_*`) predate `a416fd1` and still record `f_metab` 0.285 / `f_maint` 0.374. Four more
(`anatomy`, `validation`, `calibration_vanderlinden`, `elasticity_tuned`, `decompose_tuned`)
predate `8085036`, the O2-sink closure. `control_tuned` is the only directory written after
every change — it was regenerated for that closure, and the decomposition and elasticity
beside it were not.

Two structural findings: **five of the eleven carry no `resolved_config.yaml` at all**, and
`assemble.py` is not read-only — it writes three of the files it reads.

## TASK 2 — the cap-regime hypothesis

| state | T_opt | r_max | plateau @1 % | cap binds at T_opt |
|---|---|---|---|---|
| PRE (`27cafef^`) | 37.0 °C | 0.3407 | 1.0 °C | **YES** (30–45 °C) |
| CURRENT | 31.0 °C | 0.5429 | 2.0 °C | **YES** (31–44 °C) |
| TUNED (the decomposition's own point) | 39.0 °C | 2.1558 | 2.0 °C | **NO — 0 of 48 temperatures** |

**Verdict: wrong as posed.** No state has a flat top (N1 measured 14.0 °C for the genuinely
flat case), and the cap binds at T_opt in the current state too. **What is true instead:** in
both nominal states the top of the curve is allocation-determined — PRE, T_opt is the argmax
of the measured f_bio(T) ceiling; CURRENT, it is the crossover where the falling ceiling takes
over. A regime change, not a plateau artefact. φ_envelope = 0.999 is measured at a third point
where the cap never binds, so it is not a cap artefact — but it is regime-conditional and the
report did not say so. **Caveat sentence added** to `report.qmd`; `report.tex` not re-rendered.

New artefact recorded, not fixed: the Glucose proteome stops at 37 °C, so growth is *exactly*
0.524757 /h from 37 to 44 °C — an 8 °C flat shoulder at 96.7 % of r_max that N1's guard cannot
see.

## TASK 3 — escalation

**Reproduces (3):** `control_tuned` (r_max to 7 d.p.); `proteome_sectors/sector_fractions_vs_T`
(exact); the `anatomy` config. **Does not reproduce (8):** `decompose_tuned` and
`elasticity_tuned` (−0.235 % r_max, `B80` −4.5 %); `validation` (`abs_R2` 0.265 → 0.258);
`proteome_sectors/validation_correlations` (log-Pearson R² up to 23×); `sweep_default`
(−1.75 % r_max); `sweep_dltkcat_ext` (**T_opt 37 → 31 °C**); `sweep_calibrated` (**T_opt 37 →
30 °C, r_max −49 %**); `ablation_complete`. Plus the `anatomy` figures, stale by date.
**Not cheaply testable (3):** the two 120-sample sweep ensembles (~2 h each), the three other
ablation variants (no config recorded, no harness committed).

**Stopped for a human (1):** `calibration_vanderlinden`. Settling it means re-running emcee —
60 walkers × 6000 steps, **wall time 16 118 s = 4 h 28 min on 10 processes**, as its own
`summary.json` records. Its posterior defines the tuned operating point, so all three tuned
analyses depend on it.

## TASK 4 — recorded

`reports/N3_output_audit/report.md` carries the table, the causes, and §6 "what a reader of
`reports/ecoli_tpc/` should currently believe". D5 promoted into `README.md` as a stated
limitation: rescaling is off wherever sectors are wired, so the strains carrying sectors —
`eciML1515`, `mmaripaludis`, `syn6803`/`syn6803_ecmodel`, Candida rung B4 — are exactly the
ones that never get the conditioning fix. The README's now-false claim that
`strains/eciML1515/outputs/tpc/` "no longer reproduces" was corrected in the same pass.

## The honest headline

**The audit is not clean.** Eight of the eleven directories the E. coli report renders from no
longer reproduce. Nothing found contradicts a scientific claim — T_opt, CT_max and curve shape
are stable across every test — but the report currently prints, side by side, numbers from
three different model states, and its supplementary provenance config belongs to a run that
reproduces neither its T_opt nor its r_max. **Nothing was regenerated**: causes are established
for both large groups, and what to do about them is a human's decision.
