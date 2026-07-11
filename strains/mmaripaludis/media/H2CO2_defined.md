# Defined H2/CO2 medium — iMR539 (M. maripaludis), M1 foundation

**Principle (project rule): medium is *availability*, not pinned uptake.** Exchanges below
are opened (uptake allowed) or closed; uptake *rates* are never fixed. In plain FBA the
absolute growth rate therefore scales with the H2 availability bound and is not meant to
match measured mu_max — the enzyme/maintenance ceiling that sets physiological rates is
added in M2.

Reaction IDs are ModelSEED/`cpd`-style with cobra's bracket mangling
(`[e0]` -> `_LSQBKT_e0_RSQBKT_`).

## Opened for uptake (lb = -1000)
| role | metabolite | exchange id |
|---|---|---|
| electron donor | H2 | `EX_cpd11640_LSQBKT_e0_RSQBKT_` |
| carbon source | CO2 | `EX_cpd00011_LSQBKT_e0_RSQBKT_` |
| nitrogen | NH3 | `EX_cpd00013_LSQBKT_e0_RSQBKT_` |
| sulfur | H2S | `EX_cpd00239_LSQBKT_e0_RSQBKT_` |
| minerals/vitamins | H2O, Pi, Mn, Zn, Cu, Ca, Cl, Mo, Co, K, Ni, Mg, Fe2/Fe3, Selenate, Thiamin, NMN | `cpd00001/00009/00030/00034/00058/00063/00099/00131/00149/00205/00244/00254/10515/10516/03396/00305/00355` |

## Required biomass precursors — opened, but ARTEFACTUAL (M1 finding, close in M2)
The published reconstruction **cannot grow without** free uptake of four biomass
components (closing any one -> mu = 0): they have no biosynthesis route in the draft.
Left open in M1 so the published model runs; flagged for gap-filling in M2.
- Membrane_lipid `EX_Membrane_lipid_LSQBKT_c0_RSQBKT_`
- Flagellin `EX_Flagellin_LSQBKT_e0_RSQBKT_`
- NAC (NDP-2-acetamino cell-wall sugar) `EX_NAC_LSQBKT_c0_RSQBKT_`
- tRNA(SeCys) `EX_cpd15573_LSQBKT_c0_RSQBKT_`

## Closed (organic-carbon leaks; genuine, non-essential)
- Acetate `EX_cpd00029_LSQBKT_e0_RSQBKT_`  (open bidirectional in shipped model)
- octadecenoate `EX_cpd15269_LSQBKT_e0_RSQBKT_`

## Methane
Shipped model **pins** CH4 exchange at (50, 50). M1 frees it to `(0, 1000)` so methane
is an emergent product. `EX_cpd01024_LSQBKT_e0_RSQBKT_`.

## Validated behaviour (plain FBA / pFBA)
- Grows on H2/CO2: mu = 0.547 /h (overshoots lit. ~0.23/h — no enzyme/ATPM ceiling yet).
- Methanogenesis stoichiometry **H2 : CO2 : CH4 = 4.12 : 1.06 : 1** (theory 4:1:1) — Wolfe
  cycle correctly wired (Mcr rxn03127, Mtr rxn03020, Fwd rxn11938, Hmd rxn06696, HdrABC,
  Na+ A1A0 ATP synthase all carry flux).
- No growth without electron donor (CO2-only infeasible) or without carbon (H2-only infeasible).
- H2/CO2 >= formate/CO2 (formatotrophic growth not supported by the base GEM — see audit).
