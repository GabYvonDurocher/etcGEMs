# Calibration TPC source — Jones, Paynter & Gupta 1983

**Citation.** Jones WJ, Paynter MJB, Gupta R (1983). *Characterization of Methanococcus
maripaludis sp. nov., a new methanogen isolated from salt marsh sediment.* Archives of
Microbiology **135**: 91–97.

**Relevant data.** Figure 2 — growth rate (or reciprocal generation time) vs temperature
for *M. maripaludis* strain JJ on H2/CO2, defined mineral medium. Reported optimum near
**38 °C**, growth range ~**18–47 °C**, with mu_max on the order of **0.18–0.19 /h**
(doubling time ~3.6 h at optimum; the paper reports generation times).

**Status: NOT YET DIGITIZED.** The accompanying `mmaripaludis_tpc_curves.csv` is a
**PLACEHOLDER** — approximate values consistent with the reported optimum/range/mu_max,
used only to scaffold the M2 calibration pipeline. Every row is flagged `PLACEHOLDER`.

## To finalise (M2)
1. Obtain the paper (Arch Microbiol 135:91–97) and digitise Fig. 2 (WebPlotDigitizer).
2. Confirm the y-axis units (growth-rate constant k /h vs generation time g; k = ln2/g).
3. Confirm the strain (type strain JJ / S2) and medium (H2/CO2 defined) match the GEM.
4. Replace the placeholder rows; drop the `PLACEHOLDER` flag; record the digitised points'
   provenance here.
5. Cross-check against any second independent M. maripaludis TPC if available (mirrors the
   eciML1515 multi-source convention in `strains/eciML1515/thermal/sources/`).
