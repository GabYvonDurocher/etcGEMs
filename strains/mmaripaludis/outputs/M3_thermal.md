# M3 — thermal layer + emergent methanogenesis TPC (nothing fit)

Temperature-dependent envelope on the M2b base ecModel, reusing the E. coli thermal
machinery (`mmrt.py` kcat(T), `unfolding.py` two-state f_N(T), NGAM(T)). **Emergent —
nothing fit to the Jones 1983 data.** No calibration (M4), no Ea dissection (M5). Solver:
**Gurobi**. Loads via the standard config/CLI (`strain.yaml` → `thermal_model: unfolding`).

## PART A — per-enzyme thermal envelope (`thermal/enzyme_thermal_params.csv`, 527 rxns)
Each reaction's cost becomes `base_cost / (rel_kcat(T)·f_N(T))`:
- **kcat(T)**: MMRT/Eyring turnover anchored at a per-enzyme **Topt**, curvature from the
  literature MMRT **dCp prior (−4 kJ/mol/K**, Hobbs 2013) — so the rising-limb Ea EMERGES.
- **Topt route (documented prior).** The Li-Engqvist sequence predictor is **not runnable
  in-session**, so Topt is a **mesophile prior**: `N(39.3 °C, 10)` matched to the E. coli
  *predicted* enzyme-Topt distribution (both are mesophiles growing at ~37–38 °C). Flagged
  as the a-priori Topt; the archaeal/sequence Topt predictor is the future upgrade, and M4's
  `dTopt`/`topt_scale` refine it.
- **f_N(T)** two-state native fraction keyed on **Tm**. **Tm route (documented prior):** a
  **mesophile Tm prior** `N(55.6 °C, 7.59)` (the E. coli meltome mean + spread we already
  use), **independent of Topt**, since M. maripaludis is mesophilic (~38 °C) so its stability
  regime is broadly mesophile-like. Flagged as the a-priori Tm to be refined by M4's `dTm`; a
  methanogen/archaeal Tm predictor is the future upgrade. Protein **Length** from UniProt
  (506/527); `dCpt` from the literature MMRT prior.

## PART B — NGAM(T) from Goyal 2015 (`ngam_base_scale = 1.3021`)
The M2b-deferred hard-pinned ATP drain (rxn00062) becomes a temperature-dependent non-growth
maintenance NGAM(T) (Boltzmann/Arrhenius form, E. coli shape), **amplitude anchored on the
MEASURED M. maripaludis maintenance NGAM = 7.836 mmol ATP/gDW/h at 37 °C** (Goyal et al.
2015, *Microb Cell Fact* 14:146; also GAM 27.14, 0.35 mol ATP/mol CH4 — GAM stays in
biomass). NGAM(T) runs 4.2 (low-T floor) → 7.8 (37 °C) → 9.9 (55 °C) mmol ATP/gDW/h.

## PART C — emergent methanogenesis TPC (`outputs/M3_thermal/`)
**Primary a-priori result (kcat_scale = 1, nothing scaled): peak mu ≈ 0.** The measured
maintenance (Goyal NGAM 7.84 ≈ 22 mmol CH4/gDW/h of ATP demand) **exceeds the pool-limited
energy supply** of the a-priori-parameterised model, whose emergent methanogenesis capacity
(~19 mmol CH4/gDW/h) undershoots real cells ~5×. So the ~4× M2b magnitude undershoot
**compounds fatally with realistic maintenance** — an honest, informative finding: at the
a-priori magnitude the cell can barely maintain itself, let alone grow.

**Emergent SHAPE** (revealed with the in-vitro→in-vivo `kcat_scale` **physical prior ≈ 4×** —
the Davidi 2016 / Heckmann 2020 median apparent-kcat gap; a documented prior, **NOT fit to
Jones**). The TPC shape is largely magnitude-invariant; NGAM(T) rounds the peak.

| descriptor | emergent | Jones 1983 | verdict |
|---|---|---|---|
| **CTmax** | **46.8 °C** (CH4 TPC 47.9) | ~47–48 °C | **✓ matches** (Tm-driven falling limb) |
| Topt | 42.0 °C | 37 °C | +5 °C warm (mesophile Topt prior runs warm) |
| rising-limb Ea | 1.72 eV (166 kJ/mol) | ~0.6–0.8 eV | too steep (~2–3×) |
| B80 width | 5.5 °C | broader | too narrow |
| peak mu | 0.069 /h | 0.181 /h | **2.6× undershoot** (few-fold, → M4) |

The qualitative shape is right — single-peaked, in the correct temperature range, **CTmax
matching**. The rising limb is too warm/steep and the niche too narrow (the mesophile-Topt
prior + NGAM interplay). Growth ≈ CH4 for a hydrogenotroph (CH4 TPC tracks the growth TPC).
Figure: `emergent_tpc_vs_jones.png` (raw + normalised-shape overlay).

**Growth-law/allocation coupling is OFF** (single sMOMENT pool + NGAM(T) is the M3 envelope).
NOTE: the coupled proteome-allocation layer was the key **Ea-buffering** term in E. coli — it
is the next consideration (M3b or folded into M4) before the M5 Ea comparison.

## PART D — GO / NO-GO for M4 (Bayesian calibration to Jones)
**GO.** The thermal envelope is wired and emergent: the falling limb (CTmax) already matches
Jones a-priori, and the residuals are exactly what the M4 knobs address — magnitude
(`kcat_scale`/σ), Topt (`dTopt`), and rising-limb Ea/breadth (`dCp`/`topt_scale`/`dTm`).

**Carry-forward caveats (honest):**
1. **A-priori magnitude → mu ≈ 0** (maintenance-dominated); the shape is shown at a physical
   kcat_scale prior. M4 must calibrate magnitude first (kcat_scale/σ, f_metab vs Xia proteome)
   so growth clears maintenance.
2. **Topt +5 °C and Ea ~2–3× too steep / niche too narrow** — the mesophile Topt prior and the
   dCp prior; M4's dTopt/dCp/topt_scale/dTm calibrate these.
3. **Tm mesophile prior** and **Topt mesophile prior** (no sequence predictor) — the two
   a-priori thermal routes; sequence/meltome predictors are the future upgrade.
4. **Mcr kcat 3–294/s** sensitivity persists (carried from M2b) — matters for the M5 Ea.
5. **Growth-law/allocation OFF** — the Ea-buffering allocation layer is the next step before M5.
