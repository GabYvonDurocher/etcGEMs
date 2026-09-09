# Claude Code prompt — R2: merge what is open, reconcile the local machine with `main`, and prove they match (autonomous, short)

Run from the project root (`.../MICROADAPT/etcGEMs`). **Nothing is running and nothing is
outstanding** — P6 was halted under addendum 6 and its diagnosis is on PR #18; Y1 finished and is on
PR #19; P7 has NOT started. This is the first moment since the merge began that the primary working
tree can be switched freely. Use it to leave the repository in a state where `main` on the machine,
`main` on origin, and a fresh clone are the same thing.

**State at the last inspection — verify each, act on none until TASK 0 confirms.**
  * Primary tree: `p6/convergence` at `158b6f5`, six commits ahead of `origin/main`. PR #18 open.
  * `../etcGEMs-synthesis`: worktree on `y1/yeast-audit`, eight commits ahead. PR #19 open. Note
    #19 touches `src/etcgem/sink_audit.py` (the Yeast7 matcher fix) — it is NOT documentation-only.
  * Both PRs touch `docs/OPEN_ITEMS.md`, `reports/report_status.yaml` and stamp files, so the second
    merge will probably conflict. Those files are additive records; a conflict is resolved by
    keeping BOTH sides, never by dropping either.
  * Merged-and-lingering local branches: `r1/prompts`, `rename-report-dir`, `reorg-etcgem`,
    `repo-restructure`, `s1b/synthesis-pdf`. Remote: `r1/prompts`, `s1/synthesis`, `s1b/synthesis-pdf`.
  * Untracked in the primary tree: `brenda_sdh.html` (stray), `prompts/P7_walker_test_prompt.md`
    (new, should be committed), and eleven prompts that are already on `main` and will resolve
    themselves once the tree is on `main`.

NOTE TO USER: launch in an auto-approving mode. It merges two PRs, switches the primary tree to
`main`, deletes merged branches, and opens and merges one small housekeeping PR. It runs no models.
It deletes nothing that is not a merged branch; the stray file is reported, not removed.

---

```
Work AUTONOMOUSLY. Print a short report. Standing rules carry over. Check exit codes explicitly,
never `cmd && check`. Never delete a git lock file, never --force, never `git clean`.

TASK 0 - confirm the premise
- No process has the primary tree or ../etcGEMs-synthesis as cwd; no log under reports/ written in
  the last ten minutes. If anything is running, STOP.
- `git fetch origin --prune`. Report origin/main, every open PR (number, head, mergeable), every
  local and remote branch with whether it is merged into origin/main, `git worktree list` with
  whether each path exists on disk, and `git status --porcelain` in both trees.

TASK 1 - merge the two open PRs, in order, server-side
- #18 first (p6/convergence), then #19 (y1/yeast-audit). Match the merge style of #14-#17.
- If #19 reports a conflict after #18 lands: rebase y1/yeast-audit onto origin/main IN THE
  ../etcGEMs-synthesis WORKTREE (nothing is running there now), resolve by keeping both sides of
  every additive file (OPEN_ITEMS.md, report_status.yaml, stamps), re-run scripts/stamp_reports.py
  so the stamps are regenerated rather than hand-merged, push, and merge. Report every file you
  resolved and how.
- Confirm both MERGED from the API. Report the final commit on origin/main.

TASK 2 - bring the primary tree onto main
- `git switch main`, `git pull`. Confirm HEAD equals origin/main and the tree is clean apart from
  the two genuinely new untracked files.
- The eleven prompts that were untracked on p6/convergence should now be tracked and identical.
  Confirm `git status` no longer lists them. If any still shows as untracked or modified, the copy
  on main differs from the working file: report the diff and STOP on that file - do not overwrite
  either way.
- `brenda_sdh.html`: report what it is (size, first lines, anything it references). Do NOT delete
  it and do NOT commit it. If it looks like a BRENDA download used by a report, say which; if it
  looks like a stray, say so. The user decides.

TASK 3 - one housekeeping PR, then merge it
On a branch `r2/reconcile`, one commit:
- Add prompts/P7_walker_test_prompt.md and this prompt.
- docs/OPEN_ITEMS.md: add the following, in the sections named, in the house style:
    section 4 (standing hazards), two lines:
      * "An audit that finds nothing must first prove it can find something. Y1's matcher was
        blind to Yeast7 naming and would have returned a clean bill of health for the wrong
        reason; proved inert on all seven strains before use."
      * "A scan's conclusion is scoped to the points scanned. P6's five-temperature O2 FVA read
        'unique' at 25-44 C; the degeneracy lives at 20 and 35-50 C. See D3a."
    section 2 (ready), one item: "Y1 PART C re-run at the Zenodo posterior rather than the prior,
      before the 10.09 / 0.81 C numbers are quoted. ~1 h."
    section 2 (ready), one item: "P7 walker test (prompts/P7_walker_test_prompt.md). Decides
      whether D6's options (i)-(iii) are needed."
    section 1 (waiting on people), one item under the PI: "E/F tie-break: pFBA, min-O2 or max-O2
      for the respiration likelihood on an LP face (D3a). Modelling decision."
    section 1 (waiting on people), one item under the PI: "Whether a Li-style calibration
      (predictor as wide prior, narrowed against the measured Candida TPCs) is worth attempting,
      given the A1 noise floor of 0.043 C between clades. See reports/Y1_yeast_audit/ PART D."
    Update 1.12 to reflect D6: not a budget problem; sampler-limited; awaiting P7.
- Re-run scripts/stamp_reports.py; confirm reports/report_status.yaml has an entry for every
  report directory including Y1 and P6, and no stale stamp remains.
- Push, PR, merge (same style). Report the commit. `git switch main && git pull` afterwards -
  as two commands with two exit checks.

TASK 4 - delete what is merged, keep what is not
- Delete every LOCAL branch that is an ancestor of origin/main, except main. Delete the same
  branches on origin where they still exist, plus the two just merged (p6/convergence,
  y1/yeast-audit) once TASK 1 has confirmed they are merged. Use non-force deletion only; if git
  refuses because a branch is not merged, that is information - report it and leave the branch.
- Report the branch list before and after, local and remote.

TASK 5 - the second worktree
- Read Y1's PART F recommendation in reports/Y1_yeast_audit/report.md and follow it. If it made
  none, or recommended keeping it: keep it, `git worktree move` it to ../etcGEMs-work, switch it to
  a clean detached checkout of main (not a branch, so it cannot drift), and say so. The reason to
  keep it: long runs block the primary tree for hours and both S1b and Y1 needed a second tree.
  If it recommended removal: `git worktree remove` (non-force; if it refuses, report why and stop).
- Either way, `git worktree prune` is NOT run; report `git worktree list` afterwards.

TASK 6 - prove local and remote match
- Fresh clone of origin/main into a scratch directory outside the repository.
- `git rev-parse HEAD` in the clone, the primary tree and the second worktree (if kept): all three
  identical.
- `git diff --stat` between the clone's tree and the primary tree's tracked files: empty.
- `git status --porcelain` in the primary tree: only brenda_sdh.html, or nothing if the user has
  removed it.
- In the clone, confirm the presence of reports/Y1_yeast_audit/report.md,
  reports/P6_convergence/DECISIONS.md with entries D3a and D6, reports/synthesis/_output/
  synthesis.pdf, prompts/P7_walker_test_prompt.md, and that src/etcgem/sink_audit.py contains the
  Yeast7 matcher fix (grep for the identifier Y1 used).
- Run the framework's test suite or gate once from the clone, whichever is the house check that
  the ports are intact, and report the pass count. The sink_audit change came in through #19 and
  this is the first time it is on main.
- Delete the scratch clone.

VERIFY (report all)
1. TASK 0: nothing running; the state table.
2. TASK 1: #18 and #19 MERGED; any conflict and its resolution file by file; the commit.
3. TASK 2: primary tree on main == origin/main; the eleven prompts resolved; brenda_sdh.html
   described and left in place.
4. TASK 3: the housekeeping PR merged; OPEN_ITEMS additions quoted; stamps regenerated with no
   stale entry.
5. TASK 4: branches before/after, local and remote; anything git refused to delete.
6. TASK 5: what Y1 recommended and what was done; `git worktree list`.
7. TASK 6: three identical HEADs; empty diff; clean status; the five files present; the gate
   pass count.

CONSTRAINTS
- Never --force, never git clean, never delete a lock file, never delete an unmerged branch.
- Conflicts in additive files keep both sides; stamps are regenerated, not hand-merged.
- The stray file is reported, not removed.
- One housekeeping PR; no other content changes.
- Autonomous.
```
