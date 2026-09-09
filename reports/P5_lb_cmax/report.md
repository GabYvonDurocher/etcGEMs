# P5 — merge P4 and K9, settle `c_max` on LB, and close two loose ends

| task | status | one line |
|---|---|---|
| **0** — merge P4, then K9 | **DONE** | Both merged `--no-ff`, both sets of rows kept, gates green after each, worktree removed, PRs closed, branches deleted |
| **1** — the LB `c_max` fit | **DONE** | His 257 / 459 / 510 confirmed at source; the one chain was **trapped in a dead mode by the warm start** and answers nothing; the question was answered deterministically at fixed points — **`c_max` is the cause**, and the LB cap is set to **450**, his E/F nominal, with provenance and scope in the strain file |
| **2** — the convergence caveat | **DONE** | At the top of `reports/ecoli_gasflux/README.md`, `reports/P3_gate/gate.md` and `SUMMARY.md`, with the numbers, the cost, and the port-check distinction |
| **3** — two standing hazards | **DONE** | `docs/OPEN_ITEMS.md` §4: a gate only protects the fields it checks; a recommendation is scoped to its conditions |
| **4** — the unexplained 10 °C | **DONE** | Already recorded as OPEN_ITEMS 3.19 with strain and evidence; dated confirmation added; not investigated |

Detail: [DECISIONS.md](DECISIONS.md) (D0–D4), `task1_parsa_lb_cmax.py` → `parsa_lb_cmax.csv`,
`run_lb_fit.py` → `lb_cmax_comparison.csv` and
`strains/eciML1515/outputs/calibration_configD_LB_recipe_cmax257/`.

---

## TASK 0 — the merges

`main` went `450e317` → `b6bc6bb` (Merge P4, PR #12) → `4863d61` (stamp refresh, D0) → `0947569`
(Merge K9, PR #13). Both merges were `--no-ff`; neither conflicted. The two files both branches
touch, `docs/OPEN_ITEMS.md` and `reports/report_status.yaml`, merged automatically and **both
sets of rows are present**: P4's items 1.11 and 1.12 and its `P4_refit` status entry; K9's item
3.19 and its `K9_criterion` entry (and K5–K8's 3.13–3.18 between them). K9's branch was fully
pushed (local = origin at `2582ab9`) before its worktree `../etcGEMs-k9` was removed; both PRs
show MERGED on GitHub; both branches deleted locally (`-d`, which refuses an unmerged branch)
and on origin.

Verification, run **twice** — after the P4 merge and again after the K9 merge — with
`$CANDIDAS_ROOT` unset and every exit code printed:

| check | after P4 (`4863d61`) | after K9 (`0947569`) |
|---|---|---|
| K1 Candida gate (`gate_table.py`) | rc 0, **79/79 PASS** | rc 0, **79/79 PASS** |
| P1 gate, configurations A/B/C (`gate.py`) | rc 0, **60/60 PASS** | rc 0, **60/60 PASS** |
| four Candida strains: `transfer_candida`, `transfer_candida_unpinned` re-run | rc 0, byte-identical under `strains/` | rc 0, byte-identical |
| eciML1515, mmaripaludis, syn6803: `etcgem tpc` re-run | rc 0, byte-identical | rc 0, byte-identical |
| `outputs/transfer_candida*/calibration.json` | **`"fixed": {}` reappears** — K8's regression, K9's fix not yet on `main` | **clean** — K9's fix verified on `main` |
| `stamp_reports.py --check` | rc 0 after D0's refresh | rc 0 |

Two things the batteries found that were not merge failures, both recorded rather than acted on:

* **the stamps** — `p4/refit` was one commit stale against its own stamps, and a third stamp
  went stale on merge; refreshed in one TASK 0 commit on `main` before the first gate ran (D0);
* **two stale FBA config dumps** — the K1 gate's two `etcgem fba` output directories differ from
  their committed `resolved_config.yaml` by one key (`rescale_pool_row: false`) that N2's hotfix
  began recording after they were last written. Numerically identical, stale since the N2
  merge, never re-run by any TASK 0. Left as found under VERIFY 6, and recorded in OPEN_ITEMS
  §4 as the second instance of TASK 3's first hazard (D1).

P4 was **not** running — no process, last commit "P4: summary" — so `strains/eciML1515/` was
free to write, and the only thing written there is the new fit directory.

## TASK 1 — the LB `c_max` fit

### 1a. What his three LB fits actually used, read at source

From `$PARSA_ROOT` (read only): each run's `meta.json` for the parameter list and `cfg`, and
`chain.h5` for the MAP and posterior-median point (`task1_parsa_lb_cmax.py`). On LB his cap is
`C_max_LB_mult × nominal`, the nominal being **230** for configuration D and **450** for E and F
(`CAP_NOM` / `CAP_NOM_E` in his `calibration_configD_full.py`), the multiplier sampled in log
space under a lognormal prior of sd 0.40 centred on 1.

| config | his run | how the cap is set | mult at MAP | **c_max at MAP** | at median | steps | quoted where |
|---|---|---|---|---|---|---|---|
| D | `configD_LB_full` | 230 × fitted mult | 1.116 | **256.7** | 267.0 | 2000 | his 0.90; P3 gate; P4 |
| E | `configE_LB_freecmax` | 450 × fitted mult | 1.021 | **459.3** | 353.9 | 1500 | his 0.83 / 0.81; P3 gate; P4 |
| E | `configE_LB` | **pinned** `cfg.cmax_fixed.LB` | — | 459.0 | 459.0 | 1500 | sibling run, cap fixed from the above |
| F | `configF_LB` | 450 × fitted mult | 1.133 | **509.9** | 391.6 | 1500 | his 0.88 / 0.85; P3 gate; P4 |
| F | `configF_LB_combined` | 450 × fitted mult | 0.910 | 409.5 | 347.5 | 1500 | not gated |
| D | `configD_LB_growthonly` | no cap (`use_cap: false`) | — | — | — | 4000 | not gated |

**P4's 257 / 459 / 510 are confirmed at source** (256.7 / 459.3 / 509.9, MAP). Two
qualifications the P4 report did not carry (D2): the fitted multipliers are **1.02–1.13**, i.e.
the posterior barely left the prior centre, so "his LB fits chose these" means the data did not
pull the cap away from wherever he centred it — and D's 257 differs from E's and F's 459–510
mainly because he centred D on 230 and E/F on 450; and at the posterior median the three are
267 / 354 / 392, so the spread is narrower than the MAP values suggest.

### 1b. The fit

**The chain.** Configuration D on LB, recipe medium (LB is a plain component list, identical
in his build and ours — checked in `gate_def.build_pm_for_fit` against `build_gasflux_pm`), k_cat
300, **c_max = 257** (his D_LB MAP cap, D2), P4's sampler settings (36 → 40 walkers, 2000 steps,
seed 1), into `strains/eciML1515/outputs/calibration_configD_LB_recipe_cmax257/`. It ran to the
end — 2000 × 40 in **156 min**, three times P4's 46 min for the same settings because one
worker's slow solves serialised the ensemble — and is **not converged** (τ_max 172, chain/τ 11.6,
n_eff 384). And it is **useless for the question**: its MAP predicts zero growth at every
temperature (growth R² **−2.19**, r_max 0.0002, acetate and RQ undefined). D3 has the anatomy:
P4's warm-start repair worked as wired this time, its 12-generation differential evolution
returned the **dead mode** (growth ≡ 0, `disc_growth` ≈ 1.4 absorbing the data), all 40 walkers
were seeded there, and 100 % of them were still there after 2000 steps. Recorded as OPEN_ITEMS
**3.20** with a trigger, because P6 is about to run nine chains with this warm start on. The
chain is kept as that record (`lb_cmax_comparison.csv`) and nothing else is quoted from it.

**So the question was answered without a sampler**, which is a better instrument for it anyway:
the same parameter vector, scored the same way (P4's recipe — dense grid, interpolated onto the
observed temperatures), in our model at different caps. Three scripts, all deterministic, all
reading his chains read-only:

*1c — his D_LB MAP and P4's D_LB MAP, each at c_max 120 and 257, plus a Powell re-optimisation
of the log-posterior from each start at each cap* (`fixed_point_r2.csv`):

| point | cap | growth R² | resp R² | r_max | log-posterior |
|---|---|---|---|---|---|
| his D_LB MAP (P3's gate reproduced his 0.90 at this point, cap 256.7) | **257** | **0.895** | 0.795 | 2.44 | −10.7 |
| same point, cap changed and nothing else | **120** | **0.641** | 0.397 | 1.80 | −48.3 |
| P4's D_LB MAP (the collapsed refit) | 120 | 0.196 | 0.923 | 1.70 | −19.6 |
| same point | 257 | 0.320 | 0.809 | 1.95 | −36.9 |
| best found by Powell at 120 (from P4's MAP) | 120 | 0.258 | 0.943 | 1.76 | −15.6 |
| best found by Powell at 257 (from his MAP) | 257 | **0.893** | 0.836 | 2.43 | **−9.1** |
| the P5 chain's MAP (dead mode) | either | −2.19 | −21.2 | 0.000 | −33.2 |

At 120 the posterior *trades growth for respiration*: its best point has growth R² 0.26 and
respiration 0.94, and the growing point that keeps growth at 0.64 costs 30 log units. At 257 the
best point has both (0.89 / 0.84) and is six log units better than anything at 120. P4's 0.196 is
therefore what the cap does, polished by a sampler that found the 120 optimum honestly.

*1d — the cap alone, at fixed parameters, for all three LB configurations*, using P3's gate
machinery so that the only number that changes is his `C_max_LB_mult` (`cap_sweep_fixed_point.csv`;
measured LB peak **2.94 h⁻¹** at 43 °C):

| cap | D growth / resp R² (r_max) | E | F |
|---|---|---|---|
| **120** (P4's canonical) | 0.641 / 0.397 (1.80) | **0.048** / 0.497 (1.18) | **−0.102** / 0.409 (1.07) |
| **257** | 0.895 / 0.795 (2.44) | 0.699 / 0.387 (1.98) | 0.678 / 0.631 (1.91) |
| 350 | 0.898 / 0.813 (2.46) | 0.795 / 0.598 (2.23) | 0.813 / 0.403 (2.24) |
| **450** (his E/F nominal) | 0.901 / 0.627 (2.48) | 0.825 / 0.802 (2.39) | 0.869 / 0.900 (2.49) |
| his fitted (256.7 / 459.3 / 509.9) | 0.895 / 0.794 | 0.826 / 0.802 | 0.880 / 0.853 |

**`c_max` is confirmed as the cause**, and the mechanism is in the r_max column: a 120 mmol C
cap holds LB's peak growth at 1.1–1.8 h⁻¹ against a measured 2.94, whatever the parameters. On
NLDM the measured peak is ≈ 1.6, which is why 120 does not bind there and his sweep — run on
glucose-minimal and NLDM — never saw this. Against the two comparators the prompt names: P4's
collapsed 0.16–0.20 is reproduced at 120 (0.20–0.26 at D's best), and his blanket-medium
0.83–0.90 is reproduced at his own caps (0.895 / 0.826 / 0.880) — on the **same** LB medium, so
"blanket" versus "recipe" is not a distinction on LB and the whole movement is the cap.

*1e — re-optimised at the other cap* (`reoptimise.csv`; Powell, 600 evaluations, from his MAP):

| config | cap 257 (fixed → re-optimised) | cap 450 (fixed → re-optimised) | better log-posterior at |
|---|---|---|---|
| D | 0.895 / 0.795 → **0.894 / 0.826** (−9.3) | 0.901 / 0.627 → **0.898 / 0.779** (**−7.7**) | 450 |
| E | 0.720 / 0.430 → 0.766 / 0.417 (−22.2) | **0.827 / 0.863** (−14.9) → 0.887 / 0.396 (−17.5, see caveat) | 450 |
| F | 0.755 / 0.730 → 0.888 / 0.625 (−19.3) | 0.880 / 0.851 → **0.898 / 0.848** (**−11.4**) | 450 |

*Caveat.* For E and F the likelihood re-applies the ETC area constraint on every evaluation.
`stateful_check.py` evaluates E's likelihood at two points in alternation: five of six repeats
agree exactly, the sixth drifts by 0.016 — solver-level noise, small. It does not explain
Powell returning a *worse* log-posterior than its start for E at 450 (−17.5 from −14.9), which
an optimiser cannot do on a pure function, so that one re-optimised row is not trusted and E's
fixed row (0.827 / 0.863) is the one quoted. D has no ETC constraint and is unaffected.

**The canonical LB value: 450** (D4), recorded as a new key `carbon_cap.by_medium.LB` in
`strains/eciML1515/gas_exchange.yaml` with its provenance — his E/F nominal, within 13 % of all
three of his fitted LB caps — and with the scope of the 120 written beside the 120: a
glucose-minimal/NLDM value that P4 over-applied to LB. Why 450 and not the 257 this prompt
anticipated: D's growth is on its plateau at both (0.895 / 0.898) and its log-posterior is best
at 450; E and F reach their gated values at 450 and do not at 257 (E 0.77, F's respiration 0.63);
and P6 will run all three on LB. Its limits, in the file: above 450 nothing has been tested
(r_max 2.4–2.7 against 2.94 measured) and no LB sensitivity to an unbounded cap exists — that
is the trigger. The key is consumed by the fit runners' explicit `c_max=` argument, not by
`config.apply_gasflux`, so **no committed output changes**: verified by regenerating
`outputs/tpc` and `gasflux_configB` after the edit (both rc 0, tree clean but for the edit and
the new fit directory).

**None of the R² above is a converged posterior.** The fixed-point values are exact evaluations
of single parameter points; the re-optimised ones are local optima; the chains they come from
run at ~9–12 τ. They are a like-for-like diagnostic of the cap, which is what was asked.

## TASK 2 — the convergence caveat, where it will be read

Added at the **top** of `reports/ecoli_gasflux/README.md`, `reports/P3_gate/gate.md` and
`reports/P3_gate/SUMMARY.md`, as one identical block, and a one-line pointer beside the gate's
Table 1. No number removed or restated. Parsa's six chains were **re-measured here** with the
same estimator P4 used (`emcee.autocorr.integrated_time`, τ_max over parameters) and agree with
P4's values to 0.1:

| chains | steps × walkers | τ_max | chain / τ | n_eff |
|---|---|---|---|---|
| his six | 1500–2000 × 36 | 160.4–214.1 | 8.2–9.4 | 148–170 (first half discarded, P4's convention) / 296–340 (none discarded) |
| P4's nine refits | 1500–2000 × 40 | 145.7–244.7 | 8.2–10.3 | 247–332 (the sampler's own: walkers × (steps − 2τ) / τ) |

Against the criterion chain > 40 τ **and** n_eff ≥ 200, none of the fifteen converges. The
distinction the block preserves, verbatim: *P3's gate remains valid as a PORT check — it reads
the same parameter point out of his chain and recomputes his R² to within 0.009, which proves
the port reproduces his computation whether or not the chain converged. What does not follow is
reading those R² as validated model performance.* The cost: 40 τ ≈ 8 000–10 000 steps per fit,
four to five times the chain, ≈ 40 h for all nine on this machine, with P4's warm-start repair
untested at scale.

## TASK 3 — the two hazards

Both added to `docs/OPEN_ITEMS.md` §4, dated, each with its instances and its rule:

1. **A gate only protects the fields it checks.** K8's unconditional `fixed` field (every
   committed `calibration.json` stale, gate 79/79 throughout, caught by K9 re-running the
   transfers); and the second instance TASK 0 found, the two FBA config dumps one key stale since
   N2. Rule: re-run the byte-identity check AFTER the last change, diff the whole tree, and treat
   a `resolved_config.yaml` diff as a finding until explained.
2. **A recommendation is scoped to the conditions it was derived under.** `c_max ≈ 100–120` from
   a glucose/NLDM sweep, adopted by P3, applied to LB by P4, where the fit collapsed while his
   own LB fits had used 257 / 459 / 510. Rule: record the value AND the conditions (the medium),
   and say so where the value is applied outside them.

## TASK 4 — the unexplained 10 °C

Recorded already: OPEN_ITEMS **3.19** (K9) names *Synechocystis* sp. PCC 6803 (`syn6803`), the
committed ceiling 45.70 °C from `outputs/P2_thermal/` against 55.50 °C from a plain build, and
the two exclusions (the committed curve is not truncated — growth 0.2 % of peak at 50 °C — and
the light-saturated medium `run_p2_thermal.py` applies does not move the plain build). A dated
confirmation was appended to the row. **Not investigated here**; it needs its own run.

## Verification

| check | result |
|---|---|
| TASK 0: both merges `--no-ff`; both sets of rows in `OPEN_ITEMS.md` and `report_status.yaml` | done; 1.11, 1.12, 3.13–3.19, `P4_refit`, `K9_criterion` all present |
| TASK 0: gates after each merge | 79/79, 60/60, seven strains byte-identical, stamps clean — twice (table above) |
| TASK 0: K9 worktree removed; PRs #12 and #13 closed (MERGED); branches deleted | done |
| TASK 1: his three LB `c_max` at source | 256.7 / 459.3 / 509.9 (MAP), from his chains |
| TASK 1: the fit's growth R² | chain: −2.19 (trapped, D3); at fixed points: 0.895 at 257 vs 0.641 at 120 for the same point |
| TASK 1: `c_max` confirmed as the cause | **yes** — same parameters, cap alone, three configurations |
| TASK 1: canonical LB value | **450**, `gas_exchange.yaml` `carbon_cap.by_medium.LB`, with provenance and the 120's scope |
| TASK 2: caveat in `reports/ecoli_gasflux/README.md` and `reports/P3_gate/` | at the top of both (and `SUMMARY.md`), port-check distinction stated, numbers beside not instead |
| TASK 3: both hazards in OPEN_ITEMS §4 | added, dated, with instances |
| TASK 4: the 10 °C discrepancy | OPEN_ITEMS 3.19, *Synechocystis*, evidence present; confirmation dated; not investigated |
| `git diff main --stat` | see the PR; the only committed-output addition is `calibration_configD_LB_recipe_cmax257/` |
| byte-identity after the last change | `etcgem tpc --strain eciML1515` and `gasflux_configB` regenerated after the yaml edit: nothing committed changed |
| read-only trees | `$PARSA_ROOT`, `$CANDIDAS_ROOT` untouched |
