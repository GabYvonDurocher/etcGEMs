# Claude Code prompt — E4: show the model against the data, explain the carbon cap, fix an attribution (autonomous, ~1 h)

**Run from `../etcGEMs-work`**, continuing on branch `e2/deck`. **Run E3 first if it has not run**
(`prompts/E3_deck_corrections_and_layout_prompt.md`) — this builds on it. P15 is running nested fits
in `etcGEMs`; write nothing there, and keep any solving here **single-process** so it does not
compete for cores.

---

**JOB 1 — an attribution that is wrong.**

Three files attribute work to "Parsa Amirmoeini". **That is not his surname.** Remove it:

  * `strains/eciML1515/media/NLDM_media.csv` line ~3 (provenance comment)
  * `strains/eciML1515/respirometry/README.md` line ~7
  * `reports/P2_settle/SUMMARY.md` line ~30

**Do not guess a replacement surname.** Use "Parsa", which is what the rest of the repository uses.
Search the deck and every report for the same string and fix it everywhere. If it appears anywhere
formatted as a literature citation, that is doubly wrong — his work is unpublished and is
team-internal, not a reference.

---

**JOB 2 — remove internal framing from an external document.**

The deck says something to the effect of *"CUE is listed in our own E. coli paper as future work. It
is measured, in three media, and not yet folded in."* The group has never seen that paper, so this
is meaningless to them and reads as internal bookkeeping. **Cut it.** Say what the measurement *is*
and what it shows; the fact that an unpublished internal draft listed it as future work is not
content. Sweep the whole deck for the same failure — any sentence whose meaning depends on the
audience knowing our internal documents or prompt series.

---

**JOB 3 — the carbon cap needs explaining properly. It currently appears without being defined.**

Read the implementation before writing anything: `add_total_carbon_constraint` in the gas-flux code,
`strains/eciML1515/gas_exchange.yaml` (`carbon_cap.by_medium`), and `reports/P3_gate/TASK4_cmax.md`,
`reports/P5_lb_cmax/`, `reports/P2_settle/task3_cmax_table.csv`. Then give it **its own slide**
covering, in bullets:

  * **What it constrains** — state the actual quantity and units from the code, not a paraphrase.
  * **What it produces.** Overflow metabolism *emerges* rather than being imposed. That is the
    point of configuration D and it is what distinguishes it from a model where acetate secretion
    is written in by hand.
  * **Why the value matters, with the measured numbers.** At `c_max = 60` acetate overflow is
    **zero on both media** — the cap suppresses the very mechanism configuration D exists to
    produce. Applying the glucose/NLDM value of 120 to LB collapses growth R² from **0.83–0.90 to
    0.16–0.20**, because 120 holds r_max at 1.1–1.8 against a measured 2.94 h⁻¹. LB is settled at
    **450**.
  * **That it is medium-dependent** — 60 / 120 / 450 is not three guesses at one number, it is one
    quantity that differs by medium, and that was the resolution of a real disagreement.
  * **A second role worth stating**: the docstring records that the constraint *pins the flux
    distribution, making O₂ and CO₂ unique*. That bears directly on the identifiability story later
    in the deck — a cap that binds removes an LP face.

Check each of these against its source; correct the prompt's numbers if the files disagree.

---

**JOB 4 — show the model against the data. This is the biggest gap in the deck.**

The deck currently shows model predictions (`configD_growth.png`, `configD_gasflux.png`) and
measurements (`fig_respirometry.png`, `fig_cue.png`) on **separate slides**. Any audience will ask
how well it fits, and the deck does not answer. Overlay them.

  * **Growth: model against measured**, per medium, across the temperature series.
  * **O₂ consumption: model against measured**, same.
  * **CUE: model against measured**, if the model's predicted CUE is derivable from committed
    outputs (biomass carbon over total carbon consumed). If it is not derivable without assumptions
    you would have to invent, say so and leave CUE as measurement-only.
  * Report R² on each panel **from `reports/P3_gate/gate_def_headline.csv`** (the gated values,
    `cur_g` and `cur_r`) rather than recomputing — and say on the slide that these are at the gated
    parameters.

**The caveat that must appear on those slides, in one short line:** these are the model at Parsa's
gated parameters, **not** a converged posterior — there are no intervals, and P15 is still running.
A fit shown without that line overstates what exists.

Per-temperature model predictions are **not** in a committed table (the gate file has R² only), so
generating these needs solves. Budget: single process, at most ~300 evaluations, the parameters read
from `gate_def_headline.csv` rather than assumed. If that budget is not enough for all three
quantities, do growth and O₂ and report CUE as not done. Producing script committed under
`reports/ecoli_deck/`; figures sourced by path; captions naming the script.

---

NOTE TO USER: launch in an auto-approving mode after E3. Text, a small amount of solving, and a
re-render.

---

```
Work AUTONOMOUSLY; commit in parts, prefixed "E4: "; append to reports/ecoli_deck/DECISIONS.md.
Standing rules carry over. Check exit codes explicitly, never `cmd && check`. Continue on `e2/deck`
in ../etcGEMs-work; do not push to main; the PR stays unmerged. Write NOTHING under ../etcGEMs.
Keep all solving SINGLE-PROCESS.

TASK 0 - premise
- Confirm worktree, branch, interpreter; confirm E3 has run; confirm P15 is untouched. Confirm the
  deck renders and record the baseline page count.

TASK 1 - the attribution (JOB 1)
- Find every occurrence of the incorrect surname across the repository and the deck. Fix each to
  "Parsa". Report every file and line changed. Do not invent a surname.

TASK 2 - internal framing (JOB 2)
- Quote every sentence in the deck whose meaning depends on the audience knowing our internal
  documents, drafts or prompt series. Rewrite or cut each. Report them.

TASK 3 - the carbon cap slide (JOB 3)
- Read the implementation and the four sources named above. Write the slide. Verify every number
  against its source file and report any disagreement with this prompt's values - the files win.

TASK 4 - model against data (JOB 4)
- Read the gated parameters from gate_def_headline.csv. Solve the model across the measured
  temperature series per medium, single process, <= 300 evaluations, and write the predictions to a
  committed CSV so the figures are reproducible without re-solving.
- Build the overlay figures: growth, O2, and CUE if derivable. State on each slide that these are at
  gated parameters and not a converged posterior.
- If any quantity cannot be overlaid honestly - units that do not match, a normalisation that would
  have to be invented, per-cell rates that 1.9 makes unreliable - say so plainly and leave it as
  measurement-only. **Do not manufacture agreement by rescaling.** Note that OPEN_ITEMS 1.9 makes
  absolute per-cell rates unreliable (N0 and fg-C-per-cell constants ~6x off) while growth R2 and
  scale-free quantities are immune; if the overlay requires per-cell absolutes, carry that caveat.

TASK 5 - render and verify
- Re-render. Verify: opens, every figure resolves, no overfull box, no unresolved citation. Report
  path and page count. Re-run scripts/stamp_reports.py. Commit the PDF if that is the directory's
  convention.

VERIFY (report all)
1. TASK 0: worktree, branch, E3 confirmed run, P15 untouched, baseline page count.
2. TASK 1: every file and line where the surname was fixed.
3. TASK 2: every internal-framing sentence quoted, and what was done to it.
4. TASK 3: the carbon-cap slide's bullets, each with the source file it was verified against; any
   number where the file disagreed with this prompt.
5. TASK 4: the gated parameters used and where they came from; the evaluation count; the committed
   prediction CSV; which overlays were made and which were not, with reasons; confirmation the
   gated-parameters caveat appears on each.
6. TASK 5: PDF path, page count before/after, render clean, stamps.
7. `git diff main --stat`: reports/ecoli_deck/, the three attribution fixes, stamps. Nothing under
   ../etcGEMs, src/ or strains/ beyond the two attribution comments.

CONSTRAINTS
- Do not invent a surname. "Parsa" only.
- Nothing in the deck may depend on the audience knowing our internal documents.
- Every carbon-cap number is verified against its source file; the file wins over this prompt.
- Overlays are honest or absent. No rescaling to manufacture agreement.
- Every fit slide states that it is at gated parameters, not a converged posterior.
- Single-process solving, <= 300 evaluations. Do not compete with P15.
- Nothing from P15 appears in the deck.
- Autonomous; commit in parts: "E4: attribution", "E4: framing", "E4: carbon cap", "E4: fits",
  "E4: render".
```
