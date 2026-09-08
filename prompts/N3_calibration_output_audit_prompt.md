# Claude Code prompt — N3: merge N2, then audit the committed outputs the E. coli report actually renders from — and test whether the old T_opt was a translation-cap artefact (autonomous)

Run from the project root (`.../MICROADAPT/etcGEMs`). Follows N2
(https://github.com/GabYvonDurocher/etcGEMs/pull/2, branch `n2/followups`). TASK 0 merges it.

**Why this exists.** N2 found that `strains/eciML1515/outputs/tpc/descriptors.json` was stale *at the
moment it was committed* — `c6a20ad` produced Topt 31.0 / rmax 0.5429 while committing 37.0 / 0.3413.
That was harmless because no report reads `outputs/tpc`. But it establishes that this repository can
commit an output its own code does not produce, and **`reports/ecoli_tpc/assemble.py` renders the
E. coli paper from other committed output directories entirely** — `sweep_default`,
`calibration_vanderlinden`, `validation`, `decompose_tuned`, `elasticity_tuned`, `control_tuned`,
`proteome_sectors`, `anatomy` and the `ablation_*` trees. N2 explicitly did not check those. The same
failure there would put stale numbers in a paper.

This prompt does NOT re-run emcee or the dissections. It establishes, cheaply and by evidence,
whether each of those directories is consistent with the code and the commit that wrote it, and
escalates only what looks wrong.

NOTE TO USER: launch in an auto-approving mode. TASK 0 needs network and credentials. TASKS 1-2 are
local and mostly cheap; TASK 3 re-runs a small number of things and will say before it does. If a
full recomputation turns out to be the only way to settle something, it STOPS and asks rather than
spending the night on emcee.

Standing rules from N1/N2 carry over: decide and proceed when reversible or precedented; stop the
task and record when it would change a committed number, need a scientific judgement, or write
inside `$CANDIDAS_ROOT` (READ ONLY). Never weaken a test; never edit a number to match a result. Keep
`reports/N3_output_audit/DECISIONS.md` from the first judgement call. TASK 0 is the only write to
`main`; TASKS 1-4 are branch work on `n3/output-audit` and end in a PR that is NOT merged.

REFERENCE, read first: `reports/N2_followups/SUMMARY.md` and `DECISIONS.md` (D5 especially),
`reports/N2_followups/` TASK 1's bisection, `reports/N1_overnight/TASK4_sector_cap.md`,
`reports/ecoli_tpc/assemble.py` (the authoritative list of what the report reads), and
`reports/ecoli_tpc/report.qmd` §"What sets each feature of the curve" (the φ_envelope = 0.999 claim
for T_opt that TASK 2 tests).

---

```
Work AUTONOMOUSLY; commit per task, prefixed "N3 TASK n: "; maintain reports/N3_output_audit/DECISIONS.md.
Print a final summary with each task DONE / PARTIAL / STOPPED.

TASK 0 - merge N2
- Working tree clean, `main` current with origin, else STOP.
- `git diff main...n2/followups --stat`; confirm against N2's claims that the only strain output
  changed is the regenerated strains/eciML1515/outputs/tpc/, and that $CANDIDAS_ROOT is untouched.
- `git switch main && git merge --no-ff n2/followups -m "Merge N2: eciML1515 TPC cause diagnosed and regenerated, conditioning default, flatness and coverage recorded"`
- Verify: gate 79/79 with $CANDIDAS_ROOT UNSET; mmaripaludis and syn6803 byte-identical; eciML1515
  outputs/tpc NOW reproduces (it was regenerated in N2 — this is the check that N2's fix took).
- Push; close PR #2 as merged; delete the branch locally and remotely.
- If verification fails, do not proceed. Report and stop.
- Housekeeping while you are here: N2 recorded 100644->100755 mode flips caused by the OneDrive
  checkout. Set `git config core.fileMode false` in this clone and note it in the report, so the
  noise stops. This is local config only, not a committed change.

TASK 1 - the audit: is every output the report reads consistent with the code that wrote it?
Cheap checks first. Do NOT re-run anything in this task.
- Read reports/ecoli_tpc/assemble.py and enumerate EVERY committed directory and file it reads. That
  list, not my summary above, is authoritative. Report it.
- For each such directory, establish and tabulate:
    * the commit that last wrote it, and its date;
    * whether a `resolved_config.yaml` is present, and whether that config is still VALID against
      the current code — i.e. every key it sets still exists and means the same thing. This is the
      check that caught `_toy` in N2: structurally stale while numerically fine.
    * whether any config key it sets has since changed DEFAULT or MEANING — pay particular attention
      to the a416fd1 change N2 identified (sector split re-grounded, f_metab 0.285 -> 0.483) and to
      anything touching allocation, the growth law, the translation cap, pool reconciliation or the
      O2-sink closure;
    * whether the directory predates a416fd1. Anything written before it is under suspicion for the
      same reason outputs/tpc was.
- Classify each directory: CONSISTENT / STRUCTURALLY STALE (config keys drifted, numbers may be
  fine) / SUSPECT (predates a change that would move its numbers) / UNKNOWN (cannot tell cheaply).
- Report the table. Do not fix anything in this task.

TASK 2 - the cap-regime hypothesis, and what it means for the decomposition
N2's bisection showed T_opt moving 37 -> 30 C when f_metab went 0.285 -> 0.483, described as "pool
budget +70%, ribosome cap out of the way", with the envelope unmoved. The report meanwhile states
T_opt has phi_envelope = 0.999 — essentially all stability, magnitude contributing nothing. Both
cannot be casually true. The hypothesis to test: before a416fd1 the translation cap was BINDING, so
the old T_opt of 37 C was a cap-limited plateau edge — the same artefact N1's guard found in Candida
B4 — and phi_envelope = 0.999 holds only within the cap-free regime.
- Test it directly: run N1's flatness metric on the pre-a416fd1 state (scratch worktree, as N2 did
  for the bisection) and on the current state. Report the plateau width for each.
- Report whether the translation cap binds at T_opt in each state.
- If the hypothesis holds: this is a REGIME CHANGE that a local decomposition around one operating
  point with +-20% perturbations cannot see, and it means N1's flatness guard has caught a pathology
  that affected the reference strain historically, not only Candida. Say exactly that, in
  reports/N3_output_audit/, and add a caveat sentence to reports/ecoli_tpc/report.qmd noting that the
  phi_envelope = 0.999 attribution for T_opt is conditional on the cap not binding. Do NOT restate or
  recompute the decomposition.
- If it does not hold: say so plainly and give the alternative explanation for the 7 C shift, or
  record it as unresolved. Do not force the hypothesis.

TASK 3 - escalate only what TASK 1 flagged, and only cheaply
- For anything classified SUSPECT or UNKNOWN, find the cheapest test that would settle it. Often
  that is re-running one deterministic stage (a sweep summary, an ablation, proteome_sectors,
  anatomy) rather than a calibration.
- Run only the cheap ones. Report, per directory: reproduces / does not reproduce / not cheaply
  testable, with the numbers where it does not reproduce.
- DO NOT re-run emcee calibrations or the dissections. If one of those is the only way to settle a
  SUSPECT directory, STOP, say which, estimate the cost, and leave it for a human. That decision is
  not yours to spend a night on.
- Do NOT regenerate anything. If an output is stale, it is LISTED with its evidence. N2's discipline
  applies: a regenerated file with an unexplained cause looks correct and is worse than a stale one.
  The one exception already taken (eciML1515 outputs/tpc) had its cause established first.

TASK 4 - record, and close the loop on D5
- reports/N3_output_audit/report.md: the TASK 1 table, the TASK 2 result, the TASK 3 outcomes, and a
  plain statement of what a reader of reports/ecoli_tpc/ should currently believe about the
  provenance of its numbers.
- Promote N2's D5 out of the decision log into documentation: `rescale_pool_row` auto-disables when
  sectors are on, so "default on" means default on WHERE IT WORKS — and the strains carrying sectors
  are arguably the most exposed to conditioning problems. Put this in README.md beside the two
  configurations, as a known limitation.
- If TASK 1 or TASK 3 found nothing wrong, say so as clearly as you would say the opposite. A clean
  audit is a result and must be reported as one, not buried.

VERIFY (report all)
1. TASK 0: merge commit; gate 79/79 with $CANDIDAS_ROOT unset; eciML1515 outputs/tpc now reproduces;
   mmaripaludis and syn6803 byte-identical; PR #2 closed; core.fileMode set.
2. TASK 1: the enumerated list from assemble.py; the classification table; which directories predate
   a416fd1.
3. TASK 2: plateau widths before and after; whether the cap binds at T_opt in each state; the verdict
   on the hypothesis; the caveat sentence added, or why not.
4. TASK 3: per-directory outcome; anything left for a human, with its cost.
5. TASK 4: the report; D5 promoted to README.
6. DECISIONS.md complete.
7. `git diff main --stat` for the branch; confirmation that no committed output was regenerated and
   no scientific conclusion altered.

CONSTRAINTS
- List, do not fix. The only thing this prompt changes is documentation and one caveat sentence.
- No emcee, no dissections, no overnight recomputation. Stop and ask instead.
- A clean result is reported as clearly as a dirty one.
- Autonomous; commit per task. TASK 0 produces a merge commit on `main`; TASKS 1-4 commit to
  `n3/output-audit`.
```
