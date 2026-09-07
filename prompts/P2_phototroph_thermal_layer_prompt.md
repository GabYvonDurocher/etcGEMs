# Claude Code prompt — P2 (phototroph build): add the thermal layer (kcat(T) MMRT + two-state unfolding + NGAM(T)) to the Synechocystis 6803 ecModel, and produce the emergent (a-priori) light-saturated growth TPC (autonomous)

Run from the project root (`.../MICROADAPT/etcGEMs`). Adds the TEMPERATURE-DEPENDENT envelope to the P1 base
ecModel (iSynCJ816_STAR, pre-built AUTOPACMEN sMOMENT), reusing the E. coli / methanogen thermal machinery
(src/etcgem/mmrt.py, unfolding.py). Produces the EMERGENT (nothing-fit) light-saturated growth TPC and compares
it a-priori to the Zavrel 2015 curve. SS-E (Sharpe-Schoolfield) descriptors throughout (the current standard).
NO calibration (P3), NO Ea dissection (P4). Emergent-then-calibrate: nothing tuned to the data.

NOTE TO USER: launch in an auto-approving mode, from the venv with Gurobi. Needs the Li-Engqvist predictor + the
digitised Zavrel 2015 TPC.

CONTEXT (P1): Synechocystis 6803, light-SATURATED / in-mechanism regime confirmed in-silico — under pure autotrophy
the photon exchange goes non-binding and the enzyme pool binds (carbon-fixation capacity limits), so NO new
light-supply layer is needed. Base GEM iSynCJ816 (1044 rxns / 928 mets / 816 genes); enzyme layer iSynCJ816_STAR
(AUTOPACMEN sMOMENT, the same enzyme-cost family as the methanogen). Objective BIOMASS_Ec_SynAuto_1; RuBisCO
(RBPC_1) carries carbon fixation; zero net photorespiration at the optimum under saturating CO2. RuBisCO/Calvin
kcats are already in the ecModel and well-measured — the easy direction. Validation TPC: Zavrel 2015, Topt ~35 C.

---

```
Work AUTONOMOUSLY end to end; commit in parts; print a summary. Read first: src/etcgem/{mmrt.py (kcat(T) MMRT),
unfolding.py (two-state native fraction f_N(T), Tm), enzyme_cost.py (how kcat(T)/f_N enter the pool cost; the
set_temperature + NGAM(T) gate), providers.py (from_gem_smoment + how the thermal envelope is wired for E. coli
and the methanogen), sectors.py (NGAM(T) + the growth-law toggle), config.py, tpc.py (the TPC engine +
descriptors), sharpe_schoolfield.py (the SS-E fit)}, strains/syn6803/{strain.yaml, model/ (base + ecModel),
outputs/P1_scaffold_and_base.md, thermal/ (the digitised Zavrel 2015 TPC — the user will add it; if absent, digitise
from the paper figure and save it there)}, strains/mmaripaludis/outputs/{M3_thermal.md, M6_sector_layer.md} (the
methanogen precedent to mirror), and docs/PHOTOTROPH_ETCGEM_PLAN.md. Gurobi with a GLPK-abort guard; print solver.
Operate under the P1 light-SATURATED autotrophic medium (photon bound non-limiting, CO2 available).

PART A - per-enzyme thermal envelope (kcat(T) + unfolding)
- kcat(T): wrap each enzyme's iSynCJ816_STAR base kcat with the MMRT curvature (the literature dCp prior
  -4 kJ/mol/K used for E. coli + the methanogen) and a per-enzyme optimum Topt from the Li-Engqvist sequence
  predictor run on the Synechocystis 6803 reference proteome (UniProt UP000001425 — confirm the ID; reuse the
  pipeline; ~90%-style coverage, rest at dataset mean). Reuse mmrt.py; do NOT fork.
- Native fraction f_N(T): two-state unfolding keyed on a per-enzyme melting temperature Tm. Tm ROUTE (the open
  input for a mesophilic cyanobacterium — DOCUMENT the choice, same precedent as the methanogen): use a MESOPHILE
  Tm PRIOR (the E. coli meltome mean ~55.6 C + spread), INDEPENDENT of Topt, since 6803 is mesophilic (~35 C) and
  absent from the Meltome Atlas. Flag as the a-priori Tm to be refined by P3's dTm; note a cyanobacterial/meltome-
  trained Tm predictor is the future upgrade. Reuse unfolding.py.

PART B - NGAM(T) maintenance (phototroph maintenance energy)
- Add a temperature-dependent non-growth maintenance NGAM(T), same Boltzmann/Arrhenius form as E. coli / methanogen.
  Anchor its amplitude on a MEASURED Synechocystis 6803 maintenance-energy value if one exists (search: chemostat /
  photobioreactor maintenance ATP or maintenance respiration for 6803 — e.g. from the Zavrel 2019 cell-economy or
  Jahn 2018 datasets, or a cyanobacterial maintenance estimate); if no clean measured value is available, carry a
  DOCUMENTED prior (state the source + that P3's ngam_scale will refine it). NOTE the phototroph subtlety: under
  light the maintenance ATP is met by photophosphorylation, so NGAM(T) draws on the same photon/enzyme budget —
  keep it in the standard maintenance form and document this. (GAM stays in the biomass reaction.)

PART C - emergent light-saturated growth TPC (nothing fit)
- Sweep temperature (e.g. 5-50 C) under the light-saturated medium and compute the EMERGENT growth TPC. ALSO report
  the carbon-fixation-flux TPC (RuBisCO carboxylase flux) as the SECONDARY descriptor for the direct Yvon-Durocher
  2014 comparison (their photosynthesis Ea is a flux rate). Compute descriptors: Topt, rmax, CTmax, niche width, and
  the window-independent SHARPE-SCHOOLFIELD E (reuse sharpe_schoolfield.py) as the reportable Ea. Compare A-PRIORI
  (nothing fit) to the digitised Zavrel 2015 TPC: report the shape match (expect Topt ~33-35 C, the rising-limb
  behaviour) and the honest magnitude offset (to be closed by P3). Save the emergent TPC (growth + carbon-fixation)
  + a figure overlaying the Zavrel data.
- PHOTORESPIRATION caveat (document, do not build): the classic photosynthesis temperature response includes
  RuBisCO's declining CO2/O2 specificity with warming (rising photorespiration). Under Zavrel's CO2-replete
  saturating-light conditions photorespiration is suppressed (P1: zero net at the optimum), so the emergent growth-
  TPC is dominated by Calvin-cycle kcat(T), which the framework carries. State this as a modelling choice + a future
  refinement (a temperature-dependent RuBisCO specificity factor), consistent with the honest-caveat house style.
- Keep the growth-law/allocation coupling OFF for now (single sMOMENT pool + NGAM(T) is the P2 envelope); NOTE that
  the cyanobacterial allocation layer (the phototroph analog of Scott/Muller — Zavrel 2019 + Jahn 2018 + the 2021
  temperature-growth-law paper) is the next step (P2b or folded into P3) before the three-way Ea comparison, exactly
  as the methanogen sector layer (M6) was.

PART D - outputs + GO/NO-GO
- Save under strains/syn6803/outputs/P2_thermal/: the emergent TPC (growth + carbon-fixation), descriptors (incl.
  SS-E), the Zavrel-overlay figure, and P2_thermal.md documenting the Topt source, the Tm route + caveat, the
  NGAM(T) source, the emergent descriptors vs Zavrel, the photorespiration caveat, and the carry-forward items
  (allocation layer deferred; Tm prior). GO/NO-GO for P3 (Bayesian calibration to Zavrel).

VERIFY (report all)
0. solver=gurobi. Thermal layer wired onto the iSynCJ816_STAR ecModel; loads/runs via the standard provider/CLI;
   operated under the light-saturated medium (photon non-binding confirmed still holds across the sweep).
1. kcat(T) (MMRT dCp + Li-Engqvist Topt on UP000001425) + f_N(T) (mesophile Tm prior, documented + flagged) applied;
   coverage reported.
2. NGAM(T) added; amplitude from a measured 6803 maintenance value if available (cited) or a documented prior.
3. Emergent light-saturated TPC produced (growth + carbon-fixation flux); descriptors incl. SS-E reported and
   compared A-PRIORI to Zavrel 2015 (shape match + honest magnitude offset); overlay figure saved.
4. Growth-law/allocation OFF (noted as the next step before P4); photorespiration caveat documented; nothing tuned.
5. P2_thermal.md + outputs saved; GO/NO-GO for P3 with the carry-forward caveats.

CONSTRAINTS
- Emergent thermal envelope only (kcat(T) + unfolding + NGAM(T)). NO calibration, NO Ea dissection, NO growth-law
  coupling, NO new light-supply layer (in-mechanism is confirmed). Reuse the E. coli / methanogen thermal machinery
  (mmrt/unfolding/sectors/tpc/sharpe_schoolfield); do not fork. Nothing fit to the Zavrel data. SS-E throughout.
- Document the Tm route (mesophile prior), the NGAM source, and the photorespiration caveat explicitly.
- Autonomous; commit in parts: "phototroph P2: thermal envelope (kcat(T) MMRT + Li-Engqvist Topt + mesophile-prior Tm unfolding)",
  "phototroph P2: NGAM(T) + emergent light-saturated growth/carbon-fixation TPC vs Zavrel 2015 (SS-E) + P2 note".
```
