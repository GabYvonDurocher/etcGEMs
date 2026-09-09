# P6 — run the fits to convergence

| task | status | one line |
|---|---|---|
| **0** — pre-flight | **DONE** | P5 merged on instruction; settings read back (LB at 450); τ re-measured; warm start tested and **rejected** (dead mode on both D fits); E/F likelihood found non-deterministic and diagnosed |
| **0b** — benchmark | **DONE** | stretch move kept, 16 processes adopted (+11 %); DE+Snooker not adopted |
| **0c** — target | **DONE** | n_eff ≥ 600 AND chain/τ ≥ 25, stated as weaker than 40 τ |
| **0d** — E/F degeneracy | **DONE** | non-unique O2 at optimal growth at specific temperatures, selected by solver basis history; E and F **held**; fix recommended, not made |
| **1** — the fits | **HALTED** | D NLDM stopped at ~1250 steps on instruction: τ ∝ chain length for every parameter; D LB, D M9 not started; E/F not run. **Nothing converged, nothing quoted** |
| **2** — what converging changed | **NOT RUN** | no converged posterior exists |
| **3** — closing the loop | **NOT RUN** | P5's caveat stands; OPEN_ITEMS 1.12 restated, not closed |

Detail: [DECISIONS.md](DECISIONS.md) (D0–D6); `preflight.py` → `preflight_settings.csv`,
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

**Which mechanism the evidence supports — one line:** *the O2 uptake at optimal growth is
genuinely non-unique at particular temperatures in E and F, and the solver's basis history
selects which point of that continuum is returned; D carries the same history and jitters by
0.0000 because its O2 is unique.* Not "unidentifiable" alone, not "leaking state" alone: the
degeneracy is what makes the state matter. The rebuild numbers (`state_vs_identifiability.csv`,
addendum 5), at P4's MAP θ and a second vector θ′:

| fit | one model, θ then θ again | one model, θ, θ′, θ (Δ vs first) | same, with a Gurobi basis reset before the last θ | two fresh models, θ once each (Δ) | fresh model, θ′ then θ (Δ vs fresh θ) |
|---|---|---|---|---|---|
| D NLDM / D LB | 0.0000 / 0.0000 | +0.000 / −0.000 | +0.000 / +0.000 | 0.0000 / 0.0000 | −0.000 / −0.000 |
| E NLDM | **0.515** | +0.515 | +0.515 | 0.0000 | +0.515 |
| E LB | **2.498** | −2.499 | **−0.000** | 0.0000 | −2.498 |
| F NLDM | 0.0000 | +0.000 | +0.012 | 0.0000 | +0.000 |
| F LB | **2.353** | +2.353 | +2.353 | 0.0000 | +2.353 |

Two fresh models agree to four decimals (the rebuild test taken alone would say "state"); one
model gives a different answer on its second call than on its first with nothing in between.
What the second call changes, temperature by temperature (`state_detail.json`): **growth does
not move** (E LB 1.75853 → 1.75853 at every moved temperature; E NLDM 0.07458 → 0.07461), **O2
does** (E NLDM 20 °C 2.92 → 3.25; E LB 37–50 °C 23.1 → 24.1), and the FVA of O2 with growth
held at that optimum, at those temperatures, is a continuum:

| fit, temperature | growth (fixed) | O2 returned, first / second call | O2 range at that growth (FVA) |
|---|---|---|---|
| E NLDM, 20 °C | 0.0746 | 2.92 / 3.25 | **[3.25, 7.84]** |
| E LB, 37 °C | 1.7585 | 23.11 / 24.11 | **[5.8, 114.5]** |
| E LB, 40 / 43 / 45 / 47 / 50 °C | 1.7585 | 23.0 / 24.1 | **[3.3, 172]; [1.5, 185]; [0, 190]; [0, 192]; [0, 191]** |
| F LB, 35 °C | 0.56 | 26.24 / 16.83 (θ′-history) | **[16.5, 26.3]** |
| D NLDM / D LB / D M9, every temperature | — | identical | width ≤ 0.04 |

The earlier five-temperature sweep (`degeneracy.csv`, 25/30/37/40/44 °C) missed 20 and 35 °C,
which is why its widths looked negligible for the NLDM fits; for E LB it had already found
[5.8, 114.5] at 37 °C with the carbon cap **active**, so an active cap does not pin O2 and
`gasflux.py`'s claim that it "pins the flux distribution (O2/CO2 unique)" holds for D — where
the proteome pool, not the ETC budget, binds and respiration is cost-optimal uniquely — and not
once the ETC area constraint is present. A basis reset before every call would make E LB
deterministic (its reset row returns to the fresh value exactly) and **no more identified**: the
fresh value is one arbitrary point of a [0, 190] interval. Ruling out and ruling in are both
results here: alternate optima *are* the substance, state is the selector, and the fix has to
remove the degeneracy.

*Note on D NLDM:* the cap's primal reads **0 of 120** at every temperature there, while on LB
and M9 it reads active. Either the cap's carbon-source expression does not cover the uptake
reactions the recipe medium actually uses, or the recipe ceilings bind first and the cap term
is genuinely empty; P4 said the latter in words. Not investigated; a trigger in OPEN_ITEMS 3.21.

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

**Halted by the user (addendum 6) after five checkpoints of D NLDM**, at step ~1250 of a
7500-step cap: τ_max 28.1, 53.4, 78.5, 103.5, 128.9 at steps 250–1250, chain/τ pinned at 9.7,
n_eff plateaued at ~308. Neither adopted criterion was reachable by running longer. **The
in-flight steps were not preserved**: the driver writes the chain only at the end of a run, so
stopping it discarded ~1250 steps (~40 min); the diagnosis below uses the chains on disk. **D LB
and D M9 were not started**, on instruction, pending a decision. No fit in this run reached
either target, and none is quoted.

### Why τ tracks chain length (`diffusion.py`, D6)

On P4's 2000-step D NLDM chain plus the 500-step stretch-move continuation from its final state:

* **no single parameter carries it** — τ is 187–298 for all sixteen; the top is `disc_growth`
  (298, ×1.16 the next, `sigma` 257); `clearance_mult` (K) is rank 6 at 216. τ_max measured on
  250-step prefixes: 25.9, 55.9, 90.6, 127.8, 158.5, 185.9, 213.3, 244.7, 271.5, 298.4 —
  linear, chain/τ 7.8–9.7 — which is emcee's estimator saturating (window c = 5) because the
  autocorrelation has not decayed inside the chain. **The true τ is unknown and > 300.**
* **the top parameter drifts, then mixes slowly; it does not excurse** — 38 of 40 walkers move
  down in `disc_growth` between first and last quarter (0.43 → 0.23); its ensemble median
  0.470 → … → 0.186 over 2500 steps, flattening in the last 750; σ 0.58 → 0.77 then flat;
  log-posterior median −26.8 → −14.4, flat over the last 1000 steps. ~1500 steps of burn-in,
  then stationary in level — and the P6 chain, started at the end of that drift, still read
  chain/τ 9.7, so the ensemble is stationary and not mixing on any measurable time scale.
* **it is not K** — K's τ is mid-pack and its width ratio is 0.55 (P4: 0.57–0.64): prior-
  determined, unchanged, and not the slow direction.
* **width ratios, every parameter** (last half): prior-determined **topt_scale 0.79, dCp_scale
  0.75, sigma 0.56, clearance_mult 0.55**; data-determined dTopt 0.41, f_metab 0.33, ngam_scale
  0.33, f_maint 0.31, ngam_steepness 0.30, kcat_scale 0.27, tm_scale 0.26, dTm 0.25, kappa_scale
  0.15, disc_resp 0.13, disc_growth 0.12, resp_scale 0.07. Medians of the twelve data-determined
  parameters are stable to a few per cent across the last three 500-step blocks.

**Recommendation (c):** stop; do not start D LB or D M9 under this sampler expecting
convergence (their P4 chains carry the same signature). Report the D family as medians stable
and quotable *with a "not converged" label*, intervals not converged, four parameters
prior-determined. The options that would change it — fixing the four prior-determined
parameters (16 → 12 dimensions), narrowing the discrepancy priors to the decade the data occupy,
a different sampler, or accepting the diagnostic status — are decisions, listed in D6, none
taken here.

## TASK 2 — what converging changed

Not run: no fit reached a convergence target (TASK 1), so there is no converged posterior to compare with P4's. `compare.py` is in place for when one exists.

## TASK 3 — closing the loop

Not run: nothing here replaces P5's "not converged" caveat, which stands. OPEN_ITEMS 1.12 is restated by this run's findings (see 3.21 and D6) rather than closed. P3's gate is a port-fidelity check and is unaffected by anything in this run.

## Verification

| check | result |
|---|---|
| P5 merged; tree clean at start | yes (`50cbffd`; battery 79/79, 60/60, seven strains byte-identical, stamps clean) |
| settings read back from resolved configs; LB c_max | `preflight_settings.csv`: all nine as P4 set them; **LB 450** in all three LB fits |
| warm start | runs; finds the zero-growth mode on both D NLDM and D LB; rejected by the growth check; not used |
| P5 left LB unsettled? | no — 450 settled; fallback not needed |
| per-fit target length and total, before starting | 25 τ: 27.3 h all nine / ≈ 8 h the three D fits at 16 processes; stated in D5 |
| benchmark; cores; adopted configuration; posterior unchanged | `bench.csv`; 12 P + 4 E cores, idle at 10; stretch + 16 proc, +11 %; same move as P4 so unchanged by construction |
| adopted target stated as weaker than 40 τ | yes, TASK 0c |
| likelihood jitter | ≤ 0.0004 D; 0.5–7.5 E/F; mechanism measured (addendum 5) |
| per-fit table | none converged; D NLDM halted at ~1250 steps (chain not preserved); D LB, D M9 not started; E/F held |
| `git diff main --stat` | code: `src/etcgem/calibration_multi.py` only — three sampler-only options, defaults unchanged; no model, prior or likelihood change; no committed output regenerated; `strains/eciML1515/outputs/calibration_configD_NLDM_recipe_P6/` holds a `resolved_config.yaml` only |
| read-only trees | `$PARSA_ROOT`, `$CANDIDAS_ROOT` untouched |
