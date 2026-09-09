# Y1 PART F — housekeeping

## 1. Should `../etcGEMs-synthesis` become a standing second worktree?

**Recommendation: yes, keep it — and rename it.** Not acted on; this is a recommendation only.

**The case for.** Y1 is the third run in a row that would otherwise have waited on the main
checkout. It ran end to end while `p6/convergence` held the main checkout with a long MCMC job,
and it needed nothing from there but the shared `.venv` interpreter and one PDF in `refs/`. Long
runs block the main checkout regularly — P4's nine fits, P5's LB sweep, P6's convergence run — and
each of those blocks is measured in hours or days. A second worktree costs one directory and no
duplicated history.

**The case against, and why it does not hold.** The usual objection is drift between two trees.
That is a real risk, and it is why the argument is for **one** standing second worktree rather than
a habit of making them: a second tree that is always there and always merged back through PRs is a
lane, not a fork; a third and fourth would be a mess.

**Two conditions.**

* **Rename it.** `etcGEMs-synthesis` was named for S1 and has now been used for S1b and Y1, neither
  of which is synthesis. The name will mislead the next person. `etcGEMs-work` was suggested in the
  Y1 prompt and is right.
* **Never leave it on a branch that has diverged and been forgotten.** Merged or deleted at the end
  of each run; on `main` between runs.

**One thing that would need checking before it becomes routine.** The shared `.venv` lives in the
main checkout (`etcGEMs/.venv`), so the second worktree borrows an interpreter from a directory a
long run may be actively using. Read-only in practice and it caused no trouble here, but if the
worktree becomes standing, the venv should move somewhere neutral or be duplicated. Recorded as an
item, not acted on.

## 2. `docs/OPEN_ITEMS.md`

Updated: Y1's outcome recorded, and two new items — the posterior re-run of PART C, and the venv
location above.

## 3. The main checkout was not touched

`git worktree list` at the end of Y1:

```
.../etcGEMs             158b6f5 [p6/convergence]
.../etcGEMs-synthesis   <Y1 HEAD> [y1/yeast-audit]
```

The main checkout is on `p6/convergence` at `158b6f5`, where Y1 found it, and `git status` there
shows only the untracked prompt files that were already present. Y1 read two things from it and
wrote nothing: the shared `.venv` interpreter, and `refs/Lietal2021NatComms.pdf` for PART D.
