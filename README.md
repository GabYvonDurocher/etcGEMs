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

**Thermal model — MMRT vs two-state unfolding** (`provider.thermal_model`). The
falling limb of the TPC can be produced two ways:

- `mmrt` (default in code) — *peak-normalised* MMRT: the reference kcat is treated
  as each enzyme's maximum, so any deviation only raises cost and the MMRT curvature
  `dCp` sets both breadth and Ea (`enzyme_cost._costs` divides the shape by its own
  peak). Simple, but couples breadth to Ea and can push CTmax unrealistically high.
- `unfolding` — two-state native↔denatured model after Li et al. 2021 and the MRes
  (Madkaikar 2023): `cost_i(T) = base_i / (rel_kcat_i(T)·f_N_i(T))`, where `f_N(T)`
  is the **native fraction** keyed on a per-enzyme melting temperature `Tm`
  (`unfolding.py`). Denaturation (`Tm`) sets CTmax and the falling limb, decoupled
  from the rising-limb Ea (kcat(T)/Topt). Grounded per-enzyme `Tm` (melting proteome,
  Leuenberger 2017) and `Topt` (Li–Engqvist 2019) are joined by UniProt id from a
  parameter table (`provider.enzyme_params`); unmatched enzymes fall back to dataset
  means. Adds an optional temperature-dependent maintenance term
  (`provider.ngam_temperature`). For **other library strains** without measured
  values, sequence predictors (DeepET/TOMER-type for Topt/Tm) supply per-enzyme
  parameters; not needed for the *E. coli* eciML1515 worked example, which ships with
  a grounded table under `strains/eciML1515/thermal/`. The `mmrt` path is byte-for-
  byte unchanged when selected.

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
etcgem calibrate-dcp --strain eciML1515 --target-ea 0.65   # set provider.default_dCp for a target Ea
```

`calibrate-dcp` bisects `provider.default_dCp` (nominal Ea rises monotonically with
`|dCp|`) so the nominal rising-limb Ea matches `--target-ea`, then writes the
calibrated `default_dCp` back into `strain.yaml` (and, since a shallower dCp
broadens the TPC, extends `temperature_grid.stop_C`/`n` if CT_max would run past the
grid). **The target is configurable** and defaults to 0.65 eV (the metabolic-theory
value); set it to your measured bacterial growth-TPC Ea. Note the resulting dCp is
chosen purely to hit the Ea target — it also sets curve width, so a low Ea implies a
broad TPC.

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

## Per-enzyme control & identifiability (H1.1 / H1.2)

`control.py` asks, per individual enzyme: which enzymes' thermal parameters set
the organismal TPC **envelope** (Topt, CT_max), which enzymes' capacity sets the
**rate** (rmax/B0), and — the identifiability flip side — which parameters the
growth TPC is *insensitive* to and therefore cannot be inferred from growth data
alone (they need proteome/flux data). Strain-level; no experiment sweep.

**Two control-coefficient families** (central finite differences, reusing the
mutate-entry → `refresh_params` pattern):
- **Thermal control** `CC[D, Topt_i] = (D(Topt_i+dT) − D(Topt_i−dT))/(2dT)` (and a
  fractional step for `dCp_i`) for envelope descriptors `D` — how much one enzyme's
  optimum moves the organismal Topt / CT_max / niche width.
- **Rate control** `FCC_i(T) = d ln µ / d ln kcat_i` (via `base_cost`) — flux
  control of growth at temperature T; only used enzymes can be nonzero.

**Two-stage** (tractable on ~2500 enzymes): Stage A screens *all* enzymes from the
nominal solution using usage share `u_i(T)=cost_i(T)|v_i(T)|/budget` and analytic
cost sensitivity `s_i(T)=−d ln(relative_kcat_i)/dT`; the top `screen_top_k` go to
Stage B finite differences. Analysis temperatures default to sub/opt/supra
(Topt−10, Topt, min(CT_max−2, Topt+8)).

```bash
etcgem control --strain eciML1515 --experiment control          # full (fine grid)
etcgem control --strain eciML1515 --experiment control_quick    # fast smoke
```

Writes into `strains/NAME/outputs/control_EXP/`: `thermal_control.csv`,
`rate_control.csv`, `usage_by_temperature.csv`, `identifiability.csv`,
`summary.json`, and figures `thermal_control_bar.png`,
`bottleneck_vs_temperature.png`, `identifiability_hist.png`.

**Identifiability** is computed **proteome-wide** — one row per enzyme × parameter
(`Topt_i`, `dCp_i`, `kcat_i`) in `identifiability.csv`, not just the top-K screened
enzymes. For every enzyme the score is the cheap Stage-A screen (usage share ×
analytic thermal/rate sensitivity), max-normalised across the proteome; where a
top-K finite-difference control coefficient exists it replaces the proxy (more
accurate) and the row is marked `refined = True`. `p_i` is flagged identifiable
from the growth TPC if `ident_i > threshold`, else "requires omics".
`summary.json` reports **both** the proteome-wide identifiable fraction (small —
most parameters cannot be inferred from growth alone, H1.2) and the fraction among
the top-K control enzymes (high — a few enzymes dominate control, H1.1). On the toy
strain the two **summation checks are O(1)** (Σ FCC(opt) ≈ 1–2, Σ CC[Topt_org,
Topt_i] ≈ 1 on a refined grid), thermal control is **concentrated in a few enzymes**
(H1.1), and only a **minority of parameters are identifiable from growth** (~15–17%
proteome-wide; the rest never limit → require omics, H1.2).

**Notes.** `Topt_C` is an argmax descriptor, so single-enzyme thermal CCs need a
fine TPC grid to register (set by `control.grid_refine`, default ×4); `CT_max_C`
and `niche_width_C` are interpolated and behave smoothly. This is a first-order,
control-magnitude proxy for identifiability — not a full Fisher-information /
profile-likelihood analysis. Descriptor extraction is generic, so it can later
target respiration/CUE curves too.

---

## Allocation sectors (Basan/Scott)

Optionally refine the single scalar proteome pool into three sectors of the total
proteome mass fraction `P_total` that sum to 1 (`sectors.py`):

- **f_metab** — metabolic enzymes → the existing pool bound = `f_metab · P_total`
- **f_bio** — biosynthesis/ribosomes → a translation cap `translation_coeff · v_biomass ≤ f_bio · P_total`
- **f_maint** — maintenance/housekeeping → proteome overhead + maintenance ATP (ATPM/NGAM lb scaled)

`translation_coeff` is auto-calibrated so the translation cap and the metabolic
pool are co-limiting at the nominal split and T0 — so B0 becomes an explicit
allocation trade-off with an **interior optimum** (too little metabolic pool
starves enzymes; too little biosynthesis caps translation). Opt-in per strain:

```yaml
# strains/NAME/strain.yaml
proteome_sectors: {enabled: true, P_total: null, f_metab: 0.5, f_maint: 0.15,
                   atpm_reaction: null, translation_coeff: auto}
```

```bash
etcgem sweep --strain eciML1515 --experiment sectors   # sweeps f_metab / f_maint
```

`Perturbation.f_metab/f_maint` (and `maint_to_bio`) drive `set_allocation` instead
of `set_budget`; sensitivity/decomposition accept `f_metab`/`f_maint` as allocation
params with the ANOVA untouched. **Disabled by default → identical to the scalar
pool.** Growth-law couplings (`translation_coeff`, maintenance ATP, `P_total`) are
calibratable against growth-rate proteomics; the defaults are order-of-magnitude
and auto-calibration co-limits only at the nominal point.

### Temperature-dependent allocation from proteomics (`proteome_alloc.py`)

The sector split can be made **temperature-dependent** from a measured, temperature-
resolved *E. coli* proteome (Wang 2026), rather than fixed. Set
`allocation_from_data: proteomics/tem_proteomic.csv` (with `proteome_sectors.enabled:
true`): proteins are mapped to coarse sectors by COG category, mass-weighted sector
fractions are computed per temperature, and `compute_tpc` sets the sector allocation
at each T from the measured `f_sector(T)` (anchored to the nominal split at T0). The
CLI runs the data product + a predicted-vs-measured validation:

```bash
etcgem proteome-sectors --strain eciML1515   # -> outputs/proteome_sectors/
```

It writes `sector_fractions_vs_T.csv/.png` (the measured chaperone ramp above 37 °C),
reports mapping coverage (b-number → UniProt, ~62 % of enzymes), and compares
predicted per-enzyme mass (`cost_i(T)·|v_i|`) to measured abundance × MW
(`validation_*.csv`, `usage_pred_vs_meas.png`). **Disabled by default → identical to
the fixed sectors.**

## Calibrated thermal sampling (M1.2)

Instead of the two global envelope knobs, sample each enzyme's `(Topt_i, dCp_i)`
from a one-factor model (`thermal_sampling.py`):

```
Topt_i = mean_i + sd_i · ( sqrt(rho)·Z + sqrt(1-rho)·eps_i )   # rho = shared_fraction
```

with a shared organism regime `Z` per ensemble member and per-enzyme `eps_i`.
**rho=1** → coherent whole-proteome shift (like a global `dTopt`); **rho=0** →
independent per-enzyme optima. Modes: `knobs` (default, current behaviour),
`correlated` (mean = nominal, sd from config), `posterior` (mean + sd per enzyme
from DLTKcat `fits.csv`). Add to any sweep/decompose experiment:

```yaml
envelope_sampling: {mode: correlated, shared_fraction: 0.7, topt_sd_K: 4.0,
                    dcp_sd_frac: 0.3, posterior_from: dltkcat}
```

```bash
etcgem sweep --strain eciML1515 --experiment calibrated   # correlated envelope ensemble
```

**Posterior uncertainty.** `dltkcat.fit_mmrt` is linear least squares in
`(dH, dS, dCp)`, so it has covariance `Cov = sigma^2 (XᵀX)⁻¹`; `Topt_sd`/`dCp_sd`
come from sampling `(dH,dS,dCp) ~ N(coef, Cov)` and computing `Topt` per draw
(Topt is nonlinear, so sampled not linearised), with `sigma` **floored by
DLTKcat's global skill** (log10 RMSE ≈ 0.9) so optimistic residuals don't
understate uncertainty. `fit_predictions` writes `Topt_sd`/`dCp_sd` into
`fits.csv`; `posterior` mode reads them. **No `envelope_sampling` block →
identical to the knobs path.**

Caveats: the one-factor correlation is a deliberately simple stand-in for the true
(phylogenetic/structural) covariance of thermostability — rho is the single knob;
the posterior sd is a floored local-Gaussian approximation, not a full Bayesian
posterior (the floor makes the DLTKcat-derived sds large, honestly reflecting its
noise).

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
  control.py      per-enzyme thermal control coefficients + identifiability (H1.1/H1.2)
  sectors.py      optional proteome-sector allocation (Basan/Scott)
  thermal_sampling.py correlated / DLTKcat-posterior per-enzyme thermal sampling (M1.2)
  cli.py          two-tier CLI: build/tpc/fba/control (strain) + sweep/decompose (strain+experiment) + dltkcat
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
