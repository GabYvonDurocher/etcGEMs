# Claude Code prompt — P7: is the non-mixing a walker-count artefact? One bounded test before any modelling decision (autonomous, ~3–4 hours)

Run from the project root (`.../MICROADAPT/etcGEMs`). **Nothing is running.** P6 was halted under
addendum 6 and its diagnosis is on PR #18; Y1 lives in `../etcGEMs-synthesis` and is not touched.

**Why.** P6's D6 found that τ grows in exact proportion to chain length on the configuration-D fits —
25.2 ± 0.2 per 250 steps over five checkpoints, chain/τ pinned at 9.7, n_eff plateaued at ~308 —
for every one of the sixteen parameters, with no single carrier, a unimodal stationary ensemble and a
flat log-posterior. Brute force has no ceiling. D6 lists four options and three of them change what
the fit *is*: fixing parameters, narrowing priors, or a new sampler.

**Before any of those, one thing has not been tried that changes nothing about the model.** The fits
use **40 walkers in 16 dimensions**. The affine-invariant stretch move builds every proposal from the
spread of the complementary half-ensemble — twenty walkers — and in this many dimensions that
ensemble is thin. Slow mixing across all parameters together, with no carrier, is what that looks
like. It is also D6's own option (iii). More walkers sit inside P6's existing allowance (chain length
and sampler configuration) and touch neither model nor priors.

**What this test does and does not establish.** The sampler is known to degrade in ~16 dimensions
even with generous walker counts, so more walkers may help partially rather than fix it. This test is
not "the fix"; it is the *cheapest* discriminating experiment, and its result decides whether D6's
modelling options are needed at all. Either outcome is the deliverable.

**Two traps, stated in advance so the run cannot fall into them.**
  1. **n_eff is not the test.** n_eff = walkers × steps / τ, so 128 walkers triples n_eff even if τ
     is unchanged. A run that declares success because n_eff crossed 600 has measured nothing. The
     test is whether τ **stops growing with chain length**. Report n_eff, but do not let it decide.
  2. **A 500-step benchmark cannot see this.** P6's TASK 0b compared samplers over 500 steps using
     chain/τ, and under τ ∝ N every sampler scores ~9–10 by construction. That benchmark was
     uninformative, not negative. This test needs enough length for the τ(N) curve to show
     curvature or not — a minimum of 1500 steps, checkpointed every 250.

NOTE TO USER: launch in an auto-approving mode. One emcee run on one fit, roughly 2.5–3.5 hours at
128 walkers (per-step cost scales with walker count: 1.86 s/step at 40 → ~6 s/step at 128). It
merges PR #18 first, so the primary tree changes branch; that is intended, since nothing is running.

REFERENCE, read first: `reports/P6_convergence/DECISIONS.md` D5, D6 and D3a; `reports/P6_convergence/
run_fits.log` (the five logged checkpoints of the halted chain are the 40-walker control); `reports/
P4_refit/` for the fit definitions.

---

```
Work AUTONOMOUSLY; commit in parts, prefixed "P7: "; maintain reports/P7_walkers/DECISIONS.md FROM
THE FIRST JUDGEMENT CALL. Standing rules carry over. Check exit codes explicitly, never
`cmd && check`. Branch `p7/walkers` from main AFTER TASK 0; do not push to main; end in a PR that is
NOT merged.

TASK 0 - merge P6's diagnosis and start from main
- Confirm nothing is running: no process with the primary tree as cwd, run_fits.log not written in
  the last ten minutes. If something is running, STOP.
- Merge PR #18 server-side, matching the style of #14-#17. Confirm MERGED from the API and report
  the commit on origin/main. Then, in the primary tree, `git switch main` and `git pull`, and
  confirm the tree is clean. Branch `p7/walkers`.
- If the merge is blocked, STOP and report why.

TASK 1 - make the driver checkpoint, and prove it changes nothing
D6 lost 1250 steps because the driver writes chain.npy only at run end. Fix that first.
- Save the chain (and the random state) every 250 steps, so a halt loses at most one block. emcee's
  HDF5 backend does this natively; use it if the driver can, otherwise write the block yourself.
- Prove it is a no-op for the sampling: run the same short chain (say 100 steps, fixed seed) with
  and without checkpointing and confirm the chains are IDENTICAL. Report the check. If they differ,
  STOP - a checkpoint that alters the sample is a bug, not a feature.
- Prove resumability: halt a short run mid-way, resume from the checkpoint, and confirm the
  resumed chain matches an uninterrupted run of the same length and seed.

TASK 2 - state the decision rule BEFORE running
Write into DECISIONS.md, before TASK 3 starts, exactly how the result will be read:
- The null (non-mixing): tau_max grows ~0.10 x N, i.e. ~25 per 250-step block, as P6 measured.
- Mixing: the per-block increment in tau_max falls and tau_max approaches a plateau. State the
  threshold you will use - e.g. the increment over the last three blocks below 10 per block AND
  tau_max at N=1500 below 100 - and commit to it. Do not choose the threshold after seeing the data.
- Partial: increments fall but do not plateau within 1500 steps. Say now what you will report in
  that case (extend to 2500 if so, once, and report both).

TASK 3 - the test: D NLDM, 128 walkers, otherwise identical
- Configuration D NLDM, exactly as P6 defined it (D5): same model, same priors, same data, same
  c_max, stretch move, 16 processes. ONLY the walker count changes: 40 -> 128.
- Initialisation: resample the 128 starting positions from P4's final 40-walker ensemble with the
  same jitter P6 used for its own init (D2). State the rule and record the seed. The point is that
  the ensemble starts where the 40-walker chain ended, so the comparison is like-for-like with the
  five logged P6 checkpoints and not confounded by burn-in.
- 1500 steps minimum, tau_max and per-parameter tau at every 250, logged as P6 did. Apply TASK 2's
  rule. Extend once to 2500 only under the "partial" case.
- Report per checkpoint: N, tau_max, the parameter carrying it, the per-block increment, chain/tau,
  n_eff, acceptance, wall-clock. Put the P6 40-walker checkpoints beside them in the same table.
- Report the ensemble's per-parameter spread at the start and at the end. If 128 walkers collapse
  toward the 40-walker spread, or blow out, say so.
- If the run fails for a reason unrelated to walkers, STOP and report. Do not fix the model to make
  it run.

TASK 4 - what the answer licenses
State ONE of:
  (a) MIXING at 128 walkers. Then estimate, from the measured tau, the steps and hours to bring all
      three configuration-D fits to the P6 target (n_eff >= 600 AND chain/tau >= 25) at this walker
      count. Also estimate the cost for the six E/F fits should the tie-break decision reinstate
      them. Do NOT run them; that is P6's job, restarted under these settings.
  (b) NOT MIXING. tau still tracks N. Then D6's options (i)-(iv) are the real menu and this test has
      ruled out the cheap one. Say so plainly.
  (c) PARTIAL. Report the tau curve and what a further doubling of walkers would cost to test.
- Whichever it is: state whether the finding also applies to the six committed chains (same walker
  count) and therefore to the synthesis's section 7 claim.
- Update docs/OPEN_ITEMS.md 1.12 with the outcome and what it now needs.

VERIFY (report all)
1. TASK 0: PR #18 merged, the commit on origin/main, primary tree on p7/walkers from a clean main.
2. TASK 1: checkpointing proven a no-op on the sample (identical chains) and proven resumable.
3. TASK 2: the decision rule, written before TASK 3 ran, quoted verbatim in the report.
4. TASK 3: the checkpoint table with the P6 40-walker rows beside it; ensemble spread start/end;
   wall-clock and s/step.
5. TASK 4: the verdict, the rule it was decided by, and what it licenses; OPEN_ITEMS updated.
6. `git diff main --stat`: driver checkpointing, reports/P7_walkers/, OPEN_ITEMS, one new fit output
   directory. Nothing else. No change to any strain, prior, or fit definition.

CONSTRAINTS
- Walker count is the only sampling change. Model, priors, data, c_max, move set, process count and
  fit definitions are P6's exactly.
- The decision rule is written before the run and is not revised after it.
- n_eff does not decide. tau's dependence on N decides.
- Checkpointing must be shown to leave the sample identical before it is used.
- Either verdict is the deliverable. A negative result here is what licenses D6's options.
- Do not run D LB, D M9 or any E/F fit. Do not implement a tie-break.
- Autonomous; commit in parts.
```
