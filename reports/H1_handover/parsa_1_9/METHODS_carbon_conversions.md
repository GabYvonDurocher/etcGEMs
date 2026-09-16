# Medium-dependent carbon / cell-number conversions (pipeline 09)

**Scope.** `09_medium_constants.R` is a standalone add-on. It reads the finished
derived table (whose specific growth rate `r` and O2-consumption rate `K` are
immune to any of these constants) and regenerates only the carbon-unit and CUE
figures in this folder. It does **not** alter the derived table the calibration
likelihood consumes, so no fit changes. This note records where the conversion
constants come from.

The two size-dependent constants are both derived from **one per-medium input,
the cell volume**, by fixed formulas — so every medium is processed identically:

- **cells per OD600 (inoculum N0)** — from the Volkmer & Heinemann (2011)
  OD invariant.
- **carbon per cell** — from a single carbon *density* (fg C µm⁻³) × volume.

---

## 1. Cells per OD600 → N_inoc

Volkmer & Heinemann (2011) report that E. coli K-12 packs a constant total cell
volume per unit OD600 across growth conditions: **3.6 µL of cell volume per mL of
culture at OD600 = 1**. With an inoculum of OD600 = 0.0005:

```
N_inoc [cells/L] = 3.6 (µL mL⁻¹ at OD1) × 0.0005 (OD)
                   × 1e9 (µm³ per µL) × 1e3 (mL per L) / V(µm³)
                 = 1.8e9 / V
```

## 2. Carbon per cell → carbon density × volume

Carbon per unit **cell volume** is far more conserved across growth conditions
than carbon per cell, so we fix the density and let the medium-specific volume
set the per-cell carbon:

```
cell_carbon_fg = 180 (fg C µm⁻³) × V(µm³)
```

### Where the 180 fg C µm⁻³ comes from

Three independent direct measurements, each converted to the common unit
fg C µm⁻³. Carbon is taken as **47 % of dry weight**, measured on the exact
strain MG1655 by Folsom & Carlson (2015).

| source | what they measured | conversion to fg C µm⁻³ | result |
|---|---|---|---|
| Fagerbakke, Heldal & Norland (1996) | X-ray microanalysis of single actively-growing cells: ~0.20 pg C per µm³ of cell volume | 0.20 pg × 1000 fg/pg | **~200** |
| Loferer-Krößbacher, Klima & Psenner (1998) | TEM densitometry: ~435 fg **dry mass** per µm³ of cell volume | 435 × 0.47 (C fraction) | **~204** |
| Neidhardt & Ingraham (average E. coli cell) | ~1 µm³ cell, ~280 fg dry mass, carbon ≈ 47 % | 280 × 0.47 / 1 µm³ | **~132** |

The three estimates span **~132–204 fg C µm⁻³**; their midpoint is **~180**, which
is the value used. The independent methods (elemental microanalysis, mass
densitometry, and textbook composition) therefore agree to within about ±20 %,
which sets the uncertainty on the absolute carbon level. (Note: `r`, `K`, the
growth rate in h⁻¹, and every thermal-performance-curve *shape* are unaffected by
this constant; it moves only absolute carbon levels and the CUE curve.)

---

## 3. Per-medium constants applied

Cell volumes are representative E. coli K-12 average cell volumes for each growth
condition from Volkmer & Heinemann (2011) (they span ~1.5–4.4 µm³ over slow→fast
growth). N_inoc and carbon follow from §1 and §2.

| medium | cell volume (µm³) | N_inoc = 1.8e9/V (cells L⁻¹) | carbon = 180×V (fg C cell⁻¹) |
|---|---|---|---|
| LB | 4.4 | 4.09 × 10⁸ | 792 |
| R2A | 3.8 | 4.74 × 10⁸ | 684 |
| M9-glucose | 2.2 | 8.18 × 10⁸ | 396 |

This **replaces** an earlier route that read per-cell dry mass off a growth-rate
relationship, which required extrapolating past its fast-growth calibration
ceiling for LB and R2A. The density × volume route above rests on direct
elemental/mass measurements instead.

---

## 4. Planned experimental replacement

These are literature-anchored placeholders. Cells-per-OD600 (by microscopy
and/or flow-cytometry counting) and carbon content per cell are planned to be
measured directly in all three media, and will replace §1's OD invariant and
§2's carbon density respectively.

---

## References

- **Volkmer B, Heinemann M (2011)** Condition-dependent cell volume and
  concentration of Escherichia coli to facilitate data conversion for systems
  biology modeling. *PLoS ONE* 6(7):e23126.
- **Fagerbakke KM, Heldal M, Norland S (1996)** Content of carbon, nitrogen,
  oxygen, sulfur and phosphorus in native aquatic and cultured bacteria.
  *Aquatic Microbial Ecology* 10:15–27.
- **Loferer-Krößbacher M, Klima J, Psenner R (1998)** Determination of bacterial
  cell dry mass by transmission electron microscopy and densitometric image
  analysis. *Applied and Environmental Microbiology* 64(2):688–694.
- **Neidhardt FC, Ingraham JL, Schaechter M** *Physiology of the Bacterial Cell:
  A Molecular Approach* (composition of an average E. coli cell).
- **Folsom JP, Carlson RP (2015)** Physiological, biomass elemental composition
  and proteomic analyses of Escherichia coli ammonium-limited chemostat growth,
  and comparison with iron- and glucose-limited chemostat growth.
  *Microbiology* 161:1659–1670. (Measured MG1655 carbon = 45.5–47.4 % of dry weight.)
