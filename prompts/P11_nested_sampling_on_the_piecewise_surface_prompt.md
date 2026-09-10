# Claude Code prompt — P11: the last wall, an absolute smoothness rule, and a sampler that matches a piecewise surface (autonomous, ~3–4 hours)

Run from the project root (`.../MICROADAPT/etcGEMs`), on `../etcGEMs-venv`. **Merge PR #25 (P10)
first**, server-side, matching #14–#24; then `git switch main`, `git pull`, branch
`p11/nested`. Nothing is running.

**Where this stands.** P10 built the tie-break and the variance floor and cut the cliffs from
13–72 log-likelihood units to single digits — largest remaining 7.8 (one O₂ vertex jump at 20 °C
above the floor), the rest 1–3 units, of which the growth-term kinks are the LP being an LP. It
stopped, correctly, because P9's smoothness rule did not read SMOOTH. But that rule was *relative* —
a step above 20% of the line's range — and P10 shrank the ranges along with the cliffs. What decides
whether a walker can cross a step is its *absolute* height: e⁻³⁰ is a wall, e⁻² is a kink.

**Two decisions taken, both of which this prompt executes rather than revisits.**
  1. The floor moves to the largest measured jump, not the modal temperature's. One line. It
     removes the 7.8.
  2. The growth term is NOT floored. Its 1–3 unit kinks are the model's piecewise-linear response
     to its parameters, present in every enzyme-constrained model, and inflating the variance on
     the primary data to make MCMC comfortable trades information for convenience.

**The sampler changes class, for a reason the evidence now supports.** P6–P8 tried three
random-walk ensemble samplers on a surface that turned out to be cliffed; they were the wrong tool
for a reason nobody could see. With the walls down, what remains is *intrinsically piecewise* with
single-digit kinks. Random-walk MCMC on plateaus with kinks mixes slowly by construction. Nested
sampling needs only the *ordering* of likelihood values, not smoothness or gradients, and its
parallelism is over independent likelihood calls — no worker starves the rest, which is what killed
zeus. Li et al. used SMC-ABC on their yeast model, a sampler with the same property; this is
probably why. `dynesty` is the implementation; at ~1.35 s per evaluation with pFBA and 16
processes, 50–100k evaluations is 1–2.5 h.

NOTE TO USER: launch in an auto-approving mode. Merges one PR. Minutes of setup, then one nested
run of D NLDM, 1–3 h. Nothing else changes. If nested sampling also stalls, it stops and says so.

REFERENCE, read first: `reports/P10_respiration_likelihood/report.md` (the floor, the remaining
steps per line, the unused fit runner); `reports/P9_surface/` (the line-scan instrument);
`reports/P7_walkers/` (the checkpointing driver); `reports/P4_refit/` (the fit definition, priors,
the MAP and medians to compare against).

---

```
Work AUTONOMOUSLY; commit in parts, prefixed "P11: "; maintain reports/P11_nested/DECISIONS.md FROM
THE FIRST JUDGEMENT CALL. Standing rules carry over. Check exit codes explicitly, never
`cmd && check`. Branch from main after the merge; do not push to main; end in a PR that is NOT
merged.

TASK 0 - merge; the floor; the absolute rule
- Merge #25; switch; pull; branch. Gates 79/79, 60/60 on ../etcGEMs-venv with the options OFF.
- Move the respiration floor to the largest measured vertex jump (P10 reports it; read the number
  and its line, do not assume). One value, one commit. Report old and new.
- Write the absolute smoothness rule into DECISIONS.md BEFORE re-scanning: a line is SAMPLEABLE if
  no single 0.05 sd step exceeds 5 log-likelihood units; the surface is SAMPLEABLE if every line
  is. Report P9's twelve lines under the new floor by this rule AND by P9's relative rule, side by
  side, so the reader sees why the rule changed and what it would have said. The growth-term kinks
  will appear in this table; they are expected and are reported, not fixed.
- If any line still has a step above 5 units after the floor move, STOP and report which and why.

TASK 1 - wire dynesty behind the same likelihood
- Install dynesty into ../etcGEMs-venv; add to requirements.lock.txt; report the version.
- Prior transform: dynesty samples the unit cube; write the transform from P4's priors exactly
  (state each prior's form and the transform used - uniform, log-uniform, half-normal via ppf).
  Prove it: draw 10,000 samples through the transform and report their marginal means and
  quantiles against the priors' analytic values.
- Likelihood: the P10 likelihood with both options ON for eciML1515, fresh-model-safe (P10's
  evaluation path), through a process pool of 16. Confirm the pool path returns the same number as
  a single-process fresh evaluation at P4's MAP to the 1e-4 P7 measured, and say so.
- Toy check: a 16-dimensional Gaussian with the P8 covariance, log-evidence known analytically.
  dynesty recovers log Z within its own reported error and the posterior mean and covariance
  within Monte Carlo error. Report. If it fails, STOP.
- Checkpointing: dynesty's own save/restore, every N iterations; prove a restart resumes.

TASK 2 - the run, with its stopping rule written first
- D NLDM. Settings: state nlive (start at 500 for 16 dimensions; justify), the bound and sample
  method (default 'multi' bounds; 'rwalk' or 'rslice' - rslice is the natural choice on a
  piecewise surface; state which and why), dlogz stopping at 0.1, and the wall-clock cap (4 h).
- Write BEFORE running: CONVERGED if dynesty reaches dlogz < 0.1 within the cap and the posterior
  n_eff (dynesty reports it) is >= 600; STALLED if the cap is hit first; report both numbers
  either way. Also record the acceptance/efficiency dynesty reports per iteration.
- Run. Report: iterations, likelihood evaluations, wall-clock, evaluations per second across the
  pool, final dlogz, log Z with error, n_eff.
- Sanity: run a SECOND, shorter nested run with a different seed and nlive = 250. The two log Z
  estimates must agree within their combined error and the posterior medians within Monte Carlo
  error. That is the reproducibility check MCMC could never pass in this family; report it.

TASK 3 - what the posterior is, and what it says about the old one
- Posterior medians and 5/95 intervals for all sixteen parameters, weighted correctly (dynesty's
  importance weights - state how you resampled).
- Beside them: P4's under-converged medians and the (invalid) intervals P4 would have quoted. Which
  medians moved outside the old intervals? Which intervals are wider, which narrower?
- Posterior/prior width ratio per parameter. Then P9's caveat: one line scan per parameter through
  the NEW posterior median, and classify each parameter GRADIENT-DETERMINED (curved line),
  WALL-BOUNDED (plateau with steps), or FLAT (no change within one posterior sd). Report the
  three lists. This is the first time the identifiability of this model can be stated properly.
- The respiration scale's posterior: what it says the model's respiration precision is, in
  log-O2 units, against the floor.
- R2 for growth and respiration at the posterior median, against P4's at its median and Parsa's
  at his - one table.
- sigma on NLDM against P4's observation that it lands near the literature value on M9 (~0.48)
  and rails on rich media (~0.7): where does it sit now?

TASK 4 - cost the rest, do not run it
- From the measured evaluations and wall-clock: the cost of D LB and D M9 at the same settings;
  of E NLDM, E LB, E M9 under pfba; F NLDM and F M9; and F LB stated as HELD (P10: no tie-break at
  1e-9). Report as a table with hours. Do not run them.

TASK 5 - record
- reports/P11_nested/report.md: the floor move; the two-rule table; the dynesty wiring and its
  proofs; the run and the reproducibility check; the posterior; the identifiability
  classification; the costs.
- docs/OPEN_ITEMS.md: 1.12 closed with the verdict if CONVERGED (or restated if STALLED); 1.15
  closed - the route taken and the two decisions above; new PI item: run the remaining fits at
  the costed hours, or not. New section-4 hazard: "a smoothness rule must be absolute in
  log-likelihood units; a relative rule flags kinks once cliffs are gone."
- reports/synthesis/evidence.csv: rows for the floor, the sampler, the verdict, the
  identifiability classification. README correction note: section 7 now needs to say what the
  convergence finding actually was - a cliffed likelihood, not a sampling budget - and what
  resolved it. No re-render.
- Stamps.

VERIFY (report all)
1. TASK 0: #25 merged; gates; the floor old/new with its source; the absolute rule quoted from
   before the scan; the two-rule table on twelve lines; SAMPLEABLE or the line that is not.
2. TASK 1: dynesty version; the prior transform proven on 10,000 draws; pool == single-process at
   the MAP to 1e-4; the toy log Z and moments; checkpoint resume proven.
3. TASK 2: settings and the stopping rule quoted from before the run; iterations, evaluations,
   wall-clock, dlogz, log Z +/- error, n_eff; the verdict; the second-seed agreement.
4. TASK 3: the sixteen-parameter table old vs new; width ratios; the GRADIENT / WALL / FLAT lists;
   the respiration scale; the R2 table; sigma.
5. TASK 4: the cost table.
6. TASK 5: OPEN_ITEMS; the hazard; evidence rows; README note; stamps.
7. `git diff main --stat`: one floor value in strains/eciML1515 config, the dynesty runner in src
   or reports/P11_nested (state which and why), lock file, reports/P11_nested/, OPEN_ITEMS,
   evidence.csv, synthesis README, stamps, one run output. Nothing else. No prior changed. No
   growth-term change.

CONSTRAINTS
- Two decisions are executed, not revisited: floor at the largest jump; growth term untouched.
- The absolute rule and the stopping rule are written before their data are seen.
- No emcee. No zeus. One sampler, whose class matches the surface, with a second-seed
  reproducibility check.
- STALLED is reported as STALLED, with the numbers. Not extended past the cap, not quoted.
- F LB stays HELD. No other fit is run.
- Autonomous; commit in parts: "P11: floor and rule", "P11: dynesty wiring", "P11: run",
  "P11: posterior", "P11: record".
```
