# Claude Code prompt — P15: the criterion resolved, now run the posterior (autonomous, ~20 h of runs)

Run from the project root (`.../MICROADAPT/etcGEMs`), on `../etcGEMs-venv`. **Merge PR #30 (P14)
first**, server-side, matching #14–#29; then `git switch main`, `git pull`, branch `p15/posterior`.
Nothing is running in either tree.

**The decision this prompt carries.** P14 refused to lift its own criterion after seeing the data,
which was right. The PI has now resolved OPEN_ITEMS 1.23: **the discontinuity conjunct is lifted.**
The reasoning must be recorded as follows, because it matters that this is not a threshold moved to
suit inconvenient data.

  * The conjunct was **wrong when written**, on an argument available before any data existed. The
    addendum that specified it correctly named plateaus as nested sampling's failure mode and then
    required no-jumps *as well*. Those are different objects.
  * Nested sampling estimates Z = ∫ L dX with X(λ) the prior volume where L > λ. It needs L to have
    **no atoms** under the prior: an atom makes X(λ) jump and voids the shrinkage estimate
    X_i ≈ exp(−i/nlive), which assumes live points uniform in X. **A plateau creates that atom.** A
    jump discontinuity in L(θ) instead leaves a *gap* in L's support — X(λ) flat over an interval
    of λ carrying no prior mass — and Z = Σ L_i w_i remains a valid Riemann sum in X.
  * P14 measured **0 of 480 adjacent evaluations exactly equal**: no plateaus. The test that matters
    passes perfectly.
  * The four real jumps are **0.145–0.885 units**, all one mechanism (97–100 % respiration term,
    growth unchanged to five decimals, O₂ moving 0.57–1.86× at a single cold temperature) — the
    residue of P9's LP vertex switch, two orders of magnitude below its diagnosis. The **growth-term
    kinks P11 accepted as irreducible are 1–3 units** and no respiration change touches them
    (P10). So 1.22 would remove the smaller discontinuities while larger ones remain from another
    term: the jumps are not the binding constraint on this likelihood.

**What P14 established and this run inherits.** The refinement test is a proper instrument —
`axis:topt_scale` refines 8.5517 → 4.3325 → 2.2295 → 1.1236, ratios 0.507 / 0.515 / 0.504, textbook
linear scaling, so pure steepness. And the old rule **ranked all twelve lines backwards**: steps of
0.05–0.59 that do not shrink are genuine discontinuities while the 8.55 is not. The flat directions
resolved as predicted in advance — {L = c} is codimension-1 extruded along the axis, zero 16-D
volume, so dynesty returns the prior as the marginal. That is **R2 unidentifiability surfacing
honestly in the posterior, not an R1 failure**, and TASK 2 must report it that way.

NOTE TO USER: launch in an auto-approving mode. Two nested runs of roughly ten hours each, run
**sequentially** — each wants 16 processes and P11 measured 8.5/16 utilisation from stragglers, so
overlapping them buys little and confounds the timing. Run 1 overnight, run 2 through the following
day.

REFERENCE, read first: `reports/P14_posterior/report.md` and DECISIONS (the refinement instrument,
the plateau census, the feasibility exemption, D2's corrected first pass); `reports/P13_support/`
(clamp, the attractor, the centre-dependence hazard); `reports/Y3_tm_shift/` (the flat dTm profile,
the `tm_scale` compensation, the tail requirement); `reports/P11_nested/` (the dynesty wiring and
its proofs, `first_update`, the cost model, the seed-disagreement table); `docs/OPEN_ITEMS.md` §0,
1.12, 1.17, 1.19, 1.20, 1.22, 1.23.

---

```
Work AUTONOMOUSLY; commit in parts, prefixed "P15: "; maintain reports/P15_posterior/DECISIONS.md
FROM THE FIRST JUDGEMENT CALL. Standing rules carry over. Check exit codes explicitly, never
`cmd && check`. Branch from main after the merge; do not push to main; end in a PR that is NOT
merged.

TASK 0 - merge, verify the inherited state, record the 1.23 decision BEFORE running
- Merge #30 server-side; switch; pull; branch. Resolve any conflict keeping BOTH sides,
  regenerating stamps rather than hand-merging; report file by file.
- Verify, do not assume: clamp is ON for eciML1515 and OFF elsewhere; the seven-strain gate is
  79/79 and 60/60 with it OFF; ten fresh-model evaluations at p38 under clamp give a spread of
  0.0000000000. If any fails, STOP - something did not survive the merge.
- Write the 1.23 resolution into DECISIONS.md D0, in the terms given in this prompt's preamble:
  the conjunct was wrong when written, the argument (atoms void shrinkage, gaps do not), the
  plateau census that passes, the jump sizes against the irreducible growth kinks, and the PI's
  decision. **State explicitly that this is a criterion corrected on an argument that predates the
  data, not a threshold moved to accommodate it** - and that P14 was right to refuse to move it
  itself. Commit D0 alone, before anything else runs.
- Read docs/OPEN_ITEMS.md 0a-0c; state in D0 which of R1-R4 this run moves (expected R1 only).

TASK 1 - the two runs, SEQUENTIALLY, everything written first
- dynesty, P11's wiring, each proof re-verified in one line: prior transform against the priors,
  pool == single-process at p38 to 1e-4, checkpoint restore. Include
  `first_update={'min_eff': 30}` (P11 D4: ~1 h of single-core unit-cube phase without it).
- nlive = 800, `rslice`, dlogz < 0.1, two runs with DIFFERENT seeds, one after the other.
  Checkpoint every 30 minutes. Wall-clock cap 16 h each. If run 1 hits the cap: checkpoint
  cleanly, report STALLED with a projection, and do NOT start run 2.
- Written BEFORE running and quoted verbatim in the report:
    AGREED if the two log Z agree within their combined reported error AND no posterior median
    differs by more than two Monte-Carlo errors; DISAGREED otherwise, with the table P11 produced.
- Also written before running - the two predictions orphaned by P13 and P14, now evaluable:
    (i)  the clamp posterior moves AWAY from parameter values placing any temperature within 1 %
         of _MASK_G. Report the fraction of posterior samples doing so, against P11's posterior as
         comparator. P13 found four of twelve optimisations parked there exactly.
    (ii) the 15 C growth residual becomes more expensive, so the fit should trade toward growing at
         the cold end. Report posterior-predictive growth at 15 C under both.
  If (i) holds the attractor is confirmed by a second route; if not it was optimiser-specific and
  P12's dated qualification narrows. Report against the prediction as written, either way.
- Progress line every 250 iterations to reports/P15_posterior/run.log: iteration, evaluations,
  efficiency, log Z, dlogz, wall-clock, evals/s.

TASK 2 - the posterior, if AGREED
- Medians and 5/95 intervals for all sixteen parameters, importance-weighted (state the
  resampling), beside P4's medians and P11's main-run values.
- Posterior/prior width ratio per parameter, and the classification by line scan through the new
  median: GRADIENT-DETERMINED, WALL-BOUNDED or FLAT.
- **The flat directions, reported as P14 resolved them.** Where a marginal returns the prior, say
  so explicitly and state that this is the model being unidentified in that direction given this
  data (R2), NOT a sampling failure (R1) - P14 established {L = c} there has zero 16-D volume.
  P12 found f_metab pinned at 0.28000 and f_maint at ~0.35 from every starting point; state
  whether the posterior agrees.
- **dTm, read correctly.** Report its posterior and interval, then state - citing Y3 - that dTm is
  NOT load-bearing (the profile is flat; dTm = 0 costs 0.077 units with growth 1.739 /h), that the
  compensation runs through `tm_scale`, a stability parameter and not catalysis, and that what
  survives reparameterisation is the per-enzyme requirement that the least-stable few per cent of
  enzymes sit 4-6 C below the measured meltome. Report where the posterior puts that tail. Do not
  present dTm's value as a result in itself.
- R2 for growth and respiration at the posterior median, against P4's and Parsa's, with the 1.42
  floor and the clamp support form named beside the respiration figure.
- Cost the remaining eight fits (1.17) at the measured rate. F LB stays HELD (P10 D1).

TASK 3 - record and reconcile
- reports/P15_posterior/report.md: D0's reasoning; the runs; the posterior or the stall; both
  predictions against their outcomes; the flat directions as R2 not R1.
- docs/OPEN_ITEMS.md: 1.23 closed with the resolution; 1.19 closed or restated; 1.12 appended;
  1.17 unblocked with costs if AGREED; 1.22 restated with what P14 measured (the jumps it would
  remove, and that they are below the irreducible growth kinks - so it is a cost optimisation for
  the remaining eight fits, not a correctness fix). Section 4: keep P13's and P14's hazards and
  add - a criterion must test the failure mode it names; the one specified here named plateaus and
  then also required no-jumps, and the two are different objects.
- reports/synthesis/evidence.csv: rows for the resolved criterion, the agreement verdict, dTm's
  interval with its Y3 scoping, the two predictions' outcomes, and the flat-direction result.
  README correction note extended. No re-render.
- **Reconcile against 0c** in the closing section: which of R1-R4 moved; what is retracted or
  qualified by dated note, numbers unedited; what this does NOT license.
- Stamps.

VERIFY (report all)
1. TASK 0: #30 merged, conflicts file by file, the commit; clamp ON for eciML1515 and OFF
   elsewhere; gates; the ten-evaluation spread; D0 committed alone before any run, with the 1.23
   reasoning quoted.
2. TASK 1: settings; the agreement rule and both predictions quoted from before the runs; per run
   iterations, evaluations, wall-clock, dlogz, log Z +/- error, n_eff; AGREED or DISAGREED.
3. TASK 2 (if AGREED): the sixteen-parameter table; width ratios; GRADIENT/WALL/FLAT with the flat
   directions stated as R2; dTm with its Y3 scoping and the tail position; the R2 table; the 1.17
   costs.
4. TASK 3: OPEN_ITEMS items; the new §4 hazard; evidence rows; the 0c reconciliation; stamps.
5. `git diff main --stat`: reports/P15_posterior/, OPEN_ITEMS, evidence.csv, synthesis README,
   stamps, two run outputs. Nothing under src/ or strains/.

CONSTRAINTS
- Nothing about the likelihood, the floor, the tie-break, the clamp form, the priors, the data or
  c_max changes. No lexicographic tie-break (1.22) - it would confound the runs.
- The agreement rule and both predictions are written before the runs and not revised after.
- The two runs are SEQUENTIAL with different seeds. A stalled first run stops the task.
- A flat marginal is reported as unidentifiability (R2), never as a sampling failure (R1).
- dTm is reported as a summary of the tail requirement, per Y3, never as a result in itself.
- Either verdict is the deliverable.
- Autonomous; commit in parts: "P15: the 1.23 resolution", "P15: run 1", "P15: run 2",
  "P15: posterior", "P15: record".
```
