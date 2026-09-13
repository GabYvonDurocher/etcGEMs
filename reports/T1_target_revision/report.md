# T1 — the target revision, prepared to its approval gates

_2026-09-13, branch `t1/target-revision` from main `e80ffd2`, in the `../etcGEMs-t1` worktree.
**Three decisions and a protocol for signature; no revised fit was run, no option turned on, no
candidate implemented, no correction applied, no parameter fixed, no prior changed.** The decision
package is `DECISION_PACKAGE.md`; this report is the evidence behind it. Sections marked ⏳ are
filled from audited outputs of batches still running when the settled sections were written._

## TASK 0a — housekeeping R3 left

One tiny PR (#39, base `main` read before merging — RIGOUR 11), merged at `e80ffd2`:

- **The archive rule** in OPEN_ITEMS §4: `codex/p17-inactive-prior` is the only ref keeping ~2.9 GB
  of P17 objects reachable; never merged, pushed or deleted; the worktree is recreatable, the
  branch is not. **RIGOUR.md rule 11**: read `baseRefName` before merging a PR you did not open.
- **The archive worktree relocated** — `git worktree move /private/tmp/etcGEMs-p17
  ../etcGEMs-p17-archive`, same APFS volume (`/dev/disk3s5`), so a rename. Verified: `git worktree
  list` shows the new path at `ef1961b`, the branch resolves to `ef1961b`, the tree is clean, the
  manifest parses to 1,905 files, the old path is gone. Item 1.28 closed.
- **Leftovers deleted, non-force, after ancestry checks**: local and origin `y2/regime-posterior`
  and `y3/tm-shift`. `r3/record` and `r3/restamp` were already absent from origin; their stale
  tracking refs pruned.
- **`../etcGEMs-work` detached at `3222b9d`**, then re-detached at current main; clean.

**A blocker recorded rather than removed:** the primary tree's `.git/index.lock` is a stale
zero-byte file held open only by the sandbox VM's file server (`com.apple.Virtualization`, pid
62662, fd `952r`); no git process exists. T1 forbids deleting a lock file, so all writes went
through the `../etcGEMs-t1` worktree, whose index is independent. The primary tree holds
uncommitted edits identical to what #39 merged; they reconcile when the lock clears.

## TASK 0b — premise, scope, registration

R3 complete: main = origin = `3222b9d` → `e80ffd2`; gates 79/79 and 60/60; R3's report present.
Archive branch local-only at `ef1961b`, worktree at the relocated path.

**Scope (D0): this run moves none of R1–R4 directly; it may clarify R2** — TASK 1 establishes what
the model *can* identify. RIGOUR rules 1–11 applied by number in D0.

**Registered before any computation:** tolerance **1e-6**; the audit set with on-disk identity —
D44's 58 evaluations (with saved per-temperature solver status), the six saved stratum states,
the 800-point red2/6800 live set (archive-only `.npz`, sha256 `ef1c50d1…`), P12's twelve
endpoints, P13's four feasible-non-growing examples; development seeds **17201–17205**, disjoint
from P17's and from the **reserved 17901–17905, untouched**; SIGALRM budgets per step; the
three-rung bounded retry ladder under which a solve failing every rung is UNRESOLVED, never zero.
D0 was committed alone (`b462c6b`).

## TASK 1 — `f_metab`: the fact, the removal, the proof

**Finding: (i) intentional by design.** The growth-law branch of `enzyme_cost.set_allocation`
(`:600–607`, written by `922e13d`, 2026-07-09 08:27) computes `f_metab,0 = 1 − f_maint − f_bio,0`
and states in its own comment that the `f_metab` argument is ignored; the only other reader is a
simplex guard that cannot fire (maximum prior sum 0.95). `gasflux_configD.yaml:17–18` selects that
branch. `report.qmd:363` publishes the derived form. `f_metab` entered the sampled set the day
before (`8c0914c`) under the static-partition design where it mattered; the law was switched on
50 minutes after being written (`96e64c3`) with a docstring true of `f_maint` and false of
`f_metab` — a documentation discrepancy, not a wiring omission. **`f_maint` is a different case
and stays sampled**: it sets the pool bound and the maintenance-ATP bound.

**The removal, prepared default OFF:** `build_gasflux_specs` accepts `remove_inactive` (drops a
named coordinate; its normalised prior integrates out to factor one) and `diagnostic_coords`
(appends inactive coordinates with a declared prior and `pert=None`, which `to_pert` provably never
forwards to the model). Threaded through `_build_gasflux_ctx(spec_options=None)`. **Gate with it
OFF, run in the worktree: K1 79/79, P1 60/60**; thirteen `resolved_config.yaml` dumps differed only
by the worktree's absolute path (§4's known artefact), not one value.

**The invariant, PROVEN.** At all **870** registered points, old target = removal-only target =
old target with `f_metab` at 0.15 / 0.28 / 0.45: **maximum difference 2.02e-08** against 1e-6,
**0 violations, 0 unresolved**, recomputed from the CSV (sha256 `1377ab9a…`) independently of the
script's summary. D44 and red2/6800 reproduce their saved log L to 3.6e-10 and 7.4e-09; P12's
twelve differ from their *saved* values by exactly P13's clamp-versus-current change (p38 2.8034,
B(b3) 1.7060) and satisfy the invariant regardless (D4).

**Nothing turned on. `f_metab` not wired. Recommendation: approve removal** — decision 1.29.

## TASK 2 — infeasibility: the observation model laid bare

**Classification by solver status (D8)** — two batches (2 h + 66.9 min), hash-audited and
recomputed (`task2_merge_audit.py`): **876 points, 10,512 solves, 9,355 STRUCTURAL_ZERO, 0
UNRESOLVED, 0 RESOLVED_ON_RETRY**; saved status reproduced 64/64. D44: `infeasible` at 15 °C on
all three rungs at every one of the 58. The six stratum states: infeasible at **all twelve
temperatures**. red2/6800: **765 of the 800** validated live points infeasible at all twelve —
P17's "765 compatible" (81.5 % of red2's weight) now given as a solver fact: log L on that set is
the growth term alone, ceiling −18.6825, above most of the **35** living points. P12: eleven
endpoints feasible everywhere, `B(b3)` infeasible 15–65 °C.

**Measurement facts (D3):** observable `R_O2_mg_cell_min`, mg O₂ cell⁻¹ min⁻¹, reached via
`o2_conv = 2.8e-13 · 32 / 60` × `resp_scale`; `s` = the **replicate SD** at every one of 12
temperatures (5 replicates each; the 30 % floor never fires); `y/s` from 2.6 to 17.6; **no
detection limit documented**; every value positive; **three no-growth series at 50 °C respire at
~2×10⁻¹²** — O₂ is not structurally zero when growth is.

**Candidates** (package §2): NORMAL on the original scale with the measured `s` and `r = 0` only
where STRUCTURAL_ZERO on growth — derivable, but `r = 0` is contradicted for O₂ by the data; the
existing log-scale term — **undefined** at a zero prediction, and a lognormal ε is not derivable
from it; CENSORED — **not derivable**. Datum-by-datum tables (`task2_datum_table.csv`, 156 rows; `task2_datum_totals.csv`)
reconciled to the code's total at all 13 points (≤ 5e-12 at D44 and the stratum, ≤ 1.65e-9 at
P12's six — three miss the registered 1e-9 by ≤ 0.65e-9, reported not re-registered). 73 positive
measurements escape scoring under the omission, 0 under NORMAL r = 0; that candidate's totals are
densities on the original scale (D44's 15 °C term is +17.54, dominated by −½ log 2π s² at
s ≈ 5e-13) and are not comparable with the log-scale term without the Jacobian — said in §2. **Nothing chosen. No posterior read.**
Decision 1.30.

## TASK 3 — the seven axes, traced ⏳

`task3_trace.json`: at D44's parent and 56 stencils, then at the five registered points; per
observation, per enzyme (above `Topt_eff`, past `Tm`, clipped at the registered
`np.clip(rk·fN, 1e-6, 1e6)`), per LP status; refinement h, h/2, h/4; classification per axis.
Nothing smoothed, no value changed. Decisions 1.31.

## TASK 4 — the protocol draft

`docs/VALIDATION_PROTOCOL_DRAFT.md`: six checks, each with statistic, DRAFT threshold, P17 source
by DECISIONS entry, and its limit; reserved seeds; what is deliberately not a threshold. Decision
1.32.

## TASK 5 — the package, and the reconciliation ⏳

`DECISION_PACKAGE.md`; OPEN_ITEMS 1.20/1.25/1.27 restated, 1.29–1.32 added, §0b restated;
evidence rows T1a ⏳. Reconciliation against §0c and RIGOUR: **none of R1–R4 moved; R2 clarified**
(one sampled coordinate shown inert by design and by proof); the old §0b sequence is qualified by
dated addition; **nothing here is a fit, no revised posterior exists, and no option is on.**
