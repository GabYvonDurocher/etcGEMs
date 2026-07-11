# What sets the organism-level activation energy (Ea) of the E. coli growth TPC

A mechanistic dissection on the **tuned** model (P2 v3 posterior medians), rich BHI, growth
law ON, reconciled pool, with the free-O2 sinks closed. Seed material for the future
`reports/activation_energy/` paper. **Non-circular by construction:** the per-enzyme
activation energies `Ea_i` are INPUTS (MMRT `dCp` + `Topt` via DLTKcat; folded fraction
`f_N` via `Tm`). The result is not "the Ea" — it is how the organism-level `Ea_org`
**aggregates** the enzyme `Ea_i` and **departs from their naive mean**.

## Headline (rich BHI)

`Ea_org = 0.909 eV` (rising-limb window 17–35 °C; identical descriptor/window to the report's
tuned Ea). It is, to first order, a **control-weighted mean of the enzyme `Ea_i`**, shifted by
two non-kinetic couplings:

| term | eV | what it is |
|------|----|------------|
| control-weighted mean `Ea_i` | **0.970** | the enzyme-kinetic backbone (`Σ C_i Ea_i / Σ C_i`) |
| allocation (growth law) | **−0.107** | growth-law proteome reallocation lowers Ea |
| maintenance NGAM(T) | **−0.010** | temperature-dependent maintenance (small) |
| residual (nonlinear) | +0.057 | higher-order / window nonlinearity |
| **= `Ea_org`** | **0.909** | closes |

**The decomposition closes.** (Cross-check: with the growth law switched off, `Σ C_i ≈ 1.02`
and `Σ C_i Ea_i = 0.96 ≈ Ea_org(no-GL) = 1.02` directly — the summation theorem holds on the
kinetic backbone.)

## Control is concentrated — and the growth law shares it

`Σ C_i = 0.556` over the 230 flux-carrying enzymes (`C_i = ∂ln μ/∂ln kcat_i`, finite
difference, reusing the control harness). The metabolic pool is the sole binding enzyme-mass
constraint, but the **growth-law biomass term inside that pool holds the remaining ~0.44 of
marginal growth control** (verified: σ/budget elasticity ≈ 1.0). Off the growth law `Σ C_i`
returns to ≈ 1. Within the metabolic share, control is concentrated in a handful of enzymes
(consistent with the concentrated thermal-control finding).

## The departure from the naive mean (the non-circular result)

| mean of `Ea_i` | eV |
|----------------|----|
| unweighted (flux-carrying) | 0.867 |
| proteome-mass-weighted | 0.896 |
| **control-weighted** | **0.970** |
| **`Ea_org`** | 0.909 |

`Ea_org − unweighted mean = +0.042 eV`, attributed as:
**control concentration +0.103** (the controlling enzymes have a *higher* Ea than the average
enzyme) **− allocation 0.107 − maintenance 0.010**. So the organism-level Ea is pulled *up* by
which enzymes hold control and *down* by the growth-law reallocation — the departure, not the
value, is the finding.

## Which enzymes / pathways set it

Top contributors `C_i·Ea_i` (rich BHI): **gapA** (GAPDH, glycolysis), **fabB** (fatty-acid
synthase), **acpP/aas** (acyl-carrier protein, high `Ea_i` 2.0), **eno** (enolase), **glnA**
(glutamine synthetase), **fadA** (β-oxidation). By functional category (COG), the contribution
is dominated by **lipid / fatty-acid metabolism (+0.28)** and **carbohydrate / glycolysis
(+0.15)**, with amino-acid and coenzyme metabolism minor. `Ea_org` is thus **pathway-localised**
to central-carbon + lipid biosynthesis rather than distributed evenly across the proteome.

## Robustness

- **Homogenise** (all enzymes → the common mean `Topt`/`dCp`): `Ea_org → 1.320 eV`. **Caveat
  (see `DIAGNOSTIC_NOTE.md`):** this large value is largely a numerical/edge artefact — setting
  all `Topt` equal sharpens the peak and shifts the rising-limb window (17–35 → 23–35 °C) into a
  steeper, hotter region where maintenance amplifies it (+0.40), and the homogenisation is
  incomplete (`Tm`/`f_N` not homogenised). Do **not** read it as "heterogeneity lowers Ea"; use
  the moderate-spread result below instead.
- **Spread sensitivity** (scale the `Topt`/`dCp` heterogeneity ×0.5–1.25): `Ea_org` is stable at
  ~0.90–0.93 over the moderate range (it diverges only at unphysically large spreads that break
  the curve).
- **Medium:** at glucose-minimal `Ea_org = 0.976` vs 0.909 on BHI, and the top-15 controlling
  enzymes overlap only **6/15** — the *mechanistic basis* of Ea is **medium-dependent** (a
  different controlling set), even though the value is similar.
- **Emergent vs tuned:** the top-15 controlling set overlaps **7/15** with the emergent model —
  the control-weighting mechanism is **structural**, not an artefact of the Bayesian fit.

## One-line account

`Ea_org` is a **control-weighted mean of the enzyme activation energies**, set mainly by a few
**glycolytic and fatty-acid-synthesis** enzymes; it sits **above** the naive enzyme-Ea mean
because control is concentrated on higher-Ea enzymes (+0.10 eV), and is pulled back **down** by
the growth-law proteome reallocation (−0.11 eV) and, slightly, temperature-dependent
maintenance (−0.01 eV). The controlling set is medium-dependent but structural. (First-order
MCA; residual labelled.)
