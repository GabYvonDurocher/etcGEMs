# Claude Code prompt — R1: assess the repository state and make `main` fit to send (autonomous, short)

Run from the project root (`.../MICROADAPT/etcGEMs`). Mechanical and quick — well under an hour. Its
purpose is to make a plain `git pull` on `main` give a collaborator everything they need, and to
report honestly on anything it cannot fix.

**Two runs may be live and this prompt must not disturb either.**

1. **P6 owns the primary working tree**, which is on `p6/convergence` and is mid-chain on a
   configuration-D fit. Do NOT `git switch`, `git checkout`, `git stash`, `git reset`, `git clean` or
   `git pull` in the primary working tree, and do NOT write anything under `strains/eciML1515/`.
   Anything needing a checkout happens in a SEPARATE WORKTREE.
2. **Y1 may be running in `../etcGEMs-synthesis`** on branch `y1/yeast-audit`. Do not touch that
   worktree beyond reading its state. Do not restart it, do not commit in it, do not merge its branch.

**Concurrency.** P6 commits after each fit, so `.git` is in use by another process. If any git command
fails on `index.lock` or similar, WAIT and RETRY. **Never delete a lock file and never pass `--force`.**
A lock is another process working, not a stale artefact.

**The known gaps, as of the last inspection.** Verify each rather than trusting this list — it may
have moved.
  * `origin/main` is `5ddc23e`. It carries all twenty-one report directories including
    `reports/synthesis`, but **not the rendered PDF**. The PDF and a README live on branch
    `s1b/synthesis-pdf` at `80d76c6`, in an OPEN, UNMERGED PR (believed #16 — confirm the number
    from the API rather than trusting it). So a collaborator who pulls today gets `synthesis.qmd`
    and no way to read it without a Quarto and LaTeX toolchain.
  * **The prompt files are incomplete on `main`.** `prompts/` there has K1, K2, A1, N1–N3 and the
    Parsa port series, but K4 through K9, P4, P5, P6, S1, S1b and Y1 exist only as UNTRACKED files
    in the primary working tree. The reports reference them and are much harder to follow without.
  * `y1/yeast-audit` appears to sit at `80d76c6` with no commits of its own, and is branched from
    `s1b/synthesis-pdf` rather than from `main`. Establish whether Y1 has actually started.

NOTE TO USER: launch in an auto-approving mode. It merges one PR and pushes one commit, both of
which are documentation only. It runs no models.

---

```
Work AUTONOMOUSLY. Print a short report at the end. Standing rules carry over. Check exit codes
explicitly, never `cmd && check`. Do not push anything to `main` except what TASK 2 authorises.

TASK 0 - establish the state before changing any of it
Report, from commands rather than assumption:
- The primary working tree's branch and HEAD; confirm it is P6's and leave it alone.
- `git worktree list`; the branch and HEAD of every worktree; whether each directory actually
  exists on disk. A worktree reported "prunable" may simply be unreadable from where you are
  standing -- check the path before concluding it is gone, and do NOT prune anything.
- `origin/main`'s commit; every open PR with its number, branch, head commit and mergeable state.
- Every untracked and modified path in the primary working tree, grouped: prompts, stray artefacts,
  run outputs. Name them; do not act yet.
- Whether P6 is live: the most recent line and mtime of `reports/P6_convergence/run_fits.log`, and
  which fit it is on. Report it; do not interfere.

TASK 1 - merge the synthesis PDF into main, server-side only
- Identify the PR whose head is `s1b/synthesis-pdf`. Confirm from the API, do not assume a number.
- Confirm its diff against `origin/main` is CONFINED to `reports/synthesis/` and touches nothing
  under `strains/` or `src/`. If it touches either, STOP and report -- that would mean the branch is
  not what this prompt believes.
- Merge it server-side with `gh pr merge <n> --merge`. Match whatever merge style the previous PRs
  used; check how #14 and #15 went in.
- **Do NOT pass `--delete-branch`.** `s1b/synthesis-pdf` exists locally and is the base of
  `y1/yeast-audit`; leave both alone.
- Confirm from the API that it is MERGED, and report the new commit on `origin/main`.
- If the merge is blocked, STOP and report why. Do not resolve it by switching branches locally.

TASK 2 - put the missing prompts on main, without touching the primary working tree
The reports on `main` cite prompts that are not on `main`. Fix that.
- Create a temporary worktree from `origin/main` at a path OUTSIDE the repository and outside /tmp
  if /tmp is pruned on this machine -- e.g. `../etcGEMs-housekeeping`.
- Copy in every prompt file that exists in the primary working tree but not on `main`. List exactly
  which files those are before copying, and report the list.
- **Prompts only.** Do NOT commit stray artefacts (e.g. `brenda_sdh.html`), run outputs, scratch
  files, or anything under `strains/` or `reports/`. If a file's category is unclear, leave it and
  report it.
- Read two or three of the existing committed prompts first and confirm the new ones match the
  house convention for that directory (naming, and whether anything is stripped before committing).
- Commit on a branch, push, open a PR, and merge it the same way as TASK 1. One commit, message in
  the house style. Report the PR number and the resulting commit on `origin/main`.
- Remove the temporary worktree when finished. Do NOT remove `../etcGEMs-synthesis`.

TASK 3 - establish whether Y1 is actually running
- Read `../etcGEMs-synthesis`: does the directory exist, what branch is it on, does
  `reports/Y1_yeast_audit/` exist, are there commits on `y1/yeast-audit` beyond `80d76c6`, and is
  any process writing there?
- Report one of: RUNNING (with what it has produced so far), STARTED-BUT-STALLED, or NEVER-STARTED.
- **Do NOT restart it, do not commit in that worktree, do not merge its branch.** If it never
  started, say so and say what would be needed. That is a decision for the user, not a fix.

TASK 4 - verify the collaborator experience, which is the point of the whole task
Do not infer this from the state -- test it.
- Clone `origin/main` fresh into a scratch directory (a clone, not a worktree; it must be
  independent of this repository).
- In that clone confirm the presence and non-emptiness of:
    reports/synthesis/_output/synthesis.pdf   (and that it is a valid PDF -- report its page count)
    reports/synthesis/synthesis.qmd
    reports/synthesis/evidence.csv            (report its row count)
    reports/synthesis/README.md
    docs/OPEN_ITEMS.md
    every prompt referenced by any report under reports/
- For the last item: grep the reports for references to prompt filenames and confirm each exists in
  the clone. Report any that do not. This is the check that catches what TASK 2 missed.
- Delete the scratch clone afterwards.

TASK 5 - report, and flag what you could not fix
- State the final commit on `origin/main` and what a collaborator gets from `git pull`.
- List anything still missing, stale or inconsistent that you did NOT fix, and why -- particularly
  anything that would need the primary working tree, which is unavailable while P6 runs.
- Note that `prompts/` on main contains filename collisions across projects (P1, P2, P3 exist with
  different meanings for the methanogen, phototroph and Parsa-port series). Report whether this is
  actually confusing in practice. RECOMMEND, do not rename anything.
- Confirm the primary working tree is still on `p6/convergence`, still clean of your changes, and
  that P6 is still running on the same fit or has progressed normally.

VERIFY (report all)
1. TASK 0: the state table -- branches, worktrees, open PRs, untracked files, P6's live position.
2. TASK 1: the PR number, its diff confined to reports/synthesis/, MERGED confirmed from the API,
   the new commit on origin/main, and that the branch was NOT deleted.
3. TASK 2: the exact list of prompt files added; the PR; the resulting commit; confirmation that
   nothing outside prompts/ was committed and the temporary worktree was removed.
4. TASK 3: Y1's status as one of the three verdicts, with the evidence.
5. TASK 4: the fresh clone's contents -- PDF page count, evidence.csv row count, and any report-
   referenced prompt still absent.
6. TASK 5: the primary working tree untouched and on p6/convergence; P6 still running.

CONSTRAINTS
- The primary working tree is P6's. No switch, checkout, stash, reset, clean or pull there.
  Everything needing a checkout happens in a separate worktree.
- Never delete a git lock file, never use --force. Contention means another process is working.
- Documentation only. Nothing under strains/ or src/ is committed, moved or modified.
- Do not touch, restart or merge Y1. Do not prune any worktree.
- The collaborator check is a fresh clone, not an inspection of local state.
- Anything you cannot fix is reported, not worked around.
- Autonomous; commit in parts, prefixed "R1: ".
```
