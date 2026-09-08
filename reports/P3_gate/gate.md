# P3 TASK 3 — the gate: configurations D, E and F against experiment

> ## NONE OF THESE R² IS A CONVERGED POSTERIOR — read this before any number below (added 2026-09-08, P5 TASK 2)
>
> P4 measured the integrated autocorrelation time τ on every chain in this family, and P5
> re-measured Parsa's six independently (same estimator, `emcee.autocorr.integrated_time`,
> τ_max over parameters; agreement to 0.1). **Every chain — his six committed ones and all nine
> P4 refits — has run about nine autocorrelation times against a ≥ 40 criterion.** This is a
> property of the sampling budget for this likelihood, not of the model and not of anyone's
> diligence; the step counts are conventional and are simply not enough for a posterior with
> this τ. It applies evenly to both families.
>
> | chains | steps × walkers | τ_max | chain / τ | n_eff | converged (chain > 40 τ and n_eff ≥ 200) |
> |---|---|---|---|---|---|
> | Parsa's six (`configD_NLDM_full`, `configD_LB_full`, `configE_NLDM`, `configE_LB_freecmax`, `configF_NLDM`, `configF_LB`) | 1500–2000 × 36 | 160–214 | **8.2–9.4** | 148–170 (first half discarded) / 296–340 (none discarded) | **NO**, all six |
> | P4's nine refits (D/E/F × NLDM/LB/M9, recipe medium, c_max 120) | 1500–2000 × 40 | 146–245 | **8.2–10.3** | 247–332 (sampler's own: walkers × (steps − 2τ) / τ) | **NO**, all nine |
>
> **What follows and what does not.** The ten R² values P3 gated, the values his report prints,
> and every R² in `reports/P4_refit/` are point estimates (MAP or posterior median) from
> unconverged chains. They are indicative; they are not validated model performance, and they
> must not be quoted as such. **P3's gate remains valid as a PORT check**: it reads the same
> parameter point out of his chain and recomputes his R² here to within 0.009, which proves the
> port reproduces his computation whether or not the chain it was read from converged. Those are
> two different claims and the second was never made by the gate.
>
> **The cost of fixing it** is arithmetic: 40 τ ≈ 8 000–10 000 steps per fit, four to five times
> the chain, ≈ 40 h for all nine on this machine (P4 ran 1500–2000 steps in 10 h). P4's
> warm-start repair should shorten the burn-in but is untested at scale. Until it is spent, no
> number in this family is a result. See `reports/P4_refit/TASK3_what_moved.md` and
> `docs/OPEN_ITEMS.md` 1.12.

**Result: all ten R² values his reports print reproduce, the worst to 0.009.** Configurations
D, E and F move from *ported* to *gated*.

Reproduce with `python reports/P3_gate/gate_def.py`; full table in `gate_def_table.csv`, the
headline rows in `gate_def_headline.csv`.

## How, without emcee

His six fits are committed as `chain.h5`, and his own figure script computes the reported R²
from a **single parameter point** out of the chain. So the gate *reads* that point and
recomputes the prediction here — ~32 deterministic solves per configuration. No sampler runs.
Exactly his recipe: grid `np.arange(8.0, 55.01, 1.5)`; prediction from `flux_tpc`, with
per-cell respiration `o2_uptake × gDW_per_cell × 32/60 × resp_scale`; R² by interpolating the
curve onto the observed temperatures, then `1 − SS_res/SS_tot`, linear on both axes.

## Table 1 — against the **pre-boundaryfix** data (what his figures used)

*(Added 2026-09-08, P5.) Every R² in this table and the next is read from a chain that ran ~9 autocorrelation times, his and ours alike — see the caveat at the top. The PASS column is a statement about the port reproducing his computation, which it does; it is not a statement that the value is a converged posterior, which none of them is.*

| config | medium | his run | point | quantity | his | port | Δ | verdict |
|---|---|---|---|---|---|---|---|---|
| **D** | NLDM | `configD_NLDM_full` | posterior median | growth R² | 0.71 | **0.707** | −0.003 | **PASS** |
| **D** | LB | `configD_LB_full` | MAP | growth R² | 0.90 | **0.896** | −0.004 | **PASS** |
| **E** | NLDM | `configE_NLDM` | MAP | growth R² | 0.85 | **0.849** | −0.001 | **PASS** |
| | | | | respiration R² | 0.72 | **0.721** | +0.001 | **PASS** |
| | | | | F_ETC | 0.28–0.32 | **0.282** | in range | **PASS** |
| **E** | LB | `configE_LB_freecmax` | MAP | growth R² | 0.83 | **0.828** | −0.002 | **PASS** |
| | | | | respiration R² | 0.81 | **0.801** | −0.009 | **PASS** |
| | | | | F_ETC | ≈0.32 | **0.284** | −0.036 | see below |
| **F** | NLDM | `configF_NLDM` | MAP | growth R² | 0.91 | **0.905** | −0.005 | **PASS** |
| | | | | respiration R² | 0.96 | **0.964** | +0.004 | **PASS** |
| **F** | LB | `configF_LB` | MAP | growth R² | 0.88 | **0.881** | +0.001 | **PASS** |
| | | | | respiration R² | 0.85 | **0.852** | +0.002 | **PASS** |
| | | | | C_max | ≈510 | **509.9** | +0.02 % | **PASS** |

Tolerance 0.01 in R². The one number outside it is **F_ETC on LB, 0.284 against his stated
≈0.32** — his text gives the same 0.32 for both media ("The F_ETC landed at ~0.32 which was the
same as R2A/NLDM fit"), while the two fits' MAPs are 0.282 (NLDM) and 0.284 (LB): the port's
two values agree with each other and with his *NLDM* value, and his LB figure is quoted to one
significant digit in prose. Recorded, not chased.

## Table 2 — against the **current** data, and what the boundary fix does

| config | medium | growth R² pre-fix → current | Δ | respiration R² pre-fix → current | Δ |
|---|---|---|---|---|---|
| D | NLDM | 0.7066 → 0.7276 | **+0.021** | 0.7246 → 0.7268 | +0.002 |
| D | LB | 0.8964 → 0.8950 | −0.001 | 0.7931 → 0.7945 | +0.001 |
| E | NLDM | 0.8492 → 0.8644 | **+0.015** | 0.7214 → 0.7213 | −0.000 |
| E | LB | 0.8284 → 0.8260 | −0.002 | 0.8014 → 0.8019 | +0.000 |
| F | NLDM | 0.9051 → 0.9179 | **+0.013** | 0.9636 → 0.9625 | −0.001 |
| F | LB | 0.8809 → 0.8799 | −0.001 | 0.8524 → 0.8527 | +0.000 |

**The fix improves NLDM growth by 0.013–0.021 and changes nothing else by more than 0.002.**
That is what one expects from adding four measured zero-growth points at 50 °C to the medium
whose collapse limb was previously empty. No reported conclusion changes.

## Every movement, attributed to a named cause

The prompt's rule is that an unattributable movement is a FAIL. Four causes had to be
established before anything matched, each by testing rather than reading (P3 DECISIONS D2):

1. **The medium: blanket NLDM, not the recipe.** As in P1 and P2 — his fits are dated 28 Jul –
   18 Aug and the recipe entered his script on 4 Sep. Evidence: under the recipe the same MAPs
   give growth R² 0.667 (E) and 0.574 (F) against his 0.85 and 0.91.
2. **His O2-sink closure order.** He closes the four sinks *after* building the provider; the
   core closes them inside `from_gecko`, before the sector layer calibrates
   `translation_coeff`. P1 measured **no** effect for configurations A–C. With an ETC area
   constraint there is one: configuration E on NLDM gives respiration R² **0.721 in his order**
   and **0.608 in ours**. His order reproduces his 0.72. Both are in the table.
3. **The parameter point.** Configurations E and F quote the **MAP**; configuration D quotes the
   **posterior median** (0.707 at the median, 0.798 at the MAP, against his 0.71). Measured both
   ways for every fit.
4. **Which run.** The directory names mislead: `calibration_configE_LB` pins C_max at 459, while
   his reported LB numbers come from `calibration_configE_LB_freecmax`; `calibration_configF_NLDM`
   (no cap) is the reported one, not `_cap`, `_recipe` or `_kfit`. The gate reads each run's own
   `meta.json`.

And a fifth, which is a correction to P1 rather than an attribution: **his configuration F is
configuration E's ETC table plus a non-electrogenic bd-II**, not the Bekker-turnover table in
his `configF.py` — that table is used by three diagnostic scripts and by nothing that produced
a reported number. P1 wired the wrong one. Configuration F now uses
`etc/complexes_configF_as_fitted.csv`; the Bekker table is kept as `etc/complexes.csv`, a
labelled variant.

## What is NOT gated, and why

**The M9 data set.** It is ingested, and no configuration was ever fitted against it — every
`meta.json` names `NLDM` or `LB`, both drawn from the R2A/LB file. Gating against data no fit
ever saw would be inventing a comparison. It is the obvious next dataset to fit.
