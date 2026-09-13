# Claude Code prompt — E5: correct the stopping rule, the holdout claim, and the posterior slide (autonomous, ~30 min)

**Run from `../etcGEMs-work`**, continuing on branch `e2/deck` (PR unmerged, +15 commits). P16 may
be running in `etcGEMs` — write nothing there. Text and a re-render only; no solves.

Three corrections. Two are factual errors about method; the third undersells the work.

---

**ERROR 1 — the stopping rule on "Where the posterior stands" is the wrong sampler's criterion.**

The slide says:

> **Two runs are in flight.** The stopping rule was fixed **before** they started: chain length
> $> 40$ autocorrelation times **and** effective sample size $\geq 200$

That describes **emcee**, the sampler this project abandoned at P8. Autocorrelation time is not a
nested-sampling concept. The runs were **dynesty**, and their pre-registered criterion was
**dlogz < 0.1**, plus an agreement rule between two seeds: *log Z agreeing within combined reported
error AND no posterior median differing by more than two Monte-Carlo errors*. The numbers quoted are
also wrong for emcee — P6's adopted target was n_eff ≥ 600 and chain/τ ≥ 25. **Verify all of this
against `reports/P15_posterior/DECISIONS.md` D1 and rewrite the bullet from the file.**

**ERROR 2 — the runs are not in flight.** P15 run 1 **crashed** at 9.9 h and iteration 11,547;
run 2 was never started. No posterior exists. But the crash is a result, and the slide should say so:
from the checkpoint's own 800 live points the smallest covariance eigenvalue is **1.947e-04**, its
direction dominated by **dTm (+0.903) and `tm_scale` (−0.217)**, correlation **+0.831**, condition
number **1,457**; the bounding ellipsoid had been singular for hours. **That is the same
non-identified pair Y3 found by profiling the likelihood** — two methods sharing no machinery, one
optimisation and one the geometry of a sampler's point cloud.

**ERROR 3 — the holdout claim on "Settled · in flight · needs measurement" is false, and it
undersells us.** The slide says:

> **Never yet tested.** Nothing in this framework has been asked to predict data it was not
> fitted to.

`reports/ecoli_tpc/report.qmd` has a Validation section: the **emergent** model predicts the
exact-strain Van Derlinden curve **a priori** — *"Nothing is fit to growth"* — tracking the shape
(T_opt, E_a) and under-predicting the absolute peak **~2.3-fold**. That is an out-of-sample test and
it half-succeeded. What has no holdout is the **calibrated** model, because the calibration was then
fitted to that same curve. The honest and more interesting statement is: *one a priori test was run,
shape held and magnitude did not, and the test data was then consumed by the calibration.* Cooper
et al. remains the right holdout. **The same error is in `docs/OPEN_ITEMS.md` §0a R4** — fix it
there too if E1 never ran.

---

**JOB 4 — figure 12 needs a page of its own, and the slide needs a lay explanation.**

The twelfth figure is `../P9_surface/task1_scan.png` on **"The surface, scanned"**, currently at
`height=66%`. It is twenty-two sub-panels at two-thirds of a slide: unreadable. **Give it a full
slide of its own**, bullets moved to the slide before it, and enlarge accordingly.

And the caption is currently jargon — *"22 line scans, 902 model builds"* and *"12 of 22 lines jump
by more than 20 % of their range on a small step"* mean nothing to someone outside this work.
Explain both in plain language on the preceding slide, in bullets:

  * **What a line scan is.** Start from the best-fitting parameter set. Choose a direction in
    parameter space — a single parameter, or a combination. Step along it in small increments,
    rebuilding and re-solving the entire metabolic model at every step, and record how well it fits
    the data. Twenty-two directions, about forty steps each, ≈ 900 full model solves. It is a set of
    transects: walking out from a summit in twenty-two directions and recording the altitude every
    few metres.
  * **What the step size is.** One step is a twentieth of the width of the plausible range for that
    parameter — deliberately small.
  * **What "20 % of the range" means.** The range is the total change in fit quality across that
    whole line. So in twelve of twenty-two directions, **one small step changed the fit by more than
    a fifth of everything that changed along the entire line**. That is a cliff, not a slope.
  * **Why it matters, and this is the point of the slide.** Fitting algorithms work by feeling
    their way downhill. A cliff means a tiny change in a parameter makes the model look
    catastrophically worse, so the algorithm cannot cross it and gets stuck against it. The
    landscape was not a hill to climb; it was a plateau with sheer drops.

Verify the numbers against `reports/P9_surface/` — the file wins over this prompt.

---

**JOB 5 — "live basin" and "dead basin" are used without being defined.**

On "How many answers are there?", explain in bullets, before the result:

  * **What a basin is.** A region of parameter space from which the optimiser, started anywhere
    inside it, ends at the same bottom. A valley: drop a ball anywhere in it and it rolls to the
    same place.
  * **How we found them.** Start the optimiser from ~100 randomly drawn parameter sets and record
    where each stops. Then test every pair of endpoints: walk in a straight line between them and
    see whether the fit has to get *worse* in between. A ridge means two separate basins; no ridge
    means one basin reached from two directions. **State the threshold used and that it was fixed
    before the data were seen** (`reports/P12_modes/`).
  * **What makes a basin "dead".** A dead basin is a mathematically valid solution in which the
    model organism does not grow — peak predicted growth 0.000 h⁻¹ against a measured 2.08. It is a
    set of parameters that fits by describing a corpse.
  * **Why it scored at all**, stated in one line, and whether it survives the current likelihood —
    check `reports/P13_support/` and say so accurately. Do not assert it has been removed unless
    the file says so; P12's map predates the clamp.

---

**JOB 6 — remove the retraction framing, but keep what retraction 1 actually found.**

Cut the "two retractions" framing from the slide title and body. These were internal corrections to
claims that never left the group, so to this audience they are process, not content.

**But retraction 1 carries a finding that must survive, relocated.** It says a fit honouring the
measured meltome on **both** levers exists at **7.6 log-likelihood units worse**, growing at
1.66 h⁻¹ against two prior bounds. The "−4 K stability shift" slide separately says a fit at zero
shift costs **0.08 units**. Those are not in conflict — they are the degeneracy, quantified:

  * pin **one** melting-temperature lever and the other compensates: **0.08 units**;
  * pin **both** and it costs **7.6 units**.

That is the same dTm/`tm_scale` pair the eigenspectrum found (ERROR 2), stated in units anyone can
read, and it is the strongest single line in the deck. **Fold it into the −4 K slide** as the
quantitative version of what is already there. Retraction 2 (the threshold attractor) is internal
methodology and can go without replacement.

Check whether either retraction concerns something in a document already shared outside the group —
the synthesis report went to both postdocs. If so, that one stays, as a correction to a shared
record rather than an internal note. Report what you found.

---

NOTE TO USER: launch in an auto-approving mode. Six or seven slides and a re-render.

---

```
Work AUTONOMOUSLY; commit in parts, prefixed "E5: "; append to reports/ecoli_deck/DECISIONS.md.
Standing rules carry over. Check exit codes explicitly, never `cmd && check`. Continue on `e2/deck`
in ../etcGEMs-work; do not push to main; the PR stays unmerged. Write NOTHING under ../etcGEMs.

TASK 0 - premise
- Confirm worktree, branch, interpreter; confirm nothing of yours is running in the primary tree.
- Confirm the deck renders; record the baseline page count.
- Check whether `reports/E1_paper_register/` exists anywhere. Report yes or no - if no, E1 never
  ran and ERROR 3's OPEN_ITEMS half falls to this run.

TASK 1 - the stopping rule (ERROR 1)
- Read reports/P15_posterior/DECISIONS.md D1 and quote the criterion as actually pre-registered.
- Rewrite the bullet from that file. Do not paraphrase from this prompt.
- Sweep the whole deck for any other place an emcee-era criterion (autocorrelation time, chain
  length, walkers) is used to describe the nested runs, and fix each. Report every one found.

TASK 2 - the posterior slide (ERROR 2)
- Rewrite "Where the posterior stands": the run crashed, what the crash localised, and that no
  posterior exists. Keep "nothing is quoted" and keep the closing block - "mechanisms that
  reproduce, a likelihood we understand, and no intervals" is still exactly right.
- Verify every number against reports/P15_posterior/ before putting it on a slide.
- One bullet on what is being done: fix one of the pair, re-run at 15 dimensions, with the full
  eigenspectrum checked first for further degenerate pairs. **Do not claim it will work** - P16 has
  not reported.
- **Do not claim the degeneracy is a general property of etcGEMs.** It is measured in this model, by
  two routes. That is the claim.

TASK 3 - identifiability, with a worked example
- On the slide that answers which levers the data can move, add dTm/`tm_scale` as the concrete
  instance, stated correctly: **the pair is jointly constrained; neither member is individually
  determined.** That is a different thing from a flat lever and must not be presented as one - dTm
  is among the most tightly constrained parameters in the model.
- Check the three-way split E3 was asked to make is present and correct: levers the data move;
  levers nothing measures (genuinely unidentified); levers FIXED BY MEASUREMENT that the data is
  not asked to move. A jointly-constrained pair is a fourth category - add it or fold it in, and
  say which you did.

TASK 4 - the holdout (ERROR 3)
- Rewrite the "Never yet tested" bullet per ERROR 3, verified against report.qmd's Validation
  section - quote the line number and the 2.3-fold figure from the file.
- Fix docs/OPEN_ITEMS.md §0a R4 to the same statement.
- Update the "In flight" bullet on that slide to match TASK 2.

TASK 5 - the line-scan slide and figure 12 (JOB 4)
- Give `../P9_surface/task1_scan.png` a slide of its own and enlarge it; move the bullets to a
  preceding slide. Report its rendered size before and after.
- Write the lay explanation per JOB 4 - line scan, step size, what 20 % of range means, and why a
  cliff defeats a fitting algorithm. Verify "22", "902" and "12 of 22" against reports/P9_surface/
  and correct them if the files disagree.
- While you are there, apply the same legibility check E3 used to any figure this restructuring
  moves, and report.

TASK 6 - live and dead basins (JOB 5)
- Write the definitions per JOB 5 into "How many answers are there?", before the result. Read
  reports/P12_modes/ for the clustering/barrier method and the threshold, and state that the
  threshold was fixed in advance.
- Check reports/P13_support/ for whether the dead basin survives the current likelihood and state
  it accurately. Do not assert removal the files do not support.

TASK 7 - the retractions (JOB 6)
- Remove the retraction framing from the title and body.
- Fold retraction 1's content into the "-4 K stability shift" slide as the two-number statement:
  one lever pinned costs 0.08 units, both pinned costs 7.6 units with growth at 1.66 h-1 against
  two prior bounds. Verify both numbers against reports/Y3_tm_shift/ and reports/P12_modes/
  respectively. Connect it explicitly to the dTm/tm_scale pair from TASK 2 - it is the same finding
  in readable units.
- Report whether either retraction concerns anything in the synthesis report, which was shared
  outside the group. If so, that one stays and is framed as a correction to a shared record.

TASK 8 - render and verify
- Re-render. Verify: opens, every figure resolves, no overfull box, no unresolved citation. Report
  path and page count. Re-run scripts/stamp_reports.py. Commit the PDF if that is the directory's
  convention.

VERIFY (report all)
1. TASK 0: worktree, branch, baseline page count, whether E1 ever ran.
2. TASK 1: the criterion quoted from P15 D1; the rewritten bullet; every other emcee-era
   description found and fixed.
3. TASK 2: the rewritten slide; every number checked against its source; confirmation no claim is
   made about P16's outcome and none about etcGEMs in general.
4. TASK 3: the worked example as written; how the jointly-constrained category was handled.
5. TASK 4: the holdout bullet, with report.qmd's line number and the 2.3-fold figure; OPEN_ITEMS
   R4 before and after.
6. TASK 5: figure 12's rendered size before and after; the lay explanation as written; "22", "902"
   and "12 of 22" verified against P9_surface with any correction noted.
7. TASK 6: the basin definitions as written; the threshold and confirmation it was pre-registered;
   whether the dead basin survives the current likelihood, with the file that says so.
8. TASK 7: the retraction framing removed; retraction 1's two numbers verified against their
   sources and folded into the -4 K slide; whether anything shared outside the group was affected.
9. TASK 8: PDF path, page count before/after, render clean, stamps.
10. `git diff main --stat`: reports/ecoli_deck/, OPEN_ITEMS, stamps. Nothing under ../etcGEMs, src/
   or strains/.

CONSTRAINTS
- Every corrected number is read from its source file, not from this prompt.
- Do not touch the "-4 K stability shift" slide. It already carries Y3 correctly and is right.
- A jointly-constrained pair is not a flat lever. Do not conflate them.
- No claim about P16's outcome. No claim that the degeneracy generalises beyond this model.
- Jargon is explained where it first appears, in words a thermal biologist who has never opened
  this codebase can follow. No slide assumes knowledge of our prompt series or internal documents.
- Retraction 1's FINDING survives even though its framing goes. Do not lose the 7.6/0.08 pair.
- Autonomous; commit in parts: "E5: stopping rule", "E5: posterior slide", "E5: identifiability",
  "E5: holdout", "E5: line scans in plain words", "E5: basins", "E5: retractions", "E5: render".
```
