# Claude Code prompt — P12: map the modes before sampling them again (autonomous, ~2–3 hours)

Run from the project root (`.../MICROADAPT/etcGEMs`), on `../etcGEMs-venv`. **Merge PR #26 (P11)
first**, server-side, matching #14–#25; then `git switch main`, `git pull`, branch `p12/modes`.
Nothing is running.

**Read `refs/PettersenAlmaas_2023.pdf` before anything else.** It is the precedent for this task.
Pettersen & Almaas re-ran Li et al.'s SMC-ABC calibration of the yeast etcGEM with different seeds
and permuted priors and found that every run converged and each converged somewhere different
(their Fig. 1C–D); their toy example (Fig. 3) shows the mechanism — a bimodal surface on which the
sampler collapses onto one optimum per seed. They conclude the thermal-parameter posterior is
multimodal, the method assumes it is not, and the usual Bayesian interpretations fail. Their FVA on
equally-fit particles found cytochrome c oxidase flux "used extensively for some particles, not at
all in others" at the same growth rate — growth data cannot pin respiration — and they name
proteomics and fluxomics as the cure. Their chemostat evaluations were numerically unstable in
Gurobi and they propose lexicographic objectives: that is D3a and P10's tie-break, found
independently.

**Where this stands.** P11 made the surface sampleable (12/12 lines under an absolute five-unit
rule, 902 fresh evaluations) and ran two nested-sampling runs that both met the pre-registered
stopping rule and converged to *different answers*: log Z −22.886 ± 0.164 against −24.567 ± 0.185,
best log-likelihood −7.40 against −9.11, fifteen of sixteen medians apart by more than two
Monte-Carlo errors, dTopt 1.51 against 9.39. P11 retracted its own "converged posterior" claim in the
record. That was correct, and it is Pettersen & Almaas's Fig. 1 in our model.

**Why this is not a precision problem.** Seed 2 did not converge imprecisely; it converged
somewhere else, with a lower peak. Nested sampling is monotone in likelihood — once the live set has
shrunk past the prior volume holding a basin it cannot return — so each run keeps whichever basins
its initial live points landed in. OPEN_ITEMS 1.19 proposes two runs at 800 live points. That
doubles the initial sampling density; it does not establish how many basins exist or whether
*either* run found the best one.

**The one fact that is new against the precedent.** They have 2,292 per-enzyme parameters; we have
16 global ones. Multimodality in both means it sits in the thermal formulation, not the parameter
count. Say that in the report.

**It also reopens P6–P8.** Walkers split across basins that never exchange produce τ ∝ N with a
rotating carrier. P8 called the ensemble unimodal, but measured a chain initialised from P4's final
ensemble, which may already have collapsed into one basin.

**So: map the modes directly, with no sampler, then choose the sampler to fit the map.** dTopt at
1.5 versus 9.4 is two different explanations of the same thermal curve; that is a scientific result
if it holds, not a nuisance.

NOTE TO USER: launch in an auto-approving mode. Merges one PR. Line scans and a batch of local
optimisations, two to three hours on 16 cores with pFBA at ~1.35 s per evaluation. No nested run,
no MCMC.

REFERENCE, read first: `refs/PettersenAlmaas_2023.pdf`; `reports/P11_nested/report.md` and its
`task2_seed_compare` outputs (both runs' equal-weight samples and medians); `reports/P9_surface/` and
`reports/P11_nested/task3_lines.csv` (the line-scan instrument); `reports/P10_respiration_likelihood/`
(the likelihood in force: tie-break pfba, floor 1.42); `reports/P4_refit/` (the priors and the old
MAP).

---

```
Work AUTONOMOUSLY; commit in parts, prefixed "P12: "; maintain reports/P12_modes/DECISIONS.md FROM
THE FIRST JUDGEMENT CALL. Standing rules carry over. Check exit codes explicitly, never
`cmd && check`. Branch from main after the merge; do not push to main; end in a PR that is NOT
merged. Likelihood: P10's, both options ON for eciML1515, floor 1.42, fresh-model-safe evaluation
path, 16-process pool. Nothing about the likelihood or the priors changes.

TASK 0 - merge; commit the sequencing section FIRST; the two medians; the cost of an evaluation
- Merge #26; switch; pull; branch. Gates with options OFF: 79/79, 60/60.
- **The working tree already contains an uncommitted edit to `docs/OPEN_ITEMS.md`**: new sections
  0a (four requirements R1-R4), 0b (the sequence) and 0c (the reconciliation rule), written by
  the user BEFORE this run so that its results are reconciled against them rather than replacing
  them. Commit that edit AS ITS OWN FIRST COMMIT — "P12: the sequence and the reconciliation
  rule, recorded before this run's results" — before any analysis. Do not amend it, do not fold
  it into a later commit, and do not let this run's findings rewrite 0a-0c; append to them.
  If the tree does NOT contain that edit, STOP and report — it means the file was already
  committed or lost, and this run must not proceed on an unknown plan.
- Read 0a-0c and state, in DECISIONS.md D0, which of R1-R4 this run can move and which it cannot.
  P12 is expected to move R1 and to inform R3; it cannot touch R2 or R4. If the run's findings
  suggest otherwise, say so explicitly rather than quietly widening the claim.
- Take theta_A = P11 main-run posterior median, theta_B = P11 seed-2 posterior median, and
  theta_P4 = P4's median. Evaluate the log-likelihood at all three, fresh, single process, and
  report: total, and the per-temperature per-term decomposition (growth term, respiration term,
  support weight) for each. Which data points prefer A over B, and by how much? This is the
  first thing that says what the two modes ARE.
- Profile one evaluation: what fraction of the ~1.35 s is LP solve against model preparation
  (cobra bound-setting, constraint rebuilding, pFBA objective construction)? Pettersen & Almaas
  cut theirs 8.5x because 80 % was preparation. Report the split; recommend, do not act.

TASK 1 - the line between them
- 41 points along the straight line from theta_A to theta_B, extended 25 % beyond each end
  (61 points total), fresh model per evaluation. Report the profile. Is there a valley between
  A and B (two basins) or does log-likelihood rise monotonically from B to A (B is a shoulder
  of A's basin that seed 2 never climbed)? Report the depth of any valley in log-likelihood
  units and its location along the line.
- The same for theta_P4 to theta_A and theta_P4 to theta_B.

TASK 2 - local optimisation from the prior, to count the basins
This is the cruder cousin of Pettersen & Almaas's CrowdingDE niching search; use their
clustering convention so the maps are comparable.
- Draw N starting points from the prior through P11's proven transform (seed recorded). N = 96
  (six per core) as the base; extend to 192 if wall-clock allows.
- From each, a derivative-free local optimiser on the log-POSTERIOR (Powell or Nelder-Mead;
  state which and its tolerances; cap 600 evaluations per start). Record endpoint,
  log-posterior, log-likelihood, evaluations.
- Also start from theta_A, theta_B and theta_P4, so their basins are in the same set.
- Cluster the endpoints: standardise each parameter by the population sd, Euclidean distance,
  single linkage (their Methods, "Hierarchical clustering"), at a stated threshold; check
  stability to doubling and halving it. Report: number of basins; per basin its best
  log-likelihood, its centre (all sixteen), how many starts fell in, and the fraction of PRIOR
  volume it drained (starts landing there / N) - the number nested sampling needed and did not
  have.
- Which basin holds A, which B, which P4; whether any basin beats A.
- The separating parameters: per pair of basins, those whose centres differ by more than one
  within-basin sd. Expect dTopt; report what moves WITH it (dTm? dCp_scale? kcat_scale?). That
  compensation pattern is the physical content.

TASK 3 - what the basins mean, in the model's terms, without adjudicating
- For the two or three best basins: the thermal curve on NLDM at each centre (growth against T,
  15-50 C) against the measured points, one panel. Where do they differ - rising limb, optimum,
  ceiling, shoulder?
- O2 uptake likewise - AND, following Pettersen & Almaas's FVA: at each basin centre and each
  grid temperature, the FVA range of O2 exchange at optimal growth. If basins differ in
  respiration at equal growth fitness, that reproduces their cytochrome-oxidase result and is
  the direct reason the respiration term cliffed. Then the question the E. coli-first plan rests
  on: does OUR gas-exchange likelihood (the respiration term, with the floor) separate the basins
  that growth alone would not? Report the respiration-term log-likelihood per basin beside the
  growth-term one.
- One paragraph per basin saying what it is doing mechanistically, read from the parameters -
  e.g. "small Topt offset, large stability shift" against "large Topt offset, stability at the
  meltome". Do not say which is right. If one basin puts dTm near zero - removing the need for
  the -5.6 K shift that OPEN_ITEMS section 0 lists as the model's softest point - say so
  prominently. That is the single most important thing this map could contain.

TASK 4 - what sampler the map licenses, stated as a recommendation with cost
Exactly one of:
  (a) ONE basin, seed 2 was a shoulder: initialisation density is the fix and 1.19 as written
      (800 live points, two seeds) is the right run. Cost from P11's rate.
  (b) TWO OR MORE basins of comparable height: sample EACH on a restricted prior (a stated box
      around its centre), combine evidences and posteriors weighted by TASK 2's volume
      fractions. Cost per basin.
  (c) TWO OR MORE basins, one dominant by > 5 log-likelihood units and > 90 % of drained prior
      volume: sample the dominant one on a restricted prior; report the minor basins beside it.
      Cost.
  (d) Something else - say what.
- In every case: is P8's "unimodal, isotropic" reading now retracted, qualified, or intact?

TASK 5 - record
- reports/P12_modes/report.md: the decompositions, the profiles, the basin table, the curves
  and FVA, the mechanistic paragraphs, the recommendation, the evaluation profile. Frame the
  whole against Pettersen & Almaas: same phenomenon, 16 parameters against 2,292, therefore in
  the formulation.
- Dated notes, numbers untouched: in reports/Y2_regime_posterior/report.md and the Y1 report -
  the Zenodo posterior is one seed's mode (Pettersen & Almaas Fig. 1C-D); Y2's 92 % and its nine
  limit-carrying enzymes are conditional on that mode. In reports/P8_ridge/report.md if TASK 4
  retracts or qualifies it.
- docs/OPEN_ITEMS.md: 1.19 restated per TASK 4. New PI items: (i) a basin that removes the dTm
  shift, if found; (ii) whether to re-run Y2 across modes, which needs their published particle
  sets or a CrowdingDE run on the yeast model; (iii) the evaluation-cost recommendation from
  TASK 0. Section 4b: one line - their chemostat instability is the LP-face defect (D3a), found
  independently; their proposed fix is P10's lexicographic tie-break.
- reports/synthesis/evidence.csv: rows for the basin count, the separating parameters, the
  FVA-at-equal-fitness result, the recommendation; and one for candidate (d): published prior
  art now exists for instability and under-identification (Pettersen & Almaas 2023) - what
  remains ours is the mechanism, the asymmetry, the predictor validation, and the data they
  call for. Record; do not adjudicate. README correction note extended. No re-render.
- **Reconcile against section 0 (0c), in the report's closing section, as four short
  statements:** which of R1-R4 this run moved and how far; what it retracts or qualifies in an
  earlier report (dated notes, numbers unedited); what it does NOT license; and whether step 1
  of the sequence in 0b is now closed and step 2 (the dTm decision) is better informed - in
  particular, what each basin's dTm is and whether any sits near zero. APPEND to 0a-0c; do not
  rewrite them.
- Stamps.

VERIFY (report all)
1. TASK 0: #26 merged; gates; log-likelihood at A, B, P4 with per-term decomposition; the
   evaluation-time split.
2. TASK 1: the three profiles; valley or slope; depth and position.
3. TASK 2: N, optimiser, tolerances, cap; the basin table with volume fractions; clustering
   stability; A/B/P4 assignment; whether any basin beats A; separating parameters per pair.
4. TASK 3: thermal and O2 curves per basin; O2 FVA at equal fitness per basin; growth-term
   against respiration-term log-likelihood per basin; the mechanistic paragraphs; the dTm
   statement.
5. TASK 4: which of (a)-(d), with cost; the P8 statement.
6. TASK 5: the Pettersen & Almaas framing; the Y1/Y2/P8 notes; OPEN_ITEMS items; evidence rows;
   README note; stamps.
7. `git diff main --stat`: reports/P12_modes/, dated lines in Y1/Y2/(P8), OPEN_ITEMS,
   evidence.csv, synthesis README, stamps. Nothing under src/ or strains/. No sampler run.

CONSTRAINTS
- No nested run, no MCMC. Optimisation, line scans and FVA only.
- Nothing about the likelihood, the floor, the tie-break or the priors changes.
- Basin count and volume fractions are reported with the clustering threshold and its
  stability, not as bare numbers.
- TASK 3 describes; it does not say which basin is right. TASK 4 recommends; it does not run.
- Y1/Y2 numbers are not edited; they are scoped by dated note.
- Autonomous; commit in parts: "P12: fixed points", "P12: lines", "P12: basins", "P12: curves
  and FVA", "P12: record".
```
