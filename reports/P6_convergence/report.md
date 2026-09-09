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

@@EF_FINDING@@

## TASK 0 — pre-flight

@@TASK0@@

## TASK 0b — the benchmark

@@TASK0B@@

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
