# P4 — summary

| task | status | one line |
|---|---|---|
| **0** — merge P3, then scope | **DONE** | Merged and verified; nine fits scoped, ~19 of Parsa's directories excluded, runtime measured not guessed |
| **1** — pre-flight | **DONE** | Passed after catching two things; the four canonical settings read back from every resolved config |
| **2** — the nine refits | **DONE** | All nine ran (10 h wall); **none converged** |
| **3** — what moved | **DONE** | NLDM unchanged to better, **LB collapses**; K is **not identified**; RQ reconciled |
| **4** — M9 first light | **DONE** | The best growth fits in the exercise; the worst respiration fits |
| **5** — the record | **DONE** | The README now says which medium each number came from; two new open items |

Detail: [TASK3_what_moved.md](TASK3_what_moved.md), [TASK4_M9.md](TASK4_M9.md),
[DECISIONS.md](DECISIONS.md) (D0–D5).

---

## The finding that governs the whole run

**No chain converged — and neither did Parsa's.** All nine refits: τ_max 146–245 against
1500–2000 steps, chain/τ ≈ 6–12 against the ≥40 criterion. His six committed chains, measured
with the same estimator: τ 160–214, chain/τ **8.2–9.4**, n_eff 148–170. Both families have run
about nine autocorrelation times.

Applying this prompt's own rule evenly — *a non-converged chain is reported, never quoted* —
**nothing here is quoted as a result, and by the same measure neither are the ten R² values P3
gated nor the ones his report prints.** Stated neutrally: it is a property of the sampling
budget, not of the model or of anyone's diligence. The fix is arithmetic: 40·τ ≈ 8 000 steps,
four times the chain, ≈ 40 h for all nine on this machine. Not run; the cost is given so that
decision is a human's.

## Scope, and what it cost

Nine fits: the six behind the ten R² P3 gated, plus M9 for each configuration. Parsa's other
~19 calibration directories (`freebd`, `wideenv`, `nocap`, `_test`, `_resume`, `_olddata`,
`_kfit`, `_combined`, `_growthonly`) produce no quoted number and were excluded. Runtime
measured before spending: 0.27 s per likelihood evaluation → ~4–5 h estimated; **10 h actual**
(the warm start failed, D5 below, so every chain paid a full burn-in).

## TASK 1 — the pre-flight earned its place

The four canonical settings were **read back from each resolved config**, which is the exact
error P3 found (configuration D's cap leaking into E and F). All nine correct. Two things
changed before any sampler ran:

* **the behavioural checks are meaningless at the prior centre** and were re-run at a
  representative *fitted* point — at the prior centre NLDM looked fermentative and LB acetate
  was zero; at the fitted point every NLDM/LB fit is physiological (RQ 1.11–1.40);
* **M9 needs the carbon cap on E and F too** — on `glucose_minimal` nothing else limits carbon,
  and without it configuration F fermented (RQ 0.026) and E barely grew (3.7e-5).

## TASK 3 — what moved

| fit | growth R² blanket → recipe | Δ | resp R² blanket → recipe | Δ |
|---|---|---|---|---|
| D NLDM | 0.707 → **0.854** | **+0.147** | 0.725 → 0.802 | +0.077 |
| D LB | 0.896 → **0.196** | **−0.700** | 0.793 → 0.923 | +0.130 |
| E NLDM | 0.849 → **0.893** | +0.044 | 0.721 → 0.867 | +0.146 |
| E LB | 0.828 → **0.183** | **−0.646** | 0.801 → 0.866 | +0.064 |
| F NLDM | 0.905 → **0.858** | −0.047 | 0.964 → 0.562 | **−0.401** |
| F LB | 0.881 → **0.163** | **−0.718** | 0.852 → 0.909 | +0.056 |

**NLDM is unchanged to better; LB collapses.** Attributed: the LB medium did **not** change — it
is a committed component list, identical in both — so it cannot be the medium. `c_max` did, from
his fitted values to the canonical 120, and **his own LB fits chose 256.7, 459.3 and 509.9**,
2–4× higher. **`c_max = 120` is a glucose/NLDM recommendation and P4 over-applied it to LB**: his
sweep and the P2/P3 sensitivity behind it are computed on glucose-minimal and NLDM only, and no
LB sensitivity has ever been run. Reported, not acted on from one non-converged fit; **the single
run that settles it is configuration D on LB at c_max ≈ 260, ~45 min.**

The **NLDM** movements are **not separable** — medium and cap both changed — and that is said
rather than guessed; the single-change run that would separate them is named too.

## The medium clearance K — **not identified**

| fit | K median (L gDW⁻¹ h⁻¹) | 90 % CI | posterior/prior width |
|---|---|---|---|
| D NLDM | 4.78 | [2.97, 7.60] | **0.58** |
| E NLDM | 4.15 | [2.71, 7.29] | **0.57** |
| F NLDM | 4.69 | [2.88, 8.03] | **0.64** |

The posterior returns 57–64 % of a [2, 10] prior. Parsa measured 0.89; tighter here, nowhere near
identified. **Plainly: the NLDM medium ceiling is a prior choice, not a fitted quantity.** The
nominal K = 5 sits inside every posterior, so nothing argues it is wrong — only that the data
cannot tell, and "the fit chose it" is unsupported.

## RQ — the three figures reconciled

They are three different quantities and they agree: **~7–9** is configuration C on the *blanket*
medium; **1.04** is the same quantity on the *recipe* medium; **12.8 → 0.46** is the *baseline*
model, blanket → recipe. In every case **the mover is the medium, not the carbon cap.** The
refits sit at RQ 1.05–1.30 on NLDM and LB, and 0.26 for configuration D on M9.

## TASK 4 — M9, first light

| fit | growth R² | resp R² | r_max | T_opt |
|---|---|---|---|---|
| D M9 | **0.959** | 0.541 | 0.637 | 39.5 °C |
| E M9 | **0.987** | 0.160 | 0.691 | 41.0 °C |
| F M9 | **0.982** | 0.499 | 0.691 | 41.0 °C |

Against a measured peak of **0.717 h⁻¹ at 40 °C**. The best growth fits in the exercise and the
worst respiration fits. The posterior differs from the rich media in **capacity and only
capacity**: `kcat_scale` ≈ 0.9 against 1.4–1.7, `sigma` ≈ 0.48 against ≈0.7 — and σ lands on the
literature 0.45–0.5 instead of railing toward 1 as the rich fits do. Allocation is
indistinguishable across all three media.

Data-quality flags, checked: **OTU 2 (`M9`) is 7 non-monotonic rows at 4 temperatures and was not
fitted** — a control, not a series; the 25 °C no-growth row P3 found is in OTU 2, so it never
entered these fits; and the 45–47 °C replicate spread exceeds the mean, so the M9 collapse limb
is the least determined part of the curve.

## Verification

| check | result |
|---|---|
| Candida gate, `$CANDIDAS_ROOT` unset | rc=0, **79/79** |
| P1 gate (configurations A/B/C) | rc=0, **60/60** |
| nine refits | all completed; **all non-converged**, each recorded per fit |
| `stamp_reports.py --check` | rc=0 |
| **files touched under `strains/c*/`** | **none** — K4–K8 ran there in parallel; every commit staged an explicit path |
| read-only trees | `$PARSA_ROOT`, `$CANDIDAS_ROOT`, `$ECOLI_R2A`, `$ECOLI_M9` untouched |

**Merge note.** This branch is based on `ed56d4d`; `main` has since advanced through K4–K8. The
two files both lines of work touch are `docs/OPEN_ITEMS.md` and `reports/report_status.yaml`,
and both are **append-style** records — resolve by keeping both sets of rows. Nothing else
overlaps.

## What is worth doing next, in order

1. **One fit: configuration D on LB at c_max ≈ 260** (~45 min). It settles whether the LB
   collapse is the cap, which is the only material regression in this run.
2. **Longer chains** (~8 000 steps, ≈40 h for all nine) if any of these R² is to be quoted. The
   warm-start defect that lengthened this run's burn-in is fixed but untested at scale.
3. **An LB c_max sensitivity** — none has ever been run, and 120 was adopted without one.
