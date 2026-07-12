# P1 — Synechocystis sp. PCC 6803: phase-0 lock + scaffolded, QC'd autotrophic base GEM (light-saturated)

**Phase:** P1 (first build step of the low-Ea third organism). **Solver:** Gurobi (WLS academic).
**Scope:** phase-0 decisions locked + base GEM scaffolded and forward-checked under a light-SATURATED
autotrophic medium, PLAIN FBA only. **NO thermal layer, NO enzyme-layer read-through, NO calibration,
NO Ea work** — those are P2+. Mirrors the methanogen M1 step.

---

## PART A — phase-0 decisions (LOCKED)

### Strain (locked by the user)
**Synechocystis sp. PCC 6803** — the model cyanobacterium; the low-Ea third point of the
Yvon-Durocher (2014) ordering (CH4 > respiration > photosynthesis).

### Regime (locked by the user): LIGHT-SATURATED / in-mechanism
Under saturating light the photon supply is non-limiting and **carbon fixation** (RuBisCO /
Calvin-cycle enzyme capacity, kcat(T) in P2) sets the rate. The organism therefore stays fully
**in-mechanism** — the same control-weighted, enzyme-cost decomposition as E. coli and
M. maripaludis — and the framework needs **NO new light-supply layer**. This is confirmed
in-silico below (PART C): in the enzyme-constrained model the photon exchange goes slack and the
enzyme pool binds.

### Base model + P2 route (CONFIRMED — pre-built ecModel, not a from-scratch build)
- **Base GEM:** `iSynCJ816` (Joshi, Ranganathan et al. 2020, *Algal Research* 10.1016/j.algal.2017.09.013;
  816 genes). Pulled from BiGG (`model/iSynCJ816.xml`, SBML L3 + fbc, 4.95 MB).
- **Enzyme layer (P2 route, CONFIRMED and pre-built):** `iSynCJ816_STAR` — an **AUTOPACMEN sMOMENT**
  enzyme-constrained upgrade of iSynCJ816 (F. Andrews; AUTOPACMEN pipeline, Bekiaris & Klamt 2020,
  *BMC Bioinformatics* 10.1186/s12859-019-3329-9). Repo:
  `https://github.com/FraserAndrews7/iSynCJ816-` (commit `78449d2`, 2024-05-20). Local copy:
  `model/ecmodel_iSynCJ816_STAR/`. This is the **same enzyme-cost method family we used for the
  methanogen (sMOMENT)** — a `prot_pool` pseudo-metabolite with a total enzyme budget — so P2 adds
  ONLY the thermal layer (kcat(T)/unfolding) + calibration, **not** a from-scratch enzyme build. This
  de-risks the phototroph relative to the methanogen (where we built sMOMENT ourselves).
  *Decision: use the pre-built ecModel; do NOT rebuild sMOMENT.*

### Calibration/validation TPC (locked; used in P2, not P1)
**Zavrel et al. 2015** (*Eng. Life Sci.* 15:122): growth rate vs temperature for glucose-tolerant
Synechocystis 6803 in a flat-panel photobioreactor. **Light saturation is documented in the paper's
methods** — saturating red light **220-360 umol photons m^-2 s^-1**, with no photoinhibition reported
up to 660 — so the growth-Ea from this curve is a light-saturated, carbon-fixation-limited response,
exactly the in-mechanism target. Rising limb Q10 ~1.70, **Topt ~35 C**, inhibition by ~44 C. The
figure (growth rate vs T) is to be digitised in P2, as Jones 1983 / Van Derlinden 2012 were.

### Target rate (locked)
**Primary = growth-rate TPC** (symmetric with E. coli and M. maripaludis; the Sharpe-Schoolfield E of
mu(T)). Under saturating light this growth-Ea reflects carbon-fixation kcat(T) — in-mechanism.
**Secondary = a carbon-fixation-flux TPC** read off the same model, for the cleanest comparison to
Yvon-Durocher 2014 (whose photosynthesis Ea is a photosynthesis-flux rate, not growth). Both are
available from the one model; the primary claim is growth-symmetric.

**Gate 4 flipped GREEN** in `docs/PHOTOTROPH_ETCGEM_PLAN.md` (light-saturated => in-mechanism => no new
layer; confirmed in-silico). Gate 1 upgraded (pre-built ecModel obtained). Gate 3 target-rate resolved
(growth primary; C-fixation-flux secondary).

---

## PART B — scaffold + QC

Strain dir `strains/syn6803/` created mirroring `strains/mmaripaludis/`:
`strain.yaml`, `model/`, `media/`, `thermal/`, `proteomics/`, `dltkcat/`, `outputs/`,
`run_p1_forward_check.py`.

### Base GEM QC (`model/iSynCJ816.xml`, plain)
| Property | Value |
|---|---|
| Reactions / Metabolites / Genes | **1044 / 928 / 816** |
| Objective (as shipped) | empty — set to `BIOMASS_Ec_SynAuto_1` |
| Biomass reactions | `BIOMASS_Ec_SynAuto_1` (autotrophic — used), `_SynMixo_1`, `_SynHetero_1` |
| RuBisCO carboxylase | `RBPC_1` (present) |
| RuBisCO oxygenase (photorespiration) | `RBCh_2` (present) |
| Photosystems | `PSIa/PSIb/PSIIa/PSIIb/PSIIc` (present) |
| Photon supply chain | `EX_photon_e` -> `PHOtex_1` -> `PHOTON_E1` -> `PHOTON680/PHOTON700` |
| Inorganic C exchange | `EX_co2_e`, `EX_hco3_e` (CCM) |

### ecModel QC (`model/ecmodel_iSynCJ816_STAR/iSynCJ816_STAR.xml`)
| Property | Value |
|---|---|
| Reactions / Metabolites / Genes | **1303 / 960 / 835** |
| Enzyme pool | `prot_pool` pseudo-metabolite; budget reaction `ER_pool_TG_` (UB **0.26 g/gDW**) |
| sMOMENT-split arm reactions (`_TG_`) | 409 |
| Objective (as shipped) | `BIOMASS_Ec_SynAuto_1` (autotrophic) |
| Provenance | kcats BRENDA + SABIO-RK; enzyme MW mapping (`Finished_ID_MASS_MAPPING_2.json`); construction notebooks in repo |
| Loads + solves in cobrapy | yes (Gurobi) |

---

## PART C — light-saturated autotrophic medium + forward-check

**Medium** (`media/BG11_photoautotrophic_light_saturated.md`): photon NON-limiting (saturating light),
inorganic C available (`EX_co2_e` + `EX_hco3_e`), N/P/S/H2O/trace metals open, **organic C closed**
(`EX_glc__D_e = 0` — the ecModel ships photomixotrophic). Objective = `BIOMASS_Ec_SynAuto_1`.
Reproducible: `run_p1_forward_check.py`.

**No curation needed.** Closing organic C and maximising autotrophic biomass gives a finite, well-posed
optimum with RuBisCO carrying carbon-fixation flux and **zero net photorespiration** — no futile-photon
route to close (contrast the E. coli O2-sink curation). Growth delta from curation: none required.

### Forward-check result — the plain GEM is photon-LINEAR; the ecModel is LIGHT-SATURATED

**Plain base GEM (iSynCJ816):** growth is **exactly linear in photon supply** (mu approx photon/510;
RuBisCO scales with it), so photon **always binds**. This is expected and correct: a stoichiometric
model has no per-throughput enzyme cap, so the energy input is necessarily the limiting flux. Light
saturation **cannot** appear at this layer — it requires the enzyme pool. (Directly parallel to the
methanogen, whose plain FBA scaled with the H2 bound; the TPC needed the enzyme + thermal layers.)

**Enzyme-constrained ecModel (iSynCJ816_STAR), pure autotrophy (glucose = 0):**

| photon bound | mu | photon used | photon binds? | enzyme pool draw | pool binds? |
|---:|---:|---:|:--:|---:|:--:|
| 10 | 0.0196 | 10.0 | yes | 0.059 / 0.26 | no |
| 24 | 0.0471 | 24.0 | yes | 0.260 / 0.26 | yes |
| 50 | 0.0931 | 50.0 | yes | 0.260 / 0.26 | yes |
| 1000 | **0.0939** | **51.4** | **no** | 0.260 / 0.26 | **yes** |
| 999999 | **0.0939** | **51.4** | **no** | 0.260 / 0.26 | **yes** |

Growth **saturates** at mu = 0.0939 for photon >= ~51; above the saturation point the photon flux is
**slack (shadow price = 0)** and the **enzyme pool binds (0.26/0.26)**. At saturating light:
glucose uptake = 0 (truly autotrophic), RuBisCO `RBPC_1` = 3.98, photorespiration `RBCh_2` = 0,
inorganic C drawn mainly as HCO3- (CCM) and CO2.

**In-mechanism confirmed:** under saturating light, carbon-fixation *capacity* (the enzyme pool), not
photon supply, sets the rate — the photon exchange is non-binding. This is structurally impossible in
the plain GEM and appears immediately once the enzyme pool is present, which is exactly the layer P2
builds on. The ~51-photon in-silico saturation point is the model analog of the measured light
saturation in Zavrel 2015.

---

## PART D — GO/NO-GO for P2

### GO. ✅

Rationale: the base GEM is QC'd and grows autotrophically with RuBisCO carrying flux and no
photorespiration; the light-saturated / in-mechanism regime is confirmed in-silico on the pre-built
ecModel (photon slack, enzyme pool binds); and the enzyme layer — the hardest part for the methanogen —
is **already built** (`iSynCJ816_STAR`), so P2 is thermal + calibration on a solved enzyme base.

### What P2 needs
1. **Thermal layer on `iSynCJ816_STAR`:** kcat(T) MMRT/Eyring x native fraction f_N(T) per enzyme
   (reuse `src/etcgem` thermal machinery). The enzyme pool + kcats already exist.
2. **Topt per enzyme:** Li-Engqvist sequence predictor on the 6803 proteome (portable; confirm run).
3. **Tm per enzyme:** mesophile prior (6803 absent from the Meltome Atlas), same route as the
   methanogen; 6803 is mesophilic (~35 C).
4. **Curvature:** literature MMRT dCp prior -4 kJ/mol/K (Hobbs 2013), not fitted — Ea emerges.
5. **kcats:** already in the ecModel; RuBisCO/Calvin turnovers are well-measured (a de-risking vs the
   archaeal core, which needed measured specific activities + DLTKcat correction).
6. **Validation TPC:** digitise Zavrel 2015 growth-vs-T (saturating light); primary target-rate =
   growth Ea (Sharpe-Schoolfield), secondary = carbon-fixation-flux TPC for the 2014 comparison.
7. **Magnitude realism (M4-style):** keep the calibration honest — the emergent prediction first, then
   a separate labelled inverse step on the few global scalars (pool budget / sigma / NGAM).

### Residual risks (to watch in P2, none blocking)
- The ecModel's pool budget (0.26 g/gDW) and kcat provenance are the authors', not ours — treat as a
  borrowed global scalar to be checked in calibration (as we did for E. coli's P_lit / sigma).
- Topt/Tm are predictor/prior, not measured for 6803 (same honest limitation as the methanogen).
- Whether the emergent phototroph Ea lands LOW (the 2014 expectation) is the scientific test P2 runs —
  P1 only establishes that the model is in-mechanism and ready to be asked.

---

### VERIFY (all reported)
0. solver = Gurobi; strain LOCKED (Synechocystis 6803); base-model route recorded (**pre-built ecModel
   iSynCJ816_STAR**, not from-scratch sMOMENT); NO thermal/enzyme/calibration layer added in P1. ✅
1. Phase-0 LOCKED: base model confirmed; light-saturated TPC confirmed (Zavrel 2015, 220-360 umol
   m^-2 s^-1 saturating light cited); target rate set (growth primary, C-fixation-flux secondary).
   Gate 4 -> GREEN. ✅
2. `strains/syn6803/` scaffolded mirroring the methanogen; base GEM + ecModel pulled + QC'd
   (photosystems / Calvin / RuBisCO / photon-exchange / biomass present; counts reported). ✅
3. Light-saturated autotrophic medium set (photon non-limiting, CO2/HCO3- available, organic C closed);
   model grows autotrophically with RuBisCO carrying flux and the photon bound **NON-binding in the
   enzyme model** (in-mechanism confirmed); no curation required. The plain GEM's photon-linearity is
   documented as expected structural behaviour. ✅
4. `P1_scaffold_and_base.md` written; `docs/PHOTOTROPH_ETCGEM_PLAN.md` updated (Gate 4 GREEN); GO for
   P2. ✅
