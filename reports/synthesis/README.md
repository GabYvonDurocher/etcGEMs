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

## Correction note — 2026-09-09 (P8): the sampling section is wrong twice over, and the P6 slots will not fill

Not edited into `synthesis.qmd`; to be applied at the next render. Evidence rows in
`evidence.csv`: **P1, P2** (still true as measured, re-read), **P3** (now SUPERSEDED),
**P4b** (the PCA finding), **P5b** (the branch verdict).

| where in `synthesis.qmd` | sentence as it stands | what the evidence now says |
|---|---|---|
| `{#sec-sampling}`, "Reaching the criterion is ~8000 steps, ≈40 h for all nine [P3]. This is a sampling-budget property …" | a step count reaches the criterion | **No step count does.** P6 (D6): τ grows in proportion to chain length on every one of the sixteen parameters, chain/τ pinned near 9–10, the true τ unknown and > 300. P7: 128 walkers gives 10 % and no plateau. P8: the slowness is isotropic — no ridge (PC1 16.5 % of variance, τ 110–121 on every component, [P4b]) — and the ensemble slice sampler tried in its place cannot be run at this likelihood's cost [P5b]. The family is **sampler-limited, not step-limited**; "reaching the criterion" is a decision about the model (fix the prior-determined parameters, or accept medians only), not a budget. |
| "Housekeeping — known, bounded, and costed": "Under-converged chains [P1, P2, P3] — ~40 h for all nine" | bounded and costed | not bounded by steps; replace the cost with the decision above; E/F's own block [EF1] stands |
| "What is missing, and it is load-bearing": "No chain is converged [P1, P2]" | — | still true; add: and no sampler configuration tried (40 → 128 walkers, DE moves, an ensemble slice sampler) changes that [P4b, P5b] |
| the closing summary: "a whole family of published and unpublished chains at ~9 autocorrelation times [P1, P2]" | — | still true; add "and, on the evidence of P6–P8, not fixable by sampling longer" |
| "How to update this document" slots [C6], [C8]: "P6's converged configuration-D posteriors" | they wait on compute | they wait on a decision; until it is taken, quote P4's medians with a "not converged" label (OPEN_ITEMS 1.12) |

The "What is provisional" section above — "Three claims depend on P6, which was still running" —
should read that P6 was halted (its D6) and the three claims wait on the decision in
OPEN_ITEMS 1.12, not on a run.
