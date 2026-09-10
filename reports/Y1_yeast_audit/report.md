# Y1 — does the defect class we found exist in the published yeast etcGEM?

> **Dated note, 2026-09-10 (P12): PART C's asymmetry stands. One inference drawn from this
> report's precedent is withdrawn. No number below is edited.**
>
> Y1's four verdicts are untouched by P12 — the coupling-ion audit still does not fire on Li et
> al. 2021, and the T_opt/CT_max asymmetry still reproduces independently in their model with their
> own `etcpy`.
>
> The withdrawal concerns **Pettersen & Almaas 2023**, the follow-up to this paper, which found Li
> et al.'s posterior **multimodal and seed-unstable across 2,292 per-enzyme parameters**. That was
> taken as the precedent explaining P11's seed disagreement in our own 16-parameter reformulation,
> and recorded in OPEN_ITEMS §0c as "the multimodality is in the thermal formulation, not the
> parameter count". **P12 mapped our basins directly and does not reproduce it**: one live basin,
> the two runs' best samples 0.266 apart, and the single separated basin populated only by models
> with zero predicted growth. The precedent is real for *their* model; it is not evidence about
> ours, and the generalisation is withdrawn.
>
> Their *method* does carry over and was used here (barrier and FVA tests on equally-fit points,
> hierarchical clustering of endpoints). Their *cost* finding does not: their 8.5× speedup came
> from replacing COBRApy because **80 % of their time was model preparation**, whereas in this
> model **92 % is LP solving and 8 % preparation**, so the same change could buy at most 8 %.


**Li G., Hu Y., Zrimec J., Luo H., Wang H., Zelezniak A., Ji B., Nielsen J. (2021)
*Bayesian genome scale modelling identifies thermal determinants of yeast metabolism.*
Nature Communications 12:190.** Code and models: `SysBioChalmers/BayesianGEM` at `a68307e`,
GPL-3.0.

*The register throughout: we developed an audit and applied it to the reference implementation.
Nothing here is a criticism of their paper, and the one error found in this exercise was in our
own tooling.*

| part | question | answer |
|---|---|---|
| **A** | can their model be loaded, solved, run? | **yes, all three** — and their thermal layer is Python, not MATLAB |
| **B** | is the uncosted coupling-ion defect present? | **no** — four independent checks |
| **C** | does the T_opt / CT_max asymmetry hold in their model? | **yes** — 10.1 °C against 0.8 °C |
| **D** | did their calibration pull stability down, as ours did? | **no** — it moved Topt and left Tm at the meltome |

Detail: `task_a_load.md`, `task_b_audit.md`, `task_c_regime.md`, `task_d_calibration_shift.md`.
Provenance: `SOURCE.md`. Every judgement call: `DECISIONS.md`.

---

## The thing that had to be fixed first

The first run of our audit on their model reported **no ATP synthase and zero hits in classes
A–D, on 6743 reactions**. That was our bug, not their model. Every pattern in
`src/etcgem/sink_audit.py` is anchored at `^` and was matched against the metabolite id and the
joined `"id name"`; BiGG and ModelSEED put the chemistry in the id (`atp_c`), Yeast7 puts an
opaque id beside a plain name (`s_0437` / `ATP`), and an anchored pattern cannot match the joined
string from the left. The audit recognised no ATP, no NADH and no O₂ in a model with an intact
respiratory chain.

It is worth stating plainly because of what it would have produced: **a clean bill of health for
the wrong reason**, which is indistinguishable from a result. The matcher was fixed and proved
inert on the seven strains before being used — every numeric cell of K5's class-E budget identical
to 0.0, and every class A–D count identical to the committed table (`DECISIONS.md` §3,
`task0_*`).

## A — what was obtained, and what it can do

`SysBioChalmers/BayesianGEM` at `a68307e` (2020-11-22), GPL-3.0. Three deposited `.mat` models,
their thermal layer `code/etcpy`, and the prior thermal parameters for all 764 enzymes.

**Their thermal layer is Python, not MATLAB.** `etcpy/etc.py` operates directly on a cobra model.
That single fact is why Y1 cost an afternoon rather than a project: no MATLAB environment was
needed, and PARTS B and C could both be done *with their code on their model*.

Two obstacles, both resolved and both recorded. The deposited cobra-0.15.3 pickles do not unpickle
under cobra 0.31; their `.mat` twins were used instead, after two attempts, per the prompt's cap
on format archaeology. The `.mat` files need a field trim because several GECKO annotation arrays
are sized to a subset of the model; the trim is **verified against the raw MATLAB struct** — ids
identical, `lb`/`ub`/`c` max abs difference **0.0**, `S` non-zeros equal, on all three models.

All three solve. `etc.simulate_growth` runs and gives a sensible curve (T_opt ≈ 32.5 °C, collapse
by 45 °C at their σ = 0.5). `etc.simulate_chomostat` runs, and the in-place version used for the
audit reproduces its objective to **|diff| = 0.000e+00**. One compatibility shim was needed, on
the order in which `set_NGAMT` sets a pinned bound; it changes no value.

## B — the coupling-ion audit does not fire

The ion and the energised compartment were **inferred from their model's own ATP synthase**, as K5
did for the methanogen: **H⁺**, energised side the **cytosol**, ATP synthase **`r_0226No1`**
(`ADP[m] + 3 H⁺[c] + Pi[m] → ATP[m] + 2 H⁺[m] + H₂O[m]`). A name-based search would have missed
it — searching this model for "ATP synthase" returns only the cytosolic V-ATPases.

**The budget.** At the two states where ATP synthase carries flux, the respiratory chain supplies
**92.74 %** (pristine deposited batch model) and **93.15 %** (chemostat, via their own
`simulate_chomostat`) of the protons it consumes. The other three states are fermentative — on
unlimited glucose under a protein cap the model does what the Crabtree effect says, ATP synthase
carries nothing, and the budget is 0/0.

Against K5's seven strains: E. coli 123.7 %, *M. maripaludis* 104.7 %, *C. parapsilosis* 112.0 %,
*Synechocystis* 100 % once in-lumen chemistry is counted — and the three Candida models K4 found
broken, **0.04–0.05 %**. Yeast sits with the healthy models, four orders of magnitude from the
broken ones.

**K5's criterion, restated for GECKO.** GECKO writes every reaction irreversibly and supplies a
`_REV` twin, so `lb < 0 < ub` is false by construction — in ecYeast7, in eciML1515, in all of
them. Applied literally the criterion returns "clean" for a structural reason. The meaningful form
is *uncosted with an uncosted `_REV` twin*. On that reading: fifteen reactions move a proton across
the mitochondrial membrane, **twelve are uncosted, all twelve run the dissipative way (cytosol →
mitochondrion), and none has a reverse twin**. The model does contain 98 free reversible proton
movers — plasma-membrane symporters and H⁺ diffusion to the ER, Golgi, peroxisome, nucleus,
vacuole — and **not one touches the mitochondrial membrane**.

**And no free path of any length.** A pairwise census is not sufficient here: the model has a
separate `mm` compartment and a free reversible `m`/`mm` proton pair, so two steps in series could
bypass the chain invisibly. Posed as reachability on a directed compartment graph over uncosted
proton-moving edges: **no path `m → c` at any length.** The only route is the costed chain. The
dissipative direction `c → m` is freely available, as it should be.

**The three required verifications, reported although it did not fire.**
1. *Pristine.* Reproduced on the deposited `.mat` files with nothing altered; the load is verified
   exact against the raw struct.
2. *Meaningful flux.* The uncosted movers that carry flux all run dissipatively (5.88, 0.36, 0.02).
   There is no latent hazard to describe either, because no free route exists even unused.
3. *Their code.* Diffing the model across `map_fNT`, `map_kcatT`, `set_NGAMT`, `set_sigma`: their
   layer changes **3925 of 6743 reactions but only two bounds** — `NGAM` and `prot_pool_exchange`
   — and **bounds no transporter**. Nothing is constrained that our loading path missed.

**Two stress tests.** Blocking the costed chain makes the chemostat infeasible; with growth free,
the residual ATP synthase flux is supported entirely by *costed* cytosolic chemistry, with redox
and carrier translocation both **exactly 0**. And with every exchange shut and maintenance
released, maximum ATP synthase flux and maximum ATP hydrolysis are both **exactly 0** — no
energy-generating cycle.

Classes A–D, for completeness: **53 / 0 / 1 / 13**. The largest class-A count in the family sits on
the soundest coupling circuit — which is the point K5 made when it wrote class E.

## C — the T_opt / CT_max asymmetry does hold

Run with `etc.simulate_growth`, on their model, at their prior parameters.

Scaling the enzyme budget with **their own σ** — a capacity cut that does not change which
constraint binds — drops µ_max 5.7-fold and moves **T_opt 2.04 °C and CT_max 1.97 °C**; both
numbers carried by the single near-collapse setting σ = 0.1 (over σ 0.5 → 0.2 it is 1.16 °C and
0.25 °C).

Capping glucose uptake — which **substitutes a substrate limit for the enzyme limit** — drops
µ_max only 3.5-fold but moves **T_opt 10.09 °C while CT_max moves 0.81 °C**. CT_max sits at
45.9–46.7 °C through every setting.

What the substrate cap actually does is **flatten the top of the curve**: the 99 % plateau widens
from 2.5 °C to 7.0 °C, and at the tightest cap growth reads 0.0931 / 0.0968 / 0.0965 at 20 / 22 /
26 °C. So the finding is not "T_opt moves to 21 °C" — that number is the argmax of a near-tie and
is quoted as one. It is that **a substrate-limited regime removes the sharply-defined optimum
altogether, while leaving the upper thermal limit where it was.**

> **Note added 2026-09-09 (Y2).** PARTS C and D above ran at Li *et al.*'s **prior** parameters;
> the test has since been repeated at their calibrated posterior, over their own 100 posterior
> models. See `reports/Y2_regime_posterior/report.md`. Nothing above is edited, and three things
> there qualify it. (i) The prior run reproduces exactly — byte-identically, and again through an
> independent code path. (ii) The **10.09 / 0.81 °C** pair is a property of the prior *point*
> table: at the posterior it is 8.46 / 4.27 °C, because CT_max is no longer regime-insensitive
> there. Over the ensemble the effect is nonetheless far more consistent at the posterior — the
> plateau widens under the substrate cap in **93 %** of posterior models against 35 % of prior
> models, and T_opt moves further than CT_max in **92 %** against 50 %. (iii) With the posterior
> file in hand the signed shift PART D could not measure is measurable: Tm moved **+1.33 °C** on
> average across 764 enzymes while Topt moved **−6.32 °C**, but seven of the nine limit-setting
> enzymes moved *down* in Tm (ERG1 by 3.7 °C), and only three of those nine were below 42 °C in
> the prior — so the sentence below about seven against nine is true but reads as a continuity
> there is not.

## D — their calibration did not pull stability down

Their priors: **Tm** measured for 266 of 764 enzymes from the yeast meltome, the rest assigned the
population mean 51.9 °C; **Topt predicted from sequence for all 764** by Tome v1.0, carried as
N(Topt, **13.0 °C**) — the RMSE implied by that method's R² = 0.5.

That is worth a correction to how this task was framed: their Topt **is** a sequence prediction.
But the way they used it answers our Seq2Tm concern rather than instancing it — predictor as a
wide prior with its own error as the prior width, never as a measurement.

What the calibration moved was **Topt**: significant variance reduction in 59 % (449/764) and mean
change in 26 % (200/764) of enzymes (Fig. 2e), the largest contribution to posterior performance of
the three parameter categories (Fig. 2f), average SD 10.9 → 7.1 °C against 4.9 → 4.0 °C for Tm
(Supplementary Fig. 7). Their own sentence: *"the approach tended to change the enzyme Topt rather
than its Tm and ΔCp‡"*.

What it did **not** move was **Tm**: posterior against experimental gives Pearson **r = 0.97,
p < 1e−32** (Fig. 2g), against r = 0.49, p = 0.075 for Topt against BRENDA (Fig. 2h). And the nine
enzymes that carry their mechanism at the growth limit — ERG1, ATP1, ALA1, KRS1, SER1, HEM1, PDB1,
ADH1, TRP3 (Supplementary Fig. 8) — **all nine already had a measured prior Tm between 40.5 and
43.8 °C**, ERG1 lowest but one in the entire model at 40.46 °C. Seven enzymes were below 42 °C in
the prior against nine in the posterior.

So this is **not** independent support for a common over-prediction of stability. Our E. coli
needed ΔTm = −5.6 K against a measured meltome; theirs needed nothing. What *is* common is the
**tension**: both studies state that measured melting temperatures sit too high to explain where
growth stops — theirs in as many words, *"protein denaturation alone might not be sufficient to
explain the decline of yeast cell growth between 30 °C (OGT) and 42 °C"*. Both resolved it through
whichever term the formulation left free: stability for us, kcat degeneration through MMRT's
negative ΔCp‡ for them (Figs. 3b, 3c, 3e, 3f). Neither result adjudicates which is right.

## What is out of scope, and stays out

**Seq2Tm's within-proteome invalidity does not apply to them.** Their Tm is measured or a
population mean; no predictor. That finding warns anyone building etcGEMs now, ourselves included,
and it is not a criticism of theirs.

**Chain convergence does not transfer.** Different sampler (SMC-ABC), different diagnostics. Our
emcee finding is about our chains and is not restated about their work here.

**Their headline is untouched.** ERG1's flux control at 40 °C (Fig. 5a, 5b) and the *K. marxianus*
orthologue's experimental advantage after two passages (Fig. 5c) rest on flux control and on a
wet-lab validation, not on the coupling circuit — and PART B found that circuit sound in any case.

---

# Verdict

## (b) Absent, but the structural finding holds

**The defect class is not present in the published yeast etcGEM.** The proton circuit is closed
through the respiratory chain (93 % supply at both respiratory states), every uncosted proton mover
on the energised membrane runs the dissipative way, no free path back to the cytosol exists at any
length, and the model has no energy-generating cycle. Verified in the pristine deposit, under their
own thermal layer, by counterfactual and by an exchange-closed ATP test.

**And the T_opt / CT_max asymmetry generalises.** In their model, with their code, a change of
binding constraint moves T_opt 10.1 °C and CT_max 0.8 °C — the asymmetry this project found in four
organisms in its own codebase, reproduced in a fifth in someone else's.

**One half of (b) does not hold.** The calibration shift does *not* generalise: their posterior left
Tm at the measured meltome and moved Topt instead, and the enzymes carrying their thermal limit
were already unstable in the prior. What generalises there is the *tension* that provokes the
shift, not the shift.

*This verdict is (b) and not (a), and the difference matters: the audit was applied to the
reference implementation and the reference implementation passed it.*

## What each verdict would mean for the methods paper

**(a)** would have made the audit itself the contribution — a defect class demonstrated in the
field's reference implementation, with the tooling to find it, and a claim on anyone building an
enzyme-constrained model.

**(b)**, which is what the evidence says, makes the contribution the **structural claim about
constraint regimes** rather than the defect: T_opt is a property of which constraint binds and
CT_max is not, shown now in five organisms across two independent codebases, with the audit as a
method that has been run on eight models and found the reference implementation sound. The
uncosted-shortcut work becomes an account of building models carefully, evidenced by the seven
strains where the audit did fire, and not a claim about the field.

**(c)** would have confined all of it to this group's own model-building — an appendix to the
organism papers.

*No recommendation on whether to write it.*
