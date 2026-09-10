# Claude Code prompt — P8: name the ridge from the chain already on disk, then take the one branch it licenses (autonomous, ~4 hours worst case)

Run from the project root (`.../MICROADAPT/etcGEMs`), on the venv at `../etcGEMs-venv`. **Merge
PRs #21 (Y2) and #22 (P7) first** — server-side, matching #14–#20 — then `git switch main`,
`git pull`, branch `p8/ridge`. Nothing is running.

**Where this stands.** P6 D6: τ grows in proportion to chain length on every one of sixteen
parameters, carrier rotating, unimodal, log-posterior flat. P7: 128 walkers buys 10% and no plateau.
So it is not the walker count, and it is not any single slow parameter. Sixteen parameters all
slow *together*, with a known σ–kcat anti-correlated ridge (P2), is what an ensemble moving
collectively along a **curved, nearly flat ridge** looks like. The stretch move is affine-invariant:
linear correlation is free, curvature is not, and walkers do not fix curvature.

**Two branches remain that do not change the science, and one diagnostic that says which to take.**
PCA on the chain already on disk names the ridge. If the four prior-determined parameters
(`topt_scale`, `dCp_scale`, `sigma`, `clearance_mult`) load on it, fixing them removes it and a
12-dimensional refit is the branch. If the twelve data-determined parameters carry it, fixing the
four does nothing, and the branch is a sampler that handles curvature — `zeus`, an ensemble slice
sampler with emcee's interface and no gradients. Do the diagnostic, take ONE branch, report the
other as not taken and why.

**What is not on the menu here.** Narrowing the discrepancy priors (D6 ii) — it removes burn-in
drift, not mixing, and reads as tuning the prior. Nested sampling — heavier than needed. HMC — no
gradients through an LP. Do not take any of these.

NOTE TO USER: launch in an auto-approving mode. TASKs 0–1 are minutes. The branch run is one fit,
D NLDM, ~3 h either way. It merges two PRs first. It uses the new venv; the old `.venv` is still in
place and is not touched.

REFERENCE, read first: `reports/P6_convergence/DECISIONS.md` D5, D6; `reports/P7_walkers/` (the
checkpointing driver, the decision-rule pattern); `reports/P4_refit/` for the fit definitions;
`reports/P2_settle/` for the σ–kcat ridge.

---

```
Work AUTONOMOUSLY; commit in parts, prefixed "P8: "; maintain reports/P8_ridge/DECISIONS.md FROM
THE FIRST JUDGEMENT CALL. Standing rules carry over. Check exit codes explicitly, never
`cmd && check`. Branch `p8/ridge` from main after the two merges; do not push to main; end in a
PR that is NOT merged.

TASK 0 - merge and start clean
- Confirm nothing is running. Merge #21 then #22 server-side. If #22 conflicts with #21 on
  OPEN_ITEMS / stamps, resolve in a temporary worktree keeping both sides, regenerate stamps, and
  merge; report file by file. Confirm both MERGED; `git switch main`, `git pull`; branch.
- Confirm the interpreter is ../etcGEMs-venv and both gates pass on it (79/79, 60/60). Report.

TASK 1 - name the ridge, from the chain on disk, before running anything
Use the longest D NLDM chain available: P7's 128-walker 1500-step chain, and P6/P4's 40-walker
2500-step history as a second view. Post-burn-in only (D6 put burn-in at ~1500 steps on the
40-walker chain; state what you used for the 128-walker one and why).
- Standardise every parameter to zero mean, unit variance over the post-burn-in samples. PCA.
  Report the variance fraction of each principal component and the cumulative fraction.
- Compute tau ALONG each principal component (project the chain, run the same tau estimator).
  Report tau per component beside its variance fraction.
- The ridge is the component, or the two or three components, that carry both most of the
  variance AND the largest tau. Name it. Report its loadings on all sixteen parameters, signed.
- Then the decision, by a rule written BEFORE you look at the loadings:
    * if the four prior-determined parameters together carry >= 50 % of the squared loading of
      the ridge component(s): BRANCH A (fix the four).
    * if they carry < 50 %: BRANCH B (zeus on all sixteen).
  Write the rule into DECISIONS.md, then compute the number, then state the branch. If the ridge
  is not one clean direction - variance spread evenly, tau similar on all components - say so:
  that is BRANCH B, because nothing to fix is being named.
- Also report: does the ridge look curved? Project the chain onto its top two components and
  report whether the scatter is an ellipse or a banana (a simple test: fit a quadratic to
  PC2 against PC1 and report the curvature term against its standard error). Curvature is what
  the stretch move cannot follow and is the case for BRANCH B even if the four load on it.
- Commit the diagnostic with its figures before starting the branch.

TASK 2A - BRANCH A: fix the four, refit at twelve dimensions
- Fix at nominal: sigma at the literature value P4 found on M9 (~0.48 - read it from P4's
  output, do not assume), clearance_mult at its prior centre, topt_scale and dCp_scale at 1.
  Record the four values and their sources.
- D NLDM only. Everything else P6's exactly - model, data, priors on the remaining twelve, c_max,
  stretch move, 16 processes, 40 walkers (this branch is testing dimensionality, not walkers).
  Initialise from P4's final ensemble with the four fixed. Checkpoint every 250 with P7's driver.
- Decision rule, written before the run, in P7's form: mixing if the last-three mean tau increment
  < 10 per block and tau_max at 1500 < 100; partial if < 20; else not mixing. 1500 steps, extend
  once to 2500 under partial only.
- Report per checkpoint beside P6's 40-walker and P7's 128-walker rows.
- If it mixes: run to the P6 target (n_eff >= 600 AND chain/tau >= 25) and report the converged
  twelve-parameter posterior against P4's medians, with a plain statement that four parameters
  were fixed and what uncertainty that hides. Do NOT run D LB or D M9; state their cost.
- If it does not mix: STOP. Report. Do not fall through to BRANCH B in the same run - that is a
  second decision and it goes back to the user with the evidence.

TASK 2B - BRANCH B: zeus on all sixteen
- Install zeus-mcmc into ../etcGEMs-venv; add it to requirements.lock.txt. Report the version.
- Wire it into P7's driver behind the same checkpointing. Prove the wiring on a toy: a
  16-dimensional correlated Gaussian with a known covariance, 500 steps, posterior mean and
  covariance recovered to within Monte Carlo error. Report the check. If the toy fails, STOP.
- D NLDM, all sixteen parameters, P6's model/data/priors/c_max exactly, 16 processes. Walkers:
  zeus's default guidance (state it); initialise from P4's final ensemble. 1500 steps, same
  decision rule and extension as 2A. Report zeus's own diagnostics as well (it reports an
  integrated autocorrelation and an efficiency figure - quote both).
- Report per checkpoint beside the emcee rows. Report wall-clock per step - zeus takes several
  likelihood evaluations per walker per step, so the honest comparison is tau per WALL-HOUR, not
  per step. Give both.
- If it mixes: run to target, report the converged posterior against P4's medians and interval
  widths, and state which conclusions move.
- If it does not mix: STOP and report. That is D6 option (iv) confirmed as the state of this
  family, and the report should say so without softening it.

TASK 3 - record, and close the loop on what is now known
- reports/P8_ridge/report.md: the PCA (variance, tau per component, loadings, curvature); the
  branch taken and the rule that chose it; the checkpoint table; the verdict.
- docs/OPEN_ITEMS.md 1.12: restate with the outcome. If the family converged under either branch,
  say what it cost and what the other eight fits would cost; if not, 1.12 becomes a closed item
  with a stated conclusion, not an open one.
- reports/synthesis/evidence.csv: update P1-P3 status and add one row for the PCA finding and one
  for the branch verdict. No re-render.
- The synthesis's section 7 sentence about ~8000 steps is now wrong twice over. Add a dated
  correction note to reports/synthesis/README.md listing the sentences that need changing at the
  next render, with the evidence rows. Do not edit synthesis.qmd.
- docs/OPEN_ITEMS.md: add a new section "## 0. Sequencing — E. coli first (decided 2026-09-09)"
  above section 1, in the house style, saying this and no more:
    * The E. coli model (eciML1515) is the best-constrained: three media, gas exchange, a
      measured meltome. Methods are developed and proven there first, then ported through the
      core. The seven-strain gate (K1, 79/79) runs on every core change so the other strains
      cannot silently break meanwhile.
    * Order on E. coli: (1) the sampling problem - P8; (2) the E/F tie-break on the LP face
      (1.13, PI); (3) the -5.6 K Tm shift - whether a Li-style per-enzyme calibration against
      the meltome removes it (1.14 generalised to E. coli, where the data exist); (4) the CT_max
      disagreement with the yeast posterior (Y2) - definition first, then mechanism.
    * Candida: the K-series result (13.57 C required against 1.6 C measured, and why) stands
      and is what the manuscript uses. No further Candida modelling until the E. coli
      calibration recipe exists; then it ports against the measured TPCs.
    * Cross-taxon questions already answered (activation energies K6, seven-strain ceiling K9)
      stay on record and are not re-opened by this.
  Cross-reference docs/CANDIDA_DISCUSSION_2026-09-07.md section 9 with one line saying it is
  superseded on ordering by this section.
- Stamps.

VERIFY (report all)
1. TASK 0: #21 and #22 merged, conflicts resolved file by file, main commit, gates on the venv.
2. TASK 1: variance fractions; tau per component; the ridge named with signed loadings; the four's
   share of squared loading against the 50 % rule (written before computing); the curvature term
   with its SE; the branch chosen.
3. TASK 2: the checkpoint table with P6 and P7 rows beside it; the decision rule quoted verbatim
   from before the run; the verdict; wall-clock and (for 2B) tau per wall-hour.
4. TASK 3: OPEN_ITEMS 1.12 and the new section 0 (quoted); the evidence rows; the README
   correction note; stamps.
5. `git diff main --stat`: reports/P8_ridge/, driver changes (2B only), lock file (2B only),
   OPEN_ITEMS, evidence.csv, synthesis README, stamps, one fit output directory. Nothing under
   strains/ except that output. No prior changed except by fixing (2A), stated.

CONSTRAINTS
- One branch per run. The PCA decides it by a rule written before the loadings are seen.
- No prior narrowed. No discrepancy prior touched. The four are FIXED (2A) or left free (2B);
  nothing in between.
- The decision rule for mixing is written before the run and not revised.
- A branch that does not mix STOPS. The other branch is a new decision for the user.
- The old .venv is not deleted. Nothing under ../etcGEMs-work is touched.
- Either verdict is the deliverable.
- Autonomous; commit in parts.
```
