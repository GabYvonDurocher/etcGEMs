# P6 — run the fits to convergence

@@STATUS_TABLE@@

Detail: [DECISIONS.md](DECISIONS.md) (D0–@@DLAST@@); `preflight.py` → `preflight_settings.csv`,
`preflight_tau.csv`, `preflight_jitter.csv`; `jitter_diagnosis.py` → `jitter_diagnosis.json`;
`warmstart_test.py` → `warmstart_test.json`; `bench.py` → `bench.csv`, `bench_posteriors.csv`,
`sampler_config.json`; `run_fits.py` → `fits_table.csv` and
`strains/eciML1515/outputs/calibration_configD_{NLDM,LB,M9}_recipe_P6/`; `compare.py` →
`compare_posteriors.csv`.

---

## The finding that governs this run: configurations E and F cannot be converged as they stand

**Found in TASK 0's pre-flight, before any chain ran; confirmed by the user's mid-run
instruction to hold E and F.** Re-evaluating the gas-flux log-likelihood at one fixed parameter
vector (P4's MAP), six times alternating with a second vector — which is what every walker
evaluation is — spreads by **0.5–7.5 log-likelihood units for every configuration-E and -F
fit** and by **≤ 0.0004 for every configuration-D fit** (`preflight_jitter.csv`):

| fit | re-applied per call | spread at the MAP | at the other point |
|---|---|---|---|
| D NLDM / D LB / D M9 | clearance / — / — | 0.0001 / 0.0000 / 0.0000 | 0.0004 / 0.0000 / 0.0000 |
| E NLDM / E LB / E M9 | clearance + ETC / ETC / ETC | **0.52 / 6.21 / 0.13** | **2.30** / 0.46 / 0.00 |
| F NLDM / F LB / F M9 | clearance + ETC / ETC / ETC | **4.31 / 2.35 / 1.93** | **7.49** / 0.01 / 0.00 |

P4's D LB chain spans log-posterior −27 (median) to −20 (maximum): the E/F jitter is the width
of the posterior. A longer chain cannot fix that — it would sample an unidentified direction
and report converged intervals on it — so **E and F are held (D3) and only configuration D was
run.**

**Where it comes from** (`jitter_diagnosis.py`, `degeneracy.py`). Growth is stable to 1e-3 h⁻¹
in every repeat; **the O2 uptake is not**, and the difference sits at particular temperatures:
E NLDM at 20 °C (O2 3.19 ± 0.33, a 10 % swing where the log-scale respiration term is most
sensitive), F LB at 35 °C (24.4 ± 9.4, 40 %). With the ETC constraint left untouched repeated
solves agree to 1e-4; the different value appears on the **first solve after the ETC area
constraint is removed and re-added**, which the E/F likelihood does on every call, and in a
chain every call follows a different vector. Flux variability of the net O2 uptake at growth
held to its optimum, at P4's MAP:

| fit | carbon cap | O2 range at fixed optimal growth (mmol gDW⁻¹ h⁻¹) |
|---|---|---|
| D NLDM / D LB / D M9 | slack (see note) / active / active | width ≤ 0.04 at every temperature: **unique** |
| E NLDM, F NLDM | none (P4's setting) | ≤ 0.27 at 25–44 °C; the 20 °C swing above is at a temperature not in this sweep |
| **E LB** | **active** | 25–30 °C ≤ 0.09; **37 °C [5.8, 114.5]; 40 °C [3.3, 172.0]; 44 °C [0.0, 187.7]** at the same growth 1.759 |
| **F LB** | **active** | **30 °C [31.1, 46.6]**; 25 °C 0.5; 37–44 °C ≤ 0.01 |
| E M9, F M9 | active | ≤ 0.02 |

So: the model's O2 uptake at optimal growth is **a face of the LP, not a vertex**, wherever the
carbon cap and the ETC area budget between them leave the carbon that is not needed for growth
free to be respired or not; the solver returns whichever point of that face its current basis
leads to; and re-adding the constraint resets the basis. The carbon cap being active does **not**
pin O2 — E LB has the cap active and the largest degeneracy of all — so `gasflux.py`'s docstring
claim that the cap "pins the flux distribution (O2/CO2 unique)" holds for configuration D (where
the proteome pool, not the ETC budget, is the binding resource and respiration is cost-optimal
uniquely) and not once the ETC area constraint is present. Removing the ETC constraint changes
the optimum (E NLDM 30 °C: 20.3 with, 24.7 without) but does not remove the LB degeneracy.

*Note on D NLDM:* the cap's primal reads **0 of 120** at every temperature there, while on LB
and M9 it reads active. Either the cap's carbon-source expression does not cover the uptake
reactions the recipe medium actually uses, or the recipe ceilings bind first and the cap term
is genuinely empty; P4 said the latter in words. Not investigated here; recorded as a trigger
in OPEN_ITEMS 3.21, because if the cap is a no-op on the recipe NLDM medium then "c_max 120 on
NLDM" has been describing nothing.

**What would make the respiration likelihood identified — a decision, not implemented here:**

1. **A parsimonious tie-break** (pFBA: at the optimal growth, minimise total flux or total
   enzyme usage, then read O2). Standard practice, one extra LP per temperature (E/F evaluations
   go from ~0.3–0.5 s to ~0.6–1 s; a 25 τ chain from ~2 h to ~4 h), and it changes what the E/F
   respiration *means* — the most economical way to reach that growth — so P3's E/F rows and P4's
   E/F fits would have to be re-derived under it; the D fits are unaffected (their O2 is already
   unique, so pFBA returns the same value).
2. **A lexicographic O2 objective** (min or max O2 at fixed growth). Same cost as pFBA; picks an
   extreme of the face, which is a modelling assertion (most fermentative or most respiratory
   cell) rather than a tie-break.
3. **A binding carbon cap** — already active on E/F LB and M9, and not sufficient: it fixes how
   much carbon enters, not how much of the surplus is oxidised.
4. **An interval likelihood** — score the observed O2 against the FVA range rather than a point.
   Honest about the model's silence, costlier (two LPs per temperature) and it would say, for
   E LB at 37–44 °C, that the model makes no respiration prediction at all.

The first is the one to take if the E/F respiration R² are to mean anything; whichever is
chosen, P4's six E/F chains and Parsa's four sampled a likelihood with a solver-history term,
and their respiration rows should be read as such until re-run.

## TASK 0 — pre-flight

**P5 merged** (D0): `50cbffd`, `--no-ff`, full battery green, PR #14 MERGED, branch deleted.
**Tree clean** at the start of TASK 0 apart from untracked prompt files.

**Settings read back from each fit's resolved config** (`preflight_settings.csv`), not assumed:

| fit | medium | cap | c_max | ETC table | protons | clearance sampled |
|---|---|---|---|---|---|---|
| D NLDM | NLDM | on | 120 | — | no | yes |
| **D LB** | LB | on | **450** | — | no | no |
| E NLDM | NLDM | off | — | szenk_merged_bd | no | yes |
| **E LB** | LB | on | **450** | szenk_merged_bd | no | no |
| F NLDM | NLDM | off | — | configF_as_fitted | yes | yes |
| **F LB** | LB | on | **450** | configF_as_fitted | yes | no |
| D / E / F M9 | glucose_minimal | on | 120 | — / szenk / configF | no / no / yes | no |

All three LB fits carry P5's 450, read from `gas_exchange.carbon_cap.by_medium.LB` by
`p6_fits.py`, which refuses to run LB if that key is absent rather than falling back to 120.
Everything else is P4's setting. **P5 did settle the value**, so the prompt's fallback branch
(257, provisional) was not needed.

**Warm start — tested on two short runs, and it does not work as a warm start** (`warmstart_test.json`).
P4's wiring repair holds: the optimiser now runs (DE, 12 generations, 63–69 s). But on **both**
D NLDM and D LB its mode is the **zero-growth mode** — predicted peak growth 0.0000 h⁻¹ against
measured 2.08 and 2.95 — exactly what killed P5's chain (OPEN_ITEMS 3.20). The growth check
added in D1 **rejected it both times** and fell back to the emergent-point ball, and that is
what the driver now does by default. TASK 1 did not use the warm start at all: every chain
starts from P4's final ensemble state (D2), which is a better start than either.

**τ re-measured on P4's nine chains** (`preflight_tau.csv`), same estimator, agreement with P4
to 0.1 in every case, and the length each fit needs:

| fit | τ_P4 | chain/τ (P4) | steps for 25 τ | for 40 τ | s/step (P4) | h at 25 τ / 40 τ, fresh |
|---|---|---|---|---|---|---|
| D NLDM | 244.7 | 8.2 | 6117 | 9787 | 2.06 | 3.5 / 5.6 |
| D LB | 224.3 | 8.9 | 5609 | 8974 | 1.39 | 2.2 / 3.5 |
| E NLDM | 172.7 | 8.7 | 4317 | 6907 | 1.94 | 2.3 / 3.7 |
| E LB | 158.6 | 9.5 | 3964 | 6343 | 1.90 | 2.1 / 3.3 |
| F NLDM | 172.9 | 8.7 | 4322 | 6915 | 1.94 | 2.3 / 3.7 |
| F LB | 157.5 | 9.5 | 3937 | 6299 | 1.94 | 2.1 / 3.4 |
| D M9 | 201.8 | 9.9 | 5044 | 8071 | 2.39 | 3.4 / 5.4 |
| E M9 | 173.3 | 8.7 | 4333 | 6933 | 5.42 | 6.5 / 10.4 |
| F M9 | 145.7 | 10.3 | 3642 | 5826 | 2.89 | 2.9 / 4.7 |
| **all nine** | | | | | | **27.3 / 43.8** |

Stated before starting: all nine at 25 τ would have been ≈ 27 h at P4's rates (≈ 24 h at the
16-process rate); the three D fits ≈ 8 h at 25 τ, ≈ 10 h at their caps (D5).

## TASK 0b — the benchmark

On configuration D NLDM, every run from P4's final ensemble state (`bench.csv`). Machine:
**12 performance + 4 efficiency cores, 16 physical**; P4's 40 walkers give emcee halves of 20,
so 10 processes was already two full rounds and the prompt's 36-walker arithmetic does not
apply here.

| run | steps | s/step | min per 500 | τ_max (chain/τ) | acceptance |
|---|---|---|---|---|---|
| (a) stretch, 10 processes — P4's | 500 | 2.08 | 17.3 | 51.2 (9.8) | 0.166 |
| (b) DEMove 0.8 + DESnookerMove 0.2, 10 | 500 | 2.31 | 19.3 | 49.9 (10.0) | **0.051** |
| (c) stretch, 12 | 150 | 2.16 | 18.0 | — | 0.178 |
| (c) stretch, **16** | 150 | **1.86** | **15.5** | — | 0.176 |
| (c) stretch, 20 | 150 | 1.86 | 15.5 | — | 0.187 |
| (d) DE, 16 | 150 | 1.93 | 16.1 | — | 0.064 |

**Cores were idle at 10**: 16 processes is 11 % faster per step and 20 adds nothing.
**The DE move set is not adopted**: on 500 steps its τ equals the stretch move's (both estimates
are at ten autocorrelation times and unreliable in absolute terms — the 51 here against 245 on
P4's full chain is the short-chain bias, not a real drop — but they are the same number), and
its acceptance is a third of the stretch move's. On this posterior it is not the 2–5× lever the
prompt hoped for. The 500-step posterior comparison (`bench_posteriors.csv`) has medians broadly
consistent between the two move sets (clearance_mult 0.818 / 0.819, dTopt 2.0 / 2.2, sigma
0.68 / 0.70) and several 90 % widths differing up to 2× (dTm 4.1 / 7.6, sigma 0.27 / 0.41),
which at ten τ is noise rather than evidence either way; since DE is not faster, that question
does not need settling.

**Adopted: stretch move, 16 processes** (`sampler_config.json`, D4). The move set is P4's and
Parsa's, so the target distribution is unchanged by construction, and a process count cannot
change it (same seed, same proposals; only the wall clock moves). **Measured speedup 11 %.**

**Likelihood jitter** (the user's addendum 3): reported in the section above — ≤ 0.0004 for D,
0.5–7.5 for E and F. For configuration D, which is all that ran, emcee's assumption of a
deterministic target holds to four decimals.

## TASK 0c — the convergence target

The adopted target is **n_eff ≥ 600 AND chain/τ ≥ 25**, both reported per fit, with chain/τ
against 40 reported beside them. **This is a weaker criterion than chain/τ ≥ 40 and is not
presented as equivalent to it.** The 40 τ rule is emcee's guidance for estimating τ *itself*
reliably; what the deliverable quotes are posterior medians and 90 % credible intervals, whose
Monte-Carlo error is set by the effective sample size, and n_eff ≥ 600 (which at 40 walkers
chain/τ ≥ 25 gives with margin — 40 × 25 = 1000 by the simple count, ~900 after a 2 τ burn)
is ample for those. What it does *not* buy is a τ estimate accurate to better than ~10–20 %,
so every chain/τ quoted here carries that uncertainty, and a fit that meets 25 τ but not 40 τ
is reported as exactly that. The driver's own n_eff is the stricter post-burn count,
walkers × (steps − 2 τ) / τ; the simple walkers × steps / τ is reported beside it.

## TASK 1 — the fits

@@TASK1@@

## TASK 2 — what converging changed

@@TASK2@@

## TASK 3 — closing the loop

@@TASK3@@

## Verification

@@VERIFY@@
