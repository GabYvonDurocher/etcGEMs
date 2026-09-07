# Claude Code prompt — M2b (methanogen build): refine the base kcats (literature overrides for the high-pool offenders + a documented DLTKcat floor) so the emergent undershoot and the control attribution are honest, before the thermal layer (autonomous)

Run from the project root (`.../MICROADAPT/etcGEMs`). PARAMETERISATION REFINEMENT of the M2 base
ecModel's kcat table only. NO thermal layer (M3), NO calibration (M4). Still emergent-then-calibrate:
do NOT tune to mu_max. The aim is to remove the SYSTEMATIC DLTKcat archaeal-underprediction artefact
(28% of predictions <1/s) that (a) makes the emergent undershoot ~13x — far larger than E. coli's and
too big to defend via a global kcat_scale — and (b) would distort the Ea control attribution (an
artefactually-low kcat -> artefactually-high pool share -> a reaction that falsely looks rate-limiting,
e.g. PFOR at 0.26/s).

NOTE TO USER: launch in an auto-approving mode, from the venv with Gurobi. It looks up literature/BRENDA
kcats (web).

CONTEXT (from M2, strains/mmaripaludis/outputs/M2_ecmodel.md): 527 enzymatic reactions; kcat = 11
measured-core + 293 DLTKcat + 223 fallback. Emergent mu@37 C = 0.0185/h (~13x under ~0.23-0.35/h).
Mcr = 39.7% of the pool (the Ea target, kcat ~8.84/s, lit 1-100/s). PFOR predicted at 0.26/s is the #2
pool consumer.

---

```
Work AUTONOMOUSLY; commit in parts; print a summary. Read first: strains/mmaripaludis/outputs/
M2_ecmodel.md, the M2 kcat+MW+source table (strains/mmaripaludis/dltkcat/ + summary CSV), src/etcgem/
{enzyme_cost.py, providers.py (from_gem_smoment), dltkcat.py, config.py}, strains/mmaripaludis/
strain.yaml. Gurobi with a GLPK-abort guard; print the solver. Keep it temperature-independent (M3 adds
kcat(T)); do NOT change the pool (still the grounded 0.1125 g/gDW) or tune to mu_max.

PART A - rank the offenders (who consumes the pool, and is their kcat plausible?)
- Rank all enzymatic reactions by POOL-MASS CONSUMPTION at the emergent 37 C solution. Report the top
  ~20 with: reaction, enzyme/gene, MW, current kcat, source (measured/DLTKcat/fallback), pool share.
- FLAG the ones whose kcat is both (i) high pool share AND (ii) implausibly low (DLTKcat <~1/s, or
  otherwise far below known values). These are the correction targets (expect PFOR/PorABCDEF,
  CODH/acetyl-CoA synthase (Cdh), and a handful of central-carbon / energy enzymes).

PART B - literature / measured kcat overrides for the flagged offenders
- For each flagged high-pool offender, source a measured kcat from the literature / BRENDA, preferring:
  M. maripaludis > another methanogen/archaeon > a well-characterised homolog. CITE each value (source
  + organism + conditions) and record it as a documented override with provenance in the kcat table.
- RE-PIN Mcr carefully (it is the Ea target): give it the best-supported literature kcat + an explicit
  uncertainty range; note the value and its sensitivity, since it drives the eventual Ea attribution.
- Keep the M2 measured-core (Milton 2018) values; these overrides ADD to that measured set.

PART C - documented floor for the residual DLTKcat tail
- For the remaining DLTKcat predictions that are still implausibly low (<~1/s) and NOT individually
  overridden, apply a single DEFENSIBLE FLOOR (justify the value — e.g. a low percentile of the
  measured/BRENDA kcat distribution, or ~1/s as the lower bound of physiologically-plausible central-
  metabolic turnover). Document the floor + how many reactions it touches. Do NOT floor the genuinely
  slow measured/literature values (e.g. Mcr) — the floor is only for the untrustworthy prediction tail.

PART D - re-report the emergent model (honest; not tuned)
- Recompute emergent mu@37 C with the refined kcats. Report the NEW undershoot vs ~0.23-0.35/h — target
  a defensible E. coli-like few-fold (not 13x); if still undershooting, attribute the residual honestly
  (M4 closes it via kcat_scale/sigma). Confirm: methanogenesis intact (H2:CO2:CH4 ~4:1:1); the pool
  still binds; the pool DISTRIBUTION after refinement — does Mcr remain the dominant consumer (expect
  its share to CLARIFY/rise as PFOR etc. are corrected)? Report the before/after pool shares of Mcr and
  the corrected offenders.

PART E - save + document
- Update the kcat table (with override provenance + the floor) and the M2 note (or a new M2b_kcat_
  refinement.md): the offenders, each override + citation, the floor + justification, before/after
  emergent mu and pool distribution, and the honest residual. GO/NO-GO for M3 (thermal layer).

VERIFY (report all)
0. solver=gurobi; temperature-independent; pool unchanged (0.1125); not tuned to mu_max.
1. Top pool consumers ranked; implausible-low high-pool kcats flagged (PFOR/CODH etc.).
2. Literature/BRENDA overrides applied with CITATIONS (organism/conditions); Mcr re-pinned with an
   uncertainty range and its sensitivity noted.
3. Documented floor for the residual DLTKcat tail (value justified; count reported); genuine slow
   measured values not floored.
4. Refined emergent mu reported (undershoot reduced toward a defensible few-fold; residual attributed);
   methanogenesis intact; Mcr remains/becomes the dominant pool consumer (before/after shares).
5. kcat table + M2b note updated with full provenance; GO/NO-GO for M3.

CONSTRAINTS
- kcat-table refinement only; temperature-independent; pool unchanged; NOT tuned to mu_max; no thermal
  layer, no calibration. Every override CITED; the floor justified + documented.
- Autonomous; commit in parts: "methanogen M2b: rank pool consumers + flag implausible archaeal kcats",
  "methanogen M2b: literature/BRENDA kcat overrides (PFOR/CODH/Mcr...) + documented DLTKcat floor",
  "methanogen M2b: refined emergent mu + pool distribution + M2b note".
```
