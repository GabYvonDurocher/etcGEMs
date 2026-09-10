# Y3 TASK 4 — what the expensive route would cost, and whether it is worth taking

Reported, not run. Nothing here is implemented.

---

## 1. DLTKcat — and it has already been run on this proteome

The premise of the expensive route is "per-enzyme Topt from DLTKcat, as Li used Tome". **The
inference pass already exists in the repository**, and its output is the reason to think again.

**What DLTKcat takes and returns.** Input is one row per (reaction, enzyme, substrate,
temperature): `rxn_id, enz (UniProt), sub, bigg, mnx, Temp_C, Temp_K`, joined to a protein sequence
and a substrate SMILES. Output adds the predicted `pred_log10kcat` per row. It is a deep
kcat(sequence, substrate, temperature) predictor, not a thermal-parameter estimator — the Topt has
to be *fitted* from the predicted curve afterwards, which is what `src/etcgem/dltkcat.py`'s
`fit_mmrt` does.

**What was run for eciML1515** (`strains/eciML1515/dltkcat/`):

| | |
|---|---|
| reactions covered | **1 149** (`fits.csv`) and **2 214** (`fits_ext.csv`, the extended substrate set) |
| temperature grid | **5–55 °C in 5 °C steps, 11 points** |
| prediction rows | 12 639 (`output.csv`) |
| model applied at run time | **13 of 2 560 enzymes**, per the run log |

**Why only 13.** `fit_mmrt` marks a fit `ok` only if the curve is *peaked* — `dCp < 0` and the
argmax strictly inside the 0–80 °C grid — with r² > 0.8. Of the 1 149 fits:

* **736 rail at 80 °C** — predicted kcat rises monotonically across the whole biological range;
* **377 rail at 0 °C** — monotonically falling;
* **36 have an interior optimum**, and 30 pass the full `ok` test;
* only **169 of 1 149** even have `dCp < 0`, the curvature MMRT needs for a peak at all.

So **DLTKcat's predicted kcat(T) is essentially monotone in temperature over 5–55 °C for *E. coli*
enzymes.** It cannot supply per-enzyme Topt, because on its own predictions there is no per-enzyme
Topt to extract. That is not a bug in the pipeline here; it is what the predictor returns.

**What a fresh pass would cost, if wanted anyway.** Nothing was re-run for this screen. The
existing pass covers 1 149–2 214 reactions of the model's 2 560 enzymes, so an extended pass is a
matter of hours of CPU, not days: prediction is a forward pass per (enzyme, substrate,
temperature) row, ~12 600 rows here, and the fitting afterwards is linear least squares. A GPU is
not required at this scale. **The blocker is not the compute; it is that the output has no
per-enzyme optimum in it.**

## 2. The core change — much smaller than "per-enzyme thermal parameters" sounds

The thermal layer is **already per-enzyme in its data**. `enzyme_cost.py` holds `self._Topt` and
`self._Tm` as per-enzyme arrays over all 2 560 enzymes and applies the global scalars as
vectorised transforms of them:

```python
Topt_eff = T0 + topt_scale * (Topt - T0) + dTopt
Tm_shift = dTm + (tm_scale - 1.0) * (Tm - mean(Tm))
```

What is global is the **perturbation**, not the parameterisation. `dltkcat.apply_fits_to_provider`
already overrides per-enzyme `Topt`/`dCp` on a provider's table from a fits csv, and
`config.py` already wires a `dltkcat_fits:` key per strain. So:

* **Replacing the *source* of per-enzyme Topt with better estimates: ~0 half-days of core work.**
  The plumbing exists and is exercised (13 enzymes today). It needs a better table, not new code.
* **Making the *free parameters* per-enzyme — Li's 2 292 rather than our 16 — is a different and
  much larger change**, and it is not in the thermal layer. It is the calibration: priors per
  enzyme, a sampler that can move in ~2 300 dimensions (Li used SMC-ABC on a cluster for 3–5 days),
  and an identifiability story for parameters that one growth curve cannot constrain. **Estimate:
  6–10 half-days**, most of it in `calibration_multi.py` and the sampling machinery, plus the
  compute.
* **A middle route — per-enzyme Topt held FIXED from data, global scalars retained on top —
  is ~1–2 half-days** and is the one this screen's result actually points at.

**What would need re-verifying, at minimum:** the seven-strain gate (`etcgem audit-sinks` counts
and the K5 class-E budget, both of which Y1 showed can move silently); the P1 gate that reproduces
Parsa's 60/60 and 10/10 numbers; and every committed `resolved_config.yaml`, since a change in the
enzyme table changes the LP. The standing rule from N2/N3 applies: re-run the byte-identity check
after the last change, not at the point it seems safe.

## 3. The recommendation

**Do not start the DLTKcat route.** Two independent reasons, both established above rather than
argued:

1. **The input does not exist.** DLTKcat's predictions for these enzymes have no interior thermal
   optimum in 97 % of cases, so "per-enzyme Topt from DLTKcat" cannot be delivered from the pass
   that has already been run, and there is no reason to expect a second pass to differ.
2. **TASK 2 says the catalytic side is not where the tension is.** With both moments of the
   measured meltome held, re-optimising the catalytic parameters does not recover the fit; the
   compensation that works runs through the **Tm distribution's spread**, not through catalysis
   (`report.md` §4). Per-enzyme *catalysis* is therefore not the missing resolution.

**What the same evidence does point at, and it is cheaper.** The fit does not need the whole
meltome moved; it needs the **least-stable few per cent of enzymes** to be less stable in vivo than
in vitro — `dTm` and `tm_scale` are two global ways of buying the same low tail (§3 of the report).
That is a per-enzyme *stability* question, not a per-enzyme *catalysis* question, and it is
testable against data that exists: the meltome is per-protein, so the enzymes carrying the model's
thermal limit can be named and their measured Tm compared against what the fit needs. **That is a
half-day, not two to three days**, and it would decide the biology-versus-parameterisation question
properly rather than screening it.

**Not decided here.** The recommendation is not to start the expensive route; whether to start the
cheaper one is the PI's call.
