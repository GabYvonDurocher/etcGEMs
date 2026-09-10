# Claude Code prompt — Y2: re-run Y1's regime test at the published posterior, so the numbers can be quoted (autonomous, ~1 hour)

**Run from `../etcGEMs-work`, NOT from the primary checkout.** P7 is running in `etcGEMs` and owns
it for the next several hours. `etcGEMs-work` is a detached checkout of `main` at `2af5815`; make a
branch there and work there. Item 2.5 in `docs/OPEN_ITEMS.md`.

**Why.** Y1 PART C found the T_opt/CT_max asymmetry reproduces in Li et al.'s yeast etcGEM —
T_opt moves 10.09 °C and CT_max 0.81 °C when the binding constraint changes — the first replication
outside this group's code. But it ran at their **prior** enzyme parameters, not the calibrated
posterior, and Y1 flagged that itself. The prior is deliberately wide (Topt from Tome with the
predictor's RMSE as width); the posterior is what their paper's results are stated at. Until the
test is repeated there, the 10.09 / 0.81 figures describe an uncalibrated model and must not be
quoted as a property of theirs.

**Environment.** P7 is rebuilding the venv at `../etcGEMs-venv` and validating it. Do NOT use that
one and do NOT touch it. Use the existing venv inside the primary checkout — P7 leaves it in place —
by absolute path. Read-only on everything under `etcGEMs/`; you are only borrowing its interpreter.

REFERENCE, read first: `reports/Y1_yeast_audit/report.md` PART C and PART D, its DECISIONS.md, and
the scripts it used for the regime test. Reuse them; do not rewrite them.

---

```
Work AUTONOMOUSLY; commit in parts, prefixed "Y2: "; maintain reports/Y2_regime_posterior/
DECISIONS.md FROM THE FIRST JUDGEMENT CALL. Standing rules carry over. Check exit codes explicitly,
never `cmd && check`. In ../etcGEMs-work: branch `y2/regime-posterior` from the detached main; do
not push to main; end in a PR that is NOT merged. Do not write anything under ../etcGEMs.

TASK 0 - premise
- Confirm you are in ../etcGEMs-work, on main at 2af5815 or later, clean. Branch.
- Confirm the interpreter is the primary checkout's existing venv (absolute path) and that
  ../etcGEMs-venv is not on your path. Report both paths.
- Confirm Y1's BayesianGEM clone is still where Y1's report says, at a68307e, unmodified
  (`git status` in it is clean). If it is gone, re-fetch to the same path and commit; do not
  proceed on a different version.

TASK 1 - obtain the posterior, and be exact about which one
- Li et al. deposited posterior samples on Zenodo; Y1's report cites the DOI. Fetch them. Record
  the DOI, version, file names, checksums, and how many posterior samples of how many parameters.
- Establish what Y1's regime test consumed as "the prior" - which file, which fields - and map
  the posterior onto exactly the same fields. If the posterior's parameterisation differs from the
  prior's (units, transforms, enzyme ordering), say so and show the mapping is exact on one enzyme
  by hand before applying it to 764.
- Do NOT use a posterior from their figures or supplementary tables if the sample file exists.
  Point estimates from a figure are not the posterior.

TASK 2 - the regime test at the posterior
Y1's test, unchanged in method, at three parameter sets:
  (a) the prior, re-run - to confirm you reproduce Y1's 10.09 / 0.81 / plateau 2.5 -> 7.0 C
      before changing anything. If you do not, STOP and report the difference.
  (b) the posterior MEDIAN, enzyme by enzyme.
  (c) N posterior DRAWS - as many as an hour allows after (a) and (b), minimum 20. Report the
      spread of T_opt shift, CT_max shift and plateau width across draws. This is the number that
      lets the finding be quoted with an interval rather than a point.
- Same constraint switch Y1 used, same growth-rate control (Y1 held the growth change smaller
  than the enzyme-pool scaling; keep that comparison), same 99 % plateau definition.
- Report per parameter set: T_opt before/after, CT_max before/after, plateau width before/after,
  growth at T_opt before/after.

TASK 3 - what changed between prior and posterior, and whether it matters
- Does the asymmetry survive? State it as Y1 did: as the loss of a sharply-defined optimum if the
  plateau widens, as a shift if it moves. Do not upgrade a plateau to a shift.
- Does the posterior narrow the effect (calibration pulled the enzymes toward the data, so the
  regime may be less free to move) or leave it? Report the direction and size.
- Which nine enzymes carry the thermal limit at the posterior? Y1 found nine at the prior, all
  with measured Tm 40.5-43.8 C. Same nine? Report the overlap.
- Cross-check against the paper: their Fig. 2 and Supp. Fig. 7 give posterior widths. If your
  posterior file's per-enzyme SDs do not match what the paper reports (Topt 7.1 C, Tm 4.0 C), you
  have the wrong file or the wrong transform. STOP and report.

TASK 4 - record
- reports/Y2_regime_posterior/report.md: the three-way table, the draw spread, the enzyme overlap,
  and a one-paragraph statement of what may now be quoted and at what interval.
- Update Y1's report with a dated note pointing here - do not edit its numbers.
- docs/OPEN_ITEMS.md: close 2.5 or restate it. If the asymmetry survives at the posterior, add the
  quotable figure with its interval to the synthesis's evidence slot (reports/synthesis/
  evidence.csv, status CURRENT, source this report) - one row, no re-render.
- Stamp via scripts/stamp_reports.py.

VERIFY (report all)
1. TASK 0: worktree, branch, interpreter path, BayesianGEM at a68307e clean.
2. TASK 1: DOI, version, files, checksums, sample count; the prior->posterior field mapping shown
   exact on one enzyme.
3. TASK 2: (a) reproduces Y1; the (a)/(b)/(c) table; N draws and their spread.
4. TASK 3: survives or not; direction and size of the prior->posterior change; enzyme overlap;
   the SD cross-check against Fig. 2 / Supp. Fig. 7.
5. TASK 4: the quotable statement; evidence.csv row; OPEN_ITEMS 2.5; stamp.
6. `git diff main --stat` in ../etcGEMs-work: reports/Y2_regime_posterior/, one dated line in Y1's
   report, evidence.csv, OPEN_ITEMS, stamps. Confirmation that nothing under ../etcGEMs was written
   and ../etcGEMs-venv was not used.

CONSTRAINTS
- Register as Y1: an audit applied to the reference implementation. Their model, their posterior,
  their thermal layer. No re-implementation.
- The prior run must reproduce Y1 before the posterior run counts.
- A plateau is reported as a plateau. Intervals from draws, not a point from the median alone.
- Read-only on the BayesianGEM clone and on the primary checkout.
- Autonomous; commit in parts.
```
