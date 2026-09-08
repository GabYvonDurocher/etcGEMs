# P3 TASK 4 — c_max: adopting the value Parsa's own sweep recommends

**This is his recommendation, not ours.** The change is made on his evidence and cited to it.

## The provenance

`$PARSA_ROOT/outputs_reports/etcgem3_Gas Flux report_2.pdf`, §4 *"Gas exchange and the
total-carbon-cap sweep"*, its C_max table and Figure 3. He sweeps 60 / 100 / 120 / 180 and
tabulates, in his own columns:

| C_max | glucose r_max | NLDM r_max | LB/BHI r_max | growth shape | gas (RQ range) |
|---|---|---|---|---|---|
| **60** | 0.83 | 0.97 | 0.93 | **flat plateau** | respiratory (0.90–1.07) |
| 100 | 1.07 | 1.56 | 1.51 | defined peak | respiratory (0.96–1.10) |
| 120 | 1.13 | 1.73 | 1.70 | near-clean peak | respiratory near opt. (0.96–1.18) |
| 180 | 1.17 | 2.03 | 1.99 | clean peak | degrading (glc 0.67) |

and concludes, verbatim:

> *"Growth shape and respiration trade off through the carbon cap. A tight cap gives
> respiratory gas but a flat growth plateau; a loose cap gives a peaked TPC but fermentative
> gas. **C_max ≈ 100–120 is the sweet spot**: peaked growth and respiration (RQ≈1) around the
> optimum."*

No literature citation for any value exists anywhere in his folder (P2 TASK 3 searched);
the sweep is the whole provenance, and it does not recommend 60.

## Why 120 rather than 100, within his range

One measured reason: **at c_max = 100 acetate overflow is zero on NLDM**
(`reports/P2_settle/task3_cmax_table.csv`), and a cap that suppresses overflow defeats the
configuration it exists to support. At 120 overflow is non-zero on every medium. 120 is also
the value his own table calls a "near-clean peak" with respiration still near 1 at the optimum.

## Where it lives

`strains/eciML1515/gas_exchange.yaml`, `gas_exchange.carbon_cap.c_max: 120.0`, with the
citation in the comment. `configs/experiments/gasflux_configB.yaml` adopts it;
`gasflux_configB_cmax60.yaml` keeps 60 as an explicitly labelled **sensitivity**, and P1's gate
now reads that run, because the gate's job is to reproduce his figure and his figure used 60.
**The P1 gate still passes 60/60.**

## Every number that moves, 60 → 120

| medium | T_opt (°C) | r_max (h⁻¹) | O₂ @T_opt | CO₂ @T_opt | acetate @T_opt | RQ @T_opt |
|---|---|---|---|---|---|---|
| glucose | 37.5 → **38.0** | 0.827 → 1.125 (**+36 %**) | 24.30 → 24.36 (+0.2 %) | 26.06 → 26.76 (+2.7 %) | **0 → 23.53** | 1.073 → 1.099 |
| NLDM | 32.5 → **39.5** (**+7.0 °C**) | 0.954 → 1.682 (**+76 %**) | 22.45 → 38.94 (+73 %) | 20.83 → 43.18 (+107 %) | **0 → 3.90** | 0.928 → 1.109 |
| NLDM (blanket) | 34.5 → 39.5 (+5.0 °C) | 0.966 → 1.725 (+79 %) | 22.69 → 41.98 (+85 %) | 20.36 → 40.35 (+98 %) | **0 → 4.42** | 0.897 → 0.961 |
| LB | 33.0 → **39.5** (**+6.5 °C**) | 0.927 → 1.695 (+83 %) | 22.13 → 38.94 (+76 %) | 21.94 → 45.80 (+109 %) | **0 → 2.32** | 0.992 → 1.176 |
| BHI | 32.5 → **39.5** (**+7.0 °C**) | 0.928 → 1.695 (+83 %) | 21.97 → 38.94 (+77 %) | 21.91 → 45.80 (+109 %) | **0 → 2.32** | 0.998 → 1.176 |

Full table in `task4_cmax_change.csv`.

### The two things worth reading off it

**T_opt returns to where the uncapped model puts it.** Uncapped, this model peaks at 38.0 °C on
glucose and 39.0 °C on NLDM. At c_max = 60 it peaked at 37.5 and 32.5; at 120 it peaks at 38.0
and 39.5. **The −6.5 °C displacement at 60 is gone.** From P2's sensitivity table, 120 is inside
the flat region: T_opt changes 0.00 % on glucose and 1.28 % (half a grid step) on NLDM against
uncapped, and E_a 1.86 % and 0.33 % — against 1.32 %/16.67 % and 1.46 %/29.61 % at 60.

**Acetate overflow is now non-zero on every medium** — 23.5 (glucose), 3.9 (NLDM), 2.3
(LB/BHI) mmol gDW⁻¹ h⁻¹ — where at 60 it was **exactly zero everywhere**. A cap set below the
overflow onset makes configuration D's emergent overflow unobservable, which is self-defeating;
that is no longer the case.

RQ rises from ≈0.9–1.1 to ≈1.10–1.18 — still inside the range his own table gives for 120
("respiratory near opt., 0.96–1.18"), and the price his sweep says is paid for the peaked
growth curve.

## Also recorded here, from P2 TASK 2

His report says of configuration C that "because no carbon cap is imposed the RQ is not forced
toward 1 … NLDM RQ ≈ 7–9 — the acetate branch is pinned, the gas exchange is not made
respiratory". **On the canonical recipe medium that RQ is 1.04, not 7–9.** The high value was
the blanket medium's unlimited carbon availability, not the absent carbon cap; on the recipe
medium configuration C's NLDM gas exchange is near-respiratory with no cap at all. The glucose
half of his statement is unaffected (RQ ≈ 0.2 there either way).
