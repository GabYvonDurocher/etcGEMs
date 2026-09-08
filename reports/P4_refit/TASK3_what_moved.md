# P4 TASK 3 — what moved, and why

## The finding that governs everything else: **no chain converged, and neither did his**

Every one of the nine refits is **NOT CONVERGED** by the stated criterion (chain length
> 40·τ_max **and** minimum n_eff ≥ 200): τ_max 146–245 against 1500–2000 steps, so chain/τ ≈
6–12.

**So are Parsa's.** Measured on his six committed chains with the same estimator:

| his run | steps | walkers | τ_max | chain/τ | n_eff | converged? |
|---|---|---|---|---|---|---|
| `configD_NLDM_full` | 2000 | 36 | 214.1 | 9.3 | 168 | **NO** |
| `configD_LB_full` | 2000 | 36 | 211.9 | 9.4 | 170 | **NO** |
| `configE_NLDM` | 1500 | 36 | 169.2 | 8.9 | 160 | **NO** |
| `configE_LB_freecmax` | 1500 | 36 | 160.5 | 9.3 | 168 | **NO** |
| `configF_NLDM` | 1500 | 36 | 182.4 | 8.2 | 148 | **NO** |
| `configF_LB` | 1500 | 36 | 160.4 | 9.4 | 168 | **NO** |

**The refits are no worse mixed than his.** Both families have run ~9 autocorrelation times.
Following the rule this prompt sets — *a non-converged chain is reported, never quoted* — **none
of the R² values below is a result**, and by the same rule the ten values P3 gated, and the ones
his report prints, are point estimates from chains that have not converged either. That is
stated neutrally: it is a property of the sampling budget, not of the model or of anyone's
diligence, and the fix is arithmetic — 40·τ ≈ 8 000 steps, four times the chain, ≈ 40 h for all
nine on this machine.

Two things would make that cheaper before anyone spends it: the **warm start silently failed**
in every fit here (P4 DECISIONS D3, now fixed — chains started at the emergent point instead of
the mode, which lengthens burn-in), and the acceptance fraction is 0.15–0.22, low enough that a
move-proposal change is worth trying.

## Table — indicative values only, none quoted as a result

Blanket-medium column = what P3 gated (his chains, his medium). Refit column = the canonical
settings, at the same parameter point P3 established for that configuration.

| fit | point | growth R² blanket → refit | Δ | resp R² blanket → refit | Δ | r_max | T_opt | acetate @37 °C | RQ @37 °C |
|---|---|---|---|---|---|---|---|---|---|
| **D NLDM** | median | 0.707 → **0.854** | **+0.147** | 0.725 → **0.802** | +0.077 | 1.563 | 41.0 | 13.5 | 1.05 |
| **D LB** | MAP | 0.896 → **0.196** | **−0.700** | 0.793 → 0.923 | +0.130 | 1.698 | 44.0 | 1.9 | 1.18 |
| **E NLDM** | MAP | 0.849 → **0.893** | +0.044 | 0.721 → **0.867** | +0.146 | 1.733 | 41.0 | 39.0 | 1.30 |
| **E LB** | MAP | 0.828 → **0.183** | **−0.646** | 0.801 → 0.866 | +0.064 | 1.512 | 44.0 | 11.4 | 1.15 |
| **F NLDM** | MAP | 0.905 → **0.858** | −0.047 | 0.964 → **0.562** | **−0.401** | 1.738 | 39.5 | 38.6 | 1.22 |
| **F LB** | MAP | 0.881 → **0.163** | **−0.718** | 0.852 → 0.909 | +0.056 | 1.515 | 44.0 | 13.8 | 1.17 |

## Attribution

**NLDM is unchanged to better; LB collapses.** The three LB growth R² fall by 0.65–0.72, to
0.16–0.20, with T_opt pushed to 44 °C. That is one movement with one candidate cause, and the
evidence points at it squarely:

* **the LB medium did not change** — LB is a committed component list, identical in his fits and
  in the refits, so the medium cannot be it;
* **c_max did**, from his fitted value to the canonical 120. And his own fits put LB's cap far
  higher: **256.7** (D LB, fitted), **459.3** (E LB freecmax, fitted), **509.9** (F LB, fitted).
  120 is 2–4× tighter than anything his LB fits chose.

**c_max = 120 is a glucose/NLDM recommendation, and P4 over-applied it to LB.** His sweep, and
the P2/P3 sensitivity table that supported adopting 120, are both computed on glucose-minimal
and NLDM only. No LB sensitivity was ever run. This is reported, not adjudicated: the single
run that would settle it is **configuration D on LB at c_max ≈ 260**, one fit, ~45 min.

**The NLDM movements cannot be separated**, and that is said rather than guessed: NLDM changed
medium (blanket → recipe with a sampled K) *and* cap (his fitted 146–179 → 120) at once. The
single-change run that would separate them is configuration D on NLDM under the **blanket**
medium at c_max 120 — one fit, ~70 min.

**Configuration F's respiration on NLDM falls 0.40** while E's rises 0.15, on the same medium
and the same table apart from bd-II's proton stoichiometry. Since these are non-converged
chains at a single point, this is recorded as unexplained rather than attributed.

## The medium clearance K: **not identified — the ceiling is a prior choice**

| fit | K median (L gDW⁻¹ h⁻¹) | 90 % CI | posterior/prior width | |
|---|---|---|---|---|
| D NLDM | 4.78 | [2.97, 7.60] | **0.58** | not identified |
| E NLDM | 4.15 | [2.71, 7.29] | **0.57** | not identified |
| F NLDM | 4.69 | [2.88, 8.03] | **0.64** | not identified |

The prior is K ∈ [2, 10]; the posterior returns 60 % of that width in every fit. Parsa measured
0.89 on R2A/NLDM; these are tighter but nowhere near identified.

**Stated plainly, as the prompt requires: the NLDM medium ceiling is a PRIOR CHOICE, not a
fitted quantity.** The data constrain it barely. The nominal K = 5 L gDW⁻¹ h⁻¹ sits inside every
posterior and every posterior median (4.15–4.78) is close to it, so nothing here argues the
nominal is wrong — only that the data cannot tell. Any statement of the form "the recipe medium
is the right ceiling because the fit chose it" is unsupported.

## RQ — reconciling the figures in circulation

Three numbers have been quoted and they are three different quantities:

| value | what it is |
|---|---|
| **~7–9** (his report, configuration C, NLDM) | RQ at the growth optimum, **blanket** medium, acetate line imposed, no carbon cap |
| **1.04** (P2 TASK 2, configuration C, NLDM) | the same quantity on the **recipe** medium — carbon-limited, so CO₂ is not inflated |
| **12.8 → 0.46** (Parsa, on receiving the recipe medium) | not configuration C: the *baseline* posterior model's RQ, blanket → recipe |

They agree. The blanket medium leaves carbon unlimited, so CO₂ runs far ahead of O₂ and RQ is
large (7–9, 12.8 depending on the configuration); the recipe ceilings make carbon limiting and
RQ falls to order 1 (1.04) or below (0.46). **In every case the mover is the medium, not the
carbon cap.**

The refits agree with this: at 37 °C, RQ is **1.05–1.30** on NLDM and LB — respiratory, at the
top of the window — and **0.26** for configuration D on M9. Nothing here is at 7–9 or at 12.8.
