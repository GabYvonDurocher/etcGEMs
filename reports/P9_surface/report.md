# P9 — is the likelihood surface rough? Look at the surface, not the sampler

| task | status | one line |
|---|---|---|
| **0** | **DONE** | #23 merged clean → `8830f2a`; `p9/surface`; venv; gates re-run (src changed inside P8): 79/79, 60/60 |
| **1** — line scans | **DONE — ROUGH** | 22 lines, 902 fresh builds, 52 min; 12 of 22 lines with a 0.05 sd step > 20 % of range (median 39 %, max 99 %); parabolas between cliffs; two axes exactly flat |
| **2** — is it the solver? | **DONE — no** | cliffs unchanged under 1e-9 tolerances and dual simplex; each large jump is the respiration term at one cold temperature where O2 at the optimum switches vertex (unique at each end) |
| **3** — the chains | **DONE** | acceptance median 0.17; a third of walkers hold a constant log-posterior for ≥ 50 steps; accepted steps a quarter of proposed |
| **4** — verdict | **(c) ROUGH, STRUCTURAL** | intervals need a different respiration likelihood or a surrogate — a modelling decision (OPEN_ITEMS 1.15); D6 (i)/(ii) not worth their runs |

Detail: [DECISIONS.md](DECISIONS.md) (D0–D3); `task1_scan.py` → `task1_lines.csv`,
`task1_summary.csv`, `task1_meta.json`, `task1_spotcheck.json`, `task1_scan.png`;
`task2_solver.py` → `task2_lines.csv`, `task2_params.json`, `task2_basis.csv`;
`task3_chains.py` → `task3_acceptance.csv`, `task3_steps.csv`, `task3_summary.json`.

---

## TASK 0

PR #23 merged server-side clean → `8830f2a`; nothing running; `p9/surface`; interpreter
`../etcGEMs-venv`. **The gates were re-run**, because `src/` did change inside P8 after its own
gate run (the zeus wiring, `94bf3ab`): K1 **79/79**, P1 **60/60**, seven strains byte-identical,
the stamp script runs. No `src/` change in P9.

## TASK 1 — line scans through the MAP

**Setup** (D1, D2). Configuration D NLDM, P6's definition. The point is **P4's MAP** (the
maximum-log-probability sample of its chain; values in `task1_meta.json`). Scale: the posterior
sd of each parameter in sampled space over P7's 128-walker chain, steps 250–1500. Twenty-two
lines — the sixteen axes, P8's top three principal components, three random unit directions
(seed 11) — 41 points each, ±1 sd at 0.05 sd, the **log-likelihood only**. **A fresh model was
built for every one of the 902 evaluations** (3 s per build, 0.47 s per evaluation, single
process). The shortcut D1 had proposed — one model per line with the Gurobi basis discarded
before each evaluation — was tried on the first line and **differs from fresh builds by up to
0.12 in log-likelihood** (`task1_spotcheck.json`), so it was abandoned (D2); that difference is
itself a datum about the surface.

**The rule, written before any line was summarised** (D1, verbatim): SMOOTH if the median
sign-change count of the first difference is ≤ 2 AND no single 0.05 sd step exceeds 5 % of its
line's range; ROUGH if the median count is ≥ 5 OR any step exceeds 20 %; otherwise MIXED.

**Result** (`task1_summary.csv`, `task1_scan.png`; 902 evaluations, 52.4 min):

| line | sign changes | largest 0.05 sd step (logL units) | as % of the line's range | range | shape |
|---|---|---|---|---|---|
| dTopt | 3 | 13.0 | 16.4 | 79.6 | smooth peak, two cliffs on the far side |
| topt_scale | 3 | 20.0 | **40.6** | 49.2 | plateau, a cliff each side |
| dCp_scale | 7 | **71.8** | **52.6** | 136.5 | smooth to the left, a staircase of cliffs to the right |
| dTm | 1 | 3.2 | 10.4 | 30.4 | sharp peak, one small step |
| tm_scale | 7 | 3.1 | 19.0 | 16.0 | peak with several small steps |
| kcat_scale | 3 | 12.6 | **35.7** | 35.4 | smooth left, one cliff of 11 units at +0.2 sd |
| kappa_scale | 0 | 0.000 | — | **0.0** | **exactly flat** over ±1 sd |
| sigma | 1 | 1.2 | 10.0 | 12.5 | smooth parabola |
| f_metab | 0 | 0.000 | — | **0.0** | **exactly flat** over ±1 sd |
| f_maint | 7 | 18.2 | **98.3** | 18.5 | a plateau and one cliff at −0.85 sd; nothing else |
| ngam_scale | 1 | 18.4 | **85.9** | 21.4 | a plateau and one cliff at −0.15 sd |
| ngam_steepness | 1 | 0.04 | 6.9 | 0.6 | smooth, nearly flat |
| clearance_mult | 6 | 16.7 | **99.0** | 16.9 | plateau; two cliffs down and one back up between +0.45 and +0.75 sd |
| resp_scale | 1 | 1.2 | 7.9 | 14.9 | smooth parabola |
| disc_resp | 1 | 0.08 | 9.7 | 0.8 | smooth parabola |
| disc_growth | 1 | 0.13 | 9.0 | 1.4 | smooth parabola |
| PC1 | 1 | 18.5 | **38.2** | 48.3 | smooth right, two cliffs left |
| PC2 | **15** | 22.8 | **40.7** | 55.9 | a staircase of plateaus at different levels |
| PC3 | 3 | 11.8 | **46.3** | 25.5 | two cliffs bracketing the MAP |
| random1 | 9 | 35.7 | **43.1** | 83.0 | plateaus and cliffs both sides |
| random2 | 1 | 13.6 | **55.2** | 24.6 | one cliff each side |
| random3 | 8 | 14.8 | **82.6** | 17.9 | plateau, one cliff, smooth descent |

**Summary across the 22 lines:** sign changes **median 2, maximum 15**; largest single step
**median 12.8 units, maximum 71.8**; as a fraction of range **median 39 %, maximum 99 %**;
**12 of 22 lines have a single 0.05 sd step exceeding 20 % of their range and 20 of 22 exceed
5 %**; two lines are exactly flat. The MAP is the line maximum on only 3 of 22 lines, but the
excess elsewhere is ≤ 0.54 units — the MAP sits on a plateau, and what the lines show is not a
better point nearby but cliffs of 13–72 units within one posterior sd of it.

**By the rule: ROUGH** (any step > 20 % of range; here twelve lines). The sign-change count is
low (median 2) because the surface is not jagged: **between cliffs it is perfectly smooth**
(the parabolas of sigma, resp_scale, disc_resp, disc_growth; the smooth flanks of dTopt, dTm,
kcat_scale). The roughness is discontinuity, not noise — plateaus at different levels joined by
near-vertical drops of tens of log-likelihood units, at scales of one 0.05 sd step. Two
parameters, kappa_scale and f_metab, do not move the likelihood at all within ±1 sd of the MAP:
their posteriors are prior-shaped locally, and any walker move along them is accepted or rejected
on the other fourteen coordinates alone.

## TASK 2 — is the roughness the solver?

**Tolerances and method, on the three roughest lines** (`task2_lines.csv`, `task2_params.json`;
defaults read back from Gurobi: FeasibilityTol 1e-7, OptimalityTol 1e-7, BarConvTol 1e-8,
Method 0 — primal simplex, as cobra sets it):

| line | setting | sign changes | largest step (units, % of range) | max |Δ| vs defaults over the line |
|---|---|---|---|---|
| clearance_mult | defaults | 4 | 16.7 (99.0 %) | — |
| | tolerances 1e-9 / 1e-9 / 1e-12 | 4 | 16.7 (99.0 %) | 0.0008 |
| | dual simplex (Method 1) | 6 | 16.7 (98.8 %) | 0.083 |
| f_maint | defaults | 5 | 18.2 (98.2 %) | — |
| | tight | 3 | 18.2 (98.3 %) | 0.077 |
| | dual simplex | 3 | 18.2 (97.9 %) | 0.077 |
| ngam_scale | defaults | 3 | 18.4 (85.9 %) | — |
| | tight | 1 | 18.4 (85.9 %) | 0.060 |
| | dual simplex | 7 | 18.4 (85.9 %) | 0.142 |

**The cliffs do not move, shrink or shift** under either change; the rest of each line drifts by
≤ 0.14 — the same order as the 0.1 reset-versus-fresh difference in D2. Solver numerics sit at
the 0.1 level; the cliffs are a hundred times larger.

**What changes across the three largest jumps** (`task2_attribution.csv`, fresh model at each
end, the likelihood's own arithmetic split per temperature; `task2_fva_at_jump.csv`):

| jump | ΔlogL | temperature carrying it | growth from → to | O2 uptake from → to | O2 unique at each end? (FVA width) | growth term Δ | respiration term Δ |
|---|---|---|---|---|---|---|---|
| dCp_scale, +0.90 → +0.95 sd | −71.8 | **25 °C** | 0.127 → 0.114 | **1.50 → 0.36** | yes (0.012 / 0.012) | −0.35 | **−70.2** |
| random1, +0.95 → +1.00 sd | −35.7 | **20 °C** | 0.0115 → 0.0081 | **1.16 → 0.54** | yes (0.001 / 0.001) | −0.04 | **−34.2** |
| PC2, −1.00 → −0.95 sd | +22.8 | **20 °C** | 0.072 → 0.074 | **0.67 → 1.21** | yes (0.007 / 0.020) | +0.01 | **+22.6** |

Every other temperature contributes under a unit. About a thousand of twelve thousand LP
variables change basis status across any 0.05 sd step at every temperature (`task2_basis.csv`) —
the ordinary consequence of rescaling every k_cat — and the cliff is the one cold temperature
where the new vertex respires two to four times less, or more, at almost the same growth. The
O2 there is not degenerate (it is unique to 0.02 at both ends); it is **discontinuous in θ**.
Because the respiration term is a log-scale Gaussian against a per-cell rate with a small
variance, a factor of four in O2 at one temperature costs 20–70 units. **The roughness is the
model's piecewise-linear response to its parameters, magnified by how respiration is scored:
structural, not numerical.** Nothing was adopted.

## TASK 3 — what the existing chains say

Post-burn-in, P7's 128-walker chain (steps 250–1500) and the 40-walker P4+P6 history
(1500–2500); a walker counts as accepting at a step if its position changed
(`task3_summary.json`):

| | 128 w | 40 w |
|---|---|---|
| per-walker acceptance: min / q25 / median / q75 / max | 0.041 / 0.146 / **0.175** / 0.203 / 0.242 | 0.056 / 0.144 / **0.170** / 0.207 / 0.258 |
| walkers accepting < 5 % of proposals | 1 of 128 | 0 of 40 |
| walkers with a run of ≥ 50 steps at constant log-posterior | **40 of 128** (longest 160; median longest 41) | **10 of 40** (longest 98; median longest 36) |
| accepted step length, standardised, median | **0.44** | **0.42** |
| proposed step length (stretch move, reconstructed from the ensemble), median | 1.78 | 1.77 |
| accepted / proposed | **0.25** | 0.24 |

No walker is frozen outright, but a third of them sit still for fifty steps or more at a time,
and the moves that are accepted are a quarter the length of the moves proposed: the walkers
are confined to a scale well inside the ensemble's spread (one sd in every parameter is a
length of 4 here). That is what a rough surface leaves in a chain.

## TASK 4 — the verdict, and what it licenses

**(c) ROUGH, STRUCTURAL.** The log-likelihood is piecewise smooth with cliffs of 13–72 units
within one posterior sd of the MAP; the cliffs are unchanged by solver tolerances or method and
are each the respiration term at one cold temperature where the LP's optimal O2 uptake switches
vertex. **No sampler and no model reduction gives intervals from this likelihood as written**:
the posterior mass lies on plateaus separated by walls, an ensemble proposing at a quarter of a
sd hits a wall on most moves (TASK 3: accepted steps a quarter of proposed; a third of walkers
sitting still for fifty steps at a time), and fixing four parameters or narrowing two priors
leaves every wall standing. P6 D6's option (iv) stands; options (i) and (ii) are not worth
their runs. Intervals need a smoothed surrogate or a different respiration likelihood, and that
is a modelling decision — **OPEN_ITEMS 1.15**, three ways stated, none taken.

**Does it explain the burn-in drift?** Yes, in one paragraph (D3): the ~1500 steps D6 saw the
ensemble take to find the `disc_growth` scale is the ensemble draining off the cliffs into the
plateau that holds the MAP. The two discrepancy scales are the two directions in which the
surface is a smooth parabola (sign changes 1, steps under 10 % of range), so they are the
directions the walkers can move while every other coordinate is walled, and they shrink as
walkers arrive on the plateau and the residuals they must absorb fall. The drift is the
roughness seen from inside the chain; the isotropy P8 found is the walls being everywhere.

## Verification

| check | result |
|---|---|
| TASK 0 | #23 MERGED; main `8830f2a`; `p9/surface`; `../etcGEMs-venv`; gates 79/79, 60/60 (re-run because `94bf3ab` changed `src/` inside P8) |
| TASK 1: 22 lines, sign changes, largest jumps; summary; rule quoted from before; figure; wall | table above; median 2 / max 15; median 12.8 / max 71.8 units; median 39 % / max 99 %; D1 quoted; `task1_scan.png`; 52.4 min |
| TASK 2: tolerances/method before/after; jumps shrank?; basis at the three largest jumps | 1e-7/1e-7/1e-8/Method 0 → 1e-9/1e-9/1e-12 and Method 1; **no**; ~1000 of 12 000 variables re-base at every temperature, the cliff is the respiration term at one cold temperature with O2 unique at each end |
| TASK 3 | acceptance min/q25/median/q75/max 0.041/0.146/0.175/0.203/0.242 (128 w); 1 of 128 below 5 %; 40 of 128 with a ≥ 50-step constant run; accepted/proposed 0.25 |
| TASK 4: verdict; licence; OPEN_ITEMS; evidence; README; stamps | (c); 1.12 appended, **1.15** added under §1; **P6b**; README note extended; stamps clean |
| `git diff main --stat` | `reports/P9_surface/`, `docs/OPEN_ITEMS.md`, `reports/synthesis/evidence.csv`, `reports/synthesis/README.md`, `reports/report_status.yaml`, stamps. Nothing under `strains/` or `src/`. No sampler run. No default changed. |
