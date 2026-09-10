# Y2 — the T_opt / CT_max regime test at Li et al.'s calibrated posterior

> **Dated note, 2026-09-10 (P12): what this report says about Li et al.'s posterior is UNAFFECTED;
> what the project inferred from it about OUR posterior is qualified. No number below is edited.**
>
> Y2's results are conditional on **their** calibrated posterior over 100 models, and nothing in
> P12 touches that: the regime test, the plateau, the T_opt/CT_max asymmetry and the 92 % figure
> all stand exactly as reported.
>
> What changes is the inference that ran in the other direction. Between Y2 and P11 the project
> treated Pettersen & Almaas's finding of **multimodality and seed-instability in Li et al.'s
> model** as a property that any thermal etcGEM would inherit, and read P11's seed disagreement as
> a confirmation. **P12 tested that on our own model and it does not hold**: with endpoints
> converged and basins defined by bottleneck barriers rather than clustering, there is **one live
> basin**, and the two nested runs' best samples are separated by **0.266**, which is noise. The
> only separated basin contains models that do not grow.
>
> So a mode-conditional reading of our posterior is **not** required, and any statement that our
> results are conditional on which mode a run found should be dropped rather than softened. See
> `reports/P12_modes/` D8 and OPEN_ITEMS §0c, 1.19, 1.22.


Y1 PART C found the asymmetry in the published yeast etcGEM but ran it at their **prior**
parameters, and flagged that itself (`docs/OPEN_ITEMS.md` 2.5). This repeats the test at the
posterior their paper's results are stated at, over their own 100 posterior models.

**The finding survives, and over the ensemble it is stronger and far more consistent at the
posterior than at the prior — but the margin between T_opt and CT_max narrows sharply, because at
the posterior the upper thermal limit is no longer insensitive to the regime.** The 10.09 / 0.81 °C
pair Y1 quoted is a property of a single smooth prior vector and should not be quoted as a property
of their calibrated model.

Provenance: `SOURCE.md`. Judgement calls, including one analysis error found and corrected here:
`DECISIONS.md`. Li G. *et al.* (2021) *Nat Commun* **12**:190.

---

## 1. The posterior, and that it is the right one

Zenodo **10.5281/zenodo.3996543** v2.0, `results.tar.gz`, 2 356 820 868 bytes, md5
`9367d7edcea41ecd50d9fb399f064582` — matching the md5 Zenodo publishes. One member is used:
`results/smcabc_gem_three_conditions_save_all_particles.pkl`, a pickle of their `abc_etc.SMCABC`
object holding **168 generations, 21 504 simulations, final ε = −0.9026** — the paper's own
"21504 parameter sets" (Fig. 2d) and its ε = −0.9 stopping rule. `.population_t0` is the Prior
(n = **128**), `.population` the Posterior (n = **100**), over **2292 parameters = 764 enzymes ×
{Tm, Topt, ΔCp‡}**. Both n match the Fig. 2a–c caption.

**The mapping is a field rename**, and it was checked before being applied to 764 enzymes.
Particles are dicts keyed `"<uniprot>_<field>"` in the same units as
`data/model_enzyme_params.csv`, and **their own** `GEMS.format_input` converts one to a
thermal-parameter table. Giving `format_input` the prior table's own values reproduces
`etc.calculate_thermal_params(prior)` to **0.000e+00**. On ERG1 by hand:

| | prior file | prior particles | posterior median (mean ± sd) |
|---|---|---|---|
| Tm | 313.608 ± 3.40 K | 313.568 ± 3.79 | **309.771** (309.944 ± 1.47) |
| Topt | 307.150 ± 13.00 K | 299.561 ± 9.22 | **297.274** (297.151 ± 3.88) |
| ΔCp‡ | −6300 ± 2000 J/mol/K | −6374 ± 2064 | **−6405** (−6445 ± 1218) |

**The stop condition passes.** The paper reports average per-enzyme SDs prior → posterior of
Topt 10.9 → 7.1 °C, Tm 4.9 → 4.0 °C, ΔCp‡ 2.0 → 1.8 kJ/mol/K (Supplementary Fig. 7). These
populations give **10.92 → 7.16**, **4.90 → 4.01**, **2.00 → 1.79**. Six numbers, all within a
rounding step.

## 2. (a) The prior run reproduces Y1 — twice

Y1's `task_c_regime_test.py`, re-run unchanged, regenerates
`reports/Y1_yeast_audit/task_c_curves.csv` and `task_c_summary.csv` **byte-identically**:
`git status` in that directory is empty afterwards. Same headline, **T_opt range 10.09 °C and
CT_max range 0.81 °C**.

The same prior table run through Y2's own amortised path gives **10.09 and 0.81 again**. The
amortisation — their four calls applied once per temperature instead of once per (setting,
temperature) — differs from `etc.simulate_growth` by **4.5e-10**, while `etc.simulate_growth`
differs from **itself**, called twice on the same model, by **3.8e-7**. It is three orders of
magnitude quieter than the solver's own repeatability, and moves no descriptor by more than
3.7e-8 °C.

## 3. (b) The point estimates

The constraint switch is Y1's, unchanged: glucose uptake capped at 10 → 4 → 2 → 1, which
substitutes a substrate-uptake limit for the enzyme limit. Ranges are across those four settings.

| parameter set | T_opt (loose → tight) | **T_opt range** | CT_max (loose → tight) | **CT_max range** | asymmetry | 99 % plateau (loose → tight) |
|---|---|---|---|---|---|---|
| `prior_file` (Y1's) | 31.04 → 21.00 | **10.09 °C** | 46.71 → 45.90 | **0.81 °C** | **12.5×** | 1.5 → 7.0 °C |
| `prior_median` (128 particles) | 30.12 → 20.00\* | 10.43 °C | 46.25 → 45.78 | 0.46 °C | 22.5× | 1.5 → 7.5 °C |
| `posterior_median` (100 particles) | 28.46 → 20.00\* | **8.46 °C** | 43.01 → 38.75 | **4.27 °C** | **2.0×** | 2.0 → 7.5 °C |

\* censored: the optimum leaves the 20–50 °C window (§5).

Two things move between prior and posterior, and only one of them is the finding.

* **T_opt range narrows a little**, 10.09 → 8.46 °C.
* **CT_max range widens five-fold**, 0.81 → 4.27 °C. At the posterior the upper thermal limit is
  **not** insensitive to the regime: a tight substrate cap drops it from 43.0 °C to 38.7 °C, and
  the temperature at which growth actually reaches zero from 47.5 °C to 39.0 °C.

So the asymmetry falls from **12.5×** to **2.0×**. It is still an asymmetry, and it still points
the same way; it is not the near-total insensitivity the prior run showed.

## 4. (c) The draws, which are the quotable result

The paper's results are stated over 100 posterior models with percentile bands, not at a median
particle, so the ensemble is the right object. All 100 posterior particles and 40 of the 128 prior
particles were run.

| | prior draws | **posterior draws** |
|---|---|---|
| usable / total | 34 / 40 | **98 / 100** |
| T_opt range, median [5–95 %] | 3.22 [0.02, 20.14] °C | **8.89 [4.40, 27.02] °C** |
| CT_max range, median [5–95 %] | 3.67 [0.00, 11.93] °C | **4.59 [2.71, 11.03] °C** |
| 99 % plateau, loose cap | 0.50 [0.00, 8.07] °C | **1.50 [0.43, 2.72] °C** |
| 99 % plateau, tight cap | 0.50 [0.00, 3.85] °C | **7.25 [1.43, 7.50] °C** |
| T_opt range > CT_max range | **50 %** of draws | **92 %** of draws |
| plateau widens under the cap | **35 %** of draws | **93 %** of draws |

**The effect is far more consistent at the posterior than at the prior.** At the prior it is a coin
flip — half the draws have CT_max moving more than T_opt, and the plateau widens in only a third.
At the posterior, T_opt moves more than CT_max in **92 %** of models and the plateau widens under
the substrate cap in **93 %**.

That the *prior draws* do not support the finding while the *prior point table* gives a clean
12.5× is not a contradiction: the prior's per-enzyme Topt width is 13 °C, sampled independently for
764 enzymes, so an individual prior curve is ragged in a way the smooth prior table is not. The
calibration's work — shrinking Topt to 7.1 °C and Tm to 4.0 °C — is what turns a coin flip into a
93 % effect.

## 5. The plateau is the descriptor that survives, and T_opt is censored

Under a tight glucose cap the model's growth **rises with temperature until the substrate limit
binds and then goes exactly flat at the ceiling the cap allows** — 0.0968 h⁻¹ at cap 1, reached by
about 15 °C and held to about 38 °C. Probed directly on the posterior median:

| T (°C) | 5 | 7 | 9 | 11 | 13 | 15 | 17 | 19 | 21 | 23 |
|---|---|---|---|---|---|---|---|---|---|---|
| µ at cap 1 | 0.0153 | 0.0253 | 0.0396 | 0.0595 | 0.0853 | **0.0968** | **0.0968** | **0.0968** | **0.0968** | **0.0968** |
| µ at cap 10 | 0.0159 | 0.0300 | 0.0502 | 0.0777 | 0.1128 | 0.1550 | 0.2022 | 0.2471 | 0.2844 | 0.3165 |

The top is a **ceiling, not a peak**. `argmax` therefore returns the first point of an exact tie,
which is the grid's lower bound — 44 of the 98 usable posterior draws report `T_opt = 20.0 °C` for
that reason, and their T_opt range is a **lower bound**.

This is not an artefact to be filtered out, and the first version of this analysis wrongly did
filter it out (`DECISIONS.md` §9). Those 44 draws are the ones exhibiting the effect most cleanly;
dropping them biases the T_opt range downward. Extending the temperature grid downward would not
help either — growth is still rising at 5–13 °C, so the tie and the censoring would move with the
grid.

**So the finding is properly stated as Y1 stated it — as the loss of a sharply-defined optimum, not
as a shift — and the plateau is the number to quote:** 1.5 °C → 7.25 °C, in 93 % of their posterior
models.

## 6. What the calibration did to the parameters, now measurable

Y1 PART D had the paper but not the file, so it could report counts, correlations and average
widths, but no signed shift. Across all 764 enzymes, posterior mean minus prior file:

| | mean | median | sd | range | direction |
|---|---|---|---|---|---|
| **Tm** | **+1.33 °C** | +1.24 | 2.01 | [−6.30, +7.84] | 572 up, 192 down |
| **Topt** | **−6.32 °C** | −6.28 | 3.81 | [−18.65, +5.84] | 721 down, 43 up |

The calibration moved stability slightly **up** across the proteome while pulling the catalytic
optimum sharply **down** almost everywhere — consistent with *"the approach tended to change the
enzyme Topt rather than its Tm and ΔCp‡"* (Fig. 2e) and with Tm's posterior-vs-experiment
r = 0.97 (Fig. 2g), and now with a direction and a size attached.

**But not uniformly, and the exception is the one that matters.** The nine enzymes whose posterior
mean Tm falls below 42 °C reproduce the paper's named list **exactly** — ADH1, ALA1, ATP1, ERG1,
HEM1, KRS1, PDB1, SER1, TRP3 (Supplementary Fig. 8): nine of nine, none extra, none missing, which
is a second independent check on the file. **Seven of those nine moved *down* in Tm** against a
proteome that moved up:

| gene | prior Tm (°C) | posterior mean Tm (°C) | ΔTm | prior Topt (°C) | posterior Topt | ΔTopt |
|---|---|---|---|---|---|---|
| ERG1 | 40.46 | 36.79 ± 1.47 | **−3.66** | 34.0 | 24.00 | −10.00 |
| ATP1 | 43.80 | 37.49 ± 1.16 | **−6.30** | 32.0 | 21.51 | −10.49 |
| ALA1 | 42.69 | 40.63 ± 3.07 | −2.06 | 35.0 | 24.77 | −10.23 |
| KRS1 | 42.49 | 40.87 ± 2.48 | −1.62 | 35.0 | 22.68 | −12.32 |
| SER1 | 42.42 | 41.13 ± 2.73 | −1.29 | 35.0 | 27.57 | −7.43 |
| HEM1 | 43.15 | 41.30 ± 2.93 | −1.85 | 34.0 | 26.82 | −7.18 |
| PDB1 | 42.09 | 41.40 ± 2.86 | −0.69 | 35.0 | 25.72 | −9.28 |
| ADH1 | 41.32 | 41.77 ± 2.72 | +0.45 | 41.0 | 27.94 | −13.06 |
| TRP3 | 41.60 | 41.83 ± 2.73 | +0.23 | 33.0 | 25.68 | −7.32 |

**And the set is not the prior's set.** Enzymes below 42 °C in the prior: ADH1, ADK1, BPL1, ERG1,
GDB1, ILV1, TRP3 — seven, overlapping the posterior's nine in only **three**. Four left the set and
six entered it. Y1 wrote that "seven enzymes were already below 42 °C in the prior against nine in
the posterior", which is true but reads as a continuity that is not there: **the identity of the
limit-setting set is largely a product of the calibration**, and ERG1 — the paper's headline
enzyme — had its melting temperature pulled down 3.7 °C by it.

That refines, rather than reverses, Y1 PART D. Their calibration did not pull stability down
*globally* — it raised it slightly. It pulled it down **selectively, on the enzymes that end up
setting the thermal limit**, by 0.7–6.3 °C. Our E. coli needed a *global* ΔTm = −5.6 K on a
measured meltome. The two are not the same move, but they are less far apart than Y1 could see
from the paper alone.

## 7. What may now be quoted, and at what interval

> In Li *et al.*'s published yeast etcGEM, evaluated over their own 100 posterior models with
> their own code, switching the binding constraint from enzyme capacity to substrate uptake
> **widens the top of the thermal performance curve from 1.5 °C [0.4, 2.7] to 7.3 °C [1.4, 7.5]
> (99 % plateau, median and 5–95 %), in 93 % of the posterior models**, while the upper thermal
> limit moves 4.6 °C [2.7, 11.0]. The location of the optimum moves 8.9 °C [4.4, 27.0], a lower
> bound in 44 of 98 models because the optimum leaves the 20–50 °C window. T_opt moves further
> than CT_max in 92 % of posterior models, against 50 % of prior models.

Not quotable as a property of their calibrated model: **10.09 °C / 0.81 °C**. That pair is the
prior *point* table, and at the posterior CT_max is no longer regime-insensitive.

The claim that generalises, stated at the strength the evidence supports: **a change of binding
constraint destroys the sharply-defined optimum of a thermal performance curve while leaving the
upper limit far less affected — in five organisms across two independent codebases, and in 93 % of
the reference implementation's own posterior models.** The clean "T_opt moves, CT_max does not"
form of it holds at the prior and does not hold at the posterior.

## 8. What was not done

The chemostat condition was not swept; the test uses batch growth, as Y1 did. The anaerobic model
was not run. Only the glucose lever was drawn over: Y1 showed σ is not a regime change, and the
`prior_file` re-run reproduces the σ lever in full. 40 of 128 prior particles were run, not all;
100 of 100 posterior particles were.
