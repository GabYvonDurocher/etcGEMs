# T2 driver — launch status and the resumption route

_Form follows `reports/P17_inactive_prior/launch_status.md`. Updated by the session at each stage;
the driver updates `status.json`, not this file._

## Where T2 lives — READ FIRST ON RESUMPTION

**T2 runs in the worktree `../etcGEMs-t2` on branch `t2/validated-posterior`, not in the primary
tree.** The primary tree's `.git/index.lock` is held stale by the sandbox VM's file server
(`com.apple.Virtualization`, pid 62662) and the task forbids deleting lock files; an untracked
`reports/T2_validated_posterior/status.json` with `stage: "REDIRECT"` sits in the primary tree to say
so. Everything below is relative to the worktree root.

```
cd ../etcGEMs-t2            # from the primary tree
cat reports/T2_validated_posterior/status.json
```

## How to check the driver

```
cat reports/T2_validated_posterior/status.json              # stage, current run, iteration, dlogz, wall, pid
cat reports/T2_validated_posterior/driver.pid && ps -p $(cat reports/T2_validated_posterior/driver.pid)
tail -5 reports/T2_validated_posterior/driver.log            # a progress line every 250 iterations
ls strains/eciML1515/outputs/calibration_configD_NLDM_recipe_T2_validated/   # run{k}_seed{seed}/
cat strains/eciML1515/outputs/calibration_configD_NLDM_recipe_T2_validated/run1_seed17901/run_status.json
```

`stage: driver_running` + pid alive → **leave it alone**; write the one-paragraph D-entry and stop the
session. `stage: driver_finished` → TASK 5. `stage: driver_stopped` → read `stopped_reason` and
`stopped_run`; TASK 5 diagnoses; **do not relaunch to "try again"**.

## How to relaunch (ONLY if the pid is dead, `runs_complete < 5`, and `driver.log` shows no STOP verdict)

The driver is idempotent: a run complete-and-audited is skipped; a run with `dynesty.save` but no
completion resumes from that checkpoint (P11/P15-proven restore); a run with neither starts fresh.

```
cd ../etcGEMs-t2
nohup ../etcGEMs-venv/bin/python reports/T2_validated_posterior/run_protocol.py \
    >> reports/T2_validated_posterior/driver.log 2>&1 &
sleep 600; cat reports/T2_validated_posterior/status.json; tail -3 reports/T2_validated_posterior/driver.log
```

The Gurobi WLS licence is read from `~/gurobi.lic` (or `$GRB_LICENSE_FILE`); the driver asserts it
before the first solve. Keep the machine awake.

## What NOT to do

- **No duplicate launch.** The driver refuses to start if `driver.pid` names a live process, but do
  not rely on it: check `ps` first.
- **No setting changes** — nlive, sampler, slices, dlogz, seeds, alarms, the strain config, the
  likelihood. A change is a different registration and voids the run.
- **No touching run directories** (`strains/eciML1515/outputs/calibration_configD_NLDM_recipe_T2_validated/`):
  no deleting checkpoints, no "cleaning", no re-running a seed. A reserved seed is used once.
- **No reading a posterior** before TASK 5's independent audit has re-verified every run.
- **No deleting `.git/index.lock` in the primary tree**; work in the worktree.

## Dry run (TASK 3) — what was proven before leaving it unattended

Toy target (P17 `controls.Target('smooth')`, 15-D): two seeds complete with passing audits and
`status_toy.json` written at every stage; a run killed by SIGTERM at iteration 1810 (stale
`driver.pid` left) resumed from its checkpoint on relaunch and finished **bit-identical** to an
uninterrupted run of the same seed (log Z, samples, logl, logwt). Details: DECISIONS D7;
outputs `dryrun/`.

## Stage log

| when | stage | note |
|---|---|---|
| 2026-09-13 21:44 | task0_done | gates OFF 79/79, 60/60; protocol frozen 9b91420 |
| 2026-09-13 21:56 | task1_done | options ON for eciML1515; gates OFF pass; P3 gate byte-identical |
| 2026-09-13 22:16 | task2_done | invariant 876/876 as predicted; rejection 16.45 % [14.9, 18.1] |
| 2026-09-13 22:42 | task3_done | diagnostics inert (exact); driver dry run + kill-and-resume proven |
| 2026-09-13 22:42 | driver_running | launched pid 83007; 10-min check passed 22:52 (run 1 it 252, draws accumulating); expected finish 2026-09-15 evening to 09-16 morning |
