# Claude Code prompt — M5 (methanogen build, payoff): dissect what sets the M. maripaludis SS-E, test the methanogenesis-backbone hypothesis with the Mcr-kcat sensitivity, and compare mechanistically to E. coli to explain why methanogenesis Ea > respiration (autonomous)

Run from the project root (`.../MICROADAPT/etcGEMs`). The culminating cross-organism analysis. Dissects
the CALIBRATED methanogen SS-E the same way as E. coli (reusing ea_dissection + sharpe_schoolfield),
names the aggregation term, sweeps the Mcr-kcat uncertainty, and builds the E. coli-vs-methanogen
comparison. No re-calibration, no model change.

NOTE TO USER: launch in an auto-approving mode, from the venv with Gurobi. Multi-hour (per-enzyme
control coefficients for the methanogen).

CONTEXT: methanogen calibrated SS-E ~1.0 (obs Jones 1.04); E. coli tuned SS-E 0.68 (obs VdL 0.56, on
the ~0.65 eV benchmark). E. coli SS-E decomposition (rich): naive mean 0.872 + control 0.106 −
allocation 0.126 + maintenance 0.005 + AGGREGATION −0.178 = 0.68 (the "residual" is the aggregation/
heterogeneity flattening — name it). Methanogen: single sMOMENT pool (weak allocation buffer, grounded
in slow growth), methanogenesis backbone (Fwd/Mtr/Mcr/Mer/Hdr) ~60% of the pool; Mcr kcat 58.9/s,
uncertainty 3-294/s.

---

```
Work AUTONOMOUSLY end to end; commit in parts; print a summary. Read first: src/etcgem/{ea_dissection.py
(+ ea_org_ss + the SS-E decomposition), sharpe_schoolfield.py, control.py, enzyme_cost.py, providers.py
(from_gem_smoment)}, strains/mmaripaludis/{strain.yaml, outputs/{M4_calibration.md, calibration_jones/}},
strains/eciML1515/outputs/ea_dissection_ss/ (the E. coli SS-E decomposition to compare against), and
docs/METHANOGEN_ETCGEM_PLAN.md. Tuned/calibrated methanogen at the H2/CO2 operating point; Gurobi
(GLPK-abort guard). SS-E throughout.

PART A - methanogen SS-E dissection (same method as E. coli)
- Organism Ea_org := SS-E of the calibrated methanogen growth TPC (~1.0). Per-enzyme Ea_i := kcat(T)
  rising-limb E (f_N separated). Compute the growth control coefficients C_i for the methanogen
  (per-enzyme perturbations — the multi-hour part). Decompose SS-E: naive enzyme-E mean + control
  weighting + allocation + maintenance + AGGREGATION, where the AGGREGATION term is COMPUTED DIRECTLY
  and NAMED (the SS-E of the kinetic-backbone aggregate curve minus the control-weighted per-enzyme E
  mean — the heterogeneity flattening), not left as a residual. NOTE the allocation term is ~0 by the
  single-pool structure; state the slow-growth grounding (the growth-law buffer is physiologically weak
  at ~10x-slower growth) + that a sector layer would make it exactly symmetric.
- ALSO recompute the E. coli aggregation term directly (name the −0.178) so both decompositions use the
  same named 4 mechanisms: control-weighting, allocation, maintenance, aggregation.

PART B - which enzymes/pathways set the methanogen Ea (test the reframed hypothesis)
- Rank the per-enzyme contributions (C_i x E_i) to the methanogen SS-E; aggregate by pathway/subsystem.
  Test the reframed hypothesis: is the Ea set by the METHANOGENESIS BACKBONE (Fwd/Mtr/Mcr/Mer/Hdr), and
  are those enzymes HIGH-E (their kcat(T) rising-limb E above the proteome mean)? Report the top
  contributors with names, and whether the backbone (not one enzyme) carries it.

PART C - Mcr-kcat sensitivity sweep (the key uncertainty)
- Repeat the methanogen SS-E + the control attribution across the Mcr kcat range (3-294/s; e.g. a
  handful of values spanning it). Report how the organism SS-E AND the control attribution (which
  enzymes lead) depend on Mcr's kcat. State whether the "methanogen Ea >> E. coli" ordering and the
  backbone-control finding are ROBUST across the Mcr range, or hinge on the low end.

PART D - the E. coli vs methanogen comparison (why methanogenesis Ea > respiration)
- Side-by-side SS-E decomposition (both organisms, the 4 named terms) + descriptors (Ea, Topt, CTmax),
  model vs observed for each. EXPLAIN the Ea difference (~1.0 vs ~0.6) in terms of the terms: how much
  is (i) control-weighting on higher-E methanogenesis enzymes, (ii) the missing allocation buffer
  (grounded in slow growth), (iii) aggregation, (iv) the underlying enzyme-E distributions. State the
  honest bottom line on "methanogenesis Ea > respiration": is it driven by the backbone's intrinsic
  temperature sensitivity, by the lack of allocation buffering, or both — and how robust to Mcr.
- FOREGROUND: both models match their observed SS-E (validation); E. coli on the ~0.65 benchmark;
  methanogen ~1.0. Keep it honest about the caveats (single-pool allocation asymmetry; Mcr range;
  the aggregation term).

PART E - outputs (analysis; report write-up is a later step)
- Save strains/mmaripaludis/outputs/ea_dissection_ss/ (methanogen) + a shared comparison under
  outputs/ea_cross_organism/: the two decompositions, the by-pathway contributions, the Mcr sweep, and
  a comparison figure/table. Write NOTE.md: the methanogen mechanism, the backbone/Mcr result + its
  sensitivity, the cross-organism explanation of the Ea difference, and the caveats. This seeds the
  comparative section (reports/activation_energy/ extension or a dedicated cross-organism report — decide
  later). GO/NO-GO to write up.

VERIFY (report all)
0. solver=gurobi; SS-E throughout; methanogen calibrated model at H2/CO2.
1. Methanogen SS-E dissection: control coefficients computed; the 4 NAMED terms (control/allocation/
   maintenance/aggregation) with the aggregation computed directly; allocation ~0 with the slow-growth
   grounding stated; E. coli aggregation term also named.
2. Pathway attribution: the methanogenesis backbone tested (is it high-E and control-carrying?); top
   contributors named.
3. Mcr-kcat sweep: SS-E + attribution across 3-294/s; robustness of the ordering + backbone finding
   stated.
4. Cross-organism comparison: side-by-side decomposition; the Ea difference explained by the terms;
   both validated vs observed; honest bottom line on "methanogenesis Ea > respiration" + caveats.
5. Outputs + comparison figure/table + NOTE saved; GO to write up.

CONSTRAINTS
- Reuse ea_dissection + sharpe_schoolfield; SS-E throughout; no re-calibration, no model change.
- Methanogen single-pool (allocation asymmetry named + grounded in slow growth, NOT hidden). Carry the
  Mcr 3-294/s sensitivity explicitly.
- Autonomous; commit in parts: "methanogen M5: SS-E dissection + named aggregation term + backbone attribution",
  "methanogen M5: Mcr-kcat sensitivity sweep",
  "methanogen M5: E. coli vs methanogen cross-organism comparison + NOTE".
```
