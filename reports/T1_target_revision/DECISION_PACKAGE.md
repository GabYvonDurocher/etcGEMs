# T1 decision package — for the PI

_Prepared 2026-09-13 by T1. Three decisions and a protocol for signature. **Nothing below has been
acted on: no option is on, no candidate is implemented, no correction is applied, no fit has run.**
Sections marked ⏳ carry numbers from batches that were still running when this skeleton was
written; they are filled from the audited CSVs, never from memory._

---

## 1. `f_metab` — ONE decision: approve removal / approve wiring as a new hypothesis / neither

### The finding: **(i) intentional by design.**

The sampled `f_metab` **does not enter configuration D**, and the code, the configuration and the
published report all say so (DECISIONS D2 for the verbatim quotes and blame):

- `enzyme_cost.py:600–607` — the growth-law branch computes `f_metab,0 = 1 − f_maint − f_bio,0` and
  its own comment says *"the measured f_metab arg is ignored"*; the only remaining reader of the
  argument is a simplex guard that cannot fire (max sum 0.95 < 1).
- `gasflux_configD.yaml:17–18` — `biosynthesis_growth_law: true`, `allocation_from_data: null`:
  the exact combination that reaches that branch.
- `report.qmd:363` — publishes `f_metab,0 = 1 − f_maint − f_bio,0` and `f_metab(μ) = f_metab,0 − s·μ`.
- History: sampled on 2026-07-08 (`8c0914c`) under the static-partition design where it mattered;
  the superseding law written 2026-07-09 08:27 (`922e13d`) with its author stating the consequence;
  switched on at 09:17 (`96e64c3`) with a docstring that is true of `f_maint` and false of
  `f_metab`. A documentation discrepancy, not a wiring omission.

**`f_maint` is a different case and stays sampled**: it sets the pool bound and the maintenance-ATP
bound (`:606–607`, `:614–618`).

### The prepared removal (default OFF, not turned on)

`build_gasflux_specs(cfg)` now accepts `remove_inactive: ["f_metab"]` (drops the coordinate; the
normalised prior integrates out to factor one) and `diagnostic_coords: [...]` (appends inactive
coordinates with a declared prior and `pert=None`, which `to_pert` provably never forwards to the
model — the mechanism for the protocol's (a) and (b)). Gate with it OFF: **K1 79/79, P1 60/60**,
byte-identical modulo the worktree path.

### The invariant proof ⏳

Old target versus removal-only target at every registered audit point, plus the old target with
`f_metab` swapped to 0.15 / 0.28 / 0.45 at the same active point. Registered tolerance 1e-6.
First point (D44's parent): old **−17.9725**, removal **−17.9725**, max difference **1.28e-11**,
reproducing the saved −17.972547016139384. *Full counts and the maximum difference: from
`task1_invariant.csv` + `task1_invariant_batch2.csv` once audited.*

### Recommendation

**Approve removal.** It changes nothing numerically (the proof), removes one sampled dimension that
the target never read, and supplies a clean diagnostic coordinate for validation. Wiring `f_metab`
into allocation is a *different* biological hypothesis — the static-partition model that `8c0914c`
built and `922e13d` superseded — and would need its own identifier, justification and approval; it
is not prepared here and nothing here prejudges it.

**What turning it on would change:** log L and evidence unchanged at every audited point (⏳ the
proof's maximum difference); fifteen sampled coordinates instead of sixteen; a diagnostic
coordinate available. Nothing else.

---

## 2. Infeasibility — ONE decision: which observation model, or none, from the measurement process

### The measurement facts (DECISIONS D3)

| fact | value | provenance |
|---|---|---|
| observable | `R_O2_mg_cell_min`, mg O₂ cell⁻¹ min⁻¹, replicate mean per T | README; `load_respirometry` |
| model → observable | `o2_conv = 2.8e-13 · 32.0 / 60`, × fitted `resp_scale` | `calibration_multi.py:397` |
| `s` | the **replicate SD** at each T; 12 T × 5 replicates, an SD at every one, so the 30 % floor never fires | `derived_R2A_LB_current.csv`, OTU 1 |
| `y/s` range | **2.6 (35 °C) – 17.6 (20 °C)** — the spec's "5 SE" was illustrative | same |
| detection limit | **none documented** anywhere in the record | README, tables, P3 gate |
| any `y ≤ 0` or NaN | **no**; min 1.61e-12 | same |
| can O₂ be zero when growth is? | **the data say no**: three 50 °C series with `r = 1e-6` (deliberate "no measurable growth, KEPT") respire at 2.36e-12, 2.36e-12, 1.97e-12 | README boundary fix; table |

### The classification, by solver status ⏳

At D44's 58 evaluations: **696 solves — 638 `optimal`, 58 `infeasible`, every one at 15 °C; no
timeouts, no numeric failures**. *The retry-ladder confirmation (three rungs) and the counts for the
stratum states, the 800 red2/6800 points and P12's endpoints: from `task2_classify.csv`.* A point
whose solve fails all three rungs for a non-infeasible reason is **UNRESOLVED**, and every
candidate's contribution there is **undefined pending resolution** — not a number.

### The candidates, each with its exact per-observation contribution

| candidate | contribution for a missing prediction at (T) | derivation | verdict on derivability |
|---|---|---|---|
| **OMISSION** (current) | **0** — the term is skipped (`keep = isfinite(o2) & (o2 > 0)`) | the code | what exists; a positive measurement **escapes scoring** |
| **NORMAL, r = 0, original scale** | `−½[(y/s)² + log(2π s²)]`, `s` = the replicate SD | the spec's form with the *measured* `s` | derivable — **but `r = 0` is not justified for O₂ by the data** (non-growing series respire); tabulated with that caveat on every row |
| **LOG-SCALE (the existing term's own scale)** | `log 0 = −∞` | the existing term | **undefined**: the current term cannot score a zero prediction on its own scale, and a lognormal ε is a new choice the spec forbids inventing |
| **CENSORED** | needs a detection limit | none exists in the record | **not derivable** |

### The datum-by-datum table ⏳

`task2_datum_table.csv` / `task2_datum_totals.csv`: at D44's baseline, the six saved stratum states,
the four feasible-non-growing endpoints and two growing ones — measured value, `s`, detection
status, solver classification, prediction, old contribution, each candidate's contribution —
**reconciled to the code's total log L at every point**, and the count of positive measurements
that escape scoring under the omission versus each candidate.

### What is put to the PI

The choice is between (A) accepting that a missing respiration prediction is a **model
statement** — "no feasible flux distribution" — that must be scored, and doing so with the measured
`s` on the original scale while recognising the data do not support `r = 0`; or (B) recognising
that the *model* cannot supply a respiration prediction it should be able to (a non-growing cell
respires), which makes the missing value a **model deficiency** to fix in the model, not a
likelihood term to invent. T1's tables give the arithmetic for (A); they cannot make (B) into a
number. **No candidate is chosen here.** No living fraction, evidence value or posterior informed
any of it.

---

## 3. Curvature — ONE decision per defect: approve correction / retain as is ⏳

Per axis (dTopt, topt_scale, dCp_scale, tm_scale, kcat_scale, sigma, clearance_mult): the
decomposition of D44's curvature difference by observation and by mechanism; whether it coincides
with a binding-set change, a physiological switch (an enzyme crossing its effective Topt or its
shifted Tm), or the **registered candidate** — the hard clip `np.clip(rk·fN, 1e-6, 1e6)` in
`_costs_unfolding` (D1); the same at the five registered diverse points; the refinement series.
Classification SUPPORTED BY PHYSIOLOGY / IMPLEMENTATION DEFECT / UNDETERMINED, with evidence.
*From `task3_trace.json`.* Any defect is described with its proposed correction and **not
applied**.

---

## 4. The validation protocol — for signature

`docs/VALIDATION_PROTOCOL_DRAFT.md`: the six required checks, each with an exact statistic, a
DRAFT threshold, its calibration source in P17's DECISIONS and where that source stops applying;
reserved seeds 17901–17905; what is deliberately not a threshold. Unsigned, it authorises nothing.

---

## 5. What launches after approval, and what it costs

Once 1, 2 and any curvature correction are decided and the protocol signed: (i) the revised
target as core options, default OFF, gated 79/79 and 60/60; (ii) the invariant and the datum table
re-verified under the approved options; (iii) the protocol's **five** runs on seeds 17901–17905.

Cost from P16's measured rates — nlive 800, `rslice`, 15 free coordinates: **9.585 h and 7.966 h**
per run (221,781 and 197,844 evaluations at 6.4–6.9 evaluations s⁻¹ on 16 processes). Five
sequential runs: **≈ 40–48 h wall**, plus the audit scripts (minutes). If the approved observation
model scores every temperature, the per-evaluation cost is unchanged (the solves already happen);
if a correction alters the enzyme cost, the per-evaluation cost must be re-measured before the
runs are costed.
