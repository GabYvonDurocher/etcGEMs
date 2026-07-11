# E. coli Ea dissection — re-based to the Sharpe-Schoolfield E (window-independent)

This is the SS-E re-base of the E. coli activation-energy dissection. The windowed-Arrhenius
version is kept, unchanged, in `../ea_dissection/` as a deprecated cross-check. Motivation:
the Ea-definition audit (`outputs/ea_definition_audit/`) showed the windowed slope spans
0.42-1.41 eV per curve and is not comparable across curves/organisms; the Sharpe-Schoolfield
E (Schoolfield 1981; `src/etcgem/sharpe_schoolfield.py`) is window-independent, field-standard,
and — decisively — makes the model comparable to the observed data.

## Definitions (re-based)
- **Ea_org := Sharpe-Schoolfield E** fit to the tuned rich-BHI growth TPC (dense grid).
- **Per-enzyme Ea_i := the rising-limb Arrhenius E of kcat_i(T) alone** (`Ea_kcat_eV`). The
  native fraction f_N is the enzyme's *deactivation* side (organism E_h/T_h), and its
  rising-limb contribution is **-0.008 eV control-weighted (negligible)** — verified in the
  saved per-enzyme frames — so it cleanly leaves the E decomposition.
- The control coefficients C_i are **reused** from the windowed run (they do not depend on the
  Ea definition), so no per-enzyme re-perturbation was needed.

## SS-E decomposition (`decomposition_ss.json`)
Rich **BHI**: Ea_org(SS-E) = **0.678 eV** (fit R2 0.93; windowed slope cross-check reproduces
0.909):

| term | eV |
|---|---|
| naive (unweighted) enzyme mean | 0.872 |
| + control weighting | +0.106 |
| = control-weighted mean | 0.978 |
| allocation (growth law) | −0.126 |
| maintenance NGAM(T) | +0.005 |
| residual (nonlinear aggregation) | −0.178 |
| **= organism Ea (SS-E)** | **0.678** |

**glucose-minimal**: Ea_org(SS-E) = **0.890**, and the decomposition **closes cleanly**
(residual +0.001; sum_C_i 0.96 vs BHI 0.56). Emergent BHI SS-E 0.500; **observed VdL SS-E
0.558** (model 0.678 matches observed within the sparse-curve CI, and both sit on the ~0.65 eV
metabolic benchmark).

## The large BHI residual is honest, not a defect
Even with the growth law OFF and NGAM flat, the SS-E of the composite growth curve (0.80 eV)
sits ~0.18 below the control-weighted mean of the individual enzymes' *windowed* kinetic E
(0.98). The Sharpe-Schoolfield functional reads a lower E from an aggregate curve than from its
parts — an **aggregation nonlinearity**, largest in rich medium (sharp peak, growth law binds,
sum_C_i 0.56) and ~zero in glucose (Arrhenius-like, sum_C_i 0.96). This is a property of the
window-independent convention, reported transparently.

## Mechanism robust to the definition change
- Control-weighting **raises** Ea (cw 0.978 > unweighted 0.872 rich; 0.906 > 0.789 glucose).
- Allocation **lowers** Ea (−0.126 rich; ~0 glucose).
- Top pathways **unchanged**: lipid metab (0.198, fabB/fadA/acpP) > glycolysis (0.152, gapA)
  in rich BHI; amino-acid biosynthesis (argG) on glucose. (fN negligible, so C_i·Ea_kcat ranks
  as before.)
- Medium dependence holds: BHI 0.68 < glucose 0.89.
- SS-E robustness stable at 0.68-0.69 over x0.5-1.0 enzyme-heterogeneity spread.

## GO for M5 (methanogen dissection) on the SAME SS-E footing
**GO.** With E. coli now on the Sharpe-Schoolfield footing (Ea_org 0.68, matching observed
0.56), the methanogen dissection can be run and compared cleanly: the audit already puts the
methanogen SS-E at ~1.0 (observed Jones 1.04) — clearly **higher** than E. coli's ~0.6, the
signal the windowed slope had obscured. The methanogen M5 should: (a) fit Ea_org as SS-E of the
calibrated Jones TPC, (b) define per-enzyme Ea_i = kcat(T) rising-limb E (same convention),
(c) decompose with the methanogen control coefficients, testing whether Mcr / the
methanogenesis backbone is the higher-Ea controlling set. Carry the Mcr kcat 3-294/s
sensitivity. NOTE the E. coli allocation term is a growth-law/sector effect the methanogen
single-pool model lacks — so the cross-organism comparison of the *allocation* buffer is not
yet symmetric (the methanogen sector layer is deferred).
