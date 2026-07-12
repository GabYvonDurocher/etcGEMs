# P3b — Synechocystis 6803 proteome-sector / allocation layer (its OWN strategy)

Adds a proteome-sector + coupled growth-law layer to the phototroph (previously a single sMOMENT
pool, so its allocation term was 0 *by construction*). Grounded in the cyanobacterium's **own**
allocation physiology — **not** the bacterial Scott law, **not** the methanogen's flat law — so the
three-way allocation comparison is **symmetric**. Reuses `sectors.py` (no fork). SS-E descriptors;
Gurobi; light-saturated medium (photon shadow price 0 preserved). Entry point:
`strains/syn6803/run_p3b_sectors.py`. No Ea dissection (P4).

## PART A — the cyanobacterium's allocation data (from the primary PDFs in `refs/synechocystis6803/`)

**Jahn et al. 2018, Cell Reports 25:478–486** (primary — fractions + slope; verified from Fig 2A +
Results). Multiplex turbidostat, μ = 0.016–0.106 /h (μ_max 0.11), label-free proteomics; **seven
functional sectors**, and the **total cellular protein concentration is invariant across growth**
(also Du 2016, Touloupakis 2015). Sector mass fractions (α) vs μ:
- **MAI** (maintenance + regulation + hypothetical/unknown; 1,272 proteins): up to **~33 %**
  ("did not exceed 33 %"), ~flat/slightly decreasing → **f_maint**.
- **RIB** (ribosome + protein production; 112 proteins): **16.9 % (Cᵢ-lim) / 16.5 % (light-lim)**,
  **increasing with μ** (p = 5×10⁻⁴ / 2×10⁻⁵) — the growth-law **coupling slope** (the cyanobacterial
  analog of Scott 2010). The dominant RIB proteins are actually the chaperones GroEL-1/2/GroES;
  ribosomal proteins proper are less abundant → **f_bio**.
- **LHC** (light-harvesting; 57 proteins) ~15–19.6 %, **PSET** (photosystems/electron transport; 80)
  ~13 %, **CBM** (Cᵢ uptake/fixation/metabolism; 318) ~14 %, **GLM** (44) + **LPB** (96) smaller —
  together the flux-carrying proteins, **~50 %** → **f_metab** (**light-harvesting → metabolic mapping**,
  stated: LHC/PSET are the energy-input proteins that feed the kcat(T)-limited network).

**Zavrel et al. 2019, eLife 8:e42508** (corroboration + P_total + framework): confirms the direction
(translation **up**, light-harvesting **down** with μ; 1,356 proteins, 57 % growth-dependent);
instantiates the **Faizi et al. 2018** coarse-grained optimal-allocation model (sectors T/M/R/P/LHC),
which our sector layer realises; reports absolute protein content **~402 mg/gDW** (the phototroph
P_total analog, vs E. coli 0.5 g/gDW).

**Suzuki et al. 2006, J Exp Bot 57:1573** (maintenance-sector temperature response): heat-shock
chaperones (GroESL, HtpG, HspA, ClpB1, DnaK2) induced at 44 °C — the cyanobacterial analog of the
E. coli chaperone rise; informs the maintenance/NGAM(T) upper-limit behaviour (falling limb), NOT the
rising-limb Ea. (Used qualitatively; the 2-D-gel protein-level changes, not the larger transcript folds.)

### The load-bearing quantitative fact
Jahn's RIB is **nearly constant** (16.5→16.9 %) and its per-μ slope, though significant, spans a
**tiny μ range** (μ_max 0.11 vs E. coli ~1–2 /h). So the **absolute** ribosome reallocation over the
phototroph's operating range is small → **a small allocation buffer is predicted** — corroborating,
on a MEASURED footing, P3's verdict that the low phototroph Ea is kinetic, not allocation-set. This
places the phototroph **between** E. coli's steep Scott slope and the methanogen's ~0.

## PART B — implementation (reused `sectors.py`, no fork)
`calibration_multi.SYN6803_SECTOR_CFG` + `_build_pm_syn6803_sectored`, and the `strain.yaml`
`proteome_sectors` block, wire the layer onto the P3 phototroph provider:
- **f_metab 0.50 / f_maint 0.33 / f_bio 0.17**; `P_total` backed out from the P3 metabolic budget
  (0.26/0.50 = 0.52 g/gDW; Zavrel's 0.402 is the measured-total-protein cross-check — the difference
  is modeled-vs-total protein).
- **growth_law_slope 0.39 /h** (RIB rising limb, Jahn Fig 2A), `f_bio_0 = 0.133` (intercept).
- **`translation_coeff` pinned to 0.9** so the **ribosome cap is non-binding** (M6-style) — justified
  by the near-constant measured RIB. The metabolic pool therefore stays the binding constraint
  (kcat(T)-limited, preserving Topt and the P3 fit), and the small allocation buffer comes purely
  from the **metabolic-sector shrinkage** term (`+slope·P·v_bio` in the metabolic pool). Without this
  pin, an auto-calibrated cap clips the peak and drags Topt to 29 °C — an artifact, not physiology.

## PART C — forward-check: NO re-calibration needed (`P3b_sectors/p3b_forward_check.json`)
With the sector layer ON and the **P3 posterior-median** parameters, the TPC is essentially unchanged:

| | rmax (1/h) | Topt (°C) | CTmax (°C) | growth SS-E |
|---|---|---|---|---|
| single-pool P3 | 0.0944 | 35.0 | 46.8 | 0.563 |
| **sectored + growth law** | **0.0903** | **35.0** | **46.8** | **0.573** |

`max|Δμ|` across the TPC = **0.004**; ΔTopt 0, ΔCTmax 0, Δrmax −4 %, ΔSS-E +0.010. Zavrel is still
reproduced (peak residual −7 %); **photon shadow price stays 0** (in-mechanism preserved). The layer
is additive/near-neutral → **the P3 posterior holds, no re-fit** (`recalibration_needed = false`).

### The allocation buffer — measured, small, symmetric
Directly measured **allocation buffer = SS-E(growth law ON) − SS-E(growth law OFF, slope 0) =
0.573 − 0.592 = −0.019 eV**. The three-way comparison is now **structurally symmetric** (all three
organisms carry a sector/growth-law layer grounded in their **own** allocation law):

| organism | allocation law | buffer (eV) |
|---|---|---|
| E. coli | Scott rising-ribosome (steep, wide μ range) | **−0.130** |
| **phototroph** | **Jahn RIB (comparable per-μ slope, tiny μ range)** | **−0.019** |
| methanogen | Müller constant-ribosome (flat) | **0.000** |

The phototroph buffer is small and sits between E. coli and the methanogen, **closer to the
methanogen** — its low Ea is **kinetic (shallow Calvin kcat(T)), not allocation-set**, now on a
measured, symmetric footing rather than a structural zero. Figure:
`sectored_vs_singlepool_tpc.png`.

## PART D — GO for P4
**GO.** The sectored phototroph is wired, forward-checked (near-identical fit, no re-calibration),
and its allocation term is now a *measured* −0.019 eV (grounded in Jahn 2018), not a structural 0.
P4 can run the SS-E dissection on the sectored model and report the control-weighted terms for all
three organisms on the same footing — the clean expectation being that the phototroph's low Ea is
dominated by the **naive-mean / enzyme kcat(T) term** (genuinely shallow Calvin-cycle kinetics), with
a small allocation contribution (−0.019), in contrast to the methanogen's control-on-a-high-E-backbone.

**Caveats (stated, honest):**
1. Sector fractions (0.50/0.33/0.17) are grounded but approximate (a full Jahn source-data sector
   parse would refine them); the light-harvesting→metabolic mapping is a modelling choice, stated.
2. The **ribosome cap is pinned non-binding** (translation_coeff 0.9) — a deliberate representation of
   the near-constant measured RIB (M6-consistent), not a fitted lever; the buffer is the
   metabolic-shrinkage term. An auto-calibrated cap over-clips (Topt→29 °C, an artifact).
3. `P_total` backed out (0.52) vs Zavrel's measured 0.402 g/gDW — the modeled-vs-total-protein gap;
   the metabolic pool is held at the P3-calibrated 0.26 to preserve the fit.
4. The single-pool P3 model remains available (`proteome_sectors.enabled: false`) as the comparison.

## VERIFY (all reported)
0. solver=gurobi; SS-E descriptors; light-saturated medium (**photon shadow price 0 preserved**). ✅
1. Sector fractions + growth-law slope sourced from **Jahn 2018 (verified Fig 2A) + Zavrel 2019 +
   Faizi 2018 + Suzuki 2006** (cited); slope recorded honestly (small absolute buffer); the
   light-harvesting→metabolic mapping stated; NOT E. coli's / the methanogen's law forced on. ✅
2. Sector layer implemented via `sectors.py` (phototroph params; toggleable); provider + strain.yaml
   wired. ✅
3. Forward-check reported; **no re-calibration needed** (near-neutral, max|Δμ| 0.004); Zavrel still
   reproduced (rmax/Topt/CTmax/SS-E ~0.56–0.57); calibrated sector allocation + slope + buffer −0.019
   reported. ✅
4. `P3b_sector_layer.md` saved; **GO for P4** (Ea dissection + three-way E. coli / methanogen /
   phototroph comparison). ✅
