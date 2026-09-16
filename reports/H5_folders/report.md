# H5 — five sibling folders reduced to two, with the archive branch kept and proved

_2026-09-16. Filesystem and git hygiene only: no fits, no science, no model or config change, no
commit to any report's content. Run from the primary checkout on `main`._

## Before and after

| folder | what it is | before | action | after |
|---|---|---:|---|---:|
| `etcGEMs` | the repository, on `main` | 5.8 G | **keep** | 5.8 G |
| `etcGEMs-venv` | the Python environment every prompt calls `../etcGEMs-venv/bin/python` | 611 M | **keep — never delete** | 611 M |
| `etcGEMs-p17-archive` | checkout of the archive branch | 2.9 G | worktree removed; **branch kept** | — |
| `etcGEMs-work` | second tree, detached at `main` | 466 M | worktree removed | — |
| `etcGEMs-work-salvage` | superseded deck render + intermediates + obsolete marker | 664 K | deleted after item-by-item check | — |

**Recovered: 3,437 MiB (~3.4 GB).** End state: **two folders**, one worktree, two branches.

## The distinction this turned on

For the P17 archive the **branch** is irreplaceable and the **checkout** is one command. The branch
is local-only and could not be pushed — one log in it is 109,809,818 bytes, above GitHub's
file-size limit — and it is not recreatable from anything. The objects, however, live in the
**primary repository's own object store**; the worktree's `.git` was a 141-byte pointer. So
removing the checkout recovers 2.9 GB of OneDrive sync and loses nothing **provided the branch
survives**.

## The proof, taken in three stages

The selection rule was fixed before any hashing: the **largest** tracked blob on the branch, the
**smallest**, and `reports/P17_inactive_prior/report.md`, plus the manifest itself.

| artefact | (1) from the worktree | (2) from the branch, `git show` | (3) from a recreated checkout |
|---|---|---|---|
| `closure_manifest.json` | `b9e80eab215bddd5…` | **match** | **match** |
| `unif_benchmark.log` (109,809,818 B) | `aa91cc4846a2407c…` | **match** | **match** |
| `finish_third.log` (0 B) | `e3b0c44298fc1c14…` | **match** | **match** |
| `report.md` | `510b8f262744b1c1…` | **match** | **match** |
| manifest file count | 1,905 | — | 1,905 |

Stage (2) was taken **before** anything was removed and is the evidence that the objects are not
in the worktree. Stage (3) recreated the checkout from the branch after removal: all four matched
again and the big log materialised at **104.7 MiB**. The verify checkout was then removed.
Hashes are recorded in `pre_removal_hashes.json`.

**One number corrected.** The recreated checkout holds **3,929** tracked files, not the 1,905 the
manifest lists. Both are right and they count different things: the branch is a **full repository
checkout** at `ef1961b`, while the manifest enumerates P17's own artefact set — and there are
**1,906** tracked files under `reports/P17_inactive_prior/`, the manifest being the one that does
not list itself.

## The commands that bring things back

```sh
git worktree add ../etcGEMs-p17-archive codex/p17-inactive-prior   # the archive
git worktree add --detach ../etcGEMs-work main                     # a second tree for parallel runs
git worktree remove <path>                                         # when finished — never rm -rf
```

## The salvage folder, checked before deletion

| item | check | verdict |
|---|---|---|
| `deck.pdf` (615,044 B, 11 Sep) | main's `reports/ecoli_deck/_output/deck.pdf` is 1,580,218 B and current at 62 pages | superseded |
| `deck.tex`, `deck.nav`, `deck.snm` | quarto/Beamer intermediates of `deck.qmd` | regenerable by `quarto render` |
| `T2_REDIRECT_status.json` | points at `../etcGEMs-t2`, removed by H2; main tracks the real `status.json` at that path (403 B, `task6_done`) | obsolete |

Every item superseded or regenerable, so the folder was deleted. Nothing in it was unique.

## What was deliberately not touched

The **21 untracked artefacts** in the primary tree (`brenda_sdh.html`, two config experiments,
several `transfer_*` output directories, eight `.gitkeep` placeholders, a `dynesty_proof.save` and
the H5 prompt itself) are a separate decision and were listed, not deleted. `../etcGEMs-venv` was
never touched.
