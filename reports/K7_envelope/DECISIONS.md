# K7 — decisions

Standing rules carry over. `$CANDIDAS_ROOT` is READ ONLY. Branched from `main` at **3147261**,
the K6 merge. **P4 had not landed** (see D1), so `strains/eciML1515/` and `reports/ecoli_*` are
never written.

_Opened at the first judgement call, as the prompt requires._

---

## D0 — TASK 0: the K6 merge verified

PR #9 merged as `3147261`, branch deleted local and remote. Exit codes checked explicitly,
never chained:

| check | result |
|---|---|
| Candida gate, `$CANDIDAS_ROOT` unset | **79/79 PASS, exit 0** |
| `stamp_reports.py --check` | **exit 0** |
| `transfer_candida`, `candida_B3_ngamT`, `candida_B5_respire` re-run | exit 0, no numerical output changed |
| working tree | clean |

## D1 — P4 had NOT landed

Checked, not assumed. `p4/refit` at `b115791`, four commits ahead of `main`, unmerged, with
files written under `strains/eciML1515/outputs/` within the previous ninety minutes. E. coli is
therefore out of bounds for the whole of K7.
