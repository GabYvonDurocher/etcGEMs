# Open items — the running list

_Started 2026-09-08 while P2 was running; last updated 2026-09-09 by Y2._ This is the standing list of what is outstanding across
the whole project, so nothing is lost between sessions. Update it when something lands; do not let
it become a second decision log — decisions live in each prompt's `reports/*/DECISIONS.md`, this is
only what is NOT yet done and who or what it waits on._

Status: **BLOCKED** (waiting on something external) · **READY** (can start now) · **PENDING P2**
(depends on the run in flight) · **DEFERRED** (deliberately not now, with a trigger)

---

## 0. Sequencing — E. coli first (decided 2026-09-09)

- **The E. coli model (`eciML1515`) is the best-constrained**: three media, gas exchange, a
  measured meltome. Methods are developed and proven there first, then ported through the core.
  The seven-strain gate (K1, 79/79) runs on every core change so the other strains cannot
  silently break meanwhile.
- **Order on E. coli:** (1) the sampling problem — P8; (2) the E/F tie-break on the LP face
  (1.13, PI); (3) the −5.6 K Tm shift — whether a Li-style per-enzyme calibration against the
  meltome removes it (1.14 generalised to E. coli, where the data exist); (4) the CT_max
  disagreement with the yeast posterior (Y2) — definition first, then mechanism.
- **Candida:** the K-series result (13.57 °C required against 1.6 °C measured, and why) stands
  and is what the manuscript uses. No further Candida modelling until the E. coli calibration
  recipe exists; then it ports against the measured TPCs.
- **Cross-taxon questions already answered** (activation energies K6, seven-strain ceiling K9)
  stay on record and are not re-opened by this.

## 1. Waiting on people

| # | Item | Waiting on | Why it matters |
|---|---|---|---|
| ~~1.1~~ | ~~**E. coli respirometry**~~ | — | **CLOSED 2026-09-08 (P3).** Arrived as two full pipeline runs (R2A/LB and M9), ingested at `strains/eciML1515/respirometry/`. Configs D, E and F are now **gated**: all ten R² values reproduce, worst 0.009. |
| ~~1.2~~ | ~~**`c_max = 60`: grounded or fitted?**~~ | — | **CLOSED 2026-09-08 (P3 TASK 4)** — on his own evidence rather than by asking. His report calls the cap a swept boundary condition, not a fit, and his sweep concludes "C_max ≈ 100–120 is the sweet spot". **120 adopted** (the only value in his range at which acetate overflow is non-zero on both media); 60 kept as a labelled sensitivity. |
| ~~1.3~~ | ~~**Confirm recipe ceilings supersede blanket medium**~~ | — | **ACTED ON 2026-09-08/09 (P4).** All nine configurations refitted under recipe ceilings with the clearance K sampled. NLDM is unchanged to better; LB collapses, and the cause is `c_max`, not the medium (1.11). A one-line confirmation from Parsa is still welcome; nothing waits on it. |
| ~~1.4~~ | ~~**Confirm transporter kcat 30 vs 300**~~ | — | **SETTLED 2026-09-08 (P2 TASK 1)** by reproduction: 300 reproduces his figure, 30 does not. Set in the strain data. A one-line confirmation from Parsa would close it formally; nothing waits on it. |
| 1.8 | **Which configuration-F ETC table is intended?** | Parsa | P3 found his fits use configuration **E's** areas and turnovers plus a non-electrogenic bd-II, while the Bekker-turnover table in his `configF.py` was never used for a reported number. The port now matches what he fitted; whether the Bekker table is the intended future form is his call. |
| 1.9 | **Per-cell respiration: N₀ and fg C per cell** | Parsa | The inoculum back-projection is off in every row of both media sets, `cell_volume_um3`/`cell_carbon_fg` are typed constants (2 µm³ / 350 fg), and his own `config.R` log prints 21.21 µm³ / 2120.58 fg — ~6× apart. Growth R² and every scale-free quantity are immune; **respiration R², CUE and absolute per-cell rates are not.** Reported in `strains/eciML1515/respirometry/README.md`, not adjudicated. |
| ~~1.10~~ | ~~**M9: fit or not?**~~ | — | **CLOSED 2026-09-09 (P4 TASK 4).** Fitted for all three configurations — the best growth fits in the exercise (R² 0.96–0.99). OTU 2 (`M9`, 7 non-monotonic rows) was excluded as a control, not a series. |
| ~~1.11~~ | ~~**`c_max` on LB**~~ | — | **ACTED ON 2026-09-09 (P5).** P4 applied the canonical 120 to LB and all three LB growth R² collapsed (0.83–0.90 → 0.16–0.20). His own LB fits chose **257 / 459 / 510**. 120 comes from a glucose/NLDM sweep and no LB sensitivity has ever been run. **One fit settles it: configuration D on LB at c_max ≈ 260, ~45 min.** **Outcome:** confirmed at source (256.7 / 459.3 / 509.9); the one chain was trapped in a dead mode by the warm start (3.20) and the question was answered at fixed parameter points instead — the cap alone moves LB growth R² 0.64 / 0.05 / −0.10 (D/E/F at 120) → 0.90 / 0.83 / 0.88 at his own caps, because 120 holds r_max at 1.1–1.8 against a measured 2.94 h⁻¹. **LB cap set to 450** (`gas_exchange.yaml` `carbon_cap.by_medium.LB`, his E/F nominal); 257 serves D only. Not tested above 450; no LB sensitivity to an unbounded cap exists — that is the remaining trigger. `reports/P5_lb_cmax/`. |
| 1.12 | **Chain length: every fit in this family is under-converged** | us | All nine P4 refits AND all six of Parsa's committed chains run ~9 autocorrelation times (chain/τ 6–12 against ≥40). Reaching the criterion is ~8 000 steps, ≈ 40 h for all nine. Until then no R² from either family is a converged posterior. The warm-start defect that lengthened P4's burn-in is fixed but untested at scale. **UPDATED 2026-09-09 (P6 D6): not a budget problem.** τ grows in proportion to chain length on every configuration-D chain (chain/τ pinned at ~9.7 over 1250 steps; the true τ is unknown and > 300 on all 16 parameters), so more steps have no ceiling — the family is **sampler-limited**, not step-limited. D NLDM halted at step ~1250; D LB and D M9 not started under this sampler. Medians of the twelve data-determined parameters are stable and quotable with a "not converged" label; intervals are not. **UPDATED 2026-09-09 (P7): not a walker-count artefact either.** D NLDM at 128 walkers, otherwise P6's fit exactly, read by a rule written before the run: τ_max 26.1 → 140.8 over 1500 steps, increments 26 → 20 per block (mean of the last three 21.4 against 10 for mixing), chain/τ 9.6–10.7, the carrier rotating — 10 % below the 40-walker curve and no plateau. **NOT MIXING.** The same applies to Parsa's six chains (36 walkers, same sampler). What it now needs is one of P6 D6's decisions — fix the four prior-determined parameters, narrow the discrepancy priors, change sampler, or quote medians only — none of which is compute. `reports/P7_walkers/`. **Awaiting P7** (`prompts/P7_walker_test_prompt.md`), which decides whether D6's options (i)–(iii) are needed. `reports/P6_convergence/DECISIONS.md` D6. |
| 1.13 | **E/F tie-break: pFBA, min-O2 or max-O2 for the respiration likelihood on an LP face** | PI | Modelling decision. O2 uptake at optimal growth is a continuum for configurations E and F (D3a), so the respiration likelihood needs a rule that makes it unique before any E/F fit is sampled again. See 3.21 and `reports/P6_convergence/DECISIONS.md` D3a. |
| 1.14 | **Whether a Li-style calibration is worth attempting** — predictor as wide prior, narrowed against the measured Candida TPCs | PI | Li et al. carried a sequence-predicted Topt as a wide prior (width = the predictor's RMSE) and let the measured curves narrow it. Given the A1 noise floor of 0.043 C between clades, whether the Candida TPCs carry enough signal to narrow anything is the question. See `reports/Y1_yeast_audit/` PART D. |
| 1.5 | **`common_network.py` result** — does the optimum still compress on a common scaffold? | Ilgaz | Never recorded in `gem/notes/`. Note the K1 finding that makes it partly moot: the two draft models ARE the *auris* network with genes reassigned, so the control is near a no-op for them and informative only for *C. parapsilosis*. |
| 1.6 | **Did any Candida audit touch lipid or membrane pathways?** | Ilgaz | Bears on §6a. `allocation_and_trehalose.py` suggests compatible solutes were looked at; membranes unknown. |
| 1.7 | **`15_run_seq2tm.py` truncation bug** — truncates at 1022 aa citing a non-existent ESM-2 positional limit; committed predictions are untruncated, so the script cannot reproduce the data beside it (up to 2.6 °C) | Ilgaz — **told, not yet fixed** | A live reproducibility break in his repository. |

## 2. Ready to start

| # | Item | Notes |
|---|---|---|
| 2.1 | **A3 follow-through: gene content → mechanism** | A3 measured that models see only ~2–5 % of the gene-content difference (0–15 genes in-model vs 122–647 in proteome), and that AOX and the glutaredoxins are in NO model. Nothing has been done with that. |
| ~~2.2~~ | ~~**Membrane-area constraint on Candida**~~ | **DONE 2026-09-08 (K4).** Built and applied; `reports/K4_membrane/report.md`. **It cannot carry the interspecies comparison, for two independent reasons.** Structurally, the respiratory chain is not load-bearing in three of the four models (the three *Candidozyma*; TASK 1), so an area budget there binds on ATP synthase and not on respiration. Parametrically, no footprint differs between the species — there is no Candida or fungal equivalent of Szenk 2017 (TASK 2). The mechanism is **available and not tested**; 3.8-3.11 are what would change that. |
| 2.3 | **K3 — retire the Candidas fork** | N1 prepared the patch (unapplied, `git apply --check` clean) and confirmed nothing in etcGEMs needs `$CANDIDAS_ROOT` at run time now the gate has a fixture. Needs a human to apply it in Ilgaz's repository. |
| 2.4 | **`_toy/resolved_config.yaml`** structurally stale (numbers fine, 6.2e-15) | Listed by N2, not fixed. Trivial. |
| ~~2.5~~ | ~~**PART C at Li et al.'s POSTERIOR, not their prior**~~ | **CLOSED 2026-09-09 (Y2).** Downloaded (10.5281/zenodo.3996543 v2.0, md5 verified) and run at the posterior median and all 100 posterior particles. **The asymmetry survives in direction and is far more consistent at the posterior** — the 99 % plateau widens under the substrate cap in **93 %** of their posterior models (1.5 → 7.3 °C) against 35 % of prior models, and T_opt moves further than CT_max in **92 %** against 50 %. **But the margin narrows and Y1's 10.09 / 0.81 °C must not be quoted as a property of their calibrated model:** at the posterior median it is 8.46 / 4.27 °C, because a substrate cap now drops CT_max from 43.0 to 38.7 °C. Y1's prior run reproduces byte-identically. `reports/Y2_regime_posterior/`. |
| 2.6 | **The shared `.venv` lives in the main checkout** | `etcGEMs/.venv` is the only interpreter, so a second worktree borrows one from a directory a long run may be using. Read-only in practice; harmless so far. If `../etcGEMs-synthesis` becomes standing (Y1 PART F), move the venv somewhere neutral or duplicate it. |
| ~~2.7~~ | ~~**P7 walker test**~~ (`prompts/P7_walker_test_prompt.md`) | **DONE 2026-09-09.** Not a walker-count artefact: NOT MIXING at 128 walkers by the pre-registered rule. D6's options (i)–(iv) are the real menu. See 1.12 and `reports/P7_walkers/`. |

## 3. Deferred, with triggers

| # | Item | Trigger to act |
|---|---|---|
| 3.1 | **Re-run `decompose_tuned` + `elasticity_tuned`** to match `control_tuned`'s model state | When that dissection material is used in a paper. Until then P2 TASK 5 annotates it. |
| 3.2 | **`calibration_vanderlinden`** (4 h 28 min emcee) | When a specific number from it is needed and must be current. |
| 3.3 | **Full E. coli regeneration** | Paper time, and then only the directories that paper uses. Reports are logs; provenance stamps (P2 TASK 4) are the standing fix. |
| 3.4 | **Extend the E. coli proteome above 37 °C** | This is a measurement, not a modelling job. Until then the 37–44 °C bit-identical shoulder is documented as a limitation (P2 TASK 5). |
| 3.5 | **DLTKcat on the four Candida proteomes** | A1 recommended against for now: wrong half of the curve, no benchmark, ~50,000 predictions. Revisit only if the kinetic envelope becomes load-bearing. |
| 3.6 | **Per-protein *S. cerevisiae*/*S. uvarum* Tm from the authors** | Would allow A1's strongest test (correlation of measured against predicted *differences*), currently impossible — only the summary statistic is published. |
| 3.7 | **A measured meltome for any *Candida*** | None exists. Would replace the load-bearing literature benchmark with own data. |
| ~~3.8~~ | ~~**Repair the mitochondrial proton accounting**~~ | **CLOSED 2026-09-08 (K5 TASK 2).** Costing the transport does not fix it; a direction constraint on uncosted reversible carriers does, at 36-38 % of predicted growth. The chain goes from supplying 0.04-0.05 % of ATP synthase's protons to 200-272 %. Lives in `configs/experiments/candida_B5_respire.yaml` as rung B5, not as a strain default, so no committed output moved and the gate still passes 79/79. |
| ~~3.9~~ | ~~**A fifth sink-audit class: uncosted transport of the coupling ion**~~ | **CLOSED 2026-09-08 (K5 TASK 1).** Class E added to `src/etcgem/sink_audit.py` and wired into `etcgem audit-sinks --coupling-ion` as an opt-in flag, so no committed audit output changed. It infers the coupling ion from each strain's own ATP synthase (*M. maripaludis* is sodium-driven), counts both translocation and in-compartment chemistry (*Synechocystis* scores 19 % on the first and 100 % on both), and contracts GECKO arm/isozyme splits (without which eciML1515 has no detectable ATP synthase). Run on all seven strains: only the three *Candidozyma* are defective. |
| 3.13 | **Complex III is wired backwards in the three iRV973-derived models.** `R02161__mito` moves its 1.5 protons cytosol→matrix, the opposite direction to a mitochondrion, so it SPENDS proton-motive force. Quantified by K5: it eats **exactly half** of what cytochrome *c* oxidase pumps, which is why the repaired chain over-supplies at 200-272 % instead of ~100 %. Correcting it as a labelled sensitivity moves respiration per unit growth from 1.8-2.4× measured to **0.9-1.3×**, i.e. onto the measurement. | Whenever the respiration level is load-bearing for a claim. It is a one-line stoichiometry correction and it is the single change that most improves agreement with the measured O₂ assay. Send to Ilgaz with 3.14: both are in the published iRV973. |
| 3.14 | **The model's growth activation energy is too steep on the rising limb** — 1.20 eV against a measured 0.901 for *C. auris*, and 0.93-1.80 against 0.62-0.90 across the four. **REVISED 2026-09-08 by K6**, which found K5's version of this item ("the maintenance layer cannot produce the measured decoupling") to be wrong twice over: the sign discrepancy it rested on was a comparator artefact, and scaling NGAM(T) up moves the model AWAY from measurement and kills it at 10x the anchored value, while switching it OFF moves E_resp from 0.231 onto the measured 0.518. With maintenance off, ~88 % of the residual gap is the growth term. | Before any claim that these models capture thermal energetics. The layer implicated is the enzyme kinetic envelope — the shared dCp prior and the MMRT curvature that set the rising limb — not maintenance and not the ETC. Note it is consistent with the same models over-predicting the thermal limit by 9.6-15.8 °C (K4 §4), which had not been connected to it. |
| 3.19 | **Synechocystis' committed ceiling is not reproducible from a strain build.** The ceiling table's 45.70 °C comes from `strains/syn6803/outputs/P2_thermal/`; `resolve("syn6803", "syn6803_ecmodel")` gives **55.50 °C**. K9 checked that the committed curve is **not** truncated (growth falls to 0.2 % of peak by 50 °C) and that the light-saturated medium `run_p2_thermal.py` applies does not account for the difference. So the committed row depends on configuration inside that script which the strain build does not carry. | Before the seven-strain ceiling table is used in a paper, and before *Synechocystis*' near-zero gap is quoted as evidence about anything. Same family as the stale-at-commit hazard in §4: a committed number that the code does not reproduce. **Confirmed recorded 2026-09-08 (P5 TASK 4)**: strain named (*Synechocystis* sp. PCC 6803, `syn6803`), evidence in `reports/K9_criterion/report.md` §4 and DECISIONS D3 (committed 45.70 °C from `outputs/P2_thermal/`, plain build `resolve("syn6803", "syn6803_ecmodel")` 55.50 °C; truncation excluded — growth 0.2 % of peak at 50 °C; the light-saturated medium of `run_p2_thermal.py` excluded — applying it does not move the plain build). Not investigated by P5; it needs its own run. |
| 3.20 | **The gas-flux warm start can seed every walker in a dead mode, and the chain never leaves it.** P4 repaired `_warm_start` (its D3, "untested at scale"); P5 ran it once at scale — configuration D on LB at c_max 257 — and its short differential evolution (`maxiter=12, popsize=4`) returned the zero-growth mode (growth ≡ 0 at every temperature, `disc_growth` ≈ 1.4 absorbing the data, −logpost 37.6). All 40 walkers were seeded there and 100 % of them were still there after 2000 steps (156 min); the chain's MAP scores growth R² −2.19. P4's nine chains, whose warm start silently failed, started from the emergent-point ball and found growing solutions. The dead mode is a genuine local optimum of this posterior, so a mode-seeking start is the wrong start unless it is checked. | **Before P6 spends ~40 h on nine chains with this warm start on.** Cheapest fix: reject a warm-start mode whose predicted r_max is below a floor (say 10 % of the measured peak) and fall back to the emergent-point ball; or seed from P4's committed MAP for the same configuration and medium. Evidence: `reports/P5_lb_cmax/DECISIONS.md` D3 and `strains/eciML1515/outputs/calibration_configD_LB_recipe_cmax257/`. |
| 3.21 | **The configuration-E and -F gas-flux likelihood is not a function of its parameters.** Found by P6's pre-flight (2026-09-09): re-evaluating the likelihood at one fixed parameter vector spreads by **0.5–7.5 log-likelihood units** for every E and F fit (NLDM, LB, M9) and by ≤ 0.0004 for every configuration-D fit. Diagnosed: the model's **O2 uptake at optimal growth is not unique**; `flux_tpc` reads it from whichever LP vertex the solver returns, and after the ETC area constraint is removed and re-added (which the E/F likelihood does on every call) the first solve lands on a different vertex from later ones — at F LB the O2 uptake differs by 9.4 on a mean of 19.8 mmol gDW⁻¹ h⁻¹. Growth is stable. So the respiration term of every E/F chain in this family — P4's six and Parsa's four — carried a solver-history component, and τ measured on those chains includes it. P6 did not run E or F for this reason (its DECISIONS D3). | **Before any E or F fit is sampled again, and before their respiration R² is quoted.** The fix is in the likelihood, not the sampler: make O2 uptake unique at the growth optimum (a lexicographic second objective — minimise total flux, or minimise O2 uptake at fixed growth — in `flux_tpc` or in `gasflux_log_likelihood`), then re-run all six E/F fits from scratch. P3's gate is unaffected as a *port* check (one evaluation after a fresh build, both sides), but its E/F respiration rows are a statement about a quantity the model does not determine. Evidence: `reports/P6_convergence/preflight_jitter.csv`, `jitter_diagnosis.json`, `degeneracy.csv` (FVA of O2 at fixed optimal growth: E LB at 37–44 °C spans 0–188 mmol gDW⁻¹ h⁻¹ at growth 1.759 with the carbon cap ACTIVE, so an active cap does not pin O2; configuration D is unique to ≤ 0.04 everywhere). **Second trigger, found on the way:** on D NLDM the carbon cap's primal reads 0 of 120 at every temperature — either its carbon-source expression does not cover the uptake reactions the recipe medium uses, or the recipe ceilings leave it empty; check before "c_max 120 on NLDM" is quoted as doing anything.  **Mechanism settled 2026-09-09 (P6 D3a):** two fresh models agree to 0.0000; one model differs on its second call by 0.5–2.5 with growth unchanged and only O2 moved, and FVA at the moved temperatures shows O2 at fixed optimal growth is a continuum (E NLDM 20 °C 3.2–7.8; E LB 37–50 °C 0–190; F LB 35 °C 16.5–26.3). So: non-unique O2 (identifiability) selected by solver basis history (state). A basis reset makes E LB deterministic and no more identified. The fix is a tie-break that makes O2 unique, not a reset. |
| 3.17 | **The Candida ceiling's second component is not a common term.** K8 sized a predictor component of ≈5.4 K and observed that *E. coli*, with **measured** Tm, still needs ≈5.6 K, and framed the latter as common. **REVISED 2026-09-08 by K9**, which tested it across every strain where it can be computed: the residuals after removing the predictor bias are 0.05 (*M. maripaludis*), 4.38 (*C. auris*), 5.60 (*E. coli*), 10.08–10.48 (the three relatives). **There is no constant.** *E. coli*'s 5.6 K is real, unexplained and confined to one organism; the two strains that might corroborate it cannot, because their Tm come from a mesophile prior built on *E. coli*'s own meltome and the methanogen has no a-priori ceiling. | Whenever the ceiling is load-bearing. The unexplained quantity is now *E. coli*'s alone and is testable there once P4 lands. The Candida relatives' 10 °C residual is a separate and larger question. |
| 3.18 | **The per-enzyme Tm spread is carrying error, not signal.** Replacing predicted Tm with the relationship A1 measured (`Tm = 52.60 − 0.061 × Tm_pred`) collapses the spread from sd 2.2–2.9 °C to 0.14–0.18 °C and **improves** the fit in all four species (*C. auris* R² 0.518 → 0.687), while moving E_growth toward measurement. | Before any analysis that attributes between-enzyme thermal variation in these strains to biology. It also bears on whether the unfolding form's per-enzyme structure is doing useful work in *Candida* at all, which is a larger question than K8 asked. |
| 3.16 | **The shared ΔCp prior is not the best-supported value for these organisms.** `provider.dcp_prior_kJ = -4.0` (Hobbs 2013) makes the model's growth activation energy 1.24-2.29× the measured value in every *Candida* species. **−3.0, inside the literature range of −2 to −6, reconciles it for three of the four AND maximises the fit to the measured growth curve** (*C. auris* R² 0.518 → 0.575). K7 changed nothing: it is fitted to one quantity on four species, *C. haemulonii* disagrees (it needs −1.0, outside the range), and adopting it would move every committed number for these strains. | When the rising limb is load-bearing for a claim, or when the *E. coli* and methanogen strains are next revisited — they carry the same prior and it has never been tested against any of them. Any adoption should be a ladder rung with its own before-and-after, not an edit to `strain.yaml`. |
| 3.15 | **`resolved_config.yaml` records an absolute `provider.model_path`**, so a run made from a different directory produces a spurious diff and "byte-identical on re-run" is only checkable from the same checkout. Found by K5 TASK 0 running from a git worktree. | Trivial; whenever the config dump is next touched. Record the path relative to the repository root. |
| 3.10 | **Add alternative oxidase to the Candida reconstructions.** AOX is in all four proteomes (A3, and confirmed independently in K4 TASK 1 by EC/name/chemistry search) and in none of the four models. It is non-electrogenic, which is exactly the role cytochrome *bd*-II plays in the **gated** *E. coli* configuration F — the one ETC result this project has tested against experiment. Adding it is one reaction. | Together with 3.8, since an AOX branch is pointless while the chain is bypassed. Then respirometry with SHAM and antimycin A across temperature (K4 TASK 5 item 4) turns it into a measurement. |
| 3.11 | **Mitochondrial inner-membrane area per gDW, per Candida species, at 30 °C and 40 °C.** The measurement an ETC-area budget actually consumes, and it does not exist for any *Candida*: no published inner-membrane area, cristae density or mitochondrial volume fraction for *C. auris*, *C. haemulonii*, *C. duobushaemulonii* or *C. parapsilosis*, and **no inner:outer membrane area ratio for any fungus**. Nearest proxies: *S. cerevisiae* stereology (Perktold 2007; Stevens 1981), and Arthur & Watson (1976), which measured cytochrome *aa*₃ per mg dry weight across seven yeasts and found **7×** interspecific variation. | If the membrane axis is to be tested rather than made available. Method and the discriminating result are in `reports/K4_membrane/task5_what_would_test_it.md`. Serial-section electron tomography or FIB-SEM with stereological sampling; two temperatures, not one. |
| 3.12 | **Organelle-resolved mitochondrial lipidomics for any *Candida*.** Whole-cell lipidomics for *C. auris* is rich (Shahi 2020; Zamith-Miranda 2021; Singh 2020/2024); **fractionated mitochondrial lipidomics for any *Candida* does not exist**. The only comparative isolated-mitochondria phospholipid dataset across yeasts, which includes *C. parapsilosis*, is Arthur & Watson (1976) — and it shows **>10×** interspecific variation in mitochondrial cardiolipin, the largest measured fungal membrane difference on record. | Note this feeds A8 (fluidity, phase behaviour, proton leak), **not** the area budget, which has no lipid term. K4 TASK 5 §5 separates the two; they should not be commissioned as one study. |

## 4. Standing hazards — not tasks, but re-read before trusting a result

- **THE REPOSITORY HOLDS MORE THAN ONE MEASURED VALUE FOR SOME QUANTITIES, AND THEY DISAGREE.**
  This has now cost the project twice: Parsa's NLDM CSV predating its own medium change, and
  K5 comparing the model's activation energies against the wrong one of two measured growth
  fits. **The rule: when comparing a model to data, fit both sides over the same window with
  the same functional form, and state in the report which measured source was used.** The known
  multi-valued quantities, all of them legitimately so:
  - **E_growth**, 4.6-fold spread. `arrhenius_growth_fgC_h_coefs.csv` (OLS Arrhenius over every
    temperature) gives **0.194 eV** for *C. auris* clade I and is **negative for three
    isolates**, which is not biology — it is a straight line through a curve that turns over.
    The same data on the rising limb gives **0.732 eV**, and the manuscript's hierarchical
    Sharpe-Schoolfield fit gives **0.901 eV**. Use the rising-limb value against a model.
  - **E_resp**, 1.45-fold spread, and four published values for the same clade: 0.518 (OLS and
    the published Bayesian Arrhenius, which agree because respiration does not turn over), 0.454
    (equilibration-corrected), 0.654 (term-free), 0.545 (Sharpe-Schoolfield with `Eh` at its
    bound). `bayes_resp_arr_E_three_treatments.csv` holds three of them. The headline is
    "With term (published)".
  - **The measured growth TPC itself.** `measured_tpc_honest.csv`, which every Candida strain
    calibrates against, counts a dead well as an **observed zero** — deliberately, and
    documented in `gem/17_build_measured_tpc.py`, because the previous file silently dropped
    temperatures where everything died. `derived_N0_R_results_with_carbon.csv` keeps only valid
    fits, i.e. the survivors. So at 40-44 °C the first says *C. haemulonii* grows at 0.000/h and
    the second says its surviving wells grow at 0.66-0.83/h. **Both are right and they are not
    interchangeable**: the zeros curve is the one for "the relatives die at 40 °C", the
    survivors table is the one for any log-scale fit. Never mix them in one comparison.
  - **T_opt**, three sources that differ by up to 2 °C: each `strain.yaml`'s
    `measured_Topt_C`, the argmax of `measured_tpc.csv`, and the Bayesian `growth_Topt_C`. For
    *C. haemulonii* they are 32.0, 30.0 and 31.98.
  - **Per-cell respiration** carries the cell-mass constants, which disagree ~6-fold
    (item 1.9). Scale-free comparisons only.
- **Never verify with `cmd && check`.** The `cli.main` exit-code defect made one such check vacuous
  and produced a false PASS. Check exit codes explicitly. (Fixed in `a467d23`, but the habit is the
  hazard.)
- **Stale-at-commit has happened three times in three codebases by three people** — `outputs/tpc`
  committed with numbers its own code did not produce; `control_tuned` diverging from
  `decompose_tuned`; Parsa's NLDM CSV predating its own `build_pm`. Assume it until checked.
- **T_opt is regime-determined.** Three constraints relocate it (sector re-grounding `a416fd1`, the
  translation cap, Parsa's carbon cap); CT_max has been insensitive to all three. Quote T_opt with
  its binding constraint named; CT_max may be quoted plainly.
- **A variance decomposition can only attribute to mechanisms the model contains.** φ_envelope
  = 0.999 for T_opt is a local measure inside one regime, not a statement about what sets T_opt.
- **The two Candida draft models are the *auris* network with genes reassigned** (2,863 reactions,
  ~1,312 costed, differing by 2–4). Network differences cannot explain their behaviour — and cannot
  be tested there either.
- **Sectors without temperature-dependent allocation flatten the curve.** Confirmed on E. coli:
  plateau 2.0 → 14.0 °C with `allocation_from_data` off. N1's guard warns; it cannot see a shoulder
  *below* the maximum (the 37–44 °C case).
- **A GATE ONLY PROTECTS THE FIELDS IT CHECKS** (added 2026-09-08, P5, from P4 and K9). K8 added a
  field (`fixed`) to the calibration record and wrote it unconditionally; every committed
  `calibration.json` went stale on the next run and the K1 gate passed 79/79 throughout, because
  it does not read that field. K9 TASK 0 caught it only by re-running the transfers and diffing
  the tree. **Adding a field to a record is a silent way to break byte-identity.** The same week
  a second instance surfaced: N2's hotfix started recording `rescale_pool_row` in the config
  dump, and the two `etcgem fba` output directories the K1 gate reads
  (`strains/cauris_iRV973/outputs/fba_candida_pool_{binding,unconstrained}/resolved_config.yaml`)
  have been one key stale since — numerically identical, never re-run by any TASK 0, and hidden
  from a worktree by 3.15's absolute-path artefact in the same file. Left as found by P5 (VERIFY 6);
  clear it in a housekeeping commit that says so. **The rule: re-run the byte-identity check
  AFTER the last change, not at the point it seems safe; diff the whole tree, not the fields
  the gate names; and treat a `resolved_config.yaml` diff as a finding until it is explained.**
- **A RECOMMENDATION IS SCOPED TO THE CONDITIONS IT WAS DERIVED UNDER** (added 2026-09-08, P5,
  from P4). `c_max ≈ 100–120` came from Parsa's sweep on glucose-minimal and NLDM; P3 adopted 120
  as canonical from that sweep; P4's settings table applied it to LB, where every LB growth R²
  collapsed (0.83–0.90 → 0.16–0.20) while NLDM was unchanged to better. His own LB fits had used
  257 / 459 / 510 (`reports/P5_lb_cmax/parsa_lb_cmax.csv`). Nobody had run an LB sensitivity, and
  the number carried no medium with it when it moved. **The rule: record the value AND the
  conditions it was established on (here, the medium), and when a value is applied outside those
  conditions say so where it is applied, not only where it was derived.** See 1.11 and
  `reports/P5_lb_cmax/`.
- **AN AUDIT THAT FINDS NOTHING MUST FIRST PROVE IT CAN FIND SOMETHING** (added 2026-09-09, R2,
  from Y1). Y1's matcher was blind to Yeast7 naming and would have returned a clean bill of health
  for the wrong reason; proved inert on all seven strains before use. **The rule: a clean result
  from an audit on an unfamiliar namespace is not evidence until the matcher has been shown to
  find something.** See 4b and `reports/Y1_yeast_audit/`.
- **A SCAN'S CONCLUSION IS SCOPED TO THE POINTS SCANNED** (added 2026-09-09, R2, from P6). P6's
  five-temperature O2 FVA read "unique" at 25–44 °C; the degeneracy lives at 20 and 35–50 °C.
  **The rule: say which points a scan covered where its conclusion is quoted.** See D3a in
  `reports/P6_convergence/DECISIONS.md` and 3.21.

---

## 4b. Y1 — the published yeast etcGEM (2026-09-09)

**The gate on the fourth-paper idea was run and it came back (b): the defect class is ABSENT from
Li et al. 2021, and the structural finding holds.** `reports/Y1_yeast_audit/report.md`.

* **Coupling-ion audit: does not fire.** Their chain supplies 92.7 % (pristine batch) and 93.1 %
  (chemostat) of ATP synthase's protons. All twelve uncosted proton movers on the mitochondrial
  membrane run the dissipative way; none has an uncosted `_REV` twin; **no free path `m -> c`
  exists at any length**; and with every exchange shut, maximum ATP synthase flux and maximum ATP
  hydrolysis are both exactly 0. Verified pristine, under their own thermal layer, by
  counterfactual, and by the exchange-closed test.
* **T_opt / CT_max asymmetry: reproduces independently.** In their model with their `etcpy`, a
  change of binding constraint moves T_opt **10.1 C** and CT_max **0.8 C**. Five organisms, two
  codebases.
* **Calibration shift: does NOT generalise.** Their posterior left Tm at the measured meltome
  (r = 0.97 with experiment, Fig. 2g) and moved Topt instead; the nine enzymes carrying their
  thermal limit already had measured prior Tm of 40.5-43.8 C. Our E. coli needed dTm = -5.6 K;
  theirs needed nothing. What is common is the tension, not the shift.
* **A defect in OUR audit, found first.** `sink_audit`'s anchored patterns were matched against the
  metabolite id and the joined `"id name"`, so the Yeast7 convention (opaque id `s_0437`, plain
  name `ATP`) matched nothing: **zero hits in classes A-D on 6743 reactions and no ATP synthase
  found**, on a model with an intact chain. A clean bill of health for the wrong reason. Fixed and
  proved inert on all seven strains (every class-E cell identical to 0.0; every A-D count
  unchanged). **The rule: when an audit returns a clean result on a model from an unfamiliar
  namespace, verify the matcher found ANYTHING before believing the absence.**
* **Their Topt is a sequence prediction** (Tome v1.0, R^2 = 0.5) carried as a wide prior with the
  predictor's own RMSE (13.0 C) as the prior width. That is the methodological answer to our Seq2Tm
  concern, and it is theirs.
* **Their thermal layer is Python, not MATLAB** (`code/etcpy`), which is why this cost an afternoon.
  Anyone extending Y1 can run their model directly.

---

## 4c. Y2 — the regime test at Li et al.'s posterior (2026-09-09)

`reports/Y2_regime_posterior/report.md`. Closes 2.5.

* **Quotable, with an interval.** Over their own 100 posterior models, switching the binding
  constraint from enzyme capacity to substrate uptake widens the 99 % plateau of the TPC from
  **1.5 °C [0.4, 2.7] to 7.3 °C [1.4, 7.5]**, in **93 %** of models, while CT_max moves
  **4.6 °C [2.7, 11.0]**. T_opt moves 8.9 °C [4.4, 27.0] — a **lower bound** in 44 of 98 models,
  because under a substrate cap the top of the curve is a ceiling, not a peak, and the optimum
  leaves the 20–50 °C window.
* **NOT quotable as a property of their calibrated model: 10.09 / 0.81 °C.** That is the prior
  *point* table. At the posterior CT_max is no longer regime-insensitive.
* **The prior distribution does not support the finding; the posterior does.** Prior draws: T_opt
  beats CT_max in 50 % of draws, plateau widens in 35 %. Posterior draws: 92 % and 93 %. The
  calibration's shrinkage — Topt 10.9 → 7.1 °C, Tm 4.9 → 4.0 °C — is what turns a coin flip into a
  consistent effect.
* **The signed calibration shift, which Y1 could not measure.** Across 764 enzymes, Tm moved
  **+1.33 °C** and Topt **−6.32 °C**. But seven of the nine limit-setting enzymes moved *down* in
  Tm (ATP1 −6.30, ERG1 −3.66), and only **three** of those nine were below 42 °C in the prior. The
  identity of the limit-setting set is largely a product of the calibration.
* **The file is the right one, checked three ways:** md5 matches Zenodo; the populations reproduce
  the paper's average per-enzyme SDs (10.92 → 7.16, 4.90 → 4.01, 2.00 → 1.79 against 10.9 → 7.1,
  4.9 → 4.0, 2.0 → 1.8, Supplementary Fig. 7); and the nine enzymes below 42 °C reproduce
  Supplementary Fig. 8's named list exactly, nine of nine.
* **An analysis error found and corrected inside Y2.** The first pass called a parameter set
  "degenerate" when its T_opt landed at the grid edge, and dropped 44 of 100 posterior draws — the
  ones showing the effect most cleanly, because a substrate ceiling makes the top an exact tie.
  **The rule: before excluding a case as degenerate, check whether the degeneracy IS the effect.**
  `reports/Y2_regime_posterior/DECISIONS.md` §9.
* **New:** the σ-lever and chemostat conditions were not drawn over at the posterior, and the
  anaerobic model was not run. Neither is needed for the quotable figure; both are cheap.

---

## 5. What to do with P2's outcome — the checklist to run against its report

_Written before P2 finished, so the reaction is not shaped by the result._

**Verify, in this order:**

1. **The merge held.** Gate 79/79 with `$CANDIDAS_ROOT` unset, exit codes checked explicitly not
   chained; all seven strains byte-identical. If either failed, nothing below matters.
2. **The ungated notice is at the top of the config report**, not buried. A reader must not be able
   to mistake ported for verified. Quote it and check.
3. **TASK 1 (kcat).** If neither 30 nor 300 reproduces his figure → that is a finding, not a
   failure, and it goes to Parsa as a fourth question. If one does → record as provisional, and
   expect his reply to ratify.
4. **TASK 2 (NLDM).** The 1.2 % must be **fully** explained by the medium. A residual means
   something else moved and is a stop condition — chase it before merging.
5. **TASK 3 (c_max) — read this one hardest.** The question is whether 60 sits in a flat region or
   on a slope.
   - *Flat region* → the thermal claims are safe whatever Parsa says about provenance, and 1.2
     downgrades from blocking to housekeeping.
   - *On a slope* → every T_opt and E_a number in the new paper depends on a constant whose
     justification is unknown, and that becomes the most urgent item on the list.
   - Either way, do NOT let a tidy sensitivity table substitute for the provenance question.
6. **TASK 4 (stamps).** Check the stamp is generated by a script, not hand-written — a hand-written
   stamp is the next thing to go stale. Check HISTORICAL is phrased neutrally.
7. **TASK 5 (annotations).** All three must be in files a reader reaches, not in decision logs.
   Verify by opening the file, not by trusting the report.

**Then update this document:**

- Move anything P2 closed out of §2 and into a struck-through line or delete it.
- Add anything P2 discovered — expect at least one; every run so far has produced a finding the
  prompt did not anticipate (K1: the draft-model construction; K2: the reversible ATP reaction;
  A1: the predictor's absent validity; N1: the E. coli allocation cliff; N2: stale-at-commit;
  N3: the exit-code defect; P1: the missing respirometry).
- Re-rank §2. If TASK 3 says c_max is on a slope, 1.2 outranks everything.

**Then the next prompt is one of:**

- **P3** — gate D/E/F, if Parsa's data has arrived. Highest value when possible.
- **K4** — the membrane-area constraint on Candida (2.2). Highest value when it has not, and it does
  not depend on anything outstanding.
- A short corrective run, if P2 raised a stop condition.
