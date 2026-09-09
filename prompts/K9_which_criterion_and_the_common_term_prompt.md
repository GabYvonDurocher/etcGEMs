# Claude Code prompt — K9: which criterion should Figure 4 use, and does the ~5.6 K common ceiling term generalise? (autonomous)

Run from the project root (`.../MICROADAPT/etcGEMs`). Follows K8 (PR #11 — merge it in TASK 0).

Two questions, both raised by K8, both answerable from what is already in the repository.

## Question 1 — the same quantity, two criteria, a threefold difference

Figure 4's claim is a ratio: how much interspecies ΔTm the model REQUIRES against how much is
AVAILABLE. K8 showed the requirement depends on which criterion you ask it under:

| criterion | required interspecies ΔTm | against the measured congeneric 1.6 °C |
|---|---|---|
| growth below the 0.05 h⁻¹ detection floor at 40 °C (what Fig 4 uses) | **13.57 °C** | 8.5× |
| CT_max matches the observed thermal limit (K8) | **~5 °C** | ~3× |

Both are defensible. They are not the same question — one asks the model to kill a relative at a
particular temperature, the other asks it to reproduce where the organism actually dies — and they
demand threefold different things of the same quantity. One of them puts the requirement within
about threefold of a directly measured congeneric difference, which is a materially different
sentence from the one the figure currently carries.

**A caution that must be tested, not assumed.** K8's ~5 °C may be less independent than it looks:
the four models predict near-identical ceilings, so "the offset difference needed to match observed
ceilings" could be close to a restatement of the observed ceiling difference itself. If so it is not
a model-derived requirement at all, and must not be quoted as one. Establish this before anything
else in TASK 2.

## Question 2 — the common term, now a quantity rather than a hypothesis

K8's cross-organism check found *E. coli*'s tuned row needed **−5.6 K against a MEASURED meltome**,
taking its ceiling gap from +5.9 to −0.01. Measured melting temperatures cannot carry predictor
bias, so this is a separate component from the Candida predictor artefact: **even when the melting
temperatures are right, cells die about five degrees before the model says their enzymes unfold.**

This was claimed as universal earlier in the project on two data points and the claim was wrong —
K4's seven-strain table found *M. maripaludis* at −0.2 and *Synechocystis* at +1.7, so it is not
universal. It is now properly separated from the predictor artefact and pinned to one organism.
**Whether it generalises is a genuine open question**, and this prompt tests it rather than assuming
either way. K8 already flagged the confounds: the methanogen and phototroph draw their Tm from a
mesophile prior built on *E. coli*'s meltome rather than from a sequence predictor, their median Tm
are higher than Candida's, and the methanogen runs at a calibrated turnover scale that may have
absorbed a gap.

NOTE TO USER: launch in an auto-approving mode. No emcee. Deterministic solves and comparisons.
P4 may still be running on `strains/eciML1515/` — check, and read E. coli from committed outputs
rather than writing to it if so.

REFERENCE, read first: `reports/K8_tm_bias/report.md` and `DECISIONS.md`,
`reports/K7_envelope/report.md`, `reports/candida_thermal_limit/K2_core_thermal_form.md` (how the
13.57 °C requirement is computed), `docs/CANDIDA_DISCUSSION_2026-09-07.md` §1 and §4, and
`reports/predictor_calibration/report.md` (A1's measured benchmark).

---

```
Work AUTONOMOUSLY; commit per task, prefixed "K9 TASK n: "; maintain reports/K9_criterion/DECISIONS.md
FROM THE FIRST JUDGEMENT CALL. Print a final summary with each task DONE / PARTIAL / STOPPED.
Standing rules carry over. Check exit codes explicitly, never `cmd && check`. $CANDIDAS_ROOT is
READ ONLY. Branch `k9/criterion`; TASK 0 is the only write to `main`; end in a PR that is NOT merged.
Change no default.

TASK 0 - merge K8
- Merge PR #11 (`k8/tm-bias`) --no-ff. Verify with exit codes checked: Candida gate 79/79 with
  $CANDIDAS_ROOT unset, seven strains byte-identical, `stamp_reports.py --check` passes. Push,
  close, delete branch. If anything fails, stop.
- Report whether P4 has landed.

TASK 1 - is the ~5 °C requirement independent of the observed ceilings, or a restatement of them?
This gates everything downstream. Answer it first and plainly.
- The four models predict near-identical CT_max. If the required offset difference simply equals the
  observed ceiling difference, the ~5 °C is arithmetic, not a model constraint.
- Test it: does the required offset difference change when the model changes? Recompute it under at
  least two model states that alter the ceiling — for instance the K5-repaired versus unrepaired
  model, and with and without the carbon cap — and report whether the required difference moves.
  If it tracks the observed ceiling difference regardless of the model, say so.
- Report the observed CT_max spread across the four species alongside the required offset spread. If
  they are the same number to within noise, that is the answer.
- **If the ~5 °C is a restatement, say so plainly and do not soften it.** The comparison in Question 1
  would then be between a genuine model requirement (13.57 °C) and an arithmetic identity, and the
  table above must be corrected in the report and in the discussion notes.

TASK 2 - characterise both criteria properly, whatever TASK 1 concludes
- For the detection criterion, state exactly what it asks: growth below 0.05 h⁻¹ at 40 °C for each
  relative, with the uniform Tm shift applied to all enzymes. Report its sensitivity to the two
  choices inside it — the detection floor (sweep it, e.g. 0.01 to 0.10 h⁻¹) and the temperature
  (sweep 38 to 42 °C). A requirement that moves a lot with an arbitrary threshold is weaker than one
  that does not.
- For the ceiling criterion, state what it asks and its sensitivity to how CT_max is defined
  (the growth grid resolution, and whatever cutoff the descriptor uses).
- Report both requirements with those sensitivities, as ranges rather than points.
- Then recommend which criterion Figure 4 should use, with reasons, and say what changes in the
  figure's claim under each. Do NOT change the figure or any default; recommend and record.

TASK 3 - does the ~5.6 K common term generalise?
Test it; do not assume it either way. The earlier universal claim was wrong on two data points.
- Establish, per strain, the provenance of the Tm distribution: measured meltome, mesophile prior,
  or sequence prediction. Report the median and spread per strain alongside its ceiling gap.
- For each of the seven strains, compute what uniform Tm shift would bring predicted CT_max onto the
  observed limit. That number is the strain's total ceiling correction. Report all seven.
- Then decompose where you can: for strains with PREDICTED Tm, how much of the correction is
  attributable to A1's measured predictor bias (K8's method), and how much remains? For strains with
  MEASURED or PRIOR-BASED Tm, the whole correction is the common term by construction.
- State whether a common term of roughly 5–6 K is visible across strains, or whether E. coli is
  alone. Address K8's three confounds explicitly: the methanogen's calibrated turnover scale, the
  higher median Tm in the non-Candida strains, and the fact that the mesophile prior is itself built
  on E. coli's meltome (so those strains are not independent evidence).
- If the term does NOT generalise, say so as clearly as if it did. A one-organism observation
  honestly labelled is worth more than a pattern asserted across seven.

TASK 4 - what would a common term MEAN, if it is real
Short, speculative, and clearly labelled as such — one or two paragraphs, no modelling.
- If cells reliably die several degrees below where bulk unfolding predicts, list the candidate
  explanations that the model class cannot currently express, and what measurement would distinguish
  them. Membrane integrity, proton leak, ROS, chaperone capacity and in-vivo destabilisation relative
  to in-vitro meltome measurement are the obvious candidates.
- Note which of these the framework could express with work, and which it cannot.
- Do NOT model any of them. Label the section as speculation and keep it brief.

TASK 5 - record
- `reports/K9_criterion/report.md`: TASK 1's verdict first and prominently, then the two criteria
  with their sensitivities, the recommendation, the seven-strain decomposition, and TASK 4's short
  speculative section.
- Update `docs/CANDIDA_DISCUSSION_2026-09-07.md` §1 (the requirement table — correct it if TASK 1
  says the ~5 °C is arithmetic) and §4 (the ceiling table, with the decomposition). Dated additions
  beside the existing text; do not rewrite it.
- Update `docs/OPEN_ITEMS.md`. Re-run `scripts/stamp_reports.py`.

VERIFY (report all)
1. TASK 0: merge; gates; whether P4 had landed.
2. TASK 1: the verdict — is the ~5 °C independent or a restatement? With the evidence: required
   offset spread against observed ceiling spread, and whether it moves when the model changes.
3. TASK 2: both requirements as ranges, with the floor and temperature sensitivities; the
   recommendation and what changes under each criterion.
4. TASK 3: the seven-strain table — Tm provenance, median, ceiling gap, total correction, predictor
   component where applicable, residual; the verdict on whether ~5–6 K generalises; the three
   confounds addressed.
5. TASK 4: the speculative section, labelled.
6. DECISIONS.md from the first judgement call.
7. `git diff main --stat`; no default changed; nothing under `strains/eciML1515/` or `reports/ecoli_*`
   if P4 is running.

CONSTRAINTS
- TASK 1 gates the rest. If the ~5 °C is a restatement of the observed spread, the headline table in
  this prompt is wrong and the report must say so before anything else.
- Requirements are reported as ranges with their sensitivities, not as points. Both criteria contain
  arbitrary choices and the reader needs to see how much they matter.
- Do not change the figure, the criterion, or any default. Recommend and record.
- The common term is tested, not assumed. A negative is reported with equal prominence.
- TASK 4 is explicitly speculation and must be labelled as such. No modelling.
- Autonomous; commit per task.
```
