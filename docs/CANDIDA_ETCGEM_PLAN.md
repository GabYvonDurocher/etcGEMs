# Plan: bringing the Candida etcGEMs into the common framework

_Scoping document, in the pattern of `METHANOGEN_ETCGEM_PLAN.md` and `PHOTOTROPH_ETCGEM_PLAN.md`.
Structural only: one core model in `src/etcgem`, every organism a subfolder under `strains/` that
uses it, strain-specific variation confined to that subfolder. What is asked of the unified
framework afterwards is a separate matter and is not set out here._

## 1. Where things stand

Two implementations of the etcGEM exist in the group.

`src/etcgem` (this repository) is the core: a package with a config model
(`defaults ← strain ← experiment`), providers for several model kinds (`gecko`, `smoment_gem`,
`csv`, `fba`), one thermal layer, one enzyme-cost layer, and the analysis commands. Three
organisms use it, each as a data folder under `strains/` containing nothing but a `strain.yaml`,
a model, media, thermal parameters, kcat inputs and outputs.

`gem/` in `icakin/Candidas` is Ilgaz's separate implementation for four Candida species. It does
not import `etcgem`. It re-implements the enzyme-cost and thermal layers in its own scripts, with a
different thermal function, its own path map, its own environment, and species handled by a
dictionary rather than by folders.

The rule adopted for the O2 model applies: the method lives in one place and does not drift between
implementations. Bringing Candida in means the four species become `strains/` entries like the other
three and `gem/` stops being a second core.

## 2. The target structure

```
etcGEMs/
├── src/etcgem/                      the ONE core: providers, thermal layer, enzyme cost, analyses
├── configs/                         method defaults + experiment overlays (shared)
├── tools/reconstruction/            NEW: building a strain's inputs from a proteome (shared)
├── strains/
│   ├── eciML1515/                   existing
│   ├── mmaripaludis/                existing
│   ├── syn6803/                     existing
│   ├── cauris_iRV973/               NEW  ─┐
│   ├── cparapsilosis_iDC1003/       NEW   │  one folder per species, same layout as the others:
│   ├── chaemulonii_draft/           NEW   │  strain.yaml, model/, media/, thermal/, dltkcat/, outputs/
│   └── cduobushaemulonii_draft/     NEW  ─┘
└── reports/                         per deliverable, unchanged
```

**What is shared** (lives once, in `src/etcgem`, `configs/`, `tools/`): the model loaders, the
thermal function, the proteome-budget constraint, the calibration and analysis code, the
reconstruction tools.

**What is strain-specific** (lives only in `strains/<name>/`): the model file, the medium, the
per-enzyme thermal parameters, the kcat/MW table, the measured curves, the `strain.yaml` that
selects the provider and sets organism values, and that strain's outputs. No strain folder contains
code that implements the method.

## 3. What maps directly

Ilgaz's models are plain SBML GEMs plus a kcat table plus a MW table — exactly the `smoment_gem`
provider (`providers.from_gem_smoment`) already used for *M. maripaludis*. The translation is
mechanical.

| Ilgaz `gem/` | `strains/<name>/` | How |
|---|---|---|
| `models/<sp>.xml` | `model/` | copy |
| `tables/kcat_reaction_<sp>.csv` + `tables/enzyme_mw_<sp>.csv` | `dltkcat/kcat_table.csv` (rxn_id, mw_kDa, kcat_s, source, group) | one converter, join on best_gene |
| `tables/thermal_topt.csv`, `tables/thermal_tm.csv` | `thermal/enzyme_thermal_params.csv` keyed `rxn_id` (Topt, Tm, Length, dCpt) | same converter; Length from the proteome; dCpt from the shared prior as for the methanogen |
| `inputs/medium_*.csv` | `media/YMS.md` + `set_medium` | copy + document |
| measured growth / respiration TPCs | `thermal/measured_tpc.csv` | copy; source commit of the Candidas pipeline recorded in `strain.yaml` |
| the species map in `gempaths.py` | four `strain.yaml` | write |

## 4. What the core needs added

Three things, none of them Candida-specific once written.

**(a) `tools/reconstruction/`.** Ilgaz's `01–07` (curated-model fetch, KOfam annotation, draft
reconstruction, RBH orthologs) and `08–15` (MW, DLKcat, Seq2Topt, Seq2Tm) build a strain's inputs
from a proteome. They are upstream of any provider and belong in a shared tools directory with
their own `requirements.txt` and `fetch_external.sh` (DLKcat, Seq2* weights, KOfam database
external and gitignored, as `DLTKcat/` is). Output: a populated `strains/<name>/` skeleton.

**(b) `etcgem transfer`.** The core runs one strain at a time. Ilgaz's design — calibrate the
global parameters on one strain, freeze, predict others — is a multi-strain experiment kind the
core does not have: a `transfer.yaml` with `calibrate_on:` and `predict:` lists, and a CLI verb.

**(c) `thermal_model: phenomenological`.** Ilgaz's Gaussian × logistic added as a third option
beside `mmrt` and `unfolding`, selectable per run like the others. Needed so the port can be
verified against his existing numbers (K1), and thereafter available as a switch on any strain.

## 5. The audits and notes

`gem/audits/` and `gem/notes/` are his record of the Candida result. They move to
`reports/candida_thermal_limit/` as `audits/` and `notes/` with a `report.qmd` + `assemble.py`
reading the core's outputs, per the report convention. Any that generalise to other strains become
experiment overlays later; that is noted, not done, in this plan.

## 6. Phased plan

Each phase is one prompt in `prompts/`, run from `.../MICROADAPT/etcGEMs`, K-series (C is the
Candidas repository's series).

**K1 — Port and verify.** The converter; four `strain.yaml`; `tools/reconstruction/` from
`gem/01–15` with paths generalised; `thermal_model: phenomenological`; `etcgem transfer`.
**Gate:** under the phenomenological form the core reproduces Ilgaz's locked numbers
(`FIG4_LOCKED.md`) to a stated tolerance. This is the one point at which the two implementations can
be compared exactly; it verifies the port and decides nothing else.

**K2 — Candida under the core's thermal form.** Same strains, `thermal_model: unfolding`, the
shared ΔCp prior, grounded proteome budget, `transfer` from *auris*. Outputs recorded beside K1's.
This is the point at which the four species are on the same footing as the other three.

**K3 — Retire the fork.** `gem/` in Candidas becomes `archive/gem_standalone/` with a README
pointing here. Anything in Candidas that needs an etc-GEM output takes it from a pinned commit of
this repository by path — never vendored back.

Everything after K3 is use of the unified framework, not part of the merge.

## 7. Risks / caveats

- **Numbers move under K2.** Expected, and the point: K1 is the regression test, K2 is the same
  strains under the shared method. Both are kept.
- **DLKcat versus DLTKcat.** Ilgaz's kcat is temperature-independent; the core's `dltkcat` module
  fits MMRT from DLTKcat's kcat(T). K1/K2 take the kcat table as-is with Topt/Tm from Seq2*, as the
  methanogen route does. Running DLTKcat on the four proteomes is a later refinement.
- **Proteome budget.** Ilgaz fitted P; the core grounds it (p_total × f_metab × σ). K2 uses
  grounded yeast values. If the a-priori budget does not bind, that is reported.
- **Two drafts.** *C. haemulonii* and *C. duobushaemulonii* are KOfam reconstructions, not curated
  models. Their `strain.yaml` says so.
- **Access.** Ilgaz needs write access to `GabYvonDurocher/etcGEMs`, branch-and-PR as before, and
  should run K1 himself: it is his pipeline being ported and he will catch what a port misses.

## 8. Open decisions

1. Keep `thermal_model: phenomenological` after K1, or remove it? Recommended: keep — a per-run
   switch costs nothing and every strain can use it.
2. Measured TPCs copied into `strains/<name>/thermal/` (self-contained, E. coli precedent) or
   referenced from the Candidas repository? Recommended: copied, source commit recorded in
   `strain.yaml`, so this repository runs without a second one present.
