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

## D3 — the verdict: ROUGH, STRUCTURAL, by the rule in D1; what it licenses

**Where:** after TASKS 1–3.

**By D1's rule: ROUGH.** Twelve of twenty-two lines have a single 0.05 sd step exceeding 20 % of
the line's range (median 39 %, maximum 99 %); the median sign-change count is 2, so the surface
is not jagged — it is **piecewise smooth with cliffs**: exact parabolas between drops of 13–72
log-likelihood units, plateaus at different levels, and two axes (kappa_scale, f_metab) exactly
flat within ±1 sd of the MAP.

**Not numerical.** On the three roughest lines the cliffs are the same height and place under
Gurobi tolerances tightened a hundredfold (FeasibilityTol, OptimalityTol 1e-7 → 1e-9; BarConvTol
1e-8 → 1e-12) and under a fixed dual simplex (Method 0 → 1): 16.7 / 18.2 / 18.4 units in every
arm; the other points move by ≤ 0.14. The reset-versus-fresh difference D2 found (0.1) is the
same order as that drift — solver-history noise sits at the 0.1 level, three orders below the
cliffs.

**Structural, and attributable.** Each of the three largest jumps, recomputed on fresh models at
both ends with the likelihood's own arithmetic split per temperature and per term
(`task2_attribution.csv`): the growth term moves by < 1 unit at every temperature; **the
respiration term moves by −70.2 (dCp_scale, 25 °C), −34.2 (random1, 20 °C) and +22.6 (PC2,
20 °C) at a single cold temperature**, where the LP's O2 uptake changes **1.50 → 0.36, 1.16 →
0.54 and 0.67 → 1.21** mmol gDW⁻¹ h⁻¹ across the step while growth moves 3–30 %. And that O2 is
**unique at both ends** — FVA at growth held to its optimum gives widths of 0.001–0.02
(`task2_fva_at_jump.csv`) — so this is not the E/F degeneracy of P6 D3a; it is the LP's optimal
vertex switching to one where the cell respires two to four times less (or more) for a change
of 0.05 sd in θ. About a thousand of twelve thousand variables change basis status across any
such step at every temperature (`task2_basis.csv`), which is what an LP does when every k_cat
is rescaled; the cliff is the one temperature where the switch lands on a different O2. The
respiration likelihood is on a log scale against a per-cell rate with a small variance, so a
factor of four in O2 at one temperature costs tens of units. The cliffs are the model's
piecewise-linear response to its parameters — real kinks at basis changes — magnified by how the
respiration term is scored.

**Verdict (c): ROUGH, STRUCTURAL.** No sampler, no walker count and no reduction of dimension
gives credible intervals from this likelihood as written: the posterior mass sits on plateaus
separated by walls, and an ensemble proposing at 0.05–0.5 sd is rejected at every wall and
accepted only inside its plateau — which is exactly TASK 3's accepted-to-proposed ratio of 0.25
and the third of walkers holding a constant log-posterior for fifty steps at a time. P6 D6's
option (iv) stands, and options (i) and (ii) are not worth their runs. **Intervals need either a
smoothed surrogate or a different respiration likelihood, and that is a modelling decision**
(OPEN_ITEMS 1.15): a tie-break that makes the O2 at the optimum move continuously (pFBA or a
lexicographic objective, the same change 3.21 needs for E/F, ~2× per evaluation, the P3 gate to
re-run), a noise-aware respiration term that absorbs the vertex spread, or a surrogate for
sampling only. None taken here.

**The burn-in drift.** D6 saw the ensemble take ~1500 steps to find the scale of `disc_growth`.
On this surface that is not slow learning of a scale; it is the ensemble draining off the cliffs
into the plateau that contains the MAP. `disc_growth` and `disc_resp` are the two directions in
which the surface is a smooth parabola (sign changes 1, jumps < 10 %), so they are the two
directions the walkers can actually move in while every other coordinate is walled; the
discrepancy scales shrink as walkers arrive on the plateau and the residuals they must absorb
fall. The drift is the roughness seen from inside.
