# P8 — name the ridge from the chain on disk, then take the one branch it licenses

@@STATUS@@

Detail: [DECISIONS.md](DECISIONS.md) (D0–@@DLAST@@); `task1_pca.py` → `task1_variance.csv`,
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

@@TASK2B@@

## TASK 3 — the record

@@TASK3@@

## Verification

@@VERIFY@@
