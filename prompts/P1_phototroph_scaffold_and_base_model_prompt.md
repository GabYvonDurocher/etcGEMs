# Claude Code prompt — P1 (phototroph build): lock the phase-0 decisions (strain, light-saturated TPC, target rate) to flip Gate 4 GREEN, then scaffold the cyanobacterium strain dir and stand up a QC'd autotrophic base GEM under a light-SATURATED medium (autonomous)

Run from the project root (`.../MICROADAPT/etcGEMs`). First build step for the LOW-Ea third organism (cyanobacterium)
of the Yvon-Durocher 2014 ordering. Decision locked by the user: target the LIGHT-SATURATED regime so the rate is
RuBisCO / Calvin-cycle (kcat(T))-limited and the organism stays fully IN-MECHANISM (same control-weighted
decomposition as E. coli + methanogen; NO new light-supply layer). This step (a) resolves the remaining phase-0
decisions with data and flips Gate 4 to GREEN, and (b) scaffolds strains/syn6803/ and stands up a QC'd base GEM
growing autotrophically under saturating light. NO thermal layer, NO enzyme layer, NO calibration yet — that is P2+.

NOTE TO USER: launch in an auto-approving mode, from the venv with Gurobi. Web research (GEM + TPC sourcing) +
light compute (FBA forward-checks). Mirrors the methanogen M1 step.

CONTEXT: docs/PHOTOTROPH_ETCGEM_PLAN.md scoped four gates (Base GEM GREEN; Topt/Tm AMBER: Li-Engqvist portable +
mesophile Tm prior; TPC AMBER: digitisable but target-rate unresolved; Light-reactions AMBER-not-RED). The user
chose the light-saturated / in-mechanism regime, which collapses Gate 4: under saturating light the photon-supply
bound is non-limiting and carbon fixation sets the rate, so the framework needs NO new layer. This step confirms
that holds for the chosen strain + TPC and pins the target rate.

TAXON LOCKED BY THE USER (research-backed): **Synechocystis sp. PCC 6803** — the model cyanobacterium and the
only candidate with a pre-built enzyme-constrained ecModel. Use these specific resources (confirm availability,
fall back as noted):
- Base GEM: **iSynCJ816** (Joshi et al. 2020; 816 genes / 1045 reactions), and PREFERENTIALLY the pre-built
  **enzyme-constrained ecModel of Synechocystis 6803** (Sudfeld/de Groot-style "Upgrading a cyanobacterial
  genome-scale model by inclusion of enzymatic constraints", ScienceDirect / Metabolic Engineering 2024,
  S2211926424001966) as the enzyme layer analog of eciML1515. FALLBACK if the ecModel is not cleanly
  downloadable/usable: build sMOMENT on iSynCJ816 from scratch, exactly as done for iMR539.
- Calibration TPC: **Zavrel et al. 2015** (Eng. Life Sci. 15:122, glucose-tolerant Synechocystis 6803 in a
  flat-panel photobioreactor) — growth vs temperature with DOCUMENTED light saturation (saturating red light
  220-360 umol m^-2 s^-1, no photoinhibition to 660): Topt ~35 C, Q10 ~1.70 on the rising limb, inhibition by
  ~44 C. Digitise the temperature response (as for Van Derlinden / Jones). If a finer-grained multi-temperature
  6803 growth curve under saturating light exists, prefer it and cite it; otherwise Zavrel 2015 is the anchor.
- Layer-3 allocation data (for P2/later, note in the handoff): **Zavrel et al. 2019** (eLife 8:e42508, cyanobacterial
  cell economy), **Jahn et al. 2018** (Cell Reports 25:478, growth constrained by light + carbon-assimilation
  proteins), and the temperature-dependent cyanobacterial growth-law treatment (npj Syst. Biol. Appl. 2021,
  "Optimal proteome allocation and the temperature dependence of microbial growth laws"). These are the phototroph
  analog of Scott 2010 / Muller 2021 — the organism's OWN allocation strategy, not a borrowed law.
- Tm: mesophile prior (6803 absent from the Meltome Atlas), same route as the methanogen; 6803 is mesophilic (~35 C).

---

```
Work AUTONOMOUSLY end to end; commit in parts; print a summary + GO/NO-GO for P2. Read first:
docs/PHOTOTROPH_ETCGEM_PLAN.md (the gates + candidate GEMs/TPCs), docs/METHANOGEN_ETCGEM_PLAN.md +
strains/mmaripaludis/{strain.yaml, outputs/M1_audit_and_readiness.md, M1b_curation.md} (the M1 house pattern to
mirror), src/etcgem/{providers.py (from_gem_smoment + how a base GEM + medium are wired), config.py} and
strains/eciML1515/ + strains/mmaripaludis/ layout (to mirror the strain-dir structure). Gurobi (GLPK-abort guard);
print the solver.

PART A - phase-0 decisions: confirm the GEM/ecModel, lock the light-saturated TPC + target rate (flip Gate 4 GREEN)
- STRAIN is LOCKED: Synechocystis sp. PCC 6803. Confirm the base model: try to obtain the pre-built enzyme-
  constrained ecModel (2024) first; if it is not cleanly downloadable/usable, obtain iSynCJ816 (SBML) and plan the
  sMOMENT layer for P2 (as for iMR539). Record which route (pre-built ecModel vs sMOMENT-on-iSynCJ816) and why.
- Confirm + document the CALIBRATION TPC: Zavrel et al. 2015 growth-vs-temperature under saturating light (or a
  finer 6803 curve if one exists) — Topt, range, CTmax, approx rising-limb Ea. CRITICAL: confirm from the paper's
  methods that light was saturating (report the intensity + saturation evidence). If on inspection the anchor curve
  is NOT clearly light-saturated, say so and either (i) find a 6803 curve that is, or (ii) flag Gate 4 as still
  AMBER with the specific reason — do NOT build on an ambiguous-regime curve. Note the figure to digitise.
- Settle the TARGET RATE. For cross-organism symmetry we compare growth-rate-TPC Ea across all three organisms;
  under saturating light, growth-Ea reflects carbon-fixation kcat(T) and is the in-mechanism target. Record this,
  AND note the Yvon-Durocher 2014 caveat (their photosynthesis Ea is a photosynthesis-flux rate): document that we
  will ALSO be able to read a carbon-fixation-flux TPC off the same model as a secondary descriptor for the
  cleanest comparison to 2014, but the primary target-rate is growth (symmetric with E. coli + methanogen).
- UPDATE docs/PHOTOTROPH_ETCGEM_PLAN.md: flip Gate 4 to GREEN (light-saturated => in-mechanism, no new layer) with
  the confirmation, record the locked strain/TPC/target-rate decisions and the Gate 3 target-rate resolution. If
  any decision cannot be cleanly resolved, record it as the remaining blocker instead of forcing it.

PART B - scaffold the strain dir + pull and QC the base GEM
- Create strains/syn6803/ mirroring strains/mmaripaludis/ (strain.yaml, model/, thermal/, outputs/). Pull the
  chosen GEM (SBML from its repository/BioModels/BiGG), load with cobrapy, and QC: reaction/metabolite/gene counts,
  mass-charge balance, presence of the photosystems / Calvin cycle (RuBisCO) / photorespiration, the light/photon
  exchange, and the biomass objective. Record the QC in the readiness note.

PART C - set the light-SATURATED autotrophic medium + forward-check growth
- Configure the medium for photoautotrophic growth under SATURATING light: set the photon/light-uptake bound
  NON-LIMITING (saturating) and CO2/inorganic-C available, so carbon fixation (not photon supply) is rate-limiting
  — this is the encoding that keeps the organism in-mechanism. Confirm the model grows autotrophically (biomass
  flux > 0) with RuBisCO carrying carbon-fixation flux and the photon bound slack (report the photon shadow
  price / that it is non-binding, evidencing light-saturation in-silico). If the base GEM needs light-saturation
  curation to behave (e.g. an unconstrained futile photon route, analogous to the E. coli O2-sink curation),
  document it SCIENTIFICALLY as a curation step (no person-named correction) and record the growth delta.
- Do a plain FBA forward-check across a coarse temperature-free baseline (no thermal layer yet): report autotrophic
  growth rate, the active carbon-fixation flux, and that the photon bound is non-binding. This is the base the
  thermal + enzyme layers (P2) will sit on.

PART D - outputs + GO/NO-GO for P2
- Save the scaffolded strain + base model + medium config, and strains/syn6803/outputs/P1_scaffold_and_base.md:
  the locked phase-0 decisions (strain, light-saturated TPC + evidence, target rate), the GEM QC, the
  light-saturated medium encoding + any curation, the autotrophic forward-check, and confirmation that the photon
  supply is non-binding (in-mechanism). GO/NO-GO for P2 (thermal + enzyme layer), listing what P2 will need
  (Li-Engqvist Topt on the cyano proteome; mesophile Tm prior; kcat sourcing — RuBisCO/Calvin kcats are
  well-measured, unlike the archaeal core). Keep the M4-style magnitude realism in mind for later calibration.

VERIFY (report all)
0. solver=gurobi; strain LOCKED (Synechocystis 6803); base-model route recorded (pre-built ecModel vs
   sMOMENT-on-iSynCJ816); NO thermal/enzyme/calibration layer added.
1. Phase-0 decisions LOCKED: the confirmed base model, a confirmed LIGHT-SATURATED growth TPC (Zavrel 2015 or
   better; light intensity + saturation evidence cited), and the target rate (growth primary; carbon-fixation-flux
   secondary for the 2014 comparison). Gate 4 flipped to GREEN in the plan doc (or the remaining blocker recorded).
2. strains/syn6803/ scaffolded mirroring the methanogen; base GEM pulled + QC'd (photosystems/Calvin/RuBisCO/
   photon-exchange/biomass present; counts + balance reported).
3. Light-saturated autotrophic medium set (photon bound non-limiting, CO2 available); model grows autotrophically
   with RuBisCO carrying flux and the photon bound NON-BINDING (in-mechanism confirmed); any light-saturation
   curation documented scientifically with the growth delta.
4. P1_scaffold_and_base.md written; docs/PHOTOTROPH_ETCGEM_PLAN.md updated (Gate 4); GO/NO-GO for P2.

CONSTRAINTS
- Phase-0 lock + base-model scaffold ONLY. NO thermal layer, NO enzyme/ecModel layer, NO calibration, NO Ea work.
  Do NOT build the light-limited regime or any new light-supply layer (the user chose light-saturated / in-
  mechanism). Mirror the methanogen M1 house style + the strain-dir layout. Scientific curation only (credit in
  acknowledgements, not a person-named correction). Cite every GEM/TPC/light source.
- Autonomous; commit in parts: "docs: phototroph phase-0 decisions locked (strain, light-saturated TPC, target rate); Gate 4 -> GREEN",
  "phototroph P1: scaffold strain dir + QC'd autotrophic base GEM under light-saturated medium".
```
