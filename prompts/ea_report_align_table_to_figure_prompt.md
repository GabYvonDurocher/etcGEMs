# Claude Code prompt — align Table 1 of the activation-energy report with the signed-contribution figure (same departure-from-naive-mean baseline) (autonomous)

Run from the project root (`.../MICROADAPT/etcGEMs`). TABLE + render only. No analysis, no model
change, no re-run. Fixes a presentation mismatch: the figure (ea_signed_contributions.png) anchors on
the NAIVE unweighted enzyme mean and shows "control weighting" as a deviation (+0.103), while Table 1
anchors on the control-weighted mean (0.9699) as an absolute — so the first term looks like two
different quantities. Make the TABLE match the FIGURE.

NOTE TO USER: launch in an auto-approving mode. Needs quarto to render.

---

```
Work AUTONOMOUSLY; commit; print a summary. Read first: reports/activation_energy/report.qmd (the
Table 1 code/markdown + the figure reference), reports/activation_energy/assemble.py, and
strains/eciML1515/outputs/ea_dissection/summary.json (the ACTUAL numbers: unweighted/naive enzyme
mean, control-weighted mean, allocation, maintenance, residual, Ea_org). Derive values from the
outputs — do NOT hardcode.

CHANGE - reformat Table 1 to the departure-from-naive-mean layout (matching the figure)
- New rows, in this order, using the ACTUAL numbers:
  * naive (unweighted) enzyme mean            = <unweighted_mean>            (e.g. 0.867)
  * + control weighting                       = +(control_weighted − unweighted)  (e.g. +0.103)
  * = control-weighted mean                   = <control_weighted_mean>     (e.g. 0.970)  [intermediate]
  * − allocation (growth law)                 = <allocation>                (e.g. −0.107)
  * − maintenance NGAM(T)                      = <maintenance>               (e.g. −0.010)
  * + residual (nonlinear)                     = <residual>                  (e.g. +0.057)
  * = organism Eₐ (actual)                     = <Ea_org>                    (e.g. 0.909)
- So the "control weighting" row is the DEVIATION (control_weighted_mean − unweighted_mean), exactly
  the figure's first bar; keep the control-weighted mean as a labelled intermediate for reference.
- ASSERT closure and print it: unweighted_mean + control_weighting + allocation + maintenance +
  residual ≈ Ea_org (small tol). Use consistent sign convention and decimals (3 dp) so figure and
  table read identically.
- Update the table caption to state it is the decomposition of the DEPARTURE of Eₐ_org from the naive
  enzyme mean, matching the figure (not a separate framing). Keep the units column (eV).

BUILD + VERIFY
- Re-run reports/activation_energy/assemble.py; quarto render report.qmd to PDF; confirm it builds.
- VERIFY: Table 1 now uses the naive-enzyme-mean baseline with a "+control weighting" deviation row
  matching the figure's first bar; the control-weighted mean appears as a labelled intermediate; the
  rows close to Ea_org (print the residual of the check); figure and table use the same numbers and
  signs; PDF builds (page count).

CONSTRAINTS
- Table + caption + render only. Values derived from ea_dissection outputs; no hardcoding, no
  re-analysis, no model change, no figure change.
- Autonomous; commit: "report(activation_energy): align Table 1 with the signed-contribution figure (departure-from-naive-mean baseline)".
```
