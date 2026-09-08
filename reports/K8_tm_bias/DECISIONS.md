# K8 — decisions

Standing rules carry over. `$CANDIDAS_ROOT` is READ ONLY. Branched from `main` at **028e908**,
the K7 merge. **P4 had not landed** (D1), so `strains/eciML1515/` and `reports/ecoli_*` are read
only, never written. **No default is changed anywhere in K8.**

_Opened at the first judgement call._

---

## D0 — TASK 0: the K7 merge verified

PR #10 merged as `028e908`, branch deleted local and remote. Exit codes checked explicitly:

| check | result |
|---|---|
| Candida gate, `$CANDIDAS_ROOT` unset | **79/79 PASS, exit 0** |
| `stamp_reports.py --check` | **exit 0** |
| `transfer_candida`, `candida_B3_ngamT`, `candida_B5_respire` re-run | exit 0, no numerical output changed |
| working tree | clean |

## D1 — P4 had NOT landed

`p4/refit` at `51327b1`, **five** commits ahead of `main`, unmerged, writing under
`strains/eciML1515/outputs/` within the previous ninety minutes. *E. coli* is therefore read
from committed outputs only (TASK 4), never re-run.
