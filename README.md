# etcgem

Enzyme- and temperature-constrained genome-scale metabolic modelling for
**thermal performance curve (TPC) sensitivity analysis**. Given a genome's
enzyme-constrained model, sweep proteome allocation and per-enzyme kcat
temperature responses to see the *range of TPCs that genome can generate*.

The organismal TPC (growth rate vs temperature) is not assumed — it *emerges*
from FBA: each enzyme's kcat is rescaled by a temperature response, the total
enzyme demand is bounded by a proteome budget, and biomass is maximised at every
temperature.

---

## The model

**kcat(T) — Macromolecular Rate Theory (MMRT).** Each enzyme's turnover follows

```
ln k(T) = ln(kB·T/h) + (−dH0 − dCp·(T−T0))/(R·T) + (dS0 + dCp·(ln T − ln T0))/R
```

A negative heat-capacity of activation `dCp` gives the single-peaked rise-and-
fall shape of an enzyme TPC. Instead of exposing the abstract `dH0/dS0`, the
curve is described by two interpretable knobs and anchored on the model's
existing kcat:

- `Topt` — temperature of peak kcat
- `dCp`  — curvature / thermal breadth

Given `(kcat_ref, T0, Topt, dCp)` the code solves `dH0, dS0` in closed form so
that **kcat(T0) = kcat_ref exactly** and the curve **peaks exactly at Topt**.
Consequence: the plain enzyme-constrained model is reproduced when the knobs sit
at their nominal values, and every sweep is a controlled deformation around it.
(See `mmrt.py`; the relative response `kcat(T)/kcat_ref` is invariant to the
absolute kcat_ref, which is what makes the GECKO extractor robust.)

**Proteome constraint — sMOMENT pool.** A single total-protein budget

```
Σ_i  MW_i / (kcat_i(T)·3600) · |v_i|   ≤   P            [g protein / gDW]
```

is built explicitly on the cobra model and updated in place as temperature and
budget change (`enzyme_cost.py`). Optional per-group sub-budgets let you probe
allocation *between* pathways, not just the total pool. Raising T past an
enzyme's Topt lowers its kcat, inflates its cost, tightens the budget, and
eventually starves growth — the mechanistic origin of the whole-cell TPC.

**Sensitivity knobs** (`Perturbation`), any subset swept via Latin hypercube:

| parameter      | meaning                                             |
|----------------|-----------------------------------------------------|
| `dTopt`        | shift (K) applied to *every* enzyme optimum         |
| `topt_scale`   | scales spread of enzyme optima about T0 (heterogeneity) |
| `dCp_scale`    | scales curvature / thermal breadth                  |
| `budget_scale` | multiplies total proteome pool P                    |
| `alloc_<grp>`  | multiplies one group's sub-budget (allocation)      |

---

## Install

```bash
pip install -e .        # editable; installs the `etcgem` CLI + deps
# (or: pip install -r requirements.txt  -- cobra, numpy, scipy, pandas, matplotlib, pyyaml)
```

The package uses a `src/` layout (`src/etcgem`) and exposes one console command,
`etcgem`, plus `python -m etcgem`. Run commands from the project root.

## Quickstart (offline, no model download)

```bash
etcgem tpc   --strain _toy                       # nominal curve, no experiment needed
etcgem sweep --strain _toy --experiment quick    # a small sensitivity sweep
```

`_toy` runs on `e_coli_core` (ships with cobrapy) with synthetic enzyme kinetics,
so it works with no network access. The sweep writes to
`strains/_toy/outputs/sweep_quick/`:

| file                          | contents                                        |
|-------------------------------|-------------------------------------------------|
| `nominal_tpc.csv`             | the unperturbed TPC (growth vs °C)              |
| `curves.npy` / `temps_C.npy`  | every sampled TPC (n_samples × n_temps)         |
| `samples.csv`                 | the sampled input parameters                     |
| `descriptors.csv`             | Topt, rmax, CTmin, CTmax, niche width, B80, Ea, skew per sample |
| `sensitivity_spearman.csv`    | Spearman ρ, each input × each descriptor        |
| `summary.json`                | nominal descriptors + ensemble medians/IQR      |
| `*.png`                       | ensemble fan, descriptor histograms, sensitivity heatmap |

TPC descriptors (`tpc.py`): `Topt`, `rmax`, critical limits `CTmin/CTmax` (at a
fraction `crit_frac` of rmax), niche width, `B80` (width at 80% of rmax),
Boltzmann–Arrhenius activation energy `Ea` of the rising limb (eV and kJ/mol),
and curve skewness.

---

## Config model: defaults / strain / experiment

Configuration is split into three tiers, merged as **defaults ← strain ←
experiment** (organism keys come from the strain; method keys from defaults,
overridden by the experiment):

| file | holds |
|------|-------|
| `defaults.yaml` (root) | universal **method** defaults: `solver_timeout`, `crit_frac`, a fallback `temperature_grid` |
| `strains/NAME/strain.yaml` | **organism only**: `provider` block, `T0_C`, `temperature_grid` — enough to build and run the model |
| `experiments/EXP.yaml` | optional **method overlay**: `kind` + a `sensitivity` (sweep) or `decomposition` block |

`config.resolve(strain, experiment)` returns the merged dict with
`provider.model_path` injected from the strain folder; every run also writes the
exact merged config as `resolved_config.yaml` in its output folder.

```
strains/eciML1515/
  strain.yaml            # organism biophysics only
  model/eciML1515_batch.xml
  dltkcat/               # input.csv, output.csv, fits.csv (DLTKcat workflow)
  outputs/{build,tpc,fba,sweep_EXP,decompose_EXP}/
strains/_toy/            # offline synthetic strain (no model file)
strains/_template/       # copy this to start a new strain
experiments/             # default.yaml, quick.yaml, decomposition.yaml
```

Shipped experiments: `default` (120-sample sweep), `quick` (tiny smoke sweep),
`decomposition` (variance decomposition — see the `decompose` command).

## Commands: two tiers

**Strain-only** (a strain runs with no experiment):

```bash
etcgem build --strain eciML1515                 # build provider; print+save model summary
etcgem tpc   --strain eciML1515 [--fits]        # nominal TPC + descriptors + plot
etcgem fba   --strain eciML1515 --temp 37       # single enzyme-constrained solve at 37 °C
```

**Strain + experiment:**

```bash
etcgem sweep     --strain eciML1515 --experiment default          # -> outputs/sweep_default
etcgem sweep     --strain eciML1515 --experiment default --fits   # + DLTKcat fits
etcgem sweep     --strain eciML1515 --experiment quick --resume --seconds 60   # checkpointed
etcgem decompose --strain eciML1515 --experiment decomposition    # -> outputs/decompose_decomposition
```

`--fits` (optionally with a path; default `strains/NAME/dltkcat/fits.csv`) applies
DLTKcat-derived Topt/dCp before the run. `sweep` also accepts `--config PATH` as
an escape hatch for an ad-hoc self-contained config.

To add a strain: `cp -r strains/_template strains/NAME`, drop the model in
`strains/NAME/model/`, set `provider.model_file` in `strain.yaml`, then
`etcgem build --strain NAME` and `etcgem sweep --strain NAME --experiment default`.

## Using another model (ecYeastGEM etc.)

Get an enzyme-constrained model (for yeast, the GECKO ecYeastGEM lives at
`github.com/SysBioChalmers/ecModels`, or build one with GECKO 3; any GECKO-style
SBML/`.mat`/`.json` works) and make it a strain as above — put the file under
`strains/NAME/model/` and set `provider.model_file`.

The `gecko` provider (`providers.from_gecko`) auto-detects both encodings:
"full" GECKO (`prot_pool → prot_<id>` draw reactions carrying MW, metabolic
reactions consuming `prot_<id>` with coefficient `1/kcat`) and "short"/sMOMENT
(reactions consuming `prot_pool` directly). Check the `prot_prefix` / `pool_id`
match your model's metabolite names. GECKO stores no temperature parameters, so
`Topt`/`dCp` start from defaults you set in the config — override per enzyme as
below.

### Temperature-specific kcats — DLTKcat workflow (`dltkcat.py`)

**DLKcat vs DLTKcat.** DLKcat predicts a single, temperature-agnostic kcat from
sequence + substrate — use it only to fill missing *reference* kcats when
building an ec-model. DLTKcat predicts kcat *as a function of temperature*; that
is the input for the thermal response here. The `dltkcat` module fits an MMRT
curve to DLTKcat's kcat-vs-T points and recovers per-enzyme `Topt`/`dCp`.

The MMRT fit is a linear least-squares solve (no initial guess); round-trip
tests recover Topt to ~0.1 °C under 5% noise.

DLTKcat ([SizheQiu/DLTKcat](https://github.com/SizheQiu/DLTKcat)) takes an enzyme
UniProt id + a substrate *name* + temperature; its `convert_input` resolves the
SMILES and sequence for you, so the prep only has to emit `(enz, sub, temp)`.

**1. Prep — write DLTKcat's input from the model.**

```bash
etcgem dltkcat prep --strain eciML1515 --tmin 5 --tmax 55 --n 11
# writes strains/eciML1515/dltkcat/input.csv
# (or, standalone:  etcgem dltkcat prep --model MODEL.xml --out input.csv ...)
```

Columns: `rxn_id, enz` (UniProt), `sub` (substrate name), `bigg, mnx, Temp_C,
Temp_K`. The primary substrate is chosen per reaction (currency metabolites like
ATP/NAD(P)H/H2O excluded; GECKO `pmet_*` arm pseudo-metabolites traced back to
the real substrate). On eciML1515 this resolves ~2340 reactions; the rest
(purely inorganic/transport) are reported and skipped. Keep the `rxn_id` column
through the DLTKcat run so predictions map back.

**2. Run DLTKcat** (in its repo, on your machine): `convert_input(path,
enz_col='enz', sub_col='sub')` to add `smiles`/`seq`, normalise the temperatures
to `Temp_K_norm`/`Inv_Temp_norm`, then `predict.py` → a table of log10(kcat).

**3. Parse → fit MMRT, and apply.**

Put DLTKcat's output at `strains/eciML1515/dltkcat/output.csv`, then:

```bash
etcgem dltkcat parse --strain eciML1515 --temp-col Temp_C --kcat-col pred_log10kcat
# reads dltkcat/output.csv, writes dltkcat/fits.csv (log10 by default)
etcgem sweep --strain eciML1515 --fits      # apply fits -> outputs/dltkcat
```

Equivalently from Python:

```python
from etcgem import providers, dltkcat
pm = providers.from_gecko("strains/eciML1515/model/eciML1515_batch.xml", T0=303.15, pool_scale=0.9)
fits = dltkcat.parse_dltkcat_output("strains/eciML1515/dltkcat/output.csv", key="rxn_id")
dltkcat.apply_fits_to_provider(pm, fits, key="rxn_id")   # keeps calibrated costs, sets Topt/dCp
# pm now carries DLTKcat-derived thermal params; run compute_tpc / run_sensitivity
```

`--key enzyme_id` broadcasts one protein's fit to every reaction it catalyses;
`--key rxn_id` (default) is per-reaction. Reactions without a usable fit (flagged
by the `ok`/`r2` columns — DLTKcat is noisy, R²≈0.6) keep the default thermal
knobs. `etcgem dltkcat csv` instead writes a full `from_kcat_csv` provider table.

### Worked example: eciML1515 (included)

`etcgem sweep --strain eciML1515 --experiment default` runs a 120-sample sweep on
the GECKO *E. coli* model, output in `strains/eciML1515/outputs/sweep_default/`.
The extractor finds 2560 enzyme-linked reactions and reuses the model's own
0.091 g/gDW pool bound.
The nominal curve is single-peaked at ~37 C (rmax 0.57 /h, CTmax ~57 C), and the
sweep generates optima from ~30-45 C with varying peak rate and breadth.

**Getting a realistic (non-flat) TPC — two coupled settings.** A naive
enzyme-constrained TPC comes out flat-topped, for a subtle reason worth knowing:

* **Peak-normalised costs.** The model's reference kcat is treated as each
  enzyme's *maximum* (at its Topt), so temperature only ever *raises* cost
  (`enzyme_cost._costs` divides the MMRT shape by its own peak). Without this,
  anchoring kcat at T0 while placing Topt above T0 makes enzymes *cheaper* than
  the calibrated reference near the optimum, so the proteome pool goes slack and
  growth pins to an internal network ceiling — a flat top. Normalising removes
  the super-efficiency.
* **`pool_scale` (default 0.9 here).** Even normalised, the model's own pool
  bound is only marginally binding at the optimum. Scaling it slightly (<1)
  makes the pool bind across the whole curve, so `rmax` responds to temperature
  and allocation instead of sitting at the ceiling. Substrate uptake is *not*
  the limiter (glucose is unconstrained), so the lever is the pool, not the
  medium.

Curve width is set by `default_dCp` (more negative = narrower); `-12` gives a
falling limb that reaches ~zero by ~58 C. Real *E. coli*-specific shape comes
from per-enzyme `Topt`/`dCp` via DLTKcat (below).

Note the loader auto-handles a GECKO SBML quirk: reaction ids are encoded with
`__32__` for spaces, which cobra decodes to a literal space that the LP backend
rejects; `_read_sbml_safe` strips these on load.

---

## Allocation vs envelope decomposition (H1.3)

`decomposition.py` partitions the TPC variation a single genome can generate into
an **allocation** part, an **envelope** part, and their **interaction** — testing
hypothesis H1.3 (a TPC has a genome-set envelope shape and an allocation-set
magnitude, and they separate).

**Two parameter groups** (both fields of `Perturbation`):
- **envelope** (genome-set thermal shape): `dTopt`, `topt_scale`, `dCp_scale`
- **allocation** (proteome): `budget_scale` (and any per-group `alloc_<grp>`)

**Crossed design** (so the ANOVA is exact and balanced): draw M allocation samples
(envelope at nominal) and N envelope samples (allocation at nominal) by Latin
hypercube, then evaluate every crossed pair (allocation_i, envelope_j) to a TPC
and its descriptors, giving an M×N matrix `f_ij` per descriptor. For each
descriptor:

```
mu = mean(f_ij);  a_i = mean_j f_ij - mu;  e_j = mean_i f_ij - mu;  g_ij = f_ij - mu - a_i - e_j
V_A = mean(a_i^2);  V_E = mean(e_j^2);  V_AE = mean(g_ij^2);  V = V_A + V_E + V_AE
S_A,S_E,S_AE = V_A/V, V_E/V, V_AE/V        # grouped Sobol fractions (sum to 1)
phi_A = S_A + S_AE/2;  phi_E = S_E + S_AE/2 # Shapley effects, exact for two groups
```

```bash
etcgem decompose --strain eciML1515 --experiment decomposition        # M=N=24
etcgem decompose --strain eciML1515 --experiment decomposition_quick  # M=N=12 smoke
```

Writes into `strains/NAME/outputs/decompose_EXP/`: `decomposition_table.csv`,
`grids.npz`, the two marginal curve ensembles + `temps_C.npy`, `summary.json`,
and figures `achievable_ranges.png` (allocation-only | envelope-only fans),
`variance_partition.png` (stacked S_A/S_E/S_AE), `shapley_effects.png` (φ_A vs φ_E).

On eciML1515 the split is clean and matches H1.3: **rmax** (magnitude) is ~99%
**allocation**, while **Topt_C, CTmax_C, niche_width_C, Ea_eV** (temperature/shape)
are ~98–100% **envelope**.

**Caveat.** The variance fractions are defined relative to the chosen input
distributions (uniform over the configured ranges), so quote the ranges with any
result — this is a structural, in-silico decomposition of what the model *can*
generate, not a claim about real cells. Keep `budget_scale` in the pool-binding
regime (≲1.1) or the allocation axis looks artificially inert. The descriptor
table is the generic input to the ANOVA, so this can later target
respiration/CUE curves, not only growth.

---

## Library use

```python
from etcgem import providers, compute_tpc, run_sensitivity, Perturbation
import numpy as np

pm = providers.toy_ecoli_core(T0=303.15)          # or from_gecko(...) / from_kcat_csv(...)
temps = np.linspace(5, 53, 49)

# one curve
tpc = compute_tpc(pm, temps, Perturbation(dTopt=4.0, dCp_scale=1.5))
print(tpc.descriptors())

# a sweep
res = run_sensitivity(pm, temps,
    param_ranges={"dTopt": (-8, 8), "dCp_scale": (0.5, 2.0), "budget_scale": (0.7, 1.3)},
    n_samples=200)
res.save("outputs/my_run")
```

---

## Layout

```
pyproject.toml    package metadata + `etcgem` console script (src layout)
src/etcgem/
  mmrt.py         MMRT kcat(T) + Topt/dCp anchoring
  enzyme_cost.py  EnzymeEntry, cost table, sMOMENT pool constraint, Perturbation
  providers.py    toy_ecoli_core / from_gecko / from_kcat_csv + budget calibration
  tpc.py          compute_tpc + TPC descriptors
  sensitivity.py  Latin-hypercube sweep, ensemble, Spearman sensitivity
  plotting.py     ensemble fan, descriptor histograms, sensitivity heatmap
  config.py       defaults/strain/experiment loading, resolve, dump + provider dispatch
  dltkcat.py      DLTKcat kcat(T) -> MMRT (Topt, dCp) fitting + apply
  decomposition.py allocation vs envelope Shapley/ANOVA variance decomposition (H1.3)
  cli.py          two-tier CLI: build/tpc/fba (strain) + sweep/decompose (strain+experiment) + dltkcat
  __main__.py     `python -m etcgem` -> cli.main
defaults.yaml     universal method defaults (solver_timeout, crit_frac, fallback grid)
experiments/      default.yaml, quick.yaml, decomposition.yaml (method overlays)
strains/NAME/     strain.yaml (organism), model/, dltkcat/, outputs/<tag>/
docs/RUNBOOK.md   step-by-step run guide
```

## Assumptions & caveats

- Enzyme cost is a single lumped sMOMENT pool (one constraint), not per-enzyme
  GECKO usage variables. It reads kcats *from* a GECKO model but drives its own
  transparent constraint, which is what keeps the engine organism-agnostic and
  fast to update at each temperature. If you need GECKO's exact per-protein
  accounting, treat this as a screening layer on top of it.
- Only enzyme kcats carry temperature dependence; membrane/maintenance/non-
  enzymatic temperature effects are not modelled. Add them as extra constraints
  if needed.
- MMRT `dCp` defaults (≈ −12 kJ/mol/K) are literature-typical but not organism-
  specific — fit them where you have data (DLTKcat). Enzyme costs are normalised
  so the reference kcat is each enzyme's peak; combined with `pool_scale<1` this
  keeps the pool binding and the TPC single-peaked (see the eciML1515 example).
- Budget calibration (`target_fraction`) picks a pool that makes growth enzyme-
  limited at T0 so the TPC has meaningful structure; for real GECKO models the
  model's own `prot_pool` bound is used instead when present.
