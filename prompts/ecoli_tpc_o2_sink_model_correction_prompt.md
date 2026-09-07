# Claude Code prompt — update the ecoli_tpc report: document the uncosted-O2-reaction closure as a model-curation step, and put the enzyme-control analysis on the corrected model (autonomous)

Run from the project root (`.../MICROADAPT/etcGEMs`). REPORT UPDATE + regenerate the enzyme-control
analysis on the corrected model. NO Ea-dissection content (that is the separate reports/
activation_energy/ report). No model-default changes (the closure is already the default), no
Bayesian re-run. Growth only; Gurobi.

NOTE TO USER: launch in an auto-approving mode. Needs quarto to render.

CONTEXT: the core model now closes four uncosted O2-consuming reactions by default
(close_free_o2_sinks). The ecoli_tpc report does NOT yet mention this, and its enzyme-control section
(fig-ctrlthermal / tbl-control / tbl-ident) was computed BEFORE the closure. Add a scientific
model-curation note and put the control analysis on the corrected model. DESCRIBE THE CLOSURE
SCIENTIFICALLY — do NOT name it after a person in the report text (credit belongs in acknowledgments).

---

```
Work AUTONOMOUSLY; commit in parts; print a summary. Read first: reports/ecoli_tpc/{report.qmd,
supplementary.qmd, assemble.py}, src/etcgem/providers.py (close_free_energy_sinks + the four IDs),
strains/eciML1515/outputs/free_o2_sink_fix/NOTE.md (the audit numbers), src/etcgem/control.py, and
the current strains/eciML1515/outputs/control_tuned/ (pre-closure). Use Gurobi with a GLPK-abort
guard; print the solver. Operate on the TUNED model at rich BHI (the report's analysis baseline).

PART A - add the model-curation note (scientific; no person-named "correction")
- In the methods / model section (near the base-GEM + enzyme-constraint description, i.e. Layer 1 /
  model curation), add a concise paragraph, e.g.: "Four reactions in eciML1515 consume O2 at
  negligible enzyme cost — two quinol/menaquinol monooxygenases (QMO2, QMO3), a malate oxidase (MOX)
  and a copper oxidase (CU1Opp). Because they are effectively free, the optimiser routes O2 through
  them instead of the enzyme-costed terminal oxidases, creating a futile cycle (~75% of gross O2
  turnover at the rich optimum) that inflates and scrambles the O2 read-out. We close these four
  reactions; this routes O2 through a genuine terminal oxidase, makes net O2 consumption equal the
  exchange flux, and costs only ~0.3% growth, leaving the growth TPC essentially unchanged. Catalase
  and superoxide dismutase, whose high turnover makes their negligible cost correct biology, are
  retained." Use the ACTUAL audit numbers from free_o2_sink_fix/NOTE.md. Frame it as model curation
  for physically-interpretable energy metabolism — NOT as a named correction.

PART B - put the enzyme-control analysis on the corrected model
- Regenerate the control/identifiability run (control_tuned) on the CURRENT model (O2 sinks closed by
  default), tuned params, rich BHI — so the "which enzymes matter" section matches the model the
  methods now describe. Confirm QMO2/QMO3 (and the other closed reactions) no longer appear in the
  flux-carrying enzyme set. Update the assets (fig-ctrlthermal, tbl-control, tbl-ident) via assemble.
- Report whether the top envelope-control ranking CHANGES on the corrected model (expect it to stay
  acpP-led / lipid-associated, since O2 routing mainly affects respiratory enzymes that were not top;
  but check and report). Keep the existing control-coefficient framing (already in the report) — this
  is a re-run on the corrected model, not a re-analysis.

PART C - integrity check on the other reported values (no heavy regen)
- Spot-check that the closure leaves the report's headline tuned/emergent values unchanged within
  rounding (rmax, Topt, Ea, CTmax shift <~0.5%); state this in the summary so we know the validation/
  calibration/decomposition sections do not need regenerating. Do NOT regenerate those heavy sections.

PART D - build + verify
- Re-run reports/ecoli_tpc/assemble.py; quarto render report.qmd (+ supplementary if affected);
  confirm they build with no unresolved crossrefs. Report page count.

VERIFY (report all)
1. Model-curation note added in the methods/model section, described SCIENTIFICALLY (no person-named
   "correction" in the text); actual audit numbers used; catalase/SOD retention stated.
2. Control/identifiability regenerated on the corrected (O2-closed) model; QMO2/QMO3 gone from the
   enzyme set; tbl-control/fig-ctrlthermal/tbl-ident updated; whether the top ranking changed reported.
3. NO Ea-dissection content added (that is reports/activation_energy/).
4. Headline tuned/emergent values confirmed unchanged within rounding (heavy sections not regenerated).
5. report.pdf builds (page count reported); solver=gurobi.

CONSTRAINTS
- Report update + control-analysis regen only. No model-default changes, no Bayesian re-run, no
  Ea-dissection content, no heavy re-generation of validation/calibration/decomposition.
- Scientific description only; credit (if any) in acknowledgements, not the main text.
- Autonomous; commit in parts: "report(ecoli_tpc): document uncosted-O2-reaction closure as model curation",
  "report(ecoli_tpc): regenerate enzyme-control analysis on the corrected (O2-closed) model".
```
