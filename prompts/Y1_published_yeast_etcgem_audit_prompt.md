# Claude Code prompt — Y1: does the defect class we found exist in the published yeast etcGEM? (autonomous)

**Run from `../etcGEMs-synthesis`, NOT from the main checkout.** That worktree is on `main`; the
main checkout is on `p6/convergence` with a run in progress. This prompt must not touch it. Rename
the worktree to something honest if you like (`etcGEMs-work`), or leave it — but work there.

**Why this matters more than anything else in the queue.** Every finding behind the proposed methods
paper comes from models this group built. The obvious referee question is: *does any of this apply to
the published etcGEM?* Li et al. (Nat Commun 2021, "Bayesian genome scale modelling identifies
thermal determinants of yeast metabolism") is the only one. If the defect class is there, we have a
finding about the field. If it is not, we have a careful account of our own model-building — worth an
appendix, not a paper. **This test is the gate on the whole fourth-paper idea, and it is cheap.**

**Which of our findings could transfer, and which cannot.** Be precise about this; it shapes the
whole exercise.
  * **Seq2Tm's within-proteome invalidity — DOES NOT APPLY.** Li used curated per-enzyme parameters
    with Bayesian (SMC-ABC) calibration, not a sequence predictor. That finding warns anyone building
    etcGEMs *now*, including us; it is not a criticism of theirs. Say so explicitly in the report.
  * **Uncosted reversible energy/ion shortcuts — TESTABLE AND THE POINT.** This is a property of the
    underlying reconstruction, not the thermal layer, so it is portable. Nobody has looked, because
    the coupling-ion audit class did not exist until K5 wrote it.
  * **T_opt regime-determined / CT_max stability-determined — SHOULD transfer if structural**, but we
    have shown it in one codebase on four organisms. Testing it independently is the generalisation.
  * **Chain convergence — DOES NOT TRANSFER.** Different sampler (SMC-ABC), different diagnostics.
    Do not attempt to restate our emcee finding about their work.

**Tone, and this is not optional.** This is other people's published work, and it is the paper this
whole framework is built on. The register is "we developed an audit and applied it to the reference
implementation", not "we found errors in a published paper". Any positive finding must be verified
independently before it is stated, and reported with what was done to rule out an artefact of our
own tooling. A false positive here would be both embarrassing and unfair.

NOTE TO USER: launch in an auto-approving mode. It downloads a public model. Budget a few hours, not
a project — if it turns into one, that is itself the finding (see PART A).

---

```
Work AUTONOMOUSLY; commit in parts, prefixed "Y1: "; maintain reports/Y1_yeast_audit/DECISIONS.md
FROM THE FIRST JUDGEMENT CALL. Standing rules carry over. Check exit codes explicitly, never
`cmd && check`. Work in the `../etcGEMs-synthesis` worktree on a branch `y1/yeast-audit`; do not push
to `main`; end in a PR that is NOT merged. DO NOT touch the main checkout or anything under
`strains/eciML1515/` there.

PART A - obtain the model, and be honest about what is obtainable
- Find and fetch Li et al.'s deposited model and code (SysBioChalmers on GitHub; check the paper's
  data-availability statement and any Zenodo DOI). Record exactly what you got, from where, and its
  version.
- Establish the format. The Chalmers group works in MATLAB/RAVEN, so the reconstruction may not be
  directly readable by cobrapy, and their thermal layer is their own code. Report:
    * can the underlying GEM be loaded and solved with our tooling?
    * can their thermal layer be RUN, or only read?
- **If the model cannot be loaded in a few hours of work, STOP and say so.** That is a legitimate
  and reportable outcome — it means the audit needs a MATLAB environment and is a bigger job than an
  afternoon. Do not burn a day on format conversion. Record what would be needed.

PART B - the coupling-ion audit, which is the decisive test
This is the portable part: it runs on the reconstruction, not the thermal layer.
- Run `sink_audit` including the coupling-ion class on the yeast reconstruction. Report the proton
  budget: what fraction of ATP synthase's protons the respiratory chain actually supplies at a
  solved state, exactly as K5 reported for our seven strains.
- Classify every proton-translocating reaction costed/uncosted and reversible/irreversible. **K5
  established that the separating feature is REVERSIBILITY, not uncostedness** — E. coli has twelve
  uncosted proton-movers and is fine because none is reversible. Apply that criterion.
- Yeast is a eukaryote with a mitochondrion, so the energised compartment and the coupling ion must
  be inferred as K5 did for the methanogen (sodium) — do not assume.
- **IF THE AUDIT FIRES, VERIFY IT THREE WAYS BEFORE STATING IT:**
    1. Reproduce it from the pristine downloaded model, not from anything we have modified.
    2. Confirm the reactions involved carry meaningful flux at a solved state — a reaction that
       *could* short the circuit but carries no flux is a latent hazard, not an active defect, and
       must be described as such.
    3. Check whether Li's own code constrains those reactions somewhere our loading path misses.
       Their thermal layer may bound things the raw SBML does not.
  Report all three checks whether or not it fires.

PART C - the T_opt / CT_max regime test, if their model can be run
- If PART A found the thermal layer runnable: test whether T_opt moves under a capacity constraint
  while CT_max does not, as we found in three independent cases. Use whatever capacity lever their
  formulation offers.
- If it cannot be run, say so and describe what would be needed. Do NOT re-implement their thermal
  layer to get an answer — that would be testing our re-implementation, not their model.

PART D - the calibration shift, from the published posterior
Cheap and needs no model execution.
- From the paper and its supplementary, establish what their Bayesian calibration DID to the enzyme
  thermal parameters: did the posterior move Tm or Topt substantially from the prior, and in which
  direction?
- Compare with what we found: E. coli needed dTm = -5.6 K against a MEASURED meltome to bring CT_max
  onto the observed limit. If Li's calibration also pulled stability down substantially, that is
  independent support for a common over-prediction; if it did not, say so.
- This is reading a published result, not re-analysing it. Cite figures and tables by number.

PART E - the verdict, stated as one of three
Write `reports/Y1_yeast_audit/report.md` ending in exactly one of:
  (a) **The defect class is present in the published model** — with the three PART B verifications,
      the flux evidence, and a plain statement of what it does and does not imply about their
      conclusions. Their headline (ERG1, sterol metabolism) may be entirely unaffected; say so if so.
  (b) **Absent, but the structural finding holds** — the T_opt/CT_max asymmetry or the calibration
      shift generalises, which supports a narrower paper.
  (c) **Neither** — the findings are specific to the models this group built. State that plainly.
      It is the least convenient outcome and the most important one to report honestly.
- Then say, in two or three sentences, what each verdict means for the methods paper. Do NOT
  recommend whether to write it.

PART F - housekeeping while you are here
- The worktree: report whether `../etcGEMs-synthesis` should become a standing second worktree
  (useful — long runs block the main checkout regularly) or be removed once P6 finishes. Recommend,
  do not act.
- Update `docs/OPEN_ITEMS.md` with the outcome and any new item.

VERIFY (report all)
1. What model was obtained, from where, its version; whether the GEM loads and whether the thermal
   layer runs.
2. PART B: the proton budget; the costed/reversible classification; if it fired, all three
   verifications with their results.
3. PART C: the regime test, or why it could not be run.
4. PART D: what the calibration moved, cited to figures/tables.
5. PART E: which of the three verdicts, with the evidence beneath it.
6. `git diff main --stat` in this worktree; confirmation the main checkout was untouched.

CONSTRAINTS
- Register: an audit applied to the reference implementation, never a critique of a paper.
- A positive finding requires all three verifications before it is stated. A reaction with no flux
  is a latent hazard, not a defect.
- Do not re-implement their thermal layer. Do not restate our convergence finding about their work.
- Do not spend more than a few hours on format conversion. Stopping and saying what is needed is a
  valid result.
- Report verdict (c) as prominently as (a) if that is what the evidence says.
- Autonomous; commit in parts.
```
