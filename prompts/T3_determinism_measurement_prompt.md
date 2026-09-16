# Claude Code prompt — T3: measure the four determinism schemes, choose on evidence, and stop (autonomous, ~2–3 h, no fits)

Run from the project root (`.../MICROADAPT/etcGEMs`), on `../etcGEMs-venv`. **Merge PR #41 (T2)
first** — TASK 0 does it. Branch `t3/determinism` from the resulting `main`. **No nested run, no
fit, no posterior.** This prompt measures and reports; the remedy is the PI's to register.

**Read first, and treat as the authority:** `docs/RIGOUR.md`, `reports/T2_validated_posterior/`
report and DECISIONS D10–D12 (the crash, the exhaustive live-point audit, item 1.34),
`reports/P17_inactive_prior/` DECISIONS D3a (the basis-reset arm, which already made E LB reproduce
its fresh value exactly) and D1 (the jitter instrument), `docs/OPEN_ITEMS.md` 1.22 and 1.34.

**What T2 found.** Run 3 crashed on a live point stored at log L −18.480, above its threshold of
−19.163. Re-evaluated fresh on three new model instances it is **−19.7608540096 every time**: the
stored value was **1.28 units too high** and the true value is below the threshold, so no slice step
from it could succeed. Four of run 3's live points carry the same +1.28 offset — one warm-worker
evaluation and its descendants. **Runs 1 and 2 carry the same defect at ≤5×10⁻³.** No solve was
unresolved, no −∞ point was involved: the approved revision is not the cause. The cause is that the
tie-broken LP in a **persistent worker process** returns solver-state-dependent vertices, so the
likelihood is not a deterministic function of θ — which nested sampling cannot tolerate. P15's crash
had the same signature.

**Why this is measured rather than fixed.** The defect is not binary: 1.28 in one run, 5×10⁻³ in the
others. **So runs 1 and 2's disagreements may be this same defect at sub-crash scale** — log Z 0.34
apart, all 14 medians beyond 2 MC errors, unrelated eigen-directions, accumulated over ~200,000
evaluations each. If so, one fix removes the crash *and* the disagreement. Four candidate schemes
differ by an order of magnitude in cost, and choosing among them by cost or intuition is how this
project has lost time before.

NOTE TO USER: launch in an auto-approving mode. It merges one PR, runs four measurement batteries
on the same fixed inputs, and ends with a table and a recommendation. It changes no default, turns
on no option, and runs no fit.

---

```
Work AUTONOMOUSLY; commit in parts, prefixed "T3: "; maintain reports/T3_determinism/DECISIONS.md
FROM THE FIRST JUDGEMENT CALL and follow docs/RIGOUR.md throughout. Check exit codes explicitly,
never `cmd && check`. Branch from main after the merge; do not push to main; end in a PR that is
NOT merged. Every battery has an enforced alarm. No fit, no sampler, no reserved seed consumed.

TASK 0 - merge, and pre-register the whole measurement before running any of it
- Merge PR #41 server-side, reading baseRefName first. Confirm MERGED; switch; pull; branch.
- D0, committed ALONE before anything runs, registering:
  * THE FIXED INPUT SET, by hash, and why each was chosen: (i) run 3's crashing live point (stored
    -18.480, fresh -19.7608540096) - the point the defect is known to hit; (ii) the other three
    +1.28 points; (iii) ten points drawn by a registered rule from runs 1 and 2's live sets,
    spanning the range of their measured offsets including the largest; (iv) five prior draws by
    registered seed, at least two of them infeasible somewhere; (v) P17's D3a theta for E LB, the
    historical face case. State the count.
  * THE PROTOCOL per scheme: N = 50 evaluations of each input in ONE persistent worker process,
    in a registered interleaved order (never all of one input consecutively - the point is to
    provoke cross-contamination between different theta), plus the same inputs evaluated in a
    FRESH process as the reference truth. Record every value to full precision, the wall-clock
    per evaluation, and the solver status per temperature.
  * THE STATISTIC: for each input and scheme, max |value - fresh reference|, the spread across
    the 50, and the count exceeding 1e-9, 1e-6, 1e-3 and 1.0. The headline is MAX ABSOLUTE
    DEVIATION FROM THE FRESH REFERENCE, because that is what corrupted run 3.
  * THE DECISION RULE, written now and not revised: a scheme is DETERMINISTIC if every input's
    max deviation is <= 1e-9 across all 50 evaluations; MARGINAL if <= 1e-6; FAILS otherwise.
    Among deterministic schemes, recommend the cheapest by measured wall-clock. If none is
    deterministic, say so and recommend nothing.
  * The per-battery alarm and the total budget.

TASK 1 - the four schemes, same inputs, same protocol
  A. CURRENT - the pooled path exactly as T2 ran it. This is the control and it must reproduce
     the defect; if it does not, STOP and report - the instrument is not measuring the thing.
  B. SOLVER RESET PER CALL - reset the solver/basis before every likelihood evaluation. P17 D3a
     found a basis reset returned E LB to its fresh value exactly; this tests whether that
     generalises. State exactly what is reset and how.
  C. LEXICOGRAPHIC TIE-BREAK (item 1.22) - Gurobi's native lexicographic objectives: growth then
     parsimony in ONE solve, so there is no second LP to inherit a basis. Implement it in a
     scratch module for measurement only, NOT in the core. Verify first, on the fresh reference,
     that it returns the SAME vertex as the current pFBA tie-break at every input (or report
     where it differs and by how much - a different tie-break is a different model and that must
     be visible before it is recommended).
  D. FRESH MODEL PER EVALUATION - build a new model instance for every call. Guaranteed
     deterministic by T2's own evidence; measured here for its cost.
- Report the table: scheme x input, max deviation, spread, threshold counts, s per evaluation,
  and the scheme-level verdict by the registered rule.

TASK 2 - what it implies for runs 1 and 2, without re-running them
- From the audit's per-point offsets in runs 1 and 2 (<=5e-3), estimate what accumulated deviation
  of that magnitude over ~200,000 evaluations could do to log Z and to the medians. State the
  method and its assumptions plainly; this is an order-of-magnitude argument, not a correction.
- Then the direct check: take the 10-20 highest-weight posterior samples from each of runs 1 and 2,
  re-evaluate them fresh, and report the deviation of each from its stored value. If the
  highest-weight samples carry material offsets, the disagreement is plausibly this defect; if
  they are clean to 1e-9, it is not, and something else is also wrong. **Report whichever it is.**
- Do NOT recompute log Z or any median. Do NOT correct either run. This establishes whether the
  defect is a candidate explanation, nothing more.

TASK 3 - the reach backwards, stated carefully
- P15's crash, P17's 0.088 and 0.028 events, and this are the same signature. Say so, with the
  references, in one paragraph.
- Then the limit: P17's ANALYTICAL controls failed with no LP present at all (narrow-mixture
  active probability 0.084 / 0.785 / 0.231 against 0.304), so a genuine sampler weakness exists
  independently. What may need revisiting is P17's attribution of its REAL-PATH findings - in
  particular whether living-group ancestry collapse (correlation 0.995, 30 ancestors) is what you
  would get mechanically when points with inflated stored log L stay above threshold longer than
  they should. State this as a hypothesis with its test, NOT as a retraction of P17. Do not edit
  P17's numbers; a dated note in its report pointing here is the correct handling.

TASK 4 - record and stop
- reports/T3_determinism/report.md: D0's registration quoted; the four-scheme table; the verdict
  per scheme; TASK 2's implication for runs 1 and 2; TASK 3's backward reach with its limit; the
  recommendation with its measured cost, or the statement that no scheme qualified.
- docs/OPEN_ITEMS.md: 1.34 updated with the measurement and the recommendation; 1.22 restated -
  if scheme C is deterministic it is a CORRECTNESS fix, not the cost optimisation it was filed as;
  a new PI item for the remedy decision with the costs from TASK 1; R1's status unchanged (open).
- Section 4: add the hazard in its general form - "a likelihood evaluated in a persistent worker
  pool is not necessarily a deterministic function of its parameters; nested sampling cannot
  tolerate that, and the failure is intermittent, so a passing spot-check does not establish it."
- evidence.csv rows; dated note in P17's report; the 0c/RIGOUR reconciliation; stamps; PR opened,
  NOT merged. Then STOP. Do not implement the recommended scheme, do not turn anything on, do not
  launch a fit, whatever the table says.

VERIFY (report all)
1. TASK 0: #41 merged with base read; D0 committed alone with the input set by hash, the protocol,
   the statistic, the decision rule and the budgets.
2. TASK 1: the full table; confirmation scheme A reproduced the defect; for scheme C, whether it
   returns the same vertex as pFBA and where it differs; the verdict per scheme by the registered
   rule.
3. TASK 2: the accumulation estimate with its stated assumptions; the high-weight sample
   re-evaluation for both runs, with the deviations; the verdict on whether the defect is a
   candidate explanation for their disagreement.
4. TASK 3: the backward reach; the analytical-control limit; the ancestry hypothesis stated as a
   hypothesis with its test; the dated note in P17.
5. TASK 4: OPEN_ITEMS 1.34, 1.22 and the new PI item; the section-4 hazard; evidence rows; stamps;
   PR unmerged; confirmation nothing was implemented, enabled or run.
6. `git diff main --stat`: reports/T3_determinism/ (including the scratch lexicographic module),
   OPEN_ITEMS, evidence.csv, a dated line in P17's report, stamps. **Nothing under src/ or
   strains/.** No fit output.

CONSTRAINTS
- Measurement only. No core change, no default changed, no option enabled, no fit, no sampler run.
- The decision rule is written before the data and not revised after.
- Scheme A must reproduce the defect or the instrument is invalid and the task stops.
- Scheme C is verified to return the same vertex before it can be recommended; a different
  tie-break is a different model and must be visible as one.
- Runs 1 and 2 are not corrected, recomputed or re-run. TASK 2 establishes candidacy only.
- P17 is qualified by dated note, never edited.
- If no scheme is deterministic, recommend nothing and say so plainly.
- Autonomous; commit in parts: "T3: D0", "T3: the four schemes", "T3: runs 1 and 2",
  "T3: the backward reach", "T3: record".
```
