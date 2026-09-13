# P17 final report — negative diagnostic result

**Closed by PI decision, 13 September 2026. The audited inference is unreliable. Several mechanisms are characterised, but no tested computational correction has met full confirmation on the real model. P17's original decisive-conclusion gate did not pass.** The PI [closure addendum](../../prompts/P17_PI_closure_addendum_2026-09-13.txt) changes the stopping rule: stop new sampler candidates, finish and audit the already running D50 batch, preserve everything, and prepare a separate target revision. This is not sampler validation or permission for further biological fits.

Two limits are central. **D44/D45 concern reproducible scale-dependent curvature at ONE non-optimal point.** They undermine direct transfer of the tested quadratic approximation; they do not prove that all samplers fail or that the likelihood is the sole cause. **The 80–87% living fractions are analytical toy outcomes from specified priors and likelihoods.** They are not targets or acceptance thresholds for revised biology.

All P16/P17 statements condition on **dTm=0**: the meltome mean is assumed exactly right. Uniform melting-temperature uncertainty is excluded and would otherwise be absorbed by tm_scale and catalytic parameters. No additional biological parameter was fixed; no scientific target, prior, allocation, maintenance or medium was changed in P17.

## Exact null target and independent reproduction

Configuration D uses growth-dependent proteome allocation; measured temperature-dependent allocation is off, and temperature-dependent maintenance is on. The sampled f_metab is inactive on this path. Its independent prior is Normal(0.28,0.03²), truncated to [0.15,0.45]. The f_maint bound [0.2,0.5] cannot activate a sum-to-one constraint (maximum sum 0.95). The parameter mapping from fifteen free coordinates to sixteen model coordinates was checked by name with dTm fixed to zero. Nominal allocation settings are not the unused sampled coordinate.

Consequently, for the intended target, p(f_metab | data) equals its prior exactly, and its truncated-normal CDF is Uniform(0,1). This is a known-answer instrument, not an inference that biological allocation is identified. The weighted CDF distance is descriptive: nested samples are dependent, and weight ESS is not independent sample size. Do not attach IID KS p-values.

`independent_audit.py` reconstructed the saved P16 samples, likelihoods, integrated weights, final 800 live points, inverse priors and stopping trace independently of the earlier audit's posterior helpers. Checkpoint/sample arrays agree, inverse-prior cube error is at most 1.7e−15, there are no duplicate full vectors, and reported-weight normalisation differs from one by less than 1.5e−13. Both runs actually reached dlogz < 0.1; a separate reporting defect labelled logzerr as dlogz_final and was isolated. None of these arithmetic checks repairs sampling.

| P16 output | red1 | red2 |
|---|---:|---:|
| Weighted inactive prior-CDF mean (target 0.5) | 0.319120 | 0.393715 |
| Weighted CDF distance (target zero in the limit) | 0.290878 | 0.216146 |
| log Z | −26.029894 | −26.052380 |
| Reported log Z error | 0.109358 | 0.099392 |
| Actual final dlogz | 0.099993 | 0.099958 |

Fourteen of fifteen marginals disagree under the historical comparison rule, with strand-bootstrap checks also adverse. Agreement in log Z therefore does not validate the posterior. P16's saved eigenspectrum and marginals remain diagnostic outputs, not validated uncertainty estimates. Runtime source provenance is not exhaustive: committed model sources agree across the relevant revisions, but transient uncommitted historical runtime changes cannot be excluded by a complete contemporaneous hash manifest.

## Characterised mechanisms and their limits

**Stratum-dependent exploration and ancestry concentration (D13–D38).** The zero-growth/no-scored-O2 stratum has a one-dimensional likelihood depending on disc_growth, with maximum −18.68250229422251 at 1.1407216216373017. The respiration clamp masks nonfinite or nonpositive O2, allowing missing predictions to contribute no respiration term. P16 posterior weight algebraically compatible with this curve is 0.531688 / 0.814783. Selected compatible states are infeasible at every temperature; compatibility alone is not a solver-status classification of every sample. This is not an exactly flat positive-volume likelihood plateau: disc_growth varies.

Three independently seeded conditional diagnostics started at the same archived 800 active positions from red2/6800 with independently redrawn inactive coordinates. All 800 likelihood rechecks agreed within 1e−6 (maximum 1.3409e−8). Each finished the registered 2,500 replacements, including the third repeat's final 103. These are continuations from biased active positions, not fresh posterior/evidence runs.

| Conditional seed | Final inactive CDF mean / distance | Complementary slots / initial roots | Complement nuisance movement |
|---|---|---|---|
| 17511 | 0.511148 / 0.082725 | 634 / 30 | RMS 0.02769; parent-child r=0.99602 |
| 17512 | 0.512886 / 0.083451 | 800 / 32 | RMS 0.04231; r=0.98890 |
| 17513 | 0.508306 / 0.048993 | 592 / 29 | RMS 0.02289; r=0.99698 |

The compatible stratum is much more mobile (first repeat RMS 0.15245, r=0.86106). Few complementary ancestors and restricted movement recur; no traced region crossings were seen. Prior reset does not reproduce the full P16-sized global inactive drift in these finite traces. Small ancestry counts alone neither quantify the global posterior error nor establish complete causal attribution.

**Group/pooled width mismatch (D31).** The narrowest complementary/pooled covariance width ratios are 0.012725 and 0.017074: about 79-fold and 59-fold narrower. Tight combinations load on dTopt, dCp_scale, sigma and topt_scale; the inactive coordinate has little loading, and its marginal width is similar across groups. Pooled direction scaling can therefore impede a coordinate that is itself unconstrained. This is conditional live-set geometry, not a posterior eigenspectrum.

**External occupancy hypothesis (D28–D30).** A 95%-prior low region and 5%-prior upper region, separated by about 11 likelihood units with fourteen-dimensional structure, tested whether occupancy alone produces upper-region ancestry collapse. Twenty flat/smooth and lowered-low-stratum controls retain approximately 26–42 upper roots, yet nuisance RMS remains 0.142–0.163 and maximum CDF distance is 0.1102. Thus occupancy alone did not reproduce P16's large drift; interaction with restricted mixing remains plausible. Lowering a low stratum does not automatically supply 800 independent living ancestors. The exact upper posterior fractions 0.7981 / 0.8686 belong only to these toys.

**Local curvature and numerical state (D44/D45).** At one non-optimal saved parent, diagonal stencils at 0.02 and 0.04 group SD produce relative curvature changes of dTopt 0.204688, topt_scale 0.938242, dCp_scale 0.299965, tm_scale 0.574308, kcat_scale 0.279304, sigma 0.874742 and clearance_mult 0.102119, against the registered 0.001 quadratic-readiness criterion. All 58 evaluations preserve feasibility and respiration masks (15°C infeasible, remaining temperatures optimal). Baseline repeat difference is 7.43e−13. Fresh-model reverse replay of all inputs differs by at most 4.08e−10 and finds the same seven axes. This defeats the direct tested local-quadratic transfer, not the possibility of other geometry or samplers. Negative curvatures at a non-optimum are not evidence of a posterior mode.

A separate earlier low-growth input showed likelihood variation of about 0.088 despite identical canonical LP matrices, bounds and objectives; basis reset did not fix it. Selected high-weight/bottleneck replays were stable. Numerical-state sensitivity exists at some inputs, but does not explain the D44/D45 result or establish a sole cause of P16 bias.

**Recording defect, with withdrawal (D17–D19).** Dynesty 3.1.0's bound-history entries alias one mutable bound: 92/90 historical entries each represent one distinct object. A recording-only deepcopy yields 24 distinct toy bounds instead of one without changing sampled trajectories. This is not a sampling correction. Historical-axis interpretations from `real_kernel_probe`, `stratum_probe` and `bound_coverage` were withdrawn; their files remain. Reconstructed live positions and newly snapshotted bounds remain usable. No installed library was changed.

## Intervention register — adverse results retained

The narrow-mixture control has exact P(u0<0.5)=0.3043739263. Unless stated otherwise, five development repeats are retained. Full per-seed results, runtime, arrays, checkpoints and audit hashes remain in their original directories and DECISIONS; the pre-closure chronological report is preserved as `report_before_PI_closure_2026-09-13.md`.

| Intervention | Observed result | Conclusion / evidence |
|---|---|---|
| Plain versus chunked wrapper; transformed priors; serial/pool | Plain/chunked coordinates and likelihoods identical, weights within ~1.5e−12; prior-transform roundtrip equivalent. Pool queueing changes RNG trajectories without reproducing the large smooth-control failure | These tested wrapper mechanisms do not explain the failure; `control_comparison.json` |
| Original rslice, 3 slices | Narrow-mixture region weights 0.00720, 0.11692, 0.01121, 0.00860, 0.00628 | Severe active error despite inactive distances 0.014–0.065 |
| Increase to 15 slices | Region weights 0.08359, 0.78499, 0.23061, 0.04727, 0.40121; smooth/ordinary-mixture mean log Z error improves +0.233→+0.069 / +0.227→+0.073 | Useful toy improvement, no reliable narrow-region repair (D6) |
| Single bound | Region weights 0.06383, 0.06326, 0.00709, 0.00854, 0.03541 | Multi-ellipsoid splitting is not necessary for the failure (D7) |
| Original traced slices | 2–8 initial narrow-core points; no six-SD-core entries/exits; core inactive r≈0.9993, RMS≈0.0114 versus outside≈0.1527 | Local trapping reproduced on a known target (D8–D9) |
| Full-interval coordinate Gibbs | Region weights 0.2371, 0.3949, 0.3727, 0.2177, 0.3357; 5–6 million calls/run, 100–120 s | Exact conditional updates are not independent joint draws; no certified repair (D10–D12) |
| Unpartitioned independent rejection | Incomplete after ~3.6 h and 100.8 million calls | Retained failure; intended runtime cap was not enforced, a workflow error (D15) |
| Nuisance-only refresh | 35 diagnostic copies give inactive distances ~0.009–0.021 while bad active weights remain exactly unchanged | Explicitly falsifies nuisance recovery as sufficient (D26) |
| Real local-group versus pooled axes | First three paired proposals improve inactive displacement 31.5×, 339.4×, 19.5×; replication ratios 0.291×, 23.26×, 5.47×; active ratios also mixed | No uniform geometry repair (D32/D34/D36) |
| Real-path appended Beta(3,1), 32 transitions | Beta-CDF distances original/local: 0.63149/0.56599, 0.42039/0.39694, 0.57536/0.54158. f distances 0.71067/0.35951, 0.33493/0.44597, 0.48160/0.45497. Six chains, 5,731.83 s | All 24 repeat checks <1e−6, but poor known-prior coverage on the real path; short correlated chains are not a posterior certificate (D37/D38) |
| Pilot-fitted global Metropolis, 32 attempts | Spike region weights 0.057856, 0.397422, 0.007630, 0.042116, 0.112575; max inactive distance 0.334734; max active distance 0.382679 | Correct stationary kernel inherits bad pilot geometry (D39) |
| Oracle global geometry | Region weights 0.310703, 0.321536, 0.327914, 0.304908, 0.326863; inactive distances 0.0063–0.0107; active 0.0129–0.0257; log Z errors −0.3139 to +0.3084 | Working geometry control, unavailable real oracle; evidence errors remain (D40) |
| Diagonalised pilot geometry | Region weights 0.531051, 0.730877, 0.117156, 0.089870, 0.159435; max inactive 0.621754, active 0.696149 | Removing correlations alone fails (D41) |
| Likelihood-derived quadratic geometry | Forward-gradient optimiser fails line search. Central-gradient fit succeeds on toys; region weights 0.310703, 0.320306, 0.327922, 0.302553, 0.324461; inactive 0.0063–0.0124 | Good toy geometry, D44/D45 real readiness fails. D43 dispatch-before-test-inspection error retained (D42–D45) |
| Global trace replay | Pilot and oracle recordings reproduce saved trajectories exactly; all 677 core-parent kernels across two middle progress stages stall in the pilot; oracle core remains mobile | Explains this pilot failure; these are not 677 consecutive kernels of the entire run (D46) |
| Global kernel plus coordinate slices | Region weights 0.354792, 0.369979, 0.360091, 0.156349, 0.196265; inactive distances 0.008–0.011; no duplicate full vectors; ~164 s total, 1.18–1.23 million calls/run | Restores local mobility without consistent active weights (D47) |
| Known-partition allocation, rslice | 400 live per stratum, volumes 0.006/0.994; region weights 0.279282, 0.330504, 0.312926, 0.246327, 0.324765. All ten conditional log Z errors positive +0.1564 to +0.6127; combined +0.1707 to +0.5289 | Region allocation alone fails evidence checks (D48) |
| Same partition, direct rejection | Region weights 0.311119, 0.370518, 0.276170, 0.336349, 0.235514; combined log Z errors +0.104570, −0.100417, −0.002069, −0.039360, +0.053942; inactive 0.0098–0.0159 | Improved known-partition control, not real-model transfer (D49); D50 final disposition below |

## Controls that worked, and what they establish

The analytical Beta(3,1) positive control distinguishes its correct CDF from the wrong Uniform target: ten runs give correct-CDF distances 0.009–0.033 versus 0.383–0.415 for the wrong distribution; an added independent coordinate gives 0.023–0.070. This verifies that the diagnostic can recognise a nonuniform prior, not that it explores real biological cliffs.

The corrected global-Metropolis unit control gives CDF distance 0.02424 below its 0.04359 bound; omission of the proposal-density ratio gives 0.73194. The hybrid's IID stationarity control gives distances 0.01745/0.01388 and region error 0.009 against bound 0.04664. These check stationary transitions from exact starts, not finite-run mixing from biased starts. Oracle and fitted-quadratic proposals work for the analytically accessible narrow component; the corresponding unknown real geometry and region prior volumes were not supplied by P17. Known-partition rejection reduces the D48 evidence pattern without proving real bound coverage or universal correctness.

## What remains uncertain and what happens next

The relative causal contributions of missing-observation occupancy, geometry, ancestry, finite mixing and numerical-state sensitivity remain incompletely separated. No new posterior establishes fifteen individually or jointly identified biological parameters. No claim that likelihood revision alone will repair inference is supported. The registered reserved confirmation seeds remain unused under the PI closure.

The original requirements remain in `current_gate.md`; DECISIONS records the stopping-rule change and sole running batch's final disposition. `docs/RIGOUR.md` is the standing discipline, including historical exceptions. `docs/TARGET_REVISION_SPEC.md` proposes configuration-D parameter consistency, observation-model-derived infeasibility handling and a seven-axis mechanism investigation, **awaiting PI approval in a different session**. Integration and handover documents describe the next operational work; nothing is merged or pushed here. R1 remains open, R3 provisional and R4 untouched; D/E/F/M9 work remains blocked.


## D50 final batch disposition — independently audited at closure

The only batch running when the PI instruction arrived completed **200/200 target-seed cases (100 smooth and 100 spike; 400 conditional runs)** in **1,439.57 seconds (24.0 minutes)**. No reserved confirmation or new experiment followed. `audit_calibration_closure.py` independently reconstructed every saved likelihood, conditional evidence, volume-weight recombination, active/inactive CDF distance, region mass and summary; all 200 saved result hashes match. Initial/periodic checkpoint hashes and arrays are retained in `stratified_calibration/closure_audit.json`; all assertions passed.

| Target | Score envelope | Mean Z/Ztruth (approximate 99% t interval) | Inactive distance range | Max-active distance range | Region-mass range | log Z error range |
|---|---:|---|---|---|---|---|
| smooth | 2.746233 | 1.008075 (0.974121, 1.042029) | 0.007440–0.024452 | 0.014707–0.032897 | 0.480382–0.518822 | -0.277288–0.411935 |
| spike | 2.248029 | 1.003983 (0.975790, 1.032176) | 0.006052–0.021671 | 0.012897–0.103451 | 0.204959–0.406815 | -0.257381–0.337204 |

Both approximate intervals contain one; this does not prove unbiasedness. The registered maximum-score envelopes correspond, in original units, to inactive distance / active distance / region error / absolute log Z error bounds of **0.054925 / 0.137312 / 0.137312 / 0.411935** (smooth) and **0.044961 / 0.112401 / 0.112401 / 0.337204** (spike). These are conservative joint-score component envelopes, not the observed range of each metric. The maximum of 100 exchangeable calibration scores gives 100/101 pointwise coverage for one further exchangeable case; it does not provide simultaneous five-run confirmation or real-model certification. The independent 400-point IID CDF reference is retained in `iid_reference.json`; it is a scale comparison, not an IID test of nested samples. Known prior partition volumes remain supplied information unavailable on the real surface. **D50 is a retained calibration control; the original P17 correction gate remains unpassed.**
