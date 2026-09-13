# P17 — this directory is CURATED

**The complete P17 artefact set is NOT here. It is preserved, in full and unmodified, on the local
branch `codex/p17-inactive-prior` at `ef1961bfc4e26a9e69eb51fe8d0b8dbad109e997`, checked out at
`../etcGEMs-p17-archive` (relocated from `/private/tmp/etcGEMs-p17` by T1 on 2026-09-13, because
`/private/tmp` is cleared on reboot), which is deliberately never pushed.**

## What is here, and what is not

| | files | size |
|---|---:|---:|
| **in this commit** (documents, scripts, decisions, small results) | **580** | **15.7 MB** |
| excluded (evidence blobs) | 1365 | 2634 MB |
| full P17 branch, tracked | 3,929 | 2,962 MB |

Included: every `.md`, `.py`, `.json`, `.csv`, `.yaml`, `.yml`, `.txt`, `.toml`, `.cfg`, `.png`,
`.svg` and `.pdf` — reports, scripts, DECISIONS, manifests, per-run summaries and figures. **None
of these exceeds 5 MB**; the largest is a few hundred kB.

Excluded, by kind: **486 `.save` dynesty checkpoints (1,511 MB)**, **775 `.npz` array archives
(857 MB)**, **72 `.log` files (265 MB)**, plus `.pyc` caches and three `.claim` process-lock files
of 4–74 bytes. These are re-derivable run evidence, not results.

## Why, and the one hard constraint

`reports/P17_inactive_prior/unif_benchmark.log` is **109,809,818 bytes**, above GitHub's 100 MiB
per-file limit, and no LFS is configured. That file alone makes the full branch unpushable. Rather
than rewrite history or migrate to LFS, the PI's decision was to push a curated commit and keep the
full branch locally.

Files over 5 MB that were excluded (named individually):

| path | MB |
|---|---:|
| `reports/P17_inactive_prior/unif_benchmark.log` | 104.7 |
| `reports/P17_inactive_prior/global_coordinate_replicates.log` | 82.3 |
| `reports/P17_inactive_prior/global_coordinate_benchmark.log` | 18.9 |
| `reports/P17_inactive_prior/positive_control.log` | 8.9 |
| `reports/P17_inactive_prior/independence_trace_oracle/spike_17752/checkpoint.save` | 8.5 |
| `reports/P17_inactive_prior/controls_s15_spike.log` | 7.7 |
| `reports/P17_inactive_prior/hybrid_controls/spike_17754/checkpoint.save` | 7.4 |
| `reports/P17_inactive_prior/hybrid_controls/spike_17752/checkpoint.save` | 7.4 |
| `reports/P17_inactive_prior/hybrid_controls/spike_17753/checkpoint.save` | 7.3 |
| `reports/P17_inactive_prior/hybrid_controls/spike_17751/checkpoint.save` | 7.3 |
| `reports/P17_inactive_prior/independence_laplace/spike_17754/checkpoint.save` | 7.3 |
| `reports/P17_inactive_prior/independence_oracle/spike_17754/checkpoint.save` | 7.2 |
| `reports/P17_inactive_prior/independence_oracle/spike_17752/checkpoint.save` | 7.2 |
| `reports/P17_inactive_prior/independence_laplace/spike_17752/checkpoint.save` | 7.2 |
| `reports/P17_inactive_prior/hybrid_controls/spike_17755/checkpoint.save` | 7.2 |
| `reports/P17_inactive_prior/independence_laplace/spike_17755/checkpoint.save` | 7.2 |
| `reports/P17_inactive_prior/independence_oracle/spike_17755/checkpoint.save` | 7.2 |
| `reports/P17_inactive_prior/independence_laplace/spike_17751/checkpoint.save` | 7.2 |
| `reports/P17_inactive_prior/independence_oracle/spike_17751/checkpoint.save` | 7.2 |
| `reports/P17_inactive_prior/independence_diagonal/spike_17754/checkpoint.save` | 7.0 |
| `reports/P17_inactive_prior/independence_laplace/spike_17753/checkpoint.save` | 7.0 |
| `reports/P17_inactive_prior/independence_oracle/spike_17753/checkpoint.save` | 7.0 |
| `reports/P17_inactive_prior/independence_diagonal/spike_17753/checkpoint.save` | 6.9 |
| `reports/P17_inactive_prior/independence_diagonal/spike_17755/checkpoint.save` | 6.5 |
| `reports/P17_inactive_prior/independence_trace_pilot/spike_17752/checkpoint.save` | 6.3 |
| `reports/P17_inactive_prior/independence_controls/spike_17751/checkpoint.save` | 6.3 |
| `reports/P17_inactive_prior/occupancy_smooth_0_17705/checkpoint.save` | 6.2 |
| `reports/P17_inactive_prior/occupancy_smooth_0_17703/checkpoint.save` | 6.1 |
| `reports/P17_inactive_prior/occupancy_smooth_0_17702/checkpoint.save` | 6.1 |
| `reports/P17_inactive_prior/occupancy_smooth_-13.5_17702/checkpoint.save` | 6.1 |
| `reports/P17_inactive_prior/occupancy_smooth_-13.5_17704/checkpoint.save` | 6.0 |
| `reports/P17_inactive_prior/occupancy_smooth_0_17701/checkpoint.save` | 6.0 |
| `reports/P17_inactive_prior/occupancy_smooth_-13.5_17703/checkpoint.save` | 6.0 |
| `reports/P17_inactive_prior/occupancy_smooth_-13.5_17705/checkpoint.save` | 6.0 |
| `reports/P17_inactive_prior/occupancy_smooth_-13.5_17701/checkpoint.save` | 6.0 |
| `reports/P17_inactive_prior/occupancy_smooth_0_17704/checkpoint.save` | 6.0 |
| `reports/P17_inactive_prior/independence_diagonal/spike_17751/checkpoint.save` | 6.0 |
| `reports/P17_inactive_prior/independence_diagonal/spike_17752/checkpoint.save` | 5.8 |
| `reports/P17_inactive_prior/independence_controls/spike_17754/checkpoint.save` | 5.8 |
| `reports/P17_inactive_prior/independence_controls/spike_17755/checkpoint.save` | 5.8 |
| `reports/P17_inactive_prior/independence_controls/smooth_17755/checkpoint.save` | 5.8 |
| `reports/P17_inactive_prior/independence_controls/spike_17753/checkpoint.save` | 5.8 |
| `reports/P17_inactive_prior/independence_controls/smooth_17752/checkpoint.save` | 5.8 |
| `reports/P17_inactive_prior/spike_plain_p1_t0_s3_17001_unif.save` | 5.8 |
| `reports/P17_inactive_prior/independence_controls/smooth_17753/checkpoint.save` | 5.7 |
| `reports/P17_inactive_prior/independence_controls/smooth_17751/checkpoint.save` | 5.7 |
| `strains/eciML1515/outputs/calibration_configD_NLDM_recipe_P16_reduced/dynesty_red2.save` | 5.7 |
| `reports/P17_inactive_prior/independence_controls/smooth_17754/checkpoint.save` | 5.7 |
| `reports/P17_inactive_prior/independence_controls/spike_17752/checkpoint.save` | 5.4 |
| `reports/P17_inactive_prior/occupancy_flat_-13.5_17705/checkpoint.save` | 5.3 |
| `reports/P17_inactive_prior/occupancy_flat_-13.5_17702/checkpoint.save` | 5.3 |
| `reports/P17_inactive_prior/occupancy_flat_-13.5_17703/checkpoint.save` | 5.2 |
| `reports/P17_inactive_prior/occupancy_flat_0_17701/checkpoint.save` | 5.2 |
| `reports/P17_inactive_prior/occupancy_flat_0_17702/checkpoint.save` | 5.2 |
| `reports/P17_inactive_prior/occupancy_flat_-13.5_17704/checkpoint.save` | 5.1 |
| `reports/P17_inactive_prior/occupancy_flat_-13.5_17701/checkpoint.save` | 5.1 |
| `reports/P17_inactive_prior/occupancy_flat_0_17703/checkpoint.save` | 5.1 |

## The hashes remain the authority

`closure_manifest.json` is **copied unchanged, never regenerated**. It carries the SHA-256 and byte
count of **all 1,905** P17 files, including every excluded one, so any file in the archive can be
verified against this repository's record. `closure_artifact_inventory.json` is likewise unchanged.

At curation, **549 of the files copied here were verified against `closure_manifest.json` and all
549 matched; none mismatched.** The remaining 31 copied files lie outside the manifest's scope
(`docs/`, `prompts/`, `reports/P16_reduced/`, and the manifest itself, which excludes its own hash).

## Commit hashes elsewhere in the documentation remain valid

`DECISIONS.md`, `docs/CLOSURE_VERIFICATION_2026-09-13.md` and `docs/INTEGRATION_STATE.md` reference
commits on `codex/p17-inactive-prior`. Those references are **to that local branch** and remain
valid there. They do not resolve in a clone of `origin/main`, by design.

## One thing not excluded

The five `strains/eciML1515/outputs/calibration_configD_NLDM_recipe_P16_reduced/*red2*` files —
including `dynesty_red2.save` at 5.7 MB — appear in the excluded list above but **are in the
repository**: they were committed from the primary tree in R3 TASK 1, at byte-identical hashes,
before this curation ran.

_Written by R3, 2026-09-13._
