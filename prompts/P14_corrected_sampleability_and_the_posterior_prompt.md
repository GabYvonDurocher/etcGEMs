# Claude Code prompt — P14: fix the sampleability test, then earn the posterior (autonomous, ~1 h then ~20 h of runs)

Run from the project root (`.../MICROADAPT/etcGEMs`), on `../etcGEMs-venv`. **Merge PR #28 (Y3) and
PR #29 (P13) first**, server-side, matching #14–#27; then `git switch main`, `git pull`, branch
`p14/posterior`. Nothing is running in either tree.

**Why this exists.** P13 did everything asked of it and stopped at TASK 3 on a rule fixed in
advance. That was correct discipline. **The rule was wrong, and it is mine.** I specified
SAMPLEABLE as "no 0.05 sd step above 5 log-likelihood units" as a proxy for *discontinuity*. It does
not measure discontinuity — it measures steepness. The step that stopped P13 is 8.55 units on the
`topt_scale` axis, monotone, forty units below p38, and **reads 3.20 on the same line at θ_A under
the same rule with nothing about the likelihood changed**. P13 logged that centre-dependence as a
§4 hazard; it is also the proof that the rule measures how good the centre is, not whether the
surface is broken.

**And the rule tests the wrong property for this sampler.** Nested sampling depends only on the
*ordering* of likelihood values — it is invariant to any monotone transformation of the likelihood,
so gradient magnitude is irrelevant to it. What genuinely breaks it is **plateaus**: sets of
positive prior volume with exactly equal likelihood, which void the volume-shrinkage estimate
(Fowlie, Handley & Su 2021, flagged in P11). Steepness is not a problem. Flatness is.

**What P13 did establish, and it stands.** Impute is withdrawn — a non-growing cell still respires
for maintenance, and 4 of 4 dead temperatures among the live endpoints are feasible with real O₂ of
0.525–5.674, so the growth mask was discarding predictions. **Clamp is adopted** on the stronger
justification: it scores those predictions. It is state-independent at the boundary (ten fresh
evaluations, spread 0.0000000000, where current fails at 0.0157). And the **knife-edge is an
attractor** — four of twelve independent optimisations park a temperature on `_MASK_G` exactly,
p38's 15 °C growth sitting 1.4e-12 below it.

**One thing from Y3 that changes how a number in TASK 3 must be read.** dTm is not load-bearing:
with the compensating parameters free the profile is flat, and dTm = 0 costs 0.077 units with the
model still growing at 1.739 /h. The compensation runs through `tm_scale`, which is a *stability*
parameter, not catalysis — two redundant knobs on one axis. What survives reparameterisation is a
**per-enzyme** statement: every solution puts the least-stable few per cent of enzymes 4–6 °C below
the measured meltome. So dTm's posterior is a summary of that tail requirement, not a result in
itself, and TASK 3 must report it that way.

NOTE TO USER: launch in an auto-approving mode. TASK 1 is under an hour. TASK 2 is two nested runs
of roughly ten hours each, **sequential** — each wants 16 processes and P11 measured 8.5/16
utilisation from stragglers, so overlapping them buys little and confounds the timing. Expect run 1
overnight, run 2 through tomorrow.

REFERENCE, read first: `reports/P13_support/report.md` and DECISIONS (clamp, the attractor, the
centre-dependence hazard, the line that stopped it); `reports/Y3_tm_shift/report.md` (the flat dTm
profile, the `tm_scale` compensation, the tail requirement); `reports/P11_nested/` (the dynesty
wiring and its proofs, `first_update`, the cost model, the seed-disagreement table);
`reports/P12_modes/` (the basin map, the ceiling test and its dated qualification);
`docs/OPEN_ITEMS.md` §0, 1.12, 1.17, 1.19, 1.20, 1.21, 1.23.

---

```
Work AUTONOMOUSLY; commit in parts, prefixed "P14: "; maintain reports/P14_posterior/DECISIONS.md
FROM THE FIRST JUDGEMENT CALL. Standing rules carry over. Check exit codes explicitly, never
`cmd && check`. Branch from main after the merges; do not push to main; end in a PR that is NOT
merged.

TASK 0 - merge both, start clean, verify the state P13 left
- Merge #28 (Y3) then #29 (P13), server-side. If the second conflicts on OPEN_ITEMS, evidence.csv
  or stamps, resolve in a temporary worktree keeping BOTH sides, regenerate stamps rather than
  hand-merging, and report file by file. Confirm both MERGED; switch; pull; branch.
- Verify, do not assume: the clamp option exists in the core, defaults OFF, is ON for eciML1515
  only, and the seven-strain gate is 79/79 and 60/60 with it OFF. Report.
- Re-confirm P13's state-independence result at p38 under clamp: ten fresh-model evaluations,
  spread must be 0.0000000000. If it is not, STOP - something did not survive the merge.
- Read docs/OPEN_ITEMS.md 0a-0c. In D0 state which of R1-R4 this run moves (expected R1 only).

TASK 1 - the corrected test, criterion written BEFORE it is applied
Write the criterion into DECISIONS.md first, then compute. Do not revise it afterwards.
- (a) DISCONTINUITY TEST, on the largest step of every one of P11's twelve lines under clamp,
  centred at p38. Refine the grid at that step: evaluate at h, h/2, h/4, h/8 where h is the
  0.05 sd spacing. For a smooth function |delta| falls in proportion to h; for a genuine jump it
  converges to a constant. Report the four values and the ratio per halving, per line. SMOOTH if
  |delta| roughly halves each time (state your tolerance, e.g. ratio in [0.35, 0.65]); JUMP if it
  plateaus. Fresh model per evaluation, single process.
- (b) PLATEAU TEST, which is what dynesty actually needs. On all twelve lines under clamp: count
  exactly-equal adjacent log-likelihood values, report the longest run and the fraction of all
  evaluations lying on any plateau. P12 found kappa_scale and f_metab exactly flat within a
  posterior sd - state whether those constitute plateaus in the nested-sampling sense and what
  dynesty does with them.
- (c) FEASIBILITY BOUNDARIES are not cliffs and do not disqualify. Report where each line crosses
  into infeasibility, if it does, relative to +/-1 sd of p38. The model makes no claim beyond that
  boundary; nested sampling proposes there, gets -inf and discards, exactly as it handles a prior
  bound. Do not smooth, floor or soften it.
- THE CORRECTED CRITERION: SAMPLEABLE if every line's largest step tests SMOOTH under (a) AND no
  plateau under (b) spans more than a stated fraction of a line. **Steepness alone does not
  disqualify.**
- Report the twelve lines under the OLD rule and the NEW one side by side, so the change is
  visible and auditable. Record plainly in DECISIONS.md that the original rule was a proxy for
  discontinuity that measured steepness, was centre-dependent (3.20 at theta_A against 8.55 at
  p38), and cost a run slot.
- If any line tests JUMP: STOP and report which, where, and its refinement series. Do not start
  TASK 2.

TASK 2 - the two runs, SEQUENTIALLY, with everything written first
- dynesty, P11's wiring, each of its proofs re-verified in one line: prior transform against the
  priors, pool == single-process at p38 to 1e-4, checkpoint restore. Add
  `first_update={'min_eff': 30}` (P11 D4: ~1 h of single-core unit-cube phase without it).
- nlive = 800, `rslice`, dlogz < 0.1, two runs with DIFFERENT seeds, one after the other.
  Checkpoint every 30 minutes. Wall-clock cap 16 h each. If run 1 hits the cap: checkpoint
  cleanly, report STALLED with a projection, and do NOT start run 2 - a second stalled run
  answers nothing.
- Written BEFORE running and quoted in the report: AGREED if the two log Z agree within their
  combined reported error AND no posterior median differs by more than two Monte-Carlo errors;
  DISAGREED otherwise, reported with the same table P11 produced.
- ALSO written before running - the two predictions from P13's addendum 2, which could not be
  evaluated there:
    (i) the clamp posterior moves AWAY from parameter values placing any temperature within 1 %
        of _MASK_G. Report the fraction of posterior samples doing so, against P11's posterior as
        comparator.
    (ii) the 15 C growth residual becomes more expensive, so the fit should trade toward growing
        at the cold end. Report posterior-predictive growth at 15 C under both.
  If (i) holds, the attractor is confirmed by a second route; if not, it was optimiser-specific
  and P12's dated qualification narrows. Report against the prediction as written, either way.
- Progress line every 250 iterations to reports/P14_posterior/run.log: iteration, evaluations,
  efficiency, log Z, dlogz, wall-clock, evals/s.

TASK 3 - the posterior, if AGREED
- Medians and 5/95 intervals for all sixteen parameters, importance-weighted (state the
  resampling), beside P4's medians and P11's main-run values.
- Posterior/prior width ratio per parameter, and P11's classification by line scan through the new
  median: GRADIENT-DETERMINED, WALL-BOUNDED or FLAT. P12 found f_metab pinned at 0.28000 and
  f_maint at ~0.35 from every starting point - state whether the posterior agrees they are flat.
- **dTm, read correctly.** Report its posterior and interval, then state - citing Y3 - that dTm is
  NOT load-bearing (profile flat, dTm = 0 costs 0.077 units with growth 1.739 /h), that the
  compensation runs through `tm_scale` which is a stability parameter and not catalysis, and that
  what survives reparameterisation is the per-enzyme requirement that the least-stable few per
  cent of enzymes sit 4-6 C below the measured meltome. Report where the posterior puts that tail.
  Do not present dTm's value as a result in itself.
- R2 for growth and respiration at the posterior median, against P4's and Parsa's, with the 1.42
  floor and the clamp support form named beside the respiration figure.
- Cost the remaining eight fits (1.17) at the measured rate. F LB stays HELD (P10 D1).

TASK 4 - record and reconcile
- reports/P14_posterior/report.md: the corrected test and the old/new comparison; the runs; the
  posterior or the stall; the two predictions against their outcomes.
- docs/OPEN_ITEMS.md: 1.19 closed or restated; 1.12 appended; 1.17 unblocked with costs if AGREED;
  1.23 closed with the corrected test. Section 4: keep P13's centre-dependence hazard and add that
  a smoothness criterion must test discontinuity by grid refinement, not by step size.
- reports/synthesis/evidence.csv: rows for the corrected criterion, the agreement verdict, dTm's
  interval with its Y3 scoping, and the two predictions' outcomes. README correction note
  extended. No re-render.
- **Reconcile against 0c** in the closing section: which of R1-R4 moved; what is retracted or
  qualified by dated note, numbers unedited; what this does NOT license.
- Stamps.

VERIFY (report all)
1. TASK 0: both PRs merged, conflicts resolved file by file, the commit; clamp verified ON for
   eciML1515 and OFF elsewhere; gates; the ten-evaluation spread at p38; D0's R1-R4 statement.
2. TASK 1: the criterion quoted from before it was applied; per line the refinement series and
   its ratios; the plateau counts; the feasibility crossings; the old-rule/new-rule table;
   SAMPLEABLE or the line that tests JUMP.
3. TASK 2: settings; the agreement rule and both predictions quoted from before the runs; per run
   iterations, evaluations, wall-clock, dlogz, log Z +/- error, n_eff; AGREED or DISAGREED.
4. TASK 3 (if AGREED): the sixteen-parameter table; width ratios; GRADIENT/WALL/FLAT; dTm with
   its Y3 scoping and the tail position; the R2 table; the 1.17 costs.
5. TASK 4: OPEN_ITEMS items; the new §4 hazard; evidence rows; the 0c reconciliation; stamps.
6. `git diff main --stat`: reports/P14_posterior/, OPEN_ITEMS, evidence.csv, synthesis README,
   stamps, two run outputs. Nothing under src/ or strains/ - clamp is already committed by P13.

CONSTRAINTS
- The corrected criterion is written before it is applied and not revised after.
- Steepness does not disqualify. Feasibility boundaries do not disqualify. Plateaus and genuine
  jumps do.
- Nothing about the likelihood, the floor, the tie-break, the clamp form, the priors, the data or
  c_max changes. No lexicographic tie-break (1.22).
- The two runs are SEQUENTIAL with different seeds. A stalled first run stops the task.
- dTm is reported as a summary of the tail requirement, per Y3, never as a result in itself.
- Either verdict is the deliverable.
- Autonomous; commit in parts: "P14: corrected test", "P14: run 1", "P14: run 2",
  "P14: posterior", "P14: record".
```
