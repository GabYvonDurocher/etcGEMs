# M2b — kcat refinement (remove the DLTKcat archaeal-underprediction artefact)

Parameterisation refinement of the M2 base ecModel's kcat table **only**. No thermal layer
(M3), no calibration (M4). Temperature-independent; **pool unchanged** (0.1125 g/gDW); **not
tuned to mu_max**. Solver: **Gurobi**. The goal: remove the systematic DLTKcat
archaeal-underprediction (28% of predictions <1/s) that both inflated the emergent
undershoot (~10×) and distorted the pool/Ea attribution (a low kcat → a high pool share → a
reaction that falsely looks rate-limiting, e.g. PFOR at 0.26/s = 18.8% of the pool).

## PART A — ranked offenders (M2 baseline, `dltkcat/pool_ranking_M2.csv`)
Top pool consumers at the emergent 37 °C solution, flagged where pool >1% AND kcat <2/s AND
not measured-core:
| reaction | enzyme | pool% | kcat | source |
|---|---|---|---|---|
| rxn03127 | Mcr | 39.7% | 8.84 | measured (low-end guess) |
| **rxn05938** | **PFOR** (pyruvate:Fd oxidoreductase) | **18.8%** | **0.26** | DLTKcat ⚠ |
| rxn11938 | Fwd (formyl-MF dehydrogenase) | 8.1% | 8.53 | measured |
| rxn03020 | Mtr | 6.0% | 62.2 | measured |
| **rxn05939** | **OGOR** (2-oxoglutarate:Fd oxidoreductase) | **1.8%** | **0.23** | DLTKcat ⚠ |
| **rxn03147** | phosphoribosyl-aminoimidazole (purine) | **1.7%** | **0.02** | DLTKcat ⚠ |

## PART B — literature / BRENDA overrides (`dltkcat/kcat_overrides.csv`, each cited)
- **PFOR** rxn05938: 0.26 → **16.83/s** — BRENDA EC 1.2.7.1 (pyruvate synthase, ferredoxin),
  SA ~7.4 U/mg (pyruvate + CoA); kcat = 7.4 × 136.5 kDa ×1000/60000.
- **OGOR** rxn05939: 0.23 → **11.99/s** — *Aeropyrum pernix* (archaeon) Ape1473/1472 Vmax
  7.46 U/mg (Nishizawa 2005, FEBS Lett; BRENDA EC 1.2.7.3).
- **Mcr re-pinned** (the Ea target), measured core: SA 3 → **20 U/mg** (mature Mcr *average*,
  *Methanothermobacter*; Thauer, ACS Biochemistry 2019; Nature 2025), U = µmol CH4/min/mg →
  kcat 8.84 → **58.92/s**. **Uncertainty range** SA 1–100 U/mg → kcat **~3–294/s**; source is
  a thermophile (mesophilic M. maripaludis at 37 °C may be lower); sensitivity below.
- CODH (fallback 4.87/s) and ACS (DLTKcat 7.09/s) left as-is: both are above the floor and no
  clean archaeal kcat was found — a documented residual uncertainty (combined ~8% of pool).

## PART C — documented floor for the residual DLTKcat tail
DLTKcat predictions **< 1.0/s → 1.0/s** (**79 reactions**). Justification: 1/s is the lower
bound of physiologically-plausible central-metabolic turnover (the measured methanogen core
spans 9–290/s; BRENDA central-C kcats are rarely <1/s). Applied **only** to DLTKcat (not to
measured/literature/fallback), so genuine slow measured values (Mcr, Fwd) are never floored.
Final table: 11 measured_core + 2 literature_override + 291 dltkcat (79 floored) + 223 fallback.

## PART D — refined emergent model (`outputs/M2b_validation.json`; honest, not tuned)
- **Emergent mu @37 °C = 0.044 /h** (M2 was 0.0185). Pool still **binds**; methanogenesis
  intact (**H2:CO2:CH4 = 4.12:1.06:1**); sanity: no growth without donor or carbon.
- **Undershoot vs the Jones 1983 digitized peak (0.181 /h @37 °C) = 4.1×** (M2 was ~10×) — a
  defensible, E. coli-like few-fold. The residual is closed in M4 by the global
  `kcat_scale`/σ in-vitro→in-vivo lever (the E. coli model used kcat_scale ≈ 1.25), plus
  f_metab refinement against the Xia proteome.
- **Pool distribution before → after** (this is the substantive result):
  | enzyme | M2 pool% | M2b pool% |
  |---|---|---|
  | PFOR | 18.8 | **0.7** (artefact removed) |
  | Mcr | 39.7 | **14.2** (re-pinned to cited kcat) |
  | Fwd | 8.1 | **19.3** (now #1) |
  | Mtr | 6.0 | 14.2 |
  | Mer / Hdr | 3.0 / 2.4 | 7.2 / 5.7 |

  **Honest correction to the M2 narrative:** with Mcr at its best-supported literature kcat,
  Mcr is **not** uniquely dominant — the methanogenesis backbone (**Fwd + Mtr + Mcr + Mer +
  Hdr ≈ 60% of the pool**) *shares* the enzyme cost, and the current #1 is **Fwd**
  (formylmethanofuran dehydrogenase, kcat 8.53/s). The M2 "Mcr dominates" reading was partly
  an artefact of the low-end Mcr guess. **Caveat:** the *ranking within* the backbone is
  sensitive to the core kcats — Fwd/Mtr/Mer are classic-biochem representative values, not as
  carefully sourced as Mcr — so which single enzyme is "rate-limiting" at 37 °C is not robust
  from the static pool share alone. The real Ea-control test is the temperature-dependent
  control analysis (kcat(T) shapes) in M3/M5, not the 37 °C pool share.

## PART E — GO / NO-GO for M3 (thermal layer)
**GO.** The base ecModel now has a defensible kcat parameterisation: the DLTKcat
underprediction artefact is removed (overrides + floor), the emergent undershoot is a
few-fold (4.1×), and the pool distribution is honest (methanogenesis backbone shares ~60%,
no artefactual bottleneck). Refreshed `model/iMR539_ecmodel_base.xml`.

**Residual caveats carried into M3/M4:**
1. **Mcr kcat uncertainty (3–294/s)** directly sets its share and the eventual Ea attribution
   — the single most important value to pin down for a mesophilic Mcr at 37 °C.
2. **Fwd/Mtr/Mer core kcats** are representative classic-biochem values, not primary-sourced;
   they now set the backbone ranking — worth sourcing if the Ea attribution hinges on them.
3. **CODH/ACS** (acetyl-CoA pathway) kcats remain fallback/DLTKcat (~8% of pool).
4. **Residual 4.1× undershoot** — expected; M4 closes it via kcat_scale/σ + f_metab (Xia).
