# Y1 — what was obtained, from where

_Named `SOURCE.md`, not `PROVENANCE.md`: `scripts/stamp_reports.py` owns that filename in every report directory and would overwrite this._

## The deposit

| | |
|---|---|
| Paper | Li G., Hu Y., Zrimec J., Luo H., Wang H., Zelezniak A., Ji B., Nielsen J. (2021) *Bayesian genome scale modelling identifies thermal determinants of yeast metabolism.* **Nature Communications** 12:190 |
| Code and models | `https://github.com/SysBioChalmers/BayesianGEM` |
| Commit obtained | `a68307ecd9530d7d78a47f80c9e0c018791b8d8a`, 2020-11-22, "Update README.md" (repository HEAD) |
| Licence | GPL-3.0 |
| Pre-computed SMC-ABC results | Zenodo `https://zenodo.org/record/3996543` (`results.tar.gz`) — **not downloaded**; nothing in Y1 needs the posterior samples, and PART D reads the published figures |

The clone is **read-only** and lives outside the repository, in this session's scratch directory.
Nothing in this report writes to it. Everything committed here was produced by the scripts in
this directory, which take the clone's path as an argument.

## What is in the deposit

* `models/ecYeast7_v1.0_batch.mat` — the plain ecYeast7 GECKO batch model (glucose uptake capped
  at 1, protein pool 0.0786).
* `models/ecYeast7_v1.0_batch_minimal_thermo.mat` — the **aerobic** model their thermal
  simulations run on: minimal medium, glucose unlimited, protein pool 0.17866.
* `models/ecYeast7_v1.0_batch_minimal_thermo_anaerobic.mat` — the same with oxygen uptake shut.
* `models/aerobic.pkl`, `models/anaerobic.pkl`, `models/models.pkl` — cobra 0.15.3 pickles of the
  above. **These do not load under cobra 0.31** (see `DECISIONS.md` §1).
* `code/etcpy/etc.py` — their thermal layer. **Python, not MATLAB**, operating on a cobra model.
* `data/model_enzyme_params.csv` — the prior thermal parameters for all 764 enzymes: `Topt`,
  `Topt_std`, `Length`, `Tm`, `Tm_std`, `T90`, `dCpt`, `dCpt_std`.
* `data/ExpGrowth.tsv`, `data/Chemostat_exp_data.txt` — the measured aerobic/anaerobic batch
  growth curves and chemostat fluxes they calibrate against.

## Environment

Run with this repository's `.venv` (Python 3.9, cobra 0.31, Gurobi). Their stated environment was
Python 3.6.7 with cobra 0.15.3 and Gurobi 8.0.
