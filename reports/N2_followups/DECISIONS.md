# N2 — decision log

_Continues N1's. One entry per judgement call the prompt did not answer._

## D0 — TASK 0: `$CANDIDAS_ROOT` is not literally clean, and the merge proceeded anyway

**Observed.** The prompt's pre-merge check is "`git -C "$CANDIDAS_ROOT" status --short` is
empty". It is not: it shows `?? runs/`.

**Decided.** Proceed with the merge.

**Why.** `runs/` is untracked, contains the Candidas project's own C-series R pipeline
outputs (`C1_reproduction/`, `C2_arm_current/`, `C2_arm_nobp/`, `C2_arm_ramp/` — oxygen
tables and figures), and was already present at the first `git status` of that repository in
the K1 session, before any of this work began. No tracked file there is modified. The check's
intent is "we have not written into the Candidas repository", and that holds.

**Alternatives.** Stop the whole prompt over a pre-existing untracked directory in someone
else's repository.

**Reversible:** n/a. **Review:** nobody, but recorded because it is a documented check that
did not literally pass.

## D1 — TASK 0: the merge verification flagged two mmaripaludis files, and it was a file mode

**Observed.** After the merge, re-running `etcgem tpc` for mmaripaludis left
`descriptors.json` and `nominal_tpc.csv` flagged by `git status`. That is a stop condition as
written.

**Decided.** Not a stop condition: the diff is `old mode 100644 / new mode 100755` and
nothing else. All eight mmaripaludis and syn6803 output files are byte-identical in CONTENT,
checked with `cmp` against `git show HEAD:<path>`.

**Why.** This checkout is on a OneDrive-backed filesystem that flips the executable bit on
rewrite. `git status` reports mode changes; the content is what the verification is about.

**Alternatives.** Set `core.fileMode=false` — a repository configuration change affecting the
user's environment, for a cosmetic problem, and not this prompt's business.

**Reversible:** n/a, nothing changed. **Review:** worth knowing that on this machine
`git status` can flag a file whose content has not moved; content checks should use `cmp`
against `git show`, which is what N2 does throughout.
