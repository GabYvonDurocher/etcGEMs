# Claude Code prompt — P6: run the fits to convergence, so this family of results can be quoted (autonomous, ~40 hours)

Run from the project root (`.../MICROADAPT/etcGEMs`). **Run P5 first** — this must not start on an
unmerged tree, and it should use whatever `c_max` P5 settles for LB.

**Why.** P4 measured the autocorrelation time on every fit in this family and found the same thing
everywhere: **chain/τ ≈ 6–12 against a ≥40 criterion**. That covers all nine of P4's refits (τ
146–245 against 1500–2000 steps) AND all six of Parsa's committed chains (chain/τ 8.2–9.4,
n_eff 148–170). It is a sampling-budget property of this likelihood, not a failure of anyone's
diligence — the step counts look conventional and simply are not enough for a posterior with this
autocorrelation.

Until it is fixed, **no R² from either family is a converged posterior**, including the ten P3 gated.
The naive fix is roughly 8,000 steps and about 40 hours for all nine. **TASK 0b benchmarks three
cheap changes that may cut that substantially** — do it before spending the night.

**What it is not.** It is not a refit under new settings and not an opportunity to change the model.
The model configuration is whatever P5 leaves canonical. Only three things may change: chain length,
the SAMPLER configuration TASK 0b selects (move set and process count — which must be shown to leave
the posterior unchanged), and LB's `c_max` from P5.

NOTE TO USER: launch in an auto-approving mode and leave it overnight and through the following day.
It is emcee-bound. Do not switch branches, run other heavy work in this repository, or start another
session against `strains/eciML1515/` while it runs. It commits after every completed fit, so an
interruption costs one fit, not the run.

REFERENCE, read first: `reports/P4_refit/` (the convergence measurement, the sampler settings, the
scoped list of nine), `reports/P5_lb_cmax/` (the LB `c_max` decision), and `docs/OPEN_ITEMS.md` 1.12.

---

```
Work AUTONOMOUSLY; commit AFTER EVERY COMPLETED FIT, prefixed "P6: ";
maintain reports/P6_convergence/DECISIONS.md FROM THE FIRST JUDGEMENT CALL. Print a final summary.
Standing rules carry over. Check exit codes explicitly, never `cmd && check`. Branch `p6/convergence`;
do not push to `main`; end in a PR that is NOT merged.

TASK 0 - pre-flight, and do not skip it
A 40-hour run that starts misconfigured is 40 hours wasted.
- Confirm P5 is merged and the tree is clean. If not, STOP.
- Take the nine scoped fits from P4 — the six behind the ten gated R² values plus M9 for each
  configuration. Use P4's settings unchanged EXCEPT chain length, the sampler configuration TASK 0b
  selects, and LB's `c_max`, which takes whatever P5 settled. State all three, read back from each
  run's resolved config rather than assumed.
- **If P5 did NOT settle a canonical LB `c_max`**, do not run the three LB fits at 120 — that is the
  value P4 showed collapses the fit (growth R² 0.83-0.90 -> 0.16-0.20), and converging it would spend
  hours reaching a confident wrong answer. Use Parsa's own lowest LB value (257), label those three
  fits as provisional on an unsettled cap, and say so. Or skip LB entirely and report it. State which.
- P4 found the warm-start optimiser fails in this environment and falls back to emergent-point init;
  the defect is fixed but untested at scale. **Test it now, on one short run**, and report whether
  warm start works. If it does, burn-in shortens and the estimate below improves; if it does not,
  proceed without it and say so.
- Re-measure τ on P4's existing chains with the same estimator, and from that compute the steps
  needed for chain/τ ≥ 40 per fit. Report the per-fit target and the total wall-clock estimate
  BEFORE starting. If the total materially exceeds ~40 h, say so and proceed in the order below so a
  partial run is still useful.

TASK 0b - BENCHMARK BEFORE SPENDING THE NIGHT
Half an hour here can halve or better the whole run. On ONE fit (ConfigD NLDM), compare three
changes, reporting tau and wall-clock per 500 steps for each:
  (a) the current settings, as a baseline;
  (b) **emcee `DEMove` + `DESnookerMove`** in place of the default stretch move. The default
      struggles with correlated posteriors, and this one IS correlated — the E. coli work found
      sigma and kcat_scale on an anti-correlated ridge. This is emcee's own recommendation for such
      problems and commonly cuts tau by 2-5x. Required steps scale directly with tau, so this is the
      largest available lever;
  (c) **processes matched to the machine and to the walker split.** emcee splits 36 walkers into two
      halves of 18; 18 on 10 processes is two rounds with the second only 80% full. Try 9 and 18.
      Report the machine's physical core count (`sysctl -n hw.perflevel0.physicalcpu` on macOS) and
      say whether cores were idle at 10.
- Then adopt the fastest configuration THAT LEAVES THE POSTERIOR UNCHANGED. Verify that: compare
  posterior medians and interval widths from the short runs across configurations, and report them.
  A move set that samples the same distribution faster is a free win; one that samples a different
  distribution is a bug.
- Record the chosen configuration and the measured speedup in DECISIONS.md before starting TASK 1.
- If none of the three helps, say so and proceed with the original settings. A benchmark that finds
  nothing is still worth the half hour.

TASK 0c - state the convergence target as TWO numbers, and report both
`chain/tau >= 40` comes from emcee's guidance for estimating tau RELIABLY, not from needing that
many samples. What the deliverable needs is effective sample size: n_eff = walkers x steps / tau.
At 36 walkers, chain/tau = 20 already gives n_eff ~ 720, which is ample for posterior medians and
90% credible intervals. P4 measured n_eff 148-170 currently, so the real gap may be 2-3x rather
than 4-5x.
- Adopt as the target: **n_eff >= 600 AND chain/tau >= 25**, with BOTH reported per fit.
- Also report chain/tau against 40, so a reader can see how far each fit is from the stricter
  criterion for tau estimation itself.
- If a fit meets the adopted target earlier than the naive 8,000 steps, STOP THAT FIT THERE and
  record which criteria it satisfies. Do not run steps you do not need.
- Do NOT present the adopted target as equivalent to 40 tau. State plainly in the report that it is
  a weaker but sufficient criterion for the quantities being quoted, and why.

TASK 1 - run them, in this order
Order matters: a partial run must still leave the most important fits converged.
  1. ConfigD NLDM, ConfigD LB
  2. ConfigE NLDM, ConfigE LB
  3. ConfigF NLDM, ConfigF LB
  4. M9 for each configuration
- Use the configuration TASK 0b chose, and the target TASK 0c set.
- Extend rather than restart where the sampler supports it (resume from P4's final state); if it does
  not, run fresh and say so. Either is fine; silently doing one while implying the other is not.
  NOTE: if TASK 0b changed the move set, resuming a chain sampled under a different move is not
  clean — say which you did and why.
- After EACH fit: write outputs, compute τ and chain/τ, record whether the ≥40 criterion is met, and
  COMMIT. A crash at fit 7 must not lose fits 1–6.
- Report per fit: tau, chain steps, chain/tau, n_eff, acceptance fraction, and CONVERGED yes/no
  against BOTH the adopted target (n_eff >= 600 and chain/tau >= 25) and the stricter chain/tau >= 40.
- **If a fit still does not converge at the target length, report it as not converged.** Do not
  extend it silently, and do not quote it. State what length it would need.

TASK 2 - what converging changed
- For every fit, tabulate the converged posterior against P4's under-converged one: the R², the
  posterior medians and the credible interval widths for every shared parameter.
- Say plainly which conclusions move and which do not. The interesting cases are (i) any R² that
  changes materially, and (ii) any parameter whose interval was misleadingly narrow.
- Report K's posterior/prior width ratio again. P4 measured 0.57–0.64 under-converged, Parsa 0.89.
  If K is still unidentified at convergence, the medium ceiling is definitively a prior choice and
  the report must say so.
- Report whether σ still lands on the literature value on M9 (~0.48) while railing on rich media
  (~0.7). That contrast was one of P4's more interesting observations and it should be checked at
  convergence before it is relied on.

TASK 3 - close the loop on what was provisional
Several numbers in this project are currently quoted with a caveat that this run can remove.
- Update `reports/ecoli_gasflux/README.md` and `reports/P3_gate/`: replace the "not converged
  posteriors" caveat P5 added with the converged values, keeping the caveat's history as a dated note
  rather than deleting it.
- Update `docs/OPEN_ITEMS.md` 1.12 — close it if the criterion is met everywhere, or restate it with
  what remains.
- Re-run `scripts/stamp_reports.py`.
- **Do NOT re-open P3's gate against Parsa's numbers.** His chains remain under-converged; the gate
  is a port-fidelity check against his computation and stays as it is. Say so explicitly so nobody
  later reads the converged values as a failed gate.

VERIFY (report all)
1. TASK 0: P5 merged; settings and LB `c_max` read back from resolved configs; whether warm start
   works; what was done if P5 left LB unsettled; the per-fit target length and total estimate,
   stated before starting.
1b. TASK 0b: the benchmark table (tau and wall-clock per 500 steps for baseline, DE moves, and
   process counts); the machine's core count; the configuration adopted and its measured speedup;
   confirmation that posterior medians and interval widths are unchanged across configurations.
1c. TASK 0c: the adopted target stated, with the explicit note that it is weaker than 40 tau and
   sufficient for the quantities quoted.
2. TASK 1: the per-fit table — τ, steps, chain/τ, n_eff, acceptance, CONVERGED yes/no; anything that
   failed to converge, named, with the length it would need.
3. TASK 2: converged against under-converged for every fit; which conclusions moved; K's width ratio;
   σ on M9 against rich media.
4. TASK 3: the caveats replaced with dated history; OPEN_ITEMS 1.12; stamps; the explicit note that
   P3's gate is unaffected.
5. `git diff main --stat`; confirmation that nothing changed except chain length and LB's `c_max`.

CONSTRAINTS
- Three things may change and no others: chain length, the sampler configuration TASK 0b selects
  (move set and process count), and LB's `c_max` from P5. If anything else needs changing to make a
  fit run, STOP and report — that is a finding, not a fix.
- A faster sampler configuration is adopted ONLY if it leaves the posterior unchanged, demonstrated
  rather than assumed. Speed is worthless if the target distribution moved.
- Commit after every fit. This is the whole reason a 40-hour run is acceptable.
- A fit that does not converge at the target is reported as such, never quoted, never silently
  extended.
- P3's gate is a port check and is not re-opened here.
- Autonomous; commit per fit and per task.
```
