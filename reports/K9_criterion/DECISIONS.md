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
