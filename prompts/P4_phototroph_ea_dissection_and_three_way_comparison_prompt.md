# Claude Code prompt — P4 (phototroph build, payoff): dissect what sets the Synechocystis 6803 SS-E, test the shallow-Calvin-kinetics hypothesis with a RuBisCO/curvature sensitivity, and consolidate the THREE-WAY (E. coli vs methanogen vs phototroph) comparison that explains the full Yvon-Durocher 2014 ordering (autonomous)

Run from the project root (`.../MICROADAPT/etcGEMs`). The culminating cross-organism analysis. Dissects the
CALIBRATED, SECTORED phototroph SS-E the same way as E. coli + methanogen (reusing ea_dissection +
sharpe_schoolfield), names the aggregation term, sweeps the key kinetic uncertainty (RuBisCO/Calvin kcat + the
dCp curvature prior), and produces ONE consolidated THREE-WAY comparison that mechanistically explains the 2014
ordering (methanogenesis > respiration > photosynthesis). No re-calibration, no model change.

NOTE TO USER: launch in an auto-approving mode, from the venv with Gurobi. Multi-hour (per-enzyme control
coefficients for the phototroph).

CONTEXT: phototroph calibrated + SECTORED (P3/P3b) SS-E 0.563 (obs Zavrel ~0.56 window-independent, validated
against Inoue flux 0.52); allocation buffer measured -0.019 (small, Jahn 2018 shallow RIB slope). E. coli
(sectored): naive 0.872 + control +0.106 - allocation 0.130 + maintenance 0.005 + aggregation -0.175 = 0.68.
Methanogen (sectored): naive 0.512 + control +0.343 + allocation 0.000 + maintenance -0.016 + aggregation +0.218
= 1.056. P3 verdict for the phototroph: the low Ea is shallow Calvin-cycle kcat(T) (plausible dCp x0.85), NOT
allocation-set. P4 must TEST that in the decomposition: is the low Ea because the CONTROLLING enzymes (carbon
fixation / Calvin) are LOW-E (opposite of the methanogen's high-E backbone), plus a small buffer.

---

```
Work AUTONOMOUSLY end to end; commit in parts; print a summary. Read first: src/etcgem/{ea_dissection.py (+ the SS-E
decomposition into the 4 named terms + naive mean), sharpe_schoolfield.py, control.py, enzyme_cost.py, providers.py
(the route-B from_gecko phototroph path), sectors.py}, strains/syn6803/{strain.yaml, outputs/{P3... calibration_
zavrel/, P3b_sector_layer.md}}, strains/eciML1515/outputs/ea_dissection_ss/ + strains/mmaripaludis/outputs/ea_
dissection_ss/ (the two existing decompositions to compare against + match method), outputs/ea_cross_organism/ (the
existing TWO-way comparison to EXTEND to three), and strains/mmaripaludis/outputs/{M5..., M5b...}.md (the precedent
to mirror). Calibrated + SECTORED phototroph at the light-saturated operating point; Gurobi (GLPK-abort guard);
SS-E throughout.

PART A - phototroph SS-E dissection (same method as E. coli + methanogen)
- Organism Ea_org := SS-E of the calibrated sectored phototroph growth TPC (~0.56). Per-enzyme Ea_i := kcat(T)
  rising-limb E (f_N separated). Compute the growth control coefficients C_i (per-enzyme perturbations — the
  multi-hour part). Decompose SS-E into: naive enzyme-E mean + control-weighting + allocation + maintenance +
  AGGREGATION, with the AGGREGATION term computed DIRECTLY and NAMED (the SS-E of the kinetic-backbone aggregate
  curve minus the control-weighted per-enzyme E mean), not left as a residual. Use the MEASURED allocation term
  from P3b (-0.019), not a structural zero. Confirm the terms sum to the organism SS-E.

PART B - which enzymes/pathways set the phototroph Ea (test the shallow-Calvin hypothesis)
- Rank the per-enzyme contributions (C_i x E_i) to the phototroph SS-E; aggregate by pathway/subsystem. TEST the
  P3 verdict: is the Ea set by the CARBON-FIXATION / CALVIN-CYCLE enzymes (RuBisCO/RBPC, PRK, GAPDH, FBA, SBPase,
  TK...), and are those enzymes LOW-E (their kcat(T) rising-limb E BELOW the proteome mean)? This is the mirror
  image of the methanogen (whose backbone was HIGH-E): report whether the controlling set is low-E, and name the
  top contributors. State clearly the mechanistic contrast: methanogen = narrow control on a HIGH-E backbone ->
  high Ea; phototroph = control on a LOW-E carbon-fixation backbone (+ small buffer) -> low Ea; E. coli = broad
  control + allocation buffer -> mid Ea. Distinguish how much of the phototroph's low Ea is (i) low-E controlling
  enzymes (control-weighting onto shallow-kcat(T) Calvin enzymes) vs (ii) the globally shallower calibrated
  curvature (the naive mean itself) vs (iii) aggregation.

PART C - robustness sweep (the key kinetic uncertainty, analog of the methanogen Mcr sweep)
- The phototroph's low-Ea claim rests on shallow carbon-fixation kcat(T). Sweep the two things it depends on:
  (i) the leading carbon-fixation enzyme kcat (RuBisCO/RBPC and, if it co-leads, the next Calvin enzyme) across a
  plausible range, and (ii) the MMRT dCp curvature prior (e.g. -2 to -6 kJ/mol/K around the -4 prior). Report how
  the organism SS-E AND the control attribution depend on each. State whether (a) the phototroph < E. coli <
  methanogen ORDERING and (b) the low-Ea-is-Calvin-kinetics finding are ROBUST across the range, or hinge on an
  extreme. Carry this as the phototroph's explicit sensitivity caveat (as Mcr 3-294/s is for the methanogen).

PART D - the THREE-WAY comparison (why the 2014 ordering emerges)
- Produce ONE clean cross-organism comparison, ALL THREE organisms on the SAME 4 named terms + naive mean, all with
  a grounded sector/growth-law layer (E. coli Scott; methanogen Muller-flat; phototroph Jahn-shallow):
  * a comparison TABLE: per organism — naive enzyme-E mean, control-weighting, allocation, maintenance, aggregation,
    = organism SS-E; plus observed SS-E and model-vs-observed. (E. coli 0.68 / obs ~0.56; methanogen 1.06 / obs
    ~1.04; phototroph 0.56 / obs ~0.56.)
  * a comparison FIGURE: the three decompositions side by side, SIGNED-CONTRIBUTION style (deviations from the naive
    mean), NEVER a waterfall — so the three DISTINCT routes are visually obvious (methanogen high-E backbone control;
    E. coli allocation buffer; phototroph low-E Calvin control).
  * carry each organism's sensitivity caveat (methanogen Mcr 3-294/s; phototroph RuBisCO/dCp sweep).
- EXPLAIN the full 2014 ordering (methanogenesis 1.06 > respiration 0.68 > photosynthesis 0.56) mechanistically as
  THREE DISTINCT ROUTES to a position in the range, NOT one mechanism scaled: (i) methanogenesis high because narrow
  control sits on a high-E energy backbone with no allocation buffer; (ii) respiration mid because broad control +
  the Scott allocation buffer; (iii) photosynthesis low because control sits on intrinsically low-E carbon-fixation
  enzymes with only a small buffer. FOREGROUND that all three models match their observed SS-E (validation), and
  that E. coli sits on the ~0.65 benchmark. Keep the caveats honest (aggregation term definition-sensitivity; the
  per-organism kinetic sweeps; three organisms not a phylogeny).

PART E - outputs + GO to write up
- Save strains/syn6803/outputs/ea_dissection_ss/ (phototroph) + EXTEND outputs/ea_cross_organism/ to THREE
  organisms (final table + signed-contribution figure + the three decompositions + the sweeps). Update NOTE.md: the
  three-way mechanism (three distinct routes), the phototroph's low-E-Calvin result + its robustness, the symmetric
  allocation story (Scott / Muller-flat / Jahn-shallow), the robust bottom line, and the caveats. Keep the two-way
  originals. GO to fold all three into the paper (three-TPC scene-setter + three-way decomposition + extend the
  construction methods/departures table to Synechocystis).

VERIFY (report all)
0. solver=gurobi; SS-E throughout; phototroph calibrated + SECTORED model at the light-saturated operating point.
1. Phototroph SS-E dissection: control coefficients computed; the 4 NAMED terms (control/allocation/maintenance/
   aggregation) with aggregation computed directly; the measured allocation -0.019 used; terms sum to ~0.56.
2. Pathway attribution: the carbon-fixation/Calvin backbone tested (is it LOW-E and control-carrying?); the
   mechanistic contrast with the methanogen's high-E backbone stated; top contributors named; the low-E vs
   shallow-curvature vs aggregation split reported.
3. Robustness: RuBisCO/Calvin kcat + dCp curvature sweep; whether the ordering + the low-E-Calvin finding are robust.
4. Three-way comparison: side-by-side decomposition (all 3, same 4 named terms + naive mean + observed); the 2014
   ordering explained as THREE DISTINCT routes; all three validated vs observed; signed-contribution figure (no
   waterfall); caveats carried.
5. Outputs + three-way figure/table + NOTE saved; GO to write up.

CONSTRAINTS
- Reuse ea_dissection + sharpe_schoolfield; SS-E throughout; no re-calibration, no model change. Phototroph on its
  SECTORED model (measured allocation -0.019, not hidden). Carry the RuBisCO/dCp sensitivity explicitly. NO waterfalls.
- Autonomous; commit in parts: "phototroph P4: SS-E dissection + named aggregation term + Calvin-backbone attribution",
  "phototroph P4: robustness sweep (RuBisCO/Calvin kcat + dCp curvature prior)",
  "phototroph P4: three-way E. coli vs methanogen vs phototroph comparison (table + figure + NOTE)".
```
