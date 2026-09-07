# Claude Code prompt — fold the phototroph in: rewrite the activation-energy paper as a THREE-organism manuscript that reproduces AND mechanistically explains the full Yvon-Durocher 2014 ordering (methanogenesis > respiration > photosynthesis) as THREE DISTINCT routes, fully self-contained and publication-standard (autonomous)

Run from the project root (`.../MICROADAPT/etcGEMs`). The paper (reports/activation_energy/) is currently a TWO-organism
manuscript (E. coli respiration vs M. maripaludis methanogenesis). The phototroph build (P1-P4, Synechocystis 6803) is
now complete and reproduces the LOW-Ea third point, so the paper must become a THREE-organism manuscript. This is a major
revision, not an addition: the central question BROADENS from "why is methanogenesis Ea higher than respiration" to "what
cellular mechanisms underpin the FULL thermal-sensitivity ordering methanogenesis > respiration > photosynthesis" — the
complete 2014 pattern, reproduced and explained from mechanism as THREE DISTINCT ROUTES. Keep it SELF-CONTAINED (bring
E. coli model content IN; never cite reports/ecoli_tpc, which stays unchanged as a content source). Write-up only, plus
the ONE allowed light analysis (the phototroph SS-E posterior for Fig 1). No model re-runs.

NOTE TO USER: launch in an auto-approving mode. Needs quarto. Large — commit in parts.

FRAMING (unchanged spine, widened): Yvon-Durocher et al. 2014 (Nature 507:488-491) established EMPIRICALLY that the
activation energy of methane flux > respiration > photosynthesis, consistently from cells to ecosystems — implying the
pattern ORIGINATES at the cellular/enzymatic scale. This paper builds mechanistic etcGEMs of all THREE metabolic
strategies (a hydrogenotrophic methanogen, a respiring heterotroph, an oxygenic phototroph) and decomposes what sets each
organism's Ea, reproducing the full ordering and explaining it as three distinct mechanisms.

---

```
Work AUTONOMOUSLY end to end; commit in parts; print a summary. READ FIRST (write from the REAL numbers): the finalised
THREE-WAY assets outputs/ea_cross_organism/{comparison_table_3way.csv, cross_organism_signed_contributions_3way.png,
NOTE_3way.md}; the phototroph build record strains/syn6803/outputs/{P1_scaffold_and_base.md, P2_thermal.md (or
P2_thermal/), P3... calibration_zavrel/, P3b_sector_layer.md, ea_dissection_ss/ + robustness_sweep.json}; the existing
E. coli + methanogen dissections strains/{eciML1515,mmaripaludis}/outputs/ea_dissection_ss/; the calibration outputs for
all three (E. coli calibration_vanderlinden*; methanogen calibration_jones/; phototroph calibration_zavrel/ incl.
posterior draws); the E. coli MODEL construction content in reports/ecoli_tpc/{report.qmd, supplementary.qmd} (INCORPORATE,
do not cite); src/etcgem/* (for accurate methods, esp. sharpe_schoolfield.py, sectors.py, providers.py); and the CURRENT
paper reports/activation_energy/{report.qmd, supplementary.qmd, assemble.py} (the two-organism version to revise). Gurobi
only for the one light analysis (Fig 1 phototroph SS-E posterior); otherwise reuse saved figures.

THE THREE-WAY RESULT (write to these numbers; SS-E throughout):
- Descriptors + validation: methanogen SS-E 1.06 (obs 1.04); respiration 0.68 (obs 0.56, on the ~0.65 benchmark);
  photosynthesis 0.57 (obs 0.52). All three match observed.
- Decomposition (naive enzyme-E mean + control + allocation + maintenance + aggregation = organism SS-E):
  * Methanogenesis 1.06: naive 0.51 + control +0.34 + allocation 0.00 + maintenance -0.02 + aggregation +0.22.
  * Respiration 0.68:   naive 0.87 + control +0.11 + allocation -0.13 + maintenance +0.01 + aggregation -0.17.
  * Photosynthesis 0.57: naive 0.68 + control -0.02 + allocation -0.02 + maintenance -0.03 + aggregation -0.05.
- THREE DISTINCT ROUTES: methanogenesis high = narrow control (89%) on a HIGH-E energy backbone + no allocation buffer;
  respiration mid = high enzyme E BUFFERED DOWN by the Scott allocation buffer; photosynthesis low = control sits on a
  LOW-E carbon-fixation/Calvin backbone (RuBisCO/TKT/FBA/PRK/FBPase, mean E 0.63 < proteome 0.68) with only small buffers.
- Allocation grounded per organism: E. coli Scott rising-ribosome (-0.13); methanogen Muller constant-ribosome (0.00);
  phototroph Jahn shallow-RIB (-0.02). Robustness: methanogen Mcr 3-294/s sweep; phototroph RuBisCO/Calvin kcat sweep
  leaves SS-E invariant [0.565,0.577] (a SHAPE property) + the shared dCp prior scales all three together.

PART A - Introduction (widen to three strategies)
Reframe the question from the two-organism version to the FULL ordering: the metabolic-theory context + the "universal"
~0.65 eV and the open question of what sets it; the 2014 pattern (methanogenesis > respiration > photosynthesis, cells to
ecosystems -> cellular origin); the approach (the first etcGEMs of all three strategies; a control-weighted, window-
independent SS-E decomposition). Preview the answer: the ordering is reproduced and arises from THREE DISTINCT routes,
not one mechanism scaled.

PART B - Results (three-organism)
- FIGURE 1 (SCENE-SETTER): the THREE calibrated Bayesian TPCs side by side — methanogenesis (H2/CO2, Jones), respiration
  (BHI, Van Derlinden), photosynthesis (light-saturated autotrophy, Zavrel) — posterior-predictive median + band +
  observed points, PLUS the three SS-E POSTERIOR distributions as insets, making the SEPARATED, correctly-ORDERED Ea
  posteriors obvious (methanogen ~1.06 > E. coli ~0.68 > phototroph ~0.57). Propagate ~200 phototroph calibration_zavrel
  posterior draws through sharpe_schoolfield.py (the ONE allowed light analysis; E. coli + methanogen posteriors already
  exist — reuse). Tie explicitly to the 2014 pattern reproduced at the cellular scale.
  * PLOT RANGE — do NOT show the model curve far outside the data. For EACH organism, restrict the plotted temperature
    axis to its supported range: begin near the LOWEST observed temperature and extend only slightly (a few C) beyond the
    HIGHEST observed temperature. This matters most for the PHOTOTROPH, whose model currently runs well past the Zavrel
    points at both ends — clip the phototroph panel to start close to the lowest Zavrel measurement and stop just beyond
    the highest. Keep the observed points and the posterior band within this data-supported window; no long extrapolated
    tails.
  * POSTERIOR STYLE — render the three SS-E posteriors as VIOLIN plots (the style used in the earlier two-organism
    figure), NOT histograms.
- Validation: all three etcGEMs reproduce their observed TPC and SS-E (foreground: genuine predictions; E. coli on the
  ~0.65 benchmark; the phototroph independently corroborated by the Inoue 2001 light-saturated O2-evolution Ea 0.52).
- What sets each Ea: the THREE-way control-weighted decomposition (the table above) as the SIGNED-CONTRIBUTION figure
  (cross_organism_signed_contributions_3way.png; NOT a waterfall). Explain the three routes; foreground that the phototroph
  is the MIRROR IMAGE of the methanogen (low-E vs high-E controlling backbone), with E. coli's allocation buffer as the
  third, distinct route. State the robust bottom line per organism + the honest definition-sensitivity of the aggregation
  term.
- Robustness: methanogen Mcr sweep; phototroph RuBisCO/Calvin kcat invariance (the low Ea is a shape property).

PART C - Discussion
- The mechanistic answer to 2014: the ordering is NOT one mechanism scaled but THREE DISTINCT routes to a position in the
  Ea range — a high-E controlling backbone (methanogenesis), an allocation buffer on high enzyme E (respiration), and an
  intrinsically low-E controlling backbone (photosynthesis). The "universal" Ea is therefore an organism-specific, control-
  weighted, allocation-modulated aggregate whose VALUE depends on WHERE control sits (high- vs low-E enzymes) and HOW MUCH
  allocation buffers it.
- Resource-allocation STRATEGY and the intrinsic E of the CONTROLLING pathway TOGETHER set thermal sensitivity (the novel
  link). Why it matters across scales: the cellular mechanism is what propagates to the ecosystem consistency 2014 found.
- Phototroph-specific honesty: the result is for the LIGHT-SATURATED (carbon-fixation-limited) regime; under light
  LIMITATION a temperature-insensitive photon supply lowers Ea further (the Inoue Fig 1 light-limited curve; Topt 25 vs
  35) — so field/ecosystem photosynthesis Ea may be even lower for a reason OUTSIDE the enzyme mechanism. State this as a
  scope boundary + a future refinement (a temperature-dependent RuBisCO CO2/O2 specificity term for ambient-CO2 regimes).
- Caveats: the aggregation term definition-sensitivity; the per-organism kinetic sweeps; three organisms are three
  strategies, not a phylogeny; the mesophile Tm priors. Future: within-strategy diversity (thermophiles) as the next axis.

PART D - Methods (extend the comprehensive, self-contained construction to the THIRD organism)
Keep the GENERAL etcGEM framework + full equation set + the descriptive construction sections (The complete model /
four layers; per-enzyme Inputs and data provenance; Enzyme abundance & the compensation question; Parameter-provenance
tables; Model hierarchy; Relationship to & departures from Li et al. 2021; Validation) that the paper already has for
E. coli + methanogen, and ADD the phototroph throughout:
- The "Taxon-specific construction and departures" section + summary table gains a THIRD column (Synechocystis 6803):
  base GEM iSynCJ816 + the pre-built enzyme-constrained ecModel (route analog of eciML1515); the LIGHT-SATURATED /
  in-mechanism curation (photon supply non-limiting so carbon fixation sets the rate — confirmed by a zero photon shadow
  price; the photorespiration caveat under CO2-replete conditions); kcat provenance (ecModel + well-measured RuBisCO/
  Calvin kcats); mesophile Topt/Tm prior; the Jahn 2018 shallow-RIB allocation law (vs Scott vs Muller); NGAM(T) from
  Touloupakis 2015 + the Suzuki 2006 maintenance-sector temperature response; Zavrel 2015 validation (+ Inoue 2001
  cross-checks); Davidi/Heckmann saturation.
- Add the phototroph Parameter-provenance TABLE (Symbol | Quantity | Source | Coverage) and its per-enzyme Inputs/
  provenance paragraph, at the same depth as the other two. Data sources named: iSynCJ816 (Joshi 2020), the ecModel
  (2024), Jahn 2018 + Zavrel 2019 + Faizi 2018 (allocation), Suzuki 2006 (maintenance T-response), Touloupakis 2015
  (NGAM), Zavrel 2015 + Inoue 2001 (validation).
- The SS-E + control-weighted decomposition Methods stay general (now applied to three organisms).

PART E - Supplement (full three-model construction + robustness)
Add the full phototroph construction (P1 scaffold + light-saturated base; P2 thermal envelope; P3 calibration to Zavrel
incl. the observed-SS-E CI + the shape-first Ea-lever diagnostic; P3b the Jahn/Zavrel/Suzuki allocation layer; P4
dissection) with the honest caveats (mesophile Tm prior, the light-saturated-vs-limited regime choice, the photorespiration
scope boundary), per-enzyme-layer parameter/provenance tables, the RuBisCO/dCp robustness sweep, the Inoue light-saturated-
flux + light-limited cross-checks, the calibration corner/prior-vs-posterior. Keep the E. coli + methanogen supplements.

PART F - integrate + build
- Update the abstract + all cross-references for three organisms. Ensure self-contained (no citation of reports/ecoli_tpc).
  assemble.py collects the three-way figure/table + the Fig 1 three-panel scene-setter; quarto render report + supplement;
  build clean (no unresolved crossrefs); report page counts.

VERIFY (report all)
1. Structure Intro -> Results -> Discussion -> Methods -> Supplement; publication-quality prose; the question widened to
   the full three-strategy ordering.
2. Fig 1 = three-TPC scene-setter with three SEPARATED, correctly-ordered SS-E posteriors (phototroph posterior computed;
   others reused); all three validated vs observed (incl. the phototroph Inoue-flux corroboration).
3. Three-way signed-contribution decomposition (no waterfall); the THREE DISTINCT ROUTES explained (methanogen high-E
   backbone; respiration allocation buffer; phototroph low-E Calvin backbone); robust bottom line + aggregation caveat.
4. Discussion makes the "not one mechanism scaled — three routes" point + the allocation-strategy/controlling-pathway-E
   link + the light-saturated-vs-limited scope boundary.
5. Methods + Supplement extend the full self-contained construction to Synechocystis (departures table 3rd column;
   provenance table; per-enzyme inputs; all sources cited); reports/ecoli_tpc NOT cited and unchanged.
6. report + supplement build (page counts).

CONSTRAINTS
- Write-up to PUBLICATION standard + the ONE allowed light analysis (phototroph SS-E posterior for Fig 1). No model
  re-runs, no re-calibration, no changes to reports/ecoli_tpc. SS-E throughout; slope deprecated. NO waterfalls. Self-
  contained (bring E. coli model content in; never cite the unpublished precursor). Each organism's allocation grounded
  in its own measured strategy; each carries its kinetic sensitivity caveat; the phototroph light-saturated scope stated.
- Autonomous; commit in parts: "paper(activation_energy): reframe to three strategies — intro + Fig 1 three-TPC scene-setter (+ phototroph SS-E posterior)",
  "paper: results (three-way decomposition, three routes) + discussion (not-one-mechanism-scaled + light-saturation scope)",
  "paper: Methods + Supplement — extend self-contained construction to Synechocystis (departures table, provenance, robustness); render".
```
