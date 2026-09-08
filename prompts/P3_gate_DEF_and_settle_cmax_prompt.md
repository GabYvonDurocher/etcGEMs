# Claude Code prompt — P3: merge N3 then P2, ingest Parsa's E. coli respirometry, adopt the c_max his own sweep recommends, and gate Configs D/E/F against experiment (autonomous)

Run from the project root (`.../MICROADAPT/etcGEMs`). Parsa's data has arrived, so the last blocker
is gone. Two PRs are open and their order matters.

NOTE TO USER: launch in an auto-approving mode. TASK 0 needs network and credentials. No emcee; the
gate and the regenerations are deterministic solves. Parsa's data is at
`$ECOLI_R2A` (default `/Users/g.yvon-durocher/Downloads/Ecoli_R2A_LB`) and
`$ECOLI_M9` (default `/Users/g.yvon-durocher/Downloads/Ecoli_M9`), both **READ ONLY**, as are
`$PARSA_ROOT` and `$CANDIDAS_ROOT`.

## Four things established before this prompt, which it must not re-litigate

1. **Merge order is N3 (PR #3) then P2 (PR #5).** Both edit the same bullet of
   `reports/ecoli_tpc/report.qmd`. Keep BOTH sentences, N3's first — P2's own `DECISIONS.md` D0
   records this.
2. **`c_max = 60` is past the transition.** T_opt is flat to ~150 and moves 39.0 → 32.5 °C between
   80 and 60, with E_a +29.6 %; CT_max is insensitive throughout. No citation for any c_max exists in
   Parsa's folder; his report calls it a swept boundary condition and **his own sweep concludes
   "C_max ≈ 100–120 is the sweet spot"**. At 60 there is no acetate overflow at all — the cap behind
   the Config B figures suppresses the mechanism Config D exists to produce.
3. **Parsa's data moved on 7 September.** `_backup_before_boundaryfix_20260907_*/` holds the version
   his committed figures were made from; the current tables add four 50 °C rows with `r` pinned at
   1e-6 (dead cells: no growth, respiration only). Gating against the current file will NOT reproduce
   his figures.
4. **It is the Candida respirometry pipeline** (`01_convert_xlsx.R` … `06_oxygen_fits.R`,
   `config.R`, `run_all.R`), at a slightly different revision. Everything established about that
   method applies to these numbers.

---

```
Work AUTONOMOUSLY; commit per task, prefixed "P3 TASK n: "; maintain reports/P3_gate/DECISIONS.md.
Print a final summary with each task DONE / PARTIAL / STOPPED. Standing rules carry over: decide and
proceed when reversible or precedented; stop the task and record when it would change a committed
number, need a scientific judgement, or write inside any READ ONLY root. Never verify with
`cmd && check` — check exit codes explicitly. TASK 0 is the only write to `main`; the rest is branch
work on `p3/gate-def` ending in a PR that is NOT merged.

TASK 0 - merge N3, then P2, in that order
- Working tree clean, `main` current, else STOP.
- Merge PR #3 (`n3/output-audit`) --no-ff. Verify: Candida gate 79/79 with $CANDIDAS_ROOT unset;
  seven strains byte-identical; exit codes checked explicitly.
- Then merge PR #5 (`p2/settle-and-stamp`) --no-ff. Expect a conflict in
  `reports/ecoli_tpc/report.qmd`: RESOLVE BY KEEPING BOTH SENTENCES, N3's FIRST. Quote the resolved
  passage in your report.
- Verify again as above, plus: `scripts/stamp_reports.py --check` passes, and the D/E/F ungated
  notice is still at the top of `reports/ecoli_gasflux/README.md`.
- Push; close both PRs as merged; delete both branches.
- If anything fails, stop and report. Do not proceed with a broken base.

TASK 1 - ingest the respirometry as strain data, both media sets
Parsa sent more than was asked: R2A/LB and M9. Both are full pipeline runs.
- Copy into `strains/eciML1515/respirometry/` (or the house equivalent): the derived tables needed
  as model INPUTS, from BOTH media sets, and BOTH the current and the pre-boundaryfix versions of
  `derived_N0_R_results_with_carbon.csv`, clearly named (e.g. `..._20260907_prefix.csv`).
- Do NOT copy raw exports, figures, models/ or scripts/ — they belong in the respirometry
  repository, not here. Record where they are.
- Write `strains/eciML1515/respirometry/README.md`: provenance (Parsa, both media, dates), what the
  boundary fix changed, and the columns used downstream.
- Replace the hard-coded Windows absolute paths in the ported scripts with this location. Report
  every path changed.

TASK 2 - what the boundary fix did, before it is used for anything
- Diff current against pre-boundaryfix for both media sets. Report rows added/changed and every
  column that moves.
- The four new rows are 50 °C with `r = 1e-6`, `CUE ≈ 4e-4`, `resp_over_growth ≈ 2500`. Establish
  whether they are intended as observed dead-cell points or as fitting failures, from the pipeline's
  own logs (`Skipped_Series_Log.csv`, `Oxygen_Trimmed_Series_Metadata.csv`) — do NOT guess.
- State whether including them changes any R² in TASK 3, quantitatively.

TASK 3 - THE GATE: Configs D, E and F against experiment
- Gate against the **pre-boundaryfix** data, because that is what his figures used. Reproduce every
  R² and comparison his reports print, per config and per medium: his value, port value, tolerance,
  PASS/FAIL.
- Then repeat against the **current** data and report the difference. Two tables, both labelled.
- Attribution rule, as in P1: a movement must be explained by a NAMED cause (the boundary fix, the
  recipe-ceiling medium, k_cat 300, or the c_max change in TASK 4) with evidence. **An
  unattributable movement is a FAIL, not a footnote.**
- Update `reports/ecoli_gasflux/README.md`: D/E/F move from UNGATED to gated, with the result. If any
  fail, say so at the top with the same prominence the ungated notice had.

TASK 4 - adopt the c_max his own sweep recommends
- Set `c_max` in the E. coli strain data to the value his sweep identifies (≈100–120; pick within
  that range and justify the choice), citing HIS OWN SWEEP as the provenance, with the file and
  figure named. This is his recommendation, not ours.
- Regenerate the Config B figures and any quantity computed at c_max = 60. Report every number that
  moves, with magnitudes, and confirm from the sensitivity table that the new value sits in the flat
  region for T_opt and E_a.
- Confirm acetate overflow is now non-zero — at 60 it was suppressed entirely, which was
  self-defeating for Config D.
- Keep c_max = 60 as a labelled sensitivity, not as the baseline, and record WHY it was changed:
  his own sweep, plus the fact that 60 sits past the T_opt transition.
- Also record the Config C RQ correction P2 found: NLDM RQ is 1.04, not the ~7–9 his report gives;
  the high value was the unlimited medium, not the absent carbon cap.

TASK 5 - the method caveats these numbers inherit
His R² validation is against per-cell respiration, the quantity most exposed to the assumptions the
Candida work spent weeks characterising. State them plainly in
`strains/eciML1515/respirometry/README.md` and in the gasflux report, with evidence from the data:
- `delta_Ninoc_to_N0_min = 0` and `N0_cells_per_L == N_inoculation_cells_per_L` in the new rows —
  the inoculum back-projection is OFF. Establish whether that holds for all rows or only some.
- `cell_volume_um3 = 2` and `cell_carbon_fg = 350` are typed constants, not measurements. Check
  whether they vary anywhere in the tables.
- Say which reported quantities are affected and which are not: scale-free comparisons (activation
  energies, ratios, the shape of a curve) are immune; absolute per-cell respiration, CUE and any R²
  computed against them are not.
- Report only. Do not adjudicate whether his R² values should change.

FINALLY
- reports/P3_gate/SUMMARY.md; re-run `scripts/stamp_reports.py` so the new and changed reports are
  stamped; push; open a PR; do NOT merge.
- Update `docs/OPEN_ITEMS.md`: close 1.1, and 1.2/1.3/1.4 if this prompt settles them; add anything
  discovered.

VERIFY (report all)
1. TASK 0: both merges; the resolved report.qmd passage quoted; gate 79/79 with $CANDIDAS_ROOT
   unset; stamp --check passes; both PRs closed.
2. TASK 1: what was copied and what deliberately was not; every hard-coded path replaced.
3. TASK 2: the boundary-fix diff; what the 50 °C rows are, established from the logs.
4. TASK 3: BOTH gate tables (pre-fix and current), every movement attributed to a named cause;
   the README updated from UNGATED.
5. TASK 4: the c_max adopted and its justification; every number that moves; acetate overflow
   non-zero; 60 retained as a labelled sensitivity.
6. TASK 5: the caveats, with evidence from the data rather than asserted.
7. `git diff main --stat`; no committed output regenerated beyond what TASK 4 names.

CONSTRAINTS
- Merge order N3 then P2. Both sentences kept, N3's first.
- Gate against the data his figures used, then report the fix separately. Do not conflate them.
- An unattributable movement is a FAIL.
- c_max changes on HIS evidence, cited to his sweep. Do not present it as our judgement.
- TASK 5 reports caveats; it does not revise his results.
- Autonomous; commit per task.
```
