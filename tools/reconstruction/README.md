# `tools/reconstruction/` — building a strain's inputs from a proteome

**These tools produce INPUTS. Nothing in this directory implements the model.** The
method — the enzyme-cost layer, the thermal layer, the proteome pool, the analyses —
lives in `src/etcgem` and only there. What this pipeline does is turn a genome's protein
sequences into the four tables a `strains/<name>/` folder needs:

| a strain needs | this pipeline's step |
|---|---|
| a metabolic model (`model/*.xml`) | 01 (fetch a curated one) or 04 + 06 (draft it from KO annotation) |
| a medium (`media/*.csv`) | hand-curated, checked by 03 |
| molecular weights and turnover numbers (`dltkcat/kcat_table.csv`) | 08 + 09 + 12 + 10 + 11 |
| per-enzyme thermal parameters (`thermal/enzyme_thermal_params.csv`) | 13 + 14 |
| all of the above, in the layout `src/etcgem` reads | `to_strain_inputs.py` |

Ported from `gem/01_ … 15_` of the standalone Candida etcGEM (the `Candidas`
repository, commit `f123bc7`). The scripts are the standalone's, with their paths
generalised: the layout and the taxon set now come from a **reconstruction config**
instead of a fixed `gempaths.py`, so the same pipeline can add any taxon. Nothing in
this directory was re-executed for K1 — the Candida strains carry the standalone's own
committed outputs, and the two deep-learning predictors need external weights that are
out of scope here.

## Layout and configuration

`reconstruction.yaml` (this directory) names the taxa and, optionally, the directories;
`paths.py` resolves them, and `common.sh` gives the shell steps the same four values.
Every Python step accepts `--config`, `--work`, `--external`, `--proteomes` and
`--out-strain`; the shell steps read `RECON_CONFIG`, `RECON_WORK`, `RECON_EXTERNAL`,
`RECON_PROTEOMES`.

```
tools/reconstruction/
├── reconstruction.yaml       taxa (model, medium, proteome, KO table, strain name) + dirs
├── paths.py                  resolves the layout for the Python steps
├── common.sh                 the same, for the shell steps
├── 01_ … 15_                 the pipeline, numbered in running order (below)
├── to_strain_inputs.py       the last step: <work>/tables -> strains/<name>/
├── fetch_external.sh         downloads external/ (NOT tracked)
├── requirements.txt          pinned Python environment
├── external/                 DLKcat, Seq2Topt/Seq2Tm weights, ESM2, KOfam   [gitignored]
└── work/<name>/              inputs/ models/ tables/ notes/                  [gitignored]
```

`external/` and `work/` are gitignored, the same convention as the vendored `DLTKcat/`.

## What must be fetched before anything runs

`bash tools/reconstruction/fetch_external.sh` (≈9 GB, most of it KOfam profiles; add
`--no-kofam` to skip that 8 GB if you are not redoing step 04). It downloads:

| into `external/` | for | used by |
|---|---|---|
| `DLKcat/` | kcat prediction from sequence + substrate SMILES | 10 |
| `Seq2Topt/` | the Topt and Tm predictors' code (v1.0.0) | 14, 15 |
| `large_model_pth/` | their two release checkpoints | 14, 15 |
| `torch_home/` | ESM2-t6-8M weights, in the layout `torch.hub` expects | 14, 15 |
| `kofam/` | KOfam HMM profiles + `ko_list` | 04, 06 |

Also needed in `PATH`: `exec_annotation` (KofamScan) for 04, `diamond` for 07.
Python dependencies are in `requirements.txt` — two tiers, the modelling tier (cobra,
pandas, numpy, scipy, biopython) and the predictor tier (torch, fair-esm, rdkit).

## The steps, in order

| step | script | what it does | needs | writes |
|---|---|---|---|---|
| 01 | `01_fetch_curated_models.sh` | download the curated SBML scaffold(s) | network | `<work>/models/*.xml` |
| 02 | `02_inspect_models.py` | report each model's namespace, compartments, biomass, exchanges, default growth — so harmonisation is decided from fact | cobra | `<work>/notes/model_report.md` |
| 03 | `03_apply_medium_fba.py MODEL MEDIUM` | check a medium map on a model: min / proxy / rich scenarios with a pooled amino-acid carbon budget. Growth must rise across the three | cobra | `<work>/tables/medium_fba_<model>.csv` |
| 04 | `04_kofam_annotate.sh [proteome:tag …]` | KofamScan KO annotation of each taxon's proteome | kofamscan, `external/kofam` | `<work>/inputs/kofam/<tag>_ko.txt` |
| 06 | `06_build_drafts.py` | project the scaffold's reaction network onto each taxon, giving every reaction a GPR from that taxon's own genes (KO→reaction, then KO→EC). Reactions with no evidence are kept but GPR-cleared. Also re-keys the scaffold itself when its published GPRs use locus tags with no sequences | cobra | `<work>/models/<taxon model>.xml`, `<work>/tables/<taxon>_evidence.csv` |
| 07 | `07_rbh_orthologs.py` | reciprocal-best-hit orthologs reference ↔ each other taxon, with percent identity (a control, not how models are built) | diamond | `<work>/tables/rbh/pid_<taxon>.tsv` |
| 08 | `08_enzyme_mw.py` | molecular weight and length of every model enzyme, from its sequence | cobra, biopython | `<work>/tables/enzyme_mw_<taxon>.csv` |
| 09 | `09_dlkcat_pairs.py` | every (reaction, enzyme, substrate) triple DLKcat must score; currency metabolites excluded | cobra | `<work>/tables/dlkcat_pairs_<taxon>.tsv`, `dlkcat_input_<taxon>.tsv`, `<work>/inputs/kegg_compounds_needed.txt` |
| 12 | `12_fetch_kegg_smiles.py` | SMILES for every substrate, from KEGG (run once, then re-run 09 to write the DLKcat inputs) | network, rdkit | `<work>/inputs/kegg_smiles.tsv` |
| 10 | `10_run_dlkcat.sh [taxon …]` | kcat per triple | torch, rdkit, `external/DLKcat` | `<work>/tables/kcat_<taxon>.tsv` |
| 11 | `11_aggregate_kcat.py` | one kcat per reaction: the maximum over its enzymes and substrates | pandas | `<work>/tables/kcat_reaction_<taxon>.csv` |
| 13 | `13_seq2topt_input.py` | the sequence table the two predictors read (≤ 2000 aa) | cobra | `<work>/tables/seq2topt_input.csv` |
| 14 | `14_run_seq2topt_seq2tm.sh` | Seq2Topt and Seq2Tm over that table, in file order, batch 4 | torch, `external/Seq2Topt` + checkpoints + ESM2 | `<work>/tables/thermal_topt.csv`, `thermal_tm.csv` |
| 15 | `15_run_seq2tm.py` | Seq2Tm over a whole proteome, or at batch = 1 (the padding audit) | torch | as named on the command line |
| — | `to_strain_inputs.py --species TAXON` | assemble `strains/<name>/`: model, medium, `dltkcat/kcat_table.csv`, `thermal/enzyme_thermal_params.csv`, `thermal/measured_tpc.csv` | cobra, pandas | `strains/<name>/` |

Step 05 does not exist (it did not in the standalone either). Steps 16–26 of the
standalone are **not** ported: those are the model and its analyses, and they are
`src/etcgem` here.

### Two steps whose output depends on how they are run

* **14 (and 15 at `--batch-size 4`).** Seq2Topt/Seq2Tm feed padded batches to the model
  with no attention mask, so a protein's prediction depends on which proteins share its
  batch. The predictions shipped with the Candida strains were made at batch = 4 in the
  file order of `seq2topt_input.csv`; re-running on a re-ordered or subsetted input gives
  different numbers. Do not sort or filter the input. (The standalone measured the size of
  this effect and showed it does not bias the between-species comparison; see its
  `gem/FIG4_LOCKED.md`.)
* **04.** KofamScan's assignments depend on the KOfam release. The Candida KO tables were
  produced against the release current on 2026-09-02; regenerate only against the same
  profiles.

## Adding a taxon

1. Put its proteome (FASTA, or a UniProt TSV with `Gene Names (ordered locus)` and
   `Sequence`) in `--proteomes`.
2. Add an entry under `taxa:` in `reconstruction.yaml`: `model`, `medium`, `proteome`,
   `kofam` (omit if it has a curated model with usable GPRs), `strain`.
3. Run 04 → 06 (draft the model), then 08, 09, 12, 09 again, 10, 11 (kcat and MW), then
   13, 14 (Topt and Tm).
4. Write its medium map and check it with 03.
5. `to_strain_inputs.py --species <taxon>` to populate `strains/<name>/`, then write that
   strain's `strain.yaml` (copy one of the Candida ones and change the organism block).

That is the whole procedure. Everything after it is `etcgem`.
