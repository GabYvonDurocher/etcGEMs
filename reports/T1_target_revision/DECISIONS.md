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

## D4 — the invariant is PROVEN at every registered point. Batch 2 was a no-op. One discrepancy explained, not refreshed.

Batch 1 finished **all 870 points in 92 min**, inside its 2 h cap — the red2/6800 set's many dead
points solve fast, so the ~17 s/point projection from D44's living stencils was pessimistic. Batch 2
(`--only-missing`) started per D1, found **0 labels not reached**, and exited; it consumed nothing.

**Audited independently of the script's own summary (RIGOUR 7):** `task1_invariant.csv`, sha256
`1377ab9a12507622fc66df523531a6189daac4759b0767d7367684ea018bbe40`, 870 rows, status `OK` × 870.
Recomputed from the five columns (old at the saved `f_metab`; old at `f_metab` = 0.15 / 0.28 /
0.45; the removal-only target):

| set | points | max spread across the five | max |old − saved| |
|---|---:|---:|---:|
| D44 baseline + stencils | 58 | | **3.6e-10** |
| red2/6800 live set | 800 | | **7.4e-09** |
| P12 converged endpoints | 12 | | 10.48 — *see below* |
| **all** | **870** | **2.02e-08** (tolerance 1e-6) | |

**0 violations, 0 unresolved.** Moving `f_metab` across its whole prior, or removing it, changes
log L by at most 2.0e-08 anywhere — solver-repeat noise, not a dependence. **The sampled `f_metab`
does not enter configuration D. Proven, not assumed.**

**The 10.48 is not a reproducibility failure and is not refreshed away.** All twelve rows with
|old − saved| > 1e-4 are P12 endpoints, and each difference is **P13's measured clamp-versus-current
change to the digit**: p38 **2.8034** (P13: −7.186 → −9.989), B(b3) **1.7060** (P13 D4's credit
1.706), worst(b5) **10.478** and big(b6) **8.10** (P13 D5's discount credits 9.15 and 8.10 plus the
mask). P12 scored its endpoints under the `current` support ramp; the strain config has been
`clamp` since P13 (item 1.21). The saved values are correct *for the likelihood that produced
them*; the fresh values are correct for the one in force; and **the invariant holds in both**,
since old = removal at every one of the twelve.

**What this licenses:** approving removal changes **no** likelihood value and **no** evidence.
**What it does not:** anything about whether the model is right — this is a statement about one
coordinate's absence from the target, nothing more.

## D5 — the classification will exceed its 2 h cap; a second bounded batch registered BEFORE it fires

Measured, not guessed: one fresh `_build_gasflux_ctx` costs **6.7 s**, and the registered ladder
rebuilds fresh on every rung, so a point with a non-optimal temperature costs three builds plus
36 solves (~1 min), a fully optimal point one build plus 12 solves (~20 s). With ~half of the 800
red2/6800 points dead, the 876-point set needs **≈ 3.5–4.5 h** against the **2 h** cap in D0. The
cap fires around **17:34** with D44 (58), the six stratum states and roughly the first 250–300
red2 points done; P12's twelve — last in the order — are not reached.

**Batch 1 is not extended.** As for the proof: a **second batch** over **exactly the labels batch 1
did not reach**, same three-rung ladder, same 60 s per-rung alarm, its **own 2 h cap**, its own CSV,
merged only after both are audited. If batch 2 also hits its cap, the remainder is reported
**UNEVALUATED with the count** and every downstream table says so on the affected rows. The
ladder itself is not changed to make it finish faster — a cheaper "fresh" would be a different
procedure from the one registered in D0.

## D6 — batch 2 audit and merge registered before its result is read; four tracked PNGs found missing from the worktree and restored from HEAD

Written at 18:18 with batch 2 at 201/322 and its CSV unread.

**The audit (RIGOUR rule 7), `task2_merge_audit.py`.** Both batch CSVs are hashed; the label sets
must be disjoint (a duplicate stops the merge); the registered set — 800 red2/6800 + 58 D44 + 6
stratum + the 12 keys of `P12_modes/task2c_converged.csv`, read from that file and not from memory
— is compared with the union, and every registered label reached by neither batch is listed
**UNEVALUATED with its count**. Every STRUCTURAL_ZERO / UNRESOLVED / RESOLVED_ON_RETRY count is
**recomputed from the three rung columns** by the rule `task2_classify.py:102–103` states, then
compared with the script's own `n_*` tallies; a disagreement is printed per label, not silenced.
The merged table is `task2_classify_all.csv`; `task2_datum_table.py` reads it when present (one
line changed, before the table is run), because the P12 points it tabulates were in batch 2's
order, not batch 1's.

**Housekeeping, recorded because the T1 rules say nothing is deleted.** `git status` at 18:14
showed four *tracked* files missing from the T1 worktree —
`strains/{_toy,eciML1515,mmaripaludis}/outputs/tpc/nominal_tpc.png` and
`strains/syn6803/outputs/tpc_syn6803_ecmodel/nominal_tpc.png`. They were present at the gate
(`task1_gate_off.log`'s status at ~14:01 lists only the thirteen `resolved_config.yaml` dumps,
D1), no git operation in the reflog touches them, no T1 script names a `.png`, and the primary
tree still has all four. The cause is not established (the tree is under OneDrive). They were
restored with `git checkout -- <four paths>` — a restore of tracked content, not a `clean` — and
each restored blob hashes identically to HEAD and to `main` (`0a7c75e4…`, `3a5b6180…`,
`22339820…`, `f1fdec55…`). The T1 branch therefore carries no deletion.

## D7 — TASK 3's classification rule, registered before `task3_trace.py` runs

Written at 18:21, batch 2 still running, no trace evaluation made.

**The quantity.** P17's D44 curvature is `k(h) = −[L(u+h·s) − 2L(u) + L(u−h·s)] / h²` with `s` the
saved per-axis scale (`plan.json`) and `h ∈ {0.02, 0.04}` in SD units; its readiness statistic is
`rel = |k(0.02) − k(0.04)| / max(1, |k(0.02)|, |k(0.04)|)` with threshold 1e-3. Reproduced from
`evaluations.json` before writing this (dTopt 4.5280/3.6011, topt_scale 3.6188/58.5956, sigma
−2.4180/−19.3044 — P17's numbers to six figures). The trace re-evaluates all 58 saved `u` fresh
and must reproduce each saved log L to **1e-6** (D44's own repeatability criterion) before anything
is decomposed; a miss is reported, not smoothed.

**Decomposition by observation.** Because `growth_term[i] + resp_term[i]` sums to the code's log L
(reconciled to 1e-9 at every evaluation), `k(h)` splits exactly into 24 per-datum curvatures
(12 temperatures × growth/respiration). The datum carrying the largest share of `k(0.02) − k(0.04)`
is named, with its share.

**Decomposition by mechanism.** Across the five stencils −0.04, −0.02, 0, +0.02, +0.04 on an axis,
per temperature: (m1) LP status; (m2) the scored mask; (m3) the count of enzymes clipped at
`rk·fN ≤ 1e-6` — the candidate D1 registered; (m4) the count above their effective Topt;
(m5) the count past their shifted Tm. A mechanism *moves* on an interval if its count differs
between adjacent stencils. D44 already established m1 and m2 do not move at the parent (audit.json:
no status or mask changes), so at D44 the live candidates are m3, m4, m5 and the one thing this
trace **cannot see**: an LP basis change with unchanged status (P9's "kink"). That blindness is
stated in the classification, not papered over.

**Refinement.** P14's instrument and rule, verbatim: one-sided steps h, h/2, h/4, h/8 with
h = 0.04 SD; *"SMOOTH if the ratio |Δ(h/2)|/|Δ(h)| lies in [0.35, 0.65] at every one of the three
halvings; JUMP if any ratio exceeds 0.80; AMBIGUOUS in between, and an ambiguous line is treated as
a JUMP."* Ratios are undefined and reported as such if |Δ(h)| < 1e-6 (evaluation jitter).

**The classes, decided by the rule and not by the outcome:**
- **IMPLEMENTATION DEFECT** — the axis reads JUMP/AMBIGUOUS, **m3 moves** on the interval that
  carries the curvature difference, and **neither m4 nor m5 moves at the same temperatures on the
  same interval**. The clip is then the only traced mechanism coinciding with the kink; the defect
  is the hard clamp, and the proposed (unapplied) correction is a smooth floor or the removal of
  the clamp with the overflow handled where it arises.
- **SUPPORTED BY PHYSIOLOGY** — (a) the axis reads SMOOTH: the curvature difference is genuine
  higher-order curvature of a smooth function, and P17's 1e-3 is a Gaussian-adequacy test that a
  smooth non-quadratic surface fails legitimately; or (b) JUMP/AMBIGUOUS with **m4 or m5 moving**
  (an enzyme crossing its effective optimum or its melting point) or m1/m2 moving, and **m3 not
  moving** on that interval.
- **UNDETERMINED** — JUMP/AMBIGUOUS with (a) no traced mechanism moving (the untraced basis change
  is then the candidate, and P9's basis-status instrument the next step), or (b) m3 and a
  physiological mechanism moving on the same interval, inseparable at this resolution.
At the five diverse points the same rule applies to each point's own stencils; the D44 verdict
and the diverse-point verdicts are reported per axis side by side, and an axis's package
classification is the D44 verdict, with disagreement across points reported as such.

## D8 — TASK 2's classification: every missing prediction in the audit set is STRUCTURAL_ZERO; not one UNRESOLVED; and 765 of the 800 validated live points are infeasible at all twelve temperatures

Batch 2 finished inside its cap (322/322, 66.9 min, no timeout). Audit (`task2_merge_audit.py`,
RIGOUR 7): batch 1 `d16e9bfd…3484d8`, batch 2 `ca86af08…e638ca`, merged `d1309afb…f600c8`;
no label in both batches; the union covers the registered 876 exactly — **0 UNEVALUATED**; every
count below recomputed from the rung columns, **0 disagreements** with the script's tallies; saved
solver status agrees with the fresh first solve at all **64 of 64** points that carry one (D44 + the
six stratum states).

**The counts.** 10,512 temperature-solves across 876 points: **9,355 STRUCTURAL_ZERO** (infeasible
on the fresh model, at tolerances 1e-12, and under dual simplex — all three rungs), **0 UNRESOLVED,
0 RESOLVED_ON_RETRY**. There is no numerical-failure class in this audit set; "unresolved" appears
in the package only as the category the ladder was built to detect and did not find. Per set:

| set | points | temps | STRUCTURAL_ZERO | where |
|---|---|---|---|---|
| D44 (parent + 56 stencils + repeat) | 58 | 696 | 58 | 15 °C at every one of the 58 |
| stratum states (2 stored × 3 seeds) | 6 | 72 | **72** | all twelve temperatures, every state |
| red2/6800 validated live | 800 | 9,600 | 9,214 | **765 points at all 12 T**; 32 at 15 °C only; 1 at two T; 2 at none |
| P12 endpoints | 12 | 144 | 11 | `B(b3)` at 15–65 °C; the other eleven feasible everywhere |

**What that says about the stratum.** P17's `stratum.json` labelled itself *"algebraic
compatibility only; not solver-status classification"* and counted **765 compatible** live points
at red2's iteration 6800 (`live_history`), carrying **81.5 %** of red2's posterior weight (53.2 % of
red1's). T1's solver-status classification now gives the same **765**, point for point, and says
what they are: parameter vectors at which the LP is **infeasible at every temperature**, so
growth is 0 everywhere, the respiration term is skipped everywhere (12 positive measurements
escape scoring at each), and log L is the growth term alone — a function of `disc_growth` only,
whose ceiling is P17's `curve_max` **−18.6825** at `disc_growth` 1.1407. Their stored log L runs
−18.7807 to −18.6825; the 35 living points (peak growth 1.40–1.53 /h) run −18.7738 to −16.4412,
so the plateau's ceiling sits *above* most living points. That is the mechanism of "the posterior
is half dead", stated as a solver fact rather than an algebraic one. **It is reported, not acted
on** — the decision it bears on is 1.30's, and §0a forbids T1 from making it.

**The six stratum rows carry two labels.** `stratum_probe.json` holds two stored states
(`red1:8285`, `red2:9051`), each perturbed under three seeds (17201–17203) to a distinct `start`;
the classify script labelled rows by `tag:stored_index`, so three rows share each label. Rows are
in seed order in every T1 file and are distinct evaluations; all six are 12/12 STRUCTURAL_ZERO, so
the collision loses nothing, and it is recorded here rather than re-run.

**Living count for TASK 3.** By D1's criterion (peak growth ≥ 50 % of 2.0761 /h) from the
classification's own recorded growth: **35 of 800**. The living median of D1's rule is drawn from
those 35; the number is stated in the trace log.
