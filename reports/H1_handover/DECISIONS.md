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

## D1 — TASK 2: the deck brought current. Nine slides changed, three added, one clipped slide caught by the deck's own checker

The deck was at its E6 state (13 September), which predates T2 and T3 entirely. It was **updated,
not rebuilt**; its tone, its structure and its stated limits are unchanged. **59 → 62 pages**,
59 frames, render clean (0 overfull boxes, 0 unresolved citations).

| slide | what it said | what it says now |
|---|---|---|
| *The reduced posterior: run 1 converged* | *"Seed 2 is in flight. Independent confirmation is pending."* | **Seed 2 landed and the two seeds DISAGREED** — evidence agreed (Δlog Z 0.022 vs 0.148 combined) but **14 of 15 medians** failed the two-MC-error rule (`P16_reduced/audit_summary.json`); and the run is marked superseded by the revised target |
| *The stopping and reproducibility rules* | *"The two-seed agreement test has no result yet"* | the test has a result, **DISAGREE**, and the same rule has since been applied twice more |
| *What the reduction assumes* | `tm_scale` median **1.069** [0.793, 1.515], seed 1 only, "no boundary pile-up" | both P16 seeds (1.069 and **0.956**) plus the revised target's **1.319 / 1.232 at the 99.4th percentile of the prior**: the hard bound 2.2 is still never reached, and the distinction between the bound and the prior's mass is now stated |
| *Run 1 assigns about half its weight to very low growth* | 50.7 % of draws below half the measured peak | unchanged as history, **plus** the revised likelihood's **1.4 % and 2.4 %** — the low-growth mass was the scoring rule |
| *The infeasibility exemption: a diagnosis under test* | *"Test now: quantify infeasibility…"* | retitled **"diagnosed, then fixed"**; carries the measurement (**765 of 800** points infeasible at every temperature, **81.5 %** of posterior weight from ~**16 %** of prior volume) and the adopted zero-likelihood rule |
| *Why a converged posterior can favour poor predictions* | *"The cause remains under test"* | the cause was confirmed and the rule changed |
| *Model evidence asks which mechanism the data support* | D on NLDM **−26.030 ± 0.109 from seed 1** | the **revised** target's **−27.707 ± 0.110** and **−28.047 ± 0.100**, which **do not agree**; plus the caution that E and F's face degeneracy is an order of magnitude worse |
| *Established results and pending confirmation* | *"Converged, awaiting confirmation… seed 2 is in flight"* | **"Diagnosed, not yet solved"** — five runs across two likelihoods, no two agreeing; the scoring defect fixed, the reproducibility obstacle measured with a costed remedy |
| *What happens next* | confirm reproducibility; resolve infeasibility; M9; D/E/F; proteomics | the determinism remedy **first** because everything inherits it, then the cheap test of whether a second cause is real, then the rest unchanged |

**Three slides added** (the prompt's maximum): *The revision worked — and the runs still disagree*;
*The likelihood is not a function of its parameters* (the four-scheme table); *What is handed over*.

**One thing worth recording because it is exactly the hazard the deck documents.** `check_frames.py`
exists because *"Beamer CLIPS an overfull frame and LaTeX does not emit an Overfull warning for
it, so a slide can quietly drop its last bullets and a clean render log proves nothing."* The
render log was clean and the new T3 slide was **silently dropping its last bullet** — caught only
by that checker, and fixed in three passes (a four-row table with a three-line lead and three
bullets does not fit; a one-line lead and two bullets does). Final check: **0 frames with content
missing.** The tone is unchanged: nothing is presented as a failure, and the three standing limits
(D44/D45 at one point; the toy living fractions are not targets; dTm = 0 assumes the meltome mean
is exact) are untouched.

## D2 — TASK 1: the investigation report, organised by what was learned

`reports/H1_handover/calibration_investigation.{qmd,pdf}`, rendered in the house convention
(the synthesis's `header.tex`, `nature-communications.csl` and `_quarto.yml`, copied not
re-invented). **9 pages, 14 sections, 0 unresolved cross-references.** It is the successor to
`reports/synthesis/` for everything after 9 September and explicitly **not** a replacement of it.

**Every number is traced.** Where `evidence.csv` carries a row, it is cited by row id
(P13a–P13g, P14a–P14d, P15a–P15d, Q1, T1a–T1c, T2a–T2e, T3a–T3d, Y2). P9–P12, P16 and P17 have
**no evidence rows** — they postdate the synthesis's row set — so those numbers name their file
and commit inline (`P9_surface/report.md` @ `dbb2e3d`, `P10_respiration_likelihood/report.md` @
`409d70b`, `P11_nested/report.md` and `P12_modes/report.md` @ `4f4c56f`,
`P16_reduced/audit_summary.json` @ `b8b181b`, `P17_inactive_prior/` @ `3a5de32`).

**Self-corrections carry their own numbered sections at the same level as the findings**
(§3.1 the criterion that tested the wrong failure mode; §6.1 the 765 points and the 96 % → 16.45 %
correction) and appear in-line in four more places: the withdrawn multimodality reading, the
unread parameter, the withdrawn impute form, and the solver reset measured worse than doing
nothing. The document states in §1 why they are there.

**One judgement call, recorded.** The prompt's outline asks for the P17 section to carry its two
limits verbatim; the report carries **three**, adding that fixing dTm at 0 assumes the meltome's
mean is exact — because every run after P16 conditions on it and the handover's readers will not
know that otherwise. RIGOUR.md and the P17 closure both state it; adding it is consistent with
both.
