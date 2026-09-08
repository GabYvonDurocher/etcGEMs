# K7 TASK 1 — which growth convention Figure 4's requirement uses, and how much it matters

**The two conventions agree to 0.07 °C, and the trace shows why they must.** The worry is
retired. Calibration and counterfactual read the **same** file, so the model is not fitted to
one curve and falsified against another.

Reproduce with `CANDIDAS_ROOT=... python3 reports/K7_envelope/task1_convention.py` (exit 0).
Tables: `task1_conventions.csv`, `task1_auris_curves.csv`.

---

## The trace, followed to the file on disk

| step | code | what it reads |
|---|---|---|
| calibration target | `transfer.run` line 324, `load_measured_tpc(cal, ...)` | `strains/cauris_iRV973/thermal/measured_tpc.csv` |
| growth scale | line 345, `_scale(pred_cal, measured["mu"], "peak_match")` | **only `measured.mu.max()`** |
| counterfactual | `required_separation(pm, pert, scale, "dTm", T_fail=40, threshold=0.05)` | **nothing** — it takes `scale` as a scalar |
| the floor | inside `required_separation`, `mu_at(T,d) = model_growth × scale` vs `threshold` | applied to a **scaled model prediction** |

`strain.yaml`'s `measured:` block names `gem/17_build_measured_tpc.py` as the provenance, which
is the **zeros** convention — a dead well is an observed zero.

**`required_separation` makes zero calls to `load_measured_tpc`.** The predicted strain's own
measured curve never enters the counterfactual. That is the whole answer: the 40 °C value of
*C. haemulonii*, which is 0.000 under one convention and 0.66 under the other, is not an input.

The only measured quantity that reaches the counterfactual is the **peak of the *C. auris*
curve**, and *C. auris* peaks at 36 °C where it is fully alive either way.

**Calibration and counterfactual read the same file** (both via line 324). From K2 rung B2 on
`globals: []`, so nothing is fitted at all and only the scale survives.

## The two *C. auris* curves

| T (°C) | zeros convention | survivors convention |
|---|---|---|
| 22 | 0.2607 | 0.2875 |
| 30 | 0.6482 | 0.6252 |
| 34 | 0.7761 | **0.8479** |
| **36** | **0.7988** | 0.7950 |
| 40 | 0.6639 | 0.6432 |
| 44 | 0.2721 | 0.3604 |

Peaks: **0.7988 at 36 °C** against **0.8479 at 34 °C**, a ratio of **1.061**. They diverge only
where wells die, and *C. auris* barely dies before 44 °C — which is exactly why the choice does
not propagate.

## The requirement under both

| model state | zeros convention | survivors convention | difference |
|---|---|---|---|
| B3, before the K5 repair | **13.64 °C** | 13.71 °C | 0.07 °C |
| B5, repaired | **13.57 °C** | 13.57 °C | **0.00 °C** |

Beside the figures already in circulation:

| | required ΔTm |
|---|---|
| the standalone (K1 / K2 rung B0) | 32.5 °C |
| K2, the core's unfolding form | 13.8 °C |
| K6 / K7, repaired, zeros convention | **13.57 °C** |
| K7, repaired, survivors convention | **13.57 °C** |

A 6.1 % difference in the growth scale moves a bisection on a steep exponential by at most
0.07 °C. **The number in circulation is safe from this particular objection.**

## Which convention is appropriate, and why

**The zeros convention**, for a detection-threshold counterfactual, and not merely because it is
what the repository already uses.

The question asked is whether a strain falls **below a detection floor** — a statement about the
population in the well. A survivors-only curve conditions on being alive, so it cannot represent
death: under it "below detection" is unreachable by construction, and the counterfactual would
be asking a question its own data had defined away. The zeros convention is the only one of the
two that can express the phenomenon under test.

That the two agree here is a separate and lucky fact, and it holds only because *C. auris* — the
one strain whose measured curve reaches the counterfactual — is alive at its own optimum.

**No default is changed.** The recommendation is recorded; `strain.yaml` is untouched.
