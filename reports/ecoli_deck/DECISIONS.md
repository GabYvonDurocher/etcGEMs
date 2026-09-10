# E2 — decisions and judgement calls

Kept from the first judgement call.

---

## D0. **E1 has not been run, and this deck's inputs were rebuilt from primary sources**

The prompt says "Run this AFTER E1 finishes … E1's `brief.md` and `corrections.csv` are inputs
here", and lists `reports/E1_paper_register/` under "read first". **That directory does not exist**
— not on `main`, not on any branch, and not anywhere in the history (`git log --all
--diff-filter=A --name-only` finds no `E1_`, `paper_register`, `brief.md` or matching
`corrections.csv`). There is no `e1/*` branch on the remote and no commit prefixed "E1:". Only the
prompt `prompts/E1_ecoli_paper_restructure_register_prompt.md` exists.

**Decision: proceed, and rebuild the two things E2 actually needs from primary sources rather than
wait or guess.** E2 uses E1 for exactly two purposes, and both are obtainable directly:

* **The UNSUPPORTED status of the old E. coli intervals.** E1's own prompt states the basis:
  `tbl-corrections` and every 90 % CI in the calibration section come from the "P2 v3 posterior",
  and P8, P11 and P12 established that intervals from this family's emcee chains are not
  available. That is verifiable here without E1 — `reports/ecoli_gasflux/README.md`'s standing
  banner and `docs/OPEN_ITEMS.md` 1.12 say the same thing in the repository's own words, and
  `reports/P12_modes/` shows the mode structure that makes a single interval meaningless. **No
  interval from that family reaches a slide.**
* **The gas-flux inventory.** `reports/ecoli_gasflux/README.md` (118 lines) and its fourteen
  committed figures are the source E1 would itself have read.

**What is therefore NOT in this deck, and would have been:** E1's sentence-by-sentence correction
register, and its restructure options for `report.qmd`. The deck presents the state of the science;
it makes no claim about how the paper should be reorganised, because the run that was to establish
that has not happened. Recorded in `docs/OPEN_ITEMS.md`.

## D1. The MRes baseline, from the thesis rather than from assumption

Madkaikar A. (2023), *Predicting the thermal niche of a ubiquitous bacterium using whole genome
sequence*, MRes Computational Methods in Ecology and Evolution, Imperial College London;
supervisor Samraat Pawar. Read from `refs/Madkaikar_CMEE_MRes_02299268.pdf`.

**What the model was:**

* **Reconstruction: `iJO1366`**, enzyme-constrained with **GECKO 3 in MATLAB**; enzyme information
  queried from KEGG. **1 366–1 367 enzymes.**
* **Thermal layer: the same physics this project uses** — two-state denaturation with
  ΔGu(Tm) = 0, kcat from transition-state theory with a heat-capacity change ΔCp‡, and a
  temperature-dependent NGAM. FBA at each temperature over **8–48 °C**.
* **Parameters: 4 101** — Topt, Tm and ΔCp‡ for each of 1 367 enzymes.
* **Parameter sources:** Tm measured for **841 of 1 366**, the rest set to the measured mean
  **55.57 °C** with the empirical SD as uncertainty; Topt from **Li & Engqvist (2019)** for
  **894 of 1 366**, the rest initially 37 °C.
* **Calibration: not Bayesian.** Repeated FBA with each parameter class varied, scored by R² and
  MSE against one growth TPC and the estimates updated — a hand-rolled tuning loop, described in
  its Supplementary Information.
* **Data: growth TPCs only.** Trained on **one** curve (Mohr & Krawiec 1980, 20–48 °C) chosen from
  Smith et al. (2019)'s database; **validated against the other 25** *E. coli* curves in it.
* **Media:** minimal and LB explored, crossed with changed enzyme-availability bounds.
* **Result: R² = 0.94** on the growth TPC, with a steep decline above 46.5 °C.
* **No gas exchange, no respirometry, no acetate, no O₂.**

**Two places where the thesis does not match what this prompt assumes, and the thesis wins.**

1. **The reconstruction was replaced, not extended.** The baseline is `iJO1366`; this project's
   *E. coli* strain is **`eciML1515`**. "What we added" is therefore not a continuous extension of
   the MRes model — the GEM underneath it changed, and the MATLAB/GECKO pipeline became a Python
   core. The deck says this plainly rather than implying continuity.
2. **The baseline already had per-enzyme thermal parameters — 4 101 of them, more than Li's
   2 292.** So the honest framing of this project's sixteen global levers is **a deliberate
   reduction**, not a shortfall in resolution: the MRes had per-enzyme parameters and no way to
   constrain them, and the project traded them for a small identifiable set plus data that can
   constrain it. Any slide that framed "16 vs 2 292" as *coarseness* would be misleading, and Y3's
   result is what makes the trade defensible.

## D2. Pettersen & Almaas 2023 — the three things this deck uses them for

Read from `refs/PettersenAlmaas_2023.pdf` (*Sci Rep*, `@Pettersen2023`).

1. **The Bayesian method is unstable and does not estimate the posterior.** Their abstract:
   *"the Bayesian calculation method for inferring parameters for an etcGEM is unstable and unable
   to estimate the posterior distribution. The Bayesian calculation method assumes that the
   posterior distribution is unimodal, and thus fails due to the multimodality of the problem."*
   They replace it with an evolutionary algorithm to recover a diversity of solutions.
2. **The FVA result, and it is specifically the oxygen-consuming reaction.** Of six signature
   reactions, *"Ferrocytochrome-c:oxygen oxidoreductase are for some particles used extensively,
   but in other cases not at all, still giving rise to approximately the same growth rates
   regardless"* — the O₂-consuming step of the respiratory chain is the one that varies most
   between equally-fit particles. Two of the six barely varied; the rest *"displayed huge variation
   in flux-carrying capacity"*.
3. **What they say is needed.** *"the main source for the lack of identifiability is a result of
   the external measurements being insufficient … we believe that measurements of proteomics and
   fluxomics will help narrow down the solution space"*, and *"Given new measurements of fluxes
   where there currently is high variability … fewer particles would be supported by the
   experimental data."*

**Why this is a precise match and not a loose one.** The reaction they name as most
under-determined is the oxygen-consuming step of the respiratory chain, and the data they ask for
is a **measured flux**. Parsa's respirometry is a measured O₂ flux over a temperature series in
three media. The deck sets the two against each other directly, in their words.

## D3. Every gas-flux number on a slide is labelled mechanism or interval

`reports/ecoli_gasflux/README.md` opens with a standing banner: none of its R² values is a
converged posterior — Parsa's six chains and P4's nine refits all ran ~9 autocorrelation times
against a ≥ 40 criterion, so every R² in that family is a point estimate (MAP or median) from an
unconverged chain, *indicative and not validated model performance*. The gate remains valid as a
**port check** — it reproduces his computation to within 0.009 — which is a different claim.

**Decision: gas-flux slides carry the mechanism and say so on the slide; where a fit quality is
mentioned at all it is labelled an unconverged point estimate, and no interval is given.**
