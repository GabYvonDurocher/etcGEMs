# P14 — fix the sampleability test, then earn the posterior

_Run 2026-09-10 on `../etcGEMs-venv`, branch `p14/posterior`, from main after PRs #28 (Y3) and #29
(P13) merged._

**Outcome: the test was corrected and it changed the verdict on the line that mattered — but four
other lines test JUMP, so by the prompt's own instruction TASK 2 did not start and no posterior is
quoted.** The case for proceeding anyway is measured, argued, and put to the PI rather than acted
on.

---

## TASK 0 — both merged, and the state P13 left verified rather than assumed

- **#28 (Y3) merged**, then **#29 (P13)**, which conflicted. Resolved keeping **both** sides, file
  by file, in the primary tree (clean and on main, so a temporary worktree would have added
  nothing):
  - `reports/synthesis/evidence.csv` — both appended rows after a common base ending at P12g. Kept
    main's 78 ids (base + Y3's `O1–O7`, `D1–D5`) and appended P13's 7 (`P13a–P13g`).
  - `docs/OPEN_ITEMS.md` — **each side touched only its own item**: P13 restated **1.19** (main was
    identical to base there), Y3 extended **1.20** (P13 was identical to base there). Verified by
    diffing each against the merge base, then kept P13's 1.19 and Y3's 1.20.
  - `reports/report_status.yaml` — kept **both** entries, `Y3_tm_shift` and `P13_support`.
  - `reports/synthesis/PROVENANCE.md` — a stamp; **regenerated, not hand-merged**.
- **Gates with the option OFF: Candida 79/79, P1 60/60**, all three `tpc` runs rc=0.
- **`support: clamp` is set in `strains/eciML1515/gas_exchange.yaml` and nowhere else** (verified by
  grep across `strains/`); the core default is `current` (`calibration_multi.py:291`).
- **State-independence re-confirmed after the merge**: ten fresh-model evaluations at p38 give
  **−9.9893897954 ten times, spread 0.0000000000**, matching P13's −9.9894.

**D0 — moves R1 only.** R2 is *measured*, not fixed — and Y3 makes it worse, adding `dTm`/`tm_scale`
as not jointly identified on top of P11's five flat parameters. R3 is untouched. R4 is untouched.
Stated in advance: agreement between two runs would establish the posterior is **reproducible**, not
**right**.

## TASK 1 — the corrected test

The old rule is **retired, not patched**. Recorded reason: it was a proxy for discontinuity that
measured **steepness**, and it was **centre-dependent** — 3.20 at θ_A against 8.55 at p38, same
line, same instrument, same likelihood.

The criterion was written into `DECISIONS.md` **before any of its data existed** (D1): **(a)**
discontinuity by grid refinement, SMOOTH if every halving ratio is in [0.35, 0.65], JUMP if any
exceeds 0.80; **(b)** plateaus — PASS if no run of exactly-equal values spans more than 10 % of a
line; **(c)** feasibility boundaries reported and exempt. **SAMPLEABLE = (a) SMOOTH on every line
AND (b) PASS.**

### Old rule against new, side by side

| line | old rule: largest step | old | new (a) series | new (a) | plateaus (b) |
|---|---|---|---|---|---|
| `axis:topt_scale` | 8.5517 | **FAIL** | 8.5517 → 4.3325 → 2.2295 → 1.1236 | SMOOTH | 0 |
| `axis:dCp_scale` | 4.8156 | pass | 4.8156 → … → 0.3791 | **JUMP** | 0 |
| `axis:kcat_scale` | 2.7260 | pass | 2.7260 → 1.3808 → 0.6938 → 0.3484 | SMOOTH | 0 |
| `random1` | 2.5010 | pass | 2.5010 → 1.4430 → 1.0535 → 0.8849 | **JUMP** | 0 |
| `random2` | 1.1993 | pass | 1.1993 → 0.6041 → 0.3032 → 0.1519 | SMOOTH | 0 |
| `PC3` | 0.7895 | pass | 0.7895 → 0.3974 → 0.1991 → 0.0996 | SMOOTH | 0 |
| `PC1` | 0.7111 | pass | 0.7111 → … → 0.1453 | **JUMP** | 0 |
| `PC2` | 0.6839 | pass | 0.6839 → 0.5672 → 0.5073 → 0.4672 | **JUMP** | 0 |
| `random3` | 0.3682 | pass | 0.3682 → 0.1877 → 0.0964 → 0.0500 | SMOOTH | 0 |
| `axis:clearance_mult` | 0.2606 | pass | 0.2606 → 0.1324 → 0.0667 → 0.0335 | SMOOTH | 0 |
| `axis:ngam_scale` | 0.0639 | pass | 0.0639 → 0.0323 → 0.0162 → 0.0081 | SMOOTH | 0 |
| `axis:f_maint` | 0.0566 | pass | 0.0566 → 0.0284 → 0.0142 → 0.0071 | SMOOTH | 0 |

### (b) PLATEAUS — PASS, and this is the test that matters

**0 of 480 adjacent evaluations are exactly equal.** Longest plateau run: **0 intervals**, on every
one of the twelve lines, against a 10 % rule. The property that voids nested sampling's
volume-shrinkage estimate — a set of *positive prior volume* on which the likelihood is *exactly*
constant — **is absent**.

On the exactly-flat parameters, predicted in D1 before measuring: **a flat *direction* is not a
plateau.** If the likelihood does not depend on `kappa_scale`, the level set {L = c} is a
codimension-1 surface extruded along that axis and still has **zero** 16-dimensional volume, so
shrinkage is unaffected; dynesty returns that parameter's prior as its marginal. That is what
"unidentified" means — an **R2** statement, not an R1 one.

### (a) DISCONTINUITY — and the line that stopped P13 tests SMOOTH

**`axis:topt_scale`: 8.5517 → 4.3325 → 2.2295 → 1.1236, ratios 0.507, 0.515, 0.504.** Textbook
linear scaling in h. **The 8.55 units are steepness, now measured rather than argued**, and P13's
stop is vindicated as correct discipline on a rule that was wrong.

A first pass tested each line's largest step *overall*; on **eight of twelve that is the feasibility
transition** D1(c) exempts, identified exactly — location and size equal P13's committed transition
table to the digit, all converging to ≈1.56, the size of one temperature's contribution entering or
leaving the scored set. D2 records the correction and the second pass tests the largest
**feasible-to-feasible** step, recording the support set at *every* refinement evaluation so a
crossing hiding inside a refined interval is caught rather than read as a jump.

**Four lines still JUMP**, and all four are one mechanism. Bisected to 1.95e-04 sd:

| line | step | growth term | respiration term | % growth | biggest O₂ move |
|---|---|---|---|---|---|
| `axis:dCp_scale` | 0.3791 | −0.0090 | **−0.3702** | 2 % | 25 °C, 0.278 → 0.228 (**0.82×**) |
| `PC1` | 0.0525 | +0.0017 | **+0.0508** | 3 % | 15 °C, 1.153 → 1.452 (**1.26×**) |
| `PC2` | 0.4007 | +0.0010 | **+0.3997** | 0 % | 20 °C, 1.462 → 2.718 (**1.86×**) |
| `random1` | 0.5886 | −0.0052 | **−0.5834** | 1 % | 20 °C, 1.174 → 0.665 (**0.57×**) |

**97–100 % respiration term, growth unchanged to five decimal places, O₂ moving 0.57–1.86× at a
single cold temperature.** This is **P9's LP vertex switch** — made deterministic by P10's tie-break
(state spread 0.0000000000, measured twice) and cut by the 1.42 floor from **13–72 log-likelihood
units to 0.05–0.59**.

## TASKS 2 and 3 — NOT RUN

*"If any line tests JUMP: STOP and report which, where, and its refinement series. Do not start
TASK 2."* Four lines test JUMP. **The two runs were not started; no posterior, log Z, agreement
verdict, `dTm` interval or R² is quoted, because none was computed.** The two predictions carried
forward from P13 remain unevaluated for the same reason.

## The decision this leaves — put to the PI, not taken

**The stop was honoured. The case for lifting it is this, and it is evidence, not preference:**

1. **(b) — the test the prompt itself calls decisive — passes perfectly**, 0/480.
2. **A jump is not a plateau, and nested sampling is insensitive to it.** The estimator depends on
   X(L), the prior mass above L. A discontinuity in L(θ) leaves an *interval of likelihood values
   carrying no prior mass*: X is flat there, no live point lands in it, nothing is mis-estimated. A
   plateau puts an **atom** in the distribution of L, which is what breaks the shrinkage argument.
   Only one of the two is fatal, and the surface has none of it.
3. **The jumps are 0.05–0.59 units** — below the 1–3 unit LP kink scale P9/P10 measured and P11
   accepted as irreducible.
4. **They are not removable under this prompt's constraints.** Their mechanism is the pFBA vertex;
   the lexicographic tie-break that would address it is item **1.22**, excluded here by name.

So D1's conjunction is **over-strict in its first conjunct**: it demands a property the sampler does
not need. That criterion was mine, and it is recorded rather than exercised — because moving it now
would be the fourth time in this series that a threshold shifted after its data were seen. **The
options are (a) lift the (a)-conjunct and run, (b) implement 1.22 first and re-test, or (c) keep the
rule.** OPEN_ITEMS 1.23.

## Reconciliation against §0c

- **Which of R1–R4 moved: none closed.** R1 advanced — the sampleability test now measures what it
  claims to, and the surface has no plateaus — but no posterior was earned. R2 got *worse* as a
  matter of record, not of fact: Y3 adds `dTm`/`tm_scale` to the unidentified set. R3 and R4
  untouched.
- **Retracted or qualified, numbers unedited:** the **old absolute rule** is retired with its
  failure demonstrated (`topt_scale` SMOOTH at 8.55); **P13's stop is confirmed correct** on the
  rule as it stood, and its blocking line is now shown to be steepness.
- **What this does NOT license:** quoting any posterior; unblocking 1.17; or claiming the surface is
  sampleable — four lines carry genuine, if small, discontinuities.
