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
