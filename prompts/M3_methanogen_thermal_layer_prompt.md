# Claude Code prompt — M3 (methanogen build): add the thermal layer (kcat(T) MMRT + two-state unfolding + NGAM(T)) to the M. maripaludis ecModel, and produce the emergent (a-priori) methanogenesis TPC (autonomous)

Run from the project root (`.../MICROADAPT/etcGEMs`). Adds the TEMPERATURE-DEPENDENT envelope to the
M2b base ecModel, reusing the E. coli thermal machinery (src/etcgem/mmrt.py, unfolding.py). Produces
the EMERGENT (nothing-fit) methanogen growth TPC and compares it a-priori to the Jones 1983 curve.
NO calibration (M4), NO Ea dissection (M5). Emergent-then-calibrate: nothing tuned to the data.

NOTE TO USER: launch in an auto-approving mode, from the venv with Gurobi.

CONTEXT (M2/M2b): carbon-honest H2/CO2 autotroph + base sMOMENT ecModel with refined kcats; emergent
mu@37 C = 0.044/h (~4x under the Jones peak 0.181/h — an honest, E. coli-like few-fold). Pool binds.
Mcr NOT uniquely dominant (14%); the methanogenesis backbone (Fwd/Mtr/Mcr/Mer/Hdr ~60%) shares it.
Mcr kcat 58.9/s, uncertainty 3-294/s (carry forward to M5). The M2b-deferred ATP drain (rxn00062)
becomes NGAM(T) here.

---

```
Work AUTONOMOUSLY end to end; commit in parts; print a summary. Read first: src/etcgem/{mmrt.py
(kcat(T) MMRT), unfolding.py (two-state native fraction f_N(T), Tm), enzyme_cost.py (how kcat(T)/f_N
enter the pool cost; the E. coli set_temperature + NGAM(T) gate), providers.py (from_gem_smoment +
how the E. coli thermal envelope is wired), sectors.py (NGAM(T) + the growth-law toggle),
config.py, tpc.py (the TPC engine + descriptors)}, strains/mmaripaludis/{strain.yaml, model/, dltkcat/
(the M2b kcat+MW table), outputs/M2b_kcat_refinement.md, thermal/ (the digitised Jones 1983 TPC — the
user has added it)}, and docs/METHANOGEN_ETCGEM_PLAN.md. Gurobi with a GLPK-abort guard; print solver.

PART A - per-enzyme thermal envelope (kcat(T) + unfolding)
- kcat(T): wrap each enzyme's M2b base kcat with the MMRT curvature (the literature dCp used for
  E. coli) and a per-enzyme optimum Topt from the Li-Engqvist sequence predictor run on the
  UP000000590 sequences (reuse the pipeline; 90%-style coverage, rest at dataset mean). Reuse mmrt.py.
- Native fraction f_N(T): two-state unfolding keyed on a per-enzyme melting temperature Tm. Tm ROUTE
  (the open input for a mesophilic archaeon — DOCUMENT the choice): use a MESOPHILE Tm PRIOR — assign
  Tm from a mesophile Tm distribution (the E. coli meltome mean ~55.6 C + spread we already use),
  INDEPENDENT of Topt (to match the E. coli model structure), since M. maripaludis is mesophilic
  (~38 C) so its proteome stability regime is broadly mesophile-like. Flag this as the a-priori Tm to
  be refined by M4's dTm, and note that an archaeal/methanogen Tm predictor is the future upgrade.
  Reuse unfolding.py.

PART B - NGAM(T) maintenance (convert the deferred ATP drain)
- Replace the M2b-deferred hard-pinned ATP drain (rxn00062) with a temperature-dependent non-growth
  maintenance NGAM(T), same Boltzmann/Arrhenius form as E. coli. Anchor its amplitude on the MEASURED
  M. maripaludis maintenance energy (Goyal et al. 2015 GAM/NGAM) rather than the E. coli value;
  document the number + source. (The GAM stays in the biomass reaction.)

PART C - emergent methanogenesis TPC (nothing fit)
- Sweep temperature (e.g. 5-55 C) and compute the EMERGENT growth TPC (and, since growth ~ CH4 for a
  hydrogenotroph, report the CH4-flux TPC too). Compute descriptors (Topt, rmax, CTmax, Ea, niche
  width). Compare A-PRIORI (nothing fit) to the digitised Jones 1983 TPC: report the shape match
  (expect Topt ~37-38 C, CTmax ~47-48 C, the rising-limb Ea) and the honest magnitude undershoot
  (~few-fold, to be closed by M4). Save the emergent TPC + a figure overlaying the Jones data.
- Keep the growth-law/allocation coupling OFF for now (single sMOMENT pool + NGAM(T) is the M3
  envelope); NOTE that the coupled allocation layer — which was the key Ea-buffering term in E. coli —
  is the next consideration (M3b or folded into M4) before the M5 Ea comparison.

PART D - outputs + GO/NO-GO
- Save under strains/mmaripaludis/outputs/M3_thermal/: the emergent TPC (growth + CH4), descriptors,
  the Jones-overlay figure, and M3_thermal.md documenting the Topt source, the Tm route + its caveat,
  the NGAM(T) source, the emergent descriptors vs Jones, and the carry-forward caveats (Mcr 3-294/s
  sensitivity; growth-law layer deferred; Tm prior). GO/NO-GO for M4 (Bayesian calibration to Jones).

VERIFY (report all)
0. solver=gurobi. Thermal layer wired onto the M2b ecModel; loads/runs via the standard provider/CLI.
1. kcat(T) (MMRT dCp + Li-Engqvist Topt) + f_N(T) (mesophile Tm prior, documented + flagged) applied;
   coverage reported.
2. NGAM(T) replaces the deferred ATP drain; amplitude from Goyal 2015 measured maintenance (cited).
3. Emergent methanogenesis TPC produced (growth + CH4); descriptors (Topt/rmax/CTmax/Ea) reported and
   compared A-PRIORI to Jones 1983 (shape match + honest magnitude undershoot); overlay figure saved.
4. Growth-law/allocation OFF (noted as the next step before M5); nothing tuned to the data.
5. M3_thermal.md + outputs saved; GO/NO-GO for M4 with the carry-forward caveats.

CONSTRAINTS
- Emergent thermal envelope only (kcat(T) + unfolding + NGAM(T)). NO calibration, NO Ea dissection,
  NO growth-law coupling yet. Reuse the E. coli thermal machinery (mmrt/unfolding/sectors/tpc); do not
  fork it. Nothing fit to the Jones data.
- Document the Tm route (mesophile prior) and the NGAM source (Goyal 2015) explicitly.
- Autonomous; commit in parts: "methanogen M3: thermal envelope (kcat(T) MMRT + Li-Engqvist Topt + mesophile-prior Tm unfolding)",
  "methanogen M3: NGAM(T) from Goyal 2015 maintenance; emergent methanogenesis TPC vs Jones 1983 + M3 note".
```
