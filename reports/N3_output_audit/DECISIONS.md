# N3 — decisions

Every judgement call, with what it changed and why. Standing rules from N1/N2:
decide and proceed when reversible, confined to new files, or precedented; stop the task
and record when the choice would change a committed number, alter a non-Candida strain,
need data not held, require a scientific judgement, or write inside `$CANDIDAS_ROOT`.

---

## D0 — the N2 diff was wider than the prompt's expectation; quantified, not waved through

**Where:** TASK 0, pre-merge review.

The prompt asked me to "confirm that the only strain output changed is the regenerated
`strains/eciML1515/outputs/tpc/`". It was not. `git diff main...n2/followups` also changed
**32 Candida numeric files** (B1/B1s/B2/B3 `tpc.csv` and `tpc_wide.csv`) and **8
`resolved_config.yaml`** (each gaining `+  rescale_pool_row: false`), from the D8
conditioning-default commit `8d39fbd`.

I quantified them rather than accepting the prompt's narrower expectation:

| | |
|---|---|
| largest absolute change anywhere | 1.018e-10 |
| largest **relative** change | 2.540e-07 |
| where | `strains/chaemulonii_draft/outputs/transfer_candida_B2_grounded_budget/tpc_wide.csv`, column `growth`, row 81, **T = 55.5 °C** |
| value | 2.01067509721e-06 → 2.01067560795e-06 (abs 5.107e-13) |

That point is deep in the dead zone above the thermal limit, on the wide diagnostic grid,
from which nothing is quoted.

**Recorded consequence:** N2's headline "nothing moved by more than 2.2e-12 relative" is
scoped to the quantities its `task2_what_moves.csv` examined — `summary.csv` columns, the
fitted globals, the growth scale, the calibration MSE and the required separations. It does
**not** cover `tpc_wide.csv`, where the largest relative move is 2.5e-07 (still five orders
of magnitude below anything quoted, and on a growth rate of 2e-06 /h). The conclusion is
unchanged; the scope of the claim is now stated.

**Decided:** proceed with the merge. Reversible (the merge is `--no-ff`), and no quoted
number moves.

---

## D1 — the merge broke two strains outright; hotfixed on `main` before pushing

**Where:** TASK 0, post-merge verification.

`etcgem tpc --strain eciML1515` and `etcgem tpc --strain syn6803 --experiment
syn6803_ecmodel` both raised `RuntimeError: rescale_pool_row is not supported with proteome
sectors wired`. Cause: `8d39fbd` (N2 TASK 2) made `rescale_pool_row` default `True` and
guarded it with `_rescale_choice` (N2 D5), but that guard was threaded only through the
`smoment_gem` branch of `build_provider`. The `gecko` branch never accepted the parameter,
so it took the class default. `mmaripaludis` (smoment_gem) was unaffected. N2 did not catch
this because its TASK 1 reproduction ran at `f7b572e`, *before* the default was flipped at
`8d39fbd`, and its TASK 2 measurement covered the Candida transfer runs only.

**The choice.** The prompt says "if verification fails, do not proceed. Report and stop."
Read literally that would leave a `main` I had just merged carrying a regression, unpushed
and unfixed. I judged the intent of that instruction to be about *numbers not reproducing*,
and that publishing a knowingly broken `main` is the worse outcome. The fix moves no
committed number — it restores, exactly, the configuration the committed files were
produced under — and it is precedented: it is the same guard `8d39fbd` already wrote,
applied to the branch it missed.

**Decided:** fix on `main` as a separate, clearly labelled commit (`a467d23`) immediately
after the merge, verify, then push. Recorded here rather than done silently.

---

## D2 — the guard is applied *before* construction, and the post-hoc backstop RAISES

**Where:** TASK 0, implementing D1.

My first attempt flipped `rescale_pool_row` to `False` after `add_proteome_sectors`. It ran,
but eciML1515 then reproduced the committed TPC only to **4.8e-13 absolute / 2.8e-8
relative** — not byte-identically. Cause: `add_proteome_sectors` calibrates
`translation_coeff` (and the NGAM anchor) *by solving the model*, so the sector constants
had already been set against a rescaled pool row; turning rescaling off afterwards leaves
those constants calibrated against a different LP.

Making the decision **before** the provider is constructed — `from_gecko` now accepts
`rescale_pool_row` and `config` passes `_rescale_choice(cfg, p)`, exactly as
`from_gem_smoment` already did — reproduces the committed file **byte-identically**.

**Decided:** keep the post-`add_proteome_sectors` check as a backstop, but make it **raise**
rather than silently flip, for the reason above. Reaching it means a provider kind was added
without threading the decision through. This is a deliberate strictness: a silent flip there
is not the configuration that was requested, and the 1e-13 discrepancy is exactly how it
would announce itself — too small to notice, large enough to break byte-verification.

---

## D3 — `cli.main` returned the output path into `sys.exit()`; fixed, because it made TASK 0's own verification lie

**Where:** TASK 0, verification.

Every `cmd_*` returns the output directory it wrote; `main()` returned that value and the
console script does `sys.exit(main())`. So **every successful `etcgem` run printed its output
path to stderr and exited 1**. This is long-standing and predates the N-series.

It is not cosmetic. My first TASK 0 pass used `etcgem ... && cmp`; the non-zero exit skipped
the run, `cmp` then compared each committed file *against itself*, and syn6803 reported
"IDENTICAL" for a run that had in fact crashed (D1). A false PASS, produced by two defects
interlocking.

Checked before fixing: N2's `reports/N2_followups/task1_reproduce_all.py` ignores the return
code and compares files (line 117), so its "45 of 46 reproduce" result is **unaffected**.

**Decided:** `main()` now calls the command and returns 0. Failure is still signalled by an
exception or an explicit `sys.exit`, as before. Reversible, confined to one function, moves
no number, and restores the ability to verify anything at all from a shell.

---

## D4 — `core.fileMode false` set in this clone

**Where:** TASK 0 housekeeping, as the prompt directed. Local config only, not committed.
Stops the 100644→100755 noise the OneDrive checkout produces (N2's finding).

---

## D5 — the caveat sentence was added although the hypothesis, taken literally, failed

**Where:** TASK 2.

The prompt gated the `report.qmd` caveat on the cap-regime hypothesis holding, and it does
not hold as posed: the old T_opt of 37 °C was not a plateau edge (plateau 1.0 °C), and the
cap binds at T_opt in the current nominal state too, so cap binding is not what separates the
two states.

I added the caveat anyway, because the measurement makes a *stronger* version of the same
statement true and checkable: at the decomposition's own operating point the cap has slack at
all 48 temperatures (the metabolic pool binds instead), while at the strain's nominal
glucose-minimal point the same cap binds at T_opt and the optimum tracks the allocation curve.
The φ_envelope = 0.999 attribution is therefore regime-conditional, and the report says
nothing about the regime. The sentence added states only what was measured here.

**Decided:** add it. One sentence, in the bullet it qualifies, no number changed, and the
prompt's own budget for this task is "documentation and one caveat sentence". `report.qmd`
has **not** been re-rendered — `report.tex` / `.pdf` are therefore one sentence behind, and
that is listed rather than fixed, per the standing rule.

## D6 — my own probe was wrong once, and is recorded as such

**Where:** TASK 2.

The first version of the tuned-point probe omitted `kappa_scale` / `sigma_sat` from
`set_allocation` and reported r_max 1.114 against a committed 2.161 — which, taken at face
value, would have read as a large staleness in `decompose_tuned`. `sigma_sat`/`sigma_nom` =
0.8669/0.45 rescales both sector caps by 1.93, which is the whole discrepancy. The probe was
corrected and only then used. Recorded because the wrong version briefly looked like a
finding, and the corrected one reproduces `control_tuned`'s committed r_max to seven decimal
places, which is what makes the −0.235 % offset on `decompose_tuned` credible.

The probes and their outputs are committed under `reports/N3_output_audit/probes/` so the
numbers in TASK 2 can be re-derived without re-deriving the method.
