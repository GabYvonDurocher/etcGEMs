# Open items — the running list

_Started 2026-09-08 while P2 was running; last updated 2026-09-13 by T1._ This is the standing list of what is outstanding across
the whole project, so nothing is lost between sessions. Update it when something lands; do not let
it become a second decision log — decisions live in each prompt's `reports/*/DECISIONS.md`, this is
only what is NOT yet done and who or what it waits on._

Status: **BLOCKED** (waiting on something external) · **READY** (can start now) · **PENDING P2**
(depends on the run in flight) · **DEFERRED** (deliberately not now, with a trigger)

---

## 0. CLEANUP FINISHED — 2026-09-16 (H3, H4)

**H2's and H3's follow-ups are all closed.** The primary checkout `MICROADAPT/etcGEMs` is now on
**`main`**, clean of tracked modifications, and is the tree a collaborator opens. Exactly **two
local branches** remain — `main` and the protected `codex/p17-inactive-prior` — and **three
worktrees**: the primary on `main`, `../etcGEMs-work` detached at main's tip for parallel runs, and
`../etcGEMs-p17-archive` at `ef1961b`. Both gates pass from the primary tree: **79/79 and 60/60**.

- **The stale `.git/index.lock` is gone** (H3), removed only after confirming no git process owned
  it — no git process was running at all, and the only holder of the descriptor was a VM.
- **An abandoned merge was cleared** (H4): `Merge branch 'main' into p13/support` from 10 September,
  whose `MERGE_HEAD` and `HEAD` were both already ancestors of `main` with zero conflicted paths.
  Cleared with `git merge --quit`, never `--abort`, which would have discarded the untracked
  prompts.
- **Three stale tracked files discarded** after re-verifying each: `docs/RIGOUR.md` and
  `reports/P17_inactive_prior/ARCHIVE.md` were byte-identical to `main`, and `docs/OPEN_ITEMS.md`
  was byte-identical to the version at `86d182a`, an ancestor of `main` — strictly older, never
  divergent.
- **The prompt series is complete on `main`** (PR #48): T2, T3, H1, H2, H3 and H4 were absent
  entirely and T1's 278-line revision replaced its 242-line committed version. A reader of
  `reports/T2_validated_posterior/`, `reports/T3_determinism/` or `reports/H1_handover/` can now see
  what was asked as well as what was found.
- **`../etcGEMs-k7` deleted** (H3) after verifying it held a 2026-09-08 checkout of main's own
  history with zero unique files; **`../etcGEMs-k6` restored and removed** (H4) — its 1,172 missing
  files were tracked-and-absent with zero untracked, so `checkout -- .` made it clean by git's own
  definition and it removed non-force. Its branch is deleted.

**Two things the cleanup prompts did not anticipate, resolved and recorded:**

1. **A branch lives in exactly one worktree.** H2 left `../etcGEMs-work` holding `main`, so the
   primary checkout could not take it. The primary is the checkout a collaborator opens, so it
   holds the branch and `../etcGEMs-work` is **detached** at the same commit — which is the state
   it was in before H2's rename.
2. **An untracked file can block a switch** when the target branch tracks a file at that path. The
   obsolete T2 redirect marker `reports/T2_validated_posterior/status.json` — which pointed at a
   worktree that no longer exists — collided with main's real `status.json`. It was **moved**, not
   deleted, to `../etcGEMs-work-salvage/T2_REDIRECT_status.json`.

**Still on disk, reported and deliberately untouched:** twenty untracked artefacts in the primary
tree (`brenda_sdh.html`, two config experiments, several `transfer_*` output directories, eight
`.gitkeep` placeholders and a `dynesty_proof.save`) and `../etcGEMs-work-salvage/` (664 KB: a
superseded 11 September deck render, its LaTeX intermediates, and the redirect marker above). All
are safe to delete; none was deleted, because none of it is ours to discard.

---

## 0. WORKTREES CLEANED — 2026-09-16 (H2)

Filesystem and git hygiene only; no science, no model or config change. **Ten disposable worktrees
removed or pruned and seven merged branches deleted, recovering ~2.2 GiB**; `origin` carries only
`origin/main`. **The second working tree is now `../etcGEMs-work`** (renamed from `../etcGEMs-h1`),
on `main` and clean — use it for parallel runs.

**`../etcGEMs-p17-archive` is protected and was re-verified by name at every step:** branch
`codex/p17-inactive-prior` at **`ef1961b`**, clean, 2.9 GB, its manifest readable (1,905 files),
**absent from origin**. It is the only ref keeping those artefacts reachable and is never merged,
pushed or deleted.

**Three things were deliberately left, because removing them would have needed `--force` or would
have destroyed unsaved work:**

- **The primary checkout `MICROADAPT/etcGEMs` is still on `t1/housekeeping` at `3222b9d`, not on
  `main`.** Two blockers: its `.git/index.lock` is still a stale zero-byte file held open by the
  sandbox VM's file server (`com.apple.Virtualization`, pid 62662) since 13 September, so git
  cannot write its index at all; and it carries **real uncommitted work** —
  `prompts/T1_target_revision_prepare_prompt.md` differs from every committed version by 43 lines,
  and several prompt files (`H1`, `H2`, `T2`, `T3`) exist only there, untracked. Its
  `docs/OPEN_ITEMS.md` is by contrast merely **stale** (it is byte-identical to the version
  committed at `86d182a`, 653 lines against main's 749) and can be discarded safely. **To finish:
  clear the lock (a reboot releases it), commit or copy out the prompt edits, then
  `git switch main && git pull`.**
- **`../etcGEMs-k6`** (2.9 MB stub): its content was deleted from disk, so git sees 1,172 deleted
  files and refuses a non-force removal. There is **nothing unsaved** — 0 untracked files, every
  entry a deletion of a file git still holds, and `k6/like-for-like` is merged into `main` — so
  `git -C ../etcGEMs-k6 restore .` then `git worktree remove ../etcGEMs-k6` clears it in two safe
  commands.
- **`../etcGEMs-k7`** (64 MB): its `HEAD` points at `refs/heads/k7/envelope`, **a branch that no
  longer exists**, so the head reads `0000000`, every file looks untracked and both `remove` and
  `prune` decline. Its work is on `main` (`reports/K7_envelope/`). Delete the directory by hand and
  run `git worktree prune`.

Four local branches remain: `main`, the protected `codex/p17-inactive-prior`, and
`k6/like-for-like` and `t1/housekeeping`, each held by one of the two worktrees above.
`../etcGEMs-work-salvage/` (660 KB) holds four untracked LaTeX build artefacts moved out of the old
`etcGEMs-work` before it was removed — a superseded 11 September deck render and its `.tex`,
`.nav`, `.snm` intermediates, all regenerable by `quarto render`. Delete it when you are satisfied
nothing is wanted from it.

---

## 0. PAUSED AND HANDED OVER — 2026-09-16 (H1)

**The calibration investigation is written up and the repository is closed for handover.** The
report is `reports/H1_handover/_output/calibration_investigation.pdf` (the successor to
`reports/synthesis/` for everything after 9 September; the synthesis's §1–§6 stand). The handover
a new collaborator should open first is [HANDOVER.md](HANDOVER.md), which supersedes
`HANDOVER_2026-09-13.md`.

**Where it stands in one paragraph.** The framework is merged and gated (79/79 and 60/60 on every
commit). The likelihood is now scientifically correct: a parameter that was never read has been
removed and proven inert at 870 points; structural infeasibility, which was winning 13.5
log-likelihood units by not being scored, now carries zero likelihood; and the prior-rejection rate
that follows is measured at 16.45 % [14.9, 18.1] rather than the ~96 % anticipated. **No posterior
is reproducible.** Five runs across two versions of the likelihood have met their stopping rules
and no two agree. One cause is measured — the likelihood is not a deterministic function of its
parameters in a persistent worker pool, and only a fresh model per evaluation fixes it, at 3.2×
cost (**1.34**, **1.35**) — and a second cause is unidentified, because the high-weight samples of
the disagreeing runs re-evaluate clean.

**The decisions waiting, in order:** **1.35** (the determinism remedy — everything inherits it),
**1.36** (Parsa's per-medium constants, assessed as a likelihood change), then 1.33, 1.17 and 1.26.
The PI decision list is §0e below; §4's hazards gained three entries this week.

**Reserved seeds 17901–17903 are spent; 17904–17905 are not.** `codex/p17-inactive-prior` remains
local-only at `ef1961b` with its worktree at `../etcGEMs-p17-archive`, and is never merged, pushed
or deleted.

### 0e. The PI decision list, in one place

| # | decision | state |
|---|---|---|
| **1.35** | Adopt a deterministic likelihood-evaluation scheme, or accept non-reproducibility | **measured, awaiting decision** — everything else inherits it |
| **1.36** | Parsa's per-medium N₀ and carbon constants | **assessed, awaiting decision** — a likelihood change, not a figures update |
| 1.33 | Why the model is infeasible over ~16 % of a defensible prior, and whether 15 °C is the right first temperature | opened by measurement, undiagnosed |
| 1.17 | Run the remaining eight gas-flux fits, or not | blocked by 1.35; re-costed at ~320 h under the exact remedy |
| 1.26 | The D/E/F evidence comparison | the biological question; needs one reproducible number first |
| 1.14 | Whether a Li-style calibration is worth attempting | untouched |
| 1.20 / 1.24 | The `dTm` decision and the `dTm`/`tm_scale` ridge | Y3 showed the shift is parameterisation; the pair is non-identified |
| 1.16 | Should the Candida respiratory audits use the parsimonious vertex? | a K-series decision, independent of the above |
| 1.15 / 1.25 | The respiration likelihood and the treatment of missing predictions | **superseded in substance** by 1.29–1.32, which were decided and executed (T1/T2) |

---

## 0. Integration — completed 2026-09-13 (R3)

**Everything since the P15 merge is on `origin/main` at `64393edede223feebbcebbf4554d548f38e03cf9`.**
Four bodies of work merged as four PRs plus one correction:

| PR | branch | merge | what |
|---|---|---|---|
| #34 | `p16/reduced` | `96d11d1` | the reduction, spectrum, both 15-D runs, the post-run audit, and the primary tree's 32 uncommitted evidence files |
| #35 | `p17/curated` | `32160f2` | P17's closure, **curated**; RIGOUR, HANDOVER, INTEGRATION_STATE, TARGET_REVISION_SPEC, CLOSURE_VERIFICATION |
| #31 | `e2/deck` | `99279a4` | the E2–E6 deck, 59 pages |
| #33 → #36 | `q1/n0-check` → `e2/deck` → main | `64393ed` | Q1's conversion/CUE null result, reconciled onto E6 |

**P17 on main is CURATED, and complete elsewhere.** 580 files and 15.7 MB of reports, scripts,
DECISIONS, manifests and figures are on main; the full 2,962 MB artefact set — 486 `.save`
checkpoints, 775 `.npz` archives, 72 logs — stays on the **local, never-pushed** branch
`codex/p17-inactive-prior` at `ef1961b`. `closure_manifest.json` is on main **unchanged**, carrying
the SHA-256 of all 1,905 files including every excluded one. A fresh clone of `origin/main` was
verified: **549 P17 files matched the manifest, 0 mismatched**, both gates pass (79/79, 60/60), the
deck is 59 pages. The full branch could not be pushed because `unif_benchmark.log` is 109,809,818
bytes, above GitHub's 100 MiB limit, with no LFS configured. See `reports/R3_integration/`.

**No duplication item arose from E6.** The concern that `E6: E5 carry-forward` had re-applied E5's
edits was inspected slide by slide and is **unfounded**: E6 removed four P15-crash slides, added
eleven P16 slides (49 → 56), edited deck.qmd lines in place, and left no duplicated slide title or
bullet.

**A §4 item closed as a side effect.** The two `strains/cauris_iRV973/.../resolved_config.yaml`
dumps, one key stale since N2's hotfix and reappearing as modified after every gate battery, are
now committed regenerated. Confirmed: after the battery ran on merged main,
`git status --porcelain strains/` is empty.

| # | Item | Waiting on | Why it matters |
|---|---|---|---|
| ~~1.28~~ | ~~**Relocate the P17 archive worktree out of `/private/tmp`**~~ | — | **DONE 2026-09-13 (T1 0a).** `git worktree move` to `../etcGEMs-p17-archive`; verified at `ef1961b`, clean, manifest readable, old path gone. Original note follows. `/private/tmp/etcGEMs-p17` is the only checkout of `codex/p17-inactive-prior`, and this machine **does** run `com.apple.tmp_cleaner`; it has survived only because there has been no reboot in 58 days. **The evidence itself is not at risk** — the worktree's `.git` is a 141-byte pointer, every P17 blob lives in the primary repository's 1.9 GB object store in OneDrive, and the branch ref is in `.git/refs/heads/`; a reboot would cost a 2.9 GB checkout recreatable with one command. Recommended: `git worktree move /private/tmp/etcGEMs-p17 ../etcGEMs-p17-archive`. Not done by R3, which was asked to recommend rather than act. |

**Next scientific step:** `docs/TARGET_REVISION_SPEC.md`, **awaiting PI approval** (item 1.27). No
revised fit launches before that approval and the full validation protocol. See
`docs/HANDOVER_2026-09-13.md`.

---

## 0. Sequencing — E. coli first (decided 2026-09-09, sequence added 2026-09-10)

- **The E. coli model (`eciML1515`) is the best-constrained**: three media, gas exchange, a
  measured meltome. Methods are developed and proven there first, then ported through the core.
  The seven-strain gate (K1, 79/79) runs on every core change so the other strains cannot
  silently break meanwhile.
- **Candida:** the K-series result (13.57 °C required against 1.6 °C measured, and why) stands
  and is what the manuscript uses. No further Candida modelling until the E. coli calibration
  recipe exists; then it ports against the measured TPCs.
- **Cross-taxon questions already answered** (activation energies K6, seven-strain ceiling K9)
  stay on record and are not re-opened by this.

### 0a. What "a reliable model" means — four separate things, in order

Written 2026-09-10, **before P12 reported**, so that each new result is reconciled against it
rather than replacing it. These were tangled together for most of the P-series; separating them
is what the last week bought.

| | Requirement | State | What closes it | Cost |
|---|---|---|---|---|
| **R1** | **Statistically reliable** — a posterior two independent runs agree on | Surface sampleable (P10/P11); mode structure unknown. **T2, 2026-09-15: OPEN, blocker named** — the gas-flux likelihood evaluated in a persistent pool worker is not a deterministic function of θ (path-dependent tie-broken LP vertices at the 1e-3 to 1.3 log-likelihood level at posterior points); run 3 crashed on a live point stored 1.28 above its true value, runs 1 and 2 disagree in log Z (Δ 0.34 vs 0.15), 14 medians and direction, and the Beta(3,1) control on an inert coordinate is not recovered. `reports/T2_validated_posterior/DECISIONS.md` D11; item 1.34. | P12's basin map, then per-basin sampling on restricted priors | ~1 day of runs after P12 |
| **R2** | **Identified** — parameters set by data, not prior | **Restated 2026-09-11 (E3): the five "flat" parameters are not one category but three.** `f_metab` and `f_maint` are **FIXED BY MEASUREMENT** — they enter from the measured proteome matched to medium *and* temperature and carry deliberately tight priors, *"measurement wiggle only — the proteome is not free-fit"* (`report.qmd` §free set and priors; the fractions are *"never fit to growth"*, §eq-alloc). The likelihood being insensitive to them within that width is **the designed behaviour**: growth and respiration are not asked to re-derive a proteomics measurement. **Never call them unidentified.** `kappa_scale` (effective translation demand, auto-calibrated once at build time) and `ngam_steepness` (*borrowed* maintenance steepness, ported constants a_m≈8.5, b≈0.62, E_m≈0.5 eV from the MRes model) are **genuinely unidentified**. `clearance_mult` is a property of the experiment, not a model lever. (P11 TASK 3 measured the flatness correctly; the classification was wrong.) | **The real allocation gap is RANGE, not existence:** the measured allocation is held at its endpoint beyond the measured range, so above 37 °C on glucose the sector split is frozen — and that is exactly where `CT_max` is set. Extending the measured glucose series above 37 °C is a **proteomics experiment, not a modelling problem**. Separately and genuinely missing: maintenance vs temperature from a low-dilution chemostat (`ngam_*` are borrowed, verified not measured). | **Proteomics: one measured series.** Chemostat: days / months |
| **R3** | **Right for the right reason** — the mechanism is discriminated, not just fitted | **Screened 2026-09-10 (Y3): partly answered, and the answer redirects the route.** The −4 K `dTm` is not uniquely required — an equally good living fit exists at `dTm` = 0 — but the compensator is `tm_scale`, another **stability** parameter, not a catalytic one. Both solutions put the least-stable few per cent of enzymes 4–6 °C below the measured meltome. So the mechanism is **not** discriminated, and the undetermined part is Tm's **low tail**, not catalysis | **Not DLTKcat.** It has already been run on this proteome (1 149 reactions, 5–55 °C): fitting MMRT to its predictions gives an interior optimum for **36 of 1 149** — its kcat(T) is essentially monotone over the biological range, so there is no per-enzyme Topt in it to extract. What the evidence points at instead: the meltome is per-protein, so **name the enzymes carrying this model's thermal limit and compare their measured Tm against what the fit needs** | **~½ day** for the named-enzyme test, against 2–3 days for the DLTKcat route Y3 recommends against |
| **R4** | **Predictively reliable** — holds out of sample | **Corrected 2026-09-11 (E5): one a priori test WAS run, and it half-succeeded.** `reports/ecoli_tpc/report.qmd` §563–570: the **uncalibrated** model predicts the exact-strain Van Derlinden curve with *"Nothing is fit to growth"* — it tracks the **shape** (T_opt, E_a) and under-predicts the peak **~2.3-fold** (1.04 against 2.40 h⁻¹). So shape held and magnitude did not. **What has no holdout is the CALIBRATED model**, because the calibration was then fitted to that same curve. The earlier wording — "nothing has ever been tested against data it was not fit to" — was wrong and undersold the work. | Cooper 2007 (`refs/`): TPCs of *E. coli* lines after 20,000 generations. Predicting how a curve *shifts* under evolution is the real test of a temperature-dependence framework, and it is the holdout the calibrated model still lacks | ~1 day once R1 holds |

### 0b. The sequence

1. **P12 — map the modes.** No sampler. Basin count, heights, prior-volume fractions, and what
   separates them. Licenses the sampler choice. *(prompt written; not yet run)*
2. **The dTm decision — PI.** Currently `dTm` is a free parameter with a wide prior landing at
   −3.9 to −5.6 K against a **measured** meltome. If the meltome is trusted, that shift becomes a
   model failure to explain rather than a number to fit — and constraining it may collapse the
   multimodality on its own, because the stability-shift mode dies. This is the single highest-
   leverage decision outstanding and P12's per-basin `dTm` will sharpen it. See 1.14, 1.20.
3. **Fix the five flat parameters** at nominal, stated as a limitation (R2, short form).
4. **Decide the respiration term's support — PI.** *(added 2026-09-10 by P12 addendum 1.)* The
   current weight discounts a dead model's respiration penalty by up to 16.7 log-likelihood
   units where a live one gets 1.2, so basins can be kept alive by the likelihood's support
   rather than by the data. This must be settled BEFORE per-basin sampling, because sampling
   a basin that only exists under a discount spends a day on an artefact. See 1.21.
5. ~~**Per-basin posteriors** on restricted priors, combined by volume fraction (R1).~~
   **STRUCK 2026-09-10 (P13), on P12's recommendation (c).** The line is kept rather than deleted
   so the change is visible: P12 found **one live basin**, so there are no per-basin posteriors
   to combine and no volume fractions to weight them by. What replaces it is a single
   well-converged run on the live basin, which is 1.19 — currently blocked by 1.23, not by this.
6. **Cooper 2007 as holdout** (R4). Only meaningful after 5.
7. **Then, and only then, port the recipe to Candida** against Ilgaz's measured TPCs.

### 0d. E6 deck snapshot and next steps (2026-09-11)

P16 seed 1 converged with dTm fixed to zero, log Z -26.030 +/- 0.109 and effective sample
size 5,988. Seed 2 remains pending in this deck snapshot. The agreement rule requires log Z
within combined error AND no parameter median differing by more than two Monte-Carlo errors.

1. Confirm reproducibility and whether seed 2 reproduces seed 1's low-growth predictive mass.
2. Quantify infeasibility among low-growth predictions and settle its respiration-likelihood
   exemption before any new fit. The 50.7% figure estimates draws growing below half the measured
   peak, not the fraction proven infeasible. MAP and weighted predictive distributions are the
   useful summaries; the vector of marginal medians is unrepresentative.
3. Run D on M9, changing the medium only. NLDM stands in for experimental R2A; M9 + glucose is
   fully defined. First check the M9 oxygen tie-break, carbon-cap binding and excluded control
   series. A stricter medium may increase infeasibility.
4. Compare D/E/F evidences on the same medium and observations, with the same likelihood and
   comparable declared priors. Any likelihood repair requires recomputing D evidence too.
5. Measure proteome allocation above 37 C on glucose.

The emergent model DID predict Van Derlinden a priori (1.04 versus 2.40 per hour, shape held).
The calibrated model has no independent holdout. R4 already records E5's correction in this
branch. E6 supersedes E5's P15-crash slide and carries forward its other corrections.

### 0d. Next steps — written 2026-09-11 20:30, while P16 seed 2 is running

_Seed 2 launched 19:50, tracking run 1 within ~8 % on wall-clock at matched iterations,
**expected to converge 05:15–05:45 on 12 Sep**. Run 1: 14,088 iterations, 9.585 h,
log Z = −26.030 ± 0.109, n_eff 5,988, no crash. Pick up here._

**First, on return — read P16's TASK 5 against these three, in order.**

1. **Do the two seeds agree?** The pre-registered rule (D3): log Z within combined reported error
   AND no posterior median differing by more than two Monte-Carlo errors. **If they disagree, stop
   and diagnose** — that is P11's failure recurring at nlive 800 and it changes everything below.
2. **Does D6 reproduce in seed 2?** The half-dead posterior — MAP log L −10.704 with peak growth
   1.7255 /h against a componentwise median of log L −30.558 and peak growth 0.0043 /h, with 50.7 %
   of posterior mass growing less than half the measurement. If both seeds show it identically it
   is a property of the model-plus-likelihood, not a sampling artefact, and that is a *stronger*
   result than one run.
3. **Never quote the componentwise median.** With correlated parameters the vector of marginal
   medians need not lie in the posterior's support at all; here it is a dead model and its growth
   R² of −2.01 measures its own unrepresentativeness. Report the **MAP**, and predictive quantities
   from the **full weighted sample set**. This is P12's θ_B recurring in a converged posterior.

**Then, the decision that gates everything else — 1.25, the infeasibility exemption.**

P12's decomposition: the live basin pays growth **+6.363** and respiration **−13.549**; the dead
basin pays growth **−18.860** and respiration **−0.017**. The dead basin wins 13.5 units *by not
being scored on respiration at all* — because Q1 established its temperatures are **infeasible**,
and clamp's mask is `isfinite(o2) & (o2 > 0)`. P13 fixed the feasible-but-not-growing case; the
**infeasible case was never addressed**, and a model with no feasible flux distribution is
currently exempted from the respiration likelihood rather than charged for it.

Arithmetic: the live–dead gap is ~11.7 units, and e^−11.7 ≈ 8×10⁻⁶ loses to prior volume in 15
dimensions — the live region need only be ~46 % of prior width per axis for volume to win. Charge
the dead basin a respiration penalty comparable to the live basin's −13.5 and the gap goes to ~25,
which needs the live region under ~18 % per axis. Far less plausible.

**Cheap test, no solves, from the existing posterior:** compare `disc_growth`, `disc_resp` and σ
between living and dead samples, and report what fraction of the dead mass sits on infeasible
parameter sets. If the dead mass is overwhelmingly infeasible, the diagnosis is confirmed and the
fix is a large finite penalty for infeasibility — the same question P13 answered one level up.
**Settle this before any further fit**, because a likelihood that exempts infeasible models will
hurt E and F far worse than D: they are the configurations that constrain respiration.

**Then the next fit: configuration D on M9 — one variable changed.**

Decided 2026-09-11. Not F, and not F-on-M9. **Change the medium, hold the configuration**, because
every verified component — pFBA tie-break, 1.42 floor, clamp support, sampleability scans, the whole
P10–P16 chain — was established on configuration D. D NLDM → D M9 is then a controlled experiment:
if the dTm/`tm_scale` degeneracy and the half-dead posterior reproduce, they are structural
properties of the thermal layer; if they do not, the medium is implicated.

**Why M9 and not NLDM.** M9 + glucose is fully defined. **NLDM is a defined recipe used as a
stand-in for R2A**, which is what the experiments were actually run in and which is itself
undefined — so every NLDM fit carries an approximation between the model's medium and the real one,
and any mismatch is absorbed into the parameters we are trying to interpret. M9 has no such gap.
`report.qmd` independently calls a defined-minimal TPC "the gold-standard future test", and P4 found
M9 gave the best growth fits in the exercise (R² 0.959 / 0.987 / 0.982 for D/E/F).

**Three checks before committing ten hours:**
  * **The tie-break has never been tested on M9.** P10's D3a instrument covered six fits — D/E/F ×
    NLDM and LB only. D M9's LP-face status is unknown and decides whether the run is well-posed.
  * **Does the carbon cap bind on M9 at `c_max` = 120?** If not, configuration D on M9 is the base
    model without the overflow mechanism — not a problem, but it changes which experiment you are
    running, and it should be stated going in.
  * **P4 excluded OTU 2 on M9** (seven non-monotonic rows) as a control rather than a series. Fine,
    but explicit.

**One caution running against the choice:** M9 is the more demanding medium, so the fraction of
parameter space producing a non-growing model may be *larger* there. If D6 is a volume effect, M9
could make it worse — which is another reason 1.25 is settled first.

**Before any programme of runs: benchmark `slices`.** Run 1 used `slices: 3` at 15.7 calls per
iteration, and that product is where its 221,781 evaluations went. `slices` is the one sampler
parameter worth tuning, under the same discipline as every other sampler change in this series —
**demonstrate the posterior and the evidence are unchanged, not merely that it is faster.** An hour
there could remove a day from the E/F/M9 set.

**And the prize that reframes the programme (1.26).** Nested sampling's second output is the
**evidence**. D, E and F on the same medium under the same likelihood give three values of log Z —
a **model comparison** answering which mechanism the data supports: overflow from a carbon cap,
a respiratory membrane-area limit, or that limit with bd-II non-electrogenic. That is the
biological question, it is nearly free once the machinery works, and emcee could never have
produced it. P16 has already delivered the first number, −26.030 ± 0.109 for D NLDM. **These are
competing hypotheses, not versions** — "the latest configuration" is a misreading.

**Deck and paper, while the runs go:** E5 is written and unrun (`prompts/E5_deck_posterior_and_holdout_prompt.md`);
E1's register never ran, so §0a R4's holdout claim is still wrong in both the deck and this file —
the *emergent* model was tested a priori against Van Derlinden (shape held, peak 2.3× low) and the
*calibrated* model has no holdout. Q1 also found the deck's CUE slide needs a caveat (CUE changes
*shape* under the alternative conversion, not just level), and 2.12 records a citation error where
Cooper2007 resolves to a 2001 paper.

**Restated 2026-09-15 (T2).** (a) and (b) of the T1 restatement are DONE: the four decisions were taken
by the PI on 2026-09-13 and executed (1.29–1.32 closed below); the revised target is on for eciML1515,
gated and verified. (c) was launched and **did not pass**: three of five reserved-seed runs consumed,
one crashed, two disagree (R1 row above; 1.34). The live sequence is now: **(c′)** the PI decides the
remedy for likelihood reproducibility in pool workers (1.34), registered as its own proposal; then five
runs on **new** reserved seeds (17901–17903 are spent; 17904–17905 unused) under the same frozen
protocol; (d) Cooper 2007 only after (c′) passes; (e) the Candida port after that. Section 4's new
hazards apply to every long run.

**Restated 2026-09-13 (T1).** Steps 1–5 above are historical. The live sequence, under RIGOUR.md:
**(a)** the three target-revision decisions **1.29, 1.30, 1.31** and the protocol signature **1.32** — all
PI, all prepared to their gates by T1, none acted on; **(b)** only then, the revised target as core options
default OFF, gated, the invariant and datum tables re-verified under the approved options; **(c)** the
protocol's five reserved-seed runs, sequential, ≈ 40–48 h at P16's measured rate; **(d)** Cooper 2007 as
holdout (R4) only after (c) passes; **(e)** then the Candida port. No revised fit before (a) and (b).

### 0c. Reconciliation rule — read before absorbing any new result

**13 September 2026:** This reconciliation rule and [RIGOUR.md](RIGOUR.md) together govern every subsequent run. P17 is closed negatively by PI stopping-rule change; see the dated closure below.

Every run in this series has produced a result that looked like the answer and was one layer of a
stack. **A new result does not replace this section; it is reconciled against it.** Each report
must state, explicitly:

- **which of R1–R4 it moves**, and which it leaves untouched;
- **what it retracts or qualifies** in an earlier report, by dated note, numbers unedited
  (P8's "unimodal" reading and Y2's mode-conditional posterior are the live examples);
- **what it does NOT license** — the standing hazard is that a result is quoted outside the
  conditions it was derived under (§4).

Precedent for the whole exercise: **Pettersen & Almaas 2023** (`refs/PettersenAlmaas_2023.pdf`)
found seed-dependent posteriors and multimodality in Li et al.'s yeast etcGEM with 2,292 per-enzyme
parameters; P11 found the same with 16 global ones. **The multimodality is in the thermal
formulation, not the parameter count.** They name proteomics and fluxomics as the cure and did not
have them; Parsa's gas-exchange data is that data, which is the argument for E. coli first. What
remains ours beyond their prior art: the *mechanism* (cliffs from the respiration term at cold
temperatures, LP kinks), the T_opt/CT_max asymmetry, the predictor validation, and the data.

> **Dated note, 2026-09-10 (P12) — one sentence of this section is withdrawn; the rest stands.**
> "**The multimodality is in the thermal formulation, not the parameter count**" was written on
> P11's seed disagreement. P12 tested it directly and it does not hold: with endpoints converged
> (11 of 12 on tolerance) and basins defined by bottleneck barriers rather than clustering, there
> is **one live basin**, and theta_A and theta_B* — the two runs' best samples — are separated by
> **0.266**, which is noise. The only separated basin is a model with zero predicted growth at
> every measured temperature. So this reformulation does **not** reproduce Pettersen & Almaas's
> multimodality, and the claim that it is intrinsic to the thermal formulation is **unsupported by
> our own evidence**. Everything else in this section stands, including the reconciliation rule
> itself, which is what caught this. See `reports/P12_modes/` D8 and OPEN_ITEMS 1.19, 1.22.

## 1. Waiting on people

| # | Item | Waiting on | Why it matters |
|---|---|---|---|
| ~~1.1~~ | ~~**E. coli respirometry**~~ | — | **CLOSED 2026-09-08 (P3).** Arrived as two full pipeline runs (R2A/LB and M9), ingested at `strains/eciML1515/respirometry/`. Configs D, E and F are now **gated**: all ten R² values reproduce, worst 0.009. |
| ~~1.2~~ | ~~**`c_max = 60`: grounded or fitted?**~~ | — | **CLOSED 2026-09-08 (P3 TASK 4)** — on his own evidence rather than by asking. His report calls the cap a swept boundary condition, not a fit, and his sweep concludes "C_max ≈ 100–120 is the sweet spot". **120 adopted** (the only value in his range at which acetate overflow is non-zero on both media); 60 kept as a labelled sensitivity. |
| ~~1.3~~ | ~~**Confirm recipe ceilings supersede blanket medium**~~ | — | **ACTED ON 2026-09-08/09 (P4).** All nine configurations refitted under recipe ceilings with the clearance K sampled. NLDM is unchanged to better; LB collapses, and the cause is `c_max`, not the medium (1.11). A one-line confirmation from Parsa is still welcome; nothing waits on it. |
| ~~1.4~~ | ~~**Confirm transporter kcat 30 vs 300**~~ | — | **SETTLED 2026-09-08 (P2 TASK 1)** by reproduction: 300 reproduces his figure, 30 does not. Set in the strain data. A one-line confirmation from Parsa would close it formally; nothing waits on it. |
| 1.8 | **Which configuration-F ETC table is intended?** | Parsa | P3 found his fits use configuration **E's** areas and turnovers plus a non-electrogenic bd-II, while the Bekker-turnover table in his `configF.py` was never used for a reported number. The port now matches what he fitted; whether the Bekker table is the intended future form is his call. |
| 1.9 | **Per-cell respiration: N₀ and fg C per cell** | Parsa | The inoculum back-projection is off in every row of both media sets, `cell_volume_um3`/`cell_carbon_fg` are typed constants (2 µm³ / 350 fg), and his own `config.R` log prints 21.21 µm³ / 2120.58 fg — ~6× apart. Growth R² and every scale-free quantity are immune; **respiration R², CUE and absolute per-cell rates are not.** Reported in `strains/eciML1515/respirometry/README.md`, not adjudicated. **CONSEQUENCE DRAWN 2026-09-11 (Q1): the respiration likelihood is NOT affected by the cell-carbon discrepancy, and this row's framing is wrong on that point.** The chain was derived from the columns and every one reproduced to <=8.5e-14. The likelihood's observable is `R_O2_mg_cell_min` = `C_tot_O2` / `biomass_integral`, which contains **N0 but not `cell_carbon_fg`** - factor **exactly 1.0000** under 2120.58 fg vs 350 fg. So "respiration R2" is immune, not at risk; `cell_volume_um3` enters **no** derived column at all. What does reach the respiration term is **N0**, and the biomass integral is `N0*(exp(r*T_end)-1)/r` **exactly** (verified 7e-14, all 183 growing rows), so an N0 error is a **uniform** factor, absorbed by the fitted `resp_scale` with **no effect on temperature dependence**. The one mechanism that could make it non-uniform - growth-rate-dependent cell size - was tested by the paired-media comparison (temperature held, growth rate differing by up to 2.00 h^-1) and is **absent**: d(resid) vs d(growth) slope -0.252 [-0.622,+0.118] p=0.16 (D), -0.020 p=0.93 (E), +0.006 p=0.96 (F), with 2 of 3 intervals excluding the Schaechter band k=0.45-0.80 h and the test carrying 2.9-5.2x the power needed. **Affected and by how much:** `growth_fgC_h` x6.0588, `respiration_C_per_C_h` and `resp_over_growth` x0.1650 - all exactly constant factors, so level only, `d log q/dT` identical to machine precision. **`CUE` is the one that moves materially and changes SHAPE** (not linear in the constant): 0.072-0.664 -> 0.241-0.922, `d log CUE/dT` -0.0587 -> -0.0436 (NLDM), -0.0476 -> -0.0362 (LB), -0.1646 -> -0.1461 (M9). Also: the two conversions disagree on **both** constants - 10.61x on volume and 0.57x on implied carbon density (175 vs 100 fg C um^-3) - partly cancelling to the 6.06x on carbon per cell, which makes a single typo unlikely. `reports/Q1_n0_check/report.md`. **Still Parsa's to resolve**; Q1 diagnosed only and changed nothing.  **ASSESSED 2026-09-16 (H1 TASK 3), NOT APPLIED.** Parsa sent `09_medium_constants.R` and `METHODS_carbon_conversions.md` (copied with their SHA-256 into `reports/H1_handover/parsa_1_9/`). His arithmetic reproduces his table exactly: N₀ = 1.8e9/V and carbon = 180 × V give 4.09e8 / 4.74e8 / 8.18e8 cells L⁻¹ and 792 / 684 / 396 fg C for LB / R2A / M9. **His script is safe** — it reads the finished table and writes only to a new figures directory. **His constants are not**, and his METHODS' claim that the change cannot reach the likelihood is true of the script and false of the constants: Q1 established the likelihood's observable `R_O2_mg_cell_min` contains N₀, and every committed derived table carries a single N₀ = 4.0e8, so the observable would move by **−15.6 % for the NLDM fits, −2.2 % for LB and −51.1 % for M9**. The shift is exactly absorbable by each fit's `resp_scale` (R², curve shapes and the within-medium evidence comparison are protected) but **not** by `resp_scale`'s absolute value, by any cross-medium comparison, or by any posterior already computed. **It is a likelihood change needing a new identifier and a re-gate. The decision is 1.36.** Full assessment: `reports/H1_handover/parsa_1_9_assessment.md`. |
| ~~1.10~~ | ~~**M9: fit or not?**~~ | — | **CLOSED 2026-09-09 (P4 TASK 4).** Fitted for all three configurations — the best growth fits in the exercise (R² 0.96–0.99). OTU 2 (`M9`, 7 non-monotonic rows) was excluded as a control, not a series. |
| ~~1.11~~ | ~~**`c_max` on LB**~~ | — | **ACTED ON 2026-09-09 (P5).** P4 applied the canonical 120 to LB and all three LB growth R² collapsed (0.83–0.90 → 0.16–0.20). His own LB fits chose **257 / 459 / 510**. 120 comes from a glucose/NLDM sweep and no LB sensitivity has ever been run. **One fit settles it: configuration D on LB at c_max ≈ 260, ~45 min.** **Outcome:** confirmed at source (256.7 / 459.3 / 509.9); the one chain was trapped in a dead mode by the warm start (3.20) and the question was answered at fixed parameter points instead — the cap alone moves LB growth R² 0.64 / 0.05 / −0.10 (D/E/F at 120) → 0.90 / 0.83 / 0.88 at his own caps, because 120 holds r_max at 1.1–1.8 against a measured 2.94 h⁻¹. **LB cap set to 450** (`gas_exchange.yaml` `carbon_cap.by_medium.LB`, his E/F nominal); 257 serves D only. Not tested above 450; no LB sensitivity to an unbounded cap exists — that is the remaining trigger. `reports/P5_lb_cmax/`. |
| 1.12 | **Chain length: every fit in this family is under-converged** | us | All nine P4 refits AND all six of Parsa's committed chains run ~9 autocorrelation times (chain/τ 6–12 against ≥40). Reaching the criterion is ~8 000 steps, ≈ 40 h for all nine. Until then no R² from either family is a converged posterior. The warm-start defect that lengthened P4's burn-in is fixed but untested at scale. **UPDATED 2026-09-09 (P6 D6): not a budget problem.** τ grows in proportion to chain length on every configuration-D chain (chain/τ pinned at ~9.7 over 1250 steps; the true τ is unknown and > 300 on all 16 parameters), so more steps have no ceiling — the family is **sampler-limited**, not step-limited. D NLDM halted at step ~1250; D LB and D M9 not started under this sampler. Medians of the twelve data-determined parameters are stable and quotable with a "not converged" label; intervals are not. **UPDATED 2026-09-09 (P7): not a walker-count artefact either.** D NLDM at 128 walkers, otherwise P6's fit exactly, read by a rule written before the run: τ_max 26.1 → 140.8 over 1500 steps, increments 26 → 20 per block (mean of the last three 21.4 against 10 for mixing), chain/τ 9.6–10.7, the carrier rotating — 10 % below the 40-walker curve and no plateau. **NOT MIXING.** The same applies to Parsa's six chains (36 walkers, same sampler). What it now needs is one of P6 D6's decisions — fix the four prior-determined parameters, narrow the discrepancy priors, change sampler, or quote medians only — none of which is compute. `reports/P7_walkers/`. **CLOSED 2026-09-09 (P8) with a conclusion, not a task.** PCA of the chains finds no ridge (PC1 16.5 % of the variance, τ 110–121 on every one of the sixteen components; the four prior-determined parameters carry 14 % of the slow loading), so fixing them removes nothing that is slow; the ensemble slice sampler (zeus) costs 11× emcee per step on this likelihood (one walker's sequential slice loop idles the pool, 10 % utilisation) and its τ rises at the same 0.10 N. **The family is sampler-limited and no sampling change tried — walkers, moves, slice sampling — fixes it.** Conclusion: quote the configuration-D medians (P4) with a "not converged" label; the credible intervals are not available from these chains; any change from here is a model decision (fix the four, or narrow the discrepancy priors), listed in P6 D6 and P8 D5, for the user. `reports/P8_ridge/`. **VERDICT 2026-09-09 (P9): ROUGH, STRUCTURAL.** Line scans of the log-likelihood through the MAP (fresh model per evaluation, 22 lines, ±1 posterior sd at 0.05 sd) find a piecewise-smooth surface with cliffs: 12 of 22 lines have a single 0.05 sd step exceeding 20 % of the line's range (median 39 %, up to 99 %), between cliffs the curves are exact parabolas, two axes (kappa_scale, f_metab) are exactly flat. The cliffs survive tightened Gurobi tolerances and a fixed dual-simplex method unchanged (16.7 / 18.2 / 18.4 units), and each of the three largest is the **respiration term at one cold temperature** (20–25 °C) where the LP's O2 uptake changes 2–4× across the step while growth moves 1–10 %. So neither fixing the four nor narrowing priors gives intervals from this likelihood as written: the fix is to the likelihood (see 1.15). `reports/P9_surface/`. **Awaiting P7** (`prompts/P7_walker_test_prompt.md`), which decides whether D6's options (i)–(iii) are needed. `reports/P6_convergence/DECISIONS.md` D6. **P10 (2026-09-09):** the respiration likelihood now has a tie-break, a variance floor and a continuous support for eciML1515 (default OFF in the core); the cliffs fall from 13–72 units to single digits and the surface is still not SMOOTH by P9's rule, so no chain has been run under it and the medians-only conclusion stands. **NOT CLOSED — RESTATED 2026-09-10 (P11), and the reason matters.** Moving the floor to the largest measured vertex jump (0.76 → 1.42) made all twelve of P9's lines SAMPLEABLE by an absolute rule (no 0.05 sd step above 5 log-likelihood units; largest 3.53), and **dynesty reached its dlogz criterion twice** — nlive 400 in 7,118 iterations and 111,420 evaluations (log Z −22.886 ± 0.164, n_eff 4,052), nlive 250 in 4,443 and 68,947 (log Z −24.567 ± 0.185, n_eff 1,974). **The two converged runs disagree: log Z by 6.8 combined standard errors, and 15 of 16 posterior medians by more than two Monte-Carlo errors, up to 50** (dTopt 1.51 against 9.39). The second run never reached the first's region — its best likelihood is 1.7 nats worse and its mass sits 4.5 nats lower — and its dlogz was satisfied anyway, because dlogz weighs the remaining volume by *the live points' own* maximum. **So dlogz < 0.1 is necessary and not sufficient, and no posterior for this family is established yet.** What is established: the surface is sampleable (a measurement of the likelihood, not of a run), and the convergence problem was never a sampling budget — it was a cliffed likelihood. What it needs: two runs at **nlive ≥ 800** with different seeds that agree, ≈ 10–12 h each. See 1.15 and 1.19, `reports/P11_nested/`.  **APPENDED 2026-09-10 (P14):** the surface has **no plateaus** (0 of 480 adjacent evaluations exactly equal across twelve lines), so the one property that would make nested sampling structurally unable to converge here is **absent**. What remains are discontinuities of 0.05–0.59 units from the LP's O₂ vertex at cold temperatures — the P9 mechanism, two orders of magnitude smaller than when it was diagnosed.  **APPENDED 2026-09-11 (P15):** the first direct measurement of this posterior's **geometry**, from a sampler's own 800 live points: covariance **condition number 1,457**, smallest eigenvalue **1.947e-04** in a direction dominated by **`dTm` +0.903 / `tm_scale` −0.217**, and **corr(dTm, tm_scale) = +0.831**. Three parameters sit essentially **at their priors** (`f_metab` 0.273, `dCp_scale` 0.266, `f_maint` 0.265 against 0.289). The family's problem is now named: not a plateau, not a budget, but a **thin correlated ridge from a non-identified pair**. |
| ~~1.13~~ | ~~**E/F tie-break: pFBA, min-O2 or max-O2 for the respiration likelihood on an LP face**~~ | — | **CLOSED 2026-09-09 (P10): pfba chosen**, as `flux_tpc(tiebreak="pfba")` (growth held at its optimum, total absolute flux minimised, every solve at 1e-9), default OFF in the core, ON for eciML1515. The D3a instrument reads **0.0000 on D NLDM, D LB, E NLDM, E LB and F NLDM**; **F LB is 0.05–0.5** between calls and stays held (3.21). The face bounds at Parsa's E LB θ (37/40/45/50 °C): min_o2 38.07/46.60/40.70/28.48, max_o2 38.24/46.66/40.74/28.49, pfba at the low end — 0.17 wide at his θ, [0, 190] at P4's MAP. Cost ×4.5 per evaluation. `reports/P10_respiration_likelihood/` D1. |
| 1.14 | **Whether a Li-style calibration is worth attempting** — predictor as wide prior, narrowed against the measured Candida TPCs | PI | Li et al. carried a sequence-predicted Topt as a wide prior (width = the predictor's RMSE) and let the measured curves narrow it. Given the A1 noise floor of 0.043 C between clades, whether the Candida TPCs carry enough signal to narrow anything is the question. See `reports/Y1_yeast_audit/` PART D. |
| 1.5 | **`common_network.py` result** — does the optimum still compress on a common scaffold? | Ilgaz | Never recorded in `gem/notes/`. Note the K1 finding that makes it partly moot: the two draft models ARE the *auris* network with genes reassigned, so the control is near a no-op for them and informative only for *C. parapsilosis*. |
| 1.6 | **Did any Candida audit touch lipid or membrane pathways?** | Ilgaz | Bears on §6a. `allocation_and_trehalose.py` suggests compatible solutes were looked at; membranes unknown. |
| 1.7 | **`15_run_seq2tm.py` truncation bug** — truncates at 1022 aa citing a non-existent ESM-2 positional limit; committed predictions are untruncated, so the script cannot reproduce the data beside it (up to 2.6 °C) | Ilgaz — **told, not yet fixed** | A live reproducibility break in his repository. |
| 1.15 | **Decide the respiration likelihood: the surface is discontinuous where the LP's O2 uptake jumps** | PI | P9 found the configuration-D log-likelihood is piecewise smooth with cliffs of 13–72 units within one posterior sd of the MAP, each carried by the respiration term at one cold temperature where O2 uptake changes 2–4× between LP vertices while growth barely moves (`reports/P9_surface/`). No sampler and no model reduction gives credible intervals from that surface. Three ways to make the likelihood a smooth function of the parameters, none taken: (a) a tie-break that makes O2 unique at the growth optimum at every temperature — pFBA or a lexicographic O2 objective — the same change 3.21 needs for E/F, costing ~2× per evaluation and a re-run of the P3 gate; (b) a noise-aware respiration term that treats the vertex spread as model error (an interval or a widened variance at low O2), which changes what the respiration R² means; (c) a smoothed surrogate of the growth/O2 response for sampling only. Until one is chosen, the family's posteriors are medians with a "not converged" label. **RESTATED 2026-09-09 (P10):** routes (a) and (b) were built as core options (default OFF, ON for eciML1515) and measured. The tie-break resolves the E faces (F LB not); the variance floor (0.76, the model's O2 granularity at 20 °C) with a continuous support cuts every cliff by an order of magnitude — P9's −70/−32/+23 become −6/−3/+2 — **and the surface still reads ROUGH by P9's rule on two of twelve lines** (steps of 7.8 and 2.2 units, 27 % and 32 % of ranges that shrank to 29 and 7). What remains is single digits: the one vertex jump above the floor (1.42 in log at 25 °C), 1–2-unit O2 jumps at 20 °C, and **growth-term kinks of 1–3 units** that no respiration change touches. No fit was run. The decision now: a floor at the largest jump (≈ 1.4), the same treatment of the growth term, or the surrogate route (c) for both — `reports/P10_respiration_likelihood/` D5. **ACTED ON 2026-09-10 (P11); the surface question is closed, the posterior is not.** The route taken was (a) the tie-break plus (b) the variance floor, with two decisions executed: the floor sits at the **largest measured vertex jump (1.42 in log O2), not the modal temperature's**, and the **growth term is not floored** — its 1–3 unit kinks are the LP's piecewise response and inflating the primary data's variance to suit a sampler would trade information for convenience. The surrogate route (c) was not needed. Cost, stated: the respiration sd is now at least 1.42 in log everywhere, a factor-4 band, and the converged fit accordingly buys growth R² (0.900 against P4's 0.854) at the price of respiration R² (0.626 against 0.795). Any respiration R² from this family must be quoted with the floor beside it. **ADDENDUM 2026-09-10 (P12 addendum 1): the SUPPORT handling is a separate, unclosed decision inside this item, and it discounts rather than bounds.** The term's support is `w = min(1, g/g_s)`, `g_s = 0.01`, a function of the model's PREDICTED growth, multiplying the respiration term only (`calibration_multi.py:299-301`); the growth term is linear and untouched. P10 introduced it for a real defect — the hard mask at `g ≥ 1e-4` switched a whole temperature in or out as a step, which was half of P9's cliffs — and it fixes that. But at a near-dead point it hands back **16.7 log-likelihood units** against ~1.2 at every live point, so a model that predicts almost no growth is charged almost nothing for predicting the wrong respiration. Removing the discount (`w ≡ 1`, hard mask kept) widens the θ_A − θ_B gap from +24.5 to **+40.0**. Removing support handling altogether is **not available**: at 15 °C the model does not grow at θ_A, θ_B* or θ_P4 and `flux_tpc` returns **NaN** for O₂, so there is no prediction to score. The open question is therefore which BOUNDED form replaces a discount, not whether support handling is needed. Not changed in P12. Numbers: `reports/P12_modes/addendum1_schemes.csv`, DECISIONS D4. See 1.21. |
| 1.16 | **Should the Candida strains' respiratory audits use the parsimonious vertex?** | PI (K-series) | P10 ran the K5 coupling-ion audit on the four repaired Candida models at both the plain growth optimum and cobra's pfba solution at the same growth (information only, nothing adopted): the translocation-only chain-supply fraction is unchanged to three decimals in all four (2.000 / 2.722 / 2.133 / 1.120), but the figure including in-compartment proton chemistry moves for two — *C. haemulonii* 3.25 → 3.53, *C. duobushaemulonii* 2.68 → 3.23 — so the solver's vertex choice was carrying part of the K5 story there. Whether the Candida likelihoods and audits should read the pfba vertex is a K-series decision, to be made against the measured TPCs when the E. coli recipe ports (§0). `reports/P10_respiration_likelihood/task4_candida_pfba.csv`. |
| 1.17 | **Run the remaining eight gas-flux fits under the new likelihood, or not** | PI (blocked) | P11 converged configuration D on NLDM in 4.8 h and 111,420 evaluations. Projected at the same evaluation count and P10's per-fit tie-break costs: **D LB 4.5 h, D M9 4.8, E NLDM 4.7, E LB 5.0, E M9 4.8, F NLDM 4.8, F M9 4.8 — about 33 h in total**; **F LB is HELD** (P10 D1: its tie-break is not exact at 1e-9, so its likelihood is not yet a function of its parameters). Two caveats: the projection assumes each fit needs a comparable number of iterations, which scales with its own information H and is unmeasured elsewhere; and ~1 h of P11's run was dynesty's single-core unit-cube phase, which `first_update={'min_eff': 30}` would remove. `reports/P11_nested/task4_costs.csv`. **Blocked by 1.19:** running eight more fits at settings whose reproducibility has not been established would multiply the problem rather than solve it. **RE-COSTED 2026-09-15 (T2):** the driver measured **11.2 h and 13.4 h per 16-D run at 4.3–5.8 evaluations s⁻¹ on 16 processes** (235,542 and 206,277 evaluations), not P16's 8–9.6 h; eight fits at that rate ≈ **100 h**, and a fresh-model-per-evaluation remedy for 1.34 would multiply it by ~4–5. Blocked by 1.34.  **STILL BLOCKED 2026-09-10 (P13):** the two runs that would have unblocked this were not started (TASK 3 stop; see 1.19, 1.23). No costs are updated.  **STILL BLOCKED 2026-09-10 (P14):** the two runs were again not started (1.23).  **STILL BLOCKED 2026-09-11 (P15):** run 1 crashed and run 2 was not started. |
| ~~1.18~~ | ~~**Finish the second-seed reproducibility check**~~ | — | **DONE 2026-09-10 (P11): it FAILED.** The nlive 250 / seed 2 run converged on its own criterion and disagrees with the nlive 400 run by 6.8 sigma in log Z and by up to 50 Monte-Carlo errors in the medians; it never reached the first run's region. Superseded by 1.19. `reports/P11_nested/task2_seed_compare.csv`. |
| 1.19 | **Establish a posterior that two runs agree on: two nested runs at nlive ≥ 800, different seeds** | PI | P11 showed dlogz < 0.1 is necessary and not sufficient here: runs at nlive 400 and 250 both met it and disagree (log Z 6.8 sigma; 15 of 16 medians beyond two MC errors). nlive 250 is below dynesty's guidance for multi-ellipsoid bounding in 16 dimensions (25 × D = 400) and 400 sits exactly at it, so neither is demonstrated adequate. **Cost, from P11's measured 0.155 s per evaluation and its H = 9.22: ≈ 10–12 h per run, so ≈ 20–24 h for the pair.** Cheaper things to try first, in order: `first_update={'min_eff': 30}` (P11 D4 — dynesty ran its first 1,250 iterations on one core, costing an hour); and checking whether the disagreement is multimodality by seeding one run's live points from the other's high-likelihood region. Until this is settled, **no posterior from this family should be quoted**, and 1.17 is blocked. `reports/P11_nested/` D8.  **RESTATED 2026-09-10 (P12): the requirement is unchanged but its PURPOSE has narrowed, and one prerequisite is now ahead of it.** P12's basin map finds **ONE live basin**: theta_A and theta_B* — the two runs' best samples — have a bottleneck barrier of **0.266**, which is noise. So the two runs did not find two modes; they explored one basin to different depths, and the disagreement is a stopping-rule failure, exactly as P11 concluded. Two agreeing runs at nlive ≥ 800 are therefore still what closes this, but they are no longer needed to *arbitrate between modes* — only to establish the single posterior. **Do not start them until 1.21 is settled**: as the likelihood stands a sampler can spend real mass on the dead basin (peak predicted growth 0.000 /h, respiration term −0.017), which is what the second seed did. Per-basin sampling on restricted priors (§0b) is **not needed** — there is one live basin. Cost unchanged at 10–12 h each. `reports/P12_modes/`.  **RESTATED 2026-09-10 (P13): still open, and now blocked on a DIFFERENT thing.** 1.21 is closed, so the support obstacle is gone. The runs were nevertheless **not started**, because P13's TASK 3 found the surface **NOT SAMPLEABLE at p38**: `axis:topt_scale` carries a step of **8.55 log-likelihood units between two FEASIBLE points** at +0.90 → +0.95 sd, against the absolute rule's 5. It is **96 % growth term**, and it is **identical under the old and new support handling (8.5519 vs 8.5517)**, so it predates P13. It is smooth curvature rather than a cliff — the steps run −0.71 … −5.63, −7.25, −8.55, −8.46, monotone, at a log-likelihood 40 units below p38 — but that was **not** used to override a rule fixed in advance. See 1.23.  **STILL OPEN 2026-09-10 (P14).** The blocker moved but did not clear: the line that stopped P13 (`axis:topt_scale`, 8.55 units) is now shown to be **steepness, not a discontinuity**, and the surface has **no plateaus at all** (0/480). Four lines retain genuine discontinuities of **0.05–0.59 units**, all of them the cold-temperature O₂ vertex switch. Whether that blocks the runs is 1.23 and is the PI's call. Cost unchanged at 10–12 h each, sequential.  **STILL OPEN 2026-09-11 (P15), and the obstacle has changed again.** The sampleability question is closed (1.23), and the run then **CRASHED** rather than converging or hitting its cap: at iteration **11,547**, dlogz **2.168**, log Z **−25.730**, ~9.9 h, dynesty raised *Slice sampler has failed to find a valid point* with **denormal** bracket steps (−5.4e-323 / 5e-323 / 1.04e-322) and a proposal bit-identical to the current point. **Deterministic** — a resume from the checkpoint reproduced it exactly. **No samples were written and run 2 was not started.** See 1.24. |
| 1.20 | **The `dTm` decision: the fit needs a 3–4.5 K shift against a MEASURED meltome** | PI | Forward-referenced by §0b step 2 since 2026-09-10; P12 now puts numbers under it and they are worse than the sequence anticipated. **Every** converged live endpoint requires `dTm` between **−3.07 and −4.50 K** (A −3.81, p38 −4.02, B\* −4.08, p81 −4.08, P4 −4.07, p50 −3.07, p83 −4.50), and the two weight-propped poor endpoints require −10.18 and −13.07. **The only point in the whole map with `dTm` = 0 is the DEAD basin** — 0.000 exactly, with `dTopt` 13.873 and predicted growth 0.000 /h at every measured temperature. §0b step 2 hoped that constraining `dTm` would collapse the multimodality by killing a stability-shift mode; P12 shows there is no second live mode to kill, and that **the meltome-honouring region of parameter space contains no growing model**. So the choice is starker: either the measured meltome is not the right constraint on this model's `Tm`, or the model cannot fit these data without contradicting it and the shift is a **failure to explain**, not a parameter to fix. Either way it is a modelling decision, not a fit. See 1.14, §0a R3, `reports/P12_modes/` D8. | **SCREENED 2026-09-10 (Y3), and one sentence above is retracted.** The claim that *the meltome-honouring region of parameter space contains no growing model* is **wrong**: with `dTm` = 0 **and** `tm_scale` = 1 both held and the four catalytic parameters re-optimised to convergence, the model grows at **1.659 /h** at log L **−14.786** — **7.60 units** worse than p38 and pressed against two prior ceilings (`dCp_scale` 4.0, `topt_scale` 1.35). P12's inference was sound for what P12 did: its only `dTm` ≈ 0 point was an *unconstrained* optimum of the 16-dimensional log posterior, a different object from a *constrained* optimum with both Tm parameters pinned. **And the −4 K itself is not required:** the profile of `dTm` with catalysis free is flat — 4.02 K for **0.077** log L units, alive throughout — but the parameter that pays is **`tm_scale`**, not a catalytic one, and both solutions put the least-stable few per cent of enzymes **4–6 °C below the measured meltome** (1st percentile 38.7 °C via the shift, 36.7 °C via the stretch, against 42.6 °C measured). So the **value** −4 K is a parameterisation artefact; the contradiction with the meltome's **low tail** is not. Third option now on the table: the model can honour the meltome's *mean* and cannot honour its *low tail*. **`dTm` and `tm_scale` are not jointly identified** — add to §0a R2. `reports/Y3_tm_shift/` **RESTATED 2026-09-13 (T1):** the reduced runs' `dTm = 0` conditioning is unchanged and T1 adds nothing to the meltome question itself; but the **curvature trace** on `tm_scale` and `dTopt` (T1 TASK 3, item 1.31) is where any implementation kink on the stability axes would show, and Y3's per-enzyme tail requirement remains the reported quantity. Nothing here fixes a further parameter. |
| 1.22 | **One live basin: replace per-basin sampling with a single run, once the support is settled** | us | P12 recommends **(c) one dominant basin**, stronger than that phrasing: among models that grow there is exactly one, and the second basin is a zero-growth model separated by 13.9 units that survives scoring only because the support weight charges it −0.017 instead of a full respiration penalty. **§0b step 5 (per-basin posteriors on restricted priors, combined by volume fraction) is therefore unnecessary** and should be struck once 1.21 is decided; what replaces it is a single well-converged run on the live basin, which is 1.19. **RESTATED 2026-09-16 (T3): this was filed as a cost optimisation and it is not one.** T3 measured Gurobi's native lexicographic (hierarchical) objectives as scheme C, on 22 hashed inputs against a fresh-process reference: it is **faster** than the current two-solve path (1.49 s against 1.79 s per evaluation) but it **returns a different vertex** — O₂ differs from pFBA by up to 4.58 mmol gDW⁻¹ h⁻¹ on D NLDM (47 % relative) and 8.40 on E LB (96 %), growth by up to 2.27 /h on E LB — and **111 of its 150 E LB evaluations returned `numeric`**. It is also not deterministic (max deviation 0.223 on D NLDM). **A different tie-break is a different model**, so this cannot be adopted as a correctness fix for 1.34 without re-establishing the P3 gate and every P10–P16 result that depends on the pFBA vertex. Whether a *correct* single-solve formulation exists is open and unmeasured. `reports/T3_determinism/report.md`. This is a simplification of the plan, not a new task, and it is recorded so the sequence is not run as written. `reports/P12_modes/` TASK 4.  **RESTATED 2026-09-11 (P15): it is a cost optimisation, not a correctness fix, and that is now measured.** The lexicographic tie-break would remove the O₂-vertex discontinuities P14 sized at **0.145–0.885 log-likelihood units** — but the **growth-term kinks are 1–3 units** and no respiration change touches them (P10), so larger discontinuities would remain from another term. It does not unblock 1.19, and it would not have prevented P15's crash, whose cause is a degenerate direction rather than a jump. |
| 1.24 | **Remove the `dTm`/`tm_scale` ridge, or change the sampler — the decision P15's crash forces** | PI | P15's run died deterministically on a degenerate direction, and the direction has a name: **`dTm` +0.903 / `tm_scale` −0.217, `corr` = +0.831 among the live points**, smallest covariance eigenvalue **1.947e-04** in a unit cube whose largest is 0.2835. **This is exactly the pair Y3 showed is not jointly identified, confirmed by a wholly independent route** — Y3 profiled the likelihood, P15 watched a sampler's live points collapse onto the same correlation. Two redundant knobs on one axis give a ridge of ever-shrinking width, and any sampler that brackets along a direction will eventually fail on it. **(a) Fix `tm_scale` (or `dTm`) at nominal and re-run** — removes the degeneracy at source, drops to 15 dimensions, converts an unidentifiability into a stated limitation; this is **§0b step 3** and item **1.20**, and it is the recommended route, at the same cost as this run. **(b) Change the sampler** (`rwalk`, or more `slices`) — cheapest in thought, but it would sample a known degeneracy and forfeit comparability with P11, which used `rslice`. **(c) Both**, (a) as the scientific run and (b) as a robustness check. P15 did **not** choose, because the settings were fixed in its D1 before the run. `reports/P15_posterior/` D2–D3. |
| 1.23 | **Decide whether the absolute smoothness rule should distinguish CURVATURE from a CLIFF** | PI | Raised by P13 (2026-09-10) and left deliberately undecided. The rule — no single 0.05 sd step above 5 log-likelihood units — was written in P11 to catch **cliffs**: isolated jumps among small steps, which is what P9 measured (`0.1, 0.1, 70, 0.1`). At p38 it now fails on `axis:topt_scale` at **8.55 units**, but the steps there are **monotone and smoothly increasing** (−0.71, −0.83, −1.11, −1.18, −1.44, −1.83, −2.39, −3.05, −4.15, −5.63, −7.25, −8.55, −8.46) at a log-likelihood of −47.8, **40 units below p38** and carrying essentially no posterior mass. That is a steep tail, not a discontinuity, and nested sampling is untroubled by steepness. **P13 did not override the rule**, because inventing a criterion after seeing the data is the error P12 D5/D7 recorded. The decision is: (a) keep the rule as written and treat the surface as unsampleable, which blocks 1.19 and 1.17 indefinitely; (b) add a second-difference or isolation test so the rule separates curvature from a jump, **written down before it is applied** and re-run on P9's twelve lines so it is calibrated against known cliffs; or (c) restrict the rule to the region carrying posterior mass, e.g. within the 99 % credible region rather than ±1 sd of an optimum. **A related hazard is now in §4**: a sampleability verdict measured at ONE centre is not a property of the surface — P11's was 3.20 on this line at θ_A and is 8.55 at p38. `reports/P13_support/` D7.  **ANSWERED IN PART, AND SHARPENED, 2026-09-10 (P14).** The rule was replaced, not patched, by a criterion written before its data: **(a)** discontinuity by **grid refinement** (h, h/2, h/4, h/8 — for a bounded derivative |Δ| halves; for a jump it converges to the jump height), **(b)** plateaus — runs of *exactly* equal likelihood, which is what actually voids nested sampling's volume shrinkage — and **(c)** feasibility boundaries exempt. Outcome: **`axis:topt_scale`, the line that stopped P13 at 8.55 units, tests SMOOTH** (ratios 0.507, 0.515, 0.504), so the old rule's verdict was **steepness**, demonstrated rather than argued. **(b) passes perfectly: 0 of 480 adjacent evaluations exactly equal on any of the twelve lines.** But **four lines carry genuine small discontinuities** — `dCp_scale` 0.379, `PC1` 0.145, `PC2` 0.467, `random1` 0.885 — and all four are **one mechanism**: 97–100 % respiration term, growth unchanged to five decimals, **O₂ moving 0.57–1.86× at a single cold temperature**. That is P9's LP vertex switch, made deterministic by P10's tie-break and cut by the 1.42 floor from 13–72 units to 0.05–0.59. **THE DECISION NOW OPEN IS NARROWER AND IS THE PI'S:** (a) **lift the discontinuity conjunct and run** — a jump is not a plateau, and nested sampling depends on X(L), the prior mass above L, so a discontinuity leaves an interval of likelihood values carrying no mass (harmless) whereas a plateau puts an atom in the distribution of L (fatal), and the surface has none of the latter; (b) **implement 1.22, the lexicographic tie-break, and re-test** — it addresses the exact mechanism and is excluded from P13 and P14 by name; or (c) keep the rule and leave 1.19 and 1.17 blocked. P14 did **not** lift it itself, because moving a threshold after seeing its data would be the fourth time in this series. `reports/P14_posterior/` D1–D3.  **CLOSED 2026-09-10/11 (P15): the discontinuity conjunct is LIFTED, by PI decision, on an argument that predates the data.** Nested sampling estimates Z = ∫L dX and requires only that **L have no atoms under the prior**: an atom makes X(λ) jump and voids X_i ≈ exp(−i/nlive). **A plateau creates that atom; a jump does not** — it leaves a *gap* in L's support carrying no prior mass, and Z = ΣL_i w_i stays a valid Riemann sum in X. The criterion named plateaus as the failure mode and then required no-jumps as well; those are different objects. P14 measured **0 of 480** adjacent evaluations exactly equal (no atoms), and its four real jumps are **0.145–0.885 units** against the **1–3 unit** growth kinks P11 accepted as irreducible — so 1.22 would remove the smaller discontinuities while larger ones remain from another term. **P14 was right to refuse to lift this itself**; the correction required someone not holding the pen. `reports/P15_posterior/` D0. |
| ~~1.21~~ | ~~**Decide the respiration term's SUPPORT**~~ | — | **CLOSED 2026-09-10 (P13): `clamp`.** Raised by P12 addendum 1 (2026-09-10), characterised and deliberately not acted on. The weight `w = min(1, g/g_s)` with `g_s = 0.01` scales the whole per-temperature respiration term by the model's own predicted growth, so the less a parameter set grows, the less it pays for getting respiration wrong. Measured credit, in log-likelihood units: **θ_A 1.263, θ_B 16.696, θ_B\* 1.115, θ_P4 1.234**; the A−B gap moves +24.535 → **+39.967** with the discount removed. It is not manufacturing the P11 seed disagreement — θ_B is a median artefact that neither run visited as a mode (25.9 units worse than seed 2's own best sample, peak predicted growth 0.163 /h against an observed 2.076), and θ_B\* is not propped up. But it does let dead regions of parameter space score far better than they should, which is exactly what a basin map is sensitive to. Options: (a) keep it, and always report peak predicted growth beside any log-likelihood; (b) replace it with a bounded penalty — score respiration at full weight but cap each temperature's contribution, so the term is continuous AND a dead model is charged in full; (c) make aliveness explicit in the model rather than in the likelihood's support. **Constraint on all three:** support handling cannot simply be dropped — where the model is dead `flux_tpc` returns NaN for O₂ and there is nothing to score. **Anything decided here invalidates P11's sampleability scan on the cold lines (15–25 °C)**, where predicted growth is small and `w < 1`; the floor and the tie-break are unaffected. `reports/P12_modes/` D4.  **THE FORM CHOSEN, and why it is not the one recommended.** `respiration.support: clamp` with `weight_floor: 1.0` is now ON for eciML1515: the mask becomes `isfinite(o2) & (o2 > 0)`, so a **FEASIBLE-NOT-GROWING** temperature is scored at full weight instead of being discarded by the growth mask. The justification is stronger than "it removes a discount": of the 15 dead temperatures across P12's twelve converged endpoints, 11 are genuinely INFEASIBLE (all of them the dead basin) and **4 are FEASIBLE-NOT-GROWING with O₂ = 0.525–5.674 — and among the eleven LIVE endpoints it is 4 of 4**. A non-growing cell still respires for maintenance, so **the mask was discarding real predictions and clamp scores them**. The recommended form — impute O₂ = 0 where growth stops — was **withdrawn on physiology and measurement**: it fails P10's D3a state gate at the dead basin by **119.14** log-likelihood units, its continuity step is 2,300 units per 0.05 sd, and its apparent live–dead gap is the epsilon (774 / 1,553 / 2,511 at 1e-6 / 1e-9 / 1e-12). Cost, stated: p38 loses **2.8 units** and the live–dead gap moves 11.691 → 11.245 — small, because the discount was never the dead basin's main protection; **the NaN mask is, and that is irreducible**. Gate 79/79 and 60/60 with the option OFF; the P3 gate table is byte-identical with it ON. `reports/P13_support/` D3–D5. |

## 2. Ready to start

| # | Item | Notes |
|---|---|---|
| 2.1 | **A3 follow-through: gene content → mechanism** | A3 measured that models see only ~2–5 % of the gene-content difference (0–15 genes in-model vs 122–647 in proteome), and that AOX and the glutaredoxins are in NO model. Nothing has been done with that. |
| ~~2.2~~ | ~~**Membrane-area constraint on Candida**~~ | **DONE 2026-09-08 (K4).** Built and applied; `reports/K4_membrane/report.md`. **It cannot carry the interspecies comparison, for two independent reasons.** Structurally, the respiratory chain is not load-bearing in three of the four models (the three *Candidozyma*; TASK 1), so an area budget there binds on ATP synthase and not on respiration. Parametrically, no footprint differs between the species — there is no Candida or fungal equivalent of Szenk 2017 (TASK 2). The mechanism is **available and not tested**; 3.8-3.11 are what would change that. |
| 2.3 | **K3 — retire the Candidas fork** | N1 prepared the patch (unapplied, `git apply --check` clean) and confirmed nothing in etcGEMs needs `$CANDIDAS_ROOT` at run time now the gate has a fixture. Needs a human to apply it in Ilgaz's repository. |
| 2.4 | **`_toy/resolved_config.yaml`** structurally stale (numbers fine, 6.2e-15) | Listed by N2, not fixed. Trivial. |
| ~~2.5~~ | ~~**PART C at Li et al.'s POSTERIOR, not their prior**~~ | **CLOSED 2026-09-09 (Y2).** Downloaded (10.5281/zenodo.3996543 v2.0, md5 verified) and run at the posterior median and all 100 posterior particles. **The asymmetry survives in direction and is far more consistent at the posterior** — the 99 % plateau widens under the substrate cap in **93 %** of their posterior models (1.5 → 7.3 °C) against 35 % of prior models, and T_opt moves further than CT_max in **92 %** against 50 %. **But the margin narrows and Y1's 10.09 / 0.81 °C must not be quoted as a property of their calibrated model:** at the posterior median it is 8.46 / 4.27 °C, because a substrate cap now drops CT_max from 43.0 to 38.7 °C. Y1's prior run reproduces byte-identically. `reports/Y2_regime_posterior/`. |
| 2.6 | **The shared `.venv` lives in the main checkout** | `etcGEMs/.venv` is the only interpreter, so a second worktree borrows one from a directory a long run may be using. Read-only in practice; harmless so far. If `../etcGEMs-synthesis` becomes standing (Y1 PART F), move the venv somewhere neutral or duplicate it. |
| ~~2.7~~ | ~~**P7 walker test**~~ (`prompts/P7_walker_test_prompt.md`) | **DONE 2026-09-09.** Not a walker-count artefact: NOT MIXING at 128 walkers by the pre-registered rule. D6's options (i)–(iv) are the real menu. See 1.12 and `reports/P7_walkers/`. |
| 2.8 | **E1 was never run, and E2 needed it** | E2 (the deck) found `reports/E1_paper_register/` absent — not on `main`, not on any branch, nowhere in the history, no `e1/*` remote branch and no "E1:" commit. Only `prompts/E1_ecoli_paper_restructure_register_prompt.md` exists. E2 rebuilt the two things it needed from primary sources — the UNSUPPORTED status of the old *E. coli* intervals, and the gas-flux inventory — and says so on the record. **Still missing: the sentence-by-sentence correction register for `reports/ecoli_tpc/report.qmd`, and the restructure options.** The paper still states things the evidence contradicts and nothing yet records which sentences. `reports/ecoli_deck/DECISIONS.md` D0. |
| 2.9 | **`references.bib` mis-titles the MRes thesis** | `reports/ecoli_tpc/references.bib` gives `@Madkaikar2023` as *"Predicting the temperature dependence of microbial metabolism with enzyme- and temperature-constrained genome-scale models"*. The thesis is **"Predicting the thermal niche of a ubiquitous bacterium using whole genome sequence"** (Imperial College London, MRes CMEE, August 2023). Corrected in `reports/ecoli_deck/references.bib` only: the `ecoli_tpc` copy is cited by the paper and by `reports/activation_energy/`, so fixing it there is a paper edit and belongs with 2.8. `reports/ecoli_deck/DECISIONS.md` D8. |
| 2.10 | **Eight committed figures are illegible on a slide** | E3 measured every figure in the deck against a threshold fixed in advance (a tick label must render at ≥ 9 pt, i.e. rendered-to-native scale ≥ 0.9, `reports/ecoli_deck/DECISIONS.md` D17). The three figures the deck owns were regenerated at slide width and pass (0.91–0.94). The **eight borrowed from `reports/ecoli_tpc/`, `reports/ecoli_gasflux/` and `reports/P9_surface/` cannot**: they are journal figures, 432–1224 pt wide natively against a 398 pt slide, so their ceiling is ≈ 0.47 and `task1_scan.png` is 0.15. **The fix is to give their producing scripts a slide-width figure size** (`reports/ecoli_tpc/assemble.py`, `scripts/gasflux_figures.py`, `reports/P9_surface/task1_lines.py`) — which rewrites those reports' committed assets and needs their model outputs, so it is a deliberate job, not a deck edit. `reports/ecoli_deck/measure_figures.py` exits 1 until it is done. Interim workaround used for the worst case: the elasticity result is now a **typeset table** on the slide, which is legible and loses nothing. |
| 2.8 | **Ground κ (`translation_coeff`) in the proteome data instead of auto-calibrating it** | κ is the effective ribosomal protein demand per unit biomass flux in the biosynthesis cap, $\kappa v_\text{bio} \le f_\text{bio} P_\text{tot}$ (`report.qmd` @eq-biocap). It is **not measured**: it is auto-calibrated once at build time so that the metabolic pool and the translation cap are *exactly co-limiting* at the nominal split and $T_0$. That is good hygiene — switching the sector layer on does not move the nominal prediction — but it embeds a modelling assertion (translation and metabolism equally limiting at the reference point) as though it were a constant, and it gives a single temperature-independent value. **Nothing in the calibration tests it:** the paper's own sensitivity section calls `kappa_scale` *inert* at the peak (the growth-law biosynthesis cap is not the binding constraint there), the calibration reports it "stays near its prior", and P9/P11/P12 put it in the FLAT class — `range_logL` exactly 0.0 along its axis and the prior centre in all twelve independent optimisations. So the auto-calibrated value is neither confirmed nor refuted by any fit. **It is grounded-able from data already committed.** Scott et al. 2010 [@Scott2010] measure translational capacity $\kappa_t$ directly, and the model already uses its *slope* ($s = 0.33$ h $\approx 1/\kappa_t$) in coupled mode while auto-calibrating the *level*. More directly, the Wang et al. 2026 proteome [@Wang2026] that sets $f_\text{bio}$ per medium and temperature also carries the ribosomal fraction; paired with the growth rate at which each proteome was measured, that yields κ **as a function of temperature**, which a single build-time value cannot be. Cheap — arithmetic on a committed table, no new experiment and no fit. Two things to check rather than assume: whether the Wang tables record the growth rate alongside each proteome, and whether κ derived that way agrees with the co-limitation value at $T_0$ (a disagreement is itself the finding). **Context:** the biosynthesis cap has no equivalent in Li et al.'s etcGEM, which is a GECKO model with a single pool and no separate translation constraint — so this is a genuine addition here, and worth grounding for that reason. ME-models parameterise the same physics mechanistically from measured elongation rates. |
| 2.11 | **The respiration and growth observables are not statistically independent** | us | Q1 D5 derived the biomass integral from the committed columns as `N0*(exp(r*T_end_min)-1)/r`, exactly (max|ratio-1| 6.9e-14 on R2A/LB n=117, 7.1e-14 on M9 n=66). So `R_O2_mg_cell_min` = `C_tot_O2` divided by a function of the **fitted growth rate `r`** - the same `r` that, times 60, *is* the growth observable. The likelihood multiplies the growth and respiration terms as though they were independent, and they share `r`. Magnitude unassessed: it would need the joint uncertainty on `r`, which the derived tables do not carry. Also worth noting that the integral is **exponential** - the fitted `K` appears in the table but enters no derived column - though the fit window is temperature-adapted so `r*T_end` stays at ~3.0-3.3 through the mid-range, which is why this introduces no hidden temperature dependence. `reports/Q1_n0_check/report.md` TASK 4. |
| 2.12 | **`references.bib`: `Cooper2007` is a 2001 paper, and nothing in the bib covers cell size** | us | Q1 TASK 3 needed the cell-size/growth-rate relation and found the repository cites no source for it - `Basan2015` and `Scott2010` are proteome allocation against growth rate, `Mairet2021` is temperature dependence of growth laws. Separately, the key `Cooper2007` holds Cooper, Bennett & Lenski **2001**, *Evolution* **55**:889-896: the key and the `year` field disagree, in all three copies of `references.bib` (`ecoli_deck/`, `ecoli_tpc/`, `activation_energy/`). Q1 cited Schaechter, Maaloe & Kjeldgaard 1958 in its report text rather than add to a bib on another branch. Cheap to fix; do it with the next bib edit. **Note also a pre-existing collision: two rows in this section are both numbered 2.8** ("E1 was never run" and "Ground kappa"), left as found rather than silently renumbered. |

## 3. Deferred, with triggers

| # | Item | Trigger to act |
|---|---|---|
| 3.1 | **Re-run `decompose_tuned` + `elasticity_tuned`** to match `control_tuned`'s model state | When that dissection material is used in a paper. Until then P2 TASK 5 annotates it. |
| 3.2 | **`calibration_vanderlinden`** (4 h 28 min emcee) | When a specific number from it is needed and must be current. |
| 3.3 | **Full E. coli regeneration** | Paper time, and then only the directories that paper uses. Reports are logs; provenance stamps (P2 TASK 4) are the standing fix. |
| 3.4 | **Extend the E. coli proteome above 37 °C** | This is a measurement, not a modelling job. Until then the 37–44 °C bit-identical shoulder is documented as a limitation (P2 TASK 5). |
| 3.5 | **DLTKcat on the four Candida proteomes** | A1 recommended against for now: wrong half of the curve, no benchmark, ~50,000 predictions. Revisit only if the kinetic envelope becomes load-bearing. |
| 3.6 | **Per-protein *S. cerevisiae*/*S. uvarum* Tm from the authors** | Would allow A1's strongest test (correlation of measured against predicted *differences*), currently impossible — only the summary statistic is published. |
| 3.7 | **A measured meltome for any *Candida*** | None exists. Would replace the load-bearing literature benchmark with own data. |
| ~~3.8~~ | ~~**Repair the mitochondrial proton accounting**~~ | **CLOSED 2026-09-08 (K5 TASK 2).** Costing the transport does not fix it; a direction constraint on uncosted reversible carriers does, at 36-38 % of predicted growth. The chain goes from supplying 0.04-0.05 % of ATP synthase's protons to 200-272 %. Lives in `configs/experiments/candida_B5_respire.yaml` as rung B5, not as a strain default, so no committed output moved and the gate still passes 79/79. |
| ~~3.9~~ | ~~**A fifth sink-audit class: uncosted transport of the coupling ion**~~ | **CLOSED 2026-09-08 (K5 TASK 1).** Class E added to `src/etcgem/sink_audit.py` and wired into `etcgem audit-sinks --coupling-ion` as an opt-in flag, so no committed audit output changed. It infers the coupling ion from each strain's own ATP synthase (*M. maripaludis* is sodium-driven), counts both translocation and in-compartment chemistry (*Synechocystis* scores 19 % on the first and 100 % on both), and contracts GECKO arm/isozyme splits (without which eciML1515 has no detectable ATP synthase). Run on all seven strains: only the three *Candidozyma* are defective. |
| 3.13 | **Complex III is wired backwards in the three iRV973-derived models.** `R02161__mito` moves its 1.5 protons cytosol→matrix, the opposite direction to a mitochondrion, so it SPENDS proton-motive force. Quantified by K5: it eats **exactly half** of what cytochrome *c* oxidase pumps, which is why the repaired chain over-supplies at 200-272 % instead of ~100 %. Correcting it as a labelled sensitivity moves respiration per unit growth from 1.8-2.4× measured to **0.9-1.3×**, i.e. onto the measurement. | Whenever the respiration level is load-bearing for a claim. It is a one-line stoichiometry correction and it is the single change that most improves agreement with the measured O₂ assay. Send to Ilgaz with 3.14: both are in the published iRV973. |
| 3.14 | **The model's growth activation energy is too steep on the rising limb** — 1.20 eV against a measured 0.901 for *C. auris*, and 0.93-1.80 against 0.62-0.90 across the four. **REVISED 2026-09-08 by K6**, which found K5's version of this item ("the maintenance layer cannot produce the measured decoupling") to be wrong twice over: the sign discrepancy it rested on was a comparator artefact, and scaling NGAM(T) up moves the model AWAY from measurement and kills it at 10x the anchored value, while switching it OFF moves E_resp from 0.231 onto the measured 0.518. With maintenance off, ~88 % of the residual gap is the growth term. | Before any claim that these models capture thermal energetics. The layer implicated is the enzyme kinetic envelope — the shared dCp prior and the MMRT curvature that set the rising limb — not maintenance and not the ETC. Note it is consistent with the same models over-predicting the thermal limit by 9.6-15.8 °C (K4 §4), which had not been connected to it. |
| 3.19 | **Synechocystis' committed ceiling is not reproducible from a strain build.** The ceiling table's 45.70 °C comes from `strains/syn6803/outputs/P2_thermal/`; `resolve("syn6803", "syn6803_ecmodel")` gives **55.50 °C**. K9 checked that the committed curve is **not** truncated (growth falls to 0.2 % of peak by 50 °C) and that the light-saturated medium `run_p2_thermal.py` applies does not account for the difference. So the committed row depends on configuration inside that script which the strain build does not carry. | Before the seven-strain ceiling table is used in a paper, and before *Synechocystis*' near-zero gap is quoted as evidence about anything. Same family as the stale-at-commit hazard in §4: a committed number that the code does not reproduce. **Confirmed recorded 2026-09-08 (P5 TASK 4)**: strain named (*Synechocystis* sp. PCC 6803, `syn6803`), evidence in `reports/K9_criterion/report.md` §4 and DECISIONS D3 (committed 45.70 °C from `outputs/P2_thermal/`, plain build `resolve("syn6803", "syn6803_ecmodel")` 55.50 °C; truncation excluded — growth 0.2 % of peak at 50 °C; the light-saturated medium of `run_p2_thermal.py` excluded — applying it does not move the plain build). Not investigated by P5; it needs its own run. |
| 3.20 | **The gas-flux warm start can seed every walker in a dead mode, and the chain never leaves it.** P4 repaired `_warm_start` (its D3, "untested at scale"); P5 ran it once at scale — configuration D on LB at c_max 257 — and its short differential evolution (`maxiter=12, popsize=4`) returned the zero-growth mode (growth ≡ 0 at every temperature, `disc_growth` ≈ 1.4 absorbing the data, −logpost 37.6). All 40 walkers were seeded there and 100 % of them were still there after 2000 steps (156 min); the chain's MAP scores growth R² −2.19. P4's nine chains, whose warm start silently failed, started from the emergent-point ball and found growing solutions. The dead mode is a genuine local optimum of this posterior, so a mode-seeking start is the wrong start unless it is checked. | **Before P6 spends ~40 h on nine chains with this warm start on.** Cheapest fix: reject a warm-start mode whose predicted r_max is below a floor (say 10 % of the measured peak) and fall back to the emergent-point ball; or seed from P4's committed MAP for the same configuration and medium. Evidence: `reports/P5_lb_cmax/DECISIONS.md` D3 and `strains/eciML1515/outputs/calibration_configD_LB_recipe_cmax257/`. |
| 3.21 | **The configuration-E and -F gas-flux likelihood is not a function of its parameters.** Found by P6's pre-flight (2026-09-09): re-evaluating the likelihood at one fixed parameter vector spreads by **0.5–7.5 log-likelihood units** for every E and F fit (NLDM, LB, M9) and by ≤ 0.0004 for every configuration-D fit. Diagnosed: the model's **O2 uptake at optimal growth is not unique**; `flux_tpc` reads it from whichever LP vertex the solver returns, and after the ETC area constraint is removed and re-added (which the E/F likelihood does on every call) the first solve lands on a different vertex from later ones — at F LB the O2 uptake differs by 9.4 on a mean of 19.8 mmol gDW⁻¹ h⁻¹. Growth is stable. So the respiration term of every E/F chain in this family — P4's six and Parsa's four — carried a solver-history component, and τ measured on those chains includes it. P6 did not run E or F for this reason (its DECISIONS D3). | **Before any E or F fit is sampled again, and before their respiration R² is quoted.** The fix is in the likelihood, not the sampler: make O2 uptake unique at the growth optimum (a lexicographic second objective — minimise total flux, or minimise O2 uptake at fixed growth — in `flux_tpc` or in `gasflux_log_likelihood`), then re-run all six E/F fits from scratch. P3's gate is unaffected as a *port* check (one evaluation after a fresh build, both sides), but its E/F respiration rows are a statement about a quantity the model does not determine. Evidence: `reports/P6_convergence/preflight_jitter.csv`, `jitter_diagnosis.json`, `degeneracy.csv` (FVA of O2 at fixed optimal growth: E LB at 37–44 °C spans 0–188 mmol gDW⁻¹ h⁻¹ at growth 1.759 with the carbon cap ACTIVE, so an active cap does not pin O2; configuration D is unique to ≤ 0.04 everywhere). **Second trigger, found on the way:** on D NLDM the carbon cap's primal reads 0 of 120 at every temperature — either its carbon-source expression does not cover the uptake reactions the recipe medium uses, or the recipe ceilings leave it empty; check before "c_max 120 on NLDM" is quoted as doing anything.  **Mechanism settled 2026-09-09 (P6 D3a):** two fresh models agree to 0.0000; one model differs on its second call by 0.5–2.5 with growth unchanged and only O2 moved, and FVA at the moved temperatures shows O2 at fixed optimal growth is a continuum (E NLDM 20 °C 3.2–7.8; E LB 37–50 °C 0–190; F LB 35 °C 16.5–26.3). So: non-unique O2 (identifiability) selected by solver basis history (state). A basis reset makes E LB deterministic and no more identified. The fix is a tie-break that makes O2 unique, not a reset. **RESTATED 2026-09-09 (P10):** the tie-break (1.13) makes the E-configuration likelihoods and F NLDM functions of θ to 0.0000; **F LB alone remains non-deterministic (0.05–0.5)** at the parsimonious optimum even at 1e-9 — its face is not resolved by pfba; min_o2/max_o2 are deterministic bounds but a modelling assertion. F LB is the one fit still held on this ground. |
| 3.17 | **The Candida ceiling's second component is not a common term.** K8 sized a predictor component of ≈5.4 K and observed that *E. coli*, with **measured** Tm, still needs ≈5.6 K, and framed the latter as common. **REVISED 2026-09-08 by K9**, which tested it across every strain where it can be computed: the residuals after removing the predictor bias are 0.05 (*M. maripaludis*), 4.38 (*C. auris*), 5.60 (*E. coli*), 10.08–10.48 (the three relatives). **There is no constant.** *E. coli*'s 5.6 K is real, unexplained and confined to one organism; the two strains that might corroborate it cannot, because their Tm come from a mesophile prior built on *E. coli*'s own meltome and the methanogen has no a-priori ceiling. | Whenever the ceiling is load-bearing. The unexplained quantity is now *E. coli*'s alone and is testable there once P4 lands. The Candida relatives' 10 °C residual is a separate and larger question. |
| 3.18 | **The per-enzyme Tm spread is carrying error, not signal.** Replacing predicted Tm with the relationship A1 measured (`Tm = 52.60 − 0.061 × Tm_pred`) collapses the spread from sd 2.2–2.9 °C to 0.14–0.18 °C and **improves** the fit in all four species (*C. auris* R² 0.518 → 0.687), while moving E_growth toward measurement. | Before any analysis that attributes between-enzyme thermal variation in these strains to biology. It also bears on whether the unfolding form's per-enzyme structure is doing useful work in *Candida* at all, which is a larger question than K8 asked. |
| 3.16 | **The shared ΔCp prior is not the best-supported value for these organisms.** `provider.dcp_prior_kJ = -4.0` (Hobbs 2013) makes the model's growth activation energy 1.24-2.29× the measured value in every *Candida* species. **−3.0, inside the literature range of −2 to −6, reconciles it for three of the four AND maximises the fit to the measured growth curve** (*C. auris* R² 0.518 → 0.575). K7 changed nothing: it is fitted to one quantity on four species, *C. haemulonii* disagrees (it needs −1.0, outside the range), and adopting it would move every committed number for these strains. | When the rising limb is load-bearing for a claim, or when the *E. coli* and methanogen strains are next revisited — they carry the same prior and it has never been tested against any of them. Any adoption should be a ladder rung with its own before-and-after, not an edit to `strain.yaml`. |
| 3.15 | **`resolved_config.yaml` records an absolute `provider.model_path`**, so a run made from a different directory produces a spurious diff and "byte-identical on re-run" is only checkable from the same checkout. Found by K5 TASK 0 running from a git worktree. | Trivial; whenever the config dump is next touched. Record the path relative to the repository root. |
| 3.10 | **Add alternative oxidase to the Candida reconstructions.** AOX is in all four proteomes (A3, and confirmed independently in K4 TASK 1 by EC/name/chemistry search) and in none of the four models. It is non-electrogenic, which is exactly the role cytochrome *bd*-II plays in the **gated** *E. coli* configuration F — the one ETC result this project has tested against experiment. Adding it is one reaction. | Together with 3.8, since an AOX branch is pointless while the chain is bypassed. Then respirometry with SHAM and antimycin A across temperature (K4 TASK 5 item 4) turns it into a measurement. |
| 3.11 | **Mitochondrial inner-membrane area per gDW, per Candida species, at 30 °C and 40 °C.** The measurement an ETC-area budget actually consumes, and it does not exist for any *Candida*: no published inner-membrane area, cristae density or mitochondrial volume fraction for *C. auris*, *C. haemulonii*, *C. duobushaemulonii* or *C. parapsilosis*, and **no inner:outer membrane area ratio for any fungus**. Nearest proxies: *S. cerevisiae* stereology (Perktold 2007; Stevens 1981), and Arthur & Watson (1976), which measured cytochrome *aa*₃ per mg dry weight across seven yeasts and found **7×** interspecific variation. | If the membrane axis is to be tested rather than made available. Method and the discriminating result are in `reports/K4_membrane/task5_what_would_test_it.md`. Serial-section electron tomography or FIB-SEM with stereological sampling; two temperatures, not one. |
| 3.12 | **Organelle-resolved mitochondrial lipidomics for any *Candida*.** Whole-cell lipidomics for *C. auris* is rich (Shahi 2020; Zamith-Miranda 2021; Singh 2020/2024); **fractionated mitochondrial lipidomics for any *Candida* does not exist**. The only comparative isolated-mitochondria phospholipid dataset across yeasts, which includes *C. parapsilosis*, is Arthur & Watson (1976) — and it shows **>10×** interspecific variation in mitochondrial cardiolipin, the largest measured fungal membrane difference on record. | Note this feeds A8 (fluidity, phase behaviour, proton leak), **not** the area budget, which has no lipid term. K4 TASK 5 §5 separates the two; they should not be commissioned as one study. |

## 4. Standing hazards — not tasks, but re-read before trusting a result

**Standing protocol:** [RIGOUR.md](RIGOUR.md), with decision references and recorded historical exceptions, governs subsequent runs.

- **THE REPOSITORY HOLDS MORE THAN ONE MEASURED VALUE FOR SOME QUANTITIES, AND THEY DISAGREE.**
  This has now cost the project twice: Parsa's NLDM CSV predating its own medium change, and
  K5 comparing the model's activation energies against the wrong one of two measured growth
  fits. **The rule: when comparing a model to data, fit both sides over the same window with
  the same functional form, and state in the report which measured source was used.** The known
  multi-valued quantities, all of them legitimately so:
  - **E_growth**, 4.6-fold spread. `arrhenius_growth_fgC_h_coefs.csv` (OLS Arrhenius over every
    temperature) gives **0.194 eV** for *C. auris* clade I and is **negative for three
    isolates**, which is not biology — it is a straight line through a curve that turns over.
    The same data on the rising limb gives **0.732 eV**, and the manuscript's hierarchical
    Sharpe-Schoolfield fit gives **0.901 eV**. Use the rising-limb value against a model.
  - **E_resp**, 1.45-fold spread, and four published values for the same clade: 0.518 (OLS and
    the published Bayesian Arrhenius, which agree because respiration does not turn over), 0.454
    (equilibration-corrected), 0.654 (term-free), 0.545 (Sharpe-Schoolfield with `Eh` at its
    bound). `bayes_resp_arr_E_three_treatments.csv` holds three of them. The headline is
    "With term (published)".
  - **The measured growth TPC itself.** `measured_tpc_honest.csv`, which every Candida strain
    calibrates against, counts a dead well as an **observed zero** — deliberately, and
    documented in `gem/17_build_measured_tpc.py`, because the previous file silently dropped
    temperatures where everything died. `derived_N0_R_results_with_carbon.csv` keeps only valid
    fits, i.e. the survivors. So at 40-44 °C the first says *C. haemulonii* grows at 0.000/h and
    the second says its surviving wells grow at 0.66-0.83/h. **Both are right and they are not
    interchangeable**: the zeros curve is the one for "the relatives die at 40 °C", the
    survivors table is the one for any log-scale fit. Never mix them in one comparison.
  - **T_opt**, three sources that differ by up to 2 °C: each `strain.yaml`'s
    `measured_Topt_C`, the argmax of `measured_tpc.csv`, and the Bayesian `growth_Topt_C`. For
    *C. haemulonii* they are 32.0, 30.0 and 31.98.
  - **Per-cell respiration** carries the cell-mass constants, which disagree ~6-fold
    (item 1.9). Scale-free comparisons only.
- **Never verify with `cmd && check`.** The `cli.main` exit-code defect made one such check vacuous
  and produced a false PASS. Check exit codes explicitly. (Fixed in `a467d23`, but the habit is the
  hazard.)
- **Stale-at-commit has happened three times in three codebases by three people** — `outputs/tpc`
  committed with numbers its own code did not produce; `control_tuned` diverging from
  `decompose_tuned`; Parsa's NLDM CSV predating its own `build_pm`. Assume it until checked.
- **T_opt is regime-determined.** Three constraints relocate it (sector re-grounding `a416fd1`, the
  translation cap, Parsa's carbon cap); CT_max has been insensitive to all three. Quote T_opt with
  its binding constraint named; CT_max may be quoted plainly.
- **A variance decomposition can only attribute to mechanisms the model contains.** φ_envelope
  = 0.999 for T_opt is a local measure inside one regime, not a statement about what sets T_opt.
- **The two Candida draft models are the *auris* network with genes reassigned** (2,863 reactions,
  ~1,312 costed, differing by 2–4). Network differences cannot explain their behaviour — and cannot
  be tested there either.
- **Sectors without temperature-dependent allocation flatten the curve.** Confirmed on E. coli:
  plateau 2.0 → 14.0 °C with `allocation_from_data` off. N1's guard warns; it cannot see a shoulder
  *below* the maximum (the 37–44 °C case).
- **A GATE ONLY PROTECTS THE FIELDS IT CHECKS** (added 2026-09-08, P5, from P4 and K9). K8 added a
  field (`fixed`) to the calibration record and wrote it unconditionally; every committed
  `calibration.json` went stale on the next run and the K1 gate passed 79/79 throughout, because
  it does not read that field. K9 TASK 0 caught it only by re-running the transfers and diffing
  the tree. **Adding a field to a record is a silent way to break byte-identity.** The same week
  a second instance surfaced: N2's hotfix started recording `rescale_pool_row` in the config
  dump, and the two `etcgem fba` output directories the K1 gate reads
  (`strains/cauris_iRV973/outputs/fba_candida_pool_{binding,unconstrained}/resolved_config.yaml`)
  have been one key stale since — numerically identical, never re-run by any TASK 0, and hidden
  from a worktree by 3.15's absolute-path artefact in the same file. Left as found by P5 (VERIFY 6);
  clear it in a housekeeping commit that says so. **The rule: re-run the byte-identity check
  AFTER the last change, not at the point it seems safe; diff the whole tree, not the fields
  the gate names; and treat a `resolved_config.yaml` diff as a finding until it is explained.**
- **NEVER RUN A `multiprocessing` SCRIPT FROM STDIN. IT RESPAWNS FOREVER AND SURVIVES THE
  SESSION** (added 2026-09-10, P12; **second occurrence**). macOS uses the *spawn* start method,
  so every worker re-imports the parent's `__main__`. When `__main__` is stdin — `python - <<'EOF'`,
  a heredoc, or a piped script — each worker re-executes the whole module top level, creates its
  own `Pool`, and spawns more workers, without limit. The first occurrence (P9/P10 week) was
  caught only because the user heard the fan. The second, **pid 43407, ran undetected from
  2026-09-09 22:00 for 13.6 hours**, orphaned to `launchd` (PPID 1) with its heredoc temp file
  already deleted, respawning continuously — its worker PIDs rotated 85783→87519 within seconds
  of each other while being inspected — and had consumed ~58 minutes of CPU. It was found only
  because the user asked whether the workers were still consuming CPU.
  **The rules, all three:** (1) any script that imports `multiprocessing` is written to a FILE
  with an `if __name__ == "__main__": main()` guard and run as a file, never fed to `python -`;
  (2) after any pooled run, sweep for stray interpreters that are not in the live run's process
  tree and check their PPID — **PPID 1 on a compute process means orphaned, not finished**;
  (3) `ps -o pcpu` is a lifetime average and reads low on a sleeping parent, so a runaway hides
  from it — check process STATE and whether the child PIDs are CHANGING, which is the only
  signature that distinguishes a respawn loop from a long job.
- **LONG RUNS GO IN A DETACHED, IDEMPOTENT, SELF-AUDITING DRIVER; THE SESSION LAUNCHES AND LEAVES;
  RESUMPTION READS `status.json` FIRST** (added 2026-09-15, T2). `reports/T2_validated_posterior/
  run_protocol.py` is the pattern: it reads its state file and each run's own status, skips runs
  complete-and-audited, resumes runs with a checkpoint (proven bit-identical to an uninterrupted
  run on the toy), audits each completed run by independent reconstruction before starting the
  next, and stops itself on any failure with the reason in `status.json`. A session never polls
  it beyond a ten-minute launch check, never relaunches while its pid is alive, and never touches
  a run directory. The atexit hook did not remove `driver.pid` on the crash path; the pid file is
  a record, and a relaunch checks the pid is dead rather than trusting the file's absence.
- **A COMMAND THAT FAILS CAN RETURN EMPTY OUTPUT; EMPTY IS NOT A RESULT. CHECK THE EXIT CODE AND
  THE STDERR BEFORE READING SILENCE AS CLEANLINESS** (added 2026-09-16, H4). The general rule is
  the heading, and it belongs beside the `cmd && check` hazard above. **What actually happened here
  was subtler and is worth the extra line:** H2's `git status --porcelain` in the primary tree
  did *not* fail — it exited 0 and reported 29 entries, which H2 printed. What was incomplete was
  H2's **prose summary** in this file, which named the uncommitted prompt files as examples without
  enumerating the other twenty-four artefacts; a later prompt read that summary as an exhaustive
  list and asserted "five uncommitted files". H3's premise check caught it at thirty and stopped.
  **So the operational rule is two-part:** check exit codes *and* never let a narrative summary of
  a machine-readable result stand in for the result — if a later step depends on a list being
  complete, re-derive the list, do not quote the prose.
- **A LIKELIHOOD EVALUATED IN A PERSISTENT WORKER POOL IS NOT NECESSARILY A DETERMINISTIC FUNCTION
  OF ITS PARAMETERS; NESTED SAMPLING CANNOT TOLERATE THAT, AND THE FAILURE IS INTERMITTENT, SO A
  PASSING SPOT-CHECK DOES NOT ESTABLISH IT** (added 2026-09-16, T3; the general form of the entry
  below). Measured: 49 % of evaluations deviate from their fresh-process value above 1e-9 and
  0.3 % by more than a full log unit, **and which θ is hit depends on what the worker evaluated
  before it** — T3's control battery found the point that crashed T2's run 3 to be clean over 50
  evaluations while two of its siblings carried the same +1.28 offset. **The rule: determinism is
  a property of the evaluation path, not of a parameter vector, so it is established by
  re-evaluating in a fresh process — not by repeating a call in the same one — and a scheme is
  only deterministic if every registered input reproduces at every repeat.** A solver reset per
  call makes it worse, not better (T3 D3). Items 1.34, 1.35.
- **A LIKELIHOOD EVALUATED IN A WARM SOLVER IS NOT A FUNCTION OF θ, AND NESTED SAMPLING WILL FIND
  THE POINT WHERE THAT MATTERS** (added 2026-09-15, T2). The tie-broken LP returns different
  vertices depending on the worker's solver history — usually at 1e-9, sometimes at 1e-3, once at
  1.28 log-likelihood units at a posterior point. A sampler that stores a value it cannot
  reproduce carries a live point that becomes unbeatable when the threshold passes its true
  value; the run then crashes deterministically (P15, T2 run 3) or finishes with inflated points
  in its live set (T2 runs 1–2). **The rule: before any long run, re-evaluate a sample of
  accepted points fresh and compare to their stored values; a discrepancy above the registered
  repeatability tolerance is a stop, not a footnote.** Item 1.34.
- **`codex/p17-inactive-prior` IS THE ONLY REF KEEPING ~2.9 GB OF P17 OBJECTS REACHABLE IN THE
  PRIMARY REPOSITORY** (added 2026-09-13, T1). It is local-only by decision (R3). Deleting it, or
  any "clean up merged branches" pass that touches it, makes those objects prunable by `git gc`.
  **It is never merged, never pushed, never deleted.** Its checkout lives in the archive worktree
  at `../etcGEMs-p17-archive` (a sibling of the repository, on the same OneDrive volume as the
  object store; relocated from `/private/tmp` by T1 on 2026-09-13 because that path is cleared on
  reboot). **The worktree is recreatable from the branch with one command; the branch is not
  recreatable from anything.** `git worktree list` must always show it at `ef1961b`.
- **A CRITERION MUST TEST THE FAILURE MODE IT NAMES** (added 2026-09-11, P15). The sampleability
  criterion specified for P14 **named plateaus** as nested sampling's failure mode — correctly — and
  then **also required no jumps**. Those are different objects, and only one is fatal: a plateau puts
  an **atom** in the distribution of L under the prior, which voids X_i ≈ exp(−i/nlive); a jump
  leaves a **gap** in L's support, carrying no prior mass, which nothing ever samples. The surplus
  conjunct cost a full run slot (P13) and then blocked a second (P14), on a surface that had **no
  plateaus at all**. **The rule: when a criterion names a failure mode, every conjunct must be
  derivable from that failure mode — and a conjunct that cannot be is not conservatism, it is a
  different criterion smuggled in.** See 1.23.
- **A SMOOTHNESS CRITERION MUST TEST DISCONTINUITY BY GRID REFINEMENT, NOT BY STEP SIZE — AND
  FOR NESTED SAMPLING THE PROPERTY THAT MATTERS IS FLATNESS, NOT STEEPNESS** (added 2026-09-10,
  P14). A step size confounds two different things: a steep smooth gradient and a jump. Refining
  the grid separates them in four evaluations — |Δ| halves with h for a bounded derivative and
  converges to a constant for a jump. Measured here: the step that stopped P13, **8.55 units on
  `axis:topt_scale`, halves cleanly (0.507, 0.515, 0.504) and is pure steepness**, while steps of
  **0.05–0.59 units elsewhere do not shrink at all** and are real discontinuities. **Step size
  ranked them backwards.** And for a nested sampler the ranking barely matters either way: its
  estimate depends only on X(L), the prior mass above L, so it is invariant to any monotone
  transformation of the likelihood. A jump leaves an interval of likelihood values carrying no
  prior mass — harmless. A **plateau** puts an **atom** in the distribution of L and voids the
  shrinkage argument — fatal (Fowlie, Handley & Su 2021). **The rule: test discontinuity by
  refinement, test plateaus by exact equality, and do not let gradient magnitude gate a sampler
  that is blind to it.** See 1.23.
- **A SAMPLEABILITY VERDICT MEASURED AT ONE CENTRE IS NOT A PROPERTY OF THE SURFACE** (added
  2026-09-10, P13). P11 scanned twelve lines through **θ_A** and reported the surface SAMPLEABLE:
  largest step 3.53, and 3.20 on `axis:topt_scale`. P13 re-scanned the **same twelve lines with the
  same instrument and the same rule** through **p38** — the better optimum P12 found, which beats
  P11's own best sample — and `axis:topt_scale` gives **8.55**, failing the rule. Nothing about the
  likelihood changed between the two measurements. **The rule is a statement about a neighbourhood,
  not about a function**, and a surface verified at the point a previous run happened to stop at
  has not been verified where the next run will go. **The rule: re-scan at the current best point
  before every sampling run, and quote a sampleability verdict with the centre it was measured at,
  always.** See 1.23.
- **A SMOOTHNESS RULE MUST BE ABSOLUTE IN LOG-LIKELIHOOD UNITS; A RELATIVE ONE FLAGS KINKS ONCE
  THE CLIFFS ARE GONE** (added 2026-09-09, P11). P9 judged a likelihood surface by whether any
  0.05 sd step exceeded 20 % of its line's range. That was the right instrument for cliffs of
  13–72 units on ranges of 15–137. But a fix that removes the cliffs shrinks the ranges with
  them, so the same rule kept reading ROUGH on lines whose largest step was 0.8 units — a
  likelihood ratio of about 2, which no sampler notices. What decides whether a sampler can
  cross a step is e^−Δ: e^−30 is a wall, e^−2 is a kink. **The rule: state smoothness criteria in
  absolute log-likelihood units** (P11 used 5, the same threshold P10 used to identify the steps
  it fixed), **and re-derive a relative criterion whenever the thing it normalises by has
  changed.** Under both readings the same twelve lines are SAMPLEABLE (largest step 3.53 units)
  and ROUGH (two lines above 20 % of ranges of 3.6 and 15.8) at once. See `reports/P11_nested/`.
- **A RECOMMENDATION IS SCOPED TO THE CONDITIONS IT WAS DERIVED UNDER** (added 2026-09-08, P5,
  from P4). `c_max ≈ 100–120` came from Parsa's sweep on glucose-minimal and NLDM; P3 adopted 120
  as canonical from that sweep; P4's settings table applied it to LB, where every LB growth R²
  collapsed (0.83–0.90 → 0.16–0.20) while NLDM was unchanged to better. His own LB fits had used
  257 / 459 / 510 (`reports/P5_lb_cmax/parsa_lb_cmax.csv`). Nobody had run an LB sensitivity, and
  the number carried no medium with it when it moved. **The rule: record the value AND the
  conditions it was established on (here, the medium), and when a value is applied outside those
  conditions say so where it is applied, not only where it was derived.** See 1.11 and
  `reports/P5_lb_cmax/`.
- **AN AUDIT THAT FINDS NOTHING MUST FIRST PROVE IT CAN FIND SOMETHING** (added 2026-09-09, R2,
  from Y1). Y1's matcher was blind to Yeast7 naming and would have returned a clean bill of health
  for the wrong reason; proved inert on all seven strains before use. **The rule: a clean result
  from an audit on an unfamiliar namespace is not evidence until the matcher has been shown to
  find something.** See 4b and `reports/Y1_yeast_audit/`.
- **A SCAN'S CONCLUSION IS SCOPED TO THE POINTS SCANNED** (added 2026-09-09, R2, from P6). P6's
  five-temperature O2 FVA read "unique" at 25–44 °C; the degeneracy lives at 20 and 35–50 °C.
  **The rule: say which points a scan covered where its conclusion is quoted.** See D3a in
  `reports/P6_convergence/DECISIONS.md` and 3.21.

---

## 4b. Y1 — the published yeast etcGEM (2026-09-09)

**The gate on the fourth-paper idea was run and it came back (b): the defect class is ABSENT from
Li et al. 2021, and the structural finding holds.** `reports/Y1_yeast_audit/report.md`.

**Dated note, 2026-09-10 (P12).** Pettersen & Almaas 2023 found Li et al.'s yeast etcGEM **multimodal and seed-unstable across 2,292 per-enzyme parameters**, and P11 read the same signature into this 16-parameter reformulation. **P12 does not reproduce it.** With the endpoints actually converged and basins defined by bottleneck barriers rather than by clustering, there is **one live basin**; the only separated basin is a model that does not grow. So the precedent's multimodality is **not** simply inherited by any thermal etcGEM — on this evidence it is not present here at all, and the earlier framing ("the multimodality is in the thermal formulation, not the parameter count", §0c) is **withdrawn as unsupported**. What does carry over from their work is the *method* — FVA on equally-fit particles, hierarchical clustering of endpoints — and their cost finding does **not**: their 8.5× came from replacing COBRApy because 80 % of their time was model preparation, whereas here **92 % is LP solving and 8 % preparation**, so that route could buy at most 8 %.

* **Coupling-ion audit: does not fire.** Their chain supplies 92.7 % (pristine batch) and 93.1 %
  (chemostat) of ATP synthase's protons. All twelve uncosted proton movers on the mitochondrial
  membrane run the dissipative way; none has an uncosted `_REV` twin; **no free path `m -> c`
  exists at any length**; and with every exchange shut, maximum ATP synthase flux and maximum ATP
  hydrolysis are both exactly 0. Verified pristine, under their own thermal layer, by
  counterfactual, and by the exchange-closed test.
* **T_opt / CT_max asymmetry: reproduces independently.** In their model with their `etcpy`, a
  change of binding constraint moves T_opt **10.1 C** and CT_max **0.8 C**. Five organisms, two
  codebases.
* **Calibration shift: does NOT generalise.** Their posterior left Tm at the measured meltome
  (r = 0.97 with experiment, Fig. 2g) and moved Topt instead; the nine enzymes carrying their
  thermal limit already had measured prior Tm of 40.5-43.8 C. Our E. coli needed dTm = -5.6 K;
  theirs needed nothing. What is common is the tension, not the shift.
* **A defect in OUR audit, found first.** `sink_audit`'s anchored patterns were matched against the
  metabolite id and the joined `"id name"`, so the Yeast7 convention (opaque id `s_0437`, plain
  name `ATP`) matched nothing: **zero hits in classes A-D on 6743 reactions and no ATP synthase
  found**, on a model with an intact chain. A clean bill of health for the wrong reason. Fixed and
  proved inert on all seven strains (every class-E cell identical to 0.0; every A-D count
  unchanged). **The rule: when an audit returns a clean result on a model from an unfamiliar
  namespace, verify the matcher found ANYTHING before believing the absence.**
* **Their Topt is a sequence prediction** (Tome v1.0, R^2 = 0.5) carried as a wide prior with the
  predictor's own RMSE (13.0 C) as the prior width. That is the methodological answer to our Seq2Tm
  concern, and it is theirs.
* **Their thermal layer is Python, not MATLAB** (`code/etcpy`), which is why this cost an afternoon.
  Anyone extending Y1 can run their model directly.

---

## 4c. Y2 — the regime test at Li et al.'s posterior (2026-09-09)

`reports/Y2_regime_posterior/report.md`. Closes 2.5.

* **Quotable, with an interval.** Over their own 100 posterior models, switching the binding
  constraint from enzyme capacity to substrate uptake widens the 99 % plateau of the TPC from
  **1.5 °C [0.4, 2.7] to 7.3 °C [1.4, 7.5]**, in **93 %** of models, while CT_max moves
  **4.6 °C [2.7, 11.0]**. T_opt moves 8.9 °C [4.4, 27.0] — a **lower bound** in 44 of 98 models,
  because under a substrate cap the top of the curve is a ceiling, not a peak, and the optimum
  leaves the 20–50 °C window.
* **NOT quotable as a property of their calibrated model: 10.09 / 0.81 °C.** That is the prior
  *point* table. At the posterior CT_max is no longer regime-insensitive.
* **The prior distribution does not support the finding; the posterior does.** Prior draws: T_opt
  beats CT_max in 50 % of draws, plateau widens in 35 %. Posterior draws: 92 % and 93 %. The
  calibration's shrinkage — Topt 10.9 → 7.1 °C, Tm 4.9 → 4.0 °C — is what turns a coin flip into a
  consistent effect.
* **The signed calibration shift, which Y1 could not measure.** Across 764 enzymes, Tm moved
  **+1.33 °C** and Topt **−6.32 °C**. But seven of the nine limit-setting enzymes moved *down* in
  Tm (ATP1 −6.30, ERG1 −3.66), and only **three** of those nine were below 42 °C in the prior. The
  identity of the limit-setting set is largely a product of the calibration.
* **The file is the right one, checked three ways:** md5 matches Zenodo; the populations reproduce
  the paper's average per-enzyme SDs (10.92 → 7.16, 4.90 → 4.01, 2.00 → 1.79 against 10.9 → 7.1,
  4.9 → 4.0, 2.0 → 1.8, Supplementary Fig. 7); and the nine enzymes below 42 °C reproduce
  Supplementary Fig. 8's named list exactly, nine of nine.
* **An analysis error found and corrected inside Y2.** The first pass called a parameter set
  "degenerate" when its T_opt landed at the grid edge, and dropped 44 of 100 posterior draws — the
  ones showing the effect most cleanly, because a substrate ceiling makes the top an exact tie.
  **The rule: before excluding a case as degenerate, check whether the degeneracy IS the effect.**
  `reports/Y2_regime_posterior/DECISIONS.md` §9.
* **New:** the σ-lever and chemostat conditions were not drawn over at the posterior, and the
  anaerobic model was not run. Neither is needed for the quotable figure; both are cheap.

---

## 4d. Y3 — is the −4 K stability shift biology or parameterisation? (2026-09-10)

A screen, not the experiment. `reports/Y3_tm_shift/report.md`. Moves **R3 only**, and licenses
nothing about the Candida models (their Tm is predicted, and A1 measured that predictor's bias at
+5.43 °C).

* **Verdict PARAMETERISATION by the rule — narrower than its label.** Both arms fire: partial
  correlations +0.696 / +0.663 / +0.661, and a compensating direction of 4.02 K for **0.077 log L
  units**, alive throughout.
* **What pays for it is not catalysis.** `tm_scale` — which stretches the Tm *spread*, not a
  catalytic parameter — moves 0.990 → 1.467 along the profile while `kcat_scale` stays 1.33–1.43.
  The control is decisive: pinning `tm_scale` = 1 **while keeping** the −4 K shift costs *nothing*
  (−0.15 units); it only becomes load-bearing when `dTm` is forced to 0.
* **Both solutions buy the same low tail.** 1st percentile of effective Tm: **38.7 °C** via the
  shift, **36.7 °C** via the stretch, against **42.6 °C** measured. The fit does not need the
  meltome moved down; it needs the least-stable few per cent of enzymes several degrees less
  stable than measured.
* **1.20 partly retracted:** the meltome-honouring region *does* contain a growing model — 1.659 /h
  at log L −14.786, 7.60 units worse and pressed against two prior ceilings.
* **New non-identification for R2:** `dTm` and `tm_scale` are not jointly identified.
* **DLTKcat recommended against, on its own output.** 36 interior optima out of 1 149 fits; 736
  rail at 80 °C. The thermal layer is already per-enzyme in its *data* (`enzyme_cost.py` holds
  per-enzyme `Topt`/`Tm` arrays), so swapping in a better table is ~0 half-days — the blocker is
  that there is no better table to swap in. Making the *free parameters* per-enzyme is 6–10
  half-days in the calibration, not the thermal layer.
* **The rule did not distinguish stability from catalytic compensation.** It listed `tm_scale`
  among "the catalytic parameters". **The rule: when a decision rule names a parameter set, check
  each member does what the label says before the rule is allowed to decide anything.** Y3 caught
  it only because the profile's compensator was visible in the per-step table.

---

## 5. What to do with P2's outcome — the checklist to run against its report

_Written before P2 finished, so the reaction is not shaped by the result._

**Verify, in this order:**

1. **The merge held.** Gate 79/79 with `$CANDIDAS_ROOT` unset, exit codes checked explicitly not
   chained; all seven strains byte-identical. If either failed, nothing below matters.
2. **The ungated notice is at the top of the config report**, not buried. A reader must not be able
   to mistake ported for verified. Quote it and check.
3. **TASK 1 (kcat).** If neither 30 nor 300 reproduces his figure → that is a finding, not a
   failure, and it goes to Parsa as a fourth question. If one does → record as provisional, and
   expect his reply to ratify.
4. **TASK 2 (NLDM).** The 1.2 % must be **fully** explained by the medium. A residual means
   something else moved and is a stop condition — chase it before merging.
5. **TASK 3 (c_max) — read this one hardest.** The question is whether 60 sits in a flat region or
   on a slope.
   - *Flat region* → the thermal claims are safe whatever Parsa says about provenance, and 1.2
     downgrades from blocking to housekeeping.
   - *On a slope* → every T_opt and E_a number in the new paper depends on a constant whose
     justification is unknown, and that becomes the most urgent item on the list.
   - Either way, do NOT let a tidy sensitivity table substitute for the provenance question.
6. **TASK 4 (stamps).** Check the stamp is generated by a script, not hand-written — a hand-written
   stamp is the next thing to go stale. Check HISTORICAL is phrased neutrally.
7. **TASK 5 (annotations).** All three must be in files a reader reaches, not in decision logs.
   Verify by opening the file, not by trusting the report.

**Then update this document:**

- Move anything P2 closed out of §2 and into a struck-through line or delete it.
- Add anything P2 discovered — expect at least one; every run so far has produced a finding the
  prompt did not anticipate (K1: the draft-model construction; K2: the reversible ATP reaction;
  A1: the predictor's absent validity; N1: the E. coli allocation cliff; N2: stale-at-commit;
  N3: the exit-code defect; P1: the missing respirometry).
- Re-rank §2. If TASK 3 says c_max is on a slope, 1.2 outranks everything.

**Then the next prompt is one of:**

- **P3** — gate D/E/F, if Parsa's data has arrived. Highest value when possible.
- **K4** — the membrane-area constraint on Candida (2.2). Highest value when it has not, and it does
  not depend on anything outstanding.
- A short corrective run, if P2 raised a stop condition.

## P16 completed-run audit — 12 September 2026

**This dated update supersedes the expectation in 0d that an agreeing posterior is about
to arrive.** Both seeds stopped successfully and log Z agrees (difference 0.0225 versus
combined error 0.1478), but **14/15 medians fail the pre-registered agreement rule**.
A supplementary dynesty strand bootstrap gives the same failure set. R1 remains open.
No further parameter fixed, sampler changed or D/E/F fit launched.

Neither tm_scale distribution rails, but eigen-width classifications and tail positions
differ between seeds. The inactive f_metab coordinate does not recover its prior, providing
an independent computational diagnostic. The next investigation is constrained-prior
exploration and sampling quality; fixing the biological likelihood's infeasibility exemption
remains necessary, but does not explain or excuse sampling a truly inactive coordinate
incorrectly. Do not treat seed 1's low-growth fraction as a reproduced property yet.

See reports/P16_reduced/audit_report.md and DECISIONS D7 for all addendum checks, corrected
weighted correlations, full eigenvectors and the outstanding original TASK 5 deliverables.
All results condition on dTm=0: the measured meltome mean is assumed exact and uniform
mean error must be absorbed by tm_scale/catalytic parameters. No full-model posterior claim.


## P17 PI closure and reconciliation — 13 September 2026

P17 closes as a negative diagnostic result by explicit PI stopping-rule change, not by passing its original gate. No validated posterior exists for this family; R1 remains open, R3 provisional, R4 untouched. D/E/F/M9 fits remain blocked behind the separately approved target revision. No further biological parameter is fixed. dTm=0 assumes an exact meltome mean and excludes uniform melting-temperature uncertainty, which would otherwise be absorbed by tm_scale and catalytic parameters.

This dated correction supersedes §0d's running-P16 status, reliance on its evidence as validated model comparison, recommendation to commission more sampler-only development, and the claim that E5 has not run. The original text remains visible as history. The inspected e2/deck branch contains E5 and subsequent E6 work; its old E6 prompt must be marked superseded during integration. P17's final report and INTEGRATION_STATE.md govern the current state.

D44/D45 concern reproducible scale-dependent curvature at ONE non-optimal point, not proof all samplers fail or that the likelihood is the sole cause. The 80–87% living fractions are analytical toy outcomes from their specified priors and likelihoods, NOT biological targets or acceptance thresholds.

| # | Current decision or dependency | Owner | Disposition |
|---|---|---|---|
| 1.25 | Consistent treatment of missing/infeasible respiration predictions | PI | Open; formalises §0d's existing number. Derive from observation model, distinguish structural zero from numerical failure; TARGET_REVISION_SPEC item 2 awaits approval.  **PREPARED TO ITS GATE 2026-09-13 (T1 TASK 2), NOT DECIDED.** From the record, not the spec's illustration: `s` is the **measured replicate SD** at every one of the 12 temperatures (5 replicates each; the code's 30 % floor never fires for D NLDM); **no detection limit is documented anywhere**, so a censored model is not derivable; every scored value is positive; and **the data say O₂ is not structurally zero when growth is** — three 50 °C series with `r = 1e-6` (the pipeline's deliberate no-growth marker) respire at ~2×10⁻¹². Solver-status classification with the three-rung retry ladder: at D44 all 58 missing predictions are Gurobi `infeasible` at 15 °C on every rung (STRUCTURAL_ZERO on growth); the full counts (`task2_classify_all.csv`, audited by hash and recomputation, D8): **876 points, 10,512 solves, 9,355 STRUCTURAL_ZERO, 0 UNRESOLVED, 0 RESOLVED_ON_RETRY**; the six saved stratum states are infeasible at all twelve temperatures, and **765 of the 800 validated live points** are too — P17's "765 compatible" (81.5 % of red2's weight) as a solver fact: on that set log L is the growth term alone, ceiling −18.6825, above most of the 35 living points. The existing log-scale term **cannot score a zero prediction** (`log 0`), and a lognormal ε is not derivable from it. Candidates, each with its per-observation formula and a datum-by-datum table reconciled to totals, are in `DECISION_PACKAGE.md` §2. **The decision is item 1.30.** |
| 1.26 | D/E/F evidence-based model comparison | PI | Blocked programme decision; formalises §0d's existing number. P16 evidence agreement does not validate those estimates. No new fits. |
| 1.27 | Approve separately scoped scientific target revision | PI | Open: configuration-D f_metab removal versus a distinct allocation hypothesis; observation-model treatment under 1.25; seven-axis mechanism investigation and the complete preregistered validation plan. TARGET_REVISION_SPEC.md is preparation only.  **PREPARED TO ITS GATES 2026-09-13 (T1).** Item 1 of the spec is settled as a *fact*: the sampled `f_metab` **does not enter configuration D by design** (`enzyme_cost.py:600–607`, `gasflux_configD.yaml:17–18`, `report.qmd:363`; history `8c0914c` → `922e13d` → `96e64c3`), the removal is prepared as a core option **default OFF**, and the algebraic invariant is **proven at all 870 registered audit points, max difference 2.02e-08** against 1e-6. `f_maint` is a different case and stays. Item 2 is prepared to its gate (1.25 / 1.30). Item 3's trace is 1.31. The validation protocol is drafted for signature (1.32). **Approval of the specification remains this item; the three sub-decisions are 1.29–1.31.** |
| 1.29 | **`f_metab`: approve removal / approve wiring as a new hypothesis / neither** | PI | T1 TASK 1's decision. The finding is (i) intentional by design, with file/line/commit evidence in `reports/T1_target_revision/DECISIONS.md` D2; the removal (`remove_inactive`, plus a `diagnostic_coords` mechanism for validation runs) is implemented default OFF and gated 79/79, 60/60; the invariant is proven at 870 points to 2.02e-08. **Recommendation: approve removal.** Turning it on changes no log L and no evidence; fifteen sampled coordinates instead of sixteen. Wiring `f_metab` into allocation is the static-partition hypothesis `922e13d` superseded and needs its own identifier and approval — not prepared here. **CLOSED 2026-09-15 (T2): removal APPROVED by the PI (2026-09-13) and ON for eciML1515** (`calibration.remove_inactive`); gates 79/79, 60/60 byte-identical OFF; invariant re-verified at 876 points under the full revision (13 feasible to 9.6e-08, 863 at −∞). |
| 1.30 | **Infeasibility: which observation model for a missing respiration prediction, or none — from the measurement process** | PI | T1 TASK 2's decision. See 1.25 for the facts. Candidates: NORMAL on the original scale with the measured replicate `s` and `r = 0` where the solve is STRUCTURAL_ZERO on growth (derivable, but `r = 0` is contradicted for O₂ by the non-growing series that respire); the existing term's own scale (**undefined** at a zero prediction); CENSORED (**not derivable**, no documented limit). Datum-by-datum tables at D44's baseline, the six saved stratum states, the four feasible-non-growing and two growing endpoints, reconciled to totals (≤ 1.65e-9; `task2_datum_table.csv`, 156 rows). 73 positive measurements escape scoring under the omission, 0 under NORMAL r = 0. The NORMAL candidate is a density in `y` on the original scale — its 15 °C term at D44 is +17.54, dominated by the normalising constant at s ≈ 5e-13 — and the existing term a density in `log y`; the totals are not comparable without the Jacobian, which the package states beside the table. The underlying choice is whether a missing prediction is a model **statement** to be scored or a model **deficiency** to be fixed; T1 supplies the arithmetic for the first and cannot make the second a number. **T1 chose nothing** and read no posterior. **CLOSED 2026-09-15 (T2): −∞ for structural infeasibility APPROVED by the PI (2026-09-13) and ON** (`respiration.infeasible: zero_lik`; the limit of the existing log-scale term; coldest-first short-circuit; UNRESOLVED is an exception, never a number). Verified: every −∞ point in the audit set at −∞; every feasible point unchanged; 0 unresolved in 20,413 + 3 × 2,000 + 578,466 solves. Correction to T1's record (T2 D3): T1's rung 2 did not run at 1e-12 — Gurobi's floor is 1e-9 and the failed `setParam` was swallowed — its classification stands as executed. See 1.33 for the prior-rejection finding. |
| 1.31 | **Curvature: per axis, approve correction / retain as is** | PI | T1 TASK 3's decisions, one per anything classified IMPLEMENTATION DEFECT among dTopt, topt_scale, dCp_scale, tm_scale, kcat_scale, sigma, clearance_mult. Trace-only; new log L = old log L at every point. The candidate mechanism registered before tracing is the hard clip `np.clip(rk·fN, 1e-6, 1e6)` in `_costs_unfolding`. **Classified 2026-09-13 (T1 D10, rule D7):** at D44, dTopt, tm_scale, kcat_scale, sigma, clearance_mult **SUPPORTED** (SMOOTH on both refinement sides; sigma's failure is a slope kink where growth at 30 °C reaches a ceiling); topt_scale and dCp_scale **UNDETERMINED** — the failure is carried by respiration at 27 °C on [+0.02, +0.04] where the tie-broken O₂ drops 15.7 → 11.1 with the LP `optimal` and no traced enzyme state moving: an untraced vertex change (P9's kind), next instrument P9's basis-status capture, not run. **No IMPLEMENTATION DEFECT; the clip moved on two axes and carried no curvature.** Decision offered: retain as is on all seven; nothing to approve for application. Evidence `task3_trace.json`, `task3_classification.csv`, `DECISION_PACKAGE.md` §3. Nothing applied. **CLOSED 2026-09-15 (T2): the PI decided "retain as is" (2026-09-13); nothing applied.** |
| 1.32 | **Sign the validation protocol** | PI | `docs/VALIDATION_PROTOCOL_DRAFT.md`: the six checks the spec freezes, each with an exact statistic, a DRAFT threshold, its P17 calibration source and where that source stops applying; reserved seeds 17901–17905; what is deliberately not a threshold. Unsigned, it authorises nothing; missing thresholds block launch rather than invite post-hoc selection. **CLOSED 2026-09-15 (T2): SIGNED by the PI 2026-09-13 with one amendment — (d) is the prior fraction rejected as infeasible, with its uncertainty — frozen as `docs/VALIDATION_PROTOCOL.md` (commit `9b91420`); the draft retained beside it.** Applied to three runs (T2 D11): NOT PASSED. |
| 1.33 | **Why is configuration D infeasible over part of a defensible prior on NLDM, and is 15 °C the right first temperature?** | PI | **Opened 2026-09-15 (T2) with the measurement:** 2,000 prior draws (seed 17302) → **16.45 % rejected, Wilson 95 % [14.9 %, 18.1 %]**; the first infeasibility fires at **15 °C in 326 of 329** rejections (47 °C once, 50 °C twice); the three driver runs' own samples give 16.10 %, 14.50 %, 13.70 %. About 32 % of the prior is living (peak growth ≥ 50 % of 2.076 /h). The prompt's "~96 %" was P16's live-point fraction at iteration 6800 (765 of 800), not the prior — the dead stratum held 81.5 % of posterior *weight* from ~16 % of prior *volume* because its ceiling −18.68 out-scored most living points under the old omission. What makes a draw infeasible at 15 °C (which constraint binds first — the cold-side enzyme cost, maintenance, or the carbon cap) is not diagnosed here. `reports/T2_validated_posterior/task2_rejection.json`. |
| 1.34 | **Likelihood reproducibility in persistent pool workers — the R1 blocker** | PI | **Opened 2026-09-15 (T2 D11).** The tie-broken LP in a warm worker returns path-dependent vertices: run 3's crash point is stored at log L −18.480 and evaluates fresh to −19.7608540096 (three instances identical to 1e-12, warm to 5e-8); four of its 800 live points carry the same +1.28 offset; run 1 one at +4.8e-3; D6 saw 0.028 at a prior draw. Nested sampling needs an exact ordering; a stored value fresh evaluation cannot reproduce is fatal when loglstar overtakes it (run 3 at dlogz 2.6; P15's crash at 2.17 had the same signature). Candidate remedies, each a new registration, none applied: fresh model per evaluation (6.7 s build vs ~1.9 s evaluation, ~4–5× cost), a solver-state reset per call, or a tie-break proven state-independent at every temperature (P10 D1 found F LB's was not; D NLDM's evidently is not either at posterior points). Reserved seeds 17901–17903 are spent; 17904–17905 unused; new seeds must be registered for a re-run. **MEASURED 2026-09-16 (T3):** four schemes, 22 hashed inputs, 50 evaluations each in one persistent worker against a bit-reproducible fresh-process reference. **Only a fresh model per evaluation is deterministic** (0.0 deviation at every input and every evaluation), at a measured **3.2×** the current cost (5.70 s against 1.79 s per evaluation end-to-end, not the 4–5× estimated). **A solver reset per call is worse than doing nothing** (max deviation 23.28 against the current path's 1.82, at 63 % more cost, spreading order-1 excursions from 3 evaluations to 13 of 19 D-NLDM inputs): it discards the basis but not the degeneracy. **Gurobi's lexicographic tie-break is a different model** — O₂ differs from pFBA by up to 4.58 (D NLDM) and 8.40 (E LB), growth by 2.27 /h on E LB, with 111 of 150 E LB evaluations returning `numeric` — and is disqualified. Two magnitudes, plausibly one cause: D NLDM shows a 1e-8 haze with rare order-1 excursions, E LB (an LP *face*: FVA [0, 190] at 45–50 °C per P6 D3a) shows 1.54–1.82 routinely. **The corruption attaches to the evaluation, not to θ** — the crash point itself was clean over 50 evaluations while its siblings carried the +1.28 — so no θ can be certified by a spot check. `reports/T3_determinism/report.md`; the remedy decision is **1.35**. |
| 1.35 | **Adopt a deterministic likelihood-evaluation scheme, or accept non-reproducibility — the decision T3 measured for** | PI | **Opened 2026-09-16 (T3).** The only scheme that met the registered determinism bar is **a fresh model instance per likelihood evaluation** (T3 D3), at **3.2×** the current per-evaluation cost. Consequences if adopted: one 16-D D-NLDM run goes from ≈ 11–13 h to ≈ **35–43 h**, and the protocol's five runs from ≈ 60 h to ≈ **7–9 days** sequential; 1.17's eight remaining fits re-cost from ≈ 100 h to ≈ **320 h**. Options the PI may prefer instead, none measured here: parallelise across runs rather than within (the driver is sequential by registration, and 16 single-process runs would fit the machine); re-examine whether the tie-break itself can be made state-independent (P10 D1 already held F LB for this; T3's scheme C shows Gurobi's own hierarchical objective is *not* a drop-in substitute); or accept the defect and abandon nested sampling for this likelihood. **T3 implemented nothing.** A re-run also needs new registered seeds (17901–17903 are spent) and must state whether E/F configurations are in scope, since their face degeneracy is an order of magnitude worse. |
| 1.36 | **Parsa's per-medium N₀ and carbon constants: adopt as a new target identifier, or not** | PI | **Opened 2026-09-16 (H1 TASK 3)** from the assessment of 1.9. The derivation is sound and better founded than the growth-rate extrapolation it replaces; the arithmetic is verified. Adopting it changes a number the likelihood consumes for six of the nine registered fits, moving the respiration observable by −15.6 % (NLDM), −2.2 % (LB) and **−51.1 % (M9)**. Because the shift is a constant per medium and every fit is per-medium, `resp_scale` absorbs it exactly, so **R² is protected and the within-medium D/E/F comparison is too** — but `resp_scale`'s absolute value, its physical interpretation, every cross-medium comparison and every posterior already computed are not. **Recommended:** accept the derivation; register it as a core option, default OFF, gated 79/79 and 60/60 and turned on per strain, with the absorption *measured* rather than assumed; **sequence it after 1.35**, since nothing is gained by re-fitting while the likelihood is not yet deterministic and the shift costs nothing to defer. Also: reconcile the two documents' provenance for the 180 fg C µm⁻³, and pick one of the two routes to N₀ they propose. `reports/H1_handover/parsa_1_9_assessment.md`. **Nothing was applied and no derived table was altered.** |

Existing decisions reconciled: 1.14 (Candida predictor calibration) and 1.16 (Candida respiratory vertex) remain open. 1.15's remaining respiration-model issue is linked to 1.25/1.27; the old support choice 1.21 remains historically closed, not silently undone. 1.17 and 1.19 remain blocked, now by target revision and full validation. 1.20's meltome-tail interpretation remains open. 1.24 was acted on by P16 fixing dTm=0, but this did not validate inference and grants no authority to fix another parameter; further action now follows 1.27. 1.23's PI criterion decision remains closed. 1.22's lexicographic tie-break is deferred and needs a separate justified decision before adoption. External provenance requests 1.5–1.9 and the formal 1.4 confirmation are unaffected.
