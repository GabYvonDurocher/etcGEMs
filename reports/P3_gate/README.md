# `reports/P3_gate/` — README

## What the gate is, restated 2026-09-09 (P10) — a dated note; the gate's history is not rewritten

P3's gate is a **port-fidelity check**: it reads one parameter point out of each of Parsa's
committed chains and recomputes, in this repository's code, the ten R² values his reports
print, under his media and his caps. It passed to within 0.009 (`gate.md`). P6 established
that none of those chains is converged, and P6 D3a / P9 / P10 that the respiration term as it
stood scored a quantity the model does not determine continuously — the O2 uptake at the growth
optimum, read off whichever LP vertex the solver returned.

P10 added a tie-break (`flux_tpc(tiebreak="pfba")`: growth held at its optimum, total absolute
flux minimised, O2 read at that vertex, all solves at 1e-9) and re-read the gate at Parsa's own
θ under it (`reports/P10_respiration_likelihood/task4_regate.csv`):

| config, medium (point) | growth R², P3 → P10 | respiration R², P3 → P10 |
|---|---|---|
| D NLDM (posterior median) | 0.7066 → 0.7066 | 0.7246 → 0.7246 |
| D LB (MAP) | 0.8964 → 0.8964 | 0.7931 → 0.7931 |
| E NLDM (MAP) | 0.8492 → 0.8492 | 0.7214 → 0.7215 |
| E LB (MAP) | 0.8284 → 0.8284 | 0.8014 → 0.7749 |
| F NLDM (MAP) | 0.9051 → 0.9051 | 0.9636 → 0.9635 |
| F LB (MAP) | 0.8809 → 0.8809 | 0.8524 → 0.8518 |

**The restated criterion.** *Growth fidelity is unchanged* — the tie-break never touches the
growth solve, and all ten growth values reproduce to four decimals. *Respiration fidelity for
configuration D is unchanged* — its O2 at the optimum was already unique. *For E and F the
respiration value is now deterministic and is compared at the pfba point*; the difference
from P3's number (E LB 0.8014 → 0.7749; E NLDM, F NLDM, F LB within 0.001) is **the width of
the face at his θ**, not a regression — the old number was one arbitrary point of it, and at
his θ that face happens to be narrow (0.17 mmol gDW⁻¹ h⁻¹ at 37–50 °C on E LB) where at P4's
MAP it is [0, 190]. F LB's tie-break is not exact (P10 D1: 0.05–0.5 between calls), so its
respiration row carries that caveat. The gate is not re-opened against his numbers: his chains
remain what they were, and the gate still says what it said — the port reproduces his
computation.
