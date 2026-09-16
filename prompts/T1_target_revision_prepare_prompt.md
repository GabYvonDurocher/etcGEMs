# Claude Code prompt — T1: prepare the target revision to its approval gates (autonomous, ~1 day)

Run from the project root (`.../MICROADAPT/etcGEMs`), on `../etcGEMs-venv`. **R3 must be complete**
— `main` integrated, pushed, gates 79/79 and 60/60 from a fresh clone. If `docs/INTEGRATION_STATE.md`
is not on `main` or `reports/R3_integration/report.md` does not exist, STOP: the repository is not
ready. Branch `t1/target-revision` from `main`.

**Read first, in this order, and treat them as the authority over this prompt:**
`docs/HANDOVER_2026-09-13.md`, `docs/RIGOUR.md`, `docs/TARGET_REVISION_SPEC.md`,
`reports/P17_inactive_prior/report.md` and `current_gate.md`, `docs/OPEN_ITEMS.md` §0 and §4.
Where this prompt and `TARGET_REVISION_SPEC.md` differ, the spec wins; report the difference.

**What this prompt is.** P17 closed as a negative diagnostic: the inference on the current
likelihood is unreliable, the mechanism is localised (living-group trapping, ancestry collapse,
stratum-dependent proposal geometry, scale-dependent curvature on seven axes), and no sampler
change fixed it. The specification names three revisions to the *target* and requires PI approval
before any revised fit. **This prompt takes each of the three to its approval gate and stops
there with a decision package.** It launches no revised posterior fit. That is a later prompt,
after approval and after the validation protocol is signed.

**The discipline is RIGOUR.md, and it is not optional.** Every rule, threshold and seed is
committed before the data it judges. Every outcome is retained. Every completed batch is
independently audited against saved hashes before it is interpreted. Deadlines are enforced by
alarm, not written. Reserved seeds are not consumed in development. Nuisance recovery, evidence
agreement and toy passes are each necessary and none is sufficient. Scope is preserved: no change
to any biological prior, no additional fixed parameter, no penalty chosen to obtain a preferred
outcome. Where a criterion turns out wrong, correct it by an argument that predates the data and
record the correction. Record an exact blocker rather than manufacturing a decisive answer.

**Limits that survive into every summary:** D44/D45 concern one non-optimal point; the 80–87 %
toy living fractions are not biological targets; dTm = 0 assumes the meltome mean is exact.

NOTE TO USER: launch in an auto-approving mode. It reads, derives, tables, traces and drafts. Its
model solves are bounded and diagnostic (the curvature trace and the datum-by-datum table). It
ends by presenting three decisions and a draft protocol, and does not proceed past them.

---

```
Work AUTONOMOUSLY; commit in parts, prefixed "T1: "; maintain reports/T1_target_revision/
DECISIONS.md FROM THE FIRST JUDGEMENT CALL, and follow docs/RIGOUR.md in every task. Check exit
codes explicitly, never `cmd && check`. Branch `t1/target-revision` from main; do not push to
main; end in a PR that is NOT merged. Every expensive step has an enforced alarm; every batch is
one job at a time; every completed batch is hash-audited before interpretation.

TASK 0 - housekeeping R3 left, then premise and the pre-registration that governs the prompt

0a. Four pieces of housekeeping, done BEFORE branching, each as its own small commit on main
    pushed directly (they are record and branch hygiene, not science; no PR needed) - or, if
    the house convention forbids direct pushes to main, as one tiny PR merged first:
  - The archive rule, written down. Add to docs/OPEN_ITEMS.md section 4 as a standing hazard:
    "codex/p17-inactive-prior is the ONLY ref keeping ~2.9 GB of P17 objects reachable in the
    primary repository. It is local-only by decision (R3). Deleting it, or any 'clean up merged
    branches' pass that touches it, makes those objects prunable by git gc. It is never merged,
    never pushed, never deleted. Its checkout lives in the archive worktree; that worktree is
    recreatable from the branch with one command, the branch is not recreatable from anything."
    Add to docs/RIGOUR.md, under integration: "Read baseRefName before merging a PR you did not
    open (R3, PR #33)."
  - Relocate the archive worktree out of /private/tmp. R3 found com.apple.tmp_cleaner.plist
    present; the worktree has survived only on uptime. `git worktree move /private/tmp/etcGEMs-p17
    ../etcGEMs-p17-archive` (a sibling of the repository, on the same OneDrive volume as the
    object store). Verify afterwards: `git worktree list` shows the new path at ef1961b, the
    branch still resolves to ef1961b, and reports/P17_inactive_prior/closure_manifest.json is
    readable there. Record the new path in OPEN_ITEMS beside the archive rule and in
    reports/P17_inactive_prior/ARCHIVE.md on main. If the move fails for any reason, STOP and
    report; do not copy-and-delete by hand.
  - Delete the merged leftovers, non-force: locally y2/regime-posterior and y3/tm-shift; on
    origin r3/record, r3/restamp, y2/regime-posterior, y3/tm-shift. Confirm each is an ancestor
    of main before deleting it. If git refuses any, leave it and report.
  - Bring ../etcGEMs-work to the current main: it sits detached at 64393ed, four commits behind.
    `git -C ../etcGEMs-work checkout --detach origin/main` after a fetch. Confirm it is at
    3222b9d or later and clean.
  Report all four. Then `git switch main && git pull` in the primary tree (two commands, two exit
  checks) so the branch below starts from the housekept main.

0b. Premise.
- Confirm R3 complete: main's commit, both gates from the primary tree, the R3 report present.
  Confirm the archive branch codex/p17-inactive-prior exists locally at ef1961b, is not on
  origin, and its worktree is at the relocated path from 0a.
- Read the five documents named above. In D0, state which of R1-R4 this prompt can move
  (expected: none directly - it prepares; it may clarify R2) and quote RIGOUR.md's rules you
  will apply by number.
- Register, before any computation: the repeatability tolerance for old-versus-new likelihood
  comparisons (the spec's 1e-6); the set of archived audit points every comparison will use
  (D44's baseline and stencils, the saved stratum states, the 800-point red2/6800 set, P12's
  twelve converged endpoints); the seeds for any new evaluation; the per-step alarm budgets.
  Commit D0 alone before anything else runs.

TASK 1 - f_metab: establish the fact, prepare the removal, present the decision
The spec's item 1. The decision is the PI's; this task supplies the evidence and prepares both
outcomes so approval is one step.
- Establish from the code and its history whether sampled f_metab is unused in configuration D
  BY DESIGN. Read enzyme_cost.set_allocation and the growth-law branch; read report.qmd's
  description of the growth-law mode (f_metab(mu) = f_metab,0 - s*mu, computed from growth rate,
  not sampled); read git log/blame for when f_metab entered the sampled set and whether any
  commit intended it to be read. Report the finding with file/line and commit references. State
  plainly which of these it is: (i) intentionally computed from mu in growth-law mode, so the
  sampled coordinate was never meant to enter; (ii) a wiring omission that was meant to enter;
  (iii) cannot be determined from the record.
- Also check f_maint and the simplex guard: is f_maint likewise unused, or does it enter the
  maintenance term? The spec's item 1 is about f_metab; report whether the same question applies
  to f_maint, with evidence, and do not assume the answer carries over.
- PREPARE the removal as a core option, default OFF: production calibration without sampled
  f_metab (and f_maint if the same finding applies), the independent prior integrated
  analytically (factor one). Retain a dedicated diagnostic-coordinate mechanism - an appended
  inactive coordinate with a declared prior, entering nothing - for validation runs only.
- PROVE the algebraic invariant the spec states: at every registered archived audit point, the
  old target and the removal-only target give the same log L within 1e-6. Report the count and
  the maximum difference. STOP on any violation: that would mean f_metab does enter somewhere.
- Seven-strain gate with the option OFF: 79/79, byte-identical. Report.
- DO NOT turn the option on for eciML1515. DO NOT wire f_metab into allocation - the spec is
  explicit that this is a separate biological hypothesis needing its own approval and identifier.
- Present, in the decision package: the finding (i)/(ii)/(iii) with evidence; the prepared
  removal with its invariant proof; the recommendation; and what turning it on would change
  (expected: nothing numerically, one fewer sampled dimension, a diagnostic coordinate available
  for validation).

TASK 2 - infeasibility: derive the observation model from the data, build the table, present
the options
The spec's item 2. This is the one where the PI must choose from the measurement process, and
the task's job is to lay the process bare so the choice can be made on it.
- First, the classification the spec requires, at every registered archived point and every
  saved infeasible example: for each measured observation, is the model's missing prediction
  (a) an UNRESOLVED NUMERICAL SOLVE - solver status not optimal, tolerance failure, timeout - or
  (b) a STRUCTURAL ZERO - the LP is genuinely infeasible under valid constraints (no flux
  distribution exists that satisfies them)? Read the solver status codes, not the NaN. Build
  the registered bounded retry procedure for (a): fresh model, tightened tolerance, alternative
  method, each with an alarm; a point that fails all retries is UNRESOLVED and is reported as
  such, never treated as zero. Report counts of (a) and (b) across the audit set, and confirm
  what fraction of the -18.68 stratum is (b).
- Second, the measurement side. From strains/eciML1515/respirometry/ - the replicate tables,
  otu/derived files, and the README - establish for the respiration observable the model
  actually scores (R_O2_mg_cell_min per Q1): its units; its replicate-derived uncertainty s per
  (medium, temperature); whether any observation is at or below a detection limit, and what the
  limit is; and whether the observable can be zero (a non-growing cell still respires for
  maintenance - Q1 and P13 established this - so a structural zero on GROWTH does not imply a
  structural zero on O2; say what the data show).
- Third, derive candidate observation models for a structural-zero state, each from the
  measurement process and each with its exact per-observation contribution written out:
    * Normal on the original scale with the replicate s, prediction r=0 where structurally
      justified - the spec's illustration, with s now the MEASURED value, not 5 SE by fiat;
    * a censored contribution where the measurement is detection-limited, using the measured
      limit;
    * whatever the actual scale of the existing respiration term implies, stated honestly
      (the spec warns that a lognormal epsilon is not justified merely because the code logs
      respiration - address that directly).
  For each candidate, and for the current omission, build the DATUM-BY-DATUM TABLE the spec
  requires: measured value, uncertainty, detection status, solver classification, predicted
  value, old contribution, new contribution - at the D44 baseline, at every saved infeasible
  example, at the saved feasible-non-growing examples (Q1's four, with O2 0.525-5.674), and at
  growing examples. Reconcile the columns to the total log L at each point.
- Show what each candidate does to the -18.68 stratum's log L, as arithmetic on the table -
  and state, as the spec does, that where a stratum point's solves are UNRESOLVED its new total
  is undefined pending resolution, not a number.
- Demonstrate that under every candidate no positive measurement escapes scoring because its
  prediction is missing. That is the property the current code lacks.
- DO NOT choose. DO NOT implement any candidate as a production option. DO NOT look at any
  posterior. Present the candidates with their tables, their derivations, their external
  uncertainty provenance, and their consequences at the saved points, and STOP for the PI to
  choose from the measurement process. Record in DECISIONS that no living fraction, evidence
  value or posterior appearance informed anything in this task.

TASK 3 - the seven curvature-sensitive axes: trace, do not smooth
The spec's item 3. Trace-only; new log L equals old log L at every point by construction.
- At D44's saved parent and stencils first: for each of dTopt, topt_scale, dCp_scale, tm_scale,
  kcat_scale, sigma, clearance_mult, at each stencil offset, capture and save: every
  observation's individual contribution; the enzyme thermal-response state (which enzymes are
  above Topt, above Tm, clipped, denatured); the proteome and membrane constraint residuals;
  the nutrient/clearance state; the maintenance requirement; the LP's binding constraint set
  and basis or active-set information where the solver exposes it; solver tolerances and
  whether the solve was warm or fresh; hashes of every input and output.
- Decompose each axis's curvature difference (the spec quotes them: topt_scale 0.938,
  sigma 0.875, tm_scale 0.574, dCp_scale 0.300, kcat_scale 0.279, dTopt 0.205,
  clearance_mult 0.102) by observation and by mechanism: which temperatures carry it, and
  whether it coincides with a change in the binding constraint set, a physiological switch
  (an enzyme crossing Topt or Tm, a clipping threshold), or neither.
- Then a separately registered set of physiologically diverse points - register them in
  DECISIONS before evaluating: at least p38 (P12's best), P4's MAP, the red2/6800 median
  living point, and two points chosen by rule from the living region of P16's posterior
  (state the rule). Repeat the trace at each. Report whether the same seven axes carry the
  scale-dependence everywhere, or whether it is specific to D44's parent.
- Compare successive stencil refinements (P14's instrument) without equating high smooth
  curvature to a cliff - the spec is explicit on this.
- Classify each axis's scale-dependence as: SUPPORTED BY PHYSIOLOGY (a real switch the model
  should have); IMPLEMENTATION DEFECT (a discontinuity with no physiological counterpart -
  clipping applied inconsistently, a tolerance interacting with a threshold, warm-state
  dependence); or UNDETERMINED. For anything classified as a defect, describe it with the
  evidence and what a correction would be - and DO NOT implement it. The spec requires separate
  approval for any changed value.
- Retain every adverse example.

TASK 4 - draft the validation protocol the spec requires, with calibrated thresholds
The spec freezes the required checks and says a signed follow-up protocol must supply the
calibrated quantitative thresholds before any revised run. Draft that protocol as
docs/VALIDATION_PROTOCOL_DRAFT.md for the PI to sign. It covers, for the revised target once
approved:
  (a) inactive-coordinate CDF recovery against its exact independent prior;
  (b) appended Beta(3,1) recovery judged on b^3, with the wrong-Uniform positive contrast;
  (c) consistency of all active distributions and covariance directions across independent
      initialisations;
  (d) preregistered region occupancy with ancestry-aware uncertainty;
  (e) feasibility-aware posterior predictive checks at every observed temperature, including
      the unresolved-evaluation rate;
  (f) evidence and final-live-point reconstruction with independent hash audits.
For each: the exact statistic; the threshold; HOW THE THRESHOLD WAS CALIBRATED - from P17's
controls where they apply (the D25 positive-control KS ranges 0.009-0.033 correct against
0.38-0.42 wrong; D40/D43's region-mass recovery to within ~0.02; the evidence-error range
+0.07 to +0.41 that must NOT be treated as calibrated), stated as the calibration source and its
limits; the seeds reserved; the budget and alarm; and the stopping rule if it fails. State what
is deliberately NOT a threshold: no living-fraction target, no IID KS p-values on nested
samples, weight-ESS not independent N. Mark every threshold as DRAFT pending signature.

TASK 5 - the decision package, and stop
- reports/T1_target_revision/DECISION_PACKAGE.md, for the PI, in this order:
    1. f_metab: the finding, the evidence, the prepared removal and its invariant proof, the
       recommendation. ONE decision: approve removal / approve wiring as a new hypothesis /
       neither.
    2. Infeasibility: the classification counts, the measurement facts (units, s, detection
       limits, whether O2 can be structurally zero), the candidate observation models with
       their datum-by-datum tables and stratum consequences. ONE decision: which candidate, or
       none, from the measurement process.
    3. Curvature: the per-axis classification with evidence; anything labelled a defect with
       its proposed correction. ONE decision per defect: approve correction / retain as is.
    4. The validation protocol draft, for signature.
    5. What launches after approval: the revised-target implementation as core options default
       OFF, gated, the invariant and datum tables re-verified, then the protocol's runs on
       reserved seeds. Cost it from P16's measured rates.
- Update docs/OPEN_ITEMS.md: 0b's sequence restated with T1 done and the four decisions as PI
  items with numbers; 1.20 and 1.25 restated; the curvature findings as new items.
- reports/synthesis/evidence.csv: rows for the f_metab finding, the infeasibility
  classification counts, and the curvature classification. No re-render.
- Reconcile against 0c and RIGOUR.md in the report's closing section: which of R1-R4 moved
  (expected: none; R2 clarified), what is retracted or qualified, what this does NOT license -
  in particular that no revised posterior exists and nothing here is a fit.
- Stamps. PR opened, NOT merged. Then STOP. Do not proceed to implementation of any candidate,
  do not launch any fit, whatever the findings suggest.

VERIFY (report all)
0. TASK 0a: the archive rule in OPEN_ITEMS section 4 and the baseRefName rule in RIGOUR.md;
   the worktree's new path with `git worktree list` output and the branch still at ef1961b;
   the six leftover branches deleted (or which git refused and why); etcGEMs-work detached at
   current main; main pulled before branching.
1. TASK 0b: R3 complete; archive branch present, local-only, at the relocated path; D0
   committed alone with the registered tolerance, audit set, seeds and budgets.
2. TASK 1: the finding (i)/(ii)/(iii) with file/line/commit; f_maint's status; the prepared
   option default OFF; the invariant proven at every audit point with the maximum difference;
   gate 79/79 OFF; confirmation nothing is ON and nothing is wired.
3. TASK 2: (a)/(b) counts with the stratum's fraction; the retry procedure and how many
   resolved; the measurement facts with provenance; each candidate's derivation and its
   datum-by-datum table reconciled to totals at every registered point; the no-escape
   demonstration; confirmation nothing was chosen, implemented or posterior-inspected.
4. TASK 3: the per-axis, per-observation, per-mechanism decomposition at D44's parent; the
   registered diverse points and the same at each; the refinement comparison; the
   classification per axis with evidence; adverse examples retained; confirmation no value
   changed.
5. TASK 4: the protocol draft with every threshold, its calibration source and its limits;
   what is deliberately not a threshold; reserved seeds.
6. TASK 5: the decision package with its four decisions and the costed next step; OPEN_ITEMS;
   evidence rows; the 0c/RIGOUR reconciliation; stamps; PR unmerged.
7. `git diff main --stat`: reports/T1_target_revision/, src/etcgem (one option, default OFF,
   plus a diagnostic-coordinate mechanism), docs/VALIDATION_PROTOCOL_DRAFT.md, OPEN_ITEMS,
   evidence.csv, stamps. No strain config changed. No prior changed. No fit output.

CONSTRAINTS
- TARGET_REVISION_SPEC.md and RIGOUR.md govern; this prompt yields to them.
- codex/p17-inactive-prior is never merged, pushed or deleted. Its worktree is MOVED, never
  removed. A failed move stops the task.
- No revised posterior fit. No candidate implemented as production. No option turned ON. No
  parameter fixed. No prior changed. No penalty or treatment chosen by outcome.
- Every comparison is against registered archived points with a registered tolerance.
- Unresolved solves are reported as unresolved, never as zero.
- Curvature is traced, never smoothed; a defect is described and its correction proposed,
  never applied.
- Every threshold in the protocol draft names its calibration source and is marked DRAFT.
- The prompt ends at the decision package. Whatever the findings, it does not continue.
- Autonomous; commit in parts: "T1: D0", "T1: f_metab", "T1: infeasibility", "T1: curvature",
  "T1: protocol draft", "T1: decision package".
```
