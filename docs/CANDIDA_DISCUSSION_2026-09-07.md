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

The reason is in the inputs. Paired across orthologs, *C. auris* enzymes are predicted **0.411 °C**
more heat-stable than *C. haemulonii*'s (the deduplicated value in `FIG4_LOCKED.md`; the 0.52 °C
quoted in correspondence and in earlier drafts of this document is the superseded reaction-level
figure). The fitted model needs about **33 °C**.
A ~79-fold gap on the deduplicated value (~63× as reported at the time). Substituting a *measured*
proteome-wide ΔTm — *S. cerevisiae* vs *S. uvarum*, 1.6 °C across 827 proteins for an 8 °C
difference in growth limit — still leaves ~20-fold.
Concentrating large shifts on ranked bottleneck enzymes does not rescue it (flux reroutes; a beam
search over pairs and triples found nothing crossing detection).

Conclusion as it stands: **within this model class, sequence-predicted enzyme thermal properties
are far too similar between these species to reproduce the observed divergence.**

**Revised twice, by K2 and A1 (2026-09-07).** Both sides of the ratio moved.

| | required | available | fold gap |
|---|---|---|---|
| as published | 32.54 °C | 0.411 °C | **79×** |
| K2: the core's thermal form | 13.77 °C | 0.411 °C | **34×** |
| K2 + A1: compression-corrected | 13.77 °C | 2.56 °C | **5.4× [2.5, 10.3]** |
| **K5: the model repaired so it respires** | **13.57 °C** | 0.411 °C | **33×** |
| **K7: the same, under the OTHER measured growth convention** | **13.57 °C** | 0.411 °C | **33×** |

_Added 2026-09-08 by K9 (`reports/K9_criterion/report.md`)._ **A second criterion was proposed
for this row and it does not work, which is worth recording so it is not proposed again.** Since
the requirement above asks the model to kill a relative below a detection floor at 40 °C, an
apparently gentler alternative is to ask instead what uniform ΔTm would bring each species'
predicted CT_max onto its *observed* thermal limit. That gives about 5 °C of interspecies
difference rather than 13.6, which would put the requirement within roughly threefold of A1's
measured congeneric 1.6 °C — a materially weaker claim than the one this table carries.
**It is arithmetic.** The four models predict near-identical ceilings, so the offset difference
between species is just the difference between their *observed* limits. Tested across five model
states — before and after the K5 proton repair, with and without a carbon cap, and with the
curvature prior at −3 and −6 — the model's own ceiling spread varies **4.5-fold** while the
required-offset spread stays at **6.05–6.45 °C** against an observed limit spread of **6.00 °C**.
A model-derived requirement would move when the model moves; this does not. The **detection**
criterion remains the right one for this table, and K9 recommends quoting it as **13.6 °C, range
11.2–15.8 °C** over interrogation temperatures 38–42 °C, noting that the detection floor is
nearly immaterial (a tenfold change in it moves the requirement by 0.31 °C).

_Added 2026-09-08 by K5 (`reports/K5_respire/report.md`)._ The last row closes a possibility
that was open until it was computed. K4 showed the models had two escape routes — a free proton
circuit, so the respiratory chain carried 0.02–0.05 % of the load, and fermentation with no
carbon budget — and it was reasonable to suspect the 13.8 °C requirement was inflated by them: a
cell that can escape is harder to kill. **It was not.** With the proton circuit closed and a
carbon cap applied, the requirement falls from 13.64 °C to **13.57 °C**, half a percent. The
reason is that the counterfactual shifts *every* enzyme's Tm, so the fermentation and
biosynthetic enzymes denature along with the chain and the escape routes are beside the point at
the shift that kills the cell. The escape routes mattered enormously for a constraint aimed at
respiration — closing them turned K4's "no A_ETC, including zero, changes anything" into a finite
122-fold membrane requirement — and almost not at all here. So this row is not a new estimate;
it is the old one, now known not to be an artefact of two model defects.

_Added 2026-09-08 by K7 (`reports/K7_envelope/task1_convention.md`)._ **A second way the number
could have been an artefact is now also closed.** K6 found the repository holds two conventions
for the measured growth curve — one counting a dead well as an observed zero, one keeping only
survivors — and at 40 °C, the temperature this counterfactual interrogates, *C. haemulonii* grows
at 0.000 h⁻¹ under the first and 0.66 under the second. K7 traced the code rather than reasoning
about it: `required_separation` takes the growth scale as a scalar and **never reads the
predicted strain's measured curve at all**. The only measured input is the PEAK of the *C. auris*
curve, at 36 °C, where *C. auris* is alive under either convention. Recomputed both ways the
requirement is **13.57 °C either way** (13.64 vs 13.71 before the K5 repair). Calibration and
counterfactual read the same file, so the model is not fitted to one curve and falsified against
another.

K2 halved the requirement (the standalone's figure was inflated ~2.4× by its thermal form alone).
A1 then found the *available* side is not a measurement of the proteomes but an artefact of a
predictor with no demonstrated validity in this regime (§3a). Treat the bottom row as the most
generous reading available rather than a point estimate: a 17× correction derived from means, when
per-protein r ≈ 0 and the noise floor throws spuriously significant differences, is soft, and its
lower bound of 2.5× is close enough that model uncertainty could plausibly close it.

**What survives all of this, untouched, is the measured benchmark.** *S. cerevisiae* vs *S. uvarum*:
1.6 °C across 827 proteins, for a pair **8 °C apart in growth limit — further apart than our
species**. Against 13.77 °C that is **8.6×**, and it involves no predictor at all. The defensible
form of the claim therefore inverts the figure's current emphasis: *even a directly measured
proteome-wide ΔTm, from a yeast pair with a larger thermal-limit separation than ours, falls ~9-fold
short of what the model requires.* The sequence-prediction arm becomes supporting texture with a
stated caveat, not the headline. Ilgaz added the measured benchmark to pre-empt exactly this
objection; it turns out to be the load-bearing member.

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

**Two defects K2 found in the standalone, neither of which Ilgaz's audits caught in the model
script.** (i) *C. parapsilosis*'s `ATP_Maintenance__cyto` ships REVERSIBLE at (−3.9, 3.9), so the
solver can synthesise ATP from ADP + Pi. Ilgaz found this in `ngam_falsification.py` and corrected
it there, but the correction never reached `18_build_etcgem_tpc.py`. Uncorrected, *C. parapsilosis*
is **unreachable by any Tm shift** — no finite value crosses detection — and its fit is R² = −0.323,
worse than a flat line. Corrected: 32.64 °C required, R² = +0.042. One of the four species in the
published counterfactual was structurally incapable of being killed by the mechanism under test.
(iii) **A1 found a live reproducibility break**: `15_run_seq2tm.py` truncates sequences at 1022 aa
citing an "ESM2 positional limit" that does not exist (ESM-2 uses rotary embeddings), while the
*committed* predictions are untruncated. The script in the repository does not reproduce the data
beside it, differing by up to 2.6 °C on affected batches. Independent of everything else, and Ilgaz
should be told.
(ii) The pool constraint row spans 8.2×10⁸ at 22 °C, and GLPK makes a ~0.4 % error at the cold end
of the draft models as a result — numerical, not alternate optima, established three ways. A
conditioning problem worth fixing in the framework.

**The general lesson.** Any mechanism whose species-specificity is *sourced from* Seq2Tm/Seq2Topt
is already answered, whatever layer it is routed through. Mechanisms sourced from measurement are
not. (One correction to an earlier over-generalisation: the maintenance falsification is *not* in
this class — it asks what multiplier would be required, against a measured comparator of 1.34×
respiration per unit growth at 40 °C in the relatives versus *auris*.)

## 3. Claims that were being conflated

1. **Within a model, Tm controls the upper limit.** E. coli's variance decomposition gives
   φ_stability = 0.994 for CT_max and 0.999 for T_opt. True.
2. **Between species, Tm is what differs.** False here — 0.411 °C predicted (and see 3a on what
   that number is worth), 1.6 °C even when measured in the *S. cerevisiae*/*S. uvarum* pair.

Both hold at once, and together they are a problem for the model class rather than for Ilgaz's
execution.

**(3a) A third claim, established by A1: the predictor has no per-protein validity in this
regime.** Seq2Tm scored against a measured *S. cerevisiae* meltome gives Pearson **r = −0.048**
(ρ = +0.025, RMSE 7.51 °C, bias +5.43 °C, n = 1947). The same predictor and code across the tree of
life gives **r = +0.762**. So it distinguishes a thermophile's proteins from a mesophile's and
cannot resolve proteins within one organism — which is the regime Figure 4 uses it in. Two
consequences: Fig 4B's overlapping densities may overlap because the predictor cannot resolve rather
than because the proteomes are similar; and the same-species noise floor (four *C. auris* clades,
99.3–100 % identical, true ΔTm ≈ 0) is |mean| 0.043 °C with **five of six clade pairs significantly
non-zero**, so the method manufactures differences where none exist. 0.411 °C is 9.5× that floor —
above it, but the floor should not be non-zero at all.

Note this reframes the earlier "compression" idea recorded under A1: the regression slope of
measured on predicted is **−0.061 ± 0.029**, so there is no scaling factor to divide out, only
absence of signal. (Where the predictor works, across the tree of life, the slope is +1.11 — mild
compression, which is what compression actually looks like.)

**A1's finding now has a measured consequence inside the model (K8, 2026-09-08).** Two of A1's
results were, until now, statements about a predictor rather than about this model's behaviour.
Both now bite. Applying A1's **mean** bias of +5.43 °C closes a third to a half of the Candida
ceiling over-prediction. Applying the **relationship** A1 actually measured — `Tm = 52.60 − 0.061
× Tm_predicted`, which is what "no within-proteome validity" means when written as a correction —
collapses the per-enzyme Tm spread from sd 2.2–2.9 °C to **0.14–0.18 °C** and **improves the fit
to the measured growth curve in all four species** (*C. auris* R² 0.518 → 0.687). A correction
that removes almost all of a distribution's variance and makes the model fit *better* is direct
evidence that the variance was error rather than signal. Detail:
`reports/K8_tm_bias/report.md`.

**The circularity to keep in view.** A variance decomposition can only attribute to mechanisms the
model contains. If two-state unfolding is the only thing that can produce a hot collapse, the
decomposition will assign the collapse to unfolding whether or not that is what kills real cells.
Membrane fluidity, proton leak and ROS receive zero share by construction, not by evidence.

## 4. The unfolding ceiling across seven strains

_Rewritten 2026-09-07 after K2. The earlier version of this section generalised from two organisms
and was wrong; K2 PART C2 measured it properly across all seven strains._

| strain | gap (predicted CT_max − observed limit) |
|---|---|
| *M. maripaludis* | **−0.2 °C** |
| *Synechocystis* | **+1.7 °C** |
| *E. coli* (measured meltome Tm) | **+5.9 °C** |
| the four *Candida* | **+9.6 to +15.8 °C** |

**The over-prediction is not universal.** The archaeon is essentially exact and the cyanobacterium
close; only *E. coli* and the yeasts over-predict, and the yeasts by two to three times as much as
*E. coli*. The earlier claim — that bulk enzyme unfolding sets a systematically-too-high ceiling —
does not survive contact with four organism types.

What remains, and is more specific: **in the two organisms where the ceiling is wrong, it is wrong
in the same direction and by an amount that scales with how badly the model misses the phenotype.**
E. coli's Bayesian calibration independently had to pull Tm down by −5.6 K [−7.2, −2.8] to match the
observed collapse — consistent with its +5.9 °C gap, and with a *measured* meltome, so not a
predictor artefact. Candida needs a larger uniform shift still; under one, *C. auris*'s CT_max lands
on 44.6 °C against ~45 °C observed and the fit rises to R² 0.674.

So the open question is no longer "why is the unfolding ceiling always too high" but **"why is it
right in a methanogen and a cyanobacterium and wrong in a bacterium and four yeasts?"** That is a
sharper question, it is only askable because the seven strains now share a code base, and it should
be resolved before the membrane hypothesis (§6a) is treated as the leading explanation — whatever
explains the pattern must also explain the two organisms where nothing is wrong.

**And the ΔCp prior is not the explanation either (K7, 2026-09-08).** The obvious candidate for
a single cause behind both the over-predicted ceiling and the too-steep rising limb is the shared
MMRT curvature prior, `dcp_prior_kJ = -4.0`. K7 swept it from −1 to −16 kJ/mol/K against a
literature range of −2 to −6. **The two failures are strictly opposed**: the CT_max gap falls
monotonically as ΔCp becomes more negative while the rising-limb activation energy rises
monotonically with it. For *C. auris* the steepness and the fit are both best at −3.0, inside
the range, where the ceiling gap is +9.4 °C; the gap is smallest at −16.0, four times outside the
range, where the fit R² is −4.17. **Within the defensible range ΔCp closes at most about a fifth
of the ceiling error.** So the ceiling and the rising limb are not one failure with one cause,
and the most obvious candidate for making them one is ruled out. Detail:
`reports/K7_envelope/task3_dcp.md`.

**The ceiling numbers do not move under the K5 repair, and one of them now has a mechanism
attached (K5, 2026-09-08).** Closing the free proton circuit lowers predicted growth by 36-38 %
in the three *Candidozyma* but leaves the unfolding CT_max essentially where it was, because
CT_max is read off the falling limb, which the enzyme layer still owns. What *does* move it is
the membrane-area budget once the model can respire under a carbon cap: *C. auris*' CT_max then
falls from 53.0 °C to 36.5 °C across the A_ETC sweep, against 53.6 to 47.0 in K4. So the
over-prediction recorded in this section is not immovable — it is simply not moved by anything
in the enzyme layer. Detail: `reports/K5_respire/task3b_membrane_retest.md`.

**The ~5.6 K "common term" does not generalise, and this section should not be read as claiming
it does (K9, 2026-09-08).** K8 separated the Candida ceiling error into a predictor component and
a residual, and observed that *E. coli* — whose Tm are **measured** — still needs a −5.6 K
correction, suggesting a second, common cause. K9 tested that across every strain where it can be
computed. The residuals after removing A1's measured predictor bias are **0.05 °C**
(*M. maripaludis*), **4.38** (*C. auris*), **5.60** (*E. coli*), **10.08, 10.33, 10.48** (the three
relatives). **There is no constant.** *E. coli*'s 5.6 K is real and unexplained but is a
one-organism observation, and the two strains that might have corroborated it cannot: the
methanogen has no a-priori ceiling at all (its predicted TPC is identically zero until its
calibrated `kcat_scale` is applied), and both it and the phototroph draw their Tm from a
**mesophile prior built on *E. coli*'s own meltome**, so they are not independent evidence about
a term seen in *E. coli*. Separately, *Synechocystis*' committed ceiling of 45.70 °C could not be
reproduced from a plain strain build, which gives 55.50 °C; the committed curve is not truncated
and the medium does not explain it, so that row should be treated as provisional until the
difference is found.

**Part of the over-prediction is a predictor artefact, and it can now be sized (K8, 2026-09-08;
`reports/K8_tm_bias/report.md`).** A1 measured Seq2Tm's bias against a real *S. cerevisiae*
meltome at **+5.43 °C**. Subtracting exactly that from every Candida enzyme's Tm — a test with the
expected shift recorded in advance — moves CT_max by **4.1–5.1 °C** (dCT_max/dTm = 0.75–0.94) and
takes the gaps from +9.0…+15.3 °C to **+4.2…+10.2 °C**, closing a third to a half. *C. auris*
lands **below** *E. coli*'s +5.9. **E_growth and T_opt do not move at all**, so this is the
orthogonal lever K7 showed the curvature prior could not supply.

**But it is not the whole story, and the remainder is the interesting part.** Full closure needs
10 °C for *C. auris* and 15 °C for each relative, 1.8–2.8× the measured bias — and the offsets the
four species need differ by **5 °C**, which no uniform predictor bias can produce, since a
predictor bias is common to all four by construction. Meanwhile *E. coli*'s own tuned row in the
table above already records a **−5.6 K** correction to a **measured** meltome, which cannot be
predictor bias at all. **So the ceiling has at least two components** — a common ≈5.6 K term and a
Candida-only ≈5.4 K predictor term, summing to ≈11 K against *C. auris*' required 10 — and a
species-specific residual of about 4 °C in the relatives, which is the divergence this document
exists to explain. Note also that *M. maripaludis* and *Synechocystis* take Tm from a **mesophile
prior built on E. coli's measured meltome**, not from Seq2Tm, which is consistent with their
near-zero gaps but is weak evidence: their median Tm are higher than Candida's, and the methanogen
runs at a calibrated `kcat_scale`.

_Checked against the flatness guard (N2). N1's guard fires wherever proteome sectors run
without temperature-dependent allocation, which is true of the Candida B4 rung, of
M. maripaludis and of Synechocystis — so it is fair to ask whether the table above is reading
descriptors off flat-topped curves. It is not: CT_max is read off the falling limb, which the
flat top does not touch; M. maripaludis reports NaN because its a-priori curve is identically
zero and its analyses run at the calibrated operating point where the metabolic pool binds;
and Synechocystis' plateau is 2.0 °C at the 1% level and 0.0 at 0.01%, i.e. a genuine peak.
The table survives. Detail:_ `reports/candida_thermal_limit/K2_core_thermal_form.md` §C2.

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
predicted ΔTm of 0.411 °C. That was posed here as an either/or — thermostability is that conserved,
or the predictor cannot see the substitutions that matter. **A1 answered it: the predictor cannot
see them** (§3a). Whether thermostability is *also* conserved remains unknown, and now needs
measurement rather than prediction.

**MEASURED (A3, N1): the models see about 2–5 % of the gene-content difference.** This section
inferred a coverage problem from proteome sizes; A3 measured it directly, by aligning all four
proteomes against each other and crossing the result with model membership.

| | proteome level | of which in a metabolic model |
|---|---|---|
| genes present in one species, absent from another (no hit at e < 1e-3) | **122–647** per comparison | **0–15** |

Concretely, *C. auris* against *C. haemulonii*: 209 genes absent at e < 1e-10, of which **four**
are in a model — protoheme IX farnesyltransferase, Dpm2p, an uncharacterised protein and cytidine
deaminase. Against *C. duobushaemulonii* it is seven of 244. Gene content differs by 2.4–3.8 % in
each direction within the *Candidozyma* clade and 8.5–11.2 % against *C. parapsilosis*; **almost
none of it is inside the models.**

Two methodological caveats make that trustworthy rather than merely striking, and both were
corrections to the obvious method. **RBH-absence over-states true absence more than threefold** —
569 genes lack a reciprocal best hit for *C. auris* against *C. haemulonii*, and 172 lack any hit
at all — which matters because RBH is the pairing the rest of this project uses. And **a
description-only search for a named gene is not a presence/absence test**: it missed alternative
oxidase in *C. haemulonii*, where alignment finds one at 86.4 % identity, and returned nothing at
all in *C. parapsilosis*, whose model namespace carries no description field. A3 therefore finds
candidates by description and decides presence by alignment. Full method and lists:
`reports/N1_overnight/A3_gene_content.md`.

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

**TESTED, in the only form currently available (K4, 2026-09-08;
`reports/K4_membrane/report.md`). The membrane-AREA half of this axis has now been carried to
the four Candida strains, and it is available rather than tested — for a reason that was not
anticipated here.** P1's table-driven ETC area budget, gated on *E. coli* by P3, applies to
these models without a code change, and the complex footprints turned out to be better sourced
than expected: derived from solved fungal structures (*Yarrowia lipolytica* complex I,
*S. cerevisiae* complexes II–V) rather than transferred from *E. coli*. But **in the three
*Candidozyma* models the respiratory chain supplies 0.03 % of the protons ATP synthase
consumes**, because eleven uncosted, reversible metabolite/H⁺ symporters close the proton
circuit outside it — a defect in the published iRV973, not in the port. Constraining complexes
I–IV all the way to zero area changes growth at 40 °C by 0.0000 h⁻¹ in *C. auris*; ATP synthase
takes 99.6–99.99 % of the area budget. Only *C. parapsilosis*, independently curated and the
outgroup, has a chain the constraint can bind on (it costs 52 % of growth there). Two further
findings bear directly on this section: **no footprint or turnover differs between the four
species, because none has been measured for any *Candida***, so the parameters are as
undifferentiated as Seq2Tm's were; and **per gram dry weight, mitochondrial cristae give yeast
no more bioenergetic membrane than *E. coli* has** (~2.4 × 10¹⁸ vs 4.3 × 10¹⁸ nm²/gDW), so the
"cristae give a much larger area" intuition is about area per cell volume, not per unit
biomass. A first-principles yeast budget sits ~9× above the point where it would bind.
Unlike the Tm route, which fails quantitatively by 26×, this one fails structurally: **no value
of A_ETC, including zero, puts any relative below detection at 40 °C**, and tightening the
budget hurts *C. auris* most — the wrong direction. What would change this is listed at
`docs/OPEN_ITEMS.md` §3.8–3.12, and the cheapest item, repairing the proton accounting, needs
no new data at all. Note this leaves the LIPID half of §6(a) entirely untouched: an area budget
has no lipid term, and lipidomics bears on A8's fluidity-and-leak extension rather than on this.

**(b) Proteome allocation, with measured sector fractions — and a warning from K2.** K2 rung B4
enabled sectors with literature yeast fractions, identical across species, and the result was worse
than inert: the **temperature-independent translation cap removes the optimum rather than shifting
it**, leaving a flat curve, so T_opt becomes the argmax of a tie and any apparent species ordering
is an ordering of plateau heights. Fit fell from R² 0.254 to 0.111 (E. coli's ablation, for
comparison, was 0.74 → 0.49). **Sectors should not be a Candida default until measured
temperature-dependent allocation exists.** Worth establishing whether E. coli escapes this only
because `allocation_from_data` makes its cap temperature-dependent — if so, that is a framework-level
precondition for enabling the sector layer at all, not a Candida quirk.

The original point stands otherwise: E. coli's model carries measured,
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

**(e) Gene content.** Presence/absence is genuinely species-specific and needs no new data.
**Looked at now (A3, N1; `reports/N1_overnight/A3_gene_content.md`), and the result narrows the
axis rather than opening it.**

All four Xiao et al. candidates that could be located — alternative oxidase, the GRX5-family
glutaredoxins, the FRE-like ferric reductases and the FET3-like ferroxidases — are **present in all
four species**, by alignment. None of them distinguishes the species by presence/absence. And
**alternative oxidase and the glutaredoxins are in no metabolic model at all**; the ferric
reductases are in one (iDC1003).

So that proposed mechanism is untestable in this framework as it stands, **on two separate
grounds**: the genes do not differ between the species in the way presence/absence could express,
and the two most-cited of them are not in any model, so the models could not express them even if
they did. That is a **scope limit of these reconstructions**, not a refutation of Xiao et al. — a
gene being present says nothing about whether it is expressed, when, or at what level, and the
mechanism they propose is regulatory rather than combinatorial. Testing it would need the enzymes
in the models and expression data, neither of which exists here.

(FTR1 and SIT1 orthologues could not be assessed at all: no protein in any of the four RefSeq
proteomes carries a matching description, so there was nothing to align. That is a missing
annotation, not an absence.)

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

**A1 — Calibrate the sequence predictors against measured truth. — RUN 2026-09-07.**
Three predictors supply every species-specific input the etcGEM has: **Seq2Tm** (stability),
**Seq2Topt** (kinetic optimum) and **DLKcat/DLTKcat** (turnover). A1 asked of each: how much
interspecies variance does it produce, and is that variance real? It was written expecting a
*compression factor* to divide out. That framing turned out to be wrong — see the outcome, and §3a.

**OUTCOME (2026-09-07, `reports/predictor_calibration/report.md`).** Done for Seq2Tm and Seq2Topt;
DLTKcat scoped and recommended against for now (A1 PART G). Against 1949 MEASURED
*S. cerevisiae* melting points, **Seq2Tm's within-proteome correlation is r = -0.05** — while the
same code on a cross-species Meltome Atlas sample gets **r = +0.76**, so the predictor resolves
thermophily between organisms and not variation within a proteome. It under-states the one
checkable congeneric difference (*S. cerevisiae* vs *S. uvarum*, measured 1.6 °C) **17-fold**, and
it returns significant ΔTm of up to 0.078 °C between *C. auris* clades that are 99.3-100% identical
— a floor the Figure 4 estimate exceeds by only 3.5-9.5×. For **Seq2Topt** the *C. auris* vs
*C. haemulonii*/*C. duobushaemulonii* separations are not distinguishable from zero **or from that
floor**. Correcting Figure 4's arithmetic for K2's requirement (13.8 °C, not 33) and A1's measured
17× compression takes the fold gap from ~79× to **5.4× [2.5, 10.3]** — still a failure, and a
materially different sentence. Two corrections to numbers used above: §1's **0.52 °C is the
superseded reaction-level value**; the project's own deduplicated figure is 0.411 °C, and A1's
proteome-wide equivalent is 0.151 °C. A1 reports numbers and adjudicates no mechanism.

**A2 — Get the `common_network.py` result on record.** Ilgaz ran the identical-scaffold control; the
number is not in `gem/notes/`. If optima still compress on a common scaffold, network and
reconstruction differences were not the cause and the four species are safe to compare. If they do
not compress, reconstruction depth (662–997 metabolic genes) was confounding the comparison. Either
way it should be a recorded result, and later a framework-level experiment kind rather than a
one-off script.

**A3 — Gene-content screen. DONE** (N1 TASK 1; `reports/N1_overnight/A3_gene_content.md`).
Proteome-level orthology across all four species by alignment, with absence graded at three
thresholds, crossed with model membership. **The models see about 2–5 % of the gene-content
difference** — 0–15 genes per comparison against 122–647 in the proteome (§5) — and **all four
locatable Xiao et al. candidates are present in all four species, with alternative oxidase and the
glutaredoxins in no model** (§6e). Reported without adjudicating mechanism.

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
    K2  the core's thermal layer, one component per rung (DONE - gate now 79/79; required
        separation 32.5 -> 13.8 C; ceiling measured on all seven strains; sink audit added)
    A1  predictor calibration (DONE - Seq2Tm has no per-protein validity in this regime; the
        MEASURED benchmark is now the load-bearing evidence; DLTKcat recommended against)
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

**Added after K2, not yet action points.** Three items fell out of the K2 report and need a home:
the pool-row conditioning problem (spans 8.2x10^8 at 22 C; causes a ~0.4% GLPK error at the cold end
of the draft models) should be fixed in the framework rather than pinned around; the sector
translation cap needs to be temperature-dependent before sectors are enabled anywhere without
measured allocation (SS6b); and the emergent Candida model under-predicts C. auris growth by 7.6x
against E. coli's ~2.3x, with R^2 0.205 - a grounded eukaryote budget that binds far too tightly,
which is a finding about the framework's transferability to eukaryotes rather than about Candida.

**Left open by A1.** The measured benchmark is now the load-bearing evidence (SS1) and it rests on a
single yeast pair from the literature, published as a summary statistic only - which is why A1's
paired test is summary-to-summary and the strongest form (correlation of measured against predicted
DIFFERENCES) could not be run. Two things would strengthen it: obtaining the per-protein
S. cerevisiae/S. uvarum data from the authors, and a measured meltome for any Candida, which does
not exist (SS7). Neither is scheduled.
