# T1 — decisions, from the first judgement call

## D0 — premise, scope under §0a, the RIGOUR rules applied, and the registration that governs every computation in this prompt

_Committed alone, before any computation, in the `../etcGEMs-t1` worktree on `t1/target-revision`
from main `e80ffd2` (the housekept main: TASK 0a merged as PR #39)._

### Why the worktree, and the one thing left untidy

The primary tree's `.git/index.lock` is a **stale zero-byte file** held open only by the sandbox
VM's file server (`com.apple.Virtualization.VirtualMachine.xpc`, pid 62662, fd `952r`); no git
process exists. The T1 constraint says never delete a lock file, so it was not deleted, and it did
not clear in 200 s of polling. **All T1 writes therefore go through `../etcGEMs-t1`, whose index is
independent.** The primary tree is left on branch `t1/housekeeping` holding uncommitted edits
identical to what PR #39 merged; they are regenerable and are reconciled once the lock clears.
Recorded as a blocker (RIGOUR 10), not worked around by deletion.

### R3 complete — confirmed, not assumed

`main` = `origin/main` = `3222b9d` before housekeeping, `e80ffd2` after. Gates on the primary tree
79/79 and 60/60 (R3 TASK 5). `docs/INTEGRATION_STATE.md` and `reports/R3_integration/report.md`
present. `codex/p17-inactive-prior` local at `ef1961b`, absent from origin, its worktree now at
`../etcGEMs-p17-archive` (moved in 0a, same APFS volume, verified clean with the manifest readable).

### Which of R1–R4 this prompt can move

**None directly.** It prepares three decisions and a protocol; it launches no fit. It **may clarify
R2**: TASK 1 establishes from the code and its history whether the sampled `f_metab` enters
configuration D at all — that is a statement about what the model *can* identify, which is R2's
subject. R1, R3 and R4 are untouched, and any summary that reads otherwise is wrong.

### RIGOUR.md rules applied, by number

**1** — this D0 registers tolerance, audit set, seeds and budgets before any judged computation.
**2** — no threshold moves to suit data; the 1e-6 tolerance is the spec's, not mine.
**3** — every outcome retained, including every stencil, every unresolved solve, every adverse trace.
**4** — withdrawals by dated addition; nothing erased.
**5** — nothing here is a posterior certificate; the invariant proof shows two targets agree, not that either is right.
**6** — reserved seeds 17901–17905 are **not consumed**; new evaluations use the seeds registered below.
**7** — every batch is reconstructed from saved arrays and hash-audited before interpretation.
**8** — every model solve runs under a tested SIGALRM deadline, one job at a time.
**9** — the scientific target is unchanged: no prior, parameter, medium, allocation or maintenance moves; a core option may be *added* default OFF, never turned on here.
**10** — an unresolved solve is reported as unresolved; a blocker is recorded, not papered over.
**11** — any PR merged here has its `baseRefName` read first.

### Registered before any computation

**Repeatability tolerance for old-versus-new log L:** **1e-6** (the spec's existing repeatability
tolerance, §1 "Validation after approval"). Reported as the maximum absolute difference over the
audit set; any point exceeding it STOPS TASK 1.

**Archived audit points every comparison uses**, with their on-disk identity:

| set | count | source | identity |
|---|---:|---|---|
| D44 baseline + stencils | **58** | `reports/P17_inactive_prior/real_curvature_probe/evaluations.json` (on main) | `u` in the 15-D unit cube, saved `logl`, saved per-temperature `status`/`growth`/`o2_uptake`; baseline `−17.972547016139384` |
| saved stratum states | per `stratum.json` | `reports/P17_inactive_prior/stratum.json` (on main) | curve max `−18.68250229422251` at `disc_growth = 1.1407216216373017`; scope "algebraic compatibility only" |
| red2/6800 live set | **800** | `reports/P17_inactive_prior/validated_live_input.npz` — **archive only** (`../etcGEMs-p17-archive`; a `.npz`, excluded from main by R3's curation) | sha256 `ef1c50d10a99063a9843289d08078f9fea3781b1654c43a692ad3d1e36357c1e`; arrays `u`(800,15), `theta`(800,15), `indices`, `stored_logl` |
| P12 converged endpoints | **12** | `reports/P12_modes/task2c_converged.csv` (on main) | 16-D sampled coordinates incl. `dTm`; p38 log L `−7.186` under the P13 likelihood |
| feasible-non-growing examples | **4** | `reports/P13_support/addendum1_dead_temperatures.csv` | A/B\*/p81 at 15 °C, worst(b5) at 50 °C, O₂ 0.525–5.674 |
| saved infeasible examples | as found | every `status == 'infeasible'` temperature across the sets above | the 15 °C solve at D44's baseline is one |

Every point is used **as saved**; nothing is re-optimised.

**Seeds for any new evaluation in T1:** **17201–17205** (development; disjoint from P17's
development seeds 17001–17005/17501–17513/17701–17755/17821 and from the reserved 17901–17905).
Used only for TASK 3's rule-chosen living-region points and any bounded retry that needs one.
**The reserved seeds 17901–17905 are not touched.**

**Per-step alarm budgets** (SIGALRM, tested before first use; a timeout is a recorded UNRESOLVED
outcome, never a retry without limit):

| step | per-solve | per-batch |
|---|---:|---:|
| invariant proof, one log L (TASK 1) | 120 s | 58 + 800 + 12 + 4 points, one job at a time, 2 h |
| classification + bounded retry, one temperature (TASK 2) | 60 s per attempt, 3 attempts max | 2 h |
| curvature trace, one stencil evaluation (TASK 3) | 300 s | 58 D44 + 5 diverse × 7 axes × 4 offsets, 4 h |

**Bounded retry ladder for an unresolved solve** (TASK 2), registered now: (1) fresh model, same
tolerances; (2) fresh model, `tiebreak_tol`/feasibility 1e-9 → 1e-12; (3) fresh model, dual simplex
only. A solve that fails all three is **UNRESOLVED**, reported as such, never scored as zero.

### What no task in this prompt may do

Turn any option ON; wire `f_metab` into allocation; choose an observation model; implement a
candidate as production; apply a curvature correction; fix a parameter; change a prior; look at a
posterior to inform any of TASKS 1–3; launch a fit. The prompt ends at the decision package.
