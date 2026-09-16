# Claude Code prompt — H1: the calibration investigation written up, the deck brought current, the repository closed, and a handover the collaborators can work from (autonomous, ~4–6 h)

Run from the project root (`.../MICROADAPT/etcGEMs`), on `../etcGEMs-venv`. **Nothing is running.**
This is a pause-and-hand-over: no fits, no sampler, no model change, no new science. Everything here
is assembly, writing, git and one deck render.

**Read first, and treat as the authority over this prompt:** `docs/RIGOUR.md`,
`docs/HANDOVER_2026-09-13.md`, `docs/OPEN_ITEMS.md` (all of §0 and §4),
`docs/TARGET_REVISION_SPEC.md`, `docs/VALIDATION_PROTOCOL.md`, and the reports for
P16, P17, Q1, T1, T2, T3 with their DECISIONS. Where this prompt and those differ, they win;
report the difference.

**The state.** `origin/main` is `b5b06c6` (T2 merged, PR #41). One PR is open: **#42 (T3)**. The
P17 archive branch `codex/p17-inactive-prior` is local-only at `ef1961b` with its worktree at
`../etcGEMs-p17-archive` — **never merged, never pushed, never deleted**; it is the only ref
keeping ~2.9 GB of P17 artefacts reachable.

**What is being handed over, in one sentence.** A merged, gated, seven-strain framework with a
validated likelihood whose posterior is not yet reproducible, a complete and honest record of why,
and a named list of what each collaborator owns next.

NOTE TO USER: launch in an auto-approving mode. It merges one PR, writes a report, updates the
deck, writes the handover, records Parsa's 1.9 fix as a decision for you, cleans the repository and
pushes. It ends with everything on `main` and a fresh clone proving it.

---

```
Work AUTONOMOUSLY; commit in parts, prefixed "H1: "; maintain reports/H1_handover/DECISIONS.md FROM
THE FIRST JUDGEMENT CALL and follow docs/RIGOUR.md throughout. Check exit codes explicitly, never
`cmd && check`. Work on `h1/handover` from main after TASK 0. No fit, no sampler, no model or
likelihood change, no reserved seed touched.

TASK 0 - merge T3 and take stock
- Merge PR #42 server-side, reading baseRefName first. Confirm MERGED; switch to main; pull;
  branch `h1/handover`. Gates 79/79 and 60/60 with all options OFF. Report.
- Confirm the archive branch is present locally at ef1961b, not on origin, worktree at
  ../etcGEMs-p17-archive. Report; touch nothing.
- Inventory every report directory on main with one line on what it established, so TASK 1 is
  written from the record rather than from memory. State which reports are SUPERSEDED by later
  ones and which stand.

TASK 1 - the report: the calibration investigation, P16 to T3
`reports/H1_handover/calibration_investigation.md`, rendering to PDF in the house convention
(match reports/synthesis/ for fonts, CSL and header; figures sourced BY PATH from committed
outputs; every number traced to a file and a commit). This is the successor to
reports/synthesis/ for everything after it, NOT a replacement of it.

Organise by what was learned, not by the order the prompts ran:
  1. **Where it stood.** The synthesis (9 Sept) left a merged framework, medians with a
     not-converged label, and no intervals. The question was whether a posterior was reachable.
  2. **The likelihood was cliffed, not the sampler weak.** P9's line scans; the cliffs traced to
     the LP's O2 uptake jumping between vertices at cold temperatures while growth barely moves;
     P10/P11's tie-break and variance floor; the surface made sampleable by an ABSOLUTE rule after
     the relative one proved centre-dependent.
  3. **One live basin, not many.** P12's barrier map; the retraction of the multimodality reading
     and what that says about PCA clustering as a mode-finder.
  4. **A parameter that was never read.** f_metab sampled but computed from mu in the growth-law
     branch; its FLAT classification in P11/P12 was a wiring artefact; T1's invariant proof.
  5. **Infeasibility was being rewarded.** P13's clamp fixed the feasible-not-growing case and
     left the infeasible one; T1's solver-status classification; the decision to score it as zero
     likelihood; T2's measured prior-rejection rate of 16.45 % [14.9, 18.1], firing at 15 C -
     and the correction that "~96 %" was P16's live points, not the prior.
  6. **The null test, and what it did and did not show.** P17: the inactive-prior failure
     reproduced, the mechanism localised (ancestry collapse, stratum-dependent trapping, the
     60-80x width mismatch, seven curvature-sensitive axes), every within-sampler remedy
     falsified, and the gate closed NEGATIVE. Carry its two limits verbatim.
  7. **The likelihood is not a function of its parameters in a worker pool.** T3: scheme A
     reproduces the defect (max 1.815); B makes E LB worse (23.277); C is a different tie-break
     and disqualified on the vertex check regardless of determinism; D is exactly 0.000 at 3.2x
     cost. And TASK 2's inconvenient finding: the 20 highest-weight samples of runs 1 and 2
     re-evaluate clean, so **the defect does not explain their disagreement and a second cause
     remains**.
  8. **What a validated posterior would need**, from the signed protocol, and what it would cost
     at scheme D's measured rate.
Then three sections that are the point of the document:
  - **What is established** and survives all of this: the merged core and its gates; the
    mechanisms (sectors, overflow from a carbon cap, the ETC area budget); the audits of the
    published yeast model (Y1 absent and structurally impossible in GECKO; Y2's asymmetry at
    their posterior with an interval); the predictor validation; the tie-break, floor and
    support form as core options.
  - **What is not**: no reproducible posterior for any configuration; R1 open; R3 provisional;
    R4 untouched; the D/E/F/M9 programme blocked.
  - **What it would take**, with costs, as a menu rather than a plan.
Every self-correction appears with the same prominence as any other finding - there are several,
and that even-handedness is the document's credibility.

TASK 2 - the deck, brought current
The deck is at reports/ecoli_deck/ (59 pages, last updated by E6 on 13 Sept, so it predates T2
and T3 entirely). Update it; do not start again.
- Its posterior slide says a five-seed validation is running. It is not: two runs finished and
  disagree, run 3 crashed, the cause is diagnosed. Rewrite from the record.
- Add, at most, three slides: what T2 established (the revision worked - every posterior sample
  feasible, dead stratum gone - and the runs still disagree); what T3 measured (the four-scheme
  table, the vertex disqualification, D deterministic at 3.2x); and what is handed over.
- Check every slide that quotes a number against the current record and fix what has moved.
  Report each change.
- Do NOT present any of this as a failure. The framework works; the calibration is unsolved and
  its obstacle is named. Keep the existing tone and the existing limits (D44/D45 at one point;
  the toy living fractions are not targets; dTm = 0 assumes the meltome mean is exact).
- Re-render; verify it opens, every figure resolves, no overfull box, no unresolved citation;
  report the page count before and after.

TASK 3 - Parsa's 1.9 fix, assessed and put to the PI
He has sent `09_medium_constants.R` and `METHODS_carbon_conversions.md` (in the uploads folder;
copy both into reports/H1_handover/parsa_1_9/ with their hashes). Write
`reports/H1_handover/parsa_1_9_assessment.md`:
- What he did: Volkmer & Heinemann's OD invariant for N0; medium-specific cell volumes (LB 4.4,
  R2A 3.8, M9 2.2 um3); carbon density 180 fg C um-3 from three independent measurements
  (200 / 204 / 132) with the carbon fraction measured on MG1655; N_inoc = 1.8e9/V;
  carbon = 180 x V. Verify his arithmetic reproduces his table.
- **The thing that needs a decision.** His METHODS says the change does not alter the table the
  likelihood consumes. That is true of his SCRIPT (figures only) and NOT of his CONSTANTS: Q1
  established the likelihood's observable is R_O2_mg_cell_min and that N0 enters it. His N0 moves
  from a single 4e8 to per-medium 4.09e8 / 4.74e8 / 8.18e8 - **M9 by +105 %**. Quantify, from the
  committed tables, exactly how much R_O2_mg_cell_min would move per medium if the constants were
  propagated into the pipeline. State that per-medium constants are absorbable by each fit's
  resp_scale (the fits are per-medium) so R2 is protected, but resp_scale's absolute value and any
  cross-medium comparison are not - so this is a LIKELIHOOD change needing a new identifier and a
  re-gate, not a figures update.
- Two smaller points to record: cell volume varies with growth rate and growth rate varies across
  a TPC, so one volume per medium still ignores the within-curve variation (note Q1's paired-media
  test found no growth-rate imprint, so empirically small); and he proposes two routes to N0 in
  one paragraph - the OD invariant and Ilgaz's Bayesian pipeline - which needs resolving to one.
- Recommend; do NOT decide, do NOT apply anything, do NOT alter any derived table. Open the
  decision as an OPEN_ITEMS PI item.

TASK 4 - the handover document
`docs/HANDOVER.md`, superseding HANDOVER_2026-09-13.md (keep that file, mark it superseded with a
pointer). Written for a collaborator with no memory of any of this, who will open the repository
cold. Sections, in this order:
  1. **What this is and where it lives.** The framework in a paragraph; the seven strains; the
     two gates and how to run them; main's commit; what a fresh clone contains and what it does
     not (the P17 archive, and where it is).
  2. **How to work on it.** RIGOUR.md in summary with a pointer: branch off main and open a PR;
     a new mechanism is a core option default OFF, gated, turned on per strain; a changed model
     gets a new identifier; pre-register thresholds and seeds before the run and never move them
     after; retain every outcome including the adverse ones; long runs go in a detached,
     idempotent, self-auditing driver; read OPEN_ITEMS before starting.
  3. **What is established.** From TASK 1's section, condensed.
  4. **What is open**, as a numbered list with its OPEN_ITEMS reference and its OWNER by name:
     the PI's decisions (1.35 the determinism remedy, Parsa's 1.9 constants, the E/F tie-break,
     the Li-style calibration question, F-prime's port); Parsa's items (1.8 the config-F table,
     the acetate measurement, the proteome allocation above Topt); Ilgaz's items; and the ones
     that are nobody's until someone claims them.
  5. **What to do next, in order, with costs.** The determinism remedy first because everything
     else inherits it; then whether a single scheme-D run reproduces runs 1 and 2's disagreement
     (the cheap test of whether a second cause is still there); then D on M9; then the D/E/F
     comparison. State plainly that the order is a recommendation and the PI owns it.
  6. **The standing hazards**, from OPEN_ITEMS section 4, each in one line - these are the ones
     that have cost this project time and they are the most useful thing a new collaborator can
     read.
  7. **How to reproduce anything**: the null test, the gates, the stamp check, and the exact
     commands.
  8. **Who to ask about what.**

TASK 5 - close the repository
- OPEN_ITEMS: a dated §0 entry recording the pause and pointing at TASK 1's report and the
  handover; every item whose status changed in the last week brought current; the PI decision
  list assembled in one place so TASK 4's section 4 can reference it rather than duplicate it.
- reports/synthesis/: a dated note in its README saying which of its sections are superseded by
  TASK 1's report and which stand. Do NOT edit synthesis.qmd or re-render it.
- Stamps regenerated; report_status.yaml carrying an entry for every report directory.
- Merge h1/handover to main by PR, matching the house style. Then delete every merged branch,
  local and on origin, non-force, EXCEPT codex/p17-inactive-prior. Report the list before and
  after, and anything git refused.
- Push main. Report the final commit.

TASK 6 - prove it from a fresh clone
- Fresh clone of origin/main into a scratch directory outside every worktree. Confirm:
    * both gates pass (79/79, 60/60);
    * docs/HANDOVER.md, docs/RIGOUR.md, docs/OPEN_ITEMS.md, docs/VALIDATION_PROTOCOL.md,
      docs/TARGET_REVISION_SPEC.md present;
    * reports/H1_handover/ with the report PDF and the Parsa assessment;
    * reports/ecoli_deck/_output/deck.pdf at TASK 2's page count;
    * every report directory referenced by the handover exists;
    * stamps --check passes.
- Report the clone's commit and tracked size. Delete the scratch clone.
- Confirm the archive worktree and branch are untouched and that the branch is still NOT on
  origin.

VERIFY (report all)
1. TASK 0: #42 merged with base read; gates; the archive confirmed untouched; the report
   inventory with superseded/standing marked.
2. TASK 1: the report's sections; every number traced to a file and commit; the PDF path and page
   count; confirmation that self-corrections appear with equal prominence.
3. TASK 2: every slide changed, with its old and new claim; the posterior slide rewritten from
   the record; page count before and after; render clean.
4. TASK 3: his arithmetic verified or the discrepancy; the per-medium movement in
   R_O2_mg_cell_min quantified; the likelihood-change conclusion; the OPEN_ITEMS PI item;
   confirmation nothing was applied.
5. TASK 4: HANDOVER.md with all eight sections; the owner-by-name list; the old handover marked
   superseded.
6. TASK 5: OPEN_ITEMS entries; the synthesis README note; stamps; the PR merged; branches deleted
   or retained with reasons; main pushed with its commit.
7. TASK 6: the fresh clone's checks, its commit and tracked size; the archive still local-only.
8. `git diff` on main before and after H1: reports/H1_handover/, reports/ecoli_deck/,
   docs/HANDOVER.md and the superseded marker, OPEN_ITEMS, synthesis README, evidence.csv,
   report_status, stamps. **Nothing under src/, strains/ or configs/.**

CONSTRAINTS
- No fit, no sampler, no model or likelihood change, no derived table altered, no option enabled.
- Parsa's constants are assessed and recommended, never applied.
- codex/p17-inactive-prior is never merged, pushed or deleted; its worktree is never removed.
- The deck is updated, not rebuilt; its tone and its stated limits are preserved.
- Every number in the report and the deck is read from a committed file, not from this prompt.
- Self-corrections appear with the same prominence as other findings.
- Nothing is deleted until the fresh clone proves it landed.
- Autonomous; commit in parts: "H1: T3 merged and inventory", "H1: the investigation report",
  "H1: the deck", "H1: Parsa 1.9", "H1: the handover", "H1: repository closed".
```
