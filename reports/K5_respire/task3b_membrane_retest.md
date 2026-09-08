# K5 TASK 3b — the membrane constraint, re-tested on a model that can respire

**A required interspecies difference now exists, for one species out of three, and it is
122-fold.** K4 got "no answer at all". The two escape routes it ran with are now closed, and
the mechanism does have thermal leverage — but the direction is still backwards, and the
parameter caveat that made K4's result uninterpretable as an explanation is unchanged.

Reproduce with `python3 reports/K5_respire/task3b_membrane_retest.py` (exit 0). Tables:
`task3b_sweep.csv`, `task3b_counterfactual.csv`, `task3b_flatness.json`.

---

## Why K4's null result did not settle it

K4 swept A_ETC on models with two escape routes, and both are now known.

**The proton leak**, repaired in TASK 2. The chain carried 0.04–0.05 % of the load, so
constraining the area of complexes carrying no flux could not do anything.

**Fermentation with no carbon cap.** Measured here, on the repaired *C. auris* at 40 °C: as
A_ETC tightens from non-binding to zero, carbon uptake **triples** while growth falls by two
thirds.

| A_ETC | growth | carbon uptake (mmol C/gDW/h) | qO₂ |
|---|---|---|---|
| unconstrained | 0.0654 | 12.0 | 5.08 |
| 0.5 × A\* | 0.0486 | 28.3 | 2.61 |
| 0 | 0.0225 | 35.9 | 0.09 |

The cell buys its way out of the area budget with carbon. P4 found the same in *E. coli* on M9.

**The cap, and why this value.** `c_max = 12.0 mmol C/gDW/h`, the carbon the calibration strain
consumes at 40 °C with no area constraint. It is therefore the tightest cap that does not itself
reduce base growth — P4's criterion, which is to close the escape rather than impose a new
limitation. One shared value across the four species deliberately: a per-species cap would
encode a species difference nothing measured supports. Swept at 8, 12 and 20 as a sensitivity.

## The required interspecies difference

By what factor must a relative's A_ETC be reduced, relative to *C. auris*, to put it below the
0.05 h⁻¹ detection floor at 40 °C?

| species | K4 (unrepaired, no cap) | repaired, no cap | **repaired + cap** |
|---|---|---|---|
| *C. haemulonii* | none at any budget | none at any budget | **122× smaller** |
| *C. duobushaemulonii* | none | none | none (0.197 h⁻¹ at zero area) |
| *C. parapsilosis* | none | none | none (0.200 h⁻¹ at zero area) |

**Both changes were needed.** The repair alone does not produce an answer; the cap alone would
act on a model whose chain carries no flux. Together, one of the three relatives becomes
killable by a membrane-area budget.

## Beside K2's 13.8 °C

| mechanism | required difference | available | shortfall |
|---|---|---|---|
| enzyme Tm (K2) | 13.8 °C | 0.411 °C predicted; 1.6 °C measured | 26× ; 8.6× |
| **ETC membrane area (K5)** | **122-fold in A_ETC**, and only for one of three relatives | no *Candida* measurement exists; nearest fungal proxy is **7×** (cytochrome content per gDW across seven yeasts, Arthur & Watson 1976) | **≈17×** |

The membrane route can now at least be *expressed* as a ratio, which K4 could not do. Expressed,
it falls about seventeen-fold short of the largest between-species difference anyone has measured
in fungal bioenergetic membrane content — and that proxy is cytochrome density, not membrane
area, because no fungal membrane-area comparison exists at all.

## The direction still runs backwards

K4's decisive objection was that tightening the budget hurt *C. auris* most, which is the
opposite of the phenotype. **That survives both the repair and the carbon cap.** Peak growth at
zero area as a fraction of unconstrained:

| species | repaired, no cap | repaired + cap |
|---|---|---|
| ***C. auris*** | **0.448** | **0.231** |
| *C. haemulonii* | 0.674 | 0.371 |
| *C. duobushaemulonii* | 0.812 | 0.578 |
| *C. parapsilosis* | 0.511 | 0.352 |

*C. auris*, the thermotolerant species, remains the most membrane-limited of the four, and the
cap makes the gap wider rather than narrower. For the mechanism to explain the phenotype the
ordering would have to invert.

## What the constraint now does to the curve

It has real thermal leverage, which it did not have in K4. With the cap on, as A_ETC goes from
non-binding to zero:

| | *C. auris* | *C. haemulonii* | *C. duobushaemulonii* | *C. parapsilosis* |
|---|---|---|---|---|
| CT_max (°C) | 53.0 → **36.5** | 51.6 → 41.1 | 51.7 → 46.7 | 53.2 → 45.8 |
| T_opt (°C) | 36.5 → 27.5 | 36.5 → 30.0 | 33.5 → 29.5 | 37.0 → 31.5 |
| E_a (eV) | 1.33 → **2.41** | 1.42 → 2.13 | 1.45 → 2.08 | 1.15 → 1.75 |

In K4 the same sweep moved *C. auris*' CT_max only from 53.6 to 47.0 °C. A membrane budget on a
model that respires under a carbon budget is a far stronger lever on the upper thermal limit.

**Flatness**, per N1's guard: the 1 %-of-peak plateau is **0.0–3.0 °C on a 60 °C grid** across
all 160 runs, so these are genuine peaks and T_opt is meaningful here.

## The parameter caveat, restated because none of this touches it

**Zero of twenty area and turnover values in `strains/*/etc/complexes.csv` are measured in any
*Candida*.** All four species carry identical tables. A constraint whose parameters do not
differ between species cannot **explain** a difference between them, however it now behaves.
Everything above describes what the mechanism *does*; none of it is evidence that membrane area
is what separates these species. The 122-fold figure is what the model would *require*, not
something anyone has observed, and the direction result says the mechanism is pushing the wrong
way regardless.
