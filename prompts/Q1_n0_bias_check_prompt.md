# Claude Code prompt — Q1: is the N₀ / cell-carbon conversion imprinting itself on the respiration data? (autonomous, ~30 min, no solves)

**Run from `../etcGEMs-work`.** Branch `q1/n0-check` **from `e2/deck`**, not from main — the inputs
this needs (`reports/ecoli_deck/fit_predictions.csv`, `fit_observed.csv`) were committed by E4 and
are not on main. P16 is running a 15-dimensional nested fit in `etcGEMs`; **write nothing there**.
Use `../etcGEMs-venv`. **Arithmetic on committed tables only — no model solves, no fits.**

**The question.** `docs/OPEN_ITEMS.md` 1.9 records that `cell_volume_um3` and `cell_carbon_fg` are
typed constants (2 µm³ / 350 fg) in every row of both media sets, while Parsa's own `config.R` log
prints **21.21 µm³ / 2120.58 fg** — about 6× apart. `otu_cell_sizes_*.csv` confirms the constants
are constant: every OTU carries the same 2 / 175 / 350. The README states growth R² and scale-free
quantities are immune while respiration R², CUE and absolute per-cell rates are not. **1.9 flags the
discrepancy but has never drawn the consequence, and P16 is fitting against the respiration term
right now.**

**The consequence worth testing.** A *uniform* scale error would be largely absorbed by the free
`resp_scale` parameter — ugly, since `resp_scale`'s posterior would then partly encode the
conversion error rather than physiology, but not fatal to the *shape*. The problem is that it will
not be uniform: **E. coli cell size varies strongly with growth rate** (Schaechter's growth law), and
growth rate varies enormously across a temperature series. A constant fg-C-per-cell is therefore
wrong by a factor that itself changes along the temperature axis — a distortion of the *temperature
dependence* of per-cell respiration, which is exactly the signal the thermal parameters read. That
is not something a constant `resp_scale` can absorb.

**The confound this must handle.** Growth rate and temperature are strongly correlated along a TPC,
so a residual trending with growth rate could equally be the model failing with temperature. **The
two media separate them**: at the same temperature they grow at different rates. That comparison is
the decisive test and TASK 1 must do it explicitly rather than regressing on growth rate alone.

NOTE TO USER: launch in an auto-approving mode. Reading committed CSVs and doing statistics.

REFERENCE, read first: `docs/OPEN_ITEMS.md` 1.9; `strains/eciML1515/respirometry/README.md` and its
`derived_*_current.csv`, `otu_cell_sizes_*.csv`; `reports/ecoli_deck/fit_predictions.csv`,
`fit_observed.csv`, `make_fit_figures.py`.

---

```
Work AUTONOMOUSLY; commit in parts, prefixed "Q1: "; maintain reports/Q1_n0_check/DECISIONS.md FROM
THE FIRST JUDGEMENT CALL. Standing rules carry over. Check exit codes explicitly, never
`cmd && check`. Branch `q1/n0-check` from `e2/deck` in ../etcGEMs-work; do not push to main; end in
a PR that is NOT merged. Write NOTHING under ../etcGEMs. No solves.

TASK 0 - premise and the conversion chain
- Confirm the worktree, the branch (off e2/deck), the interpreter; confirm P16 untouched.
- Read the derived tables' construction and write into DECISIONS.md D0 the **exact chain** from the
  raw O2 measurement to each derived quantity: which columns `cell_volume_um3` and
  `cell_carbon_fg` enter, where `N0_cells_per_L` enters, and therefore which of
  `growth_fgC_h`, `respiration_fgC_h`, `growth_C_per_C_h`, `respiration_C_per_C_h`, `CUE`,
  `resp_over_growth` are affected and which cancel. **Derive this from the code/columns, not from
  the README's summary** - then say whether your derivation agrees with the README. A disagreement
  is a finding.
- State which quantity the model's respiration likelihood actually compares against, read from the
  fitting code. Everything below matters only insofar as it touches that one.

TASK 1 - does the residual trend, and is it growth rate or temperature?
- Join fit_predictions.csv to fit_observed.csv and to derived_*_current.csv on medium/temperature.
  Compute the residual r = log(measured O2 / modelled O2) per point. State how you handled
  replicates.
- Plot and regress r against (a) temperature and (b) measured growth rate, per medium. Report
  slope, 95 % CI, p and R2 for each.
- **The decisive comparison:** at temperatures where BOTH media have data, is the difference in
  residual between media predicted by the difference in their growth rates? Report the pairing
  explicitly - temperature, growth rate per medium, residual per medium - and whether residual
  difference tracks growth-rate difference. That separates a cell-size artefact (tracks growth
  rate at fixed temperature) from a model failure (tracks temperature regardless of medium).
- A flat scatter with no trend in either is the clean outcome and should be reported as plainly as
  a positive one.

TASK 2 - sensitivity to the conversion, which is free because the columns are in the table
- Recompute every affected quantity with Parsa's config.R values (21.21 um3 / 2120.58 fg) in place
  of the typed constants, and report: the factor by which each moves; whether the TEMPERATURE
  DEPENDENCE moves or only the scale; and whether TASK 1's residual trend changes.
- Report CUE under both conversions - it appears in the deck (`fig_cue.png`) and the README says it
  is affected, so if it moves the deck slide needs a caveat.
- If a quantity is scale-invariant your TASK 0 derivation says should be, verify numerically that it
  does not move. That is the check on your own derivation.

TASK 3 - what a growth-rate-dependent cell size would do, WITHOUT implementing one
- State, from the literature the repository already cites where possible, the approximate magnitude
  of the E. coli cell-size/growth-rate relation. Do NOT fit one and do NOT alter the data.
- Report what fraction of the observed residual trend (TASK 1) a plausible size-growth relation
  could account for - order of magnitude, clearly labelled as an estimate.
- Say what measurement would settle it: per-condition cell size or dry mass alongside the
  respirometry. Whether that exists is Parsa's to answer; do not assume.

TASK 4 - what it means for P16, stated as a caveat not a correction
- If TASK 1 finds a growth-rate trend at fixed temperature: state plainly that `resp_scale`'s
  posterior in P16 partly encodes the conversion rather than physiology, and that the respiration
  term's temperature dependence carries the same imprint. Quantify how large the effect is against
  the respiration term's own scale where you can.
- If it does not: say so, and that the respiration likelihood is safe from this on current
  evidence - which is equally worth knowing before the posterior is interpreted.
- **Do not change any data, any conversion, or any config.** This diagnoses; 1.9 remains Parsa's to
  resolve.

TASK 5 - record
- reports/Q1_n0_check/report.md: D0's conversion chain; the three regressions; the paired-media
  test; the sensitivity table; the estimate; the P16 caveat.
- docs/OPEN_ITEMS.md 1.9: append the consequence, drawn rather than flagged - what is affected,
  by how much, and whether the trend is present. Keep the existing text.
- reports/synthesis/evidence.csv: one row for the verdict.
- If CUE moves materially, note in reports/ecoli_deck/DECISIONS.md that the CUE slide needs a
  caveat - do NOT edit the deck here, that is E5's branch and it may be mid-flight.
- Stamps.

VERIFY (report all)
1. TASK 0: the conversion chain derived from code; which quantities are affected and which cancel;
   agreement or disagreement with the README; what the likelihood compares against.
2. TASK 1: the two regressions with slope, CI, p, R2; the paired-media table; the verdict on
   growth-rate versus temperature.
3. TASK 2: the sensitivity table under both conversions, separating scale from temperature
   dependence; CUE under both; the numerical check on scale-invariant quantities.
4. TASK 3: the size-growth magnitude with its source; the fraction accounted for, labelled as an
   estimate; the measurement that would settle it.
5. TASK 4: the P16 caveat or the all-clear, quantified.
6. `git diff e2/deck --stat`: reports/Q1_n0_check/, OPEN_ITEMS, evidence.csv, possibly one line in
   the deck's DECISIONS, stamps. Nothing under ../etcGEMs, src/, strains/ or the deck's .qmd.

CONSTRAINTS
- No solves, no fits, no data altered, no conversion changed. Diagnosis only.
- The growth-rate/temperature confound is separated by the paired-media comparison, not by
  regression on growth rate alone.
- TASK 0's derivation comes from the code; the README is checked against it, not assumed.
- A null result is reported as prominently as a positive one.
- 1.9 stays Parsa's to resolve; this run draws the consequence and stops.
- Autonomous; commit in parts: "Q1: conversion chain", "Q1: residual trend", "Q1: sensitivity",
  "Q1: record".
```
