# K5 TASK 4 — what the repair does to Figure 4's arithmetic

**Almost nothing. The required interspecies Tm separation moves from 13.64 °C to 13.57 °C —
0.07 °C, half a percent.** Closing both escape routes does not make the model easier to kill.

Reproduce with `python3 reports/K5_respire/task4_required_separation.py` (exit 0). Table:
`task4_required_separation.csv`.

---

## The number, in its lineage

The uniform downward shift of every enzyme's Tm that first puts a relative below the 0.05 h⁻¹
detection floor at 40 °C, median over the three relatives. Computed by the same function the
`transfer` command uses, so these sit directly beside K2's.

| model state | required ΔTm | vs predicted 0.411 °C | vs measured 1.6 °C |
|---|---|---|---|
| the standalone, phenomenological form (K1 / K2 rung B0) | **32.5 °C** | 79× | 20× |
| K2, the core's unfolding form (B1–B4) | **13.8 °C** | 34× | 8.6× |
| K5, B3 reproduced here | 13.64 °C | 33× | 8.5× |
| **K5, repaired chain, no carbon cap** | **13.57 °C** | 33× | 8.5× |
| **K5, repaired chain + carbon cap 12** | **13.57 °C** | 33× | 8.5× |
| K5, unrepaired + carbon cap 12 | 13.64 °C | 33× | 8.5× |

Per species, the repaired and capped model: *C. haemulonii* 13.23 °C, *C. duobushaemulonii*
13.57 °C, *C. parapsilosis* 13.77 °C. Permissive-temperature growth is preserved in every case.

## Direction of movement, and why it is so small

The requirement **falls**, by 0.07 °C. The prompt's expectation was reasonable — a model with
fewer escape routes should be easier to kill — and it is met in sign and missed in magnitude by
about two orders.

The reason is what the counterfactual actually does. It shifts **every enzyme's** Tm, not the
respiratory ones. That denatures the fermentation enzymes and the biosynthetic enzymes along
with the chain, so whether the cell *could* have escaped into fermentation or into a free proton
circuit is beside the point: at the shift that kills it, those routes have been denatured too.
The escape routes mattered enormously for a constraint aimed at **respiration** — TASK 3b, where
closing them turned "no answer at any budget" into a finite 122-fold requirement — and they
matter almost not at all for a perturbation aimed at **every enzyme at once**.

Stated the other way round: the 13.8 °C figure was never propped up by the leaks. It is a
property of how far a whole proteome has to be destabilised before growth stops, and that is
robust to the two model defects K5 removed.

## Not adjudicated here

The number is reported and left for the humans to read against §1 of the discussion notes. What
K5 adds is that it is not an artefact of the two defects K4 and K5 found, which was a live
possibility before this was computed and is now closed.
