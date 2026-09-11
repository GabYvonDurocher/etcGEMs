# E2 — decisions and judgement calls

Kept from the first judgement call.

---

## D0. **E1 has not been run, and this deck's inputs were rebuilt from primary sources**

The prompt says "Run this AFTER E1 finishes … E1's `brief.md` and `corrections.csv` are inputs
here", and lists `reports/E1_paper_register/` under "read first". **That directory does not exist**
— not on `main`, not on any branch, and not anywhere in the history (`git log --all
--diff-filter=A --name-only` finds no `E1_`, `paper_register`, `brief.md` or matching
`corrections.csv`). There is no `e1/*` branch on the remote and no commit prefixed "E1:". Only the
prompt `prompts/E1_ecoli_paper_restructure_register_prompt.md` exists.

**Decision: proceed, and rebuild the two things E2 actually needs from primary sources rather than
wait or guess.** E2 uses E1 for exactly two purposes, and both are obtainable directly:

* **The UNSUPPORTED status of the old E. coli intervals.** E1's own prompt states the basis:
  `tbl-corrections` and every 90 % CI in the calibration section come from the "P2 v3 posterior",
  and P8, P11 and P12 established that intervals from this family's emcee chains are not
  available. That is verifiable here without E1 — `reports/ecoli_gasflux/README.md`'s standing
  banner and `docs/OPEN_ITEMS.md` 1.12 say the same thing in the repository's own words, and
  `reports/P12_modes/` shows the mode structure that makes a single interval meaningless. **No
  interval from that family reaches a slide.**
* **The gas-flux inventory.** `reports/ecoli_gasflux/README.md` (118 lines) and its fourteen
  committed figures are the source E1 would itself have read.

**What is therefore NOT in this deck, and would have been:** E1's sentence-by-sentence correction
register, and its restructure options for `report.qmd`. The deck presents the state of the science;
it makes no claim about how the paper should be reorganised, because the run that was to establish
that has not happened. Recorded in `docs/OPEN_ITEMS.md`.

## D1. The MRes baseline, from the thesis rather than from assumption

Madkaikar A. (2023), *Predicting the thermal niche of a ubiquitous bacterium using whole genome
sequence*, MRes Computational Methods in Ecology and Evolution, Imperial College London;
supervisor Samraat Pawar. Read from `refs/Madkaikar_CMEE_MRes_02299268.pdf`.

**What the model was:**

* **Reconstruction: `iJO1366`**, enzyme-constrained with **GECKO 3 in MATLAB**; enzyme information
  queried from KEGG. **1 366–1 367 enzymes.**
* **Thermal layer: the same physics this project uses** — two-state denaturation with
  ΔGu(Tm) = 0, kcat from transition-state theory with a heat-capacity change ΔCp‡, and a
  temperature-dependent NGAM. FBA at each temperature over **8–48 °C**.
* **Parameters: 4 101** — Topt, Tm and ΔCp‡ for each of 1 367 enzymes.
* **Parameter sources:** Tm measured for **841 of 1 366**, the rest set to the measured mean
  **55.57 °C** with the empirical SD as uncertainty; Topt from **Li & Engqvist (2019)** for
  **894 of 1 366**, the rest initially 37 °C.
* **Calibration: not Bayesian.** Repeated FBA with each parameter class varied, scored by R² and
  MSE against one growth TPC and the estimates updated — a hand-rolled tuning loop, described in
  its Supplementary Information.
* **Data: growth TPCs only.** Trained on **one** curve (Mohr & Krawiec 1980, 20–48 °C) chosen from
  Smith et al. (2019)'s database; **validated against the other 25** *E. coli* curves in it.
* **Media:** minimal and LB explored, crossed with changed enzyme-availability bounds.
* **Result: R² = 0.94** on the growth TPC, with a steep decline above 46.5 °C.
* **No gas exchange, no respirometry, no acetate, no O₂.**

**Two places where the thesis does not match what this prompt assumes, and the thesis wins.**

1. **The reconstruction was replaced, not extended.** The baseline is `iJO1366`; this project's
   *E. coli* strain is **`eciML1515`**. "What we added" is therefore not a continuous extension of
   the MRes model — the GEM underneath it changed, and the MATLAB/GECKO pipeline became a Python
   core. The deck says this plainly rather than implying continuity.
2. **The baseline already had per-enzyme thermal parameters — 4 101 of them, more than Li's
   2 292.** So the honest framing of this project's sixteen global levers is **a deliberate
   reduction**, not a shortfall in resolution: the MRes had per-enzyme parameters and no way to
   constrain them, and the project traded them for a small identifiable set plus data that can
   constrain it. Any slide that framed "16 vs 2 292" as *coarseness* would be misleading, and Y3's
   result is what makes the trade defensible.

## D2. Pettersen & Almaas 2023 — the three things this deck uses them for

Read from `refs/PettersenAlmaas_2023.pdf` (*Sci Rep*, `@Pettersen2023`).

1. **The Bayesian method is unstable and does not estimate the posterior.** Their abstract:
   *"the Bayesian calculation method for inferring parameters for an etcGEM is unstable and unable
   to estimate the posterior distribution. The Bayesian calculation method assumes that the
   posterior distribution is unimodal, and thus fails due to the multimodality of the problem."*
   They replace it with an evolutionary algorithm to recover a diversity of solutions.
2. **The FVA result, and it is specifically the oxygen-consuming reaction.** Of six signature
   reactions, *"Ferrocytochrome-c:oxygen oxidoreductase are for some particles used extensively,
   but in other cases not at all, still giving rise to approximately the same growth rates
   regardless"* — the O₂-consuming step of the respiratory chain is the one that varies most
   between equally-fit particles. Two of the six barely varied; the rest *"displayed huge variation
   in flux-carrying capacity"*.
3. **What they say is needed.** *"the main source for the lack of identifiability is a result of
   the external measurements being insufficient … we believe that measurements of proteomics and
   fluxomics will help narrow down the solution space"*, and *"Given new measurements of fluxes
   where there currently is high variability … fewer particles would be supported by the
   experimental data."*

**Why this is a precise match and not a loose one.** The reaction they name as most
under-determined is the oxygen-consuming step of the respiratory chain, and the data they ask for
is a **measured flux**. Parsa's respirometry is a measured O₂ flux over a temperature series in
three media. The deck sets the two against each other directly, in their words.

## D3. Every gas-flux number on a slide is labelled mechanism or interval

`reports/ecoli_gasflux/README.md` opens with a standing banner: none of its R² values is a
converged posterior — Parsa's six chains and P4's nine refits all ran ~9 autocorrelation times
against a ≥ 40 criterion, so every R² in that family is a point estimate (MAP or median) from an
unconverged chain, *indicative and not validated model performance*. The gate remains valid as a
**port check** — it reproduces his computation to within 0.009 — which is a different claim.

**Decision: gas-flux slides carry the mechanism and say so on the slide; where a fit quality is
mentioned at all it is labelled an unconverged point estimate, and no interval is given.**

## D4. The figure inventory, and the seven figures that cannot be used at all

`figure_inventory.csv`: 54 candidates — 33 in `reports/ecoli_tpc/assets/figures/`, 14 in
`reports/ecoli_gasflux/assets/figures/`, 5 elsewhere, 2 new here. **26 AS IS, 21 WITH A CAVEAT,
7 NOT USABLE.** Ten are used.

**A correction to the prompt's count.** It says `reports/ecoli_tpc/` holds "66 committed figures".
It holds **33 figures and 33 tables** under `assets/` — 66 assets. Nothing turns on it; recorded so
the next reader is not looking for thirty figures that do not exist.

**The seven NOT USABLE, and the reason is the same for five of them: the unsupported interval is
drawn INSIDE the image, where no slide caveat can reach it.** `prior_vs_posterior_tpc.png` carries
a 90 % posterior band; the three `elasticity_tornado*.png` carry 90 % CI whiskers over posterior
draws; `calibrated_ensemble.png` is an ensemble over those draws. `corner_v3.png` is the old
posterior in its entirety. That is why the elasticity result reaches slide 7 as
`elasticity_heatmap.png` — the same finding, computed deterministically at the tuned point, with no
interval in it. The seventh, `requirement_arithmetic.png`, is Candida and Y3 forbids reading it
across.

**Every gas-flux figure is CAVEAT, none is AS IS**, on the strength of the `ecoli_gasflux/README.md`
banner (D3). One is used, and its slide says mechanism.

## D5. Two new figures, not three

Parsa's respirometry has no committed figure anywhere in the repository, so it is the one thing the
deck cannot assemble. `make_figures.py` draws two from committed tables only:
`fig_respirometry.png` (per-cell growth and respiration against temperature, three media) and
`fig_cue.png` (carbon-use efficiency, the quantity `report.qmd` lists as future work). The third
allowed figure was not spent: the activation energies are three rows and belong on a slide as
numbers, not as a plot.

**Two things the prompt asked for that the tables do not contain, and the slides say so.**
**No acetate** — the derived tables carry O₂-based respiration, growth and CUE and no acetate
column; acetate appears only as a *model* output, in the gas-flux figures. **No model curve on the
same axes** — no committed table gives the model's prediction against these measurements, so the
measurements are plotted alone and model-against-measurement is left to the committed
`configD_gasflux.png`.

`M9`'s OTU 2 (7 rows) is the blank control P4 TASK 4 excluded as a control rather than a series;
only OTU 1 is plotted for M9, stated in the script rather than done silently.

## D6. What the measured data itself says, which shaped two slides

Reading the tables to draw them produced two facts worth a slide each, neither of which is in any
committed report:

* **Respiration peaks 3–5 °C above growth.** Mean respiration peaks at 45 °C (R2A) and 43 °C
  (LB, M9); growth peaks near 40 °C and is already collapsing where respiration is still rising.
* **CUE is flat then falls off a cliff.** ~0.6 (R2A, LB) and ~0.4 (M9) from 25 to 40 °C, then
  0.29 / 0.52 / 0.05 at 45 °C.

Both are measurement, not model, and are labelled as such.

**Deliberately not on a slide:** the committed OLS activation energies. `growth_E_eV` is
−0.167 ± 0.23 (R2A), 0.172 ± 0.18 (LB) and −1.003 ± 0.31 (M9) with R² of 0.009–0.159 — a straight
line through a curve that turns over, which K6 established is the wrong estimator for growth over
this range. Respiration's are well determined (0.345–0.591 eV, R² 0.35–0.88). Quoting the growth
numbers to a room of thermal biologists without the estimator argument would invite exactly the
wrong conclusion, and the estimator argument is a slide of its own that this deck does not have
room for.

## D7. Three slides carry no figure, and the reason is that no honest one exists

The prompt asks that every substantive slide carry a figure. Three do not.

* **Pettersen & Almaas** — the slide is three verbatim quotations. Their figures are theirs, and
  putting one of ours next to their words would imply we had reproduced their result. We have not.
* **The MRes baseline** — no figure of that model exists in this repository; it was a separate
  codebase on a different reconstruction. A figure of the *current* model on that slide would
  misattribute it.
* **One live basin / the posterior status** — P12 and P14 produced tables, not figures, and the
  slide's content is two retractions and a statement that nothing is being quoted. A figure would
  be decoration.

Every other substantive slide carries one, and every figure names its producing report on the
slide.

## D8. The bibliography's entry for the MRes thesis was wrong

`reports/ecoli_tpc/references.bib` gives the title as *"Predicting the temperature dependence of
microbial metabolism with enzyme- and temperature-constrained genome-scale models"*. The thesis is
titled **"Predicting the thermal niche of a ubiquitous bacterium using whole genome sequence"**
(Imperial College London, MRes Computational Methods in Ecology and Evolution, August 2023).

**Decision: correct it in this directory's own copy, and raise it rather than reach into
`ecoli_tpc/`.** That file is cited by the paper and by `reports/activation_energy/`; changing it is
a paper edit, and E1 — the run that was to produce the correction register — has not happened.
Recorded in `docs/OPEN_ITEMS.md`.

## D9. In-text citations had to be written out

The house CSL (`nature-communications.csl`) is a **numeric** style, so a bare `@Key` renders as a
superscript number with no author — the first render produced a slide reading "**1** — the only
published etcGEM". Every in-text mention is now written out with the key in brackets beside it.
Caught by looking at the rendered slide rather than at the source.

## D10. The Beamer theme is `default`, not `metropolis`

`metropolis` requires Fira Sans, which is not installed on this machine; the first render fell back
with a page of font warnings. **Decision: use the stock Beamer theme with `seahorse` colours and
`professionalfonts`** — it needs nothing external, matches the plain-font habit of the other
rendered reports, and does not put a font install into a shared venv while P15 runs.

## D11. What this deck deliberately does not claim (reconciled against §0c)

**It moves none of R1–R4.** It is a presentation of state: no fit, no sampler, no prior change, no
new measurement. Specifically it does not claim:

* **any interval on any parameter of the *E. coli* model.** None is available (D3, D4).
* **that the gas-flux configurations are validated.** They are gated as a *port* — his computation
  reproduces here — which is a different claim from validated performance.
* **anything about the posterior.** Two runs are in flight; the criterion is stated and no number
  from them appears.
* **that Li et al.'s model is wrong.** Y1 found the defect class absent from it. The register is an
  audit applied to the reference implementation.
* **that per-enzyme parameters would fix our −4 K.** Y3 screened that and the answer was no.
* **anything about the Candida models.** Their Tm is predicted, not measured.

---

## D12. Revision round, 2026-09-11 — six notes from the PI

The deck went from 20 slides to **37 pages / 34 frames**. What changed, note by note.

**1. A slide for the sixteen levers.** Two table slides (thermal envelope; budget / maintenance /
medium / observation) plus a third that says **which of the sixteen the data can actually move**.
The third is the one that matters: twelve are model levers, four are the experiment and the
observation model, and **five are flat** — `kappa_scale`, $f_{metab}$, $f_{maint}$,
`ngam_steepness`, `clearance_mult`. The honest count is "six thermal levers and $\sigma$ doing the
work, four bookkeeping terms, and five passengers", and the slide says so.

**2. Where the sector numbers come from, and the gap.** The source is now named on the slide:
**Wang et al. 2026** measured the *E. coli* proteome at a series of temperatures, in separate
LB / glucose / glycerol series. The gap gets a slide of its own, with the concrete numbers: the
**glucose series was measured at 25, 30 and 37 °C only**, the allocation is held at its endpoint
outside that range, and the consequence is a prediction that is **bit-identical from 37 to 44 °C**
(0.524757 h⁻¹ at all eight grid points). *"That shoulder is the proteomics table running out, not a
property of the cell."* The rendered figure makes the point visible on its own — the LB series has
five markers.

**3. Words to levers, and why the heatmap has 12 rows not 16.** The elasticity slide now defines
each word as a set of levers — catalysis = $\sigma$ + `kcat_scale`; kinetic envelope = $dT_{opt}$ +
`topt_scale` + $\Delta C_p$`_scale`; stability = $dT_m$ + `tm_scale`; allocation/maintenance = the
rest — and states that the missing four are `clearance_mult` (the experiment) and
`resp_scale`/`disc_resp`/`disc_growth` (the observation model), none of which touches the predicted
curve. Verified against `reports/ecoli_tpc/assets/tables/elasticity_table.csv`, which has exactly
those twelve rows.

**4. Overflow metabolism, expanded from one slide to four.** What it is (acetate excreted while O₂
is available; the measured law, threshold 0.76 h⁻¹ and slope 21 mmol gDW⁻¹ h⁻¹, from Basan et al.
2015) · **why a temperature model needs it at all** (an enzyme-constrained TPC fixes growth but not
the flux distribution, so O₂ and CO₂ are under-determined — *the same degeneracy Pettersen & Almaas
found by FVA, seen from the other side*) · the four-mechanism ladder A–F with imposed-or-emergent
marked · why D is the interesting one (nothing imposed on the acetate branch; the oxidase choice
becomes a prediction because *bd* and *bo₃* have different $T_m$) · the data behind it (the acetate
law, Szenk's membrane geometry, Parsa's respirometry, and $c_{max}$ from **his** sweep with his
verbatim conclusion) · and the advance: **Li et al. and the MRes both stop at growth.**

**5. The Bayesian work in plain terms, two new slides.** What everyone is trying to do, in one
sentence. Then what Li et al. did (SMC-ABC: simulate, keep the close ones, narrow, repeat) and what
Pettersen & Almaas found (different seeds, different answers; the method assumes one hill).
Then ours: 16 parameters not 2 292, a proper MCMC sampler rather than an approximate one, and a
likelihood that includes the measured respiration. Then **the three things that went wrong**, named
without jargon: chains ~9 autocorrelation times against a standard of ≥ 40, so **no interval
exists**; the surface itself is cliffed; and the cause is the O₂ flux jumping between equally
optimal solutions — *the degeneracy again*. **No report codes ("P9", "P12") appear on any slide.**

**6. Figures enlarged.** Eight figures moved to slides of their own, sized 52–100 % and set by
**height** where the figure is square or tall (see D13). The message and every honesty label moved
**above** the figure, where a clipped frame cannot eat them.

## D13. Beamer silently clips overfull frames, and it ate content four times

**This is the defect of the round and it would not have been caught by reading the render log.**
LaTeX emits **no Overfull warning** for a Beamer frame whose content exceeds the slide: it simply
truncates. The render log said `0 Overfull` at every stage while:

* the two lever tables dropped **every bullet that followed them**;
* the overflow ladder table lost **two of its five rows and both trailing bullets**;
* four figure slides lost their **captions** — one of them mid-sentence, taking the words *"no
  measurement is plotted here"* with it, which is an honesty label.

**Decision: add `check_frames.py` and make it part of the re-render instruction.** For every frame
it takes the last substantive source line — figure captions included — reduces it to letters-only
words (a numeric CSL glues the reference number to the preceding word, which defeats substring
matching) and requires 90 % of them to appear on the page carrying that frame's title. Exit 1 if
any frame has lost content. It found all four clips, and it found them again each time a fix
introduced a new one.

**Two lessons worth keeping.** A clean LaTeX log is not evidence that a deck is complete. And
shrinking a figure's **width** does nothing for a square figure that is too **tall** — the first
attempt shrank five figures by 30 % without fixing anything, which is the opposite of what was
asked for; the sizes are now set per figure by aspect.

## D14. One figure was mis-captioned, and the caption claimed a measurement that is not there

The first version's overflow slide read *"predicted O₂ uptake and acetate secretion … over Parsa's
measurements"*. Opening `configD_gasflux.png` shows three panels — **O₂ consumption, CO₂ formation
and respiratory quotient** — across four media, with **no measurement overlaid and no acetate
panel**.

**Decision: correct the caption, split the slide, and say on both halves that no measurement is
plotted.** `configD_growth.png` (predicted growth, four media, $r_{max}$ and $T_{opt}$ annotated)
now carries the medium-ladder point, and the gas-exchange slide points at the respiratory-quotient
panel, which is the one the carbon-cap argument rests on. `figure_inventory.csv` carried the same
wrong description and is corrected too.

This is the second time in this deck that a claim was checked by *looking at the artefact* rather
than at its filename, and both times the artefact disagreed. The rule from D4 applies to captions
as well as to intervals: **read the figure before describing it.**

---

## D15. `f_metab` and `f_maint` are FIXED BY MEASUREMENT, and calling them flat was wrong (E3, 2026-09-11)

The PI's correction, and it withdraws an earlier reading of his own. Verified against the paper
rather than taken on trust:

* the sector fractions $(f_{metab}, f_{bio}, f_{maint})(m,T)$ are *"taken from the measured
  proteome, matched to growth medium $m$ and temperature $T$ — **never fit to growth**"*
  (`report.qmd`, the allocation equation);
* in the calibration, *"Measured sector fractions get **tight** priors (measurement wiggle only —
  the proteome is not free-fit)"* (`report.qmd`, "The free set and priors"). That sentence is in
  the **prior specification** — a design choice — not a conclusion drawn from a posterior.

So the likelihood being insensitive to them **within one posterior standard deviation is the design
working.** Growth and respiration are not asked to re-derive a proteomics measurement. **The phrase
is "fixed by measurement", never "unidentified" and never "flat for want of data".**

**The five "flat" parameters are three different things**, and the deck now says so on the
"Which of the sixteen the data can actually move" slide as a **three-way** split:

| | levers | why |
|:--|:--|:--|
| the data move them | $dT_{opt}$, `topt_scale`, $\Delta C_p$`_scale`, $dT_m$, `tm_scale`, `kcat_scale`, $\sigma$, `ngam_scale` | eight |
| **fixed by measurement** | $f_{metab}$, $f_{maint}$ | measured proteome, tight priors |
| **genuinely unidentified** | `kappa_scale`, `ngam_steepness` | nothing measures them here |
| not model levers | `clearance_mult`, `resp_scale`, `disc_resp`, `disc_growth` | the experiment and the observation model |

**`ngam_scale` / `ngam_steepness` checked rather than assumed.** The paper's own free-set list calls
them *"the borrowed maintenance"*, and the NGAM constants ($a_m \approx 8.5$ mmol ATP gDW⁻¹ h⁻¹,
$b \approx 0.62$, $E_m \approx 0.5$ eV, $T_{ref} = 298.15$ K) are **ported from the MRes *E. coli*
model**, not measured for this strain or condition. So the NGAM half of R2 is a **genuine** gap and
stands. `ngam_scale` is moved by the data; `ngam_steepness` is not.

**`kappa_scale` likewise checked.** $\kappa$ (`translation_coeff`) is *auto-calibrated once at build
time* so that the metabolic pool and the translation cap are exactly co-limiting at the nominal
point. It is neither measured nor borrowed from a paper — a derived quantity nothing measures
independently. Genuinely unidentified.

**Three other places in the deck carried the wrong framing and are corrected:** the elasticity
slide (the two near-zero rows are now named as *different reasons, same appearance*); the
posterior-status slide (what we still will not know is `kappa_scale`/`ngam_steepness`, and
$f_{metab}$/$f_{maint}$ *"need nothing: they are already measurements"*); and the
needs-measurement slide (the gap is the **range** of the allocation measurement, not its
existence).

**Left alone, because it was already right:** the *"…and this is where we need more data"* slide.
It never said the sectors were unidentified — it said the measured series stops at 37 °C on
glucose and the allocation is then frozen, which is the real gap and is where $CT_{max}$ is set.

**`docs/OPEN_ITEMS.md` §0a R2** restated accordingly: the classification was wrong, P11's
measurement of the flatness was not, and the allocation gap is **range, not existence** — one
proteomics series, not a modelling problem.

## D16. E1 is still absent, so only the OPEN_ITEMS half of the withdrawal could be done

`reports/E1_paper_register/` does not exist — still not on `main`, on any branch, or anywhere in
the history, and there is still no commit prefixed "E1:". **There is therefore no
`corrections.csv` and no INVERTED row to withdraw.**

**Decision: do the OPEN_ITEMS half, record that the other half has no target, and do not
reconstruct E1's register** — the prompt forbids it and D0 already records why. When E1 runs, the
row it should carry is a **WITHDRAWN** entry stating the misreading: *"Measured sector fractions get
tight priors (measurement wiggle only — the proteome is not free-fit)"* sits in the prior
specification and describes a design choice, not a conclusion from the posterior. The paper is
right. This paragraph exists so that the withdrawal is on the record even though its file is not.

## D17. The legibility threshold, fixed before any figure was measured (E3, 2026-09-11)

Written and committed before the assessment, so it cannot be tuned to excuse a figure.

**The geometry.** The slide is `aspectratio=169` at Beamer's default 128 mm × 96 mm scaled to
16:9, so the text block is **`\linewidth` = 307.28 pt** wide (measured from the render, not
assumed) and `\textheight` ≈ 192 pt. A figure declared `{width=W%}` is rendered `W% × 307.28` pt
wide; one declared `{height=H%}` is `H% × 192` pt tall.

**The scale factor.** Matplotlib wrote every figure in this deck at a known figure size in inches
and a known dpi, so its native width in PostScript points is `figsize_in × 72`. The rendered
scale is then

$$ f = \frac{\text{rendered width in pt}}{\text{native width in pt}} $$

and any text element drawn at $s$ pt in the source appears at $f \times s$ pt on the slide.

**The threshold: a text element must render at $\geq$ 9 pt to count as legible**, and the element
that governs is the **smallest** one that has to be read — in practice the **tick labels**, since
every figure here has smaller ticks than axis labels, titles or legends. Matplotlib's default tick
label size is **10 pt** (`xtick.labelsize`), so the criterion reduces to a scale factor

$$ f \geq 0.9 . $$

Figures whose own script sets a smaller tick size are measured against their own value, not the
default.

**Why 9 pt.** It is the bottom of the range typography guides give for projected body text, and it
is roughly the size of the deck's own caption text — so the rule is "a tick label must be no
smaller than the caption under it", which is checkable by eye afterwards as well as by arithmetic
beforehand.

**What the rule is not.** It says nothing about whether a figure is *useful* at that size — a
22-panel scan can be legible by this rule and still be a gestalt rather than something to read.
Those are handled separately and named where they occur.

**Remedy order, as the prompt sets it:** (a) move the bullets to a preceding slide and give the
figure the whole frame; (b) split a multi-panel figure across two slides; (c) crop to the
informative region, stated; (d) last resort, regenerate at a different aspect — and then the
producing script is edited and committed, never the PNG alone.

## D18. The legibility measurement, and what it found (E3, 2026-09-11)

**A correction to D17 first.** D17 said the slide's text block was "measured from the render" at
307.28 × 192 pt. It was not measured — it was assumed, and it was wrong. Measured with a one-frame
Beamer probe (`\typeout{\the\linewidth}` under `lualatex`): **`\linewidth` = 398.3386 pt,
`\textheight` = 252.0748 pt.** The threshold ($f \geq 0.9$) is unchanged; only the arithmetic
behind the rendered widths moves. `measure_figures.py` now computes the table from the measured
values, so it cannot drift again.

**The result, and it is not a near miss.** At the sizes the deck had, **every figure failed** —
$f$ between 0.14 and 0.57, tick labels rendering at **1.4 to 5.7 pt**. The cause is structural, not
layout: these are **journal figures**. `task1_scan.png` is 17 inches wide natively and the slide is
5.5 inches, so nothing done to the slide can make its tick labels 9 pt.

**What was fixed, properly.** The three figures this directory owns are regenerated **at the width
they occupy on the slide** — `make_figures.py` now carries `SLIDE_W_IN = 398.3386/72` and
`FRAME_W_IN`, and draws at those sizes rather than at journal width. The producing script is
edited and committed, never the PNG. All three now pass:

| figure | before | after |
|:--|--:|--:|
| `fig_respirometry.png` | $f$ 0.57 (5.7 pt) | **$f$ 0.91 (9.1 pt)** |
| `fig_y2_asymmetry.png` | $f$ 0.57 (5.7 pt) | **$f$ 0.92 (9.2 pt)** |
| `fig_cue.png` | $f$ 0.46 (4.6 pt) | **$f$ 0.94 (9.4 pt)** |

`fig_cue` also came out of its 58 % column onto its own frame — the column gives a figure only
167 pt, and a figure drawn for 167 pt is mostly axis.

**What could not be fixed, and the honest number for each.** The eight borrowed figures were moved
to their frame maximum, which raised them but nowhere near the threshold. The ceiling is set by
native width against a 398 pt slide:

| figure | before | after (frame maximum) | ceiling |
|:--|--:|--:|:--|
| `example_enzyme_kcatT.png` | 0.37 | **0.47** | native 809 pt |
| `reference_tpc.png` | 0.29 (in column) | **0.46** | out of the column, own frame |
| `proteome_sector_fractions.png` | 0.38 | **0.46** | native 504 pt |
| `configD_growth.png` | 0.34 | **0.41** | native 619 pt |
| `elasticity_heatmap.png` | 0.31 | **0.35** | native 518 pt, nearly square |
| `configD_gasflux.png` | 0.35 | **0.35** | already full width; native 1152 pt |
| `validation_trusted_curves.png` | 0.39 | 0.39 | left in its column; own frame gains 0.03 |
| `task1_scan.png` | 0.14 | **0.15** | native 1224 pt — hopeless by any layout |

**The fix for those eight is not a layout change**: it is re-running their producing scripts
(`reports/ecoli_tpc/assemble.py`, `scripts/gasflux_figures.py`,
`reports/P9_surface/task1_lines.py`) with slide-width figure sizes. That rewrites other reports'
committed assets and needs model runs — outside a deck run, and recorded in `docs/OPEN_ITEMS.md`
rather than done here.

**The named case — the elasticity heatmap — is resolved a different way, and better.** Its image
went from $f$ 0.31 to 0.35 (159 → 182 pt rendered), which is not legible and never will be at
518 pt native. So **the numbers are now a typeset table on a slide of their own**, at full slide
width and perfectly readable, with the heatmap kept on the following frame as the pattern view.
Same content, same source (`reports/ecoli_tpc/assets/tables/elasticity_table.csv`), read rather
than squinted at. That is the remedy the prompt's order does not list and it is the right one for
a 12 × 5 table of numbers that had been drawn as a picture.

**Two figures are legible by the rule and still not readable as data**, and the slides say so
rather than pretending: `task1_scan.png` (22 panels — *"read the pattern, not the axes"*) and
`configD_gasflux.png` (three panels — *"look at the right-hand panel"*). The threshold measures
text size, not whether a figure is the right object; D17 said so in advance.

**`measure_figures.py` is committed and exits 1 while any figure is below threshold**, so the eight
outstanding cannot quietly become acceptable.
