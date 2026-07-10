# etcgem

**Predicting microbial thermal performance curves (TPCs) from genomes** with an
enzyme- and temperature-constrained genome-scale metabolic model (etc-GEM).

The organismal TPC — growth rate vs temperature — is **not assumed**; it *emerges*
from enzyme-constrained FBA: every enzyme's turnover carries a temperature response,
protein folding sets a high-temperature collapse, total enzyme demand is bounded by a
measured proteome allocation, and biomass is maximised at each temperature. The worked
example is *E. coli* (GECKO **eciML1515**), built as **one complete, data-grounded
model** and validated **per individual growth curve** — with **nothing fit to the
growth data**: magnitude, activation energy and allocation all come from independent
data or literature values.

> This repo also contains a full write-up in `reports/etcgem/` (Quarto → PDF/docx):
> model equations, parameter provenance, validation and results. See
> [The report](#the-report-quarto).

---

## The complete model

For *E. coli*, `strains/eciML1515/strain.yaml` assembles four data-grounded layers.
(The engine is organism-agnostic; each layer is opt-in, and the classic
peak-normalised-MMRT path is preserved byte-for-byte as a baseline.)

### 1. Metabolic network + enzyme constraints (GECKO)

iML1515 stoichiometry + GPRs (Monk 2017), enzyme-constrained via GECKO
(Sánchez 2017; Domenzain 2022), solved with cobrapy. Each reaction's flux costs enzyme
mass `MW_i · |v_i| / (kcat_i · 3600)`; the summed cost is bounded by a shared proteome
pool (a transparent sMOMENT constraint driven in place at each temperature —
`enzyme_cost.py`).

### 2. Thermal envelope — MMRT + two-state unfolding (`provider.thermal_model`)

Each enzyme's turnover follows **Macromolecular Rate Theory (MMRT)** on the rising limb
(`mmrt.py`):

```
ln k(T) = ln(kB·T/h) + (−dH0 − dCp·(T−T0))/(R·T) + (dS0 + dCp·(ln T − ln T0))/R
```

anchored on the model's reference kcat and two interpretable knobs — `Topt` (peak) and
`dCp` (curvature). Two ways to produce the falling limb:

- **`unfolding`** *(the eciML1515 default; `unfolding.py`)* — a two-state
  native↔denatured equilibrium after **Li et al. 2021** / the **MRes (Madkaikar 2023)**.
  The effective cost is `c_i(T) = base_i / (rel_kcat_i(T) · f_N_i(T))`, where the
  **native fraction** `f_N(T) = 1/(1+exp(−dGu(T)/RT))` is keyed on a per-enzyme
  **melting temperature `Tm`**. Denaturation sets `CTmax` and the falling limb,
  **mechanistically decoupled** from the rising-limb `Ea`. Per-enzyme `Tm`
  (Leuenberger 2017 melting proteome) and `Topt` (Li–Engqvist 2019 predictor) are joined
  by UniProt id (`provider.enzyme_params`); ~90 % of eciML1515 enzymes are grounded,
  the rest fall to dataset means. A temperature-dependent maintenance term
  (`provider.ngam_temperature`) is included.
- **`mmrt`** *(backward-compatible baseline; the code default)* — peak-normalised MMRT:
  the reference kcat is each enzyme's maximum, so any deviation only raises cost and the
  MMRT curvature `dCp` alone sets both breadth and `Ea`. Simpler, but couples breadth to
  `Ea` and pushes `CTmax` unrealistically high (~76 °C). Selecting it reproduces
  pre-unfolding results byte-for-byte.

### 3. Per-enzyme `dCp` from independent data — **emergent `Ea`** (`provider.dcp_from`)

`dCp_from: prior` grounds per-enzyme curvature in an **independent MMRT literature
prior** (−4 kJ/mol/K, Hobbs 2013) plus **DLTKcat** kcat(T) fits where available
(`provider.dltkcat_fits`) — **no value is chosen to hit an `Ea` target**. The
organismal `Ea` therefore **emerges** (0.83 eV on LB, 0.96 on minimal) and is *tested*
against the independent mesophilic-bacterial-growth benchmark (0.84–0.88 eV, Smith 2019),
far from the 0.65 eV metabolic-theory value earlier (wrongly) calibrated to. The
`calibrate-dcp` CLI that fit `dCp` to a target `Ea` is **deprecated / unused**.

### 4. Proteome allocation — measured, medium- *and* temperature-matched sectors

The pool is refined into three growth-law sectors (Basan 2015; Scott 2010;
`sectors.py`):

- **f_metab** — metabolic enzymes → pool bound `= f_metab · P_total`
- **f_bio** — biosynthesis/ribosomes → translation cap `translation_coeff · v_biomass ≤ f_bio · P_total`
- **f_maint** — maintenance/housekeeping → proteome overhead + maintenance ATP

The sector fractions are **set from the measured *E. coli* proteome, matched to growth
medium *and* temperature** (Wang 2026; per-medium LB / Glucose / Glycerol series;
`proteome_alloc.py`), never hand-set or fit. This captures the **growth law**: the
measured ribosome fraction at 37 °C is **f_bio = 0.36 on LB but 0.18 on glucose-minimal**,
so a run under LB gets a higher translation cap and predicts faster growth — straight
from data. `providers.set_medium(pm, "LB" | "glucose_minimal")` opens the medium's
component uptakes (availability, uptake **not** pinned) *and* switches the active
per-medium sector curve.

### Emergent magnitude — **nothing fit to growth**

The metabolic pool budget is derived from independent quantities, not the
growth-calibrated GECKO bound:

```
P_metab = P_total × f_metab × σ
        = 0.5 g/gDW  ×  f_metab(medium, T)  ×  0.45
```

with `P_total` literature total protein, `f_metab` the *measured* metabolic fraction, and
`σ` the in-vivo enzyme saturation (Davidi 2016 / Heckmann 2020; range 0.4–0.5). The
deprecated `pool_scale` knob is set to 1.0. Emergent `rmax` ≈ **0.55 h⁻¹ on
glucose-minimal, 1.04 h⁻¹ on LB** (the ~2× growth-law boost, from the measured
ribosome fraction), `CTmax` ≈ 47 °C (Tm-set).

---

## Install

```bash
pip install -e .        # editable; installs the `etcgem` CLI + deps
# deps: cobra, numpy, scipy, pandas, matplotlib, pyyaml (+ jupyter/tabulate for the report)
```

`src/` layout (`src/etcgem`); one console command `etcgem` (also `python -m etcgem`).
Run from the project root.

## Quickstart

```bash
# offline synthetic strain (e_coli_core, no network) — good smoke test
etcgem tpc   --strain _toy
etcgem sweep --strain _toy --experiment quick

# the complete E. coli model
etcgem build --strain eciML1515                 # build + coverage summary
etcgem tpc   --strain eciML1515                 # emergent nominal TPC + descriptors
```

A `sweep` writes `strains/NAME/outputs/sweep_EXP/`: `nominal_tpc.csv`, `curves.npy` +
`temps_C.npy`, `samples.csv`, `descriptors.csv`, `sensitivity_spearman.csv`,
`summary.json`, and PNGs (ensemble fan, descriptor histograms, sensitivity heatmap,
descriptor-interval + sector-tradeoff plots). TPC descriptors (`tpc.py`): `Topt`,
`rmax`, critical limits `CTmin/CTmax` (at `crit_frac` of rmax), niche width, `B80`,
Boltzmann–Arrhenius `Ea` of the rising limb (eV / kJ·mol⁻¹), skewness.

---

## Config model: defaults ← strain ← experiment

Three tiers merged as **defaults ← strain ← experiment** (organism keys from the
strain; method keys from defaults, overridden by the experiment):

| file | holds |
|------|-------|
| `configs/defaults.yaml` | universal **method** defaults: `solver_timeout`, `crit_frac`, fallback `temperature_grid` |
| `strains/NAME/strain.yaml` | **organism only**: `provider` block, `T0_C`, `temperature_grid`, `proteome_sectors`, `allocation_from_data` |
| `configs/experiments/EXP.yaml` | optional **method overlay**: `kind` + a `sensitivity` / `decomposition` / `control` block |

`config.resolve(strain, experiment)` returns the merged dict (with
`provider.model_path` injected); every run also writes the exact merged config as
`resolved_config.yaml`.

### The complete-model strain (`strains/eciML1515/strain.yaml`)

```yaml
provider:
  type: gecko
  model_file: eciML1515_batch.xml
  pool_scale: 1.0                 # DEPRECATED knob (1.0 = nothing tuned to growth)
  thermal_model: unfolding        # two-state Tm envelope (vs `mmrt` baseline)
  ngam_temperature: true          # temperature-dependent maintenance
  enzyme_params: thermal/BestParamsTopt.csv   # grounded Topt/Tm (Li-Engqvist / Leuenberger)
  dcp_from: prior                 # per-enzyme dCp: literature prior (+DLTKcat), Ea EMERGES
  dcp_prior_kJ: -4.0              # literature MMRT dCp prior (Hobbs 2013)
  dltkcat_fits: dltkcat/fits_ext.csv          # DLTKcat Topt/dCp where fits exist
  p_total: 0.5                    # total protein per gDW (literature) — emergent magnitude
  sigma: 0.45                     # in-vivo enzyme saturation (Davidi/Heckmann)
proteome_sectors:                 # ENABLED; nominal = measured Glucose 30 C fractions
  enabled: true
  f_metab: 0.483
  f_maint: 0.326
  translation_coeff: auto
allocation_from_data: proteomics/tem_proteomic.csv   # measured, medium+T-matched sectors
default_medium_proteome: Glucose  # default medium's sector fractions
```

Strain data folders:

```
strains/eciML1515/
  model/eciML1515_batch.xml       GECKO ecModel
  thermal/     BestParamsTopt.csv (Topt/Tm), ExpGrowth.csv + ecoli_tpc_curves.csv (validation)
  dltkcat/     input/output/fits[_ext].csv  (DLTKcat workflow)
  proteomics/  tem_proteomic.csv  (per-medium temperature proteome, Wang 2026)
  media/       LB_media.csv       (rich-medium definition)
  outputs/<tag>/
strains/_toy/         offline synthetic strain (no model file)
strains/_template/    copy to start a new strain
```

### Repository layout

```
etcGEMs/
├── configs/                     ALL config: defaults.yaml, examples/, experiments/
├── scripts/                     helper scripts (push_updates.sh)
├── src/etcgem/                  the package
├── strains/eciML1515/           strain descriptor + raw data (model/ media/ thermal/
│   │                            proteomics/ dltkcat/) + outputs/
│   └── outputs/
│       ├── <canonical runs>     the runs the report renders from
│       └── _archive/            superseded / quick / diagnostic runs (on disk, gitignored)
├── reports/etcgem/              report.qmd, supplementary.qmd, assets/, assemble.py
├── prompts/                     README index; repo_restructure_prompt.md; archive/ (executed)
└── docs/                        RESTRUCTURE_PROPOSAL.md, correspondence/
```

External, kept outside the tracked tree and **gitignored** (documented, not committed):
`DLTKcat/` (vendored kcat(T) predictor clone) and `refs/` (reference PDFs). The legacy
`tpc_pipeline/` scaffold has been removed (fully superseded by `src/etcgem/`).

---

## Commands

**Strain-only** (runs with no experiment):

```bash
etcgem build --strain eciML1515                 # build + report coverage (Topt/Tm, sectors)
etcgem tpc   --strain eciML1515                 # emergent nominal TPC + descriptors
etcgem fba   --strain eciML1515 --temp 37       # single enzyme-constrained solve
etcgem proteome-sectors --strain eciML1515      # measured sector fractions + predicted-vs-measured proteome
etcgem calibrate-dcp --strain eciML1515 --target-ea 0.65   # [DEPRECATED — fits dCp to an Ea target; not used]
```

**Strain + experiment:**

```bash
etcgem sweep     --strain eciML1515 --experiment default              # global sensitivity
etcgem sweep     --strain eciML1515 --experiment sectors              # sector-allocation sweep
etcgem sweep     --strain eciML1515 --experiment calibrated           # correlated/DLTKcat-posterior uncertainty
etcgem sweep     --strain eciML1515 --experiment dltkcat_ext --fits strains/eciML1515/dltkcat/fits_ext.csv
etcgem decompose --strain eciML1515 --experiment decomposition_sectors  # allocation-vs-envelope Shapley split
etcgem control   --strain eciML1515 --experiment control              # per-enzyme control + identifiability
```

Shipped experiments: `default`, `quick`, `sectors`, `calibrated(_quick)`,
`control(_quick)`, `decomposition(_quick/_sectors)`, `dltkcat_ext`. `sweep` supports
`--resume --seconds N` (checkpointed) and `--config PATH` (ad-hoc self-contained config).

To add a strain: `cp -r strains/_template strains/NAME`, drop the GECKO model in
`strains/NAME/model/`, set `provider.model_file`, then `etcgem build --strain NAME`.
GECKO stores no temperature parameters; for library strains without measured
`Topt`/`Tm`, sequence predictors (DeepET/TOMER-type) supply them.

---

## The analyses

### Global sensitivity
`sensitivity.py` — Latin-hypercube sweep over envelope knobs (`dTopt`, `topt_scale`,
`dCp_scale`) and allocation (`budget_scale` / sector `f_metab`,`f_maint`), reducing each
sampled TPC to descriptors + Spearman indices. On the complete model, `rmax` is depressed
by envelope shifts more than raised by the budget — the envelope drives the rate.

### Allocation vs envelope decomposition (H1.3)
`decomposition.py` — a crossed **allocation × envelope** design (M×N), split per
descriptor into allocation / envelope / interaction variance with an exact two-group
Shapley attribution `φ_A = S_A + S_AE/2`. **Headline result on the complete model:**
`rmax` is only **28 % allocation** (φ_A = 0.28), and the thermal **envelope dominates
every descriptor** (72–99 %) — overturning the peak-normalised model's ~100 %-allocation
`rmax` and showing that clean "allocation sets magnitude" split was **largely a
structural artifact**. `etcgem decompose --experiment decomposition_sectors`.

### Per-enzyme control + identifiability (H1.1 / H1.2)
`control.py` — Stage A screens all ~2560 enzymes (usage × thermal sensitivity), Stage B
computes finite-difference control coefficients on the top-K. **Identifiability** is
computed **proteome-wide** (every enzyme × {Topt, dCp, kcat}): only ~2 % of parameters
are identifiable from growth alone (the rest need omics), while thermal control is
concentrated in a few enzymes. `etcgem control --experiment control`.

### Calibrated uncertainty (M1.2)
`thermal_sampling.py` — sample each enzyme's `(Topt, dCp)` from a one-factor model
(`shared_fraction = ρ`; modes `knobs` / `correlated` / `posterior` from DLTKcat fits).
Add an `envelope_sampling:` block to any experiment. Sharpens the physically pinned
descriptors (`CTmax` IQR ~0.4 °C, Tm-fixed) while propagating per-enzyme optimum
uncertainty.

### Temperature/medium proteome allocation + proteome validation
`proteome_alloc.py` + `etcgem proteome-sectors` — the data product (per-medium sector
fractions, chaperone ramp) and a **predicted-vs-measured** test: predicted per-enzyme
mass `cost_i(T)·|v_i|` vs measured abundance × MW (Spearman ρ ≈ 0.3, ~62 % coverage).

### Per-curve validation against empirical TPCs
The complete model is validated **per individual curve** against 26 *E. coli* growth
TPCs (Smith 2019 database; `strains/eciML1515/thermal/ecoli_tpc_curves.csv`), each
predicted under **its** medium (2 defined glucose-minimal, 24 rich → LB) with
medium-matched allocation. **Primary metric: absolute R²/RMSE on raw growth rate
(h⁻¹)**; shape R² and the rising-limb `Ea` are secondary. Outputs under
`outputs/percurve_validation/` (small-multiples flagged by medium, R² distribution). The
medium-matched allocation reproduces the growth-law magnitude difference (LB ~2×
minimal) and closes much of the rich-curve gap (median absolute R² −0.8 → +0.2), with an
honest residual under-prediction of the fastest curves.

---

## Parameter provenance (nothing fit to growth)

| symbol | quantity | source | coverage / value |
|---|---|---|---|
| `MW_i, kcat_ref` | enzyme mass, reference turnover | GECKO ecModel of iML1515 | 2560 enzymes |
| `Topt_i` | catalytic optimum | Li–Engqvist 2019 predictor; DLTKcat overlay | 90 % grounded; 13 DLTKcat |
| `Tm_i` | melting temperature | Leuenberger 2017 melting proteome | 90 % grounded, rest at mean 55.6 °C |
| `dCp_i` | MMRT curvature | literature MMRT prior −4 kJ/mol/K (Hobbs 2013) + DLTKcat | prior for all; 13 DLTKcat |
| `f_metab / f_bio / f_maint` | sector fractions | measured proteome, per medium & T (Wang 2026) | LB / Glucose / Glycerol, 16–43 °C |
| `P_total` | total protein per gDW | literature | 0.5 g/gDW |
| `σ` | in-vivo enzyme saturation | Davidi 2016 / Heckmann 2020 | 0.45 (range 0.4–0.5) |
| medium | growth condition | Smith 2019 metadata; LB from MRes / Machado 2018 | per curve |

### DLTKcat workflow (`dltkcat.py`)

DLTKcat ([SizheQiu/DLTKcat](https://github.com/SizheQiu/DLTKcat)) predicts kcat *as a
function of temperature*; the module fits an MMRT curve to its kcat-vs-T points and
recovers per-enzyme `Topt`/`dCp` (+ posterior sds for calibrated sampling).

```bash
etcgem dltkcat prep  --strain eciML1515 --tmin 5 --tmax 55 --n 11   # -> dltkcat/input.csv
#  run DLTKcat in its repo -> dltkcat/output.csv
etcgem dltkcat parse --strain eciML1515 --temp-col Temp_C --kcat-col pred_log10kcat  # -> dltkcat/fits.csv
```

`apply_fits_to_provider` sets `Topt`/`dCp` (and, in unfolding mode, the transition-state
`dCpt`) in place, keeping the calibrated enzyme costs. Reactions without a usable fit
(DLTKcat is noisy, R²≈0.6) keep the grounded/prior thermal parameters.

---

## The report (Quarto)

`reports/etcgem/` renders a complete, collaborator-ready write-up to PDF + docx —
model equations, parameter provenance, in-silico experiments, and the per-curve /
proteome / ablation validation.

```bash
python reports/etcgem/assemble.py        # copy the chosen run outputs into assets/
cd reports/etcgem && quarto render       # -> _output/report.pdf (+ .docx, supplementary)
```

`report.qmd` embeds the pre-generated figures and reads result CSVs via executable
Python chunks; `assemble.py` curates which run dirs feed each figure/table (edit its
`RUNS` map to re-point). Requires Quarto + a LaTeX toolchain (`quarto install tinytex`)
and `pip install jupyter tabulate`.

---

## Library use

```python
import numpy as np
from etcgem import providers, compute_tpc, Perturbation
from etcgem.config import resolve, build_provider

# the complete E. coli model from config
pm = build_provider(resolve("eciML1515"))
providers.set_medium(pm, "LB")                     # or "glucose_minimal"
tpc = compute_tpc(pm, np.linspace(5, 50, 91), Perturbation())
print(tpc.descriptors())                            # Topt, rmax, CTmax, Ea, ...

# or a bare provider + a sweep
from etcgem import run_sensitivity
pm = providers.toy_ecoli_core(T0=303.15)
run_sensitivity(pm, np.linspace(5, 53, 49),
    param_ranges={"dTopt": (-8, 8), "dCp_scale": (0.5, 2.0), "budget_scale": (0.7, 1.3)},
    n_samples=200).save("outputs/my_run")
```

---

## Layout

```
pyproject.toml       package metadata + `etcgem` console script (src layout)
src/etcgem/
  mmrt.py            MMRT kcat(T) + Topt/dCp anchoring
  unfolding.py       two-state native<->unfolded model (Tm falling limb) + NGAM(T)
  enzyme_cost.py     cost table, sMOMENT pool, sectors, thermal_model dispatch, Perturbation
  providers.py       toy / from_gecko / from_kcat_csv; grounded params; emergent budget; set_medium
  proteome_alloc.py  measured per-medium sector fractions + temperature/medium allocation + proteome validation
  sectors.py         proteome-sector partition (metab/bio/maint), translation cap
  tpc.py             compute_tpc + TPC descriptors
  sensitivity.py     Latin-hypercube sweep, ensemble, Spearman sensitivity
  decomposition.py   allocation-vs-envelope Shapley/ANOVA variance decomposition
  control.py         per-enzyme thermal control + proteome-wide identifiability
  thermal_sampling.py correlated / DLTKcat-posterior per-enzyme sampling
  dltkcat.py         DLTKcat kcat(T) -> MMRT (Topt/dCp) fitting + apply
  plotting.py        ensemble/descriptor/sensitivity/decomposition figures
  config.py          defaults/strain/experiment resolve + provider dispatch + emergent/medium wiring
  cli.py             build/tpc/fba/calibrate-dcp/proteome-sectors (strain) + sweep/decompose/control (+experiment) + dltkcat
defaults.yaml        universal method defaults
experiments/         default, quick, sectors, calibrated, control, decomposition[_sectors], dltkcat_ext
strains/NAME/        strain.yaml (organism) + model/ thermal/ dltkcat/ proteomics/ media/ outputs/
reports/etcgem/      Quarto report (report.qmd, supplementary.qmd, assemble.py, header.tex, references.bib)
docs/RUNBOOK.md      step-by-step run guide
```

---

## Assumptions & caveats

- **Nothing is fit to the growth curve.** Magnitude (`P_total·f_metab·σ`), envelope
  (`Tm`, grounded `Topt`, literature/DLTKcat `dCp`) and allocation (measured per-medium
  sectors) all come from independent data or stated literature values with ranges. The
  emergent TPC is a genuine a-priori prediction — and is reported honestly where it fits
  worse (steep low-T rising limb; under-prediction of the fastest rich curves).
- **Enzyme cost is a lumped sMOMENT pool**, not GECKO's per-protein usage variables — a
  transparent, organism-agnostic screening layer that reads kcats from a GECKO model.
- **Only enzyme turnover + folding carry temperature dependence**; membrane/non-enzymatic
  effects and a flux-carrying chaperone sector are not modelled (chaperones enter as a
  maintenance input).
- **Medium is availability, not pinned uptake** — the enzyme constraints set actual
  uptake.
- **Identifiability is a first-order control-magnitude proxy**, not a
  Fisher-information / profile-likelihood analysis.
- Variance-decomposition fractions are defined relative to the swept input ranges (a
  structural, in-silico decomposition — quote the ranges).
- The `mmrt` peak-normalised path and the scalar-pool / temperature-independent-sector
  configurations remain available (and byte-identical when selected) as
  backward-compatible baselines / ablations.
```
