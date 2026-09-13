# P17 decisions — inactive prior diagnostic

## D0 — 12 September 2026: freeze and pre-registration

Execution is on `codex/p17-inactive-prior` in `/private/tmp/etcGEMs-p17`, based on
191b4b0. The primary checkout and E-series worktree are untouched. No active calibration
jobs were found at launch. Named uncommitted P16 inputs were copied and hashed in
`inherited_uncommitted_manifest.json`. Originals remain the evidence of record.
Current source is a reconstruction until compared with the commits and logs at run time.

No biological parameter, prior, likelihood, medium or allocation will change. In all
P16/P17 inference summaries dTm=0 assumes the meltome mean is exact: uniform melting
temperature error is excluded and absorbed by tm_scale and catalytic parameters.

### Hypotheses registered before new experiments

| Hypothesis | Discriminating test | Initial status |
|---|---|---|
| Reporting / row or weight alignment | Independently reconstruct checkpoint rows, final live and weights | Open |
| Wrong prior transform | Per-spec scipy truncated-normal CDF and forward round trip | Open |
| Hidden f_metab dependence / numerical state | Full-support scans, fresh/reused/order/worker comparisons | Open |
| Runner / checkpoint chunking | Identical analytical target and seed, plain vs chunked | Open |
| Worker RNG or state | Serial vs pool on known targets; real path repeatability | Open |
| Insufficient constrained exploration | Drift/ancestry then controlled proposal intervention | Open |
| Bounding or proposal defect | Minimal target and implicated-layer intervention | Open |
| Legitimate finite-run uncertainty | Known-target independent replicate distribution and strand limits | Open |

### Diagnostic rules and first batches

1. Arithmetic/provenance batch: no solver; budget 15 minutes, one process. Reimplement
CDF and ECDF directly without importing prior audit functions. Check all weights,
restored rows, final-live inclusion, duplicated vectors, and all-parameter medians.
Stop on an input inconsistency and locate it before sampling. Errors in historical
conditional-bootstrap significance do not by themselves explain a biased null marginal.
2. Premise batch: start with both seeds' maximum-likelihood and coordinate-median
vectors, with f_metab at 0.15, 0.28, 0.45, then reversed and fresh-model repeats.
Record unrounded likelihood, growth, oxygen, feasibility and solver fingerprints.
One worker initially; benchmark before expansion. Budget 30 minutes, checkpoint each
vector. Expand to worker/order/support cases only as required. Differences must be
compared with same-input repeatability, not an arbitrary rounded equality.
3. Analytical baseline: 15-dimensional smooth Gaussian density in the cube and
an unequal-width two-region mixture, each with analytically known active marginal,
inactive Uniform(0,1) marginal and evidence. Also use P16 prior transform with its
inverse in the likelihood. Initial seeds 17001–17005; reserved confirmation seeds
17901–17905. Exact P16 nlive=800, multi bound, rslice, slices=3, dlogz=0.1,
first_update min_eff=30; compare plain/chunked and then pool sequentially.
Measure cost first; batch cap 4h. Calibration uses replicate effect sizes (mean,
weighted KS, active CDF error, logZ and region probability), never IID KS p-values.
Use a 99% reference envelope calibrated from independent exact-posterior draws and
nested replicate scatter, explicitly reporting small replicate-count limitations.
Freeze intervention confirmation tolerances after baseline controls and before heldout
seeds. Do not claim P16-sized deviations impossible from five passing toy seeds.

All diagnostic scripts/results go under this directory. Checkpoints remain separate
from historical P16 files. A failed experiment is retained. The decisive gate in P17
is not passed merely by recovering the nuisance marginal.

## D1 — arithmetic reproduced; numerical-state discriminator

Independent reconstruction exactly recovers checkpoint samples, likelihoods and weights,
including exactly 800 final live points. Prior-CDF agreement is <1.7e-15; natural
round trip <8.5e-13. The two null means and KS distances reproduce. The reporting field
`dlogz_final` is logzerr; the trace verifies the stopping statistic independently.

The first model scan ran after obtaining network access for the existing Gurobi WLS
licence (sandbox DNS failed; no model loading defect). Four representative active
vectors, endpoints and reverse order, include growing and fully non-growing points.
A low-growth seed-1 median has likelihood variation ~0.088, including different
answers at identical f_metab; best-point differences are <4e-8. This motivates
12 identical-vector repeats, canonical LP comparisons, two fresh workers and a
solver-basis reset intervention. This changes computation only. Budget 15 minutes,
2 workers, eight specified worker inputs per variant; preserve all failures. A reset
is not a proposed sampler remedy unless numerical history quantitatively explains
P16 and passes independent confirmation. Raw matrix hashes are order-sensitive;
canonical constraints/variable names are needed before interpreting hash differences.

Smooth control benchmark: ~2.7 seconds / 170k calls, nlive800. Plain vs chunked
matches first three seeds exactly; complete all five before concluding. Unexpected
bounding floating-point warnings are retained for investigation. These warnings are
not assumed causal. Mean nuisance is near 0.5 in these controls; logZ deviations
require checking against control variability, not just a null-marginal pass.

## D2 — initial controls completed; next batch

All five smooth baseline, chunked and P16-transformed controls and five unequal-width
mixture controls completed. Chunked and plain sample coordinates/log likelihoods are
bit-identical; accumulated log weights differ only ~1.5e-12. Thus the earlier phrase
"exactly" applies to samples, not the last bits of the weight integration. Applying
P16's physical prior transform and inverting it in the known likelihood also reproduces
the uniform-cube control to numerical precision. Neither is a cause on these targets.

The 12 identical-vector model repeats reproduce the ~0.088 log-likelihood variation
with **zero canonical LP coefficient/bound/objective differences**, while two workers
reproduce the same sequence. Resetting the growth solver basis before solving does not
remove it. This isolates a numerical-history issue, not sampled f_metab dependence,
at that point; it has not been shown to explain the much larger posterior discrepancy.
The failed reset intervention is retained. Need inspect tie-break re-solve and its
basis/optimality handling before interpreting this as a remedy.

Next cheap batch is smooth known target, nproc16 / queue16, seeds17001–17005, same
settings otherwise. Expected minutes, hard diagnostic budget 30 minutes; this tests
the original worker queue separately from transformation and chunking. No solver
or biological fits involved. Continue with mixture pool/chunk controls if required.
The early known-target logZ errors are all positive; do not call these controls fully
passed until this and active-marginal uncertainty are evaluated.

Automatic continuation is registered in this task every 30 minutes as
`p17-inactive-prior-investigation`. It must perform work toward the decisive gate,
not merely monitor. Pause it after completion or an externally blocked handoff.

## D3 — 07:57 UTC continuation: constrained-exploration discriminator

No P16/P17 sampling processes remain. The pool16 smooth controls completed. The next
batch tests constrained mixing, motivated by positive evidence errors on every smooth
and mixture baseline seed and by the 3-direction kernel in 15 dimensions. This is a
hypothesis test, not a declared remedy. Reuse calibration seeds17001–17005, changing
only slices from3 to15 on smooth and mixture targets, serial. Budget30min, expected
<5min from measured baseline; stop to inspect any crash. Record nuisance CDF, active
CDF/region mass, evidence and runtime. Then, if ambiguity persists, extend calibration
replicates (not confirmation seeds) rather than select a favourable seed. Fresh
confirmation17901–17905 remains untouched.

In parallel with cheap sampling, reconstruct P16 dead/live marginal drift from saved
cube coordinates and strand slot IDs. Slot IDs are not proposal-parent ancestry;
never interpret their counts as a complete genealogical effective sample size.
Read and fingerprint installed bounding/proposal source and preserve warning counts.
No model solves are needed in this batch.

## D4 — localisation and a harder known-target control

Reconstructed initial P16 live sets are close to Uniform: seed1 mean0.5041, KS0.0216;
seed2 also starts close. Drift is already material near iteration4800–5600. By late
iterations the two live sets collapse toward different nuisance regions. This is a
pre-summary sampling phenomenon; slot IDs do not recover parent genealogy.

The smooth target's mean logZ error falls from+0.233 (slices3) to+0.0693 (slices15),
across the five specified seeds. This is suggestive, not decisive: only five calibration
seeds and a simple smooth geometry. Mixture slices15 batch is in progress.

100 well-conditioned covariance checks trigger the same floating-point warnings as
sampling, yet inverse residuals remain below2.5e-14. Warnings alone do not demonstrate
corrupted matrices; library source hashes and results are retained. Need avoid
attributing P16 failure to warning text without an actual numerical violation.

Next test: the same analytically normalised mixture with a narrower first-coordinate
component (sd0.0005 instead of0.035, other component sd0.10; masses0.3/0.7 unchanged).
Motivation is P16's transition from a broad likelihood region around-18.69 into a
small high-likelihood region accompanied by loss of nuisance spread. This is a
stress test of founder/mixing effects, not a fitted surrogate for the metabolic model.
Known inactive prior and active CDF/evidence remain exact. Seeds17001–17005,
slices3, same other settings, serial, then slices15 only if failure is seen. Budget
30min; preserve misses/crashes. No heldout seeds used to select target or remedy.

## D5 — active-region failure retained; quantify numerical history where weights lie

The narrow-mixture baseline assigns only0.006–0.117 probability to x0<0.5, versus
exact approximately0.3044 (0.3 narrow mass plus the broad component tail). Nuisance KS remains
0.014–0.065: a passing-looking nuisance can coexist with an active-region failure.
Longer-slice stress runs are therefore diagnostic, not confirmation of a chosen cure.

Original P16 output/checkpoint/trace hashes all remain unchanged. No tracked source
changes occurred between pre-run ab77189 and reconstruction191b4b0 in relevant model,
config, prior or runner paths. Transient uncommitted changes and historical installed
library identity cannot be ruled out by Git; record that provenance limitation.
Isolated runner reporting patch now writes actual dlogz, not logzerr; no historical
output or scientific model changes. Calibration output's misnamed field becomes logzerr.

Next model batch: replay each seed's maximum-weight stored point and dead point8000,
four exact repeats, then fresh contexts, with the actual unmodified likelihood. Also
probe f_metab endpoints at each held-fixed vector. Existing worker-path instrumentation
captures growth/O2/status. Budget15min, one process, ~32 evaluations; checkpoint after
each. Purpose: determine whether the numerical-history discrepancy is large where
posterior weights concentrate or the live population collapses. This is diagnostic
re-evaluation of recorded points, not a new posterior fit. No selective omission of
non-growing points or infeasibility-mask changes. Bound differences by same-input
repeat variation; do not assume the earlier0.088 effect explains the full failure.

## D6 — numerical replay and failed longer-slice remedy

All28 prespecified numerical re-evaluations completed. At each seed's maximum-weight
sample and stored index8000, four identical repeats, both f_metab endpoints and a fresh
model return exactly the archived likelihood. The earlier0.088 history issue is real
at one low-growth median but does not appear at these weight/transition points. This
bounds, rather than eliminates globally, numerical history as a contributing cause.

Increasing slices improves smooth evidence accuracy but does not reliably recover the
narrow-mixture active probability: first three slices15 runs give0.084,0.785,0.231
against0.30437. Retain all five completed outcomes. No remedy selected and no
confirmation seeds consumed. This falsifies "15 slices is sufficient" on these controls.

Next discriminating batch: narrow-mixture, slices3, single ellipsoid instead of multi,
otherwise identical, same five calibration seeds. Budget30min, serial. Purpose is to
separate multiple-bound partition effects from a failure that persists with one global
bound. It is not an attempt to choose the most flattering result. Retain evidence and
active/nuisance failures; if failure persists, the multi partition is not necessary
for the demonstrated toy failure. Do not generalise toy causality to P16 without the
relevant conditional-kernel or fresh-run tests.

## D7 — single-bound falsification completed

All five narrow-mixture single-bound runs completed with region probabilities
0.0638,0.0633,0.0071,0.0085,0.0354 (truth0.30437). The failure therefore persists
without multiple-ellipsoid partitioning. This rules out that partition as a necessary
cause of the toy miss, not every possible bounding defect in P16. Longer slices15
and a global single bound have both failed as adequate remedies. The inactive
marginal still looks much less alarming than the active-region error.

Continuation should now instrument proposal parents and displacements on these
known targets and/or at selected P16 constrained likelihood levels; do not repeat
plain/chunk/transform checks without new evidence. Need distinguish missing-region
initial discovery from loss of exploration after discovery and recover an analytically
known active distribution with a controlled intervention. Retain f_metab and the
fresh confirmation seeds. No biological fit authorised. No running batch remains
at this checkpoint; the active heartbeat continues investigative work.

## D8 — 09:07 UTC: proposal-parent instrumentation

No prior batch remains running. Instrument the original RSliceSampler via a local
subclass that records start and end cube coordinates, likelihood cutoff and call
count, returning the original result unchanged. No site-packages edits. Run narrow
mixture seed17001, slices3, serial, then compare rows against the existing baseline
before interpreting the trace. Extend to the five calibration seeds only after
identity is verified. Budget30min, expected minutes. Classify the narrow core as
abs(x0-0.2)<0.003 (six narrow-component standard deviations); retain exact region
probability x0<0.5 separately. Measure entries/exits, displacement and ancestor
weights, with explicit missing-parent counts for the initial uniform proposal phase.
Do not label a constrained sample's slot ID as its proposal parent.

## D9 — traced mechanism and controlled full-interval update

The traced seed17001 is bit-identical to baseline. Five live points start within
six standard deviations of the narrow centre. After the independent proposal phase,
10,792 rslice proposals contain zero entries or exits from that core. Core-to-core
nuisance RMS movement is0.0114, versus0.153 outside; parent-child correlation is0.9993
inside. This supports lost exploration after discovery, not simply absent initial
support. Remaining four prespecified traces are running. Ancestral weight concentration
is descriptive, not a statistically calibrated ESS after within-lineage moves.

Controlled intervention: one random-order sweep of full-prior-interval coordinate
updates. For each coordinate, draw uniformly over[0,1] until the unchanged likelihood
exceeds the current cutoff. This samples the EXACT one-coordinate conditional uniform
measure, including disconnected permitted intervals, instead of shrinking around the
starting connected piece. It is a valid invariant Gibbs kernel, not an independent
constrained-prior draw or an automatically adequate production sampler. It refreshes
an inactive coordinate exactly, so success requires active region mass/evidence too.

Benchmark narrow target seed17001 first, same nlive/dlogz/bounds/target/priors, serial.
Budget30min, checkpoint1800s; hard per-coordinate cap1,000,000 evaluations raises an
explicit failure rather than accepting a wrong point. No real likelihood sampling yet.
If benchmark cost is acceptable, complete seeds17002–17005; evaluate active accuracy
and cost before selecting any confirmation protocol. This intervention tests whether
access to disconnected coordinate intervals removes the traced failure. A passing
toy kernel alone is not permission to fit P16 again.

## D10 — full-interval benchmark cost and replication

Benchmark completed in106s and5.53million likelihood calls. Nuisance KS0.0096,
active region probability0.2371 (truth0.3044), logZ error-0.1171. This is substantial
recovery versus matched baseline0.0072 but is not a declared pass or adequate error
calibration. Complete the remaining four prespecified seeds sequentially, expected
~8min, batch cap30min, checkpoint1800s. No real-model use of this expensive kernel is
authorised by toy runtime: millions of metabolic solves would be inappropriate.
The output field slices3 refers to the original comparison setting; this custom
kernel actually performs ONE full-coordinate sweep and ignores the slice count.

All five proposal traces are identical to their baselines; every seed has2–8 initial
narrow-core points and zero subsequent rslice core entries/exits. Installed source
shows starting live points chosen uniformly but ellipsoid axes chosen independently,
weighted by ellipsoid volume. This is a valid proposal design, not automatically a
library defect; on small disconnected regions it can impose directions scaled for
other regions. Localising that geometry and the tiny within-core movement is the
next causal comparison. Preserve trace and source provenance rather than attributing
any failure merely to the library name.

## D11 — kernel unit proof and bounded real-path protocol

While sequential analytical replicates complete, validate the new one-coordinate
transition on two fixed constrained sets: disjoint intervals[0.1,0.2] and[0.6,0.9]
(length weights1:3), and a Gaussian likelihood cut selecting[0.6,0.8]. Use10,000
independent transitions each, seed17250, exact conditional CDFs and the prespecified
DKW bound at alpha0.001. IID testing is justified here ONLY because this one-coordinate
full-interval rejection redraws independently; never apply this bound to the weighted
nested samples. This is a regression test for the diagnostic kernel, not a substitute
for the known-target fits or a whole-likelihood plateau experiment.

After current analytical batch ends, run six bounded P16 kernel probes: seed1 archived
live set at iterations4800 and9600, the maximum-logL point of each set, three random
seeds17201–17203 with independently drawn inactive coordinate. Reconstruct live points
and use the recorded bound and scale, with current rslice3 default stepping-out.
Record starts, ends, cutoffs, axes norms, calls and failures. This is a local test
from a biased saved population, NEVER an unbiased posterior or exact historical RNG
replay. Budget30min total; each transition stops with an explicit failure after200
likelihood calls or600s, whichever first; checkpoint every transition. One process,
existing solver/target unchanged. Need compare movement with toy mechanism; a handful
of moves cannot certify global mixing. Prepared real_kernel_probe.py is not launched
until the ongoing analytical batch finishes.

## D12 — 09:55 UTC: completed intervention and a real-path falsification

All five full-coordinate controls completed. Region probabilities are0.2371,0.3949,
0.3727,0.2177,0.3357 (truth0.3044); errors span-0.0866 to+0.0906. Nuisance KS is
0.0084–0.0157 by the kernel's exact refresh. This strongly improves mean recovery but
replicate variability is material and has not been calibrated or confirmed.

All six maximum-logL P16 probes completed. Nuisance moves range0.020–0.269 in absolute
size, including large moves after the population collapsed. Therefore the toy claim
"every real proposal is trapped with a tiny inactive step" is falsified at those
chosen points. Do not generalise the narrow-toy mechanism to P16 on that evidence.
The maximum-logL point may not represent the numerous points near the observed
-18.69 bottleneck. Need investigate the likelihood stratum, not select a flattering
alternative probe without explaining the change.

Next no-solver diagnostic: derive the exact likelihood of zero growth with no scored
respiration from the unchanged likelihood/data, as a function of disc_growth alone.
Compare all archived log likelihoods to this curve at tolerances1e-12,1e-8,1e-4;
report counts, weights, inactive means and live-set occupancy, plus the exact curve's
maximum. Label equality as algebraic compatibility, not verified feasibility status.
If it explains the -18.69 stratum, validate selected points with actual solver status
and then test median live points in that stratum. Budget15min arithmetic, one process.
No infeasibility penalty, biological parameter or target changes are permitted.

## D13 — zero-growth stratum identified; targeted validation

The zero-growth/no-scored-respiration curve peaks at-18.6825022942 with disc_growth
1.14072162. Archived compatibility counts/weights are identical at all three chosen
tolerances; seed2 compatible weight is0.814783. At iteration8800 seed2 has415/800
compatible live points. At iteration8000 seed1 has464/800. Complementary live groups
already have nuisance means~0.14 (red1) and~0.72 (red2), before the compatible group
vanishes. This accounts algebraically for the observed likelihood bottleneck, but
solver status still needs direct validation and sampling causality remains open.

Next batch: red1 at8000 and red2 at8800, median-logL member of the compatible live
group (specified by exact-curve error<1e-8), seeds17201–17203. Verify initial growth,
O2/feasibility and likelihood through the actual path, then one rslice3 proposal using
saved bound/scale with f_metab independently refreshed initially. Same transition
caps as D11 (200 calls/600s) and1800s total; one process, expected5–10min. This tests
a different, empirically dominant stratum after the maximum-logL probe falsified a
universal freezing story. Retain that falsification. No change of mask or target.

## D14 — known-target control for the newly located likelihood geometry

The previous narrow-mixture control established a real kernel weakness but did not
reproduce P16's large global nuisance bias, and maximum-logL P16 probes did not freeze.
The identified one-parameter likelihood ceiling now motivates one specific new known
target, rather than another numerical setting sweep: a disjoint two-region density,
with x0<0.5 having only the last active coordinate Gaussian (all other coordinates
uniform), and x0>0.5 having all14 active coordinates Gaussian. Each region has exact
posterior mass0.5; every density is normalised on its support, so logZ=0. Inactive
coordinate7 is uniform throughout. The broad region's likelihood has a continuous
one-dimensional maximum, not a positive-volume mathematical plateau. This mirrors
the identified low-dimensional stratum and its handover without changing biology.

Specify broad Gaussian centre0.5, sd0.15; narrow-region x0 centre0.75, sd0.08 restricted
to(0.5,1); its other active coordinates centre0.5, sd0.15. All supports are in the unit
cube. Baseline original rslice3 settings, seeds17001–17005, serial, budget15min.
Analytical target only; can run alongside the bounded single-worker solver probes.
Retain complete outcomes; if this does not reproduce the null failure, state that and
use the actual stratum probes to decide further work. No automatic new target search.

## D15 — stratum validation and limits of the simplified explanation

All six stratum probes completed. Selected points are infeasible at every measured
temperature, with zero growth and no finite O2, validating their algebraic signature.
Inactive displacements are0.0007–0.060, substantially smaller than many maximum-logL
probes. Thus proposal behaviour depends on the stratum; none of these six-transition
experiments establishes posterior convergence or an adequate kernel.

The simplified stratum target does NOT reproduce the large P16 null failure: five
nuisance KS distances0.010–0.061 and region probabilities0.435–0.472. Retain this
negative result. A one-dimensional likelihood ceiling alone is insufficient; actual
feasible-region geometry and inadequate exploration of it remain plausible. Do not
invent another surrogate merely to force P16-sized bias.

Next independent-kernel discriminator: library uniform sampling within its proposed
multi-ellipsoid bound (sample='unif'), on the existing narrow-mixture target. This
removes within-bound MCMC ancestry while retaining a possible bound-coverage failure.
Same nlive800 and target/prior, seeds17001–17005, serial. First benchmark17001 then
remaining seeds if cost permits. Budget30min, checkpoint1800s. Bound-update scheduling
uses the library's resolved defaults for this kernel and must be reported; do not
pretend only proposal arithmetic changes. It is not full-prior rejection or a
proof of complete bound coverage. Active probability/evidence must be checked.

## D16 — geometric coverage check for the independent-proposal alternative

Before considering uniform-bound sampling on P16, test saved bounds against the
known inactive direction: at each live active vector, changing only f_metab must
preserve the constrained likelihood, but a geometric bound may not include the
whole prior interval. Check five fixed CDF values0,0.25,0.5,0.75,1 at iterations
4800,8000,9600 of both seeds. No model solves; budget5min. Report coverage rather
than assuming an ellipsoid enclosing live points encloses the true support.
This is not a demonstrated truncation in rslice, whose candidate may leave the bound;
it is a required check before interpreting uniform-bound draws as an independent
reference. Do not use a coverage defect to retroactively blame the wrong kernel.

## D17 — historical-bound recording defect; correction of D11–D16 interpretation

Uniform-bound benchmark exceeded its30min budget while continuation was delayed; it
ran~3h36min before SIGINT (exit130). Preserve its .save checkpoint and log. This
resource overrun is a workflow failure; future expensive runners need an enforced
internal deadline, not merely a written budget or periodic wakeup. No completed
posterior exists for this benchmark; do not use it as a result or restart blindly.

The bound coverage check exposed a CONCRETE installed dynesty3.1.0 history defect:
update_bound_if_needed calls update_bound (which returns a deep copy) but ignores its
return, then appends self.bound to bound_list. Thus every recorded non-unit-cube
bound is the SAME mutable object. Restoring red2 shows entries1,10,22,24,60,88 have
the same Python identity and final geometry. Red1 must also be checked explicitly.

CORRECTION: D11 real_kernel_probe and D13 stratum_probe used FINAL geometry indexed
as though historical, with historical scales. They are valid likelihood evaluations
and arbitrary-direction conditional transitions, but NOT reconstructions of the
historical proposal geometry. Withdraw that interpretation from all comparisons.
The solver-status validations, exact likelihood repeats, independent output audit and
live-coordinate drift reconstruction do not use historical bounds and remain valid.
D16's old-bound coverage output likewise does not describe earlier bounds. Do not
attribute the original posterior failure to this recording-only defect: current
sampling uses self.bound, so copying the history alone does not alter its proposals.

Next: independent regression reproducer for bound aliasing and a local diagnostic
patch, without editing site-packages. Demonstrate trajectory identity before/after
and distinct preserved bound snapshots. Rebuild bounds from reconstructed live sets
only as an explicitly new local experiment, not recovery of lost historical state.

## D18 — regression result and corrected local experiment

Bound aliasing is confirmed in BOTH P16 checkpoints (92/90 recorded bounds but only
one distinct non-cube object each). A minimal3D regression reproduces it. A local
recording-only wrapper preserves24 distinct snapshots instead of one, with bitwise
identical samples AND weights. This proves the recording defect and falsifies it as
a direct explanation of the posterior bias. No installed package was edited.

The interrupted uniform-bound checkpoint contains100,770,078 calls and12,255 completed
iterations; no terminal posterior is available. This method is not a practical
candidate for the expensive real likelihood in its tested configuration. Future
controls now enforce SIGALRM per-run deadlines, preserve safe periodic checkpoints,
and emit timeout records. A deadline-trigger test is required before another costly
analytical batch. Do not resume the100M-call benchmark.

Corrected local experiment: freshly fit MultiEllipsoid bounds to the reconstructed
800 live points at red1/8000 and red2/8800, using recorded bootstrap/enlarge settings
and fixed reconstruction seed17400+iteration. Verify containment of all live points.
These are NEW reconstructed bounds, explicitly not lost historical snapshots. Repeat
D13's six stratum proposals with these bounds, preserving the earlier outputs as
superseded-geometry evidence. Same200-call/600s per proposal and1800s batch limits,
one process. This restores a valid local-geometry test without pretending the saved
history can be recovered. Output in rebuilt_stratum_probe.*, never overwrite D13.

D18 implementation note: first rebuilt-bound probe reached output but failed JSON serialization of a NumPy integer containment count (exit1). The failure log is preserved; cast the count to Python int and rerun the registered batch. No scientific or diagnostic acceptance criterion changed.

## D19 — rebuilt results and full live-set likelihood validation

All six rebuilt-bound probes completed with800/800 containment. Nuisance displacements
range0.0068–0.2823; some are large. This does not support a universal frozen-coordinate
mechanism, even within the selected infeasible stratum. Preserve the contrast with
superseded final-bound probes. Six transitions cannot answer multigeneration ancestry.

Next discriminating batch is a prerequisite to a possible traced conditional
continuation: reconstruct all800 live active points at red2 iteration6800 (where the
non-zero-curve group is small), independently refresh only f_metab with seed17501,
and re-evaluate the complete set in eight fresh original worker contexts. Preserve
all likelihood differences, growth maxima, O2 finiteness and solver statuses. Budget
15min with an enforced alarm; incremental output per returned point. Expected~3–5min
from measured solve costs. No nested fit is launched in this batch.

Predeclare maximum absolute likelihood mismatch1e-6 as the threshold for proceeding
to a continuation that relies on the archived ordering. This is a numerical
reproducibility discriminator, not a biological cutoff or a posterior acceptance
rule. If any point exceeds it, locate/repeat the discrepant states before continuation;
do not relax the threshold. If validation passes, a bounded genealogy-recording
continuation from this biased active population may distinguish ancestry/selection
from mutation. It would remain a conditional diagnostic, not a fresh posterior.

## D20 — likelihood validation passed; instrumented conditional continuation

All800 fresh-context likelihoods reproduce within1.341e-8, passing the preregistered
1e-6 maximum-error threshold. Thus archived ordering is reproducible for this set;
numerical history is not a supported explanation for its bottleneck. Validation
completed in146s, with unchanged likelihood and independent f_metab redraw.

Next is a CONDITIONAL diagnostic continuation, not a full posterior or a biological
fit: use those800 active positions at red2/6800, independently redrawn inactive
coordinates, and validated likelihoods. Start a new sampler with this supplied live
set, nlive800, rslice3, multi bounds, queue8/workers8. Begin bound sampling immediately
(first min_ncall0/min_eff101) because the supplied set already lies above a likelihood
cut. Rebuild bounds rather than using corrupted history; recording-only history fix
is applied. Scientific evaluator/prior mapping remain unchanged. The starting active
population is biased; no evidence or posterior claim can be made from this run.

Run2500 replacement iterations, no final-live evidence integration. Seeds17511–17513
are preregistered for successive independent diagnostic segments; begin17511 only
for cost/trace verification, then complete the remaining seeds if the run is valid.
Each segment capped7200s by an enforced alarm, checkpoints600s and every250 completed
iterations. One expensive batch at a time. Eight workers preserve responsiveness.
Trace accepted proposal parent/child coordinates and initial ancestry. Per live-set
checkpoint decompose its inactive mean into ancestor-value contribution and cumulative
movement; this is an exact accounting identity, not an ESS or a causal proof by itself.
Keep initial independent-phase roots explicitly counted. Report whether the factorised
inactive distribution drifts and whether a few ancestors acquire disproportionate
occupancy. Do not claim a favourable/no-drift seed settles the question. This records
the missing mechanism through actual likelihood evaluations at bounded cost.

D20 setup correction: min_ncall0 alone does not trigger bounding before the first proposal queue. Source inspection caught the diagnostic still in initial uniform rejection after~3min with zero replacements. Stopped it (exit130), preserved initial folder/log under conditional_17511_initialization_attempt, and added an explicit forced bound update before the first queue, as the registered protocol intended. The sampler now asserts it is out of unit-cube sampling before starting. Existing output directories cannot be overwritten. No completed segment or parameter setting was selected in response to results.


## D21 — independent live trace audit and conditional group movement

Read-only audit of a single checkpoint byte snapshot at1927 replacements accounts
for every accepted parent/child and every live point back to an initial ancestor.
The independent recursive genealogy agrees with the running decomposition. Overall
mean0.47953/KS0.05077 does not reproduce the historical P16 failure. Splitting by
the previously defined zero-growth likelihood curve reveals503 compatible live
points (mean0.46062) and297 complementary points (mean0.51156, KS0.13734). The latter
have30 initial ancestors, with the largest occupying13.47% of this live group.

Among271 complementary-to-complementary accepted proposals, nuisance RMS movement
is0.03244 and parent/child correlation0.99488; compatible-to-compatible proposals
have RMS0.15350 and correlation0.86147. At the established1e-8 compatibility
tolerance there is one apparent compatible-to-complementary transition; at1e-6
there are none. Live group memberships are identical at both tolerances. Report
this classification sensitivity rather than claiming one real mode crossing.
Curve compatibility remains algebraic, not proof of feasibility status. This is
descriptive localisation of restricted movement, not a completed causal test.
Group-conditioned ancestry counts are not statistical ESS. The script snapshots
and hashes checkpoint bytes, performs no model solves, and never resumes the run.

## D22 — bounded sequential execution of already registered diagnostic seeds

Trace validity has passed at1927 replacements. To avoid idle gaps between expensive
segments, launch a batch coordinator that waits for17511 to finish its original
2500-iteration/7200s limit, audits the terminal checkpoint, then runs17512 and17513
sequentially under the identical limits. No additional seed or criterion is added.
Each terminal audit must account for all2500 parent/child transitions and all live
ancestors. Launch permission depends on completion/accounting, never on whether
the nuisance distribution looks favourable. A timeout, crash, missing terminal
status or failed accounting stops this coordinator for autonomous diagnostic review;
it never silently extends a run or skips a seed. The coordinator has an exclusive
claim file to prevent duplicate dispatch, a one-hour maximum wait for the currently
running first segment, and a backup process-group cleanup deadline for its own
children. Expected remaining cost<=5h, eight model workers at most. No simultaneous
expensive batch, new biology, posterior/evidence claim or confirmation-gate claim.
The heartbeat should inspect conditional_batch_status.json before any new launch.

D22 launch verified: coordinator PID4599/session38225 is waiting for17511; no
additional sampler is running. Direct safety checks passed: a timed-out status
prevents dispatch, and an existing claim prevents a duplicate coordinator. The
first test attempt mocked subprocess before scientific-module imports and failed
inside a NumPy platform probe; moving the audit import after the terminal-status
check removes that unnecessary import on the rejection path. Retest passed.


## D23 — hard timeout preserved; finish the unchanged diagnostic endpoint

Seed17511 reached the7200s hard limit. Last safe checkpoint2250 has all2250
accepted parent/child links independently accounted for,800 live points and115
initial ancestors. The coordinator correctly stopped without launching17512/17513;
both original processes have exited. This is a runtime-budget failure, not a
sampler covariance exception. The overall mean0.48679/KS0.07273 remains unlike
the historical P16 bias. The complementary group454live/30ancestors has nuisance
RMS step0.02994/correlation0.99556. No causal gate is declared.

Preserve the original timeout status and an exact hashed checkpoint snapshot.
Next batch resumes the SAME saved RNG, live set, bounds, proposal queue and
accepted trace to reach the originally registered2500 replacements, with a new
1800s hard cap. Expected~1100s from the last250 replacements (943s), eight
workers, no concurrent expensive work. This explicitly adds a resource segment;
it does not change any scientific criterion, seed, target, or diagnostic endpoint.
Do not claim the original two-hour cost estimate passed. Reconstruct genealogy
from all saved accepted transitions and original roots, never reset ancestry.
Fresh worker solver contexts are unavoidable on resume and are a provenance
limitation; the full earlier800-point validation passed1e-6 but does not prove
global solver determinism. Do not claim exact real-model trajectory equivalence.
The existing coordinator remains stopped and its exclusive claim is retained.
After this segment, audit completion before deciding dispatch of registered
replicates; no seed may be dropped or selected for favourable nuisance behaviour.

D23 launch verified: session37862; resumed2250-step record exactly reproduces
all pre-timeout live/ancestry statistics with zero unknown roots. A serial
3D known-target check using the same ParentSlice class and checkpoint restoration
produced bit-identical subsequent samples, live set and weights (seed17590).
This checks restoration, not parallel real-solver determinism.


## D24 — first conditional segment complete; second registered seed

Seed17511 completed the original2500 replacements after1191.75s of bounded
continuation. Independent audit accounts for every accepted transition and live
ancestor. Overall inactive mean0.51115/KS0.08273 does not reproduce P16-size
distortion. The complementary634 live points have30 initial ancestors;608
within-group proposals have nuisance RMS0.02769/correlation0.99602, compared
with0.15245/0.86106 in the compatible group. No crossings at1e-6 compatibility;
one apparent crossing at1e-8. Restricted movement is supported; a decisive
historical cause and remedy are not established by this conditional experiment.

No diagnostic process remains active. Launch the already registered seed17512
with the original800 live positions, independently redrawn nuisance values and
independent RNG, same2500-step endpoint and7200s hard cap, eight workers. Based
on17511, the full endpoint may need a separately reviewed checkpoint continuation;
do not silently extend the cap or skip an unfavourable seed. Expected initial
batch<=2h. Seed17513 remains pending. No scientific setting or acceptance criterion
changes; the stopped old coordinator stays stopped.


## D25 — positive dependency control and separately added inert coordinate

While registered real repeat17512 runs, close TASK4's missing cheap positive
control without another expensive model batch. Use the existing14-active smooth
Gaussian target times u7^2. Analytically p(u7)=3u7^2, CDF=u7^3, mean3/4;
logZ equals smooth logZ minus log3. This deliberately informative coordinate
should fit its correct CDF better than the incorrect uniform CDF in every
replicate. Report all errors, active marginal and evidence too; this discriminator
is not a calibrated inference-accuracy certificate.

Five diagnostic seeds17601–17605, original nlive800/rslice3/multi settings.
Then repeat with one additional exactly independent cube coordinate (dimension16)
and report its uniform CDF error separately; added dimension is a changed toy
control, not an inert relabeling or biological intervention. The original first15
coordinate target and evidence remain identical. These are diagnostic controls,
not heldout remedy confirmation; seeds17901–17905 remain reserved.
Baseline smooth cost2.66s/run predicts~30–60s total, one CPU, no metabolic solves.
Enforce120s/run alarm; stop batch on timeout/error, preserve each result immediately.
No expansion of worker pool or overlap with another expensive experiment.

D25 results: all10 controls completed in32.39s total, exit0. Correct Beta(3,1)
CDF is closer than the incorrect uniform CDF in every run: KS0.0090–0.0330
versus0.3826–0.4153. Additional inactive coordinate KS0.0232–0.0703 across
five16D seeds. Other active-coordinate KS0.0116–0.0642. Evidence errors remain
positive in all10 runs (+0.0689 to+0.4065); this positive-control discriminator
passes, but it is not general inference validation or a remedy. Numerical bound
warnings occurred, as in earlier controls; no new causal attribution follows
from warnings alone. All outcomes and raw weighted arrays retained. Ten original
P16 calibration input hashes rechecked unchanged. Real seed17512 remains active,
without another expensive batch.


## D26 — falsify nuisance recovery as sufficient evidence of repair

Perform an exact nuisance-only prior refresh on COPIES of weighted output rows
from both P16 runs and all five existing narrow-mixture controls. No sampler,
model solve, parameter fixing, active-row movement or scientific target change.
Because the proved target factorises, replacing only u7 by an independent
Uniform(0,1) draw is an invariant conditional kernel. It cannot repair wrong
active-region weights. This is a controlled diagnostic/falsification of the
proposition that a passing inactive marginal certifies inference, not a proposal
to publish repaired P16 posterior rows.

Prespecified refresh seeds17651–17655 for each source, one CPU, expected<10s.
Report all before/after inactive means and weighted KS; assert the other14
coordinates and all weights are bit-identical. For known-mixture controls report
the unchanged region mass against truth0.3043739263. Retain no altered P16
posterior file; record source hashes and deterministic seed/code provenance.
No significance threshold is selected. Any inactive recovery here is conditional
on the saved active rows and cannot constitute the P17 confirmation gate.


D26 outcome: all35 diagnostic refreshes completed; original rows/weights were
not modified. P16 red1 KS drops from0.29088 to0.00910–0.01245, red2 from0.21615
to0.01427–0.02139. The narrow-mixture control refreshes have KS0.00762–0.01353,
yet their active-region probabilities remain0.00628–0.11692 against exact
truth0.30437. This directly falsifies nuisance recovery as sufficient validation
of active inference. It does not by itself isolate P16's original cause. No
refreshed P16 posterior file was saved; source hashes and deterministic refresh
seeds are recorded. Independent controls and real-path causal confirmation remain
required. Real seed17512 is still progressing under its existing bounded run.


D24 ongoing repeat check: seed17512 checkpoint2000 independently audited; every
accepted transition and live ancestor accounted for. Overall mean0.51538/KS0.06362.
Complementary group462live/32initial ancestors, within-group nuisance RMS0.03647
and parent/child correlation0.99173, versus compatible-group0.15604/0.85434.
No group crossings at either1e-8 or1e-6 compatibility. This partially replicates
restricted movement, while again not reproducing historical P16-sized drift.
It is an interim checkpoint, not the2500-step endpoint; continue current run
within its existing time limit, with no duplicate launch or endpoint change.


## D27 — second repeat timed out; bounded checkpoint continuation

Seed17512 hit7200s, with verified2250-step checkpoint. All accepted transitions
and live ancestry accounted for; processes confirmed exited. Overall nuisance
mean0.51948/KS0.09163; complementary634 live points descend from32 roots,
within-group RMS0.03863/correlation0.99062 versus compatible0.15516/0.85767.
No algebraic group crossings at either recorded tolerance. Partial restricted
movement replicates, but historical P16-size drift is still not reproduced.

Use the already tested --resume path, preserving timeout and audited checkpoint,
to finish the original2500-step endpoint with unchanged saved sampler/RNG state.
Separate1800s cap, eight workers, expected~1200s based on seed17511 continuation.
No new diagnostic seed, scientific threshold or model change; fresh worker
contexts retain D23's numerical provenance caveat. Seed17513 remains pending
audit of completion. Do not restart the stopped batch coordinator.


## D28 — external causal hypothesis and second completed conditional trace

External review proposes that prolonged occupancy by the zero-growth stratum
causes a bottleneck in complementary ancestry, amplified by poor within-group
exploration. Treat occupancy and mixing as interacting mechanisms, not mutually
exclusive explanations. D14's equal posterior masses did not test the proposed
asymmetry. This is a specific new reason for a targeted toy test under D14's
no-blind-search rule; it does not authorise changing biological infeasibility
penalties, mask, priors or fixed parameters.

Two qualifications precede a causal claim. First, reducing the low group's score
cannot create800 independent high-group ancestors: high-group replenishment
depends on transitions and initial high-group prior volume. The counterfactual
near-32 likelihood is untested and is not a defined authorised scientific change.
Second, the actual zero-growth group varies continuously with disc_growth; an
exactly flat toy introduces tied likelihoods/positive-volume atoms. Compare
flat and smooth versions explicitly to separate plateau handling from ancestry
loss. Scores/gaps, prior volume and posterior mass must be reported separately.

Second real conditional trace17512 has now completed2500 replacements after
1405.36s bounded continuation. All transitions/ancestry audited. All800 final
live points are complementary, descended from32 initial roots, with no observed
group crossings at1e-8 or1e-6. Overall nuisance mean0.51289/KS0.08345; this
demonstrates ancestry concentration through handover but does not reproduce
P16-size drift or isolate occupancy as its cause. No discarded seed.

External review also proposes an appended inactive Beta(3,1) coordinate on the
real likelihood. Its exact posterior remains Beta(3,1), CDF b^3; transforming by
that CDF recovers the same uniform null. Replacing the existing inactive prior
would change a declared P16 prior, so retain the original15 coordinates and use
an explicitly separate augmented diagnostic if commissioned within P17. D25's
informative toy used a likelihood factor u7^2, which is a different positive
control. An appended inactive prior tests real-path plumbing and exploration
but provides no known answer for the active posterior. Adding a dimension can
change proposal geometry; do not describe it as a harmless relabeling or full
certification. Do not substitute this for the registered third conditional seed.

Next registered real batch17513: same supplied active positions and independent
nuisance/RNG draws,800live/2500replacements,7200s cap,eightworkers. Expected
~2h plus separately reviewed continuation if needed, based on both earlier
seeds. Preserve final audits and original timeout statuses. No concurrent
expensive batch or scientific-target change.


## D29 — pre-register the asymmetric occupancy falsification

Next cheap toy batch, not yet run:15 cube dimensions, inactive index7, high
region u0>0.95 (5% prior volume), low region u0<=0.95 (95%). High logL is
11 minus0.5 times the sum of squared standardised deviations over the other13
active coordinates, centre0.5/sd0.25. Low logL is either exactly0 (flat) or
-0.5*((u14-0.5)/0.25)^2 (smooth one-coordinate stratum). For each shape compare
low offset0 against-13.5, keeping the high geometry, volume and seed fixed.
This is a toy-only counterfactual;13.5 is the review's proposed decrement, not
an evaluated or endorsed biological penalty.

Let z=0.25*sqrt(2*pi)*(Phi(2)-Phi(-2)). Exact high evidence contribution is
0.05*exp(11)*z^13. Low contribution is0.95*exp(offset) times1 (flat) or z
(smooth). Region posterior mass is each contribution divided by their sum;
compute and report it before sampling. This illustrates why an11-unit height
gap does not fix posterior occupancy without integrating the regional volumes.
The inactive posterior is uniform; high-region active marginals are truncated
Gaussians and u0 is region-uniform, with exact mixture CDFs available.

Seeds17701–17705, four fixed variants, nlive800/rslice3/multi, serial. Benchmark
first flat/offset0 seed, per-run hard120s and batch cap15min; stop batch on
error or overrun rather than adding target variants. Record initial high-group
count, accepted proposal ancestry, inter-region entries/exits, root concentration
through the cutoff, nuisance weighted CDF, active CDF, region mass and evidence.
Use paired seeds, keep all results. Hypothesis predicts delayed low-stratum
elimination plus poor high-region movement increases high-group concentration
and nuisance distortion relative to lowered-low-score runs. If score lowering
does not restore diversity, do not assert800 ancestors would result. If only
flat variants fail, isolate tied-likelihood handling rather than attributing
the result to the continuous real stratum. No automatic parameter sweep after
negative outcomes. Compare effects descriptively before any heldout criterion;
reserved confirmation seeds remain untouched.


D29 benchmark: flat/offset0/seed17701 completed3.26s, exit0; expected exact
high mass0.798115/logZ1.548762, sampled0.850832/logZ1.843626. Nuisance
KS0.03715. Initial45 high points, final27 high roots, no traced bounded-phase
crossings. High nuisance RMS0.15036 is not frozen. This benchmark neither
reproduces P16-sized null drift nor certifies evidence. Continue all19 remaining
registered cases, expected~1min total, one CPU, existing120s/run and15min/batch
caps. Traces use250-step wrapper chunks already checked in D0–D3; unknown
initial unit-cube roots are treated as independent and are not counted as
bounded-proposal crossings. No new settings selected from the benchmark.


## D30 — asymmetric toy outcomes and limits of the occupancy test

All20 registered cases completed, exit0, total72.87s. Independent quadrature
agrees with all four analytic normalisations within1e-12. Paired seeds have
identical initial high-group counts. No case was dropped or replaced.
Flat baseline versus lowered-low score: mean nuisance KS0.05347 versus0.05791;
mean final high roots26.2 versus27.8. Smooth baseline versus lowered-low score:
mean KS0.02656 versus0.03558; mean roots42.4 versus38.6. No systematic diversity
or nuisance-recovery improvement follows lowering the low score. None reproduces
P16 KS0.216–0.291; maximum here0.1102. Evidence errors and active CDF errors
are retained in full, not treated as passing inference validation.

Crucial limit: high-group nuisance RMS moves are0.142–0.163 across all cases,
so these toys do NOT reproduce the restricted high-group mobility (~0.028–0.042)
of the real conditional traces. Thus the result challenges occupancy asymmetry
ALONE, including the automatic800-independent-ancestors counterfactual. It does
not falsify the proposed interaction of occupancy with genuinely poor mixing.
Flat and smooth variants both retain few roots even after lowering the low score,
but root counts alone are not independent sample counts when within-lineage
moves are substantial. No flat-only P16-size failure supports a plateau-specific
explanation here. No further toy parameter sweep is authorised by these outcomes;
next causal work must address the missing real-surface mixing mechanism.

Source/weighted trace hashes, full case results, stage ancestry histories and
checkpoints preserved. Large arrays/checkpoints remain local; compact JSON
and diagnostic script are committed. Third real conditional seed17513 remains
in its original bounded run. No scientific target or biological penalty changed.


## D31 — read-only group-geometry discriminator after usage reset

The usage reset restored access; D29/D30 results committed as40d7b0c. Third
registered real repeat remains running. Next no-solve diagnostic compares
complementary-group covariance with whole-live covariance in the preserved
2000-step snapshots of17511 and17512. These exact new-run snapshots are valid;
never use aliased P16 historical bounds. Work in prior-CDF coordinates, compute
all15 generalised covariance eigenvectors and sqrt eigenvalue width ratios,
plus group counts, f-coordinate widths, and condition numbers. This is live
geometry, NOT posterior/prior constraint counting or evidence. Expected<10s,
one CPU, no new RNG or model evaluations.

If complementary directions are much narrower than the mixed population, this
motivates a controlled proposal-axis test on the unchanged real likelihood after
current expensive work completes. Covariance alone cannot prove which axes were
used or locate nonlinear bottlenecks, so do not assert causality from this result.
If no mismatch exists, retain the negative result; do not tune covariance floors
to manufacture it. No ridging unless numerically singular, in which case report
singularity and stop this diagnostic.


D31 result: all generalised eigenvalues positive without regularisation.
Complementary/mixed width ratios are0.01273–1.47064 (17511) and0.01707–1.28412
(17512); thus the tightest direction is about79 or59 times narrower. Both
tightest loading vectors are led by dTopt, dCp_scale, sigma, topt_scale. f_metab
loading is only0.00206/-0.00049. Its marginal live SD remains comparable
(whole/complementary0.2957/0.3153 and0.2822/0.2814). Covariance condition
numbers~1500–7300 do not require a ridge. This supports an anisotropic geometry
mismatch as a candidate explanation, not proof of actual proposal-axis use.

## D32 — next bounded real-path proposal-axis intervention (NOT YET RUN)

After third registered conditional run finishes or reaches its reviewed boundary,
test the missing mixing mechanism with six local proposals, one worker, no
concurrent expensive batch. Use exact preserved17511/2000 checkpoint, median
logL complementary live member (tolerance1e-6), unchanged original transform
and likelihood, saved scale and minimum-live likelihood cut. First re-evaluate
the parent and require mismatch<=1e-6; stop to diagnose rather than relax it.

Seeds17801–17803. For each seed select axes from saved current bound via
get_random_axes (not corrupted P16 history). Pair original axes with Cholesky
axes of complementary-group covariance, normalised to the same Frobenius norm
as the selected original axes. This changes relative shape/orientation while
holding overall norm and scale fixed. Both kernels use identical RNG state
after axis selection, rslice3, same parent and cut. Local covariance axes are
fixed for each probe, not recomputed from its proposed points.

Record actual axes, eigenvalues, displacement on all15 coordinates, nuisance
and active RMS, call count, likelihood and solver status, plus curve group.
Prediction: local geometry permits larger nuisance movement at comparable
acceptance cost. If it fails, do not increase slices or try a new ridge to rescue
it. A success motivates a stationary-kernel controlled continuation, not a
claimed posterior repair. Six transitions alone do not certify global mixing.
Limit each probe200 calls/600s, batch1800s enforced alarm, expected~2–10min
from previous local probes. No biological target, mask, prior or parameter fix.

D32 preparation implemented in axis_probe.py; --prepare-only executed with no
model initialisation or solves. plan.json fixes parent/index, actual recorded
axes, local axes, scale, paired RNG states and checkpoint hash before outcomes.
Preparation rerun reproduces the plan exactly; Frobenius norms match, local
axis covariance eigenvalues positive and paired RNG streams identical. Installed
RSlice source multiplies axes by a random direction, confirming Cholesky
orientation. Saved scale is internal_sampler.scale, not a Sampler.scale field
(the initial field-inspection attempt raised AttributeError and was corrected).
Imported preparation initially could not unpickle CLI __main__.ParentSlice;
explicitly binding the existing class as in the earlier read-only audit fixes
that provenance issue. Repeated preparation now passes from both invocation paths.
Runtime guards include per-probe200 calls/600s and1800s batch alarm; parent and
endpoint reproducibility checks stop on mismatch. Existing status blocks accidental
reruns. DO NOT execute the real probes until the current third conditional batch
finishes or reaches its reviewed boundary. No result of the axis intervention yet.


## D33 — finish third registered trace and dispatch prepared causal probe

Seed17513 reached7200s limit. Safe checkpoint2397 is independently audited: all
2397 accepted transitions and live ancestry accounted for. No original process
remains. Overall nuisance mean0.50150/KS0.04233, complementary516 live points
from29 roots; within-group RMS0.02319/correlation0.99689. No group crossings
at either recorded tolerance. This repeats restricted movement but not P16's
large inactive distortion; incomplete endpoint is not selected as a final result.

Finish remaining103 replacements via existing --resume, new1800s hard cap,
eight workers, expected~500–700s based on recent rate. Preserve initial timeout
and checkpoint. On completion only, independently audit2500 accepted links and
all live ancestry, then dispatch already prepared D32 six-proposal test in one
worker under its own1800s batch/600s per-probe/200call caps. No overlap or new
seed/target/criterion. Sequential runner finish_third_and_probe.py uses an
exclusive claim and stops before the next child on any error, timeout, partial
completion or audit failure; backup process-group cleanup timeout1980s each.
Expected total15–25min, maximum~1h plus cleanup. Existing completed work is never
overwritten. Model/settings remain unchanged; causal gate remains open.

D33 launch verified: session75740, coordinator17379, continuation child17388.
Resumed2397-step live/ancestry statistics exactly match audited checkpoint,
with zero unknown roots. Direct guard tests pass: incomplete trace blocks
geometry dispatch; existing claim blocks duplicate runner.


## D34 — first paired geometry intervention completed; independent-point replication

All third-repeat2500 replacements and accepted ancestry have passed final audit.
D32 six proposals completed146.91s; parent/endpoint reproducibility checks
passed and all endpoints remain above the same likelihood cutoff, complementary
to the zero-growth curve. Local axes increased absolute nuisance displacement
in all three pairs (~31.5,339.4,19.5 times), active RMS also increased (~5.5,84.5,
5.1 times). Calls including verification changed9->15,10->12,10->14. This is
controlled evidence that proposal geometry can restrict movement at this parent.
It does not demonstrate an unbiased posterior, adequate inter-region mixing, or
that this one point explains the original P16 posterior failure.

Next discriminating replication: use the SAME recipe at the median-logL
complementary live point in the independently evolved17512/2000 snapshot;
seeds17811–17813, original recorded axes versus local Cholesky covariance axes
with equal Frobenius norm, same paired RNG states/rslice3/scale/cut. New folder
axis_probe_replication, preserve original results. No selection by nuisance
movement, no slice/ridge adjustment. Parent and endpoint mismatch cap1e-6,
200calls/600s each,1800s batch alarm, one worker; expected~3min from D32.
On failed reproduction or adverse results stop this batch and interpret them,
not select a new parent. No concurrent model run. This is diagnostic replication,
not the fresh-posterior confirmation required by P17.


## D35 — explicit unattended overnight continuation

User explicitly requests autonomous overnight completion of P17 and diagnostic
follow-ons. Continue routine implementation, bounded causal tests, interpretation,
known-target and relevant real-path confirmation without waiting for further
messages. This does not authorise biological likelihood/prior changes, another
fixed biological parameter, subsequent biological fits, merges, or collaborator
messages. Do not confuse a completed batch with a completed investigation.

Existing thread heartbeat updated to15min cadence and ACTIVE, with explicit
instructions to interpret completed batches and execute next discriminating
work, preserve checkpoints, avoid duplicate/overlapping expensive work, and
continue after transient usage access returns without bypassing any rejection.
Record an exact persistent blocker instead of manufacturing a decisive answer.
Final deliverable remains the P17 gate-backed report and reviewable unmerged
branch/PR if access permits. Diagnostic Beta augmentation remains to be assessed
and implemented within unchanged-original-target scope; it cannot certify active
inference alone.

A bounded12h idle-sleep assertion was started for unattended local work, PID19116,
execsession63089. pmset confirms both idle-system and system-sleep assertions.
Existing older user sleep-prevention process69828 was left untouched. Keep app
open and machine powered; sleep prevention is temporary, not a settings change.
Current model job is D34 axis_probe_replication, session86160; five of six
proposals have reported at this check. Continue from final result before
commissioning the next batch. Sources, results, limitations and new preregistrations
belong in DECISIONS/report/launch_status; commit in parts as before.


## D36 — independent-point geometry replication is mixed

D34 replication completed6/6 in168.52s; all reproducibility checks passed.
Absolute nuisance movement local/original ratios are0.291,23.26,5.47; active
RMS ratios1.073,2.390,0.455. Calls8->16,11->19,10->13. Thus local axes do
not improve every transition at an independent parent. Retain the adverse pair;
no parent or seed replaced. The first intervention remains controlled evidence
of local restriction, not a universal repair. Repeated-chain behaviour must
now discriminate improved exploration from fortunate isolated jumps.

## D37 — repeated real-path transitions with an appended Beta control

This addresses external review's requested known answer on the actual surface
without replacing any original prior: append b~Beta(3,1), prior transform
b=u15^(1/3); likelihood calls the unchanged original P16 evaluator on the first
15 physical coordinates only. Existing f_metab remains present and unchanged.
For any fixed likelihood cut, the exact added-coordinate marginal is Beta(3,1),
CDF b^3=u15, even when the active starting point is biased. This is a conditional
real-path mixing diagnostic, NOT fresh posterior confirmation or a biological fit.

Three paired fixed-cut chains: median-logL complementary parents from preserved
17511/2000,17512/2000,17513/2397 snapshots; seeds17821–17823 respectively.
For each pair select original bound axes once with its seed. Alternative axes
are the group's Cholesky covariance normalised to the same Frobenius norm.
Append an independent Beta-CDF axis to each15D matrix with length equal to
original Frobenius norm/sqrt(15); both arms have exactly the same new-axis
length. This deliberately adds a dimension and changes geometry; never call
it a pure relabeling. Matrices remain fixed within each chain, selected before
its results. Prior transformation and original15-dimensional likelihood agree
exactly by construction; no added likelihood term or biological penalty.

Initial Beta-CDF value drawn once per pair from its seed; same starting point
and random state in both arms. Run32 rslice3 transitions per arm, no independent
nuisance refresh. Record every accepted16D state, likelihood, calls and both
inactive CDF coordinates, all15 original coordinate displacements and statuses
at verified endpoints. Report CDF errors, lag dependence and active movement
without IID p-values, arbitrary burn-in deletion or declaring32 steps enough
for convergence. Known target is uniform prior in the constrained cube; each
fixed-axis slice kernel is invariant for that target under deterministic exact
evaluation, but irreducibility/global mixing and numerical repeatability remain
to be checked. No active known-answer certificate is claimed.

Sequential six chains, one model worker,1000calls/1800s cap per chain and
10800s total enforced; checkpoint arrays each transition. Expected~15min/chain
from D32/D34 costs,~90min total. First chain is cost/validity gate: any timeout,
reproducibility failure or exception stops the whole batch; do not skip it or
launch subsequent arms. Parent must match archived logL within1e-6. Re-evaluate
current point every8 transitions and at end; stop on mismatch>1e-6. No concurrent
expensive batch. No new sampler-setting sweep or chosen thresholds after results.
This follows the mixed D36 finding; remaining P17 confirmation gates stay open.

D37 preparation checks passed: appended Beta transform leaves all first15
physical prior coordinates bit-identical across full Beta support checks;
b^3 reproduces its input cube coordinate within1e-14. Fixed plans reproduce
exactly; paired full matrix norms/new-axis lengths match, all local axes
positive definite. No prior real model process remained at launch. Batch
now running, session22850, log beta_path_chains.log, outputs beta_path_chains/.

D37 interim checkpoint: first original-axis arm17821 completed32 transitions
in666.61s/357 calls, passing all four scheduled repeatability checks. Its new
Beta-CDF coordinate stayed within0.25988–0.36851 (mean0.30954, descriptive
KS0.63149). This directly records limited exploration in32 steps, not an
IID-significance claim or proof that a converged nested posterior is biased.
Paired local arm is running; do not select or interpret the intervention from
this first baseline alone. Trace shape33x16, means and repeatability records
independently checked; completed arm checkpoint and hash retained.

D37 first paired chain completed: local17821 took751.70s/408calls, all four
repeatability checks passed. Beta-CDF RMS step0.05560 versus original0.01594
(~3.49x), existing f_metab RMS0.12925 versus0.02063 (~6.26x). However,
Beta-CDF KS remains0.5660 versus0.6315, and local coverage only0.0260–0.4340
over32 transitions. Thus larger moves do NOT yet establish known-prior
recovery. This is retained as a limitation; no extra steps or burn-in trimming
selected after inspection. Second parent original arm is running; complete
the remaining registered pairs before deciding the next batch.


## D38 — all real-path Beta chains completed; geometry is not a certified repair

D37 completed6/6 in5731.83s, no time/call-limit breach or repeatability stop.
Beta-CDF KS original/local by pair:0.6315/0.5660,0.4204/0.3969,0.5754/0.5416.
The original f_metab KS improves in two pairs but worsens in the second
(0.3349->0.4460). Larger local-axis moves have not recovered the known
added-coordinate prior over the registered32 transitions. Preserve every arm;
no retrospective extra steps, burn-in deletion, or pass threshold. These short
chains demonstrate limited mixing on the real surface, not complete posterior
calibration or a proof that axes alone caused all P16 error. The original
computational pathology remains unresolved at the full P17 gate.

## D39 — global independence-Metropolis candidate on known targets only

Both axis changes and longer local slices leave global inference unverified,
and the narrow-mixture control had no bounded-proposal core entries. The next
method tests explicit between-region proposals, with exact density correction,
rather than another local slice setting. No real-model fit is authorised by
this candidate test.

Construct frozen Gaussian proposal components from weighted baseline17001 rows:
one component for smooth; two for spike (existing six-sigma core classifier
abs(u0-0.2)<0.003 versus complement). This uses imperfect pilot data, not true
mixture weights. Fixed component probabilities total0.9 divided equally;0.1
uniform cube component guarantees full cube support. Covariances are weighted
empirical and must pass unregularised Cholesky; stop on singularity, no ridge
selection. Proposals are draws on R^15 from this mixture; outside-cube draws
are rejected, NOT repeatedly redrawn until inside. Inside, accept with
min(1,q(old)/q(new)) if unchanged logL(new)>cut. Exactly32 proposal attempts
per replacement, retain self-transitions. Never condition on at least one move.
For uniform constrained-prior target, both directional probability fluxes equal
min(q(old),q(new)); this is the detailed-balance reason for the correction.
A frozen proposal is independent of current chain state; no fitted-on-the-fly
state-dependent mixture weights. The pilot may be biased; acceptance corrects
the proposal mathematically but does not guarantee adequate practical mixing.

Before nested controls: independently verify the proposal density and finite
detailed-balance identity, and test preservation of a known disjoint-interval
uniform target from2000 independent exact starts, one32-step transition each.
DKW alpha0.001 is valid ONLY for those independent endpoint draws. Include a
deliberately uncorrected proposal as a negative control. Fixed test seed17740.
Then benchmark smooth seed17751; if within180s and no implementation failure,
run smooth/spike seeds17751–17755, nlive800, original prior/dlogz0.1 and bound
settings, one CPU. Per-run180s alarm, batch1800s; checkpoint each run. Expected
~30–60s per run from32 global attempts, benchmark governs actual cost. Evaluate
active CDF, region mass, evidence and inactive CDF together; no nuisance-only
certificate. These are development seeds, not reserved17901–17905 confirmation.
No parameter/target changes, no blind further kernel-setting sweep after failure.

## D40 — pilot-informed global proposals still fail; isolate inherited geometry

D39 completed10/10. Smooth inactiveKS0.0073–0.0118 and activeKS0.0077–0.0145,
but spike region masses0.05786,0.39742,0.00763,0.04212,0.11258 versus0.30437.
Spike seed17752 inactiveKS0.33473: P16-sized drift is possible even with a
mathematically invariant global kernel when the frozen proposal is inadequate.
Self-loops/duplicate vectors remain in all outputs. No successful repair claim.

The pilot fit came from a trapped run. To distinguish inadequate pilot geometry
from failure of the corrected global-kernel implementation, change ONLY the
frozen Gaussian means/covariances to the known spike target geometry. Component
means0.2/0.75 in coordinate0,0.5 elsewhere; independent SD0.0005/0.1 in coordinate0,
0.15 in other active coordinates, nuisance SDsqrt(1/12). Keep equal component
weights0.45/0.45 plus0.1 uniform,32 attempts, same seeds17751–17755,800live,
same stopping/bound settings. This deliberately oracle-informed proposal is a
diagnostic positive control, not a deployable model repair. No target changes.
Prediction: active region weights and nuisance coverage improve together if
inherited bad proposal geometry is the limitation. Retain contrary outcomes.
Five runs,180s each/900s batch cap, one CPU, expected~60s total from D39 costs.
This is development only; reserved confirmation seeds remain untouched.

D40 completed5/5, approximately94s total. Region masses0.31070,0.32154,0.32791,
0.30491,0.32686 versus0.30437. Independent audit of all14 active marginals gives
maximum KS0.0129–0.0257; inactiveKS0.0063–0.0107. LogZ errors-0.3139,-0.0649,
+0.3084,-0.1434,+0.1537 remain material relative to nominal errors0.127–0.135;
do not call evidence uncertainty calibrated from five runs. The frozen pilot
geometry failed where oracle geometry succeeded using the same corrected kernel.
This isolates inadequate proposal geometry on the analytical control, not a
deployable correction or a complete causal attribution for the real model.
The pilot narrow component's nuisance mean0.8767 and correlation eigenvalue
minimum0.00218 (true independent coordinates) show that trapped-pilot structure
was carried into proposals. Broad component minimum correlation eigenvalue0.7527.
All15 completed control arrays independently audited; hashes and all active
CDF distances are in independence_audit.json. No seed omitted.

## D41 — isolate spurious pilot correlations without oracle means or widths

D40 changed means, widths and correlations together. The narrow pilot correlation
matrix has minimum eigenvalue0.00218 although the known target factorises within
components. Test removal of ONLY off-diagonal covariance entries, retaining every
pilot mean, marginal variance, component weight and source hash. This uses no
oracle parameter values. It distinguishes spurious directional correlations from
biased pilot centres/marginal widths as limiting geometry. Prediction: if the
correlations dominate, active and inactive recovery improve together; if not,
diagonalising alone is insufficient. No assumed cure for correlated real biology.
Use spike seeds17751–17755 paired with D39, unchanged32 attempts/nlive800/settings.
One CPU,180s/run900s/batch, expected60–90s; stop on failure, retain all results.
No scientific target changes or real-model run. Fresh confirmation still reserved.

D41 completed5/5 (~56s), independently audited. Region masses0.5311,0.7309,
0.1172,0.0899,0.1594; maximum activeKS0.1888–0.6961; inactiveKS up to0.6218.
Removing correlations alone is insufficient and sometimes substantially worse.
Do not deploy diagonalisation on the real path. Preserve all failures.

## D42 — likelihood-derived local geometry, not supplied oracle values

The pilot means and widths are also unreliable. Test whether numerical local
optimisation and curvature of the unchanged analytical likelihood recover usable
geometry from those same component centres. No true target means/widths supplied
to fitting. Optimise14 active cube coordinates with L-BFGS-B, scaled by each
pilot marginal SD; nuisance remains in sampler and gets a proposal-only Gaussian
centre0.5/variance1/12 from its proved prior. This is not a fixed model parameter
or independent replacement of output nuisance values. The proposal still uses
the exact MH density correction and all active diagnostics remain required.
Finite difference gradient step1e-4 in scaled coordinates; max500 iterations,
20000 likelihood calls per component. Estimate negative-logL Hessian centrally
at scaled steps1e-3 and2e-3; require relative matrix difference<1e-3 and positive
definite Hessian without ridge. Stop if optimisation fails, ends at a bound,
or curvature fails. Two starting components from baseline17001, one CPU,
fitting60s cap. Save optimisers, Hessians, call counts and source hashes.
If geometry checks pass, run same spike17751–17755 development protocol as D40,
32 attempts/nlive800,180s/run900s/batch. Expected fitting<5s and sampling~90s.
Prediction: target-derived geometry improves active and inactive recovery together;
otherwise reject this candidate without a parameter sweep. No real-model job yet.

D42 fitting stopped with L-BFGS-B ABNORMAL_TERMINATION_IN_LNSRCH before a
proposal was saved; no sampling launched. A recording-only rerun retains the
failed optimiser vector/gradient in forward_failure.json. This is not a fitted
geometry pass. The forward difference used by scipy's eps option has a known
nonzero gradient at a quadratic minimum: for f(x)=x²/2, [f(h)-f(0)]/h=h/2.
It can therefore ask a line search to descend from an already minimal point.

## D43 — discriminate finite-difference optimiser failure

Before abandoning likelihood-derived geometry, replace the forward gradient
with a central difference at the SAME1e-4 step. Verify the quadratic check
independently. Keep starts, optimisation limits, acceptance of success/bounds,
Hessian steps/checks and sampling protocol unchanged. This tests a specific
gradient bias, not a tolerance relaxation. Save and retain the original failure.
Same60s fit cap. If central fit fails, stop this candidate rather than sweep
optimiser settings. If it passes, D42's registered five sampling runs apply.

Central-gradient fit passed both components in0.042s/1714+960 calls; relative
Hessian differences4.00e-10 and1.86e-10, positive definite without ridge.
The quadratic check initially used exact floating equality and failed by rounding
(4.9999999999999996e-5 versus5e-5); a1e-14 relative comparison passes. The central
fit was inadvertently dispatched before inspecting that unit-check failure;
record this ordering error, corrected check now passes before sampling.
No fit acceptance tolerance changed. Proceed with registered five toy controls.

D43 completed5/5 sampling runs (~92s). Region masses0.31070,0.32031,0.32792,
0.30255,0.32446 versus0.30437; inactiveKS0.0063–0.0124. Likelihood-derived
geometry reproduces the oracle improvement without supplying true active means
or widths to fitting. Still development only, and evidence uncertainty remains
uncalibrated. This does not certify transfer to the cliff-bearing real surface.

## D44 — real-surface local curvature readiness before any proposal fit

Do not apply the successful smooth-toy fit blindly to biology. At the existing
D37 first parent (17821, conditional17511/2000 median complementary point),
measure diagonal central curvatures on14 active coordinates at offsets0.02 and
0.04 times the complementary live marginal SD. This is a local diagnostic,
not optimisation, posterior sampling, or a new biological calibration.
Use the unchanged15-coordinate prior/likelihood and saved parent; exclude only
the proved inactive coordinate from curvature measurement, not from the model.
Recheck baseline before and after all stencils; require1e-6 agreement with saved
LL. Save every evaluation and feasibility capture. If offsets cross cube bounds,
record untested; do not clip them. For each tested coordinate report both
curvatures in scaled units and relative difference divided by max(1,abs(k1),abs(k2)).
Readiness requires every tested coordinate difference<=1e-3, no untested axes,
and baseline repeatability. This is necessary only, not full-Hessian positivity
or global Gaussian adequacy. Failure bars direct transfer of the D42 fitter;
do not retune steps/thresholds. Budget80 calls/300s, one fresh solver worker,
expected~120s based on D37 costs, checkpoint after each likelihood evaluation.
No other model process is running. Stop on repeatability or execution failure.

D44 completed58 evaluations in121.00s; final baseline differs7.43e-13.
Independent audit confirms source hash and all curvatures. Seven axes fail:
dTopt,topt_scale,dCp_scale,tm_scale,kcat_scale,sigma,clearance_mult. Relative
differences0.102–0.938. All58 points retain identical solver feasibility status
and respiration support mask. Thus these local changes do not require a mask
transition, although this does not settle the global stratum hypothesis.
Do not transfer the toy Laplace fitter directly. Curvature at this non-optimal
parent is not curvature at a mode and this is not a universal Hessian claim.

## D45 — repeat the stencil to separate local structure from solver history

D44 repeated only the baseline. Re-evaluate all58 saved inputs in REVERSE order
in one fresh model, preserving the full original target and f_metab values.
Require maximum absolute logL difference<=1e-6, as in earlier repeatability
checks. Recompute curvature from the repeated values and retain changed
feasibility/mask outcomes. Prediction: if D44 is reproducible local structure,
the seven large step-dependent changes persist with likelihood differences
below1e-6. If not, numerical state remains implicated and no smoothness claim
is justified. No optimisation or posterior fitting. One worker80calls/300s,
expected~120s from D44; record every evaluation. No other batch active.

D45 completed58 calls/121.50s. Maximum absolute likelihood difference4.08e-10
passes1e-6; the same seven axes fail the unchanged curvature-readiness rule.
This bounds solver-history variation at these actual perturbed points and
supports reproducible scale-dependent local curvature. It does not establish
mathematical nondifferentiability or rule out optimisation elsewhere. Both D44
and D45 preserve the scientific target. No posterior fit was launched.
The next method must accommodate real-surface geometry without relying on
the failed direct local-quadratic transfer. P17 confirmation remains open;
known-target improvements alone do not authorise claiming a repaired sampler.

## D46 — trace global-kernel stalls and region exchange without changing draws

The D39 pilot run17752 has inactiveKS0.3347 while oracle geometry with the
same seed recovers it. Replay these two analytical runs with recording-only
proposal diagnostics: cutoff, parent/child first active and nuisance coordinate,
parent/child proposal log density, accepted attempts and rejection counts.
Require saved samples and log weights bit-identical to the corresponding D39/D40
arrays before interpreting traces. This separates early broad-cut stalls from
late narrow-region trapping; either may be present. Report exchange between
the existing six-sigma narrow core and complement by cutoff stage, retaining
self-transitions. No assumption that a stationary kernel produces independent
live points. Same seed/settings/target/proposal/32attempts. One CPU,180s each,
expected30s combined. No real-model evaluations or new sampler setting.

D46 completed both replays bit-identically in samples, logL and log weights.
Pilot narrow-core parents have100% self-transitions in stages3/4 (250+427
kernels); nuisance RMS0. Broad parents remain mobile. Oracle core parents
remain mobile and exchange regions. This isolates a region-specific exploration
failure on the toy, not just early broad-cut rejection. Trace hashes and
stage summaries are in global_trace_audit.json. The subsequent usage interruption
did not run the proposed hybrid test; resume it explicitly below.

## D47 — compose the global kernel with coordinate slice updates

Keep D39's failed pilot proposal and32 corrected global attempts. Follow each
kernel with one randomly ordered sweep of all15 cube-coordinate slice updates,
using installed dynesty generic_slice_step, unit initial width, stepping-out
(not doubling). Each slice targets the same unchanged constrained uniform prior;
composition preserves that target if both component kernels do. This makes
local progress possible when the frozen global proposal misses a region's
conditional shape. It needs no Hessian, oracle means or widths. Do not infer
active correctness merely because the inactive coordinate now moves freely.
First verify stationarity on2000 independent exact starts in two disjoint
2D boxes of unequal area, seed17841; check both marginal CDFs and region mass
using a simultaneous DKW/Hoeffding bound with total alpha0.001. This is valid
only for independent exact-start endpoints, not nested output.
Then benchmark spike17752 against D39/D46,180s cap, original800live/stopping
settings. If valid and affordable, complete remaining17751/17753–17755, each
180s, total900s. Expected~30–60s/run; one CPU, no model solves. Preserve every
outcome, active CDFs/evidence/region weights and inactive CDF together. Fresh
confirmation remains reserved. No scientific change or new fixed parameter.

D47 unit control passes: marginalKS0.01745/0.01388 and region error0.009,
simultaneous bound0.04664. Corrected the wrapper to accept actual dynesty namedtuple
arguments before benchmarking; repeated the unit test with that actual type.
Benchmark17752 completed32.91s: inactiveKS0.00798, active-firstKS0.0660,
region0.36998 versus0.30437, logZ error+0.12666; zero duplicate full vectors.
This is movement improvement but not an accuracy certificate. Library call
accounting1.21M includes out-of-cube slice attempts and is much larger than
D39. Complete remaining four predeclared repeats before interpreting adequacy.

D47 completed5/5 (~164s total), independently audited. All inactiveKS0.0080–
0.0110 and no duplicate full vectors, but region masses0.3548,0.3700,0.3601,
0.1563,0.1963 versus0.3044. Restoring local movement does not establish region
weight accuracy. No real-model transfer; substantially higher call accounting.

## D48 — isolate region-population allocation using exact prior stratification

Rather than add another local kernel setting, partition the existing spike toy
at its already-used core classifier A=abs(u0-0.2)<0.003. Exact prior volumes
are0.006 and0.994. Run each conditional prior with400live original rslice3,
then combine unnormalised weights with the respective prior volume. Total
initial allocation remains800, target and scientific prior after recombination
are exactly unchanged: Z=0.006*Z_A+0.994*Z_notA. The control distinguishes scarce
regional representation from local nuisance mobility; it explicitly supplies
the known partition, not Gaussian likelihood parameters or oracle mode weights.
Conditional prior transforms: core0.197+0.006*u0; complement let v=0.994*u0,
return v below0.197, otherwise v+0.006. Other14 coordinates unchanged.
Use development seeds17751–17755 paired across regions via independent spawned
RNG streams. Original stopping0.1/multi/rslice3,400live each, no hybrid/global
proposal. Test transform range/volumes and recombination arithmetic first.
Benchmark one pair17751,180s per stratum/360s per pair, expected<30s/pair;
if valid continue four pairs, batch1800s. One CPU, checkpoints30s.
Report all active/nuisance CDFs, evidence, region mass and runtime after exact
recombination. Do not call this a real-model remedy: the corresponding biological
partition and its prior measure are not supplied by this toy. No model solves.

D48 completed5/5 pairs (~21s), independently checked against analytical
conditional evidences and exact weight recombination. Region masses0.2463–
0.3305, but all10 conditional evidence errors positive (+0.1564 to+0.6127)
and combined errors+0.1707 to+0.5289. Do not certify stratification alone.

## D49 — direct rejection within the unchanged known partition

The D48 pattern implicates within-region sampling as well as region allocation.
Change only sample='rslice' to sample='unif' in the same two conditional-prior
runs. Keep400live per stratum, transforms, seeds17751–17755, bounds/stopping and
exact prior-volume recombination. This removes slice-chain dependence; it does
not guarantee that ellipsoid bounds cover every constrained point. Unlike the
earlier failed100M-call unpartitioned rejection experiment, this control has
separate well-conditioned region coordinates. Benchmark17751 first under the
unchanged180s/stratum cap; stop if unaffordable, no cap extension. If valid/costed,
run remaining four pairs, batch1800s, one CPU. Expected<60s/pair, benchmark
governs actual continuation. No real-model job. All results retained.

D49 completed5/5 pairs (~38s), independently audited. Combined logZ errors
+0.1046,-0.1004,-0.0021,-0.0394,+0.0539; region masses0.2355–0.3705 and
inactiveKS0.0098–0.0159. The systematic conditional evidence overestimate is
absent in these repeats, but five runs do not calibrate uncertainty reliably.

## D50 — calibrate the known-target error budget before reserved confirmation

Freeze the D49 partitioned rejection method. Use100 calibration seeds18101–
18200 on each of smooth and spike, then assess before launching reserved
17901–17905. All scientific targets/priors and400live per stratum unchanged.
This is confirmation of a known-partition computational control, not a claim
that a corresponding real-model partition is available.
Per-run joint discrepancy score is max(inactiveKS/0.02,maxActiveKS/0.05,
abs(regionMass-truth)/0.05,abs(logZ-truth)/0.15). These fixed scales only put
quantities on comparable units; they are not adjustable pass tolerances.
For each target freeze the maximum of100 scores as its reference envelope.
Under exchangeable independent repetitions this is a100/101 (~99%) pointwise
prediction envelope, NOT simultaneous99% coverage of five future runs and
NOT proof of small absolute error. Report the actual envelope in original
units and any broad limits. Do not bias-correct estimates or discard outliers.
Also report mean Z/Ztruth and its99% t interval as an approximate large-sample
bias diagnostic; distinguish logZ Jensen effects from Z bias. If discrepancies
or bias remain, investigate rather than declare the control certified.
Independently simulate2000 exact-posterior CDF reference datasets of400 points
for each target (the15 marginal CDF coordinates are independent Uniforms),
seed17842, and report their99th-percentile joint score. These are reference
effect scales only, never IID p-values assigned to nested samples.
One CPU, sequential targets, expected~25min total from D49 costs;180s per
stratum,1800s per target, restartable per completed seed, checkpoints30s.
Stop on failure/budget and preserve all completed outcomes. No model solves.


## D51 — 13 September 2026: PI stopping-rule closure, negative diagnostic result

Authority: the user's explicit “Addendum — P17 closes as a negative diagnostic result. Consolidate, prepare integration, hand over”, preserved verbatim at `prompts/P17_PI_closure_addendum_2026-09-13.txt`. This replaces the original autonomous-until-decisive stopping instruction. The original gate requirements remain unchanged and the real-model correction gate has NOT passed. No sampler-only candidate, biological fit, likelihood/prior change or additional fixed parameter follows this decision.

The sole running D50 batch was allowed to finish: 100/100 smooth and 100/100 spike cases (400 conditional runs), 1,439.57 s. The independent closure audit reconstructs raw analytical likelihoods, weights, conditional and combined evidence, all CDFs and region masses, and verifies all 200 result hashes. All assertions pass. Mean Z/Ztruth is 1.008075 (approximate 99% interval 0.974121–1.042029) for smooth and 1.003983 (0.975790–1.032176) for spike; score envelopes 2.746233 / 2.248029. This is known-partition calibration, not real-model confirmation or a completed held-out certificate. Reserved seeds 17901–17905 remain unused. The producer's final status phrase “inspect before reserved confirmation” is preserved as historical output; this entry supersedes any instruction to launch it. The running.claim file is retained as evidence, not an active job. The recurring investigation automation was paused on receipt of closure.

The final report consolidates all failed and working toy interventions with their limits; the prior chronological report is preserved verbatim. RIGOUR.md records prospective rules and historical exceptions (including D15 timeout and D43 ordering). TARGET_REVISION_SPEC.md is preparation only, pending PI approval in a separate Claude Code session. Integration/handover inventories preserve external dirt by file and hash. All P17 artifacts, previously ignored logs/caches and inherited P16 audit files are committed; nothing is pruned. No merge, push or branch switch is performed; no other worktree content is edited. Git writes needed for this branch use its shared worktree metadata only.

D44/D45 establish reproducible scale-dependent curvature at ONE non-optimal point, undermining direct quadratic transfer without proving every sampler fails or that the likelihood is the sole cause. The 80–87% living fractions belong to analytical toy priors/likelihoods and are NOT revised biological targets or thresholds. dTm=0 assumes the meltome mean is exact, excluding uniform melting-temperature uncertainty otherwise absorbed by tm_scale and catalytic parameters. R1 remains open, R3 provisional, R4 untouched, and D/E/F/M9 blocked behind approved target revision and validation. Closure records the exact unmet requirements rather than manufacturing a decisive answer.
