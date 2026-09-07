# Claude Code prompt — dissect what sets the organism-level activation energy (Ea) of the E. coli growth TPC: control-weighted aggregation of enzyme Eas and its departure from the naive mean (autonomous)

Run from the project root (`.../MICROADAPT/etcGEMs`). NEW ANALYSIS + a new module/CLI command + a
figure set + a findings note. It does NOT build the full report (that is the future
reports/activation_energy/), does NOT change the emergent/tuned model defaults, and does NOT re-run
the Bayesian. Growth only. Use Gurobi (many perturbation solves).

NOTE TO USER: launch in an auto-approving mode, from the venv with Gurobi.

MOTIVATION: the rising-limb sensitivity (activation energy, Ea) of thermal performance curves is a
famously unresolved quantity. Our etcGEM is a mechanistic testbed: it can say what sets the
organism-level Ea. THE GUIDING PRINCIPLE (non-circularity): the per-enzyme activation energies Ea_i
are an INPUT (MMRT dCp + Topt via DLTKcat). So the goal is NOT "what is Ea" (that would be Ea-in-
Ea-out) but "HOW does the organism-level Ea_org emerge from, and DEPART FROM, the naive average of
the enzyme Ea_i" — the departure is created by things NOT in the input distribution: the
concentration of flux control in a few enzymes, the rising maintenance cost, and the growth-law
proteome reallocation. Frame every result as a departure/attribution, not as "the Ea".

THEORY (the backbone — implement this decomposition):
By the chain rule / metabolic control analysis, the Arrhenius slope of growth is
    Ea_org  =  Σ_i C_i · Ea_i        (enzyme-kinetic term)
             + non-kinetic terms (native-fraction f_N, maintenance NGAM(T), allocation)
where
  * C_i = ∂ln(μ)/∂ln(kcat_i) is enzyme i's GROWTH FLUX CONTROL COEFFICIENT at the operating T
    (small kcat_i perturbation, re-solve, finite difference); the C_i of binding enzymes carry the
    weight and slack enzymes are ~0 (summation theorem => Σ C_i ≈ 1 over the controlling set);
  * Ea_i = local activation energy of the enzyme's effective rate capacity r_i(T)=kcat_i(T)·f_N_i(T)
    over the SAME rising-limb window used for Ea_org (Arrhenius slope d ln r_i / d(1/(k_B T)), eV).
So Ea_org is, to first order, a CONTROL-WEIGHTED MEAN of the enzyme Ea_i, offset by the non-kinetic
terms. The analysis quantifies (a) whether this identity holds, (b) how the control-weighted mean
departs from the unweighted mean, and (c) how much the non-kinetic terms shift it.

---

```
Work AUTONOMOUSLY end to end; commit in parts; print a summary. Read first: src/etcgem/{tpc.py (how
the Ea descriptor + rising-limb window are computed — reuse EXACTLY),mmrt.py (kcat_i(T)),unfolding.py
(f_N_i(T)),enzyme_cost.py (per-enzyme capacity + how kcat enters),control.py (per-enzyme perturbation
machinery to reuse),sectors.py (growth-law + NGAM toggles),calibration.py (load the v3 posterior
medians),providers.py (set_medium),cli.py,config.py,plotting.py}, the tuned posterior
strains/eciML1515/outputs/calibration_vanderlinden/summary.json, and the enzyme-identity join
reports/ecoli_tpc/assets/tables/thermal_control_annotated.csv (gene/enzyme names). Do NOT change model
defaults or re-run the Bayesian.

PART 0 - solver: Gurobi with a GLPK-abort guard (as in the other prompts); print which solver is used.
- PREREQUISITE: run AFTER the free-O2-sink closure (close_free_o2_sinks_prompt). CONFIRM the four
  uncosted O2 sinks (QMO2/QMO3/MOX/CU1Opp) are closed by default before running — the control
  attribution must be on the corrected model, so those artefact reactions do not pollute the enzyme
  set or divert respiratory flux/control. If the closure is not active, STOP and report.

PART A - build the Ea-dissection capability + define quantities consistently
- Add src/etcgem/ea_dissection.py (+ an `etcgem ea` CLI subcommand or a scripts entry) that operates
  on a given model configuration and operating point.
- PRIMARY substrate: the TUNED model (v3 posterior medians) at the RICH (BHI) operating point (growth
  law ON, reconciled pool) — so Ea_org matches the report's tuned Ea. Also run GLUCOSE-MINIMAL as a
  second operating point (same tuned params) for the medium comparison.
- Ea_org: reuse tpc.py's exact Ea descriptor + rising-limb window so it is identical to the report.
- Per-enzyme Ea_i: for every flux-carrying enzyme, compute r_i(T)=kcat_i(T)·f_N_i(T) on the SAME
  window and take its Arrhenius slope (eV). Record the enzyme's kcat-only Ea and the f_N contribution
  separately.

PART B - growth flux control coefficients C_i
- At the operating point (a representative sub-Topt temperature in the Ea window; also report window-
  averaged), compute C_i = ∂ln(μ)/∂ln(kcat_i) for each enzyme by a small symmetric kcat_i perturbation
  and re-solve (reuse control.py's perturbation harness). Report Σ C_i (expect ≈1 over the controlling
  set) and the distribution (expect concentration in a few enzymes, consistent with the thermal-
  control finding).

PART C - the MCA decomposition of Ea_org (does it close?)
- Kinetic term: Σ_i C_i · Ea_i. Compare to the ACTUAL Ea_org from the TPC.
- Non-kinetic terms, each isolated by a controlled switch-off and re-derivation of Ea_org:
  * NATIVE FRACTION: the f_N(T) contribution below Topt (usually small) — quantify.
  * MAINTENANCE: flatten NGAM(T) (make it T-independent at its operating value) -> recompute Ea_org
    -> the shift is the maintenance contribution.
  * ALLOCATION: freeze the growth-law partition (no reallocation with growth) -> recompute Ea_org ->
    the shift is the allocation contribution.
- Show the decomposition approximately closes: Σ C_i Ea_i + (f_N) + (maintenance) + (allocation) ≈
  Ea_org, with a labelled residual for higher-order/nonlinearity. This is the headline figure (a
  waterfall/stacked bar from the enzyme-kinetic control-weighted term to Ea_org).

PART D - departure from the naive enzyme-Ea mean (the non-circular headline)
- Compute the UNWEIGHTED mean of Ea_i (flux-carrying enzymes) and the proteome-MASS-weighted mean.
- Quantify Ea_org − mean(Ea_i) and ATTRIBUTE the departure: (i) control concentration = (control-
  weighted mean Σ C_i Ea_i) − (unweighted mean) [the effect of a few enzymes dominating]; (ii)
  maintenance; (iii) allocation. State clearly that this departure — not the Ea value — is the result.

PART E - which enzymes / pathways set Ea_org
- Rank enzymes by their CONTRIBUTION C_i·Ea_i to Ea_org; name the top ones (gene/enzyme names via the
  annotated join). Aggregate contributions by SUBSYSTEM/pathway (glycolysis, TCA, ETC, translation/
  ribosome, amino-acid/biosynthesis, transport) using the model's subsystem annotations. Report
  whether Ea_org is pathway-localised or distributed, and connect to the concentrated thermal control.

PART F - robustness / sensitivity (guards against artefacts)
- HOMOGENISE Ea_i: set every enzyme's Ea_i to the common mean (keep the model otherwise intact) and
  recompute Ea_org — does it collapse to that value, or does the network/maintenance still bend it?
- SPREAD sensitivity: widen/narrow the Ea_i distribution (scale its variance) and report how Ea_org
  responds — i.e. how much enzyme heterogeneity matters.
- MEDIUM comparison: repeat B/E at glucose-minimal — is the controlling enzyme set (and thus the
  mechanistic basis of Ea) medium-dependent? Report the overlap of top contributors.
- (Optional, if cheap) EMERGENT vs TUNED: confirm the mechanism (control-weighting, top contributors)
  is structural, i.e. similar on the emergent model, so it is not an artefact of the fit.

PART G - outputs + findings note (NO full report yet)
- Save under strains/eciML1515/outputs/ea_dissection/: the decomposition table + waterfall figure,
  the departure-from-mean attribution, the top-enzyme and by-subsystem contribution figures, the
  homogenisation + spread robustness, and the glucose-vs-rich medium comparison. Dump a resolved
  config for provenance.
- Write strains/eciML1515/outputs/ea_dissection/NOTE.md: a concise mechanistic account — Ea_org is a
  control-weighted mean of enzyme Eas, dominated by <the named few/pathways>, departing from the
  naive mean by <X> because control is concentrated, and shifted by <Y> by maintenance and <Z> by
  allocation; medium dependence; robustness. Written so it can seed the future reports/
  activation_energy/ paper. Do NOT build the Quarto report here.

VERIFY (report all)
0. Solver = gurobi (or aborted). Ea_org matches the report's tuned Ea (same window/descriptor).
1. C_i computed; Σ C_i ≈ 1 over the controlling set; control concentrated in few enzymes.
2. The MCA decomposition closes: Σ C_i Ea_i + f_N + maintenance + allocation ≈ Ea_org (report the
   residual). Predicted-vs-actual Ea_org agree to first order.
3. Departure from the unweighted/mass-weighted mean quantified and ATTRIBUTED (control concentration
   vs maintenance vs allocation). Framed as a departure, not "the Ea".
4. Top enzymes + by-subsystem contributions named (gene/enzyme names); pathway-localised vs distributed.
5. Robustness: homogenisation, spread sensitivity, and glucose-vs-rich medium comparison reported.
6. Outputs + NOTE.md written under strains/eciML1515/outputs/ea_dissection/; NO Quarto report built.

CONSTRAINTS
- Analysis + new module/CLI + figures + NOTE only. No model-default changes, no Bayesian re-run, no
  full report. Switch-offs (NGAM flat, allocation frozen, Ea_i homogenised) are TEMPORARY/in-analysis,
  never written back to defaults.
- Enforce the non-circularity framing: Ea_i are inputs; the results are the AGGREGATION and the
  DEPARTURE from the naive mean. Report ACTUAL numbers with the first-order caveat where the linear
  decomposition is approximate.
- Autonomous; commit in parts: "ea_dissection: module + CLI (Ea_org, per-enzyme Ea_i, growth control coefficients)",
  "ea_dissection: MCA decomposition of Ea_org + departure-from-mean attribution",
  "ea_dissection: enzyme/pathway contributions + robustness (homogenise/spread/medium)",
  "ea_dissection: figures + NOTE.md (mechanistic account for the future activation-energy report)".
```
