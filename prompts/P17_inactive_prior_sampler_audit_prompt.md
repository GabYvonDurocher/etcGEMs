# Claude Code prompt — P17: explain the inactive-prior failure before fitting any more biology (autonomous, diagnostic work until resolved)

Run from the project root (`.../MICROADAPT/etcGEMs`), using `../etcGEMs-venv`.
**Read the live repository state first. Do not repeat P16, merge anything automatically, or
assume either worktree is idle.** E-series work lives in `../etcGEMs-work`; leave it alone.
Create an isolated checkout on `codex/p17-inactive-prior` if needed, preserving the current
checkout and all uncommitted work. Carry the named, uncommitted P16 audit inputs into it explicitly,
with hashes and a manifest, rather than silently auditing an older committed state.

**The question is now computational and unusually sharp.** Configuration D's growth-law path
ignores sampled `f_metab`, but P16 still sampled it. If that premise is correct, and its prior is
independent, its exact posterior marginal MUST equal its prior. This is an analytical control:
no biological interpretation, growth data or assumed meltome shift is needed to know the answer.

The completed P16 audit found:

| diagnostic | seed 1 | seed 2 |
|---|---:|---:|
| log Z | -26.029894 +/- 0.109358 | -26.052380 +/- 0.099392 |
| actual final dlogz | 0.09999335 | 0.09995762 |
| importance-weight ESS | 5,987.56 | 3,252.25 |
| `f_metab` prior-CDF coordinate mean (expected **0.5**) | **0.319120** | **0.393715** |
| weighted KS distance from Uniform(0,1) | **0.290878** | **0.216146** |

Evidence agreement passes, but **14/15 marginal medians fail P16's agreement rule**, including
under a supplementary strand bootstrap. The saved arrays, weights and restored unit-cube
coordinates cross-check. These observations justify an investigation; they do **not** yet prove
that dynesty itself is wrong, that `slices=3` is the cause, or even that the inactivity premise
holds through every execution path. **Establish the premise before diagnosing its violation.**

The source files win over this table if new evidence has landed.

**What would count as progress.** A cause located in a reproducible example, a controlled change
that removes its effect, and independent verification that the correction preserves the intended
likelihood and target distribution. Another attractive converged run or another parameter fixed
would not answer the question.

**What this is NOT allowed to become.** Do not repair the biological infeasibility exemption,
change priors, enable measured allocation, fix another biological parameter, or start the D/E/F/M9
programme as a way to make the diagnostic pass. Those are separate questions. A computational
failure must not be absorbed into a changed scientific model.

REFERENCE, read first:
- `reports/P16_reduced/audit_report.md`, `audit_summary.json`, `audit_inputs.json`,
  `audit_agreement.csv`, `audit_strand_agreement.csv`, `audit_inactive_parameter.csv`;
  `audit_completed_runs.py`, `audit_sampling_uncertainty.py`.
- P16 `DECISIONS.md` D0–D7, `reduced.py`, `run_reduced.py`, both traces, logs and saved outputs.
- `reports/P11_nested/prior_transform.py` and its verification; P15's runner and crash analysis.
- `src/etcgem/calibration_multi.py`, `config.py`, `tpc.py`, `enzyme_cost.py`, `sectors.py`,
  `gasflux.py`; `configs/experiments/gasflux_configD.yaml`; the actual P16 fit definition.
- `docs/OPEN_ITEMS.md` section 0 and the dated 12 September P16 audit.
- The **installed** dynesty source and version. Read its actual runner, constrained proposal,
  bounding, multiprocessing/RNG, checkpoint and bootstrap implementations before attributing
  behaviour to a library. Use primary documentation/source if external verification is needed.

NOTE TO USER: launch in an auto-approving mode. This authorises the diagnostic experiments,
isolated computational fixes and confirmation runs below. **It does not authorise new biological
calibrations, changing the scientific model, or merging the result.**

---

```
Work AUTONOMOUSLY until the decisive-conclusion gate below is met. Maintain
reports/P17_inactive_prior/DECISIONS.md FROM THE FIRST JUDGEMENT CALL. Commit in parts,
prefixed "P17: ". End with a reviewable branch and an unmerged PR if repository access permits.
Do not push to main, merge, alter active runs, or include unrelated user changes.

Check exit codes explicitly; do not hide a failure behind the exit code of a later command.
Use the project interpreter. Record input hashes, software versions, seeds and resolved
configurations. Never overwrite P16 checkpoints, arrays, logs or prior audit tables.

AUTONOMY AND RESOURCE RULE
- Do not stop at "more investigation is needed", a suggested experiment, or the first plausible
  explanation. Perform the next experiment that distinguishes the surviving explanations.
- Cheap arithmetic and analytical controls first; real-model evaluations only where needed.
  Benchmark before expensive work. State each batch's hypothesis, stopping condition, seeds,
  expected cost and concurrency in DECISIONS before launch.
- Keep batches bounded (normally <=4 h, checkpoint at least every 30 min); a batch boundary is
  a review/checkpoint, not the end of the investigation. Continue with the next justified batch.
- Do not overlap expensive batches or monopolise workers already used by another task. Preserve
  machine responsiveness. Do not increase workers or buy resources to compensate for poor design.
- Revisit a rejected hypothesis only if new evidence gives a concrete reason. Keep a live table
  of hypotheses, discriminating tests and outcomes. No endless blind sampler-parameter sweep.
- If routine implementation choices arise, resolve and record them. Ask only for genuinely
  missing access/authority or a scientific-model change outside this remit. If externally
  blocked, preserve a restartable record and report the exact blocker; do not manufacture a
  decisive scientific conclusion just to satisfy the stopping instruction.

TASK 0 — freeze the evidence and pre-register the diagnostic rules
- Confirm worktree, branch, interpreter, running jobs, installed dynesty/numpy/scipy/solver
  versions and the precise code/configuration both P16 seeds executed. Check for changes during
  the runs, not merely the current HEAD. Distinguish known run provenance from reconstruction.
- Hash both checkpoints, samples, log weights, log likelihoods, summaries and traces. Include
  uncommitted inputs and the audit scripts in the manifest. Preserve originals read-only.
- Reproduce the two reported inactive-coordinate means/KS distances and the agreement failure.
  Use a second implementation independent of the existing TASK 5/audit functions.
- Write the hypotheses BEFORE experiments: reporting/weight alignment; wrong prior transform;
  hidden dependence or stateful likelihood; runner/checkpoint/chunking behaviour; RNG or worker
  state; inadequate constrained-prior exploration; bounding/proposal implementation; legitimate
  finite-run uncertainty. Add hypotheses later only with a dated reason.
- Pre-register the null diagnostics, replicate schedule and decision procedure below. Calibrate
  statistical thresholds with controls, not by choosing a tolerance after seeing P16's answer.

TASK 1 — is f_metab REALLY inactive, through the complete executed path?
- Trace prior transform -> 15-to-16 expansion -> worker initialisation -> perturbation ->
  temperature state -> allocation -> solver -> likelihood. Establish parameter order by name
  and index. Verify dTm insertion cannot shift another coordinate.
- Inspect every use of f_metab: initial model budget versus sampled perturbation, simplex checks,
  exception paths, log-prior/support and any context-dependent cached state. Check factorisation
  of the actual joint prior. Do not mistake a tight independent prior for fixed input data.
- At varied held-fixed active parameter vectors, vary ONLY f_metab across its full allowed
  support. Include both seeds' representative points, growing and low-growth regions, and
  boundary cases. Compare matrix/bounds/objective fingerprints, feasibility, growth, O2 and
  log likelihood. Start with a small informative set; expand only to resolve discrepancies.
- Use fresh models and reused models; permute evaluation order; compare serial and worker paths.
  Separate solver repeatability noise from a systematic f_metab effect. Do not declare numerical
  equality merely because rounded log-likelihoods match.
- If hidden dependence exists, locate its exact operation. Decide whether it is intended model
  semantics or an implementation defect. Derive the correct null rather than insisting on a
  uniform marginal. Demonstrate whether it quantitatively explains the recorded discrepancy.
- If inactivity holds, write the proof: p(f_metab | y) = p(f_metab), with its necessary assumptions.
  Transform by the EXACT truncated-prior CDF; report the expected natural-space distribution and
  the Uniform(0,1) expectation. Retain f_metab as a diagnostic control throughout this task.

TASK 2 — audit the inference output, including its uncertainty claims
No model solves unless TASK 1 demonstrated they are needed.
- Independently reconstruct normalised posterior weights from logwt/logZ. Check sum, finite
  values, row order, sample IDs, duplicate vectors, sample count, and inclusion of the final live
  points exactly once. Reconstruct saved arrays from restored checkpoints without modifying them.
- Check whether the periodic checkpoint is actually the terminal state. Account explicitly for
  incomplete chunks, final-live additions, resumed runs and any missing or duplicated tail.
- Recompute prior CDF coordinates independently and round-trip them through the forward transform.
  Report weighted ECDFs, means, quantiles and covariances. Do not use unweighted correlations.
- Reconcile stopping dlogz with logzerr. The current runner mislabels logzerr as dlogz_final;
  locate and correct that reporting bug in an isolated change, but do not mistake it for proof
  that the underlying samples are wrong.
- Audit uncertainty: importance-weight ESS is NOT an independent-draw count, and IID weighted
  resampling is not full nested-sampling uncertainty. Use independent runs/strands where suitable,
  with explicit limitations. Never attach an ordinary IID KS p-value to correlated weighted
  nested samples or treat hundreds of conditional-bootstrap errors as calibrated significance.
- If a reporting bug alone explains the failure, prove it with independently reconstructed
  results for both seeds. Still perform the matched analytical controls needed for confirmation.

TASK 3 — recover a known inactive prior on known targets
- Build a minimal diagnostic harness independent of the metabolic model, but using P16's actual
  prior transform, runner settings and parallel/serial paths as selectable components.
- Use at least (a) a smooth, analytically tractable target with known evidence and active
  marginals, plus an exactly independent nuisance coordinate; and (b) a target with known
  mixture weights/unequal-volume regions and exact inactive marginals. Keep dimensions comparable
  to P16 where informative. Derive or independently verify all reference answers.
- Include both a uniform nuisance and a transformed truncated-normal nuisance. Include at least
  one active known marginal: making the nuisance look uniform does not prove active inference works.
- Avoid using an everywhere-constant likelihood as the only control: whole-likelihood plateaus
  have separate nested-sampling behaviour. A likelihood constant ALONG an inactive coordinate
  is not by itself a positive-prior-volume atom in the likelihood distribution.
- Start with the exact P16 settings, across a predeclared set of at least five seeds on cheap
  controls. Compare evidence, inactive ECDFs, active marginals and region weights with truth.
- Use the replicate distribution to assess whether P16-sized deviations are plausible from the
  claimed finite-run uncertainty. Report effect sizes and uncertainty, not just pass/fail.
- Compare a plain uninterrupted library invocation with P16's chunked/checkpointed wrapper,
  then serial versus multiprocessing, changing ONE component at a time. Check random streams,
  worker seeding, queue reuse, initial live points and callable pickling where evidence points.
- If a cheap control reproduces the failure, reduce it to the smallest reproducer that retains
  it before spending another full night on the real likelihood.

TASK 4 — locate where independence is lost
- Trace the inactive coordinate through nested iterations and likelihood levels, not just the
  final marginal. Inspect initial live points, replacements, discarded points and final live
  points; record proposal ancestry and any repeated/stagnant coordinates available from the run.
- Distinguish an accidentally selected collection of ancestors from independent prior draws.
  Plot/check drift, strand dominance and association with active regions and likelihood level.
- If archived checkpoints cannot answer a question, run an instrumented diagnostic replay of the
  implicated stage. Do not present a replay started from a biased checkpoint as an unbiased
  new posterior. Use it to localise a mechanism, then confirm from fresh initialisation.
- Test slice length/mixing only if the evidence implicates it. An increased slice count is a
  controlled intervention, not a cure by definition. Keep likelihood, priors, bounds and seed
  protocol explicit. If needed, test an alternative bound or constrained-prior kernel separately.
- For a proven independent nuisance, an independent prior refresh conditional on the active
  coordinates is an exact diagnostic intervention. Use it to test the proposed mechanism.
  **It is not a sufficient repair:** uniformising the nuisance after the fact can conceal a
  biased active posterior. Evaluate active marginals and mixture weights against known truth too.
- Use a positive control that deliberately introduces a known dependency, to show the diagnostic
  can distinguish genuine information from sampling drift. Test any newly added independent
  nuisance coordinate as a separate check, without confusing extra dimension with an inert label.
- Keep numerical likelihood state/history separate from the biological infeasibility mask.
  Do not change the mask or penalty to rescue the inactive marginal.

TASK 5 — make and falsify the causal diagnosis
For each surviving explanation, state what observation would falsify it and perform that test.
- Produce a baseline-versus-intervention table: same target and priors, what changed, inactive
  marginal, active known marginals, evidence, region weights, runtime and seed-to-seed variation.
- Locate the responsible layer precisely: audit arithmetic; wrapper; prior/parameter wiring;
  stateful numerical evaluation; parallel RNG; insufficient exploration; or a specific library
  defect. Multiple contributing causes are allowed if their effects are separated.
- If a code defect is responsible, supply the smallest regression reproducer and isolated patch.
  Do not edit installed site-packages in place. Pin/version any diagnostic library patch and
  record its provenance so the effect can be reproduced elsewhere.
- If a computational setting is responsible, establish what makes it adequate, rather than
  declaring the largest setting tried successful. Use the pre-registered independent controls.
- If the original audit premise is false or the discrepancy is explained by finite-run
  uncertainty, demonstrate that quantitatively. Retract the premise plainly; this is a valid
  decisive outcome, provided active-posterior disagreement is still accounted for or delimited.
- A null-prior test is a necessary diagnostic, not a certificate of correct inference everywhere.

TASK 6 — independent confirmation, with the scientific model held fixed
- Write the confirmation protocol before running it, after the diagnosis has been established.
  Reserve fresh seeds not used to select the intervention. No threshold adjustment afterwards.
- Pass the analytical controls on at least five fresh seeds. Recover BOTH nuisance and active
  reference distributions, and reference evidence/region weights where defined, within the
  calibrated error budget. Investigate failures rather than dropping unfavourable seeds.
- Then test the relevant real-model path from fresh initialisation on at least three independent
  seeds if the diagnosis requires new real-model sampling. These are P17 diagnostic confirmation
  runs of the SAME P16 target, not new biological fits. Keep dTm=0, all other scientific priors,
  medium, allocation settings, maintenance and likelihood unchanged, including the inactive
  coordinate used as the control. Label changed COMPUTATIONAL settings explicitly.
- Prefer shorter matched diagnostics when they can demonstrate the cause; use full posterior
  runs when needed to verify final weights and active distributions. Cost them before launching,
  checkpoint them, and run sequentially. Do not stop at a promising early segment.
- Establish inactive-prior recovery and independent-run consistency of active marginals and
  region occupancy. Distinguish regions operationally; a parameter cluster alone is not proof
  of a separate biological mode. Predictive checks, if used, must carry feasibility status.
- If nuisance recovery succeeds but active inference still disagrees, the full gate has NOT
  passed: localise the remaining defect or show precisely which original claim was too strong.
  Do not call agreement of log Z alone confirmation.

DECISIVE-CONCLUSION GATE — ALL applicable parts must be met
1. The analytical null is proved for the executed model, or a demonstrated hidden dependency
   replaces it with the correct target.
2. The observed P16 failure is reproduced independently, or disproved by a located reporting error.
3. A mechanism is isolated by a controlled intervention and a falsification test; alternatives
   left viable are explicitly bounded. "Probably too few slices" does not qualify.
4. The intervention survives fresh-seed controls with known active and inactive answers, and the
   relevant real-model confirmation when necessary. No favourable seed selection or retrofitted
   tolerance. If the result instead refutes the original premise, show the corrected audit and
   explain what that does and does not settle about active-posterior disagreement.
5. The scientific target has not changed to obtain the answer. Any remaining limitation is stated
   narrowly, and the proposed remedy addresses the demonstrated cause rather than hiding it.

If a test fails, return to the earliest implicated task and continue. A failed repair is data,
not a reason to commission the next biological fit. A hard external blocker is the only reason
for an unresolved handoff; document it rather than declaring success without these gates.

TASK 7 — record, reconcile and hand off
- reports/P17_inactive_prior/report.md: opening verdict, null proof, hypothesis table, controlled
  experiments, causal diagnosis, confirmation, remaining limitations and the gate checklist.
- DECISIONS.md: every pre-registration, branch choice, failed hypothesis, computational change
  and reason. Include measured costs and restart instructions.
- Commit scripts, compact tables, decisive figures, input hashes and environment manifest.
  Include the minimal reproducer/regression test if a defect was found. Do not commit redundant
  giant checkpoints; preserve checkpoint paths/hashes and the arrays needed to reproduce claims.
- Append dated corrections to P16's decisions, OPEN_ITEMS and relevant synthesis evidence. Keep
  earlier results as historical records. State which of R1–R4 actually moved. Do not edit E6's
  deck or collaborators' drafts in another worktree as part of this investigation.
- Re-run report stamps and check them after the final commit. If core model code was changed,
  run the applicable seven-strain 79/79 and 60/60 regression checks and meaningful targeted tests.
  If only diagnostic/reporting code changed, run its relevant checks without unrelated model work.
- State whether the corrected evidence permits a subsequent fit. **Do not launch it.** Resolving
  the biological infeasibility exemption, choosing an allocation hypothesis and removing unused
  parameters from future production runs remain separately reviewable decisions.
- For every P16/P17 posterior summary retain: dTm=0 assumes the meltome mean is exact; uniform
  error is excluded and must be absorbed by tm_scale/catalytic parameters. No full-model claim.

VERIFY — report all
1. Branch/worktree, run provenance, versions, unchanged original-input hashes.
2. Exact null proof or its refutation, parameter mapping and fresh/reused/worker checks.
3. Independent audit reproduction; true dlogz versus logzerr; weighting and uncertainty findings.
4. Known-target truth, seeds, diagnostics, thresholds and all control outcomes.
5. Where independence was lost, with iteration/ancestry evidence where available.
6. Controlled intervention and falsification results; alternatives rejected or still viable.
7. Fresh-seed confirmation, including active distributions rather than nuisance recovery alone.
8. Decisive-conclusion checklist, failed attempts, costs, remaining limitations and next permitted action.
9. Changed-file scope, tests, provenance check and unmerged PR/branch status.

CONSTRAINTS
- No additional biological parameter fixed. No new D/E/F/M9 programme. No scientific likelihood,
  prior, medium or allocation change disguised as a sampler repair.
- Keep the inactive coordinate as a control until the diagnostic is complete. Removing it and
  reporting a faster run does not explain its biased marginal.
- No claim that f_metab is informative because a sampled distribution is narrow.
- No inference of a full-dimensional likelihood plateau merely from one inactive axis.
- No unweighted posterior correlations, IID KS significance on weighted dependent points,
  ESS-as-independent-samples claim, or evidence-agreement-only success.
- Preserve all original evidence and other tasks. Computational interventions are isolated,
  reversible and recorded; changing them is authorised for diagnosis, not retroactive P16 rescue.
- Be decisive about what the evidence establishes, and candid about what it does not.
- Autonomous; suggested commit sequence: "P17: premise", "P17: independent audit",
  "P17: controls", "P17: localisation", "P17: causal test", "P17: confirmation", "P17: record".
```
