# Claude Code prompt — Y3: is the −4 K stability shift biology, or is it having 16 global parameters instead of 2,292 per-enzyme ones? (autonomous, ~2 h — a screen, not the experiment)

**Run from `../etcGEMs-work`, NOT from the primary checkout.** P13 is running there and owns it for
the next day. `etcGEMs-work` is a detached checkout of `main`; make a branch and work there.

**Environment:** use `../etcGEMs-venv`. This is a screen — arithmetic on files P12 already wrote,
plus a few hundred targeted evaluations. It should not fight P13 for cores for more than a few
minutes at a time; if a step would take more than ~15 minutes of solving, say so and defer it
rather than slowing the runs.

**The finding this screens.** P12 established that every living optimum in the E. coli model needs
`dTm` between −3.07 and −4.49 K against a **measured** meltome, and that the only dTm ≈ 0 point
anywhere in the map (b3) is a model that does not grow at all. So §0b step 2's hope — that
constraining dTm to the meltome would collapse a stability-shift mode — is inverted: there is no
second living mode. Constraining dTm does not select between explanations; it removes the fit. The
shift is **load-bearing**.

**Two readings, and they are distinguishable.**
  * **Biology.** In-vitro melting temperature is not in-vivo functional inactivation. Crowding,
    chaperones and ligand binding all shift apparent stability, and a systematic few-K offset is
    physically unremarkable. On this reading the meltome is right and the model is asking it the
    wrong question.
  * **Parameterisation.** Li et al. had measured Tm, needed **no** shift, and resolved the identical
    tension through ΔCp‡ and kcat degeneration — with **2,292 per-enzyme parameters**. We have one
    global `dTm`. With per-enzyme kcat you can degrade the enzymes that actually limit; with a
    global scalar you can only move the whole meltome down. On this reading the −4 K is an artefact
    of resolution, and per-enzyme thermal parameters would remove it.

**What this prompt is and is not.** It is the **cheap screen that decides whether the expensive
route is worth taking.** The expensive route — DLTKcat inference over the eciML1515 proteome, then
per-enzyme Topt wired into the thermal layer — is two to three days and a core change, and must not
be started on a hunch. This screen costs two hours and most of its data already exists.

**Do not implement anything.** No per-enzyme layer, no DLTKcat run, no prior change, no fit.

REFERENCE, read first: `reports/P12_modes/task2c_converged.csv` (twelve converged endpoints with
all sixteen parameters), `reports/P12_modes/report.md` and DECISIONS; `reports/Y1_yeast_audit/`
PART D (what Li's calibration moved: Topt 10.9 → 7.1 °C, Tm 4.9 → 4.0, posterior Tm vs experiment
r = 0.97, and the nine limit-carrying enzymes at measured prior Tm 40.5–43.8 °C);
`reports/K8_tm_bias/` and `reports/predictor_calibration/` (A1's measured Seq2Tm bias, for the
Candida contrast); `refs/Lietal2021NatComms.pdf`; `refs/DLTKcat*.pdf`; `docs/OPEN_ITEMS.md` 1.20,
§0a R3.

---

```
Work AUTONOMOUSLY; commit in parts, prefixed "Y3: "; maintain reports/Y3_tm_shift/DECISIONS.md
FROM THE FIRST JUDGEMENT CALL. Standing rules carry over. Check exit codes explicitly, never
`cmd && check`. In ../etcGEMs-work: branch `y3/tm-shift` from the detached main; do not push to
main; end in a PR that is NOT merged. Write NOTHING under ../etcGEMs and do not disturb P13.

TASK 0 - premise, and the discipline this screen needs
- Confirm the worktree, the branch, and that the interpreter is ../etcGEMs-venv. Confirm P13 is
  running in the primary tree and that you will not write there.
- Read docs/OPEN_ITEMS.md 0a-0c. State in D0 which of R1-R4 this screens (expected: R3, and only
  R3 - it informs a decision, it does not move R1, R2 or R4).
- **Write the decision rule into DECISIONS.md BEFORE computing anything**, in this form:
    PARAMETERISATION if dTm is strongly traded against the catalytic parameters - a partial
      correlation with dCp_scale, kcat_scale or dTopt across the live endpoints above |0.6|, AND
      a compensating direction exists along which log L changes by less than 2 units while dTm
      moves at least 2 K.
    BIOLOGY if dTm is close to orthogonal to all of them - no partial correlation above |0.3| -
      and no such compensating direction exists.
    AMBIGUOUS otherwise, which is a legitimate outcome and is reported as such.
  Do not revise the rule after seeing the numbers.

TASK 1 - what the existing endpoints already say (arithmetic, no solves)
- From `task2c_converged.csv`, take the LIVE endpoints only (exclude b3 and any point whose peak
  predicted growth is below half the observed 2.076 - P12 TASK 3 has the peaks; state which you
  excluded and why).
- Report the correlation matrix over the sixteen parameters across those endpoints, and
  specifically dTm against dCp_scale, kcat_scale, dTopt, topt_scale and tm_scale: Pearson,
  Spearman, and the PARTIAL correlation of dTm with each controlling for the others.
- Report each endpoint's dTm beside its log L. Is the spread -3.07 to -4.49 K correlated with
  quality - do the better optima need less shift, or the same?
- Caveat it honestly: n is about ten, these are optima not posterior samples, and the correlations
  are over a set selected by an optimiser. Say what that does and does not support.

TASK 2 - the compensating direction, which is the decisive test (a few hundred solves)
Correlation across optima is suggestive; a direct scan is decisive.
- At p38 (the best point, log L -7.186), scan dTm from its value up to 0 in 21 steps, RE-OPTIMISING
  the catalytic parameters at each step - dCp_scale, kcat_scale, dTopt, topt_scale, tm_scale -
  with everything else held. Powell, a stated modest cap (300 evaluations is enough for five
  parameters), fresh model per evaluation.
- This is the profile likelihood of dTm with catalysis free. Report, per step: dTm, the
  re-optimised log L, the peak predicted growth, and the five re-optimised values.
- **The number that decides it:** how much log L is lost at dTm = 0 with catalysis free to
  compensate, and does the model still grow there? Under CURRENT support handling b3 sat 11.7
  units below the live optimum with zero growth. If catalysis can hold a living model at dTm = 0
  for a few units of log L, the shift is compensable and the finding is PARAMETERISATION-leaning.
  If growth still collapses, no amount of global catalytic freedom substitutes and it is
  BIOLOGY-leaning.
- If this exceeds ~15 minutes of solving, reduce to 11 steps and say so.

TASK 3 - the comparison with Li, stated precisely
- From Y1 PART D and the paper: their Tm was measured for 266/764 and population-mean for the
  rest; their calibration moved Topt (SD 10.9 -> 7.1 C) and left Tm at the meltome (r = 0.97);
  their nine limit-carrying enzymes had measured prior Tm of 40.5-43.8 C.
- State the structural difference in one paragraph: they had per-enzyme freedom in the catalytic
  term and used it; we have global scalars. Then say what TASK 2's profile implies about whether
  that difference explains our -4 K.
- **Do not claim their model needs no shift because per-enzyme freedom removed it** unless TASK 2
  supports it. The alternative - that yeast and E. coli genuinely differ - is not excluded by
  anything here, and the honest report says so.

TASK 4 - what the expensive route would cost, and what would make it worth it
- DLTKcat: read `refs/` for what it takes as input and returns, and report - not run - what an
  inference pass over the eciML1515 proteome would need (number of enzymes, input format, whether
  a GPU is required, rough wall-clock on CPU).
- The core change: describe what per-enzyme Topt would require in `src/etcgem` - how the thermal
  layer currently applies global scalars and what would have to become per-enzyme. Estimate the
  work in half-days and name what would need re-verifying (the seven-strain gate, at minimum).
- State the decision gate plainly: on this screen's verdict, is the expensive route worth taking?
  RECOMMEND with the evidence; do not decide, and do not start it.

TASK 5 - record
- reports/Y3_tm_shift/report.md: the rule as written before the data; TASK 1's correlations with
  their caveats; TASK 2's profile with the dTm = 0 result; the Li comparison; the costing; the
  verdict as one of PARAMETERISATION / BIOLOGY / AMBIGUOUS.
- docs/OPEN_ITEMS.md 1.20: the screen's verdict and what it licenses. §0a R3: the state column
  updated with what is now known.
- reports/synthesis/evidence.csv: one row for the profile-likelihood result at dTm = 0, one for
  the verdict.
- **Reconcile against 0c:** which of R1-R4 this moved (R3 only, and as a screen not a result);
  what it retracts or qualifies; what it does NOT license - in particular it does not license
  any statement about the Candida models, whose Tm is PREDICTED not measured and whose bias A1
  measured at +5.43 C, a different problem.
- Stamps.

VERIFY (report all)
1. TASK 0: worktree, branch, interpreter; P13 untouched; D0's R1-R4 statement; the decision rule
   quoted from before any computation.
2. TASK 1: which endpoints were excluded and why; the correlation and partial-correlation table;
   dTm against log L; the honest caveat on n and selection.
3. TASK 2: the profile - dTm, re-optimised log L, peak growth, the five catalytic values per step;
   the log L cost and the growth at dTm = 0; wall-clock.
4. TASK 3: the structural comparison; what the profile does and does not imply about Li.
5. TASK 4: DLTKcat's requirements; the core change in half-days; what needs re-verifying; the
   recommendation.
6. TASK 5: the verdict; OPEN_ITEMS 1.20 and R3; evidence rows; the 0c reconciliation; stamps.
7. `git diff main --stat` in ../etcGEMs-work: reports/Y3_tm_shift/, OPEN_ITEMS, evidence.csv,
   stamps. Nothing under src/ or strains/. Confirmation nothing under ../etcGEMs was written.

CONSTRAINTS
- A screen, not the experiment. Nothing is implemented: no per-enzyme layer, no DLTKcat run, no
  prior change, no fit.
- The decision rule is written before the data and not revised after.
- AMBIGUOUS is a legitimate verdict and is reported as prominently as the other two.
- Read-only on the primary checkout. Defer anything that would take more than ~15 minutes of
  solving while P13 runs.
- Nothing here licenses a statement about Candida, whose Tm is predicted and biased (+5.43 C, A1).
- Autonomous; commit in parts: "Y3: rule and correlations", "Y3: profile", "Y3: comparison and
  costing", "Y3: record".
```
