# Claude Code prompt — M2 (methanogen build): build the enzyme-constrained (ecModel) layer on the curated M. maripaludis GEM — sMOMENT pool via enzyme_cost, kcats from measured core + DLTKcat (autonomous)

Run from the project root (`.../MICROADAPT/etcGEMs`). Builds the ENZYME-CONSTRAINT (ecModel) layer on
the M1b carbon-honest autotroph, reusing src/etcgem/enzyme_cost (sMOMENT total-protein pool). This is
the BASE (temperature-INDEPENDENT) ecModel. NO thermal layer (M3), NO calibration (M4). Use the
emergent-then-calibrate philosophy: set a GROUNDED proteome pool from independent data and report the
resulting mu HONESTLY — do NOT tune the pool to hit the observed mu_max (that is M4).

NOTE TO USER: launch in an auto-approving mode, from the venv with Gurobi + DLTKcat.

CONTEXT (from M1/M1b): curated iMR539 (strains/mmaripaludis/model/iMR539_curated.xml) is a carbon-
honest H2/CO2 autotroph; 85% metabolic GPR coverage; MMP gene tags map to UniProt UP000000590; core
methanogenesis/electron-bifurcation enzymes are gene-mapped (Mcr=McrABG MMP1555-7, Mtr, Fwd, Hmd,
HdrABC, Fru/Vhu, Fdh, Na+-A1A0 ATP synthase). Recon recommended a Python sMOMENT layer reusing
enzyme_cost. The plain-FBA mu (~0.55/h) overshoots the ~0.23-0.35/h literature value — the enzyme pool
should bring it down.

---

```
Work AUTONOMOUSLY end to end; commit in parts; print a summary. Read first: src/etcgem/{enzyme_cost.py
(the sMOMENT total-protein pool constraint + how base_cost/kcat enter),providers.py (how eciML1515 is
wrapped as an enzyme-constrained provider; add a path for a sMOMENT-on-GEM methanogen provider),
config.py, dltkcat.py (the DLTKcat kcat-prediction pipeline + input format),sectors.py}, strains/
mmaripaludis/{model/iMR539_curated.xml, strain.yaml, outputs/M1b_curation.md, outputs/
M1_audit_and_readiness.md}, and docs/METHANOGEN_ETCGEM_PLAN.md (the Milton 2018 measured kinetics +
Xia proteome + the plan). Gurobi with a GLPK-abort guard; print the solver.

PART A - per-enzyme kcat + MW table (the parameterisation)
- Map each enzymatic reaction -> gene(s) -> UniProt (via the MMP->UP000000590 map) -> protein
  sequence + MW. Report GPR/sequence coverage.
- Assign a base kcat to each enzymatic reaction, by SOURCE PRIORITY, and record the source per enzyme:
  1) MEASURED CORE: derive kcat from measured specific activities for the electron-bifurcation /
     energy core — Milton et al. 2018 (the three Hdr complexes + Vhu/Fdh; SA ~25-165 U/mg) and classic
     biochemistry for Mcr, Mtr, Fwd, Hmd, Fru/Frc. Convert SA (U/mg = umol/min/mg) to kcat (1/s) using
     the complex/subunit MW: kcat ≈ SA[U/mg] × MW[g/mol] / 60000. SHOW the conversion + the assumed MW
     per core enzyme. PAY SPECIAL ATTENTION TO Mcr (methyl-CoM reductase) — it is the famously slow
     terminal enzyme and the Ea hypothesis target; source its kcat carefully from the literature (it is
     low, ~1-100/s depending on source) and cite/flag the value + uncertainty.
  2) DLTKcat: predict kcat for the remaining enzymatic reactions from sequence (reuse the existing
     DLTKcat pipeline). Flag that DLTKcat is bacteria-trained (archaeal accuracy uncertain) — a prior.
  3) FALLBACK: dataset-mean kcat for reactions with no gene/sequence.
- Output a kcat+MW+source table (strains/mmaripaludis/dltkcat/ + a summary CSV). Report the coverage
  breakdown: measured-core / DLTKcat / mean-fallback counts.

PART B - build the sMOMENT ecModel (reuse enzyme_cost)
- Attach the sMOMENT total-protein pool constraint to the curated GEM using enzyme_cost: each reaction
  i costs MW_i/kcat_i per unit flux, drawn from a shared proteome pool. Add a provider path/type (e.g.
  "smoment_gem") so strains/mmaripaludis loads as an enzyme-constrained model via the standard config/
  CLI (update strain.yaml). Keep it temperature-INDEPENDENT here (M3 adds kcat(T)/unfolding).

PART C - set a GROUNDED proteome pool (do NOT tune to mu_max)
- Set the pool budget (P_total × f_metab × sigma) from INDEPENDENT data: the measured M. maripaludis
  proteome (Xia 2006/2009) enzyme-mass fraction if usable, else a literature methanogen total-protein
  value × metabolic fraction × the literature saturation sigma (~0.4-0.5). Document the choice.
- Report the resulting enzyme-constrained mu at the reference T (~37-38 C). Do NOT tune the pool to
  match mu_max ~0.23-0.35/h — report honestly whether the a-priori pool over/under-shoots (this is the
  emergent methanogen prediction; M4 calibrates sigma/pool to the Jones TPC). Confirm the pool BINDS
  (is the limiting constraint) and that mu moved in the right direction vs the plain-FBA 0.55/h.

PART D - enzyme-cost artefact audit (now possible with costs)
- With enzyme costs assigned, repeat the artefact audit at the enzyme level (analogue of the E. coli
  uncosted-O2-sink audit): find reactions carrying flux at ZERO/negligible enzyme cost that bypass
  costed pathways or short-circuit the energy metabolism (e.g. free ferredoxin/electron shortcuts,
  uncosted energy-currency reactions). LIST them; CLOSE the clearly-artefactual ones (as a documented,
  reversible default, like close_free_energy_sinks) with justification; report the growth effect.

PART E - validate the base ecModel
- Confirm: enzyme-constrained growth on H2/CO2 with realistic-direction mu; methanogenesis intact
  (H2:CO2:CH4 ~4:1:1; Mcr and the core carry flux AND enzyme cost); the pool is the binding constraint;
  the core enzymes' costs are physically sensible (report Mcr's mass fraction / usage). Save the base
  ecModel + provider config; write strains/mmaripaludis/outputs/M2_ecmodel.md (kcat sources + coverage,
  the pool choice + resulting mu, the artefact closures, and readiness for M3).

VERIFY (report all)
0. solver=gurobi. Base ecModel loads via the standard provider/CLI for strains/mmaripaludis.
1. kcat+MW+source table built: coverage breakdown (measured-core / DLTKcat / fallback); core enzymes
   (esp. Mcr, Mtr, Hdr, hydrogenases) sourced from measured/literature with the SA->kcat conversion
   + MW shown; Mcr value + uncertainty flagged.
2. sMOMENT pool attached via enzyme_cost; temperature-independent; provider/strain.yaml wired.
3. Grounded pool set from independent data (documented); resulting mu reported HONESTLY (not tuned to
   mu_max); pool binds; mu moved down from the plain-FBA 0.55/h.
4. Enzyme-cost artefact audit done; artefacts listed + clearly-artefactual ones closed (reversible,
   justified); growth effect reported.
5. Methanogenesis intact (4:1:1; Mcr carries flux+cost); base ecModel + M2_ecmodel.md saved; GO/NO-GO
   for M3 (thermal layer).

CONSTRAINTS
- Base (temperature-INDEPENDENT) ecModel only. NO thermal layer (M3), NO calibration (M4). Emergent-
  then-calibrate: grounded pool, honest mu — do NOT tune to mu_max.
- Reuse enzyme_cost (sMOMENT); do not fork the E. coli pipeline. Keep the curated GEM intact; build the
  ecModel as a wrapped/derived model.
- Measured/literature kcats for the core (cite/flag, esp. Mcr); DLTKcat as a prior for the rest.
- Autonomous; commit in parts: "methanogen M2: per-enzyme kcat+MW table (measured core + DLTKcat + fallback)",
  "methanogen M2: sMOMENT ecModel via enzyme_cost + provider wiring + grounded pool",
  "methanogen M2: enzyme-cost artefact audit + base ecModel validation + M2 note".
```
