# Claude Code prompt — clean up overlapping text in Fig 1 panel D (the SS-E posterior violins) of the activation-energy paper (autonomous)

Run from the project root (`.../MICROADAPT/etcGEMs`). SMALL, FIGURE-ONLY layout fix to reports/activation_energy/ Figure 1,
panel D only (the "Activation-energy posteriors" violin panel). The violins/data are correct; only the TEXT LAYOUT needs
fixing. NO model re-runs, NO re-analysis, NO changes to the other panels' data or the numbers — reuse everything; only
adjust positioning/rotation/spacing of labels in panel D.

NOTE TO USER: launch in an auto-approving mode. Needs quarto to re-render.

THE PROBLEMS (panel D):
1. The x-axis category labels (Methanogenesis / Respiration / Photosynthesis) overlap each other — they are too long to sit
   horizontally under three narrow violins.
2. The "~0.65 eV benchmark" annotation on the dotted line overlaps the median value labels (0.69, 0.64).
3. The median value labels (1.04, 0.69, 0.64) sit on/near the benchmark line and each other.

---

```
Work AUTONOMOUSLY; commit; print a summary. Read first: reports/activation_energy/{assemble.py, report.qmd} and locate the
Fig 1 panel D (violin) plotting code. Change ONLY the text/label layout in panel D; do not touch the violins, the data, the
other three panels, or any numbers.

FIX 1 - x-axis category labels (stop the overlap)
- Rotate the three x-tick labels (Methanogenesis / Respiration / Photosynthesis) to ~30-40 degrees, right-aligned
  (ha='right'), and/or reduce their font size a step, so they no longer overlap. If rotation alone is not enough, ALSO give
  panel D a bit more width (e.g. bump its gridspec width ratio) so the three labels fit. Ensure the labels sit fully within
  the figure (no clipping at the bottom).

FIX 2 - the benchmark annotation (move it clear of the medians)
- Reposition the "~0.65 eV benchmark" text so it does NOT overlap the median value labels or the violins: place it at one
  end of the dotted benchmark line (e.g. top-left of the panel, or just above the line at an x well clear of the violins),
  with the dotted line spanning the panel. Keep it small/muted (grey) so it reads as a reference, not a data label.

FIX 3 - the median value labels (separate them cleanly)
- Place each median value label (1.04, 0.69, 0.64) consistently just beside/above its own median tick, offset to a side
  that avoids the benchmark line and the neighbouring violin, so all three are legible and none collide with the benchmark
  text or each other. Keep the observed-SS-E reference markers.

GENERAL
- Use constrained_layout / tight_layout or manual spacing so nothing in panel D overlaps. Do a quick self-check: after
  building, confirm (by inspecting the rendered PNG/PDF, e.g. crop panel D) that the x labels, the benchmark text, and the
  three median labels are all separated and legible.

BUILD
- Re-run reports/activation_energy/assemble.py (or the Fig 1 builder); quarto render report.qmd (+ supplement if it shares
  the figure); confirm it builds. Report the page count.

VERIFY (report all)
1. Panel D x-axis labels no longer overlap (rotated/resized and/or panel widened); not clipped.
2. The "~0.65 eV benchmark" text no longer overlaps the median labels or violins.
3. The three median value labels are separated and legible; observed markers preserved.
4. Only panel D text layout changed; violins/data/other panels/numbers untouched; report builds (page count).

CONSTRAINTS
- Figure-text layout only; no new analysis, no data or numeric changes, no edits to the other panels. Single commit:
  "paper(activation_energy): Fig 1 panel D — fix overlapping axis/benchmark/median labels".
```
