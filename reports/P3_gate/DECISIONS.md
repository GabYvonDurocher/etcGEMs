# P3 — decisions

Standing rules carry over. `$PARSA_ROOT`, `$CANDIDAS_ROOT`, `$ECOLI_R2A` and `$ECOLI_M9` are
READ ONLY.

---

## D0 — the expected merge conflict did not arise, and both sentences survive

**Where:** TASK 0. N3's caveat is in the O4 bullet and P2's rule is in "Interpretation and
caveats" — different sections, so git merged them cleanly. Verified by reading both back;
N3's comes first in the document, as required. Nothing was resolved by hand and nothing was
discarded.

## D1 — the gate reads his committed chains; that is not sampling

**Where:** TASK 3.

His D/E/F R² values are goodness-of-fit of a *fitted* model, so reproducing them appears to
need emcee — which this prompt forbids. It does not: the six fits are committed as `chain.h5`,
and his own figure script recomputes the R² from a single parameter point out of the chain.
So the gate **reads** the MAP (and the posterior median) from each chain and recomputes the
prediction and the R² here, in ~32 deterministic solves per configuration.

**Decided:** gate this way. No sampler is run, and nothing about his posterior is re-derived —
only the model prediction at a point he already published.

## D2 — four things had to be established rather than assumed before any number matched

**Where:** TASK 3. Each was found by testing, and each is a named cause in the gate table.

1. **His configuration F is configuration E's ETC table plus a non-electrogenic bd-II.** His
   fits and figures call `configE.add_etc_area_constraint` and only add
   `configF.set_bdII_nonelectrogenic`; his own comment reads "0 H+ only (config-E turnovers via
   E weights)". The alternative table inside his `configF.py` (bd split, Bekker turnovers
   225/218/818 s⁻¹) is used by three diagnostic scripts and by **nothing that produced a
   reported number**. **P1 read `configF.py` and wired that table as configuration F — that was
   wrong**, and the gate is what surfaced it. Configuration F now uses
   `etc/complexes_configF_as_fitted.csv` (E's areas and turnovers, bd split only so bd-II can
   carry `h_p_target = 0`, so the area expression is unchanged); the Bekker table is retained as
   `etc/complexes.csv`, a labelled variant.
2. **Which run each reported number came from.** The names mislead: `calibration_configE_LB`
   pins `C_max` at 459 while his report says "a fitted light carbon bound" — the reported
   numbers are from `calibration_configE_LB_freecmax`. `calibration_configF_NLDM` (no cap) is
   the reported one, not `_cap`, `_recipe` or `_kfit`. The gate reads each run's own
   `meta.json` rather than trusting the directory name.
3. **The parameter point differs between configurations.** E and F quote the **MAP**
   (`scripts_configE_fig.py`); configuration D's 0.71 and 0.90 are the **posterior median**
   (0.707 and — at the MAP — 0.896; measured both ways). Both are reported.
4. **The O2-sink closure ORDER matters here, where P1 found it did not.** P1 measured no effect
   for configurations A–C. With an ETC area constraint it does: configuration E on NLDM gives a
   respiration R² of **0.721 in his order** (sinks closed after the provider is built) against
   **0.608 in ours** — his order is what reproduces his 0.72. The gate reports both.

**And one bug of my own, recorded because it briefly looked like a finding:** the first gate
run built the model from the `gasflux_configD` overlay and left that overlay's carbon cap
switched on, so every configuration-E and -F run silently carried a 230 mmol C cap it was never
fitted with. That is what made NLDM appear irreproducible (respiration R² −2.5 against his
+0.72). Fixed before any conclusion was drawn; the gate now applies only what each fit's own
`meta.json` says.

## D3 — c_max 120, on his evidence, and 60 kept as a labelled sensitivity

**Where:** TASK 4.

The change is **his recommendation, not ours**: his Gas Flux report sweeps 60/100/120/180 and
concludes "C_max ≈ 100–120 is the sweet spot", while calling the growth shape at 60 a "flat
plateau". Within his range, **120** rather than 100 for one measured reason: at 100 acetate
overflow is **zero on NLDM**, and a cap that suppresses overflow defeats the configuration it
exists to support. At 120 overflow is non-zero on every medium.

The value lives in the strain's `gas_exchange.carbon_cap` with the citation, and the experiment
overlay adopts it. `c_max = 60` is kept as `configs/experiments/gasflux_configB_cmax60.yaml`,
explicitly labelled a sensitivity, and **P1's gate now reads that run**, because the gate's job
is to reproduce his figure and his figure used 60. The gate still passes 60/60.

## D4 — the M9 set is ingested but not gated against

**Where:** TASKS 1 and 3.

Parsa sent M9 as well as R2A/LB, and both are ingested. **No configuration was ever fitted
against M9** — every `meta.json` names `NLDM` or `LB`, both of which come from the R2A/LB file
(OTU 1 and OTU 2). So M9 is committed as strain data, its boundary-fix diff is reported, and it
is **not** used in the gate: gating against data no fit ever saw would be inventing a
comparison. It is the obvious next dataset to fit, and that is a human's call.
