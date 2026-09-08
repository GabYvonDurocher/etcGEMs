# Open items — the running list

_Started 2026-09-08 while P2 was running; last updated 2026-09-08 by K9._ This is the standing list of what is outstanding across
the whole project, so nothing is lost between sessions. Update it when something lands; do not let
it become a second decision log — decisions live in each prompt's `reports/*/DECISIONS.md`, this is
only what is NOT yet done and who or what it waits on._

Status: **BLOCKED** (waiting on something external) · **READY** (can start now) · **PENDING P2**
(depends on the run in flight) · **DEFERRED** (deliberately not now, with a trigger)

---

## 1. Waiting on people

| # | Item | Waiting on | Why it matters |
|---|---|---|---|
| ~~1.1~~ | ~~**E. coli respirometry**~~ | — | **CLOSED 2026-09-08 (P3).** Arrived as two full pipeline runs (R2A/LB and M9), ingested at `strains/eciML1515/respirometry/`. Configs D, E and F are now **gated**: all ten R² values reproduce, worst 0.009. |
| ~~1.2~~ | ~~**`c_max = 60`: grounded or fitted?**~~ | — | **CLOSED 2026-09-08 (P3 TASK 4)** — on his own evidence rather than by asking. His report calls the cap a swept boundary condition, not a fit, and his sweep concludes "C_max ≈ 100–120 is the sweet spot". **120 adopted** (the only value in his range at which acetate overflow is non-zero on both media); 60 kept as a labelled sensitivity. |
| 1.3 | **Confirm recipe ceilings supersede blanket medium** | Parsa | P2 TASK 2 takes recipe as canonical on evidence, and P3 shows his D/E/F fits all used the **blanket** medium — so the model his numbers came from and the model now quoted differ. His answer ratifies or corrects. **Still open, and now more consequential.** |
| ~~1.4~~ | ~~**Confirm transporter kcat 30 vs 300**~~ | — | **SETTLED 2026-09-08 (P2 TASK 1)** by reproduction: 300 reproduces his figure, 30 does not. Set in the strain data. A one-line confirmation from Parsa would close it formally; nothing waits on it. |
| 1.8 | **Which configuration-F ETC table is intended?** | Parsa | P3 found his fits use configuration **E's** areas and turnovers plus a non-electrogenic bd-II, while the Bekker-turnover table in his `configF.py` was never used for a reported number. The port now matches what he fitted; whether the Bekker table is the intended future form is his call. |
| 1.9 | **Per-cell respiration: N₀ and fg C per cell** | Parsa | The inoculum back-projection is off in every row of both media sets, `cell_volume_um3`/`cell_carbon_fg` are typed constants (2 µm³ / 350 fg), and his own `config.R` log prints 21.21 µm³ / 2120.58 fg — ~6× apart. Growth R² and every scale-free quantity are immune; **respiration R², CUE and absolute per-cell rates are not.** Reported in `strains/eciML1515/respirometry/README.md`, not adjudicated. |
| 1.10 | **M9: fit or not?** | Parsa / us | The M9 set is ingested but **no configuration was ever fitted against it** — every `meta.json` names NLDM or LB. It is the obvious next dataset; fitting it is an emcee job. |
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
| 3.19 | **Synechocystis' committed ceiling is not reproducible from a strain build.** The ceiling table's 45.70 °C comes from `strains/syn6803/outputs/P2_thermal/`; `resolve("syn6803", "syn6803_ecmodel")` gives **55.50 °C**. K9 checked that the committed curve is **not** truncated (growth falls to 0.2 % of peak by 50 °C) and that the light-saturated medium `run_p2_thermal.py` applies does not account for the difference. So the committed row depends on configuration inside that script which the strain build does not carry. | Before the seven-strain ceiling table is used in a paper, and before *Synechocystis*' near-zero gap is quoted as evidence about anything. Same family as the stale-at-commit hazard in §4: a committed number that the code does not reproduce. |
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
