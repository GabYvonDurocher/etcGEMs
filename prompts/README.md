# Prompts — etcGEM project

Each file here is a prompt to paste into **Claude Code** (run from the project root
`.../MICROADAPT/etcGEMs`). Most are autonomous and modify code, run analyses, and
commit; launch Claude Code in an auto-approving mode (accept edits + allow commands,
e.g. `--dangerously-skip-permissions`) to run them unattended. They build on each
other, so run them roughly in the order below.

Status legend: ✅ run · ▶ in progress · ⏳ pending

## Recommended run order

**Structure & packaging**
1. `reorg_prompt.md` — ✅ reorganise to a `src/etcgem` package, per-strain folders.
   *(Superseded by #2 for the config model; kept for history.)*
2. `project_restructure_prompt.md` — ✅ config model = `defaults / strain / experiment`
   + two-tier CLI (`build/tpc/fba` strain-only; `sweep/decompose/control` + experiment).

**Core analyses**
3. `decomposition_prompt.md` — ✅ allocation-vs-envelope Shapley variance decomposition (H1.3).
4. `control_identifiability_prompt.md` — ✅ per-enzyme thermal control coefficients + identifiability (H1.1/H1.2).
5. `allocation_and_sampling_prompt.md` — ✅ proteome-sector allocation + correlated / DLTKcat-posterior thermal sampling (M1.2).

**Data (DLTKcat) + figures + runs**
6. `dltkcat_sweep_prompt.md` — ✅ run DLTKcat → per-enzyme MMRT params → eciML1515 sweep.
7. `native_figures_and_runs_prompt.md` — ✅ native descriptor-interval & sector-tradeoff figures; run the `calibrated` & `sectors` experiments with plots.

**Fixes & model realism**
8. `fixes_identifiability_ea_sectordecomp_prompt.md` — ✅ proteome-wide identifiability, dCp→Ea calibration, sector-based H1.3 decomposition.
9. `per_enzyme_dcp_decouple_prompt.md` — ✅ per-enzyme thermal heterogeneity (dCp/Topt) to decouple breadth & Ea.
   *(Interim fix; #12 is the more principled, data-grounded route.)*

**Reporting**
10. `quarto_report_prompt.md` — ✅ set up the Quarto report (PDF/docx), `reports/etcgem/`.
11. `flesh_out_report_prompt.md` — ✅ full write-up: Background → Model → Design → Results → Next steps.
12. `report_addendum_structural_caveat_prompt.md` — ✅ add the "clean separation is partly
    structural / growth-fit can't resolve it / temperature-dependent allocation" caveat
    + refs (Mairet2021, Wang2026). *(Targeted edit to the fleshed-out report.)*

**Data-grounded model**
13. `align_with_mres_unfolding_model_prompt.md` — ✅ two-state **Tm-based unfolding** thermal
    model from the MRes/Li work; grounds the *envelope* in per-enzyme Topt/Tm (reuses the
    MRes repo's parameter tables — no BRENDA/TOMER needed for E. coli).
14. `ingest_temperature_proteomics_prompt.md` — ✅ ingest E. coli temperature proteomics
    (DeyuWang `tem_proteomic.csv`) to ground **temperature-dependent proteome allocation**
    and validate predicted vs measured enzyme usage. (Measured chaperone sector ramps
    2.7× by 43 °C; wired in as an opt-in run + validation.)

**Consolidation & report**
15. `complete_model_consolidation_and_report_prompt.md` — ⏳ assemble ONE **complete**
    data-grounded model (unfolding envelope + measured temperature-dependent sector
    allocation + DLTKcat), validate it against the empirical E. coli TPC and the proteome,
    re-run sensitivity / decomposition / control **on the complete model**, and
    **restructure the report** (complete model → validation → results; incremental
    build-up moved to a supplementary construction section). **Run after #13 and #14.**

**Fully emergent, per-curve validation (current frontier)**
16. `emergent_tpc_per_curve_validation_prompt.md` — ⏳ make the TPC a genuine PREDICTION:
    remove the growth-fit knobs (`pool_scale`, `calibrate-dcp`); make **magnitude** emergent
    (pool = P_total × f_metab × σ, from proteome + literature σ) and **Ea** emergent (grounded
    per-enzyme dCp), set the **medium per curve** from the Smith 2019 database
    (`smithtp/hotterbetterprokaryotes`), and validate against **individual** E. coli curves
    (many per-curve fits) + the ~0.85 eV growth-Ea benchmark. **Growth only** at this stage.
    **Run after #15.**

17. `rich_medium_and_percurve_medium_prompt.md` — ⏳ add an **LB / rich medium**
    (availability, from the MRes `media.csv` / Machado 2018) so the 24 rich-broth E. coli
    curves are predicted under the correct condition; re-validate per-curve on **RAW
    ABSOLUTE rates (1/h)** — magnitude is emergent, so drop peak-normalisation as the primary
    metric (shape kept as secondary); **highlight minimal vs LB panels**; switch the ablation
    plot to absolute too; document the medium treatment. (Only 2/26 curves were
    defined-minimal before; the rest were shape-only.) **Run after #16.**
18. `medium_matched_sector_allocation_prompt.md` — ⏳ make the proteome-sector fractions
    **medium-matched** (LB vs Glucose vs Glycerol, all from the DeyuWang proteomics) so the
    ribosome/translation cap is medium-dependent and LB grows faster than minimal (the
    growth-law effect, data-grounded not fitted). Fixes the #17 finding that rmax was stuck
    at 0.34/h on every medium because `f_bio` was fixed; re-runs the per-curve absolute
    validation. **Also upgrades the report** to a reproducible, equation-backed write-up:
    model **equations** (MMRT, unfolding, sector caps, decomposition), a **parameter-
    provenance table** (source + coverage for every parameter), and detailed in-silico-
    experiment and validation descriptions. **Run after #17 finishes.**

_Deferred — respiration & CUE:_ once the growth model is trusted, add respiration
(CO₂/O₂ flux) and CUE TPC outputs and validate the Smith benchmarks (E_μ > E_R; CUE rises/
flat with warming; max CUE ≈ 0.4–0.6). Full library-scale validation against the 29 Smith
2021 environmental strains needs draft GEMs for those strains.

## The through-line

The scientific thread these encode: build an enzyme- & temperature-constrained GEM of
E. coli (eciML1515), decompose its TPC into a genome-set **envelope** and an
allocation-set **magnitude** (H1.1–H1.3), then progressively replace assumed pieces
with data — DLTKcat kcat(T), the MRes/Li Tm-based unfolding envelope (#13), and
measured temperature-dependent proteome allocation (#14). The recurring caveat
(captured in #12) is that the clean envelope/allocation split is partly a consequence
of model structure (peak-normalisation + temperature-independent allocation) and is
only resolvable with proteome/flux data — which #13 and #14 begin to supply.

## The decisive test (done by #15)

The recurring open question is whether the clean allocation-vs-envelope "division of
labour" is real or an artefact of two assumptions (peak-normalisation +
temperature-independent allocation). #13 removes the first (Tm-based unfolding) and #14
removes the second (measured temperature-dependent allocation). #15 assembles both into
one complete model, validates it against the empirical TPC, and re-runs the
decomposition on it — so whatever division of labour survives on the canonical,
data-grounded model is the real, defensible result (expected: more coupled, with `rmax`
gaining envelope share and larger interaction terms than the assumed-model 100/0 split).
