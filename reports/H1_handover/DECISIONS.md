# H1 — the investigation written up, the deck brought current, the repository closed: decisions

_Branch `h1/handover` from `main` at `897d78e` (the merge of T3's PR #42, base read first: `main`,
MERGEABLE CLEAN). Worktree `../etcGEMs-h1` (the primary tree's `.git/index.lock` is still held by
the sandbox VM, as in T1–T3). RIGOUR.md governs. **No fit, no sampler, no model or likelihood
change, no derived table altered, no option enabled, no reserved seed touched.**_

## D0 — TASK 0: the state taken from the record, not from memory

**Merge.** PR #42's `baseRefName` read first: `main`. Merged at **`897d78e`**; `main` pulled;
`h1/handover` branched. **No PR is open.**

**Gates on main with every option OFF**, run in the worktree (`task0_gates.log`): K1 **79/79**,
P1 **60/60**, every `rc=0`. The thirteen `resolved_config.yaml` dumps differ by the worktree's
absolute path only (§4's 3.15 artefact, as in T1 D1, T2 D1); restored with `git checkout --`.

**The archive, confirmed and untouched:** `codex/p17-inactive-prior` present locally at
**`ef1961b`**, **0 matches on `origin`** (`git ls-remote`), worktree at `../etcGEMs-p17-archive`.
Not merged, not pushed, not deleted, not entered.

**Nothing was running** at the start: no python process with any worktree as cwd.

**One deviation from the prompt, stated:** it says to run from the project root. The primary
tree's `.git/index.lock` is still a stale zero-byte file held open by `com.apple.Virtualization`
(pid 62662), and T1–T3's rule against deleting lock files carries over, so all work is in the
`../etcGEMs-h1` worktree, whose index is independent.
