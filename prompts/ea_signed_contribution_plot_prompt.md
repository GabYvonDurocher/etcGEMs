# Claude Code prompt — replace the Ea-decomposition waterfall with a signed-contribution bar plot (deviations from the enzyme mean) and regenerate the figure (autonomous)

Run from the project root (`.../MICROADAPT/etcGEMs`). PLOTTING change + figure regeneration only.
Reuses the existing Ea-dissection decomposition numbers (no re-analysis, no model change, no re-run).
The vertical from-zero waterfall is hard to read; replace it with a horizontal SIGNED-CONTRIBUTION bar
plot that shows each effect as a +/- deviation from the naive enzyme mean, matching the paper's
"departure from the mean" framing.

NOTE TO USER: launch in an auto-approving mode.

---

```
Work AUTONOMOUSLY; commit; print a summary. Read first: src/etcgem/ea_dissection.py (the decomposition
+ the current plot_ea_waterfall / waterfall figure code, and where the components are stored),
strains/eciML1515/outputs/ea_dissection/{summary.json, NOTE.md} (the actual numbers), and how the
figure is written. Do NOT change the analysis or model; only the plotting + the regenerated figure.

DESIGN (horizontal signed-contribution bar, matplotlib):
- Bars are the decomposition terms expressed as SIGNED DEVIATIONS FROM THE UNWEIGHTED ENZYME MEAN,
  DERIVED from the existing components (do NOT hardcode):
  * control weighting = control_weighted_mean − unweighted_mean   (e.g. 0.970 − 0.867 = +0.103)
  * allocation (growth law) = the allocation term                 (e.g. −0.107)
  * maintenance NGAM(T) = the maintenance term                    (e.g. −0.010)
  * residual (nonlinear) = the residual                           (e.g. +0.057)
  Assert they close: unweighted_mean + Σ(these four) ≈ Ea_org (within a small tol); print the check.
- Horizontal bars from a zero baseline (axvline at 0). Order top→bottom: control weighting, allocation,
  maintenance, residual. Colour by SIGN — positive (raises Ea) one colour (a teal/green, e.g. #199e70),
  negative (lowers Ea) another (a coral/orange, e.g. #d85a30). Value label at each bar end
  ("+0.103" / "−0.107", 3 dp, unicode minus). Keep the tiny maintenance bar (shows it is negligible).
- x-axis label: "Δ Eₐ from enzyme mean (<unweighted_mean> eV)  →  organism Eₐ = <Ea_org> eV" using the
  ACTUAL numbers. Symmetric-ish x-limits with padding so all bars + labels fit. Concise title (the
  report caption carries the detail). Clean, publication-style, good dpi.
- Implement as a function (e.g. plot_ea_signed_contributions(components, out_path)) that takes the
  decomposition dict, so it also works for the glucose / emergent variants if those figures exist.

REGENERATE:
- Replace the waterfall in the standard ea_dissection output/plot path so the pipeline now emits the
  signed-contribution figure. Save as strains/eciML1515/outputs/ea_dissection/ea_signed_contributions.png
  (rich BHI, tuned). If glucose/emergent waterfalls were also produced, regenerate those too with the
  new design. You may remove the old ea_waterfall.png or leave it, but the signed-contribution figure
  is now the canonical Ea-decomposition figure — note the filename in the summary. Update NOTE.md's
  figure reference if it names the waterfall.

RE-RENDER THE REPORT IF IT ALREADY EXISTS:
- If reports/activation_energy/ has already been drafted, update its assemble.py / figure reference to
  the new ea_signed_contributions.png (drop the old waterfall), re-run reports/activation_energy/
  assemble.py, and `quarto render` the report so the PDF shows the signed-contribution figure. If the
  report does not exist yet, skip this — the report-draft prompt already references the new figure.

VERIFY (report all)
1. The four signed contributions are DERIVED from the components (control weighting = control-weighted
   − unweighted mean), and close: unweighted_mean + Σ ≈ Ea_org (print the residual of the check).
2b. If the activation_energy report exists, it was re-assembled + re-rendered and its PDF shows the
   signed-contribution figure (not the waterfall).
2. ea_signed_contributions.png produced (rich BHI, tuned): horizontal, zero baseline, sign-coloured,
   value-labelled, x-axis referencing enzyme mean → Ea_org with the actual numbers.
3. Canonical Ea-decomposition figure is now the signed-contribution one; NOTE.md updated if needed; no
   analysis/model changes, no re-run.

CONSTRAINTS
- Plotting + figure regeneration only. Derive values from the existing decomposition; no hardcoded
  numbers; no re-analysis.
- Autonomous; commit: "ea_dissection: replace Ea-decomposition waterfall with signed-contribution bar (deviations from the enzyme mean)".
```
