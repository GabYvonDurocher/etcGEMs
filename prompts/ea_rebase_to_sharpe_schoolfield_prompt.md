# Claude Code prompt — re-base the E. coli Ea dissection (and the activation-energy report) from the window-dependent Arrhenius slope to the window-independent Sharpe-Schoolfield E, before the methanogen M5 (autonomous)

Run from the project root (`.../MICROADAPT/etcGEMs`). Re-runs the E. coli Ea dissection with the
organism Ea defined as the Sharpe-Schoolfield E (the new src/etcgem/sharpe_schoolfield.py), and updates
the activation-energy report to SS-E throughout. The Ea-definition audit showed the windowed slope is
severely window-dependent (0.42-1.41 eV spread) and that SS-E flips the cross-organism conclusion
(methanogen ~1.0 >> E. coli ~0.6, matching observed). No Bayesian re-fit, no model change.

NOTE TO USER: launch in an auto-approving mode, from the venv with Gurobi. Multi-hour (per-enzyme
perturbations, as the original dissection).

CONTEXT: current dissection (windowed slope) gave Ea_org 0.909 = control-weighted mean 0.970 −
allocation 0.107 − maintenance 0.010 + residual 0.057. Audit SS-E: E. coli tuned 0.68 (obs VdL 0.56),
methanogen 1.02 (obs Jones 1.04). The report currently headlines the windowed 0.909.

---

```
Work AUTONOMOUSLY end to end; commit in parts; print a summary. Read first: src/etcgem/{ea_dissection.py
(the decomposition + control coefficients + switch-offs), sharpe_schoolfield.py (the new SS fitter),
tpc.py (_activation_energy_eV — the deprecated slope; the descriptor set), mmrt.py, unfolding.py},
strains/eciML1515/outputs/{ea_dissection/, ea_definition_audit/}, reports/activation_energy/report.qmd
+ assemble.py. Tuned model, rich BHI, O2 sinks closed, Gurobi (GLPK-abort guard). Emergent + tuned as
needed.

PART A - redefine the organism Ea as SS-E; redefine per-enzyme Ea_i on the rising limb
- Organism Ea_org := the Sharpe-Schoolfield E fit (sharpe_schoolfield.py) to the tuned rich-BHI growth
  TPC (dense grid). Also compute it for the emergent model and confirm the observed VdL SS-E (0.56) for
  the report cross-check.
- Per-enzyme Ea_i := the RISING-LIMB kinetic activation energy of kcat_i(T) alone (the MMRT/Arrhenius E
  of kcat_i(T), WITHOUT the unfolding f_N — since in SS terms the unfolding is the high-T deactivation
  E_h/T_h, not the rising-limb E). VERIFY empirically that f_N's contribution to the rising-limb E is
  negligible (consistent with the old small native-fraction term), so it cleanly leaves the E
  decomposition. Document the per-enzyme E_i definition used.

PART B - recompute the decomposition ON SS-E (same structure, cleaner)
- Reuse the existing growth control coefficients C_i. Decompose Ea_org(SS-E) as: control-weighted mean
  of the per-enzyme kcat(T) rising-limb E_i  −  allocation (growth law)  −  maintenance NGAM(T)  +
  residual  =  Ea_org(SS-E). (The native-fraction term drops out vs the slope version — confirm.)
  Compute the allocation/maintenance terms the same way as before (switch each off -> re-fit SS ->
  Delta SS-E), so they are on SS-E.
- NUMERICAL CROSS-CHECK / closure: for the control-weighting and the non-kinetic terms, validate by the
  direct numerical route — perturb / switch off -> regenerate TPC -> re-fit SS -> Delta(SS-E) — and
  report how well the analytic control-weighted decomposition matches the numerical SS-E changes
  (report the residual; SS-E is nonlinear so expect a modest residual). Keep the "departure from the
  naive enzyme-Ea mean" framing.
- Confirm the MECHANISM is robust to the definition change: control-weighting still raises Ea, allocation
  still lowers it, the top pathways are still lipid synthesis + glycolysis (rich) / amino-acid
  biosynthesis (glucose), medium dependence holds. Report the NEW numbers (the signed contributions on
  SS-E) and whether the story survives.

PART C - update the activation-energy report to SS-E throughout
- Headline Ea = SS-E (E. coli tuned ~0.68; note emergent + observed VdL 0.56). Regenerate the
  signed-contribution figure (ea_signed_contributions.png) and Table 1 on the SS-E decomposition (this
  SUPERSEDES the windowed-slope figure/table). Add a METHODS note: the Ea is the Sharpe-Schoolfield E
  (Schoolfield 1981; window-independent, field-standard), motivated by the window-sensitivity of the
  naive Arrhenius slope (cite the audit range); the windowed slope is a deprecated cross-check.
- FOREGROUND the model-vs-observed SS-E validation (0.68 vs 0.56) as a genuine a-priori-style strength,
  and note E. coli's ~0.6 sits on the "universal" metabolic ~0.65 eV benchmark. Keep the comparative-
  extension section pointing to the methanogen (now: SS-E ~1.0 >> E. coli, the real signal).
- Re-run reports/activation_energy/assemble.py; quarto render; confirm the PDF shows the SS-E figure +
  table and builds cleanly.

PART D - outputs + GO for M5
- Save the SS-E dissection outputs alongside the originals (do NOT overwrite the slope version; suffix
  e.g. _ss). Update ea_dissection NOTE.md with the SS-E decomposition + the robustness of the mechanism.
  State the GO for M5 (methanogen dissection) on the SAME SS-E footing.

VERIFY (report all)
0. solver=gurobi. Organism Ea_org = SS-E (tuned ~0.68); emergent + observed VdL 0.56 reported.
1. Per-enzyme Ea_i = kcat(T) rising-limb E (f_N/unfolding separated to the deactivation side; its
   rising-limb contribution verified negligible).
2. SS-E decomposition computed (control-weighting / allocation / maintenance / residual), with the
   numerical Delta-SS-E cross-check + residual; the mechanism (control up, allocation down, lipid+
   glycolysis, medium dependence) confirmed robust; NEW numbers reported.
3. Report updated to SS-E: headline value, signed-contribution figure + Table 1 regenerated on SS-E
   (superseding the slope versions), methods note on SS-E + window-sensitivity, model-vs-observed SS-E
   validation foregrounded; PDF builds.
4. SS-E outputs saved (slope version kept); NOTE.md updated; GO for M5 on the SS-E footing.

CONSTRAINTS
- Re-analysis on the SS-E definition + report update only. No Bayesian re-fit, no model change. Reuse
  ea_dissection + sharpe_schoolfield; keep the slope version as a deprecated cross-check.
- Apply SS-E identically wherever Ea appears; the whole point is a single window-independent, model-
  observed-comparable convention.
- Autonomous; commit in parts: "ea dissection: re-base organism Ea + per-enzyme Ea_i to Sharpe-Schoolfield E",
  "ea dissection: SS-E decomposition + numerical closure + mechanism-robustness check",
  "report(activation_energy): re-base to SS-E (headline, signed-contribution fig + table, methods, model-vs-observed validation)".
```
