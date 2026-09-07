# Claude Code prompt — M1b (methanogen build): curate iMR539 into a carbon-honest H2/CO2 autotroph (gap-fill the missing biomass precursors, close organic-C leaks, unpin CH4) before the ecModel (autonomous)

Run from the project root (`.../MICROADAPT/etcGEMs`). MODEL CURATION on the M. maripaludis base GEM
only. No enzyme-constraint (ecModel) layer, no thermal layer, no calibration (those are M2+). Plain
FBA. The goal: a clean, CARBON-HONEST autotroph on H2/CO2 whose biomass carbon all derives from CO2,
so the M2 enzyme-constrained growth numbers are meaningful.

NOTE TO USER: launch in an auto-approving mode. Use Gurobi if available (print the solver).

CONTEXT (from M1, strains/mmaripaludis/outputs/M1_audit_and_readiness.md): iMR539 loads + grows on
H2/CO2 (Wolfe cycle correct), but (1) four biomass precursors have NO biosynthesis and are supplied
by free uptake — Membrane_lipid, Flagellin, NAC, tRNA-SeCys — so growth is not carbon-honest (mu=0 if
any is closed); (2) organic-C leaks exist (acetate, octadecenoate exchanges); (3) the shipped model
pins CH4 at (50,50). Resolve these. The mu overshoot (~0.55/h) is EXPECTED for plain FBA and is NOT to
be fixed here — M2's enzyme constraint sets the rate.

---

```
Work AUTONOMOUSLY; commit in parts; print a summary. Read first: strains/mmaripaludis/outputs/
M1_audit_and_readiness.md, strains/mmaripaludis/model/ (the iMR539 SBML), strains/mmaripaludis/
strain.yaml + media/, docs/METHANOGEN_ETCGEM_PLAN.md, and the Goyal 2016 / Li 2023 metabolic detail
in the plan (pathway structure). cobra + FBA only.

PART A - resolve the four missing biomass precursors (investigate, then decide per component)
For EACH of Membrane_lipid, Flagellin, NAC, tRNA-SeCys: identify what the metabolite is, whether its
biosynthesis pathway is present/partial/absent in iMR539, and whether it is essential for growth. Then
choose the LEAST-INVASIVE DEFENSIBLE fix, and JUSTIFY it:
  * GAP-FILL the biosynthesis (add the missing reaction(s), from the known M. maripaludis pathway /
    homology / a reference DB) if it is a genuine required biomass component with a real pathway gap
    (likely for the archaeal ether MEMBRANE LIPID isoprenoid route, and for tRNA-SeCys — M. maripaludis
    uses selenoproteins, so selenocysteine synthesis is real; ensure selenium is a medium trace and the
    SeCys-tRNA charging pathway is present).
  * REMOVE from the biomass reaction if it is non-essential / not a true growth requirement (FLAGELLIN
    is a structural protein, dispensable for growth — folding it out of biomass is defensible; justify).
  * SUPPLY as a DEFINED medium trace only if it is a genuine exogenous requirement the organism takes
    up (state why, and keep it minimal + documented).
Prefer synthesis over free uptake wherever the pathway can be closed; the aim is autotrophy. Report the
decision + reason for each of the four.

PART B - close organic-carbon leaks + unpin CH4
- Close the free organic-carbon exchanges (acetate, octadecenoate, and any other organic-C uptake) so
  CO2 is the sole carbon source (M. maripaludis is autotrophic on H2/CO2). Keep CO2, H2, ammonia,
  phosphate, sulfide/Se trace, and mineral exchanges open (availability, not pinned).
- Remove the shipped CH4 pin at (50,50): make CH4 a free product (lower bound 0, upper bound +inf or
  the default), so methane is an OUTPUT, not a fixed flux.

PART C - verify carbon-honest autotrophy
- Confirm the curated model grows on H2/CO2 with NO free organic-carbon uptake and (for the gap-filled
  precursors) with the free precursor uptakes now CLOSED — i.e. closing each previously-free precursor
  exchange no longer zeros growth, because it is synthesised (or was justifiably removed). Report a
  CARBON BALANCE: all biomass carbon traces to CO2. Report mu (still plain FBA — the overshoot is
  expected and fine) and the H2:CO2:CH4 ratio (should stay ~4:1:1).
- Sanity re-checks unchanged: no growth without electron donor or carbon.

PART D - save + document + GO/NO-GO
- Save the curated model (a new SBML, e.g. strains/mmaripaludis/model/iMR539_curated.xml; keep the
  original). Update strain.yaml to point at the curated model. Write strains/mmaripaludis/outputs/
  M1b_curation.md: each precursor decision + justification, the leaks closed, the CH4 unpin, the carbon
  balance, and any remaining approximation stated honestly.
- GO/NO-GO for M2 (ecModel), listing what M2 inherits (a carbon-honest autotroph) and any residual
  caveats.

VERIFY (report all)
1. Each of the four precursors resolved with a justified per-component decision (gap-fill / remove /
   trace); the model no longer needs free uptake of any biomass precursor for growth.
2. Organic-C leaks closed (CO2 the sole C source); CH4 unpinned (free product); carbon balance shows
   all biomass C from CO2.
3. Curated model grows on H2/CO2 (mu reported; overshoot expected/left for M2); H2:CO2:CH4 ~4:1:1;
   donor/carbon sanity checks pass.
4. Curated SBML saved (original kept); strain.yaml updated; M1b_curation.md written with justifications
   + honest caveats; GO/NO-GO for M2.

CONSTRAINTS
- Curation only (gap-fill/biomass/exchange edits). Plain FBA. NO ecModel, NO thermal layer, NO
  calibration, and do NOT try to fix the mu overshoot (that is M2's enzyme constraint).
- Prefer autotrophic synthesis over free uptake; least-invasive defensible fixes; justify every change.
- Keep the original model; edits on a curated copy.
- Autonomous; commit in parts: "methanogen M1b: resolve missing biomass precursors (gap-fill/curate)",
  "methanogen M1b: close organic-C leaks + unpin CH4; carbon-honest autotroph + curation note".
```
