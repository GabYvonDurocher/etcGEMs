# Y1 PART C — the T_opt / CT_max regime test, in the published model with the published code

**The asymmetry reproduces, independently.** In Li *et al.*'s ecYeast7, run through their own
`etcpy`, changing which constraint binds moves T_opt by **10.1 °C** and moves CT_max by **0.8 °C**.

This is the generalisation the prompt asked for: the claim was established in this project's own
codebase on four organisms, and here it is in someone else's codebase on a fifth.

Script: `task_c_regime_test.py`; every point in `task_c_curves.csv`; summary in
`task_c_summary.csv`. Growth at each temperature is `etc.simulate_growth` — their function, their
model, their `data/model_enzyme_params.csv` (the prior parameters, since the posterior samples were
not downloaded). Nothing is re-implemented.

---

## 1. The two levers, both theirs

**σ, the enzyme saturation factor.** `etc.set_sigma` sets the protein-pool upper bound to
`0.17866·σ`; their calibrated value is 0.5. This scales the enzyme budget **without changing which
constraint binds** — the model is protein-limited before and after.

**The glucose cap**, the upper bound on `r_1714_REV`. Unbounded in the deposited aerobic model,
which is what makes it Crabtree-positive and protein-limited. Capping it **substitutes a
substrate-uptake limit for the enzyme limit** — it changes the binding constraint, which is what
the claim is actually about.

## 2. Results

| setting | µ_max (h⁻¹) | **T_opt (°C)** | 99 % plateau width | **CT_max (1 % rel, °C)** | µ = 0 at (°C) |
|---|---|---|---|---|---|
| σ = 0.5 (their value) | 0.3853 | **31.57** | 2.5 | **46.64** | 50.0 |
| σ = 0.4 | 0.3043 | 31.12 | 2.0 | 46.59 | 49.5 |
| σ = 0.3 | 0.2243 | 30.92 | 1.5 | 46.50 | 49.5 |
| σ = 0.2 | 0.1453 | 30.41 | 1.5 | 46.39 | 48.5 |
| σ = 0.1 | 0.0679 | 29.53 | 1.0 | 44.66 | 45.0 |
| glucose ≤ 10 | 0.3362 | 31.04 | 1.5 | 46.71 | 50.0 |
| glucose ≤ 4 | 0.2865 | 31.10 | 1.5 | 46.57 | 48.0 |
| glucose ≤ 2 | 0.1969 | **26.08** | 3.5 | 45.91 | 46.0 |
| glucose ≤ 1 | 0.0968 | **21.00** | **7.0** | 45.90 | 46.0 |

**Scaling capacity without changing the regime (σ).** µ_max falls 5.7-fold. T_opt moves 2.04 °C
and CT_max 1.97 °C — and both of those numbers are carried by the single extreme setting σ = 0.1,
where the model is near collapse. Over σ = 0.5 → 0.2, a 2.7-fold cut, **T_opt moves 1.16 °C and
CT_max moves 0.25 °C.**

**Changing the regime (glucose cap).** µ_max falls 3.5-fold — *less* than the σ sweep — but
**T_opt moves 10.09 °C while CT_max moves 0.81 °C.** A twelve-fold asymmetry, under a smaller
change in growth rate.

## 3. What actually happens to the curve, and the caveat that has to come with T_opt

The substrate cap does not slide the optimum; it **flattens the top of the curve**. The width of
the region within 1 % of the maximum goes 2.5 °C (σ = 0.5) → 3.5 °C (glucose ≤ 2) → **7.0 °C**
(glucose ≤ 1). At the tightest cap the curve reads 0.0931 at 20 °C, 0.0968 at 22 °C, 0.0965 at
26 °C: the maximum is barely a maximum.

**So "T_opt = 21.0 °C" at that setting is the argmax of a near-tie and must be quoted as one** —
this project's own rule, in `docs/QUOTING_DESCRIPTORS.md`, written for exactly this situation. The
finding is not "T_opt moves to 21 °C"; it is that **under a substrate-limited regime the optimum
stops being sharply defined at all**, while the upper thermal limit does not move.

That is a stronger statement of the same asymmetry, not a weaker one. T_opt is a property of which
constraint binds — take the enzyme limit away and the thermal shape of the optimum goes with it.
CT_max is a property of the thermal parameters, and it sits at 45.9–46.7 °C through every one of
these settings.

## 4. What this does not show

It is one organism, one model, one temperature sweep, and the parameters are their **prior**, not
their calibrated posterior — the posterior samples are on Zenodo and were not downloaded (Y1 needs
no posterior; see `SOURCE.md`). Whether the asymmetry survives at the posterior is untested
and would need `results.tar.gz`. It is a cheap follow-up and is recorded as such in
`docs/OPEN_ITEMS.md`.

The σ lever is also a weaker test than it looks: scaling a budget is not a regime change, and the
result reflects that — it moves T_opt about as little as it moves CT_max. The informative lever is
the one that changes what binds.
