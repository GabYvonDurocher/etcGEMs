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

## D2 — TASK 3: the reach backwards, and its limit (written while B–D run; depends on no battery)

**One signature.** P15's run 1 crashed deterministically at iteration 11,547 (dlogz 2.168) with
dynesty's slice sampler unable to find a valid point, and its resume replayed the crash
bit-identically (P15 D3). P17 measured *"likelihood variation ~0.088"* at a low-growth seed-1
median across identical-vector repeats with *"zero canonical LP coefficient/bound/objective
differences"* (P17 D1–D2), and T2 D6 saw a single evaluation of four move by 0.028 at a deep-prior
draw. T2's run 3 crashed on a live point stored 1.28 above the value any fresh instance returns
(T2 D11), and T3's control battery reproduces +1.28 at that point's siblings and +1.54 at Parsa's
E LB θ in 12 of 50 evaluations (D1). P6 D3a had already measured the mechanism in 2026-09-09:
*"which point of that face the solver returns is set by its basis history."* These are one
phenomenon at different magnitudes: the tie-broken LP in a persistent worker returns a
solver-history-dependent vertex, so the likelihood is not a function of θ, and nested sampling —
which needs an exact ordering — either crashes when the threshold passes a point's true value or
finishes carrying inflated points.

**The limit, stated so the reach is not overstated.** P17's **analytical** controls failed with
**no LP present at all**: on the narrow-mixture target the active-region probability came out
0.084 / 0.785 / 0.231 against the exact 0.30437 (P17 D6, slices 15), so a genuine sampler weakness
exists independently of this defect, and nothing here touches that finding. What may need
revisiting is P17's attribution of its **real-path** observations — in particular the
living-group ancestry collapse (complementary group 454 live / 30 ancestors, within-group nuisance
RMS step 0.02994, correlation 0.99556; P17 D34-region entries) — which reads as sampler geometry
but is also what one would get **mechanically** if points with inflated stored log L stay above
threshold longer than they should: an inflated point is never replaced until loglstar passes its
true value, so its slice-descendants accumulate and the live set's ancestry narrows onto it.

**Stated as a hypothesis, with its test — not as a retraction of P17.** *Hypothesis:* the
ancestry concentration P17 measured on the real path is partly or wholly produced by inflated
stored likelihoods. *Test:* re-evaluate fresh (T3's reference protocol, a fresh process per
evaluation) the ancestors P17 identified as dominant in its live groups, and the live points at
the checkpoints where the collapse was measured; if the dominant ancestors carry stored values
above their fresh values by more than the registered repeatability tolerance while the
non-dominant ones do not, the hypothesis stands and P17's attribution needs a dated
qualification; if they are clean to 1e-9, the collapse is the sampler's own and P17's reading
stands unqualified. P17's numbers are not edited; a dated note in its report points here.

## D3 — TASK 1's result: only scheme D is deterministic; B makes it worse; C is a different model and is disqualified before its verdict

All four batteries completed inside their budgets (`battery_*.json`, all `complete: true`; A 1,100
evaluations in 32.8 min, B 1,100 in 53.4 min, C 1,100 in 27.2 min, D 110 in 10.5 min, C-verify 22
in 4.5 min). Every value is measured against the **fresh-process reference** of D1, which is
bit-reproducible at all 22 inputs.

### Cost, on the honest basis

The in-worker timer excludes the process spawn and the model build, which **are** scheme D. The
recommendation therefore uses each battery's own end-to-end elapsed time per evaluation:

| scheme | end-to-end s/eval | in-worker s/eval | relative to A |
|---|---:|---:|---:|
| A current | **1.79** | 1.77 | 1.00× |
| B reset per call | **2.91** | 2.90 | 1.63× |
| C lexicographic | **1.49** | 1.47 | 0.83× |
| D fresh model per evaluation | **5.70** | 1.75 | **3.19×** |

D's cost is **3.2×**, not the 4–5× T2 estimated from the 6.7 s build in isolation: the build
overlaps nothing else and the evaluation itself is unchanged.

### The table, by space (D0's set (v) is a different model and is reported separately)

| scheme | space | max deviation | inputs > 1e-9 | evaluations > 1e-9 | unresolved | verdict |
|---|---|---:|---:|---:|---:|---|
| **A** | D NLDM (19) | **1.280** | 14 | 466 / 950 | 0 | FAILS |
| A | E LB (3) | **1.815** | 2 | — | 0 | FAILS |
| **B** | D NLDM (19) | **1.578** | 15 | 448 / 950 | 0 | FAILS |
| B | E LB (3) | **23.277** | 3 | — | 0 | FAILS |
| **C** | D NLDM (19) | **0.223** | 17 | 850 / 950 | 0 | FAILS |
| C | E LB (3) | **∞** | 3 | — | **111** | FAILS |
| **D** | D NLDM (19) | **0.000** | 0 | 0 / 95 | 0 | **DETERMINISTIC** |
| D | E LB (3) | **0.000** | 0 | 0 / 15 | 0 | **DETERMINISTIC** |

**Scheme A — FAILS**, as D1 recorded; it is the control and it reproduced the defect.

**Scheme B — FAILS, and it is worse than doing nothing.** Resetting the solver before every solve
raises the maximum deviation from 1.815 to **23.277** and costs 63 % more. It also spreads the
damage: under A, 3 of 950 D-NLDM evaluations exceeded 1 unit and they sat on run 3's siblings;
under B, **13 of the 19 D-NLDM inputs** produce an order-1 deviation at least once, including the
crash point itself (1.469) and points that were clean under A (`run1:286`, `run2:570`). The
reading is mechanical and was foreseeable from P6 D3a's own wording: the reset does not remove
the **degeneracy**, it only discards the basis, so each solve re-enters a flat face from a
different starting point and returns a different vertex of it. P6 D3a saw a reset return E LB to
its fresh value *once*; P17 D2 already reported that a reset *"does not remove"* the 0.088 event.
T3 settles it: **a basis reset is not a remedy.**

**Scheme C — disqualified on the vertex check, before any determinism verdict.** D0 required that
the lexicographic objective return the same vertex as pFBA before it could be recommended. On the
fresh reference it does **not**, at any input: O₂ differs by up to **4.58** mmol gDW⁻¹ h⁻¹ on
D NLDM (`run2:149`; relative 47 %) and **8.40** on E LB (`ELB:parsa_MAP`; relative 96 %), and
growth differs by up to **2.27** /h on E LB. Every one of the 20 evaluable inputs differs in O₂
by more than 1e-9 and none matches growth to 1e-9 (the growth differences of 3e-6 to 3.7e-5 on
D NLDM are the `ObjNRelTol` slack doing what pFBA's tolerance constraint does, and are expected;
the O₂ differences are not). **Gurobi's hierarchical objective is a different tie-break, so it is
a different model**, and it also produced `numeric` statuses in **111 of its 150 E LB
evaluations** and its own max deviation of 0.223 on D NLDM. It fails twice over and is not
recommended. Whether a *correct* single-solve tie-break could be built is a separate question
this measurement does not answer.

**Scheme D — DETERMINISTIC.** Every one of the 110 evaluations returned **exactly** the reference
value: max deviation **0.0** at all 22 inputs, both spaces, including Parsa's E LB θ and the two
−∞ draws. Statuses never varied.

### The verdict by D0's registered rule, not revised

**D is the only DETERMINISTIC scheme, so D is the recommendation**, at a measured **3.2× the
current cost** (5.70 s against 1.79 s per evaluation end-to-end). A and B FAIL; C FAILS and is in
any case a different model. `task1_verdicts.json`.

### Two things the table separates, as the addendum asks

1. **The corruption attaches to the evaluation, not to θ.** Under A the crash point `run3:654` was
   *clean* (max 6.9e-8 over 50 evaluations) while its siblings `run3:791` and `run3:297` carried
   +1.280 — the same offset that crashed run 3, now on different vectors. Which θ is hit depends
   on what the worker evaluated before it, so no θ can be certified clean by a spot check.
2. **The E LB inputs are a second, larger mechanism.** Their deviations (A: 1.538 at Parsa's MAP,
   **12 of 50 evaluations above 1 unit**, and 1.815 at a prior draw; B: 23.28) sit an order of
   magnitude above D NLDM's, and E LB is exactly the configuration whose O₂ at optimal growth is a
   **face** rather than a vertex — P6 D3a measured its FVA range as [5.8, 114.5] at 37 °C and
   [0, 190] at 45–50 °C, and P10 D1 held F LB for the same reason. D NLDM's O₂ is unique at most
   temperatures, which is why its defect is mostly at 1e-8–1e-6 with rare order-1 excursions.
   **Reported separately: two magnitudes, plausibly one cause (face degeneracy) at two widths.**
   T2's runs were D NLDM; an E or F run would be far worse, which bears on 1.17.

## D4 — TASK 2: the defect explains the crash but NOT runs 1 and 2's disagreement; something else is also wrong

**The direct check** (`task2_highweight.json`, registered in D0; the first attempt failed with an
IndexError — 16-D sampled vectors passed where the 17-D expanded vector is needed — and its log is
retained as `task2_highweight_attempt1.log`). The **20 highest-importance-weight posterior samples
of each run**, re-evaluated in a fresh process with a fresh model per evaluation:

| run | max \|stored − fresh\| | > 1e-9 | > 1e-6 | > 1e-3 | weight covered by the 20 |
|---|---:|---:|---:|---:|---:|
| 1 (17901) | **2.02e-08** | 4 of 20 | 0 | 0 | 0.003 |
| 2 (17902) | **5.16e-09** | 4 of 20 | 0 | 0 | 0.004 |

**The highest-weight samples are clean.** Nothing exceeds 1e-6; the largest is 2e-8, at the
scale of the fresh-versus-fresh construction difference D1 recorded. **So the defect is not a
candidate explanation for runs 1 and 2 disagreeing** — not through their high-weight samples —
and by the prompt's own wording, *"if they are clean to 1e-9, it is not, and something else is
also wrong."* It is: they disagree in log Z by 0.34 against a combined error of 0.15, in all 14
physical medians, and in direction, with clean top-weight samples. **P17's analytical controls
already showed a sampler weakness with no LP present at all** (D2 below), and that now has to
carry the explanation for the disagreement.

**Limitation, stated rather than buried:** the top 20 samples cover only **0.3–0.4 %** of the
posterior weight (n_eff ≈ 10,400 and 7,899, so the weight is spread over thousands of samples).
The test is the one D0 registered and it is a weak one; it establishes that the *dominant* samples
are clean, not that the bulk is.

**The accumulation argument, with its assumptions.** Method: take scheme A's measured deviation
rates on the D-NLDM inputs (49.1 % of 950 evaluations above 1e-9, 6.6 % above 1e-6, 0.32 % above
1e-3 — and the 0.32 % are all above 1 unit, i.e. the distribution is bimodal: a dense 1e-8 haze
and a rare order-1 excursion) and apply them to one run's measured **≈ 221,000** evaluations.
Expected per run: **≈ 14,650** evaluations deviating above 1e-6 and **≈ 700 above one full log
unit**. Assumptions, all questionable: that this 22-input set's rates transfer to the whole
posterior path; that evaluations are independent (they are not — the corruption is history-driven,
which is why 4 of run 3's 800 live points shared one offset); and that a deviation matters only if
the point is accepted. That last one is the reason this is not a symmetric error: **42.9 % of the
deviating evaluations are inflated** (stored above true), and an inflated value is precisely the
one nested sampling keeps — an inflated live point is never replaced until the threshold passes
its *true* value. Run 3 crashed carrying 4 such points in 800. This is an order-of-magnitude
argument, **not a correction**: neither run is corrected, recomputed or re-run.
