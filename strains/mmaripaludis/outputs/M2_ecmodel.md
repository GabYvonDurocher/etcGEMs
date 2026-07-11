# M2 — base (temperature-independent) sMOMENT ecModel for M. maripaludis

> **Superseded in part by M2b** (`M2b_kcat_refinement.md`): the kcat table was refined
> (PFOR/OGOR literature overrides, Mcr re-pinned to its cited kcat, a DLTKcat <1/s floor).
> The current numbers are **mu 0.044/h** (was 0.0185; ~4.1× under the Jones peak, was ~10×)
> and a methanogenesis backbone that **shares** the pool (Fwd/Mtr/Mcr ≈ 14–19% each) rather
> than Mcr dominating at 39.7%. The parameterisation narrative below is the M2 snapshot.


Enzyme-constraint layer on the M1b carbon-honest autotroph (`iMR539_curated.xml`), reusing
`src/etcgem/enzyme_cost` (sMOMENT total-protein pool). **Base ecModel only** — no thermal
layer (M3), no calibration (M4). Emergent-then-calibrate: a grounded pool from independent
data, mu reported **honestly** (not tuned to mu_max). Solver: **Gurobi** (WLS academic).

## PART A — per-enzyme kcat + MW (`dltkcat/kcat_table.csv`)
- **Mapping.** M. maripaludis S2 proteome fetched from UniProt (UP000000590, organism
  267377; 1722 entries) -> MMP-tag→accession+MW map (`proteomics/`). All 527 enzymatic
  (GPR) reactions map to a UniProt MW (per-reaction MW = min over isozymes of summed subunit
  MW); the 101 no-GPR reactions (transport/spontaneous) carry no cost.
- **kcat by source priority (`kcat = SA[U/mg]·MW[g/mol]/60000`):**
  | source | n | notes |
  |---|---|---|
  | measured_core | 11 | Milton 2018 (Hdr/Vhu/Fdh, SA 25–165 U/mg) + classic biochemistry (Mtr/Fwd/Ftr/Mch/Hmd/Mer/ATP synthase). **Mcr flagged high-uncertainty** (~3 U/mg → 8.84/s; lit. range 1–100/s) — the famously slow terminal enzyme + Ea target. |
  | dltkcat | 293 | DLTKcat @37 °C (PubChem SMILES + UniProt seq). Bacteria-trained → **a prior**; median 4.87/s, and **28% (81/293) predict <1/s** — the archaeal underprediction tail. |
  | fallback_mean | 223 | substrate SMILES/seq unresolved (exotic cofactors/peptides) → dataset-median DLTKcat kcat 4.87/s. |

## PART B — sMOMENT ecModel (`providers.from_gem_smoment`, type `smoment_gem`)
Each enzymatic reaction costs `MW/(kcat·3600)` g protein per unit flux from a single shared
pool. Temperature-**independent**: every Topt pinned to T0 (37 °C) so the MMRT shape is flat
(cost == base_cost at reference T); M3 overrides Topt/Tm/dCp. Loads via the standard config/
CLI: `etcgem build --strain mmaripaludis` → 527 enzymes, pool binds. Base ecModel saved as
`model/iMR539_ecmodel_base.xml`.

## PART C — grounded proteome pool (NOT tuned to mu_max)
Emergent budget `P_total × σ × f_metab = 0.5 × 0.45 × 0.5 = 0.1125 g/gDW`:
- **P_total 0.5** g protein/gDW (protein ~50% of dry mass, literature);
- **σ 0.45** average in-vivo saturation (Davidi 2016 / Heckmann 2020);
- **f_metab 0.5** modelled-metabolic-enzyme mass fraction (grounded starting value; the Xia
  2006/2009 proteome can refine it in M4).

**Emergent mu @37 °C = 0.0185 /h** (`outputs/M2_validation.json`). The pool **binds**
(used == ub) and mu moved sharply **down** from the plain-FBA 0.548 /h. It **undershoots**
the measured mu_max (~0.23–0.35 /h) by ~13×. This is reported honestly, not tuned. The
undershoot is driven by two flagged parameter uncertainties, not the pool:
1. **Mcr low-end kcat** (8.84/s): Mcr alone is **39.7% of the used pool** — raising it
   saturates mu at ~0.02/h (Mcr is not the sole limiter);
2. **DLTKcat archaeal underprediction**: 28% of predicted kcats < 1/s inflate biosynthetic
   costs (e.g. pyruvate:ferredoxin oxidoreductase predicted 0.26/s — implausibly low for a
   ~tens/s enzyme — is the #2 pool consumer at 18.8%).
M4 calibrates the magnitude with the global `kcat_scale`/σ in-vitro→in-vivo lever (exactly
as the E. coli model calibrated `kcat_scale`), against the Jones 1983 TPC.

## PART D — enzyme-cost artefact audit
- **No free ferredoxin/electron shortcut.** Unlike E. coli's uncosted O2 sinks, the
  methanogen energy metabolism (Hdr, hydrogenases, Mtr, ATP synthase) is fully enzyme-costed;
  the only free reactions carrying flux are passive H2/H2O/CO2/CH4 diffusion (correctly free).
- **One artefact — a hard-pinned uncosted ATP drain.** `rxn00062` ("protein-secreting
  ATPase") ships **fixed at 5.12 mmol/gDW/h** (lb == ub, no GPR). In the enzyme-limited model
  this fixed drain dominated the energy budget: relaxing its forced lower bound to 0
  (reaction kept, ub unchanged) raised **mu 0.0033 → 0.0185 /h (5.6×)** and dropped
  **CH4/biomass 3517 → 435** (matching the plain-FBA stoichiometric 443). A *fixed* uncosted
  ATP sink is non-physiological in the base ecModel; measured maintenance is the M3 NGAM(T)
  layer (Goyal 2015). Documented + reversible via `provider.relax_pinned` in `strain.yaml`.

## PART E — validation (`outputs/M2_validation.json`)
- Enzyme-constrained growth on H2/CO2: **mu 0.0185 /h**, realistic direction (< plain-FBA).
- Methanogenesis intact: **H2:CO2:CH4 = 4.12:1.06:1**; Mcr and the whole Wolfe-cycle core
  carry flux **and** enzyme cost.
- Pool is the **binding** constraint.
- **Mcr mass fraction 39.7%** of the used pool — physically sensible for the abundant, slow
  terminal enzyme, and the concentration of enzyme cost exactly where the **Ea-control
  hypothesis** predicts it.
- Sanity: no growth without electron donor (no-H2) or carbon (no-CO2).

## GO / NO-GO for M3 (thermal layer)
**GO.** M3 inherits a working base ecModel: sMOMENT pool binds, methanogenesis wired and
enzyme-costed, Mcr dominant, artefact-audited. Add per-enzyme Topt (sequence predictor) +
Tm/unfolding + kcat(T) MMRT to generate the emergent growth/CH4 TPCs.

**Residual caveats carried into M3/M4 (honest):**
1. **Magnitude undershoots ~13×** — expected; M4 calibrates `kcat_scale`/σ to the Jones TPC.
2. **DLTKcat archaeal underprediction** (28% of kcats <1/s; e.g. PFOR 0.26/s) inflates the
   biosynthetic bulk — a kcat floor or targeted literature overrides for a few high-cost
   enzymes is an M4 refinement.
3. **Mcr kcat uncertainty** (1–100/s) directly sets the dominant cost — the key value to pin
   down; it is the Ea target.
4. **f_metab 0.5** is a grounded starting value; refine against the Xia proteome in M4.
5. Maintenance is deferred to M3's measured NGAM(T) (the relaxed rxn00062).
