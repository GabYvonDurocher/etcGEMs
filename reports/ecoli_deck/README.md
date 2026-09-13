# E. coli deck for the Pawar group

Current artifact: `_output/deck.pdf`. E6 adds the provisional P16 seed-1 posterior, the
low-growth predictive result and the next experimental/model comparisons. Seed-2 agreement
is pending in this snapshot. Editable source: `deck.qmd`.

## Render and check

From this directory:

```sh
quarto render deck.qmd
python3 check_frames.py
python3 measure_figures.py
```

Use the project virtual environment for scripts that need scientific Python packages.
`check_frames.py` checks that each source frame's final content appears on its PDF page.
A successful LaTeX render alone cannot detect Beamer clipping.

`measure_figures.py` reports eight pre-existing borrowed figures below its tick-label
threshold, including the 22-panel line scan. E5 enlarged that scan to a dedicated slide;
E6 retains the size and explains its meaning on the preceding slide. Read it as a pattern
view, not as legible per-panel axes. The full-resolution source remains in `../P9_surface/`.

## Evidence and limitations

- `E6_VERIFICATION.md` records source checks, exact replacement slide text and render checks.
- `DECISIONS.md` records choices and corrections. Earlier entries describe earlier versions.
- P16 evidence was read from commit `191b4b0` in the primary worktree, without merging or
  changing it. Q1 was read at `b163bad` without merging its branch.
- No model fit or solver evaluation was run for E6. Predictions from 300 weighted draws are
  quoted from P16 D6's saved account, not independently regenerated here.
- P16's marginal-median vector is shown only as an example of an unusable summary. The deck
  uses the MAP and predictive distribution for interpretation.
- The growth/O2 overlays are historical comparisons at Parsa's gated parameter sets, not P16
  posterior predictions. `fit_predictions.csv` and `fit_observed.csv` preserve their inputs.
- CUE remains measurement-only and depends on an unresolved carbon-per-cell conversion.
- The published PDF is committed with the source. No push or merge is part of E6.

Existing figure-generation scripts are preserved. `make_fit_figures.py --no-solve` redraws
from committed predictions; invoking it without that flag performs model solves and was
not part of this text-only update.
