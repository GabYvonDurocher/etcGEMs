# Claude Code prompt — S1b: merge the synthesis and render it somewhere I can read it (autonomous, short)

Run from the project root (`.../MICROADAPT/etcGEMs`). Mechanical, a few minutes.

**Two constraints that shape how this must be done.**

1. **P6 is running and owns the main checkout**, which is on `p6/convergence`. Do NOT `git switch`
   in the primary working tree, do not merge locally, and do not write anything under
   `strains/eciML1515/`. The merge must happen SERVER-SIDE.
2. **The rendered PDF is not committed** — `s1/synthesis` carries `synthesis.qmd`, `evidence.csv`,
   the figure and the build scripts, but no PDF. The worktree that rendered it was under `/tmp` and
   is now prunable, so the output is probably gone. It has to be re-rendered.

---

```
Work AUTONOMOUSLY. Print a short summary. Check exit codes explicitly, never `cmd && check`.

TASK 1 - merge PR #15 server-side
- `gh pr merge 15 --merge --delete-branch` (or `--squash` if that is this repository's habit — check
  how the previous PRs were merged and match it).
- Do NOT switch branches, pull, or rebase in the primary working tree. `git fetch origin` is fine.
- Confirm from the API that the PR is MERGED and report the resulting commit on origin/main.
- If the merge is blocked for any reason, STOP and report why. Do not resolve it by switching
  branches locally.

TASK 2 - render it in a fresh worktree, outside /tmp
- Create a worktree from `origin/main` at a stable path that will survive — e.g.
  `../etcGEMs-synthesis` beside the main checkout, NOT under /tmp.
- Render `reports/synthesis/synthesis.qmd` there. Verify: the PDF exists, opens, has no missing
  figure and no unresolved cross-reference. Report the page count and the absolute path.
- If Quarto or a LaTeX dependency is missing in that worktree, say exactly what and stop — do not
  install anything into the primary environment while P6 is running.

TASK 3 - make it easy to read again
The PDF being uncommitted is why it vanished the first time.
- Check whether `reports/synthesis/.gitignore` excludes the PDF, and whether the OTHER report
  directories in this repository commit theirs. Match the established convention — if the house
  habit is to commit rendered reports, commit this one on a small branch and open a PR; if the habit
  is to gitignore them, leave it and say so.
- Either way, add one line to `reports/synthesis/README.md` (create it if absent) giving the exact
  command to re-render, so nobody has to reconstruct it.
- Do NOT push to main. Any commit here goes on a branch with a PR.

TASK 4 - tell me where it is
- Print the absolute path of the PDF, its page count, and the command to re-render it.
- Print the path of `evidence.csv` too — it is the document's backing table and worth opening
  alongside.

VERIFY (report all)
1. PR #15 merged server-side; the commit on origin/main; primary working tree still on
   `p6/convergence`, untouched.
2. The worktree path; the PDF path and page count; render clean.
3. The gitignore/commit convention found and what was done about it.
4. Confirmation that nothing under `strains/eciML1515/` was written and P6 was not disturbed.

CONSTRAINTS
- Server-side merge only. No branch switching in the primary working tree.
- The render worktree lives beside the repository, not in /tmp.
- Nothing installed into the running environment.
- Autonomous.
```
