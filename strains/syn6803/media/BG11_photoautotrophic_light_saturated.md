# Medium: photoautotrophic, light-SATURATED (Synechocystis sp. PCC 6803)

Defined inorganic (BG-11-like) photoautotrophic medium for the etc-GEM, encoding the
**light-saturated regime** chosen by the user: the photon supply is set NON-limiting so
that **carbon fixation** (RuBisCO / Calvin-cycle enzyme capacity), not photon supply,
sets the rate. This keeps the phototroph *in-mechanism* — the same enzyme-cost /
kcat(T)-limited decomposition as E. coli and M. maripaludis, with no new light-supply
layer.

Availability (open exchange bounds), not pinned uptakes. Resolved by reaction ID at run
time. The base GEM is iSynCJ816 (Joshi et al. 2020); the enzyme layer is iSynCJ816_STAR
(AUTOPACMEN sMOMENT; see model/ecmodel_iSynCJ816_STAR/).

## Energy input — SATURATING light (the in-mechanism encoding)
- `EX_photon_e`  — photon uptake bound set NON-limiting (lb = -999999): photons are in
  excess, so light capture is never the binding constraint. In the enzyme-constrained
  model the photon flux then goes SLACK (shadow price 0) and the enzyme pool binds — the
  in-silico signature of light saturation (see outputs/P1_scaffold_and_base.md).
  Physical anchor: Zavrel et al. 2015 grew glucose-tolerant 6803 under SATURATING red
  light (220-360 umol photons m^-2 s^-1, no photoinhibition to 660) — the regime this
  medium reproduces.

## Inorganic carbon (the fixed substrate RuBisCO acts on)
- `EX_co2_e`   — CO2 available (lb = -1000): dissolved CO2 for RuBisCO carboxylation.
- `EX_hco3_e`  — bicarbonate available (open as shipped): the cyanobacterial CO2-
  concentrating mechanism (CCM) substrate; the model draws inorganic C predominantly as
  HCO3- and fixes it via RuBisCO (RBPC_1).

## Other inorganic nutrients (BG-11 constituents; open as shipped in the ecModel)
- Nitrogen `EX_no3_e`; phosphate `EX_pi_e`; sulfate `EX_so4_e`; water `EX_h2o_e`;
  protons `EX_h_e`; O2 `EX_o2_e` (photosynthetically evolved, net EFFLUX at the
  autotrophic optimum).
- Trace metals: Ca, Co, Cu, Fe2+, Fe3+, K, Mg, Mn, Mo, Na, Ni, Zn (all open).

## Organic carbon — CLOSED (forces true autotrophy)
- `EX_glc__D_e` set to 0 (the only open organic-C uptake as shipped; the ecModel ships
  photoMIXOtrophic). Also keep closed: EX_ac_e, EX_pyr_e, EX_succ_e, EX_glcglyc_e.
  At the autotrophic optimum glucose flux = 0 (verified).

## Objective
- `BIOMASS_Ec_SynAuto_1` — the AUTOTROPHIC biomass reaction (Joshi et al. 2020 provide
  three: SynAuto / SynMixo / SynHetero; we use SynAuto for photoautotrophy).

## Curation note (scientific, not a person-named correction)
No futile-photon curation was required: closing organic carbon and maximising autotrophic
biomass gives a finite, well-posed optimum with RuBisCO carrying carbon-fixation flux and
zero net photorespiration. (Contrast the E. coli O2-sink curation.) The plain-FBA base
GEM is photon-LINEAR by construction — growth scales with the photon bound because a
stoichiometric model has no per-throughput enzyme cap — so light saturation cannot appear
until the enzyme pool is present. It appears immediately in the enzyme-constrained model:
growth saturates at ~51 photon units and photon becomes non-binding (P1 forward-check).
