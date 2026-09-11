# `reports/ecoli_deck/` — the *E. coli* deck for the Pawar group

**Re-render:**

```bash
cd reports/ecoli_deck && quarto render deck.qmd      # -> _output/deck.pdf, 37 frames / 40 pages
python3 check_frames.py                              # exit 1 if any frame lost content
python3 measure_figures.py                           # exit 1 if any figure is illegible
python3 make_fit_figures.py --no-solve                # redraw the model-vs-data overlays
```

The overlays need the model only once: `make_fit_figures.py` without `--no-solve` reads Parsa's
committed chains (`--chains $PARSA_ROOT/strains/eciML1515/outputs`), runs **192 single-process
solves** and writes `fit_predictions.csv`. Everything after that redraws from the CSV.

**Always run `check_frames.py` after rendering.** Beamer silently truncates a frame whose content
overruns the slide and LaTeX emits **no** Overfull warning for it, so a clean render log does not
mean the deck is complete — it ate two lever tables' bullets, two rows of a table and four figure
captions while this deck was being written (`DECISIONS.md` D13).

The three figures that are not assembled from other reports are rebuilt with:

```bash
python3 reports/ecoli_deck/make_figures.py           # -> assets/figures/*.png
```

Everything else is **pointed at by relative path in its producing report** rather than copied, so
there is one source of truth per figure: `../ecoli_tpc/assets/figures/`,
`../ecoli_gasflux/assets/figures/`, `../P9_surface/`.

## What is here

| file | what it is |
|---|---|
| `deck.qmd` | the deck. Beamer, 16:9, lualatex |
| `_output/deck.pdf` | the rendered deck, committed (the convention in `reports/activation_energy/` and `reports/synthesis/`) |
| `make_figures.py` | the three figures drawn here, from committed tables only |
| `make_fit_figures.py` | the model-vs-data overlays; reads the gate's parameters, 192 solves, then `--no-solve` |
| `fit_predictions.csv`, `fit_observed.csv` | the committed predictions and measurements behind those two figures |
| `check_frames.py` | the frame-clipping check; run it after every render |
| `measure_figures.py` | the legibility check: rendered tick-label size per figure, against the threshold in `DECISIONS.md` D17 |
| `figure_inventory.csv` | all 54 candidate figures, marked AS IS / CAVEAT / NOT USABLE, with the deciding fact for each |
| `DECISIONS.md` | the judgement calls, including the MRes baseline (D1) and Pettersen & Almaas (D2) |
| `references.bib`, `nature-communications.csl` | house convention, copied per report directory |

## Two things to know before reusing anything from it

* **No interval from the older *E. coli* fits appears on any slide**, and seven otherwise
  attractive figures are excluded because the unsupported interval is drawn *inside the image*
  (`DECISIONS.md` D4).
* **`measure_figures.py` exits 1 and will keep doing so.** The three figures drawn here pass
  ($f$ 0.91–0.94, tick labels 9.1–9.4 pt); the **eight borrowed ones cannot** — they are journal
  figures, natively 432–1224 pt wide against a 398 pt slide, so their ceiling is $f \approx 0.47$
  whatever the layout. Fixing them means re-running their producing scripts at slide width, which
  rewrites other reports' committed assets. `DECISIONS.md` D18; `docs/OPEN_ITEMS.md`.
* **Figure sizes are set per figure, by aspect** — `{height=...}` for a square or tall figure,
  `{width=...}` for a wide one. Shrinking the width of a tall figure does nothing; it is the
  height that overruns the frame.
* **No slide claims a model-over-measurement overlay**, because no committed table provides one.
  The gas-flux figures are model output; the respirometry figures are measurement; they are on
  separate slides and both say which they are.
* **Gas-flux slides carry the mechanism and say so.** The R² behind them are point estimates from
  chains that ran ~9 autocorrelation times against a ≥ 40 criterion — see the banner at the top of
  `../ecoli_gasflux/README.md`.

**Nothing from P15 appears.** The posterior slide says the runs are in flight and what the
criterion is.
