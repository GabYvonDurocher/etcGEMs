# Claude Code prompt — K5: make the Candida models actually respire, and test them against the measured respiration for the first time (autonomous)

Run from the project root (`.../MICROADAPT/etcGEMs`). Follows K4 (PR #7 — merge it in TASK 0).

**The finding this repairs.** K4 established that the respiratory chain delivers **0.02–0.03 %** of
the protons ATP synthase consumes in the three *Candidozyma* models. Eleven uncosted, reversible
metabolite/proton symporters close the circuit outside the chain — one aspartate carrier alone
supplying 32.5 of the 31.0 protons per hour required. The chain's only essential role is
re-oxidising the ubiquinol from pyrimidine biosynthesis. It is functional and bypassed, not broken:
stripping the proton coupling makes it carry the whole load at a cost of one third of predicted
growth. Verified against the published `iRV973`, so this is in the reconstruction, not the port.

**Why it can be fixed properly rather than patched.** We have MEASURED respiration for these
species — Ilgaz's O₂ assay — and have never once compared it against what the models predict. So
this prompt does not just close a leak; it repairs the mechanism and then asks whether the repaired
model respires like the organism does. That is a validation these models have never had.

**Parallel work.** P4 may still be running on `strains/eciML1515/`. This prompt AUDITS all seven
strains (read-only) but FIXES only `strains/c*/`. E. coli repairs wait for P4 to land.

NOTE TO USER: launch in an auto-approving mode. No emcee. Deterministic solves and comparisons.

REFERENCE, read first: `reports/K4_membrane/report.md` and its `DECISIONS.md`,
`docs/OPEN_ITEMS.md` §3.8–§3.12, `src/etcgem/sink_audit.py` (which cannot see this defect class),
Parsa's Config A transport costing as ported by P1, and the measured tables under
`$CANDIDAS_ROOT/results/tables/` (READ ONLY) — `derived_N0_R_results_with_carbon.csv`,
`arrhenius_respiration_fgC_h_coefs.csv`, `arrhenius_growth_fgC_h_coefs.csv`.

---

```
Work AUTONOMOUSLY; commit per task, prefixed "K5 TASK n: "; maintain reports/K5_respire/DECISIONS.md.
Print a final summary with each task DONE / PARTIAL / STOPPED. Standing rules carry over: stop and
record rather than guess; never weaken a test; never edit a number to match. Check exit codes
explicitly, never `cmd && check`. $CANDIDAS_ROOT is READ ONLY. Branch `k5/respire`; do not push to
`main` except TASK 0; end in a PR that is NOT merged. DO NOT WRITE TO `strains/eciML1515/` OR
`reports/ecoli_*` while P4 is running — check whether it has landed and say which you found.

TASK 0 - merge K4
- Merge PR #7 (`k4/membrane-candida`) --no-ff. Verify with exit codes checked explicitly: Candida
  gate 79/79 with $CANDIDAS_ROOT unset, seven strains byte-identical, `stamp_reports.py --check`
  passes. Push, close, delete branch. If anything fails, stop.

TASK 1 - extend the sink audit to the coupling ion, and run it on all seven strains
The audit watches ATP and reducing equivalents. It cannot see a free proton circuit, which is why
this went unnoticed.
- Add a proton class to `sink_audit.py`: for a built model at a solved state, identify reactions
  that translocate H+ across the energising membrane, classify each as costed/uncosted and
  reversible/irreversible, and report the proton BUDGET — what the chain delivers against what
  ATP synthase and any other consumer draw, as a fraction.
- Run on all seven strains, READ ONLY where P4 is active. Report the fraction per strain.
- **If E. coli or the other two organisms show the same defect, that is a significant finding**
  bearing on Parsa's Config E/F respiration R² (0.72 and 0.96). Report it prominently; do NOT fix
  it here.

TASK 2 - fix the Candida models, least invasive first
Try these IN ORDER and stop at the first that works. Report what each achieves, and do not skip
ahead — the cheapest fix that restores the chain is the right one.
  (a) COST THE TRANSPORT. These symporters are uncosted; Config A (MMRT-costed transport, gated on
      E. coli by P3) makes transport draw on the enzyme budget. If free proton pumping stops being
      free, the solver may prefer the chain on its own. Test this first — it is a mechanism we
      already have and have validated elsewhere.
  (b) IRREVERSIBILITY where the biology justifies it, reaction by reaction, with the justification
      recorded per reaction. A symporter running backwards to import protons is not automatically
      wrong; say why it is wrong for each one you constrain.
  (c) EXPLICIT BOUNDS as a last resort, named and documented, in the strain data not the core.
- Whatever works, the criterion is the same: report the proton budget before and after, and confirm
  the chain carries the load.
- Report the cost: K4 measured one third of predicted growth for the coupling strip alone. State
  what the chosen fix costs, per species.
- Do NOT delete reactions. These are real biology; the defect is that they are free, not that they
  exist.

TASK 3 - THE TEST: does the repaired model respire like the organism?
This has never been done. Use SCALE-FREE comparisons — absolute per-cell O₂ depends on the cell-mass
conversion, which is unreliable (2 µm³ / 350 fg typed in the tables against `config.R`'s
21.21 µm³ / 2120.58 fg, ~6× apart, recorded in OPEN_ITEMS 1.9).
Compare, per species, model against measurement:
  * **Respiration-to-growth ratio.** The measured `resp_over_growth` is carbon per carbon, so the
    cell-mass conversion cancels. The model predicts both. This is the cleanest test available.
  * **Activation energy of respiration**, from `arrhenius_respiration_fgC_h_coefs.csv`, against the
    model's predicted E_a of O₂ uptake across the same temperature range.
  * **The shape of the respiration TPC** — where it peaks relative to growth, and whether
    respiration continues rising while growth turns over (the decoupling the Candida work
    established from data).
- Report before-fix and after-fix for each, so the repair's effect is visible.
- Report absolute per-cell respiration too, but LABEL IT as carrying the cell-mass assumption, and
  do not draw conclusions from it.
- If the repaired model still does not match, that is a result. Report it. Do not tune to fit.

TASK 3b - RE-TEST THE MEMBRANE CONSTRAINT, now that the model can respire and carbon is capped
K4's null result on the ETC-area constraint was obtained on models with TWO escape routes, and both
are now known:
  * the proton leak this prompt repairs (the chain carried 0.02-0.03% of the load, so constraining
    the area of complexes carrying no flux could not do anything); and
  * FERMENTATION with no carbon cap. P4 independently found the same in E. coli on M9 — "nothing
    limits carbon, so the ETC area budget alone left the cell fermenting (F: RQ 0.026, zero acetate;
    E: growth 3.7e-5)" — and fixed it by adding the carbon cap. K4 ran its A_ETC sweep with NO
    carbon cap, which is why "no budget, including zero" changed nothing.
So the membrane constraint has never actually been tested on a Candida model capable of respiring
under a carbon budget. Test it now.
- Re-run K4's A_ETC sweep, per species, on the REPAIRED model AND with a carbon cap active. Choose
  the cap the way P4 did for M9 and record the value and the reason.
- Report, per species and per A_ETC: T_opt, CT_max, E_a, growth at 40 C, whether the constraint
  binds, and the flatness metric.
- Ask K4's question again: what interspecies difference in A_ETC would be required to put a relative
  below detection at 40 C? K4 got "no answer at all". If there is now an answer, report it beside
  K2's 13.8 C enzyme-thermal requirement.
- CHECK THE DIRECTION. K4 found tightening the budget hurt C. auris MOST, which is backwards for the
  phenotype. State whether that survives the repair.
- The parameter caveat is unchanged and must be restated: zero of twenty area/turnover values are
  measured in any Candida, so all four species carry identical tables. A constraint with
  undifferentiated parameters cannot EXPLAIN a species difference however it now behaves. Report
  what the mechanism does; do not present it as an explanation.

TASK 4 - what it does to Figure 4's arithmetic
K2's required separation of 13.8 °C was computed on a model with at least two escape routes: free
protons, and fermentation ("no budget, including zero, puts any relative below detection, because
the models can ferment" — K4).
- Recompute the required interspecies Tm separation on the REPAIRED model, exactly as K2 did — and
  report it BOTH with and without a carbon cap, since K4/P4 have now shown fermentation is the
  escape route that made the earlier requirement so large.
- Report it beside K2's 13.8 °C and the standalone's 32.5 °C, and against the sequence-predicted
  0.411 °C and the measured *S. cerevisiae*/*S. uvarum* benchmark of 1.6 °C.
- State plainly whether the repair moves the requirement, and in which direction. A model with
  fewer escape routes should be easier to kill, so the requirement may FALL — if it does not, say so.
- Do NOT adjudicate what this means for the conclusion. Report the number and let the humans read it.

TASK 5 - record
- `reports/K5_respire/report.md`: the audit table for all seven strains, the fix and its cost, the
  three scale-free comparisons before and after, and the recomputed requirement.
- Update `docs/CANDIDA_DISCUSSION_2026-09-07.md` §1 with the recomputed requirement (a few dated
  lines beside the existing table; do not rewrite it) and §4 if the ceiling numbers move.
- Update `docs/OPEN_ITEMS.md`: close what this closes; add the E. coli proton finding as a new item
  if TASK 1 found one.
- Re-run `scripts/stamp_reports.py`.

VERIFY (report all)
1. TASK 0: merge; gates; whether P4 had landed.
2. TASK 1: the proton budget per strain, all seven; whether E. coli shows the same defect.
3. TASK 2: which fix worked; per reaction, what was changed and why; proton budget before/after;
   growth cost per species.
4. TASK 3: the three scale-free comparisons, before and after, per species; the labelled absolute
   comparison; an explicit statement of whether the repaired model respires like the organism.
5. TASK 3b: the A_ETC sweep on the repaired, carbon-capped model; whether a required interspecies
   difference now exists; whether the direction still runs backwards; the parameter caveat restated.
6. TASK 4: the recomputed required separation beside 13.8 and 32.5 °C, with and without the carbon
   cap, and the direction of movement.
7. `git diff main --stat`; nothing under `strains/eciML1515/` or `reports/ecoli_*` if P4 is running.

CONSTRAINTS
- Least invasive fix first, and stop at the first that works. Do not reach for explicit bounds if
  costing the transport suffices.
- Do not delete reactions. The defect is that they are free.
- Scale-free comparisons carry the conclusions. Absolute per-cell numbers are reported and labelled,
  never concluded from.
- If the repaired model does not match measurement, report it. Do not tune.
- Do not fix E. coli here, however tempting — P4 owns it.
- The membrane re-test (3b) reports what the mechanism DOES. With identical parameters across
  species it still cannot explain a difference between them, and the report must say so plainly
  however favourable the numbers look.
- Autonomous; commit per task.
```
