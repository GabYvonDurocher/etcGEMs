# K1 — port verification: the core reproduces the standalone Candida etcGEM

**Verdict: PASS. 57 of 57 comparisons within tolerance; 48 of them (the predicted growth
rate at every temperature for all four species) agree exactly at the standalone's own
4-decimal precision.**

This file is the evidence that two implementations of the same model agree at one point.
It decides nothing scientific. K2 — the same four strains under this repository's own
thermal form — is where any number is allowed to move.

* **Port:** `src/etcgem` (this repository) with `thermal_model: phenomenological`, four
  strains under `strains/`, run by `etcgem transfer`.
* **Standalone:** `gem/` of the `Candidas` repository at commit
  `f123bc7489cc4f8a1d0e198a93725034c9f347e6`, read only. Nothing in it was modified, and
  the only thing run there was `22_thermal_sensitivity.py`, which writes no files.
* **Machine-checked:** `reports/candida_thermal_limit/gate_table.py` regenerates
  `gate_table.csv` and exits non-zero if any row fails.

## Tolerance (stated before the comparison was run)

| quantity | tolerance |
|---|---|
| fitted globals (σ, w, P, SCALE, MSE) | within 2% |
| predicted µ at each temperature | within 1×10⁻³ h⁻¹ **or** 1%, whichever is larger |
| thermal limits | within 0.2 °C |
| pool-binding growth rates | same rule as µ |

## The gate table

### 1. The fitted globals — `gem/tables/etcgem_calib.json`, from `18_build_etcgem_tpc.py`

| quantity | standalone | port | tolerance | |
|---|---|---|---|---|
| σ, Gaussian peak width (°C) | 10.231397 | 10.231397 | 2% | **PASS** |
| w, denaturation width (°C) | 8.788455 | 8.788455 | 2% | **PASS** |
| P, pool budget (g enzyme/gDW) | 0.356974 | 0.356974 | 2% | **PASS** |
| SCALE, growth scale (peak match on *C. auris*) | 2.074124 | 2.074124 | 2% | **PASS** |
| *C. auris* calibration MSE | 0.00359151 | 0.00359151 | 2% | **PASS** |

The three fitted globals agree to every digit the standalone stores — the multi-start
Nelder-Mead search visits the same points and converges to the same simplex, which it can
only do if the objective it is evaluating is the same function.

### 2. Predicted µ at every temperature, all four species — `gem/tables/etcgem_tpc_pred.csv`

48 comparisons (4 species × 12 temperatures, 22–44 °C). **Largest absolute difference:
0.000000 h⁻¹.** Every value is identical at the 4 decimal places the standalone rounds to.

| °C | 22 | 24 | 26 | 28 | 30 | 32 | 34 | 36 | 38 | 40 | 42 | 44 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| *C. auris* | 0.1871 | 0.3023 | 0.4350 | 0.5660 | 0.6785 | 0.7595 | 0.7988 | 0.7931 | 0.7452 | 0.6635 | 0.5599 | 0.4474 |
| *C. haemulonii* | 0.2213 | 0.3191 | 0.4294 | 0.5388 | 0.6314 | 0.6996 | 0.7305 | 0.7192 | 0.6689 | 0.5884 | 0.4891 | 0.3833 |
| *C. duobushaemulonii* | 0.2132 | 0.2931 | 0.3754 | 0.4495 | 0.5074 | 0.5424 | 0.5537 | 0.5381 | 0.4962 | 0.4346 | 0.3611 | 0.2843 |
| *C. parapsilosis* | 0.2922 | 0.4183 | 0.5452 | 0.6562 | 0.7377 | 0.7808 | 0.7861 | 0.7825 | 0.7423 | 0.6662 | 0.5652 | 0.4496 |

(Port and standalone; one table, because they do not differ.)

### 3. Thermal limit at the detection floor — `gem/FIG4_LOCKED.md`, from `22_thermal_sensitivity.py`

`FIG4_LOCKED.md` states the range across the four species, not the four values.

| quantity | standalone | port | tolerance | |
|---|---|---|---|---|
| lowest of the four species (°C) | 52.7 | 52.72 | 0.2 °C | **PASS** |
| highest of the four species (°C) | 54.5 | 54.53 | 0.2 °C | **PASS** |

Port values, all four species (`outputs/transfer_candida_pinned_maint/summary.csv`):
*C. duobushaemulonii* 52.72, *C. parapsilosis* 53.33, *C. haemulonii* 53.56,
*C. auris* 54.53 °C — i.e. 52.7–54.5 °C, the locked range.

**This row uses `transfer_candida_pinned_maint`, not `transfer_candida`, and that is a
finding about the standalone (see below), not a change of configuration to make a number
fit.**

### 4. The pool-binding precondition — `gem/notes/POOL_BINDING_RESULT.md`, from `16_pool_binding_test.py`

| quantity | standalone | port | tolerance | |
|---|---|---|---|---|
| *C. auris* maximum, pool removed (plain GEM), h⁻¹ | 2.045 | 2.0450 | 1×10⁻³ or 1% | **PASS** |
| *C. auris* maximum, pool at P = 0.25 with EC-class kcats, h⁻¹ | 0.758 | 0.7579 | 1×10⁻³ or 1% | **PASS** |

(The prompt's 2.05 vs 0.76 are these two, rounded.) The second uses the generic EC-class
prior kcats that test deliberately uses, not the DLKcat kcats — hence the separate table
`strains/cauris_iRV973/dltkcat/kcat_table_ecclass.csv`, written by
`to_strain_inputs.py --ec-class-kcat`.

## What was switched off in the core to match sMOMENT

The core's `smoment_gem` per-flux cost is `MW/(kcat·3600)` charged on the forward **and**
reverse variable of every enzymatic reaction from one shared pool — the same expression
the standalone writes, with no extra factor. What the core adds for **other** strains and
what the Candida `strain.yaml` therefore switches off:

| the core's addition | how it is switched off | why |
|---|---|---|
| grounded pool budget `P_total × σ_sat × f_metab` | `provider.pool_budget` given directly (0.356974); `p_total`, `sigma`, `f_metab` absent | the standalone **fits** P; the grounded product is a different, and better, way of setting it, and it is K2's business |
| proteome-sector layer (metabolic / maintenance / biosynthesis caps, growth law) | `proteome_sectors.enabled: false` | the standalone has one pool and one budget |
| temperature-dependent maintenance NGAM(T) | `ngam_temperature` absent (default false) | the standalone has no maintenance layer |
| MMRT peak-normalised `kcat(T)`, and the two-state unfolding form | `thermal_model: phenomenological` | the whole point of C1: the third form is the standalone's |
| free-energy-sink closure, relaxation of pinned reactions, DLTKcat Topt/dCp overlay | `close_free_sinks`, `relax_pinned`, `dltkcat_fits` all absent | none is in the standalone |
| `kcat_scale` (global turnover level) | left at its default 1.0 | no-op |
| maintenance pin `pin_at_ub` | `null` in every `strain.yaml` | matches `18_build_etcgem_tpc.py`, which produced the locked µ table |

`close_free_o2_sinks: true` in `configs/defaults.yaml` is read only by the `gecko`
provider and never reaches this route; `dcp_prior_kJ: -4.0` is carried into the thermal
table for K2 and is ignored by the phenomenological form.

Two things had to be **added**, not switched off, because the core had no equivalent:

* `providers.apply_exchange_medium` — the medium as an exchange table on a plain GEM. The
  existing `set_medium` works on GECKO-split `EX_<met>_e_REV` uptake reactions, of which a
  plain SBML GEM has none.
* `cfg.solver` — an explicit LP solver, see the second finding below.

## Findings

**1. The standalone is not internally consistent about the maintenance reaction, and the
locked numbers come from both sides of it.** `22_thermal_sensitivity.py` pins the
maintenance reaction at its own upper bound (`MAINT`, commented "parapsilosis fix, as
everywhere else"); `18_build_etcgem_tpc.py`, which produced the locked calibration and the
locked µ table, does not. It matters for exactly one model: in the three iRV973-derived
models `ATP_maintenance_NGAM__cyto` is already fixed at (3.89, 3.89), so pinning is a
no-op, but iDC1003's `ATP_Maintenance__cyto` is **reversible** at (−3.9, 3.9), so without
the pin the LP may run maintenance backwards and make ATP for free. Unpinned,
*C. parapsilosis*' thermal limit is 55.18 °C and its peak is 0.786 h⁻¹ at 34 °C; pinned,
53.33 °C and 0.683 h⁻¹ at 36 °C — the difference between falling inside the locked
52.7–54.5 °C range and falling outside it.

This was not fixed on either side. The port runs both configurations and reports each
locked number against the run whose producing script it came from:
`transfer_candida.yaml` (no pin) for the calibration and the µ table,
`transfer_candida_pinned_maint.yaml` (pin) for the thermal limits. Which of the two is
right is a modelling question, and it is K2's.

**2. The solver is load-bearing at one point, at the 0.4% level.** With Gurobi the port
reproduced 47 of the 48 µ values exactly and missed the 48th — the coldest, numerically
hardest point (22 °C) of each of the two **draft** models — by 0.0010 and 0.0008 h⁻¹
(≈0.4%). Under GLPK, which is what the standalone solved with, all 48 agree exactly. The
four `strain.yaml` therefore pin `solver: glpk`, with the reason stated in the file. Both
answers are within the stated µ tolerance, so this did not change the verdict; it is
recorded because it is the only place where the port's numbers depend on something other
than the model.

**3. `FIG4_LOCKED.md` does not itself carry most of what a port has to match.** It locks
the counterfactual separations, the paired ΔTm/ΔTopt statistics, the fold gaps and the
thermal-limit range — the numbers Figure 4 prints. The fitted globals and the
per-temperature predictions, which are what actually pins the model, live in the committed
tables it points at (`etcgem_calib.json`, `etcgem_tpc_pred.csv`). The gate above is against
both: the locked file for what it locks, and the committed tables for the rest.

**4. `gem/tables/etcgem_tpc_pred_fine.csv` is stale.** It exists, and
`18_build_etcgem_tpc.py` as it now stands does not write it (its `main` writes
`etcgem_tpc_pred.csv` only, despite the README listing both). Its values differ from the
coarse table at shared temperatures — *C. auris* at 22 °C is 0.2155 in the fine table
against 0.1871 in the coarse one — so it was produced by an earlier calibration. It was
not used as a gate reference, and nothing downstream in the port reads it. Reported, not
touched.

**5. No measured-respiration curve was copied, because `gem/` builds none.** The prompt
asked for measured respiration "where it exists". The only measured table `gem/` consumes
is `measured_tpc_honest.csv`, and it is already respirometric: `17_build_measured_tpc.py`
fits µ from each well's oxygen trace (`Oxygen_Data_Filtered.csv`,
`derived_N0_R_results_with_carbon.csv`, `well_drawdown_peak.csv`), counting dead wells as
zeros. The Candidas repository's wider `results/tables/` has respiration analyses
(Arrhenius and Sharpe–Schoolfield coefficient tables, Bayesian posteriors), but they are
fitted coefficients rather than a per-temperature measured curve and no `gem/` script
reads them. So each strain carries one measured file, `thermal/measured_tpc.csv`.

## Input counts, port vs standalone

Per species: reactions in the model, of which enzyme-costed, of which with a DLKcat kcat,
of which with a sequence-predicted Topt and Tm. Produced by
`tools/reconstruction/to_strain_inputs.py` and recorded in each strain's
`dltkcat/converter_report.json`.

| | *C. auris* | *C. haemulonii* | *C. duobushaemulonii* | *C. parapsilosis* |
|---|---|---|---|---|
| reactions in the model | 2863 | 2863 | 2863 | 2162 |
| exchange / boundary (skipped) | 352 | 352 | 352 | 358 |
| biomass (skipped) | 1 | 1 | 1 | 1 |
| no GPR (skipped, enzyme-free) | 1196 | 1198 | 1200 | 197 |
| no molecular weight (skipped) | 0 | 0 | 0 | 0 |
| **enzyme-costed reactions** | **1314** | **1312** | **1310** | **1606** |
| with a DLKcat kcat | 1066 | 1064 | 1062 | 1313 |
| at the 13.7 s⁻¹ default | 248 | 248 | 248 | 293 |
| with predicted Topt and Tm | 1055 | 1042 | 1049 | 1305 |
| at the species median Topt/Tm | 259 | 270 | 261 | 301 |
| species median Topt / Tm (°C) | 34.65 / 53.68 | 34.64 / 53.54 | 34.55 / 53.52 | 33.65 / 54.21 |
| genes with a molecular weight | 709 | 696 | 674 | 1003 |
| genes with a Topt / Tm prediction | 704 | 679 | 662 | 997 |

The enzyme-costed counts are the standalone's own term counts, verified directly against
its `precompute()` term set (`setup {sp}: N enzyme-costed reactions`): 1314 / 1312 / 1310 /
1606. The join is complete in one direction — every row of `kcat_reaction_<sp>.csv` matched
a costed reaction, 1066 / 1064 / 1062 / 1313, none left over. It is not complete in the
other, and that is the standalone's own behaviour: a costed reaction with no DLKcat kcat
takes 13.7 s⁻¹ and, having no `best_gene`, the species-median Topt and Tm. A further
handful of reactions *do* have a `best_gene` whose sequence has no Seq2Topt/Seq2Tm
prediction (Seq2* drops sequences over 2000 aa); those genes are listed per strain in
`dltkcat/converter_report.json` — 4 (auris), 9 (haemulonii), 7 (duobushaemulonii),
3 (parapsilosis) genes — and their reactions also take the median.

## Exact commands

Since N1 TASK 2 the gate is **self-contained**: every expected value is frozen in the
committed fixture `standalone_expected.json` (Candidas commit `f123bc7`, with the md5 of
each source file), so it runs with no Candidas repository present. `--candidas-root` still
reads the standalone directly and reports any drift from the fixture first.

```bash
python3 reports/candida_thermal_limit/gate_table.py            # from the fixture; exit 0 = PASS

export CANDIDAS_ROOT=".../Candidas"      # read only, optional

# inputs (already committed; re-running reproduces them byte for byte)
python3 tools/reconstruction/to_strain_inputs.py --species all
python3 tools/reconstruction/to_strain_inputs.py --species auris --ec-class-kcat

# the gate runs
etcgem transfer --experiment transfer_candida                 # calibration + mu table (matches 18)
etcgem transfer --experiment transfer_candida_pinned_maint    # thermal limits (matches 22)
etcgem fba --strain cauris_iRV973 --experiment candida_pool_unconstrained --temp 30
etcgem fba --strain cauris_iRV973 --experiment candida_pool_binding --temp 30

# the comparison
python3 reports/candida_thermal_limit/gate_table.py --candidas-root "$CANDIDAS_ROOT"   # + drift check
```

## Existing strains unchanged

`etcgem tpc --strain eciML1515` and `etcgem tpc --strain mmaripaludis` produce
byte-identical `nominal_tpc.csv`, `descriptors.json` and `resolved_config.yaml` before and
after every change in K1 — all six files, checked with `cmp`, not asserted. (Note,
separately from K1: `strains/eciML1515/outputs/tpc/` as committed does not match what the
current code produces. That drift predates this branch and is untouched by it; the
before/after comparison above is against a baseline generated from `main`.)
