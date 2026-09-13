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
