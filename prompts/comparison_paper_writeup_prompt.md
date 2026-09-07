# Claude Code prompt — write the activation-energy paper to PUBLICATION standard: a self-contained manuscript on the mechanistic basis of the higher thermal sensitivity of methanogenesis vs respiration, with the first etcGEMs for a bacterium and a methanogen (autonomous)

Run from the project root (`.../MICROADAPT/etcGEMs`). Rewrite reports/activation_energy/ as a
PUBLICATION-STANDARD manuscript (report.qmd + supplementary.qmd). This is a major write-up, not a
report update. It must be SELF-CONTAINED: the E. coli model is documented as an unpublished precursor
in reports/ecoli_tpc — you MUST bring that content INTO this paper (methods + supplement) and MUST NOT
cite reports/ecoli_tpc (it is unpublished). Both etcGEMs are the FIRST published for their taxa, so both
need comprehensive construction, update, data-source, validation and tuning documentation. Leave
reports/ecoli_tpc/ unchanged (it is a content SOURCE, not a citation). Write-up only, plus the one
allowed light analysis (the SS-E posteriors for Fig 1). No model re-runs.

NOTE TO USER: launch in an auto-approving mode. Needs quarto. Large — commit in parts.

FRAMING (lean on this): Yvon-Durocher et al. 2014, Nature 507:488-491 ("Methane fluxes show consistent
temperature dependence across microbial to ecosystem scales") established EMPIRICALLY that the thermal
sensitivity (activation energy) of methane flux is HIGHER than that of respiration and photosynthesis,
and that this holds CONSISTENTLY from individual methanogen cultures up to whole ecosystems. That
cross-scale consistency implies the pattern ORIGINATES at the cellular/enzymatic scale. This paper asks:
what MECHANISM at the cellular scale produces the higher thermal sensitivity of methanogenesis? We build
mechanistic enzyme- and temperature-constrained genome-scale models (etcGEMs) of a respiring bacterium
(E. coli) and a hydrogenotrophic methanogen (M. maripaludis) and decompose what sets each organism's Ea.

---

```
Work AUTONOMOUSLY end to end; commit in parts; print a summary. READ FIRST (write from the REAL numbers;
bring E. coli MODEL content in, do not cite the precursor): the finalised analysis assets — outputs/
ea_cross_organism/{final comparison table, figure, NOTE.md}, strains/eciML1515/outputs/ea_dissection_ss/
+ strains/mmaripaludis/outputs/ea_dissection_ss/ (+ decomposition_ss.json), the Mcr sweep, strains/*/
outputs/ea_definition_audit/ + src/etcgem/sharpe_schoolfield.py (SS-E), the calibration outputs (E. coli
calibration_vanderlinden*; methanogen calibration_jones/ incl. posterior draws + prior-vs-posterior TPC);
the E. coli MODEL construction content in reports/ecoli_tpc/{report.qmd, supplementary.qmd} (INCORPORATE,
do not cite); the methanogen build record strains/mmaripaludis/outputs/{M1_audit_and_readiness, M1b_
curation, M2_ecmodel, M2b_kcat_refinement, M3_thermal, M4_calibration, M6_sector_layer}.md; src/etcgem/*
(the actual implementation, for accurate methods); and reports/activation_energy/{report.qmd, assemble.py}.
Gurobi only if a figure must be regenerated (prefer reusing saved figures).

PAPER STRUCTURE (this ORDER — Intro, Results, Discussion, Methods, then the Supplement):

# INTRODUCTION
- The metabolic theory context: temperature dependence of biological rates, the "universal" ~0.65 eV,
  and the OPEN question of what sets it (one rate-limiting step, an aggregate, or thermodynamics).
- The empirical pattern (Yvon-Durocher 2014): methanogenesis Ea > respiration (> photosynthesis),
  consistent from cells to ecosystems -> the pattern originates at the cellular scale, but its MECHANISM
  is unknown. State the question of THIS paper: the cellular/enzymatic mechanism of the Ea difference.
- The approach: mechanistic etcGEMs (enzyme- + temperature-constrained GEMs), the first for these taxa;
  a control-weighted decomposition of a window-independent Ea. Preview the answer in one sentence.

# RESULTS (results-first; each subsection a claim + its evidence)
- FIGURE 1 (SCENE-SETTER, first): the two CALIBRATED Bayesian TPCs side by side — E. coli respiration
  (BHI) and M. maripaludis methanogenesis (H2/CO2) — posterior-predictive median + band + observed data
  (Van Derlinden; Jones 1983), plus the SS-E POSTERIOR distributions (propagate ~200 calibration
  posterior draws per organism through sharpe_schoolfield.py — the one allowed light analysis) shown as
  inset densities/violins, making the SEPARATED Ea posteriors (methanogen ~1.0 vs E. coli ~0.6) obvious.
  Tie explicitly to the 2014 pattern reproduced at the cellular scale.
- Both etcGEMs reproduce their observed TPC and Ea (validation; SS-E model vs observed: 0.68 vs 0.56;
  1.06 vs 1.04; E. coli on the ~0.65 benchmark). This is a genuine prediction, foreground it.
- What sets each Ea: the control-weighted decomposition into 4 NAMED terms (control-weighting, allocation,
  maintenance, aggregation) + the naive enzyme-E mean. Show the SIGNED-CONTRIBUTION comparison figure
  (both organisms; NOT a waterfall). The +0.38 eV gap is STRUCTURAL: control-weighting (methanogen 89% on
  the high-E methanogenesis backbone vs E. coli's broad biosynthesis) + the allocation asymmetry (E. coli
  Scott growth-law buffer −0.13 vs methanogen constant-ribosome flat +0.00, Muller 2021), NOT higher
  intrinsic enzyme temperature-sensitivity (naive mean 0.87 vs 0.51). Robust bottom line = control +
  allocation; aggregation is largest but definition-sensitive (state it).
- Robustness: the Mcr kcat sweep (3-294/s) — ordering and backbone-control robust; leading enzyme not.

# DISCUSSION
- The mechanistic answer to the 2014 pattern: the higher methanogenesis Ea is not thermodynamic (enzymes
  less T-sensitive) but STRUCTURAL — narrow control on the high-E energy backbone + the absence of an
  allocation buffer, each grounded in the organism's own measured physiology. The "universal" Ea is an
  organism-specific, control-weighted, allocation-modulated aggregate: same mechanism, different
  controlling set + allocation strategy.
- Resource-allocation STRATEGY shapes thermal sensitivity (a novel link). Why it matters across scales:
  the cellular mechanism is what propagates to the ecosystem consistency the 2014 paper found.
- Photosynthesis (2014: even lower Ea) as the natural third test -> a cyanobacterium etcGEM. Caveats:
  the aggregation term; the Mcr kcat (pin mesophilic Mcr); two organisms; model-parameter uncertainties.

# METHODS (concise but COMPLETE and SELF-CONTAINED — the detail-heavy version goes to the Supplement)
Comprehensive enough that a reader needs neither the unpublished precursor nor external notes:
- The etcGEM FRAMEWORK: enzyme-constrained GEMs (GECKO / sMOMENT proteome-pool constraint); the thermal
  layer — kcat(T) via MMRT (Hobbs 2013) + DLTKcat (Qiu 2024) + sequence-based Topt (Li-Engqvist 2019),
  two-state unfolding/native fraction keyed on Tm; NGAM(T) maintenance; proteome-sector allocation +
  growth-law coupling; in-vivo saturation (Davidi 2016 / Heckmann 2020). State clearly what we take from
  existing frameworks (Li et al. 2021 yeast etcGEM as the thermal-core precursor) and WHAT WE UPDATED
  (two taxa; measured/ML-grounded per-enzyme params; the sector partition + organism-specific allocation
  law; emcee likelihood calibration vs ABC; the window-independent Sharpe-Schoolfield Ea).
- The E. coli etcGEM: base iML1515 (Monk 2017) -> GECKO ecModel (eciML1515); the O2-sink curation (four
  uncosted reactions closed for physically-interpretable respiration); Van Derlinden 2012 validation;
  the Scott 2010 growth law + measured proteome allocation; Bayesian calibration. (Bring this in from the
  precursor content; do NOT cite the precursor.)
- The M. maripaludis etcGEM: base iMR539 (Richards 2016); carbon-honest autotroph curation (archaellin/
  precursor + SeCys-recycling fixes; Balch-vitamin traces); sMOMENT ecModel with measured-core kcats
  (Milton 2018 Hdr/hydrogenase/Fdh SA->kcat), DLTKcat + literature overrides (PFOR/CODH/Mcr) + a
  documented floor; thermal envelope (mesophile Tm prior); NGAM(T) from measured maintenance (Goyal
  2015); the Muller 2021 constant-ribosome sector layer; Bayesian calibration to Jones 1983.
- The Sharpe-Schoolfield E (Schoolfield 1981) as the window-independent Ea (motivate with the window-
  sensitivity of the naive slope), and the control-weighted decomposition (the 4 named terms;
  non-circular framing: per-enzyme Ea_i are inputs; the result is the aggregation + departure).
- All key DATA SOURCES named with citations; a main-text parameter/data table; solver (Gurobi).

# SUPPLEMENT (supplementary.qmd) — the full construction + robustness detail
- Full per-model construction (the E. coli build; the methanogen M1-M6 build) with the honest curation
  and parameterisation caveats (Mcr uncertainty + sweep, DLTKcat archaeal underprediction + the literature
  overrides, mesophile Tm prior, sector fractions, the neutral-sector confirmation); parameter tables +
  data provenance per enzyme layer; the window-sensitivity audit table + the SS-E fits (model + observed);
  the calibration corner/prior-vs-posterior for each organism; the full decompositions.

STYLE / FIGURES
- PUBLICATION-QUALITY PROSE: flowing paragraphs, not bullet-y notes; a clear narrative arc; measured,
  precise, no overclaiming. Sentence case; consistent notation; every number traceable to the assets.
- Figure 1 = the scene-setter (TPCs + SS-E posteriors). The decomposition figure = SIGNED-CONTRIBUTION
  bars (both organisms), NEVER a waterfall — regenerate if the current asset is a waterfall.
- De-foreground: no results in Intro/Methods (results live in Results); abstract may preview.
- assemble.py: collect the finalised + regenerated figures/tables; quarto render report + supplement;
  build clean (no unresolved crossrefs); report page counts.

VERIFY (report all)
1. Structure is Intro -> Results -> Discussion -> Methods -> Supplement; publication-quality flowing prose.
2. SELF-CONTAINED: the E. coli AND methanogen etcGEM constructions are fully documented in this paper
   (frameworks used, what we updated, data sources, validation, tuning); reports/ecoli_tpc is NOT cited;
   its model content is brought in.
3. Framing on Yvon-Durocher 2014 (pattern -> cellular mechanism); the cross-scale link made.
4. Figure 1 scene-setter (two Bayesian TPCs + separated SS-E posteriors) opens the results; the
   decomposition is signed-contribution (no waterfall); both models validated vs observed SS-E.
5. The mechanism (control + allocation, grounded in each organism's measured allocation strategy) is the
   robust bottom line; aggregation + Mcr caveated; two-organism/photosynthesis-next framing.
6. Full construction + robustness detail in the supplement; report + supplement build (page counts).

CONSTRAINTS
- Write-up to PUBLICATION standard + the ONE allowed light analysis (SS-E posteriors for Fig 1). No model
  re-runs, no re-calibration, no changes to reports/ecoli_tpc. SS-E throughout; slope deprecated. NO
  waterfalls. Self-contained (bring E. coli model content in; never cite the unpublished precursor).
- Autonomous; commit in parts: "paper(activation_energy): intro (Yvon-Durocher 2014 framing) + results (scene-setter Fig 1 + validation)",
  "paper: results (signed-contribution decomposition + Mcr robustness) + discussion",
  "paper: comprehensive self-contained methods (both etcGEM constructions, frameworks, data, calibration, SS-E)",
  "paper: supplement (full construction + robustness) + render".
```
