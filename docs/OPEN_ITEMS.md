# Open items — the running list

_Started 2026-09-08 while P2 was running; last updated 2026-09-11 by P15._ This is the standing list of what is outstanding across
the whole project, so nothing is lost between sessions. Update it when something lands; do not let
it become a second decision log — decisions live in each prompt's `reports/*/DECISIONS.md`, this is
only what is NOT yet done and who or what it waits on._

Status: **BLOCKED** (waiting on something external) · **READY** (can start now) · **PENDING P2**
(depends on the run in flight) · **DEFERRED** (deliberately not now, with a trigger)

---

## 0. Sequencing — E. coli first (decided 2026-09-09, sequence added 2026-09-10)

- **The E. coli model (`eciML1515`) is the best-constrained**: three media, gas exchange, a
  measured meltome. Methods are developed and proven there first, then ported through the core.
  The seven-strain gate (K1, 79/79) runs on every core change so the other strains cannot
  silently break meanwhile.
- **Candida:** the K-series result (13.57 °C required against 1.6 °C measured, and why) stands
  and is what the manuscript uses. No further Candida modelling until the E. coli calibration
  recipe exists; then it ports against the measured TPCs.
- **Cross-taxon questions already answered** (activation energies K6, seven-strain ceiling K9)
  stay on record and are not re-opened by this.

### 0a. What "a reliable model" means — four separate things, in order

Written 2026-09-10, **before P12 reported**, so that each new result is reconciled against it
rather than replacing it. These were tangled together for most of the P-series; separating them
is what the last week bought.

| | Requirement | State | What closes it | Cost |
|---|---|---|---|---|
| **R1** | **Statistically reliable** — a posterior two independent runs agree on | Surface sampleable (P10/P11); mode structure unknown | P12's basin map, then per-basin sampling on restricted priors | ~1 day of runs after P12 |
| **R2** | **Identified** — parameters set by data, not prior | **Restated 2026-09-11 (E3): the five "flat" parameters are not one category but three.** `f_metab` and `f_maint` are **FIXED BY MEASUREMENT** — they enter from the measured proteome matched to medium *and* temperature and carry deliberately tight priors, *"measurement wiggle only — the proteome is not free-fit"* (`report.qmd` §free set and priors; the fractions are *"never fit to growth"*, §eq-alloc). The likelihood being insensitive to them within that width is **the designed behaviour**: growth and respiration are not asked to re-derive a proteomics measurement. **Never call them unidentified.** `kappa_scale` (effective translation demand, auto-calibrated once at build time) and `ngam_steepness` (*borrowed* maintenance steepness, ported constants a_m≈8.5, b≈0.62, E_m≈0.5 eV from the MRes model) are **genuinely unidentified**. `clearance_mult` is a property of the experiment, not a model lever. (P11 TASK 3 measured the flatness correctly; the classification was wrong.) | **The real allocation gap is RANGE, not existence:** the measured allocation is held at its endpoint beyond the measured range, so above 37 °C on glucose the sector split is frozen — and that is exactly where `CT_max` is set. Extending the measured glucose series above 37 °C is a **proteomics experiment, not a modelling problem**. Separately and genuinely missing: maintenance vs temperature from a low-dilution chemostat (`ngam_*` are borrowed, verified not measured). | **Proteomics: one measured series.** Chemostat: days / months |
| **R3** | **Right for the right reason** — the mechanism is discriminated, not just fitted | **Screened 2026-09-10 (Y3): partly answered, and the answer redirects the route.** The −4 K `dTm` is not uniquely required — an equally good living fit exists at `dTm` = 0 — but the compensator is `tm_scale`, another **stability** parameter, not a catalytic one. Both solutions put the least-stable few per cent of enzymes 4–6 °C below the measured meltome. So the mechanism is **not** discriminated, and the undetermined part is Tm's **low tail**, not catalysis | **Not DLTKcat.** It has already been run on this proteome (1 149 reactions, 5–55 °C): fitting MMRT to its predictions gives an interior optimum for **36 of 1 149** — its kcat(T) is essentially monotone over the biological range, so there is no per-enzyme Topt in it to extract. What the evidence points at instead: the meltome is per-protein, so **name the enzymes carrying this model's thermal limit and compare their measured Tm against what the fit needs** | **~½ day** for the named-enzyme test, against 2–3 days for the DLTKcat route Y3 recommends against |
| **R4** | **Predictively reliable** — holds out of sample | **Nothing has ever been tested against data it was not fit to** | Cooper 2007 (`refs/`): TPCs of *E. coli* lines after 20,000 generations. Predicting how a curve *shifts* under evolution is the real test of a temperature-dependence framework | ~1 day once R1 holds |

### 0b. The sequence

1. **P12 — map the modes.** No sampler. Basin count, heights, prior-volume fractions, and what
   separates them. Licenses the sampler choice. *(prompt written; not yet run)*
2. **The dTm decision — PI.** Currently `dTm` is a free parameter with a wide prior landing at
   −3.9 to −5.6 K against a **measured** meltome. If the meltome is trusted, that shift becomes a
   model failure to explain rather than a number to fit — and constraining it may collapse the
   multimodality on its own, because the stability-shift mode dies. This is the single highest-
   leverage decision outstanding and P12's per-basin `dTm` will sharpen it. See 1.14, 1.20.
3. **Fix the five flat parameters** at nominal, stated as a limitation (R2, short form).
4. **Decide the respiration term's support — PI.** *(added 2026-09-10 by P12 addendum 1.)* The
   current weight discounts a dead model's respiration penalty by up to 16.7 log-likelihood
   units where a live one gets 1.2, so basins can be kept alive by the likelihood's support
   rather than by the data. This must be settled BEFORE per-basin sampling, because sampling
   a basin that only exists under a discount spends a day on an artefact. See 1.21.
5. ~~**Per-basin posteriors** on restricted priors, combined by volume fraction (R1).~~
   **STRUCK 2026-09-10 (P13), on P12's recommendation (c).** The line is kept rather than deleted
   so the change is visible: P12 found **one live basin**, so there are no per-basin posteriors
   to combine and no volume fractions to weight them by. What replaces it is a single
   well-converged run on the live basin, which is 1.19 — currently blocked by 1.23, not by this.
6. **Cooper 2007 as holdout** (R4). Only meaningful after 5.
7. **Then, and only then, port the recipe to Candida** against Ilgaz's measured TPCs.

### 0c. Reconciliation rule — read before absorbing any new result

Every run in this series has produced a result that looked like the answer and was one layer of a
stack. **A new result does not replace this section; it is reconciled against it.** Each report
must state, explicitly:

- **which of R1–R4 it moves**, and which it leaves untouched;
- **what it retracts or qualifies** in an earlier report, by dated note, numbers unedited
  (P8's "unimodal" reading and Y2's mode-conditional posterior are the live examples);
- **what it does NOT license** — the standing hazard is that a result is quoted outside the
  conditions it was derived under (§4).

Precedent for the whole exercise: **Pettersen & Almaas 2023** (`refs/PettersenAlmaas_2023.pdf`)
found seed-dependent posteriors and multimodality in Li et al.'s yeast etcGEM with 2,292 per-enzyme
parameters; P11 found the same with 16 global ones. **The multimodality is in the thermal
formulation, not the parameter count.** They name proteomics and fluxomics as the cure and did not
have them; Parsa's gas-exchange data is that data, which is the argument for E. coli first. What
remains ours beyond their prior art: the *mechanism* (cliffs from the respiration term at cold
temperatures, LP kinks), the T_opt/CT_max asymmetry, the predictor validation, and the data.

> **Dated note, 2026-09-10 (P12) — one sentence of this section is withdrawn; the rest stands.**
> "**The multimodality is in the thermal formulation, not the parameter count**" was written on
> P11's seed disagreement. P12 tested it directly and it does not hold: with endpoints converged
> (11 of 12 on tolerance) and basins defined by bottleneck barriers rather than clustering, there
> is **one live basin**, and theta_A and theta_B* — the two runs' best samples — are separated by
> **0.266**, which is noise. The only separated basin is a model with zero predicted growth at
> every measured temperature. So this reformulation does **not** reproduce Pettersen & Almaas's
> multimodality, and the claim that it is intrinsic to the thermal formulation is **unsupported by
> our own evidence**. Everything else in this section stands, including the reconciliation rule
> itself, which is what caught this. See `reports/P12_modes/` D8 and OPEN_ITEMS 1.19, 1.22.

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
| 1.12 | **Chain length: every fit in this family is under-converged** | us | All nine P4 refits AND all six of Parsa's committed chains run ~9 autocorrelation times (chain/τ 6–12 against ≥40). Reaching the criterion is ~8 000 steps, ≈ 40 h for all nine. Until then no R² from either family is a converged posterior. The warm-start defect that lengthened P4's burn-in is fixed but untested at scale. **UPDATED 2026-09-09 (P6 D6): not a budget problem.** τ grows in proportion to chain length on every configuration-D chain (chain/τ pinned at ~9.7 over 1250 steps; the true τ is unknown and > 300 on all 16 parameters), so more steps have no ceiling — the family is **sampler-limited**, not step-limited. D NLDM halted at step ~1250; D LB and D M9 not started under this sampler. Medians of the twelve data-determined parameters are stable and quotable with a "not converged" label; intervals are not. **UPDATED 2026-09-09 (P7): not a walker-count artefact either.** D NLDM at 128 walkers, otherwise P6's fit exactly, read by a rule written before the run: τ_max 26.1 → 140.8 over 1500 steps, increments 26 → 20 per block (mean of the last three 21.4 against 10 for mixing), chain/τ 9.6–10.7, the carrier rotating — 10 % below the 40-walker curve and no plateau. **NOT MIXING.** The same applies to Parsa's six chains (36 walkers, same sampler). What it now needs is one of P6 D6's decisions — fix the four prior-determined parameters, narrow the discrepancy priors, change sampler, or quote medians only — none of which is compute. `reports/P7_walkers/`. **CLOSED 2026-09-09 (P8) with a conclusion, not a task.** PCA of the chains finds no ridge (PC1 16.5 % of the variance, τ 110–121 on every one of the sixteen components; the four prior-determined parameters carry 14 % of the slow loading), so fixing them removes nothing that is slow; the ensemble slice sampler (zeus) costs 11× emcee per step on this likelihood (one walker's sequential slice loop idles the pool, 10 % utilisation) and its τ rises at the same 0.10 N. **The family is sampler-limited and no sampling change tried — walkers, moves, slice sampling — fixes it.** Conclusion: quote the configuration-D medians (P4) with a "not converged" label; the credible intervals are not available from these chains; any change from here is a model decision (fix the four, or narrow the discrepancy priors), listed in P6 D6 and P8 D5, for the user. `reports/P8_ridge/`. **VERDICT 2026-09-09 (P9): ROUGH, STRUCTURAL.** Line scans of the log-likelihood through the MAP (fresh model per evaluation, 22 lines, ±1 posterior sd at 0.05 sd) find a piecewise-smooth surface with cliffs: 12 of 22 lines have a single 0.05 sd step exceeding 20 % of the line's range (median 39 %, up to 99 %), between cliffs the curves are exact parabolas, two axes (kappa_scale, f_metab) are exactly flat. The cliffs survive tightened Gurobi tolerances and a fixed dual-simplex method unchanged (16.7 / 18.2 / 18.4 units), and each of the three largest is the **respiration term at one cold temperature** (20–25 °C) where the LP's O2 uptake changes 2–4× across the step while growth moves 1–10 %. So neither fixing the four nor narrowing priors gives intervals from this likelihood as written: the fix is to the likelihood (see 1.15). `reports/P9_surface/`. **Awaiting P7** (`prompts/P7_walker_test_prompt.md`), which decides whether D6's options (i)–(iii) are needed. `reports/P6_convergence/DECISIONS.md` D6. **P10 (2026-09-09):** the respiration likelihood now has a tie-break, a variance floor and a continuous support for eciML1515 (default OFF in the core); the cliffs fall from 13–72 units to single digits and the surface is still not SMOOTH by P9's rule, so no chain has been run under it and the medians-only conclusion stands. **NOT CLOSED — RESTATED 2026-09-10 (P11), and the reason matters.** Moving the floor to the largest measured vertex jump (0.76 → 1.42) made all twelve of P9's lines SAMPLEABLE by an absolute rule (no 0.05 sd step above 5 log-likelihood units; largest 3.53), and **dynesty reached its dlogz criterion twice** — nlive 400 in 7,118 iterations and 111,420 evaluations (log Z −22.886 ± 0.164, n_eff 4,052), nlive 250 in 4,443 and 68,947 (log Z −24.567 ± 0.185, n_eff 1,974). **The two converged runs disagree: log Z by 6.8 combined standard errors, and 15 of 16 posterior medians by more than two Monte-Carlo errors, up to 50** (dTopt 1.51 against 9.39). The second run never reached the first's region — its best likelihood is 1.7 nats worse and its mass sits 4.5 nats lower — and its dlogz was satisfied anyway, because dlogz weighs the remaining volume by *the live points' own* maximum. **So dlogz < 0.1 is necessary and not sufficient, and no posterior for this family is established yet.** What is established: the surface is sampleable (a measurement of the likelihood, not of a run), and the convergence problem was never a sampling budget — it was a cliffed likelihood. What it needs: two runs at **nlive ≥ 800** with different seeds that agree, ≈ 10–12 h each. See 1.15 and 1.19, `reports/P11_nested/`.  **APPENDED 2026-09-10 (P14):** the surface has **no plateaus** (0 of 480 adjacent evaluations exactly equal across twelve lines), so the one property that would make nested sampling structurally unable to converge here is **absent**. What remains are discontinuities of 0.05–0.59 units from the LP's O₂ vertex at cold temperatures — the P9 mechanism, two orders of magnitude smaller than when it was diagnosed.  **APPENDED 2026-09-11 (P15):** the first direct measurement of this posterior's **geometry**, from a sampler's own 800 live points: covariance **condition number 1,457**, smallest eigenvalue **1.947e-04** in a direction dominated by **`dTm` +0.903 / `tm_scale` −0.217**, and **corr(dTm, tm_scale) = +0.831**. Three parameters sit essentially **at their priors** (`f_metab` 0.273, `dCp_scale` 0.266, `f_maint` 0.265 against 0.289). The family's problem is now named: not a plateau, not a budget, but a **thin correlated ridge from a non-identified pair**. |
| ~~1.13~~ | ~~**E/F tie-break: pFBA, min-O2 or max-O2 for the respiration likelihood on an LP face**~~ | — | **CLOSED 2026-09-09 (P10): pfba chosen**, as `flux_tpc(tiebreak="pfba")` (growth held at its optimum, total absolute flux minimised, every solve at 1e-9), default OFF in the core, ON for eciML1515. The D3a instrument reads **0.0000 on D NLDM, D LB, E NLDM, E LB and F NLDM**; **F LB is 0.05–0.5** between calls and stays held (3.21). The face bounds at Parsa's E LB θ (37/40/45/50 °C): min_o2 38.07/46.60/40.70/28.48, max_o2 38.24/46.66/40.74/28.49, pfba at the low end — 0.17 wide at his θ, [0, 190] at P4's MAP. Cost ×4.5 per evaluation. `reports/P10_respiration_likelihood/` D1. |
| 1.14 | **Whether a Li-style calibration is worth attempting** — predictor as wide prior, narrowed against the measured Candida TPCs | PI | Li et al. carried a sequence-predicted Topt as a wide prior (width = the predictor's RMSE) and let the measured curves narrow it. Given the A1 noise floor of 0.043 C between clades, whether the Candida TPCs carry enough signal to narrow anything is the question. See `reports/Y1_yeast_audit/` PART D. |
| 1.5 | **`common_network.py` result** — does the optimum still compress on a common scaffold? | Ilgaz | Never recorded in `gem/notes/`. Note the K1 finding that makes it partly moot: the two draft models ARE the *auris* network with genes reassigned, so the control is near a no-op for them and informative only for *C. parapsilosis*. |
| 1.6 | **Did any Candida audit touch lipid or membrane pathways?** | Ilgaz | Bears on §6a. `allocation_and_trehalose.py` suggests compatible solutes were looked at; membranes unknown. |
| 1.7 | **`15_run_seq2tm.py` truncation bug** — truncates at 1022 aa citing a non-existent ESM-2 positional limit; committed predictions are untruncated, so the script cannot reproduce the data beside it (up to 2.6 °C) | Ilgaz — **told, not yet fixed** | A live reproducibility break in his repository. |
| 1.15 | **Decide the respiration likelihood: the surface is discontinuous where the LP's O2 uptake jumps** | PI | P9 found the configuration-D log-likelihood is piecewise smooth with cliffs of 13–72 units within one posterior sd of the MAP, each carried by the respiration term at one cold temperature where O2 uptake changes 2–4× between LP vertices while growth barely moves (`reports/P9_surface/`). No sampler and no model reduction gives credible intervals from that surface. Three ways to make the likelihood a smooth function of the parameters, none taken: (a) a tie-break that makes O2 unique at the growth optimum at every temperature — pFBA or a lexicographic O2 objective — the same change 3.21 needs for E/F, costing ~2× per evaluation and a re-run of the P3 gate; (b) a noise-aware respiration term that treats the vertex spread as model error (an interval or a widened variance at low O2), which changes what the respiration R² means; (c) a smoothed surrogate of the growth/O2 response for sampling only. Until one is chosen, the family's posteriors are medians with a "not converged" label. **RESTATED 2026-09-09 (P10):** routes (a) and (b) were built as core options (default OFF, ON for eciML1515) and measured. The tie-break resolves the E faces (F LB not); the variance floor (0.76, the model's O2 granularity at 20 °C) with a continuous support cuts every cliff by an order of magnitude — P9's −70/−32/+23 become −6/−3/+2 — **and the surface still reads ROUGH by P9's rule on two of twelve lines** (steps of 7.8 and 2.2 units, 27 % and 32 % of ranges that shrank to 29 and 7). What remains is single digits: the one vertex jump above the floor (1.42 in log at 25 °C), 1–2-unit O2 jumps at 20 °C, and **growth-term kinks of 1–3 units** that no respiration change touches. No fit was run. The decision now: a floor at the largest jump (≈ 1.4), the same treatment of the growth term, or the surrogate route (c) for both — `reports/P10_respiration_likelihood/` D5. **ACTED ON 2026-09-10 (P11); the surface question is closed, the posterior is not.** The route taken was (a) the tie-break plus (b) the variance floor, with two decisions executed: the floor sits at the **largest measured vertex jump (1.42 in log O2), not the modal temperature's**, and the **growth term is not floored** — its 1–3 unit kinks are the LP's piecewise response and inflating the primary data's variance to suit a sampler would trade information for convenience. The surrogate route (c) was not needed. Cost, stated: the respiration sd is now at least 1.42 in log everywhere, a factor-4 band, and the converged fit accordingly buys growth R² (0.900 against P4's 0.854) at the price of respiration R² (0.626 against 0.795). Any respiration R² from this family must be quoted with the floor beside it. **ADDENDUM 2026-09-10 (P12 addendum 1): the SUPPORT handling is a separate, unclosed decision inside this item, and it discounts rather than bounds.** The term's support is `w = min(1, g/g_s)`, `g_s = 0.01`, a function of the model's PREDICTED growth, multiplying the respiration term only (`calibration_multi.py:299-301`); the growth term is linear and untouched. P10 introduced it for a real defect — the hard mask at `g ≥ 1e-4` switched a whole temperature in or out as a step, which was half of P9's cliffs — and it fixes that. But at a near-dead point it hands back **16.7 log-likelihood units** against ~1.2 at every live point, so a model that predicts almost no growth is charged almost nothing for predicting the wrong respiration. Removing the discount (`w ≡ 1`, hard mask kept) widens the θ_A − θ_B gap from +24.5 to **+40.0**. Removing support handling altogether is **not available**: at 15 °C the model does not grow at θ_A, θ_B* or θ_P4 and `flux_tpc` returns **NaN** for O₂, so there is no prediction to score. The open question is therefore which BOUNDED form replaces a discount, not whether support handling is needed. Not changed in P12. Numbers: `reports/P12_modes/addendum1_schemes.csv`, DECISIONS D4. See 1.21. |
| 1.16 | **Should the Candida strains' respiratory audits use the parsimonious vertex?** | PI (K-series) | P10 ran the K5 coupling-ion audit on the four repaired Candida models at both the plain growth optimum and cobra's pfba solution at the same growth (information only, nothing adopted): the translocation-only chain-supply fraction is unchanged to three decimals in all four (2.000 / 2.722 / 2.133 / 1.120), but the figure including in-compartment proton chemistry moves for two — *C. haemulonii* 3.25 → 3.53, *C. duobushaemulonii* 2.68 → 3.23 — so the solver's vertex choice was carrying part of the K5 story there. Whether the Candida likelihoods and audits should read the pfba vertex is a K-series decision, to be made against the measured TPCs when the E. coli recipe ports (§0). `reports/P10_respiration_likelihood/task4_candida_pfba.csv`. |
| 1.17 | **Run the remaining eight gas-flux fits under the new likelihood, or not** | PI (blocked) | P11 converged configuration D on NLDM in 4.8 h and 111,420 evaluations. Projected at the same evaluation count and P10's per-fit tie-break costs: **D LB 4.5 h, D M9 4.8, E NLDM 4.7, E LB 5.0, E M9 4.8, F NLDM 4.8, F M9 4.8 — about 33 h in total**; **F LB is HELD** (P10 D1: its tie-break is not exact at 1e-9, so its likelihood is not yet a function of its parameters). Two caveats: the projection assumes each fit needs a comparable number of iterations, which scales with its own information H and is unmeasured elsewhere; and ~1 h of P11's run was dynesty's single-core unit-cube phase, which `first_update={'min_eff': 30}` would remove. `reports/P11_nested/task4_costs.csv`. **Blocked by 1.19:** running eight more fits at settings whose reproducibility has not been established would multiply the problem rather than solve it.  **STILL BLOCKED 2026-09-10 (P13):** the two runs that would have unblocked this were not started (TASK 3 stop; see 1.19, 1.23). No costs are updated.  **STILL BLOCKED 2026-09-10 (P14):** the two runs were again not started (1.23).  **STILL BLOCKED 2026-09-11 (P15):** run 1 crashed and run 2 was not started. |
| ~~1.18~~ | ~~**Finish the second-seed reproducibility check**~~ | — | **DONE 2026-09-10 (P11): it FAILED.** The nlive 250 / seed 2 run converged on its own criterion and disagrees with the nlive 400 run by 6.8 sigma in log Z and by up to 50 Monte-Carlo errors in the medians; it never reached the first run's region. Superseded by 1.19. `reports/P11_nested/task2_seed_compare.csv`. |
| 1.19 | **Establish a posterior that two runs agree on: two nested runs at nlive ≥ 800, different seeds** | PI | P11 showed dlogz < 0.1 is necessary and not sufficient here: runs at nlive 400 and 250 both met it and disagree (log Z 6.8 sigma; 15 of 16 medians beyond two MC errors). nlive 250 is below dynesty's guidance for multi-ellipsoid bounding in 16 dimensions (25 × D = 400) and 400 sits exactly at it, so neither is demonstrated adequate. **Cost, from P11's measured 0.155 s per evaluation and its H = 9.22: ≈ 10–12 h per run, so ≈ 20–24 h for the pair.** Cheaper things to try first, in order: `first_update={'min_eff': 30}` (P11 D4 — dynesty ran its first 1,250 iterations on one core, costing an hour); and checking whether the disagreement is multimodality by seeding one run's live points from the other's high-likelihood region. Until this is settled, **no posterior from this family should be quoted**, and 1.17 is blocked. `reports/P11_nested/` D8.  **RESTATED 2026-09-10 (P12): the requirement is unchanged but its PURPOSE has narrowed, and one prerequisite is now ahead of it.** P12's basin map finds **ONE live basin**: theta_A and theta_B* — the two runs' best samples — have a bottleneck barrier of **0.266**, which is noise. So the two runs did not find two modes; they explored one basin to different depths, and the disagreement is a stopping-rule failure, exactly as P11 concluded. Two agreeing runs at nlive ≥ 800 are therefore still what closes this, but they are no longer needed to *arbitrate between modes* — only to establish the single posterior. **Do not start them until 1.21 is settled**: as the likelihood stands a sampler can spend real mass on the dead basin (peak predicted growth 0.000 /h, respiration term −0.017), which is what the second seed did. Per-basin sampling on restricted priors (§0b) is **not needed** — there is one live basin. Cost unchanged at 10–12 h each. `reports/P12_modes/`.  **RESTATED 2026-09-10 (P13): still open, and now blocked on a DIFFERENT thing.** 1.21 is closed, so the support obstacle is gone. The runs were nevertheless **not started**, because P13's TASK 3 found the surface **NOT SAMPLEABLE at p38**: `axis:topt_scale` carries a step of **8.55 log-likelihood units between two FEASIBLE points** at +0.90 → +0.95 sd, against the absolute rule's 5. It is **96 % growth term**, and it is **identical under the old and new support handling (8.5519 vs 8.5517)**, so it predates P13. It is smooth curvature rather than a cliff — the steps run −0.71 … −5.63, −7.25, −8.55, −8.46, monotone, at a log-likelihood 40 units below p38 — but that was **not** used to override a rule fixed in advance. See 1.23.  **STILL OPEN 2026-09-10 (P14).** The blocker moved but did not clear: the line that stopped P13 (`axis:topt_scale`, 8.55 units) is now shown to be **steepness, not a discontinuity**, and the surface has **no plateaus at all** (0/480). Four lines retain genuine discontinuities of **0.05–0.59 units**, all of them the cold-temperature O₂ vertex switch. Whether that blocks the runs is 1.23 and is the PI's call. Cost unchanged at 10–12 h each, sequential.  **STILL OPEN 2026-09-11 (P15), and the obstacle has changed again.** The sampleability question is closed (1.23), and the run then **CRASHED** rather than converging or hitting its cap: at iteration **11,547**, dlogz **2.168**, log Z **−25.730**, ~9.9 h, dynesty raised *Slice sampler has failed to find a valid point* with **denormal** bracket steps (−5.4e-323 / 5e-323 / 1.04e-322) and a proposal bit-identical to the current point. **Deterministic** — a resume from the checkpoint reproduced it exactly. **No samples were written and run 2 was not started.** See 1.24. |
| 1.20 | **The `dTm` decision: the fit needs a 3–4.5 K shift against a MEASURED meltome** | PI | Forward-referenced by §0b step 2 since 2026-09-10; P12 now puts numbers under it and they are worse than the sequence anticipated. **Every** converged live endpoint requires `dTm` between **−3.07 and −4.50 K** (A −3.81, p38 −4.02, B\* −4.08, p81 −4.08, P4 −4.07, p50 −3.07, p83 −4.50), and the two weight-propped poor endpoints require −10.18 and −13.07. **The only point in the whole map with `dTm` = 0 is the DEAD basin** — 0.000 exactly, with `dTopt` 13.873 and predicted growth 0.000 /h at every measured temperature. §0b step 2 hoped that constraining `dTm` would collapse the multimodality by killing a stability-shift mode; P12 shows there is no second live mode to kill, and that **the meltome-honouring region of parameter space contains no growing model**. So the choice is starker: either the measured meltome is not the right constraint on this model's `Tm`, or the model cannot fit these data without contradicting it and the shift is a **failure to explain**, not a parameter to fix. Either way it is a modelling decision, not a fit. See 1.14, §0a R3, `reports/P12_modes/` D8. | **SCREENED 2026-09-10 (Y3), and one sentence above is retracted.** The claim that *the meltome-honouring region of parameter space contains no growing model* is **wrong**: with `dTm` = 0 **and** `tm_scale` = 1 both held and the four catalytic parameters re-optimised to convergence, the model grows at **1.659 /h** at log L **−14.786** — **7.60 units** worse than p38 and pressed against two prior ceilings (`dCp_scale` 4.0, `topt_scale` 1.35). P12's inference was sound for what P12 did: its only `dTm` ≈ 0 point was an *unconstrained* optimum of the 16-dimensional log posterior, a different object from a *constrained* optimum with both Tm parameters pinned. **And the −4 K itself is not required:** the profile of `dTm` with catalysis free is flat — 4.02 K for **0.077** log L units, alive throughout — but the parameter that pays is **`tm_scale`**, not a catalytic one, and both solutions put the least-stable few per cent of enzymes **4–6 °C below the measured meltome** (1st percentile 38.7 °C via the shift, 36.7 °C via the stretch, against 42.6 °C measured). So the **value** −4 K is a parameterisation artefact; the contradiction with the meltome's **low tail** is not. Third option now on the table: the model can honour the meltome's *mean* and cannot honour its *low tail*. **`dTm` and `tm_scale` are not jointly identified** — add to §0a R2. `reports/Y3_tm_shift/`.
| 1.22 | **One live basin: replace per-basin sampling with a single run, once the support is settled** | us | P12 recommends **(c) one dominant basin**, stronger than that phrasing: among models that grow there is exactly one, and the second basin is a zero-growth model separated by 13.9 units that survives scoring only because the support weight charges it −0.017 instead of a full respiration penalty. **§0b step 5 (per-basin posteriors on restricted priors, combined by volume fraction) is therefore unnecessary** and should be struck once 1.21 is decided; what replaces it is a single well-converged run on the live basin, which is 1.19. This is a simplification of the plan, not a new task, and it is recorded so the sequence is not run as written. `reports/P12_modes/` TASK 4.  **RESTATED 2026-09-11 (P15): it is a cost optimisation, not a correctness fix, and that is now measured.** The lexicographic tie-break would remove the O₂-vertex discontinuities P14 sized at **0.145–0.885 log-likelihood units** — but the **growth-term kinks are 1–3 units** and no respiration change touches them (P10), so larger discontinuities would remain from another term. It does not unblock 1.19, and it would not have prevented P15's crash, whose cause is a degenerate direction rather than a jump. |
| 1.24 | **Remove the `dTm`/`tm_scale` ridge, or change the sampler — the decision P15's crash forces** | PI | P15's run died deterministically on a degenerate direction, and the direction has a name: **`dTm` +0.903 / `tm_scale` −0.217, `corr` = +0.831 among the live points**, smallest covariance eigenvalue **1.947e-04** in a unit cube whose largest is 0.2835. **This is exactly the pair Y3 showed is not jointly identified, confirmed by a wholly independent route** — Y3 profiled the likelihood, P15 watched a sampler's live points collapse onto the same correlation. Two redundant knobs on one axis give a ridge of ever-shrinking width, and any sampler that brackets along a direction will eventually fail on it. **(a) Fix `tm_scale` (or `dTm`) at nominal and re-run** — removes the degeneracy at source, drops to 15 dimensions, converts an unidentifiability into a stated limitation; this is **§0b step 3** and item **1.20**, and it is the recommended route, at the same cost as this run. **(b) Change the sampler** (`rwalk`, or more `slices`) — cheapest in thought, but it would sample a known degeneracy and forfeit comparability with P11, which used `rslice`. **(c) Both**, (a) as the scientific run and (b) as a robustness check. P15 did **not** choose, because the settings were fixed in its D1 before the run. `reports/P15_posterior/` D2–D3. |
| 1.23 | **Decide whether the absolute smoothness rule should distinguish CURVATURE from a CLIFF** | PI | Raised by P13 (2026-09-10) and left deliberately undecided. The rule — no single 0.05 sd step above 5 log-likelihood units — was written in P11 to catch **cliffs**: isolated jumps among small steps, which is what P9 measured (`0.1, 0.1, 70, 0.1`). At p38 it now fails on `axis:topt_scale` at **8.55 units**, but the steps there are **monotone and smoothly increasing** (−0.71, −0.83, −1.11, −1.18, −1.44, −1.83, −2.39, −3.05, −4.15, −5.63, −7.25, −8.55, −8.46) at a log-likelihood of −47.8, **40 units below p38** and carrying essentially no posterior mass. That is a steep tail, not a discontinuity, and nested sampling is untroubled by steepness. **P13 did not override the rule**, because inventing a criterion after seeing the data is the error P12 D5/D7 recorded. The decision is: (a) keep the rule as written and treat the surface as unsampleable, which blocks 1.19 and 1.17 indefinitely; (b) add a second-difference or isolation test so the rule separates curvature from a jump, **written down before it is applied** and re-run on P9's twelve lines so it is calibrated against known cliffs; or (c) restrict the rule to the region carrying posterior mass, e.g. within the 99 % credible region rather than ±1 sd of an optimum. **A related hazard is now in §4**: a sampleability verdict measured at ONE centre is not a property of the surface — P11's was 3.20 on this line at θ_A and is 8.55 at p38. `reports/P13_support/` D7.  **ANSWERED IN PART, AND SHARPENED, 2026-09-10 (P14).** The rule was replaced, not patched, by a criterion written before its data: **(a)** discontinuity by **grid refinement** (h, h/2, h/4, h/8 — for a bounded derivative |Δ| halves; for a jump it converges to the jump height), **(b)** plateaus — runs of *exactly* equal likelihood, which is what actually voids nested sampling's volume shrinkage — and **(c)** feasibility boundaries exempt. Outcome: **`axis:topt_scale`, the line that stopped P13 at 8.55 units, tests SMOOTH** (ratios 0.507, 0.515, 0.504), so the old rule's verdict was **steepness**, demonstrated rather than argued. **(b) passes perfectly: 0 of 480 adjacent evaluations exactly equal on any of the twelve lines.** But **four lines carry genuine small discontinuities** — `dCp_scale` 0.379, `PC1` 0.145, `PC2` 0.467, `random1` 0.885 — and all four are **one mechanism**: 97–100 % respiration term, growth unchanged to five decimals, **O₂ moving 0.57–1.86× at a single cold temperature**. That is P9's LP vertex switch, made deterministic by P10's tie-break and cut by the 1.42 floor from 13–72 units to 0.05–0.59. **THE DECISION NOW OPEN IS NARROWER AND IS THE PI'S:** (a) **lift the discontinuity conjunct and run** — a jump is not a plateau, and nested sampling depends on X(L), the prior mass above L, so a discontinuity leaves an interval of likelihood values carrying no mass (harmless) whereas a plateau puts an atom in the distribution of L (fatal), and the surface has none of the latter; (b) **implement 1.22, the lexicographic tie-break, and re-test** — it addresses the exact mechanism and is excluded from P13 and P14 by name; or (c) keep the rule and leave 1.19 and 1.17 blocked. P14 did **not** lift it itself, because moving a threshold after seeing its data would be the fourth time in this series. `reports/P14_posterior/` D1–D3.  **CLOSED 2026-09-10/11 (P15): the discontinuity conjunct is LIFTED, by PI decision, on an argument that predates the data.** Nested sampling estimates Z = ∫L dX and requires only that **L have no atoms under the prior**: an atom makes X(λ) jump and voids X_i ≈ exp(−i/nlive). **A plateau creates that atom; a jump does not** — it leaves a *gap* in L's support carrying no prior mass, and Z = ΣL_i w_i stays a valid Riemann sum in X. The criterion named plateaus as the failure mode and then required no-jumps as well; those are different objects. P14 measured **0 of 480** adjacent evaluations exactly equal (no atoms), and its four real jumps are **0.145–0.885 units** against the **1–3 unit** growth kinks P11 accepted as irreducible — so 1.22 would remove the smaller discontinuities while larger ones remain from another term. **P14 was right to refuse to lift this itself**; the correction required someone not holding the pen. `reports/P15_posterior/` D0. |
| ~~1.21~~ | ~~**Decide the respiration term's SUPPORT**~~ | — | **CLOSED 2026-09-10 (P13): `clamp`.** Raised by P12 addendum 1 (2026-09-10), characterised and deliberately not acted on. The weight `w = min(1, g/g_s)` with `g_s = 0.01` scales the whole per-temperature respiration term by the model's own predicted growth, so the less a parameter set grows, the less it pays for getting respiration wrong. Measured credit, in log-likelihood units: **θ_A 1.263, θ_B 16.696, θ_B\* 1.115, θ_P4 1.234**; the A−B gap moves +24.535 → **+39.967** with the discount removed. It is not manufacturing the P11 seed disagreement — θ_B is a median artefact that neither run visited as a mode (25.9 units worse than seed 2's own best sample, peak predicted growth 0.163 /h against an observed 2.076), and θ_B\* is not propped up. But it does let dead regions of parameter space score far better than they should, which is exactly what a basin map is sensitive to. Options: (a) keep it, and always report peak predicted growth beside any log-likelihood; (b) replace it with a bounded penalty — score respiration at full weight but cap each temperature's contribution, so the term is continuous AND a dead model is charged in full; (c) make aliveness explicit in the model rather than in the likelihood's support. **Constraint on all three:** support handling cannot simply be dropped — where the model is dead `flux_tpc` returns NaN for O₂ and there is nothing to score. **Anything decided here invalidates P11's sampleability scan on the cold lines (15–25 °C)**, where predicted growth is small and `w < 1`; the floor and the tie-break are unaffected. `reports/P12_modes/` D4.  **THE FORM CHOSEN, and why it is not the one recommended.** `respiration.support: clamp` with `weight_floor: 1.0` is now ON for eciML1515: the mask becomes `isfinite(o2) & (o2 > 0)`, so a **FEASIBLE-NOT-GROWING** temperature is scored at full weight instead of being discarded by the growth mask. The justification is stronger than "it removes a discount": of the 15 dead temperatures across P12's twelve converged endpoints, 11 are genuinely INFEASIBLE (all of them the dead basin) and **4 are FEASIBLE-NOT-GROWING with O₂ = 0.525–5.674 — and among the eleven LIVE endpoints it is 4 of 4**. A non-growing cell still respires for maintenance, so **the mask was discarding real predictions and clamp scores them**. The recommended form — impute O₂ = 0 where growth stops — was **withdrawn on physiology and measurement**: it fails P10's D3a state gate at the dead basin by **119.14** log-likelihood units, its continuity step is 2,300 units per 0.05 sd, and its apparent live–dead gap is the epsilon (774 / 1,553 / 2,511 at 1e-6 / 1e-9 / 1e-12). Cost, stated: p38 loses **2.8 units** and the live–dead gap moves 11.691 → 11.245 — small, because the discount was never the dead basin's main protection; **the NaN mask is, and that is irreducible**. Gate 79/79 and 60/60 with the option OFF; the P3 gate table is byte-identical with it ON. `reports/P13_support/` D3–D5. |

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
| 2.8 | **E1 was never run, and E2 needed it** | E2 (the deck) found `reports/E1_paper_register/` absent — not on `main`, not on any branch, nowhere in the history, no `e1/*` remote branch and no "E1:" commit. Only `prompts/E1_ecoli_paper_restructure_register_prompt.md` exists. E2 rebuilt the two things it needed from primary sources — the UNSUPPORTED status of the old *E. coli* intervals, and the gas-flux inventory — and says so on the record. **Still missing: the sentence-by-sentence correction register for `reports/ecoli_tpc/report.qmd`, and the restructure options.** The paper still states things the evidence contradicts and nothing yet records which sentences. `reports/ecoli_deck/DECISIONS.md` D0. |
| 2.9 | **`references.bib` mis-titles the MRes thesis** | `reports/ecoli_tpc/references.bib` gives `@Madkaikar2023` as *"Predicting the temperature dependence of microbial metabolism with enzyme- and temperature-constrained genome-scale models"*. The thesis is **"Predicting the thermal niche of a ubiquitous bacterium using whole genome sequence"** (Imperial College London, MRes CMEE, August 2023). Corrected in `reports/ecoli_deck/references.bib` only: the `ecoli_tpc` copy is cited by the paper and by `reports/activation_energy/`, so fixing it there is a paper edit and belongs with 2.8. `reports/ecoli_deck/DECISIONS.md` D8. |
| 2.10 | **Eight committed figures are illegible on a slide** | E3 measured every figure in the deck against a threshold fixed in advance (a tick label must render at ≥ 9 pt, i.e. rendered-to-native scale ≥ 0.9, `reports/ecoli_deck/DECISIONS.md` D17). The three figures the deck owns were regenerated at slide width and pass (0.91–0.94). The **eight borrowed from `reports/ecoli_tpc/`, `reports/ecoli_gasflux/` and `reports/P9_surface/` cannot**: they are journal figures, 432–1224 pt wide natively against a 398 pt slide, so their ceiling is ≈ 0.47 and `task1_scan.png` is 0.15. **The fix is to give their producing scripts a slide-width figure size** (`reports/ecoli_tpc/assemble.py`, `scripts/gasflux_figures.py`, `reports/P9_surface/task1_lines.py`) — which rewrites those reports' committed assets and needs their model outputs, so it is a deliberate job, not a deck edit. `reports/ecoli_deck/measure_figures.py` exits 1 until it is done. Interim workaround used for the worst case: the elasticity result is now a **typeset table** on the slide, which is legible and loses nothing. |
| 2.8 | **Ground κ (`translation_coeff`) in the proteome data instead of auto-calibrating it** | κ is the effective ribosomal protein demand per unit biomass flux in the biosynthesis cap, $\kappa v_\text{bio} \le f_\text{bio} P_\text{tot}$ (`report.qmd` @eq-biocap). It is **not measured**: it is auto-calibrated once at build time so that the metabolic pool and the translation cap are *exactly co-limiting* at the nominal split and $T_0$. That is good hygiene — switching the sector layer on does not move the nominal prediction — but it embeds a modelling assertion (translation and metabolism equally limiting at the reference point) as though it were a constant, and it gives a single temperature-independent value. **Nothing in the calibration tests it:** the paper's own sensitivity section calls `kappa_scale` *inert* at the peak (the growth-law biosynthesis cap is not the binding constraint there), the calibration reports it "stays near its prior", and P9/P11/P12 put it in the FLAT class — `range_logL` exactly 0.0 along its axis and the prior centre in all twelve independent optimisations. So the auto-calibrated value is neither confirmed nor refuted by any fit. **It is grounded-able from data already committed.** Scott et al. 2010 [@Scott2010] measure translational capacity $\kappa_t$ directly, and the model already uses its *slope* ($s = 0.33$ h $\approx 1/\kappa_t$) in coupled mode while auto-calibrating the *level*. More directly, the Wang et al. 2026 proteome [@Wang2026] that sets $f_\text{bio}$ per medium and temperature also carries the ribosomal fraction; paired with the growth rate at which each proteome was measured, that yields κ **as a function of temperature**, which a single build-time value cannot be. Cheap — arithmetic on a committed table, no new experiment and no fit. Two things to check rather than assume: whether the Wang tables record the growth rate alongside each proteome, and whether κ derived that way agrees with the co-limitation value at $T_0$ (a disagreement is itself the finding). **Context:** the biosynthesis cap has no equivalent in Li et al.'s etcGEM, which is a GECKO model with a single pool and no separate translation constraint — so this is a genuine addition here, and worth grounding for that reason. ME-models parameterise the same physics mechanistically from measured elongation rates. |

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
| 3.21 | **The configuration-E and -F gas-flux likelihood is not a function of its parameters.** Found by P6's pre-flight (2026-09-09): re-evaluating the likelihood at one fixed parameter vector spreads by **0.5–7.5 log-likelihood units** for every E and F fit (NLDM, LB, M9) and by ≤ 0.0004 for every configuration-D fit. Diagnosed: the model's **O2 uptake at optimal growth is not unique**; `flux_tpc` reads it from whichever LP vertex the solver returns, and after the ETC area constraint is removed and re-added (which the E/F likelihood does on every call) the first solve lands on a different vertex from later ones — at F LB the O2 uptake differs by 9.4 on a mean of 19.8 mmol gDW⁻¹ h⁻¹. Growth is stable. So the respiration term of every E/F chain in this family — P4's six and Parsa's four — carried a solver-history component, and τ measured on those chains includes it. P6 did not run E or F for this reason (its DECISIONS D3). | **Before any E or F fit is sampled again, and before their respiration R² is quoted.** The fix is in the likelihood, not the sampler: make O2 uptake unique at the growth optimum (a lexicographic second objective — minimise total flux, or minimise O2 uptake at fixed growth — in `flux_tpc` or in `gasflux_log_likelihood`), then re-run all six E/F fits from scratch. P3's gate is unaffected as a *port* check (one evaluation after a fresh build, both sides), but its E/F respiration rows are a statement about a quantity the model does not determine. Evidence: `reports/P6_convergence/preflight_jitter.csv`, `jitter_diagnosis.json`, `degeneracy.csv` (FVA of O2 at fixed optimal growth: E LB at 37–44 °C spans 0–188 mmol gDW⁻¹ h⁻¹ at growth 1.759 with the carbon cap ACTIVE, so an active cap does not pin O2; configuration D is unique to ≤ 0.04 everywhere). **Second trigger, found on the way:** on D NLDM the carbon cap's primal reads 0 of 120 at every temperature — either its carbon-source expression does not cover the uptake reactions the recipe medium uses, or the recipe ceilings leave it empty; check before "c_max 120 on NLDM" is quoted as doing anything.  **Mechanism settled 2026-09-09 (P6 D3a):** two fresh models agree to 0.0000; one model differs on its second call by 0.5–2.5 with growth unchanged and only O2 moved, and FVA at the moved temperatures shows O2 at fixed optimal growth is a continuum (E NLDM 20 °C 3.2–7.8; E LB 37–50 °C 0–190; F LB 35 °C 16.5–26.3). So: non-unique O2 (identifiability) selected by solver basis history (state). A basis reset makes E LB deterministic and no more identified. The fix is a tie-break that makes O2 unique, not a reset. **RESTATED 2026-09-09 (P10):** the tie-break (1.13) makes the E-configuration likelihoods and F NLDM functions of θ to 0.0000; **F LB alone remains non-deterministic (0.05–0.5)** at the parsimonious optimum even at 1e-9 — its face is not resolved by pfba; min_o2/max_o2 are deterministic bounds but a modelling assertion. F LB is the one fit still held on this ground. |
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
- **NEVER RUN A `multiprocessing` SCRIPT FROM STDIN. IT RESPAWNS FOREVER AND SURVIVES THE
  SESSION** (added 2026-09-10, P12; **second occurrence**). macOS uses the *spawn* start method,
  so every worker re-imports the parent's `__main__`. When `__main__` is stdin — `python - <<'EOF'`,
  a heredoc, or a piped script — each worker re-executes the whole module top level, creates its
  own `Pool`, and spawns more workers, without limit. The first occurrence (P9/P10 week) was
  caught only because the user heard the fan. The second, **pid 43407, ran undetected from
  2026-09-09 22:00 for 13.6 hours**, orphaned to `launchd` (PPID 1) with its heredoc temp file
  already deleted, respawning continuously — its worker PIDs rotated 85783→87519 within seconds
  of each other while being inspected — and had consumed ~58 minutes of CPU. It was found only
  because the user asked whether the workers were still consuming CPU.
  **The rules, all three:** (1) any script that imports `multiprocessing` is written to a FILE
  with an `if __name__ == "__main__": main()` guard and run as a file, never fed to `python -`;
  (2) after any pooled run, sweep for stray interpreters that are not in the live run's process
  tree and check their PPID — **PPID 1 on a compute process means orphaned, not finished**;
  (3) `ps -o pcpu` is a lifetime average and reads low on a sleeping parent, so a runaway hides
  from it — check process STATE and whether the child PIDs are CHANGING, which is the only
  signature that distinguishes a respawn loop from a long job.
- **A CRITERION MUST TEST THE FAILURE MODE IT NAMES** (added 2026-09-11, P15). The sampleability
  criterion specified for P14 **named plateaus** as nested sampling's failure mode — correctly — and
  then **also required no jumps**. Those are different objects, and only one is fatal: a plateau puts
  an **atom** in the distribution of L under the prior, which voids X_i ≈ exp(−i/nlive); a jump
  leaves a **gap** in L's support, carrying no prior mass, which nothing ever samples. The surplus
  conjunct cost a full run slot (P13) and then blocked a second (P14), on a surface that had **no
  plateaus at all**. **The rule: when a criterion names a failure mode, every conjunct must be
  derivable from that failure mode — and a conjunct that cannot be is not conservatism, it is a
  different criterion smuggled in.** See 1.23.
- **A SMOOTHNESS CRITERION MUST TEST DISCONTINUITY BY GRID REFINEMENT, NOT BY STEP SIZE — AND
  FOR NESTED SAMPLING THE PROPERTY THAT MATTERS IS FLATNESS, NOT STEEPNESS** (added 2026-09-10,
  P14). A step size confounds two different things: a steep smooth gradient and a jump. Refining
  the grid separates them in four evaluations — |Δ| halves with h for a bounded derivative and
  converges to a constant for a jump. Measured here: the step that stopped P13, **8.55 units on
  `axis:topt_scale`, halves cleanly (0.507, 0.515, 0.504) and is pure steepness**, while steps of
  **0.05–0.59 units elsewhere do not shrink at all** and are real discontinuities. **Step size
  ranked them backwards.** And for a nested sampler the ranking barely matters either way: its
  estimate depends only on X(L), the prior mass above L, so it is invariant to any monotone
  transformation of the likelihood. A jump leaves an interval of likelihood values carrying no
  prior mass — harmless. A **plateau** puts an **atom** in the distribution of L and voids the
  shrinkage argument — fatal (Fowlie, Handley & Su 2021). **The rule: test discontinuity by
  refinement, test plateaus by exact equality, and do not let gradient magnitude gate a sampler
  that is blind to it.** See 1.23.
- **A SAMPLEABILITY VERDICT MEASURED AT ONE CENTRE IS NOT A PROPERTY OF THE SURFACE** (added
  2026-09-10, P13). P11 scanned twelve lines through **θ_A** and reported the surface SAMPLEABLE:
  largest step 3.53, and 3.20 on `axis:topt_scale`. P13 re-scanned the **same twelve lines with the
  same instrument and the same rule** through **p38** — the better optimum P12 found, which beats
  P11's own best sample — and `axis:topt_scale` gives **8.55**, failing the rule. Nothing about the
  likelihood changed between the two measurements. **The rule is a statement about a neighbourhood,
  not about a function**, and a surface verified at the point a previous run happened to stop at
  has not been verified where the next run will go. **The rule: re-scan at the current best point
  before every sampling run, and quote a sampleability verdict with the centre it was measured at,
  always.** See 1.23.
- **A SMOOTHNESS RULE MUST BE ABSOLUTE IN LOG-LIKELIHOOD UNITS; A RELATIVE ONE FLAGS KINKS ONCE
  THE CLIFFS ARE GONE** (added 2026-09-09, P11). P9 judged a likelihood surface by whether any
  0.05 sd step exceeded 20 % of its line's range. That was the right instrument for cliffs of
  13–72 units on ranges of 15–137. But a fix that removes the cliffs shrinks the ranges with
  them, so the same rule kept reading ROUGH on lines whose largest step was 0.8 units — a
  likelihood ratio of about 2, which no sampler notices. What decides whether a sampler can
  cross a step is e^−Δ: e^−30 is a wall, e^−2 is a kink. **The rule: state smoothness criteria in
  absolute log-likelihood units** (P11 used 5, the same threshold P10 used to identify the steps
  it fixed), **and re-derive a relative criterion whenever the thing it normalises by has
  changed.** Under both readings the same twelve lines are SAMPLEABLE (largest step 3.53 units)
  and ROUGH (two lines above 20 % of ranges of 3.6 and 15.8) at once. See `reports/P11_nested/`.
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

**Dated note, 2026-09-10 (P12).** Pettersen & Almaas 2023 found Li et al.'s yeast etcGEM **multimodal and seed-unstable across 2,292 per-enzyme parameters**, and P11 read the same signature into this 16-parameter reformulation. **P12 does not reproduce it.** With the endpoints actually converged and basins defined by bottleneck barriers rather than by clustering, there is **one live basin**; the only separated basin is a model that does not grow. So the precedent's multimodality is **not** simply inherited by any thermal etcGEM — on this evidence it is not present here at all, and the earlier framing ("the multimodality is in the thermal formulation, not the parameter count", §0c) is **withdrawn as unsupported**. What does carry over from their work is the *method* — FVA on equally-fit particles, hierarchical clustering of endpoints — and their cost finding does **not**: their 8.5× came from replacing COBRApy because 80 % of their time was model preparation, whereas here **92 % is LP solving and 8 % preparation**, so that route could buy at most 8 %.

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

## 4d. Y3 — is the −4 K stability shift biology or parameterisation? (2026-09-10)

A screen, not the experiment. `reports/Y3_tm_shift/report.md`. Moves **R3 only**, and licenses
nothing about the Candida models (their Tm is predicted, and A1 measured that predictor's bias at
+5.43 °C).

* **Verdict PARAMETERISATION by the rule — narrower than its label.** Both arms fire: partial
  correlations +0.696 / +0.663 / +0.661, and a compensating direction of 4.02 K for **0.077 log L
  units**, alive throughout.
* **What pays for it is not catalysis.** `tm_scale` — which stretches the Tm *spread*, not a
  catalytic parameter — moves 0.990 → 1.467 along the profile while `kcat_scale` stays 1.33–1.43.
  The control is decisive: pinning `tm_scale` = 1 **while keeping** the −4 K shift costs *nothing*
  (−0.15 units); it only becomes load-bearing when `dTm` is forced to 0.
* **Both solutions buy the same low tail.** 1st percentile of effective Tm: **38.7 °C** via the
  shift, **36.7 °C** via the stretch, against **42.6 °C** measured. The fit does not need the
  meltome moved down; it needs the least-stable few per cent of enzymes several degrees less
  stable than measured.
* **1.20 partly retracted:** the meltome-honouring region *does* contain a growing model — 1.659 /h
  at log L −14.786, 7.60 units worse and pressed against two prior ceilings.
* **New non-identification for R2:** `dTm` and `tm_scale` are not jointly identified.
* **DLTKcat recommended against, on its own output.** 36 interior optima out of 1 149 fits; 736
  rail at 80 °C. The thermal layer is already per-enzyme in its *data* (`enzyme_cost.py` holds
  per-enzyme `Topt`/`Tm` arrays), so swapping in a better table is ~0 half-days — the blocker is
  that there is no better table to swap in. Making the *free parameters* per-enzyme is 6–10
  half-days in the calibration, not the thermal layer.
* **The rule did not distinguish stability from catalytic compensation.** It listed `tm_scale`
  among "the catalytic parameters". **The rule: when a decision rule names a parameter set, check
  each member does what the label says before the rule is allowed to decide anything.** Y3 caught
  it only because the profile's compensator was visible in the per-step table.

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
