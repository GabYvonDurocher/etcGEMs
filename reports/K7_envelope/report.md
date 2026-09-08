# K7 — the growth convention behind Figure 4, and whether the model's envelope is too steep

_2026-09-08. Branched from `main` at **3147261**, the K6 merge. **P4 had not landed**, so
`strains/eciML1515/` and `reports/ecoli_*` are never written._

Two jobs. The first retires a worry about a number already in circulation. The second measures
the sharpest open target the project has and identifies most of its cause.

**Four results.**

1. **Figure 4's requirement is convention-independent**, and the trace shows why it must be:
   the counterfactual never reads the predicted strain's measured curve at all.
2. **The model's growth envelope is too steep in every species**, by 1.24 to 2.29×, and the
   error is structural — it barely moves between configurations, unlike the respiration error.
3. **The ΔCp prior is most of it.** A value inside the literature range reconciles the
   activation energy *and* improves the fit to the measured growth curve.
4. **The same parameter cannot close the CT_max over-prediction**, and pushes it slightly the
   wrong way. The two failures are not one failure with one cause.

Reproduce with:

```bash
CANDIDAS_ROOT=... python3 reports/K7_envelope/task1_convention.py
CANDIDAS_ROOT=... python3 reports/K7_envelope/task2_envelope.py
CANDIDAS_ROOT=... python3 reports/K7_envelope/task3_dcp_sweep.py
```

Detail in `task1_convention.md` and `task3_dcp.md`; decisions in `DECISIONS.md`.

---

## 1. Which growth convention Figure 4's requirement uses

**Traced, not inferred.** `transfer.required_separation` takes the growth scale as a **scalar**
and makes **zero** calls to `load_measured_tpc`. The predicted strain's own measured curve never
enters the counterfactual, so *C. haemulonii*'s 40 °C value — 0.000 h⁻¹ under one convention and
0.66 under the other — is not an input to it.

The only measured quantity that reaches it is the **peak of the *C. auris* curve**, through the
`peak_match` scale, and *C. auris* peaks at 36 °C where it is fully alive either way. Peaks:
**0.7988** (zeros) against **0.8479** (survivors), a ratio of 1.061.

**Calibration and counterfactual read the same file.** The model is not fitted to one curve and
falsified against another.

| model state | zeros convention | survivors convention | difference |
|---|---|---|---|
| B3, before the K5 repair | 13.64 °C | 13.71 °C | 0.07 °C |
| B5, repaired | **13.57 °C** | **13.57 °C** | **0.00 °C** |

Beside the standalone's 32.5 °C and K2's 13.8 °C, **the number in circulation is safe from this
objection**. Recommended convention for a detection-threshold counterfactual: the **zeros**
convention, because a survivors-only curve conditions on being alive and cannot represent death
— under it "below detection" is unreachable by construction. **No default changed.**

## 2. Is the growth envelope too steep? Yes, in every species

Same window (the organism's rising limb, cut at its Bayesian optimum) and same functional form
on both sides.

| species | model E_growth | measured (Bayes) | measured (rising-limb OLS) | steepness |
|---|---|---|---|---|
| *C. auris* (clade I) | 1.200 | 0.901 | 0.730 | **1.33×** |
| *C. haemulonii* | 1.759 | 0.797 | 0.623 | **2.21×** |
| *C. duobushaemulonii* | 0.934 | 0.622 | 0.636 | **1.50×** |
| *C. parapsilosis* | 1.023 | 0.828 | 0.702 | **1.24×** |

**The decisive observation is that it barely moves between configurations**, while the
respiration error moves a great deal:

| configuration | growth steepness (median) | respiration ratio (median) |
|---|---|---|
| B3, before the K5 repair | 1.55× | 1.03× |
| B5, repaired | **1.42×** | 0.41× |
| B5, NGAM(T) off | 1.45× | 0.67× |

So the growth error is **structural and stable** — present before the repair, after it, and with
maintenance removed — whereas the respiration error is a property of the configuration. That
confirms K6's attribution by direct measurement rather than by subtraction, and it locates the
problem in the kinetic envelope.

## 3. ΔCp is most of the steepness, at a defensible value

Swept −1 to −16 kJ/mol/K against a literature range of **−2 to −6** taken from this
repository's own robustness analysis. Moved through `Perturbation.dCp_scale`; no default
touched.

| ΔCp | *C. auris* steepness | *C. auris* fit R² | CT_max gap |
|---|---|---|---|
| −2 *(lit)* | 0.60 | 0.388 | +9.6 |
| **−3 *(lit)*** | **0.93** | **0.575** | +9.4 |
| −4 *(configured)* | 1.33 | 0.518 | +9.0 |
| −6 *(lit)* | 2.31 | −0.072 | +7.9 |
| −16 | 4.89 | −4.173 | **+2.4** |

Three of four species reconcile at **−3.0**, inside the range; only *C. haemulonii* needs −1.0,
outside it, and it is the worst-fitting species by every measure. **The reconciling value also
maximises the fit**, which it need not have done. So the configured prior is not the
best-supported value for these organisms, and a better one is inside the literature range.

## 4. But it cannot close the ceiling, and pushes it the wrong way

The CT_max over-prediction falls **monotonically** as ΔCp becomes more negative; the steepness
rises **monotonically** with it. They are strictly opposed. For *C. auris*, steepness and fit are
both best at **−3.0**, while the ceiling gap is smallest at **−16.0**, four times outside the
range, where R² is −4.17 and the envelope is 4.9× too steep. **Within the defensible range ΔCp
closes at most about a fifth of the ceiling error.**

**The too-steep rising limb and the too-high ceiling are therefore not one failure with one
cause**, and this rules out the most obvious candidate for making them one.

## What each licenses

* **Licensed:** the 13.57 °C requirement is not an artefact of the growth convention; the model's
  growth envelope is too steep by 1.24–2.29× and this is a property of the kinetic envelope
  rather than of the repair or the maintenance layer; ΔCp accounts for most of that steepness
  and a value inside the literature range reconciles it while improving the fit; ΔCp does not
  explain the CT_max over-prediction.
* **Not licensed:** adopting −3.0. It is fitted here to one quantity on four species, it would
  move every committed number for these strains, and *C. haemulonii* disagrees with it. It is a
  diagnosis, recorded with a trigger in `docs/OPEN_ITEMS.md`.
* **Not licensed:** any claim that the ceiling problem is solved or localised. K7 rules one
  candidate out and names no other.

## Verification

| check | result |
|---|---|
| K1 gate, `$CANDIDAS_ROOT` unset | **79/79 PASS, exit 0** |
| `stamp_reports.py --check` | exit 0 |
| all three K7 scripts re-run | exit 0, tables regenerate |
| defaults changed | **none** — no file under `strains/` or `configs/` modified |
| `strains/eciML1515/`, `reports/ecoli_*` | untouched; P4 had not landed |
