# Claude Code prompt — E3: correct the sector claim, make the unreadable figures readable, re-render (autonomous, ~45 min)

**Run from `../etcGEMs-work`**, continuing on branch `e2/deck` (PR not merged). P15 is running
nested fits in `etcGEMs` and owns it — write nothing there. Use `../etcGEMs-venv`. Rendering only,
no solves.

**Two jobs, one small and one that is mostly layout.**

---

**JOB 1 — a correction that is the PI's, and it withdraws an earlier correction of his.**

`f_metab` and `f_maint` are **measured**, not free. `report.qmd` (line ~349) is explicit:
`(f_metab, f_bio, f_maint)(m,T)` are taken from the measured proteome, **matched to growth medium
and temperature, never fit to growth**, and in the calibration they carry deliberately **tight
priors — "measurement wiggle only"**.

So their FLAT classification (P11, P12) is **the designed behaviour, not a deficiency**. The
likelihood being insensitive to them within one posterior sd means growth and respiration data
neither test nor refine the sector fractions within the proteome measurement's own uncertainty —
which is what should happen when a parameter enters as a measurement. **The correct phrase is
"fixed by measurement", never "unidentified" and never "flat for want of data".**

Two things to undo, both mine:
  * If `reports/E1_paper_register/corrections.csv` exists and carries a row marking the paper's
    sector statement as **INVERTED** — **withdraw it.** That was a misreading: *"Measured sector
    fractions get tight priors (measurement wiggle only — the proteome is not free-fit)"* sits in
    the **prior specification**, describing a design choice, not a conclusion drawn from the
    posterior. The paper is right. Replace the row with a WITHDRAWN entry stating the misreading,
    rather than deleting it.
  * `docs/OPEN_ITEMS.md` §0a **R2** lists "proteome allocation vs temperature (sectors)" as the
    missing data for these parameters. It is not missing — it is in the model, medium- and
    temperature-matched. **Replace it with the real gap**, which the deck already states correctly:
    the measured allocation is **held at its endpoint beyond the measured range**, so above 37 °C
    on glucose the sector split is frozen — and that is exactly the region where CT_max is set.
    That is a proteomics experiment, not a modelling problem.

**If E1 never ran** (`reports/E1_paper_register/` absent), say so and do only the OPEN_ITEMS half.
Do not reconstruct E1's register here.

---

**JOB 2 — figures that cannot be read.**

The fifth figure in the deck is the **elasticity heatmap** (`elasticity_heatmap.png`, slide
"Elasticity: every descriptor against every lever", currently `height=58%`). Every descriptor
against every lever at that size is illegible. **Rearrange the slide so the figure can be much
larger** — move the text off it, split it, or give the figure a slide of its own with the bullets
preceding it. Do not shrink the content to fit; restructure so the figure gets the space.

**Then check every other figure the same way rather than only the one reported.** Judge legibility
at the rendered size — axis labels, tick labels, legend text, heatmap cell annotations — not at the
source PNG's native size. The likely other offenders, by content rather than assumption: the line-scan
panel (`P9_surface/task1_scan.png`, 22 panels at `height=60%`), the gas-exchange triple
(`configD_gasflux.png`), and the two-column slides where a figure is confined to 58 % of the width.

---

NOTE TO USER: launch in an auto-approving mode. Text, layout and a re-render.

---

```
Work AUTONOMOUSLY; commit in parts, prefixed "E3: "; append to reports/ecoli_deck/DECISIONS.md.
Standing rules carry over. Check exit codes explicitly, never `cmd && check`. Continue on
`e2/deck` in ../etcGEMs-work; do not push to main; the PR stays unmerged. Write NOTHING under
../etcGEMs.

TASK 0 - premise
- Confirm the worktree, the branch, the interpreter; confirm P15 is running in the primary tree and
  untouched. Confirm the deck currently renders before changing anything, and record the page count
  as the baseline.

TASK 1 - the sector correction
- Search the deck for every statement about f_metab, f_maint or the proteome sectors. Quote each
  with its slide title. For each, decide: does it say or imply these are UNIDENTIFIED or flat for
  want of data? If so, correct it to FIXED BY MEASUREMENT, with the real gap being the frozen
  allocation above 37 C. If a slide already states this correctly - the deck's "…and this is where
  we need more data" slide appears to - leave it and say so.
- The "Which of the sixteen the data can actually move" slide is the most likely place the wrong
  framing appears. Check it specifically. The honest split there is three-way, not two: levers the
  data move; levers the data cannot move and nothing measures (genuinely unidentified); and levers
  FIXED BY MEASUREMENT that the data is not asked to move. Present it that way if it is not already.
- docs/OPEN_ITEMS.md §0a R2: replace the sector entry per JOB 1. Keep the NGAM entry as it stands
  unless the same argument applies to it - check whether ngam_scale/ngam_steepness are measured or
  borrowed, and say which. The paper calls them "borrowed maintenance", so they are probably a
  genuine gap; verify rather than assume.
- reports/E1_paper_register/corrections.csv, if it exists: the INVERTED row becomes WITHDRAWN with
  the reason. Do not delete it.

TASK 2 - legibility, measured rather than judged by eye
- Build a table of every figure in the deck: path, the size directive in the .qmd, the source PNG's
  pixel dimensions, and the rendered size on the slide. From those, compute the effective scale
  factor and the rendered height in points of the smallest text element you can identify in each
  figure (axis tick labels are usually the smallest). State the threshold you adopt for legibility
  - a defensible one for a projected slide is roughly 9-10 pt equivalent - and write it into
  DECISIONS.md BEFORE assessing.
- Flag every figure below the threshold. Fix them by RESTRUCTURING THE SLIDE, in this order of
  preference: (a) move the bullets to a preceding slide and give the figure the full frame;
  (b) split a multi-panel figure across two slides; (c) crop to the informative region if the
  producing script allows it and the crop is stated. Only as a last resort regenerate a figure at a
  different aspect ratio - and if you do, the producing script is edited and committed, never the
  PNG alone.
- The elasticity heatmap is the known case and must end up substantially larger. Report its before
  and after rendered size.
- Do not reduce the figure count and do not drop content to make room; move it.

TASK 3 - render and verify
- Re-render to PDF. Verify: it opens, every figure resolves, no overfull box, no unresolved
  citation, and the page count changed only by the slides you deliberately added.
- Report the absolute path and the new page count.
- Re-run scripts/stamp_reports.py.
- Commit the rendered PDF if that is the convention the directory already follows.

VERIFY (report all)
1. TASK 0: worktree, branch, P15 untouched, baseline render and page count.
2. TASK 1: every sector statement quoted with its slide, and what was done to each; the three-way
   split on the "which of the sixteen" slide; OPEN_ITEMS R2 before and after; whether
   ngam_scale/ngam_steepness are measured or borrowed, with the evidence; the E1 row withdrawn or
   E1 reported absent.
3. TASK 2: the legibility table with the threshold quoted from before the assessment; every figure
   flagged; what was done to each; the elasticity heatmap's rendered size before and after.
4. TASK 3: PDF path, page count before and after, render clean, stamps.
5. `git diff main --stat`: reports/ecoli_deck/, OPEN_ITEMS, possibly E1's csv, stamps. Nothing
   under ../etcGEMs, src/ or strains/.

CONSTRAINTS
- "Fixed by measurement" is the phrase for f_metab and f_maint. Never "unidentified".
- The withdrawn correction is marked WITHDRAWN with its reason, not deleted.
- Legibility is assessed against a threshold written down first, not by eye afterwards.
- Slides are restructured to fit figures; figures are not shrunk to fit slides, and content is not
  dropped.
- A regenerated figure means an edited, committed producing script - never a hand-made PNG.
- Nothing from P15 appears anywhere in the deck.
- Autonomous; commit in parts: "E3: sector correction", "E3: legibility", "E3: render".
```
