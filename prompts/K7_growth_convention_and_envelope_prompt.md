# Claude Code prompt — K7: settle which growth convention Figure 4's requirement was computed under, then test whether the model's growth envelope is too steep (autonomous)

Run from the project root (`.../MICROADAPT/etcGEMs`). Follows K6 (PR #9 — merge it in TASK 0).

Two jobs, ordered deliberately. The first is small and bears on a number already in circulation; the
second is the sharpest open target the project has. Do them in order — if the first turns out badly,
the second's comparator may need rethinking.

NOTE TO USER: launch in an auto-approving mode. No emcee. Cheap: reading fitting code, deterministic
solves, and one parameter sweep. P4 may still be running on `strains/eciML1515/` — check, and stay
out of `strains/eciML1515/` and `reports/ecoli_*` if so.

## What K6 established, which this builds on

K6 found the repository holds **two conventions for the measured growth curve**, both correct, both
in use side by side:

  * one file counts a **dead well as an observed zero**, deliberately — this is what every Candida
    strain CALIBRATES against;
  * the other keeps **only survivors** — this is what every activation-energy fit uses.

At 40 °C, *C. haemulonii* grows at **0.000 h⁻¹** under the first and **0.66** under the second.

40 °C is the temperature at which Figure 4's counterfactual asks whether a relative falls below the
0.05 h⁻¹ detection floor. Under one convention it is already there before any Tm shift is applied;
under the other it is thirteen times above it. **The required separation — currently 13.57 °C, and
quoted — is therefore convention-dependent by an unknown amount.**

K6 also localised the remaining model-data discrepancy: with maintenance removed, respiration lands
almost exactly on measurement (0.231–0.474 against 0.518), and **88 % of the residual is the model's
growth rising too steeply**. That points at the kinetic envelope, not maintenance and not the chain.

REFERENCE, read first: `reports/K6_like_for_like/report.md` and `DECISIONS.md`,
`reports/K5_respire/report.md` (with K6's dated corrections), `reports/candida_thermal_limit/`
(K2's requirement and the counterfactual), and in `$CANDIDAS_ROOT` (READ ONLY) the two growth files
K6 names, plus `scripts/09_bayesian_models.R` and whatever produces the counterfactual input.

---

```
Work AUTONOMOUSLY; commit per task, prefixed "K7 TASK n: "; maintain reports/K7_envelope/DECISIONS.md
FROM THE FIRST JUDGEMENT CALL — a recent run in this series reached its final task without one, and
its reasoning existed only in a chat message. Print a final summary with each task DONE / PARTIAL /
STOPPED. Standing rules carry over. Check exit codes explicitly, never `cmd && check`.
$CANDIDAS_ROOT is READ ONLY. Branch `k7/envelope`; TASK 0 is the only write to `main`; end in a PR
that is NOT merged.

TASK 0 - merge K6
- Merge PR #9 (`k6/like-for-like`) --no-ff. Verify with exit codes checked: Candida gate 79/79 with
  $CANDIDAS_ROOT unset, seven strains byte-identical, `stamp_reports.py --check` passes. Push, close,
  delete branch. If anything fails, stop.
- Report whether P4 has landed. If it has not, do not write to `strains/eciML1515/` or
  `reports/ecoli_*` for the rest of this prompt.

TASK 1 - which convention does Figure 4's requirement use?
Small, and it bears on a number people are already quoting.
- Trace it, do not infer it: follow the counterfactual's input from the file on disk through to the
  reported requirement, and state which of the two growth files it reads, at which step, and where
  the 0.05 h⁻¹ detection floor is applied.
- Do the same for the CALIBRATION target — the C. auris curve the three global parameters were fitted
  to. If calibration and counterfactual use different conventions, say so explicitly: it would mean
  the model was fitted to one curve and falsified against another.
- Then quantify it. Recompute the required interspecies Tm separation under BOTH conventions, on the
  current repaired model, and report them side by side with K2's 13.8 °C and K6's 13.57 °C.
- If the two conventions give materially different requirements, that is the finding and it must be
  stated at the top of the report. If they agree, say so as clearly — it retires a worry cheaply.
- Recommend which convention is appropriate for a detection-threshold counterfactual, with the
  reasoning. Do NOT change any default; recommend and record.

TASK 2 - is the model's growth envelope too steep? Measure it.
K6 attributed 88 % of the residual to this. Test it directly rather than by subtraction.
- Report, per species, the model's E_growth over the ORGANISM's rising-limb window against the
  measured Bayesian value (0.62–1.15 eV) and against K6's rising-limb OLS refit (0.21–0.93 eV). Use
  the same window and functional form on both sides — K6's lesson.
- Report the model's E_resp the same way, so the difference is decomposed into its two parts rather
  than quoted as a single number. K6 found respiration lands on measurement when maintenance is
  removed; confirm which side carries the error.
- State plainly: is the model's growth too steep, and by how much, per species?

TASK 3 - the ΔCp prior: how much of the steepness is it?
The kinetic envelope's curvature comes from a single shared literature prior, `dcp_prior_kJ = -4.0`,
which has never been tested against these organisms.
- Sweep ΔCp over a defensible range (state it, with the literature basis — Hobbs 2013 is the source
  cited in the strain configs) and report, per species: E_growth, E_resp, their difference, T_opt,
  CT_max, and the fit to the measured growth curve.
- Report the value that best reconciles E_growth with measurement, AND SAY PLAINLY WHETHER THAT
  VALUE IS DEFENSIBLE. A ΔCp outside the literature range that fixes the fit is a diagnosis, not a
  parameter choice.
- Check the second consequence: the Candida models over-predict CT_max by +9 to +15.8 °C. Does the
  ΔCp that fixes the steepness also move the ceiling, and in which direction? A single parameter
  fixing both would be a real result; fixing one and worsening the other is equally worth knowing.
- Do NOT change the default. This is a sensitivity analysis, not a calibration.

TASK 4 - record
- `reports/K7_envelope/report.md`: TASK 1's trace and the two requirements, TASK 2's decomposition,
  TASK 3's sweep, and a short section on what each licenses.
- Update `docs/CANDIDA_DISCUSSION_2026-09-07.md` §1 with the convention finding (dated lines beside
  the existing table, do not rewrite it) and §4 if the ceiling picture changes.
- Update `docs/OPEN_ITEMS.md`: close what this closes; add the ΔCp question with a trigger if it
  turns out to matter.
- Re-run `scripts/stamp_reports.py`.

VERIFY (report all)
1. TASK 0: merge; gates; whether P4 had landed.
2. TASK 1: the traced path for the counterfactual AND the calibration target, naming the file each
   reads; the requirement under both conventions beside 13.8 and 13.57 °C; the recommendation.
3. TASK 2: per species, model against measured E_growth and E_resp, same window and form both sides;
   an explicit verdict on whether growth is too steep and by how much.
4. TASK 3: the ΔCp sweep; the reconciling value and whether it is defensible; its effect on CT_max.
5. DECISIONS.md, maintained from the first judgement call.
6. `git diff main --stat`; no default changed; nothing tuned; nothing under `strains/eciML1515/` or
   `reports/ecoli_*` if P4 is running.

CONSTRAINTS
- TASK 1 traces, it does not infer. Follow the code path to the file on disk.
- Same window, same functional form, both sides of every comparison. That is K6's lesson and it is
  now a standing rule.
- No default changed anywhere. TASK 3 is a sensitivity analysis; a parameter that fixes a fit is a
  finding, not a decision.
- If a value outside the literature range is needed to reconcile the model with data, say so — that
  is more informative than a reconciled fit.
- Autonomous; commit per task.
```
