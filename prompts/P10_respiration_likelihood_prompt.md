# Claude Code prompt — P10: fix the respiration likelihood — a tie-break for the faces, a variance the model can honour for the kinks — and show the surface is smooth before sampling it (autonomous, ~1 day)

Run from the project root (`.../MICROADAPT/etcGEMs`), on `../etcGEMs-venv`. **Merge PR #24 (P9)
first**, server-side, matching #14–#23; then `git switch main`, `git pull`, branch
`p10/respiration-likelihood`. Nothing is running.

**This prompt changes the model's likelihood. That is the first time in this series, and it is on
purpose.** Six runs — P6, P7, P8, P9 and the two diagnoses inside them — established that the
configuration-D chains do not mix because the *surface* is cliffed, not because the sampler is
weak; and that the cliffs are the respiration term at cold temperatures, where the LP's optimal O₂
jumps two- to four-fold across a 0.05 sd step while growth moves 3–30%, and a log-scale term with a
small variance turns that into 13–72 log-likelihood units (P9). E/F had the same disease in a
different form — O₂ on an LP face, solver-selected (D3a). One cause: **the respiration term asks the
model for a precision the model structurally cannot deliver.**

**Two halves, and they are halves, not alternatives.** A tie-break at the optimum makes O₂
deterministic where it was on a face (E/F) but does not remove kinks between vertices (D), because a
pFBA solution is piecewise too. A variance on the respiration term that reflects the model's own
granularity removes the cliffs' *height* — a factor of four in O₂ under σ_log ≈ 0.7 is ~2 units, not
30 — but leaves the face arbitrary. Both are needed; each is gated separately so its contribution
is visible.

**The discipline.** Every change is (1) implemented in the core as an option, default OFF, so the
seven-strain gate proves nothing else moved; (2) turned on for eciML1515 in its strain config; (3)
shown to do what it claims on the exact instruments that found the defect — the D3a jitter table and
P9's roughest lines — before any sampler touches it. Nothing else about the model, the priors on the
existing parameters, the data or `c_max` changes. If the surface is smooth afterwards, ONE fit is
run to see whether τ finally plateaus. If it is not, STOP: the surrogate route (1.15 c) is a
separate decision.

NOTE TO USER: launch in an auto-approving mode. Budget a day: code and gates in the morning, one
D NLDM fit of ~3–4 h after, under the P7 driver with checkpoints. It merges one PR first. Read
`docs/OPEN_ITEMS.md` items 1.13, 1.15, 3.21 and section 0 (E. coli first) before starting.

REFERENCE, read first: `reports/P9_surface/report.md` (the cliffs, the three decomposed jumps, the
line-scan scripts); `reports/P6_convergence/DECISIONS.md` D3a (the state-vs-identifiability table —
the instrument for the tie-break); `reports/P3_gate/` (the gate and its criteria); `reports/P4_refit/`
(the fit definition and MAP); `src/etcgem/` for where the likelihood is assembled.

---

```
Work AUTONOMOUSLY; commit in parts, prefixed "P10: "; maintain reports/P10_respiration_likelihood/
DECISIONS.md FROM THE FIRST JUDGEMENT CALL. Standing rules carry over. Check exit codes explicitly,
never `cmd && check`. Branch from main after the merge; do not push to main; end in a PR that is
NOT merged.

TASK 0 - merge, start clean, and READ THE CURRENT TERM BEFORE TOUCHING IT
- Merge #24; switch; pull; branch. Interpreter ../etcGEMs-venv; gates 79/79 and 60/60 as the
  baseline, recorded.
- Write down, from the code and not from memory, exactly how the respiration likelihood is
  formed today: the quantity compared (O2 uptake? RQ? per-temperature?), the scale (log or
  linear), the variance and where it comes from, and where `disc_resp` enters - D6 lists it as a
  fitted discrepancy scale with posterior/prior width 0.13, so a respiration discrepancy term
  ALREADY EXISTS and P9's cliffs happened with it in place. Explain why it did not absorb them:
  linear where it needed to be log? prior too narrow? applied to the wrong quantity? Put this in
  DECISIONS.md D0. The fix in TASK 2 must be the MINIMAL change that follows from this reading.
  Do not add a second discrepancy term next to one that exists.
- Write down how O2 at the optimum is obtained today: a single LP solve with growth as the
  objective, O2 read off the returned vertex. Note which solver method.

TASK 1 - the tie-break, in the core, default OFF
- Implement a post-optimal tie-break as a provider/config option, e.g.
  `respiration.tiebreak: none | pfba | min_o2 | max_o2`, default `none`. `pfba`: fix growth at its
  optimum (within a stated tolerance) and minimise total absolute flux. `min_o2`/`max_o2`: fix
  growth, then minimise/maximise the O2 exchange - these are the bounds of the face and are there
  for reporting, not for use. Every O2 the likelihood consumes goes through this path when the
  option is on.
- Seven-strain gate with the option OFF: 79/79, byte-identical. That proves the plumbing is inert.
- Turn on `pfba` for eciML1515 only, in its strain config. Re-run the D3a instrument exactly (fresh
  vs reused model, theta then theta again, all six fits): every cell must be 0.0000. Report the
  table. Then report O2 at Parsa's theta for E LB at 37/40/45/50 C under none / pfba / min_o2 /
  max_o2 - the reader should see where on the [0, 190] face pfba lands.
- Report the cost: s per likelihood evaluation before and after, single process.
- If pfba does not reach 0.0000 on any cell, STOP on that cell and report - a tie-break that leaves
  a face is not a tie-break.

TASK 2 - the variance, following from D0
- Make the minimal change D0 identified so that the respiration term's variance reflects the
  model's predictive granularity. The expected form is a log-scale term with a fitted scale
  (`disc_resp` or its corrected version) whose prior admits values of order the jumps P9 measured.
  Derive the floor from P9: the distribution of |delta log O2| across the 0.05 sd steps at the
  cliffs, reported as a number with its source line. State the prior, before and after, and why.
- If D0 shows the term is already log-scale with an adequate prior and the cliffs are something
  else (e.g. the term is per-temperature with one cold point dominating), say so and make THAT
  minimal change instead. Report what you did and why, not what this prompt guessed.
- Show the arithmetic on P9's three decomposed jumps: the log-likelihood step across each under
  the old term and the new one, at the same theta. The new steps should be single digits.
- Gate: seven strains with the change OFF, 79/79. On for eciML1515 only.

TASK 3 - prove the surface is smooth BEFORE sampling
Re-run P9's instrument under (a) tie-break only, (b) variance only, (c) both, on P9's twelve
lines that read ROUGH, at the same MAP, fresh model per evaluation, single process.
- Report per line and per condition: sign-change count, largest single step as a fraction of
  range, largest step in units. Apply P9's rule (written there; quote it).
- The three-column table is the evidence that each half does what it claims: (a) should change
  only E/F-type lines if any; (b) should cut every cliff's height; (c) should read SMOOTH.
- Also the D3a table under (c): still 0.0000.
- If (c) does not read SMOOTH: STOP. Report which lines remain rough and decompose them as P9 did.
  Do not proceed to TASK 5. The surrogate route is a separate decision.

TASK 4 - re-gate, and say what the gate now means
The P3 gate is a port-fidelity check against Parsa's computation. Under (c):
- Growth R2 at Parsa's theta, all ten: must be unchanged (neither half touches growth). Report.
- Respiration R2 at Parsa's theta for D: unchanged (D's O2 was unique). For E and F: report old vs
  new, and state that the difference is the width of the face, not a regression - the old number
  was one arbitrary point of it.
- Write the restated gate criterion into reports/P3_gate/README.md as a dated note: growth
  fidelity unchanged; respiration fidelity for D unchanged; E/F respiration now deterministic and
  compared at the pfba point. Do NOT rewrite the gate's history.
- Seven-strain gate ON for the Candida strains too, as INFORMATION only: does pfba change their K5
  proton-supply figures? Report; do not adopt for them - that is a K-series decision.

TASK 5 - one fit, to see whether tau plateaus at last
- D NLDM, both halves ON, P4's data/priors/c_max otherwise unchanged except the one prior TASK 2
  changed (stated). P7's driver, checkpoints every 250, 40 walkers, 16 processes, stretch move -
  the ORIGINAL sampler, so that a plateau is attributable to the surface and nothing else.
  Initialise from P4's final ensemble.
- Decision rule in P7's form, written before the run: MIXING if the last-three mean tau increment
  < 10 per block and tau_max at 1500 < 100; PARTIAL < 20; else NOT MIXING. 1500 steps; extend once
  to 2500 under PARTIAL.
- Report the checkpoint table beside P6's, P7's and P8's rows - four samplers/configurations on
  the old surface, one on the new.
- If MIXING: continue to the P6 target (n_eff >= 600 AND chain/tau >= 25). Report the converged
  posterior against P4's medians: which medians moved beyond their old (invalid) intervals, the
  new interval widths, the posterior/prior width ratio per parameter. Then the caveat P9 raised:
  re-run ONE line scan per parameter at the new MAP and state, per parameter, whether its
  posterior is gradient-determined (curved line) or wall-bounded (plateau with cliffs). Report the
  new respiration scale's posterior and what it says the model's respiration precision is.
- If NOT MIXING: STOP and report. State plainly that the surface was smooth by P9's instrument
  and the chain still did not mix, and what that leaves.
- Do NOT run D LB, D M9 or any E/F fit. Cost them.

TASK 6 - record
- reports/P10_respiration_likelihood/report.md: D0; the tie-break and its D3a table; the variance
  change and its arithmetic; the three-column smoothness table; the re-gate; the fit.
- docs/OPEN_ITEMS.md: 1.13 closed (tie-break chosen: pfba, with the face bounds reported); 1.15
  restated with the outcome; 3.21 closed or restated; 1.12 appended. New PI item if TASK 5 licenses
  the other eight fits: their cost. New PI item for the Candida pfba question from TASK 4.
- reports/synthesis/evidence.csv: rows for the tie-break, the variance change, the smoothness
  verdict, and the fit verdict. README correction note extended: section 7 and any section quoting
  E/F respiration R2. No re-render.
- Stamps.

VERIFY (report all)
1. TASK 0: #24 merged; baseline gates; D0 quoted - the current term's exact form and why the
   existing disc_resp did not absorb the cliffs.
2. TASK 1: option and default; gate 79/79 OFF; D3a table under pfba, all 0.0000; E LB O2 under the
   four tie-breaks at four temperatures; cost per evaluation before/after.
3. TASK 2: the minimal change made, the prior before/after, the P9-derived floor with its source;
   the three jumps' log-likelihood steps old vs new; gate 79/79 OFF.
4. TASK 3: the twelve-line, three-condition table; P9's rule quoted; the verdict under (c); D3a
   under (c).
5. TASK 4: growth R2 unchanged (10); D respiration unchanged; E/F respiration old vs new with the
   face-width explanation; the dated gate note; the Candida information run.
6. TASK 5: the rule quoted before the run; the checkpoint table with the four old rows; the
   verdict; if converged, the posterior comparison, width ratios, and the gradient-vs-wall
   classification per parameter.
7. TASK 6: OPEN_ITEMS items; evidence rows; README note; stamps.
8. `git diff main --stat`: src/etcgem (two options, default OFF), strains/eciML1515 config (two
   options ON, one prior), reports/P10_respiration_likelihood/, P3_gate README note, OPEN_ITEMS,
   evidence.csv, synthesis README, stamps, one fit output. Nothing else. No other strain's config
   touched.

CONSTRAINTS
- Both changes are core options, default OFF; the seven-strain gate must be byte-identical with
  them OFF before either is turned on anywhere.
- Each half is gated separately on the D3a table and P9's lines before both are combined.
- TASK 0's reading of the existing term governs TASK 2. The change is minimal and follows from
  D0, not from this prompt's guess.
- No sampling until TASK 3 reads SMOOTH. A surface that is still rough STOPS the run.
- TASK 5 uses the original sampler so a plateau is attributable to the surface.
- No other prior, no other parameter, no data, no c_max changes. No E/F fit. No other strain's
  fit. No default adopted for Candida.
- A fit that does not mix is reported, never extended silently, never quoted.
- Autonomous; commit in parts: "P10: D0", "P10: tie-break", "P10: variance", "P10: smoothness",
  "P10: re-gate", "P10: fit", "P10: record".
```
