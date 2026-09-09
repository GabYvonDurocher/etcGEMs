# `reports/ecoli_gasflux/` — the gas-exchange deliverable

> ## NONE OF THESE R² IS A CONVERGED POSTERIOR — read this before any number below (added 2026-09-08, P5 TASK 2)
>
> P4 measured the integrated autocorrelation time τ on every chain in this family, and P5
> re-measured Parsa's six independently (same estimator, `emcee.autocorr.integrated_time`,
> τ_max over parameters; agreement to 0.1). **Every chain — his six committed ones and all nine
> P4 refits — has run about nine autocorrelation times against a ≥ 40 criterion.** This is a
> property of the sampling budget for this likelihood, not of the model and not of anyone's
> diligence; the step counts are conventional and are simply not enough for a posterior with
> this τ. It applies evenly to both families.
>
> | chains | steps × walkers | τ_max | chain / τ | n_eff | converged (chain > 40 τ and n_eff ≥ 200) |
> |---|---|---|---|---|---|
> | Parsa's six (`configD_NLDM_full`, `configD_LB_full`, `configE_NLDM`, `configE_LB_freecmax`, `configF_NLDM`, `configF_LB`) | 1500–2000 × 36 | 160–214 | **8.2–9.4** | 148–170 (first half discarded) / 296–340 (none discarded) | **NO**, all six |
> | P4's nine refits (D/E/F × NLDM/LB/M9, recipe medium, c_max 120) | 1500–2000 × 40 | 146–245 | **8.2–10.3** | 247–332 (sampler's own: walkers × (steps − 2τ) / τ) | **NO**, all nine |
>
> **What follows and what does not.** The ten R² values P3 gated, the values his report prints,
> and every R² in `reports/P4_refit/` are point estimates (MAP or posterior median) from
> unconverged chains. They are indicative; they are not validated model performance, and they
> must not be quoted as such. **P3's gate remains valid as a PORT check**: it reads the same
> parameter point out of his chain and recomputes his R² here to within 0.009, which proves the
> port reproduces his computation whether or not the chain it was read from converged. Those are
> two different claims and the second was never made by the gate.
>
> **The cost of fixing it** is arithmetic: 40 τ ≈ 8 000–10 000 steps per fit, four to five times
> the chain, ≈ 40 h for all nine on this machine (P4 ran 1500–2000 steps in 10 h). P4's
> warm-start repair should shorten the burn-in but is untested at scale. Until it is spent, no
> number in this family is a result. See `reports/P4_refit/TASK3_what_moved.md` and
> `docs/OPEN_ITEMS.md` 1.12.

> ## WHICH MEDIUM EACH NUMBER CAME FROM — read this first
>
> That ambiguity is what made P4 necessary, so it is stated before anything else.
>
> **Two families of numbers exist for configurations D, E and F, and they are not
> interchangeable.**
>
> | | medium | c_max | quoted where | status |
> |---|---|---|---|---|
> | **his fits** (P3) | **blanket** — every component open at ub 1000, carbon effectively unlimited | fitted (146–510) | his report; `reports/P3_gate/gate.md` | **historical comparison** |
> | **the refits** (P4) | **recipe ceilings**, clearance K sampled | **120**, fixed | `reports/P4_refit/` | **the model this repository defines** |
>
> **NOTHING IS QUOTED AS A RESULT FROM EITHER FAMILY, because no chain in either is converged.**
> All nine refits and all six of his committed chains run only ~9 autocorrelation times
> (chain/τ 6–12 against the ≥40 criterion); reaching it needs ~8 000 steps, four times the
> chain, ≈ 40 h for all nine. The values below are indicative and are labelled so.
>
> | | his (blanket) growth R² | refit (recipe) growth R² | his respiration R² | refit |
> |---|---|---|---|---|
> | **D** NLDM / LB | 0.707 / 0.896 | **0.854 / 0.196** | 0.725 / 0.793 | 0.802 / 0.923 |
> | **E** NLDM / LB | 0.849 / 0.828 | **0.893 / 0.183** | 0.721 / 0.801 | 0.867 / 0.866 |
> | **F** NLDM / LB | 0.905 / 0.881 | **0.858 / 0.163** | 0.964 / 0.852 | 0.562 / 0.909 |
> | **D / E / F on M9** | — never fitted — | **0.959 / 0.987 / 0.982** | — | 0.541 / 0.160 / 0.499 |
>
> **NLDM is unchanged to better; LB collapses**, and the cause is named: the LB medium did not
> change, but `c_max` did — from his own fitted 257–510 to the canonical 120. **`c_max = 120` is
> a glucose/NLDM recommendation and was over-applied to LB.** One fit (configuration D on LB at
> c_max ≈ 260, ~45 min) would settle it; it has not been run.
>
> *(2026-09-09, P5.) Run, and it settled it — though not by the chain, which the warm start
> trapped in a zero-growth mode (OPEN_ITEMS 3.20). At fixed parameters the cap alone takes LB
> growth R² from 0.64 / 0.05 / −0.10 (D / E / F at 120) to 0.90 / 0.83 / 0.88 at his own caps,
> because 120 holds r_max at 1.1–1.8 against a measured 2.94 h⁻¹. **The LB cap is now 450**
> (`gas_exchange.yaml` `carbon_cap.by_medium.LB`; his E/F nominal; 257 serves D only), with
> the 120 scoped to glucose-minimal/NLDM beside it. `reports/P5_lb_cmax/`.*
>
> **The medium ceiling is a PRIOR CHOICE, not a fitted quantity.** The clearance K returns 57–64 %
> of its prior width in every NLDM fit (median 4.15–4.78 against a prior [2, 10]). The data
> barely constrain it.
>
> **M9 is first light** — the best growth fits in the exercise (R² 0.96–0.99, r_max 0.64–0.69
> against a measured 0.717, T_opt 39.5–41 °C against 40 °C) and the worst respiration fits.
>
> Configurations **A, B and C** are gated separately and unaffected: 60/60 against his committed
> gas-flux CSVs (`reports/P1_parsa_port/gate.md`). Full detail:
> `reports/P4_refit/TASK3_what_moved.md`, `TASK4_M9.md`.

> ### What the respiration R² rests on — read this before quoting it
>
> The growth R² is safe: `growth_C_per_C_h` is a **specific rate**, independent of the
> inoculum density and of the carbon-per-cell constant. The **respiration** R² is not, and
> neither is anything absolute per cell. Established from the data itself
> (`strains/eciML1515/respirometry/README.md`):
>
> * **the inoculum back-projection is off** — `delta_Ninoc_to_N0_min = 0` and
>   `N0_cells_per_L == N_inoculation_cells_per_L` in **117/117** R2A/LB rows and **66/66** M9
>   rows, so N₀ is the density as pipetted;
> * **`cell_volume_um3` = 2 and `cell_carbon_fg` = 350 are typed constants**, one value across
>   every row of both files — and the pipeline's own log prints **21.21 µm³ / 2120.58 fg** from
>   `config.R`, about 6× apart. Which is right is not settled here.
>
> The fitted `resp_scale` (4.7–11.0 across the six fits) absorbs a constant offset of exactly
> this kind, so a systematic error in N₀ or in fg C per cell is partly re-parameterised rather
> than exposed. **The respiration R² is therefore a statement about the SHAPE of the
> temperature response, and the scale factor is not evidence that the absolute level is
> right.** Scale-free quantities — activation energies, curve shapes, RQ, ratios — are immune.
>
> Reported, not adjudicated: nothing here revises his results.

A new deliverable directory in the house convention (`reports/<organism>_<topic>/`), created by
P1 for Parsa's gas-exchange and overflow work on *E. coli*.

**Status: assets only.** P1 ported the mechanisms, the configurations and the gate; it did not
write the paper. What is here is the figure builder's output plus the gate that says which of
the source numbers reproduce.

* `assets/figures/` — built by `python scripts/gasflux_figures.py --strain eciML1515
  --experiments gasflux_configA gasflux_configB gasflux_configC` from the runs of
  `etcgem gasflux --strain eciML1515 --experiment gasflux_config{A..F}`.
* the port, the gate and what does and does not reproduce: `reports/P1_parsa_port/`.
* Parsa's own prose for configurations A–F is in
  `$PARSA_ROOT/outputs_reports/etcgem3_configuration_summary.pdf`; it is the source text for
  this report when it is written. His `outputs_reports/` (and its sixteen `.bak` Word files)
  is deliberately not imported — see P1 PART G.

When the report is written it follows the convention: `report.qmd` + `assemble.py`, rendering
from committed outputs under `strains/eciML1515/outputs/gasflux_*`.
