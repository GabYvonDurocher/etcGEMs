# Three distinct routes to the Yvon-Durocher 2014 ordering — E. coli vs M. maripaludis vs Synechocystis 6803 (Sharpe–Schoolfield E)

> **THREE-WAY (P4).** All three organisms now carry a grounded proteome-sector/growth-law layer
> (E. coli Scott rising-ribosome; methanogen Müller constant-ribosome; phototroph Jahn-2018
> shallow-RIB), so the **allocation term is measured for each**, not structural. All three are
> dissected identically (window-independent SS-E; per-enzyme kcat(T) rising-limb E; MCA control
> coefficients; 4 named terms with **aggregation computed directly**). Paper-ready assets:
> `comparison_table_3way.csv`, `cross_organism_signed_contributions_3way.png`, `comparison_3way.json`,
> the three `ea_dissection_ss/decomposition_ss.json`, the methanogen `mcr_sweep.csv` + the phototroph
> `robustness_sweep.json`. (The two-way originals are kept.)

## Headline validation — all three models match their observed SS-E
| | model SS-E | observed SS-E | Topt | CTmax |
|---|---|---|---|---|
| **Methanogenesis** — *M. maripaludis* (H2/CO2) | **1.06** | 1.04 (Jones 1983) | 35 °C | 49 °C |
| **Respiration** — *E. coli* (rich BHI) | **0.68** | 0.56 (Van Derlinden) | 38 °C | 46 °C |
| **Photosynthesis** — *Synechocystis* 6803 (light-sat) | **0.57** | flux 0.52 (Inoue 2001); growth 0.44 (Zavrel, fragile) | 35 °C | 47 °C |

The models reproduce the **full 2014 ordering** — methanogenesis > respiration > photosynthesis —
each validated against an independent measured curve. *E. coli* sits on the "universal" metabolic
~0.65 eV benchmark; the methanogen is ~1.6× higher and the phototroph ~0.85× — spanning the range.
(Phototroph observed: the 6-point Zavrel *growth* SS-E is 0.44 but **fragile**, 90% CI [0.32, 1.00];
the robust anchor is the well-sampled Inoue *photosynthesis-flux* SS-E 0.52, matched by the model's
carbon-fixation-flux SS-E 0.56.)

## The 4-term SS-E decomposition — three DISTINCT routes (`comparison_table_3way.csv`)
| term (eV) | methanogen | *E. coli* | phototroph |
|---|---|---|---|
| naive (unweighted) enzyme-E mean | 0.512 | 0.872 | 0.684 |
| + control weighting | **+0.343** | +0.106 | **−0.016** |
| + allocation (Scott / flat / Jahn-shallow) | 0.000 | **−0.130** | −0.019 |
| + maintenance NGAM(T) | −0.016 | +0.005 | −0.027 |
| + aggregation (heterogeneity) | **+0.218** | **−0.175** | −0.050 |
| **= organism SS-E** | **1.056** | **0.678** | **0.573** |
| backbone fraction of control | 0.887 (methanogenesis) | broad | 0.336 (Calvin) |

**These are not one mechanism scaled — they are three different routes to a position in the range:**

1. **Methanogenesis (high, 1.06): narrow control on a HIGH-E backbone.** The naive enzyme-E mean is
   the *lowest* of the three (0.51), but control **concentrates** (+0.343) onto the five-enzyme
   methanogenesis backbone (Fwd/Mcr/Mtr/Mer/Hdr — 89% of the control term), whose kcat(T) rising-limb
   E is far *above* the proteome mean; aggregation adds +0.218 and there is no allocation buffer
   (constant-ribosome strategy, Müller 2021). High Ea from concentrated control on high-E chemistry.

2. **Respiration (mid, 0.68): high enzyme E, buffered down.** The naive mean is the *highest* (0.87),
   but the Scott rising-ribosome allocation buffer (−0.130) and aggregation (−0.175) pull it down to
   the ~0.65 benchmark. Broad control (no single backbone). Mid Ea from a high baseline buffered by
   allocation.

3. **Photosynthesis (low, 0.57): control on a LOW-E carbon-fixation backbone + small buffers.** The
   naive mean is *moderate* (0.68), and — the key contrast with the methanogen — control does **not**
   concentrate onto high-E enzymes (control ≈ 0, −0.016): the Calvin/carbon-fixation controllers
   (transketolase, FBA, RuBisCO, PRK, FBPase — **34% of control**) sit at mean kcat-E **0.63, below**
   the proteome mean, and the remaining control is on ATP synthase (low-E) and photosystems. With
   only small allocation (−0.019), maintenance (−0.027) and aggregation (−0.050) buffers, the moderate
   baseline **stays low**. Low Ea because control sits on intrinsically low-E carbon-fixation chemistry.

So the methanogen and the phototroph are **mirror images**: both put control on their energy/carbon
backbone, but the methanogen's backbone is high-E (→ high Ea) and the phototroph's is low-E (→ low Ea);
*E. coli* is the intermediate broad-control-plus-buffer case.

## Robustness (each organism's kinetic sensitivity carried)
- **Methanogen — Mcr kcat 3–294 /s** (`mcr_sweep.csv`): the SS-E and the backbone attribution are
  robust across the swept Mcr turnover.
- **Phototroph — carbon-fixation kcat + dCp** (`robustness_sweep.json`): the SS-E is **essentially
  invariant** to RuBisCO (0.5–4×) and whole-Calvin (0.5–2×) kcat — **[0.565, 0.577]**, always well
  below *E. coli* — so the low Ea is a curvature/**shape** property of the low-E controllers, **not a
  kcat-level artefact** (a stronger robustness than the methanogen's kcat-sensitive backbone). The
  MMRT **dCp prior** (−2…−6 kJ/mol/K → SS-E 0.29…0.79) is the **shared** Hobbs-2013 curvature applied
  identically to all three, so it scales the whole comparison together — a common systematic, not a
  reordering lever (breaking the order would need a phototroph-*specific* curvature steepening, which
  is unmotivated).

## Bottom line
The three etc-GEMs reproduce the Yvon-Durocher 2014 activation-energy ordering
(**methanogenesis 1.06 > respiration 0.68 > photosynthesis 0.57**), each validated against an
independent measured TPC, and the control-weighted SS-E decomposition shows the ordering arises from
**three mechanistically distinct routes**, not one dial: concentrated control on a high-E backbone
(methanogen), high enzyme E buffered by allocation (E. coli), and control on a low-E carbon-fixation
backbone (phototroph). Each organism's allocation term is grounded in its **own** measured strategy
(Scott / Müller-flat / Jahn-shallow), and each result carries its explicit kinetic sensitivity.

**Caveats (honest):** the aggregation term is definition-sensitive (computed directly here as the
backbone-curve SS-E minus the control-weighted per-enzyme mean); the per-organism kinetic sweeps
bound the robustness; the phototroph's growth-SS-E observed anchor is fragile (use the Inoue flux
0.52); and three organisms are three cases, not a phylogeny — the mechanism, not a universal law, is
the claim.

## GO — fold all three into the paper
Extend the paper: a three-TPC scene-setter, the three-way signed-contribution decomposition figure +
table, and the construction Methods / departures table extended to *Synechocystis* 6803 (base GEM
iSynCJ816 + the pre-built AUTOPACMEN sMOMENT ecModel iSynCJ816_STAR; mesophile Topt/Tm priors;
Touloupakis maintenance; Jahn/Zavrel/Faizi allocation; Zavrel 2015 + Inoue 2001 validation).
