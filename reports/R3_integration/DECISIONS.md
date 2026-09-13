# R3 — decisions, from the first judgement call

## D0 — the state re-verified; the plan is not stale

`git fetch origin --prune` succeeded and pruned nine already-merged p7–p15 remotes. **`origin/main`
and local `main` are both `dc5b4cc`**, unchanged from INTEGRATION_STATE, so the plan is current and
the STOP condition ("origin/main has moved") does not fire. All three worktrees exist on disk;
`/private/tmp/etcGEMs-p17` is **clean at `ef1961b`** with `closure_manifest.json` present.

Branch heads matched INTEGRATION_STATE exactly: `p16/reduced` 191b4b0 (+6), `codex/p17-inactive-prior`
ef1961b (+36), `e2/deck` 0215a16 (+26), `origin/e2/deck` bc356e3 (+20), `q1/n0-check` b163bad (+25).

**One difference from the prompt's table, and it is mine:** the primary tree has **34** dirty paths,
not 32 — the extra two are `reports/R3_integration/` and `prompts/R3_…_prompt.md`, both created by
this task. The documented 32 are exactly as listed.

Tracked sizes: `origin/main` **303.4 MB** (1,962 files); `ef1961b` **2,961.6 MB** (3,929 files).

## D1 — the three differing files, inspected rather than merely recorded

The prompt says to commit the primary's version without deciding which is right. Done — but two of
the three turn out to have an explanation worth stating, because one of them **closes a standing
§4 hazard**.

- **`docs/OPEN_ITEMS.md`** — the primary's content is a **strict subset** of P17's: 0 lines unique
  to the primary, 21 unique to P17 (the closure note and the RIGOUR protocol line). Not a genuine
  divergence; the TASK 4 step-2 merge takes P17's superset cleanly.
- **The two `strains/cauris_iRV973/.../resolved_config.yaml`** — P17's copies are **byte-identical
  to main's**; the primary's differ by exactly one added key, **`rescale_pool_row: false`**. That is
  the long-standing stale-dump artefact recorded in OPEN_ITEMS §4, which has reappeared after every
  gate battery since N2's hotfix because no TASK 0 ever re-ran those two FBA dumps. §4 says to
  "clear it in a housekeeping commit that says so". Committing the primary's regenerated version
  **does exactly that**, and changes no gate number — K1 compares values, not this file.

## D2 — the curation filter: a deliberate, reported deviation from the prompt's literal wording

The prompt admits a file if it has one of twelve document extensions **or** is "any file of any type
under 5 MB". **Applied literally, the second clause admits 1,888 files totalling 2,101 MB**, because
P17's checkpoints are individually *just under* the limit — 486 `.save` at 1,511 MB and 775 `.npz`
at 857 MB. Main would go from 303 MB to about **2.4 GB**, contradicting the same prompt's TASK 5
expectation of "the curated P17 (**well under 100 MB**)".

**Resolution: the extension list is the selector; the 5 MB limit is kept as a second check that
never binds** (no file with a listed extension exceeds it — the largest is a few hundred kB). That
yields **580 files, 15.7 MB**. The two clauses only ever disagree on blobs, which is what the
curation exists to drop.

Recorded as a deviation rather than silently applied, because the alternative reading is defensible
on the words and indefensible on the purpose.

**Verification:** 549 of the copied files fall inside `closure_manifest.json`'s scope and **all 549
matched their recorded SHA-256; none mismatched**. The other 31 lie outside it (`docs/`, `prompts/`,
`reports/P16_reduced/`, and the manifest, which excludes its own hash). The manifest and
`closure_artifact_inventory.json` are **copied unchanged, never regenerated**.

**P17 touched no `src/` and no `scripts/`** — `git diff --stat 191b4b0 ef1961b -- src/ scripts/` is
empty, as the prompt anticipated.

## D3 — E6 did NOT duplicate E5. The inspection, slide by slide.

The concern was that `E6: E5 carry-forward` might have re-applied edits E5 had already made. **It
did not.**

| | E5 `bc356e3` | E6 `0215a16` |
|---|---|---|
| level-2 slides | 49 | **56** |
| deck.qmd lines | 422 | 486 |
| duplicated slide titles | none | **none** |
| duplicated bullet lines | none | **none** |

E6 **removed four slides** — "The posterior: the run, and how it failed", "…what the crash
localised", "What that does and does not mean", "Settled · failed · needs measurement" — the P15
crash narrative, and **added eleven**, the P16 reduced-posterior story: "run 1 converged", "the
stopping and reproducibility rules", "what the reduction assumes", "**Run 1 assigns about half its
weight to very low growth**", "**Why separate parameter medians give a misleading model**", "the
infeasibility exemption", "why a converged posterior can favour poor predictions", and four on next
steps.

The `E5 carry-forward` commit itself changed only 3 files and **edited deck.qmd lines in place**
(42 lines, ~21 replaced) rather than appending — e.g. replacing the CUE slide's "Flat from 25 to
40 °C, then a cliff" with the conversion-caveat wording. **So E6 detected E5's work and revised it.
There is no duplication item for the next deck pass.**

**Render at `0215a16`: succeeds, 59 pages** (E5 was 52). Verified in a temporary detached worktree
at `/tmp/wt-deck` rather than in `../etcGEMs-work`, so that tree stays clean; the re-render is
1,569,596 bytes against the committed 1,569,597 — a one-byte PDF-identifier difference.

*(A first attempt failed only because I copied the deck directory outside the repository, breaking
its `../ecoli_tpc/assets/…` relative paths. That was my sandboxing, not the deck.)*

**The Q1/E6 reconciliation set** — files touched by both, against the common E5 base:
`docs/OPEN_ITEMS.md`, `reports/ecoli_deck/DECISIONS.md`, `reports/report_status.yaml`.
`reports/synthesis/evidence.csv` is touched by **Q1 only**, so it does not conflict *between those
two* — though it will against the new main, which P16 and P17 have both changed.

## D4 — a mistake of mine: PR #33's base was `e2/deck`, not `main`, and I merged it without checking

PR #33 (`q1/n0-check`) already existed. I merged it without reading its `baseRefName`. **Its base was
`e2/deck`**, so the merge placed Q1 *inside the deck branch* — and PR #31 had already carried the
deck to main, so **main did not receive Q1**. I only noticed because the post-merge check for
`reports/Q1_n0_check/report.md` came back MISSING.

**Nothing was lost.** Q1's merge commit `4e16729` was on `origin/e2/deck`, and the fix was to open
**PR #36 (`e2/deck` → main)**, which merged cleanly with **no conflicts** and brought Q1 and the Q1
reconciliation onto main at `64393ed`.

**The lesson, and it is not subtle:** the task said "merge, in order, each as its own PR". I treated
an existing PR as if it were the PR I would have opened, without verifying that it targeted the
branch I assumed. **Read `baseRefName` before merging any PR you did not open.**

## D5 — the archive worktree: the risk is real but far smaller than the prompt assumes

The prompt asks whether `/private/tmp` is cleared on reboot and to say so prominently. **It is**:
`/System/Library/LaunchDaemons/com.apple.tmp_cleaner.plist` exists on this machine. The only reason
`/private/tmp/etcGEMs-p17` has survived since 12 September is that the machine **has not rebooted in
58 days** (boot: 16 July 2026). A `/private/tmp` entry dated 2026-07-16 is still present, which is
the same fact from the other side.

**But losing that directory would NOT lose the archive.** Verified rather than assumed:

- the worktree's `.git` is a **141-byte pointer file**, not a repository;
- **every P17 blob lives in the primary repository's object store** — `git cat-file -s` reads the
  109,809,818-byte `unif_benchmark.log` from `.git` directly, with the worktree playing no part;
- the branch ref `codex/p17-inactive-prior` → `ef1961b` is stored in the **primary** repo's
  `.git/refs/heads/`, inside the OneDrive-backed folder, not in `/tmp`.

So a reboot would destroy a **2.9 GB checkout**, recreatable with one `git worktree add`, while the
**1.9 GB object store holding the actual evidence sits in OneDrive**. The archive is durable; only
the convenience copy is not.

**Recommended, not acted on** (the prompt says recommend): relocate with
`git worktree move /private/tmp/etcGEMs-p17 ../etcGEMs-p17-archive`, which puts the checkout beside
the repository. Left undone because moving another worktree is outside what this task was asked to
change, and because the data is not at risk.

## D6 — a standing §4 item cleared as a side effect, and confirmed by re-running the battery

Committing the primary tree's regenerated `resolved_config.yaml` files (D1) **closed the
long-standing OPEN_ITEMS §4 stale-dump item**. Confirmed rather than claimed: after the full gate
battery ran on the merged main, `git status --porcelain strains/` is **empty** — the two dumps that
had reappeared as modified after every gate battery since N2's hotfix no longer do. Gates unchanged
at 79/79 and 60/60.
