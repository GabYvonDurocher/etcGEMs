# R3 — integrating P16, P17, the deck and Q1 into main

_2026-09-13. Final `origin/main`: **`64393edede223feebbcebbf4554d548f38e03cf9`**._

**Everything since the P15 merge is now on main.** Four bodies of work, five PRs (one because of a
mistake of mine), no `--force`, no rewritten branch, no deleted lock file, nothing discarded before
a fresh clone proved it landed.

---

## The state before

`origin/main` and local `main` were both `dc5b4cc`, unchanged from `INTEGRATION_STATE.md` — so the
plan was current and the STOP condition did not fire. All three worktrees existed; the P17 worktree
was clean at `ef1961b` with `closure_manifest.json` present.

| branch | head | ahead |
|---|---|---:|
| `p16/reduced` | `191b4b0` | 6 |
| `codex/p17-inactive-prior` | `ef1961b` | 36 |
| `e2/deck` (local) | `0215a16` | 26 |
| `origin/e2/deck` | `bc356e3` | 20 |
| `q1/n0-check` | `b163bad` | 25 |

Tracked sizes: main **303.4 MB** (1,962 files); P17 tip **2,961.6 MB** (3,929 files).

The primary tree had **34** dirty paths, not the documented 32 — the extra two were
`reports/R3_integration/` and the R3 prompt, both created by this task.

## TASK 1 — the primary tree's evidence, committed with its differences on record

Every dirty file was SHA-256'd against P17's copy at the same path: **23 identical, 3 different,
7 absent**. All were committed to `p16/reduced` as `b8b181b`.

The three differences were inspected rather than merely recorded:

- **`docs/OPEN_ITEMS.md`** — the primary's content is a **strict subset** of P17's (0 lines unique
  to it, 21 unique to P17). Not a real divergence.
- **The two `resolved_config.yaml`** — P17's are byte-identical to main's; the primary's add exactly
  `rescale_pool_row: false`. That is the **§4 stale-dump artefact**, stale since N2's hotfix and
  reappearing after every gate battery. Committing the regenerated version **clears it**.

`prompts/E6_deck_bring_current_prompt.md` was marked **SUPERSEDED** in its header and kept.

## TASK 2 — the curated P17 commit

**580 files, 15.7 MB.** Every `.md`, `.py`, `.json`, `.csv`, `.yaml`, `.yml`, `.txt`, `.toml`,
`.cfg`, `.png`, `.svg`, `.pdf` P17 added. **549 of them fall inside `closure_manifest.json` and all
549 matched; none mismatched.** The manifest and `closure_artifact_inventory.json` were copied
**unchanged**. P17 touched no `src/` and no `scripts/` — verified, the diff is empty.

**Excluded: 1,365 files, 2,634 MB** — 486 `.save` checkpoints (1,511 MB), 775 `.npz` (857 MB), 72
logs (265 MB), `.pyc` caches, three 4–74-byte `.claim` locks. The **57 excluded files over 5 MB** are
named individually in `reports/P17_inactive_prior/ARCHIVE.md`.

**A deviation from the prompt's literal filter, reported rather than buried.** "Any file of any type
under 5 MB" would admit **1,888 files totalling 2,101 MB**, because the checkpoints sit *just* under
the limit — main would go to ~2.4 GB, contradicting the same prompt's expectation of "well under
100 MB". The extension list is used as the selector instead, with the 5 MB limit kept as a
never-binding second check. Details in DECISIONS D2.

## TASK 3 — E6 did not duplicate E5

| | E5 `bc356e3` | E6 `0215a16` |
|---|---|---|
| slides | 49 | **56** |
| duplicated titles / bullets | — | **none / none** |

E6 **removed four** slides (the P15-crash narrative) and **added eleven** (the P16 reduced-posterior
story, including "Run 1 assigns about half its weight to very low growth" and "Why separate
parameter medians give a misleading model"). The `E5 carry-forward` commit **edited deck.qmd in
place**, 42 lines, rather than appending. **No duplication item for the next deck pass.**

Deck renders at `0215a16`: **59 pages**, verified in a temporary worktree so `../etcGEMs-work` stayed
clean. Reconciliation set (files touched by both E6 and Q1): `docs/OPEN_ITEMS.md`,
`reports/ecoli_deck/DECISIONS.md`, `reports/report_status.yaml`.

## TASK 4 — the merges, and one mistake

| PR | branch → base | merge | conflicts |
|---|---|---|---|
| **#34** | `p16/reduced` → main | `96d11d1` | none |
| **#35** | `p17/curated` → main | `32160f2` | none |
| **#31** | `e2/deck` → main | `99279a4` | `OPEN_ITEMS.md` — **both sides kept** |
| **#33** | `q1/n0-check` → **`e2/deck`** | `4e16729` | `ecoli_deck/DECISIONS.md` — **both sides kept** |
| **#36** | `e2/deck` → main | **`64393ed`** | none |

**The mistake: PR #33's base was `e2/deck`, not `main`, and I merged it without checking.** Q1 went
into the deck branch *after* the deck had already reached main, so main did not receive it. I caught
it only because the post-merge content check reported `reports/Q1_n0_check/report.md` MISSING.
Nothing was lost; PR #36 brought the deck branch to main again and merged cleanly. **Read
`baseRefName` before merging a PR you did not open.** DECISIONS D4.

**Conflicts, resolved by keeping both sides, never choosing one wholesale:**

- `docs/OPEN_ITEMS.md` (#31) — both sides added a **§0d**. Main's is the 90-line P16/P17 "Next
  steps"; the deck's is a 21-line "E6 deck snapshot". Both kept; the deck's **renumbered §0d → §0e**
  with a dated note recording that it is a *snapshot* stating seed 2 as pending, true when written.
- `reports/ecoli_deck/DECISIONS.md` (#33) — E6's 114-line D24 block and Q1's 17-line CUE-caveat
  note, both appended at the same place. **Both kept verbatim**, E6's first, with an HTML comment
  recording the merge.
- `report_status.yaml` and `evidence.csv` auto-merged additively — Q1 touches item 1.9 while P16/P17
  touch the R1–R4 and closure items.

**Stamps were regenerated with `scripts/stamp_reports.py` at every merge; no hash was hand-written.**
Q1 does not touch `deck.qmd`, so the 59-page render remains valid; it was re-verified on final main.

## TASK 5 — gates and a fresh clone

**Gates on merged main: K1 79/79, P1 60/60**, all three `tpc` runs rc=0.

A fresh clone of `origin/main` at `64393ed`:

- every required path present — P16 audit, P17 `report.md` / `current_gate.md` / `DECISIONS.md` /
  `closure_manifest.json` / `ARCHIVE.md`, all five `docs/`, the deck PDF, `reports/Q1_n0_check/`;
- **549 P17 files matched `closure_manifest.json`, 0 mismatched**; 1,356 in the manifest and
  deliberately absent; one present-but-unlisted file, `PROVENANCE.md`, generated by the stamp script
  after closure;
- deck **59 pages**;
- **both gates pass from the clone**: 79/79, 60/60;
- tracked size **337.5 MB / 2,619 files**, against main's previous 303.4 MB — an increase of
  **34.1 MB** for all four bodies of work.

The clone was then deleted.

## TASK 6 — branches and worktrees

Deleted, non-force, local and origin: `p16/reduced`, `p17/curated`, `e2/deck`, `q1/n0-check`.
`e2/deck` required detaching `../etcGEMs-work` first, which TASK 6 asked for anyway; that tree is now
**detached at `64393ed`**. The two temporary worktrees R3 created (`/tmp/wt-deck`, `/tmp/wt-q1`) were
removed.

**`codex/p17-inactive-prior` is retained at `ef1961b`, local only — confirmed absent from origin.**
`/private/tmp/etcGEMs-p17` is kept.

### The `/tmp` question, answered precisely

**`/private/tmp` IS cleared** — `com.apple.tmp_cleaner.plist` is present — and the worktree has
survived only because **this machine has not rebooted in 58 days**.

**But the evidence is not at risk, and the distinction matters.** The worktree's `.git` is a
**141-byte pointer file**; **every P17 blob lives in the primary repository's 1.9 GB object store**
in OneDrive — the 109,809,818-byte `unif_benchmark.log` reads straight from it with the worktree
playing no part — and the branch ref is in the primary `.git/refs/heads/`. A reboot would cost a
**2.9 GB checkout, recreatable with one `git worktree add`**.

Recommended, not acted on: `git worktree move /private/tmp/etcGEMs-p17 ../etcGEMs-p17-archive`.
Recorded as OPEN_ITEMS **1.28**.

## Sizes

| | tracked | files |
|---|---:|---:|
| main before | 303.4 MB | 1,962 |
| **main after** | **337.5 MB** | **2,619** |
| P17 tip (never pushed) | 2,961.6 MB | 3,929 |

## What this does NOT license

Integration moved **no scientific conclusion**. P16's two runs still do not establish
reproducibility — fourteen of fifteen marginals fail and the inactive `f_metab` CDF means are
0.319120 and 0.393715 against 0.5. **P17 remains closed negatively by PI decision, not by passing
its gate.** R1 is open, R3 provisional, R4 untouched. `docs/TARGET_REVISION_SPEC.md` awaits PI
approval (item 1.27), and no revised fit launches before that and the full validation protocol.
