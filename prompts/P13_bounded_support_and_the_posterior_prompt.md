# Claude Code prompt — P13: replace the support discount with a bounded penalty, then earn the posterior (autonomous, ~4 h then ~20 h of runs)

Run from the project root (`.../MICROADAPT/etcGEMs`), on `../etcGEMs-venv`. **Merge PR #27 (P12)
first**, server-side, matching #14–#26; then `git switch main`, `git pull`, branch `p13/support`.
Nothing is running in this tree. **Y3 may be running in `../etcGEMs-work`** — do not touch it, and
expect to share the machine with it for its first two hours (it is arithmetic, not solves).

**Where this stands, and what is now known.** P12 settled the mode question: **one live basin**, its
best point log L = −7.186 (p38), beating the nested sampler's own best sample (−7.396). The only
separated basin is **dead** — b3, dTm = 0.0004, peak predicted growth 0.000 /h — and it scores at
all only because the support weight charges it −0.017 instead of a full respiration penalty. So
P11's seed disagreement was **one basin explored to two different depths**, not multimodality; that
reading is retracted in P12's record and 1.19's original diagnosis (insufficient live points for a
broad 16-D basin) was right.

**Two things follow, and this prompt does both.**

1. **The support weight discounts rather than bounds** (P12 addendum 1): it hands back 16.7
   log-likelihood units at a dead point against ~1.2 at every live one. It multiplies the
   *respiration* term only — the growth term is linear and charges a dead model in full — so the
   fix belongs there. **The recommended bounded form: impute O₂ = 0 when the model does not grow,
   floor it at the existing ε before the log exactly as the 1.42 floor already handles small
   values, and pay the full respiration penalty.** That is large, finite, undiscounted, and
   continuous — O₂ falls to zero continuously as growth does, so there is no step for a cliff to
   form on. The hard mask was a step; the weight is a ramp; imputation is neither. **Treat this as
   the leading candidate, not as settled** — TASK 1 tests it against the alternatives and reports.
2. **Then earn the posterior.** With the discount gone, basin 2 should cease to exist and the
   surface should be unimodal by construction rather than by threshold. Two nested runs at
   nlive ≥ 800 with different seeds, which is what 1.19 asked for and 1.17 is blocked behind.

**What this prompt must not do.** It does not touch the growth term, the 1.42 floor, the pFBA
tie-break, the priors, the data or `c_max`. It does not implement the lexicographic tie-break —
that is a separate, later change (1.22) that pays back on the remaining eight fits, not on these
two, and adding it here would confound the runs.

NOTE TO USER: launch in an auto-approving mode. TASKs 0–3 are about four hours; TASK 4 is two
nested runs of roughly ten hours each, run **sequentially** (they each want 16 processes and P11
measured only 8.5/16 utilisation from stragglers, so overlapping them buys little and confounds
the timing). Expect: work this afternoon, run 1 overnight, run 2 tomorrow.

REFERENCE, read first: `reports/P12_modes/report.md` and DECISIONS D1–D7 (the basin map, the
addendum-1 weight characterisation, the barrier rule); `reports/P10_respiration_likelihood/`
(the term's current form, the floor, the tie-break); `reports/P11_nested/` (the dynesty wiring,
its proofs, `first_update`, the cost model); `reports/P9_surface/` (the line-scan instrument);
`docs/OPEN_ITEMS.md` §0, 1.12, 1.15, 1.17, 1.19, 1.21.

---

```
Work AUTONOMOUSLY; commit in parts, prefixed "P13: "; maintain reports/P13_support/DECISIONS.md
FROM THE FIRST JUDGEMENT CALL. Standing rules carry over. Check exit codes explicitly, never
`cmd && check`. Branch from main after the merge; do not push to main; end in a PR that is NOT
merged.

TASK 0 - merge; baseline; state which of R1-R4 this run moves
- Merge #27; switch; pull; branch. Gates with the options OFF: 79/79, 60/60.
- Read docs/OPEN_ITEMS.md sections 0a-0c. In DECISIONS.md D0 state which of R1-R4 this run moves
  (expected: R1, and only R1) and which it does not. If your findings later suggest otherwise,
  say so explicitly rather than widening the claim quietly.
- Record the baseline: log L at p38, theta_A and b3 under the CURRENT likelihood, single process,
  fresh model, from P12's committed points. These are the numbers every later comparison uses.

TASK 1 - choose the bounded form by testing three, not by assuming one
The weight exists because a dead model returns NaN for O2 and something must score it. Three
candidate replacements, all applied to the RESPIRATION term only, all default OFF in the core:
  (i)   IMPUTE: O2 := 0 when growth is at or below the death threshold, floored at the existing
        epsilon before the log; full penalty. (The recommended form.)
  (ii)  CLAMP: keep the weight's functional form but floor it at a stated minimum (e.g. 1.0, i.e.
        no discount at all, mask retained for NaN only).
  (iii) CURRENT: as is, for comparison.
- State the death threshold you use and where it comes from (the existing support handling
  presumably defines one - read it, do not invent one).
- For each of the three, report at p38, theta_A, b3 and P12's ten other converged endpoints:
  total log L, the growth and respiration terms separately, and the change from CURRENT.
- The decisive number: **the log L gap between the live basin's best point and b3** under each
  scheme. Under CURRENT it is ~11.7. Report it under (i) and (ii).
- Continuity check, which is what P10 was defending against: for scheme (i), scan the growth
  prediction through the death threshold - 41 points along a direction that carries the model
  from living to dead - and report the largest single step in the respiration term. If imputation
  introduces a step above 1 log-likelihood unit, it is a mask in disguise; say so and prefer (ii).
- Choose one, on the evidence, and record why in DECISIONS.md. If (i) and (ii) are equivalent on
  every measure, prefer (i) as the more principled and say that is why.

TASK 2 - gate it, then turn it on for eciML1515 only
- Seven-strain gate with the new option OFF: 79/79 and 60/60, byte-identical. That proves the
  plumbing inert.
- ON for eciML1515 in its strain config. Nothing else changes.
- Re-run the P3 gate: growth R2 at Parsa's theta must be unchanged (this touches respiration
  only). Report D's respiration R2 old and new, and add a dated line to reports/P3_gate/README.md
  extending P10's note. Do not rewrite the gate's history.

TASK 3 - confirm the surface, and confirm basin 2 is gone
- Re-run P11's twelve line scans under the chosen scheme, at p38 (the better optimum), by the
  ABSOLUTE rule: SAMPLEABLE if no 0.05 sd step exceeds 5 log-likelihood units. Report per line
  the largest step, beside P11's numbers at theta_A. **Pay particular attention to the cold lines
  (15-25 C)**: P11's sampleability was measured on the weighted likelihood and the cold end is
  exactly where the support handling acts. If any cold line now exceeds 5 units, STOP and report
  - the bounded form has reintroduced a cliff and TASK 4 must not run.
- Re-optimise from b3's starting point under the chosen scheme, same optimiser and 3,000-evaluation
  cap as P12 TASK 2c. Report where it goes. If it now descends into the live basin, basin 2 was an
  artefact of the discount and the surface is unimodal by construction; say so plainly. If it
  stays put, report its new log L and the barrier to the live basin under P12's 5-unit rule.
- Report the number of basins under the chosen scheme as one sentence with its evidence.

TASK 4 - the two runs, SEQUENTIALLY, with the stopping rule written first
- dynesty, P11's wiring and its proofs re-verified in one line each (prior transform, pool ==
  single-process at p38 to 1e-4, checkpoint restore). Add `first_update={'min_eff': 30}` - P11 D4
  measured ~1 h of single-core unit-cube phase without it. State every setting.
- nlive = 800, `rslice`, dlogz < 0.1, two runs with DIFFERENT seeds, run one after the other, not
  concurrently. Checkpoint every 30 minutes. Wall-clock cap 16 h each; if a run hits the cap,
  checkpoint cleanly, report STALLED with a projection, and do NOT start the second run - report
  and stop, because a second stalled run answers nothing.
- Write BEFORE running, and quote it in the report: AGREED if the two log Z agree within their
  combined reported error AND no posterior median differs by more than two Monte-Carlo errors;
  DISAGREED otherwise, reported with the same table P11 produced.
- Progress line every 250 iterations to reports/P13_support/run.log: iteration, evaluations,
  efficiency, log Z, dlogz, wall-clock, evals/s.

TASK 5 - what the posterior is, if it AGREED
- Medians and 5/95 intervals for all sixteen parameters, importance-weighted (state the
  resampling), beside P4's medians and P11's main-run values.
- Posterior/prior width ratio per parameter. Then the classification P11 pioneered: one line scan
  per parameter through the new median, each labelled GRADIENT-DETERMINED, WALL-BOUNDED or FLAT.
  P12 found f_metab pinned at 0.28000 and f_maint at ~0.35 in all twelve endpoints from every
  starting point - report whether the posterior agrees that they are flat.
- **dTm's posterior, with its interval.** P12 found the live basin spans -3.07 to -4.49 K and the
  only dTm = 0 point is the dead basin. State the credible interval and whether zero is excluded.
  That is the number item 1.20 turns on; report it, do not interpret it.
- R2 for growth and respiration at the posterior median, against P4's and Parsa's, with the floor
  and the new support form named beside the respiration figure.
- Cost the remaining eight fits (1.17) at the measured rate, F LB still HELD.

TASK 6 - record and reconcile
- reports/P13_support/report.md: the three schemes and the choice; the gate; the surface and the
  basin count; the runs; the posterior or the stall.
- docs/OPEN_ITEMS.md: 1.21 closed with the form chosen; 1.19 closed or restated; 1.12 appended;
  1.17 unblocked with costs if AGREED. **Strike step 5 of section 0b** (per-basin sampling) per
  P12's recommendation (c), leaving a dated note saying why rather than deleting the line.
- reports/synthesis/evidence.csv: rows for the support form, the basin count, the agreement
  verdict, and dTm's interval. README correction note extended - section 7 must now say the
  convergence problem was a cliffed likelihood and a support discount, not a sampling budget.
  No re-render.
- **Reconcile against 0c** in the report's closing section: which of R1-R4 moved; what is
  retracted or qualified by dated note (numbers unedited); what this does NOT license.
- Stamps.

VERIFY (report all)
1. TASK 0: #27 merged; gates; D0's R1-R4 statement; the three baseline log L values.
2. TASK 1: the three schemes at thirteen points; the live-dead gap under each; the continuity
   scan through the death threshold; the choice and its reasoning.
3. TASK 2: gate 79/79 and 60/60 OFF; P3 growth R2 unchanged; D respiration R2 old/new; the dated
   gate note.
4. TASK 3: the twelve lines under the absolute rule with P11's beside them, cold lines called out;
   where b3 goes; the basin count in one sentence.
5. TASK 4: settings; the agreement rule quoted from before the runs; per-run iterations,
   evaluations, wall-clock, dlogz, log Z +/- error, n_eff; AGREED or DISAGREED.
6. TASK 5 (if AGREED): the sixteen-parameter table; width ratios; the GRADIENT/WALL/FLAT lists;
   dTm's interval and whether zero is excluded; the R2 table; the 1.17 costs.
7. TASK 6: OPEN_ITEMS items including the struck 0b step 5; evidence rows; README note; the 0c
   reconciliation; stamps.
8. `git diff main --stat`: src/etcgem (one option, default OFF), strains/eciML1515 config (one
   option ON), reports/P13_support/, P3_gate README note, OPEN_ITEMS, evidence.csv, synthesis
   README, stamps, two run outputs. Nothing else.

CONSTRAINTS
- The support form is chosen by testing three, not by assuming the recommended one.
- Respiration term only. The growth term, the 1.42 floor, the tie-break, the priors, the data and
  c_max are untouched.
- No lexicographic tie-break here (1.22). It would confound the runs.
- No sampling until TASK 3 reads SAMPLEABLE on every line, cold lines included.
- The two runs are SEQUENTIAL and use different seeds. A stalled first run stops the task.
- The agreement rule is written before the runs and not revised after.
- Do not touch ../etcGEMs-work or anything Y3 is doing.
- Either verdict is the deliverable.
- Autonomous; commit in parts: "P13: schemes", "P13: gate", "P13: surface", "P13: run 1",
  "P13: run 2", "P13: posterior", "P13: record".
```
