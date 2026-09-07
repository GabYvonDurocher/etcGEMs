# Claude Code prompt — M6 (methanogen build): add a proteome-sector / allocation layer to the M. maripaludis etcGEM, grounded in its OWN allocation data (Muller 2021 + Xia proteome), and re-check/re-calibrate — so the cross-organism allocation comparison is symmetric (autonomous)

Run from the project root (`.../MICROADAPT/etcGEMs`). Adds a proteome-sector + growth-law-coupling layer
to the methanogen (currently a single sMOMENT pool, so its allocation term in the Ea decomposition is 0
by construction). Grounds it in the organism's OWN allocation physiology — NOT the bacterial Scott law.
Then checks whether the M4 calibration still holds and re-calibrates only if needed. No Ea dissection
(that is the M5-redo).

NOTE TO USER: launch in an auto-approving mode, from the venv with Gurobi + emcee. Sources literature
(web). May include a multi-hour re-fit only if the sector layer materially changes the fit.

CONTEXT: M4-calibrated methanogen (single pool) reproduces Jones (SS-E 1.06 vs obs 1.04). M5 found the
Ea difference vs E. coli rests on control-weighting (+0.24) + the MISSING allocation buffer (+0.13,
which is 0 by construction because the methanogen has no sector layer). To make the comparison
symmetric, build the sector layer from the methanogen's own data. Expectation (to test, not assume):
because M. maripaludis grows ~10x slower and Muller 2021 reports it MAINTAINS its methanogenesis
proteome even at slow growth (an "alternative allocation strategy"), the ribosome/biosynthesis-vs-mu
coupling should be WEAK — so the allocation buffer should come out SMALL, confirming the asymmetry.

---

```
Work AUTONOMOUSLY end to end; commit in parts; print a summary. Read first: src/etcgem/{sectors.py
(the E. coli sector partition + coupled growth-law; the toggle + parameters), enzyme_cost.py,
providers.py (from_gem_smoment + how sectors attach), calibration.py, config.py}, strains/mmaripaludis/
{strain.yaml, outputs/{M2b_kcat_refinement.md, M4_calibration.md, calibration_jones/}}, strains/
eciML1515/ (the E. coli sector parameters for structural analogy), and docs/METHANOGEN_ETCGEM_PLAN.md
(the Muller 2021 + Xia references). Gurobi (GLPK-abort guard); SS-E for descriptors.

PART A - source the methanogen allocation data (its OWN strategy, not the bacterial growth law)
- From Muller et al. 2021 (PNAS 118 e2025854118, the M. maripaludis "alternative resource allocation
  strategy", chemostat proteome vs growth rate) and the Xia 2006/2009 quantitative proteome (sector
  mass fractions under H2/N/P limitation): extract (i) the proteome SECTOR fractions (metabolic /
  ribosome-biosynthesis / maintenance) for M. maripaludis, and (ii) HOW the ribosome/biosynthesis
  fraction varies with growth rate mu — i.e. the growth-law COUPLING SLOPE. Cite the numbers/figures.
  If the data show a flat/weak coupling (proteome maintained at slow growth), that IS the finding —
  record the slope honestly (expected small).

PART B - implement the methanogen sector layer
- Add the sector partition + coupled growth law to the methanogen provider (reuse sectors.py; do NOT
  fork). Parameterise the sector fractions + the growth-law slope from PART A (the methanogen's own
  values, NOT E. coli's). Keep it a documented, toggleable layer. Note: unlike E. coli's steep
  ribosome-scaling, the methanogen slope is expected weak/near-flat — set it from the data, don't force.

PART C - re-check, and re-calibrate only if needed
- FIRST forward-check: with the sector layer ON and the M4 posterior-median parameters, does the model
  STILL reproduce Jones (peak ~0.18/h, Topt ~38, CTmax ~47, SS-E ~1.0)? Report the deltas.
- If the sector layer leaves the fit essentially unchanged (expected, if the coupling is weak), keep
  the M4 posterior and just record that the layer is additive/near-neutral. If it materially shifts
  the fit (binding biosynthesis cap etc.), RE-CALIBRATE to Jones with the sector layer on (reuse the
  M4 emcee setup, magnitude-first, the same provenance priors + f_metab/f_maint now as real sector
  levers), and report the new posterior + whether Jones is still reproduced.
- Either way, report the calibrated sector allocation + the growth-law slope, and confirm SS-E still
  matches observed (~1.0 vs 1.04).

PART D - outputs + GO for M5-redo
- Save the sectored (+ possibly re-calibrated) methanogen model + config, and strains/mmaripaludis/
  outputs/M6_sector_layer.md: the sourced sector fractions + growth-law slope (with citations), whether
  a re-fit was needed, the fit deltas, and the expected implication for the allocation term (small, to
  be measured in M5-redo). GO/NO-GO for M5-redo (re-dissect with the allocation term now computed).

VERIFY (report all)
0. solver=gurobi; SS-E descriptors.
1. Methanogen sector fractions + growth-law slope sourced from Muller 2021 + Xia (CITED); the slope
   recorded honestly (weak/flat if that is what the data show) — NOT the E. coli law forced on.
2. Sector layer implemented via sectors.py (methanogen params; toggleable); provider/strain.yaml wired.
3. Forward-check reported; re-calibrated ONLY if the fit materially shifted; Jones still reproduced
   (peak/Topt/CTmax/SS-E), deltas stated; calibrated sector allocation + slope reported.
4. M6_sector_layer.md saved; GO/NO-GO for M5-redo.

CONSTRAINTS
- Build the methanogen's OWN sector/allocation layer (Muller 2021 + Xia), NOT the bacterial Scott law.
  Reuse sectors.py; no fork. Re-calibrate only if the forward-check demands it. NO Ea dissection here.
- Keep the single-pool M4 model as a fallback/comparison. Cite the allocation data.
- Autonomous; commit in parts: "methanogen M6: source + implement the M. maripaludis sector/allocation layer (Muller 2021 + Xia)",
  "methanogen M6: forward-check + re-calibrate-if-needed to Jones; sector allocation + growth-law slope + M6 note".
```
