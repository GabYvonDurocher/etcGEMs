# T3 — measure the four determinism schemes, choose on evidence, stop: decisions

_Branch `t3/determinism` from `main` at `b5b06c6` (the merge of T2's #41, base read first: `main`,
MERGEABLE CLEAN). Worktree `../etcGEMs-t3` (the primary tree's `.git/index.lock` is still held by
the sandbox VM, as in T1 and T2). RIGOUR.md governs. Started 2026-09-15 21:05. **No fit, no
sampler, no reserved seed, no core change, no option enabled.**_

## D0 — the whole measurement registered before any of it runs

### The fixed input set — `inputs.json`, sha256 `8aef2dfd9d61db83255add520e13e2ee831a9b188881da5249b01cb95900f27e`, built by `t3_inputs.py`

22 vectors: **20 inputs** and 2 E LB interleaving companions. Every θ is hashed (`sha256_theta`
in the file); the three T2 checkpoints they come from are hashed in `meta.checkpoint_sha256`.

| set | count | rule | why |
|---|---|---|---|
| (i) | 1 | run 3's checkpoint (it 9,288) live point **654** — the crash point; stored −18.4796, fresh −19.7608540096 | the point the defect is known to hit |
| (ii) | 3 | run 3's live points **791, 297, 105** — the other +1.28 points of T2's exhaustive audit | the defect's siblings |
| (iii) | 10 | the **five largest-\|offset\|** live points of run 1 (27, 427, 701, 286, 419; offsets 4.8e-3 … 7e-7) and of run 2 (462, 319, 608, 570, 149; 3.1e-6 … 1.1e-7), by index from T2's `task5_livepoints_all.json`, at full precision from the final checkpoints | span the finished runs' measured offsets, including each run's largest |
| (iv) | 5 | prior draws with **seed 17401**, in order: the first three feasible everywhere (draws 1, 2, 3; fresh log L −39.67, −248.38, −60.22) and the first two infeasible somewhere (draws 5, 12) | untouched by any sampler; two −∞ points test that the short-circuit is deterministic too |
| (v) | 1 (+2) | Parsa's E LB MAP in our E LB specs (P10 D3a's route: `task1e_reoptimise.his_theta_in_our_specs`, c_max 450, fresh log L recorded) plus two E LB prior draws with **seed 17402** as interleaving companions | the historical face case (P6 D3a: 2.498 units of jitter; basis reset returned it to the fresh value exactly) |

Spaces: (i)–(iv) are 16-D vectors in T2's validation configuration (14 physical + 2 diagnostics,
D NLDM); (v) is in the E LB spec list (a separate model, own worker, own reference). Seeds 17401–
17403 are T3 development seeds, disjoint from every earlier set; **17904–17905 stay reserved and
untouched; no reserved seed is consumed.**

### The protocol, per scheme

**N = 50 evaluations of every input in ONE persistent worker process** (a `multiprocessing.Pool(1)`
initialised exactly as T2's driver initialised its workers, `_gwinit(payload(validation=True))`),
in a **registered interleaved order**: 50 rounds, each a fresh permutation of the 19 D-NLDM inputs
by `default_rng(17403)` — never the same input twice in succession within a round, and the rounds
concatenated. The E LB input and its two companions run the same way in their own worker (3 items,
50 rounds). **The reference truth** for every input: the same θ evaluated in a **fresh process
with a fresh model instance**, twice (the second fresh value bounds fresh-vs-fresh). Recorded per
evaluation: the value at full precision, wall-clock, and the solver status per temperature.

**Scheme D deviates from N = 50, stated now:** a fresh model per evaluation costs the 6.7 s build
per call, so 20 × 50 would be ~2.5 h on its own; it is measured with **N = 5 per input**, its
determinism being what T2 already showed (three fresh instances identical to 1e-12) and its
*cost* being what this prompt needs from it.

### The four schemes

- **A. CURRENT** — the pooled path exactly as T2 ran it (`t2_target.loglike` in a persistent
  worker; warm solver; pFBA tie-break at 1e-9). The control: **it must reproduce the defect** at
  set (i)/(ii) — a max deviation of order 1 — or the instrument is invalid and the task stops.
- **B. SOLVER RESET PER CALL** — `pm.ec.model.solver.problem.reset()` (gurobipy `Model.reset()`,
  which discards the incumbent solution and basis) **before every LP solve inside the
  evaluation** — each temperature's growth solve and each tie-break solve — via a wrapper on
  `etcgem.gasflux.apply_state` and `_tiebroken_solve`, otherwise the current path. This is P6
  D3a's reset arm (`state_vs_identifiability.py:114`, which returned E LB to its fresh value) and
  P17 D2's (which did **not** remove the 0.088 event); the measurement decides which generalises.
- **C. LEXICOGRAPHIC TIE-BREAK** — Gurobi's native hierarchical objectives in ONE `optimize()`:
  objective 0 = growth (priority 2, weight +1), objective 1 = total absolute flux (priority 1,
  weight −1 under MAXIMIZE), with `ObjNRelTol` = the current `growth_tol` (1e-6) on the growth
  objective so the allowed growth degradation matches pFBA's `growth ≥ g_opt(1 − tol)` constraint.
  Implemented in the scratch module `lexi_tiebreak.py`, **measurement only, not in the core**;
  it reproduces `gasflux_log_likelihood`'s arithmetic on the solved growth/O₂. **Verified first,
  on the fresh reference,** that it returns the same growth and O₂ at every temperature of every
  input as the current pFBA (reported where it differs and by how much; a different tie-break is a
  different model).
- **D. FRESH MODEL PER EVALUATION** — `_build_gasflux_ctx` anew for every call.

### The statistic and the decision rule (not revised after the data)

Per input and scheme: **max |value − fresh reference|** over the N evaluations (the headline —
that is what corrupted run 3), the spread (max − min) across the N, and the counts exceeding
1e-9, 1e-6, 1e-3 and 1.0. Two −∞ values count as equal; a finite value against a −∞ reference is
a deviation of ∞. **A scheme is DETERMINISTIC if every input's max deviation ≤ 1e-9 across all its
evaluations; MARGINAL if ≤ 1e-6; FAILS otherwise. Among deterministic schemes the cheapest by
measured wall-clock per evaluation is recommended. If none is deterministic, nothing is
recommended and that is said plainly.** Scheme C can only be recommended if it also returned the
same vertex as pFBA at every input.

### Budgets (SIGALRM, tested `alarm.py`; a battery hitting its cap stops and is reported partial)

Reference 15 min; A, B, C **60 min each**; D 30 min; TASK 2's high-weight re-evaluation 15 min.
One battery at a time. Total ≈ 3 h.

### Also registered for TASK 2 (no run corrected, recomputed or re-run)

The 20 highest-importance-weight posterior samples of each of runs 1 and 2, re-evaluated **fresh**
(new instance), deviation from the stored `logl`; and an order-of-magnitude accumulation argument
stated with its assumptions. Candidacy only.

## D1 — the reference is bit-reproducible; scheme A reproduces the defect, so the instrument is valid

**Reference** (`battery_ref.json`, 4.7 min): every one of the 22 inputs evaluated twice, each time in
a fresh process with a fresh model instance (`Pool(1, maxtasksperchild=1)`, the worker
initialiser T2's driver used) — **fresh-vs-fresh 0.0 at all 22** (bit-identical). Two caveats,
recorded not smoothed: (1) the crash point's fresh value on this path is **−19.760854155863385**,
while T2's three in-process `build()` instances gave −19.760854009581777 — the two construction
paths differ by **1.5e-7** (the reference for the rule is the worker path, the one the runs use);
(2) T2's "exhaustive fresh audit" (`task5_livepoints_all.py`) evaluated 800 points per checkpoint
in a **persistent 16-process pool**, so its ≤ 5e-3 offsets for runs 1–2 were themselves measured
with the defect present — its four +1.28 points stand (this battery reproduces them), its small
offsets are not a clean measurement. T3's reference is.

**Scheme A — CURRENT, the control** (`battery_A.json`, 1,100 evaluations, 32.8 min, 1.77 s per
evaluation): **FAILS** — max deviation **1.815**; 16 of 22 inputs exceed 1e-9, 4 exceed 1.0:
`run3:791` +1.2802 in 2 of 50, `run3:297` +1.2800 in 1 of 50, `ELB:parsa_MAP` +1.5376 in **12 of
50** (P6 D3a's 2.498-unit face case, still there under pFBA at 1e-9), `ELB:prior17402:draw1`
+1.8153 in 3 of 50. The crash point itself (`run3:654`) did not re-inflate in this order (max
6.9e-8) — the event is history-dependent, and its siblings carried it instead. The three living
run-1/run-2 points with the largest T2 offsets sit at 1e-9 to 5e-6 here; the two −∞ draws are −∞
in all 50 (the short-circuit is deterministic). Solver statuses never varied. **The defect is
reproduced by the registered instrument at sets (ii) and (v); the task continues.**
