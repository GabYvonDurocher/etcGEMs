# Claude Code prompt — M5-redo / finalize: confirm the methanogen Ea decomposition on the sectored (symmetric) model and consolidate the final E. coli-vs-methanogen comparison assets for the paper (autonomous)

Run from the project root (`.../MICROADAPT/etcGEMs`). LIGHT: the M6 sector layer is exactly neutral
(TPC identical, allocation buffer +0.000), so the M5 methanogen decomposition numbers should be
unchanged — this confirms that and produces ONE consolidated symmetric cross-organism comparison for
the write-up. Reuse the saved control coefficients where the binding constraint is unchanged; only
recompute if the sector partition shifted which constraint binds. No re-calibration.

NOTE TO USER: launch in an auto-approving mode, from the venv with Gurobi. Light unless the binding
constraint shifted.

CONTEXT: methanogen on the SECTORED model (proteome_sectors.enabled: true; flat growth law per Müller
2021). M6 verified neutral (max|Δmu|=0; measured allocation buffer = SS-E(GL on) − SS-E(GL off) =
+0.000 vs E. coli −0.130). M5 decomposition (single pool): naive 0.512 + control +0.343 + allocation
0.000 + maintenance −0.016 + aggregation +0.218 = 1.056. E. coli (sectored): naive 0.872 + control
+0.106 + allocation −0.130 + maintenance +0.005 + aggregation −0.175 = 0.68.

---

```
Work AUTONOMOUSLY; commit in parts; print a summary. Read first: strains/mmaripaludis/outputs/
{M5..., M6_sector_layer.md, ea_dissection_ss/}, strains/eciML1515/outputs/ea_dissection_ss/,
outputs/ea_cross_organism/ (the M5 comparison), src/etcgem/{ea_dissection.py, sharpe_schoolfield.py,
sectors.py}. Gurobi (GLPK-abort guard); SS-E throughout; methanogen SECTORED model.

PART A - confirm the decomposition on the sectored model
- On the SECTORED methanogen, verify the binding constraint is unchanged vs the single pool (does the
  metabolic sector cap now bind instead of the total pool?). If UNCHANGED, reuse the saved control
  coefficients and confirm the M5 decomposition is numerically identical; report the (now MEASURED,
  not assumed) allocation term = +0.000. If the binding constraint SHIFTED, recompute the control
  coefficients on the sectored model and report the (small) changes. Either way, report the final
  methanogen SS-E decomposition on the symmetric footing.

PART B - consolidate the final symmetric comparison (paper assets)
- Produce ONE clean cross-organism comparison, both organisms on the SAME 4 named terms + naive mean,
  both with a sector/growth-law layer (E. coli scaling law; methanogen flat, per Müller 2021):
  * a comparison TABLE: per organism — naive enzyme-E mean, control-weighting, allocation, maintenance,
    aggregation, = organism SS-E; plus observed SS-E and model-vs-observed.
  * a comparison FIGURE: the two decompositions side by side (signed-contribution style), making the
    control (+0.24) and allocation (−0.13 vs 0) differences visually obvious.
  * carry the Mcr 3-294/s sensitivity note (ordering + backbone robust; leading enzyme not).
- Save under outputs/ea_cross_organism/ (final versions; keep the M5 originals). Update NOTE.md: the
  symmetric decomposition, the allocation asymmetry now GROUNDED in each organism's measured allocation
  strategy (E. coli growth-law scaling vs methanogen constant-ribosome, Müller 2021), the robust
  bottom line (control + allocation, not aggregation), and the caveats.

PART C - GO to write up
- State that the cross-organism comparison is final and symmetric, list the paper-ready assets (table,
  figure, the two decompositions, the Mcr sweep), and GO to write the comparison paper.

VERIFY (report all)
0. solver=gurobi; methanogen sectored model; SS-E.
1. Binding constraint checked; decomposition confirmed on the sectored model (reused C_i if unchanged,
   recomputed if shifted); the MEASURED allocation term (+0.000) reported vs E. coli (−0.130).
2. Final symmetric comparison table + figure produced (both organisms, same 4 named terms + naive
   mean + observed); model-vs-observed for each; Mcr sensitivity carried.
3. outputs/ea_cross_organism/ finalised + NOTE updated (allocation asymmetry grounded in each
   organism's measured allocation strategy); GO to write up.

CONSTRAINTS
- Light confirmation + consolidation. Reuse saved C_i unless the binding constraint shifted; no
  re-calibration; SS-E throughout. Keep M5 originals.
- Autonomous; commit in parts: "methanogen M5b: confirm Ea decomposition on the sectored model (measured allocation term)",
  "methanogen M5b: finalise the symmetric E. coli-vs-methanogen comparison (table + figure + NOTE)".
```
