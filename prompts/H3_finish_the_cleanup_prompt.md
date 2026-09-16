# Claude Code prompt — H3: clear the stale lock, commit the four missing prompts, finish H2's three follow-ups (autonomous, ~20 min)

Run from the **primary checkout**, `.../MICROADAPT/etcGEMs`. It is currently on `t1/housekeeping`
at `3222b9d` with a stale lock and five uncommitted files — that is exactly what this prompt
resolves. **Nothing is running.** No fits, no science, no model or config change.

**Read first:** `docs/OPEN_ITEMS.md` §0 (H2's three follow-ups are recorded there with their
commands — prefer what is written there over this prompt if they differ, and report the
difference).

**What H2 left, and why.** H2 stopped at its TASK 2 because the primary tree holds real
uncommitted work and its index cannot be written. That was the correct call. Three follow-ups
remain, all small, and one of them has a diagnosis attached.

**1. The lock is stale and safe to remove.** `.git/index.lock` is a zero-byte file created on
13 September and attributed to `com.apple.Virtualization` **pid 62662**. That process is a virtual
machine, **not a git process** — an assistant's sandbox mounts this repository and one of its git
commands died leaving the lock behind. Nothing holds it. **Verify that before removing it** (see
TASK 1); do not remove a lock that a live `git` process owns.

**2. The five uncommitted files are prompts, and they belong on main.** Verified against
`origin/main`:

| file | state |
|---|---|
| `prompts/T1_target_revision_prepare_prompt.md` | on main at 242 lines; local is **278** — a revision adding a housekeeping task |
| `prompts/T2_revised_target_and_validated_posterior_prompt.md` | **absent from main** |
| `prompts/T3_determinism_measurement_prompt.md` | **absent from main** |
| `prompts/H1_handover_report_deck_and_repository_prompt.md` | **absent from main** |
| `prompts/H2_worktree_cleanup_prompt.md` | **absent from main** |

Every other prompt in the series is on main — P6 through P17, Q1, R3, Y3, T1. These four produced
the last week's results, and a collaborator reading `reports/T2_validated_posterior/`,
`reports/T3_determinism/` or `reports/H1_handover/` should be able to see what was asked as well as
what was found. **Commit them; do not discard them.**

**3. Two worktree stubs.** `../etcGEMs-k7` has a `HEAD` pointing at a branch that no longer exists,
so git declines both `remove` and `prune` — it needs a plain directory deletion, then a prune.
`../etcGEMs-k6` reads 1,172 deletions **because OneDrive Files-On-Demand has evicted its content to
the cloud, not because anything is lost**. Its files exist; they are simply not materialised
locally. Do not force anything there.

NOTE TO USER: launch in an auto-approving mode. It removes one stale lock file, makes one commit,
opens and merges one PR, deletes one directory and two branches. It stops rather than forcing at
every point where H2 stopped.

---

```
Work AUTONOMOUSLY. Print a short report. Standing rules and docs/RIGOUR.md carry over. Check exit
codes explicitly, never `cmd && check`. **Never --force. Never `git clean`. Never delete an
unmerged branch. Never touch codex/p17-inactive-prior or ../etcGEMs-p17-archive.**

TASK 0 - premise
- Confirm you are in the primary checkout and it is on t1/housekeeping at 3222b9d.
- Confirm nothing is running: no process with any worktree as its cwd; no log under any reports/
  written in the last ten minutes. If anything is running, STOP.
- **The archive check, by name, before anything else:** ../etcGEMs-p17-archive exists, is on
  codex/p17-inactive-prior at exactly ef1961b, the branch is not on origin, and its
  closure_manifest.json is readable. If any clause fails, STOP.

TASK 1 - the lock: verify stale, then remove
- Report `ls -l .git/index.lock` (expect zero bytes, dated 13 September).
- **Check no live git process owns it** before removing: `ps -p 62662 -o pid,comm=` and a scan for
  any running `git` process with this repository in its command line or cwd. Report what you find.
  If a live `git` process holds it, STOP and report - the lock is then real.
- If stale: `rm -f .git/index.lock`. Then `git status --porcelain` must succeed. Report its output
  and the ignored count separately, as H2 did, so venvs and run outputs are not confused with
  untracked work.
- Confirm the working tree contains exactly the five files named above and nothing else
  unexpected. **If anything else is modified or untracked, list it and STOP** - this prompt's
  premise is that the uncommitted work is those five prompts, and a sixth file means that premise
  is wrong.

TASK 2 - onto main, carrying the files
- `git switch main` - t1/housekeeping is an ancestor of main, so the modification and the four
  untracked files carry across cleanly. Then `git pull`. Two commands, two exit checks.
- Confirm HEAD equals origin/main and the five files are still present and still uncommitted.
- Confirm the checkout now contains docs/HANDOVER.md,
  reports/H1_handover/_output/calibration_investigation.pdf and
  reports/ecoli_deck/_output/deck.pdf - this is the tree a collaborator opens.

TASK 3 - commit the prompts by PR
- `git switch -c h3/prompts`. Stage ONLY the five prompt files, by name. Nothing else.
- One commit: "H3: the T2, T3, H1 and H2 prompts, and T1's housekeeping revision".
- Before opening the PR, report `git diff --stat main` - it must show exactly five paths, all
  under prompts/, and nothing under src/, strains/, configs/, docs/ or reports/.
- Open the PR, read its baseRefName to confirm it targets main, merge it in the house style, then
  `git switch main && git pull`. Report the PR number and the resulting commit.

TASK 4 - the two worktree stubs
- ../etcGEMs-k7: confirm git still declines `worktree remove` and `worktree prune` for it and say
  why (its HEAD names a branch that no longer exists). Then delete the directory itself
  (`rm -rf ../etcGEMs-k7`) and run `git worktree prune`. Confirm it is gone from
  `git worktree list`.
- ../etcGEMs-k6: report whether its content is still evicted. **Do not force.** If OneDrive has
  rehydrated it and `git -C ../etcGEMs-k6 status --porcelain` is clean apart from ignored files,
  remove it non-force and delete the k6/like-for-like branch if it is an ancestor of main. If it
  is still evicted, LEAVE IT, say so, and record the one-line command for later. An evicted
  worktree costs disk it is not using; forcing it risks a checkout git cannot distinguish from
  deletion.

TASK 5 - the remaining branches
- Delete t1/housekeeping non-force now that main holds its content. Delete k6/like-for-like only
  if TASK 4 removed its worktree.
- Confirm by name that main and codex/p17-inactive-prior both survive.
- Report the branch list before and after. The target end state is main and
  codex/p17-inactive-prior, plus k6/like-for-like only if its worktree could not be removed.

TASK 6 - the salvage folder, reported not deleted
- ../etcGEMs-work-salvage/ holds ~660 KB that H2 rescued from the old work tree: a superseded
  11 September deck render and its LaTeX intermediates. Confirm what is in it, confirm whether an
  equivalent render exists on main (reports/ecoli_deck/_output/deck.pdf is the current 62-page
  one), and **report whether it is safe to delete. Do not delete it.** That is the PI's call and
  it costs 660 KB to leave.

TASK 7 - verify and record
- `git worktree list`: the primary on main, ../etcGEMs-work on main, the archive at ef1961b, and
  ../etcGEMs-k6 only if TASK 4 left it.
- `git branch`: main and codex/p17-inactive-prior, plus k6/like-for-like if applicable.
- The archive re-checked by name: path, branch, commit ef1961b, absent from origin, manifest
  readable.
- Both gates from the primary tree on main: 79/79 and 60/60.
- docs/OPEN_ITEMS.md: close H2's three follow-up items with what was done, and add one line
  recording that the four prompts are now on main. Commit on a branch, PR, merge - or directly if
  the house convention allows a record line. Report the commit.
- Confirm `git status --porcelain` in the primary tree is empty.

VERIFY (report all)
1. TASK 0: location and branch; nothing running; the archive check by name.
2. TASK 1: the lock's size and date; the process check and what it found; the status output after
   removal with ignored counted separately; confirmation the working tree held exactly the five
   expected files.
3. TASK 2: on main at origin/main; the five files still present; the three handover artefacts
   present.
4. TASK 3: `git diff --stat main` showing five paths under prompts/ and nothing else; the PR
   number, its base, the merge commit.
5. TASK 4: k7 deleted and pruned; k6's eviction state and what was done or deferred, with the
   command recorded if deferred.
6. TASK 5: branches before and after; main and the archive confirmed surviving by name.
7. TASK 6: the salvage folder's contents and the safe-to-delete judgement; confirmation it was
   NOT deleted.
8. TASK 7: the worktree and branch lists; the archive re-verified; both gates; the OPEN_ITEMS
   entries and their commit; a clean `git status`.

CONSTRAINTS
- The lock is removed only after it is shown that no live git process owns it.
- A sixth uncommitted file stops the task: the premise is five prompts, and more means the
  premise is wrong.
- Only the five named prompt files are staged. Nothing under src/, strains/, configs/, docs/ or
  reports/ is committed by TASK 3.
- codex/p17-inactive-prior and ../etcGEMs-p17-archive are protected by name at every step.
- Never --force, never `git clean`, never delete an unmerged branch, never delete main.
- The salvage folder is reported, never deleted.
- An evicted OneDrive worktree is left alone, never forced.
```
