> **SUPERSEDED — marked 2026-09-13 by R3, not deleted.**
>
> This prompt assumes **E5 had not run**, and directs an E5 carry-forward. Both E5 and E6 did in
> fact run: `origin/e2/deck` at `bc356e3` is the E5 tip, and the local `e2/deck` at `0215a16`
> carries six further E6 commits whose first is "E6: E5 carry-forward". Its instructions must not
> be re-executed as written. Kept as the provenance of what E6 was asked to do, and because
> `docs/INTEGRATION_STATE.md` records the disposition "mark it superseded, do not delete it".
> Whether E6 duplicated E5's already-applied edits is inspected in `reports/R3_integration/`.

# Claude Code prompt — E6: bring the deck current with today's results, and say what happens next (autonomous, ~1 h)

**Run from `../etcGEMs-work`**, continuing on branch `e2/deck` (PR unmerged). P16 seed 2 is running
in `etcGEMs` until ~05:25 — **write nothing there**. Text and a re-render only; no solves.

**This prompt SUPERSEDES `prompts/E5_deck_posterior_and_holdout_prompt.md`. Do not run E5.**
E5 was written before P16 converged and its ERROR 2 rewrites the posterior slide around P15's
crash, which is now out of date.

**But most of E5 is still correct and is carried forward.** Read
`prompts/E5_deck_posterior_and_holdout_prompt.md` and **execute ERROR 1, ERROR 3, JOB 4, JOB 5 and
JOB 6 exactly as written there.** In short, for orientation only — the text in E5 governs:

  * **ERROR 1** — the stopping rule on the posterior slide describes *emcee* (autocorrelation
    times, n_eff ≥ 200) for runs that were *dynesty*. Rewrite from `reports/P16_reduced/`'s own
    record, not from E5's paraphrase.
  * **ERROR 3** — "nothing has ever been tested against data it was not fitted to" is false; the
    *emergent* model predicted Van Derlinden a priori (shape held, peak 2.3× low) and the
    *calibrated* model has no holdout. Fix `docs/OPEN_ITEMS.md` §0a R4 too.
  * **JOB 4** — figure 12 (the 22-panel line scan) gets its own slide, enlarged, with the lay
    explanation of line scans and "20 % of range on a small step".
  * **JOB 5** — define live and dead basins before using the terms. **This job is now much more
    important than when E5 was written** — see JOB B below.
  * **JOB 6** — remove the retraction framing; fold retraction 1's content (0.08 units for one
    lever pinned, 7.6 for both) into the −4 K slide.

**DO NOT execute E5's ERROR 2.** JOB A below replaces it.

---

**JOB A — the posterior slide, which finally has content.**

P16 fixed `dTm` at 0 and re-ran at 15 free parameters. **Run 1 converged cleanly** — the first
nested run in this family to do so: 14,088 iterations, 221,781 evaluations, 9.585 h,
**log Z = −26.030 ± 0.109**, n_eff 5,988, no crash. At iteration 11,547 — exactly where P15 died —
dlogz was **0.666 against P15's 2.168**, at essentially the same evaluation count. And `tm_scale`
is not railing (median 1.069, 5/95 [0.793, 1.516], 0.00 % of mass within 5 % of its bound), so the
reduction removed the degeneracy rather than relocating it.

**A second seed is running and is not finished.** It tracks run 1 within ~8 % on wall-clock at
matched iterations and is expected to converge 05:15–05:45. The reproducibility rule was
pre-registered: log Z within combined error AND no median differing by more than two Monte-Carlo
errors. **Quote nothing as established.** The slide says run 1 converged, what it shows, and that
the confirmation is pending — that is the honest state and it is also the discipline this project
has kept all week.

**State what fixing `dTm` costs, in one line:** the posterior can no longer express a uniform
displacement of the whole meltome, so any uniform error in the measured melting temperatures is
absorbed by `tm_scale` and the catalytic parameters. This posterior assumes the meltome's mean is
right.

---

**JOB B — the result of the day, and it is uncomfortable.**

**About half the posterior is non-growing models.** From run 1:

  * **MAP sample:** log L −10.704, peak predicted growth **1.7255 /h** — 83 % of the measured 2.076.
    A good fit.
  * **Componentwise median:** log L −30.558, peak growth **0.0043 /h**. A dead model.
  * **Posterior-predictive peak growth**, 300 weighted draws: median 0.0016, 5/95 [0.0000, 1.711].
    **50.7 % of the mass grows less than half the measurement.**

Two things must be said on the slide, and neither is optional.

**First, why the median is useless here, because it generalises.** With correlated parameters the
vector of marginal medians need not lie in the posterior's support at all — take the median of each
parameter separately and you can land well off the ridge they jointly occupy. Its growth R² of
−2.01 measures its own unrepresentativeness, not the model's fit. **So the deck must report the MAP
and the predictive distribution, and the median only as evidence that it is unusable.** This is a
general point about summarising correlated posteriors and is worth the audience's time.

**Second, the likely cause, stated as a diagnosis under test rather than a property of the model.**
P12's decomposition: the live basin pays growth **+6.363**, respiration **−13.549**; the dead basin
pays growth **−18.860**, respiration **−0.017**. The dead basin wins 13.5 units **by not being
scored on respiration at all** — its temperatures are *infeasible*, the LP has no solution, and the
support mask is `isfinite(o2) & (o2 > 0)`. The feasible-but-not-growing case was fixed; the
infeasible case was never addressed. The live–dead gap is then ~11.7 units, and e^−11.7 ≈ 8×10⁻⁶
**loses to prior volume in 15 dimensions** — the live region need only be ~46 % of prior width per
axis for volume to win.

Frame it as: *a converged posterior that puts half its mass on models that do not grow, for a
reason we can name and test.* Do **not** present it as an established property of enzyme-constrained
models, and do **not** present it as a failure of the run — dlogz was met, n_eff ~6,000, and the MAP
is a good fit.

---

**JOB C — a "what happens next" slide, which is what I actually asked for.**

Read `docs/OPEN_ITEMS.md` **§0d**, written this evening, and turn it into one slide — bullets, no
more than about forty words. It should say, in order:

  1. **Confirm reproducibility** — seed 2 lands overnight against a pre-registered rule.
  2. **Settle the infeasibility exemption** — charge a model with no feasible flux distribution
     rather than exempting it. Cheap to test from the existing posterior, and it gates everything
     after it, because it would hurt configurations E and F far worse than D.
  3. **Then configuration D on M9**, changing *one* variable. M9 + glucose is fully defined;
     **NLDM is a defined stand-in for R2A**, which is what the experiments were run in and is
     itself undefined. A controlled comparison: if the degeneracy and the dead mass reproduce on
     M9 they are structural; if not, the medium is implicated.
  4. **Then the model comparison** — D, E and F on one medium give three evidences, and the
     differences say **which mechanism the data supports**: overflow from a carbon cap, a
     respiratory membrane-area limit, or that limit with bd-II non-electrogenic. **These are
     competing hypotheses, not versions.** D NLDM's −26.030 ± 0.109 is the first of the three.
  5. **The measurement that no modelling replaces** — proteome allocation above 37 °C on glucose.

Point 4 is the one to land: it is the biological question, it comes nearly free from nested
sampling, and it is not available from the sampler this project started with.

---

NOTE TO USER: launch in an auto-approving mode. Reading, editing, and a re-render.

---

```
Work AUTONOMOUSLY; commit in parts, prefixed "E6: "; append to reports/ecoli_deck/DECISIONS.md.
Standing rules carry over. Check exit codes explicitly, never `cmd && check`. Continue on `e2/deck`
in ../etcGEMs-work; do not push to main; the PR stays unmerged. Write NOTHING under ../etcGEMs.

TASK 0 - premise
- Confirm worktree, branch, interpreter; confirm P16 seed 2 is running in the primary tree and that
  you write nothing there. Confirm the deck renders; record the baseline page count.
- Read prompts/E5_...md in full, and docs/OPEN_ITEMS.md 0d. Record in DECISIONS which E5 jobs you
  are executing (1, 3, 4, 5, 6) and that ERROR 2 is superseded.

TASK 1 - E5's carried-forward jobs
- Execute E5's ERROR 1, ERROR 3, JOB 4, JOB 5 and JOB 6 as written there, with one update: ERROR 1's
  stopping rule must be read from reports/P16_reduced/ (dynesty, nlive 800, rslice, dlogz < 0.1,
  plus the two-seed agreement rule), not from P15.
- Report each as E5's VERIFY section requires.

TASK 2 - the posterior slide (JOB A)
- Rewrite it. Every number verified against reports/P16_reduced/ before it reaches a slide.
- Seed 2 is IN FLIGHT. Nothing is stated as established; the agreement rule is named and its
  outcome is pending.
- The cost of fixing dTm appears in one line.

TASK 3 - the half-dead posterior (JOB B)
- New slide or slides. The three numbers; why the componentwise median is unusable and why that
  generalises; the infeasibility diagnosis with P12's decomposition and the volume argument.
- Verify every figure against reports/P12_modes/, reports/P16_reduced/ and reports/Q1_n0_check/.
- Framed as a diagnosis under test. Not a property of the model class; not a failure of the run.

TASK 4 - what happens next (JOB C)
- One slide from OPEN_ITEMS 0d, in the order given. Place it before the closing questions slide.
- Check the closing "Three questions for the group" still fits what the deck now says; if the
  model-comparison point belongs among them, say so and adjust - but do not increase it past three.

TASK 5 - render and verify
- Re-render. Verify: opens, every figure resolves, no overfull box, no unresolved citation. Report
  path and page count. Re-run scripts/stamp_reports.py. Commit the PDF if that is the directory's
  convention.

VERIFY (report all)
1. TASK 0: worktree, branch, baseline page count, which E5 jobs are being executed.
2. TASK 1: E5's own VERIFY items for the five carried jobs, including figure 12's rendered size
   before and after and the basin definitions as written.
3. TASK 2: the rewritten posterior slide; every number's source; confirmation nothing from seed 2
   is quoted and that its pending status is stated.
4. TASK 3: the three numbers verified; the median-unusability explanation; the infeasibility
   diagnosis with its decomposition; confirmation it is framed as under test.
5. TASK 4: the next-steps slide as written; whether the closing questions changed.
6. TASK 5: PDF path, page count before/after, render clean, stamps.
7. `git diff main --stat`: reports/ecoli_deck/, OPEN_ITEMS, stamps. Nothing under ../etcGEMs, src/
   or strains/.

CONSTRAINTS
- E5's ERROR 2 is NOT executed. Everything else in E5 is.
- Nothing from seed 2 is quoted; it is in flight and its rule is pre-registered.
- The componentwise median is never presented as a summary of the posterior.
- The half-dead finding is a diagnosis under test, not a property of etcGEMs and not a failed run.
- D, E and F are competing mechanisms, never versions.
- Every number read from its source file; the file wins over this prompt.
- Do not touch the "-4 K stability shift" slide beyond E5's JOB 6 addition - it is otherwise right.
- Autonomous; commit in parts: "E6: E5 carry-forward", "E6: posterior", "E6: half-dead",
  "E6: next steps", "E6: render".
```
