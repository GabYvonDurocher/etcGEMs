# Claude Code prompt — housekeeping: rename reports/etcgem -> reports/ecoli_tpc and document the per-deliverable report convention (on a branch, render-gated) (autonomous)

Run from the project root (`.../MICROADAPT/etcGEMs`). DOCS/PATHS-ONLY: rename the report directory
and update the live references. No code, model, analysis, or report-CONTENT changes. Do it on a
branch and gate on the report re-rendering byte-identical.

NOTE TO USER: launch in an auto-approving mode; everything on a branch, you review and merge.

WHY: the report dir is named `etcgem` (the generic method/package name), but its content is already
E. coli-specific ("...model of Escherichia coli thermal performance..."). We are about to add other
organisms (a methanogen, a cyanobacterium) and other analyses (activation-energy mechanisms), so
reports need organism/topic-specific names. Convention: reports are per-DELIVERABLE, named by
organism+topic — e.g. reports/ecoli_tpc/ (this one), reports/activation_energy/ (future, cross-
organism), reports/respiration/ (future). `strains/` is deliberately left unchanged.

---

```
Work AUTONOMOUSLY; commit in phases; print a summary. Read first: reports/etcgem/ (assemble.py uses
paths relative to __file__, so the rename needs no code change inside it — CONFIRM this), README.md,
.gitignore, and any _quarto.yml / project config in the report dir. Grep the repo for `reports/etcgem`
to enumerate references.

PHASE 0 - SAFETY BASELINE
- git checkout -b rename-report-dir.
- Build the baseline: `python reports/etcgem/assemble.py` then `quarto render` BOTH report.qmd and
  supplementary.qmd; copy the two PDFs to /tmp/baseline_*.pdf for diffing. If the baseline does not
  build, STOP and report.

PHASE 1 - RENAME
- `git mv reports/etcgem reports/ecoli_tpc` (preserves history).
- CONFIRM assemble.py still resolves (HERE=dirname(__file__), ROOT=../.., STRAIN=strains/eciML1515/
  outputs) — no edit needed since paths are relative; note it. Check for any hardcoded `reports/etcgem`
  or absolute paths INSIDE the report dir (e.g. _quarto.yml output-dir, assemble.py comments) and fix
  only if they would break the build.

PHASE 2 - UPDATE LIVE REFERENCES (only the ones that matter for using the repo)
- .gitignore: `reports/etcgem/_output/` -> `reports/ecoli_tpc/_output/`.
- README.md: update every `reports/etcgem` -> `reports/ecoli_tpc` (paths, the layout tree, the build
  commands). ALSO add a short line documenting the convention: reports are per-deliverable
  (organism+topic); the current one is reports/ecoli_tpc/, and future work will live in siblings such
  as reports/activation_energy/ (cross-organism Ea analysis) and reports/respiration/. Do NOT create
  empty placeholder dirs — just document the convention.
- Do NOT touch prompts/archive/* (historical records; leaving the old name there is correct). You may
  leave docs/RESTRUCTURE_PROPOSAL.md and docs/correspondence/* as historical too; if you update the
  proposal's tree for tidiness that is fine but optional. Do not rewrite archived provenance.

PHASE 3 - REBUILD + VERIFY (the gate)
- `python reports/ecoli_tpc/assemble.py`; `quarto render` BOTH report.qmd and supplementary.qmd from
  the new path; confirm they build with no unresolved crossrefs / missing assets.
- DIFF the rebuilt PDFs against /tmp/baseline_*.pdf (page count + spot-check). Content MUST be
  identical (this is a rename, not a content change). Report the diff result. If anything differs,
  FIX the path wiring — do not alter content.

PHASE 4 - FINISH
- Print a SUMMARY: the rename, the references updated, and the PDF-diff result (identical). Leave
  everything on the rename-report-dir branch; do NOT merge or push.

VERIFY (report all)
1. Baseline built; report + supplement rebuild byte-identical after the rename (PDF diff clean).
2. reports/ecoli_tpc/ is the only report dir; no live reference to `reports/etcgem` remains in
   .gitignore or README (archived prompts/docs intentionally untouched).
3. README documents the per-deliverable report convention (reports/ecoli_tpc + reserved
   reports/activation_energy / reports/respiration).
4. strains/ unchanged; no code changes; all on the branch, not merged/pushed.

CONSTRAINTS
- Branch only; no merge, no push. Preserve history with git mv. Rename + reference updates only; no
  content/code/model changes. The byte-identical re-render is the gate — if it can't verify, STOP.
- Autonomous; commit in parts: "reports: rename etcgem -> ecoli_tpc (E. coli-specific)",
  "docs: update README + .gitignore for reports/ecoli_tpc; document per-deliverable report convention".
```
