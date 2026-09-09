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

**Extended 2026-09-09 (P9), evidence row P6b.** The sampling section must also say WHY no
sampler mixes: the configuration-D log-likelihood is not smooth. Line scans through the MAP
(fresh model per evaluation) find a piecewise-smooth surface — exact parabolas between cliffs
of 13–72 log-likelihood units within one posterior sd, unchanged by solver tolerances or
method — each cliff carried by the respiration term at one cold temperature where the LP's
O2 uptake switches vertex. "Reaching the criterion" is therefore not a sampling question at
all; it is a decision about the respiration likelihood (OPEN_ITEMS 1.15), and the sentence
about ~8000 steps should be replaced by that statement. [C6] and [C8] wait on the same decision.

**Extended 2026-09-09 (P10), evidence rows P7b–P8b (P9b–P10b follow).** Any sentence quoting an
E- or F-configuration **respiration** R² from P3's gate should say the value was one arbitrary
point of an LP face; under the pfba tie-break at Parsa's θ the E LB respiration R² is 0.7749
(was 0.8014), the others move by < 0.001, and every growth R² is unchanged to four decimals
(`reports/P10_respiration_likelihood/task4_regate.csv`; the restated criterion is in
`reports/P3_gate/README.md`). F LB's respiration R² carries the caveat that its tie-break is not
exact. The respiration likelihood itself now has a variance floor and a continuous support for
eciML1515; the D-configuration numbers P4 reports were fitted under the old term.

**Extended 2026-09-09 (P10, rows P9b–P10b).** Section 7 should now say: the respiration term
was scoring a quantity the model does not determine continuously; with a tie-break, a variance
floor at the model's own granularity and a continuous support the cliffs fall from 13–72
log-likelihood units to single digits, and the surface is still not smooth by P9's criterion
(one vertex jump above the floor, and kinks in the growth term of 1–3 units), so no chain has
been sampled under the new term and the medians-only reading stands.
