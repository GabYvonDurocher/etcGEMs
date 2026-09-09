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
