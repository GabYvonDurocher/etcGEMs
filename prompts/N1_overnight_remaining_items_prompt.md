# Claude Code prompt — N1: the remaining items after K1/K2/A1, run unattended overnight, with the freedom to decide and the obligation to say where you did (autonomous)

Run from the project root (`.../MICROADAPT/etcGEMs`). Seven tasks left over from the Candida merge
(K1, K2, A1 — all merged; `main` at 295cedc). They are independent, so a partial night is still a
useful night. They are ORDERED so that the cheapest and safest work lands first.

NOTE TO USER: launch in an auto-approving mode and leave it. It runs no predictors and downloads no
new data. Expect a few hours.

## Standing rules for the night

You will hit questions this prompt does not answer. That is expected. The rule is:

**DECIDE AND PROCEED** when the choice is reversible, is confined to new files, or has a clear
precedent already in this repository. Record it.

**STOP THE TASK AND RECORD** — then move to the next task, do not abandon the night — when the
choice would: change a committed result or a number anyone has quoted; alter a strain other than the
Candida four; require data you do not have; need a scientific judgement about what is true rather
than about how to implement something; or write anywhere inside `$CANDIDAS_ROOT`.

**NEVER**, whatever the reasoning: push to `main`; push anything to the Candidas remote; delete
committed evidence; weaken a test so it passes; or edit a number in a report to match a new result.

Keep `reports/N1_overnight/DECISIONS.md` from the first decision onward. One entry per judgement
call: what was decided, why, what the alternatives were, whether it is reversible, and who should
look at it. A decision recorded is a decision I can undo; a decision made silently is a bug I will
find in three weeks. Err heavily toward recording — an over-long log is the correct failure mode.

Work on branch `n1/overnight`. Commit after each task with the task name in the message so a partial
night is easy to read.

REFERENCE, read first: `docs/CANDIDA_DISCUSSION_2026-09-07.md` (§2, §5, §6b, §8, §9),
`reports/candida_thermal_limit/K2_core_thermal_form.md`, `reports/predictor_calibration/report.md`.

---

```
Work AUTONOMOUSLY through the tasks in order. Commit after each. Maintain
reports/N1_overnight/DECISIONS.md throughout. If a task stops, say so, record why, and start the
next one. Print a final summary listing every task as DONE / PARTIAL / STOPPED with one line each.

TASK 1 - A3: the gene-content screen  (safe; read-only inputs; nobody has done this)
Presence/absence of metabolic genes is a genuine species difference that needs no new data and no
predictor. Two levels, and they answer different questions:
  (a) PROTEOME level. From $CANDIDAS_ROOT/phylo/proteomes/*.faa (READ ONLY), establish orthology
      across C. auris (use Clade I), C. haemulonii, C. duobushaemulonii and C. parapsilosis. Report
      genes present in C. auris and absent in each relative, and vice versa. Give counts and the
      lists.
  (b) MODEL level. Which of those made it into each metabolic model at all. NOTE THE TRAP, from K1:
      the two draft models are the C. auris network with genes reassigned by RBH (2,863 reactions
      and ~1,312 costed in all three, differing by 2-4), so model-level gene content is nearly
      identical BY CONSTRUCTION for those two. Say so plainly; do not report construction as
      biology. Only C. parapsilosis (independently curated, 2,162 reactions) can differ genuinely.
- Check the Xiao et al. 2025 candidates explicitly by name: alternative oxidase (AOX), GRX5, and the
  iron-uptake genes. Present or absent, per species, at both levels.
- Annotate what you can from KEGG/KO terms already in the repository. Do NOT fetch new annotations.
- Write reports/N1_overnight/A3_gene_content.md: method, counts, the candidate table, and an
  explicit statement of what presence/absence can and cannot support. Do not adjudicate mechanism.

TASK 2 - make the gate self-contained  (safe; blocks K3 until done)
`reports/candida_thermal_limit/gate_table.py` needs $CANDIDAS_ROOT present, so it stops working the
moment the fork is archived, and cannot run on any machine without Ilgaz's repository.
- Freeze the standalone's expected values into a committed fixture (JSON or CSV) under
  reports/candida_thermal_limit/, generated FROM the current standalone, with its Candidas commit
  hash recorded inside the file.
- Make the gate read the fixture by default and keep --candidas-root as an optional path that
  regenerates the fixture and reports any drift.
- Verify: gate passes 79/79 from the fixture alone with $CANDIDAS_ROOT unset. Report both runs.

TASK 3 - the pool-row conditioning  (moderate; K2 already established the fix works)
K2 found the pool constraint row spans 8.2e8 at 22 C, causing a ~0.4% GLPK error at the cold end of
the draft models, and that rescaling to a mathematically identical well-conditioned LP makes GLPK
agree with Gurobi.
- Implement the rescaling in src/etcgem, behind an explicit option, DEFAULT OFF.
- THE TENSION YOU MUST NOT PAPER OVER: the gate reproduces the standalone exactly, INCLUDING the
  0.4% error its solver made. A better-conditioned port will not reproduce that error, so it cannot
  pass the current gate on those points. Do not fix this by loosening the gate. Instead: keep the
  default OFF so the gate is unaffected, add a separate run demonstrating the rescaled result, and
  write up the choice — that fidelity to the standalone and numerical correctness are now different
  configurations, and which should eventually be canonical is a decision for a human. Record it in
  DECISIONS.md as needing review.
- Report: the condition number before and after, per strain; which quantities move and by how much;
  and confirmation that with the option OFF every committed output is byte-identical.

TASK 4 - the sector translation cap  (moderate; diagnose and guard, do NOT change behaviour)
K2 rung B4 found that with sectors on and literature (non-temperature-dependent) allocation, the
translation cap removes the optimum rather than shifting it: the curve goes flat, T_opt becomes the
argmax of a tie, and fit fell 0.254 -> 0.111.
- FIRST establish the hypothesis in the discussion notes (§6b): does E. coli escape this only
  because `allocation_from_data` makes its cap temperature-dependent? Test it by running eciML1515
  with allocation_from_data disabled and sectors on, and reporting whether its curve also flattens.
  This is a diagnostic run into a NEW output directory; it must not touch eciML1515's committed
  outputs.
- Then implement a GUARD, not a modelling change: when sectors are enabled without
  temperature-dependent allocation, emit a clear warning naming the flattening risk, and record the
  flatness of the resulting curve (e.g. the width of the region within 1% of the maximum) in the
  run's outputs so it cannot pass unnoticed.
- Do NOT make the translation cap temperature-dependent. That is a modelling decision with
  literature implications for every strain, and it needs a human. Write what you would propose, with
  the reasoning, in the report.

TASK 5 - repository consistency  (safe housekeeping; small)
- `outputs/tpc/` is committed for eciML1515 (4 files) and untracked for mmaripaludis and syn6803.
  Decide one rule, apply it to all seven strains, document it in README.md, and record the decision.
  Either is defensible; inconsistency is not.
- Check whether reports/candida_thermal_limit/gate_table.csv is tracked or ignored, and make it
  deliberate either way.
- Look for other instances of the same inconsistency across strains (which outputs are canonical and
  committed versus scratch) and either fix or list them.

TASK 6 - K3 groundwork, PREPARED BUT NOT PUSHED  (do not write to $CANDIDAS_ROOT)
The fork retires once the framework carries everything. Do the etcGEMs-side work only:
- Confirm nothing in this repository still needs $CANDIDAS_ROOT at run time once TASK 2 is done.
  List anything that does.
- Write reports/N1_overnight/K3_readiness.md: exactly what would have to change in the Candidas
  repository (archive gem/ to archive/gem_standalone/ with a README pointing here; whatever else you
  find), what would break, and what could not be moved.
- Draft the Candidas-side commits as a PATCH FILE under reports/N1_overnight/, not applied. Do not
  clone, branch, modify or push anything in $CANDIDAS_ROOT. Read only.

TASK 7 - the message to Ilgaz  (draft only)
Draft reports/N1_overnight/message_to_ilgaz.md, plain text, pasteable, covering: the
`15_run_seq2tm.py` truncation bug (truncates at 1022 aa citing an ESM-2 positional limit that does
not exist; the committed predictions are untruncated, so the script does not reproduce the data
beside it; up to 2.6 C on affected batches) — this is the urgent one; the reversible
`ATP_Maintenance__cyto` in iDC1003 and that uncorrected, C. parapsilosis is unreachable by any Tm
shift with R^2 = -0.323; that 0.52 C is the superseded reaction-level value and 0.411 is the
project's own deduplicated one; and the two open questions for him (the common_network.py result,
which is not recorded anywhere; and whether any audit touched lipid or membrane pathways).
Even-handed in tone: these are findings from porting good work, not a list of faults.

FINALLY
- reports/N1_overnight/SUMMARY.md: each task DONE/PARTIAL/STOPPED with one line, then the decision
  log in full, then what needs a human and why.
- Push the branch. Open a PR against main if gh is available; otherwise print the URL and body.
- Do NOT merge.

VERIFY (report all)
1. Per task: status, what was produced, what was decided.
2. TASK 2: gate 79/79 from the fixture with $CANDIDAS_ROOT unset.
3. TASK 3: conditioning numbers; confirmation the default-OFF path leaves every committed output
   byte-identical.
4. TASK 4: whether eciML1515 also flattens without allocation_from_data; the guard; the proposal.
5. TASK 5: the rule chosen and applied to all seven strains.
6. TASK 6: the readiness note and the unapplied patch; confirmation $CANDIDAS_ROOT is unmodified
   (`git status` there is clean).
7. TASK 7: the draft exists.
8. DECISIONS.md: every judgement call, with reversibility and who should review.
9. `git diff main --stat`, and confirmation that no existing strain's committed outputs changed.

CONSTRAINTS
- The standing rules above outrank any individual task. When they conflict, stop the task and record.
- A partial night is a success. A night that silently changed something is not.
- Do not adjudicate scientific mechanism anywhere in this prompt's outputs. Report numbers, state
  what they support, and leave interpretation to the humans.
- Autonomous; commit per task, prefixed "N1 TASK n: ".
```
