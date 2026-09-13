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
