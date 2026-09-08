# P1 PART E — the gate: does the port reproduce Parsa's numbers?

Reproduce with:

```
etcgem gasflux --strain eciML1515 --experiment gasflux_configA
etcgem gasflux --strain eciML1515 --experiment gasflux_configB
etcgem gasflux --strain eciML1515 --experiment gasflux_configC
python reports/P1_parsa_port/gate.py
```

His values are transcribed in `parsa_expected.json` (the K1 precedent), so the gate runs
without `$PARSA_ROOT` present.

## Result

**60 comparisons, 60 PASS, 0 FAIL** — configurations A, B and C, four media each, five
quantities each (T_opt, r_max, O2 uptake, CO2 release and RQ at the optimum). T_opt matches
**exactly** in all twelve medium × configuration cases; every other quantity is within
**1 × 10⁻³ relative**, and the largest single difference anywhere is **8.3 × 10⁻⁴**.

Against the figures his PDF quotes:

| his report says | port |
|---|---|
| **B**: RQ at each medium's optimum, C_max 60 — glucose 1.07, NLDM 0.90, LB 0.99, BHI 1.00 | **1.0726, 0.8974, 0.9916, 0.9976** |
| **C**: r_max ≈ 2.27 h⁻¹ (R2A/NLDM) | **2.2649** |
| **C**: r_max ≈ 2.13 h⁻¹ (LB/BHI) | **2.1298 / 2.1304** |
| **C**: RQ ≈ 7–9 (NLDM), ≈ 0 (glucose) | **7.375**, **0.198** |
| **A**: RQ ≈ 0, fermentative | **0.0192** on glucose; the TCA cycle is off, as he reports |
| **A**: transporter k_cat 300 s⁻¹ | run setting; see the discrepancy noted below |

`gate_table.csv` carries all sixty rows.

## Attribution of every movement

The prompt's list of admissible attributions needed correcting before it could be used
(DECISIONS D0): **`a416fd1` cannot explain anything here**, because his snapshot post-dates it
by a week and his `strain.yaml` and every strain input file are byte-identical to ours. What
remains:

### 1. NLDM — attributed, demonstrated, and it is a change of his, not of ours

His NLDM references were produced with a **blanket** medium (every component open at the same
generous bound), not with the recipe-proportional uptake ceilings his committed
`set_medium_nldm` now applies. Evidence, in the order it was obtained (DECISIONS D5):

* the two medium implementations produce **identical bounds** on all 331 exchange reactions,
  so it is not a porting difference;
* closing the four O2 sinks after `build_provider`, as he did, changes `translation_coeff`
  0.07867 → 0.0775 and changes **no output number at all** (under the growth law the
  biosynthesis cap does not bind), so it is not the closure ordering;
* his own code at his own fork point (`8c2c30f`, in a scratch worktree) gives **the port's**
  numbers, not his committed ones, so it is not any commit in this repository;
* his `gasflux_C60.csv` is dated **2026-09-01 18:04** and the file supplying its `build_pm` is
  dated **2026-09-04 09:52** — the script was edited after the run — and his own
  `set_medium_nldm` carries a `recipe=False` path he calls "the legacy blanket bound";
* run with that blanket medium, the port reproduces his NLDM curve to **1.47 × 10⁻⁴** absolute
  with r_max and T_opt exact.

So the port keeps the recipe medium as the default — it is his later and better model — and
carries `NLDM_blanket` as an explicitly labelled legacy medium, which is what the gate compares
against. **The difference is a change he made and did not re-run, not an unexplained movement.**

### 2. The residual, ≤ 8.3 × 10⁻⁴ relative

Not attributable to anything in this repository, and that is a demonstrated statement rather
than a shrug: **his own code at his own fork point produces the port's numbers to the last
digit**, so no commit between his fork and today can be responsible. It is also not uniform —
his 2026-09-01 configuration-B NLDM run agrees with the port to **2 × 10⁻¹⁵**, while his
2026-07-10 and 2026-07-14 runs (configurations A and C, and configuration B's other media) sit
at 1 × 10⁻⁴ – 8 × 10⁻⁴. A residual that depends on **when he ran it** and not on what the code
says points at his run environment (solver build) rather than at either implementation. It is
four orders of magnitude below the precision his report quotes.

### 3. The O2-sink closure — the prompt's expected attribution, measured and found not to apply

His `gasflux.py` closes the same four reactions the core now closes by default (`8085036`,
credited to his audit), but *after* the provider is built, so his sector layer calibrated
`translation_coeff` on a model with the sinks open. That really is a different model state
(`translation_coeff` 0.0775 vs 0.07867, μ* 0.5545 vs 0.5462). **It moves no number in any of
these configurations**, because the coupled growth law relaxes the biosynthesis cap and the
metabolic pool binds instead. Tested rather than assumed, and `block_free_o2_sinks` was
removed from the port on the strength of it.

## One inconsistency in his own sources, reported not resolved

`gasflux.TRANSPORT_KCAT = 30.0` in his module; his configuration-A figure, its CSV filename
(`mmrt_transport_kcat300.csv`) and his report all say **300 s⁻¹**. The port takes the strain
default from `gas_exchange.transport_carrier.kcat_s` (30, his module constant) and
`gasflux_configA.yaml` overrides it to 300, so the gate compares like with like and the
disagreement stays visible instead of being silently resolved. His own
`scripts_transport_kcat_sweep.py` swept 30/100/300, so both numbers were live at some point;
which is intended is his call.

## What could NOT be checked, and what it would cost

| quantity | why not | cost |
|---|---|---|
| baseline growth R² = 0.96 | that is the v3 Van Derlinden fit | already committed here (`calibration_vanderlinden`); its posterior is **identical** to his, so the baseline is shared, not re-run |
| **D**: growth R² 0.71 (NLDM) / 0.90 (LB), respiration scale 3.4 / 3.6 | **the data is missing.** `calibration_configD` and eight scripts read `C:\Users\Parsa\Desktop\Presense_Analysis\Ecoli_R2A_LB\tables\derived_N0_R_results_with_carbon.csv`; a search of the whole 1.0 GB snapshot finds no R2A / respiration data | **cannot be run at any price until that file is supplied.** With it: an emcee fit of the same shape as the v3 run, which took 60 walkers × 6000 steps and **4 h 28 min on 10 processes** |
| **E**: growth R² 0.85/0.83, respiration R² 0.72/0.81, fitted F_ETC ≈ 0.28–0.32 | same missing data, plus a fit | as above, ×2 media |
| **F**: growth R² 0.91/0.88, respiration R² 0.96/0.85, LB C_max ≈ 510 | same | as above, ×2 media |
| **A**: the ≈ 9 mmol gDW⁻¹ h⁻¹ CO₂ FVA span on glucose | cheap, but it is an FVA over the whole model rather than a gas-flux run; not wired into the `gasflux` verb | one FVA, minutes — worth adding when the report needs it |

**Nothing that requires a calibration was run, and no substitute data was invented.** Ask
Parsa for `derived_N0_R_results_with_carbon.csv`; with it, configurations D, E and F become
gateable, and `calibration_multi.build_overflow_specs` + `build_pm_medium` +
`gasflux.overflow_threshold` are already in place to do it without a second calibrator.
