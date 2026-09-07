# Claude Code prompt — K2 (Candida into the framework, phase 2): put the four Candida strains on the core's own thermal layer, one component at a time, and report what each change does (autonomous)

Run from the project root (`.../MICROADAPT/etcGEMs`). K1 is merged: the four species are `strains/`
entries and, under `thermal_model: phenomenological` with the core's own machinery switched off,
reproduce the standalone implementation exactly (57/57, µ to 0.000000 h⁻¹). K2 switches that
machinery back ON — one component at a time — so the four species end up on the same footing as
eciML1515, mmaripaludis and syn6803.

This prompt CHANGES NUMBERS BY DESIGN. That is its purpose. What it must not do is change several
things at once, so that any movement cannot be attributed. Every step is a separate run with its own
outputs, and the deliverable is the LADDER — what each component did — not a single final answer.

NOTE TO USER: launch in an auto-approving mode. No new external data, nothing downloaded, no
predictor re-run. Budget: the transfer run is ~80 s under GLPK, so the ladder is minutes, not hours.

REFERENCE, read first: docs/CANDIDA_ETCGEM_PLAN.md (§6, K2), docs/CANDIDA_DISCUSSION_2026-09-07.md
(the scientific context — especially §4 on the unfolding ceiling and §6 on which axes are open),
reports/candida_thermal_limit/K1_port_verification.md (what K1 switched off, and its two findings),
strains/mmaripaludis/strain.yaml (the closest precedent for a grounded smoment_gem strain with
unfolding + sectors + NGAM), and reports/ecoli_tpc/report.qmd sections "Calibration", "What sets each
feature of the curve" and "Interpretation and caveats" (what the core's layers are known to do).

WHAT K1 SWITCHED OFF, and therefore what K2 switches back on (from the K1 report):
  1. the grounded proteome budget  p_total x sigma x f_metab   (K1 used a single fitted pool_budget)
  2. proteome sectors
  3. NGAM(T) - temperature-dependent maintenance
  4. free-sink closure
  5. relax_pinned
  6. the DLTKcat overlay
plus the thermal form itself: `phenomenological` (Gaussian x logistic, sigma and w fitted) ->
`unfolding` (MMRT kcat(T) with per-enzyme Topt/dCp, x two-state native fraction f_N(T) keyed on Tm).

THREE THINGS K1 FOUND THAT THIS PROMPT MUST ACT ON:
  * The standalone is inconsistent about the maintenance reaction: `22_thermal_sensitivity.py` pins
    it, `18_build_etcgem_tpc.py` does not. It matters only for iDC1003, whose
    `ATP_Maintenance__cyto` is REVERSIBLE and can otherwise synthesise ATP from ADP + Pi
    (C. parapsilosis limit 55.18 C unpinned vs 53.33 C pinned). Ilgaz found this reversibility
    independently in `gem/audits/ngam_falsification.py` and corrected it THERE, but the correction
    never reached the model script. In K2 the CORRECTED (irreversible/pinned) form is the default
    for every strain; the unpinned run is kept as a labelled sensitivity, not as the baseline.
  * This is the THIRD organism in the project with an uncosted free-energy sink (E. coli has
    `close_free_energy_sinks`, mmaripaludis has `relax_pinned` for rxn00062, now iDC1003). PART E
    makes that a framework-level audit instead of three bespoke fixes.
  * Solver: the port matches the standalone exactly under GLPK; Gurobi differs by ~0.4% at the cold
    end of the draft models, which suggests near-degenerate solutions there. K2 runs under Gurobi
    (the better solver) and reports the GLPK/Gurobi difference per step rather than hiding it behind
    a pin.

---

```
Work AUTONOMOUSLY; commit in parts; print a summary. Branch: `git switch -c k2/candida-core-thermal
main` (after K1 is merged; if it is not, branch off k1/candida-port and say so). Read the files named
above before writing anything. Do NOT re-run DLKcat, Seq2Topt, Seq2Tm or KOfam; do NOT fetch any
external data; do NOT touch $CANDIDAS_ROOT.

PART A - the corrected baseline
- Make the maintenance correction the default: for every Candida strain whose maintenance reaction
  is reversible or unpinned, set it irreversible with the same convention the other three models use,
  in strain.yaml (not in code), with a comment naming the K1 finding and Ilgaz's
  ngam_falsification.py as the source. Verify per strain which ones this actually changes; report it.
- Re-run `etcgem transfer --experiment transfer_candida` under this correction, still
  `thermal_model: phenomenological`, still with the core's machinery off. This is BASELINE-CORRECTED.
- Report the delta from K1's gate values. Expect: nothing moves except C. parapsilosis (limit
  55.18 -> 53.33 C). If anything else moves, STOP and report - it would mean the correction is doing
  more than intended.

PART B - the ladder, one component at a time
Each rung is a separate experiment YAML and a separate output directory, applied CUMULATIVELY in the
order below, starting from BASELINE-CORRECTED. After each rung record, per species: the fitted
globals, mu at every temperature, Topt, rmax, CTmax, the predicted thermal limit, and whether the
pool still binds.

  B1  thermal form:      phenomenological -> unfolding
                         per-enzyme Topt/dCp for MMRT kcat(T); f_N(T) from per-enzyme Tm; dCp from
                         the shared literature prior (dcp_prior_kJ), NOT fitted. The globals that
                         remain free are the core's, not sigma/w.
  B2  budget:            fitted pool_budget -> grounded p_total x sigma x f_metab
                         Use literature YEAST values, sourced in a comment (p_total ~0.45-0.5 g/gDW;
                         sigma ~0.45 as elsewhere; f_metab from a S. cerevisiae proteome). If the
                         grounded budget does not bind, SAY SO and report by how much - that is a
                         finding about a eukaryote in this framework, not something to tune away.
  B3  maintenance:       constant NGAM -> NGAM(T)
                         Anchor it. The measured comparator from the Candidas assay is respiration
                         per unit growth at 40 C: 0.80 in C. auris vs 1.07 in the relatives (ratio
                         1.34). Use the anchoring convention mmaripaludis uses (ngam_base_scale) and
                         state what it was anchored to.
  B4  sectors:           off -> on
                         Literature yeast sector fractions, sourced in comments, IDENTICAL across the
                         four species (no measured per-species allocation exists - see
                         docs/CANDIDA_DISCUSSION_2026-09-07.md §7). Report the ablation cost the way
                         the E. coli work does: fit R^2 with and without.
  B5  DLTKcat overlay:   report only.
                         The Candida kcat are DLKcat (temperature-independent); the core's overlay
                         expects DLTKcat kcat(T). Do NOT run DLTKcat. State what is missing, what it
                         would change, and leave the overlay off.

- Rungs are cumulative, but each must be independently reportable: keep every rung's outputs.
- If a rung makes a model infeasible or growth zero everywhere, that is a RESULT: record it, say
  which component did it, and continue the ladder with that component's setting documented rather
  than silently relaxed.

PART C - the two questions the ladder is for
C1  Does the Fig 4 conclusion survive the core's thermal form?
    Under the FULL ladder, recompute the two quantities Figure 4 rests on:
      - the interspecies Tm separation the model REQUIRES to push each relative below the 0.05 h^-1
        detection floor at 40 C (the standalone: ~33 C);
      - the fold-gap against the sequence-predicted 0.52 C and against the measured
        S. cerevisiae/S. uvarum benchmark of 1.6 C (the standalone: ~63x and ~20x).
    Report both forms side by side. State plainly whether the conclusion is form-independent. If it
    is not, that is the finding and it must be reported as such, not softened.
C2  The unfolding ceiling (docs/CANDIDA_DISCUSSION_2026-09-07.md §4).
    Under `unfolding`, report predicted CTmax against observed thermal limit for all four Candida
    strains, and pull the same two numbers from the committed outputs of eciML1515, mmaripaludis and
    syn6803 WITHOUT re-running them. One table, seven strains: predicted CTmax, observed limit, gap,
    and the median enzyme Tm. Do not interpret beyond stating what the table shows.

PART D - solver
- Run the full ladder under Gurobi. Re-run the final rung under GLPK and report every difference
  above 1e-6. If differences concentrate at the cold end of the draft models, say so and state
  whether they are numerical or alternate optima (check by re-solving with a different basis or a
  tightened tolerance; if that cannot be established cheaply, say it is unresolved).

PART E - the uncosted-energy-sink audit, framework-wide
- Write `etcgem audit-sinks --strain NAME` (or a clearly-named script under src/etcgem/): for a
  built strain, find (i) uncosted reactions that can generate ATP or reducing equivalents, (ii)
  reversible maintenance/ATPM reactions, (iii) hard-pinned uncosted drains. Report, do not fix.
- Run it on all seven strains and put the table in the report. This is the generalisation of three
  bespoke fixes (E. coli close_free_energy_sinks, mmaripaludis relax_pinned, iDC1003 maintenance)
  into one check any future strain gets for free.

PART F - the report
- `reports/candida_thermal_limit/K2_core_thermal_form.md`: the ladder table (rung x species x
  descriptor), the C1 comparison, the C2 seven-strain table, the PART D solver note, the PART E
  audit table, and a short "what moved and why" section written for someone who was not here.
- Update prompts/README.md with K2's outcome. Do not touch the manuscript in $CANDIDAS_ROOT.

VERIFY (report all)
1. Which strains the maintenance correction changed; the BASELINE-CORRECTED delta from K1 (expect
   C. parapsilosis only).
2. The ladder table, all five rungs, all four species, every descriptor named in PART B.
3. Whether the grounded budget binds, per species, with the shortfall if not.
4. What NGAM(T) was anchored to, and the sector fractions used, each with its literature source.
5. The sector ablation cost (fit R^2 with and without), the way the E. coli work reports it.
6. C1: required Tm separation and both fold-gaps, under phenomenological and unfolding side by side;
   an explicit statement of whether the conclusion is form-independent.
7. C2: the seven-strain ceiling table.
8. PART D: Gurobi vs GLPK differences, and whether they are numerical or alternate optima.
9. PART E: the sink audit for all seven strains.
10. `git diff main --stat`: strains/c*/*.yaml, configs/experiments/, src/etcgem/ (the audit command
    and any thermal-layer wiring), reports/candida_thermal_limit/, outputs/, prompts/README.md. No
    existing strain's committed outputs changed - verify eciML1515 and mmaripaludis tpc outputs are
    still cmp-identical.

CONSTRAINTS
- One component per rung. If two are changed together, the ladder is worthless.
- Nothing is tuned to make a number come out. Grounded values come from the literature with a source
  in a comment; if a grounded value gives a bad result, that is the result.
- The corrected (pinned/irreversible) maintenance is the default everywhere; the unpinned run is a
  labelled sensitivity.
- No new external data, no predictor re-run, no DLTKcat.
- K1's gate must still pass: `python reports/candida_thermal_limit/gate_table.py` exits zero on the
  phenomenological configuration. Run it at the end and report.
- Do not touch $CANDIDAS_ROOT. Do not move gem/audits or gem/notes (that is K3).
- Autonomous; commit in parts:
  "K2: correct the reversible maintenance reaction (K1 finding)",
  "K2: ladder rung 1 - unfolding thermal form",
  "K2: ladder rungs 2-4 - grounded budget, NGAM(T), sectors",
  "K2: required-separation and ceiling comparisons",
  "K2: framework-wide uncosted-energy-sink audit",
  "K2: report".
```
