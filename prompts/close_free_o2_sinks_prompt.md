# Claude Code prompt — model-quality fix: close the uncosted O2-consuming side reactions (Parsa's finding) as a default correction, before the Ea dissection (autonomous)

Run from the project root (`.../MICROADAPT/etcGEMs`). A small, permanent MODEL-QUALITY correction:
close the four O2-consuming reactions that carry effectively zero enzyme cost and create a futile O2
cycle, so flux routes through the genuine (enzyme-costed) respiratory chain. This is a prerequisite
for the Ea dissection (control attribution) and for later respiration/comparative work. It does NOT
re-run the Bayesian (the growth effect is ~-0.3%, within the posterior width). Growth only; Gurobi.

NOTE TO USER: launch in an auto-approving mode. Credit: the four reactions were identified by Parsa
(gas-flux work); his fix lives in a fork and is NOT in main, so we promote it into the core model.

BACKGROUND (from Parsa's audit): in eciML1515 four reactions consume O2 at ~zero enzyme cost and
short-circuit the electron transport chain, inflating and scrambling the O2 read-out (at LB/40C, 75%
of gross O2 turnover was a futile cycle). Closing them routes O2 through the real cytochrome oxidase
(CYTBO3) at a cost of only ~-0.3% growth and leaves the growth TPC essentially unchanged. The four:
- QMO2 (2 O2 + quinol -> 2 superoxide + quinone; gene ygiN / P0ADU2; ~free)
- QMO3 (2 O2 + menaquinol -> 2 superoxide + menaquinone; same enzyme; ~free)
- MOX  (malate + O2 -> H2O2 + oxaloacetate; no enzyme-cost entry)
- CU1Opp (4 Cu+ + O2 -> 4 Cu2+ + 2 H2O; no enzyme-cost entry)
Catalase (CATNo1) and SOD (SPODMNo1) are NOT artefacts (real kcat 1e5-1e9/s) and must stay open.

---

```
Work AUTONOMOUSLY; commit in parts; print a summary. Read first: src/etcgem/{providers.py (model
build + set_medium; where to add the closure),config.py (defaults/toggles),enzyme_cost.py,cli.py,
tpc.py}, strains/eciML1515/strain.yaml, configs/defaults.yaml, and the base model
strains/eciML1515/model/eciML1515_batch.xml. Use Gurobi with a GLPK-abort guard; print the solver.

PART A - locate + close the four reactions (as a documented default)
- Resolve the exact reaction IDs in eciML1515 for QMO2, QMO3, MOX, CU1Opp (they may carry GECKO
  isozyme suffixes, e.g. QMO2No1/QMO3No1, and reverse variants). List every matched reaction and its
  stoichiometry so the closure is auditable. If a name is absent, report it and continue with those
  present.
- Add a model-build step (in providers.py, applied by DEFAULT after the model loads) that sets the
  upper bound (and reverse bound if applicable) of exactly these reactions to 0. Gate it behind a
  config flag, e.g. `close_free_o2_sinks: true` in configs/defaults.yaml (default TRUE, documented,
  reversible), and record which reactions were closed in the resolved config. Implement it as a named,
  reusable function (e.g. close_free_energy_sinks) with the ID list as a module constant, so it can be
  extended per-organism later. Do NOT touch CATNo1 or SPODMNo1.

PART B - verify the correction is sound (and that no re-calibration is needed)
- On the TUNED model (v3 posterior medians) at rich BHI and at the optimal T, report growth WITH vs
  WITHOUT the closure (expect ~-0.3%, matching Parsa: ~2.153 -> ~2.148 on LB). Confirm the growth TPC
  descriptors (rmax, Topt, Ea, CTmax) are essentially unchanged (report the deltas). Because the shift
  is within the posterior width, do NOT re-run the Bayesian.
- O2 sanity: at the operating point, confirm net intracellular O2 consumption now equals the O2
  exchange flux (no residual futile cycle), and that O2 routes through CYTBO3. Report gross vs net O2
  before/after.

PART C - regenerate ONLY what the corrected model affects (minimal)
- Regenerate the emergent + tuned reference TPC descriptors and the validation-vs-Van-Derlinden check
  on the corrected model; confirm they match the report within rounding (the growth results should be
  essentially identical). Save under strains/eciML1515/outputs/free_o2_sink_fix/ with a NOTE.md (the
  matched reactions, the growth/TPC deltas, the O2 audit before/after, and a one-line statement that
  the calibration is unaffected within uncertainty).
- Do NOT rebuild the full report and do NOT regenerate the heavy control/decomposition runs here. Note
  in the summary that the downstream analyses (Ea dissection, and if desired a refresh of the report's
  control/identifiability section, where QMO2/QMO3 currently appear) will now inherit the corrected
  model.

VERIFY (report all)
0. Solver = gurobi (or aborted).
1. The four reactions located (with IDs + stoichiometry) and closed by default via a documented,
   reversible flag; CATNo1/SPODMNo1 left open; closed set recorded in the resolved config.
2. Growth delta ~-0.3% and the TPC descriptors essentially unchanged (deltas reported); no Bayesian
   re-run needed (stated why).
3. O2 audit: net = exchange after closure; routed through CYTBO3; gross/net before-after reported.
4. free_o2_sink_fix/NOTE.md written; full report + heavy analyses NOT rebuilt (noted as inheriting).

CONSTRAINTS
- Permanent model-quality correction only (a default closure + flag). No Bayesian re-run, no full
  report rebuild, no other model-default changes. Keep CATNo1/SPODMNo1 open.
- Reusable/auditable implementation (named function + ID constant) so other organisms can be audited
  later.
- Autonomous; commit in parts: "model: close four uncosted O2-sink reactions by default (Parsa's audit); reversible flag",
  "verify: -0.3% growth, TPC unchanged, O2 net=exchange via CYTBO3; NOTE + provenance".
```
