# Claude Code prompt — P9: is the likelihood surface rough? Look at the surface, not the sampler (autonomous, ~30–45 minutes)

Run from the project root (`.../MICROADAPT/etcGEMs`), on `../etcGEMs-venv`. **Merge PR #23 (P8)
first**, server-side, matching #14–#22; then `git switch main`, `git pull`, branch `p9/surface`.
Nothing is running.

**Where this stands.** Three samplers — stretch at 40 and 128 walkers, DE moves, zeus slice — all
show τ growing in proportion to chain length on the configuration-D fits. P8's PCA found no ridge:
the first component carries 16.5% of the variance and τ along every one of the sixteen components
lies between 110 and 121. Isotropic. The log-posterior is flat. The ensemble is unimodal.

**A smooth posterior mixes somewhere.** This one mixes nowhere, in every direction, under three
unrelated samplers. That is not the signature of a hard posterior; it is the signature of a **rough
likelihood surface** — many small discontinuities at scales below the ensemble spread, so walkers
sit in tiny basins and hop rarely. The mechanism is in plain sight: the growth prediction is an LP
solution, piecewise smooth in θ with a kink or jump at every basis change, and P7 measured the
likelihood reproducing only to 1e-4 under a process pool.

**Why this must be answered before any model decision.** D6's options (i) and (ii) — fix four
parameters, narrow the discrepancy priors — change the posterior's dimension and shape. Neither
changes the surface's roughness. If the surface is rough, a 12-dimensional refit produces the same
τ ∝ N and a day is spent learning that. If it is smooth, (i) is worth its run. Thirty minutes here
decides which.

NOTE TO USER: launch in an auto-approving mode. No sampling. A few hundred likelihood evaluations
along lines through the MAP, plus arithmetic on chains already on disk. Merges one PR first.

REFERENCE, read first: `reports/P8_ridge/report.md` (the PCA; the zeus cost stop);
`reports/P7_walkers/DECISIONS.md` D5 (the 1e-4 non-reproducibility); `reports/P6_convergence/
DECISIONS.md` D3a (the state-versus-identifiability test — its fresh-model evaluation pattern is what
TASK 1 reuses); `reports/P4_refit/` for the MAP and the fit definition.

---

```
Work AUTONOMOUSLY; commit in parts, prefixed "P9: "; maintain reports/P9_surface/DECISIONS.md FROM
THE FIRST JUDGEMENT CALL. Standing rules carry over. Check exit codes explicitly, never
`cmd && check`. Branch `p9/surface` from main after the merge; do not push to main; end in a PR
that is NOT merged. No emcee, no zeus, no fit.

TASK 0 - merge and start clean
- Confirm nothing is running. Merge #23 server-side; confirm MERGED; switch, pull, branch.
- Confirm the interpreter is ../etcGEMs-venv. Do not run the gates again unless src/ changed
  since P8 (it should not have); report which.

TASK 1 - line scans through the MAP, single process, fresh model per evaluation
Configuration D NLDM, P6's model/data/priors/c_max exactly. Take the MAP (or the posterior
median) from P4's chain; state which and its values.
- Directions: (a) each of the sixteen parameter axes; (b) the top three principal components from
  P8's PCA; (c) three random unit directions with a recorded seed. Twenty-two lines.
- Along each line, evaluate the LOG-LIKELIHOOD (not the posterior - keep the prior out so the
  surface is the model's) at 41 points spanning +/- one posterior standard deviation of that
  direction (from P8's standardisation), i.e. a step of 0.05 sd. That is the scale the ensemble
  actually proposes at.
- Single process. A fresh model per evaluation, exactly as D3a's "rebuild fresh" arm did, so no
  solver state carries between points. Report wall-clock; it is ~900 evaluations at ~0.3 s.
- For each line report, and plot on one page: the 41 values; the number of sign changes in the
  first difference (a smooth unimodal curve has 0 or 1); the largest single-step jump in
  log-likelihood; and the largest jump as a fraction of the line's total range.
- Then the summary that decides everything: across the 22 lines, the median and maximum number of
  first-difference sign changes, and the median and maximum single-step jump. State a rule BEFORE
  computing: e.g. SMOOTH if the median sign-change count is <= 2 and no single step exceeds 5 % of
  the line's range; ROUGH if the median count is >= 5 or any step exceeds 20 %; else MIXED.
  Write it into DECISIONS.md first.

TASK 2 - is the roughness the solver?
If TASK 1 reads ROUGH or MIXED, establish whether the jaggedness is the LP or the model:
- Re-evaluate the roughest three lines with the solver tolerances tightened (feasibility,
  optimality, and the barrier/crossover convergence if Gurobi is in use - state which parameters
  and the values before and after). If the jumps shrink or vanish, the roughness is numerical.
- Re-evaluate the same three lines with a FIXED solver method (e.g. dual simplex only, no
  concurrent or barrier), which removes method-selection as a source of basis change. Report.
- At the three largest jumps, report what changed in the LP solution across the step: which
  reactions changed basis status, and by how much growth and O2 moved. A jump that coincides with
  a basis change in a handful of reactions is a kink in the model's piecewise structure; a jump
  with no basis change is numerical noise.
- Do NOT change the model. Do NOT adopt any tolerance or method as a new default. This task
  characterises; the decision to change the fitting code is the user's.

TASK 3 - what the existing chains say, free
On P7's 128-walker chain and the 40-walker history, post-burn-in:
- Per-walker acceptance fraction. Report the distribution: min, quartiles, max. A rough surface
  leaves some walkers nearly frozen; report how many walkers accepted fewer than 5 % of proposals.
- Per-walker log-likelihood over time: how many walkers sit at a constant log-likelihood for runs
  of >= 50 steps? That is a walker in a basin.
- The step-size distribution of ACCEPTED moves, in standardised units, against the proposal
  distribution. If accepted moves are much smaller than proposed ones, the walkers are confined.

TASK 4 - the verdict, and what it licenses
Write reports/P9_surface/report.md ending in one of:
  (a) SMOOTH. The surface is not the problem. D6 option (i) is worth its run; say what P10 would be.
  (b) ROUGH, NUMERICAL. The jaggedness is solver tolerance or method selection. Then the fix is to
      the likelihood evaluation (tolerances, fixed method, or a noise-aware likelihood that treats
      the 1e-4 as measurement error), NOT to the model or the priors. State what each would cost
      and what would need re-verifying (the P3 gate, at minimum). Do not implement.
  (c) ROUGH, STRUCTURAL. The jaggedness is the model's piecewise-linear response to its parameters
      - real kinks at basis changes. Then no sampler and no model reduction gives intervals from
      this likelihood as written; intervals need either a smoothed surrogate or a different
      likelihood, and that is a modelling decision. State it plainly. Option (iv) stands.
  (d) MIXED - say which lines are which and what that implies.
- In every case: does the roughness also explain the D6 burn-in drift (1500 steps to find the
  discrepancy scale)? One paragraph.
- docs/OPEN_ITEMS.md: item 1.12 gets the verdict appended; add one PI item under 1 for the
  decision it raises, worded per the verdict.
- reports/synthesis/evidence.csv: one row for the surface verdict. README correction note
  extended if the verdict changes what section 7 must say. No re-render.
- Stamps.

VERIFY (report all)
1. TASK 0: #23 merged; main commit; branch; interpreter.
2. TASK 1: the 22 lines with sign-change counts and largest jumps; the summary; the rule quoted
   from before it was applied; the one-page figure's path; wall-clock.
3. TASK 2 (if run): tolerances and method before/after; whether the jumps shrank; the basis-change
   report at the three largest jumps.
4. TASK 3: per-walker acceptance distribution; frozen-walker count; accepted-vs-proposed step
   sizes.
5. TASK 4: the verdict; what it licenses; OPEN_ITEMS; evidence row; README note; stamps.
6. `git diff main --stat`: reports/P9_surface/, OPEN_ITEMS, evidence.csv, synthesis README, stamps.
   Nothing under strains/ or src/. No sampler run. No default changed.

CONSTRAINTS
- No sampling. No fit. No change to the model, the priors, the solver defaults or the fitting code.
- The smooth/rough rule is written before the scans are summarised.
- Fresh model per evaluation in TASK 1; single process. The point is to see the surface without
  the pool's non-reproducibility on top of it.
- TASK 2 characterises; it adopts nothing.
- Either verdict is the deliverable. (c) is as important to report as (a).
- Autonomous; commit in parts.
```
