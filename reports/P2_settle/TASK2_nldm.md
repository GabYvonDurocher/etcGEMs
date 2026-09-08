# P2 TASK 2 — NLDM under recipe ceilings

**PROVISIONAL, pending Parsa's confirmation.**

P1 established that his committed NLDM numbers were produced with a **blanket** medium — every
component open at one generous bound — while his own later code applies **recipe-proportional**
uptake ceilings (`ub_i = clearance × C_i`), and that he never re-ran: his `gasflux_C60.csv` is
dated 2026-09-01 18:04 and the file supplying its `build_pm` 2026-09-04 09:52.

This task takes the **recipe as canonical**: it is the more careful construction, it post-dates
his CSV, and it is what his committed code does. The blanket result is kept as a **labelled
sensitivity** (`NLDM_blanket` in `strains/eciML1515/gas_exchange.yaml`) so his numbers stay
reproducible — which is the only reason it exists.

Reproduce with `python reports/P2_settle/task2_nldm.py`; numbers in `task2_nldm_table.csv`.

## 1. Is the 1.2 % fully explained by the medium? — Yes, to machine precision

r_max at the NLDM optimum:

| configuration | Parsa | blanket (his medium) | rel. difference | recipe (canonical) | rel. difference |
|---|---|---|---|---|---|
| **B** (where the 1.2 % was seen) | 0.965755 | 0.965755 | **2.1 × 10⁻¹⁵** | 0.954407 | 1.18 × 10⁻² |
| A | 2.096173 | 2.095422 | 3.6 × 10⁻⁴ | 1.887489 | 9.96 × 10⁻² |
| C | 2.265768 | 2.264886 | 3.9 × 10⁻⁴ | 1.911021 | 1.57 × 10⁻¹ |

For configuration B — the run in which the 1.2 % discrepancy was observed — the medium accounts
for **all** of it: with his medium the port reproduces his number to **2 × 10⁻¹⁵**, which is
machine precision, and every other quantity at that optimum likewise (O₂ 2.0 × 10⁻¹⁵, CO₂
1.6 × 10⁻¹⁵, RQ 4.9 × 10⁻¹⁶). There is nothing left over.

**On the residual in A and C.** Both sit at ≤ 5.9 × 10⁻⁴ against his blanket-medium numbers.
That is not a residual of *this* task: it is the repository-wide residual P1 already isolated
and attributed by demonstration — his own code at his own fork point (`8c2c30f`, run in a
scratch worktree) produces the port's numbers to the last digit, so no change here can be
responsible, and it tracks *when he ran things* (his 2026-09-01 configuration-B run agrees to
2 × 10⁻¹⁵; his 2026-07-10 and 2026-07-14 runs sit at ~4 × 10⁻⁴), which points at his solver
build. It is four orders of magnitude below the precision his report quotes, and it is reported
here rather than stopped on because it was explained before this task began
(`reports/P1_parsa_port/gate.md` §2).

## 2. What moves when the medium becomes the recipe

Everything at the NLDM optimum. The recipe caps each carbon component at its own concentration,
so NLDM stops behaving like an unlimited rich medium:

| configuration | quantity | blanket | recipe | change |
|---|---|---|---|---|
| **A** | T_opt | 39.0 °C | 39.0 °C | — |
| | r_max | 2.0954 | 1.8875 | **−9.9 %** |
| | O₂ uptake | 89.91 | 35.39 | **−60.6 %** |
| | CO₂ release | 183.08 | 38.29 | **−79.1 %** |
| | acetate | 0 | **25.14** | overflow appears |
| | RQ | 2.036 | 1.082 | **−46.9 %** |
| **B** | T_opt | 34.5 °C | **32.5 °C** | **−2.0 °C** |
| | r_max | 0.9658 | 0.9544 | −1.2 % |
| | O₂ uptake | 22.69 | 22.45 | −1.1 % |
| | CO₂ release | 20.36 | 20.83 | +2.3 % |
| | RQ | 0.8974 | 0.9277 | +3.4 % |
| **C** | T_opt | 38.5 °C | 39.0 °C | +0.5 °C |
| | r_max | 2.2649 | 1.9110 | **−15.6 %** |
| | O₂ uptake | 31.39 | 36.58 | +16.5 % |
| | CO₂ release | 231.50 | 38.21 | **−83.5 %** |
| | acetate | 31.60 | 24.99 | −20.9 % |
| | RQ | **7.375** | **1.044** | **−85.8 %** |

## 3. One consequence that changes what a configuration shows, reported not adjudicated

His report says of configuration C that "because no carbon cap is imposed the RQ is not forced
toward 1 and is reported as-is (e.g. NLDM RQ ≈ 7–9, glucose RQ ≈ 0) — the acetate branch is
pinned, the gas exchange is not made respiratory."

**Under recipe ceilings the NLDM RQ is 1.04, not 7.4.** The high RQ was a property of the
blanket medium — unlimited carbon availability — and not of the absent carbon cap. On the
canonical medium, configuration C's NLDM gas exchange *is* near-respiratory without any cap.
The glucose half of his statement is unaffected (RQ ≈ 0.2 there, carbon-limited by the single
substrate either way).

Configuration A shows the same thing from the other side: on the blanket medium it is
non-overflowing with RQ 2.0; on the recipe medium carbon limitation makes acetate overflow
appear (25.1 mmol gDW⁻¹ h⁻¹) and RQ falls to 1.08.

**Not adjudicated here:** whether the NLDM recipe's clearance (5.0 L gDW⁻¹ h⁻¹) is right, and
what these numbers do to the argument configurations A–C are used to make. Both are Parsa's
calls. What this task establishes is that the medium, not the mechanism, is doing the work in
his NLDM gas-exchange read-out.
