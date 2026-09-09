# `reports/synthesis/` — the synthesis report

A shared record of where the etcGEM work stands, for the PI and both postdocs. Assembled by S1
(2026-09-09) and rendered here.

## Read it

**`_output/synthesis.pdf`** — 10 pages, committed so it does not have to be reconstructed to be
read. **`evidence.csv`** is its backing table and is worth opening beside it: one row per claim
the document makes, with the value, the file it came from, the commit that last wrote that file,
and whether the claim is CURRENT, HISTORICAL or PROVISIONAL-ON-P6.

## Re-render it

```bash
quarto render reports/synthesis/synthesis.qmd --to pdf     # -> reports/synthesis/_output/synthesis.pdf
```

Full refresh, in order — only the last step is needed if nothing upstream has moved:

```bash
python reports/synthesis/build_evidence.py              # re-reads every source file's commit
python reports/synthesis/fig_requirement_arithmetic.py  # only if a Candida requirement changed
quarto render reports/synthesis/synthesis.qmd --to pdf
python scripts/stamp_reports.py                         # refresh the provenance stamp
```

`build_evidence.py` looks each source file's commit up from git rather than carrying a typed
one, so a citation cannot silently go stale.

## Why the PDF is committed here and not in every report directory

`.gitignore` excludes `reports/*/_output/`, and most report directories are regenerated on
demand. The exception in this repository is `reports/activation_energy/`, whose rendered PDFs
**are** tracked — a manuscript meant to be read and circulated is kept as an artefact rather than
as a build step. This document is that kind of deliverable, so it follows that precedent (S1b).
`synthesis.qmd`, `evidence.csv`, the figure and the build scripts remain the source of truth; the
PDF is a convenience.

## What is provisional

Three claims depend on P6, which was still running when this was written. They are listed with
their slots in the document's own final section, "How to update this document". Re-rendering
after P6 lands is the intended workflow.
