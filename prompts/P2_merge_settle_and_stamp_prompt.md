# Claude Code prompt — P2: merge P1, settle what can be settled without Parsa's data, and put a provenance stamp on every report (autonomous)

Run from the project root (`.../MICROADAPT/etcGEMs`). Follows P1
(https://github.com/GabYvonDurocher/etcGEMs/pull/4, branch `p1/parsa-configs`).

**What is blocked and what is not.** Parsa's E. coli respirometry
(`Presense_Analysis/Ecoli_R2A_LB`) exists only on his machine and has been requested. Configs D, E
and F cannot be validated against experiment until it arrives. Everything else can proceed, and this
prompt does it: merge P1 with D/E/F clearly marked ungated; settle the two questions that can be
settled by experiment rather than by asking; and stamp every report with the model state it
describes, which is the standing fix for a failure this project has now hit three times in three
codebases.

NOTE TO USER: launch in an auto-approving mode. No emcee, no calibration, no overnight run. TASK 0
needs network and credentials. The rest is local and cheap.

Standing rules carry over: decide and proceed when reversible or precedented; stop the task and
record when it would change a committed number, need a scientific judgement, or write inside
`$CANDIDAS_ROOT` or `$PARSA_ROOT` (both READ ONLY). Never weaken a test; never edit a number to make
it match. Keep `reports/P2_settle/DECISIONS.md` from the first judgement call. TASK 0 is the only
write to `main`; TASKS 1-5 are branch work on `p2/settle-and-stamp` and end in a PR that is NOT
merged.

REFERENCE, read first: `reports/P1_parsa_port/gate.md` and `DECISIONS.md`,
`reports/N3_output_audit/report.md` (the eleven-directory audit), `reports/N1_overnight/DECISIONS.md`
(D8, D11), and `docs/CANDIDA_DISCUSSION_2026-09-07.md` §4.

---

```
Work AUTONOMOUSLY; commit per task, prefixed "P2 TASK n: "; maintain reports/P2_settle/DECISIONS.md.
Print a final summary with each task DONE / PARTIAL / STOPPED.

TASK 0 - merge P1, with D/E/F marked ungated
- Working tree clean, `main` current with origin, else STOP.
- `git diff main...p1/parsa-configs --stat`; confirm P1's claims: no E. coli identifier or measured
  value in the new core modules, nothing imported from $PARSA_ROOT/strains/eciML1515/outputs, all
  seven existing strains byte-identical.
- Merge --no-ff: "Merge P1: Parsa's gas-flux and overflow configs — mechanisms into the core, E. coli
  specifics into the strain folder"
- Verify: Candida gate 79/79 with $CANDIDAS_ROOT UNSET; all seven strains byte-identical; exit codes
  checked explicitly, NOT chained with `&&` (the cli exit-code defect N3 found made exactly that
  check vacuous once already).
- Before pushing, make the ungated status impossible to miss: in reports/ecoli_gasflux/ (or wherever
  P1 put the config report) state at the TOP that Configs D, E and F are ported but NOT validated
  against experiment, name the missing file and its origin, and say what will be run when it lands.
  A reader must not be able to mistake ported for verified.
- Push; close PR #4 as merged; delete the branch.
- If verification fails, stop and report; do not proceed.

TASK 1 - settle the transporter kcat by experiment, not by asking (question 3 to Parsa)
His `gasflux.py` says 30 s^-1; his figure, its filename and his report say 300.
- Run the relevant config at BOTH values and compare against his committed figure/output in
  $PARSA_ROOT (read only). Report which reproduces it.
- Set the value that reproduces his figure, in the E. coli strain data (NOT in core code), with a
  comment recording the discrepancy, which value was tested, and how it was settled.
- If NEITHER reproduces his figure, that is a finding: report it and set nothing.
- Record in DECISIONS.md as provisional pending his confirmation.

TASK 2 - the NLDM medium: regenerate under recipe ceilings (question 2 to Parsa)
P1 established that his committed NLDM CSV used a blanket medium, his later code uses recipe
ceilings, and he never re-ran — his CSV is dated 1 Sep, the script supplying its build_pm 4 Sep.
- Take RECIPE CEILINGS as canonical (the more careful construction; his CSV predates it).
- Regenerate the NLDM quantities under recipe and report every number that moves, with magnitudes.
  His 1.2% discrepancy should be explained by this and nothing else — if a residual remains after
  the medium is accounted for, STOP and report it.
- Keep the blanket-medium result as a labelled sensitivity, not as the baseline.
- Record as provisional pending his confirmation.

TASK 3 - c_max provenance: establish what can be established (question 1 to Parsa)
This is the one that changes a scientific claim, and only Parsa can give the intent. But the
EVIDENCE can be gathered now.
- Search $PARSA_ROOT (read only) — scripts, configs, reports, logs, commit-free though it is — for
  any justification of c_max = 60: a literature citation, a fit, a sweep it fell out of, a
  round-number choice. Report what you find and what you do not.
- Run the sensitivity properly and tabulate it: over a range of c_max spanning weak to strongly
  binding, report T_opt, CT_max, E_a, rmax, acetate flux, O2, CO2 and RQ. Include c_max = 60.
- State plainly at which c_max the thermal descriptors begin to move, and by how much. The
  question a reader needs answered is whether 60 sits in a flat region or on a slope.
- Do NOT change c_max. Do NOT conclude whether it is fitted. Gather and report.

TASK 4 - provenance stamps on every report
Three instances of stale-at-commit in three codebases by three people. The fix is not recomputation,
it is that every report says which model state it describes.
- Define ONE stamp format and apply it to every report directory under reports/: the commit the
  report describes, its date, the commit each input directory was last written at, and a one-line
  status — CURRENT (reproduces from present code) or HISTORICAL (a record of an earlier state).
  Generate it programmatically; a script that regenerates the stamp is worth more than a hand-written
  block.
- Use N3's audit table for reports/ecoli_tpc/ rather than recomputing it.
- Where a report is HISTORICAL, that is not a defect and must not be phrased as one. These are
  working logs. The defect was only ever that they did not say so.
- Add the convention to README.md in two or three sentences, so the next report is stamped at birth.

TASK 5 - the three annotations N3 and P1 left owed, in the files a reader reaches
Each is a note, not a re-run. All three currently live only in decision logs.
- `control_tuned` was regenerated for the O2-sink closure while `decompose_tuned` and
  `elasticity_tuned` were not, so the report presents one dissection built from two model states.
  Put that in reports/ecoli_tpc/ where the dissection is discussed. State the cost of fixing it
  (re-running the two) and that it is deferred until the material is used.
- The 37-44 C shoulder: the Glucose proteome ends at 37 C, so growth is bit-identical across eight
  temperatures — the model is answering the same question eight times. A genuine limitation; record
  it where the E. coli TPC is presented, and note that N1's flatness guard cannot see it because the
  shoulder sits below the maximum rather than around it.
- T_opt is regime-determined: three separate constraints (the sector re-grounding a416fd1, the
  translation cap, and now Parsa's carbon cap) each relocate it, while CT_max has been insensitive
  to all three. Add ONE sentence to reports/ecoli_tpc/ noting that the phi_envelope = 0.999
  attribution for T_opt holds only within a fixed constraint regime, and record the general rule in
  docs/: T_opt is quoted with its binding constraint named; CT_max may be quoted plainly.
- Do NOT re-run the decomposition. Do NOT restate it. One sentence each.

FINALLY
- reports/P2_settle/SUMMARY.md; push the branch; open a PR against main; do NOT merge.

VERIFY (report all)
1. TASK 0: merge commit; gate 79/79 with $CANDIDAS_ROOT unset, exit codes checked not chained; seven
   strains byte-identical; the ungated notice, quoted; PR #4 closed.
2. TASK 1: which kcat reproduces his figure; what was set and where; or that neither did.
3. TASK 2: every NLDM number that moves under recipe ceilings; confirmation the 1.2% is fully
   explained, or the residual.
4. TASK 3: what justification for c_max = 60 exists in his folder; the sensitivity table; the c_max
   at which thermal descriptors start to move.
5. TASK 4: the stamp format; every report stamped; the regeneration script; the README convention.
6. TASK 5: the three annotations, each quoted with its file.
7. DECISIONS.md, marking TASKS 1 and 2 provisional pending Parsa.
8. `git diff main --stat` for the branch; no committed output regenerated except the NLDM
   quantities; no scientific conclusion altered.

CONSTRAINTS
- Nothing here needs Parsa's data. If a task turns out to, stop it and say so.
- TASKS 1 and 2 are provisional: they set a value on evidence, pending his confirmation. Mark them.
- TASK 3 gathers and reports. It does not decide whether c_max is fitted.
- HISTORICAL is not a criticism. These reports are logs and the stamp says so neutrally.
- Never verify with `cmd && check`. Check exit codes explicitly.
- Autonomous; commit per task. TASK 0 is a merge commit on `main`; TASKS 1-5 commit to
  `p2/settle-and-stamp`.
```
