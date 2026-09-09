# Claude Code prompt — K8: is the Candida ceiling over-prediction a Seq2Tm bias rather than a model defect? (autonomous)

Run from the project root (`.../MICROADAPT/etcGEMs`). Follows K7 (PR #10 — merge it in TASK 0).

**The hypothesis, and why it is worth an afternoon.** Three results already in the repository line up:

  1. **A1** measured Seq2Tm against a real *S. cerevisiae* meltome and found a systematic
     **bias of +5.43 °C** (RMSE 7.51, r = −0.048, n = 1947). The predictor over-states melting
     temperature.
  2. **Ilgaz** established independently (`a21d863`) that the predicted thermal limit **tracks the
     median enzyme Tm** — it moved less than 1 °C when three metabolic defects were corrected
     together.
  3. **K4/§4** measured the ceiling gap across seven strains: *M. maripaludis* −0.2, *Synechocystis*
     +1.7, ***E. coli* +5.9** (whose Tm are **measured** from a meltome), **the four Candida
     +9 to +15.8** (whose Tm are **predicted** by Seq2Tm).

Candida's excess over *E. coli* is roughly +3 to +10 °C, which is the size of A1's measured predictor
bias. If the ceiling is set by median Tm and the Tm are biased high by 5.43 °C, the ceiling should be
biased high by about the same.

**And it is the right kind of lever.** K7 showed the two envelope failures are strictly OPPOSED under
the curvature prior: steepness and fit are best at ΔCp = −3.0, the ceiling gap is smallest at −16.0
where the fit collapses. So ΔCp cannot fix both. A Tm OFFSET is different — it moves where unfolding
begins without touching the rising limb's curvature, so it can address the ceiling without worsening
the steepness. That is exactly what K7's finding requires.

**What this prompt is not.** It is not a licence to subtract a number until the ceiling matches. The
offset is A1's MEASURED bias, applied as a test with a predicted magnitude, and the result is
whatever it is. If the ceiling moves by much more or much less than 5.43 °C, that is informative and
must be reported as such.

NOTE TO USER: launch in an auto-approving mode. No emcee. Deterministic solves and a sweep. P4 may
still be running on `strains/eciML1515/` — check, and stay out of `strains/eciML1515/` and
`reports/ecoli_*` if so.

REFERENCE, read first: `reports/predictor_calibration/report.md` (A1 — the bias, and how it was
measured), `reports/K7_envelope/report.md` (the opposed failures, the ΔCp sweep),
`reports/K4_membrane/report.md` and `docs/CANDIDA_DISCUSSION_2026-09-07.md` §4 (the seven-strain
ceiling table), and `$CANDIDAS_ROOT/gem/gap_robustness.py` (READ ONLY — Ilgaz's demonstration that
the limit tracks median Tm).

---

```
Work AUTONOMOUSLY; commit per task, prefixed "K8 TASK n: "; maintain reports/K8_tm_bias/DECISIONS.md
FROM THE FIRST JUDGEMENT CALL. Print a final summary with each task DONE / PARTIAL / STOPPED.
Standing rules carry over. Check exit codes explicitly, never `cmd && check`. $CANDIDAS_ROOT is
READ ONLY. Branch `k8/tm-bias`; TASK 0 is the only write to `main`; end in a PR that is NOT merged.
Change no default.

TASK 0 - merge K7
- Merge PR #10 (`k7/envelope`) --no-ff. Verify with exit codes checked: Candida gate 79/79 with
  $CANDIDAS_ROOT unset, seven strains byte-identical, `stamp_reports.py --check` passes. Push,
  close, delete branch. If anything fails, stop.
- Report whether P4 has landed.

TASK 1 - establish the premise before testing it
Three checks, each cheap, each capable of killing the hypothesis before any sweep.
- **Is the bias uniform or Tm-dependent?** A1's +5.43 °C is a mean. Re-examine A1's own
  predicted-vs-measured data: is the bias constant across the Tm range, or does it vary with
  predicted Tm? If it varies, a flat offset is the wrong correction and the right one must be stated.
  Report the relationship, not just the mean.
- **What sets the ceiling, in this model, quantitatively?** Confirm Ilgaz's claim in OUR code rather
  than citing it: correlate predicted CT_max against the median (and other quantiles) of each
  species' Tm distribution across the four Candida strains. If CT_max tracks a quantile other than
  the median, use that.
- **Does the arithmetic work in principle?** A 5.43 °C shift in the whole Tm distribution should move
  CT_max by how much, on the model's own structure? Predict it BEFORE running the sweep, and record
  the prediction in DECISIONS.md. A test with a stated expectation is worth more than one without.

TASK 2 - apply the measured correction
- Apply A1's bias as a uniform shift (or the Tm-dependent correction TASK 1 establishes) to the
  Candida enzyme thermal parameters, as an EXPERIMENT OVERLAY, not a strain default.
- Report, per species: CT_max before and after, the gap against the observed limit, and the same for
  T_opt, E_a, rmax and the fit to the measured growth curve.
- **Check the steepness did not move.** K7's whole point is that the two failures are opposed; a Tm
  offset should leave the rising limb alone. If it does not, the hypothesis is wrong about the
  mechanism even if the ceiling improves. Report E_growth before and after.
- Compare the corrected Candida gaps against *E. coli*'s +5.9 °C. Does Candida converge on E. coli,
  or overshoot, or fall short?

TASK 3 - a sweep, to see whether 5.43 is special
A correction that works only at exactly the measured value is more convincing than one that works
across a wide range; a correction that needs a value far from 5.43 °C is not the hypothesis.
- Sweep the offset from 0 to about 20 °C and report CT_max gap, E_growth, fit, and T_opt per species.
- State the offset that minimises the ceiling gap per species, and how far each is from A1's 5.43 °C.
- If the required offset is close to 5.43 °C: the ceiling over-prediction is largely a predictor
  artefact, and that ties A1 to the §4 table. Say so, with the numbers.
- If it is far from 5.43 °C: the predictor bias is NOT the explanation, and the ceiling needs a
  mechanism nobody has proposed. Say that just as plainly.

TASK 4 - the cross-organism check that would confirm or refute it
The hypothesis makes a prediction beyond Candida, and the data to test it are already here.
- *E. coli*'s Tm are MEASURED, so predictor bias cannot explain its +5.9 °C gap. State what that
  implies: either the ceiling has TWO causes (a predictor component in Candida, plus something
  common to both), or the E. coli gap has a different origin.
- *M. maripaludis* (−0.2) and *Synechocystis* (+1.7) — establish where THEIR Tm come from (the
  methanogen's `strain.yaml` refers to a mesophile prior; check the phototroph). If they use priors
  rather than measurements and yet have no ceiling gap, that weakens the hypothesis and must be
  reported. Note the methanogen runs at a calibrated `kcat_scale`, which may have absorbed a gap.
- Do NOT run anything on `strains/eciML1515/` if P4 is still active; read committed outputs instead.

TASK 5 - record
- `reports/K8_tm_bias/report.md`: the premise checks, the stated prediction and what actually
  happened, the sweep, the cross-organism check, and a short section separating what this licenses
  from what it does not.
- Update `docs/CANDIDA_DISCUSSION_2026-09-07.md` §4 with the outcome (dated lines beside the
  seven-strain table; do not rewrite it) and §3a if it bears on A1's finding.
- Update `docs/OPEN_ITEMS.md`. Re-run `scripts/stamp_reports.py`.

VERIFY (report all)
1. TASK 0: merge; gates; whether P4 had landed.
2. TASK 1: whether the bias is uniform or Tm-dependent; which Tm quantile the ceiling tracks; the
   PREDICTED CT_max shift, recorded before the sweep was run.
3. TASK 2: per species, CT_max and gap before/after; E_growth before/after (the steepness must not
   move); convergence on E. coli's +5.9 or not.
4. TASK 3: the sweep; the minimising offset per species against A1's 5.43 °C; the verdict.
5. TASK 4: Tm provenance for the methanogen and phototroph; what their gaps imply for the hypothesis.
6. DECISIONS.md from the first judgement call.
7. `git diff main --stat`; no default changed; nothing under `strains/eciML1515/` or `reports/ecoli_*`
   if P4 is running.

CONSTRAINTS
- State the expected CT_max shift BEFORE running the sweep. A prediction recorded in advance is the
  difference between a test and a fit.
- The offset is A1's measured bias. Do not search for the offset that works and then present it as
  the correction.
- The steepness must be checked, not assumed. If a Tm offset moves E_growth, the mechanism is not
  what this prompt claims.
- No default changed. This is an overlay and a sweep.
- A refutation is as valuable as a confirmation and must be reported with equal prominence.
- Autonomous; commit per task.
```
