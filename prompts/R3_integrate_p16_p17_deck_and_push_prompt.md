# Claude Code prompt — R3: integrate P16, P17, the deck and Q1 into main, and push (autonomous, ~2–3 h)

Run from the project root (`.../MICROADAPT/etcGEMs`). **Nothing is running anywhere.** This is the
first push-enabled session since P15 merged, and everything since sits on four unpushed or
partly-pushed branches. Read, in this order, before touching anything:
`docs/HANDOVER_2026-09-13.md`, `docs/INTEGRATION_STATE.md`, `docs/RIGOUR.md` and
`docs/CLOSURE_VERIFICATION_2026-09-13.md` — all on `codex/p17-inactive-prior` at
`ef1961bfc4e26a9e69eb51fe8d0b8dbad109e997`. They were written by the session that closed P17 and
they are the authority on what is where. Use `git show <ref>:<path>` to read them; do not switch
the primary tree until TASK 1 says to.

**The state, verified by that session and re-verified by this one before it acts:**

| branch | head | ahead of main | where |
|---|---|---:|---|
| `p16/reduced` | `191b4b0` | 6 | primary tree, **32 uncommitted files** |
| `codex/p17-inactive-prior` | `ef1961b` | 6 + 25 + closure | `/private/tmp/etcGEMs-p17`, clean, branched from `191b4b0` |
| local `e2/deck` | `0215a16` | 26 | `../etcGEMs-work`; **6 E6 commits beyond `origin/e2/deck`** |
| `origin/e2/deck` | `bc356e3` | 20 | pushed E5 tip |
| `q1/n0-check` | `b163bad` | 25 | on origin; **stacked on `bc356e3` (E5), not on local E6** |

`origin/main` and local `main` are both `dc5b4cc` (the P15 merge).

**The size problem, and the decision already taken.** `origin/main` tracks 303 MB. The P17 tip
tracks **2,962 MB** — P17 alone adds 2,639 MB under `reports/P17_inactive_prior/`, because the
closing session committed every checkpoint, array and log (1,906 files, all hashed in
`closure_manifest.json`). `unif_benchmark.log` is 104.7 MiB and **GitHub will reject the push**;
`global_coordinate_replicates.log` is 82.3 MiB. No LFS is configured. **The PI's decision:**
build a *curated* P17 commit containing reports, scripts, decisions, documents and small results,
with the manifest carrying every hash; merge that; keep `codex/p17-inactive-prior` as a local,
never-pushed archive with its original hashes intact. Nothing is lost — the full branch and the
worktree stay on disk — and main gets the work rather than the evidence blobs.

**Two things that need inspection, not assumption.** E6 ran on top of E5 although its prompt
assumed E5 had not — its first commit is "E6: E5 carry-forward", so it may have re-applied E5's
edits. And `q1/n0-check` sits on E5 while local `e2/deck` has moved on to E6, so those two need
reconciling, not just merging.

NOTE TO USER: launch in an auto-approving mode. It commits, merges, builds one curated commit,
pushes, and verifies from a fresh clone. It never uses `--force`, never rewrites a pushed branch,
never deletes a lock file, and never removes a worktree before a fresh clone proves its content
landed. `gh` and push credentials must be available.

---

```
Work AUTONOMOUSLY; commit in parts, prefixed "R3: "; maintain reports/R3_integration/DECISIONS.md
FROM THE FIRST JUDGEMENT CALL, and log every git command with its exit code. Standing rules and
docs/RIGOUR.md carry over. Check exit codes explicitly, never `cmd && check`. Never --force,
never git clean, never delete a lock file, never rewrite a pushed branch, never delete an
unmerged branch.

TASK 0 - re-verify the state; trust nothing from the table above without checking
- `git fetch origin --prune`. Report every local and remote branch with its head and its
  ahead/behind against origin/main. If anything differs from INTEGRATION_STATE.md, say what,
  and STOP if origin/main has moved past dc5b4cc - someone else pushed and this plan is stale.
- `git worktree list`; confirm each path exists on disk.
- In the primary tree: `git status --porcelain`. Expect the 32 dirty paths INTEGRATION_STATE
  lists (OPEN_ITEMS with 0d, P16 DECISIONS, fourteen audit artefacts plus trace_red2, the red2
  checkpoint/arrays/summary, six prompts, two Candida resolved configs, two TPC images). Report
  the list and any difference.
- Confirm /private/tmp/etcGEMs-p17 is clean at ef1961b and that
  reports/P17_inactive_prior/closure_manifest.json exists there.
- Report the tracked size of origin/main and of ef1961b (`git ls-tree -r -l` summed) so the
  reduction achieved later is measurable.

TASK 1 - commit the primary tree's dirty files onto p16/reduced, preserving differences
- For every dirty file, compute its SHA-256 and compare against the copy committed on
  codex/p17-inactive-prior at the same path, where one exists. Report three lists: identical to
  P17's copy; different from P17's copy; absent from P17.
- Commit ALL of them onto p16/reduced as "R3: P16 post-run evidence and the 0d sequencing note,
  committed from the primary tree", EXCEPT prompts/E6_deck_bring_current_prompt.md, which gets
  its header marked SUPERSEDED (it assumed E5 had not run; E5 and E6 both did) and is committed
  in the same commit with that marking. Do not delete it.
- For any file DIFFERENT from P17's copy: do not resolve which is right. Commit the primary
  tree's version on p16/reduced, and record the pair of hashes in DECISIONS.md so the merge in
  TASK 4 surfaces it as a conflict to be kept both-sides.
- `git status --porcelain` must now be empty. Report the commit.

TASK 2 - build the curated P17 commit
Do this on a NEW branch `p17/curated`, created from the p16/reduced tip after TASK 1.
- Copy from /private/tmp/etcGEMs-p17 (at ef1961b) into this branch's tree, under the same paths,
  everything in reports/P17_inactive_prior/ and docs/ that is one of:
    * any .md, .py, .json, .csv, .yaml, .yml, .txt, .toml, .cfg, .png, .svg, .pdf;
    * any file of any type under 5 MB;
  EXCLUDING any file over 5 MB (report each excluded file with its path and size - expect the
  two big logs, checkpoints, .h5, .npy, .save files and similar).
- Copy closure_manifest.json and closure_artifact_inventory.json UNCHANGED - they are the
  record of every hash including the excluded files, and must not be regenerated.
- Also copy from ef1961b everything under strains/eciML1515/outputs/ that P17 added and that is
  under 5 MB, and any src/ or scripts/ change P17 made (there should be none - verify with
  `git diff --stat 191b4b0 ef1961b -- src/ scripts/`; if there are, report them and copy them).
- Write reports/P17_inactive_prior/ARCHIVE.md stating: that this directory is CURATED; that the
  complete artefact set (1,906 files, 2,639 MB) lives on the local branch
  codex/p17-inactive-prior at ef1961b in /private/tmp/etcGEMs-p17 and is deliberately not
  pushed; that closure_manifest.json carries the SHA-256 of every file including the excluded
  ones; the list of excluded files with sizes; and that the full branch's commit hashes
  referenced in DECISIONS.md, CLOSURE_VERIFICATION and INTEGRATION_STATE refer to that local
  branch and remain valid there.
- Verify: for every file copied, its SHA-256 matches closure_manifest.json. Report the count
  matched, and STOP on any mismatch.
- Commit as ONE commit: "P17: closure, curated for the repository - full artefacts on local
  branch codex/p17-inactive-prior at ef1961b; every hash in closure_manifest.json". Report the
  tracked size of this branch.

TASK 3 - inspect E6 against E5 before merging the deck
In ../etcGEMs-work (on local e2/deck at 0215a16):
- `git diff --stat bc356e3 0215a16` - what E6 changed beyond E5.
- Read the "E6: E5 carry-forward" commit. E5 had already executed its ERROR 1, ERROR 3, JOB 4,
  JOB 5 and JOB 6. Did E6 re-apply them (duplicated bullets, doubled slides, a second copy of
  the line-scan slide), or detect they were done and skip? Report what actually happened in the
  deck.qmd diff, slide by slide.
- Confirm the deck renders at 0215a16 and record the page count. If E6 duplicated content, do
  NOT fix it here - record it as an item for the next deck pass. This task inspects.
- `git diff --stat bc356e3 b163bad` - what Q1 changed on the E5 base. Identify every file Q1 and
  E6 both touched (expect OPEN_ITEMS, evidence.csv, report_status.yaml, the deck's DECISIONS,
  stamps). These are the reconciliation set for TASK 4 step 4.

TASK 4 - merge, in order, each as its own PR, each verified before the next
Merge style: match #14-#32 (merge commits). Server-side by PR where possible; where a conflict
blocks a server-side merge, resolve in a TEMPORARY worktree from main, never in the primary
tree while it is on a branch you need. Conflict rule everywhere: KEEP BOTH SIDES for
OPEN_ITEMS.md, evidence.csv, report_status.yaml and any DECISIONS.md; REGENERATE stamps and
PROVENANCE with scripts/stamp_reports.py rather than hand-merging; never fabricate a hash.
Report every conflict file by file with what was kept.
  1. p16/reduced -> main. PR, merge, confirm MERGED, record the commit.
  2. p17/curated -> main. Same. Its DECISIONS/report/gate/RIGOUR/HANDOVER/INTEGRATION_STATE/
     TARGET_REVISION_SPEC all land here.
  3. Push local e2/deck to origin (a fast-forward of origin/e2/deck by six commits; no force
     needed - verify it IS a fast-forward first). Then e2/deck -> main. Same.
  4. q1/n0-check -> main. This is where E5-vs-E6 reconciliation happens: Q1's five commits sit
     on E5 and main now has E6. Merge, keep both sides on the reconciliation set from TASK 3,
     regenerate stamps, and re-render the deck so the PDF reflects the merged .qmd - a binary
     PDF cannot be merged. Verify the render. Record the final page count.
- After all four: `git switch main && git pull` in the primary tree (two commands, two exit
  checks). Report the final commit on origin/main.

TASK 5 - gates and a fresh clone
- Run the seven-strain gate (K1, expect 79/79) and the P1 port gate (expect 60/60) from the
  primary tree on main. Report. If either fails, STOP - do not push anything further and do not
  delete anything.
- Fresh clone of origin/main into a scratch directory outside every tree. In it confirm:
    * reports/P16_reduced/ with its audit files; reports/P17_inactive_prior/ with report.md,
      current_gate.md, DECISIONS.md, closure_manifest.json, ARCHIVE.md; docs/RIGOUR.md,
      docs/HANDOVER_2026-09-13.md, docs/INTEGRATION_STATE.md, docs/TARGET_REVISION_SPEC.md,
      docs/CLOSURE_VERIFICATION_2026-09-13.md; reports/ecoli_deck/_output/deck.pdf at the
      TASK 4 page count; reports/Q1_n0_check/.
    * every file in the clone's reports/P17_inactive_prior/ matches its closure_manifest.json
      hash. Report the count.
    * tracked size of the clone, against TASK 0's numbers. Expect roughly 303 MB plus the
      curated P17 (well under 100 MB) plus the deck and Q1.
    * both gates pass from the clone.
- Delete the scratch clone.

TASK 6 - branches and worktrees, only after TASK 5 passes
- Delete merged branches locally and on origin, non-force: p16/reduced, p17/curated, e2/deck,
  q1/n0-check. If git refuses any as unmerged, leave it and report why.
- Do NOT delete codex/p17-inactive-prior. It is the archive. Confirm it is still present locally
  at ef1961b and NOT on origin.
- Do NOT remove /private/tmp/etcGEMs-p17. It holds the only checkout of the archive branch.
  Report its path and that it must be kept; recommend, do not act, on relocating it out of
  /tmp to somewhere durable (e.g. beside the repository) since /tmp may be cleared on reboot.
  If the machine's /tmp is cleared on reboot, say so prominently in the report.
- ../etcGEMs-work: switch to a detached checkout of the new main so it cannot drift. Leave it.
- Remove any temporary worktree this task created.

TASK 7 - record and hand over
- docs/OPEN_ITEMS.md: a dated line under section 0 recording the integration (final main
  commit, what merged, that P17 is curated on main and complete on a local branch); a PI item
  for relocating the archive worktree out of /tmp; a PI item for the E6-vs-E5 duplication if
  TASK 3 found any; the target-revision spec as the next step awaiting approval.
- docs/HANDOVER_2026-09-13.md: append a dated "Integration completed" section pointing at the
  final main commit and this report. Do not rewrite the original.
- reports/R3_integration/report.md: the state before, every merge and conflict, the curation
  (files included, excluded with sizes, hashes matched), the E6 inspection, the gates, the fresh
  clone, the sizes before and after, the branch and worktree dispositions.
- Stamps.

VERIFY (report all)
1. TASK 0: the branch table re-verified; the 32 dirty paths; worktrees on disk; sizes.
2. TASK 1: the three hash lists; the commit; E6 prompt marked superseded; status empty.
3. TASK 2: files included and excluded with sizes; hashes matched against the manifest, count;
   ARCHIVE.md present; the curated commit and its tracked size.
4. TASK 3: E6-vs-E5 diff summary and whether content was duplicated, slide by slide; the deck
   renders at 0215a16 with page count; the Q1/E6 reconciliation set.
5. TASK 4: four PRs with numbers and merge commits; every conflict file by file; the deck
   re-rendered after step 4 with page count; final origin/main commit.
6. TASK 5: both gates on main; the fresh clone's contents; manifest hashes matched in the clone;
   tracked size before and after; gates from the clone.
7. TASK 6: branches deleted or retained with reasons; codex/p17-inactive-prior local-only at
   ef1961b; the archive worktree kept, with the /tmp warning; etcGEMs-work detached on main.
8. TASK 7: OPEN_ITEMS lines; HANDOVER appendix; the R3 report; stamps.

CONSTRAINTS
- Never --force. Never rewrite a pushed branch. Never delete a lock file or an unmerged branch.
- The curated commit is built by copying and hashing against closure_manifest.json; the
  manifest itself is copied unchanged, never regenerated.
- codex/p17-inactive-prior is never pushed and never deleted. Its worktree is never removed.
- Conflicts keep both sides. Stamps and PROVENANCE are regenerated. The deck PDF is re-rendered
  after the last merge that touches deck.qmd.
- Nothing is deleted until a fresh clone has proved it landed.
- A gate failure stops everything after it.
- Autonomous; commit in parts: "R3: P16 evidence", "P17: closure, curated ...", "R3: merges",
  "R3: record".
```
