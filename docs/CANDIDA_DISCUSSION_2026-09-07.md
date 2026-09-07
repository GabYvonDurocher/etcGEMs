# Discussion notes — what the Candida etcGEM result means, and what to do next

_2026-09-07. Recorded while K1 (the port of the four Candida species into this repository) was
running. Companion to `CANDIDA_ETCGEM_PLAN.md`, which covers the structural merge only. This
document is the scientific reasoning around it: why the Candida etcGEM cannot reproduce the
observed thermal divergence, what that does and does not license us to conclude, and which axes
remain open. Sources are named so each claim can be checked._

---

## 1. The result being explained

Ilgaz's etcGEM gives every enzyme in four *Candida* species a sequence-predicted molecular weight,
turnover number, optimum temperature and melting temperature; fits three global shape parameters
(σ, w, P) to the *C. auris* growth curve alone; freezes them; and predicts the three relatives.
The relatives' measured growth collapses above ~36 °C while the model keeps predicting 0.3–0.5 h⁻¹.

The reason is in the inputs. Paired across orthologs, *C. auris* enzymes are predicted **0.52 °C**
more heat-stable than *C. haemulonii*'s (95 % CI 0.37–0.67). The fitted model needs about **33 °C**.
A ~63-fold gap. Substituting a *measured* proteome-wide ΔTm — *S. cerevisiae* vs *S. uvarum*,
1.6 °C across 827 proteins for an 8 °C difference in growth limit — still leaves ~20-fold.
Concentrating large shifts on ranked bottleneck enzymes does not rescue it (flux reroutes; a beam
search over pairs and triples found nothing crossing detection).

Conclusion as it stands: **within this model class, sequence-predicted enzyme thermal properties
are far too similar between these species to reproduce the observed divergence.**

## 2. What Ilgaz has already closed

Recorded here so these are not re-proposed. His `gem/audits/` covers more than the emails suggest.

- **Catalysis** (Fig 4): the headline result above.
- **Proteostasis** (`proteostasis_burden.py`): temperature routed through a damaged-protein burden
  charged as ATP maintenance and/or lost capacity, with the coupling constants shared so all
  species difference comes from the Tm distributions. Fails for the same reason as Fig 4 — and
  correctly computes the discriminating quantity *before* building the model.
- **Bottleneck concentration** (`19_etcgem_counterfactual.py`, beam search): no small set of
  enzymes reproduces the collapse.
- **Model defects** (`gap_robustness.py`, commit `a21d863`): correcting the respiratory quotient,
  blocking the energy-generating cycle and setting the unfolding width to its physical value moves
  the predicted limit by less than 1 °C. The limit tracks median enzyme Tm regardless.
- **Pseudo-replication** (`24_paired_dedup_audit.py`): the paired statistic was reaction-level, so
  n over-counted and the mean was weighted by enzyme promiscuity. Corrected to unique protein pairs.
- **Seq2Tm padding artefact** (commit `55c2520`): checked, does not inflate Fig 4B.
- **Network confounding** (`common_network.py`): each species' enzyme profile run on the identical
  *auris* scaffold. **Its result is not recorded in the notes — get the number from Ilgaz.**

**The general lesson.** Any mechanism whose species-specificity is *sourced from* Seq2Tm/Seq2Topt
is already answered, whatever layer it is routed through. Mechanisms sourced from measurement are
not. (One correction to an earlier over-generalisation: the maintenance falsification is *not* in
this class — it asks what multiplier would be required, against a measured comparator of 1.34×
respiration per unit growth at 40 °C in the relatives versus *auris*.)

## 3. Two claims that were being conflated

1. **Within a model, Tm controls the upper limit.** E. coli's variance decomposition gives
   φ_stability = 0.994 for CT_max and 0.999 for T_opt. True.
2. **Between species, Tm is what differs.** False here — 0.52 °C predicted, 1.6 °C even when
   measured in the *S. cerevisiae*/*S. uvarum* pair.

Both hold at once, and together they are a problem for the model class rather than for Ilgaz's
execution.

**The circularity to keep in view.** A variance decomposition can only attribute to mechanisms the
model contains. If two-state unfolding is the only thing that can produce a hot collapse, the
decomposition will assign the collapse to unfolding whether or not that is what kills real cells.
Membrane fluidity, proton leak and ROS receive zero share by construction, not by evidence.

## 4. The convergence that makes this bigger than Candida

Both models over-predict the upper thermal limit, in the same direction:

| | predicted CT_max | observed | gap |
|---|---|---|---|
| *E. coli* (emergent, **measured** Tm from the meltome) | ~52 °C | 46 °C | **+6** |
| *C. auris* | 54.1 °C | ~45 °C | **+9** |
| the three relatives | ~53–54 °C | ~40 °C | **+13–14** |

E. coli's Bayesian calibration had to pull Tm down by **−5.6 K [−7.2, −2.8]** to match the observed
collapse — with a *measured* meltome, so this is not a predictor artefact. Ilgaz reached the same
place independently.

Read together: **bulk enzyme unfolding sets a ceiling that is systematically too high, in a
bacterium and in a yeast, with measured and predicted Tm alike. Something kills cells before their
enzymes denature.** This is a stronger and more general statement than "the Candida etcGEM failed",
it is supported by two organisms rather than one, and it is the framework-level question the merge
makes askable across all seven strains.

## 5. Coverage: what the model actually sees

| Stage | *C. auris* | Across the four |
|---|---|---|
| Proteins in the proteome | 5,424 | 5,173–5,830 |
| In the metabolic model | ~1,000 | metabolic subset 662–997 |
| Carrying a thermal prediction | ~704 | 3,043 Seq2Tm rows total |
| Carrying flux at a given temperature | fewer still | — |

The etcGEM's entire channel for species difference is **~700 enzymes × 2 parameters — about 13 % of
the proteome**. The large cut is definitional (a GEM models metabolism; ribosomes, chaperones,
transcription, signalling and transport are not reactions), not a pipeline failure.

Note also that the **metabolic subset spans 662–997 genes, a 1.5× range**, far wider than the 13 %
spread in proteome size. That is reconstruction depth — two curated models against two KOfam drafts
— so network coverage differs more between species than the proteomes do. `common_network.py` is
the right control and its result should be on record.

**Sequence divergence is real.** *C. auris* and the *haemulonii* complex differ by 0.33–0.35
substitutions per site. These are not near-identical organisms; that description applies only to
the four *C. auris* clades. So the striking fact is that genuinely divergent proteomes yield a
predicted ΔTm of 0.52 °C — either thermostability is that conserved, or the predictor cannot see
the substitutions that matter.

**Crucially: fixing coverage does not fix the species question.** Adding the missing 4,400 proteins
would bring their species-specificity through the same flat Seq2Tm channel. Coverage and
species-signal are separate problems.

## 6. Axes that remain genuinely open

Ordered by how independent each is of the Seq2Tm channel.

**(a) Membrane lipid composition — the most promising, and entirely absent from both models.**
Neither `src/etcgem` nor `gem/` represents the membrane as a physical structure with a
temperature-dependent state. Lipids appear only as metabolism (reactions consuming enzyme cost) and
as a COG label in the activation-energy dissection. Homeoviscous adaptation, phase behaviour, and
temperature-dependent proton leak cannot be expressed.

Two independent hints point here, both from our own work: Li et al.'s founding etcGEM paper found
its single most rate-limiting thermal enzyme was **ERG1, squalene epoxidase** — sterol synthesis —
and swapping it produced a thermotolerant strain; and E. coli's top control enzyme is **acpP/aas,
acyl carrier protein** — fatty-acid synthesis — dominating by an order of magnitude. Two organisms,
two analyses, a lipid-synthesis enzyme both times. The models can find the enzyme and are
structurally blind to why it might matter.

Membrane composition is also the right *shape* of mechanism: a measurable phenotype that can differ
between species with near-identical proteomes, i.e. not sourced from sequence prediction. And it is
consistent with §4 — a membrane mechanism is exactly what failure *below* the unfolding ceiling
looks like from inside a model that only has enzymes.

**(b) Proteome allocation, with measured sector fractions.** E. coli's model carries measured,
temperature- and medium-dependent sector fractions (f_metab 0.483, f_bio 0.191, **f_chaperone
0.057**, f_other 0.269) from temperature proteomics; the non-metabolic proteome enters as mass
competing for the same budget. Candida has no sector layer at all. Adding it with literature yeast
values is structural realism available today; making it carry *species* signal needs measured
per-species allocation across temperature, which does not exist.

**(c) In-vivo saturation σ.** E. coli's rich peak demanded σ ≈ 0.87, railed toward its physical
ceiling — height is a capacity quantity. Ilgaz fitted a single pool P, which conflates budget and
saturation and is shared across species by construction. Whether *auris* runs its proteome closer
to saturation at high temperature is a magnitude mechanism the current Candida model has no lever
for.

**(d) Temperature-dependent maintenance.** Ilgaz's model pins NGAM at one constant, identical
across species *and across temperature*. The core's unfolding branch has NGAM(T). This is a
structural difference, and it interacts with the measured 1.34× respiration-per-growth ratio.

**(e) Gene content.** Presence/absence is genuinely species-specific, needs no new data, and is
already partly visible in `gem/tables/*_evidence.csv`. Nobody has looked. The Xiao et al. candidates
(alternative oxidase in particular) are exactly this kind of thing.

## 7. Data availability, checked

- **Measured eukaryotic meltome exists**: the Meltome Atlas (Jarzab 2020, PRIDE PXD011929) and
  Leuenberger 2017 both include *S. cerevisiae*. **No *Candida* meltome exists.**
- **Temperature-dependent yeast proteome allocation**: thin. SWATH-MS at non-optimal temperatures
  (Sci Rep 2020) is closest but anaerobic; the 2025 absolute-quantitative atlas (>300 datasets,
  *S. cerevisiae* + *I. orientalis*) is organised by growth rate, not temperature.
- **Candida proteomes across temperature**: essentially nothing systematic. Available datasets are
  host-adaptation and stress studies (PXD074745, PXD074762 for *C. auris*; PXD035231, PXD014125 for
  *C. albicans*), typically two temperatures, not designed for allocation.
- **Worth reading**: *Pervasive Divergence in Protein Thermostability is Mediated by Both Structural
  Changes and Cellular Environments* (MBE 2025, 42:7 msaf137). If measured thermostability
  divergence is partly environmental rather than sequence-encoded, sequence-based Tm prediction has
  a ceiling no better model can cross — independent support for looking outside the enzyme layer.

---

## 8. ACTION POINTS

**A1 — Calibrate the sequence predictors against a known truth.** *(highest value; the Seq2Tm half
needs no new data)* Three predictors supply every species-specific input the etcGEM has: **Seq2Tm**
(stability), **Seq2Topt** (kinetic optimum) and **DLKcat/DLTKcat** (turnover). The same doubt applies
to all three — how much interspecies variance does each actually produce, and is that variance real
or compressed? Ask it as one question, in three parts.

*(i) The benchmark.* Run each predictor on the *S. cerevisiae* / *S. uvarum* proteomes, pair
orthologs, and compare the predicted paired difference with measured truth. For Tm the truth is
known: 1.6 °C across 827 proteins, for a pair 8 °C apart in growth limit. If Seq2Tm returns ~1.5 °C
it is not compressing and Ilgaz's 0.52 °C is real; if it returns ~0.2 °C, compression is ~8× and the
true Candida separation may be ~4 °C — still an order of magnitude short of 33 °C, but the claim
changes from "the difference does not exist" to "the predictor cannot see it, and even corrected it
is far too small". That converts an unbounded claim into a bounded one. Both proteomes are public
and Seq2Tm is already installed.

*(ii) The spread.* For each predictor, report the interspecies spread it produces across the four
Candida species, so the three channels can be compared on one scale.

*(iii) DLTKcat, run here rather than bolted onto K2.* **Deliberately excluded from K2**, for three
reasons worth recording. It improves the *wrong half of the curve*: it predicts kcat(T), and the
E. coli decomposition puts the cold-side limb and E_a under kinetics while T_opt and CT_max are
owned by stability (φ ≈ 0.99) — the Candida divergence is entirely at the upper limit, which
DLTKcat does not touch. It would *break K2's ladder*, because it changes input data rather than
model structure, so movement would no longer be attributable to a single component. And it is
expensive: external weights, substrate SMILES, and an enzyme × substrate × temperature grid of order
50,000+ predictions across four proteomes. Note what is actually lost meanwhile: E. coli uses
`dcp_from: prior` with `dltkcat_fits` as an **overlay where fits exist**, so the shared literature
prior is the base case in both organisms and Candida is missing a refinement, not a mechanism.

Run this prompt AFTER K2. By then it is known whether the thermal form matters, and DLTKcat gets
run with a benchmark attached rather than as an unfalsifiable upgrade. Only then decide whether the
overlay is worth adding to the Candida strains permanently.

**A2 — Get the `common_network.py` result on record.** Ilgaz ran the identical-scaffold control; the
number is not in `gem/notes/`. If optima still compress on a common scaffold, network and
reconstruction differences were not the cause and the four species are safe to compare. If they do
not compress, reconstruction depth (662–997 metabolic genes) was confounding the comparison. Either
way it should be a recorded result, and later a framework-level experiment kind rather than a
one-off script.

**A3 — Gene-content screen.** *(cheap, no new data, nobody has done it)* From
`gem/tables/*_evidence.csv`, list metabolic genes present in *C. auris* and absent in the relatives,
and vice versa. Presence/absence is a species difference the model can represent today. Check the
Xiao et al. candidates explicitly — alternative oxidase, GRX5, iron uptake.

**A4 — Add the proteome-sector layer to the Candida strains.** In K2/K3, using literature yeast
values (P_total ≈ 0.45–0.5 g/gDW; sector fractions from the *S. cerevisiae* proteome). Frame as
structural realism, not as a fix for the divergence — E. coli's own experience is that grounding
allocation *cost* fit (R² 0.74 → 0.49) and was kept for proteome realism and attributability. It
makes chaperone burden and a translation cap expressible, neither of which the current model has.

**A5 — Turn NGAM(T) and σ on for Candida under the core.** Both are core features the standalone
model lacks. Report what changes. This is part of putting the four species on the same footing as
the other three, not a separate investigation.

**A6 — Test the unfolding ceiling across all seven strains.** *(the framework-level question)* Once
K1/K2 land, ask systematically: by how much does the unfolding-based CT_max exceed the observed
limit in *E. coli*, *M. maripaludis*, *Synechocystis* and the four *Candida* species? §4 suggests a
consistent over-prediction of +6 to +14 °C. If that holds across seven strains it is a general
statement about the model class, and it is only askable once they share a code base.

**A7 — Add a measured-meltome eukaryote reference strain.** *S. cerevisiae* with Meltome Atlas /
Leuenberger Tm, as the yeast counterpart to *E. coli*'s grounded meltome. It gives a eukaryote whose
stability is measured rather than predicted, which is the control the Candida strains cannot be.

**A8 — Scope the membrane layer.** *(the largest and most speculative)* Representing this properly
means a lipid-composition state variable with a temperature-dependent fluidity target, a remodelling
cost drawn from the same budget, and ideally leak as temperature-dependent NGAM — a modelling
extension, not a parameter change. It also needs measurement to be more than a hypothesis:
lipidomics across temperature on the four species. Worth a scoping note before any code. Ask Ilgaz
first whether any of the 25 audits touched lipid pathways (`allocation_and_trehalose.py` suggests
compatible solutes were looked at).

**A9 — Ask Ilgaz two direct questions.** Whether `common_network.py`'s optima compressed (A2), and
whether anything in the audits covered lipid or membrane pathways (A8). Both are faster asked than
reconstructed from the repository.

---

## 9. Sequencing

    K1  port the four species onto the core (DONE - 57/57, mu to 0.000000 h^-1)
    K2  the core's thermal layer, one component per rung (prompt written)
    A1  predictor calibration: Seq2Tm, Seq2Topt, DLTKcat against the S. cerevisiae/S. uvarum
        benchmark - run AFTER K2, when it is known whether the form matters
    A3  gene-content screen (cheap, independent of the above, can run any time)
    K3  retire the fork; audits and notes into reports/candida_thermal_limit/

A2 and A9 are questions for Ilgaz, not work. A6 falls out of K2 PART C2. A4, A5 and A7 are rungs or
strains added under K2/K3. A8 (the membrane layer) is a scoping note, not yet a prompt.

One caveat carried forward from the K1 result: the two draft models (*C. haemulonii*,
*C. duobushaemulonii*) are the *C. auris* network with genes reassigned by RBH — 2,863 reactions and
~1,312 costed in all three, differing by 2-4 reactions. So network differences cannot explain their
Fig 4 behaviour (good for the conclusion), but neither can they be tested there, and the
common-network control (A2) is close to a no-op for those two. Only *C. parapsilosis*, with an
independently curated model (2,162 reactions, 1,606 costed), can show a network effect at all.
