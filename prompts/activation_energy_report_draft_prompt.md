# Claude Code prompt — draft the E. coli activation-energy report (reports/activation_energy/): what mechanistically sets the organism-level Ea (autonomous)

Run from the project root (`.../MICROADAPT/etcGEMs`). NEW REPORT deliverable. Create
reports/activation_energy/ (the second per-deliverable report, mirroring reports/ecoli_tpc/) and
write it from the ACTUAL Ea-dissection outputs. Report/writing only: no new analysis, no model
changes, no re-runs. The dissection + diagnostic are already done and validated.

NOTE TO USER: launch in an auto-approving mode. Needs quarto to render.

SCOPE: E. coli-only for now, but STRUCTURE it so a methanogen / cyanobacterium comparison slots in
later as a comparative section. Headline the TUNED-model Ea (0.909 eV); use the emergent (0.63) and
observed digitised (0.64) as the a-priori cross-check. Keep the non-circularity framing throughout:
the per-enzyme Ea_i are inputs; the contribution is the AGGREGATION and the DEPARTURE from their mean.

---

```
Work AUTONOMOUSLY end to end; commit in parts; print a summary. READ FIRST and write from the real
numbers (do not invent): strains/eciML1515/outputs/ea_dissection/{summary.json, NOTE.md,
DIAGNOSTIC_NOTE.md, per-enzyme CSVs (BHI+glucose), ea_by_cog_*.csv, ea_by_cog_*_no_carrier.csv, the
five figures + ea_top_enzymes_no_carrier.png}; reports/ecoli_tpc/{report.qmd, assemble.py, the report
infrastructure — header.tex/refs/csl/_quarto if present} to MIRROR the setup and cross-reference the
model; src/etcgem/ea_dissection.py for the exact definitions; and docs/METHANOGEN_ETCGEM_PLAN.md for
the planned comparative extension. Use the renamed report dir reports/ecoli_tpc (not etcgem).

PART A - scaffold reports/activation_energy/ (mirror reports/ecoli_tpc/)
- Create reports/activation_energy/ with report.qmd, an assemble.py that copies the ea_dissection
  figures/tables into reports/activation_energy/assets/ under stable names, and the same infra
  conventions (header/refs/csl if ecoli_tpc uses them). Add reports/activation_energy/_output/ to
  .gitignore (mirror the ecoli_tpc entry). Do NOT touch reports/ecoli_tpc/.

PART B - write report.qmd (from the actual outputs)
Structure (prose + the ea_dissection figures/tables; keep the science tight, defer model detail to
the ecoli_tpc report via cross-reference):
1. TITLE + ABSTRACT: what mechanistically sets the organism-level activation energy (Ea) of growth,
   using the enzyme- and temperature-constrained E. coli model. Headline: Ea_org is a CONTROL-WEIGHTED
   AVERAGE of per-enzyme Ea, sitting above the naive mean because control concentrates on higher-Ea
   enzymes, then offset downward by proteome allocation and maintenance; the controlling pathways are
   medium-dependent. Results up front only in the abstract.
2. BACKGROUND / the question: the emergent Ea (rising-limb temperature sensitivity) is an unresolved
   quantity — is the ~0.6-1.0 eV set by a single rate-limiting enzyme or an aggregate? Frame the
   model as the testbed; cross-reference reports/ecoli_tpc for its construction (do NOT re-derive it).
3. METHOD (conceptual, non-circular): the MCA identity Ea_org = Σ C_i·Ea_i + non-kinetic terms
   (native-fraction + allocation + maintenance); C_i = ∂lnμ/∂ln(kcat_i); Ea_i inputs from MMRT+DLTKcat.
   State the non-circularity explicitly: Ea_i are inputs, the result is the aggregation + departure.
4. RESULTS (all from the outputs):
   - The decomposition closes (use the SIGNED-CONTRIBUTION figure ea_signed_contributions.png — each
     effect as a +/- deviation from the naive enzyme mean, NOT the old waterfall): starting from the
     enzyme mean 0.867, control weighting +0.103, allocation −0.107, maintenance −0.010, residual
     +0.057 → Ea_org 0.909 (tuned, rich BHI). The near-cancellation of control weighting (+0.103) and
     allocation (−0.107) is the story. Note emergent 0.63 / observed 0.64 as the a-priori cross-check,
     and that the tuned value sits near the ~0.85 eV bacterial benchmark.
   - Departure from the naive mean: unweighted 0.867 / mass-weighted 0.896 / control-weighted 0.970 —
     control falls on higher-Ea enzymes (+0.10), the non-circular result.
   - Summation-theorem validation: with the growth law off, Σ C_i = 1.02 and Σ C_i·Ea_i ≈ Ea_org — the
     identity holds on the kinetic backbone; the growth-law allocation is what bends it.
   - The allocation link (the through-line): the growth-law/enzyme-budget term (σ elasticity ≈ 1.0)
     holds ~0.44 of control and is the biggest non-kinetic offset (−0.107) — the SAME σ lever that set
     the rich-medium magnitude ceiling in the ecoli_tpc report. So proteome allocation links magnitude
     and Ea.
   - Pathway localisation (use the _no_carrier tables/figure): rich BHI is lipid synthesis (fabB, fadA;
     robust after removing the acpP carrier-hub — state acpP's 14.5% and that fabB/fadA carry 0.198 of
     0.276) + glycolysis (gapA, eno); glucose-minimal is amino-acid biosynthesis (argG). MEDIUM
     DEPENDENCE is a headline result: the Ea is controlled by whatever the cell is actively synthesising.
   - Robustness: Ea_org stable ~0.90-0.93 over ×0.5-1.0 spread; emergent-vs-tuned mechanism structural
     (not a fit artefact). Explicitly DROP the homogenisation "heterogeneity lowers Ea" claim (the
     diagnostic showed it is a window-shift/incomplete-homogenisation artefact) — cite DIAGNOSTIC_NOTE.
5. INTERPRETATION: the organism Ea is an aggregate (not a single rate-limiting enzyme), buffered below
   the kinetic backbone by allocation, and reflects the active biosynthetic demand (hence medium-
   dependent). Implications for the "universal" metabolic Ea. Be measured; note the model-parameter
   caveats (Ea_i are inputs; ~0.85 benchmark).
6. NEXT STEPS / comparative extension: the cross-organism test — methanogen (M. maripaludis, predicted
   Mcr-dominated control at a higher Ea) and a cyanobacterium — pointing to docs/METHANOGEN_ETCGEM_PLAN.
   Frame this report as the first (E. coli) act.
- DE-FOREGROUND the method/background: keep quantitative results out of them (results up front only in
  the abstract), consistent with the ecoli_tpc report style.

PART C - build + verify
- assemble.py MUST collect the NEW signed-contribution figure ea_signed_contributions.png (the
  canonical Ea-decomposition figure) — NOT the old ea_waterfall.png — into the report assets, and the
  report must reference it. Then run reports/activation_energy/assemble.py; quarto render report.qmd to
  PDF; confirm it builds with no unresolved crossrefs / missing assets, and that the rendered PDF shows
  the signed-contribution figure (not the waterfall). Report the page count.

VERIFY (report all)
1. reports/activation_energy/ created (mirrors ecoli_tpc infra); reports/ecoli_tpc untouched; _output
   gitignored.
2. Report written from the ACTUAL ea_dissection numbers; headlines the tuned Ea 0.909 with emergent
   0.63 / observed 0.64 as cross-check; decomposition + departure + summation-theorem + allocation-link
   + pathway localisation (acpP-robust, hub noted) + medium dependence + robustness all present.
3. Homogenisation "heterogeneity lowers Ea" claim DROPPED/caveated (per DIAGNOSTIC_NOTE); non-
   circularity framing preserved; method/background de-foregrounded.
4. Comparative-extension section points to the methanogen plan; report structured as the E. coli act.
5. report.pdf builds (page count reported).

CONSTRAINTS
- New report only; no new analysis, no model changes, no re-runs. Write from the outputs.
- Mirror the ecoli_tpc report infrastructure; do not modify ecoli_tpc.
- Autonomous; commit in parts: "reports/activation_energy: scaffold (mirror ecoli_tpc) + assemble",
  "reports/activation_energy: draft report.qmd from the Ea-dissection outputs (E. coli act)",
  "reports/activation_energy: render + verify".
```
