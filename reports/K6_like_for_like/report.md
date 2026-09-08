# K6 — K5's model-versus-measurement comparison, redone like for like

_2026-09-08. Branched from `main` at **b23cb44**, the K5 merge. P4 was still running, so
`strains/eciML1515/` and `reports/ecoli_*` are never written._

K5 reported the project's sharpest discrepancy against data: an activation-energy difference of
**−0.33 eV** in the model against **+0.33 eV** measured, "the wrong sign in all four species",
and concluded it pointed at the maintenance layer. K6 checks that comparison.

**The verdict, in three parts, deliberately not rounded together.**

1. **The sign was a comparator artefact.** Against every valid comparator the model's sign
   agrees with measurement in all four species. That part of K5's result does not stand.
2. **A magnitude gap is real.** The model's difference is 2.2 to 5.1 times more negative than
   measured and lies outside the credible interval in all four species.
3. **K5's explanation is wrong in direction.** More maintenance moves the model away from
   measurement and kills it. About 88 % of the residual gap is the model's growth rising too
   steeply, which is the enzyme kinetic envelope, not maintenance and not the ETC.

Reproduce with:

```bash
CANDIDAS_ROOT=... python3 reports/K6_like_for_like/task1_two_measured_E.py
CANDIDAS_ROOT=... python3 reports/K6_like_for_like/task2_like_for_like.py
CANDIDAS_ROOT=... python3 reports/K6_like_for_like/task3_maintenance_test.py
```

Detail in `task1_measured_E.md`, `task2_like_for_like.md`, `task3_verdict.md` and
`task4_comparator_hazard.md`.

---

## 1. Two measured activation energies, and they are not the same quantity

The prompt's framing was verified rather than assumed, by reading the fitting code.

| | form | window | deactivation |
|---|---|---|---|
| OLS (`fit_arr_lm`) — **what K5 used** | `lm(ln y ~ boltz)` | every temperature | **none** |
| Bayesian growth (`fit_ss_hier`) | **Sharpe-Schoolfield** | every temperature | **yes**, own `Eh`, `Th` |
| Bayesian respiration (`fit_arr_hier`) | Arrhenius | every temperature | none |

The Sharpe-Schoolfield `E` is the **rising-limb** activation energy; the OLS `E` is the slope of
a straight line through a curve that turns over. The empirical test settles it: refitting the
OLS on the rising limb moves E_growth from 0.01–0.35 eV to 0.21–0.93, toward the Bayesian
0.62–1.15, and *C. duobushaemulonii* lands on 0.627 against a Bayesian 0.622. **E_resp is
unaffected** — OLS 0.518 against Bayesian 0.518 for the model organism — because respiration
does not turn over. A four-fold disagreement on growth and none on respiration is exactly what a
turnover-contaminated growth fit looks like.

## 2. The comparison, three ways, both sides fitted identically

E_resp − E_growth, repaired model:

| species | (a) rising limb, organism's window | | (b) full window — K5's | | (c) manuscript convention | |
|---|---|---|---|---|---|---|
| | model | measured | model | measured | model | measured [95 % CI] |
| *C. auris* (clade I) | −0.917 | −0.347 | −0.329 | **+0.341** | −0.969 | −0.383 [−0.56, −0.21] |
| *C. haemulonii* | −1.174 | −0.426 | −0.360 | +0.156 | −1.388 | −0.363 [−0.57, −0.15] |
| *C. duobushaemulonii* | −0.803 | −0.338 | −0.079 | +0.482 | −0.757 | −0.149 [−0.36, +0.06] |
| *C. parapsilosis* | −0.785 | −0.412 | −0.416 | +0.191 | −1.018 | −0.464 [−0.68, −0.27] |
| **sign agrees** | **4 / 4** | | **0 / 4** | | **4 / 4** | |

Panel (b) is the only one where the sign disagrees, and the only one whose window contains the
organism's collapse but not the model's. The models over-predict the thermal limit by 9.6 to
15.8 °C (K4, §4), so a straight line over 22–44 °C depresses the measured E_growth and leaves the
model's alone.

K5's other two rows shrink the same way once restricted to where the organism actually grows.
The respiration-to-growth rise K5 gave as **4.70× measured against 1.20× model** is **1.57×
against 1.03×** within *C. auris*' growing range — the same direction at a third of the size.

## 3. Where the surviving gap is

Scaling maintenance, *C. auris*, everything else held:

| NGAM × | E_growth | E_resp | difference | peak µ |
|---|---|---|---|---|
| 0 | 1.218 | **0.474** | **−0.744** | 0.0904 |
| 1 (as configured) | 1.200 | 0.231 | −0.969 | 0.0683 |
| 2 | 1.176 | 0.226 | −0.950 | 0.0477 |
| 5 | −3.115 | 0.430 | +3.544 | 0.0028 |
| 10 | — | — | — | **0.0000** |

More maintenance is worse, and the model is dead before the quantity moves. **Removing it fixes
the respiration term almost exactly** — E_resp 0.231 → 0.474 against a measured 0.518.

With maintenance off, the residual decomposes as: E_resp off by −0.04, E_growth off by **+0.32**.
**About 88 % of what is left is the model's growth rising too steeply on the rising limb**
(1.218 against a measured 0.901). That implicates the shared dCp prior and the MMRT curvature,
and it is consistent with the same models over-predicting the upper thermal limit by 9.6–15.8 °C
— a connection not previously drawn.

## 4. The hazard, recorded

Second time in this project. `docs/OPEN_ITEMS.md` §4 now carries the rule and the known
multi-valued quantities, with both numbers each. **A second instance was found, and it is larger
than the one that prompted this**: `measured_tpc_honest.csv`, which every *Candida* strain
calibrates against, counts a dead well as an observed zero, while
`derived_N0_R_results_with_carbon.csv` keeps only survivors. At 40 °C *C. haemulonii* grows at
0.000 /h by the first and 0.66 /h by the second. Both are right; mixing them is the trap; and
the two files are used side by side throughout the project.

## What was changed, and what was not

**Nothing was tuned.** No measured file was edited, `candida_B5_respire` is unchanged, and no
NGAM value was adopted. K5's report is corrected with two **dated notes** at the points where
the claims are made; its history stands as written.

## Verification

| check | result |
|---|---|
| K1 gate, `$CANDIDAS_ROOT` unset | **79/79 PASS, exit 0** |
| `stamp_reports.py --check` | exit 0 |
| all K6 scripts re-run | exit 0, tables regenerate |
| `strains/eciML1515/`, `reports/ecoli_*` | untouched; P4 had not landed |
