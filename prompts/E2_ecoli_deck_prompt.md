# Claude Code prompt — E2: a slide deck on what the E. coli model adds to what is published (autonomous, ~2 h, renders to PDF)

**Run from `../etcGEMs-work`, NOT from the primary checkout.** P15 is running two nested fits in
`etcGEMs` until tomorrow evening and owns it. **Run this AFTER E1 finishes** in the same worktree —
E1's `brief.md` and `corrections.csv` are inputs here, and the two must not both hold the branch.
Use `../etcGEMs-venv`. Rendering only: no fits, no solves beyond what a figure script needs.

**The deliverable.** `reports/ecoli_deck/` — a Quarto Beamer deck rendering to PDF, in the house
convention where it applies (fonts, CSL, `references.bib`). **Minimal text: bullet points, not
prose.** Every substantive slide carries a figure. The audience is a collaborating group
(Samraat Pawar's team) who know thermal biology but not this codebase.

**The organising question for every slide: what is new here relative to what is published?** Three
reference points, all already in `reports/ecoli_tpc/references.bib`:

  * **Li et al. 2021** (`refs/Lietal2021NatComms.pdf`, `@Li2021`) — the only published etcGEM.
    2,292 per-enzyme parameters, SMC-ABC, measured Tm, Topt from Tome as a wide prior. Growth and
    chemostat data; **no gas exchange**.
  * **Pettersen & Almaas 2023** (`refs/PettersenAlmaas_2023.pdf`, `@Pettersen2023`) — re-ran Li's
    calibration across seeds and found it unstable and multimodal; their FVA showed cytochrome
    oxidase flux varying hugely between equally-fit particles; they name proteomics and fluxomics
    as the missing data. **Read this before drafting — it is the paper that says what the field
    needs, and Parsa's respirometry is that data.**
  * **Madkaikar 2023 MRes** (`refs/Madkaikar_CMEE_MRes_02299268.pdf`, `@Madkaikar2023`) — the
    baseline this group inherited. **Read it and establish what the model was at that point**;
    every "what we added" claim is relative to it, and I do not know its contents. If it does not
    say what this prompt assumes, follow the thesis, not the prompt.

**Honesty constraints, which are not negotiable.**
  * **P15 is in flight.** Quote nothing from it. The posterior slide says the runs are under way and
    what the criterion is, and nothing more.
  * The gas-flux work's **mechanism** stands; its **intervals** do not (1.17, 1.19). Any slide
    carrying a gas-flux number says which it is.
  * `tbl-corrections`-style intervals from the old E. coli posterior are UNSUPPORTED (E1's
    register). Do not put them on a slide.
  * Where a defect was found in this project's own work, it appears with the same prominence as
    one found elsewhere. Several of the week's sharpest results were self-corrections.
  * The register is "we built an audit and applied it to the reference implementation", never
    "we found errors in a published paper".

NOTE TO USER: launch in an auto-approving mode after E1 reports. It reads three PDFs, assembles
committed figures, may generate two or three small ones from committed tables, and renders.

REFERENCE, read first: E1's outputs in `reports/E1_paper_register/` (brief, corrections,
gasflux inventory, restructure options); `reports/ecoli_tpc/report.qmd` (66 committed figures in
`assets/figures/`); `reports/ecoli_gasflux/README.md` (14 figures); `strains/eciML1515/
respirometry/` (Parsa's measured data as CSVs); `reports/Y1_yeast_audit/`, `Y2_regime_posterior/`,
`Y3_tm_shift/`, `P9_surface/`, `P10_respiration_likelihood/`, `P12_modes/`, `P13_support/`;
`reports/synthesis/evidence.csv`; `docs/OPEN_ITEMS.md` §0.

---

```
Work AUTONOMOUSLY; commit in parts, prefixed "E2: "; maintain reports/ecoli_deck/DECISIONS.md FROM
THE FIRST JUDGEMENT CALL. Standing rules carry over. Check exit codes explicitly, never
`cmd && check`. In ../etcGEMs-work: branch `e2/deck` from main (after E1's branch is done with the
tree); do not push to main; end in a PR that is NOT merged. Write NOTHING under ../etcGEMs.

TASK 0 - premise and the three reference points
- Confirm the worktree, branch, interpreter; confirm E1 has finished and P15 is untouched.
- Read the Madkaikar MRes thesis and write a short factual summary into DECISIONS.md D1: what the
  E. coli model was at that point - its scope, its data, its thermal layer, what it did and did not
  do. This is the baseline. **If it contradicts anything this prompt assumes, follow the thesis and
  say so.**
- Read Pettersen & Almaas and record in D2 the three things this deck uses them for: the
  instability across seeds, the FVA result on cytochrome oxidase, and their statement of what data
  the field needs.
- Confirm the Quarto/Beamer toolchain renders at all with a one-slide smoke test before writing
  content. If a LaTeX dependency is missing, say exactly what and STOP - do not install into the
  shared venv while P15 runs.

TASK 1 - the figure inventory, before any drafting
- List every candidate figure by path with one line on what it shows, drawn from
  `reports/ecoli_tpc/assets/figures/` (66), `reports/ecoli_gasflux/assets/figures/` (14), and any
  other committed report figure that bears on E. coli.
- Mark each: USABLE AS IS / USABLE WITH A CAVEAT ON THE SLIDE / NOT USABLE (superseded). In
  particular `corner_v3.png` and anything derived from the old posterior carry E1's UNSUPPORTED
  status - if used at all, the slide must say what it is.
- **Parsa's measured data has no committed figure.** Generate at most THREE new figures from
  committed tables only (`strains/eciML1515/respirometry/derived_*_current.csv` and the
  `activation_energy_*.csv`), with a producing script in `reports/ecoli_deck/`. The one I would
  most want: **measured O2 uptake and acetate against temperature, by medium**, with the model's
  prediction over it if that is available from a committed table. If the model curve is not in a
  committed table, plot the measurements alone and say so. Cap at three; a deck earns its keep by
  assembling.
- Every figure on a slide is sourced BY PATH and its caption names the producing report.

TASK 2 - the deck
Aim at 14-18 slides. Bullets, not sentences; no slide with more than ~40 words of text. Suggested
arc - adapt as the material demands, and drop anything the evidence does not support:
  1. Title; the question the framework answers.
  2. **What an etcGEM is**, one diagram-or-figure slide.
  3. **The state of the art: Li 2021.** What it achieved; 2,292 per-enzyme parameters; growth and
     chemostat, no gas exchange.
  4. **The problem the field found: Pettersen & Almaas 2023.** Seeds disagree; the method assumes
     unimodality; their own words on what is needed.
  5. **Where we started: the MRes baseline** (from D1).
  6. **What the model is now** - the merged core, seven strains, E. coli as the best-constrained;
     the gate (79/79, 60/60) as the guarantee.
  7-9. **The model developments**: proteome sectors and the growth law; the overflow mechanism
     emerging from a total-carbon cap rather than imposed; the ETC membrane-area constraint. One
     figure each. State plainly which are gated ports of Parsa's work and which are new here.
  10. **The data nobody else has**: Parsa's respirometry - O2 and acetate, three media, a
     temperature series. Set explicitly against Pettersen & Almaas's stated gap.
  11. **What we found when we tried to calibrate it**: the surface was cliffed, not
     under-sampled; the cliffs were the respiration term on LP vertices at cold temperatures. One
     figure from P9/P10 if a committed one exists.
  12. **The fixes and what each was for**: tie-break, variance floor, support clamp. Bullets.
  13. **One live basin** (P12) - and the retraction, stated as a retraction.
  14. **Where the posterior stands**: runs in flight, the criterion, nothing quoted.
  15-16. **Auditing the published model**: Y1 - the coupling-ion defect is absent from Li's model
     and the GECKO split makes it structurally impossible, so this is a property of how a
     reconstruction is built, not of the field. Y2 - the T_opt/CT_max asymmetry reproduces at
     their published posterior with an interval, and CT_max is NOT insensitive there as it was in
     ours. Register: an audit applied to the reference implementation.
  17. **What is settled, what is in flight, what needs measurement** - the three-way split from
     OPEN_ITEMS §0a, in six bullets.
  18. **Three questions for the group.** Questions, not conclusions.
- A closing references slide from `references.bib`.

TASK 3 - render and check
- Render to PDF. Verify: it opens, every figure resolves, no overfull slide, no unresolved
  citation. Report the page count and the absolute path.
- Add a `README.md` giving the one-line re-render command, matching the house habit in the other
  report directories.
- Follow the repository's convention on committing rendered output: check what
  `reports/activation_energy/` and `reports/synthesis/` do and match it. If PDFs are committed
  here, commit this one.
- Provenance stamp via `scripts/stamp_reports.py`.

TASK 4 - record
- reports/ecoli_deck/DECISIONS.md: D1 (the MRes baseline), D2 (Pettersen & Almaas), the figure
  inventory decisions, anything dropped for lack of evidence.
- docs/OPEN_ITEMS.md: one item if the deck exposed a claim that cannot be supported and should be
  checked.
- Reconcile against §0c in a closing note: this moves none of R1-R4; it is a presentation of
  state. Say what it deliberately does not claim.
- Stamps.

VERIFY (report all)
1. TASK 0: worktree, branch, E1 finished, P15 untouched; D1's MRes summary and anything in it that
   contradicted this prompt; D2; the Beamer smoke test.
2. TASK 1: the inventory with its three-way marking; which figures were generated new, from which
   committed tables, by which script, and why each was necessary.
3. TASK 2: the slide list with, per slide, its figure path and its one-line claim; confirmation
   that no slide quotes P15, no slide carries an UNSUPPORTED interval, and every gas-flux number is
   labelled mechanism-or-interval.
4. TASK 3: PDF path, page count, render clean; the README; the commit convention followed.
5. `git diff main --stat`: reports/ecoli_deck/, OPEN_ITEMS if used, stamps. Nothing under
   ../etcGEMs, nothing under src/ or strains/.

CONSTRAINTS
- Bullets, not prose. Every substantive slide carries a figure.
- Every claim is relative to Li 2021, Pettersen & Almaas 2023, or the MRes baseline, and says which.
- Nothing from P15 appears. Gas-flux numbers are labelled mechanism or interval. No UNSUPPORTED
  interval reaches a slide.
- At most three new figures, from committed tables only.
- Self-corrections appear with the same prominence as findings about others' work.
- Audit register throughout: applied to the reference implementation, never a critique of a paper.
- Autonomous; commit in parts: "E2: baseline and references", "E2: figure inventory",
  "E2: slides", "E2: render", "E2: record".
```
