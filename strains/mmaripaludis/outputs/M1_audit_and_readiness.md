# iMR539 (M. maripaludis) — M1 foundation: artefact audit, ecModel-readiness, GO/NO-GO

Foundation phase. **Plain FBA only** — no ecModel/thermal/calibration layer, and no
artefacts closed here (candidates are *listed* for M2). Numbers are the actual model
outputs; sanity checks are reported honestly including where the base GEM falls short.

## Base model
- iMR539 (Richards et al. 2016), BioModels **BIOMD0000001099**, ModelSEED-style SBML.
- **688 reactions / 710 metabolites / 539 genes** (matches the plan), objective `biomass0`.
- Loads cleanly in cobra (glpk); grows on the defined H2/CO2 medium; Wolfe cycle wired
  correctly (H2:CO2:CH4 = 4.12:1.06:1, theory 4:1:1). See `medium_validation.json`,
  `baseline_pfba.json`, `media/H2CO2_defined.md`.

## PART C — preliminary flux-level artefact audit (candidates only; NOT closed)

**1. Free biomass-precursor exchanges (TOP artefact).** Four biomass components have no
biosynthesis route; the model cannot grow unless they are supplied by free exchange
(closing any one -> mu = 0):
`Membrane_lipid`, `Flagellin`, `NAC` (cell-wall NDP-sugar), `tRNA(SeCys)`.
→ M2: gap-fill their biosynthesis (or treat as a defined supplement) so carbon/mass
balance is honest. Left open in M1 so the published model runs.

**2. Organic-carbon leak exchanges.** `Acetate` and `octadecenoate` open bidirectionally
in the shipped model — spurious organic-C uptake on a supposedly autotrophic medium.
→ Closed in the M1 defined medium already; keep closed in M2.

**3. Pinned methane exchange.** Shipped model **fixes** CH4 exchange at (50, 50) — a hard
non-physiological constraint. → Freed to (0, 1000) in M1 so methane is emergent.

**4. Thermodynamic energy/currency loops: NONE.** With all exchanges closed, **0 of 629**
internal reactions can carry flux "from nothing" — no ATP/currency-generating cycles.
The network is energetically clean. (Preliminary: a fuller loopless-FVA on the growing
model can be run in M2, but no from-nothing cycle exists.)

**5. Implausibly-large fluxes.** None that are artefactual. H2 uptake rails to its 1000
availability bound and absolute rates are correspondingly large — inherent to *unpinned*
plain FBA (rates set by availability, not enzymes), resolved by the M2 enzyme ceiling, not
a network defect.

## PART D — ecModel-readiness reconnaissance

- **GPR coverage: 84% of internal reactions (527/629); 85% of metabolic, non-transport
  reactions (506/593).** The 36 transport/diffusion reactions are mostly ungated (passive)
  as expected. Strong coverage for an sMOMENT/GECKO enzyme layer.
- **Core methanogenesis enzymes present WITH genes and flux:** Mcr (`rxn03127`, McrABG
  MMP1555-1557), Mtr (`rxn03020`), formylmethanofuran dehydrogenase Fwd/Fmd (`rxn11938`,
  `rxn02431`), Hmd (`rxn06696`), methylene-H4MPT steps (`rxn03085`), HdrABC (heterodisulfide
  reductase), F420-reducing hydrogenase (`rxn06299`), Na+-translocating A1A0 ATP synthase
  (`ATPS`), FNO. The energy-conserving backbone is fully gene-annotated.
- **Sequences obtainable:** genes are MMP locus tags (e.g. MMP1555) → UniProt reference
  proteome **UP000000590** (M. maripaludis S2). Directly fetchable for DLTKcat.
- **DLTKcat-mappability:** DLTKcat needs (protein sequence, substrate SMILES). Sequences via
  UP000000590; substrates are ModelSEED `cpd` IDs → SMILES via ModelSEED/KEGG cross-refs.
  Both sides are resolvable; kcat coverage is built and reported in M2.
- **Recommended ecModel route:** **Python sMOMENT reusing `src/etcgem/enzyme_cost`** (as for
  eciML1515), not external GECKO — keeps one code path and the thermal/MMRT + two-state
  layer plugs in unchanged. Needs: per-reaction kcat (DLTKcat + BRENDA/SABIO fallback),
  MW from UP000000590, and the lumped proteome pool.

## PART E — calibration TPC scaffold
- `thermal/sources/jones1983_archmicrobiol/SOURCE.md` — Jones, Paynter & Gupta 1983
  (Arch Microbiol 135:91-97, Fig 2), optimum ~38 C, range ~18-47 C, mu_max ~0.18-0.19/h.
- `thermal/mmaripaludis_tpc_curves.csv` — **PLACEHOLDER** (every row flagged), to be
  digitised in M2.

## PART F — GO / NO-GO for phase M2

**GO.** Rationale:
1. Base GEM acquired, loads, and reproduces hydrogenotrophic methanogenesis with the
   correct 4:1:1 stoichiometry and a gene-annotated Wolfe cycle.
2. No thermodynamic energy-loop artefacts; the two real artefacts (free biomass precursors;
   organic-C leaks) are identified, bounded, and have clear M2 remedies.
3. ecModel-readiness is strong: 85% metabolic GPR coverage, core enzymes gene-mapped,
   sequences + substrates resolvable for DLTKcat, and a clear Python-sMOMENT route reusing
   existing code.
4. Calibration data source identified and scaffolded.

**Conditions to carry into M2 (in order):**
- (a) Gap-fill / resolve the four required biomass precursors so growth is carbon-honest.
- (b) Build the ecModel (Python sMOMENT, reuse `enzyme_cost`) with DLTKcat kcats + UP000000590 MWs.
- (c) Digitise the Jones 1983 TPC to replace the placeholder.
- (d) Optionally restore formatotrophic growth (base GEM does not support formate/CO2 growth;
  M. maripaludis is a known formatotroph) — only if formate TPCs are needed.
