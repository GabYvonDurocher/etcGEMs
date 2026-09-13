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

## D1 — TASK 1 in progress: the gate, the proof launched, and what TASK 3 will evaluate, registered before it does

### The removal option, implemented default OFF (`src/etcgem/calibration_multi.py`, `build_gasflux_specs`)

`remove_inactive: [names]` drops named coordinates from the sampled set; `diagnostic_coords: [...]`
appends inactive coordinates with a declared prior and `pert=None`, which `to_pert` never forwards
to the model — proven by construction and by the smoke test (16 → 15 specs, order otherwise
identical; the diagnostic coordinate absent from `Perturbation`; an unknown name refused). Threaded
through `_build_gasflux_ctx(spec_options=None)`, default `None` → unchanged. **Nothing is turned on.
No strain config changed. `f_metab` is not wired into allocation.**

### Seven-strain gate with the option OFF — PASS, with one thing explained rather than assumed

Run **in the T1 worktree** so the code under test is the code exercised: **K1 79/79, P1 60/60**,
every `rc=0`. Thirteen tracked `resolved_config.yaml` dumps then showed as modified — more than the
two stale dumps R3 cleared. §4 says treat that as a finding until explained. **Explained:** all 26
diff lines are the worktree's absolute path (`…/etcGEMs-t1/…` against `…/etcGEMs/…`), the
"3.15 absolute-path artefact" §4 already records; **not one diff line is a value**. Restored with
`git checkout -- strains/`. Byte-identical modulo path.

### The invariant proof — launched 14:01:42, single process, under the tested alarm

870 points (58 D44 + 800 red2/6800 + 12 P12). Input hashes recorded by the script:
D44 `fc4a8a5dc6dc1947f84a41ca95604f9bb6408fc3cb9b452adee7f04c5c077041`,
red2/6800 `ef1c50d10a99063a9843289d08078f9fea3781b1654c43a692ad3d1e36357c1e` (asserted against D0),
P12 as recorded in `task1_invariant.json`. First point, D44's parent: old **−17.9725**, removal
**−17.9725**, max difference **1.28e-11**, and it reproduces the saved **−17.972547016139384** —
so the 15-D unit-cube → 16-D transform round-trips and the invariant holds there.

**Budget note, written before the outcome:** 870 points × 5 solves may exceed the registered 2 h.
If the batch deadline fires, the script stops, keeps every completed row, and the run is reported
as **partial under budget** — not extended, not restarted (RIGOUR 8).

### TASK 3's physiologically diverse points — the rule, registered before any evaluation

1. **p38** — P12's best converged endpoint (`task2c_converged.csv`, key `p38(b22)`).
2. **P4's MAP** — argmax of `log_prob.npy` in `calibration_configD_NLDM_recipe_cmax120`.
3. **the red2/6800 living median** — among the 800 validated live points, those with peak
   predicted growth ≥ 50 % of the measured 2.0761 /h ("living", the P12/P13 criterion); the one
   whose `stored_logl` is the weighted median of that subset.
4. **the highest-importance-weight living sample** of P16's red2 posterior (`samples_red2.npy`,
   `logwt_red2.npy`; living by the same criterion).
5. **the weighted-median-log-L living sample** of the same posterior.
Ties, if any, broken with seed **17201**. `dTm` is 0 at all five (the P16/P17 conditioning).

### A candidate mechanism, registered before the trace so it cannot be read back from the data

`enzyme_cost.py:_costs_unfolding` ends in `denom = np.clip(rk * fN, 1e-6, 1e6)` — a hard clamp on
the per-enzyme turnover×fold product. **Any enzyme whose product crosses 1e-6 along a stencil is
clipped**, which is a kink with no physiological counterpart. TASK 3 captures, per enzyme and per
temperature at every stencil: `T > Topt_eff`, `T − Tm_shift > Tm_i` (past its melting point), and
`rk·fN ≤ 1e-6` (clipped). Whether the clip *coincides* with any of the seven axes' curvature
differences is what decides its classification; naming it now is what stops that decision being
made after the fact.

### The proof will exceed its batch budget — a second bounded batch, registered BEFORE the first stops

At 26/870 after ~7 min the proof is running at ~17 s per point (five fresh solves each), so the
full set needs ~4 h against the **2 h** registered in D0. **The first batch is not extended**: its
deadline fires, it keeps every completed row, and that is the honest outcome of the budget I set.

But the order of the audit set is D44 (58) → red2/6800 (800) → **P12 (12)**, so a stop near point
~420 would leave P12's twelve endpoints — which carry the four feasible-non-growing and the growing
examples TASK 2's table needs — untouched. **Registered now, before batch 1 stops:** a **second
batch** covering **exactly the labels batch 1 did not reach**, same tolerance 1e-6, same fresh
single-process evaluation, its **own 2 h cap** under the same alarm, results appended to a
separate CSV and merged only after both are hash-audited. This is a bounded follow-on for an
untouched remainder — not a restart of anything that failed, not a change of criterion. If batch 2
also hits its cap, the remainder is reported **UNEVALUATED**, with the count, and TASK 1's proof is
reported as partial over the stated subset.

## D2 — TASK 1's finding: (i) INTENTIONAL BY DESIGN. The sampled `f_metab` never enters configuration D, and the record says so three times over.

**The implementation.** `src/etcgem/enzyme_cost.py:600–607`, `set_allocation`, growth-law branch:

```python
if s.get("growth_law"):
    # coupled growth law: f_maint drives the split; the biosynthesis intercept
    # f_bio_0 is fixed and f_metab_0 = 1 - f_maint - f_bio_0 (conserving). The
    # measured f_metab arg is ignored (the mu-dependent law sets it via the
    # v_bio coefficients wired at build). Both caps are LINEAR in mu.
    f_bio_0 = s["f_bio_0"]
    f_metab_0 = 1.0 - fmaint - f_bio_0
    self._pool.ub = f_metab_0 * P * sig
```

`fm` (the `f_metab` argument) is read **only** by the simplex guard at `:593–596`, which raises if
`fm + fmaint > 1 + 1e-9`. With the priors' bounds `f_metab ≤ 0.45`, `f_maint ≤ 0.50`, the maximum
sum is **0.95**; the guard cannot fire. So the sampled value has **no path into the model**.

**The configuration.** `configs/experiments/gasflux_configD.yaml:17–18`:
`proteome_sectors: {enabled: true, biosynthesis_growth_law: true}` and `allocation_from_data: null`
— exactly the combination that takes `tpc.py:62–67`'s `elif pert.uses_allocation()` branch into
the growth-law branch above.

**The published description.** `reports/ecoli_tpc/report.qmd:363`:
`f_metab,0 = 1 − f_maint − f_bio,0`, with `f_metab(μ) = f_metab,0 − s·μ` (`:171–178`, `:354–364`,
`@eq-growthlaw`) — derived from growth rate, not sampled.

**The history, by commit** (`git log -S`, `git blame`):

| commit | date | what |
|---|---|---|
| `8c0914c` | 2026-07-08 | `f_metab` **enters the sampled set** — "unified param set + rich BHI operating point + provenance priors"; the *static* partition design, where `f_metab` genuinely drove the pool bound (`enzyme_cost.py:610–611`, the `else` branch, still does) |
| `922e13d` | 2026-07-09 **08:27** | the growth law added as a toggle, default OFF, with the **explicit comment that the argument is ignored** (blame confirms lines 600–606) |
| `96e64c3` | 2026-07-09 **09:17** | growth law turned **ON** for the rich fit; docstring of `_build_pm_rich` (`calibration_multi.py:1149–1153`) says the static path exists "so the fit's f_metab/f_maint drive the split" |

So the sequence is: sampled under a design where it mattered → the law that supersedes it written
50 minutes before being switched on, with its author stating the consequence → the coordinate left
in the sampled set. **(i)**, with one inaccuracy on record: `96e64c3`'s docstring is true of
`f_maint` and false of `f_metab` under the law it enables. That is a *documentation* discrepancy,
not a wiring omission — the implementation, the config and the report all agree.

**`f_maint` is NOT the same case, and the question does not carry over.** It enters on two paths:
`f_metab_0 = 1 − fmaint − f_bio_0` sets the metabolic pool bound (`:606–607`), and
`atpm.bounds = (atpm_nom_lb · fmaint / f_maint_nom · nf, …)` sets the maintenance-ATP lower bound
(`:614–618`; ATPM auto-detected, `f_maint` nominal 0.326 > 0 in `strain.yaml`). P17's report noted
its bound `[0.2, 0.5]` "cannot activate a sum-to-one constraint" — true of the *guard*, but
`f_maint` is an active parameter regardless. **It stays sampled.**

*(The invariant proof's numbers are entered in D4 when the batches land.)*

## D3 — TASK 2's measurement facts, from the record and not from the spec's illustration

- **Observable and units.** `R_O2_mg_cell_min`: mg O₂ per cell per minute, replicate-averaged per
  temperature (`load_respirometry`, `calibration_multi.py:198–220`). The model's mmol O₂ gDW⁻¹ h⁻¹
  reaches it through `o2_conv = gdw_per_cell · M(O₂) / 60 = 2.8e-13 · 32.0 / 60` (`:397`) times the
  fitted `resp_scale`. **Q1** established the chain contains `N₀` but **not** `cell_carbon_fg`.
- **Uncertainty `s`.** The **replicate SD** at each (medium, T); the code's 30 % floor applies only
  where a single replicate leaves no SD. For D NLDM (`derived_R2A_LB_current.csv`, OTU 1): **12
  temperatures × 5 replicates**, an SD at every one, so the floor **never fires** — `s` is
  measured everywhere. The spec's "5 SE" was illustrative; the measured `y/s` ranges from **2.6
  (35 °C) to 17.6 (20 °C)**.
- **Detection limit: none documented.** Neither the README, the tables, nor the P3 gate states a
  limit of detection, a blank, or a censoring rule. Every scored value is positive (min
  **1.61e-12**), none NaN. **A censored candidate cannot be derived from this record**, and T1
  will not invent a limit.
- **Can O₂ be structurally zero when growth is?** **The data say no.** At 50 °C, **three of five**
  series have `r = 1e-6` — the pipeline's *deliberate* "no measurable growth, KEPT" marker
  (README, boundary fix of 2026-09-07) — and they respire at **2.36e-12, 2.36e-12, 1.97e-12**, the
  same order as the growing series. This is the measurement-side counterpart of Q1/P13's finding
  that a non-growing model cell still respires for maintenance (O₂ 0.525–5.674 at the four
  feasible-non-growing endpoints). **A structural zero on growth does not imply one on O₂.**
- **What the model's missing predictions are, by solver status.** D44's 58 evaluations contain
  **696 solves: 638 `optimal`, 58 `infeasible`, all 58 at 15 °C; no `time_limit`, no `numeric`.**
  The tie-break never ran there (`nan`). So at D44 the missing prediction is Gurobi's own
  INFEASIBLE, category (b) on growth — subject to the retry ladder confirming it on all three
  rungs. The classification of the other audit sets requires fresh solves and waits on the batch
  order.
- **The existing term's scale, stated honestly.** The term is Normal in **log O₂** with
  `varr = (s/y)² + disc_resp² + 1.42²`. A prediction of exactly 0 has `log 0 = −∞`: **the existing
  term cannot score a zero prediction at all**, on its own scale. A "lognormal ε" is therefore not
  something the code implies — it would be a new modelling choice, which the spec forbids inventing.
- **What informed nothing here:** no living fraction, no evidence value, no posterior. TASK 2's
  inputs are the tables, the README, the code, and the saved solver statuses.
