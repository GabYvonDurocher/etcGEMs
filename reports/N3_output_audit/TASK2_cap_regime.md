# N3 TASK 2 — the cap-regime hypothesis, tested

**The hypothesis, as posed.** Before `a416fd1` the translation cap was binding, so the old
T_opt of 37 °C was a cap-limited plateau edge — the artefact N1's flatness guard found in
Candida rung B4 — and the report's φ_envelope = 0.999 for T_opt holds only within the
cap-free regime.

**Verdict: the hypothesis is wrong as stated, and what is actually happening is sharper.**
The old T_opt was not a plateau edge — the plateau was 1.0 °C wide. And the cap binds at
T_opt *today* as well, so "the cap binds" cannot be what separates then from now. But the
optimum of the strain's nominal curve **is** set by the cap in both states, and the
φ_envelope = 0.999 attribution is measured at a *third* operating point where the cap never
binds at all.

---

## What was measured

Three states, each probed the same way: build the provider, sweep the temperature grid,
record growth and the slack on the biosynthesis/translation cap (`proteome_biosynthesis`)
and on the metabolic pool row.

| state | how it was obtained |
|---|---|
| **PRE** | scratch worktree at `27cafef^` (= `01afdf6`), the state N2's bisection used, `f_metab` 0.285 / `f_maint` 0.374 |
| **CURRENT** | this tree, `f_metab` 0.483 / `f_maint` 0.326 — reproduces the committed `outputs/tpc` exactly (`rmax` 0.5429018962625917) |
| **TUNED** | the operating point the report's decomposition actually uses: `calibration_multi._build_pm_rich` (rich BHI, growth law ON, `_alloc_from_data = None`) with the tuned medians recorded in the committed `decompose_summary.json`, on the decomposition's own 48-point grid |

### Plateau width (N1's metric, `sectors.plateau_width`)

| state | T_opt | r_max (/h) | plateau within 1 % | within 0.1 % | within 0.01 % |
|---|---|---|---|---|---|
| PRE | 37.0 °C | 0.3407 | 36.0–37.0, **1.0 °C** | — | **0.0 °C** |
| CURRENT | 31.0 °C | 0.5429 | 30.0–32.0, **2.0 °C** | — | **0.0 °C** |
| TUNED (committed baseline curve) | 39.0 °C | 2.1609 | 38.0–40.0, **2.0 °C** | **0.0 °C** | 0.0 °C |
| TUNED (recomputed today) | 39.0 °C | 2.1558 | 38.0–40.0, **2.0 °C** | **0.0 °C** | 0.0 °C |

No state has a flat top. For scale, N1 measured 14.0 °C for eciML1515 with
`allocation_from_data` switched off, and 12.5–20.5 °C for the Candida B4 rung.

### Does the translation cap bind at T_opt?

| state | at T_opt | over which temperatures | what binds instead |
|---|---|---|---|
| PRE | **YES** (slack 0) | cap binds 30–45 °C, 16 of 53 live points | pool has slack 0.012 at T_opt |
| CURRENT | **YES** (slack 0) | cap binds 31–44 °C, 14 of 56 live points | pool has slack 0.0056 at T_opt |
| TUNED | **NO** | **cap binds at 0 of 48 temperatures** | the metabolic **pool** binds, 27–44 °C, including T_opt |

---

## What actually sets T_opt in each state

**In both nominal states the top of the curve is allocation-determined, not
envelope-determined.** Over the whole range where the cap binds, growth equals
`cap_ub / translation_coeff` to five or more digits — the curve is the allocation ceiling
divided by a constant:

* **PRE.** The cap starts binding at 30 °C. The measured f_bio(T) ceiling *rises* to a
  maximum at 37 °C (`cap_ub` 0.080921) and falls after. So **T_opt = 37 °C is the argmax of
  the measured allocation ceiling** — the envelope sets only where the cap starts to bind.
* **CURRENT.** The cap starts binding at 31 °C, and from there the ceiling *declines*
  monotonically (`cap_ub` 0.042712 → 0.041284). Below 31 °C the pool-and-envelope-limited
  branch is still rising steeply (0.3252 at 23 °C → 0.5410 at 30 °C). So **T_opt = 31 °C is
  the crossover**: the last temperature before the falling cap ceiling takes over.

The 7 °C shift is therefore **a change in which feature of the allocation curve sets the
optimum** — from the peak of the ceiling to the point where the ceiling starts to bite. That
is a regime change, and it is invisible to a local ±20 % decomposition around a single
operating point, exactly as the hypothesis suspected. It is *not* a plateau artefact.

### A second artefact, not previously recorded

The measured proteome (`proteomics/tem_proteomic.csv`) has **Glucose measurements at 25, 30
and 37 °C only** (LB has 16/25/30/37/43). Outside that range the allocation is held
constant, so the cap becomes temperature-independent there. The consequence is visible in the
current nominal curve: growth is **exactly constant at 0.524757 /h from 37 °C to 44 °C** — an
8 °C dead-flat shoulder at 96.7 % of r_max, produced entirely by the data table running out.
PRE shows the same thing at 43–45 °C (0.269110 /h, 79.0 % of r_max).

`plateau_width` does not see it (it sits below the 1 % band) and N1's `sector_cap_risk()`
does not fire (it asks whether `allocation_from_data` is *absent*, and here it is present).
**The guard's condition is neither necessary nor sufficient**: allocation data can be present
and the cap still temperature-independent over part of the range (here), and allocation data
can be absent and the cap never bind at all (the tuned point). The direct test is the one run
above — does the cap actually bind, and is its ceiling flat where it does. Recorded, not
fixed: changing the guard is a modelling decision for a human, as N1 already argued.

---

## What this means for φ_envelope = 0.999

The report's decomposition is **not** run at either nominal point. `_build_pm_rich` sets
`pm.ec._alloc_from_data = None` — its own docstring says "static rich sector allocation … with
the growth law ON the biosynthesis cap relaxes and the coupled metabolic sector binds". The
measurement above confirms it: at that point the cap has slack at **every one of 48
temperatures**, and the metabolic pool binds instead. So the φ_envelope = 0.999 attribution
for T_opt is already inside the cap-free regime the hypothesis was worried about; it is not a
cap artefact.

It is still conditional, and the report does not say so. The same strain at its own nominal
Glucose-minimal operating point has a cap-bound optimum, where the attribution measured at
the tuned point would not transfer. One caveat sentence has been added to
`reports/ecoli_tpc/report.qmd` saying exactly that. Nothing in the decomposition has been
restated or recomputed.

---

## Incidental, and material to TASK 3

Reconstructing the tuned point reproduced **`control_tuned`'s** committed nominal r_max to
seven decimal places (2.1557849) and **not** `decompose_tuned` / `elasticity_tuned`
(2.1608622, −0.235 % away). That is the O2-sink closure `8085036`, whose own commit message
predicts "~−0.3 % growth". It confirms the TASK 1 classification from the other direction:
the control analysis is on the corrected model and the decomposition and elasticity beside it
in the report are not. Carried into TASK 3.

*(Method note: an earlier version of this probe omitted `kappa_scale` / `sigma_sat` from
`set_allocation` and reported r_max 1.114 — `sigma_sat`/`sigma_nom` = 0.8669/0.45 rescales
both sector caps by 1.93. The probe was corrected before any conclusion was drawn from it.)*
