# P6 — decisions

Standing rules carry over. Branch `p6/convergence`; no push to `main` beyond the P5 merge the user
instructed; end in a PR that is not merged. Three things may change and no others: chain length,
the sampler configuration TASK 0b selects, and LB's `c_max` from P5. Exit codes checked explicitly.

---

## D0 — P5 was merged on the user's instruction, the P5 TASK 0 way, before anything else

**Where:** before TASK 0.

The P6 prompt says "confirm P5 is merged; if not, STOP" and "do not push to `main`", so the first
attempt at P6 stopped and reported. The user then instructed the merge explicitly. Done as P5's
TASK 0 was: `--no-ff` (`50cbffd`), the full battery with `$CANDIDAS_ROOT` unset and every exit
code printed — 79/79, 60/60, seven strains byte-identical, `outputs/` clean, stamps clean; the
only residual diffs are the two stale FBA config dumps OPEN_ITEMS §4 already records — then
push, PR #14 MERGED, branch deleted locally and on origin.

## D1 — three sampler-only options added to `run_gasflux_fit`; the model, likelihood and priors are untouched

**Where:** TASK 0, before any run.

TASK 0b needs a move set the driver could not take, TASK 1 wants to extend from P4's final
state, and the user's addendum 1 requires the warm start to be rejected when its mode does not
grow. None of these existed. Added (`src/etcgem/calibration_multi.py`):

* `moves=` — passed straight to `emcee.EnsembleSampler`; `None` keeps the default stretch move;
* `init_state=` / `init_label=` — an explicit starting ensemble, recorded in `summary.json`;
* `warm_start_min_growth_frac=0.10` — after the DE mode is found, its predicted peak growth is
  evaluated; below 10 % of the measured peak the warm start is **rejected** and the emergent-point
  ball used, with the rejection printed and recorded (`sampler.init`, `sampler.warm_start_rejected`).

Also recorded per run: the move set and the convergence target. Everything inside the
likelihood, the priors, the specs and the model build is byte-for-byte what P4 ran. Verified
by the fact that the default call signature is unchanged (all new arguments default to the old
behaviour) and by the P1/K1 gates, which do not touch this code.

## D2 — TASK 1 chains start from P4's final ensemble state, and τ is measured on the new chain alone

**Where:** TASK 0 / TASK 1 design.

The prompt allows "extend rather than restart where the sampler supports it". emcee supports
continuing from a saved ensemble state, and every one of the nine P4 fits has its final state
in `chain.npy[-1]` (40 walkers each). Starting there gives each fit ~1500–2000 steps of burn-in
for free and is strictly better than either the warm start (which P5 showed can seed a dead
mode) or the emergent-point ball. Two consequences, stated so neither is implied:

* if TASK 0b changes the move set, the new chain is sampled under a different move from P4's,
  so the two are **not concatenated**: τ, n_eff and the posterior are computed on the new chain
  only, and P4's chain is treated as burn-in. That is the clean reading of the prompt's note;
* if TASK 0b keeps the stretch move, the same rule is applied anyway, for one bookkeeping: a
  single convention for all nine rather than two.

So every TASK 1 run is "fresh chain, initialised from P4's final ensemble state", labelled so
in `summary.json`, and the warm start is not used in TASK 1 at all. It is still TESTED in TASK 0,
as the prompt and the addendum require, because P6 is not the last run that will call it.

## D3 — the six configuration-E and -F fits are NOT run: their likelihood is not a function of the parameters

**Where:** TASK 0, pre-flight (`preflight.py`, `jitter_diagnosis.py`), before any chain started.

The user's addendum 3 asked for the likelihood jitter to be measured, expecting ~0.02. Measured
at P4's MAP, six evaluations alternating with a second vector (which is what a walker sees —
every evaluation follows a different vector):

| fit | re-applies per call | spread in log-likelihood at the MAP | at the other point |
|---|---|---|---|
| D NLDM | clearance | 0.0001 | 0.0004 |
| D LB | nothing | 0.0000 | 0.0000 |
| D M9 | nothing | 0.0000 | 0.0000 |
| **E NLDM** | clearance + ETC area | **0.52** | **2.30** |
| **E LB** | ETC area | **6.21** | 0.46 |
| **E M9** | ETC area | 0.13 | 0.00 |
| **F NLDM** | clearance + ETC area | **4.31** | **7.49** |
| **F LB** | ETC area | **2.35** | 0.01 |
| **F M9** | ETC area | **1.93** | 0.00 |

For scale, P4's D_LB chain has median log-posterior −27 and maximum −20: the E/F jitter is the
width of the posterior itself. The diagnosis (`jitter_diagnosis.py`, E NLDM and F LB):

* the growth term is stable (peak-to-peak ≤ 1e-3 h⁻¹); **the O2 uptake is not** — at F LB it
  differs by up to 9.4 mmol gDW⁻¹ h⁻¹ on a mean of 19.8 between repeats at the same vector;
* with the constraint left untouched, repeated `flux_tpc` calls agree to 1e-4: the LP is
  deterministic *given a fixed problem*;
* the difference appears on the **first solve after the ETC constraint is removed and
  re-added** (the likelihood does that on every call) and disappears on subsequent solves:
  E NLDM −0.708 then −0.192 ×4; F LB −32.5 then −30.2 ×4. Updating the constraint's bound in
  place instead of remove-and-add makes E deterministic but leaves F LB at 0.34.

So the model's O2 uptake at optimal growth is **not unique** — `flux_tpc` reads it from whatever
vertex the solver lands on, and which vertex that is depends on the basis left by the previous
solve. Configuration D never restructures the problem between calls, so its vertex is
reproducible; E and F do, so their respiration likelihood carries a solver-history term. Every
E/F chain in this family — P4's six and Parsa's four — sampled that. The P3 gate is unaffected
as a *port* check (it evaluates one point once, after a fresh build, on both sides), but the
"respiration R²" those chains report was scored on a quantity the model does not determine.

**Decided:** run the three configuration-D fits (NLDM, LB, M9) to the TASK 0c target and **do
not run E or F**. Converging a chain against a target that is not a function of its parameters
would spend ~15 h producing posteriors whose respiration term is set by solver history, and τ
measured on such a chain would be an artefact of the same noise — the prompt's own rule
("a 40-hour run that starts misconfigured is 40 hours wasted") and its constraint ("if anything
else needs changing to make a fit run, STOP and report — that is a finding, not a fix") both
point the same way. The fix is one change in the likelihood or in `flux_tpc` — make the O2
uptake unique at the growth optimum (a lexicographic second objective, e.g. minimise total flux
or minimise O2 uptake at fixed growth), which is a change to what the fits *mean* and therefore
not P6's to make. After it, all six E/F fits need re-running from scratch, and P4's E/F
comparisons and the E/F rows of P3's gate need re-reading in that light. Recorded as a new open
item with that trigger.

Two consequences for this run: the benchmark and TASK 1 proceed on configuration D only, and
the ordered list the prompt gives (D, D, E, E, F, F, M9 ×3) becomes D NLDM, D LB, D M9.

## D4 — TASK 0b: the stretch move is kept and the process count goes 10 → 16

**Where:** TASK 0b, `bench.py` on configuration D NLDM, every run initialised from P4's final
ensemble state (40 walkers → emcee halves of 20, which is why the prompt's 36-walker arithmetic
does not apply: 10 processes was already two full rounds).

| run | steps | s/step | min per 500 | τ_max (chain/τ) | acceptance |
|---|---|---|---|---|---|
| stretch, 10 processes (P4's) | 500 | 2.08 | 17.3 | 51.2 (9.8) | 0.166 |
| DE 0.8 + DESnooker 0.2, 10 | 500 | 2.31 | 19.3 | 49.9 (10.0) | **0.051** |
| stretch, 12 | 150 | 2.16 | 18.0 | — | 0.178 |
| stretch, **16** | 150 | **1.86** | **15.5** | — | 0.176 |
| stretch, 20 | 150 | 1.86 | 15.5 | — | 0.187 |
| DE, 16 | 150 | 1.93 | 16.1 | — | 0.064 |

Machine: 12 performance + 4 efficiency cores, 16 physical, 16 logical. **Cores were idle at
10.** 16 processes is 11 % faster per step; 20 gains nothing more.

**The DE move set is not adopted.** Its τ on 500 steps is the same as the stretch move's (both
estimates are at chain/τ ≈ 10 and unreliable in absolute terms, but they are the same number),
and its acceptance is a third of the stretch move's — on this posterior it is not the 2–5× lever
the prompt hoped for. The 500-step posterior comparison (`bench_posteriors.csv`) shows medians
broadly consistent (clearance_mult 0.818 / 0.819, dTopt 2.0 / 2.2, sigma 0.68 / 0.70) and
several interval widths differing by up to 2× (dTm 4.1 / 7.6; sigma 0.27 / 0.41), which at ten
autocorrelation times is noise rather than evidence either way. Since DE is not faster, the
question of whether it samples the same posterior does not need settling here.

**Adopted: stretch move, n_proc 16.** The move is P4's and Parsa's, so the target distribution
is unchanged by construction, and a process count cannot change it (the same seed gives the
same proposals; only the wall clock moves). Measured speedup 11 %. Recorded in
`sampler_config.json`, which `run_fits.py` reads.

## D5 — the plan for TASK 1, and the time it should take, stated before it starts

Three fits (D3): D NLDM, D LB, D M9, in that order, each initialised from P4's final ensemble
state (D2), stretch move, 16 processes, checked every 250 steps against the adopted target
(n_eff ≥ 600 AND chain/τ ≥ 25, TASK 0c), with `n_steps_max` = 1.2 × 25 × τ_P4 so that a fit
either reaches the target or is reported not converged *at the target length*:

| fit | τ_P4 (re-measured) | 25 τ | n_steps_max | s/step at 16 proc (est.) | hours at 25 τ / at n_steps_max |
|---|---|---|---|---|---|
| D NLDM | 244.7 | 6117 | 7500 | 1.86 | 3.2 / 3.9 |
| D LB | 224.3 | 5609 | 6750 | ~1.25 | 1.9 / 2.3 |
| D M9 | 201.8 | 5044 | 6250 | ~2.15 | 3.0 / 3.7 |

**≈ 8 h if every fit stops at 25 τ, ≈ 10 h at the caps.** The six E/F fits, which would have
been ~15 h more, are held (D3). The user's mid-run instruction (received during TASK 0b)
confirms this plan and adds a diagnosis of the degeneracy (`degeneracy.py`, run alongside the
fits, single process) and a section on what would identify the respiration likelihood — a
decision to be reported, not a fix to be made.
