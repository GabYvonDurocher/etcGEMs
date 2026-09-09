# Claude Code prompt — K6: redo K5's model-vs-measurement comparison like for like, and find out whether the "wrong sign" discrepancy is real (autonomous)

Run from the project root (`.../MICROADAPT/etcGEMs`). Follows K5 (PR #8 — merge it in TASK 0).

**Why.** K5 reported the project's sharpest discrepancy against data: the repaired Candida models
give an activation-energy difference of **E_resp − E_growth = −0.33 eV** against a measured
**+0.33 eV**, "the wrong sign in all four species", and concluded this points at the maintenance
layer. That conclusion rests on a comparator that appears to be contaminated, and the contamination
runs in exactly the direction that makes the model look broken.

**The evidence.** The repository holds TWO measured E_growth for the same organisms, differing about
fourfold:

| source | E_growth | E_resp |
|---|---|---|
| `results/tables/arrhenius_growth_fgC_h_coefs.csv` (OLS, all temperatures) — what K5 used | **0.06–0.47 eV**, and NEGATIVE for three isolates (`Hae_1768` −0.206, `Hae_1769` −0.114, `Duo_1770` −0.015) | 0.28–0.80 eV |
| the manuscript's hierarchical Bayesian fit (`manuscript/v3.qmd`) | **0.83–1.14 eV** | 0.30–0.52 eV |

A negative activation energy for growth is not biology. It is what a straight Arrhenius line returns
when fitted through a curve that turns over. E_resp is unaffected because respiration rises
monotonically, which is why the two sources agree on it and disagree fourfold on growth.

Using the manuscript's values, the measured difference is **E_resp − E_growth = −0.84 to −0.31 eV**.
The repaired model's −0.33 sits inside that range; with the complex III correction, −0.23 sits just
outside it. **The sign may not be wrong at all.**

**And there is a mechanism that guarantees the bias.** The Candida models over-predict the thermal
limit by +9 to +15.8 °C (K4/§4). So across 22–44 °C the organism's growth collapses and the model's
does not. Fitting both over the same window depresses the MEASURED E_growth through the turnover and
leaves the MODEL's undepressed. That is not like for like, and it biases toward "the model is
wrong".

The same objection applies to K5's other two rows: the respiration-per-unit-growth level (measured
0.85 against 2.01 repaired) and the 44 °C / 30 °C ratio (measured 4.70× against 1.20×) are both
dominated by the organism's growth collapsing where the model's does not.

**This prompt does not assume the model is right.** It makes the comparison valid and reports what
it then shows. If the discrepancy survives, that is a stronger result than K5's, because it will
have survived the obvious objection.

NOTE TO USER: launch in an auto-approving mode. No emcee. Cheap — re-fitting summary statistics and
re-running deterministic solves.

REFERENCE, read first: `reports/K5_respire/report.md` and `DECISIONS.md`, `manuscript/v3.qmd` in
`$CANDIDAS_ROOT` (READ ONLY) for the Bayesian E values and how they were fitted, the two OLS coef
tables, and `$CANDIDAS_ROOT/scripts/09_bayesian_models.R` for the fitting convention.

---

```
Work AUTONOMOUSLY; commit per task, prefixed "K6 TASK n: "; maintain reports/K6_like_for_like/DECISIONS.md.
Print a final summary with each task DONE / PARTIAL / STOPPED. Standing rules carry over. Check exit
codes explicitly, never `cmd && check`. $CANDIDAS_ROOT is READ ONLY. Branch `k6/like-for-like`; TASK 0
is the only write to `main`; end in a PR that is NOT merged. Do not write to `strains/eciML1515/` or
`reports/ecoli_*` if P4 is still running — check and say which you found.

TASK 0 - merge K5
- Merge PR #8 (`k5/respire`) --no-ff. Verify with exit codes checked: Candida gate 79/79 with
  $CANDIDAS_ROOT unset, seven strains byte-identical, stamps clean. Push, close, delete branch.
  If anything fails, stop.

TASK 1 - establish what the two measured E_growth actually are
Do not take the framing above on trust; verify it.
- For both tables and the Bayesian fit, establish: the temperature range fitted, the functional form,
  whether the fit is per isolate or hierarchical, and whether any temperature exclusion or
  rising-limb restriction was applied. Read `09_bayesian_models.R` and the OLS producing script.
- Confirm or refute that the OLS E_growth is depressed by the turnover: refit the OLS Arrhenius to
  growth on the RISING LIMB ONLY (temperatures at or below each isolate's own optimum) and report
  what E_growth becomes. If it moves toward the Bayesian 0.83–1.14 eV, the diagnosis holds.
- Report which measured comparator is appropriate for a model-versus-data test, and why. If the
  answer is "neither, without care", say what the correct one is.

TASK 2 - redo the comparison like for like
For each species, compare model against measurement THREE ways, and report all three:
  (a) **Rising limb only, both sides.** Fit the model's predicted growth and respiration over the
      same temperature window used for the measured rising-limb fit — the organism's window, not the
      model's. Report E_growth, E_resp and the difference, model and measured.
  (b) **Full window, both sides, with the caveat stated.** What K5 did, retained for continuity, with
      an explicit note that the model does not turn over where the organism does.
  (c) **Against the manuscript's Bayesian values**, which are what the paper quotes.
- Do the same for the respiration-to-growth level and the 44/30 ratio: restrict to temperatures where
  the organism is actually growing, and report what changes.
- ONE TABLE, three panels, so the effect of the comparator is visible at a glance.
- State plainly, for each of the three, whether the sign of E_resp − E_growth agrees with measurement.

TASK 3 - the honest verdict
- If the discrepancy DISAPPEARS under (a) and (c): K5's "sharpest open discrepancy" was a comparator
  artefact. Say so plainly, correct `reports/K5_respire/report.md` with a dated note (do not rewrite
  its history), and update `docs/OPEN_ITEMS.md`.
- If it SURVIVES: it is now a much stronger result, having survived the obvious objection. Say so,
  and say what it points at — K5 suggested the maintenance layer; test that claim if it can be done
  cheaply (does adding or scaling NGAM(T) move the model's E_resp − E_growth toward measurement, and
  by how much?).
- If it PARTLY survives — right sign, wrong magnitude — report the magnitude gap and do not round it
  into either verdict.
- Do NOT tune anything to close a gap. Report.

TASK 4 - the comparator hazard, recorded once so it stops recurring
This is the second time in this project that a comparison has been made against the wrong version of
a measured quantity (the first: Parsa's NLDM CSV predating its own medium change).
- Add to `docs/OPEN_ITEMS.md` §4 a standing hazard: **the repository holds more than one measured
  value for some quantities, and they disagree**. Name this case with both numbers, and give the
  rule — when comparing a model to data, fit both over the same window with the same functional
  form, and state which measured source was used.
- Check whether the same trap exists for any OTHER quantity used in a model-data comparison anywhere
  in the project — CUE, respiration per cell, growth rate, T_opt. Report what you find; fix nothing.

VERIFY (report all)
1. TASK 0: merge; gates; whether P4 had landed.
2. TASK 1: the fitting convention for each source; what OLS E_growth becomes on the rising limb;
   which comparator is appropriate and why.
3. TASK 2: the three-panel table, all four species; the sign verdict for each panel.
4. TASK 3: the verdict, with the maintenance-layer test if it was cheap enough to run.
5. TASK 4: the standing hazard recorded; any other quantity with the same trap.
6. `git diff main --stat`; nothing tuned; no committed result altered beyond dated corrective notes.

CONSTRAINTS
- Verify the framing in this prompt rather than assuming it. If the OLS E_growth does NOT move toward
  the Bayesian value on the rising limb, my diagnosis is wrong and the prompt should say so.
- Both sides of every comparison use the same window and the same functional form. That is the whole
  point.
- Do not tune. A surviving discrepancy is a better result than a closed one.
- Correct K5's report with a dated note; do not rewrite what it said.
- Autonomous; commit per task.
```
