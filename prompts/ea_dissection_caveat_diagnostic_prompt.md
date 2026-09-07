# Claude Code prompt — Ea-dissection diagnostic: close the two caveats (acpP/carrier-protein hub in the pathway attribution; the homogenisation -> 1.32 result) on the tuned model, before deciding on the activation-energy write-up (autonomous)

Run from the project root (`.../MICROADAPT/etcGEMs`). DIAGNOSTIC + possible attribution refresh only.
Reuses the existing `ea_dissection` machinery on the TUNED model. Does NOT build the Quarto report,
change model defaults, or re-run the Bayesian. Growth only; Gurobi.

NOTE TO USER: launch in an auto-approving mode, from the venv with Gurobi.

CONTEXT: the E. coli Ea dissection is done (strains/eciML1515/outputs/ea_dissection/): Ea_org = 0.909
eV on the tuned model, decomposed as control-weighted mean Ea_i 0.970 − allocation 0.107 − maintenance
0.010 + residual 0.057 = 0.909. Two caveats must be closed before the write-up:
(1) the top pathway contributions are lipid/fatty-acid synthesis (fabB, acpP, fadA) and glycolysis
    (gapA, eno) — and acpP (P0A6A8) is the SAME shared acyl-carrier-protein hub that inflated the
    earlier per-enzyme thermal-control analysis. Is the lipid dominance real (genuine enzymes) or an
    acpP artefact?
(2) homogenising to uniform kinetics RAISED Ea_org to 1.32 eV — large and counterintuitive. Is that a
    real allocation/network transformation, or a numerical/edge artefact?
Keep the non-circularity framing: Ea_i are inputs; results are the aggregation and departures.

---

```
Work AUTONOMOUSLY; commit in parts; print a summary. Read first: src/etcgem/ea_dissection.py (the
Ea_org / Ea_i / control-coefficient / MCA / homogenisation code), src/etcgem/control.py (per-enzyme
perturbation harness), strains/eciML1515/outputs/ea_dissection/ (summary.json, per-enzyme CSVs,
by-COG table, NOTE.md), reports/ecoli_tpc/assets/tables/thermal_control_annotated.csv (gene/enzyme
identities incl. acpP=P0A6A8), and providers.py (the four O2 sinks are now closed by default). Use
Gurobi with a GLPK-abort guard; print the solver. Operate on the TUNED model at rich BHI (the
dissection baseline), also glucose-minimal where noted.

PART 0 - confirm the substrate
- Confirm: solver=gurobi; O2 sinks closed by default; tuned (v3 posterior-median) model at rich BHI;
  Ea_org reproduces 0.909 (same window/descriptor) before diagnosing. If not, STOP and report.

PART A - CAVEAT 1: is the lipid-synthesis dominance real, or the acpP carrier-protein hub?
- Quantify the hub: report acpP (P0A6A8) — the number of reactions it participates in (its "degree"),
  its growth control coefficient C_i, and its Ea contribution C_i*Ea_i. State how much of the
  lipid-metabolism COG contribution (+0.28) is acpP ALONE vs the genuine catalytic enzymes (fabB,
  fadA, and the rest).
- Re-attribute WITHOUT the carrier: recompute the pathway / by-COG Ea contributions with acpP (and any
  other pure carrier/ACP-type entries) EXCLUDED from the enzyme set (or with its shared cost properly
  distributed across its reactions rather than concentrated on one pseudo-enzyme). Report the top
  enzymes and the by-COG ranking WITH vs WITHOUT acpP.
- Verdict: does lipid/fatty-acid synthesis still dominate via genuine enzymes (fabB, fadA, ...), or
  does the lipid signal collapse to acpP? State plainly which, so the paper can either claim the
  lipid finding robustly or caveat it. (Do the same quick check at glucose-minimal.)

PART B - CAVEAT 2: understand the homogenisation -> 1.32 eV
- State exactly what "homogenise" did in the code (e.g. set every enzyme's Topt_i and dCp_i — hence
  Ea_i — to common/mean values), and report the COMMON Ea_i that all enzymes were set to.
- Compare Ea_org(homogenised)=1.32 to that common Ea_i. If they differ, the network/allocation is
  transforming a uniform enzyme Ea into a different organism Ea — DECOMPOSE the homogenised case with
  the same MCA (control-weighted term + allocation + maintenance + residual) to show WHAT pushes it to
  1.32.
- Rule out edge effects: confirm the growth law is still ON; confirm the rising-limb window / Topt did
  not shift under homogenisation (if all Topt_i are set equal, the peak sharpens and the window may
  move into a steeper region — check and report whether that is the cause); confirm the descriptor is
  computed identically to the heterogeneous case.
- Verdict: is 1.32 a meaningful "uniform kinetics + allocation give a higher Ea, so heterogeneity
  LOWERS the organism Ea" result, or an artefact of a shifted window / changed binding set? State
  which, with the numbers.

PART C - outputs (no report build)
- Write strains/eciML1515/outputs/ea_dissection/DIAGNOSTIC_NOTE.md: the acpP verdict (with the
  with/without-acpP top-enzyme + COG rankings) and the homogenisation verdict (common Ea_i, the
  decomposition of the 1.32 case, and the edge-effect checks). If the acpP re-attribution changes the
  headline pathway story, save the corrected by-COG / top-enzyme table + figure alongside the
  originals (do NOT overwrite; suffix e.g. `_no_carrier`).
- Do NOT build the Quarto report; do NOT change model defaults or the ea_dissection defaults.

VERIFY (report all)
0. solver=gurobi; O2 sinks closed; tuned model reproduces Ea_org 0.909 before diagnosing.
1. acpP hub quantified (degree, C_i, C_i*Ea_i); lipid COG contribution split acpP-alone vs genuine
   enzymes; by-COG + top-enzyme rankings WITH and WITHOUT acpP; clear verdict (robust vs artefact),
   at rich BHI and glucose.
2. Homogenisation explained: the common Ea_i stated; Ea_org(homog)=1.32 decomposed; growth-law-on and
   window/Topt-shift edge checks reported; clear verdict (real vs artefact).
3. DIAGNOSTIC_NOTE.md written; corrected tables/figures saved with a suffix if the attribution changed;
   no report built, no model-default changes, no Bayesian re-run.

CONSTRAINTS
- Diagnostic + optional attribution refresh only, on the TUNED model. Reuse ea_dissection; no new
  model behaviour. Non-circularity framing preserved.
- Report ACTUAL numbers and give explicit verdicts on both caveats.
- Autonomous; commit in parts: "ea_dissection diagnostic: acpP carrier-protein hub in the Ea attribution (with/without-carrier re-attribution)",
  "ea_dissection diagnostic: explain the homogenisation->1.32 result (decompose + edge checks)",
  "ea_dissection: DIAGNOSTIC_NOTE + corrected attribution tables/figures (if changed)".
```
