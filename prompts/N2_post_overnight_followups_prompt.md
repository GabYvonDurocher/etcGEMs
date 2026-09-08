# Claude Code prompt — N2: the four follow-ups from the N1 review — diagnose the stale E. coli TPC, resolve D8, record what A3 and the flatness guard actually established (autonomous)

Run from the project root (`.../MICROADAPT/etcGEMs`). Follows the review of N1
(https://github.com/GabYvonDurocher/etcGEMs/pull/1, branch `n1/overnight`).

**TASK 0 merges that PR.** Everything after it assumes N1's contents are on `main`.

Five tasks. Two are diagnostic and must not be "fixed" before they are understood; two are recording
work that stops a correct result being misread later. Nothing here changes a scientific conclusion.

NOTE TO USER: launch in an auto-approving mode. No predictors, no downloads, no new data. Needs
network and credentials for `git@github.com:GabYvonDurocher/etcGEMs.git`. Should be under an hour,
most of it TASK 1's bisection.

Standing rules from N1 carry over unchanged: decide and proceed when reversible or precedented; stop
the task and record when it would change a committed number, need a scientific judgement, or write
inside `$CANDIDAS_ROOT`; never weaken a test, never edit a number to match a result. Keep
`reports/N2_followups/DECISIONS.md` from the first judgement call.

**One amendment to those rules, for TASK 0 only:** N1's rule was "never push to `main`". TASK 0
merges PR #1 and pushes it, because that merge is the explicit instruction of this prompt and has
been reviewed by a human. It is the ONLY write to `main` permitted. TASKS 1-4 are branch work on
`n2/followups`, cut from `main` after TASK 0 completes, and end in a PR that is NOT merged.

REFERENCE, read first: `reports/N1_overnight/SUMMARY.md` and `DECISIONS.md` (especially D8, D11,
D14), `reports/N1_overnight/TASK4_sector_cap.md`, `reports/N1_overnight/A3_gene_content.md`,
`reports/candida_thermal_limit/K2_core_thermal_form.md` (the C1 stability claim), and
`docs/CANDIDA_DISCUSSION_2026-09-07.md` §4 and §5.

---

```
Work AUTONOMOUSLY; commit per task, prefixed "N2 TASK n: "; maintain reports/N2_followups/DECISIONS.md.
Print a final summary with each task DONE / PARTIAL / STOPPED.

TASK 0 - merge N1, and verify the merge before building on it
This is the one place in this prompt where you write to `main`. Everything after it is branch work.
- Confirm the working tree is clean and `main` is up to date with origin. If it is not, STOP and
  report — do not merge onto a divergent or dirty tree.
- Review the PR before merging it, briefly and for real: `git diff main...n1/overnight --stat`, and
  confirm against N1's own claims that no existing strain's committed outputs changed and that
  `$CANDIDAS_ROOT` is untouched (`git -C "$CANDIDAS_ROOT" status --short` is empty; the Candidas
  repository is READ ONLY throughout this prompt).
- Merge with `--no-ff` so the overnight run stays visible as a unit:
  `git switch main && git merge --no-ff n1/overnight -m "Merge N1: gene-content screen, self-contained gate, pool conditioning option, sector flatness guard, repo consistency, K3 groundwork"`
- VERIFY IMMEDIATELY, and treat any failure as a stop condition for the whole prompt:
    * gate passes 79/79 with `$CANDIDAS_ROOT` UNSET (this is N1 TASK 2's whole point);
    * `etcgem tpc` for mmaripaludis and syn6803 leaves their committed outputs byte-identical;
    * `git status --short` clean.
  Note that eciML1515's committed TPC is ALREADY known not to reproduce — that is TASK 1's subject,
  not a merge failure. Do not conflate the two.
- Push `main`. Delete the merged branch only after the push succeeds. If `gh` is available, close
  PR #1 as merged rather than leaving it open.
- If any verification fails: do NOT proceed to TASK 1. Report what failed, leave `main` as it is
  (the merge commit stands; reverting is a human decision), and stop.

TASK 1 - the stale eciML1515 TPC: find the CAUSE before regenerating
`strains/eciML1515/outputs/tpc/descriptors.json` was committed in c6a20ad (which predates the whole
Candida merge) and says Topt 37.0 C, rmax 0.3413. The current code produces Topt 31.0 C, rmax 0.543.
CTmax agrees (46.856 vs 46.9) and Ea nearly (0.934 vs 0.96), so the ENVELOPE is unchanged and what
moved is the optimum and the magnitude — a signature that points at allocation or medium, not at the
thermal layer.

- DO NOT regenerate first. Regenerating destroys the evidence. Diagnose, then regenerate.
- Bisect the cause. Candidates, in the order I would try them: the default medium
  (`default_medium_proteome`, currently Glucose — the run reports f_bio@37C of LB 0.359 /
  Glucose 0.183 / Glycerol 0.145, and a 6 C shift in Topt with a higher rmax is consistent with a
  medium change); `allocation_from_data` landing after the output was written; the growth-law or
  translation-cap settings; the pool reconciliation. Use `git log` on strain.yaml, config.py,
  proteome_alloc.py, sectors.py and enzyme_cost.py around c6a20ad, and where cheap, check out the
  old state into a scratch worktree and re-run to confirm.
- State the cause with evidence. If it cannot be pinned down, say so and give the shortlist with
  what would settle it — do not guess in the report.
- THEN regenerate, commit, and record in the commit message the cause and the numbers before/after.
- Check whether any other committed strain output is stale the same way: for all seven strains,
  regenerate each committed output into a scratch location and compare. Report a table of which
  reproduce and which do not. Do NOT regenerate the ones that fail — list them; a second stale
  artefact deserves its own diagnosis, not a bulk overwrite.

TASK 2 - resolve D8: make the conditioning fix canonical, keep the gate honest
N1 established, via glpk_exact arbitration, that Gurobi and the exact solver agree and GLPK is 8.7%
wrong on the surviving cold-end point; and TASK 2 of N1 froze the standalone's values into
`standalone_expected.json`, so the gate no longer needs $CANDIDAS_ROOT and its fidelity check is
permanently discharged.

The decision, which you may now implement: **two documented configurations.**
- `rescale_pool_row` becomes the DEFAULT ON for all normal use.
- The gate keeps a `legacy_fidelity` configuration with rescaling OFF, because its job is to
  reproduce the standalone INCLUDING the ~0.4% GLPK error, and that job is historical and finished.
  It must still pass 79/79.
- Both must be named and explained where a user meets them: README.md, the gate's own docstring, and
  a short section in reports/candida_thermal_limit/. The explanation a reader needs is one sentence:
  fidelity to the original implementation and numerical correctness are now different things, and
  the gate tests the first while everything else uses the second.
- Report, for each Candida strain, every quantity that moves when the default flips, and by how much.
  Any quantity quoted in K2's report or in docs/CANDIDA_DISCUSSION_2026-09-07.md that changes MUST be
  listed explicitly so the humans can update the prose — do not update it yourself.
- Verify: gate 79/79 under legacy_fidelity with $CANDIDAS_ROOT unset; existing non-Candida strains
  byte-identical under the new default (they do not use this code path — confirm rather than assume).

TASK 3 - record what the flatness guard established, where it will be read
N1's guard produced numbers that change how two existing results should be read, and they currently
live only in JSON files nobody will open.
- The Candida B4 plateau is 12-14 C wide on a 22 C grid: MORE THAN HALF the tested range sits within
  1% of the maximum. Add this to reports/candida_thermal_limit/K2_core_thermal_form.md, in the B4 row
  and in the C1 section, TOGETHER WITH the fact that rescues it — K2 found the required separation
  stable to 0.3 C across B1-B4, so the 13.8 C figure does not depend on the flat rung. A reader who
  sees the plateau without that sentence will reasonably doubt the result.
- Do the same for the two strains where the guard fires but the result is FINE, so nobody later
  mistakes a fired guard for a broken result: mmaripaludis reports NaN because its a-priori TPC is
  identically zero (the maintenance-crushed state its strain.yaml documents) and its analyses run at
  a calibrated kcat_scale where the metabolic pool binds, not the translation cap; syn6803's plateau
  is 2.0 C at the 1% level and 0.0 at 0.01%. Neither undermines the seven-strain ceiling table.
- Add one line to docs/CANDIDA_DISCUSSION_2026-09-07.md §4 recording that the ceiling table was
  checked against the flatness guard and survives, with a pointer. Do not restate the table.

TASK 4 - promote A3's coverage numbers out of the report
A3 measured something §5 of the discussion notes had only inferred, and it is the most quotable
number in the whole night: 0-15 genes per species comparison are inside a metabolic model, against
122-647 in the proteome — so the models see roughly 2-5% of the gene-content difference.
- Add it to docs/CANDIDA_DISCUSSION_2026-09-07.md §5, with the two methodological caveats that make
  it trustworthy: RBH-absence over-states true absence more than threefold, and a description-only
  candidate search missed AOX in C. haemulonii (alignment finds it at 86.4%) and returned nothing at
  all in C. parapsilosis, whose model namespace has no description field.
- Add to §6(e) that all four Xiao et al. candidates are present in all four species, and that AOX and
  the glutaredoxins are in NO model — so that proposed mechanism is untestable in this framework as
  it stands, on two separate grounds. State it as a scope limit, not as a refutation of Xiao.
- Update §8 A3 to DONE with a pointer to the report.
- Do not adjudicate mechanism anywhere.

FINALLY
- reports/N2_followups/SUMMARY.md; push the branch; open a PR against main if gh is available,
  otherwise print the URL and body. Do NOT merge.

VERIFY (report all)
1. TASK 0: the pre-merge diff summary; the merge commit; gate 79/79 with $CANDIDAS_ROOT unset;
   mmaripaludis and syn6803 byte-identical; `main` pushed; PR #1 closed as merged; $CANDIDAS_ROOT
   confirmed clean.
2. TASK 1: the cause of the eciML1515 drift, with the evidence that establishes it; before/after
   numbers; the seven-strain reproduction table; any further stale artefacts LISTED not fixed.
3. TASK 2: gate 79/79 under legacy_fidelity with $CANDIDAS_ROOT unset; every Candida quantity that
   moves under the new default, with magnitudes; the list of prose that needs a human to update;
   non-Candida strains confirmed unaffected.
4. TASK 3: the three flatness notes, each in the file a reader will actually reach.
5. TASK 4: §5 and §6(e) updated; §8 A3 marked DONE.
6. DECISIONS.md complete.
7. `git diff main --stat` for the n2 branch, and confirmation that no scientific conclusion was altered anywhere —
   only measurements recorded and defaults changed.

CONSTRAINTS
- TASK 0 is the only write to `main`. If its verification fails, the prompt stops there.
- TASK 1 diagnoses before it regenerates. A regenerated file with an unexplained cause is worse than
  a stale one, because it looks correct.
- Do not bulk-overwrite other stale outputs. List them.
- Where a number in existing prose changes, LIST it for a human. Do not edit conclusions.
- Autonomous; commit per task. TASK 0 produces a merge commit on `main`; TASKS 1-4 commit to
  `n2/followups`.
```
