#!/usr/bin/env python3
"""S1 TASK 1 — the evidence base.

One row per claim the synthesis document makes: the number, the file it came from, the commit
that last wrote that file, and its status. The commit and date are looked up from git, not
typed, so a stale citation cannot survive a re-run.

    python reports/synthesis/build_evidence.py    ->  reports/synthesis/evidence.csv

STATUS
  CURRENT             reproduces from the code as it stands, or is a measurement/citation
  HISTORICAL          a record of an earlier model state (still true of that state)
  PROVISIONAL-ON-P6   depends on a run that has not finished; the slot for the converged value
                      is named in the document's "how to update" section
  SUPERSEDED          recorded because the disagreement is itself a finding
"""
import csv
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))

# id | claim | value | source file | status | note
E = [
 # ---- 1. where things stood -------------------------------------------------
 ("W1", "Two implementations of the etcGEM idea existed, with no shared core", "2",
  "docs/CANDIDA_ETCGEM_PLAN.md", "CURRENT", "the scoping document that set the merge rule"),
 ("W2", "Organisms on the shared core before the merge", "3 (E. coli, M. maripaludis, Synechocystis)",
  "docs/CANDIDA_ETCGEM_PLAN.md", "CURRENT", ""),
 ("W3", "Organisms on the shared core after K1 and P1", "7", "reports/candida_thermal_limit/K1_port_verification.md",
  "CURRENT", "four Candida strains added as data-only folders"),

 # ---- 2. the merge and its gates -------------------------------------------
 ("G1", "K1 port gate against the standalone Candida implementation", "79 comparisons, 79 PASS, 0 FAIL",
  "reports/candida_thermal_limit/gate_table.csv", "CURRENT", "re-run green at every merge since"),
 ("G2", "P1 gate, Parsa's configurations A/B/C", "60 comparisons, 60 PASS, 0 FAIL",
  "reports/P1_parsa_port/gate_table.csv", "CURRENT", "T_opt exact in all 12 medium x config cases"),
 ("G3", "P1 gate worst relative difference on any quantity", "8.3e-4",
  "reports/P1_parsa_port/gate.md", "CURRENT", ""),
 ("G4", "P3 gate, configurations D/E/F against experiment: R2 values reproduced", "10 of 10, worst 0.009",
  "reports/P3_gate/gate_def_headline.csv", "CURRENT",
  "as a PORT check; the respiration half is qualified by EF1"),
 ("G5", "Parsa's v3 posterior is identical to the one committed here", "13 of 13 medians, every stored digit",
  "reports/P1_parsa_port/PARTA_inventory.md", "CURRENT", ""),

 # ---- 3. uncosted shortcuts -------------------------------------------------
 ("S1", "E. coli: uncosted O2-sink reactions closed by default", "4 (QMO2, QMO3, MOX, CU1Opp); ~-0.3% growth",
  "src/etcgem/providers.py", "CURRENT", "Parsa's audit; adopted as a provider default at 8085036"),
 ("S2", "Candidozyma: fraction of ATP synthase's proton draw the respiratory chain supplies",
  "0.04-0.05% (three strains) vs 112% C. parapsilosis, 124% E. coli",
  "reports/K5_respire/task1_translocators.csv", "CURRENT", "class-E audit, all seven strains"),
 ("S3", "The separating feature of the defect", "reversibility, not uncostedness",
  "reports/K5_respire/report.md", "CURRENT",
  "E. coli has 12 uncosted proton movers, none reversible; Candidozyma 9-15, reversible"),
 ("S4", "Growth cost of repairing the Candidozyma proton circuit", "36-38%",
  "reports/K5_respire/task2_fix_comparison.csv", "CURRENT", "direction constraint, not costing"),
 ("S5", "Complex III wired backwards in the three iRV973-derived models", "R02161__mito, 1.5 H+ the wrong way",
  "docs/OPEN_ITEMS.md", "CURRENT", "item 3.13; found by K5, in the published reconstruction"),
 ("S6", "The audit blind spot", "no class watched the coupling ion until class E",
  "src/etcgem/sink_audit.py", "CURRENT",
  "a free proton circuit passed an audit reporting 44-47 class-A hits in the same models"),
 ("S7", "M. maripaludis coupling ion", "Na+, not H+",
  "reports/K5_respire/task1_audit.md", "CURRENT", "inferring it per strain was required for the audit to be right"),

 # ---- 4. the predictors -----------------------------------------------------
 ("A1", "Seq2Tm across the tree of life", "r = +0.762",
  "reports/predictor_calibration/report.md", "CURRENT", "between-organism thermophily"),
 ("A2", "Seq2Tm within one proteome, against measurement", "r = -0.048 on 1947 S. cerevisiae proteins",
  "reports/predictor_calibration/report.md", "CURRENT", "Meltome Atlas, Jarzab 2020"),
 ("A3", "Seq2Tm under-states a measured congeneric difference", "17-fold",
  "reports/predictor_calibration/report.md", "CURRENT", "S. cerevisiae vs S. uvarum, summary-to-summary"),
 ("A4", "Mean Seq2Tm bias", "+5.43 C",
  "reports/K8_tm_bias/task1_bias.csv", "CURRENT", "A1's measurement, re-used by K8"),
 ("A5", "The bias is not uniform", "+1.06 C per C of predicted Tm; +2.44 C lowest octile to +12.78 C highest",
  "reports/K8_tm_bias/task1_bias.csv", "CURRENT", ""),
 ("A6", "Measured Tm vs predicted Tm slope", "-0.061",
  "reports/predictor_calibration/report.md", "CURRENT", "almost all predicted spread is error"),
 ("A7", "Figure 4's fold gap, published vs A1-corrected", "~79x -> 5.4x [2.5, 10.3]",
  "reports/predictor_calibration/report.md", "CURRENT", "still a failure, a different sentence"),
 ("A8", "Per-protein measured S. cerevisiae/S. uvarum Tm", "NOT OBTAINED",
  "reports/predictor_calibration/DATA_PROVENANCE.md", "CURRENT", "the stronger paired test cannot be computed"),

 # ---- 5. what sets a thermal curve -----------------------------------------
 ("T1", "T_opt is relocated by the sector re-grounding", "37 -> 30 C (then 31 with the growth law)",
  "reports/N2_followups/TASK1_stale_eciML1515_tpc.md", "HISTORICAL", "commit a416fd1"),
 ("T2", "T_opt is relocated by the translation cap", "T_opt sits where the cap starts to bind",
  "reports/N3_output_audit/TASK2_cap_regime.md", "CURRENT", ""),
 ("T3", "T_opt is relocated by a total-carbon cap", "39.0 -> 32.5 C on NLDM between c_max 80 and 60",
  "reports/P2_settle/task3_cmax_table.csv", "CURRENT", ""),
 ("T4", "CT_max is insensitive to all three", "<=0.91% at c_max 40; unmoved by the cap regime",
  "reports/P2_settle/task3_cmax_table.csv", "CURRENT", ""),
 ("T5", "The standing rule that follows", "T_opt is quoted with its binding constraint named; CT_max may be quoted plainly",
  "docs/QUOTING_DESCRIPTORS.md", "CURRENT", ""),
 ("T6", "The 37-44 C bit-identical shoulder", "growth exactly 0.524757 /h across 8 grid points",
  "reports/ecoli_tpc/report.qmd", "CURRENT", "the Glucose proteome ends at 37 C"),
 ("T7", "Model growth envelope too steep against measurement", "1.24-2.29x, all four Candida species",
  "reports/K7_envelope/task2_envelope.csv", "CURRENT", "structural: barely moves between configurations"),
 ("T8", "Most of the envelope error is the dCp prior", "~88% of the residual gap",
  "reports/K7_envelope/task3_dcp_sweep.csv", "CURRENT", ""),
 ("T9", "The same dCp cannot also close the ceiling", "pushes it slightly the wrong way",
  "reports/K7_envelope/report.md", "CURRENT", "two failures, not one with one cause"),

 # ---- 6. the Candida figure's arithmetic -----------------------------------
 ("F1", "Required Tm separation, as published (standalone)", "32.5 C",
  "reports/candida_thermal_limit/standalone_expected.json", "HISTORICAL", "K1 reproduces it exactly"),
 ("F2", "Required Tm separation, under the core's thermal form (K2)", "13.8 C",
  "reports/candida_thermal_limit/K2_core_thermal_form.md", "HISTORICAL", ""),
 ("F3", "Required Tm separation, after the K5 repair (B5)", "13.57 C",
  "reports/K7_envelope/task1_conventions.csv", "CURRENT", "and convention-independent"),
 ("F4", "Growth convention makes no difference to the requirement", "0.00 C on B5 (0.07 C on B3)",
  "reports/K7_envelope/task1_conventions.csv", "CURRENT",
  "the counterfactual never reads the predicted strain's measured curve"),
 ("F5", "Measured congeneric Tm difference (the benchmark)", "1.6 C over 827 ortholog pairs",
  "reports/predictor_calibration/report.md", "CURRENT", "Walunjkar 2025, S. cerevisiae vs S. uvarum"),
 ("F6", "The ceiling criterion's INTERSPECIES requirement is arithmetic",
  "model CT_max spread varies 4.5x; required-offset spread moves +/-3%, pinned to the observed 6.00 C",
  "reports/K9_criterion/task1_offsets_by_model.csv", "CURRENT",
  "so it must not be set beside the measured 1.6 C"),
 ("F7", "The ~5.6 K common ceiling term does not generalise", "residuals 0.05-10.48 C across strains",
  "reports/K9_criterion/task3_seven_strain.csv", "CURRENT", "E. coli's 5.6 K is a one-organism observation"),
 ("F8", "Ceiling gap closed by applying A1's measured bias", "a third to a half, all four species",
  "reports/K8_tm_bias/task2_corrections.csv", "CURRENT", "at exactly the measured bias, untuned"),
 ("F9", "Full ceiling closure would need", "1.8-2.8x the measured bias, differing by 5 C between species",
  "reports/K8_tm_bias/task3_offset_sweep.csv", "CURRENT", "no uniform predictor bias can produce that"),
 ("F10", "Model CT_max spread vs observed", "1.6 C model against 6 C observed",
  "reports/K8_tm_bias/task1_ceiling_vs_tm.csv", "CURRENT", "the variation in the gap is almost entirely observational"),

 # ---- 7. membrane area ------------------------------------------------------
 ("M1", "ETC membrane-area mechanism gated on E. coli", "config E respiration R2 0.72, config F 0.96",
  "reports/P3_gate/gate_def_headline.csv", "CURRENT", "as a port check; see EF1"),
 ("M2", "Alternative oxidase in the Candida models", "in all four proteomes, in none of the four models",
  "reports/K4_membrane/task1_etc_complement.py", "CURRENT", "confirmed by EC, name and chemistry search"),
 ("M3", "The area constraint cannot carry the Candida comparison", "two independent reasons, one structural one parametric",
  "reports/K4_membrane/report.md", "CURRENT", "available and not tested"),
 ("M4", "Membrane re-test with both escape routes closed", "122-fold, still the wrong direction",
  "reports/K5_respire/task3b_membrane_retest.md", "CURRENT", ""),

 # ---- 8. E. coli gas flux ---------------------------------------------------
 ("C1", "c_max adopted from Parsa's own sweep", "120 (his 'C_max ~ 100-120 is the sweet spot')",
  "strains/eciML1515/gas_exchange.yaml", "CURRENT", "60, his figure's value, sits past the T_opt transition"),
 ("C2", "At c_max = 60 acetate overflow is zero on both media", "0.0",
  "reports/P2_settle/task3_cmax_table.csv", "CURRENT", "the cap suppresses the mechanism config D exists to produce"),
 ("C3", "Applying 120 to LB collapsed the LB growth fit", "R2 0.83-0.90 -> 0.16-0.20",
  "reports/P4_refit/refit_comparison.csv", "CURRENT", "c_max confirmed as the cause in P5"),
 ("C4", "His own LB fits chose", "257 / 459 / 510",
  "reports/P5_lb_cmax/parsa_lb_cmax.csv", "CURRENT", "read at source from his chains"),
 ("C5", "LB cap now set to", "450 (his E/F nominal), scoped in the strain file",
  "strains/eciML1515/gas_exchange.yaml", "CURRENT", ""),
 ("C6", "The NLDM medium clearance K is not identified", "posterior/prior width 0.57-0.64",
  "reports/P4_refit/refit_posteriors.csv", "PROVISIONAL-ON-P6", "on under-converged chains; P6 D3 does not affect config D"),
 ("C7", "Configuration C's NLDM RQ, blanket vs recipe medium", "~7-9 -> 1.04",
  "reports/P2_settle/task2_nldm_table.csv", "CURRENT", "the mover is the medium, not the cap"),
 ("C8", "M9 growth fits (first light)", "R2 0.959 / 0.987 / 0.982 (D/E/F)",
  "reports/P4_refit/refit_comparison.csv", "PROVISIONAL-ON-P6", "under-converged; E and F additionally hit EF1"),

 # ---- 9. sampling -----------------------------------------------------------
 ("P1", "P4's nine refits: convergence", "none converged; tau 146-245, chain/tau 6-12 against >=40",
  "reports/P4_refit/refit_comparison.csv", "CURRENT", ""),
 ("P2", "Parsa's six committed chains, same estimator", "tau 160-214, chain/tau 8.2-9.4, n_eff 148-170",
  "reports/P4_refit/TASK3_what_moved.md", "CURRENT", "neither family is converged"),
 ("P3", "Cost of reaching the criterion", "~8000 steps, ~40 h for all nine",
  "reports/P4_refit/TASK3_what_moved.md", "CURRENT", ""),
 ("P4", "The gas-flux warm start can seed every walker in a dead mode", "one chain trapped; answers nothing",
  "docs/OPEN_ITEMS.md", "CURRENT", "item 3.20; P4 repaired it, P5 ran it once at scale"),
 ("EF1", "Configurations E and F: the respiration likelihood is not a function of the parameters",
  "log-likelihood spread 0.13-7.49 at a fixed vector, against a posterior width of ~7",
  "reports/P6_convergence/DECISIONS.md", "PROVISIONAL-ON-P6",
  "on branch p6/convergence, not main. O2 uptake at optimal growth is degenerate; the vertex "
  "depends on the previous solve. Config D is unaffected (jitter <=0.0004)"),

 # ---- 10. process findings --------------------------------------------------
 ("R1", "Reports that no longer reproduce, of the eleven the E. coli report renders from", "8 of 11",
  "reports/N3_output_audit/report.md", "CURRENT", "two causes: a416fd1 and 8085036"),
 ("R2", "The standing fix adopted", "a generated provenance stamp on every report",
  "scripts/stamp_reports.py", "CURRENT", "--check fails if any is stale"),
 ("R3", "Defects introduced by this project's own runs", "4 named",
  "reports/synthesis/evidence.csv", "CURRENT", "rows O1-O7 of this table"),

 # ---- 11. the reference implementation ---------------------------------------
 ("Y2", "T_opt/CT_max asymmetry at Li et al.'s CALIBRATED posterior, over their own 100 models",
  "99 % plateau widens 1.5 C [0.4, 2.7] -> 7.3 C [1.4, 7.5] under the substrate cap, in 93 % of "
  "posterior models; CT_max moves 4.6 C [2.7, 11.0]; T_opt moves 8.9 C [4.4, 27.0], a lower bound "
  "in 44 of 98",
  "reports/Y2_regime_posterior/report.md", "CURRENT",
  "medians with 5-95 percentiles across their 100 posterior particles, run with their own etcpy. "
  "Y1's 10.09/0.81 C is the PRIOR point table and is not a property of their calibrated model: at "
  "the posterior median it is 8.46/4.27 C. Quote the plateau, not T_opt -- under a substrate cap "
  "the top of the curve is a ceiling, not a peak."),
 ("Y3a", "Profile likelihood of dTm with catalysis free, from p38 (E. coli, config D NLDM)",
  "dTm = 0 costs 0.077 log L units and the model still grows at 1.739 /h; the whole 4.02 K profile "
  "spans log L -6.84 to -7.45",
  "reports/Y3_tm_shift/report.md", "CURRENT",
  "the compensator is tm_scale (0.990 -> 1.467), a Tm-distribution parameter, NOT catalysis: with "
  "tm_scale pinned to 1 the meltome-honouring fit converges 7.60 units worse (log L -14.786, "
  "growth 1.659 /h) against two prior ceilings. Both solutions put the 1st percentile of Tm at "
  "36.7-38.7 C against 42.6 C measured"),
 ("Y3b", "Y3 verdict on the -4 K dTm shift", "PARAMETERISATION, by the rule fixed before the data",
  "reports/Y3_tm_shift/report.md", "CURRENT",
  "narrower than the label: the VALUE -4 K is a parameterisation artefact (dTm and tm_scale are "
  "not jointly identified), the contradiction with the meltome's LOW TAIL is not. Per-enzyme "
  "catalysis cannot pay for it, so the DLTKcat route is recommended against -- its own output has "
  "36 interior thermal optima in 1149 fits. Screens R3 only; licenses nothing about Candida"),
]

OWN = [
 ("O1", "N2's rescaling default broke every gecko strain with sectors", "reports/N3_output_audit/DECISIONS.md",
  "caught by N3 TASK 0's verification before the merge was pushed; fixed in a467d23"),
 ("O2", "cli.main returned the output path into sys.exit(), so every successful run exited 1",
  "reports/N3_output_audit/DECISIONS.md",
  "long-standing; it made a verification pass silently vacuous (`cmd && check` skipped the run)"),
 ("O3", "P1 wired the wrong ETC table as configuration F", "reports/P3_gate/gate.md",
  "the Bekker-turnover table in his configF.py produced no reported number; his fits use E's"),
 ("O4", "P3's first gate run left an overlay's carbon cap on, so E and F silently carried a cap they were never fitted with",
  "reports/P3_gate/DECISIONS.md", "made NLDM look irreproducible (respiration R2 -2.5); fixed before any conclusion"),
 ("O5", "P4's warm start failed silently in all nine fits", "reports/P4_refit/DECISIONS.md",
  "wrong worker globals; chains started at the emergent point, lengthening burn-in"),
 ("O6", "K5's activation-energy sign result did not stand", "reports/K6_like_for_like/report.md",
  "a comparator artefact: two measured E are not the same quantity (OLS vs Sharpe-Schoolfield)"),
 ("O7", "K9 corrected its own prompt's headline table", "reports/K9_criterion/report.md",
  "the interspecies requirement is arithmetic; the '~5 C within threefold of 1.6 C' sentence is not available"),
]

DISAGREE = [
 ("D1", "Measured Candida growth activation energy", "OLS 0.01-0.35 eV vs Sharpe-Schoolfield 0.62-1.15 eV",
  "reports/K6_like_for_like/task1_measured_E.csv",
  "Sharpe-Schoolfield is authoritative: the OLS fit runs a straight line through a curve that "
  "turns over. Empirical test: refitting OLS on the rising limb moves it toward the Bayesian "
  "value, and E_resp (no turnover) agrees between methods to 0.518 vs 0.518."),
 ("D2", "C. haemulonii growth at 40 C", "0.000 /h (zeros) vs 0.66 /h (survivors)",
  "reports/K7_envelope/task1_conventions.csv",
  "Neither is authoritative for Figure 4 because neither enters it: the counterfactual makes "
  "zero calls to the predicted strain's measured curve. Requirement differs by 0.00 C on B5."),
 ("D3", "Configuration C NLDM respiratory quotient", "~7-9 (his report) vs 1.04 (recipe medium) vs 12.8->0.46 (baseline model)",
  "reports/P4_refit/TASK3_what_moved.md",
  "All three are correct and are three different quantities; reconciled in P4 TASK 3. The "
  "mover is the medium in every case, not the carbon cap."),
 ("D4", "c_max for E. coli", "60 (his figure) vs 120 (glucose/NLDM sweep) vs 450 (LB)",
  "strains/eciML1515/gas_exchange.yaml",
  "Medium-dependent, and that is the resolution: 120 is a glucose/NLDM recommendation, 450 is "
  "his own LB nominal. Applying 120 to LB was P4's error and P5 corrected it."),
 ("D5", "Required Tm separation for Figure 4", "32.5 C (published) vs 13.8 C (K2) vs 13.57 C (B5)",
  "reports/K7_envelope/task1_conventions.csv",
  "Each is correct for its model state; the sequence is the finding. B5 is the current model."),
]


def last_commit(path):
    r = subprocess.run(["git", "-C", ROOT, "log", "-1", "--format=%h|%ad", "--date=short",
                        "--", path], capture_output=True, text=True)
    out = r.stdout.strip()
    return out.split("|") if out else ["(not on this branch)", ""]


def main():
    rows = []
    for cid, claim, value, src, status, note in E:
        h, d = last_commit(src)
        exists = os.path.exists(os.path.join(ROOT, src))
        rows.append(dict(id=cid, kind="claim", claim=claim, value=value, source_file=src,
                         source_exists=exists, commit=h, commit_date=d, status=status, note=note))
    for cid, claim, src, note in OWN:
        h, d = last_commit(src)
        rows.append(dict(id=cid, kind="own-defect", claim=claim, value="", source_file=src,
                         source_exists=os.path.exists(os.path.join(ROOT, src)),
                         commit=h, commit_date=d, status="CURRENT", note=note))
    for cid, claim, value, src, note in DISAGREE:
        h, d = last_commit(src)
        rows.append(dict(id=cid, kind="disagreement", claim=claim, value=value, source_file=src,
                         source_exists=os.path.exists(os.path.join(ROOT, src)),
                         commit=h, commit_date=d, status="RECORDED", note=note))
    out = os.path.join(HERE, "evidence.csv")
    with open(out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    n = len(rows)
    by = {}
    for r in rows:
        by[r["status"]] = by.get(r["status"], 0) + 1
    missing = [r["id"] + " -> " + r["source_file"] for r in rows if not r["source_exists"]]
    print(f"wrote {os.path.relpath(out, ROOT)}: {n} rows")
    for k, v in sorted(by.items()):
        print(f"  {k:20s} {v}")
    print(f"  of which disagreements recorded: {sum(1 for r in rows if r['kind']=='disagreement')}")
    print(f"  own-defect rows:                 {sum(1 for r in rows if r['kind']=='own-defect')}")
    if missing:
        print("\nsource files NOT on this branch (expected only for P6 rows):")
        for m in missing:
            print("  -", m)
    return 0


if __name__ == "__main__":
    sys.exit(main())
