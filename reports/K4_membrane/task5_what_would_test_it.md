# K4 TASK 5 — what would turn this from an available mechanism into a tested one

K4 made an ETC membrane-area constraint available for the *Candida* strains and found it cannot
carry the interspecies comparison, for two independent reasons: the respiratory chain is not
load-bearing in three of the four models (TASK 1), and the footprints available to parameterise
it do not differ between the species (TASK 2). This lists what would remove each obstacle, in
the order that makes each subsequent item worth doing.

Three different measurements are conflated in the phrase "the membrane hypothesis". They answer
different questions and only one of them is what this constraint consumes.

| measurement | what it yields | what it can decide |
|---|---|---|
| **ETC complement / abundance** | which complexes each species has, and how many | whether the *chain* differs — the `reactions` and stoichiometry columns |
| **Mitochondrial membrane area** | nm² of inner membrane per gDW, per species and per temperature | `A_ETC` — the budget itself, the single free knob |
| **Lipidomics** | acyl-chain composition, sterol and cardiolipin content | *not* this constraint at all — it feeds fluidity and proton leak, which this mechanism does not represent |

The third is the one most often proposed and the one this constraint cannot use. A membrane-area
budget is indifferent to what the membrane is made of. Lipidomics would be evidence for a
*different* mechanism — homeoviscous adaptation and temperature-dependent proton leak — which
would need the modelling extension A8 scopes, not a table of footprints.

---

## 1. Repair the proton accounting — the precondition, and it needs no new data

**What.** Remove the proton coupling from the eleven uncosted metabolite/H⁺ symporters in the
three iRV973-derived models, or cost them, so the proton circuit closes through the chain.
**Why first.** Until this is done, an area constraint in *C. auris*, *C. haemulonii* and
*C. duobushaemulonii* binds on ATP synthase and not on respiration (TASK 1), so no amount of
better footprint data would make the result mean anything. It is the only item here that is
free.
**What would distinguish.** After the repair, complex III and cytochrome *c* oxidase carry
5–9 mmol/gDW/h instead of 0.005, and predicted growth falls by about a third. Whether that
model then reproduces the measured respiration is itself a test.
**Caveat.** It is a reconstruction change with a large effect on predicted growth, so it must be
a labelled configuration compared against the published one, not a silent default — and it
should go back to Ilgaz, since it is his reconstruction's behaviour and not a porting artefact.

## 2. Mitochondrial inner-membrane area per gDW, per species — the measurement this constraint consumes

**Which quantity.** Inner-membrane (cristae) area per gram dry weight, which decomposes into
three measurable factors: mean cell volume, mitochondrial volume fraction, and cristae membrane
area per unit mitochondrial volume.
**On which species.** *C. auris* and at least one of *C. haemulonii* / *C. duobushaemulonii*,
grown together in the same medium; *C. parapsilosis* as the outgroup.
**At which temperatures.** At minimum the permissive temperature (30–32 °C) and 40 °C, the
temperature at which the relatives stop growing and *C. auris* does not. A single-temperature
comparison cannot separate a constitutive species difference from a thermal-acclimation
response, and those are different hypotheses.
**By what method.** Serial-section electron tomography or FIB-SEM with stereological sampling,
which is what yields membrane area per volume rather than a morphology score. Fluorescent
mitochondrial-volume staining is cheaper and answers only the volume-fraction factor, which is
one of three.
**What result would distinguish.** TASK 3 gives the required interspecies ratio in A_ETC. If
measured inner-membrane area per gDW differs between *C. auris* and the relatives by at least
that ratio, in the right direction, the mechanism becomes a live explanation. If it differs by
much less — as the enzyme-thermal route did — the mechanism is excluded on its own parameters,
which is the same verdict K2 reached for Tm and is worth reaching cleanly.

## 3. Respiratory-complex abundance per species — what makes the table species-specific

**Which quantity.** Copies per cell, or mol per gDW, of complexes I–IV, ATP synthase and
alternative oxidase.
**On which species.** The same four, same cultures as item 2.
**By what method.** Targeted proteomics (PRM/SRM) on isolated mitochondria against labelled
standards, or BN-PAGE with densitometry for relative complex stoichiometry. Note that a
complex's *area* footprint and its *abundance* are different quantities: this constraint takes
the footprint per complex from structure and lets the LP choose abundance, so abundance data
tests the prediction rather than parameterising it.
**What result would distinguish.** If the relatives carry a different complement — in
particular a different alternative-oxidase share, which is the one genuinely fungal branch —
that is a species difference expressible in the `reactions` and electrogenicity columns
without any new footprint measurement.

## 4. Alternative oxidase: put it in the models, then measure its engagement

**What.** AOX is present in all four proteomes and in none of the four models (A3, confirmed
here by a second method). Adding the reaction is a reconstruction edit of one line.
**Why it matters here.** AOX is non-electrogenic: it consumes oxygen and conserves no energy.
That is exactly the role cytochrome *bd*-II plays in the *E. coli* configuration F that this
mechanism was gated on, where making one oxidase non-electrogenic is what let respiration
decouple from growth. It is the single most direct transfer of the gated *E. coli* result to a
fungus, and it currently cannot be attempted.
**By what method.** For engagement: respirometry with the AOX inhibitor salicylhydroxamic acid
(SHAM) and the cytochrome-pathway inhibitor antimycin A / cyanide, across temperature, giving
the fraction of respiration that runs through the alternative pathway.
**What result would distinguish.** If the AOX-dependent fraction rises with temperature in
*C. auris* and not in the relatives, that is a species-specific, temperature-dependent,
measurable difference in the ETC, sourced from measurement rather than from a sequence
predictor — the property §6a of the discussion notes says the axis needs.

## 5. What lipidomics would and would not settle

**What.** Acyl-chain saturation, sterol content and cardiolipin content of mitochondrial
membranes, per species, across temperature.
**What it would settle.** Whether the four species differ in membrane physical state, and
whether they remodel differently with temperature. That is worth knowing and nobody has looked.
**What it would not settle.** Anything about this constraint. It has no lipid term. Using
lipidomics here would require the modelling extension A8 describes — a composition state
variable with a temperature-dependent fluidity target, a remodelling cost, and proton leak as
temperature-dependent maintenance — which is a project, not a table.
**Ranking.** Lower priority than items 1–4 *for this mechanism*, and possibly higher priority
than all of them for the membrane hypothesis in general. The two should not be conflated, and
the case for lipidomics should be made on its own terms rather than borrowed from a
membrane-area result that cannot use it.

---

## The honest ordering

Item 1 costs nothing and blocks everything else. Item 4 is cheap, is the direct analogue of the
one ETC result this project has already gated against experiment, and needs one reaction and a
respirometry run with two inhibitors. Item 2 is the measurement this constraint actually
consumes and is the expensive one. Item 3 tests rather than parameterises. Item 5 answers a
different question and should be commissioned for that question.

One prior worth carrying into any of them. The Candidas project's own screen counted sterol-
pathway gene copies across these species and clades: 9–12 per species, against 10–11 across the
four *C. auris* clades, which are 99.3–100 % identical. The between-species spread barely
exceeds the within-species spread — the same pattern that made the Seq2Tm distributions
uninformative. That is a reason to measure the phenotype rather than infer it from gene
content, not a reason to expect a large difference.
