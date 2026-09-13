# Claude Code prompt — P16: read the whole eigenspectrum before fixing anything, then run the reduced posterior (autonomous, ~30 min then ~10 h)

Run from the project root (`.../MICROADAPT/etcGEMs`), on `../etcGEMs-venv`. **Merge PR #32 (P15)
first**, server-side, matching #14–#31; then `git switch main`, `git pull`, branch `p16/reduced`.
E-series work may be running in `../etcGEMs-work` — do not touch it.

**What P15 established, and it is a result rather than a failure.** Run 1 crashed at 9.9 h and
iteration 11,547 with dynesty's slice sampler proposing denormal steps (−5.4e-323, 5e-323,
1.04e-322) and a point bit-identical to the current one. The cause is in its own checkpoint: across
800 live points the smallest covariance eigenvalue is **1.947e-04**, its direction dominated by
**dTm +0.903 / tm_scale −0.217**, correlation **+0.831**, condition number **1,457**. The bounding
ellipsoid had been singular for hours — 1,124 divide-by-zero warnings.

**That is Y3's non-identified pair, confirmed by a wholly independent route.** Y3 profiled the
likelihood and found dTm compensable by `tm_scale` at a cost of 0.077 units. P15 watched a sampler's
live points collapse onto the same correlation. One is optimisation, the other is the geometry of a
point cloud; they share no machinery. **It is not a plateau** — dTm is the most tightly constrained
parameter in the model — so this is a different failure mode from everything P6–P14 chased.

**Why this prompt does the cheap thing first.** OPEN_ITEMS 1.24 proposes fixing `tm_scale` or dTm at
nominal and re-running at 15 dimensions. That is almost certainly right. But **only the smallest
eigenvalue has been looked at.** If the second-smallest is also near-singular — another degenerate
pair waiting — then the reduced run crashes again at hour ten for a different reason and another day
is gone. The whole spectrum is arithmetic on a file already on disk.

**And the choice of which to fix has scientific content.** Y3 established that what survives
reparameterisation is the **tail**: every solution puts the least-stable few per cent of enzymes
4–6 °C below the measured meltome. Fixing `tm_scale` = 1 and freeing dTm asserts the whole meltome
is ~4 K too hot. Fixing dTm = 0 and freeing `tm_scale` asserts its centre is right and its spread is
not — which is the more defensible physical position, because the least-stable proteins are exactly
those whose in-vitro melting temperature is least trustworthy (they aggregate). **But that depends
on how `tm_scale` is defined in the code** — whether it scales about zero, the mean, or something
else — and TASK 2 reads that before choosing rather than assuming it.

NOTE TO USER: launch in an auto-approving mode. TASK 1 is minutes. TASK 4 is one nested run of
roughly ten hours; a second seed follows only if the first converges.

REFERENCE, read first: `reports/P15_posterior/` report and DECISIONS D0–D3 (the 1.23 resolution, the
crash, the covariance analysis, and D3's retraction of D2); `reports/Y3_tm_shift/` (the profile, the
`tm_scale` compensation, the tail requirement); `reports/P11_nested/` (the dynesty wiring and its
proofs); `reports/P12_modes/`, `P13_support/`, `P14_posterior/`; `docs/OPEN_ITEMS.md` §0, 1.19,
1.20, 1.23, 1.24.

---

```
Work AUTONOMOUSLY; commit in parts, prefixed "P16: "; maintain reports/P16_reduced/DECISIONS.md
FROM THE FIRST JUDGEMENT CALL. Standing rules carry over. Check exit codes explicitly, never
`cmd && check`. Branch from main after the merge; do not push to main; end in a PR that is NOT
merged.

TASK 0 - merge and verify the inherited state
- Merge #32; switch; pull; branch. Resolve any conflict keeping BOTH sides and regenerating stamps;
  report file by file.
- Verify: clamp ON for eciML1515 and OFF elsewhere; gates 79/79 and 60/60 with it OFF; ten fresh
  evaluations at p38 give a spread of 0.0000000000. If any fails, STOP.
- Read OPEN_ITEMS 0a-0c; state in D0 which of R1-R4 this run moves (expected R1, with R2 clarified).

TASK 1 - the WHOLE eigenspectrum, from the checkpoint already on disk
No solving. Load P15's run-1 checkpoint and work from its 800 live points.
- Standardise each parameter (state how - by prior sd or by live-point sd; say which and why).
  Report ALL sixteen eigenvalues of the live-point covariance, ascending, with each direction's
  loadings on all sixteen parameters and the pairwise correlations that dominate it.
- Report the condition number, and the ratio of each eigenvalue to the largest.
- **The decision this produces, by a rule written into DECISIONS.md BEFORE the numbers are read:**
  a direction is NEAR-DEGENERATE if its eigenvalue is below a stated fraction of the largest (state
  it, e.g. 1e-3). Report how many directions qualify.
    * If exactly ONE qualifies (the dTm/tm_scale pair): fixing one parameter is sufficient; proceed.
    * If TWO OR MORE qualify: say so plainly and name each pair. Fixing one parameter will not be
      enough, and TASK 4 must not start - report what the full reduction would be and STOP for the
      user. Spending ten hours to crash on the second pair is the failure this task exists to
      prevent.
- Caveat honestly: live points late in a nested run concentrate in the high-likelihood region, so
  this covariance describes the posterior's bulk, not the prior. Say what that does and does not
  license.

TASK 2 - which parameter to fix, read from the code and Y3
- Read how `tm_scale` and `dTm` enter the thermal layer: what `tm_scale` scales, and about what
  centre. Quote the code. This governs the choice and this prompt's physical argument is void if
  the definition differs from what it assumes.
- State the two options and what each ASSERTS about the meltome, in one sentence each, then choose
  on the evidence:
    (a) fix `tm_scale` = 1, dTm free -> "the measured meltome is uniformly ~4 K too hot";
    (b) fix dTm = 0, `tm_scale` free -> "the meltome's centre is right, its spread is not".
  Y3's invariant is about the TAIL (least-stable few per cent, 4-6 C below measurement), and the
  least-stable proteins are those whose in-vitro Tm is least reliable. Weigh that against what the
  code actually does. Record the choice, the nominal value fixed, and its source.
- Record as CONSIDERED AND NOT TAKEN: reparameterising into the rotated basis rather than fixing.
  It preserves the information and removes the geometry, but the degenerate direction stays
  prior-dominated and the parameters stop meaning anything physical. One paragraph, no work.
- **Whichever is fixed, the model can no longer express that axis.** Say in one line what
  uncertainty is now hidden, so TASK 5 can carry it as a stated limitation rather than an omission.

TASK 3 - verify the reduction does what it claims, before spending a night on it
- Re-run the smallest-eigenvalue analysis on a SYNTHETIC reduction: drop the fixed parameter's row
  and column from P15's live-point covariance and report the new smallest eigenvalue and condition
  number. This is not a substitute for the run but it is a five-minute check that the reduction
  removes the singularity rather than moving it.
- Evaluate the log-likelihood at p38 with the parameter fixed at nominal and the rest unchanged.
  Report the cost in log-likelihood units. Y3 measured 0.077 for dTm = 0 with catalysis free; report
  what it is here with only the one parameter fixed.
- If the synthetic reduction leaves the condition number above ~500, STOP and report - the
  reduction has not fixed it.

TASK 4 - the reduced run
- dynesty, P11's wiring, each proof re-verified in one line. `first_update={'min_eff': 30}`.
  nlive = 800, `rslice`, dlogz < 0.1, 15 free parameters, checkpoint every 30 minutes, wall-clock
  cap 16 h. **Settings are P15's D1 exactly except the dimension** - do not change the sampler. If
  it crashes again, report the crash and its covariance diagnosis as P15 did; do not switch sampler
  in response.
- Write BEFORE running, and quote in the report: AGREED if a second seed's log Z agrees within
  combined error and no median differs by more than two Monte-Carlo errors. Run the second seed
  ONLY if the first converges.
- Carry P15's two pre-registered predictions forward unchanged: (i) the posterior moves away from
  parameter values placing any temperature within 1 % of `_MASK_G`, against P11's posterior as
  comparator; (ii) posterior-predictive growth at 15 C rises. Report against both as written.
- Progress line every 250 iterations to reports/P16_reduced/run.log.

TASK 5 - the posterior, if it converges and agrees
- Medians and 5/95 intervals for the fifteen free parameters, importance-weighted, beside P4's
  medians. **State the fixed parameter, its value, and the uncertainty that is now hidden** - this
  is a stated limitation, not a silent reduction.
- Width ratios; the GRADIENT / WALL-BOUNDED / FLAT classification by line scan through the new
  median. Flat marginals are R2 unidentifiability, not R1 failure (P14).
- **The tail**: where the posterior puts the least-stable few per cent of enzymes relative to the
  measured meltome. That is Y3's invariant and the quantity that survives this reparameterisation -
  report it, and report dTm or `tm_scale` only as a summary of it.
- R2 for growth and respiration at the posterior median, with the 1.42 floor and the clamp form
  named beside the respiration figure.
- Cost the remaining eight fits (1.17) at the measured rate. F LB stays HELD.

TASK 6 - record and reconcile
- reports/P16_reduced/report.md: the full spectrum; the choice and its reasoning; the synthetic
  check; the run; the posterior or the failure; both predictions against their outcomes.
- docs/OPEN_ITEMS.md: 1.24 closed with the choice made and the hidden uncertainty stated; 1.20
  updated with what the reduction implies for the meltome question; 1.19 and 1.12 appended; 1.17
  unblocked with costs if converged. Section 4: add - a sampler crash may be geometry rather than a
  bug, and the live-point covariance is where to look.
- reports/synthesis/evidence.csv: rows for the eigenspectrum, the fixed parameter, the agreement
  verdict, the tail position.
- Reconcile against 0c: which of R1-R4 moved; what is retracted or qualified by dated note; what
  this does NOT license - in particular, a posterior with a parameter fixed is not a posterior over
  the full model.
- Stamps.

VERIFY (report all)
1. TASK 0: #32 merged; gates; the ten-evaluation spread; D0.
2. TASK 1: all sixteen eigenvalues with loadings; the near-degeneracy rule quoted from before the
   numbers; how many directions qualify; the live-point caveat.
3. TASK 2: the code quoted for `tm_scale` and dTm; the two assertions; the choice with its
   reasoning; the reparameterisation recorded as not taken; the hidden uncertainty named.
4. TASK 3: the synthetic reduction's smallest eigenvalue and condition number; the log-likelihood
   cost of fixing.
5. TASK 4: settings; the agreement rule and both predictions quoted from before the run;
   iterations, evaluations, wall-clock, dlogz, log Z +/- error, n_eff; converged or the crash with
   its diagnosis.
6. TASK 5 (if converged): the fifteen-parameter table; the fixed parameter and hidden uncertainty;
   width ratios; GRADIENT/WALL/FLAT; the tail position; the R2 table; the 1.17 costs.
7. TASK 6: OPEN_ITEMS; the new hazard; evidence rows; the 0c reconciliation; stamps.
8. `git diff main --stat`: reports/P16_reduced/, strains/eciML1515 config if the fixed value lives
   there (state where), OPEN_ITEMS, evidence.csv, stamps, run outputs. Nothing under src/.

CONSTRAINTS
- TASK 1 before anything else. Two or more near-degenerate directions STOPS the run.
- The near-degeneracy rule is written before the eigenvalues are read.
- The choice of which parameter to fix is made from the code and Y3, not from this prompt's
  physical argument, which is void if the definition differs.
- Settings are P15's exactly except the dimension. No sampler change, especially not in response to
  a crash.
- A fixed parameter is a stated limitation carried in every summary, never a silent reduction.
- The tail is the reported quantity; dTm and `tm_scale` are summaries of it.
- Either outcome is the deliverable.
- Autonomous; commit in parts: "P16: spectrum", "P16: the choice", "P16: synthetic check",
  "P16: run", "P16: posterior", "P16: record".
```
