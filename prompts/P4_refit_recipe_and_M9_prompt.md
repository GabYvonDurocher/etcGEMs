# Claude Code prompt — P4: refit Configs D, E and F under the canonical settings, add M9, and report what moved (autonomous, long-running)

Run from the project root (`.../MICROADAPT/etcGEMs`). Merge P3 first (TASK 0 does it).

**Why.** P3 gated D/E/F successfully, but against the model Parsa fitted, not the model this
repository now defines. Every one of his fits used the **blanket** medium (`uptake_ub = 1000` for
every metabolite — by his own account ~454,000 mmol C gDW⁻¹ h⁻¹, effectively unlimited, "gorging on
carbon and dumping it as CO₂ while barely respiring", RQ 12.8). Recipe ceilings are now canonical,
`c_max` is 120 not 60, transporter k_cat is 300, and Config F uses Config E's ETC table plus a
non-electrogenic bd-II. The gated R² values therefore describe a superseded model.

This prompt refits under the canonical settings, on this machine, and reports what moves. It is
LONG-RUNNING and unattended by design. **K4 (the Candida membrane-area work) is being run in
parallel and writes only to `strains/c*/`** — do not touch those, and expect the repository to
change beneath you there.

NOTE TO USER: launch in an auto-approving mode and leave it. Hours to overnight. It runs emcee —
the only prompt in this series permitted to.

## Canonical settings for every fit in this prompt

| | value | authority |
|---|---|---|
| medium | **recipe ceilings** (`uptake_ub = K · concentration`, K prior 2–10 L gDW⁻¹ h⁻¹, sampled) | Parsa, Q2; composition doi:10.3389/fmicb.2022.855331 |
| `c_max` | **120** | his own sweep ("≈100–120 sweet spot"); 120 is the only value in that range with non-zero acetate overflow on both media |
| transporter k_cat | **300 s⁻¹** | P2 TASK 1, settled by reproducing his figure |
| Config F ETC table | **Config E areas/turnovers + non-electrogenic bd-II** | P3 TASK 3; his own note, "0 H⁺ only (config-E turnovers via E weights)" |

---

```
Work AUTONOMOUSLY; commit per task, prefixed "P4 TASK n: "; maintain reports/P4_refit/DECISIONS.md.
Print a final summary. Standing rules carry over: stop the task and record rather than guess; never
weaken a test; never edit a number to match. Check exit codes explicitly, never `cmd && check`.
$PARSA_ROOT, $CANDIDAS_ROOT, $ECOLI_R2A, $ECOLI_M9 are READ ONLY. TASK 0 is the only write to
`main`; the rest is branch work on `p4/refit` ending in a PR that is NOT merged.

TASK 0 - merge P3, then SCOPE the work before spending any compute
- Merge PR from `p3/gate-def` --no-ff. Verify with exit codes checked: Candida gate 79/79 with
  $CANDIDAS_ROOT unset, P1 gate 60/60, seven strains byte-identical, `stamp_reports.py --check`
  passes. Push, close, delete branch. If anything fails, stop.
- THEN SCOPE, and report the scope BEFORE running anything:
    * Identify exactly which fits produce the TEN R² values P3 gated, and any other number quoted in
      reports/ecoli_gasflux/. Those are IN SCOPE.
    * Parsa's tree holds ~25 calibration directories including `freebd`, `wideenv`, `nocap`,
      `_test`, `_resume` variants. Those are OUT unless they produce a quoted number.
    * Add M9 for whichever configs are in scope — it is ingested and has never been fitted.
    * Print the scoped list with, per fit: config, medium, what it produces, and an estimated
      runtime from Parsa's own chain files (walkers, steps, and his wall-clock where logged).
    * If the total estimate exceeds ~20 hours, say so and run in the order given below so a partial
      run is still useful.

TASK 1 - a cheap pre-flight, before the long runs
Do NOT start emcee until these pass; a bad setting caught here saves a night.
- For each in-scope config/medium, run a single deterministic solve under the canonical settings and
  report: growth, acetate flux, O2, CO2, RQ, and whether the carbon cap binds.
- Confirm the four canonical settings are actually in force in each run's `resolved_config.yaml` —
  read them back, do not assume. P3 found a run silently carrying ConfigD's cap into E and F; that
  class of error must be excluded here explicitly.
- Confirm acetate overflow is non-zero wherever ConfigD is active, and that RQ is physiological
  (Parsa reports the recipe medium moves it from 12.8 to 0.46 — a value far outside ~0.6–1.3 in
  either direction is a stop condition, not a result).
- If anything looks wrong, STOP and report. Do not spend the night on a misconfigured model.

TASK 2 - the refits, in this order
Order matters: a partial run must still answer the most important question.
  1. ConfigD, NLDM and LB — the medium change bites hardest here; this is the headline.
  2. ConfigE, NLDM and LB.
  3. ConfigF, NLDM and LB.
  4. M9 for each config in scope.
- Use the same sampler settings Parsa used (walkers, steps, burn-in, convergence criterion) unless
  they are unrecoverable, in which case state what you chose and why.
- Write each to a NEW output directory named for the settings, e.g.
  `calibration_configD_NLDM_recipe_cmax120/`. Do NOT overwrite his ported outputs — they are the
  comparison.
- After each fit completes, immediately: write `resolved_config.yaml`, record the chain path, and
  compute the R² the way his figure script does (one point from the chain: median for D, MAP for E
  and F — P3 established this). Commit. A crash at fit 5 must not lose fits 1–4.
- Report convergence honestly per fit: acceptance fraction, autocorrelation time, whether the chain
  is converged by the stated criterion. **A non-converged fit is reported as non-converged, not
  quoted.**

TASK 3 - what moved, and why
- One table: per config and medium, his blanket-medium R² (as gated in P3) against the recipe
  refit, plus the posterior medians of every shared parameter.
- Attribute every material movement to a named cause — medium, c_max, k_cat, the ConfigF table —
  with evidence. Where several changed at once and cannot be separated, SAY SO rather than
  guessing; if separating one matters, note what single-change run would settle it.
- Report the K posterior explicitly. Parsa found its 90 % width ratio was 0.89 in R2A/NLDM, i.e.
  the data barely constrain it. State whether that holds here. **If K remains unidentified, the
  medium ceiling is a prior choice rather than a fitted quantity and the report must say so plainly.**
- Report RQ per config and medium, and reconcile the two figures in circulation: P2 found ConfigC
  NLDM RQ = 1.04 against the ~7–9 in his report; Parsa quotes 12.8 → 0.46. Establish which
  quantities those are and whether they agree.

TASK 4 - M9, first light
M9 has never been fitted by anyone.
- Report its fits as a first result, not as a comparison: parameters, R², convergence, and how the
  posterior differs from NLDM and LB.
- Flag anything that looks like a data problem rather than a model problem — M9 is minimal medium
  and the pipeline's own `Skipped_Series_Log.csv` and the 25 °C no-growth series P3 found are worth
  checking against the fit's residuals.

TASK 5 - update the record
- `reports/ecoli_gasflux/README.md`: the refit values become the quoted ones; the blanket-medium
  values stay as a labelled historical comparison. Say at the top which medium each number came
  from — that ambiguity is what made this necessary.
- Re-run `scripts/stamp_reports.py`.
- Update `docs/OPEN_ITEMS.md`: close 1.3 and 1.10 if this settles them; add anything found.

VERIFY (report all)
1. TASK 0: merge; all gates; the SCOPED list with runtime estimates and what was excluded.
2. TASK 1: the pre-flight table; the four canonical settings read back from each resolved_config.
3. TASK 2: per fit — completed/failed, convergence diagnostics, output directory.
4. TASK 3: the movement table with attributions; the K posterior and whether it is identified;
   the RQ reconciliation.
5. TASK 4: M9 results and any data-quality flags.
6. TASK 5: the README; stamps; OPEN_ITEMS updated.
7. `git diff main --stat`; confirmation that nothing under `strains/c*/` was touched (K4 owns those).

CONSTRAINTS
- Scope before you spend. A 25-directory refit is not the job; the fits behind quoted numbers are.
- Never overwrite Parsa's ported outputs — the comparison depends on them.
- Commit after every fit. A long unattended run must degrade gracefully.
- A non-converged chain is reported, never quoted.
- If K is unidentified, say so. It changes what the medium ceiling IS.
- Do not touch `strains/c*/` — K4 is running there in parallel.
- Autonomous; commit per task and per completed fit.
```
