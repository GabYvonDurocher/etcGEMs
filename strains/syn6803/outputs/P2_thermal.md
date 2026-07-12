# P2 — thermal layer + emergent light-saturated growth TPC (Synechocystis 6803, nothing fit)

Temperature-dependent envelope on the P1 base ecModel **iSynCJ816_STAR** (pre-built AUTOPACMEN
sMOMENT), reusing the E. coli / methanogen thermal machinery (`mmrt.py` kcat(T), `unfolding.py`
two-state f_N(T), NGAM(T)) via `providers.from_gecko` (route-B sMOMENT). **Emergent — nothing fit
to the Zavrel 2015 data.** No calibration (P3), no Ea dissection (P4). Solver: **Gurobi**. Operated
under the P1 light-**SATURATED** autotrophic medium (photon non-limiting, CO2/HCO3- available,
organic-C closed). Entry point: `strains/syn6803/run_p2_thermal.py`.

## PART A — per-enzyme thermal envelope (`thermal/enzyme_thermal_params.csv`, 1066 rxns, 100% matched)
Each cost carrier's cost becomes `base_cost / (rel_kcat(T)·f_N(T))`, with `base_cost` taken directly
from the STAR `prot_pool` coefficient (= MW/kcat, the authors' BRENDA/SABIO-RK kinetics) and the
temperature response added on top:
- **kcat(T)**: MMRT/Eyring turnover anchored at a per-enzyme **Topt**, curvature from the literature
  MMRT **dCp prior (−4 kJ/mol/K**, Hobbs 2013) — so the rising-limb Ea EMERGES.
- **Topt route (documented mesophile prior).** The Li-Engqvist per-enzyme optimum predictor is **not
  runnable in-session** and 6803 is absent from the precomputed E. coli/Li tables, so — exactly as
  for *M. maripaludis* (M3) — Topt is a **mesophile prior**. 6803 is a mesophile (growth optimum
  ~35 °C, Zavrel 2015), so we reuse the **same generic mesophile enzyme-Topt prior as the methanogen
  build**: `N(39.3 °C, 10)` (enzyme optima sit a little above the organism's growth optimum, as for a
  typical mesophile). The rising-limb Ea, breadth and CTmax then EMERGE and are compared a-priori to
  Zavrel. Li-Engqvist / a cyanobacterial Topt predictor is the **stated future upgrade**; P3's
  `dTopt`/`topt_scale` refine it. `thermal/gen_thermal_params.py` regenerates the table deterministically.
- **f_N(T)** two-state native fraction keyed on **Tm**. **Tm route (documented mesophile prior):**
  `N(55.6 °C, 7.59)` (the E. coli meltome mean + spread), **independent of Topt** (6803 absent from the
  Meltome Atlas; mesophile stability regime). Flagged as the a-priori Tm; P3's `dTm` refines it.
  Protein **Length** from a generic bacterial-length prior `N(335, 134)`; `dCpt` = −4000 J/mol/K prior.

Coverage: **1066/1066 (100%)** cost carriers matched by `rxn_id` (RuBisCO `RBPC_1` included).

## PART B — NGAM(T) maintenance (`ngam_base_scale = 0.548`)
A temperature-dependent non-growth maintenance NGAM(T) (Boltzmann/Arrhenius form, E. coli shape) is
added on the STAR **ATPM** reaction, **amplitude anchored on a MEASURED 6803 maintenance value**:
Touloupakis, Cicchi & Torzillo (2015, *Biotechnol. Biofuels* 8:133) report maintenance =
**0.00312 mol photons gDW⁻¹ h⁻¹ (= 3.12 mmol photon/gDW/h)** from Pirt-model continuous cultures.
This is a **photon**-based coefficient (the phototroph subtlety: under light, maintenance ATP is met
by **photophosphorylation**, not respiration). We carry it as the ATP-maintenance amplitude at Topt —
`NGAM(35 °C) = 3.12 mmol ATP/gDW/h` (a documented ~1 ATP : 1 photon order-of-magnitude equivalence in
the light-saturated regime) — running **1.8 (low-T floor) → 3.1 (35 °C) → 3.8 (44 °C)** mmol ATP/gDW/h.
Because photons are non-limiting, this maintenance ATP is supplied by photophosphorylation, so NGAM(T)
draws the shared enzyme pool (ATP synthase + photosystems) rather than a photon budget; it is kept in
the standard maintenance form. GAM stays in the biomass reaction. P3's `ngam_scale` refines the
amplitude and the photon→ATP conversion.

## PART C — emergent light-saturated TPC (`outputs/P2_thermal/`)

**A-priori result (kcat_scale = 1, nothing scaled).** The emergent growth TPC is clean, single-peaked
and **realistic in magnitude** (unlike the methanogen, whose a-priori magnitude collapsed):

| descriptor | emergent (a-priori) | Zavrel 2015 | verdict |
|---|---|---|---|
| **Topt** | **36.0 °C** | ~35 °C | **✓ matches** (+1 °C) |
| **CTmax** | **45.7 °C** | ~44 °C | **✓ matches** (Tm-driven falling limb) |
| **rmax** | **0.067 /h** | ~0.05–0.09 /h (typical 6803) | **✓ realistic magnitude** |
| CTmin | 12.9 °C | ~15 °C | ✓ close |
| niche width | 32.8 °C | broad | ✓ broad |
| **SS-E (growth)** | **0.771 eV** | **~0.42 eV** (Q10 1.70) | rising limb **~1.8× too steep** → P3 |
| SS-E (carbon fixation) | 0.765 eV | — | tracks growth (in-mechanism) |

`SS-E` is the window-independent Sharpe–Schoolfield E (T_ref = 20 °C), the reportable Ea; fits
R² = 0.96. The **carbon-fixation-flux TPC** (RuBisCO `RBPC_1`, the secondary descriptor for the
Yvon-Durocher 2014 comparison) peaks at the same 36 °C with SS-E 0.765 eV — growth and carbon fixation
are thermally locked, confirming the in-mechanism read-out. Figure: `emergent_tpc_vs_zavrel.png`
(raw + normalised-shape overlay with the Zavrel rising-limb reference).

**In-mechanism confirmed across temperature.** The photon exchange shadow price is **0 at every
temperature** in the growing range (`photon_nonbinding_maxabs_shadow = 0.0`): light saturation holds
across the whole sweep, so the enzyme pool (carbon-fixation capacity), not photon supply, sets the
rate at all T. This is the phototroph analog of the E. coli / methanogen enzyme-limited TPC.

**The honest, scientifically interesting gap.** Shape (Topt, CTmax, rmax) matches Zavrel a-priori
**better than either prior organism did**, but the emergent rising-limb SS-E (0.77 eV) lands in the
*respiration-like* ~0.65–0.8 eV band, whereas Zavrel measured a notably **LOW 0.42 eV** — the very
"low photosynthesis Ea" the phototroph is meant to test (Yvon-Durocher 2014). So the a-priori model
does **not yet** reproduce the low Ea: with a generic mesophile Topt prior + the −4 kJ/mol/K dCp prior,
the phototroph looks thermally like a respirer. Closing/explaining this gap is exactly the job of P3
(what corrections the data demand) and P4 (whether the low Ea is mechanistically from a genuinely
shallow carbon-fixation kcat(T), a wider Topt spread, or the allocation buffer). This is a sharper,
more informative a-priori position than a curve that already matched.

**Photorespiration caveat (documented, not built).** The classic photosynthesis temperature response
includes RuBisCO's declining CO2/O2 specificity with warming (rising photorespiration). Under Zavrel's
CO2-replete saturating-light conditions photorespiration is suppressed (P1: zero net at the optimum;
here RuBisCO oxygenase `RBCh_2` ≈ 0 across the sweep), so the emergent growth-TPC is dominated by
Calvin-cycle kcat(T), which the framework carries. A temperature-dependent RuBisCO specificity factor
is a stated future refinement, consistent with the honest-caveat house style.

**Growth-law/allocation coupling is OFF** (single sMOMENT pool + NGAM(T) is the P2 envelope). NOTE:
the cyanobacterial allocation layer (the phototroph analog of Scott/Müller — Zavrel 2019 + Jahn 2018 +
the 2021 temperature-growth-law paper) is the next step (P2b or folded into P3) before the three-way
Ea comparison, exactly as the methanogen sector layer (M6) was. Given the E. coli allocation buffer was
a key **Ea-lowering** term, it is a prime candidate for part of the 0.77→0.42 eV gap.

## PART D — GO / NO-GO for P3 (Bayesian calibration to Zavrel)
**GO.** The thermal envelope is wired and emergent, and the a-priori position is unusually clean:
Topt, CTmax and rmax all match Zavrel a-priori, photon stays non-binding across T (in-mechanism), and
the single clear residual — the rising-limb Ea (0.77 vs 0.42 eV) — is exactly what the P3 knobs
address.

**What P3 will need:**
1. **Digitised Zavrel 2015 growth-vs-T point cloud** to replace the descriptor reference
   (`thermal/zavrel2015_descriptors.csv`); the user can drop exact points into `thermal/`.
2. **Calibration knobs** (as for E. coli / methanogen): `dCp`/`topt_scale`/`dTm` for the rising-limb
   Ea and breadth (the 0.77→0.42 eV gap), `dTopt` for the +1 °C, `ngam_scale` for maintenance, and a
   magnitude lever (`kcat_scale`/σ) — though the a-priori magnitude is already realistic, so magnitude
   calibration should be light.
3. **Allocation layer decision** (P2b / P3): whether the cyano growth law contributes the low Ea.

**Carry-forward caveats (honest):**
1. **Topt & Tm are mesophile priors** (no runnable sequence/meltome predictor for 6803) — the two
   a-priori thermal routes; sequence/meltome predictors are the future upgrade. Same stance as M3.
2. **Rising-limb SS-E 0.77 vs Zavrel 0.42 eV** — the phototroph does not yet look low-Ea a-priori;
   the central scientific question for P3/P4.
3. **NGAM photon→ATP conversion** is an order-of-magnitude documented prior (Touloupakis photon
   maintenance); P3's `ngam_scale` refines it.
4. **Growth-law/allocation OFF** — the candidate Ea-lowering layer, next step before P4.
5. **Photorespiration T-dependence not modelled** (suppressed under CO2-replete saturating light).

## VERIFY (all reported)
0. solver = Gurobi; thermal layer wired onto **iSynCJ816_STAR** via `from_gecko` route-B (unfolding);
   operated under the light-saturated medium; **photon non-binding across the whole sweep** (in-mechanism
   holds). No calibration / Ea dissection / growth-law coupling added. ✅
1. kcat(T) (MMRT dCp prior + mesophile-prior Topt) + f_N(T) (mesophile Tm prior, documented + flagged)
   applied; **coverage 1066/1066 (100%)**. Li-Engqvist noted as the future upgrade + why not run. ✅
2. NGAM(T) added on ATPM; amplitude anchored on the **measured** 6803 maintenance (Touloupakis 2015,
   cited); phototroph photophosphorylation subtlety documented. ✅
3. Emergent light-saturated TPC produced (growth **+** carbon-fixation flux); SS-E reported and
   compared **a-priori** to Zavrel 2015 (Topt/CTmax/rmax match; honest 0.77-vs-0.42 eV Ea offset);
   overlay figure saved. ✅
4. Growth-law/allocation OFF (noted as the next step before P4); photorespiration caveat documented;
   nothing tuned to Zavrel. ✅
5. `P2_thermal.md` + `outputs/P2_thermal/` saved; GO for P3 with carry-forward caveats. ✅
