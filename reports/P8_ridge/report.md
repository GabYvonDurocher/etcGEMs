# P8 — name the ridge from the chain on disk, then take the one branch it licenses

> **Dated note, 2026-09-10 (P12): this report's geometric reading is INTACT and vindicated. No
> number below is edited.**
>
> P8 concluded the ensemble is **unimodal** with **no ridge** — PC1 carrying 16.5 % of the variance
> and tau between 110 and 121 on every one of the sixteen components. P12 mapped the basins
> directly, by local optimisation from 96 prior draws followed by bottleneck-barrier tests on
> converged endpoints, and found **one live basin** containing every point these chains and both of
> P11's nested runs ever occupied. The isotropy and the unimodality were right.
>
> What was wrong in this era was never the geometry — it was the **explanation** for tau growing in
> proportion to chain length, which P8 attributed to the sampler being outmatched. P9 corrected that
> to a **cliffed likelihood** and P10 fixed the cliffs. Read together: P8 measured the shape
> correctly and misdiagnosed the cause; P12 confirms the shape.


| task | status | one line |
|---|---|---|
| **0** — merges, clean start | **DONE** | #21 merged clean; #22 conflicted on `report_status.yaml` only, both entries kept, merged; `p8/ridge` from `033c11e`; gates on `../etcGEMs-venv` 79/79, 60/60 |
| **1** — name the ridge | **DONE — there is none** | variance spread evenly (PC1 16.5 %), τ 110–121 on every component, the four carry 14 % of the slow loading: isotropic slow mixing; **BRANCH B** by both clauses of a rule written first |
| **2B** — zeus on all sixteen | **STOPPED — NOT MIXING per wall-hour** | wired and proven on a toy; on the E. coli likelihood 20.4 s/step (11× emcee, 10 % utilisation: one walker serialises the ensemble), τ rising at the same 0.10 N; the 1500-step rule not reached |
| **2A** — fix the four | **not taken** | nothing to fix was named |
| **3** — the record | **DONE** | 1.12 closed with a conclusion; §0 sequencing; evidence P3 superseded, P4b, P5b; synthesis README correction note; stamps |

Detail: [DECISIONS.md](DECISIONS.md) (D0–D5); `task1_pca.py` → `task1_variance.csv`,
`task1_loadings.csv`, `task1_curvature.csv`, `task1_branch.json`, `task1_pca.png`;
`task2b_toy.py` → `task2b_toy.json`; `run_zeus.py` →
`strains/eciML1515/outputs/calibration_configD_NLDM_recipe_P8_zeus/`; `task2b_table.py` →
`task2b_checkpoints.csv`, `task2b_verdict.json`.

---

## TASK 0 — merges and a clean start

PR #21 (Y2) merged server-side clean → `c3d71fb`. PR #22 (P7) then conflicted on one file,
`reports/report_status.yaml`, where both branches had appended an entry at the end
(`Y2_regime_posterior` on main, `P7_walkers` on the branch); resolved in a temporary worktree
keeping both (Y2 first; the file parses to 24 entries), `docs/OPEN_ITEMS.md` auto-merged, stamps
regenerated (Y1, Y2, synthesis), pushed, #22 merged server-side → `033c11e`; worktree removed;
`p8/ridge` branched from that. Interpreter `../etcGEMs-venv`: **K1 79/79, P1 60/60**, seven
strains byte-identical. The `y2/regime-posterior` local branch survives because
`../etcGEMs-work` has it checked out; that tree is not touched.

## TASK 1 — name the ridge: there is none

Rules written before any loading was seen (D1): standardise in sampled space, PCA, τ along
each component with P6's estimator; the ridge is the smallest top-τ set reaching 50 % of the
variance (≤ 3 components); the four prior-determined parameters' variance-weighted share of
squared loading on it decides A (≥ 50 %) or B (< 50 %); an even spread of variance with τ alike
on all components is BRANCH B by the prompt's own clause. Two views, post-burn-in: P7's
128-walker chain (steps 250–1500) and P4+P6's 40-walker history (steps 1500–2500).

| | 128 walkers (P7) | 40 walkers (P4+P6) |
|---|---|---|
| PC1 / PC2 / PC3 / PC4 variance | 16.5 / 11.8 / 11.4 / 8.6 % | 21.9 / 12.1 / 10.2 / 9.4 % |
| cumulative at PC4 / PC8 | 48.3 / 75.2 % | 53.6 / 79.9 % |
| **τ across all 16 components** | **109.6–120.6** (ratio 1.10) | 88.9–105.7 (ratio 1.19) |
| top-τ components (τ) | PC6 (120.6), PC3 (120.3), PC9 (120.0) — 23.8 % of variance | PC15 (105.7), PC1 (104.2), PC4 (103.5) — 31.9 % |
| the four's share of squared loading on them | **14.3 %** | 28.4 % |
| curvature c of PC2 on PC1 (z, SE inflated by √τ) | +0.043 (**+6.7**, curved) | −0.038 (−2.8, not curved) |

Signed loadings of the top-τ component on the 128-walker view (PC6): f_maint +0.39, tm_scale
+0.37, kcat_scale +0.36, ngam_scale +0.31, disc_resp −0.30, clearance_mult −0.24, dCp_scale
+0.23, dTm +0.22, topt_scale −0.21, ngam_steepness −0.21, f_metab −0.20, sigma −0.19, dTopt
+0.18, resp_scale −0.18, kappa_scale −0.06, disc_growth −0.03 — no parameter above 0.4, the
four at 0.19–0.24. The full tables are in `task1_loadings.csv`; the scatter and loadings in
`task1_pca.png`.

**Verdict (D2).** No component carries a quarter of the variance; τ is the same on every
component to within 10–19 %; the slowest components are not the largest. That is not a ridge.
It is **isotropic slow mixing**: the ensemble moves at one slow rate in every direction of the
standardised space, which the affine-invariant stretch move — whose only lever is the
ensemble's shape — cannot improve by reshaping, and which fixing four parameters would leave
untouched in the other twelve (they carry a seventh of the slow loading). **BRANCH B**, by both
clauses. BRANCH A not taken: nothing to fix was named. Curvature is mixed between the two views
and does not bear on the choice.

## TASK 2B — zeus on all sixteen

**Wiring** (D3). zeus-mcmc **2.5.4** installed into `../etcGEMs-venv` and added to
`requirements.lock.txt` (with its seven dependencies). `run_gasflux_fit` gained
`sampler_kind="zeus"`, routed through one helper, `run_zeus_blocks`, used identically by the toy
and the driver: the same block loop, the same τ estimator at every checkpoint, zeus's `act` and
`efficiency` quoted beside it, a per-block checkpoint of `chain.npy`/`log_prob.npy` (zeus has
no resumable backend; a resume restarts from the saved positions with fresh proposals).

**Toy** (`task2b_toy.json`): 16-d correlated Gaussian, condition number 50, 40 walkers, 500
steps, a 4-process pool: every posterior mean within **2.7** Monte-Carlo SEs of the truth, every
marginal sd within **4.8 %**, correlation-matrix RMS error **0.027**; zeus efficiency 0.029,
its own act_max 49.8 against emcee-estimator τ_max 24.2. Passed. The emcee path was
smoke-tested after the driver edit and is bit-identical to P7's checkpointed run over the
first ten steps.

**The run.** D NLDM, all sixteen parameters, P6's model, data, priors and c_max, 16 processes,
seed 1, **40 walkers** (zeus asks for ≥ 2 × 16 = 32; 40 keeps the emcee rows at equal
walkers), initialised from P4's final ensemble, blocks of 250, 1500 steps, no early stop.

**Decision rule** (D3, verbatim in substance): MIXING if the mean increment in τ_max over steps
750→1500 is below 10 per block AND τ_max(1500) < 100; PARTIAL if the mean over the last three is
below 20 and each below the first block's, then extend once to 2500; anything else NOT MIXING.

**What happened.** The run was stopped after **2 h 2 min without reaching its first 250-step
checkpoint** (D5). The workers' cumulative CPU time showed utilisation falling from ~5 cores to
~1.3, and a process listing showed one worker at 78 % CPU and fifteen idle: zeus's slice move
expands and contracts sequentially within each walker's step and the pool returns only when the
slowest walker finishes, so on this likelihood — 0.45 s per evaluation, a flat discrepancy tail
to expand along — one walker starves the ensemble. Nothing but `resolved_config.yaml` had been
written (the per-block checkpoint needs a completed block). **A cost stop had been written
before any zeus τ was seen (D4)**; it was applied to a measured 30-step diagnostic instead of the
250-step checkpoint the run could not reach.

**The cost, measured** (`task2b_cost.json`; D NLDM, 40 walkers, 16 processes, blocks of 10):

| | zeus (this run) | emcee, 40 w (P6) | emcee, 128 w (P7) |
|---|---|---|---|
| s per step | **20.4** (blocks 192.9 / 199.6 / 210.3 s) | 1.86 | 5.02 |
| evaluations per walker per step | 1.86 (2 233 in 30 steps) | 1 | 1 |
| ideal parallel s per step at 16 processes | 2.1 | — | — |
| **utilisation** | **10 %** | ~100 % | ~100 % |
| cost ratio vs emcee 40 w | **11.0×** | 1 | 2.7× |

**The τ(N) curve, as far as it goes**, with the emcee rows at the same steps (emcee's own 0.10 N
slope gives its values at 10–30; its logged checkpoints start at 250):

| N | zeus τ_max (emcee estimator) | zeus act_max / efficiency / ess | chain/τ | emcee 40 w τ (0.10 N) | emcee 128 w |
|---|---|---|---|---|---|
| 10 | 0.9 | 9.2 / 0.035 / 81 | 11.2 | ~1 | — |
| 20 | 2.0 | 29.8 / 0.025 / 53 | 9.8 | ~2 | — |
| 30 | 3.2 | 49.8 / 0.022 / 50 | 9.4 | ~3 | — |
| 250 … 1500 | **not reached** | | | 28.1 … 155.9 | 26.1 … 140.8 |

**τ per wall-hour.** zeus at 20.4 s/step makes 176 steps per hour; emcee's 40-walker chain
delivered 40 × 1500 / 156 ≈ 385 walker-samples per τ in 47 min, ≈ 490 per hour (on an
unconverged τ). To match that, zeus would need τ ≤ 14 at whatever chain length it reaches; its
τ is rising at the same 0.10 N as every emcee chain in this family and reads 3.2 at N = 30,
where emcee's reads ≈ 3. **It is not ahead by 11×; it is not ahead at all.**

**Verdict: BRANCH B — NOT MIXING per wall-hour.** The D3 rule at 1500 steps was **not
reached** and is reported as such, not as satisfied or failed. What would make zeus usable here
is not a sampler setting: batching or vectorising the likelihood so a slice step is not
serialised by its slowest walker, or a cheaper likelihood, both changes to the code the fits
run on. Not made.

## TASK 3 — the record

* **OPEN_ITEMS 1.12** — **closed with a conclusion**: the family is sampler-limited and no
  sampling change tried (walkers, moves, slice sampling) fixes it; quote the configuration-D
  medians (P4) with a "not converged" label; intervals are not available from these chains; any
  change from here is a model decision (fix the four, or narrow the discrepancy priors), for the
  user.
* **OPEN_ITEMS §0 "Sequencing — E. coli first (decided 2026-09-09)"** added above §1 in the
  house style, with the four points the prompt gives and no more; `docs/CANDIDA_DISCUSSION_2026-09-07.md`
  §9 carries one dated line saying it is superseded on ordering by §0.
* **`reports/synthesis/evidence.csv`**: P1 and P2 re-read (still true as measured; sampler-limited,
  not step-limited), **P3 SUPERSEDED**, **P4b** (the PCA finding) and **P5b** (the branch verdict)
  added. CRLF preserved; the file parses (76 rows).
* **`reports/synthesis/README.md`**: a dated correction note listing, sentence by sentence, what
  the sampling section, the housekeeping list, the closing summary and the [C6]/[C8] update
  slots must say at the next render, with the evidence rows. `synthesis.qmd` not edited.
* **The synthesis's section 7 sentence** ("reaching the criterion is ~8000 steps") is now wrong
  three times over — steps (P6), walkers (P7), sampler (P8) — and the note says so.
* Stamps regenerated; `report_status.yaml` gains `P8_ridge`.

## Verification

| check | result |
|---|---|
| TASK 0: #21, #22 merged; conflicts file by file; main commit; gates on the venv | #21 clean → `c3d71fb`; #22: `report_status.yaml` one hunk, both kept; `docs/OPEN_ITEMS.md` auto-merged; stamps regenerated → `033c11e`; K1 79/79, P1 60/60, seven strains byte-identical on `../etcGEMs-venv` |
| TASK 1: variance fractions; τ per component; ridge and signed loadings; the four's share vs the 50 % rule (written first); curvature; branch | above and in `task1_*.csv`; 14.3 % (28.4 %) < 50 %; not one clean direction; curvature +6.7 z / −2.8 z; BRANCH B |
| TASK 2: checkpoint table beside P6/P7; the rule verbatim; verdict; wall-clock; τ per wall-hour | above; D3 rule quoted; NOT MIXING per wall-hour, 1500-step rule not reached; 20.4 s/step; zeus needs τ ≤ 14 to match emcee's ≈ 490 samples/h and reads 0.10 N |
| TASK 3: 1.12; §0 (quoted in OPEN_ITEMS); evidence rows; README note; stamps | done |
| `git diff main --stat` | `reports/P8_ridge/`, `src/etcgem/calibration_multi.py` (zeus wiring), `requirements.lock.txt` (zeus + 7 deps), `docs/OPEN_ITEMS.md`, `docs/CANDIDA_DISCUSSION_2026-09-07.md` (one line), `reports/synthesis/evidence.csv`, `reports/synthesis/README.md`, `reports/report_status.yaml`, stamps, one fit output directory (`calibration_configD_NLDM_recipe_P8_zeus/`, the 30-step diagnostic with a README saying so). Nothing else under `strains/`. No prior changed. |
| the old `.venv`; `../etcGEMs-work` | untouched |
