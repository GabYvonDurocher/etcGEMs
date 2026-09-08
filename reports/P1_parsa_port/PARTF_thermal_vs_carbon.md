# P1 PART F — does configuration D's overflow move the thermal descriptors, or only the carbon ones?

The question the prompt puts before anyone writes anything up: if the overflow mechanism leaves
the thermal envelope alone, the thermal work and the overflow work compose and can be written
up side by side; if T_opt or CT_max move, they cannot.

Reproduce with `python reports/P1_parsa_port/partF_thermal_vs_carbon.py` (a few hundred solves,
no calibration). Numbers in `partF_thermal_vs_carbon.csv`.

## The answer: it depends on how hard the cap binds, and at the value his own figures use, T_opt moves

Two media × three cap settings on one 5–55 °C grid (wider than the configurations' 5–50 so
CT_max is not censored), everything else at the v3 posterior operating point.

| medium | cap | T_opt | r_max | CT_max | CT_min | niche | E_a | O2@T_opt | CO2@T_opt | acetate@T_opt | RQ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| glucose | OFF | 38.0 | 1.1949 | 40.98 | 15.90 | 25.08 | 0.975 | 48.14 | 0.92 | 0 | 0.019 |
| glucose | 230 | **38.0** | 1.1869 | **40.98** | 15.87 | 25.11 | 0.974 | 29.56 | 6.44 | **5.52** | **0.218** |
| glucose | 60 | **37.5** | 0.8269 | **41.18** | 14.66 | 26.52 | 0.989 | 24.30 | 26.06 | 0 | **1.073** |
| NLDM | OFF | 39.0 | 1.9110 | 46.08 | 14.43 | 31.65 | 0.949 | 36.58 | 38.21 | 24.99 | 1.044 |
| NLDM | 230 | 39.0 | 1.9110 | 46.08 | 14.43 | 31.65 | 0.949 | 36.58 | 38.21 | 24.99 | 1.044 |
| NLDM | 60 | **32.5** | 0.9544 | **46.38** | 12.28 | 34.10 | **1.230** | 22.45 | 20.83 | 0 | 0.928 |

**With a weakly binding cap the answer is clean.** At his nominal NLDM cap of 230 on glucose,
the carbon read-out is transformed — O2 −38.6 %, CO2 +598 %, acetate 0 → 5.52 mmol gDW⁻¹ h⁻¹,
RQ 0.019 → 0.218 — while every thermal descriptor stands still: T_opt **exactly** unchanged,
CT_max 0.004 %, CT_min 0.15 %, niche 0.11 %, E_a 0.065 %. Only r_max moves, by 0.67 %. On NLDM
that cap is slack and nothing at all changes, which is an uninformative null and is labelled as
one in the script's output.

**With a cap that actually binds, it is not clean.** At C_max = 60 — the value his own
configuration-B figures use —

* **T_opt moves 39.0 → 32.5 °C on NLDM (−6.5 °C)** and 38.0 → 37.5 °C on glucose;
* **E_a moves 0.949 → 1.230 eV on NLDM (+29.6 %)**;
* CT_min −14.9 %, niche width +7.7 %;
* **CT_max does not move**: +0.66 % on NLDM, +0.49 % on glucose.

## What that means, stated and not adjudicated

**This must be flagged prominently, and it is the flag.** The upper thermal limit composes with
the overflow mechanism; the optimum, the cold limb and the activation energy do not. A carbon
cap tight enough to make the gas exchange respiratory is also tight enough to relocate T_opt by
several degrees, so a thermal result obtained without it and an overflow result obtained with
it are not two views of one model — they are two operating points, and only CT_max is common to
both.

This is the third constraint found to relocate T_opt in this model, and the pattern is
consistent: N3 established that at the strain's nominal operating point T_opt sits exactly where
the translation cap starts to bind, and that the same attribution does not hold at the tuned
rich point where that cap has slack (`reports/N3_output_audit/TASK2_cap_regime.md`). CT_max, by
contrast, has been insensitive to every constraint tried — it is set by the unfolding envelope.

**Not decided here:** which operating point the thermal results should be quoted at, or whether
the cap belongs in them. Those are the human decisions this measurement exists to inform.
