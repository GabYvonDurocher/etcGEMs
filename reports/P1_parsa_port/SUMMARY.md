# P1 — summary

| part | status | one line |
|---|---|---|
| **A** — inventory and fork point | **DONE** | Fork point is a 25-hour window, not a point; one of the prompt's premises corrected; a blocking data gap found |
| **B** — core mechanisms | **DONE** | Gas flux, carbon cap, overflow line, transport costing and ONE ETC-area mechanism; E and F collapsed; configuration D folded in as a spec set |
| **C** — E. coli specifics | **DONE** | `gas_exchange.yaml`, two ETC tables, the NLDM recipe; six selectable experiment overlays |
| **D** — scripts | **DONE** | 8 PORT (→ one CLI verb + one figure builder), 17 report builders dropped as a class, 47 one-offs dropped with reasons |
| **E** — the gate | **DONE** | **60 comparisons, 60 PASS, 0 FAIL**; every movement attributed; D/E/F listed with costs and a data gap |
| **F** — thermal vs carbon | **DONE, and it is a flag** | The overflow mechanism moves T_opt when the cap binds hard; CT_max is unmoved |

Detail: [PARTA_inventory.md](PARTA_inventory.md), [PARTD_scripts.md](PARTD_scripts.md),
[gate.md](gate.md), [PARTF_thermal_vs_carbon.md](PARTF_thermal_vs_carbon.md),
[DECISIONS.md](DECISIONS.md) (D0–D6).

---

## 1. Fork point — confirmed, and narrowed

All 21 shared modules in his `src/etcgem` are exact ancestors; he modified no core module. The
whole tree is byte-identical to `main` at eleven consecutive commits, **`e67b4c0` (2026-07-09
21:00:51) → `8c2c30f` (2026-07-10 21:55:56)**, diverging at `99eab16` (21:58:06). The prompt's
`e67b4c0` is the earliest commit consistent with the content, not the only one.

**Correction to a premise:** his baseline does **not** predate `a416fd1`. That commit is a week
earlier, and his `strain.yaml` and every file under `dltkcat/media/model/proteomics/thermal` are
byte-identical to ours. His v3 posterior is our v3 posterior to every stored digit. `a416fd1`
was struck from the gate's attributions before any number was compared.

## 2. Core mechanisms — no E. coli anything in the code

`src/etcgem/gasflux.py` (flux TPCs, total-carbon cap, overflow line, transport costing, the
emergent overflow threshold), `src/etcgem/etc_area.py` (the membrane-area budget and proton
stoichiometry), `providers.set_medium_recipe`, `tpc.apply_state`, `config.apply_gasflux`, a
`gasflux` CLI verb, and `calibration_multi.{build_overflow_specs, WIDE_ENVELOPE_SPECS,
build_pm_medium}`. Checked by grep: no reaction id, footprint or measured value in either new
module.

**E and F are one mechanism.** The ETC table carries `complex, area_nm2, kcat_s, reactions,
h_p_target`; configuration F is that table with the bd oxidases split and
`apply_proton_stoichiometry: true`. There is no configuration-F module.

**`block_free_o2_sinks` removed**, as the prompt required — and the decision was tested, not
assumed: closing the sinks after the build (his order) does change the model
(`translation_coeff` 0.0775 vs 0.07867) and changes no output number, because the growth law
relaxes the biosynthesis cap.

**Configuration D folded in, not carried across.** `build_overflow_specs()` is the v3 lever set
plus an optional fitted `C_max_mult` and optional widened envelope priors;
`gasflux.overflow_threshold` is the Basan-threshold likelihood term, generically. The growth
term is deliberately **not** written — its data is missing, and a fixture would be worse.

## 3. The gate — 60/60

| | |
|---|---|
| comparisons | 60 (configs A/B/C × 4 media × 5 quantities) |
| PASS / FAIL | **60 / 0** |
| T_opt | **exact** in all twelve medium × configuration cases |
| largest difference | **8.3 × 10⁻⁴ relative** |

His report's quoted figures, reproduced: RQ at C_max 60 — 1.07 / 0.90 / 0.99 / 1.00 → **1.0726
/ 0.8974 / 0.9916 / 0.9976**; configuration C r_max 2.27 (NLDM) and 2.13 (LB/BHI) → **2.2649**
and **2.1298 / 2.1304**; configuration C RQ 7–9 and ≈0 → **7.375** and **0.198**; configuration
A "fermentative, RQ ≈ 0" → **0.0192**.

**Every movement is attributed.** The NLDM difference is his own undocumented change of medium
(blanket → recipe), established in four steps including running his code at his own fork point;
the ≤8.3 × 10⁻⁴ residual is demonstrably not attributable to any commit here, since his
fork-point code reproduces the port exactly. Full argument in `gate.md`.

**Not checkable, and why:** configurations D, E and F are calibrations against
`derived_N0_R_results_with_carbon.csv`, which is **not in the snapshot**. They cannot be gated
at any price until that file is supplied; with it, ~4 h 28 min of emcee per fit.

## 4. PART F — the flag

| | weak cap (c_max 230, glucose) | binding cap (c_max 60) |
|---|---|---|
| T_opt | **exactly unchanged** | **39.0 → 32.5 °C (NLDM)**, 38.0 → 37.5 (glucose) |
| CT_max | +0.004 % | +0.66 % (NLDM), +0.49 % (glucose) |
| E_a | −0.065 % | **+29.6 % (NLDM)** |
| carbon | O2 −38.6 %, CO2 +598 %, acetate 0 → 5.52, RQ ×11 | RQ 0.019 → 1.073 |

**The upper thermal limit composes with the overflow mechanism; the optimum, the cold limb and
E_a do not.** A carbon cap tight enough to make the gas exchange respiratory — including the
value his own configuration-B figures use — relocates T_opt by several degrees. This is the
third constraint found to relocate T_opt in this model (N3 found the translation cap does the
same); CT_max has been insensitive to all of them. Which operating point the thermal results
should be quoted at is a human decision, and is not taken here.

## 5. Verification

| check | result |
|---|---|
| eciML1515 / mmaripaludis / syn6803 nominal TPCs | **byte-identical** to the committed files |
| Candida gate, `$CANDIDAS_ROOT` unset | **79 comparisons, 79 PASS, 0 FAIL** |
| the four Candida strains' `transfer_candida` outputs | **byte-identical** (re-run, clean `git status`) |
| E. coli identifiers in `src/etcgem/{gasflux,etc_area}.py` | **none** |
| imported from his outputs tree | **nothing** — every input his configurations need is already here and byte-identical |
| `$PARSA_ROOT` | **untouched**: no file inside modified |
| all six configurations | build and run |

## 6. What is left for a human

1. **`derived_N0_R_results_with_carbon.csv`** — without it configurations D, E and F cannot be
   fitted or gated. Everything needed to do it without a second calibrator is in place.
2. **Which operating point the thermal results are quoted at**, given PART F.
3. **The transporter turnover**: his module says 30 s⁻¹, his figure, filename and report say
   300. The port carries 30 as the strain default and 300 in the configuration-A overlay, so
   both stay visible.
4. **The report itself.** `reports/ecoli_gasflux/` holds the assets and the convention; his
   prose in `outputs_reports/etcgem3_configuration_summary.pdf` is its source text.
