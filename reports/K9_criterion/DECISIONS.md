# K9 — decisions

Standing rules carry over. `$CANDIDAS_ROOT` is READ ONLY. Branched from `main` at **450e317**,
the K8 merge. **P4 had not landed** (D1). **No default is changed in K9.**

_Opened at the first judgement call._

---

## D0 — TASK 0: the merge verified, and it caught a regression K8 introduced

PR #11 merged as `450e317`, branch deleted local and remote.

| check | result |
|---|---|
| Candida gate, `$CANDIDAS_ROOT` unset | **79/79 PASS, exit 0** |
| `stamp_reports.py --check` | exit 0 |
| the three Candida transfer experiments re-run | exit 0, **but three `calibration.json` files changed** |

**The byte-identity check earned its keep.** K8 added a `fixed` field to the calibration record
and wrote it **unconditionally**, so every transfer run — including every run that pins nothing —
started emitting `"fixed": {}`. Every committed transfer output was therefore stale on re-run.
The gate did not catch it because the gate does not read that field.

That is precisely the **stale-at-commit** hazard `docs/OPEN_ITEMS.md` §4 lists, and K8 (my own
previous run) introduced it.

**Decided:** write `fixed` only when something is actually pinned. That restores byte-identity
for every existing output while keeping the field where it means something — the K8 overlay
still records `{"dTm": -5.43}`. Fixed in TASK 0 rather than carried, because a known-stale
artefact should not survive a single task.

## D1 — P4 had NOT landed

`p4/refit` at `a5dc618`, **eight** commits ahead of `main`, unmerged, writing under
`strains/eciML1515/outputs/` within the previous ninety minutes. *E. coli* is read from
committed outputs only.

## D2 — TASK 1: the ceiling criterion's "requirement" is arithmetic, and the prompt's headline table is wrong

**Where:** TASK 1. This is the first substantive judgement call and it gates the rest.

The prompt offers a table in which the ceiling criterion demands "~5 °C" of interspecies ΔTm
against the detection criterion's 13.57 °C, and notes that ~5 °C would sit within about threefold
of the measured congeneric 1.6 °C — "a materially different sentence". It also, correctly, asks
that this be tested before being used.

**It does not survive the test.** An arithmetic identity does not care what the model is; a model
constraint does. Recomputing the required per-species offset under five model states:

| model state | model's own CT_max spread | required-offset spread | *auris* − relatives |
|---|---|---|---|
| B3, before the K5 repair | 0.63 °C | 6.45 °C | −6.11 °C |
| B5, repaired | 1.62 °C | 6.08 °C | −5.90 °C |
| B5 + carbon cap | 1.66 °C | 6.07 °C | −5.90 °C |
| B5, ΔCp −3.0 | 1.10 °C | 6.05 °C | −5.88 °C |
| B5, ΔCp −6.0 | 2.86 °C | 6.14 °C | −5.96 °C |
| **observed thermal-limit spread** | — | **6.00 °C** | **−6.00 °C** |

The model's own ceiling spread varies **4.5-fold** across these states — the K5 repair alone moves
it from 0.63 to 1.62 °C — and the required-offset spread moves by **±3 %**, staying pinned to the
observed 6.00 °C throughout.

**Decided:** report plainly that the ceiling criterion's interspecies requirement is a
restatement of the observed thermal-limit difference, not a model-derived requirement, and
correct the prompt's table in the report and in the discussion notes **before** presenting
anything else. It must not be compared with A1's measured 1.6 °C as though the two were
commensurable.

**What survives.** The ceiling criterion remains a perfectly good statement about each species
*individually* — "this model's ceiling is 9.9 °C too high for *C. auris*" is a real model
statement. It is only the *interspecies difference* that is arithmetic, and that is precisely
the quantity Figure 4 is about.

## D3 — Synechocystis' committed ceiling is not reproducible from a strain build, so its correction is left blank

**Where:** TASK 3.

Rebuilding the phototroph from `resolve("syn6803", "syn6803_ecmodel")` gives CT_max **55.5 °C**
against the committed **45.7 °C**. Three things were checked before concluding anything:

* **Is the committed curve truncated?** No. Growth falls to 0.2 % of its peak by 50 °C and 45.70
  is a genuine 5 %-of-rmax crossing. This was worth checking, because a truncated ceiling would
  have made the committed +1.7 °C gap an artefact and materially changed §4's argument.
* **Is it the medium?** `run_p2_thermal.py` applies a light-saturated autotrophic medium. Applying
  the same does not close the difference.
* **Is it the grid?** No; the difference survives the same grid.

So the committed row depends on configuration inside that run script which a plain strain build
does not reproduce, and finding it is outside K9's scope.

**Decided:** quote the phototroph's gap from the committed table and leave its total correction
**blank** rather than guess it, and record the non-reproducibility as an open item. A number I
cannot reproduce is not a number I will decompose.

## D4 — the common term: reported as absent, because that is what the numbers say

**Where:** TASK 3.

Residuals after removing A1's measured predictor bias, where they can be computed:

| strain | Tm provenance | residual |
|---|---|---|
| *M. maripaludis* | prior | **0.05 °C** |
| *C. auris* | Seq2Tm | 4.38 °C |
| *E. coli* | measured | **5.60 °C** |
| *C. haemulonii* | Seq2Tm | 10.08 °C |
| *C. duobushaemulonii* | Seq2Tm | 10.33 °C |
| *C. parapsilosis* | Seq2Tm | 10.48 °C |

**There is no constant.** The residuals span 0.05 to 10.48 °C. Only *C. auris* (4.38) is near
*E. coli*'s 5.60; the three relatives are roughly double it and the methanogen is essentially
zero.

**Decided:** report that a common ~5–6 K term is **not** visible across strains, with the same
prominence a confirmation would have had. *E. coli*'s 5.6 K is real and remains unexplained, but
it is a one-organism observation and K8's framing of it as "a common term" is not supported by
the seven-strain data.

**The three confounds, addressed rather than mentioned:**

1. *M. maripaludis*' 0.05 °C residual is computed **at its calibrated `kcat_scale` of 7.223**. At
   the a-priori point its predicted TPC is identically zero (K2 PART C2), so it has no ceiling to
   measure. It therefore cannot serve as evidence either way, and its near-zero residual should
   not be read as a strain that escapes the effect.
2. The non-Candida strains have **higher median Tm** (55.9, 56.9 against 53.5–54.2) **and higher
   observed limits** (47, 44 against 38–44). The gap is a difference of two quantities and both
   differ, so a like-for-like comparison across organisms is weaker than it looks.
3. **The mesophile prior is built on *E. coli*'s own meltome.** So the methanogen and phototroph
   are **not independent evidence** about a term seen in *E. coli*: their Tm distribution *is*
   *E. coli*'s, transplanted. That cuts both ways — it removes them as confirmation, and it also
   removes them as refutation.
