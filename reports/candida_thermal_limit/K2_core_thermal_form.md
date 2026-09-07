# K2 — the four Candida strains on the core's own thermal layer, one component at a time

K1 put the four species on this repository's core and showed that, configured to match, the
core reproduces the standalone Candida etcGEM exactly (79 of 79 comparisons; predicted
growth rate identical at every temperature). K2 switches the core's own machinery back on —
one component per rung — so the four end up on the same footing as *E. coli*,
*M. maripaludis* and *Synechocystis*.

**This changes numbers by design.** The deliverable is the ladder — what each component
did — not a single final answer. Every rung is a separate experiment with its own outputs,
and every number below comes from a committed run.

**K1's gate still passes: 79/79** (`reports/candida_thermal_limit/gate_table.py`, exit 0).

Reproduce everything here with:

```bash
etcgem transfer --experiment transfer_candida               # B0, the corrected baseline
etcgem transfer --experiment candida_B1_unfolding           # B1
etcgem transfer --experiment candida_B2_grounded_budget     # B2
etcgem transfer --experiment candida_B3_ngamT               # B3
etcgem transfer --experiment candida_B4_sectors             # B4
etcgem transfer --experiment candida_B1s_fit_dTm            # sensitivity, outside the ladder
etcgem transfer --experiment transfer_candida_unpinned      # sensitivity: uncorrected (K1 gate)

python3 reports/candida_thermal_limit/ladder_table.py       # the ladder + PART C1
python3 reports/candida_thermal_limit/ceiling_table.py      # PART C2
python3 reports/candida_thermal_limit/solver_compare.py --glpk-root DIR --arbitrate   # PART D
python3 reports/candida_thermal_limit/sink_audit_table.py   # PART E
python3 reports/candida_thermal_limit/gate_table.py         # K1's gate, still green
```

---

## PART A — the corrected baseline

Maintenance is now an obligate, **irreversible** drain in every Candida strain, set in
`strain.yaml` (`provider.pin_at_ub`), not in code. Reading each SBML, it changes exactly one
model:

| strain | reaction | ships as | after | changed? |
|---|---|---|---|---|
| cauris_iRV973 | `ATP_maintenance_NGAM__cyto` | (3.89, 3.89) | (3.89, 3.89) | no-op |
| chaemulonii_draft | `ATP_maintenance_NGAM__cyto` | (3.89, 3.89) | (3.89, 3.89) | no-op |
| cduobushaemulonii_draft | `ATP_maintenance_NGAM__cyto` | (3.89, 3.89) | (3.89, 3.89) | no-op |
| cparapsilosis_iDC1003 | `ATP_Maintenance__cyto` | **(−3.9, 3.9)** | (3.9, 3.9) | **CHANGED** |

iDC1003 ships maintenance reversible, and the solver takes the reverse direction at every
temperature: *C. parapsilosis* paid no maintenance **and** collected 3.9 mmol ATP/gDW/h from
ADP + Pi, a 7.8 swing against the other three. Ilgaz found the same reversibility
independently and corrected it in `19_etcgem_counterfactual.py` and
`22_thermal_sensitivity.py`; it never reached `18_build_etcgem_tpc.py`, which is where the
locked µ table came from.

**Delta from K1, with the solver held constant so the correction is the only change:**

| strain | max \|Δµ\| (h⁻¹) | peak µ | thermal limit (°C) | fit R² |
|---|---|---|---|---|
| *C. auris* | 0.000000 | 0.7988 → 0.7988 | 54.53 → 54.53 | 0.901 → 0.901 |
| *C. haemulonii* | 0.000000 | 0.7305 → 0.7305 | 53.56 → 53.56 | −0.668 → −0.668 |
| *C. duobushaemulonii* | 0.000000 | 0.5537 → 0.5537 | 52.72 → 52.72 | 0.255 → 0.255 |
| *C. parapsilosis* | **0.114419** | 0.7861 → **0.6831** | 55.18 → **53.33** | −0.323 → **+0.042** |

Exactly as predicted: nothing moves except *C. parapsilosis*. The fitted globals and the
growth scale are unchanged to 1×10⁻¹³, because the correction does not touch *C. auris*,
which is what the globals are fitted on.

The uncorrected run is kept as a labelled sensitivity,
`configs/experiments/transfer_candida_unpinned.yaml`, because it is the configuration
`18_build_etcgem_tpc.py` used and therefore the one K1's gate compares against.

**K1's gate is now stronger, not weaker: 79/79**, having gained the 16 corrected-maintenance
growth rates and the 6 required separations recorded in
`gem/tables/counterfactual_results.json`, all reproduced exactly. Both halves of Ilgaz's own
note on the bug now reproduce: **uncorrected**, *C. parapsilosis* cannot be pushed below
detection at 40 °C by *any* uniform Tm shift; **corrected**, it is reachable at 32.64 °C.

---

## PART B — the ladder

Each rung changes one component and is applied cumulatively. Notice what happens to the
fitted freedom: **3 free parameters at B0, 1 at B1, none from B2 on.** From B2 the Candida
model is an a-priori prediction in shape *and* magnitude, as *E. coli* and
*M. maripaludis* are.

| rung | change | free parameters |
|---|---|---|
| B0 | phenomenological form; maintenance corrected (PART A) | σ, w, P |
| B1 | thermal form: phenomenological → **unfolding** | none (P carried over from B0) |
| B2 | budget: B0's fitted P → **grounded** p_total × σ × f_metab | none |
| B3 | maintenance: constant → **NGAM(T)** | none |
| B4 | proteome sectors: off → **on** | none |
| B5 | DLTKcat overlay — **report only, not run** (below) | — |

`growth_scale: peak_match` maps the model's peak onto the *measured* peak of the calibration
strain at every rung, so a rung that changes the magnitude would be invisible in the scaled
numbers. `peak µ (model)` below is therefore the unscaled quantity, and the growth scale is
reported beside it: a scale of *s* means the model under-predicts *C. auris*' measured
0.7988 h⁻¹ by a factor of *s*.

### The ladder table

| rung | species | peak µ (model) | peak T (°C) | Topt (°C) | CTmax (°C) | limit (°C) | fit R² | pool binds | ×free |
|---|---|---|---|---|---|---|---|---|---|
| **B0** | *auris* | 0.3851 | 34 | 34.5 | 55.26 | 54.53 | **0.901** | yes | 5.3 |
| | *haemulonii* | 0.3522 | 34 | 34.5 | 54.56 | 53.56 | −0.668 | yes | 5.8 |
| | *duobushaemulonii* | 0.2669 | 34 | 34.0 | 54.70 | 52.71 | 0.255 | yes | 7.7 |
| | *parapsilosis* | 0.3293 | 36 | 36.0 | 54.36 | 53.33 | 0.042 | yes | 8.6 |
| **B1** | *auris* | 0.4165 | 38 | 38.0 | 53.68 | 53.55 | 0.205 | yes | 4.9 |
| | *haemulonii* | 0.3590 | 40 | 39.5 | 53.34 | 53.14 | −2.089 | yes | 5.7 |
| | *duobushaemulonii* | 0.2957 | 36 | 36.5 | 53.99 | 53.79 | −0.343 | yes | 6.9 |
| | *parapsilosis* | 0.4038 | 38 | 37.5 | 53.45 | 53.33 | −1.017 | yes | 7.0 |
| **B2** | *auris* | 0.1054 | 38 | 38.0 | 53.63 | 53.51 | 0.216 | yes | **19.4** |
| | *haemulonii* | 0.0905 | 40 | 39.5 | 53.31 | 53.12 | −2.070 | yes | 22.6 |
| | *duobushaemulonii* | 0.0745 | 36 | 36.5 | 53.96 | 53.74 | −0.332 | yes | 27.4 |
| | *parapsilosis* | 0.0926 | 38 | 38.0 | 53.40 | 53.23 | −0.727 | yes | 30.6 |
| **B3** | *auris* | 0.1041 | 38 | 38.0 | 53.58 | 53.47 | 0.254 | yes | 19.6 |
| | *haemulonii* | 0.0892 | 40 | 39.0 | 53.29 | 53.08 | −2.032 | yes | 22.9 |
| | *duobushaemulonii* | 0.0738 | 36 | 36.0 | 53.91 | 53.67 | −0.303 | yes | 27.7 |
| | *parapsilosis* | 0.0857 | 38 | 37.0 | 53.29 | 53.08 | −0.432 | yes | 33.1 |
| **B4** | *auris* | 0.0700 | 32 | 30.5 ‡ | 53.75 | 53.60 | 0.111 | **no** | 1.0 / **28.6** |
| | *haemulonii* | 0.0469 | 30 | 30.5 ‡ | 53.44 | 53.21 | −0.847 | **no** | 1.0 / 43.6 |
| | *duobushaemulonii* | 0.0629 | 30 | 30.0 ‡ | 53.95 | 53.83 | −1.145 | **no** | 1.0 / 32.5 |
| | *parapsilosis* | 0.0666 | 30 | 30.5 ‡ | 53.37 | 53.23 | −1.243 | **no** | 1.0 / 42.6 |

‡ **not an optimum.** At B4 the top of the curve is exactly flat over 12.5–20.5 °C (see
below), so Topt is the low edge of a plateau.

Growth scale: B0 **2.07**, B1 **1.92**, B2 **7.58**, B3 **7.67**, B4 **11.42**.
`×free` is growth with the metabolic pool removed, divided by growth as configured; the
second number at B4 is with *every* enzyme-mass cap removed.

### B1 — the thermal form

Only the form changes; the budget stays at B0's fitted 0.3570 g/gDW.

**Rung finding, and the reason this rung needed a core change.** Seq2Topt and Seq2Tm are
**independent** predictors with no joint constraint, and for 1–3% of enzymes they return
`Topt ≥ Tm` — a catalytic optimum above the enzyme's own melting temperature:

| strain | enzymes | Topt ≥ Tm | worst inversion | clamped at a 2 K floor |
|---|---|---|---|---|
| *C. auris* | 1314 | 30 (2.3%) | 31.3 K | 37 (2.8%) |
| *C. haemulonii* | 1312 | 34 (2.6%) | 8.3 K | 55 (4.2%) |
| *C. duobushaemulonii* | 1310 | 35 (2.7%) | 24.3 K | 42 (3.2%) |
| *C. parapsilosis* | 1606 | 16 (1.0%) | 22.8 K | 34 (2.1%) |

The phenomenological form does not notice — peak and death are both bounded in [0, 1], so an
inverted pair just gives low activity. The unfolding form cannot represent it at all: it
anchors turnover on ΔG_u(Topt), which is then ≤ 0, the activation enthalpy jumps from ~10⁵ to
~10⁶ J/mol, and relative turnover collapses by ~10¹⁰ a few degrees below Topt. One such
enzyme on an essential reaction crushes the pool. Unguarded, B1 gave a peak of 1×10⁻⁴ model
units with the growth scale absorbing a factor of 8000, and *C. parapsilosis* dead at every
temperature.

`EnzymeConstrainedModel` therefore gained an admissibility floor on Tm − Topt for the
unfolding form (`provider.topt_tm_min_gap_C`; `None` = off, so every existing strain is
untouched). **2.0 K is not chosen to make a number come out**: it is the smallest Tm − Topt
that already exists in this project's other strains — *M. maripaludis* +2.00 K, and
*E. coli*, with a **measured** meltome, +0.57 K. Neither has a single inverted enzyme. Tm is
kept and Topt gives way, because Seq2Tm is the better-validated predictor (reported test
R² 0.76, RMSE 7.6 °C, against Seq2Topt's 0.57 and 12.3 °C) and the move is far inside
Seq2Topt's own error.

Two smaller consequences, both because the unfolding form's cold limb is Arrhenius rather
than Gaussian: the thermal-limit bisection now brackets from the strain's own peak instead of
a fixed 20 °C, and an earlier draft of this rung that left `pool_budget` free is recorded in
the YAML as the mistake it was — the budget is unidentifiable under a peak-matched scale, so
fitting it added noise *and* changed two things in one rung.

### B2 — the grounded budget

$$P_\text{metab} = p_\text{total} \times \sigma \times f_\text{metab} = 0.46 \times 0.45 \times 0.4461 = 0.0923\ \text{g enzyme/gDW}$$

against B0's fitted **0.3570** — 3.9× smaller. The three numbers, entered as given and not
tuned (change one line of YAML if you prefer others):

* `p_total = 0.46` g protein/gDW — total protein content of *S. cerevisiae*; the value the
  GECKO/ecYeastGEM parameterisation uses as `Ptot`, inside the 0.45–0.50 range quoted for
  exponentially growing yeast.
* `sigma = 0.45` — average in-vivo enzyme saturation, this repository's convention for every
  strain (Davidi 2016; Heckmann 2020); *M. maripaludis* and *E. coli* both use 0.45.
* `f_metab = 0.4461` — mass fraction of the proteome accounted for by enzymes that are *in*
  the metabolic model. This is GECKO's `f` for *S. cerevisiae* (Sánchez et al. 2017, Mol Syst
  Biol 13:935), the same quantity defined the same way. *E. coli*'s **measured** metabolic
  sector in this repository is 0.483.

**It binds, and hard**: removing the pool raises growth 19–31× (against 5–9× at B0). The
shape is essentially unchanged — CTmax moves by less than 0.1 °C — so the grounded budget
acts almost purely on magnitude. And there it under-predicts: peak growth in model units
falls from 0.42 to 0.105, so the a-priori budget gives **7.6× less growth than *C. auris*
measures**. That is a result about a eukaryote in this framework, not something to tune away.
*E. coli*'s own experience is the same in direction (its emergent prior reaches 1.04 h⁻¹
against a measured 2.40) though not in size.

### B3 — NGAM(T)

Maintenance stops being one constant, identical across species *and* across temperature, and
becomes temperature-dependent. **Anchored, not fitted**: each strain's `ngam_base_scale` is
set so NGAM(30 °C) reproduces *that model's own published* maintenance demand — 3.89 mmol
ATP/gDW/h for the three iRV973-derived models, 3.90 for iDC1003 — which is the convention
*M. maripaludis* uses for its measured Goyal 2015 NGAM. Only the temperature dependence is
added.

The effect is small: peak −1% for the three iRV973 models, −7% for *C. parapsilosis*; fit R²
on *C. auris* 0.216 → 0.254; thermal limits down 0.03–0.15 °C.

**The measured comparator cannot be tested against this model, and that is worth saying
plainly.** The Candidas assay gives respiration per unit growth at 40 °C as 0.80 in
*C. auris* against 1.07 in the relatives, a ratio of 1.34. Under B3 at 40 °C (pFBA):

| species | µ | qO₂ | qO₂/µ |
|---|---|---|---|
| *C. auris* | 0.1022 | 0.399 | **3.90** |
| *C. haemulonii* | 0.0892 | 0.348 | **3.90** |
| *C. duobushaemulonii* | 0.0698 | 0.272 | **3.90** |
| *C. parapsilosis* | 0.0830 | 4.950 | 59.6 |

The three iRV973-derived models return *identical* ratios, to three significant figures,
because they are the same reaction network with genes reassigned — the quantity carries no
species signal by construction. *C. parapsilosis*' value comes from a different
reconstruction and lies outside even the feasible range the standalone's own oxygen-FVA
reports (3.5–19.5 at 90% of optimal growth), which is the documented non-identifiability of
qO₂/µ in these models. So the 1.34× comparator is not a test this model can pass or fail.

### B4 — proteome sectors

Yeast fractions, **identical across the four species**: `f_metab` 0.4461 (the same GECKO `f`
as B2), `f_bio` 0.200 (the biosynthesis/translation sector of exponentially growing
*S. cerevisiae* — ribosomal proteins, elongation factors, tRNA synthetases), `f_maint` 0.354
(the remainder). *E. coli*'s **measured** split in this repository is 0.483 / 0.191 / 0.326,
close on all three.

They are identical across species deliberately. No measured per-species, temperature-resolved
*Candida* proteome allocation exists (`docs/CANDIDA_DISCUSSION_2026-09-07.md` §7), so this
layer adds **structural realism** and cannot carry species signal. It is not offered as an
explanation for the interspecies divergence.

**The structural consequence is the finding, and it is larger than "the peak moved".** The
metabolic pool stops being the binding constraint (pool-free ratio 1.00) and the
temperature-**independent** translation cap binds instead (all-caps-free 29–44×). A cap that
does not vary with temperature does not shift the optimum — it *removes* it. The top of the
curve becomes exactly flat:

| rung | width of the region within 0.01% of the peak |
|---|---|
| B0 | 0–0.5 °C |
| B1, B2 | 0 °C |
| B3 | 0–0.5 °C |
| **B4** | ***C. auris* 30.0–48.0 (18.0 °C), *C. haemulonii* 30.0–50.5 (20.5), *C. duobushaemulonii* 30.0–42.5 (12.5), *C. parapsilosis* 30.0–44.5 (14.5)** |

So B4's "Topt = 30–32 °C" in the table above is the **low edge of a plateau**, not an
optimum, and the species ordering that appears to invert is an ordering of plateau heights,
not of optima. It is also why the two LP solvers disagree about B4's Topt by up to 8.5 °C
(PART D) while agreeing on growth to 2×10⁻⁵: the argmax of a tie is arbitrary. CTmax and the
thermal limit remain meaningful — they are read off the falling edge, which the enzyme layer
still owns.

**Ablation cost, reported the way the E. coli work reports it:** fit R² on *C. auris*
**0.254 (B3, no sectors) → 0.111 (B4, sectors)**. *E. coli*'s own figure was 0.74 → 0.49, and
that layer was kept for proteome realism and attributability rather than for fit. The same
judgement applies here, and it is a judgement, not a result.

### B5 — the DLTKcat overlay: report only, not run

The Candida kcats are **DLKcat** — one number per reaction, temperature-independent. The
core's overlay (`provider.dltkcat_fits`) expects **DLTKcat**, which predicts kcat(T) and is
fitted to per-enzyme MMRT (Topt, dCp).

*What is missing*: a per-enzyme kinetic temperature optimum and curvature derived from
predicted turnover, rather than Topt from Seq2Topt and dCp from a single shared literature
prior (−4.0 kJ/mol/K).

*What it would change*: the **cold limb and E_a**, not the upper limit. *E. coli*'s variance
decomposition puts the rising limb and E_a under kinetics while Topt and CT_max are owned by
stability (φ ≈ 0.99). The Candida divergence is entirely at the upper limit, which DLTKcat
does not touch.

*Why it is not run here*: it changes **input data**, not model structure, so movement would
no longer be attributable to a single component and the ladder would be worthless. It is also
expensive — external weights, substrate SMILES, and an enzyme × substrate × temperature grid
of order 50,000+ predictions across four proteomes. Note what is actually lost meanwhile:
*E. coli* uses `dcp_from: prior` with `dltkcat_fits` as an **overlay where fits exist**, so
the shared literature prior is the base case in both organisms and Candida is missing a
refinement, not a mechanism. `docs/CANDIDA_DISCUSSION_2026-09-07.md` A1(iii) schedules it
after K2, with a benchmark attached.

**The overlay stays off.**

---

## PART C1 — does the Figure 4 conclusion survive the core's thermal form?

The counterfactual: how far must a relative's enzymes move, uniformly, before the model puts
it below the 0.05 h⁻¹ detection floor at 40 °C, while its permissive-temperature growth is
checked? Median over the three relatives, against the separation that actually exists.

| form | required ΔTm | × vs predicted 0.52 °C | × vs measured 1.6 °C | required ΔTopt |
|---|---|---|---|---|
| **phenomenological** (B0 — the standalone) | **32.5 °C** | 62.6× | 20.3× | 15.6 °C |
| unfolding (B1) | 13.8 °C | 26.5× | 8.6× | 24.5 °C |
| + grounded budget (B2) | 13.7 °C | 26.4× | 8.6× | 22.5 °C |
| + NGAM(T) (B3) | 13.6 °C | 26.2× | 8.5× | 21.8 °C |
| **+ sectors (B4 — the full ladder)** | **13.8 °C** | **26.5×** | **8.6×** | 23.3 °C |

The two references are both external to this model: **0.52 °C** is the sequence-predicted
paired ortholog ΔTm, *C. auris* minus *C. haemulonii* (95% CI 0.37–0.67); **1.6 °C** is the
**measured** proteome-wide ΔTm between *S. cerevisiae* and *S. uvarum*, 827 protein pairs, for
an 8 °C difference in growth limit (Walunjkar et al. 2025) — the most generous real number
available.

**Stated plainly: the conclusion is form-independent in kind and form-dependent in
magnitude.** The core's thermal form more than halves the required separation — from 32.5 °C
to 13.8 °C — because it ties the upper limit directly to each enzyme's own Tm rather than to a
fitted logistic width. That is a real and substantial change, and the standalone's headline
fold gap of ~63× is an overstatement by a factor of about 2.4 attributable to the thermal form
alone. But 13.8 °C is still **26× the sequence-predicted difference and 8.6× the largest
measured proteome-wide difference on record**. The requirement is stable to within 0.3 °C
across every rung after B1, so neither the grounded budget, nor NGAM(T), nor the sector layer
moves it. Nothing in the core's machinery rescues the prediction.

The Topt route moves the other way, 15.6 → 23.3 °C, for the same mechanistic reason: under
`unfolding` the upper limit is owned by Tm, so shifting Topt is a less efficient way to kill
growth at 40 °C than it was under a Gaussian.

### The sensitivity that is not a rung: how much Tm correction does the curve demand?

`candida_B1s_fit_dTm` frees a single uniform Tm shift on top of B1 and asks what *C. auris*'
measured curve demands. **ΔTm = −9.17 K.** That pulls the predicted thermal limit from
53.6 °C to **44.6 °C** — onto the observed ~45 °C — and raises fit R² from 0.205 to **0.674**.
*E. coli*'s Bayesian calibration demanded **−5.6 K [−7.2, −2.8]** with a *measured* meltome.
Two organisms, same sign, same order of magnitude. It is deliberately outside the ladder: it
fits a parameter rather than switching a component on.

---

## PART C2 — the unfolding ceiling across all seven strains

Each strain at its **emergent** operating point — nothing fitted to the growth curve — which
is the like-for-like comparison with the Candida strains from B2 on. The three existing
strains are read from committed outputs and were not re-run.

| strain | config | Topt (°C) | predicted CTmax (°C) | observed limit (°C) | gap | median enzyme Tm (°C) | Tm source |
|---|---|---|---|---|---|---|---|
| eciML1515 | emergent | 39.9 | 51.82 | 45.94 | **+5.9** | 55.6 | **MEASURED** meltome |
| eciML1515 | *tuned* | 38.4 | 45.93 | 45.94 | *−0.0* | 55.6 | measured, posterior-corrected |
| mmaripaludis | emergent | 42.0 | 46.84 | 47.00 | **−0.2** | 55.9 | predicted |
| syn6803 | emergent | 36.0 | 45.70 | 44.00 | **+1.7** | 56.9 | predicted |
| *C. auris* | emergent (B4) | 30.5 ‡ | 53.60 | 44.00 † | **+9.6** | 53.7 | predicted (Seq2Tm) |
| *C. haemulonii* | emergent (B4) | 30.5 ‡ | 53.21 | 38.00 | **+15.2** | 53.5 | predicted (Seq2Tm) |
| *C. duobushaemulonii* | emergent (B4) | 30.0 ‡ | 53.83 | 38.00 | **+15.8** | 53.5 | predicted (Seq2Tm) |
| *C. parapsilosis* | emergent (B4) | 30.5 ‡ | 53.23 | 38.00 | **+15.2** | 54.2 | predicted (Seq2Tm) |

† right-censored: *C. auris* still grows at the top of the assay range (44 °C).
‡ the low edge of a plateau, not an optimum (see B4). The CTmax column, which is what this
table is about, is read off the falling edge and is unaffected; at B3, the last rung with a
genuine peak, the Candida Topt values are 36–39 °C.
Observed limits for the Candida strains are derived, not asserted: the highest assayed
temperature at which the measured curve still reaches 0.05 h⁻¹, the same definition the
model's own limit uses.

**This refines rather than confirms `docs/CANDIDA_DISCUSSION_2026-09-07.md` §4.** That
section reads as a general over-prediction across the model class. The seven-strain table
says the over-prediction is severe in the four Candida strains (+9.6 to +15.8 °C) and real in
*E. coli*'s emergent prior (+5.9 °C — reproduced here exactly, from
`outputs/calibration_vanderlinden/`), but **absent in *M. maripaludis* (−0.2) and small in
*Synechocystis* (+1.7)**. Both of those, note, take Topt and Tm from a *prior* rather than
from independent predictors, and neither is a strong test of a measured or predicted Tm
distribution.

The *E. coli* row deserves care in both directions. Its emergent prior over-predicts by
5.9 °C; its Bayesian posterior, which pulls Tm down by 5.6 K, lands on 45.93 against an
observed 45.945. So in *E. coli* a uniform Tm correction removes the ceiling entirely — and
K2's B1s sensitivity finds *C. auris* demanding the same kind of correction at −9.17 K.
That is the strongest form of the §4 claim the evidence here supports: **where the ceiling
appears, a uniform downward Tm correction of 6–9 K removes it, in a bacterium and in a
yeast.** Note also that the median enzyme Tm barely varies across the seven (53.5–56.9 °C)
while the observed limits span 38–47 °C — the table does not show the model tracking the
observed limit.

The table states what it shows; it is not interpreted further here.

---

## PART D — solver

K1 pinned GLPK because the standalone solved with it, and the port then reproduced the
standalone exactly. That hid a ~0.4% disagreement at the coldest point of the two draft
models' sweeps. K2 runs on Gurobi and reports the difference.

Every rung was run under both solvers and every per-temperature growth rate compared in
**model units** (unscaled, so a peak-matched growth scale can neither mask nor manufacture a
difference). Of 320 paired quantities, **43 differ by more than 10⁻⁶** — 35 growth rates and 8 derived descriptors (Topt, CTmax, thermal limit, peak):

| rung | species | n above threshold | max \|Δ\| | max relative | temperatures |
|---|---|---|---|---|---|
| B0 | *duobushaemulonii* | 1 | 3.8e−4 | 0.37% | 22 °C |
| B0 | *haemulonii* | 1 | 4.9e−4 | 0.46% | 22 °C |
| B1 | *haemulonii* | 2 | 1.6e−5 | 0.03% | 22–24 °C |
| B2 | *duobushaemulonii* | 3 | 1.2e−4 | **0.50%** | 22–26 °C |
| B2 | *haemulonii* | 5 | 1.7e−5 | 0.05% | 22–30 °C |
| B2 | *parapsilosis* | 2 | 2.0e−5 | 0.07% | 22–24 °C |
| B3 | *duobushaemulonii* | 3 | 1.2e−4 | **0.50%** | 22–26 °C |
| B3 | *haemulonii* | 5 | 1.7e−5 | 0.04% | 22–30 °C |
| B3 | *parapsilosis* | 1 | 1.1e−5 | 0.05% | 22 °C |
| B4 | *haemulonii* | 12 | 1.7e−5 | 0.04% | 22–44 °C |

*C. auris* never differs, at any rung, at any temperature. The differences concentrate at the
**cold end** of the two **draft** models, exactly as K1 reported; at B4 *C. haemulonii*
differs by a constant at every temperature because the temperature-independent translation cap
is what binds.

The eight non-growth differences are all at B4 and all follow from the same thing. The two
solvers agree on B4's growth to 2×10⁻⁵ but disagree about **Topt** by up to 8.5 °C
(*C. auris* 30.5 vs 39.0; *C. duobushaemulonii* 30.0 vs 36.5), because B4's curve is flat
across 12.5–20.5 °C and the argmax of a tie is arbitrary. That is not a solver defect; it is
the plateau reported under B4 showing up in a second way. CTmax and the thermal limit differ
by at most 0.006 °C.

**They are numerical, and this is established rather than asserted.** An LP's optimal
*objective* is unique — alternate optima differ in the flux vector, not in the growth rate —
so a difference in predicted growth cannot be alternate optima. Three checks, on the largest
disagreement (*C. duobushaemulonii*, B3, 22 °C):

| | as-is | rescaled | shift |
|---|---|---|---|
| Gurobi | 0.0181860104 | 0.0181860104 | +3e−18 |
| GLPK | **0.0182768108** | 0.0181860104 | **−9.1e−5** |
| `glpk_exact` (rational arithmetic) | 0.0181860104 | 0.0181860104 | −3e−12 |

1. Tightening Gurobi's feasibility and optimality tolerances to 1e−9 moves its answer by
   7e−18 — it is converged.
2. Rescaling to a **mathematically identical** but well-conditioned LP (divide every pool
   coefficient *and* the budget by the median coefficient) makes GLPK agree with Gurobi
   *exactly*.
3. GLPK's own rational-arithmetic solver agrees with Gurobi.

So GLPK's floating-point answer is the wrong one. The cause is conditioning: at 22 °C the
pool constraint's coefficients span **1.2×10⁻⁷ to 98**, a dynamic range of 8.2×10⁸, because
the 1×10⁻⁶ activity floor puts a handful of enzymes many orders of magnitude above the
median cost.

**The consequence for K1 should be stated.** K1 reproduced the standalone exactly — including,
at one temperature per draft model, a value that was slightly wrong. The standalone's own
numbers at 22 °C for *C. haemulonii* and *C. duobushaemulonii* are off by ~0.4%. Nothing in
Figure 4 depends on the coldest point of the two draft curves, so this changes no conclusion;
it is recorded because "reproduces the reference exactly" and "is correct" are different
claims, and K1 established only the first.

---

## PART E — the uncosted-energy-sink audit, framework-wide

Three strains have needed the same kind of correction, each found by hand and fixed
differently. All three are one failure: a reaction that moves free energy **without paying
enzyme cost**, so the proteome constraint cannot see it. `etcgem audit-sinks` is that check,
generalised. It reports and fixes nothing.

| class | what it finds |
|---|---|
| A | uncosted reaction that can produce ATP / NAD(P)H / FADH₂ / quinol / reduced ferredoxin |
| B | reversible maintenance/ATPM — maintenance the solver can run backwards |
| C | hard-pinned uncosted drain — a forced non-zero bound with no enzyme cost |
| D | uncosted consumer of a terminal electron acceptor (O₂, nitrate, fumarate) — bypassing the costed respiratory chain |

`--raw` rebuilds without the strain's own corrections, so the audit can be checked against the
cases it was written from.

| strain | mode | reactions | costed | uncosted | A | B | C | D |
|---|---|---|---|---|---|---|---|---|
| eciML1515 | configured | 6085 | 2560 | 3525 (58%) | 10 | 0 | 1 | **25** |
| eciML1515 | raw | 6085 | 2560 | 3525 | 10 | 0 | 1 | **27** |
| mmaripaludis | configured | 688 | 527 | 161 (23%) | 23 | 0 | 1 | 0 |
| mmaripaludis | raw | 688 | 527 | 161 | 23 | 0 | 1 | 0 |
| syn6803 | configured | 1303 | 1066 | 237 (18%) | 7 | 0 | 1 | 17 |
| syn6803 | raw | 1303 | 1066 | 237 | 7 | 0 | 1 | 17 |
| *C. auris* | configured | 2863 | 1314 | 1549 (54%) | 44 | 0 | 1 | 26 |
| *C. auris* | raw | 2863 | 1314 | 1549 | 44 | 0 | 1 | 26 |
| *C. haemulonii* | configured / raw | 2863 | 1312 | 1551 (54%) | 45 | 0 | 1 | 26 |
| *C. duobushaemulonii* | configured / raw | 2863 | 1310 | 1553 (54%) | 47 | 0 | 1 | 28 |
| *C. parapsilosis* | configured | 2162 | 1606 | 556 (26%) | 24 | **0** | **1** | 18 |
| *C. parapsilosis* | raw | 2162 | 1606 | 556 | 25 | **1** | **0** | 18 |

**It finds all three known cases by itself:**

* *E. coli* — class D falls 27 → 25 when the O2-sink closure is applied. This class exists
  because the E. coli sinks *dissipate* free energy rather than producing it; classes A–C
  would have missed them.
* *M. maripaludis* — class C, `rxn00062_LSQBKT_c0_RSQBKT_`, **FIXED at [7.836, 7.836]** raw,
  becoming a floor `[7.836, 1000]` once `relax_pinned` is applied.
* *C. parapsilosis* — class B, `ATP_Maintenance__cyto` at **[−3.9, 3.9]** raw, becoming class
  C `FIXED [3.9, 3.9]` once the K1/K2 correction is applied. This is the K1 finding,
  rediscovered automatically.

Two standing facts the table states without editorialising. Every strain has exactly one
class C hit, and in every case it is maintenance: **maintenance is uncosted by design in all
seven models**. And 18% (*Synechocystis*) to 58% (*E. coli*) of reactions carry no enzyme cost
at all — 54% in the three iRV973-derived Candida models — which is the layer the discussion
notes identify as thermally unconstrained.

---

## What moved, and why

For a reader who was not here.

**Nothing that mattered moved because of the maintenance correction.** It touches one model,
*C. parapsilosis*, whose reconstruction let the solver run maintenance backwards and make ATP
for free. Correcting it lowers that species' predicted growth by ~13% and its thermal limit
by 1.9 °C, and brings it into line with the other three. It is the standalone's own
correction, applied consistently for the first time.

**The thermal form is the one component that changes the scientific answer.** Under the
standalone's Gaussian × logistic, the model needed 32.5 °C of interspecies Tm separation to
reproduce the observed collapse. Under this repository's two-state unfolding form it needs
13.8 °C. That is a factor of 2.4, and it is worth knowing, because the standalone's published
fold gap of ~63× was computed under the form that requires the most. Under the shared form the
gap is ~26× against the sequence prediction and ~8.6× against the largest measured
proteome-wide difference in the literature. **The conclusion — that sequence-predicted enzyme
thermal properties are far too similar between these species to reproduce the observed
divergence — survives, with a smaller number attached to it.**

**Nothing else moved it.** Grounding the proteome budget in yeast literature, adding
temperature-dependent maintenance and adding a proteome-sector layer change the required
separation by less than 0.3 °C between them. They change other things — the grounded budget
under-predicts growth by 7.6×, and the sector layer's temperature-independent translation cap
takes over as the binding constraint and drags the predicted optimum down to 30–32 °C — but
none of them is a candidate mechanism for the interspecies difference, and the sector layer in
particular cannot be, because no measured per-species allocation exists to put in it.

**Two things the ladder found that were not on the list.** The two sequence predictors
disagree about physics for 1–3% of enzymes, returning a catalytic optimum above the melting
temperature; the standalone's thermal form is blind to that and this repository's is not, so
the core needed an admissibility check. And the LP is badly enough conditioned at the cold end
that GLPK, the standalone's solver, gets one point per draft model wrong by ~0.4%.

**What the ceiling table says.** Across seven strains at their emergent operating points the
model over-predicts the upper thermal limit by +9.6 to +15.8 °C in the four Candida species
and by +5.9 °C in *E. coli*, but not in *M. maripaludis* or *Synechocystis*. Where it does
over-predict, a uniform downward Tm correction of 6–9 K removes it — −5.6 K demanded by
*E. coli*'s measured meltome, −9.2 K by *C. auris*' growth curve. The median enzyme Tm hardly
varies across all seven strains (53.5–56.9 °C) while their observed limits span 38–47 °C.
Whatever sets the real upper limit in these organisms, the model is not tracking it through
bulk enzyme stability.

---

## Files

| what | where |
|---|---|
| ladder, all rungs × species × descriptor | `ladder_table.csv`, `ladder_wide.csv` |
| required separations and fold gaps (PART C1) | `ladder_counterfactual.csv` |
| seven-strain ceiling (PART C2) | `ceiling_table_B4.csv` |
| Gurobi vs GLPK, every difference (PART D) | `solver_comparison.csv` |
| sink audit (PART E) | `sink_audit_table.csv`, `sink_audit_hits.csv` |
| K1's gate, still green | `gate_table.csv`, `K1_port_verification.md` |
| per-strain outputs, per rung | `strains/*/outputs/transfer_*/`, `outputs/transfer_*/` |
