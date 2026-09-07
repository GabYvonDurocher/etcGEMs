# Claude Code prompt — rebuild the activation-energy paper's Methods + Supplement to the FULL rigor of the E. coli report: not just the equation set, but ALL the descriptive construction sections (the complete layered model, per-enzyme inputs & data provenance, enzyme abundance & the compensation question, the parameter-provenance tables, the Li et al. 2021 relationship & departures), each tailored to BOTH taxa and structured general-then-departures (autonomous)

Run from the project root (`.../MICROADAPT/etcGEMs`). The paper (reports/activation_energy/) now has a
good equation set, BUT it is still missing the DESCRIPTIVE construction sections that make the E. coli
report (reports/ecoli_tpc) comprehensive. Add them — tailored to BOTH E. coli and M. maripaludis, in the
general-framework-then-departures structure. Fully SELF-CONTAINED: bring the content IN from
reports/ecoli_tpc (the unpublished precursor); do NOT cite it. Write-up only; no model re-runs; leave
reports/ecoli_tpc/ unchanged (content SOURCE only). Keep the existing Intro/Results/Discussion and the
equation blocks already added; this pass ADDS the missing prose sections + provenance tables.

NOTE TO USER: launch in an auto-approving mode. Needs quarto. Commit in parts.

THE GAP (explicit): the E. coli report contains these sections, and the paper is missing their equivalents.
Every one must appear in the paper, generalised to a framework common to both taxa and then specialised
per organism. Read them in reports/ecoli_tpc/report.qmd to match their depth and style:
- "# The complete model" — the plain-language FOUR-LAYER overview (Layer 1 network + enzyme budget;
  Layer 2 temperature-dependent enzyme envelope; Layer 3 proteome allocation / sectors / growth law;
  Layer 4 the emergent-a-priori-vs-calibration epistemic stance), each layer described in words before
  any algebra.
- "Inputs and data provenance — what the model uses for each enzyme, and where it comes from" — the
  per-enzyme itemisation (flux = predicted output not input; kcat(T) source; Topt + curvature source;
  Tm / native-fraction source), stating explicitly which quantities are per-enzyme vs whole-cell.
- "Enzyme abundance, and the compensation question" — abundance is an optimisation outcome not an input;
  the implicit least-cost "compensation" as kcat falls with T vs the absence of regulatory sensing
  (a stated limitation).
- "**9 — Parameter provenance**" + the @tbl-provenance table (Symbol | Quantity | Source | Coverage/value).
- "Model hierarchy — how the components link" — the (i)-(vii) forward chain from grounded per-enzyme
  parameters to descriptors.
- "Relationship to, and departures from, the Li et al. 2021 yeast etc-GEM" — what we follow (thermal core)
  and the deliberate departures/upgrades.
- "Validation" — the a-priori validation logic (metric, benchmark) per organism.

---

```
Work AUTONOMOUSLY end to end; commit in parts; print a summary. READ FIRST (to INCORPORATE, not cite):
reports/ecoli_tpc/report.qmd — in particular the WHOLE of "# The complete model" (lines ~80-231: the four
layers + "Inputs and data provenance..." + "Enzyme abundance, and the compensation question") and
"# Model equations, parameters and methods" (the equation blocks, the "9 — Parameter provenance" table
@tbl-provenance, "Model hierarchy", "Relationship to, and departures from, the Li et al. 2021 yeast
etc-GEM", "In-silico experimental design", "Validation") — plus reports/ecoli_tpc/supplementary.qmd. Then
the ACTUAL implementation for accuracy: src/etcgem/{enzyme_cost.py, mmrt.py, unfolding.py, sectors.py,
providers.py, calibration.py, sharpe_schoolfield.py, ea_dissection.py, tpc.py}. Then the methanogen
construction record strains/mmaripaludis/outputs/{M1_audit_and_readiness, M1b_curation, M2_ecmodel,
M2b_kcat_refinement, M3_thermal, M6_sector_layer, M4_calibration}.md. Then the current paper
reports/activation_energy/{report.qmd, supplementary.qmd, assemble.py}. Gurobi only if a figure must be
regenerated.

The paper already has the equation blocks. This pass ADDS the missing DESCRIPTIVE sections below. Keep the
general-framework-then-departures structure throughout: describe the general principle common to BOTH
taxa, then state where E. coli and M. maripaludis differ.

PART A - "The complete model": the FOUR-LAYER plain-language overview (general, then per-taxon)
Add a "The complete model" section (before or wrapping the equation blocks) that describes the etcGEM in
four stacked layers IN WORDS, at the E. coli report's level, GENERAL to both taxa, each layer flagging the
taxon-specific instantiation:
- Layer 1 (network + enzyme budget): FBA on a genome-scale reconstruction made enzyme-constrained (a
  shared proteome pool; per-reaction demand v_i/kcat_i). GENERAL. Departure: E. coli = pre-built GECKO
  ecModel eciML1515 (iML1515, Monk 2017); methanogen = our sMOMENT enzyme layer on iMR539 (Richards 2016).
  Curation departure: E. coli four uncosted-O2-sink closures; methanogen carbon-honest autotroph curation.
- Layer 2 (temperature-dependent enzyme envelope): MMRT kcat(T) + two-state native fraction f_N(T) keyed
  on Tm; the effective per-flux cost rises when catalysis is slow (cold) or the enzyme denatures (hot).
  GENERAL. Departure: parameter provenance (E. coli meltome Tm + Li-Engqvist Topt; methanogen mesophile
  Tm/Topt prior + measured-core kcats).
- Layer 3 (proteome allocation): partition into metabolic / biosynthesis-ribosome / maintenance sectors;
  temperature-dependent NGAM; the growth-law coupling of ribosome fraction to mu. GENERAL. Departure (the
  LOAD-BEARING one): E. coli Scott 2010 rising-ribosome growth law vs methanogen Muller 2021 constant-
  ribosome (flat) strategy.
- Layer 4 (the epistemic stance): the emergent model is an a-priori forward prediction (nothing fit to the
  growth curve); Bayesian calibration is a separate, labelled inverse step over global knobs. GENERAL to
  both.

PART B - "Inputs and data provenance — what the model uses for each enzyme" (general, then per-taxon)
Add this subsection: the model is per-enzyme; for EACH enzyme it uses (i) flux — predicted OUTPUT, not an
input; (ii) turnover kcat(T); (iii) thermal optimum Topt + curvature; (iv) melting temperature Tm / native
fraction. State plainly which are per-enzyme vs whole-cell (only the pool scalars P_total, sigma and the
sector fractions are whole-cell). Then give the SOURCE of each per organism (E. coli: GECKO ref kcat,
Li-Engqvist Topt + DLTKcat, meltome Tm; methanogen: Milton 2018 measured-core SA->kcat + DLTKcat +
literature overrides PFOR/CODH/Mcr + floor, mesophile Topt/Tm prior). Report per-enzyme grounding coverage
for each organism honestly.

PART C - "Enzyme abundance, and the compensation question" (general to both)
Add this subsection (general — it is a structural property of the sMOMENT/GECKO pool, true for both taxa):
per-enzyme abundance is an optimisation outcome, not an input; only sector fractions are supplied. As T
rises and kcat falls (or the enzyme unfolds), carrying the same flux costs more enzyme mass, so the
optimiser draws more pool toward those steps — an implicit least-cost "compensation" — until the pool
binds and growth is throttled. But this is least-cost allocation under a fixed budget, NOT regulatory
sensing (no mechanism detects a falling product and up-regulates a gene): a stated limitation for both
models.

PART D - "Parameter provenance" TABLES (one per organism) + "Model hierarchy"
- Add a "Parameter provenance" subsection with a PROVENANCE TABLE for EACH organism (Symbol | Quantity |
  Source | Coverage/value), mirroring @tbl-provenance in the E. coli report: MW_i/kcat_ref, Topt_i, Tm_i,
  dCp curvature, T_H/T_S, sector fractions, P_lit, sigma, growth-law slope s (E. coli Scott vs methanogen
  ~0 Muller), NGAM constants, validation curve (E. coli Van Derlinden 2012; methanogen Jones 1983). Use
  the ACTUAL values/coverage from the E. coli report and the methanogen M-notes. Two tables (or one table
  with an E. coli column and a M. maripaludis column) — whichever reads cleaner.
- Add the "Model hierarchy — how the components link" (i)-(vii) forward chain (grounded per-enzyme
  parameters -> per-enzyme responses -> cost -> sector constraints + growth law + NGAM(T) -> FBA -> TPC ->
  descriptors; knobs act at the parameter level). General to both.

PART E - "Relationship to, and departures from, the Li et al. 2021 yeast etc-GEM" + "Validation"
- Add the "Relationship to, and departures from, the Li et al. 2021 yeast etc-GEM" subsection: we FOLLOW
  Li 2021 for the thermal core (transition-state kcat(T), two-state Tm-keyed denaturation, T-dependent
  maintenance, the enzyme-pool idea) and DEPART/upgrade in the deliberate ways — TWO taxa (a bacterium and
  an archaeon, the first etcGEMs for both) rather than yeast; grounded (not fitted) per-enzyme parameters
  so the TPC is an a-priori prediction; sector-partitioned proteome + organism-specific allocation law;
  likelihood (emcee) not SMC-ABC; the window-independent Sharpe-Schoolfield E; the control-weighted Ea
  decomposition. Keep this GENERAL (both taxa are descendants of the same framework) and note the
  methanogen-specific departures (sMOMENT rather than pre-built GECKO; measured-core archaeal kcats).
- Add a "Validation" subsection per organism: the a-priori validation logic (E. coli vs Van Derlinden 2012
  BHI; methanogen vs Jones 1983 H2/CO2), the metric, and the emergent-vs-observed SS-E.

PART F - Supplement: keep the exhaustive per-model construction
Ensure the Supplement still holds the full per-organism construction (E. coli build; methanogen M1-M6)
with the honest caveats and the per-enzyme-layer parameter/provenance tables + robustness (window audit,
SS-E fits, calibration corner/prior-vs-posterior, full decompositions, Mcr sweep). If any of the new
main-text provenance tables duplicate supplement tables, cross-reference rather than repeat.

PART G - integrate + build
- Weave the new sections into the existing Methods (equation blocks stay; these prose sections wrap and
  contextualise them). Update cross-references. Keep the paper SELF-CONTAINED (no citation of
  reports/ecoli_tpc). assemble.py collects any needed tables; quarto render report + supplement; build
  clean (no unresolved crossrefs); report page counts.

VERIFY (report all)
1. "The complete model" four-layer plain-language overview present, GENERAL then per-taxon, at the E. coli
   report's depth.
2. "Inputs and data provenance — what the model uses for each enzyme" present, per-enzyme itemisation +
   per-organism sources + grounding coverage.
3. "Enzyme abundance, and the compensation question" present (general to both).
4. "Parameter provenance" TABLE for each organism + "Model hierarchy" (i)-(vii) present.
5. "Relationship to, and departures from, the Li et al. 2021 yeast etc-GEM" present (general + methanogen
   departures); per-organism "Validation" present.
6. Structure is general-framework-then-departures throughout; equation blocks retained; Intro/Results/
   Discussion retained with updated cross-refs.
7. Self-contained: reports/ecoli_tpc NOT cited and unchanged; its content brought in. Supplement holds the
   full per-model construction + provenance + robustness. report + supplement build (page counts).

CONSTRAINTS
- Write-up only; no model re-runs, no re-calibration, no changes to reports/ecoli_tpc. Bring the E. coli
  content IN; never cite the unpublished precursor. Values accurate to src/etcgem + the M-notes.
- General-framework-then-departures; publication-quality prose; every section tailored to BOTH taxa.
- Autonomous; commit in parts: "paper(activation_energy): Methods — complete layered model + per-enzyme inputs/provenance + compensation (both taxa)",
  "paper(activation_energy): Methods — parameter-provenance tables + model hierarchy + Li 2021 relationship/departures + validation",
  "paper(activation_energy): weave, cross-refs, render (self-contained)".
```
