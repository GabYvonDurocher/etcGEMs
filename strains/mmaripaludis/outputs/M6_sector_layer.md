# M6 — M. maripaludis proteome-sector / allocation layer (its OWN strategy)

Adds a proteome-sector + growth-law layer to the methanogen (previously a single sMOMENT
pool, so its allocation term in the M5 Ea decomposition was 0 *by construction*). Grounded in
the organism's **own** allocation physiology, **not** the bacterial Scott law, so the
cross-organism allocation comparison is symmetric. SS-E for descriptors; Gurobi.

## PART A — the methanogen's allocation data (cited)
**Müller et al. 2021, PNAS 118:e2025854118** ("An alternative resource allocation strategy in
the chemolithoautotrophic archaeon *Methanococcus maripaludis*"): in energy(formate)-limited
chemostats from 0.09 down to 0.002 /h (≈1% of mu_max 0.23),
- **the ribosomal proteome fraction is CONSTANT** with growth rate (E. coli/yeast *increase*
  it with mu),
- **catabolic/anabolic proteome allocation is INVARIANT** with growth rate,
- cells **maintain maximum methanogenesis capacity** even at slow growth.

So the growth-law **coupling slope is ~0 (flat)**, not the bacterial Scott ~0.30 — this is the
finding, recorded honestly. Sector mass fractions (Xia 2006/2009 + Müller; the most abundant
proteins are the S-layer, Mcr subunits ~10% of protein, Hsp60 chaperonin, EF/ribosomal
proteins): **f_metab 0.55 / f_maint 0.30 / f_bio 0.15** (methanogenesis-heavy metabolic sector,
low constant ribosome fraction consistent with slow growth).

## PART B — implementation (reused `sectors.py`, no fork)
`strain.yaml` `proteome_sectors` block wires the layer onto the `smoment_gem` provider with the
methanogen's own params: **growth_law_slope 0.0** (flat, Müller), a **constant ribosome cap at
mu_max** (translation_coeff = f_bio·P/mu_max = 0.15·0.2045/0.23 = 0.133), so the ribosome cap
sits *above* the TPC peak and never clips — the metabolic pool binds across the TPC. Two
integration fixes (E. coli path untouched — the anchor fix is `smoment_gem`-gated,
`nominal_kcat_scale` defaults to 1.0):
- `add_proteome_sectors` gains `nominal_kcat_scale` (=7.223, the M4 magnitude) so the sector
  co-limit calibrates where the model grows (the a-priori kcat_scale=1 methanogen is
  maintenance-crushed to mu≈0);
- config resets the sector NGAM anchor `atpm_nom_lb` to the **25 °C** NGAM so the sector
  branch's ngam_T rescaling yields NGAM(37 °C)=7.836 (Goyal), not a double-scaled 14.6.

## PART C — forward-check: NO re-calibration needed (`M6_forward_check.json`)
With the sector layer ON and the **M4 posterior-median** parameters, the TPC is **identical**
to the single-pool M4:
| | peak (1/h) | Topt (°C) | CTmax (°C) | SS-E |
|---|---|---|---|---|
| single-pool M4 | 0.186 | 36 | 49 | 1.056 |
| **sectored M6 (flat GL)** | **0.186** | **36** | **49** | **1.056** |

**max\|Δmu\| across the whole TPC = 0.00000.** Jones is still reproduced (peak 0.181, obs SS-E
1.04). The flat growth law is **exactly neutral**, so the M4 posterior holds unchanged — no
re-fit. Directly measured **allocation buffer = SS-E(GL on, slope 0) − SS-E(GL off) =
1.056 − 1.056 = +0.000 eV**, vs **E. coli −0.130**.

## Result: the M5 allocation asymmetry is real physiology, not a modelling artefact
The methanogen's allocation buffer is ~0 **because of its own constant-ribosome-fraction
strategy** (Müller 2021), not because the single-pool model omitted the layer. The
cross-organism comparison is now **symmetric in structure** (both organisms carry a
sector/growth-law layer) and the buffer difference (E. coli −0.13 vs methanogen 0) is grounded
in each organism's **own** allocation law (Scott vs flat). This strengthens the M5 bottom line:
the methanogen's higher growth Ea comes from control on the high-E backbone **and** the
genuinely weak allocation buffer that its slow-growth physiology entails.

## PART D — GO for M5-redo
**GO.** The sectored methanogen is wired, forward-checked (identical fit, no re-calibration),
and the allocation term is now a *measured* 0.000 (grounded), not a structural 0. M5-redo can
re-run the methanogen SS-E dissection on the sectored model and report the 4 named terms with
the allocation term now on the same footing as E. coli's — expected to confirm the M5 numbers
(the layer is neutral) while making the allocation comparison honest and symmetric.

**Caveats (stated):** the sector fractions (0.55/0.30/0.15) are grounded but approximate (a
full Xia-proteome sector parse would refine them); the flat slope is the robust, cited
quantity. translation_coeff is pinned to mu_max 0.23 (Müller), so the ribosome cap is
non-binding across the modelled TPC — a deliberate representation of "constant ribosome
fraction", not a fitted lever. The single-pool M4 model remains available (`proteome_sectors.
enabled: false`).
