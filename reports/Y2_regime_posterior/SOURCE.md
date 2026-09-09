# Y2 — what was obtained, from where

_Named `SOURCE.md`, not `PROVENANCE.md`: `scripts/stamp_reports.py` owns that filename in every
report directory and would overwrite this._

## The posterior

| | |
|---|---|
| Zenodo record | **3996543**, DOI **10.5281/zenodo.3996543** (concept DOI 10.5281/zenodo.3686995) |
| Title | *Computed results for Bayesian genome scale modelling temperature effect on yeast metabolism* |
| Version | **2.0**, published 2020-02-25; it is the latest — the concept DOI resolves to this record |
| File | `results.tar.gz`, **2 356 820 868 bytes**, 23 files |
| md5 | `9367d7edcea41ecd50d9fb399f064582` — **matches the md5 Zenodo publishes** |
| sha256 | `ca6097c65f394443f394542c4654e0315b78479d2c76e21c3a0ef3ea1806a553` |

One member is extracted and used:

| | |
|---|---|
| Path in archive | `results/smcabc_gem_three_conditions_save_all_particles.pkl` |
| Size | 702 024 454 bytes |
| md5 | `bea1639e7a5c9ba8d0584b240fe2f113` |
| sha256 | `4f96519aa4954a92caadf4c941c7d87d4a98f288e106173e4bd44dff71c9ecf4` |

It is a pickle of their `abc_etc.SMCABC` object, written by
`code/gem_smcabc_at_three_conditions.py`. It carries **168 generations**, **21 504 simulations**
and a final ε of **−0.9026** — the paper's own "21504 parameter sets" (Fig. 2d) and its ε = −0.9
stopping rule. `.population_t0` is the Prior (n = 128) and `.population` the Posterior (n = 100),
over **2292 parameters = 764 enzymes × {Tm, Topt, ΔCp‡}**.

The archive and the extracted pickle live in this session's scratch directory, outside the
repository. Nothing here is committed; every script takes `--results <extracted>` and
`--bayesiangem <clone>`.

## The model and the code

Y1's read-only clone of `SysBioChalmers/BayesianGEM`, still at **`a68307e`** (2020-11-22,
GPL-3.0). The three files Y2 reads, unchanged since Y1:

```
3baacd44ac9c5e4f5e436710c64d05e299ff7b100449fa46a74764099277102a  models/ecYeast7_v1.0_batch_minimal_thermo.mat
87298b02bc752f4a8363729b94d327693dbc3efcb233fff7ecbc6f3fd2cd1609  data/model_enzyme_params.csv
6e1b9c1f184cee411ce2dd32fe43e076e7a28c3e6d31fe85dcd8532111fe0794  code/etcpy/etc.py
```

`git status` in the clone is **not** empty — three validation figures in `validate_smc_abc/`
report as modified. Nothing modified them; the deposit contains three pairs of filenames differing
only in case, which a case-insensitive filesystem cannot hold. `DECISIONS.md` §1 has the
demonstration. `git status models data code` is empty.

## Environment

`/Users/…/MICROADAPT/etcGEMs/.venv/bin/python` — the primary checkout's existing venv, borrowed
read-only: Python 3.9, cobra 0.31.1, numpy 2.0.2, pandas 2.3.3, Gurobi. `../etcGEMs-venv`, which
P7 was rebuilding, was **not used and not touched**; it never appeared on `PATH`.

## What Y2 touched, and what it did not

Every script here takes `--bayesiangem <clone>` and `--results <extracted>` explicitly and writes
only into `reports/Y2_regime_posterior/`, plus the one deliberate re-run of Y1's own
`task_c_regime_test.py`, which rewrote `reports/Y1_yeast_audit/task_c_*.csv` **byte-identically**
(that is the reproduction check, and `git status` there was empty afterwards).

**Nothing under `../etcGEMs` was written.** Its only use was `sys.executable` — recorded as
`/Users/…/etcGEMs/.venv/bin/python`, `sys.prefix` the same — and `git -C ../etcGEMs status` shows
only P7's own untracked files. Many files there do have recent modification times; those are P7's,
from its branch switch (`p6/convergence` → `p7/walkers`) and its run, not Y2's.

**`../etcGEMs-venv` was not used.** It never appeared on `PATH`, and the ~18 000 files with recent
modification times inside it are P7 rebuilding it, as its prompt said it would.

**The BayesianGEM clone was not written.** `git status models data code` in it is empty and the
three checksums above are unchanged from Y1.
