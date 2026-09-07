# Plan: assembling an etcGEM for a methanogen

_Scoping document. The aim is a methanogen etcGEM, parallel to the E. coli one, so we can ask what
sets the activation energy (Ea) of methanogenesis and compare it mechanistically to respiration._

## 1. Why, and the hypothesis

We have shown empirically that methanogenesis tends to have a higher Ea than respiration. The
etcGEM framework lets us ask *why*, mechanistically. The sharp, falsifiable hypothesis: the high
methanogenesis Ea is set by the temperature sensitivity of the rate-controlling step(s). The leading
candidate is **methyl-coenzyme-M reductase (Mcr)** — the famously slow terminal, methane-releasing
enzyme (F430 cofactor). A second candidate is **Mtr** (methyl-THMPT:HS-CoM methyltransferase), which
Goyal 2016 confirms is the *only* membrane-bound step and the one that conserves energy by
translocating Na+ (driving the A1A0 ATP synthase). Crucially, in a hydrogenotroph methanogenesis is
the *only* energy-generating pathway and CO2 is both electron acceptor and carbon source, so growth
and CH4 are tightly coupled and the growth Ea's control should fall squarely on the methanogenesis
enzymes — a clean, testable prediction. The Ea-dissection machinery being built on E. coli
(control-weighted aggregation of per-enzyme Eas) applies directly.

A powerful ADDITIONAL comparison the reviews surface: the order *Methanococcales* contains close
thermophilic relatives with the SAME hydrogenotrophic methanogenesis but temperature optima >65 C
(e.g. *Methanocaldococcus jannaschii*, which has its own GEM and a well-characterised proteome).
That gives a within-metabolism, across-thermal-niche test — is the methanogenesis Ea different in the
thermophile, and is it explained by the same controlling enzyme (Mcr) with shifted thermal
parameters? This complements the across-metabolism comparison (methanogen vs E. coli vs
cyanobacterium) and is a natural second methanogen once the mesophile pipeline works.

## 2. Organism choice: Methanococcus maripaludis (recommended)

**M. maripaludis S2** is the cleanest first methanogen:

- **Hydrogenotrophic** (CO2 + H2 -> CH4): a single, clean methanogenesis route (the Wolfe cycle),
  terminating in Mcr — ideal for a clean Ea attribution. Contrast with *Methanosarcina*, which has
  multiple methanogenesis routes (acetoclastic + methylotrophic + hydrogenotrophic) and a messier
  attribution.
- **Mesophilic** (optimum ~38 C, range 20-45 C). This is important: it keeps the thermal-stability
  (Tm) and Topt assumptions in the same regime as E. coli, so the biggest data gap (Tm) is far less
  severe than it would be for a thermophile.
- **Defined minimal medium**, genetically tractable, relatively fast-growing for a methanogen
  (mu_max ~0.23 h^-1 — note ~10x slower than E. coli, so the proteome/enzyme budget will bind very
  differently; the model must reflect slow growth).
- Good published GEM (see Gate 1), and — usefully — existing proteome-allocation and maintenance-
  energy data (see Gate 2/Layer 3).

**Fallback:** *Methanosarcina barkeri* (iMG746) or *M. acetivorans* (iMB745/iMAC868) — more complete,
more versatile GEMs, but the multi-route methanogenesis complicates the Ea story.

## 3. The three feasibility gates (researched)

| Gate | Status | Detail |
|------|--------|--------|
| **Base GEM** | GREEN | Two GEMs exist. **iMM518** (Goyal et al. 2014) — 570 reactions, 556 metabolites, 518 genes (30% ORF coverage), 52 pathways; gene essentiality validated (278/518 essential, cross-checked against Tn5 data); the model the review's group uses for C/N-source and maintenance work. **iMR539** (Richards et al. 2016, *J Bacteriol*) — explicit hydrogenotrophic methanogenesis + central electron bifurcation, 93% knockout accuracy, SBML on BioModels (BIOMD0000001099). iMR539's explicit electron-bifurcation energetics may be the better substrate for our enzyme-cost layer; iMM518 is broader/validated. Fallbacks: iMG746, iMB745, iMAC868. Note both are smaller than iML1515 (methanogen central metabolism + methanogenesis), which is fine — even helpful — for a clean Ea attribution. |
| **Tm / thermal stability** | AMBER (manageable) | The **Meltome Atlas** (Jarzab et al. 2020, *Nat Methods*; 48,000 proteins, 13 species archaea->human, Tm 30-90 C) covers archaea and thermophiles but **not a methanogen**, so no direct Tm for our organism. Viable routes: (a) because M. maripaludis is mesophilic (~38 C), a mesophile Tm distribution (e.g. the E. coli meltome we already use) is a defensible first-pass prior; (b) train a sequence-based Tm predictor on the Meltome Atlas cross-species data; (c) scale to growth temperature. The mesophile choice is what keeps this amber rather than red. |
| **Calibration TPC** | GREEN | **Jones, Paynter & Gupta 1983** (*Arch Microbiol* 135:91-97), the original species description, **Fig 2** is a full growth-rate TPC for the type strain JJ (DSM 2067) on defined H2/CO2 medium: mu_max ~0.18-0.19 h^-1 at ~37-38 C, Topt 35-39 C, range 18-47 C, CTmax ~48 C, rough rising-limb Ea ~0.6-0.8 eV. Needs proper digitising (as we did for Van Derlinden; only 2 experiments averaged, so modest but usable). KEY ADVANTAGE: for a hydrogenotrophic methanogen all catabolism flows through methanogenesis, so growth and CH4 are tightly coupled and this growth TPC's Ea IS essentially the methanogenesis Ea — no respiration/fermentation split to disentangle (unlike E. coli). Note: the curve is the type strain JJ; the GEM iMR539 is strain S2 (same species) — use JJ's own curve for the fit. |

## 4. Layered build: what is portable vs what needs sourcing

The entire `src/etcgem` pipeline (kcat(T), unfolding, enzyme pool, sectors, TPC engine, sensitivity/
decomposition/control, calibration) is organism-agnostic. Building the methanogen etcGEM = a new
`strains/<methanogen>/` with its own model + thermal params + config. Per layer:

- **Base GEM** -> source iMR539 (SBML from BioModels), quality-check, set the medium (H2/CO2 defined
  medium). *New (sourcing).*
- **Enzyme constraints (ecModel)** -> GECKO-ify iMR539: assign kcats + the enzyme-mass pool. Archaeal
  kcats are sparse in BRENDA, so lean on **DLTKcat** sequence predictions (already in our pipeline)
  as a prior — BUT for the energy-conserving CORE (where the Ea control should concentrate) there is
  MEASURED kinetics: Milton et al. 2018 (*Biochemistry*) gives specific activities (25-165 U/mg) and
  redox thermodynamics for the three heterodisulfide-reductase / flavin-based-electron-bifurcation
  complexes (Vhu/Fdh hydrogenases + Hdr), and classic biochemistry covers Fdh, Mcr, Mtr. So the
  enzymes that matter most for the Ea attribution can be parameterised from data, not just prediction.
  A quantitative *M. maripaludis* proteome exists too (Xia et al. 2006/2009; ~939 of 1722 ORFs, with
  chemostat abundances under H2/N/P limitation) — use it to validate the predicted enzyme-mass pool
  (as we did with the E. coli measured proteome) and to inform allocation. *New, but data-rich.*
- **kcat(T) / Topt** -> MMRT machinery is portable; per-enzyme Topt from the Li-Engqvist sequence
  predictor (works from any sequence). *Portable + archaeal-accuracy caveat.*
- **Tm / unfolding** -> the key gap (Gate 2). Start with a mesophile Tm prior; upgrade to a
  meltome-trained sequence predictor. *New.*
- **Proteome pool / sectors / growth law / NGAM / GAM** -> do NOT port the bacterial Scott growth law
  blindly: M. maripaludis has a documented *alternative resource-allocation strategy* (Muller et al.,
  *PNAS* 2021), and — importantly — Goyal et al. 2015 (*Microb Cell Fact*) MEASURED the extracellular
  CO2/H2/CH4 fluxes and gives a procedure to estimate BOTH growth-associated (GAM) and non-growth-
  associated (NGAM) maintenance. So the maintenance layer has organism-specific numbers, not borrowed
  ones — a major de-risk. Start simple (static measured allocation + measured NGAM) and add a
  growth-law coupling only if the allocation data support it. *Adapt, with organism-specific data available.*
- **Calibration** -> fit to a methanogen growth and/or CH4-flux TPC once curated (Gate 3). *New.*

## 5. Phased plan

0. **Data gather + go/no-go.** Pull iMR539; confirm/curate a temperature TPC (growth and/or CH4);
   collect the allocation + maintenance-energy values; decide the Tm route. This phase resolves the
   two amber gates before any building.
1. **Base -> ecModel.** GECKO-ify iMR539 with DLTKcat kcats; validate the emergent (untuned)
   methanogenesis + growth at the reference temperature against known mu_max (~0.23 h^-1) and yield.
2. **Thermal layer.** Add per-enzyme Topt (sequence), Tm (chosen route), kcat(T) MMRT; generate the
   emergent growth + CH4 TPCs.
3. **Allocation / maintenance.** Apply the measured proteome allocation + NGAM(T); check the slow-
   growth regime binds sensibly.
4. **Calibrate.** Bayesian tuning to the methanogen TPC (reuse the emcee machinery), same provenance-
   prior philosophy.
5. **Ea dissection + cross-organism comparison.** Run the Ea-dissection (control-weighted
   decomposition) and test the Mcr hypothesis; compare the Ea mechanism to E. coli (respiration).

## 6. Key risks / caveats

- **kcat coverage for archaeal enzymes** (BRENDA sparse; DLTKcat untested on archaea) — still the
  main parameterisation uncertainty for the biosynthetic bulk, but substantially reduced for the
  energy-conserving core, which now has measured kinetics (Milton 2018) and a measured proteome (Xia
  2006/2009). Treat DLTKcat predictions as priors; anchor the methanogenesis/electron-bifurcation
  enzymes on the measured values.
- **Tm data** — mitigated by the mesophile choice + a meltome-trained predictor, but still a prior.
- **Unusual energetics (a major structural departure from E. coli)** — there is NO cytochrome
  electron transport chain. Energy is conserved by a *single* membrane step, Mtr (Na+ translocation),
  driving an A1A0-type ATP synthase, with Hdr electron bifurcation setting the electron flow and a
  fractional ATP yield per methane. The base GEM must represent this correctly, and the enzyme costs
  of the energy-conserving steps (Mtr, Mcr, the hydrogenases, Hdr) are exactly where the Ea control
  should concentrate — so getting their kcats/costs right matters as much as the ETC did for E. coli.
  Repeat the per-organism "uncosted energy side-reaction" audit before trusting flux attribution.
- **Slow growth** — the proteome budget binds differently than in fast-growing E. coli; expect the
  controlling enzyme set (and thus the Ea mechanism) to differ, which is exactly the comparison we
  want.
- **Per-organism artefact audit** — repeat the "uncosted energy side-reaction" audit (the O2-sink fix
  on E. coli) for the methanogen's own free reactions before trusting flux attribution.

## 7. Open decisions

1. Organism: M. maripaludis (recommended) vs a Methanosarcina. And, if M. maripaludis, which base
   GEM — iMR539 (explicit electron bifurcation, likely better for the energetics/Ea) vs iMM518
   (broader, essentiality-validated). Lean: start from iMR539.
2. Calibration target: RESOLVED for growth — the Jones 1983 Fig 2 growth-rate TPC (type strain JJ),
   which for a hydrogenotroph doubles as the methanogenesis TPC. Open sub-question: is the digitised
   rising-limb Ea of this curve (rough ~0.6-0.8 eV) actually higher than E. coli's, or is the
   "methanogenesis Ea > respiration" pattern an across-system/aggregate result? The etcGEM's job is to
   explain THIS organism's Ea (Mcr hypothesis) regardless, but knowing the empirical target sharpens
   the comparison.
3. Tm route: mesophile prior first, or invest in a meltome-trained sequence predictor up front.
4. Whether to build this in the same repo as a sibling strain (`strains/<methanogen>/`, feeding a
   future `reports/activation_energy/`) — recommended, since the machinery and the Ea comparison are
   shared.
