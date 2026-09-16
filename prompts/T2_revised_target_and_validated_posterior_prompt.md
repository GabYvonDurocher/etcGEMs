# Claude Code prompt — T2: implement the approved target revision, validate it against the signed protocol, and earn the first posterior (resumable; ~4 h of session work around ~1–2 days of detached runs)

Run from the project root (`.../MICROADAPT/etcGEMs`), on `../etcGEMs-venv`.

> **RESUMPTION — READ THIS BEFORE ANYTHING ELSE.**
> This prompt is designed to be interrupted by session limits and picked up cold, possibly several
> times. The long runs execute in a **detached batch driver** that does not need this session to be
> alive. **On every start, first check whether you are resuming:**
>
> 1. `cat reports/T2_validated_posterior/status.json 2>/dev/null` — if it exists, this is a
>    resumption. Read it, read `launch_status.md` beside it, and read the last five entries of
>    `DECISIONS.md`. Jump to the stage `status.json` names. **Never redo a stage marked
>    complete.** Confirm the branch is `t2/validated-posterior` and `git status` is clean or
>    contains only the driver's own outputs.
> 2. If `status.json` says `stage: "driver_running"`, check whether the driver process is alive
>    (`driver.pid`, and `ps -p $(cat driver.pid)`). **If alive: do not relaunch it, do not touch
>    its outputs, do not run anything expensive.** Read its progress log, write a one-paragraph
>    D-entry on where it is, and STOP this session with a summary. Come back when it has
>    finished. If dead and `runs_complete < 5` and the driver's own log shows no STOP verdict:
>    it was killed externally (reboot, `/tmp` clear, credit cut mid-write). Relaunch it exactly
>    as TASK 4 specifies — the driver is idempotent and resumes each seed from its checkpoint.
> 3. If `status.json` says `stage: "driver_finished"` or `"driver_stopped"`, go to TASK 5.
> 4. If there is no `status.json`, this is the first start: begin at TASK 0.
>
> Every task below ends by writing its stage to `status.json` atomically (write to a temp file,
> then rename) and committing. If a session dies mid-task, the next session sees the last
> committed stage and repeats only the unfinished part.

**T1's PR #40 must be merged first** — TASK 0 does it. Branch `t2/validated-posterior`.

**Read first, and treat as the authority over this prompt:** `docs/RIGOUR.md`,
`docs/TARGET_REVISION_SPEC.md`, `reports/T1_target_revision/DECISION_PACKAGE.md`,
`docs/VALIDATION_PROTOCOL_DRAFT.md`, `reports/P17_inactive_prior/report.md` and
`launch_status.md` (the detached-run pattern this prompt copies), `docs/OPEN_ITEMS.md` §0 and §4.

**The PI's decisions on T1's package (2026-09-13), which this prompt executes:**

1. **f_metab (1.29): removal APPROVED.** Turn on `remove_inactive: ["f_metab"]` for eciML1515.
2. **Infeasibility (1.30): −∞ for structural infeasibility APPROVED**, with a separate finding
   (1.33) on why the model is infeasible over ~96 % of a defensible prior on NLDM.
3. **Curvature (1.31): retain as is.** No defect found; nothing to apply.
4. **Protocol (1.32): SIGNED, with one amendment** — check (d) becomes the PRIOR fraction rejected
   as infeasible, with its uncertainty; under −∞ the dead stratum is excluded, not occupied.

**What −∞ means, precisely.** At every measured temperature the likelihood evaluates, the LP is
solved. Gurobi `infeasible` → the parameter set has zero likelihood: it cannot describe an
organism measured growing and respiring there. This is the limit of the existing log-scale term,
not a penalty and not an ε substitution. Feasible-but-not-growing states are unchanged — the clamp
scores their real maintenance respiration. `UNRESOLVED` (a numerically failed solve) is a distinct
category: it triggers the registered retry ladder, and a point that fails every retry is reported
as unresolved, never as −∞ and never as zero.

**The cost of −∞, and how it is handled.** ~96 % of the prior at −∞ means ~20,000 prior draws to
seat 800 finite live points. **Short-circuit**: solve temperatures in a registered order, return −∞
at the first infeasibility, so a dead draw costs one solve. **Measure** the prior rejection rate as a
reported number — it is item 1.33's finding. Efficiency recovers after the first bound update.

**This is D NLDM, and that is deliberate.** Every instrument here is calibrated on that fit, so a
pass attributes the fix to the likelihood revision alone. **M9 is the first scientific run and comes
next (T3)**, after the tie-break instrument is run on M9, which P10 never did.

**Limits that survive into every summary:** dTm = 0 assumes the meltome mean is exact; D44/D45
concern one point; the 80–87 % toy fractions and the prior-rejection fraction are findings, not
targets.

NOTE TO USER: launch in an auto-approving mode. The session does TASKs 0–3 (a few hours), writes
and launches the detached driver in TASK 4, and **stops**. The driver then runs the five seeds
unattended — about 1–2 days, checkpointing every 30 minutes, auditing each run, halting itself on
any failure. When it has finished (or when your limits refresh), **start a new session with this
same prompt**; the resumption block at the top routes it to the right place. Keep the machine
awake and the Gurobi WLS credentials in the environment the driver inherits.

---

```
Work AUTONOMOUSLY; commit in parts, prefixed "T2: "; maintain reports/T2_validated_posterior/
DECISIONS.md FROM THE FIRST JUDGEMENT CALL and follow docs/RIGOUR.md in every task. Check exit
codes explicitly, never `cmd && check`. Branch from main after the merge; do not push to main;
end in a PR that is NOT merged. Every expensive step has an enforced alarm; one expensive job at
a time. Reserved seeds 17901-17905 are used ONLY by the driver, once each.

STATE FILE, used by every task: reports/T2_validated_posterior/status.json, written atomically
(temp file + rename), committed with the task. Fields at minimum: stage (one of task0_done,
task1_done, task2_done, task3_done, driver_running, driver_finished, driver_stopped,
task5_done, task6_done), timestamp, branch, head, runs_complete (0-5), runs_audited (0-5),
driver_pid or null, last_note. Resumption reads it first.

TASK 0 - merge T1, record the decisions, pre-register everything  [skip if stage >= task0_done]
- Merge PR #40 server-side, reading its baseRefName first. Confirm MERGED; switch; pull; branch.
  Gates 79/79 and 60/60 with all options OFF as the baseline.
- D0, committed ALONE before anything else runs: the four decisions verbatim with their
  OPEN_ITEMS numbers; the (d) amendment; the registered short-circuit temperature order (coldest
  measured first is the obvious choice - T1 found 15 C is where D44 fails - register what you
  use); the retry ladder for UNRESOLVED with its alarm; the audit set (T1's 876 points) and the
  1e-6 tolerance; seeds 17901-17905 assigned to runs 1-5; per-run alarm 16 h; checkpoint 30 min;
  every protocol threshold quoted with its calibration source.
- docs/VALIDATION_PROTOCOL_DRAFT.md -> docs/VALIDATION_PROTOCOL.md: (d) restated; PI signature
  line dated; thresholds non-DRAFT. Own commit. Frozen from here.
- Write status.json stage task0_done. Commit.

TASK 1 - implement the two approved options and gate them  [skip if stage >= task1_done]
- `remove_inactive: ["f_metab"]` ON for eciML1515. Nothing else in that config changes.
- Infeasibility as a core option, e.g. `respiration.infeasible: exempt | zero_lik`, default
  `exempt`, ON as `zero_lik` for eciML1515 only. In the likelihood, per measured temperature in
  the registered order: status `infeasible` -> return -inf for the parameter set immediately;
  non-optimal non-infeasible -> the retry ladder; still unresolved -> an explicit UNRESOLVED
  result the runner records and never converts to a number. Feasible states scored as before.
- Seven-strain gate with BOTH options OFF: 79/79 and 60/60, byte-identical.
- Both ON for eciML1515: P3 gate. Growth R2 at Parsa's theta unchanged; D respiration R2 at his
  theta unchanged (verify his theta is feasible everywhere). Dated line in reports/P3_gate/README.md.
- status.json task1_done. Commit.

TASK 2 - re-verify T1's instruments under the new likelihood  [skip if stage >= task2_done]
- The invariant at all 876 audit points: identical to 1e-6 at every FEASIBLE point; -inf at every
  point T1 classified STRUCTURAL_ZERO at any temperature. Counts per class, maximum feasible
  difference. STOP on any feasible point that moved or any infeasible point not at -inf.
- The datum-by-datum table for T1's 13 points under zero_lik: the seven stratum/D44 rows total
  -inf with every positive measurement accounted for; the six feasible P12 rows unchanged to 1e-9.
- Short-circuit: 50 registered prior draws, solves per draw with and without; identical verdicts.
- Prior rejection rate: 2,000 registered prior draws, fraction returning -inf, binomial interval,
  and the temperature at which rejection most often fires. This is 1.33's number.
- status.json task2_done. Commit.

TASK 3 - the diagnostic coordinates and the driver, tested but NOT launched  [skip if >= task3_done]
- Validation configuration (not production): append an inactive coordinate with f_metab's
  original prior (check a) and a Beta(3,1) coordinate (check b). Prove neither enters the model,
  feasibility or likelihood: 100 evaluations at registered points, log L unchanged to 1e-12.
  Record both configuration hashes.
- Write the batch driver, reports/T2_validated_posterior/run_protocol.py, with these properties:
    * IDEMPOTENT: on start it reads status.json and each run's own status file; a run marked
      complete-and-audited is skipped; a run with a checkpoint but no completion is RESUMED from
      that checkpoint (dynesty restore, P11-proven); a run with neither starts fresh.
    * SEQUENTIAL: seeds 17901-17905 in order, one at a time, 16 processes each.
    * SELF-AUDITING: after each run completes, it runs the independent hash audit (P16's
      audit_completed_runs.py pattern: restored arrays match saved, weights sum to one, ESS
      reproduces, unit-cube positions match the inverse CDF) and writes the verdict.
    * SELF-STOPPING: an audit FAIL, a run hitting its 16 h alarm, or a crash -> write
      stage driver_stopped with the reason and the run number, and EXIT. Do not start the next
      seed. Do not change any setting.
    * CHECKPOINTED: every 30 min per run; status.json updated after every checkpoint with
      runs_complete, current run, iteration, dlogz, wall, and the unit-cube draw count.
    * DETACHABLE: writes driver.pid on start, removes it on exit; logs to driver.log with a
      progress line every 250 iterations; inherits the Gurobi WLS environment (assert the licence
      variables are present before the first solve and exit with a clear message if not).
    * ALARMED: SIGALRM per run at 16 h, and a whole-driver ceiling of 72 h.
    * On all five complete and audited: stage driver_finished; exit 0.
  The driver does NOT judge the protocol checks (TASK 5 does, in a session, against the frozen
  thresholds) - it only runs, checkpoints, audits reproducibility, and stops on failure.
- DRY RUN: launch the driver against a registered toy target (P17's smooth analytical target,
  nlive 100, two seeds) in the foreground, ~5 min, and confirm: both runs complete, both audits
  pass, status.json is written at every stage, and a kill-and-relaunch mid-run resumes from the
  checkpoint rather than restarting. Report each. STOP if any fails - a driver that cannot resume
  must not be left unattended.
- Write launch_status.md in P17's form: how to check the driver, how to relaunch it, what NOT to
  do (no duplicate launches, no setting changes, no touching run directories), and the
  resumption route for the next session.
- status.json task3_done. Commit.

TASK 4 - launch the driver, detached, and STOP THIS SESSION  [skip if stage >= driver_running]
- `nohup ../etcGEMs-venv/bin/python reports/T2_validated_posterior/run_protocol.py
   > reports/T2_validated_posterior/driver.log 2>&1 &` (or the equivalent via `setsid`/`disown`
  that survives this terminal), from the project root, with the WLS environment exported.
- Wait 10 minutes. Confirm: driver.pid exists and the process is alive; driver.log shows the
  first seed in its unit-cube phase with draws accumulating; status.json shows stage
  driver_running with driver_pid set. If any of these is false, kill the driver, diagnose, fix,
  and relaunch - but do NOT proceed to leave it unattended until all three are true.
- Write D-entry: launched at <time>, pid, expected completion range from P16's rates (note that
  -inf should shorten runs; the first run measures it), and the exact resumption instruction.
- Commit status.json and launch_status.md. Then END THE SESSION'S WORK with a short summary:
  driver launched, where to look, when to come back. Do not wait for the driver. Do not poll it
  beyond the 10-minute check.

  [After run 1 completes - the DRIVER does this, not the session]: append to DECISIONS.md, via
  the driver, a projection for runs 2-5 from run 1's measured wall-clock, unit-cube draws and
  iteration count, before starting run 2. The next session reads it.

TASK 5 - judge against the signed protocol  [on resumption, when stage is driver_finished or
driver_stopped]
- If driver_stopped: read the reason. Audit FAIL, alarm or crash -> diagnose (a crash gets P15's
  live-point covariance treatment), name the blocker, R1 stays open, go to TASK 6 with that
  verdict. Do not relaunch to "try again".
- If driver_finished: re-verify each of the five audits independently in this session (the
  driver's verdicts are inputs, not conclusions). Then each protocol check with its frozen
  threshold, per run and pooled:
    (a) inactive-coordinate CDF against its exact prior;
    (b) Beta(3,1) recovery on b^3 with the wrong-Uniform contrast;
    (c) consistency of the fifteen physical marginals AND leading eigen-directions across seeds;
    (d) AMENDED: prior-rejection fraction per run against TASK 2's measurement and interval;
    (e) feasibility-aware posterior predictive checks at every measured temperature, growth and
        O2 bands from weighted samples against the data, and the unresolved-evaluation rate;
    (f) log Z per run with error; final-live-point reconstruction; independent hash audit.
  PASS/FAIL against frozen thresholds. R1 CLOSED only if every check passes on every run. Any
  FAIL: R1 open, blocker named, no posterior quoted. No threshold revisited.
- If R1 CLOSED: the posterior as the protocol prescribes - MAP, weighted predictive bands, the
  eigendecomposition with directions labelled, the fifteen marginals with the correlated-
  parameters caveat, NEVER the componentwise median; the living fraction (expected ~100 % by
  construction, stated as such, not a target); the tail position (Y3's invariant) with tm_scale
  as its summary.
- status.json task5_done. Commit.

TASK 6 - record and reconcile  [after TASK 5]
- reports/T2_validated_posterior/report.md: decisions executed; gates; instruments; the prior
  rejection rate; the driver's five runs with audits and the run-1 projection against actuals;
  the six checks; the verdict; the posterior if earned.
- docs/OPEN_ITEMS.md: 1.29-1.32 closed; 1.33 opened with TASK 2's number and firing temperature;
  R1 in 0a closed or restated; 0b restated - if R1 closed: T3 is D on M9 (tie-break check first),
  then E/F on M9, then the three-evidence comparison; 1.17 re-costed from the driver's measured
  rates. Section 4: add "long runs go in a detached, idempotent, self-auditing driver; the session
  launches and leaves; resumption reads status.json first".
- evidence.csv rows; synthesis README note; 0c/RIGOUR reconciliation (a validated D NLDM
  posterior licenses nothing about E, F, M9 or another organism); stamps; PR opened, NOT merged.
- status.json task6_done. Commit.

VERIFY (report all, per session - a resumed session reports the tasks it ran)
0. Resumption: what status.json said on start; what was skipped; driver alive/dead/finished.
1. TASK 0: #40 merged with base read; D0 alone; protocol signed and frozen with (d) amended.
2. TASK 1: options and defaults; gates OFF; P3 gate unchanged; README line.
3. TASK 2: invariant by class with max feasible difference; datum table under zero_lik;
   short-circuit saving; prior rejection rate with interval and firing temperature.
4. TASK 3: diagnostics inert to 1e-12 with config hashes; the driver's dry run - two toy runs,
   two audits, kill-and-resume proven; launch_status.md.
5. TASK 4: launch time, pid, the 10-minute check, the D-entry, the session ended.
6. TASK 5: per run - seed, iterations, evaluations, unit-cube draws and duration, wall, log Z,
   ESS, audit re-verified; the six checks PASS/FAIL; verdict; posterior report if closed.
7. TASK 6: OPEN_ITEMS; evidence rows; reconciliation; stamps; PR unmerged.
8. `git diff main --stat`: src/etcgem (one option), eciML1515 config, a validation config,
   reports/T2_validated_posterior/ including the driver and status files, VALIDATION_PROTOCOL.md,
   P3_gate README, OPEN_ITEMS, evidence.csv, synthesis README, stamps, five run outputs.

CONSTRAINTS
- The resumption block is read first on every start. A completed stage is never redone. A
  running driver is never relaunched or touched.
- The driver is idempotent, sequential, self-auditing, self-stopping, checkpointed, alarmed. It
  is not left unattended until the dry run has proven kill-and-resume.
- The spec, the signed protocol and RIGOUR.md govern. -inf is the limit of the existing term.
  UNRESOLVED is never a number. No threshold revisited. No sampler change in response to a
  result. Reserved seeds used once each, by the driver only.
- The componentwise median is never a posterior summary. A validated D NLDM posterior licenses
  nothing beyond D NLDM.
- Autonomous; commit in parts, each task ending with its status.json.
```
