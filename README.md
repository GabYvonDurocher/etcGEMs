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
etcgem sweep --config configs/toy.yaml
```

Runs on `e_coli_core` (ships with cobrapy) with synthetic enzyme kinetics, so it
works with no network access. Writes to `outputs/toy_run/`:

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

## Strains (per-organism folders)

Real models live under `strains/NAME/`:

```
strains/eciML1515/
  config.yaml            # provider knobs + temperature grid + sensitivity block
  model/eciML1515_batch.xml
  dltkcat/               # input.csv, output.csv, fits.csv (DLTKcat workflow)
  outputs/default/       # sweep with default thermal params
  outputs/dltkcat/       # sweep with DLTKcat-derived Topt/dCp (--fits)
strains/_template/       # copy this to start a new strain
```

`config.yaml` names the model with `provider.model_file`; the CLI injects the
absolute `provider.model_path` and `output_dir` at run time, so the config stays
path-free and portable. Run the worked E. coli sweep with:

```bash
etcgem sweep --strain eciML1515                 # -> strains/eciML1515/outputs/default
etcgem sweep --strain eciML1515 --fits          # + DLTKcat fits -> outputs/dltkcat
etcgem sweep --strain eciML1515 --resume --seconds 60   # checkpointed, call repeatedly
```

To add a strain: `cp -r strains/_template strains/NAME`, drop the model in
`strains/NAME/model/`, set `model_file`, then `etcgem sweep --strain NAME`.

## Using another model (ecYeastGEM etc.)

1. Get an enzyme-constrained model. For yeast, the GECKO ecYeastGEM lives at
   `github.com/SysBioChalmers/ecModels` (or build one with GECKO 3). Any
   GECKO-style SBML/`.mat`/`.json` works.
2. Make it a strain (recommended, as above), or point a standalone config at it
   (`configs/example_gecko.yaml`, which still carries an explicit `model_path`):

```bash
etcgem sweep --config configs/example_gecko.yaml
```

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

`strains/eciML1515/config.yaml` runs a 120-sample sweep on the GECKO *E. coli*
model, output in `strains/eciML1515/outputs/default/`. The extractor finds
2560 enzyme-linked reactions and reuses the model's own 0.091 g/gDW pool bound.
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
  config.py       YAML/JSON config + provider dispatch
  dltkcat.py      DLTKcat kcat(T) -> MMRT (Topt, dCp) fitting + apply
  cli.py          unified CLI: sweep (one-shot/resume/+fits) + dltkcat tools
  __main__.py     `python -m etcgem` -> cli.main
configs/          toy.yaml (offline), example_gecko.yaml (standalone model)
strains/NAME/     config.yaml, model/, dltkcat/, outputs/{default,dltkcat}
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
