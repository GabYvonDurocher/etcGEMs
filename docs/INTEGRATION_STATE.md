# Integration state — 13 September 2026

**Preparation only. No merge, push, branch switch or other worktree edit was performed.** Integrate before scientific work in the next Claude Code session. P17 closes as a negative diagnostic result, not a passed correction gate. Read HANDOVER_2026-09-13.md and RIGOUR.md first.

The inventory uses locally cached origin refs; no fetch or remote-freshness claim was made. Cached origin/main and local main are both `dc5b4cc78997b1cdb047bbe49bee1527d9ec261d`. Every local and cached remote ref was compared against origin/main. Full commit subjects, ancestry, artifact sizes and file lists are in [the machine-readable inventory](integration_inventory_2026-09-13.json).

## Branches ahead of cached origin/main

| Ref | Exact head at inventory | Ahead / behind | Contents and worktree |
|---|---|---|---|
| p16/reduced | `191b4b0c89e0eb9091425aeaae2910669b7fd3ec` | 6 / 0 | P16 reduction, spectrum, first posterior and adverse interpretation; primary `etcGEMs` tree |
| codex/p17-inactive-prior | `14b46deae53a77c8d5ef27388696e15e25a67a57` before closure commits | 31 / 0 before closure | P16 ancestry plus 25 P17 diagnostic commits, followed by this closure's artifact/report/document commits; `/private/tmp/etcGEMs-p17` |
| e2/deck | `0215a1671aa6ab1ffc3a038c77833ad2d7f68a18` | 26 / 0 | E2–E6 slides, renders and provenance; `../etcGEMs-work` |
| origin/e2/deck | `bc356e332f4200089651d0d6a85e74df237a5096` | 20 / 0 | Cached E5 deck tip; local e2/deck is SIX commits ahead |
| q1/n0-check and origin/q1/n0-check | `b163bad26dd13751e82575f9056cd614c1e6ce5a` | 25 / 0 | E5 deck ancestry plus five Q1 conversion/CUE/provenance commits; no checked-out worktree |

There are no other ahead refs in this inspection. y2/regime-posterior, y3/tm-shift and their cached remotes, and cached p7–p15 refs, are already ancestors of origin/main. The P17 row intentionally gives its immutable **pre-closure inventory head**: the commits containing this inventory necessarily follow it. Resolve the final closure tip with `git rev-parse codex/p17-inactive-prior`; the delivered final response records that full hash. Do not mistake the table's inventory hash for the completed closure tip.

Verified relationships: p16/reduced is P17's ancestor, merge base `191b4b0c89e0eb9091425aeaae2910669b7fd3ec`. Q1 is stacked on **cached E5** `bc356e332f4200089651d0d6a85e74df237a5096`, not on the local E6 tip: local e2/deck and Q1 diverge by six versus five commits. This differs materially from assuming both are remote-only branches in the other tree.

## Uncommitted state and preservation

[INTEGRATION_UNCOMMITTED_FILES.md](INTEGRATION_UNCOMMITTED_FILES.md) lists **every nonignored uncommitted file in the external trees**, with status and SHA-256; the JSON contains the full pre-closure P17 list as provenance. Primary p16/reduced has 32 dirty paths: OPEN_ITEMS (including §0d), P16 DECISIONS, fourteen audit artifacts plus trace_red2, the red2 checkpoint/arrays/summary, six prompts, two Candida resolved configurations and two nominal TPC images. Do not discard these when preparing the primary tree for integration. Compare hashes against the copies committed by P17; preserve any genuine differences as dated evidence. The P16 post-commit audit additions inherited into P17 are committed here. The primary's unrelated files remain there, untouched.

The `etcGEMs-work` e2/deck tree was clean. The P17 worktree is made clean by this closure's commits, including all P17 files previously ignored (logs, caches and checkpoints). The historical inventory's P17 dirty list is not its delivered final status. Ignored external output inventories are recorded separately in the JSON; a clean ordinary status never proves those outputs are tracked.

## Recommended later integration order

1. Preserve and reconcile primary p16/reduced's uncommitted files, then merge **p16/reduced → main**. This establishes the reduction and original evidence as a distinct historical step.
2. Merge **codex/p17-inactive-prior → main**, including every closure artifact and inherited completed-run audit. Retain the negative conclusion and PI stopping-rule change.
3. Merge **local e2/deck → main**, including its six E6 commits beyond cached origin. Reconcile the deck's posterior claims against final P17; do not restore a validated-posterior claim.
4. Merge **q1/n0-check → main**, retaining its conversion/CUE findings and the newer E6 work. Its five Q1 commits sit on E5 and need reconciliation with E6.

This is a recommendation, not execution or permission to discard external dirt. Recheck remote state in a push-enabled session before integration. Preserve original branch histories and evidence.

## Conflict rules

These are inspected overlapping files and integration-sensitive records, not an assertion that a merge was attempted or exact textual conflicts simulated.

| File family | Rule |
|---|---|
| `docs/OPEN_ITEMS.md` | Keep P16/P17 findings, E5/E6 holdout corrections and Q1 provenance corrections. Reconcile chronology and numbers by dated additions; retain both histories and the P17 closure. Never choose one side wholesale. |
| `reports/synthesis/evidence.csv` | Retain each distinct evidence row from both branches, check schema/keys and factual consistency; do not drop adverse rows or silently overwrite shared identifiers. |
| `reports/report_status.yaml` | Preserve all report entries, reconcile status with the final evidence, and retain both sets of provenance; P17 is closed-negative and the original correction gate remains unpassed. |
| `PROVENANCE.md`, render/hash stamps and generated deck records | Preserve the source histories, then regenerate stamps and affected renders from the integrated sources using the repository's documented tooling. **Never hand-merge a stamp or fabricate a hash.** |
| Deck sources and generated figures/PDF | Keep E6 content and Q1 CUE caveats together, reconcile against P17, then regenerate and verify. A binary PDF cannot be combined by choosing stale content. |

## Tracked versus ignored artifacts and clone completeness

The JSON lists each inspected P16/P17/eciML1515 output by path, bytes and tracked/ignored state at inventory. The closure's `reports/P17_inactive_prior/closure_manifest.json` is the final SHA-256 inventory of P17 artifacts (excluding itself to avoid a self-hash). Every P17 artifact is force-added to Git in this closure, including previously ignored logs, arrays, initial/periodic checkpoints, failure evidence and caches. Both P16 red1 and red2 checkpoint/sample/logwt/logl evidence are tracked after the closure; inherited P16 audit outputs are also tracked. The five inherited P16 logs are also committed at closure. In this P17 tree, all 421 existing files under `strains/eciML1515/outputs/` are tracked; the primary tree has additional ignored archive/diagnostic outputs, including `_archive/calibration_vanderlinden_v2/corner.png`, that are **not automatically in a clone**. Consult the per-tree inventory rather than assuming identical physical contents across worktrees.

An actual large-file transfer issue remains for the later push session: `reports/P17_inactive_prior/unif_benchmark.log` is **109,809,818 bytes**, above 100 MiB. It is retained and committed as requested. A host with a 100 MiB per-file restriction cannot accept that ordinary Git blob. This session does not prune, rewrite history, migrate to LFS or attempt a push. The later session must arrange an approved lossless hosting/transfer strategy, including any required history/LFS decision, and verify full materialisation in a fresh clone. A Git commit alone is not evidence of remote availability.

`/private/tmp/etcGEMs-p17` is a Git worktree, not disposable scratch evidence. **Remove it only after the branch is merged and pushed and a fresh clone contains reports/P17_inactive_prior/ in full**, with all manifest hashes checked. Preserve any ignored external P16 outputs needed for reproduction before removing or relocating their trees.

## Prompt disposition

`prompts/E6_deck_bring_current_prompt.md` is an untracked file in the **primary tree**, absent from the P17 and e2/deck tracked trees at inspection. It assumes E5 has not run and directs E5 carry-forward, whereas cached e2/deck already includes E5 and local e2/deck includes six E6 commits. **Mark it superseded, do not delete it**, during later integration. It was not edited here because only P17 worktree writes are authorised.

Scientific limits survive integration: D44/D45 concern one non-optimal point and do not prove all samplers fail or likelihood is the sole cause; analytical toy living fractions of 80–87% are not biological targets. dTm=0 excludes uniform meltome-mean uncertainty that would otherwise enter tm_scale and catalytic parameters.


Final artifact preservation was independently verified at commit `45616c2a0429de121b5a9a371b0ebfca6e4493c6`: every P17 file is tracked and every manifest hash matches. See [closure verification](CLOSURE_VERIFICATION_2026-09-13.md) and [final artifact inventory](closure_artifact_inventory.json). The following documentation-only commit records that verification; resolve the delivered tip as described above.
