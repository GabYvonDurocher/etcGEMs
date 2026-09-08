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

## D2 — TASK 1 is answered by TRACING, and the trace is what makes the number safe

**Where:** TASK 1.

The worry was that Figure 4's requirement might be convention-dependent, because at 40 °C —
the temperature its counterfactual interrogates — *C. haemulonii* grows at 0.000 h⁻¹ under one
measured convention and 0.66 under the other.

Following the code rather than reasoning about it removes the worry before any number is
computed. `transfer.required_separation` takes `scale` as a **scalar** and makes **zero** calls
to `load_measured_tpc`. **The predicted strain's own measured curve never enters the
counterfactual.** The single measured input is the growth scale, and under `peak_match` that is
`measured.max() / predicted.max()` on the **calibration** strain — so only the PEAK of the
*C. auris* curve is used, at 36 °C, where *C. auris* is fully alive under either convention.

**Decided:** report the trace first and the numbers second, because the numbers are only
reassuring if one knows why they must be.

## D3 — the recommendation is the zeros convention, and it is a recommendation, not a change

**Where:** TASK 1.

For a **detection-threshold** counterfactual the zeros convention is the right one, and not
merely because it is what the repository already uses. The question asked is whether a strain
falls below a detection floor — a statement about the population in the well. A survivors-only
curve conditions on being alive, so it cannot represent death at all: under it "below detection"
is unreachable by construction, and the counterfactual would be asking a question its own data
had defined away.

That the two happen to agree here is a separate and lucky fact. **No default is changed**;
the recommendation is recorded and `strain.yaml` is untouched.
