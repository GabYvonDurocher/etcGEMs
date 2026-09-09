# Y1 PART A — can the published yeast etcGEM be loaded, solved, and run?

**Yes to all three.** The model loads in cobrapy, solves, and their thermal layer runs. The audit
did not need a MATLAB environment and did not turn into a project.

Provenance in `PROVENANCE.md`; the judgement calls in `DECISIONS.md`; the numbers in
`task_a_load.json`, written by `task_a_load.py`.

## 1. The format

Their thermal layer is **Python, not MATLAB** — `code/etcpy/etc.py`, operating directly on a cobra
model. That is the single fact that makes Y1 cheap. The expectation in the prompt (Chalmers works
in MATLAB/RAVEN, so the thermal layer may only be readable) does not hold for this deposit.

Two obstacles, both resolved, both recorded in `DECISIONS.md`:

* The deposited **pickles do not load** under cobra 0.31 (§1). Their `.mat` twins are used.
* The **`.mat` files need a field trim** because several GECKO annotation arrays are sized to a
  subset of the model (§2). The trim keeps only what defines the linear program, and is verified
  against the raw MATLAB struct rather than assumed inert.

## 2. The models load, and the load is faithful

All three deposited `.mat` models: **6743 reactions, 3389 metabolites, 909 genes, 764 enzymes**,
14 compartments including `m` (mitochondrion) and `mm` (mitochondrial membrane), objective
`r_2111` (growth).

Fidelity of the load, against the raw MATLAB struct, for every one of the three:

| check | result |
|---|---|
| reaction ids identical | yes |
| metabolite ids identical | yes |
| `lb` max abs difference | **0.0** |
| `ub` max abs difference | **0.0** |
| objective `c` max abs difference | **0.0** |
| `S` non-zeros, struct vs model | 24805 = 24805 (24804 = 24804 anaerobic) |
| objective reaction | `r_2111` both sides |

## 3. The models solve

| deposit | protein pool | glucose | O₂ | status | growth |
|---|---|---|---|---|---|
| `ecYeast7_v1.0_batch.mat` | 0.0786 | ≤ 1 | open | optimal | **0.097023** |
| `ecYeast7_v1.0_batch_minimal_thermo.mat` | 0.17866 | unlimited | open | optimal | **0.865388** |
| `..._minimal_thermo_anaerobic.mat` | 0.17866 | unlimited | **shut** | optimal | **0.765785** |

The last two are the untreated linear programs: their code applies σ and the temperature layer
before simulating, which is what brings growth to a physiological value (§4).

**Which deposit is `aerobic.pkl`.** Inferred, not proved (`DECISIONS.md` §1): the anaerobic `.mat`
is the aerobic `.mat` with `r_1992_REV` (O₂ uptake) upper bound 0 instead of ∞, same protein pool,
same everything else — which is exactly the aerobic/anaerobic distinction `GEMS.py` draws between
the two pickles. `etc.set_sigma` hard-codes `0.17866*sigma`, matching those two files and not
`ecYeast7_v1.0_batch.mat`.

## 4. Their thermal layer runs

`etc.map_fNT`, `etc.map_kcatT`, `etc.set_NGAMT`, `etc.set_sigma` and `etc.simulate_growth` all run
on the `.mat`-loaded model against the deposited `data/model_enzyme_params.csv` (764 enzymes, no
missing parameters). One compatibility shim was needed, on the order in which `set_NGAMT` sets a
pinned bound; it changes no value (`DECISIONS.md` §7).

Growth at σ = 0.5 under the **prior** (uncalibrated) parameters, i.e. their Fig. S2 setting:

| T (°C) | 25 | 27.5 | 30 | 32.5 | 35 | 37.5 | 40 | 42.5 | 45 |
|---|---|---|---|---|---|---|---|---|---|
| µ (h⁻¹) | 0.283 | 0.338 | 0.378 | **0.384** | 0.375 | 0.353 | 0.312 | 0.242 | 0.061 |

A thermal performance curve with T_opt ≈ 32.5 °C and collapse by 45 °C.

`etc.simulate_chomostat` also runs, and the in-place version used for the audit reproduces its
objective to |diff| = 0.000e+00 (`task_b2_verifications.py`).

## 5. Consequence for the rest of Y1

PART B (the coupling-ion audit) and PART C (the T_opt/CT_max regime test) can both be done on
**their model with their code**. Neither needs a re-implementation of their thermal layer, and
PART C's capacity lever is their own σ (`etc.set_sigma` sets `prot_pool_exchange` upper bound to
`0.17866·σ`).
