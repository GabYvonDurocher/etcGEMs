# Handover — 16 September 2026

_This supersedes [HANDOVER_2026-09-13.md](HANDOVER_2026-09-13.md), which is kept and marked as
superseded. It is written for someone opening this repository cold, with no memory of any of it._

**In one sentence:** a merged, gated, seven-organism modelling framework with a likelihood that is
now scientifically correct, whose posterior is not yet reproducible for reasons that are diagnosed
and costed, plus a complete record of how that was established.

---

## 1. What this is and where it lives

**The framework.** Enzyme- and temperature-constrained genome-scale models (etcGEMs). A
genome-scale metabolic model is given a proteome budget; every enzyme's turnover and stability
carry a temperature dependence; the model then predicts growth and gas exchange as a function of
temperature, and those predictions are compared with measured thermal performance curves. One
shared core (`src/etcgem/`) drives **seven organism models** — `eciML1515` (*E. coli*),
`cauris_iRV973`, `chaemulonii_draft`, `cduobushaemulonii_draft`, `cparapsilosis_iDC1003` (the
Candida set), `mmaripaludis` and `syn6803` — each in `strains/<name>/` with its own data,
configuration and committed outputs.

**The two gates**, which are the repository's safety net. Both must pass on every change:

```sh
# from the repository root, with CANDIDAS_ROOT unset
V=../etcGEMs-venv/bin
unset CANDIDAS_ROOT
$V/python reports/candida_thermal_limit/gate_table.py   # expect: 79 comparisons, 79 PASS, 0 FAIL
$V/python reports/P1_parsa_port/gate.py                 # expect: 60 comparisons, 60 PASS, 0 FAIL
```

The first checks that this core reproduces a standalone Candida implementation exactly; the second
that it reproduces the *E. coli* gas-exchange port. Check the exit code explicitly — never
`cmd && check`, which has produced a false pass here before.

**The interpreter lives outside the checkout**, at `../etcGEMs-venv`, and is shared by every
worktree. Recreate it from `requirements.lock.txt`. A Gurobi WLS licence is needed for the
linear-programming work (`~/gurobi.lic`).

**Where main is.** `origin/main` at the commit this handover was merged in; `git log --oneline -5`
tells you the rest. A fresh clone contains everything in this document **except** the P17 archive.

**What you should find on disk: two folders.** `MICROADAPT/etcGEMs`, this repository, and
`MICROADAPT/etcGEMs-venv`, the Python environment every prompt and script refers to as
`../etcGEMs-venv/bin/python`. **Do not delete `../etcGEMs-venv`** — it is outside the checkout on
purpose (P7 moved it there so two worktrees could not fight over one interpreter) and it is
recreatable only by rebuilding from `requirements.lock.txt`. Anything else beside them is
temporary and is created on demand:

```sh
git worktree add ../etcGEMs-p17-archive codex/p17-inactive-prior   # to read the P17 archive
git worktree add --detach ../etcGEMs-work main                     # a second tree for parallel runs
git worktree remove <path>                                         # when finished -- never rm -rf
```

**The P17 archive.** The full artefact set of the P17 investigation — 486 checkpoints, 775
archives, 72 logs, about **2.9 GB** — is reachable only through the **local-only** branch
`codex/p17-inactive-prior` at `ef1961b`, checked out at `../etcGEMs-p17-archive`. It is **never
merged, never pushed, never deleted**; it could not be pushed because one log exceeds GitHub's
file-size limit. `main` carries the curated 580 files (15.7 MB) plus a manifest with the SHA-256 of
all 1,905 files including the excluded ones, so a fresh clone can verify what it does not have.
**A "clean up merged branches" pass that deletes this branch destroys the artefacts.** Its checkout
is **not** on disk by default — H5 removed it after proving the objects live in the primary store
and that the checkout comes back identical; recreate it with the command above when you need it.

---

## 2. How to work on it

The governing document is [RIGOUR.md](RIGOUR.md), and it is short. In summary:

- **Branch off `main` and end in a pull request.** Do not push to `main` directly. Read a PR's
  `baseRefName` before merging it — a PR opened against another branch merges into that branch,
  silently.
- **A new mechanism is a core option, default OFF, gated, then turned on per strain.** That is how
  every mechanism in here arrived. The gate is run with the option off to prove the plumbing is
  inert, and again with it on.
- **A changed model gets a new identifier.** If the numbers a model produces change, it is a
  different model, and it does not quietly replace the old one.
- **Pre-register thresholds, seeds, budgets and stopping rules in a commit before the run that
  they judge, and never move them afterwards.** A mistaken criterion needs an argument that
  predates the data it will judge, plus a dated correction.
- **Retain every outcome**, including the adverse ones, the crashed runs and the attempts that
  were replaced. Several of the most useful findings here are failures that were kept.
- **Withdraw by dated addition, never by erasure.** Numbers in an earlier report are not edited;
  a dated note is added saying what no longer holds and why.
- **Long runs go in a detached, idempotent, self-auditing driver.** The session launches it and
  leaves; the driver checkpoints, audits each run before starting the next, and stops itself on
  failure. `reports/T2_validated_posterior/run_protocol.py` is the working example.
- **Read [OPEN_ITEMS.md](OPEN_ITEMS.md) before starting anything**, especially its §4.

---

## 3. What is established

Full argument and every number in
`reports/H1_handover/_output/calibration_investigation.pdf`. In brief:

- **The framework and its gates.** Seven organism models on one core; 79/79 and 60/60, byte-identical
  with the options off; the *E. coli* port reproduces the reference implementation's ten R² values
  to within 0.009.
- **The mechanisms**, implemented and separable: measured proteome sectors; overflow metabolism
  emerging from a total-carbon cap rather than imposed; a respiratory-chain membrane-area budget —
  which is *available and untested* in the Candida models because their respiratory chain supplies
  only 0.02–0.05 % of the protons ATP synthase consumes.
- **The audits of the published yeast etcGEM.** Our coupling-ion defect class does not fire on it;
  its temperature-optimum/ceiling asymmetry reproduces in their model with their code and survives
  at their calibrated posterior over 100 models, with the margin narrowing.
- **The predictor validation.** The thermostability predictor resolves between organisms (r = +0.76)
  and not within a proteome (r = −0.05 on 1,947 proteins).
- **The likelihood's machinery**, each piece measured before adoption: the parsimonious tie-break,
  the log-O₂ floor at 1.4216, the `clamp` support form, the removal of a parameter proven never to
  be read (870-point invariant, maximum difference 2.02e-08), and zero likelihood for structural
  infeasibility (876 points, 10,512 solves, 9,355 structural zeros, 0 unresolved).
- **One a-priori prediction, half-successful and correctly labelled:** the *uncalibrated* model
  tracked an exact-strain growth curve's shape and under-predicted its peak ~2.3-fold. That curve
  was then consumed by the calibration, so the calibrated model has no holdout.
- **That the −4 K stability shift is parameterisation, not biology** — but both solutions put the
  least stable enzymes 4–6 °C below the measured meltome.

**And what is not:** no reproducible posterior for any configuration; R1 open; R3 provisional;
R4 untouched; the configuration comparison blocked. Both finished runs also under-predict the
measured growth peak at 35–43 °C by about 25 %.

---

## 4. What is open, and who owns it

The full text of every item is in [OPEN_ITEMS.md](OPEN_ITEMS.md), which is the single source; this
is an index to it.

### The PI's decisions (Gabriel)

| # | what | why it is first |
|---|---|---|
| **1.35** | **Adopt a deterministic likelihood-evaluation scheme, or accept non-reproducibility** | Everything else inherits it. Only a fresh model per evaluation is exact, at 3.2× cost; alternatives are listed and unmeasured |
| **1.36** | **Parsa's per-medium N₀ and carbon constants** | Assessed in `reports/H1_handover/parsa_1_9_assessment.md`: it is a **likelihood change**, not a figures update — M9's observable would halve |
| 1.34 | The reproducibility blocker itself | Measured; 1.35 is the decision it feeds |
| 1.33 | Why the model is infeasible over ~16 % of a defensible prior, and whether 15 °C is the right first temperature | Opened by the measurement; nobody has looked at which constraint binds |
| 1.14 | Whether a Li-style calibration is worth attempting | Predictor as wide prior, named enzymes |
| 1.20 / 1.24 | The `dTm` decision and the `dTm`/`tm_scale` ridge | Y3 showed the shift is parameterisation; the pair is non-identified |
| 1.16 | Should the Candida respiratory audits use the parsimonious vertex? | A K-series decision, unaffected by the above |
| 1.17 | Run the remaining eight gas-flux fits, or not | Blocked by 1.35; re-costed at ~320 h under the exact remedy |
| 1.26 | The D/E/F evidence comparison | The biological question; needs one reproducible number first |

### Parsa

| # | what |
|---|---|
| 1.8 | Which configuration-F ETC table is intended |
| 1.9 | The per-cell constants — **now assessed and awaiting the PI's 1.36 decision**; his script is safe to run for figures |
| 3.4 | Proteome allocation **above 37 °C on glucose** — a measurement, on the critical path, and the thermal ceiling is set exactly where the measured series stops |
| 2.11 | The respiration and growth observables are not statistically independent |

### Ilgaz

| # | what |
|---|---|
| 1.5 | `common_network.py` — does the optimum still compress on a common scaffold |
| 1.6 | Did any Candida audit touch lipid or membrane pathways |
| 1.7 | The `15_run_seq2tm.py` truncation bug — told, not yet fixed |
| 3.13 | Complex III is wired backwards in the three iRV973-derived models — a one-line stoichiometry fix in the published model |

### Nobody's until someone claims them

1.22 (the single-run plan), 2.1 (gene content → mechanism), 2.8 (the paper's correction register,
never written), 2.9 / 2.12 (bibliography errors), 2.10 (eight committed figures illegible on a
slide), 3.19 (a committed *Synechocystis* ceiling the code does not reproduce), 3.16 / 3.18 (the
shared ΔCp prior and the per-enzyme Tm spread), and the measurement wishlist 3.5–3.12.

---

## 5. What to do next, in order, with costs

**This order is a recommendation. The PI owns it.**

1. **Decide 1.35** (no compute). Everything below inherits it. The measured options are: a fresh
   model per evaluation, exact at **3.2×** cost; or three unmeasured alternatives —
   parallelise across runs instead of within them (wall-clock instead of compute), make the
   tie-break itself state-independent (fixes the cause, and is the only route that also helps the
   configurations whose oxygen sits on an LP face), or abandon nested sampling for this likelihood.
2. **One run under the chosen scheme** (~35–43 h if the exact one), and ask whether the two runs
   still disagree. **This is the cheap test of whether the second, unidentified cause is real**,
   and it is worth doing before committing to five runs. Register new seeds: three of the five
   reserved ones are spent.
3. **The five-run protocol** if step 2 is clean (~7–9 days sequential under the exact scheme).
   `docs/VALIDATION_PROTOCOL.md` is signed and frozen; a failed check is a failure of the
   programme, and no threshold may be revisited.
4. **The medium comparison** — the same configuration on fully defined M9, one variable changed —
   with the tie-break instrument run on that medium first, which has never been done.
5. **The mechanism comparison**, three configurations on one medium under one likelihood. This is
   the biological question and it is nearly free once one reproducible run exists.
6. **In parallel, and independent of all of the above:** the two missing measurements (3.4 and
   maintenance vs temperature from a chemostat) and the external holdout on evolved lines.

---

## 6. The standing hazards

These have each cost this project time. They are in OPEN_ITEMS §4 in full; one line each here.

- **The repository holds more than one measured value for some quantities, and they disagree.**
  Activation energies, the measured growth curve, T_opt, per-cell respiration. Fit both sides over
  the same window with the same functional form, and say which source you used.
- **Never verify with `cmd && check`.** A CLI exit-code defect made one such check vacuous and
  produced a false PASS.
- **Stale-at-commit has happened three times in three codebases by three people.** Assume a
  committed output does not reproduce until you have re-run it.
- **A gate only protects the fields it checks.** Adding a field to a record is a silent way to
  break byte-identity while the gate keeps passing.
- **Never run a `multiprocessing` script from stdin.** On macOS every worker re-imports
  `__main__`; a heredoc respawns forever and survives the session. One instance ran orphaned for
  13.6 hours. Write it to a file with an `if __name__ == "__main__"` guard.
- **A criterion must test the failure mode it names.** A sampleability rule here carried a surplus
  conjunct that tested a different failure mode and cost two run slots.
- **Test discontinuity by grid refinement, not by step size.** A step size confounds a steep
  gradient with a jump; refining separates them in four evaluations.
- **A likelihood evaluated in a persistent worker pool is not necessarily a deterministic function
  of its parameters**, the failure is intermittent, and a passing spot check does not establish it.
  Re-evaluate in a **fresh process**, not by repeating the call in the same one.
- **Beamer silently clips an overfull frame** and LaTeX emits no warning, so a slide can drop its
  last bullets with a clean render log. `reports/ecoli_deck/check_frames.py` catches it; it caught
  one while this handover was being written.
- **`codex/p17-inactive-prior` is the only ref keeping ~2.9 GB of artefacts reachable.** Never
  delete it.

---

## 7. How to reproduce anything

```sh
V=../etcGEMs-venv/bin          # the shared interpreter
unset CANDIDAS_ROOT

# the two gates
$V/python reports/candida_thermal_limit/gate_table.py     # 79/79
$V/python reports/P1_parsa_port/gate.py                   # 60/60

# provenance stamps: every report's inputs and their hashes
$V/python scripts/stamp_reports.py --check                # expect: every report stamp is up to date

# the null test — does the sampler recover a prior it cannot be learning from?
$V/python reports/P17_inactive_prior/null_check.py \
  --samples strains/eciML1515/outputs/calibration_configD_NLDM_recipe_P16_reduced/samples_red1.npy \
  --logwt   strains/eciML1515/outputs/calibration_configD_NLDM_recipe_P16_reduced/logwt_red1.npy \
  --column 7 --prior p16-f-metab \
  --expected-samples-sha256 fb134be7f90066e7129bdc0acba3b1f89227a49fc398921912b7b88bce7e1cbf \
  --expected-logwt-sha256   35b32f1b9ba6d21d156101e437cec155f99c8ac6f350229548a6259856af4ac2 \
  --output /tmp/null_check_new.json      # it refuses to overwrite an existing file

# the determinism measurement (T3): one battery per invocation, ~5-55 min each
$V/python reports/T3_determinism/t3_battery.py --scheme ref     # the fresh-process reference
$V/python reports/T3_determinism/t3_battery.py --scheme A       # the current path
$V/python reports/T3_determinism/t3_table.py                    # applies the registered rule

# the deck
cd reports/ecoli_deck && quarto render deck.qmd && $V/python check_frames.py
```

Every report directory carries a `PROVENANCE.md` stamp and, where it ran anything, a `DECISIONS.md`
recording the judgement calls in order. `reports/report_status.yaml` says, for each report, whether
it is CURRENT, HISTORICAL or SUPERSEDED, and how to re-run it.

---

## 8. Who to ask about what

| topic | ask |
|---|---|
| Any decision in §4's PI table; scope, priorities and whether a run is worth its hours | **Gabriel** (PI) |
| The *E. coli* respirometry, the derived tables, the medium recipes, the per-cell constants, the configuration-F ETC table | **Parsa** |
| The Candida reconstructions, `common_network.py`, Seq2Tm and the predictor pipeline, the published iRV973 stoichiometry | **Ilgaz** |
| The core, the gates, the likelihood, the samplers, and anything in `reports/P*/`, `reports/T*/` or `reports/Y*/` | the record: each directory's `report.md` and `DECISIONS.md`, and `reports/H1_handover/_output/calibration_investigation.pdf` |

**If you read only one other thing, read `docs/OPEN_ITEMS.md` §4.** It is the list of ways this
project has already lost time, and it is the most useful page in the repository.
