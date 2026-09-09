# S1 — decisions

Standing rules carry over. This document assembles; it runs no model and generates no analysis
beyond one figure built from committed tables.

---

## D0 — S1 runs in its own worktree, because P6 owns the main checkout

**Where:** before TASK 1.

The repository's working tree was on branch `p6/convergence`, with P6's TASK 0 committed and its
long fits not yet run. Creating `s1/synthesis` in that tree would have switched it out from under
a session that may resume in it.

**Decided:** `git worktree add -b s1/synthesis` from `main` (`50cbffd`), and work there. Nothing
under `strains/` is written at all; every E. coli number is read from a committed output.

## D1 — P6's TASK 0 findings are cited as PROVISIONAL-ON-P6, from the branch

**Where:** TASK 1.

P6's pre-flight is committed on `p6/convergence` and is **not on `main`**. Its D3 — that the
configuration-E and -F respiration likelihood is not a function of the parameters — is a
completed, evidenced finding that materially qualifies numbers this document would otherwise
present flat.

**Decided:** cite it, name the branch in the evidence row, and mark it PROVISIONAL-ON-P6 —
provisional as to *where it is*, not as to whether it was measured. The three rows so marked have
a defined slot in §"How to update this document".

## D2 — the fold-gap figure keeps A1's arithmetic and does not recompute it

**Where:** TASK 3.

A1's PART F table gives the fold gap at three stages with a credible interval on the corrected
value. The requirement has since moved from 13.77 °C (K2) to 13.57 °C (B5, after the K5 repair),
so a naive redraw would put a new number inside A1's interval without re-deriving the interval.

**Decided:** the figure shows the requirement sequence including B5 in panel A, and A1's fold-gap
arithmetic **unchanged** in panel B, with the 13.77 °C denominators labelled. Recomputing the
interval is a re-analysis, and this document does not do those.

## D3 — the four disagreements between files are reported as findings, not resolved silently

**Where:** TASK 1, `evidence.csv` rows D1–D5.

Five quantities have more than one value in the repository. Each row records both values, the
file, and which is authoritative **with the reason**. Two of them (the two measured activation
energies; the two growth conventions) were themselves the subject of a whole prompt, and the
resolution is the finding.

## D4 — §7 lays out evidence and reaches no verdict, as instructed

**Where:** TASK 5. Marked FOR PI JUDGEMENT at its head. Each candidate carries evidence for,
evidence against, what is missing and the strongest referee objection. No recommendation on
which to pursue appears anywhere in the document, including in the summary.
