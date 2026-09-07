# Claude Code prompt — Ea-definition audit: quantify the window-sensitivity of the current Arrhenius-slope Ea, fit the Sharpe-Schoolfield model to extract a window-independent E, and recommend one consistent Ea convention across E. coli + methanogen (autonomous)

Run from the project root (`.../MICROADAPT/etcGEMs`). DIAGNOSTIC + a new Sharpe-Schoolfield fitter.
No Bayesian re-fitting, no model changes, no Ea-dissection re-plumb (that is a follow-up decision from
the results). The current descriptor Ea (tpc.py `_activation_energy_eV`) is a Boltzmann-Arrhenius slope
over a RELATIVE window (10-95% of rmax), which is window-dependent because the rising limb is curved
(MMRT). This audit measures that sensitivity and provides the field-standard, window-INDEPENDENT
alternative (Sharpe-Schoolfield E), then recommends a single convention to standardise on before M5.

NOTE TO USER: launch in an auto-approving mode. Reads saved TPCs; regenerate a curve only if needed.

CONTEXT: E. coli emergent Ea 0.63 / tuned 0.909 (Van Derlinden obs 0.64); methanogen calibrated Ea
0.85 (Jones obs 0.66) — all on the 10-95%-of-rmax window. A different window gave the methanogen ~1.16.
The cross-organism headline ("methanogenesis Ea ~ respiration, not >>") hinges on this, so the Ea
definition must be consistent, window-independent, and comparable to the observed/literature values.

---

```
Work AUTONOMOUSLY; commit in parts; print a summary. Read first: src/etcgem/tpc.py
(_activation_energy_eV + the descriptor set), the saved TPC curves for: E. coli emergent + tuned
(strains/eciML1515/outputs/... the validation/reference/anatomy TPC + the tuned/posterior-predictive
curve), the methanogen calibrated posterior-predictive TPC (strains/mmaripaludis/outputs/
calibration_jones/), and the digitised OBSERVED curves (Van Derlinden strains/eciML1515/thermal/...;
Jones strains/mmaripaludis/thermal/...). Gurobi only if a TPC must be regenerated.

PART A - window-sensitivity of the current Arrhenius-slope Ea
- For each TPC (E. coli emergent, E. coli tuned, methanogen calibrated) AND each observed curve,
  recompute the Boltzmann-Arrhenius slope Ea under several WINDOW conventions, all as ln(rate) vs
  1/(k_B T) below Topt:
  * the current 10-95%-of-rmax relative window (reproduce the reported values as a check);
  * a FULL below-Topt window (all points below the peak with rate>0 — the user's convention);
  * a couple of intermediate relative windows (e.g. 10-80%, 30-90%) and a FIXED-TEMPERATURE window
    (e.g. the near-linear low-rising portion, or a range matched to how the observed Ea would be read).
- Tabulate Ea per (curve × window). Quantify the spread — this is the problem statement.

PART B - Sharpe-Schoolfield fitter (window-INDEPENDENT E)
- Implement the Schoolfield 1981 high-temperature-inactivation model (the rTPC "sharpeschoolhigh_1981"
  form; add the low-T term only if the cold end demands it):
    rate(T) = r_Tref * exp( (E/k_B) * (1/T_ref - 1/T) ) / ( 1 + exp( (E_h/k_B) * (1/T_h - 1/T) ) )
  T, T_ref, T_h in KELVIN; k_B = 8.617333e-5 eV/K; E, E_h in eV. Fit r_Tref, E, E_h, T_h by nonlinear
  least squares (scipy.optimize.curve_fit) with a FIXED, documented T_ref (e.g. a low rising-limb
  reference, consistent across all curves), sensible starting values (E~0.6-1, E_h~2-5, T_h near the
  curve's CTmax) and bounds; report parameter estimates + CIs and fit R².
- Fit it to EACH model TPC (E. coli emergent + tuned; methanogen calibrated) AND each OBSERVED curve.
  E is the window-independent activation energy; E_h/T_h describe the deactivation (relate to CTmax).
- Put the fitter in a small reusable module (e.g. src/etcgem/sharpe_schoolfield.py) so it can be reused
  for M5/the reports and future organisms.

PART C - compare + does the conclusion hold
- Build one comparison table: for E. coli (emergent, tuned) and the methanogen (calibrated), and their
  observed curves, show the Arrhenius-slope Ea (per window) alongside the Sharpe-Schoolfield E.
- Answer explicitly: (i) how window-dependent is the slope Ea (range across windows per curve);
  (ii) the Sharpe-Schoolfield E for each (with CI); (iii) does the MODEL's SS-E match the OBSERVED
  SS-E (a cleaner validation than the windowed slope); (iv) UNDER SS-E, is the methanogen Ea higher
  than, comparable to, or lower than E. coli's — i.e. does the "methanogenesis vs respiration" headline
  survive the switch from the windowed slope to SS-E? State the numbers.

PART D - recommendation
- Recommend ONE consistent organism-level Ea convention to standardise on (I expect Sharpe-Schoolfield
  E: window-independent, field-standard, comparable to observed + literature). State the implication
  for the E. coli activation-energy DISSECTION (whether Ea_org there should be re-based to the chosen
  convention — a follow-up, since the MCA identity needs Ea_org and the per-enzyme Ea_i defined the
  same way), but do NOT re-plumb the dissection in this prompt.

PART E - outputs
- Save under strains/eciML1515/outputs/ea_definition_audit/ (or a shared outputs/ea_definition_audit/):
  the window-sensitivity table, the Sharpe-Schoolfield fits (params + CIs + R²), the comparison table,
  and a figure overlaying each SS fit on its TPC (model + observed). Write NOTE.md: the window-
  sensitivity, the SS-E values, whether model matches observed, whether the cross-organism conclusion
  holds under SS-E, and the recommended convention + the dissection-rebasing decision to make next.

VERIFY (report all)
1. Windowed Arrhenius-slope Ea recomputed under several conventions for all model + observed curves;
   the current 10-95% values reproduced; the spread quantified.
2. Sharpe-Schoolfield (Schoolfield 1981) fitter implemented + fit to every model + observed curve;
   E, E_h, T_h, r_Tref + CIs + R² reported; reusable module saved.
3. Comparison table + explicit answers: window-dependence; SS-E per curve; model-vs-observed SS-E
   agreement; and whether methanogen-vs-E.coli Ea ordering survives under SS-E (with numbers).
4. Recommended convention + the dissection-rebasing implication stated (not executed); outputs + NOTE
   saved.

CONSTRAINTS
- Diagnostic + a new SS fitter only. NO Bayesian re-fit, NO model changes, NO dissection re-plumb.
- Apply every convention identically to model AND observed, both organisms — the whole point is
  consistency + comparability.
- Autonomous; commit in parts: "ea audit: window-sensitivity of the Arrhenius-slope Ea (all curves)",
  "ea audit: Sharpe-Schoolfield fitter + fits to model + observed (window-independent E)",
  "ea audit: comparison + recommended convention + NOTE".
```
