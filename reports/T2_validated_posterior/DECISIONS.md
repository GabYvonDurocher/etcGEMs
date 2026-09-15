# T2 — implement the approved target revision, validate it against the signed protocol, earn the first posterior: decisions

_Branch `t2/validated-posterior` from `main` at `fe35aac` (the merge of T1's PR #40). Worktree
`../etcGEMs-t2`. RIGOUR.md, TARGET_REVISION_SPEC.md, T1's DECISION_PACKAGE.md and the signed
protocol govern; this prompt yields to them. Started 2026-09-13 20:40._

## D0 — first start; the PI's decisions recorded; everything registered before anything runs

**Resumption check (the prompt's first instruction).** No `reports/T2_validated_posterior/
status.json` exists in the primary tree, in `../etcGEMs-t1`, or anywhere else; no driver, no
`driver.pid`; no python job with either tree as cwd. **First start: TASK 0.**

**Merge.** PR #40's `baseRefName` read first: `main` (MERGEABLE, CLEAN). Merged server-side at
`fe35aac` 20:38 UTC. `main` fast-forwarded, worktree created on `t2/validated-posterior`.

**One deviation, stated up front.** The prompt says "run from the project root". The primary
tree's `.git/index.lock` is still a stale zero-byte file held open by `com.apple.Virtualization`
pid 62662 (uptime 2 d), and T1's rule against deleting lock files carries over; the primary tree
also sits on `t1/housekeeping` with uncommitted duplicates of #39. So, as T1 did, every write goes
through a worktree, `../etcGEMs-t2`, whose index is independent. **Resumption hazard, handled:**
a session started cold in the primary root would find no `status.json` and begin at TASK 0. An
untracked redirect file `reports/T2_validated_posterior/status.json` is therefore placed in the
primary tree with `stage: "REDIRECT"` and the worktree path, and `launch_status.md` says the same.
The driver runs from the worktree root; all its paths are relative to it.

### The PI's decisions on T1's package (2026-09-13), verbatim from the prompt, executed here

1. **f_metab (1.29): removal APPROVED.** Turn on `remove_inactive: ["f_metab"]` for eciML1515.
2. **Infeasibility (1.30): −∞ for structural infeasibility APPROVED**, with a separate finding
   (1.33) on why the model is infeasible over ~96 % of a defensible prior on NLDM.
3. **Curvature (1.31): retain as is.** No defect found; nothing to apply.
4. **Protocol (1.32): SIGNED, with one amendment** — check (d) becomes the PRIOR fraction rejected
   as infeasible, with its uncertainty; under −∞ the dead stratum is excluded, not occupied.

**What −∞ means (the prompt's definition, adopted):** at every measured temperature the
likelihood evaluates, the LP is solved; Gurobi `infeasible` → the parameter set has zero
likelihood, the limit of the existing log-scale term (`log 0`), not a penalty and not an ε.
Feasible-but-not-growing states are unchanged: the clamp scores their real maintenance
respiration. UNRESOLVED is a distinct category: the retry ladder, then an explicit unresolved
result, never −∞ and never zero.

### Registered before any computation (RIGOUR 1; this commit is the registration)

**Short-circuit temperature order.** The twelve measured temperatures in **ascending order**
(coldest first): 15, 20, 25, 27, 30, 35, 37, 40, 43, 45, 47, 50 °C. Reason from T1's record:
at D44 the only failing temperature is 15 °C at all 58 evaluations; across the 800 validated live
points every point that is infeasible anywhere is infeasible at 15 °C (798 of 800 fail there;
765 fail everywhere). A dead draw therefore costs one solve. The first `infeasible` returns −∞
immediately; the remaining temperatures are not solved.

**Retry ladder for a non-optimal, non-infeasible solve, inside the likelihood:** (1) the
registered solve (pfba tie-break, tolerances 1e-9); (2) the same temperature re-solved with
`OptimalityTol`/`FeasibilityTol` 1e-12; (3) re-solved with dual simplex (`Method=1`). A rung
returning `optimal` continues normally (recorded as RESOLVED_ON_RETRY in the worker's counter); a
rung returning `infeasible` returns −∞ (STRUCTURAL_ZERO: T1 found no case where a first-rung
non-optimal status became infeasible on retry or vice-versa, and the same three rungs are kept).
A solve still non-optimal and non-infeasible after all three rungs, or a temperature exceeding
its **60 s SIGALRM per attempt**, is **UNRESOLVED**: the worker raises `UnresolvedSolve` carrying
θ, the temperature and the three statuses; the runner appends it to `unresolved.jsonl` in the
run directory and **the run halts**; the driver writes `driver_stopped` with reason
`UNRESOLVED_SOLVE`, the run number and the θ. It is never converted to a number and no fit
containing one is accepted (spec §2). Difference from T1's offline ladder, stated: T1 rebuilt the
model fresh on every rung; inside a pool worker the same model is re-solved (P10 D3a: fresh vs
reused agree to 0.0000 under pfba). Evaluation alarm: **300 s per likelihood evaluation**.

**The audit set** is T1's 876 points, by label and source exactly as `reports/T1_target_revision/
task2_classify.py::points()` builds them: 58 D44 (`real_curvature_probe/evaluations.json` `u`,
sha `fc4a8a5d…`), 6 stratum states (`stratum_probe.json` `start`), 800 red2/6800 (archive-only
`validated_live_input.npz`, sha `ef1c50d1…`), 12 P12 (`task2c_converged.csv`); their T1 classes
in `task2_classify_all.csv` (sha `d1309afb…`). **Tolerance 1e-6** for old-versus-new log L at
every FEASIBLE point (the spec's repeatability tolerance). **Prediction, written now:** the 13
points T1 classified feasible at every temperature (2 red2 + 11 P12) reproduce their old log L
to 1e-6 under the revised target, and every one of the 863 points with a STRUCTURAL_ZERO at any
temperature returns exactly −∞; any feasible point that moves, or any infeasible point not at −∞,
STOPS TASK 2. The datum table's seven stratum/D44 rows total −∞ with all 12 (or 1) positive
measurements accounted for by the −∞; the six feasible P12 rows are unchanged to 1e-9.

**Development seeds for T2:** **17301–17305** (disjoint from every earlier development set and
from the reserved 17901–17905): 17301 short-circuit draws (50), 17302 prior-rejection draws
(2,000), 17303 diagnostic-coordinate draws (100), 17304–17305 the driver's dry run on the toy.
**Reserved seeds 17901, 17902, 17903, 17904, 17905 → runs 1, 2, 3, 4, 5**, used only by the
driver, once each. Each run's prior-rejection sample for check (d) uses
`np.random.default_rng([seed, 1])` — a seed sequence derived from that run's reserved seed, used
once, by the driver.

**Sampler settings: P16's exactly** — nlive 800, `rslice`, slices 3, bound `multi`, dlogz 0.1,
`first_update={'min_eff': 30}`, 16 processes, checkpoint every 1800 s, chunks of 250
iterations. Dimension: 16 − f_metab (removed) − dTm (pinned at 0, the P16/P17 conditioning) =
**14 physical**, plus in the validation configuration **2 diagnostic** coordinates: `f_metab_diag`
with f_metab's original prior (truncated Normal(0.28, 0.03) on [0.15, 0.45]) and `beta31_diag`
with Beta(3,1) on [0, 1] (transform u ↦ u^{1/3}), both `pert=None`, both proven inert in TASK 3
before launch. **The five runs use the validation configuration.** The physical posterior is the
same by independence. **Per-run alarm 16 h; driver ceiling 72 h.** Outputs under
`strains/eciML1515/outputs/calibration_configD_NLDM_recipe_T2_validated/run{k}_seed{seed}/`.

**How dynesty 3.1.0 treats −∞, read from its source before deciding anything** (`sampler.py`
113–236, `utils._LOWL_VAL = −1e300`): the initialiser draws batches of nlive prior points until at
least `min_npoints = 100` have finite log L, fills the remaining live slots with the −∞ draws at
`_LOWL_VAL`, and sets `logvol_init = −log(attempts)`; the plateau of −∞ points is then removed
with the volume accounted for. **Consequently dynesty's log Z is over the FULL prior, feasible
fraction included**, and the run's early iterations replace the −∞ slots by unit-cube draws at
~1 solve per rejected draw — the ~20,000 draws the prompt anticipates. The unit-cube draw count
is read from `ncall` at the first bound update and reported per run.

**The protocol's thresholds, quoted with their calibration source, frozen in
`docs/VALIDATION_PROTOCOL.md` in the next commit:**
(a) weighted CDF distance ≤ 0.05 and |CDF mean − 0.5| ≤ 0.05 on each run [P17 D25];
(b) correct-CDF distance on b³ ≤ 0.05 and wrong-Uniform distance ≥ 0.30 [P17 D25];
(c) every physical median within 2 bootstrap MC errors across all pairs [P11 rule]; leading three
unit-cube eigenvectors pairwise |cos| ≥ 0.9; width ratio per direction within 0.1 [uncalibrated,
from P16 D5];
(d) **AMENDED by the PI:** each run's prior-rejection fraction (2,000 derived-seed draws) within
2 standard errors of the two-sample difference from TASK 2's 2,000-draw measurement, and the
dead stratum's posterior mass exactly 0 by construction (no sample with a finite weight is
infeasible anywhere) — reported with the living fraction as a finding, not a target;
(e) unresolved-evaluation rate ≤ 1 % of draw-temperatures; measured value inside the predictive
2.5–97.5 % interval at ≥ 10 of 12 temperatures; no positive measurement unscored [uncalibrated];
(f) reconstructed log Z within 1e-9; weights normalise within 1e-12; inverse-prior cube error
≤ 1e-14; every hash matching; five log Z within combined reported error [P17 audit / P11 rule].
Any single failed check on any run: NOT PASSED for the programme, R1 open, blocker named.

**Not done by this prompt, whatever the outcome:** no sampler change in response to a result; no
threshold revisited; no second use of a reserved seed; no componentwise median quoted; no claim
beyond D NLDM.

## D1 — TASK 0 complete: baseline gates with every option OFF; the protocol frozen

Battery run in the worktree at `b9c79c2` (`gates_worktree.sh`, log `task0_gates_off.log`, git-ignored):
**K1 79/79, P1 60/60**, every `rc=0`. The thirteen `resolved_config.yaml` dumps differed by the
worktree's absolute path only (26 lines, none a value — §4's 3.15 artefact, as in T1 D1); restored
with `git checkout -- strains/`. `docs/VALIDATION_PROTOCOL.md` committed at `9b91420`, (d) restated,
signature dated, no DRAFT threshold left; the draft retained beside it. `status.json` → `task0_done`.
The redirect `status.json` is in the primary tree (untracked there; D0).

## D2 — TASK 1: the two approved options implemented (default OFF), gated OFF byte-identical, switched ON for eciML1515, and the P3 gate unchanged

**The code.** `src/etcgem/gasflux.py`: `UnresolvedSolve`, `_ladder` (rung 2 tolerances 1e-12, rung 3
dual simplex, parameters restored), and `flux_tpc(..., stop_on_infeasible=False, retry_ladder=False)`
— the loop returns at the first `infeasible` with `df.attrs["infeasible_at"]` set when the first is
on, and runs the ladder for the growth solve and the tie-break solve when the second is on, raising
`UnresolvedSolve` if every rung fails. `src/etcgem/calibration_multi.py`:
`respiration.infeasible: exempt | zero_lik` (default `exempt` = the code as it was) in
`gasflux_log_likelihood` — under `zero_lik`, −∞ on the first infeasibility, `UnresolvedSolve`
re-raised (a solver exception is likewise an `UnresolvedSolve`, not a silent −∞), feasible states
scored exactly as before; and `_build_gasflux_ctx` reads `gas_exchange.calibration`
(`remove_inactive`, `diagnostic_coords`) into the spec options. Smoke test before any gate: D44's
baseline reproduces its saved log L to **0.0** on the default path and returns **−∞ in 0.2 s** (one
solve) under `zero_lik`; p38 (feasible everywhere) differs between the two paths by 2.6e-10 (a
second solve on the same warm model).

**Gates with both options OFF, on the patched code:** K1 **79/79**, P1 **60/60**, every `rc=0`;
the thirteen `resolved_config.yaml` diffs are the worktree path only (26 lines, 0 values), restored.

**ON for eciML1515 only** (`gas_exchange.yaml`, with the reasons in the file): production sampled set
**14** (`dTopt, topt_scale, dCp_scale, tm_scale, kcat_scale, kappa_scale, sigma, f_maint, ngam_scale,
ngam_steepness, clearance_mult, resp_scale, disc_resp, disc_growth`; dTm pinned, f_metab removed);
validation set **16** (+ `f_metab_diag`, `beta31_diag`). Configuration hashes `85da50e9…`
(production) and `fe223870…` (validation), recorded again by TASK 3.

**P3 gate with both ON:** `gate_def_table.csv` **byte-identical** to the committed table (all ten
comparisons, growth and respiration R² unchanged) — structural, as the P10/P13 notes said, and now
verified for these two options too. **Parsa's D NLDM θ is feasible at every measured temperature**
(MAP and median; recipe and blanket media; `task1_parsa_feasible.json`), so the −∞ rule does not
touch the gate's point. Dated note appended to `reports/P3_gate/README.md`.

**One thing noticed and NOT changed (RIGOUR 9), flagged for the PI:** under `clamp` a feasible
temperature whose model O₂ uptake is exactly ≤ 0 is still unscored (the `o2 > 0` mask). The
approval covers infeasibility only; T2 leaves that case as it was and **counts it** (every TASK 2
and TASK 5 script reports unscored positive measurements). If it ever occurs it is reported, not
silently absorbed.

## D3 — a dated correction to the retry ladder's rung 2, forced by the solver's parameter bounds; and a correction to T1's record

**What happened.** TASK 2's prior-rejection sample (2,000 draws, seed 17302) crashed in a pool
worker: `GurobiError: Unable to set parameter OptimalityTol to value 1e-12 (minimum is 1e-09)`.
The ladder had fired — a tie-break solve on a prior draw returned a status that is neither optimal
nor infeasible — and its rung 2, registered in D0 as "1e-12 tolerances", cannot be set: Gurobi's
documented floor for `OptimalityTol` and `FeasibilityTol` is **1e-9**. The argument for the
correction is the solver's parameter bound, independent of and predating any judged data (RIGOUR 2).

**The correction.** `_ladder` rung 2 now re-solves at the **tightest tolerances the solver
accepts**, read from `getParamInfo` (1e-9 for Gurobi) rather than hard-coded; rung 3 is unchanged
(dual simplex). Since the registered first solve already runs at `tiebreak_tol` = 1e-9, rung 2 is a
re-solve from the current basis at the same tolerances — a legitimate retry, and the statuses it
returns are recorded with their tolerance (`optimal@tol1e-09`, `…@dual`) so the record shows which
rung resolved what. Nothing else in the ladder or the likelihood changes. The rejection sample is
re-run from scratch with the same seed; the crashed attempt produced no data.

**Consequence for T1's record (RIGOUR 4: dated addition, nothing erased).** T1's
`task2_classify.py` passed `tiebreak_tol=1e-12` to `flux_tpc` for its rung 2, and `flux_tpc`'s
P10-era `try/except` around `setParam` swallows the failure and leaves the model's tolerances as
they were. **T1's rung 2 therefore ran at the model's existing tolerances, not at 1e-12**, and the
same holds for rung 3 (dual simplex at those tolerances). The *classification* is unaffected as a
fact — every non-optimal temperature was `infeasible` on all three rungs as executed, and 0 were
UNRESOLVED — but T1 D8's and the T1 package's phrase "at tolerances 1e-12" is wrong and is
corrected here; OPEN_ITEMS 1.25/1.30 get the dated note in TASK 6. The P10 `except` is not changed
by T2 (it is the default path's behaviour and the gates depend on it); the ladder reads the floor.

## D4 — TASK 2: the instruments re-verified under the revised target; the prior rejection rate measured (item 1.33's number)

**The invariant at all 876 audit points** (`task2_invariant.csv`, sha `309d87cf…`; 2.7 min, one
warm ctx, 120 s alarm per evaluation): exactly as predicted in D0 — the **13** points T1 classified
feasible everywhere reproduce their old log L with **maximum difference 9.59e-08** (tolerance 1e-6;
2 red2 + 11 P12), and all **863** points with a STRUCTURAL_ZERO at any temperature return
**−∞** (798 red2/6800, 58 D44, 6 stratum, 1 P12). **0 STOP, 0 UNRESOLVED.**

**The datum table's 13 points under zero_lik** (`task2_datum.csv`): the seven stratum/D44 rows are
**−∞** — the parameter set has zero likelihood, so all 12 (or 1) positive measurements that escaped
scoring under the omission (73 in total) are accounted for by the verdict, none by silence; the six
feasible P12 rows are unchanged to **≤ 1.85e-9**. Stated against the prompt's bar: **2 of the 6 are
within 1e-9 and 4 miss it by ≤ 0.85e-9** (A 1.85e-9, B* 1.29e-9, worst 1.65e-9, p50 1.07e-9) —
the same solve-to-solve reproducibility T1's own table showed at three of these points (≤ 0.65e-9),
and the same points pass the registered 1e-6 invariant above at ≤ 9.6e-8. The 1e-9 is not moved
(RIGOUR 2); the miss is reported.

**Short-circuit** (`task2_shortcircuit.csv`, 50 draws, seed 17301): **50/50 identical verdicts**,
7 infeasible, every first failure at 15 °C on both paths; **77 of 600 solves saved** (the seven dead
draws cost one solve each instead of twelve); 1.66 s vs 1.88 s per draw.

**Prior rejection rate — 1.33's number** (`task2_rejection.json`, 2,000 draws, seed 17302, 16
processes, 5.3 min, 20,413 solves): **16.45 % rejected, Wilson 95 % [14.89 %, 18.14 %]**; the
rejection fires at **15 °C in 326 of 329** cases, at 47 °C once and at 50 °C twice; **0 UNRESOLVED**
(the ladder, when it fired, resolved). Of the 1,671 feasible draws, **636 are living** (peak growth
≥ 50 % of 2.0761 /h) — i.e. about 32 % of the prior. **The prompt's "~96 % of the prior at −∞" is
not what the prior does**: that figure described P16's *live points at iteration 6800* (765 of 800),
which is where the sampler had concentrated, not the prior volume. The dead stratum's advantage
was 81.5 % of posterior *weight* from 16 % of prior *volume*, because its ceiling −18.68 out-scored
most living points under the omission. Reported as a finding; the (d) reference is this measurement.

`status.json` → `task2_done`.

## D5 — the diagnostic-inertness instrument corrected before it is read: same model instance, exact Perturbation equality, bracketing repeats

**What the first run showed** (`task3_diagnostics.log`, 22:16–22:24, retained): 100 points, 85
finite, 15 at −∞ on all three evaluations; **20 of 100 within 1e-12, maximum difference 2.98e-05**.
The script evaluated the production configuration on one `_build_gasflux_ctx` model instance and
the validation configuration on a second, so the comparison contained the **cross-instance
reproducibility of the LP** (P7 D5: 1e-4; P10 D3a: 0.0000 at four decimals under pfba) — a property
of two solver histories, not of the diagnostic coordinates. The 1e-12 bar was registered for the
coordinates' effect; the instrument measured something else. Argument independent of the data:
the two instances would differ by ~1e-5 with no diagnostic coordinates at all.

**The corrected instrument, registered now:** (1) **exact** equality of the `Perturbation` object
`to_pert` hands the model under the validation specs and under the production specs, at every one
of the 100 points and both diagnostic draws — the model can only see θ through that object, so
equality is the proof that the diagnostics "do not enter the model or feasibility"; (2) on **one**
model instance, in the order production → validation(d1) → validation(d2) → production(repeat),
the validation log L compared with both bracketing production values; the point is INERT at 1e-12
if |val − prod| ≤ 1e-12, and otherwise the residual is reported against that point's own
production-repeat difference (the same-instance solve-to-solve floor, ~1e-9 at p38 in D2). The
1e-12 column is kept and reported as registered; the exact-Perturbation column is the structural
proof; the repeat-floor column says what any residual is. Same 100 points, same seed 17303.

## D6 — TASK 3 (i): the diagnostic coordinates are inert by the exact test; what the log L residuals are

`task3_diagnostics.csv/json` (corrected instrument, D5; 100 points = 13 feasible audit points + 87
prior draws with seed 17303; 10.8 min; configuration hashes production `85da50e9…`, validation
`fe223870…`). **The `Perturbation` the model receives is identical under the validation specs and
the production specs at 100 of 100 points, for both diagnostic draws** — the diagnostics enter
neither the model nor feasibility, exactly. The 15 points at −∞ are −∞ in all four evaluations.

**The log L column, reported as registered and then explained.** Within 1e-12: **17 of 85**
finite points; within the point's own production-repeat difference: 50. Median same-instance
difference **3.9e-11**, 90th percentile 1.4e-8; two points exceed 1e-6: `prior17303:15`
(log L −404.4; validation 2 and the production *repeat* both moved by 8.8e-5 from the first
production value) and `prior17303:72` (log L −148.1; one of four evaluations moved by **0.0276**,
the other three agree to 5e-8; on the other instance in attempt 1 all three agreed). With the
Perturbation provably identical, these are the LP's **warm-state path dependence** at deep-prior
draws — the "solver tolerances and warm-state effects" the spec's item 3 names — not the
coordinates. Recorded as a hazard for interpretation: the runs' pool workers are warm (as P16's
were), and check (e)'s predictive draws are evaluated fresh under the ladder. The 1e-12 bar is
reported failed as written (RIGOUR 2); the exact-Perturbation criterion of D5 is the proof.

## D7 — TASK 3 (ii): the driver, dry-run on P17's smooth analytical target; kill-and-resume proven bit-identical

`run_protocol.py` (properties in its header: idempotent, sequential, self-auditing, self-stopping,
checkpointed, detachable, alarmed). Toy mode uses `controls.Target('smooth')` (15-D, identity
transform) through the same code path — pool, chunks, checkpoints, status writes, manifest,
audit — with its own `status_toy.json` so the real `status.json` is untouched.

**A — two seeds (17304, 17305), nlive 100, 4 processes, foreground:** both complete (1,343–1,344
iterations, ~3 s each), **both audits PASS** (restored arrays == saved; weights normalise to
9.4e-15; ESS reproduces; log Z re-derived by this file's own quadrature to 1.8e-15; cube inverse
0; every hash), `status_toy.json` written at every stage (`driver_running` per chunk →
`driver_finished`), `driver.pid` removed at exit.

**Kill-and-relaunch — nlive 3000, one process, checkpoint every 2 s (the nlive-100/800 toys finish
in 3–11 s, before any kill):** run 1 (seed 17305) was killed with SIGTERM at **iteration 1810** (a
checkpoint existed; `run_status.json` said `complete: false`; the stale `driver.pid` was left, as
after a reboot). The relaunch found the pid dead, **RESUMED from the checkpoint at iteration
1810, ncall 5245**, ran to completion (44,189 iterations, 677,023 calls), audit PASS. An
uninterrupted control with the same seed and settings gives **bit-identical** log Z
(−13.578464251949018), `samples`, `samples_u`, `logl` and `logwt` (sha256 equal) — dynesty's
restore replays its own random state (P15 D3's finding, used constructively). No stray workers
after the kill (`spawn_main` count 0). Outputs retained under `dryrun/{A,B,C,D,E}` (B and C were an
earlier attempt where the run finished before the kill; retained, not counted).

**The driver is therefore fit to be left unattended.** `launch_status.md` carries the check,
relaunch and do-not-do lists and the resumption route. `status.json` → `task3_done`.

## D8 — TASK 4: the driver launched, detached, and checked at ten minutes; this session's work ends here

**Launched 2026-09-13 22:42:33**, from the worktree root, `nohup ../etcGEMs-venv/bin/python -u
reports/T2_validated_posterior/run_protocol.py > reports/T2_validated_posterior/driver_stdout.log
2>&1 &` with `GRB_LICENSE_FILE=~/gurobi.lic` exported; **pid 83007**; the driver's own log is
`driver.log` (git-ignored; the stdout copy carries the solver banners). No prior `driver.pid`, no
other driver process.

**The ten-minute check (22:52:53), all three true:** (1) `driver.pid` = 83007 and the process is
alive, with 16 pool workers; (2) `driver.log` shows run 1 (seed 17901) started **fresh** at 22:50:32
after its check-(d) sample — **rejection 16.10 % [14.55 %, 17.78 %]**, 320 of 322 at 15 °C, 0
unresolved, consistent with TASK 2's 16.45 % — and its first chunk logged at iteration 252 with
1,098 draws accumulating in the unit-cube phase (dlogz 146.5, log Z −170.0 so far); (3) `status.json`
reads `stage: driver_running`, `driver_pid: 83007`, `current_run: 1`, `iteration: 252`.

**Expected completion, from P16's measured rates** (6.4–6.9 evaluations s⁻¹ on 16 processes,
198k–222k evaluations per 15-D run, 8.0–9.6 h each): five sequential 16-D runs ≈ **40–50 h**, i.e.
**2026-09-15 evening to 2026-09-16 morning**, plus ~5 min of rejection sampling per run. The −∞
short-circuit cuts a dead draw to one solve, and only ~16 % of prior draws are dead, so the
per-evaluation cost is P16's; run 1 measures it, and the driver appends the run-1 projection to
this file before starting run 2. Each run has its 16 h alarm; the driver its 72 h ceiling.

**Resumption instruction, exactly:** start a new session with the same prompt; its resumption
block reads `status.json` — **in the worktree `../etcGEMs-t2`** (the primary tree's file is a
REDIRECT saying so) — and `launch_status.md`, then the last five D-entries here. If
`driver_running` and the pid is alive: write the one-paragraph D-entry and stop. If
`driver_finished` or `driver_stopped`: TASK 5. If the pid is dead with `runs_complete < 5` and no
STOP verdict in `driver.log`: relaunch with the command in `launch_status.md` (idempotent; resumes
from checkpoints, as the dry run proved).

This session does not wait for the driver and does not poll it further.


## D-driver — run 1 measured; projection for runs 2–5 (written by run_protocol.py, 2026-09-14 10:01:35)

Run 1 (seed 17901): 15277 iterations, 235542 likelihood evaluations, unit-cube draws to the first bound
6229, 11.224 h wall (5.83 evals/s on 16 processes), log Z -27.707 ± 0.110,
n_eff 10400, converged on dlogz: True. **Projection, if runs 2–5 track run 1:** 44.9 h more,
finishing about 2026-09-16 06:55. Each run's own 16 h alarm stands.

## D9 — status check 2026-09-15 06:57 (session asked "is this still going"): driver alive, runs 1–2 complete and audited, run 3 in progress; nothing touched

`status.json` reads `driver_running`, pid **83007** alive with 16 workers. **Run 1** (17901): 15,277
iterations, 235,542 evaluations, 6,229 unit-cube draws, **11.22 h** (5.83 evals s⁻¹), log Z
**−27.707 ± 0.110**, n_eff 10,400, converged, **audit PASS**, rejection 16.10 %. **Run 2** (17902):
13,465 iterations, 206,277 evaluations, **13.39 h** (4.28 evals s⁻¹), log Z **−28.047 ± 0.100**,
n_eff 7,899, converged, **audit PASS** (log Z re-derived to 0.0, cube 5.6e-16, weights 7.6e-15,
0 unresolved), rejection 14.50 %. **Run 3** (17903) started fresh 23:40:59 after its rejection sample
(13.70 %); at 06:42 iteration 9,288, dlogz 2.62, 7.07 h. The runs are **slower than P16's rate**
(11–13 h against 8–9.6 h; the pool ran at 4.3–5.8 evals s⁻¹, not 6.4–6.9) and the driver's own
run-1 projection (D-driver, 2026-09-16 06:55) is already behind: at 12–13.5 h per run the five
finish about **2026-09-16 14:00–16:30**, against the 72 h ceiling at **2026-09-16 22:42** — a 6–8 h
margin; the ceiling is checked between runs, so run 5 must *start* before it, which it should by
~03:00 on the 16th. The two log Z so far agree within their combined error (|Δ| 0.34 vs 0.15 — **no:
0.340 > 0.149**, they do NOT agree by P11's rule as they stand; TASK 5 judges this against the
frozen (f) with all five runs, and it is noted now, not interpreted). No relaunch, no setting
change, no run directory touched; this session stops here as the resumption block requires.

## D10 — resumption 2026-09-15 20:21: `driver_stopped`, reason CRASH in run 3; the diagnostic registered before it is run

`status.json`: `stage: driver_stopped`, `stopped_reason: CRASH`, `runs_complete: 2`, `runs_audited: 2`,
written 07:45:47; pid 83007 dead, 0 workers; `git status` shows only the driver's own writes
(`status.json`). Run 3 (seed 17903) last checkpointed at **iteration 9,288** (06:42:03, ncall
136,647, dlogz 2.62, log Z −28.33 so far); the crash came ~64 min later, so the exact crash
iteration is not on disk. The exception, verbatim in `driver_stdout.log` and `status.json`:
`RuntimeError: Slice sampler has failed to find a valid point`, with `nstep_left −1e-323`,
`nstep_right 3.5e-323` (the slice bracket collapsed to floating-point zero), `loglstar
−19.163290012175775`, `u_prop == u` — the proposal never left the starting point — the starting
live point `u` at (0.403, 0.971, 0.355, **0.991**, 0.501, 0.678, 0.855, 0.532, 0.585, 0.387, 0.479,
0.969, 0.188, 0.571, 0.964, 0.206) in the sampled order (dTopt … disc_growth, f_metab_diag,
beta31_diag) — **tm_scale at u = 0.991**, i.e. at the upper edge of its prior (2.2), where P16's
addendum said to watch for railing — and a slice direction whose largest components are
ngam_scale (+0.073) and ngam_steepness (−0.045). `unresolved.jsonl` does not exist: no solve was
UNRESOLVED; the crash is the sampler's, not the ladder's. **No relaunch** (the prompt: a crash is
diagnosed, the blocker named, R1 stays open). `driver.pid` was left behind (the atexit hook did not
run on the exception path); it names a dead process and is harmless; not deleted here — it is
the driver's file and the record of the stop.

**The diagnostic, registered now (P15's live-point covariance treatment, plus one test that
P15 could not make):**
1. Restore run 3's checkpoint (no pool); take the 800 live points in the unit cube at iteration
   9,288; eigendecomposition of their covariance; report the three smallest widths (√12λ) with
   their dominant coordinates, the live-point range of tm_scale (fraction with u > 0.95) and of
   the two diagnostics; the live log L range against loglstar −19.163; and the nearest live point
   to the crash `u` (it should be one of them or its descendant).
2. Same for runs 1 and 2 at their final checkpoints, for comparison.
3. **Reproducibility test of the crash point:** map the printed `u` through the prior transform,
   evaluate log L **fresh** (new model instance) three times and **warm** (one instance,
   three consecutive calls); report each value against loglstar. If the fresh values sit below
   loglstar while the sampler had stored a value above it, the live point's likelihood was a
   warm-state artefact (D6's 0.028 event class) and the slice collapse is mechanical: no step
   along any direction can beat a threshold the point itself no longer meets. If they sit above,
   the collapse is geometric (a ridge, P15's reading) and (1) says along which direction.
4. Runs 1 and 2 are re-audited independently and the protocol checks computed on them **as
   information**; with 2 of 5 runs R1 cannot close whatever they show.

## D11 — TASK 5 verdict: R1 OPEN. The blocker is named: the likelihood a warm pool worker returns is not always the likelihood of θ, and nested sampling cannot survive that

### The crash, diagnosed (D10's plan, executed; `task5_crash_livepoints.json`, `task5_crash_point.json`, `task5_livepoints_all.json`)

1. **The crash point is a live point.** The `u` in the exception is live point 654 of run 3's
   iteration-9,288 checkpoint (distance 0.0000), **stored log L −18.4796**, above loglstar
   −19.1633.
2. **Its true likelihood is below loglstar.** Re-evaluated on three fresh model instances:
   **−19.760854009581777, −19.760854009581777, −19.760854009581777**; on one warm instance three
   times: −19.7608540096, −19.7608540506, −19.7608540042. The stored value is **1.281 units too
   high**. So the sampler held a point above the threshold that, evaluated again, sits 0.6 below
   it: every slice proposal from it evaluates below loglstar, the bracket contracts to the point
   (`nstep_left −1e-323`), and dynesty raises. The crash was mechanical and deterministic — as
   P15 D3 found for its crash, the checkpoint would replay it.
3. **How many such points, exhaustively.** All 800 live points of each checkpoint re-evaluated
   fresh in a pool (`task5_livepoints_all.py`, 7.7 min): **run 3: four live points (654, 791,
   297, and one more) stored 1.279–1.281 above their true values** — the same offset, so one
   warm-worker evaluation and its slice-descendants — and all four true values lie below the
   current loglstar; a fifth differs at the 1e-6 level. **Run 1: one final live point stored
   4.8e-3 above its true value** (and one at 1e-3); **run 2: none above 1e-3** (one true value
   1.6e-3 below its loglstar). Runs 1 and 2 finished because dlogz reached 0.1 before loglstar
   overtook their inflated points; run 3 did not.
4. **What it is.** D6 measured the same phenomenon at a deep-prior draw (one of four same-instance
   evaluations off by 0.028): the tie-broken LP solution in a warm worker depends on the solver's
   path, so `gasflux_log_likelihood(θ)` is not a function of θ alone — P9's kink and P10's D1 (F
   LB) in another guise, here on D NLDM inside the posterior at a magnitude of 1.28 units.
   Nested sampling requires exact ordering of likelihood values; a stored value that a fresh
   evaluation cannot reproduce violates it, and the violation is fatal precisely when the run
   is closing in (dlogz 2.6 here; P15's crash at dlogz 2.17). No solve was UNRESOLVED; the ladder
   is not implicated; **no −∞ point is involved** — the approved revision did not cause this.
5. **The live-point covariance (P15's treatment), for the record.** Run 3's narrowest live
   direction (width 0.080) is tm_scale (loading −0.96); runs 1 and 2 end with tm_scale widths
   0.0069 and 0.0175 — **the posterior rails tm_scale against the upper edge of its prior mass**
   (median u 0.994 → tm_scale ≈ 1.46 with the lognormal(0.15) prior; the 2.2 truncation is not
   reached). The P16 addendum's warning realised; a finding for the PI (Y3's tail question), not
   a T2 decision. The slice direction at the crash was not along it (ngam_scale/steepness).

### The protocol checks on the two complete runs — as information only (2 of 5; R1 cannot close)

(`task5_judge.py`, `task5_checks.json`; both audits re-derived here: PASS, log Z reconstructed to
0.0, weights 1e-13 / 8e-15, cube 5.6e-16.)

| check | run 1 (17901) | run 2 (17902) | frozen threshold |
|---|---|---|---|
| (f) log Z | −27.707 ± 0.110 | −28.047 ± 0.100 | agree within combined error: **FAIL** (Δ 0.340 vs 0.149) |
| (a) f_metab_diag CDF | dist 0.044, mean 0.477 **PASS** | dist **0.088**, mean 0.508 **FAIL** | ≤ 0.05 / ≤ 0.05 |
| (b) Beta(3,1) on b³ / wrong-Uniform | **0.259** / 0.292 **FAIL** | **0.119** / 0.370 **FAIL** | ≤ 0.05 / ≥ 0.30 |
| (c) medians within 2 MC errors | — | **14 of 14 physical FAIL** (dTopt 0.33 vs −1.62, 38 MC errors; disc_growth 65) | all |
| (c) leading eigenvectors | — | min \|cos\| **0.013 FAIL** | ≥ 0.9 |
| (c) width ratios | — | max diff 0.090 PASS | ≤ 0.1 |
| (d) prior rejection | 16.10 % PASS | 14.50 % PASS | within 2 SE of 16.45 %; 0 infeasible with weight (both) |
| (e) unresolved rate | 0 PASS | 0 PASS | ≤ 1 % |
| (e) coverage growth / resp | **8/12** / 11/12 **FAIL** | **8/12** / 11/12 **FAIL** | ≥ 10/12 |
| (e) unscored positive | 0 | 0 | 0 |
| living fraction (finding) | 0.986 | 0.976 | no threshold |

**What the two runs say.** They are each internally consistent (audits pass, rejection fractions
agree with the prior's, every posterior sample feasible everywhere, ~98 % living — the −∞ rule
did what it was approved to do: **the dead stratum is excluded, not occupied**) and they
**disagree with each other in almost every physical coordinate** (dTopt by 2 K), in evidence, and
in direction. And a coordinate that provably enters nothing (D6) comes out **non-uniform in b³**
in both — the P17 D38 pattern: an inert coordinate not recovered means the sampler is not drawing
the prior correctly on the *coordinates that matter either*. With stored likelihoods that fresh
evaluation cannot reproduce at the 5e-3–1.3 level, the runs are sampling a surface with noise
on it, and noise on an ordering statistic is what neither run can recover from.

**Growth coverage 8/12** fails at **35, 37, 40, 43 °C** in both runs: the measured peak (2.076 /h
at 40 °C) lies above the predictive 97.5 % (1.62 /h). That is the *model* under-predicting the
warm-side growth peak — the same 2.3-fold-low peak E5 records for the uncalibrated prediction,
now ~25 % low calibrated — a scientific finding about configuration D, distinct from the
sampling failure, and reported as such.

### Verdict

**R1 OPEN. NOT PASSED for the programme.** Blocker, precisely: *the gas-flux likelihood as
evaluated in a persistent pool worker is not a deterministic function of θ — the tie-broken LP
returns path-dependent vertices at the 1e-3 to 1.3 log-likelihood level at posterior points — so
the nested sampler's ordering is violated, one run crashed on it, and the two that finished do
not agree.* The approved target revision (f_metab removed; −∞ for infeasibility) is implemented,
gated and verified and is **not** the cause. No posterior is quoted. No threshold is revisited, no
sampler changed, no seed reused; runs 4–5 are not started. `status.json` → `task5_done`.

## D12 — TASK 6: recorded and reconciled; the PR is opened and not merged

`report.md`; OPEN_ITEMS — 1.29–1.32 closed by dated addition (executed, not merely decided),
**1.33** opened with the rejection number and its firing temperature, **1.34** opened as the R1
blocker, R1's row restated, §0b restated (the live sequence is now the reproducibility remedy,
then five runs on new reserved seeds), 1.17 re-costed from the driver's measured 11.2–13.4 h per
run, two §4 hazards added (the detached-driver rule; the warm-solver rule); evidence rows
T2a–T2e; synthesis README correction note; `report_status.yaml` entry; stamps.

**Reconciliation (§0c, RIGOUR).** R1 moves from "surface sampleable; mode structure unknown" to
**OPEN with the blocker named**; R2 is clarified further (f_metab removed; tm_scale railing
recorded); R3 and R4 untouched. Retracted or qualified by dated note: the "~96 % of the prior"
premise (T2b), T1's "rung 2 at 1e-12" (D3), the driver's run-1 projection (D9). What this does not
license: any posterior summary, any statement about E, F, M9 or another organism, any change to a
threshold, sampler or seed. RIGOUR by number: 1 — D0 committed alone before anything ran, D5/D10
registered before their data; 2 — the 1e-9 datum miss and the 1e-12 diagnostics bar reported as
failed, not moved; 3 — the crashed run, its checkpoint, the first diagnostics attempt and the dry
run's non-interrupted attempt all retained; 4 — every correction a dated addition; 5 — (a)
passing on run 1 certified nothing; 6 — 17901–17903 used once each by the driver, 17904–17905
unused; 7 — every batch and both finished runs audited by independent reconstruction before
interpretation, and all 2,400 live points re-evaluated fresh; 8 — every job under an alarm, one
at a time, the driver's caps untouched; 9 — the target unchanged beyond the approved revision;
10 — the blocker recorded, no relaunch to "try again"; 11 — #40's base read before merging.

`status.json` → `task6_done`. The primary tree still holds the untracked REDIRECT and its stale
`index.lock`; `driver.pid` names the dead pid 83007 and stays as the record of the stop.
