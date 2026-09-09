# P8 — decisions

Standing rules carry over. Branch `p8/ridge` from `main` after the two merges; no push to `main`;
end in a PR that is not merged. Interpreter `../etcGEMs-venv`. Exit codes checked explicitly.
One branch per run; the PCA decides it by a rule written before the loadings are seen.

---

## D0 — TASK 0: #21 then #22, one conflict, one file, both sides kept

**Where:** TASK 0.

Nothing was running (one shell snapshot process, no python with either tree as cwd, nothing
under `reports/` written in ten minutes). PR #21 (Y2) merged server-side clean → `c3d71fb`. PR
#22 (P7) then reported CONFLICTING. Resolved in a temporary worktree (`../etcGEMs-p7merge`, on
`p7/walkers`, since the primary tree had to leave that branch for a worktree to take it) by
merging `origin/main` into the branch:

| file | what happened |
|---|---|
| `docs/OPEN_ITEMS.md` | auto-merged (both sides append-style) |
| `reports/report_status.yaml` | one hunk: both branches appended an entry at the end (`Y2_regime_posterior` on main, `P7_walkers` on the branch). **Both kept**, Y2 first; the file parses to 24 entries |
| `reports/{Y1_yeast_audit,Y2_regime_posterior,synthesis}/PROVENANCE.md` | stamps regenerated after the merge commit, then once more for the usual one-commit lag |

Pushed; #22 became MERGEABLE and was merged server-side → `033c11e`; worktree removed;
primary tree `git switch main`, `git pull`, branch `p8/ridge`. The `y2/regime-posterior` local
branch could not be deleted by `gh` because `../etcGEMs-work` has it checked out; that tree is
not touched, so the local branch stays (the remote one is gone).

## D1 — TASK 1: the rules, written before any loading is seen

**Where:** before `task1_pca.py` is run.

**Data.** Two views, post-burn-in only. (a) P7's 128-walker, 1500-step D NLDM chain: it started
from P4's final ensemble, i.e. after the ~1500-step drift D6 located, so its burn-in is the
sampler's own settling at the new walker count — **the first 250 steps are discarded** (≈ 5 τ
at the first checkpoint's τ of 26; D6's drift criterion, a flat block-median log-posterior, is
met from the first block). (b) P4's 40-walker chain plus P6's benchmark continuation, 2500
steps of one history, **steps 1500–2500** (D6: drift over the first ~1500).

**Standardise** every parameter in sampled space (the space the sampler moves in; log for the
log-space parameters) to zero mean and unit variance over the retained samples; PCA of the
pooled walker-samples; τ along each component from the projected chain (steps × walkers ×
components) with the same estimator as P6/P7 (`integrated_time`, `tol=0`).

**Naming the ridge.** Rank components by τ. The ridge is the smallest set of top-τ components
whose summed variance fraction reaches 50 %, capped at three. If that set needs more than three
components, or if τ across all sixteen components lies within a factor of 1.5 and no component
carries more than 25 % of the variance, the ridge is **not one clean direction** and that is
BRANCH B by the prompt's own clause.

**The branch rule** (the prompt's, verbatim): the four prior-determined parameters
(`topt_scale`, `dCp_scale`, `sigma`, `clearance_mult`) carry ≥ 50 % of the squared loading of
the ridge component(s) → BRANCH A (fix the four); < 50 % → BRANCH B (zeus on all sixteen). With
more than one ridge component, the share is variance-weighted: Σ_k f_k · (Σ_{four} L_{k,i}²) /
Σ_k f_k, where f_k is the component's variance fraction and the loadings are unit-norm. The
128-walker view decides; the 40-walker view is reported beside it and, if it disagrees on the
branch, that is stated and the 128-walker view still decides (it is the longer, better-mixed
ensemble at fixed history).

**Curvature.** Project the retained samples onto PC1 and PC2; fit PC2 = a + b·PC1 + c·PC1² by
ordinary least squares and report c with two standard errors: the OLS one (which treats every
sample as independent and is an underestimate) and the same inflated by √(τ_PC1) for the
autocorrelation. Curvature is "present" if |c| exceeds three inflated SEs. **Curvature does not
override the branch rule** here — the prompt says it "is the case for BRANCH B even if the four
load on it", and that is read as: if curvature is present AND the four load ≥ 50 %, BRANCH A is
still taken (fixing the four may remove the curved direction with them), and the curvature is
reported prominently as the reason BRANCH A may fail, in which case BRANCH B is the next decision
for the user, not this run.

## D2 — TASK 1 verdict: there is no ridge to name; BRANCH B, by both clauses of the rule

**Where:** after `task1_pca.py`, rules D1 unchanged.

| view | PC1 variance | cumulative at PC4 | τ across all 16 components | top-τ set to 50 % variance | the four's share on it | curvature c (z, inflated SE) |
|---|---|---|---|---|---|---|
| 128 w (P7), steps 250–1500 | **16.5 %** | 48.3 % | **109.6–120.6** (ratio 1.10) | needs > 3 components (PC6, PC3, PC9 reach 23.8 %) | 14.3 % | +0.043 (**+6.7**, curved) |
| 40 w (P4+P6), steps 1500–2500 | 21.9 % | 53.6 % | 88.9–105.7 (ratio 1.19) | > 3 (PC15, PC1, PC4 reach 31.9 %) | 28.4 % | −0.038 (−2.8, not curved) |

**The variance is spread evenly and τ is the same on every component.** No component carries a
quarter of the variance; the slowest and fastest directions differ in τ by 10–19 %; the
top-τ components are not the top-variance ones (PC6, PC3, PC9 on the 128-walker view). That is
D1's "not one clean direction" clause, and the prompt's: BRANCH B. The branch rule proper gives
the same answer — the four prior-determined parameters carry 14.3 % (28.4 %) of the squared
loading on the top-τ set, far below 50 % — so fixing them would remove nothing that is slow.
Both views agree on the branch. **The picture is not a ridge; it is isotropic slow mixing**: the
ensemble moves slowly in every direction of the standardised space at the same rate, which the
affine-invariant stretch move, whose only lever is the ensemble's own shape, cannot improve by
reshaping. The curvature reading is mixed (curved on the 128-walker chain at z = 6.7, not on the
40-walker one) and is reported as such; it does not bear on the branch since the four do not
load.

**Decided: BRANCH B — zeus on all sixteen.** BRANCH A is not taken because nothing to fix was
named: the four carry a seventh of the slow directions' loading, and fixing them would leave
twelve parameters mixing at the same isotropic rate. A 12-dimensional refit would be a
dimensionality test, not a ridge removal, and the prompt allows one branch.

## D3 — TASK 2B: the wiring, the walker count, the checkpoint, and the decision rule — written before the run

**Where:** before any zeus chain on the E. coli model.

**Wiring.** `run_gasflux_fit` gains `sampler_kind="emcee" | "zeus"`. For zeus the ensemble is
`zeus.EnsembleSampler(n_walkers, ndim, _gwlogprob, pool=pool)` with zeus's default move
(differential) and default tuning of the slice width (`tune=True`); the block loop is the same
as emcee's — `check_every` steps, then τ with the SAME estimator P6/P7 used
(`emcee.autocorr.integrated_time`, `tol=0`) so the checkpoint rows are comparable, plus zeus's own
`act` (its integrated autocorrelation time per parameter) and `efficiency` quoted beside them.
The block runner is one helper (`run_zeus_blocks`) used identically by the toy check and the
driver, so the toy proves the wiring the driver uses.

**Checkpoint.** zeus has no resumable HDF5 backend of emcee's kind; the helper saves the full
chain and log-probability (`chain.npy`, `log_prob.npy`) after **every block of 250 steps**, so a
halt loses at most one block — P7's requirement — and `resume=True` restarts from the saved
last positions and concatenates. The random state is not restorable across a resume in zeus;
that is stated, and a resumed zeus chain is therefore "same ensemble, fresh proposals", which is
fine for τ and the posterior and not bit-identical.

**Walkers.** zeus's guidance is "at least twice the number of parameters" (≥ 32 here); **40 is
used**, P6's count, so the comparison with the emcee rows is at equal walkers and the only thing
that changes is the move. Initialised from P4's final 40-walker ensemble state (D2 of P6), no
warm start. 16 processes, seed 1.

**Cost.** zeus's slice move takes several likelihood evaluations per walker per step (typically
3–10, tuned), so the honest comparison is **τ per wall-hour**, reported beside τ per step.

**Decision rule** (P7's form, verbatim in substance): at every 250-step checkpoint τ_max on the
chain so far; **MIXING** if the mean increment over steps 750→1500 is below 10 per block AND
τ_max(1500) < 100; **PARTIAL** if the mean over the last three is below 20 and each of the last
three is below the first block's, then extend once to 2500 by resume and apply the same
conditions to 1750→2500 and τ_max(2500) < 100; anything else **NOT MIXING**. If MIXING, run on
to the P6 target (n_eff ≥ 600 AND chain/τ ≥ 25) and report the posterior against P4's. If NOT
MIXING, STOP: that is P6 D6's option (iv) confirmed as the state of this family.

## D4 — a cost stop, written before zeus's first checkpoint has been seen

**Where:** 111 minutes into the zeus run, no 250-step checkpoint yet.

The prompt estimated ~3 h for 1500 steps. From the workers' cumulative CPU time (21 000 s at
91 min, ≈ 47 000 likelihood evaluations at ~0.45 s each) the run is doing roughly 5–10
evaluations per walker per step with an effective parallelism of ~5 of 16 processes — zeus's
slice move is sequential within each walker's step and the pool waits for the slowest walker —
so a step costs **≥ 20 s against emcee's 1.86 s**, and 1500 steps would be ≥ 8 h, possibly 12.
That is a fact about the sampler on this likelihood and is part of the answer (the prompt asks
for τ per wall-hour for exactly this reason).

**Decided, before any zeus τ is known:** the D3 rule on τ(N) is not revised. But the prompt's
honest comparison is per wall-hour, and a per-wall-hour verdict can be reached earlier than
1500 steps. So: at the 250-step checkpoint the per-step cost ratio r = (zeus s/step) /
(emcee 40-walker s/step, 1.86) is measured. If zeus's τ_max(250) is **not below emcee's
40-walker τ_max(250) = 28.1 divided by r** — i.e. zeus is not ahead per wall-hour by at least
its cost — then it cannot win on the wall-hour criterion whatever τ does later, and the run is
stopped **at 500 steps** (one more block, so that an increment exists), the 1500-step rule is
reported as *not reached*, and the verdict is **NOT MIXING per wall-hour**, with the τ(N) curve
as measured and the cost stated. If zeus IS ahead by at least r at 250, the run continues to
1500 and the D3 rule applies as written. This is a resource decision made on the cost the run
has already revealed, recorded before its τ has; it does not touch the mixing rule.

## D5 — the zeus run was stopped before its first checkpoint; the cost was measured instead; BRANCH B does not mix per wall-hour, and the 1500-step rule was not reached

**Where:** TASK 2B, 2 h 2 min into the run.

**What was seen.** No 250-step checkpoint after 122 minutes. The workers' cumulative CPU time
went 15 756 s at 52 min → 21 228 s at 91 min → 22 867 s at 112 min: utilisation falling from
~5 cores to ~1.3. A process listing showed **one worker at 78 % CPU and fifteen idle** — zeus's
slice move expands and contracts sequentially within each walker's step (up to `maxiter`
10 000 evaluations), the pool returns only when the slowest walker finishes, and on this
likelihood (0.45 s per evaluation, a flat discrepancy tail to expand along) that walker starves
the ensemble. The run was killed. It had written nothing but `resolved_config.yaml`: the
per-block checkpoint needs a completed block. That loss is stated.

**What was measured instead** (`task2b_cost.py`, `task2b_cost.json`): the same fit, 40
walkers, 16 processes, 30 steps in blocks of 10 — **20.4 s per step** (blocks 192.9, 199.6,
210.3 s), **11.0× emcee's 1.86 s** at the same walker count; 2 233 evaluations, **1.86 per
walker per step** on average, so the ideal parallel cost would be 2.1 s/step and the realised
**utilisation is 10 %**. zeus's own diagnostics at 30 steps: act_max 9.2 → 29.8 → 49.8,
efficiency 0.035 → 0.022, ess 81 → 50. emcee's estimator on the same chain: **τ_max 0.9, 2.0,
3.2 at steps 10, 20, 30 — 0.10 N, the same slope as every emcee chain in this family**, chain/τ
9.4–11.2.

**The verdict, by D4's cost stop.** D4 was to be applied at the 250-step checkpoint, which the
run could not reach in any acceptable time; the same test is applied to what the diagnostic
gives. zeus is ahead per wall-hour only if its τ_max is below emcee's at the same step divided
by the cost ratio, 11.0. At step 30 emcee's τ (from its own 0.10 N slope) is ≈ 3 and zeus's is
3.2 — zeus is not ahead by 11×, it is not ahead at all. In independent samples per wall-hour:
emcee's 40-walker chain gave 40 × 1500 / 156 in 47 min ≈ 490 per hour (on an unconverged τ);
zeus at 176 steps per hour would need τ ≤ 14 to match, and its τ is rising at 0.10 N from a
chain of 30. **BRANCH B: NOT MIXING per wall-hour; the D3 τ(N) rule at 1500 steps was not
reached and is reported as not reached, not as satisfied or failed.** The fix that would make
zeus usable here — vectorising or batching the likelihood so a slice step is not serialised by
its slowest walker, or a cheaper likelihood — is a change to the code the fits run on, not to
the sampler, and is not this run's to make.

**What this confirms.** P6 D6's option (iv) is the state of this family: no sampler
configuration tried — 40 → 128 walkers (P7), DE moves (P6), an ensemble slice sampler (P8) —
changes the τ ∝ N signature or is affordable, and the PCA (D2) says there is no ridge to remove.
The remaining options change the model: fix the four prior-determined parameters, or narrow the
discrepancy priors. Until one is taken, the configuration-D posteriors are quoted as P4's
medians with a "not converged" label, and E/F wait on the LP tie-break (OPEN_ITEMS 3.21).
