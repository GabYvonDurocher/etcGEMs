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

**Extended 2026-09-10 (P11, rows P11a–P11e) — section 7 needs rewriting, not annotating, and
the rewrite must not claim a posterior.** The sampling section still describes the convergence
problem as a sampling budget ("reaching the criterion is ~8000 steps"). The finished sequence
says something different and simpler: **the likelihood was cliffed** — discontinuous by 13–72
log-likelihood units within one posterior sd, because the respiration term scored an LP vertex
that jumps — **and no sampler can integrate that**. Three changes to the model and one to the
sampler class addressed it: a pFBA tie-break so O2 at the optimum is a function of the
parameters (P10), a variance floor at the model's own vertex granularity with a continuous
support (P10, P11), and nested sampling, which needs only the ordering of likelihood values
(P11). The surface is now demonstrably sampleable: all twelve line scans pass an absolute
5-unit rule, largest step 3.53 (row P11b).

**But the posterior is still not established, and the document must not imply it is.** Two
nested runs that both met dlogz < 0.1 disagree — log Z by 6.8 combined standard errors, and 15
of 16 posterior medians by more than two Monte-Carlo errors (row P11e) — because the smaller run
never reached the larger one's region and its stopping criterion could not tell. So [C6] and
[C8], the claims that were waiting on P6, **still cannot be filled**: they wait on two agreeing
runs at nlive ≥ 800 (OPEN_ITEMS 1.19, ≈ 20–24 h). What section 7 can now say is what the problem
actually was, that it was in the likelihood rather than the budget, and that the surface has
been fixed — with the floor quoted beside any respiration R², since it grants the model a
factor-four band on O2.

## Correction note — 2026-09-10 (P12): section 7's cause is settled, and one framing must not be written in

Extends the P8, P9/P10 and P11 notes above rather than replacing them. Not edited into
`synthesis.qmd`; to be applied at the next render. Evidence rows: **P12a–P12g**, of which
**P12b** is typed `retraction`.

| where in `synthesis.qmd` | what must change | what the evidence says |
|---|---|---|
| `{#sec-sampling}`, the whole convergence story | the arc now has an end, and it is not "sampler-limited" | The chain of causes is complete: **not a step budget** (P6), **not walker count** (P7), **not a ridge** (P8), but a **cliffed likelihood** (P9) from the respiration term at cold temperatures, **fixed** by a tie-break and a variance floor (P10/P11) — after which the surface is sampleable and a nested sampler converges. What remained open was the *posterior*, not the surface. [P12a] |
| any sentence attributing the P11 seed disagreement to **multimodality** | **must not be written.** | **RETRACTED [P12b].** θ_A and θ_B\* — the two runs' best samples — have a bottleneck barrier of **0.266**, which is noise. There is **one live basin**. The two runs explored it to different depths; the disagreement is a stopping-rule failure. P11's own conclusion that **dlogz < 0.1 is necessary and not sufficient** is unaffected and is the sentence to keep. |
| any sentence generalising **Pettersen & Almaas 2023** to our model | drop the generalisation | Their multimodality is real for Li et al.'s 2,292-parameter model. It **does not reproduce** in this 16-parameter reformulation [P12a], their FVA diagnostic **does not fire** (O₂ face 0.001–0.28 % of the pFBA value under the tie-break, [P12e]), and their **cost** finding inverts — 80 % preparation there against **92 % LP solving** here [P12g note]. Their *method* is what carries over, and it is what P12 used. |
| anywhere respiration R² or a likelihood value is quoted | add the support caveat | The respiration term's support weight **discounts** rather than bounds: it hands a near-dead model **16.7** log-likelihood units where it hands a live one ~1.2 [P12d]. A model with zero predicted growth is charged **−0.017** for respiration against a live basin's −13.549 [P12c]. Any likelihood comparison must be quoted with peak predicted growth beside it. OPEN_ITEMS 1.21. |
| anywhere `dTm` is quoted as a fitted parameter | flag it as a modelling decision, not a fit | Every converged live endpoint requires **dTm −3.07 to −4.50 K against a measured meltome**, and the **only** point in the map with dTm = 0 is a model that does not grow [P12f]. This is a failure to explain, not a nuisance parameter. OPEN_ITEMS 1.20. |

No re-render.
