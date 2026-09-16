# Claude Code prompt — H2: put the primary tree on main, remove the disposable worktrees, keep the archive (autonomous, ~20 min)

Run from **`../etcGEMs-h1`** — the worktree that currently holds `main` at `e53e114`. The primary
checkout at `MICROADAPT/etcGEMs` is on `t1/housekeeping` at `3222b9d` and is one of the things this
prompt fixes, so do not start from it.

**Nothing is running.** No fits, no science, no commits to any report. This is filesystem and git
hygiene only, and every destructive step is gated on a check that can stop it.

**Why.** H1 left thirteen worktrees plus six Claude scratchpads. They are full checkouts of a
180 MiB repository with untracked run outputs and virtual environments on top, **all of them inside
a OneDrive-synced folder**. H1 correctly declined to remove them unasked, because a worktree can
hold uncommitted work and `git worktree remove` is a filesystem deletion git cannot undo. The check
is cheap; this prompt does it first and stops on anything dirty.

**THE ONE THING THAT MUST SURVIVE.** `../etcGEMs-p17-archive` holds
`codex/p17-inactive-prior` at `ef1961b`. That branch is the **only ref keeping ~2.9 GB of P17
artefacts reachable**, it is deliberately not on origin, and it is not recreatable from anything.
**Never remove that worktree. Never delete that branch. Never push it.** Check by name before every
destructive step, and if any command would touch it, stop.

**The inventory, to be re-verified rather than trusted:**

| worktree | branch / head | disposition |
|---|---|---|
| `MICROADAPT/etcGEMs` (primary) | `t1/housekeeping` @ `3222b9d` | **move to `main`**, keep |
| `etcGEMs-p17-archive` | `codex/p17-inactive-prior` @ `ef1961b` | **KEEP — protected** |
| `etcGEMs-h1` | `main` @ `e53e114` | keep, **rename to `etcGEMs-work`** |
| `etcGEMs-k4`, `-k5`, `-k6`, `-k7`, `-k8`, `-k9` | K-series, merged; `k7` already broken (`0000000`) | remove |
| `etcGEMs-t1`, `-t2`, `-t3` | T-series, merged | remove |
| `etcGEMs-work` (existing) | detached @ `3222b9d` | remove — its name is reused above |
| `/private/tmp/wt-deck` | detached @ `0215a16` | remove |
| six `/private/tmp/claude-502/…/scratchpad/*` | detached, prunable | remove |

Eleven local branches remain, not the nine H1 reported: `main`, `t1/housekeeping`,
`codex/p17-inactive-prior` and eight held by worktrees.

NOTE TO USER: launch in an auto-approving mode. It reports before it deletes anything, and stops if
any worktree is dirty or if the archive is not exactly where it should be.

---

```
Work AUTONOMOUSLY. Print a short report. Standing rules carry over. Check exit codes explicitly,
never `cmd && check`. **Never --force. Never `git clean`. Never delete an unmerged branch. Never
touch codex/p17-inactive-prior or its worktree.**

TASK 0 - verify the premise before touching anything
- Confirm you are in ../etcGEMs-h1 and it is on main at e53e114 or later. Confirm nothing is
  running: no process with any worktree as cwd, no log under any reports/ written in the last ten
  minutes. If anything is running, STOP.
- `git fetch origin --prune`. Report origin/main and every remote branch. Report every local
  branch with its head and whether it is an ancestor of main.
- `git worktree list`. For EACH worktree: does the path exist on disk; what branch or detached
  head; is it an ancestor of main; and its approximate size on disk (`du -sh`, and say if a path
  is unreadable rather than guessing).
- **The archive check, by name:** confirm ../etcGEMs-p17-archive exists, is on
  codex/p17-inactive-prior at exactly ef1961b, that the branch is NOT on origin, and that
  reports/P17_inactive_prior/closure_manifest.json is readable there. If any of that fails, STOP
  and report - nothing below may run.

TASK 1 - the dirty check, which gates everything destructive
- `git -C <path> status --porcelain` in EVERY worktree, including the primary and the archive.
- Report, per worktree: clean, or the list of dirty and untracked paths.
- **If any worktree slated for removal is dirty:** do NOT remove it. Report exactly what is there
  and leave it in place. Removing a worktree with uncommitted work destroys that work; a leftover
  directory costs disk space. Those are not comparable, so err toward keeping.
- Ignored files (venvs, run outputs) are expected and do not block removal; state that you
  distinguished them from genuinely untracked work, and how.

TASK 2 - the primary tree onto main
- In MICROADAPT/etcGEMs: confirm TASK 1 found it clean (or that its dirty paths are ignored
  artefacts only - if there is real uncommitted work, STOP and report it).
- `git switch main` then `git pull` - two commands, two exit checks. Confirm HEAD equals
  origin/main and the tree is clean.
- This is the checkout a collaborator opens. Confirm it now contains docs/HANDOVER.md,
  reports/H1_handover/_output/calibration_investigation.pdf and
  reports/ecoli_deck/_output/deck.pdf.

TASK 3 - remove the disposable worktrees
In this order, each non-force, each reported, each skipped if TASK 1 found it dirty:
  1. The six /private/tmp/claude-502/…/scratchpad/* worktrees.
  2. /private/tmp/wt-deck.
  3. etcGEMs-k4, -k5, -k6, -k8, -k9 (all merged). For -k7, whose head reads 0000000, the
     worktree metadata is broken: use `git worktree prune` rather than `remove`, and say so.
  4. etcGEMs-t1, -t2, -t3 (all merged).
  5. The EXISTING etcGEMs-work (detached at 3222b9d) - remove it before TASK 4 reuses the name.
- `git worktree prune` afterwards. Report `git worktree list` before and after, with the disk
  space recovered.
- **Do not remove etcGEMs-h1 or etcGEMs-p17-archive.**

TASK 4 - rename the surviving second tree
- `git worktree move ../etcGEMs-h1 ../etcGEMs-work`. Verify afterwards that it is still on main at
  the same commit and clean.
- Two trees now remain besides the archive: the primary on main, and etcGEMs-work on main, for
  parallel runs. State that in the report.
- If you are executing this prompt FROM ../etcGEMs-h1, move to the primary tree first so you are
  not standing in the directory you are renaming.

TASK 5 - delete the orphaned branches
- After TASK 3, the branches those worktrees held are free. Delete, non-force, every local branch
  that is an ancestor of main: the K-series, the T-series, t1/housekeeping, and any other.
- **Do NOT delete main. Do NOT delete codex/p17-inactive-prior.** Confirm both survive, by name,
  afterwards.
- If git refuses any deletion as unmerged, leave it and report why - that is information, not an
  obstacle.
- Report the branch list before and after. The expected end state is exactly two local branches:
  main and codex/p17-inactive-prior.

TASK 6 - verify, and record
- `git worktree list`: exactly three entries - the primary on main, etcGEMs-work on main, and the
  archive at ef1961b.
- `git branch`: exactly main and codex/p17-inactive-prior.
- The archive, re-checked by name: path exists, branch at ef1961b, absent from origin, manifest
  readable. Report its size.
- Both gates from the primary tree on main: 79/79 and 60/60.
- Total disk recovered.
- docs/OPEN_ITEMS.md: one dated line under section 0 recording the cleanup - the end state, the
  archive's path and its protection, and that the second worktree is ../etcGEMs-work. Commit that
  one line on main and push; no PR needed for a record line, unless the house convention forbids
  direct pushes, in which case a one-commit PR.

VERIFY (report all)
1. TASK 0: the branch and worktree tables with sizes; the archive check by name.
2. TASK 1: the dirty status of every worktree; anything found dirty and therefore kept; how
   ignored artefacts were distinguished from untracked work.
3. TASK 2: the primary tree on main at origin/main, clean, with the three handover files present.
4. TASK 3: every worktree removed or skipped with its reason; k7 handled by prune; the before and
   after lists; space recovered.
5. TASK 4: the rename verified, still on main, clean.
6. TASK 5: branches before and after; confirmation main and the archive branch survive; anything
   git refused.
7. TASK 6: the three worktrees; the two branches; the archive re-verified with its size; both
   gates; total space recovered; the OPEN_ITEMS line committed and pushed.

CONSTRAINTS
- codex/p17-inactive-prior and ../etcGEMs-p17-archive are protected by name at every step. If any
  command would touch either, stop.
- A dirty worktree is kept, never removed. Disk space is cheaper than lost work.
- Never --force, never `git clean`, never delete an unmerged branch, never delete main.
- No commits to any report, no science, no model or config change. One record line in OPEN_ITEMS
  is the only content change permitted.
- Report before deleting; if any check in TASK 0 or TASK 1 fails, stop rather than proceed.
```
