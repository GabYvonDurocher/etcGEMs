# K6 TASK 3 — the verdict

**It partly survives. The sign was a comparator artefact; a magnitude gap is real; and K5's
explanation for it is wrong in direction.**

Reproduce the maintenance scan with
`CANDIDAS_ROOT=... python3 reports/K6_like_for_like/task3_maintenance_test.py` (exit 0). Table:
`task3_maintenance_scan.csv`.

---

## 1. The sign: a comparator artefact

K5 reported E_resp − E_growth as −0.33 model against **+0.33 measured**, "the wrong sign in all
four species". The measured +0.33 is a straight Arrhenius line fitted through a growth curve
that turns over. The manuscript's own value for the same organisms, from a Sharpe-Schoolfield
fit in which the collapse is modelled, is **−0.383 [−0.56, −0.21]**.

Under both valid comparators the model's sign agrees with measurement in **all four species**.
That part of K5's result does not stand.

## 2. The magnitude: real, and about 2.5-fold

| species | model (repaired) | measured [95 % CI] | ratio |
|---|---|---|---|
| *C. auris* (clade I) | −0.969 | −0.383 [−0.56, −0.21] | 2.5× |
| *C. haemulonii* | −1.388 | −0.363 [−0.57, −0.15] | 3.8× |
| *C. duobushaemulonii* | −0.757 | −0.149 [−0.36, +0.06] | 5.1× |
| *C. parapsilosis* | −1.018 | −0.464 [−0.68, −0.27] | 2.2× |

Outside the credible interval in all four. **This is not rounded into either verdict**: the
model gets the direction of the growth-respiration decoupling right and its size wrong by a
factor of two to five.

## 3. K5 said this points at the maintenance layer. It does not

The claim was cheap to test, so it was tested rather than repeated. Scaling `ngam_base_scale`,
with everything fitted exactly as in TASK 2:

| NGAM × | *C. auris* E_growth | E_resp | difference | peak µ |
|---|---|---|---|---|
| 0 | 1.218 | **0.474** | **−0.744** | 0.0904 |
| 1 (as configured) | 1.200 | 0.231 | −0.969 | 0.0683 |
| 2 | 1.176 | 0.226 | −0.950 | 0.0477 |
| 5 | −3.115 | 0.430 | +3.544 | 0.0028 |
| 10 | — | — | — | **0.0000** |

**More maintenance moves the model away from measurement, not toward it**, and the model is
dead at ten times the anchored value before the quantity has moved usefully. The same holds in
all four species.

**Turning maintenance off moves it toward measurement**, and does so by fixing the respiration
term almost exactly: *C. auris*' model E_resp goes from 0.231 to **0.474** against a measured
**0.518**. So the maintenance layer is not the missing mechanism; as configured it is
*suppressing* the respiration activation energy.

## 4. What the residual gap is actually in

With NGAM off, decomposing *C. auris*' remaining difference:

| | model | measured | gap |
|---|---|---|---|
| E_resp | 0.474 | 0.518 | −0.04 |
| E_growth | 1.218 | 0.901 | **+0.32** |
| difference | −0.744 | −0.383 | −0.36 |

**About 88 % of what is left is the model's growth rising too steeply**, not its respiration
rising too slowly. That is a statement about the enzyme kinetic envelope — the shared dCp prior
and the MMRT curvature that set the rising limb — and not about the ETC or maintenance, which
were the two layers K5 pointed at.

It is also consistent with a fact already on record and not previously connected to this: the
same models over-predict the upper thermal limit by 9.6–15.8 °C (K4, §4). A curve that rises too
steeply and turns over too late is one description of both.

## 5. What was and was not changed

Nothing was tuned. The maintenance scan reports how far that layer can move the quantity and at
what cost; no value was adopted, and `candida_B5_respire` is unchanged.

K5's report is **corrected with a dated note, not rewritten** — its history stands as written,
with the correction attached at the point where the claim is made.
