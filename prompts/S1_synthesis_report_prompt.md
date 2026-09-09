# Claude Code prompt — S1: the synthesis report — what the etcGEM work has established, what is missing, and what is publishable (autonomous)

Run from the project root (`.../MICROADAPT/etcGEMs`). Produces `reports/synthesis/` — a Quarto
document rendering to PDF, in the house convention, figures sourced from committed outputs BY PATH so
it regenerates when the numbers move.

**Audience: the PI and both postdocs.** Ilgaz and Parsa will read it. It contains findings about
their code and their published numbers. Write it as a shared record of where the science stands, not
as a review of anyone's work: describe what was found, say what it means, and where a defect was
introduced by our own runs SAY SO with the same prominence as one found in theirs. Several of the
sharpest findings this week came from correcting things this project itself got wrong.

**Scope: the etcGEM framework only.** Empirical work — the respirometry assays, the phylogenetics,
the manuscript's own measured claims — is IN SCOPE ONLY where it is used by or bears on the etcGEM
work (measured TPCs as calibration or validation targets, the measured meltome benchmark, measured
activation energies as comparators). Do not summarise the Candida manuscript's empirical results as
though they were ours to assess.

NOTE TO USER: launch in an auto-approving mode. No emcee, no fits. It reads the repository and
assembles. **P6 may be running** — read `strains/eciML1515/` from committed outputs, never write
there, and mark every P6-dependent number PROVISIONAL with a defined slot for the converged value.

---

```
Work AUTONOMOUSLY; commit in parts, prefixed "S1: "; maintain reports/synthesis/DECISIONS.md FROM THE
FIRST JUDGEMENT CALL. Standing rules carry over. Check exit codes explicitly, never `cmd && check`.
Branch `s1/synthesis`; do not push to `main`; end in a PR that is NOT merged.

TASK 1 - assemble the evidence base before writing a word
Every number in this document must come from a file, not from a summary of a file.
- Read every report under `reports/` and every `DECISIONS.md`, plus `docs/OPEN_ITEMS.md`,
  `docs/CANDIDA_DISCUSSION_2026-09-07.md`, `docs/CANDIDA_ETCGEM_PLAN.md`, `reports/report_status.yaml`
  and the prompt series in `prompts/`.
- Build `reports/synthesis/evidence.csv`: one row per claim the document will make, with the number,
  the file it came from, the commit that wrote that file, and whether it is CURRENT, HISTORICAL or
  PROVISIONAL-ON-P6. Every later section cites this table.
- Where two files disagree on the same quantity, record BOTH and say which is authoritative and why.
  This has happened more than once (two measured E_growth differing fourfold; two growth conventions
  differing 0 vs 0.66 at 40 C; three RQ figures now reconciled). Those disagreements are findings,
  not noise to be tidied.

TASK 2 - the narrative: what was done and what it established
Organise by what was LEARNED, not by the order the prompts ran. Suggested structure, adapt as the
material demands:
  1. Where things stood at the start: two implementations of the etcGEM idea, no shared core, one
     published method whose absolute scale was unexplained.
  2. **The merge.** Candida and E. coli brought onto one core (K1, P1); what the common framework
     now is; the gate that proves the ports are faithful.
  3. **What the models turned out to be doing.** The uncosted-shortcut findings — E. coli's O2
     sinks, the methanogen's ATP drain, C. parapsilosis's reversible maintenance, the Candidozyma
     proton circuit — and the audit blind spot on the coupling ion. Four instances, three organisms,
     one in a published reconstruction.
  4. **What the predictors turned out to be doing.** A1's validation: Seq2Tm r = -0.048 within a
     proteome against +0.762 across the tree of life; the bias non-uniform, rising ~1.06 C per degree
     of predicted Tm; the same-species noise floor from the four C. auris clades.
  5. **What sets a thermal curve in these models.** T_opt regime-determined (three constraints
     relocate it); CT_max stability-determined and insensitive to all three; the ceiling
     over-prediction decomposed into a predictor component, a residual, and an interspecies term;
     the growth envelope structurally too steep and unresponsive to configuration.
  6. **What the arithmetic of the Candida figure now is**, stated as a sequence with each step's
     cause: as published, after the core's thermal form, after the predictor correction, and what
     the ceiling criterion turned out to be (arithmetic, not a model constraint).
  7. **Sampling.** The convergence finding, applying to both families evenly, and its status.

TASK 3 - the figures
- Identify every figure ALREADY COMMITTED that this document should carry, and reference it by path.
  Do not regenerate figures and do not create new analyses.
- Where a figure is needed that does not exist, and can be made from committed tables alone (no
  refit, no solve), write a small producing script under `reports/synthesis/` and source it by path
  like everything else. Cap this at what is genuinely necessary — a summary document earns its keep
  by assembling, not by generating.
- The one figure I would like if it can be made cheaply from committed tables: **the Candida
  requirement arithmetic as a single panel** — as-published, K2, A1-corrected, with the measured
  congeneric benchmark as a reference line. If the numbers are not all in committed tables, say so
  and leave it out.
- Every figure caption names its producing script and the commit.

TASK 4 - gaps and what remains
- From `OPEN_ITEMS.md` and the reports, produce the honest state: what is blocked and on whom; what
  is ready; what is deferred and on what trigger.
- Separate three kinds of gap explicitly, because they need different responses:
    * **Measurement gaps** — things no amount of modelling fixes (no Candida meltome; no measured
      fungal ETC footprints; no per-species proteome allocation; the per-cell carbon conversion).
    * **Model gaps** — mechanisms the framework cannot express (membrane as a physical structure;
      whatever kills cells below the unfolding ceiling).
    * **Housekeeping** — under-converged chains, stale artefacts, the unexplained 10 C.
- For each, state what it would cost to close and what it would license if closed.

TASK 5 - the publication assessment: DRAFT IT, DO NOT ADJUDICATE IT
This section is for the PI to decide. Your job is to lay out the evidence FOR and AGAINST each
candidate, not to reach a verdict.
- For each candidate below, give: the claim it would make, the evidence in hand (with citations to
  `evidence.csv`), what is missing, and the strongest objection a referee would raise.
    (a) **The Candida thermal-limit paper** — what survives of the etcGEM half after this week, and
        what the defensible form of the claim now is.
    (b) **The E. coli gas-flux and overflow work** — what is established, and what depends on P6.
    (c) **The cross-organism activation-energy comparison** — READ IT FIRST
        (`reports/activation_energy/`) before assessing; it predates this work. Say plainly if the
        findings about T_opt regime-dependence bear on it.
    (d) **A methods paper on what enzyme-constrained thermal models can and cannot do** — the
        predictor validation, the four reconstruction defects, the coupling-ion audit gap, the
        T_opt/CT_max asymmetry, the convergence finding. Assess whether these cohere into one
        argument or are a list of unrelated observations. Be sceptical of your own case here.
- Mark the whole section **FOR PI JUDGEMENT** and do not write a recommendation on which to pursue.
- Do NOT inflate a negative result into a headline. Several of these are negatives; some negatives
  are valuable and some are just absent effects, and the document should distinguish them.

TASK 6 - render and record
- `reports/synthesis/synthesis.qmd` -> PDF, house conventions (fonts, CSL, header) matching the
  existing report directories. Figures by path. Verify the PDF opens, has no missing figure and no
  unresolved cross-reference; report the page count.
- Add the provenance stamp via `scripts/stamp_reports.py`.
- A short "how to update this document" section at the end: which numbers are provisional on P6,
  where they slot in, and that re-rendering after P6 lands is the intended workflow.

VERIFY (report all)
1. `evidence.csv`: row count; how many CURRENT / HISTORICAL / PROVISIONAL-ON-P6; every disagreement
   between files recorded with its resolution.
2. Any number in the document that could NOT be traced to a file — list them; there should be none.
3. The figures used, by path, with their producing scripts; anything newly generated, and why it was
   necessary.
4. TASK 4: the three gap categories, populated.
5. TASK 5: the four candidates, each with evidence for, evidence against, and the strongest referee
   objection; confirmation that no verdict was reached.
6. PDF renders; page count; stamped.
7. `git diff main --stat` — reports/synthesis/ only, plus the stamp file. Nothing under
   `strains/eciML1515/` touched.

CONSTRAINTS
- Every number comes from a file. If it cannot be traced, it does not appear.
- Scope is the etcGEM framework. Empirical work appears only where the framework uses it.
- Where a defect or error originated in this project's own runs, say so as plainly as one found in a
  postdoc's code. That even-handedness is the document's credibility.
- Mark P6-dependent numbers PROVISIONAL with a defined slot. Do not wait for P6.
- TASK 5 lays out evidence; it does not adjudicate. No recommendation on which paper to write.
- Do not generate new analyses. Assemble what exists.
- Autonomous; commit in parts: "S1: evidence base", "S1: narrative", "S1: figures", "S1: gaps",
  "S1: publication assessment (for PI judgement)", "S1: render".
```
