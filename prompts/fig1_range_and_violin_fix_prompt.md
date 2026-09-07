# Claude Code prompt — fix Fig 1 of the activation-energy paper: clip each TPC panel to its data-supported temperature range (no extrapolated tails, esp. the phototroph) and render the SS-E posteriors as violins, not histograms (autonomous)

Run from the project root (`.../MICROADAPT/etcGEMs`). SMALL, FIGURE-ONLY fix to reports/activation_energy/ Figure 1 (the
three-TPC scene-setter + the SS-E posterior insets). Two changes only. NO model re-runs, NO re-calibration, NO new
analysis — reuse the existing posterior draws / SS-E samples the paper already produced; only the PLOTTING changes.

NOTE TO USER: launch in an auto-approving mode. Needs quarto to re-render.

---

```
Work AUTONOMOUSLY; commit; print a summary. Read first: reports/activation_energy/{assemble.py, report.qmd,
supplementary.qmd} and locate the Fig 1 generation code (the three-panel TPC + SS-E posterior figure). Find where the
per-organism TPC curves are plotted and where the SS-E posteriors are drawn. Also read the digitised observed-TPC data
files for the three organisms (strains/eciML1515/... Van Derlinden; strains/mmaripaludis/thermal/ Jones; strains/syn6803/
thermal/ Zavrel) to get each organism's observed temperature range. Reuse any saved posterior-draw / SS-E-sample arrays
the Fig 1 code already computed — do NOT recompute them.

FIX 1 - clip each TPC panel to its DATA-SUPPORTED temperature range (no extrapolated tails)
- For EACH organism, restrict the plotted temperature axis to its data window: START near the LOWEST observed temperature
  and EXTEND only slightly (a few C, ~2-3) beyond the HIGHEST observed temperature. Derive min/max observed T from each
  organism's digitised TPC data (do not hard-code). Keep the observed points, the posterior-predictive median and the
  band all WITHIN this window; drop the long low- and high-temperature model tails that currently run past the data.
- This matters MOST for the PHOTOTROPH (Zavrel): its model curve currently extends well beyond the Zavrel points at BOTH
  ends — clip the phototroph panel to start close to the lowest Zavrel measurement and stop just beyond the highest.
  Apply the same data-bounded rule to the E. coli and methanogen panels for consistency (they may already be close).
- If the three panels currently share one x-axis, give each its own data-appropriate x-range (small multiples) rather
  than one wide shared axis that forces extrapolation.

FIX 2 - render the SS-E posteriors as VIOLINS, not histograms
- Change the SS-E posterior insets from histograms to VIOLIN plots (the style used in the earlier two-organism figure —
  search the git history / older figure scripts if a violin helper already exists, and reuse it). Keep the three
  posteriors on a shared Ea axis so the SEPARATED, correctly-ORDERED medians (methanogen ~1.06 > E. coli ~0.68 >
  phototroph ~0.57) stay obvious. Preserve the observed-SS-E reference markers if the previous version had them.

BUILD
- Re-run reports/activation_energy/assemble.py (or the Fig 1 builder); quarto render report.qmd (+ supplementary if it
  shares the figure); confirm it builds with no unresolved crossrefs. Report the page count and confirm Fig 1 now shows
  (a) data-bounded temperature ranges per panel and (b) violin posteriors.

VERIFY (report all)
1. Each TPC panel is clipped to its data-supported range (starts near the lowest observed T, ends just beyond the highest);
   the phototroph panel no longer shows extrapolated tails past the Zavrel data at either end.
2. The SS-E posteriors are violins (not histograms); the three are on a shared Ea axis with the correct ordering visible.
3. No model re-runs / re-calibration; existing posterior draws reused; only plotting changed.
4. report (+ supplement if affected) builds; page count reported.

CONSTRAINTS
- Figure-only change; reuse saved posteriors; no new analysis. SS-E throughout. Do not alter the numbers, the other
  figures, or the text (beyond a caption tweak if the range/style is described there).
- Autonomous; single commit: "paper(activation_energy): Fig 1 — data-bounded TPC ranges (no extrapolated tails) + violin SS-E posteriors".
```
