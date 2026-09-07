# Claude Code prompt — P3b (phototroph build): add a proteome-sector / allocation layer to the Synechocystis 6803 etcGEM, grounded in its OWN allocation physiology (Zavrel 2019 + Jahn 2018 + the 2021 temperature-growth-law treatment), and re-check/re-calibrate — so the three-way allocation comparison is symmetric (autonomous)

Run from the project root (`.../MICROADAPT/etcGEMs`). Adds a proteome-sector + growth-law-coupling layer to the
phototroph (currently a single sMOMENT pool, so its allocation term in the Ea decomposition is 0 by construction).
Grounds it in the organism's OWN allocation data — NOT the bacterial Scott law and NOT the methanogen's flat one.
This makes the eventual three-way decomposition SYMMETRIC (E. coli Scott rising-ribosome; methanogen Muller flat;
phototroph its own cyanobacterial law). Then checks whether the P3 calibration still holds and re-calibrates only if
needed. No Ea dissection (that is P4). Mirrors the methanogen M6 step exactly.

NOTE TO USER: launch in an auto-approving mode, from the venv with Gurobi + emcee. Sources literature (web). May
include a re-fit only if the sector layer materially changes the fit (expected NOT to, given the weak coupling).

CONTEXT: P3-calibrated phototroph (single pool) reproduces Zavrel (calibrated growth SS-E 0.563, validated against
Inoue flux 0.52). P3's verdict: the low phototroph Ea is genuinely shallow Calvin-cycle kcat(T) (plausible dCp x0.85),
achieved with NO allocation buffer. So the EXPECTATION here (to test, not assume): the cyanobacterial ribosome/
biosynthesis-vs-mu coupling is WEAK (Synechocystis runs a low translation fraction, <20%, ribosomal protein <8%,
rising only weakly with growth; a large share of proteome is photosynthesis/light-harvesting), so the allocation
buffer should come out SMALL — confirming the phototroph Ea is kinetic, not allocation-set, on a symmetric footing.

---

```
Work AUTONOMOUSLY end to end; commit in parts; print a summary. Read first: src/etcgem/{sectors.py (the E. coli
sector partition + coupled growth-law; the toggle + parameters; how the methanogen reused it), enzyme_cost.py,
providers.py (the route-B from_gecko phototroph path + how sectors attach), calibration.py, config.py}, strains/
syn6803/{strain.yaml, outputs/{P2_thermal.md, P3... calibration_zavrel/}}, strains/mmaripaludis/outputs/M6_sector_
layer.md (the methanogen precedent to mirror), strains/eciML1515/ (the E. coli sector parameters for structural
analogy), and docs/PHOTOTROPH_ETCGEM_PLAN.md. Gurobi (GLPK-abort guard); SS-E for descriptors; light-saturated medium.

PART A - source the cyanobacterial allocation data (its OWN strategy) — from the PRIMARY PDFs now in refs/
The primary sources are IN THE REPO: refs/synechocystis6803/{PIIS2211124718314852.pdf (Jahn et al. 2018, Cell Reports
25:478-486), elife-42508-v2.pdf (Zavrel et al. 2019, eLife 8:e42508), erj148.pdf (Suzuki, Simon & Slabas 2006, J Exp
Bot 57:1573-1578, heat-shock proteomics)}. Extract the numbers from these PDFs/their figures + source data, not web
snippets. (The pce147.pdf = Inoue 2001 is the TPC/denaturation ref, not allocation.)

- PRIMARY (fractions + slope) — Jahn et al. 2018: reports absolute proteome mass fractions for SEVEN sectors vs growth
  rate over mu = 0.016-0.106/h (matches our rmax), with linear fits (Fig 2A + Table S2). Map their sectors onto OUR
  three for symmetry with the other two organisms:
  * biosynthesis/ribosome f_bio  <-  RIB (16.5-16.9%; ribosomal proteins alone 5-8%), which INCREASES LINEARLY with mu
    -> this is the growth-law COUPLING SLOPE (the cyanobacterial analog of Scott 2010). Extract the slope from Fig 2A /
    Table S2.
  * metabolic f_metab  <-  LHC + PSET + CBM + GLM + LPB (light-harvesting + photosystems + carbon-fixation/uptake +
    metabolism; the flux-carrying proteins), ~50% total — this IS the light-harvesting -> metabolic mapping (state it).
  * maintenance f_maint  <-  MAI (up to ~33%; regulation + hypothetical/unknown).
  Also record the load-bearing quantitative facts: the constant (growth-invariant) proteome fraction a_const = 41% in
  Synechocystis vs 65% in E. coli (Jahn's Hui-style split), and that the ribosome slope is SHALLOW IN ABSOLUTE TERMS
  over the phototroph's small mu range (0 -> ~0.09/h) -> predicts a SMALL allocation buffer. If the data show that
  shallow coupling, that IS the finding (it corroborates P3's kinetic verdict on a MEASURED footing) — record it
  honestly, between E. coli's steep Scott slope and the methanogen's ~0.
- CORROBORATION + P_total + framework — Zavrel et al. 2019: confirms the direction (translation UP, light-harvesting
  DOWN with mu; 1356 proteins, 57% growth-dependent); gives the Faizi 2018 coarse-grained optimal-allocation model
  (sectors T/M/R/P/LHC) that our sector layer instantiates (cite it); and reports absolute PROTEIN CONTENT ~402 mg/gDW
  (decreasing with mu) = the phototroph P_total analog (vs E. coli 0.5 g/gDW) — use it to set/check the pool budget.
  Its Fig 6 (immunoblot-validated ribosome/PSU/metabolic fractions vs mu) is a second slope estimate.
- MAINTENANCE-SECTOR TEMPERATURE RESPONSE (bonus, for the maintenance sector / NGAM(T)) — Suzuki et al. 2006: heat-
  shock chaperones (GroESL, HtpG, HspA, ClpB1, DnaK2) induced at 44 C. Use the 2D-gel PROTEIN-level changes (NOT the
  8-40x transcript folds, which overstate the proteome mass change) to scale how the maintenance sector rises near the
  upper thermal limit — the cyanobacterial analog of the E. coli 2.7x chaperone rise. This informs the maintenance/
  NGAM(T) upper-limit behaviour (falling limb), NOT the rising-limb Ea; note it can also cross-check the P2 NGAM(T).

PART B - implement the phototroph sector layer
- Add the sector partition + coupled growth law to the phototroph provider (reuse sectors.py; do NOT fork).
  Parameterise the sector fractions + growth-law slope from PART A (the cyanobacterium's OWN values, NOT E. coli's,
  NOT the methanogen's). Keep it a documented, toggleable layer. Unlike E. coli's steep ribosome-scaling, the
  cyanobacterial slope is expected shallow — set it from the data, don't force.

PART C - re-check, and re-calibrate only if needed
- FIRST forward-check: with the sector layer ON and the P3 posterior-median parameters, does the model STILL
  reproduce Zavrel (rmax ~0.094, Topt ~35, CTmax ~44, growth SS-E ~0.56)? Report the deltas AND re-confirm the
  photon shadow price stays 0 (in-mechanism preserved).
- If the sector layer leaves the fit essentially unchanged (expected, if the coupling is weak), keep the P3 posterior
  and record that the layer is additive/near-neutral. If it materially shifts the fit (a biosynthesis cap now binds),
  RE-CALIBRATE to Zavrel with the sector layer on (reuse the P3 emcee setup, shape-first, same provenance priors +
  f_metab/f_maint now as real sector levers), and report the new posterior + whether Zavrel is still reproduced.
- Either way, report the calibrated sector allocation + the growth-law slope, and confirm SS-E still matches (~0.56).

PART D - outputs + GO for P4
- Save the sectored (+ possibly re-calibrated) phototroph model + config, and strains/syn6803/outputs/P3b_sector_
  layer.md: the sourced sector fractions + growth-law slope (with citations; note the light-harvesting -> metabolic
  mapping choice), whether a re-fit was needed, the fit deltas, and the expected implication for the allocation term
  (small, to be measured in P4). GO/NO-GO for P4 (Ea dissection + three-way E. coli-vs-methanogen-vs-phototroph
  comparison).

VERIFY (report all)
0. solver=gurobi; SS-E descriptors; light-saturated medium (photon shadow price 0 preserved).
1. Phototroph sector fractions + growth-law slope sourced from Zavrel 2019 + Jahn 2018 + the 2021 temperature-growth-
   law treatment (CITED); the slope recorded honestly (shallow if that is what the data show) — NOT E. coli's or the
   methanogen's law forced on; the light-harvesting -> metabolic-sector mapping stated.
2. Sector layer implemented via sectors.py (phototroph params; toggleable); provider/strain.yaml wired.
3. Forward-check reported; re-calibrated ONLY if the fit materially shifted; Zavrel still reproduced (rmax/Topt/CTmax/
   SS-E ~0.56), deltas stated; calibrated sector allocation + slope reported.
4. P3b_sector_layer.md saved; GO/NO-GO for P4.

CONSTRAINTS
- Build the phototroph's OWN sector/allocation layer from the PRIMARY PDFs (Jahn 2018 for fractions + slope; Zavrel
  2019 for P_total + corroboration + the Faizi coarse-grained framework; Suzuki 2006 for the maintenance-sector
  temperature response), NOT the bacterial Scott law and NOT the methanogen's flat law. Reuse sectors.py; no fork.
  Re-calibrate only if the forward-check demands it. NO Ea dissection here. Keep the single-pool P3 model as a
  fallback/comparison. Cite the primary sources (Jahn 2018, Zavrel 2019, Suzuki 2006; Faizi 2018 for the framework).
- Autonomous; commit in parts: "phototroph P3b: source + implement the Synechocystis sector/allocation layer (Jahn 2018 fractions+slope + Zavrel 2019 P_total + Suzuki 2006 maintenance)",
  "phototroph P3b: forward-check + re-calibrate-if-needed to Zavrel; sector allocation + growth-law slope + P3b note".
```
