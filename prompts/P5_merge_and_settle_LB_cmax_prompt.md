# Claude Code prompt — P5: merge P4 and K9, settle `c_max` on LB, and close two loose ends (autonomous, short)

Run from the project root (`.../MICROADAPT/etcGEMs`). Short and cheap. Run this BEFORE P6, which
starts a ~40-hour job and should not begin on an unmerged tree.

**Why.** P4 refitted nine configurations under the canonical settings and LB collapsed — growth R²
0.83–0.90 → 0.16–0.20 — while NLDM was unchanged to better. The LB medium is a committed component
list and did not change, so `c_max` is the cause. **That is our error, not Parsa's**: his sweep
concluded "≈100–120" in a glucose/NLDM context, P3 adopted 120 as canonical, and P4's settings table
applied it to LB as well. His own LB fits chose **257, 459 and 510**. No LB sensitivity has ever been
run by anyone.

NOTE TO USER: launch in an auto-approving mode. One ~45-minute fit plus merges and bookkeeping.
Needs network and credentials.

REFERENCE, read first: `reports/P4_refit/` (the movement table and the LB collapse),
`reports/K9_criterion/report.md`, `docs/OPEN_ITEMS.md` 1.11 and 1.12, and Parsa's own LB
`meta.json` files under `$PARSA_ROOT` (READ ONLY) for the `c_max` values he actually used.

---

```
Work AUTONOMOUSLY; commit per task, prefixed "P5 TASK n: "; maintain reports/P5_lb_cmax/DECISIONS.md
FROM THE FIRST JUDGEMENT CALL. Print a final summary. Standing rules carry over. Check exit codes
explicitly, never `cmd && check`. $PARSA_ROOT and $CANDIDAS_ROOT are READ ONLY.

TASK 0 - merge P4 and K9
- Merge PR #12 (`p4/refit`) --no-ff, then PR #13 (`k9/criterion`) --no-ff. They do not collide:
  P4 wrote nothing under `strains/c*/`, and the only shared files are `docs/OPEN_ITEMS.md` and
  `reports/report_status.yaml`, both append-style. **Keep BOTH sets of rows in each** — do not let a
  conflict resolution drop one prompt's entries.
- K9 worked in a separate worktree (`.../etcGEMs-k9`). Confirm the branch is fully pushed and, once
  merged, remove the worktree so it does not drift.
- Verify after each merge with exit codes checked: Candida gate 79/79 with $CANDIDAS_ROOT unset,
  P1 gate 60/60, all seven strains byte-identical, `stamp_reports.py --check` passes.
- Push, close both PRs, delete both branches. If anything fails, stop and report.

TASK 1 - the LB `c_max` fit
- Establish from `$PARSA_ROOT` what `c_max` each of his three LB fits used, and report them. The
  values 257 / 459 / 510 are from P4's report — confirm them at source.
- Run ONE fit: configuration D on LB, recipe ceilings, k_cat 300, at `c_max ≈ 260` (justify the exact
  value from his own fits). Same sampler settings P4 used, into a new clearly-named output directory.
- Report growth R² against P4's collapsed value (0.16–0.20) and against Parsa's blanket-medium value
  (0.83–0.90). State whether `c_max` is confirmed as the cause.
- Then decide the canonical LB value, on evidence, and record it in the E. coli strain data with a
  comment naming its provenance and the fact that 120 was an NLDM value over-applied. If the single
  fit is not enough to choose, say what would be and set nothing.
- **Do NOT quote the R² as a converged result** — see TASK 2. It is a diagnostic comparison against
  P4's own fit at the same chain length, which is a fair like-for-like even though neither is
  converged.

TASK 2 - record the convergence finding where it will be read
P4 established that ALL nine of its refits and ALL six of Parsa's committed chains run at
chain/τ ≈ 6–12 against a ≥40 criterion. This is a sampling-budget property, not a failure of
anyone's diligence, and it applies evenly to both families.
- Put it at the TOP of `reports/ecoli_gasflux/README.md` and in `reports/P3_gate/`: the ten gated R²
  values, and the ones Parsa's report prints, are **not converged posteriors**. State the numbers
  (τ, chain/τ, n_eff) and the cost of fixing it.
- Preserve the distinction explicitly, because it is easy to blur: **P3's gate remains valid as a
  PORT check** — reproducing his computation to 0.009 proves the port is faithful whether or not the
  chain converged. What does not follow is reading those R² as validated model performance.
- Do not remove or restate any number. Add the caveat beside it.

TASK 3 - the standing hazard P4 and K9 exposed
Two additions to `docs/OPEN_ITEMS.md` §4, both learned the hard way this week:
- **A gate only protects the fields it checks.** K8 added a field to the calibration record and
  wrote it unconditionally; every committed output went stale and the gate missed it because it does
  not read that field. Adding a field to a record is a silent way to break byte-identity. Re-run the
  byte-identity check AFTER the last change, not at the point it seems safe.
- **A recommendation is scoped to the conditions it was derived under.** `c_max ≈ 120` came from a
  glucose/NLDM sweep and was applied to LB, where it collapsed the fit. Record the value AND the
  medium it was established on.

TASK 4 - the unexplained 10 °C
K9 found one strain whose committed ceiling cannot be reproduced from a plain build, differing by
10 °C, with truncation and medium both excluded. It was correctly left unguessed.
- Confirm it is recorded in `docs/OPEN_ITEMS.md` with its evidence and the strain named. If not, add
  it. Do NOT investigate further here — it needs its own run.

VERIFY (report all)
1. TASK 0: both merges; both sets of rows preserved in the two shared files; all gates; worktree
   removed; both PRs closed.
2. TASK 1: Parsa's three LB `c_max` values confirmed at source; the fit's growth R²; whether `c_max`
   is confirmed as the cause; the canonical LB value set, or why not.
3. TASK 2: the convergence caveat, quoted, in both places; the port-check distinction stated.
4. TASK 3: both hazards added.
5. TASK 4: the 10 °C discrepancy recorded with its strain and evidence.
6. `git diff main --stat`; no committed output regenerated beyond the new LB fit directory.

CONSTRAINTS
- Keep both sets of rows in `OPEN_ITEMS.md` and `report_status.yaml`. A dropped row is a lost finding.
- The LB fit is a diagnostic at P4's chain length, not a converged result. Say so where it is quoted.
- Do not investigate the 10 °C discrepancy here. Record it.
- Autonomous; commit per task.
```
