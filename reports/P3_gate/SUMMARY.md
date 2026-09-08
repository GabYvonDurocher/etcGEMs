# P3 — summary

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

| task | status | one line |
|---|---|---|
| **0** — merge N3 then P2 | **DONE** | Both merged in order; the expected conflict did not arise and both sentences survive |
| **1** — ingest the respirometry | **DONE** | Both media sets, both versions, 144 KB; **no hard-coded path existed to replace** |
| **2** — what the boundary fix did | **DONE** | Rows added only, every shared row bit-identical; the added rows are intended zero-growth observations, established from the code and the logs |
| **3** — **THE GATE** | **DONE — PASSES** | **All ten R² values his reports print reproduce, worst 0.009** |
| **4** — adopt his recommended c_max | **DONE** | 60 → **120** on his own sweep; T_opt returns to the uncapped optimum and overflow is non-zero again |
| **5** — the method caveats | **DONE** | Three, each with evidence from the data; reported, not adjudicated |

Detail: [gate.md](gate.md), [TASK4_cmax.md](TASK4_cmax.md), [DECISIONS.md](DECISIONS.md) (D0–D4),
`strains/eciML1515/respirometry/README.md`.

---

## TASK 0 — merged, in order, and the conflict that was not

N3 (`35f87ce`) then P2 (`c3f66be`), pushed. **The expected conflict in
`reports/ecoli_tpc/report.qmd` did not arise** — the two sentences are in different sections, so
git merged them cleanly. Both survive, N3's first in the document:

> **N3**, in the O4 bullet: *"This attribution is conditional on the constraint regime and not a
> medium-independent property of the organism: at this tuned rich operating point the
> biosynthesis/translation cap has slack at every temperature on the grid … at the same strain's
> nominal glucose-minimal operating point that cap does bind at T_opt, and there the optimum
> tracks the measured allocation curve rather than the envelope."*
>
> **P2**, in "Interpretation and caveats": *"That attribution for T_opt holds within a fixed
> constraint regime and not across regimes: three separate constraints — the sector re-grounding,
> the translation cap, and a total-carbon cap — have each been shown to relocate T_opt by several
> degrees, while CT_max has been insensitive to all three, so T_opt should be quoted with its
> binding constraint named."*

The measurement, then the rule that follows from three of them. Verified after each merge, exit
codes checked explicitly: Candida gate **79/79**, P1 gate **60/60**, seven strains
**byte-identical**, `stamp_reports.py --check` clean once the newly-arrived
`reports/N3_output_audit/` was stamped, the D/E/F notice still in place. Both PRs closed, both
branches deleted.

## TASK 1 — ingested

`strains/eciML1515/respirometry/`, 144 KB: the derived table for **both media sets** in **both
versions** (current and pre-boundaryfix, named `..._20260907_prefix.csv`), plus
`otu_cell_sizes`, `otu_names`, the replication summaries and the measured activation energies.
**Not copied**, and recorded as living at `$ECOLI_R2A` / `$ECOLI_M9`: the raw and intermediate
oxygen exports (12–15 MB each), `figures/`, `models/`, `scripts/`, the run logs.

**Hard-coded paths replaced: none, and that is the honest answer.** P1 folded configuration D
into `calibration_multi` instead of porting `calibration_configD.py`, so
`C:\Users\Parsa\Desktop\Presense_Analysis\…` never entered this repository's code. It appears
only in prose — the three ungated banners and the P1/P2 reports — all updated in TASK 3.

## TASK 2 — the boundary fix

A one-hunk change to `06_oxygen_fits.R`. **The added rows are intended observations of no
measurable growth, not fitting failures** — established from the code and the logs, not guessed:

> *"`r` pinned at its LOWER bound is not a fit failure: above CTmax the true growth rate really
> is ~0 … Vetoing it silently deleted the thermal-collapse limb"* — and the run log says it per
> series: `[boundary] at bound: r  (r at lower bound -> treated as zero growth, KEPT)`,
> distinguished from series it still drops. Both `Skipped_Series_Log.csv` are empty.

**Every row present before the fix is bit-identical after it**; the fix only adds. **+4** in
R2A/LB (all 50 °C) and **+12** in M9 — and M9 is not what the prompt describes: five at 50 °C,
three at 47, three at 45, and **one at 25 °C**, a no-growth series at a benign temperature
(`K` = 8.4e-6), not a thermal-collapse point.

**Effect on the R² values: ≤ 0.021**, and all of it an improvement in NLDM growth (D +0.021,
E +0.015, F +0.013); LB and every respiration R² move by ≤ 0.002.

## TASK 3 — the gate passes

| config | medium | his growth R² | port | his respiration R² | port |
|---|---|---|---|---|---|
| **D** | NLDM | 0.71 | **0.707** | — | 0.725 |
| **D** | LB | 0.90 | **0.896** | — | 0.793 |
| **E** | NLDM | 0.85 | **0.849** | 0.72 | **0.721** |
| **E** | LB | 0.83 | **0.828** | 0.81 | **0.801** |
| **F** | NLDM | 0.91 | **0.905** | 0.96 | **0.964** |
| **F** | LB | 0.88 | **0.881** | 0.85 | **0.852** |

plus `C_max ≈ 510` → **509.9** and `F_ETC ≈ 0.28–0.32` → **0.282 / 0.284**. Worst difference
**0.009**. **No emcee**: his six fits are committed as `chain.h5` and his figure script computes
the R² from one point out of the chain, so the gate reads that point and recomputes the
prediction — ~32 deterministic solves per configuration.

**Four causes had to be established by testing before anything matched** (DECISIONS D2), each a
named cause in the table: the **blanket NLDM medium** his fits used; **his O2-sink closure
order**, which matters once an ETC area constraint is present where P1 showed it did not for
A–C (E/NLDM respiration **0.721 his order vs 0.608 ours**); the **parameter point** (D quotes the
posterior median, E and F the MAP); and **which run** each number came from (`configE_LB` pins
C_max at 459 — the reported numbers are `configE_LB_freecmax`).

**A fifth is a correction to P1:** his configuration F is configuration **E's** ETC table plus a
non-electrogenic bd-II — his own note reads *"0 H+ only (config-E turnovers via E weights)"*.
The Bekker-turnover table in his `configF.py` produced no reported number; P1 wired it.
Corrected; the Bekker table is kept as a labelled variant.

And one bug of mine, recorded because it briefly looked like a finding: the first gate run left
the `gasflux_configD` overlay's carbon cap on, so every E and F run silently carried a
230 mmol C cap it was never fitted with — which is what made NLDM look irreproducible
(respiration R² −2.5). Fixed before any conclusion was drawn.

`reports/ecoli_gasflux/README.md` now opens with the gated result; the three overlay banners say
GATED.

## TASK 4 — c_max 120, on his evidence

| medium | T_opt | r_max | acetate @T_opt | RQ |
|---|---|---|---|---|
| glucose | 37.5 → **38.0** | +36 % | **0 → 23.53** | 1.073 → 1.099 |
| NLDM | 32.5 → **39.5** | +76 % | **0 → 3.90** | 0.928 → 1.109 |
| LB | 33.0 → **39.5** | +83 % | **0 → 2.32** | 0.992 → 1.176 |
| BHI | 32.5 → **39.5** | +83 % | **0 → 2.32** | 0.998 → 1.176 |

**T_opt returns to the uncapped optimum** (38.0 glucose, 39.0 NLDM): the −6.5 °C displacement at
60 is gone, and 120 sits in the flat region of P2's sensitivity table (T_opt 0.00 % / 1.28 %
against 1.32 % / 16.67 % at 60). **Acetate overflow is non-zero on every medium**, where at 60 it
was exactly zero everywhere — a cap below the overflow onset makes configuration D's emergent
overflow unobservable. RQ 1.10–1.18 is inside the 0.96–1.18 his own table gives for 120.

Cited to his Gas Flux report §4 ("*C_max ≈ 100–120 is the sweet spot*"); 120 rather than 100
because at 100 overflow is zero on NLDM. `c_max = 60` is kept as
`gasflux_configB_cmax60.yaml`, labelled a sensitivity, and **P1's gate reads that run and still
passes 60/60**.

Also recorded: on the canonical recipe medium configuration C's NLDM RQ is **1.04**, not the
≈7–9 his report gives — the high value was the unlimited medium, not the absent cap.

## TASK 5 — the caveats, with evidence

In `strains/eciML1515/respirometry/README.md` and in the gas-flux report:

* **the inoculum back-projection is off in every row of both sets** —
  `delta_Ninoc_to_N0_min = 0` in **117/117** and **66/66**, `N0 == N_inoculation` throughout;
* **`cell_volume_um3` = 2 and `cell_carbon_fg` = 350 are typed constants**, one value across
  every row — and the pipeline's own log prints **21.21 µm³ / 2120.58 fg** from `config.R`,
  ~6× apart;
* the M9 project's `config.R` still carries the R2A/LB condition labels.

**Immune:** activation energies, curve shapes, RQ, ratios, and the **growth** R²
(`growth_C_per_C_h` is a specific rate). **Affected:** `R_O2_mg_cell_min`, `CUE`, absolute
per-cell rates and therefore **the respiration R²** — and the fitted `resp_scale` (4.7–11.0)
absorbs exactly this kind of offset, so the respiration R² is a statement about **shape**.
Reported; his results are not revised.

## Verification

| check | result |
|---|---|
| Candida gate, `$CANDIDAS_ROOT` unset | rc=0, **79/79 PASS** |
| P1 gate (configurations A/B/C) | rc=0, **60/60 PASS** |
| P3 gate (configurations D/E/F) | **10 of 10 reported R² reproduced, worst 0.009** |
| eciML1515 / mmaripaludis / syn6803 TPCs | rc=0, **byte-identical** |
| the four Candida `transfer_candida` runs | rc=0, **byte-identical** |
| `stamp_reports.py --check` | rc=0 |
| committed outputs regenerated | only what TASK 4 names: `gasflux_configB` (c_max 60→120), plus the new `configB_cmax60`, `configD`, `configE`, `configF` runs and configuration F's corrected table |
| read-only trees | `$PARSA_ROOT`, `$CANDIDAS_ROOT`, `$ECOLI_R2A`, `$ECOLI_M9` untouched |

## For Parsa

Three of the four questions are now answered from his own material; one remains, and it matters
more than before.

1. **c_max** — answered by his own sweep; 120 adopted, 60 kept as a sensitivity. Confirm.
2. **Transporter k_cat** — 300, settled by reproduction (P2).
3. **NLDM medium — still open, and now consequential.** Every D/E/F fit used the **blanket**
   medium; the recipe ceilings are canonical here. So the model his R² values came from and the
   model now quoted are not the same. Re-fitting on the recipe medium is the resolution, and it
   is an emcee job.
4. **New:** which configuration-F ETC table is intended (his fits used E's; the Bekker table
   produced no reported number), and the per-cell respiration constants (§ TASK 5).
5. **M9 is ingested and unfitted** — every `meta.json` names NLDM or LB. It is the obvious next
   dataset.
