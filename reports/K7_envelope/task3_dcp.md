# K7 TASK 3 — the ΔCp prior: how much of the steepness is it?

**Most of it, at a value inside the literature range — but the same parameter cannot close the
ceiling over-prediction, and pushes it slightly the wrong way.**

Reproduce with `CANDIDAS_ROOT=... python3 reports/K7_envelope/task3_dcp_sweep.py` (exit 0).
Table: `task3_dcp_sweep.csv`.

---

## The range and how it was moved

`provider.dcp_prior_kJ = -4.0` kJ/mol/K, cited to Hobbs et al. 2013 in five strain configs. The
range this repository itself uses is in `strains/syn6803/run_p4_robustness.py`: **−2 to −6**,
with −4.0 central. The sweep goes **−1 to −16**, wider on both sides, so the reconciling value
is found and then judged rather than constrained.

dCp is moved through `Perturbation.dCp_scale`, which multiplies the transition-state dCp at
solve time. **No default is changed anywhere.**

## Steepness — model E_growth divided by the measured Bayesian value

| ΔCp (kJ/mol/K) | *C. auris* | *C. haemulonii* | *C. duobushaemulonii* | *C. parapsilosis* |
|---|---|---|---|---|
| −1 | 0.33 | 0.80 | 0.12 | 0.24 |
| −2 *(lit)* | 0.60 | 1.24 | 0.42 | 0.52 |
| **−3 *(lit)*** | **0.93** | 1.71 | **0.86** | **0.82** |
| −4 *(lit, configured)* | 1.33 | 2.21 | 1.50 | 1.24 |
| −5 *(lit)* | 1.81 | 2.71 | 2.33 | 1.80 |
| −6 *(lit)* | 2.31 | 3.22 | 3.30 | 2.47 |
| −12 | 3.66 | 6.28 | 4.93 | 4.19 |

**ΔCp is most of the steepness.** Moving from −4 to −3, a step well inside the literature range,
takes *C. auris* from 1.33× to 0.93× — from a third too steep to slightly too shallow. Three of
the four species reconcile at **−3.0**, and that value is **inside** the range. Only
*C. haemulonii* needs −1.0, outside it, and it is the worst-fitting species by every measure.

**And it improves the fit**, which a reconciling parameter need not have done:

| ΔCp | *C. auris* fit R² |
|---|---|
| −2 | 0.388 |
| **−3** | **0.575** |
| −4 (configured) | 0.518 |
| −5 | 0.283 |
| −6 | −0.072 |

The value that reconciles the activation energy is also the value that maximises the fit to the
measured growth curve. That is a genuine, if narrow, result: **the configured prior is not the
best-supported value for these organisms, and a better one is inside the literature range.**

## The ceiling: the same parameter pushes it the wrong way

CT_max minus the observed limit (°C):

| ΔCp | *C. auris* | *C. haemulonii* | *C. duobushaemulonii* | *C. parapsilosis* |
|---|---|---|---|---|
| −2 *(lit)* | +9.6 | +14.9 | +14.9 | +15.6 |
| **−3 *(lit)*** | **+9.4** | +14.4 | +14.3 | +15.4 |
| −4 *(configured)* | +9.0 | +13.8 | +13.7 | +15.3 |
| −6 *(lit)* | +7.9 | +12.4 | +11.9 | +14.8 |
| −12 | +3.9 | +7.7 | +7.7 | +11.2 |
| −16 | **+2.4** | +5.9 | +6.3 | +9.4 |

**The two targets are strictly opposed.** The ceiling gap falls monotonically as ΔCp becomes
more negative; the steepness rises monotonically with it. For *C. auris*:

| target | best ΔCp | |
|---|---|---|
| steepness → 1.0 | **−3.0** | inside the range; R² 0.575 |
| fit R² maximised | **−3.0** | the same value |
| CT_max gap minimised | **−16.0** | four times outside the range; R² **−4.17**, envelope 4.9× too steep |

**Within the defensible range ΔCp closes at most about a fifth of the ceiling error** — −2 to −6
moves *C. auris*' gap only from +9.6 to +7.9, against a 9 °C error. Closing the ceiling with ΔCp
needs values that destroy the fit and the rising limb.

## What this licenses

* **ΔCp is most of the growth-envelope steepness**, and the steepness can be reconciled with
  measurement by a value inside the literature range that also improves the fit. That is the
  answer to TASK 2's question about cause.
* **ΔCp is not the explanation for the CT_max over-prediction**, and the direction that fixes
  the rising limb makes the ceiling marginally worse. The two failures identified in this
  project — a too-steep rising limb and a too-high ceiling — are **not one failure with one
  cause**, and this rules out the most obvious candidate for making them one.
* **Nothing is changed.** −3.0 is a diagnosis, not a decision: it is fitted here to a single
  quantity on four species, and adopting it would move every committed number for these strains.
  Recorded in `docs/OPEN_ITEMS.md` with a trigger.
