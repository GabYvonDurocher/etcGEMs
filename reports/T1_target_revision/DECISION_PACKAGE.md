# T1 decision package — for the PI

_Prepared 2026-09-13 by T1. Three decisions and a protocol for signature. **Nothing below has been
acted on: no option is on, no candidate is implemented, no correction is applied, no fit has run.**
Sections 2 and 3 are filled from the audited CSVs and the trace JSON (D8, D10), never from
memory._

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

### The invariant proof — PROVEN

Old target versus removal-only target at **every one of the 870 registered audit points** (58 D44
stencils, 800 red2/6800 live points, 12 P12 endpoints), plus the old target with `f_metab` swapped
to 0.15 / 0.28 / 0.45 at the same active point. Registered tolerance 1e-6. **Maximum difference
across the five evaluations, over all 870 points: 2.02e-08. 0 violations, 0 unresolved.**
Recomputed from the CSV independently of the script's summary (sha256 `1377ab9a…`). D44 and
red2/6800 reproduce their saved log L to 3.6e-10 and 7.4e-09; P12's twelve differ from their saved
values by exactly P13's clamp-versus-current change (DECISIONS D4) and satisfy the invariant
regardless.

### Recommendation

**Approve removal.** It changes nothing numerically (the proof), removes one sampled dimension that
the target never read, and supplies a clean diagnostic coordinate for validation. Wiring `f_metab`
into allocation is a *different* biological hypothesis — the static-partition model that `8c0914c`
built and `922e13d` superseded — and would need its own identifier, justification and approval; it
is not prepared here and nothing here prejudges it.

**What turning it on would change:** log L and evidence unchanged at every audited point (maximum
difference 2.02e-08); fifteen sampled coordinates instead of sixteen; a diagnostic
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

### The classification, by solver status

Two audited batches (`task2_classify.csv`, `task2_classify_batch2.csv`; merged
`task2_classify_all.csv`, sha256 `d1309afb…f600c8`; D6/D8): all **876** registered points
evaluated, **0 UNEVALUATED**, counts recomputed from the rung columns with **0 disagreements**,
saved solver status reproduced at **64 of 64** points that carry one.

| set | points | solves | STRUCTURAL_ZERO | UNRESOLVED | RESOLVED_ON_RETRY | where |
|---|---|---|---|---|---|---|
| D44 parent + stencils | 58 | 696 | 58 | 0 | 0 | 15 °C at every one |
| stratum states (2 stored × 3 seeds) | 6 | 72 | **72** | 0 | 0 | every temperature |
| red2/6800 validated live | 800 | 9,600 | 9,214 | 0 | 0 | **765 points at all 12 T**; 32 at 15 °C only; 1 at two; 2 at none |
| P12 endpoints | 12 | 144 | 11 | 0 | 0 | `B(b3)` 15–65 °C; eleven feasible everywhere |
| **all** | **876** | **10,512** | **9,355** | **0** | **0** | |

Every missing prediction in the audit set is Gurobi `infeasible` on the fresh model, at
tolerances 1e-12 and under dual simplex alike — **STRUCTURAL_ZERO on growth**. The UNRESOLVED
class, for which every candidate's contribution would be *undefined pending resolution*, is
**empty** here; it is retained in the tables as the category the ladder detects.

**What the 765 are.** P17's `stratum.json` counted 765 "algebraically compatible" live points at
red2's iteration 6800 and gave the stratum **81.5 %** of red2's posterior weight (53.2 % of
red1's), labelling itself *not* a solver-status classification. This is that classification: the
same **765**, each infeasible at all twelve temperatures, so growth is 0 everywhere, all twelve
positive respiration measurements escape scoring, and log L is the growth term alone — a function
of `disc_growth` only, ceiling **−18.6825** (P17's `curve_max`). The 35 living points
(peak growth 1.40–1.53 /h) have stored log L −18.77 to −16.44; the plateau's ceiling lies above
most of them. This is the solver-side statement of "the posterior is half dead". It is reported
for decision 1.30, not acted on.

### The candidates, each with its exact per-observation contribution

| candidate | contribution for a missing prediction at (T) | derivation | verdict on derivability |
|---|---|---|---|
| **OMISSION** (current) | **0** — the term is skipped (`keep = isfinite(o2) & (o2 > 0)`) | the code | what exists; a positive measurement **escapes scoring** |
| **NORMAL, r = 0, original scale** | `−½[(y/s)² + log(2π s²)]`, `s` = the replicate SD | the spec's form with the *measured* `s` | derivable — **but `r = 0` is not justified for O₂ by the data** (non-growing series respire); tabulated with that caveat on every row |
| **LOG-SCALE (the existing term's own scale)** | `log 0 = −∞` | the existing term | **undefined**: the current term cannot score a zero prediction on its own scale, and a lognormal ε is a new choice the spec forbids inventing |
| **CENSORED** | needs a detection limit | none exists in the record | **not derivable** |

### The datum-by-datum table

`task2_datum_table.csv` (156 rows, sha256 `67170142…`) / `task2_datum_totals.csv` (`de757021…`):
13 points × 12 temperatures — D44's baseline, the six stratum states, P12's four
feasible-non-growing and two growing endpoints — with, per datum, `y`, the replicate `s`, `y/s`,
detection status, solver classification, growth, model O₂, whether scored today, the growth term,
the old respiration contribution, and each candidate's. **Reconciliation:** the per-datum sum
equals the code's own `gasflux_log_likelihood` to **≤ 5e-12** at D44 and the stratum states and to
**≤ 1.65e-9** at the six P12 endpoints; three of those (A, B*, worst) exceed the 1e-9 the script
registered by at most 0.65e-9, which is reported as a miss of that tolerance, not re-registered
(the table calls `flux_tpc` once and the likelihood solves again internally; a 1e-9 difference
between two solves of the same model is within P7's measured reproducibility).

| point | log L (code) | growth | resp (old) | missing T | +ve measurements unscored (OLD) | total under NORMAL r=0 |
|---|---|---|---|---|---|---|
| D44 baseline | −17.9725 | −2.3235 | −15.6490 | 1 (15 °C) | 1 | −0.4341 |
| stratum red1:8285 (×3 seeds) | −18.6845 | −18.6845 | 0 | 12 | 12 | −304.2048 |
| stratum red2:9051 (×3 seeds) | −18.6826 | −18.6826 | 0 | 12 | 12 | −304.2029 |
| P12 A(b20) | −10.0029 | +6.2868 | −16.2896 | 0 | 0 | −10.0029 |
| P12 B*(b8) | −11.7285 | +5.3262 | −17.0548 | 0 | 0 | −11.7285 |
| P12 p81(b7) | −10.7381 | +5.4015 | −16.1396 | 0 | 0 | −10.7381 |
| P12 worst(b5) | −36.4427 | −15.7987 | −20.6439 | 0 | 0 | −36.4427 |
| P12 p38(b22) | −9.9894 | +6.3630 | −16.3524 | 0 | 0 | −9.9894 |
| P12 p50(b19) | −9.3382 | +6.8042 | −16.1424 | 0 | 0 | −9.3382 |

**Escapes.** Under the omission, **73** positive measurements escape scoring across the 13 points
(one at D44, twelve at each stratum state, none at the P12 endpoints — all six are feasible at
every temperature, including the four "feasible-non-growing" ones, which is what that name
means). Under NORMAL r = 0 every one is scored (**0** escape, all defined, because no UNRESOLVED
solve exists). The LOG-SCALE row is −∞ wherever a prediction is missing; CENSORED is not derivable.

**What the NORMAL arithmetic exposes, stated so the PI is not misled by the totals.** At D44's
15 °C the candidate contributes **+17.54**: `−½(y/s)² = −9.94` plus the normalising constant
`−½ log(2π s²) = +27.48` at `s = 4.64e-13` mg cell⁻¹ min⁻¹. The candidate is a density in `y`
on the original scale, whereas the existing term is a density in `log y`; their totals differ by
the Jacobian `Σ log y` (−24.1 to −26.9 per datum at these units) and are **not comparable as they
stand**. Within the candidate, the stratum states fall from −18.68 to **−304.20** because the
twelve `−½(y/s)²` terms (y/s from 2.6 to 17.6) sum to **−602.22** against **+316.70** of
normalising constants, plus the growth term −18.68 (from `task2_datum_table.csv`). The table
gives the arithmetic; it does not make the choice, and the choice is not to be made from these
totals without first putting both densities on one scale.

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

## 3. Curvature — ONE decision per defect: approve correction / retain as is

### The finding: **no implementation defect on any of the seven axes at D44.**

Trace only (`task3_trace.py`, 31 min + two registered corrections, D9; `task3_trace.json`
sha256 `3576b1e8…`): all 58 of P17's D44 evaluations re-evaluated fresh and reproduced to
**≤ 8.9e-10**; the per-datum growth and respiration terms reconcile to the code's total at every
evaluation; enzyme state (above effective Topt, past shifted Tm, clipped at 1e-6) and LP status
captured per temperature at every stencil; P14's refinement (h, h/2, h/4, h/8) on **both** sides
of the parent; the rule registered in D7 applied at the carrying temperature and interval
(`task3_classification.csv`, sha256 `0c8733bf…`; D10).

| axis | P17 rel. difference | carrying datum, interval | refinement (carrying side) | mechanism moving at that T | classification | decision offered |
|---|---|---|---|---|---|---|
| dTopt | 0.205 | resp@50 °C, [+0.02,+0.04], −0.0005 | SMOOTH | none | SUPPORTED (smooth, non-quadratic) | retain as is |
| topt_scale | 0.938 | **resp@27 °C**, [+0.02,+0.04], **−0.074** | AMBIGUOUS | none — O₂ at 27 °C 15.71 → 11.09 | **UNDETERMINED** (untraced vertex change) | retain as is; instrument below |
| dCp_scale | 0.300 | **resp@27 °C**, [+0.02,+0.04], **−0.065** | JUMP | none — O₂ at 27 °C 15.68 → 15.02 → 11.10 | **UNDETERMINED** (untraced vertex change) | retain as is; instrument below |
| tm_scale | 0.574 | resp@50 °C, [0,+0.02], −0.0013 | SMOOTH | none (clip moves at 50 °C on the next interval, 39 → 42, no kink) | SUPPORTED | retain as is |
| kcat_scale | 0.279 | resp@27 °C, [−0.04,−0.02], +0.0065 | SMOOTH | none | SUPPORTED | retain as is |
| sigma | 0.875 | growth@30 °C, [−0.04,−0.02], −0.020 | SMOOTH | none — growth at 30 °C reaches a ceiling (1.16823) | SUPPORTED (slope kink: a constraint binding) | retain as is |
| clearance_mult | 0.102 | resp@45 °C, [−0.04,−0.02], +0.0016 | SMOOTH | none | SUPPORTED | retain as is |

**What the two UNDETERMINED axes are.** The same event: at 27 °C, with the LP `optimal`
throughout and no traced enzyme-state change, the tie-broken O₂ drops ~30 % between +0.02 and
+0.04 SD while growth changes by 0.5 %. That is a change of the optimal vertex — the kind P9
decomposed and P10's floor reduced from tens of units to 0.07. The trace captures no basis, so D7
places it UNDETERMINED with the vertex change as the named candidate. **Proposed (not run):**
P9's basis-status capture at 27 °C across [+0.02, +0.04] on these two axes. **No correction is
proposed, because a vertex change is the model being an LP, not a defect.**

**The registered candidate, the hard clip `np.clip(rk·fN, 1e-6, 1e6)`,** moved at D44 on two
axes (topt_scale at 45 °C, tm_scale at 50 °C) and carried no curvature on either: not implicated.
At the five diverse points it appears in one cell, coincident with a melting-point crossing and an
excess of −0.0007. **Decision offered on 1.31: retain as is on all seven axes.** There is nothing
to approve for application.

**Diverse points (descriptive; refinement was registered at the parent only, so every row is
UNDETERMINED by rule).** Two corrections were made to the trace script and are recorded in D9:
the p38 and P4-MAP bases were first evaluated at their stored dTm (−4.02, −5.12) rather than the
registered dTm = 0 — re-evaluated (−9.99 → −60.31; −10.98 → −55.85), as-stored values retained;
and the refinement had stepped the plus side only — the minus side was added. At dTm = 0 neither
p38 nor P4's MAP is the point its name suggests. The stencils show: the 15 °C feasibility
boundary (status and scored mask moving, excess ±1.6) at p38 and red2_wmedian; the 27 °C-type
cold-respiration event on topt_scale/dCp_scale again at the top-weight living sample (25 °C,
−0.02); a melting-point crossing at P4-MAP's tm_scale; nothing above 0.033 at the living median.

**No value changed:** the new log L equals the old at all 261 evaluations by construction.

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
