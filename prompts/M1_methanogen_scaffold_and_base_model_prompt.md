# Claude Code prompt — M1 (methanogen build, phase 1): scaffold the M. maripaludis strain, get the base GEM (iMR539) loading + growing on H2/CO2, run the artefact audit, and assess ecModel-readiness (autonomous)

Run from the project root (`.../MICROADAPT/etcGEMs`). FOUNDATION phase for the methanogen etcGEM.
This is scaffolding + base-model validation + reconnaissance ONLY — it does NOT build the enzyme-
constrained (ecModel) layer, the thermal layer, or any calibration (those are later phases M2+). The
goal is a clean, growing base model and a clear, data-grounded picture of how to build the ecModel.

NOTE TO USER: launch in an auto-approving mode. It downloads a public SBML model; if the download is
blocked, it will stop and ask you to provide the file.

REFERENCE: docs/METHANOGEN_ETCGEM_PLAN.md (the full plan — read it first). Mirror the strains/eciML1515/
layout. Organism: Methanococcus maripaludis (hydrogenotrophic, CO2 + H2 -> CH4 via the Wolfe cycle,
mesophile ~38 C). Base GEM: iMR539 (Richards et al. 2016; BioModels BIOMD0000001099).

---

```
Work AUTONOMOUSLY; commit in parts; print a summary. Read first: docs/METHANOGEN_ETCGEM_PLAN.md,
strains/eciML1515/ (the strain layout + strain.yaml + media/ + thermal/ conventions to mirror),
src/etcgem/{providers.py, config.py, cli.py} (how a strain/provider is defined and loaded). Use Gurobi
if available (print the solver); plain FBA here (no enzyme constraints yet).

PART A - scaffold the strain
- Create strains/mmaripaludis/ mirroring strains/eciML1515/: subdirs model/, media/, thermal/,
  outputs/ (and proteomics/, dltkcat/ as empty placeholders for later phases). Add a strain.yaml with
  the ORGANISM metadata (name, hydrogenotrophic methanogen, Topt ~38 C, base model file, medium). Note
  in a comment that the provider type is plain FBA for now and will switch to an enzyme-constrained
  provider once the ecModel is built (phase M2).

PART B - acquire + validate the base GEM (iMR539)
- Download the iMR539 SBML from BioModels (BIOMD0000001099) into strains/mmaripaludis/model/. If the
  download is blocked/unavailable, STOP and ask the user to supply the SBML (name the expected path).
- Load it with cobra; report size (reactions, metabolites, genes) and confirm it matches the plan's
  iMR539 figures (~539 genes, ~688 reactions). Fix any SBML-load issues (BioModels exports sometimes
  need minor cleanup); note what was done.
- Set the DEFINED H2/CO2 medium: open H2 and CO2 uptake and the minimal-salt/N (ammonia) exchanges,
  close organic carbon sources; identify the CH4 and biomass exchange/objective. Confirm the model
  GROWS (biomass > 0) and PRODUCES METHANE (CH4 exchange > 0). Report mu_max, the CH4 flux, and the
  CH4-per-biomass ratio.
- Literature sanity checks (report each): mu is in the right ballpark (~0.2-0.35 /h optimal); the model
  CANNOT grow on formate alone without CO2 (needs CO2 as C source); growth on H2/CO2 >= formate/CO2.
  Flag any mismatch rather than papering over it.

PART C - preliminary artefact audit (flux-level; the enzyme-cost audit is phase M2)
- Analogous to the E. coli uncosted-O2-reaction audit, but methanogens use no O2 — scan the base model
  for likely artefacts that would scramble energy/flux accounting: thermodynamically-infeasible free
  energy-currency loops (ATP-, ferredoxin-, ion-gradient-generating cycles with no substrate cost),
  reactions carrying implausibly large flux, and any obviously non-physiological free reactions. LIST
  candidates with stoichiometry; do NOT close them yet (enzyme cost — the real basis for closure —
  needs the ecModel). Save the list for phase M2.

PART D - ecModel-readiness reconnaissance (the key output for phase M2)
- Assess how to build the enzyme-constrained layer: (i) how many reactions are enzymatic and have
  gene-protein-reaction rules; (ii) whether protein sequences are obtainable (from the genome / UniProt
  via the gene IDs) for kcat prediction; (iii) DLTKcat-mappability (can our existing DLTKcat pipeline
  take these sequences?); (iv) which CORE methanogenesis / electron-bifurcation enzymes (Hdr, Vhu/Vhc,
  Fru/Frc, Fdh, EchA/EchB, Mtr, Mcr) are present and could be anchored on MEASURED kinetics (Milton
  et al. 2018 for the Hdr/FBEB complexes + hydrogenases/Fdh). Report an estimated kcat-coverage
  breakdown (measured core / DLTKcat-predicted / dataset-mean fallback) and recommend the ecModel route
  (Python sMOMENT-style layer reusing src/etcgem/enzyme_cost, vs external GECKO) with reasons.

PART E - calibration TPC data setup (structure only; digitisation is the user's)
- Create strains/mmaripaludis/thermal/ with a SOURCE note pointing to Jones, Paynter & Gupta 1983
  (Arch Microbiol 135:91-97), Fig 2 — the growth-rate TPC for type strain JJ on defined H2/CO2 medium
  (mu_max ~0.18-0.19 /h at ~37-38 C, range 18-47 C). Add a template CSV (columns: temp_C, mu_per_h,
  source, medium) and populate it with ROUGH placeholder points clearly flagged "PLACEHOLDER — replace
  with a proper WebPlotDigitizer read of Jones 1983 Fig 2". Do NOT use these for any fitting.

PART F - report + go/no-go
- Print a SUMMARY: base model loads + grows on H2/CO2 (mu_max, CH4 flux, sanity checks); the artefact
  candidates; the ecModel-readiness breakdown + recommended route; and an explicit GO/NO-GO for
  proceeding to phase M2 (ecModel construction), listing exactly what M2 needs.

VERIFY (report all)
1. strains/mmaripaludis/ scaffolded (mirrors eciML1515); strain.yaml with organism metadata.
2. iMR539 downloaded + loads; size matches the plan; grows on H2/CO2 with CH4 production; mu_max + the
   literature sanity checks reported (formate-alone fails; H2/CO2 >= formate/CO2).
3. Preliminary artefact candidates listed (not closed).
4. ecModel-readiness breakdown (GPR coverage, sequences, DLTKcat-mappability, measured-core enzymes)
   + a recommended ecModel route.
5. thermal/ set up with the Jones-1983 source note + a clearly-flagged PLACEHOLDER TPC CSV (not used).
6. GO/NO-GO for phase M2 with the concrete M2 requirements.

CONSTRAINTS
- Foundation + reconnaissance ONLY. NO ecModel/enzyme-constraint layer, NO thermal layer, NO
  calibration, NO closing of artefacts (phase M2+). Plain FBA on the base GEM.
- Mirror the eciML1515 strain conventions; do not modify the E. coli strain or the shared code beyond
  what is needed to load a second strain.
- Report ACTUAL numbers + honest sanity-check results; flag mismatches.
- Autonomous; commit in parts: "methanogen M1: scaffold strains/mmaripaludis + acquire iMR539 base GEM",
  "methanogen M1: H2/CO2 medium + growth/methanogenesis validation + sanity checks",
  "methanogen M1: preliminary artefact audit + ecModel-readiness reconnaissance + TPC data scaffold".
```
