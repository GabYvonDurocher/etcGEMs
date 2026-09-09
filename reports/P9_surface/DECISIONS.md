# P9 — decisions

Standing rules carry over. Branch `p9/surface` from `main` after the P8 merge; no push to `main`;
end in a PR that is not merged. Interpreter `../etcGEMs-venv`. No sampling, no fit, no change to
the model, the priors, the solver defaults or the fitting code. Exit codes checked explicitly.

---

## D0 — TASK 0: merged clean; the gates ARE re-run, because src/ changed inside P8 after its gate run

PR #23 merged server-side clean → `8830f2a`; nothing running; `p9/surface` branched; interpreter
`../etcGEMs-venv` (etcgem resolves to this checkout). The prompt says not to re-run the gates
unless `src/` changed since P8. It did — inside P8: commit `94bf3ab` (the zeus wiring in
`calibration_multi.py`) landed after P8's TASK 0 gate run. The gates do not import that module,
but "should not have" is a claim and the battery is eight minutes, so it runs in the background
while TASK 1 is set up. Result recorded in the report.

## D1 — how "a fresh model per evaluation" is met, and the smooth/rough rule, both before any scan

**The scan.** Configuration D NLDM, P6's definition (`gasflux_configD`, recipe NLDM medium with
the clearance multiplier sampled, c_max 120, k_cat 300). The point is **P4's MAP** (the
maximum-log-probability sample of `calibration_configD_NLDM_recipe_cmax120/chain.npy`) — a
single sample where the surface is examined; P4 scored this fit at the posterior median (P3's
convention for D) and the MAP is used here because a line scan needs one point, not a summary.
Scale: the posterior standard deviation of each direction in sampled space over P7's 128-walker
chain, steps 250–1500 (P8's standardisation). Twenty-two lines — the sixteen axes, P8's top
three principal components of that chain, three random unit directions (seed 11) — 41 points
each at steps of 0.05 sd over ±1 sd; the **log-likelihood only** (`gasflux_log_likelihood`,
prior excluded).

**"Fresh model per evaluation."** D3a's rebuild arm built a new provider for every evaluation.
A build costs ~40–60 s (SBML parse and GECKO reconciliation); 902 builds would be ~12 h for a
30-minute task. What the rebuild achieves is that no solver state carries between points, and
that is obtained by **one build per line** (22 builds) with the **Gurobi basis discarded before
every evaluation** (`model.solver.problem.reset()`), which P6 D3a showed restores the fresh-model
value exactly where state mattered (E LB). Recorded rather than assumed: on the first line, five
of the 41 points are ALSO evaluated on a genuinely fresh build each, and the two are compared; if
they differ by more than the 1e-4 P7 measured, the scan is re-run with true rebuilds on the
lines where it matters and the cost is paid. Single process throughout, no pool.

**The rule, verbatim from the prompt and committed before any line is summarised:** per line,
the number of sign changes in the first difference of the 41 log-likelihood values, the largest
single-step jump, and that jump as a fraction of the line's range. Across the 22 lines,
**SMOOTH** if the median sign-change count is ≤ 2 AND no single step exceeds 5 % of its line's
range; **ROUGH** if the median count is ≥ 5 OR any step exceeds 20 %; otherwise **MIXED**.
Ties in the jump fraction are resolved by the jump in absolute log-likelihood units, also
reported. TASK 2 runs if the reading is ROUGH or MIXED.

## D2 — D1's shortcut failed its own check and was abandoned; the scan builds a fresh model for every evaluation

**Where:** first line of TASK 1.

D1 assumed a build cost of 40–60 s and proposed one build per line with a Gurobi basis reset
before each evaluation, with a spot check against true rebuilds. The first line answered both
assumptions: a build of the D NLDM provider takes **3.7 s**, and the reset-per-evaluation values
differ from fresh-build values by up to **9.2 × 10⁻²** in log-likelihood on five points of the
`dTopt` axis (`task1_spotcheck_reset_arm.json`) — nine hundred times the 1e-4 D1 allowed. So the
reset does not reproduce a fresh model on this configuration (it did on E LB in P6 D3a), which
is itself evidence about the surface: a reused model with a discarded basis still lands
elsewhere than a fresh one, by a tenth of a log-likelihood unit. The scan was stopped after two
lines and **re-run with a genuinely fresh model per evaluation**, 902 builds at ~4 s plus ~0.5 s
per evaluation, ≈ 70 min, single process — exactly the prompt's and D3a's pattern. The rule in
D1 is untouched. The two lines scanned under the shortcut (`dTopt`, `topt_scale`: 3 sign changes
each, jumps of 16.5 % and 40.5 % of range) are discarded from the summary and kept in the log.
