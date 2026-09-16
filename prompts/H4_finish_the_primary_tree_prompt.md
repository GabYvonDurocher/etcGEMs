# Claude Code prompt — H4: clear the abandoned merge, put the primary tree on main, commit the six prompts, remove the k6 stub (autonomous, ~20 min)

Run from the **primary checkout**, `.../MICROADAPT/etcGEMs`. It is on `t1/housekeeping` at
`3222b9d`, mid-merge, with thirty uncommitted entries. The lock is already cleared. **Nothing is
running.** No fits, no science, no model or config change.

**Read first:** `docs/OPEN_ITEMS.md` §0 — H2's and H3's follow-ups are recorded there with their
commands. Prefer what is written there over this prompt if they differ, and report the difference.

**This prompt exists because H3's premise was wrong and its gate caught it.** H3 asserted five
uncommitted files on the strength of a `git status` that had silently failed under the lock and
returned nothing. H3 found thirty entries and an abandoned merge, stopped, and did not decide for
the PI. **The PI has now decided.** The three modified tracked files are all safe to discard, and
the reasoning is below so this run does not have to take it on trust.

**The state H3 established, to be re-verified rather than assumed:**

*Three modified tracked files:*
| file | state | disposition |
|---|---|---|
| `docs/RIGOUR.md` | byte-identical to main | `checkout --` is a no-op |
| `reports/P17_inactive_prior/ARCHIVE.md` | byte-identical to main | `checkout --` is a no-op |
| `docs/OPEN_ITEMS.md` | 653 lines, byte-identical to the version at `86d182a`; main's is 749 | **strictly older**, not divergent — main contains it plus everything since |

*Six untracked prompt files* — T2, T3, H1, H2, H3 and this one are absent from main; T1 is on main
at 242 lines against a local 278. **All belong on main**: every other prompt in the series is
committed, and they are what produced the last week's reports.

*Twenty-one other untracked items* — `brenda_sdh.html`, two config experiments, several
`transfer_*` output directories, eight `.gitkeep` placeholders, a `dynesty_proof.save`, and a
leftover `reports/T2_validated_posterior/` redirect directory. **Untracked files carry across a
`switch` untouched**, so they neither block anything nor get lost. They are reported, not resolved.

*An abandoned merge:* `MERGE_HEAD` `0034248` from a `Merge branch 'main' into p13/support` on
10 September. Both it and `HEAD` are already ancestors of `main` and there are **zero conflicted
paths**, so the merge is obsolete — but `git switch` refuses while it stands.

**And `../etcGEMs-k6` has a clean route that does not need `--force`.** H3 showed its 1,172 missing
files are all *tracked-and-absent* with **zero untracked**, so there is provably nothing unique in
it. Restoring them makes it clean by git's own definition, after which it removes non-force. (My
earlier "OneDrive eviction" diagnosis was wrong — an evicted file resolves as a placeholder, and
the probe file is not present at all.)

NOTE TO USER: launch in an auto-approving mode. One merge abort, three file restores, one branch
switch, one commit and PR, one worktree restored-and-removed, two branches deleted.

---

```
Work AUTONOMOUSLY. Print a short report. Standing rules and docs/RIGOUR.md carry over. Check exit
codes explicitly, never `cmd && check`. **Never --force. Never `git clean`. Never delete an
unmerged branch. Never touch codex/p17-inactive-prior or ../etcGEMs-p17-archive.**

TASK 0 - premise, re-verified
- Confirm you are in the primary checkout on t1/housekeeping at 3222b9d, and that
  `git status --porcelain` now RUNS (the lock is cleared). If it fails, STOP.
- Confirm nothing is running: no process with any worktree as cwd; no log under any reports/
  written in the last ten minutes.
- **Archive check by name, before anything else:** ../etcGEMs-p17-archive exists, on
  codex/p17-inactive-prior at exactly ef1961b, absent from origin, closure_manifest.json readable.
  If any clause fails, STOP.
- Re-verify each claim in the table above rather than trusting it:
  * `git diff --stat` for the three modified files, and for each, `git diff main -- <path>` to
    establish byte-identity or staleness. **Report the actual result.** If RIGOUR.md or ARCHIVE.md
    is NOT byte-identical to main, or if OPEN_ITEMS.md is NOT an ancestor version, STOP and report
    - the PI's decision rested on those facts.
  * the merge state: `MERGE_HEAD`, its commit, whether it and HEAD are ancestors of main, and the
    conflicted-path count (expect zero).
  * the untracked list, grouped as: the six prompts, and everything else.
- If the untracked set contains anything that is not a prompt and not in H3's twenty-one, list it
  and STOP.

TASK 1 - clear the abandoned merge
- `git merge --quit` (NOT `--abort`: abort would reset the working tree and discard the six
  prompts). Confirm MERGE_HEAD is gone and that `git status` no longer reports a merge.
- Confirm the working tree is otherwise unchanged: the same thirty entries, the six prompts still
  present. Report.

TASK 2 - discard the three stale tracked files
- `git checkout -- docs/RIGOUR.md reports/P17_inactive_prior/ARCHIVE.md docs/OPEN_ITEMS.md`.
- Confirm afterwards that `git diff --stat` is empty and the six prompts are still untracked and
  still present. Report.

TASK 3 - onto main
- `git switch main` then `git pull` - two commands, two exit checks. Confirm HEAD equals
  origin/main and that the six prompt files carried across and are still untracked.
- Confirm docs/OPEN_ITEMS.md is now main's 749-line version, and that the checkout contains
  docs/HANDOVER.md, reports/H1_handover/_output/calibration_investigation.pdf and
  reports/ecoli_deck/_output/deck.pdf. This is the tree a collaborator opens.

TASK 4 - commit the six prompts by PR
- `git switch -c h4/prompts`. Stage ONLY the six prompt files, by name:
  T1_target_revision_prepare, T2_revised_target_and_validated_posterior,
  T3_determinism_measurement, H1_handover_report_deck_and_repository, H2_worktree_cleanup,
  H3_finish_the_cleanup, and H4 (this prompt) if it is present in the tree - state which you
  found and staged.
- One commit: "H4: the T2, T3, H1, H2, H3 and H4 prompts, and T1's housekeeping revision".
- **Before opening the PR**, report `git diff --stat main`. It must show ONLY paths under
  `prompts/` - nothing under src/, strains/, configs/, docs/ or reports/. If it shows anything
  else, STOP.
- Open the PR, read its baseRefName to confirm it targets main, merge in the house style, then
  `git switch main && git pull`. Report the PR number and the resulting commit.

TASK 5 - the k6 stub, restored then removed
- `git -C ../etcGEMs-k6 checkout -- .` to restore the 1,172 tracked-and-absent files.
- `git -C ../etcGEMs-k6 status --porcelain` must now be empty apart from ignored paths. **If it is
  not, STOP and report** - do not remove a worktree that is not clean.
- `git worktree remove ../etcGEMs-k6` (non-force). Then `git worktree prune`.
- `git branch -d k6/like-for-like` - non-force, so it only succeeds if merged.
- Report each step and the space recovered.

TASK 6 - the last branch
- `git branch -d t1/housekeeping`, non-force.
- Confirm by name that `main` and `codex/p17-inactive-prior` both survive.
- Report the branch list before and after. Target end state: exactly two local branches.

TASK 7 - verify and record
- `git worktree list`: exactly three - the primary on main, ../etcGEMs-work on main, and the
  archive at ef1961b.
- `git branch`: exactly main and codex/p17-inactive-prior.
- The archive re-checked by name: path, branch, commit ef1961b, absent from origin, manifest
  readable, size.
- Both gates from the primary tree on main: 79/79 and 60/60.
- `git status --porcelain` in the primary tree: report it. The twenty-one untracked artefacts are
  expected to remain; list them so the PI can tidy them separately, and do NOT delete any.
- docs/OPEN_ITEMS.md: close H2's and H3's outstanding follow-ups with what was done; one line
  recording that the prompt series is now complete on main; and one line under section 4 adding
  the hazard this sequence exposed, in its general form: **"a command that fails can return empty
  output; empty is not a result. Check the exit code and the stderr before reading silence as
  cleanliness."** Commit and push per the house convention; report the commit.
- ../etcGEMs-work-salvage/: report its contents and that it remains, untouched. Do not delete it.

VERIFY (report all)
1. TASK 0: location, branch, `git status` working; nothing running; the archive by name; each
   table claim re-verified with its actual result; the untracked set grouped.
2. TASK 1: merge cleared with `--quit`; the six prompts still present.
3. TASK 2: the three files restored; `git diff --stat` empty; the prompts still there.
4. TASK 3: on main at origin/main; the prompts carried across; OPEN_ITEMS at 749 lines; the three
   handover artefacts present.
5. TASK 4: `git diff --stat main` showing only prompts/; which prompt files were staged; the PR
   number, its base, the merge commit.
6. TASK 5: k6 restored, clean, removed non-force, branch deleted; space recovered.
7. TASK 6: branches before and after; main and the archive confirmed by name.
8. TASK 7: three worktrees; two branches; the archive re-verified with size; both gates; the
   remaining untracked list; the OPEN_ITEMS entries and their commit; the salvage folder reported
   and intact.

CONSTRAINTS
- `git merge --quit`, never `--abort`. Abort resets the working tree and would discard the six
  prompts.
- The three tracked files are discarded only after TASK 0 re-verifies they are byte-identical or
  strictly older. If either fact fails, stop.
- Only prompt files are staged in TASK 4, by name, and the diff is proved before the PR opens.
- k6 is restored to clean and removed non-force, never forced.
- The twenty-one untracked artefacts and ../etcGEMs-work-salvage/ are reported, never deleted.
- codex/p17-inactive-prior and ../etcGEMs-p17-archive are protected by name at every step.
- Never --force, never `git clean`, never delete an unmerged branch, never delete main.
```
