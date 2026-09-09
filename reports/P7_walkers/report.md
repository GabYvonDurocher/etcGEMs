# P7 — is the non-mixing a walker-count artefact?

| task | status | one line |
|---|---|---|
| **0** — clean main; BRENDA filed; venv out of the checkout | **DONE** | `p7/walkers` from `2af5815`; `reports/K4_membrane/sources/`; `../etcGEMs-venv` from the lock file, both gates green on it before use; old `.venv` left |
| **1** — checkpointing | **DONE** | HDF5 backend + resume + seeded sampler RNG; bit-identical with/without checkpoint (one process); resume exact; the pool's 1e-4 non-reproducibility recorded as pre-existing |
| **2** — the rule | **DONE** | written and committed before the run; quoted verbatim below |
| **3** — D NLDM at 128 walkers | **DONE** | 1500 steps, 126 min, 5.0 s/step; τ 26 → 141, increments 26 → 20 per block, chain/τ ~10; spread stable |
| **4** — verdict | **NOT MIXING** | walker count is not the cause; D6's modelling options are the real menu; applies to the six committed chains and to the synthesis's section 7 |

Detail: [DECISIONS.md](DECISIONS.md) (D0–D6); `task1_checkpoint_test{,2}.py` →
`.json`; `run_walkers.py` → `strains/eciML1515/outputs/calibration_configD_NLDM_recipe_P7_w128/`
(`chain.h5`, `init_128.json`, `summary.json`); `task3_table.py` → `task3_checkpoints.csv`,
`task3_spread.csv`, `task3_verdict.json`.

---

## TASK 0 — a clean main, and two pieces of housekeeping

Primary tree on `p7/walkers` from `main` at `2af5815` (= `origin/main`, = `../etcGEMs-work`),
nothing running, nothing under `reports/` written in ten minutes. The tree was clean apart from
`brenda_sdh.html` and one more file — the P7 prompt itself, which the user had revised since R2
committed it; not a STOP (D0), committed on this branch so `main` will match what ran.

**BRENDA.** No report kept source material before, so K4's is the first `sources/` directory:
`reports/K4_membrane/sources/brenda_EC1.3.5.1_sce.html` (moved, not deleted; 387 KB; EC 1.3.5.1,
*S. cerevisiae*). The one-line pointer is in K4's sourcing table — the four complex II rows of
`task2_sourcing.csv` — and, because that table is generated, in the generating script's complex
II note and in the report's sourcing sentence; the script was not re-run because it also writes
the strain files (D1).

**The venv.** `../etcGEMs-venv`, a sibling of both trees inside no checkout, built from
`/usr/bin/python3` (3.9.6 — the same interpreter the old `.venv` wraps) and the committed
`requirements.lock.txt` (137 third-party pins; the git-pinned editable `etcgem` line replaced by
a comment and `etcgem` installed editable from the checkout, D2). **Both gates on the new
interpreter before it ran anything else: K1 79/79, P1 60/60**, seven strains byte-identical, the
stamp script runs (PyYAML present). README gained an *Environment* section (where it lives,
shared by both worktrees, how to recreate it, that the stamp script needs it, that a worktree
must set `PYTHONPATH`). **The old `.venv` was left in place**; deleting it is the user's call.

## TASK 1 — checkpointing, proven a no-op and resumable

The driver now keeps the chain in emcee's HDF5 backend (`chain.h5`, every step, with the
sampler's random state) and resumes from it; it also seeds the sampler's own RNG from `seed`,
which emcee 3 otherwise leaves unseeded (D5). Proof, D NLDM from P4's final state:

| test | result |
|---|---|
| one process, 20 steps, with vs without checkpoint | **bit-identical** |
| one process, halt at 10 and resume to 20, vs uninterrupted 20 | steps 0–9 and **the resume step identical for all 40 walkers**; divergence from step 11 (one walker), 3.5 % of walker-steps by 20 |
| 16 processes, 100 steps, with vs without checkpoint | diverge from step 19; 61 % of walker-steps by 100 |
| 16 processes, two runs **without** checkpoint, same seed | diverge from step 11; **63 %** |

The checkpoint changes nothing and resume is exact. What is not reproducible is the likelihood
under a process pool: it reproduces only to ~1e-4, workers are assigned in an order that is not
fixed, a restarted worker has a fresh solver history, and a 1e-4 change occasionally flips an
accept/reject. Two un-checkpointed runs diverge as much as a checkpointed one. **No chain in
this family is bit-reproducible run-to-run under a pool, and that predates P7** — recorded, not
fixed; it does not bias the sample.

## TASK 2 — the decision rule, written before the run (D3, verbatim)

> The quantity that decides is **τ_max as a function of chain length N**, measured at every
> 250-step checkpoint with the same estimator P6 used. n_eff is reported and does **not** decide.
> **Null — NOT MIXING:** the per-block increment in τ_max stays near what P6 measured, ~25 per
> 250 steps (τ_max ≈ 0.10 N; P6: 28.1, 53.4, 78.5, 103.5, 128.9, 155.9), chain/τ pinned near 10.
> **MIXING:** the increment falls and τ_max approaches a plateau — the **mean increment over the
> last three blocks (750→1500) below 10 per block AND τ_max at N = 1500 below 100**; both must
> hold. **PARTIAL:** the increments fall (mean over the last three below 20, each below the
> first block's) but one MIXING condition fails; then extend **once**, by resume, to 2500, report
> both readings, and apply the same two conditions to 1750→2500 and τ_max(2500) < 100. Anything
> else is NOT MIXING.

Initialisation (D4): each of the 128 walkers is a P4 final walker drawn with replacement plus
N(0, 0.05 × prior scale) jitter in sampled space, clipped inside the bounds, seed 7.

## TASK 3 — D NLDM at 128 walkers

Configuration D NLDM, exactly P6's D5 definition — same model, priors, data, c_max 120,
stretch move, 16 processes, seed 1 — with **128 walkers** instead of 40, initialised by D4's
rule from P4's final ensemble state (draw counts in `init_128.json`). 1500 steps, checkpointed
every step, τ at every 250 with P6's estimator. **125.6 min, 5.02 s/step** (2.7× the 40-walker
1.86 s/step for 3.2× the walkers). The τ estimator's carrier is named per row; the 40-walker
rows are P6's logged checkpoints of the same fit from the same start.

| N | τ_max, 128 w | carrier | increment | chain/τ | n_eff (W·N/τ) | accept | wall (min) | τ_max, 40 w (P6) | increment | chain/τ | n_eff | wall (min) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 250 | 26.1 | topt_scale | +26.1 | 9.6 | 1225 | 0.173 | 21 | 28.1 | +28.1 | 8.9 | 356 | 8 |
| 500 | 52.2 | topt_scale | +26.0 | 9.6 | 1227 | | 42 | 53.4 | +25.3 | 9.4 | 375 | 16 |
| 750 | 76.5 | dCp_scale | +24.4 | 9.8 | 1254 | | 63 | 78.5 | +25.1 | 9.6 | 382 | 23 |
| 1000 | 99.6 | dTm | +23.1 | 10.0 | 1285 | | 84 | 103.5 | +25.0 | 9.7 | 386 | 31 |
| 1250 | 120.7 | dTm | +21.1 | 10.4 | 1326 | | 105 | 128.9 | +25.4 | 9.7 | 388 | 39 |
| **1500** | **140.8** | sigma | **+20.1** | 10.7 | 1364 | 0.173 | 126 | 155.9 | +27.0 | 9.6 | 385 | 47 |

τ still tracks N: the increment eases from 26 to 20 per block over 1500 steps — a real 10 %
reduction against the 40-walker curve at 1500 — and does not approach a plateau; chain/τ stays
pinned near 10; the carrier rotates between four parameters, as it did at 40 walkers (P6 D6). The
n_eff column crossed the P6 target at the first checkpoint and decided nothing.

**Ensemble spread** (`task3_spread.csv`, natural units, sd over walkers): end/start between
0.85 and 1.36 for all sixteen parameters, and the end spread is within 20 % of the 40-walker
final spread for every one — no collapse toward the 40-walker ensemble, no blow-out. Medians
moved by less than the spread in every parameter.

## TASK 4 — what the answer licenses

**(b) NOT MIXING**, by D3's rule as written before the run: the mean increment over steps
750→1500 is **21.4** against the rule's 10 for MIXING and 20 for PARTIAL, and τ_max(1500) is
140.8 against 100. τ still tracks N. The PARTIAL extension to 2500 was not run because its own
entry condition failed.

**What that licenses.** The cheap option is ruled out: P6 D6's option (iii) at 3.2× the walkers
and 2.7× the per-step cost produces a 10 % lower τ and the same proportionality. D6's remaining
options are the real menu — (i) fix the four prior-determined parameters (σ, K, topt_scale,
dCp_scale; 16 → 12 dimensions), (ii) narrow the discrepancy priors to the decade the data
occupy, (iii′) a different sampler, (iv) accept the diagnostic status and quote medians only.
Each changes what the fit is or what is claimed of it; each is the user's decision, and none
was taken here. A further doubling to 256 walkers would cost ~10 s/step and ~4.2 h for 1500
steps; on this curve (the increment falls ~1 per block per 88 extra walkers) it would be
expected to read ~18 per block — another reading of the same null, not recommended.

**Does it apply to the six committed chains, and to the synthesis?** Yes. Parsa's chains are
the same sampler at 36 walkers on the same likelihood family, with the same τ ≈ N/9 signature
(P4), and P7 shows walker count is not what sets it. The synthesis's section 7 sentence,
*"reaching the criterion is ~8000 steps"*, is not true of this sampler at any walker count
tried, and its evidence rows [C6] and [C8], which wait on "P6's converged configuration-D
posteriors", wait on one of the decisions above rather than on compute. OPEN_ITEMS 1.12 says so.

## Verification

| check | result |
|---|---|
| TASK 0: branch, start commit, nothing running | `p7/walkers` from `main` at `2af5815`; no process, no recent writes |
| TASK 0: BRENDA page | `reports/K4_membrane/sources/brenda_EC1.3.5.1_sce.html`; pointer in `task2_sourcing.csv` (4 rows), the generating script, and the report |
| TASK 0: venv | `../etcGEMs-venv`; K1 **79/79**, P1 **60/60**, seven strains byte-identical on it BEFORE any run; `requirements.lock.txt` committed; README *Environment*; old `.venv` left in place |
| TASK 1: no-op and resumable | bit-identical (one process); resume step exact; see D5 for the pool caveat |
| TASK 2: rule before run | D3, committed at `bd4d1f6`-era before TASK 3 started; quoted verbatim above |
| TASK 3: table, spread, wall | above; 5.02 s/step, 125.6 min |
| TASK 4: verdict, rule, licence; OPEN_ITEMS | NOT MIXING by D3; D6; OPEN_ITEMS 1.12 updated, 2.7 closed |
| `git diff main --stat` | driver checkpointing (`src/etcgem/calibration_multi.py`), `reports/P7_walkers/`, `docs/OPEN_ITEMS.md`, one fit directory (`calibration_configD_NLDM_recipe_P7_w128/`), the BRENDA file + its citation (K4 script, CSV, report), `requirements.lock.txt`, README, `report_status.yaml`, the P7 prompt as run, stamps. No strain, prior or fit definition changed |
| read-only trees | `$PARSA_ROOT`, `$CANDIDAS_ROOT` untouched |
