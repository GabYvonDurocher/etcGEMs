# P10 — decisions

Standing rules carry over. Branch `p10/respiration-likelihood` from `main` after the P9 merge; no
push to `main`; end in a PR that is not merged. Interpreter `../etcGEMs-venv`. Both changes are
core options, default OFF; nothing else about the model, the other priors, the data or `c_max`
changes. Exit codes checked explicitly.

---

## D0 — TASK 0: what the respiration term is today, read from the code, and why `disc_resp` did not absorb the cliffs

PR #24 merged server-side clean → `4bdaf18`; `p10/respiration-likelihood`; baseline gates on
the venv recorded in the report.

**The term, from `gasflux_log_likelihood` (calibration_multi.py):**

* *Quantity.* Per temperature, the model's **O2 uptake** at the growth optimum, converted to a
  per-cell rate — `o2_uptake × gdw_per_cell × 32/60 × resp_scale` — against the measured
  `R_O2_mg_cell_min` averaged over replicates. Not RQ, not CO2.
* *Scale.* **Logarithmic**: `(log obs − log pred)²`. Already log.
* *Mask.* Only temperatures where the model is alive (growth ≥ 1e-4) and consuming O2 (> 0)
  are scored; dead temperatures contribute nothing to this term.
* *Variance, per temperature.* `var_T = rel_T² + disc_resp²`, where `rel_T` is the measured
  replicate sd divided by the mean (30 % where the sd is missing, `load_respirometry`) and
  `disc_resp` is one fitted scale shared by all temperatures, prior half-normal(0.5) on the
  natural value, bounds [1e-3, 3], sampled in log space. Both rel and disc_resp are relative,
  i.e. sds of log respiration. The term is `−½ Σ_T [(log obs − log pred)² / var_T + log 2π var_T]`.
* *At P4's MAP*: `disc_resp` = **0.220**, `resp_scale` = 3.63; the measured relative sds are
  **0.057 at 20 °C and 0.087 at 25 °C** (0.06–0.38 elsewhere), so `var` at the cold points is
  ≈ 0.05.

**How O2 is obtained:** one LP per temperature, growth as the objective (`slim_optimize`), O2
read off the returned vertex (`EX_o2_e_REV − EX_o2_e`), Gurobi with cobra's settings —
**Method 0, primal simplex**, FeasibilityTol/OptimalityTol 1e-7 (P9 read them back). No
tie-break of any kind.

**Why the existing discrepancy did not absorb the cliffs.** It is on the right scale (log) and
its prior is not too narrow — a half-normal(0.5) costs only 2 units at `disc_resp` = 1. The
arithmetic of P9's three decomposed jumps says what actually happens
(`reports/P9_surface/task2_attribution.csv`, recomputed here with the term's own formula):

| jump | T | log residual before → after | Δ log O2 | var at the MAP's disc_resp 0.22 | term step | step if disc_resp were 0.5 / 0.7 / 1.0 |
|---|---|---|---|---|---|---|
| dCp_scale +0.90→+0.95 sd | 25 °C | +2.05 → +3.47 | 1.42 | 0.056 | **−70.2** | −15.2 / −7.9 / −3.9 |
| random1 +0.95→+1.00 sd | 20 °C | +1.77 → +2.53 | 0.76 | 0.052 | **−31.6** | −6.4 / −3.3 / −1.6 |
| PC2 −1.00→−0.95 sd | 20 °C | +2.32 → +1.73 | 0.59 | 0.052 | **+23.1** | +4.7 / +2.4 / +1.2 |

Three things multiply. (1) At the cliffs the cold points already carry a **standing residual
of +1.8 to +2.3 in log** — at those θ the model respires 6–10× less than measured at 20–25 °C,
where the model is nearly dead (growth 0.01–0.13) and the measurement is not. (2) The
measurement's relative sd there is **0.06–0.09**, the smallest of any temperature, so the
term's variance is set almost entirely by `disc_resp`. (3) The LP's optimal O2 at those
temperatures moves by a **factor 1.8–4.1 (0.6–1.4 in log) across one 0.05 sd step** — a vertex
switch, unique at each end (P9). The step in a quadratic term is ½(2rΔ + Δ²)/var: with r ≈ 2,
Δ ≈ 1.4 and var ≈ 0.056 that is 70. `disc_resp` cannot rescue it: it is one scale shared by
twelve temperatures, ten of which the model fits within their own `rel`, and at the MAP itself
the cold residuals are small — the chain sets it to 0.22 where the MAP is, and it is the moves
*away* from the MAP that meet both a large residual and a vertex jump. A fitted scale describes
the residuals where the chain sits; it cannot know about the model's granularity where the
chain would go, and it is that granularity — how far O2 jumps between adjacent LP vertices —
that the term's variance must honour if a 0.05 sd move is not to cost 70 units.

**So the minimal change that follows from this reading is not a second discrepancy term and not
a new prior: it is a floor on the log-O2 sd, added in quadrature, set to the model's own vertex
granularity** — `var_T = rel_T² + disc_resp² + floor²` — with the floor derived from the
distribution of |Δ log O2| across the 0.05 sd steps at P9's cliffs (TASK 2), fixed, not fitted,
and default 0 so that nothing moves with it off. The prior on `disc_resp` stays as it is: the
reading says it was never the problem, and TASK 2 reports it before and after unchanged, with
this reason. The tie-break (TASK 1) is the other half: it makes E/F's O2 a function of θ at all,
and on D it does not remove vertex switches — a pFBA solution is piecewise too — which is why
the floor is needed as well.

## D2 — TASK 2: the cliffs have TWO mechanisms, not one, and the variance change follows from both

**Where:** after the baseline scan of P9's twelve ROUGH lines with per-temperature O2 recorded
(`lines_baseline.csv`, 492 evaluations, fresh model each, 33.8 min — P9's numbers reproduced
line for line).

**The 33 cliff steps** (|ΔlogL| > 5 across one 0.05 sd step) separate cleanly by what moves
across them (`task2_jumps.csv`):

| mechanism | steps | what happens | temperatures |
|---|---|---|---|
| **O2 vertex jump** (|Δ log O2| ≥ 0.1 at some alive temperature) | **17** | the LP's optimal O2 switches vertex: |Δ log O2| q25 0.37, median 0.47, q75 0.63, max 1.42 | **20 °C (14 of 17)**, 25 °C (3) |
| **support flip** (a temperature enters or leaves the hard mask `growth ≥ 1e-4 & O2 > 0`) | **13** | a whole temperature's term — its residual and its log-variance — appears or disappears; |Δ log O2| elsewhere < 0.1 | 15 °C, 47–50 °C (the edges where the model is nearly dead) |
| other | 3 | growth-term steps | — |

P9 decomposed the three largest and found the first mechanism; it did not see the second,
because its instrument recorded the log-likelihood only. Half of the cliffs are **the term's
own indicator function**: `keep = (g ≥ 1e-4) & (o2 > 0)` is a discontinuity by construction,
and at 15 and 50 °C the model's growth hovers at that threshold, so a 0.05 sd move switches an
entire temperature — whose residual is large, because a nearly-dead model respires almost
nothing — in or out, at ±16–18 units (f_maint at −0.85 sd, ngam_scale at −0.15 sd,
clearance_mult at +0.45/+0.70/+0.75 sd are all this).

**The two minimal changes, each an option, default OFF:**

1. **`log_o2_floor`** — the floor D0 identified, in quadrature: `var_T = rel_T² + disc_resp² +
   floor²`. Rule, fixed before the number was read: the floor is the model's granularity where
   the O2 cliffs live — **the largest |Δ log O2| across a 0.05 sd step among the O2-carried cliffs
   at the temperature carrying most of them**. That is 20 °C (14 of 17) and the value is
   **0.759 → 0.76**. (A variance that honours the model must cover what the model does, not its
   median; the median at 20 °C is 0.44, and the one larger jump, 1.42 at 25 °C on the dCp_scale
   line at +0.9 sd, is left to cost what it costs.) Arithmetic on P9's three decomposed jumps at
   the same θ, old → new (`task2_floor.json`): **−70.2 → −6.2; −31.6 → −2.6; +23.1 → +1.9**.
   Single digits. The prior on `disc_resp` is **unchanged** — half-normal(0.5) on [1e-3, 3] — for
   D0's reason: it was never the problem, and a fitted scale cannot know the model's
   granularity away from where the chain sits; the floor is not fitted.

2. **`alive_soft_growth`** — the term's support made continuous: a temperature's contribution
   (both the quadratic and the log-variance) is weighted by min(1, g_T / g_s) with g_s =
   **0.01 h⁻¹**, equal to 1 wherever the model grows faster than 0.01 (every temperature that
   matters for the fit; the peak is 1.6) and falling to 0 continuously as it dies, instead of
   the hard switch at 1e-4. The O2 > 0 requirement of the log stays. Not a new discrepancy term;
   a smooth version of a mask that was already there.

Both live in the strain's `gas_exchange.respiration` block, consumed by the likelihood only —
`etcgem gasflux` runs and the gate scripts keep `flux_tpc`'s defaults, so no committed
`gasflux_*` output changes and the seven-strain gate is byte-identical with them OFF (recorded
in the report). ON for eciML1515 only.

## D3 — TASK 5: the decision rule and the run's definition, written before TASK 3 has reported and before any sampler runs

**Where:** before TASK 3's verdict. Written now so that neither the smoothness table nor the
run can shape it.

**The run, if TASK 3 reads SMOOTH under (c):** D NLDM, both halves ON through the strain config
(`gas_exchange.respiration`: pfba tie-break at tolerance 1e-9, log-O2 floor 0.76, continuous
support at 0.01), everything else P4's and P6's — the data, `c_max` 120, the recipe medium with
the clearance sampled, every prior including `disc_resp`'s (unchanged, D2) — under the
**original sampler**: emcee's stretch move, 40 walkers, 16 processes, seed 1, P7's driver with
the HDF5 checkpoint every step, initialised from P4's final ensemble state (P6 D2). No warm
start. So a plateau, if one appears, is attributable to the surface and to nothing else. The
tie-break makes each evaluation ~4.5× dearer (2.0 s against 0.45 s single-process; ~8–9 s per
step at 16 processes against 1.86), so 1500 steps is ~3.5 h.

**Decision rule** (P7's form, verbatim in substance): τ_max at every 250-step checkpoint with
P6's estimator. **MIXING** if the mean increment over steps 750→1500 is below 10 per block AND
τ_max(1500) < 100. **PARTIAL** if the mean over the last three is below 20 and each of the last
three is below the first block's; then extend once, by resume, to 2500 and apply the same two
conditions to 1750→2500 and τ_max(2500) < 100. Anything else **NOT MIXING**. If MIXING, run on
to the P6 target (n_eff ≥ 600 AND chain/τ ≥ 25) and report the posterior against P4's medians,
the width ratios, and one line scan per parameter at the new MAP classed gradient-determined or
wall-bounded. If NOT MIXING, STOP and say that the surface was smooth by P9's instrument and the
chain still did not mix. The comparison rows are P6's 40-walker, P7's 128-walker and P8's zeus
checkpoints — four samplers and configurations on the old surface, one on the new.

**If TASK 3 does not read SMOOTH under (c), no sampler runs.** The remaining rough lines are
decomposed as P9 did and the surrogate route (1.15 c) is reported as the next decision.

## D1 — TASK 1: the tie-break works for five of the six fits and STOPS on F LB; two things it needed that the prompt's sketch did not have

**Where:** TASK 1, the D3a instrument (`task1_d3a.csv`).

**What was built.** `flux_tpc(..., tiebreak="none" | "pfba" | "min_o2" | "max_o2", growth_tol,
tiebreak_tol)`: after the growth solve, growth is held at its optimum (relative slack
`growth_tol` = 1e-6) and a second objective is solved — pfba minimises the sum of every
reaction's forward and reverse variable; min/max_o2 take the ends of the face — inside a cobra
context, and the exchange fluxes are read off that vertex. The likelihood reads the option from
the strain's `gas_exchange.respiration` block (`ctx["respiration"]`); every other caller keeps
the default `none`, so `etcgem gasflux` outputs and the P1/P3 gate scripts are unchanged and
the seven-strain gate with the option OFF is **79/79 and byte-identical** (only the two stale
FBA dumps OPEN_ITEMS §4 already records).

**Two things it needed.** (1) cobra's own `add_pfba` re-optimises growth and pins it at exactly
the re-solved optimum with no tolerance; on the LB models that pin is numerically fragile and
whether it solves depends on the basis — the first D3a run under it read **6.1 / 8.2 on E LB and
0.0001 / 43.7 on F LB**, worse than no tie-break. The parsimonious objective is therefore built
directly (`set_linear_coefficients`, as cobra does internally, after a first attempt as a
symbolic sum proved quadratic in 24 000 variables) over the growth constraint with the stated
tolerance. (2) At Gurobi's default optimality/feasibility tolerance of 1e-7 the parsimonious
optimum on the LB models is nearly **flat in the O2 direction**: with growth *and* total flux
fixed at their optima the O2 is a point (FVA width 0.000, `task1_why_lb.csv`), yet successive
solves inside the likelihood returned O2 of 8.9, 10.0 and 12.8 at 30 °C — vertices within
tolerance of the same objective value, two- to four-fold apart in O2, chosen by basis history.
At **1e-9** for every solve in the call (`tiebreak_tol`; tightening the tie-break solve alone
was not enough, because the growth optimum it pins was then itself history-dependent at the
tolerance level) the E-configuration cells reproduce exactly (`task1_tol.csv`). The tolerance is
scoped to calls with a tie-break on and restored on exit; nothing else in the repository sees it.

**The D3a table under pfba (1e-9), same θ, same θ′, six fits:**

| fit | none: reuse θ,θ / θ,θ′,θ | **pfba: reuse θ,θ / θ,θ′,θ** | pfba: rebuild twice / rebuild+history | s per evaluation none → pfba |
|---|---|---|---|---|
| D NLDM | 0.0000 / 0.0000 | **0.0000 / 0.0000** | 0.0000 / 0.0000 | 0.43 → 1.87 |
| D LB | 0.0000 / 0.0000 | **0.0000 / 0.0000** | 0.0000 / 0.0000 | 0.26 → 1.81 |
| E NLDM | 0.5153 / 0.5153 | **0.0000 / 0.0000** | 0.0000 / 0.0000 | 0.67 → 2.22 |
| E LB | 2.4978 / 2.4992 | **0.0000 / 0.0000** | 0.0000 / 0.0000 | 0.39 → 2.34 |
| F NLDM | 0.0000 / 0.0000 | **0.0000 / 0.0000** | 0.0000 / 0.0000 | 0.50 → 2.24 |
| **F LB** | 2.3530 / 2.3530 | **0.0525 / 0.5055** | 0.0000 / 0.0525 | 0.48 → 2.33 |

**Verdict.** The tie-break is a tie-break for D NLDM, D LB, E NLDM, E LB and F NLDM — every cell
0.0000. **It is not one for F LB**, where a reused model still returns a value 0.05–0.5 away
(down from 2.35, but not zero): on that model even the parsimonious optimum at 1e-9 leaves a
residual freedom in O2. Per the prompt, **TASK 1 STOPS on the F LB cell**, and F LB stays held
(3.21 restated rather than closed). The option is switched ON for eciML1515 with that scope
written into the strain file; TASKS 2–5 concern D NLDM, where the tie-break is exact.

**Where pfba lands on the E LB face at Parsa's θ** (37/40/45/50 °C): none 38.12 / 46.66 / 40.71
/ 28.49; **pfba 38.07 / 46.60 / 40.71 / 28.49**; min_o2 38.07 / 46.60 / 40.70 / 28.48; max_o2
38.24 / 46.66 / 40.74 / 28.49. At *his* θ the face is 0.17 wide at most and pfba sits at its
low end; the [0, 190] face P6 D3a measured is at P4's MAP θ, not his. **Cost:** 0.45 → 2.0 s
per likelihood evaluation single-process, ×4.5, not the ×2 the prompt estimated — the
parsimonious LP over 24 000 split variables is the expensive half.
