# Validation protocol for the revised target — DRAFT for PI signature

_Drafted 2026-09-13 by T1. **Every threshold below is DRAFT pending signature.** Nothing here
authorises a run. `TARGET_REVISION_SPEC.md` freezes the six required checks; this document supplies
the quantitative thresholds it says a signed follow-up must supply, and names where each came from
and where that source stops applying. RIGOUR.md rules 1, 2, 5, 6, 7, 8 and 10 govern its use._

**Applies to:** the revised configuration-D NLDM target once items 1.27 (target revision), 1.25
(observation model) and any approved curvature correction are decided — and to nothing else. Every
statistic is computed from saved arrays by an independent audit script (RIGOUR 7) before any
interpretation.

## Calibration sources, and their limits — read before any threshold

| source | what it measured | what it can calibrate | what it cannot |
|---|---|---|---|
| **P17 D25** (`DECISIONS.md:624–627`) | Beta(3,1) positive control, 10 runs: correct-CDF KS **0.0090–0.0330**; wrong-Uniform **0.3826–0.4153**; an added inert coordinate **0.0232–0.0703** | the *separation* between a recovered and a wrong inactive prior on the toy | any real-path recovery; the toy is analytically accessible |
| **P17 D47** (`:1288`) | corrected global-Metropolis unit control: KS **0.01745 / 0.01388**, region error **0.009** against its bound **0.04664** | a stationary-kernel unit check from exact starts | finite-run mixing from biased starts |
| **P17 D40** (`:1112–1113`) | oracle geometry: region weights 0.3107–0.3279 around the exact **0.3043739263**, i.e. max region error **≈ 0.0235**; log Z errors **−0.3139 … +0.3084** "material relative to nominal 0.127–0.135" | region-mass recovery **to within ~0.02** when the geometry is *supplied* | evidence error — its own range is **not** a calibration (see below); oracle geometry is unavailable on the real surface |
| **P17 D25** evidence column (`:627`) | log Z errors **+0.0689 … +0.4065, positive in all 10** | **nothing** — a one-signed bias range is evidence of a defect, not an envelope | it must NOT be read as "±0.4 is fine" |
| **P17 D50** (report, closure table) | 200/200 known-target cases; envelopes in original units — smooth **0.054925 / 0.137312 / 0.137312 / 0.411935**, spike **0.044961 / 0.112401 / 0.112401 / 0.337204** (inactive distance / active distance / region error / |log Z error|) | conservative joint-score envelopes on **known** targets with **supplied** partition volumes; 100/101 pointwise coverage for one further exchangeable case | simultaneous coverage of five runs; the real model, whose partition volumes are unknown |

The single most important limit: **every source above is a toy or a supplied-geometry control.**
A threshold calibrated on them is a *necessary* bar the real target must clear, never a sufficient
one (RIGOUR 5).

## The six required checks

### (a) Inactive-coordinate CDF recovery against its exact independent prior — DRAFT

- **Statistic:** the importance-weighted CDF mean and the weighted CDF distance of the dedicated
  diagnostic coordinate (appended with `diagnostic_coords`, `pert=None`, prior declared in the run
  manifest), computed by `reports/P17_inactive_prior/null_check.py` from saved `samples`/`logwt`
  against their recorded SHA-256, exactly as the HANDOVER's standing commands do.
- **Threshold (DRAFT):** weighted CDF distance **≤ 0.05** *and* |CDF mean − 0.5| **≤ 0.05**, on
  **each** of the independent runs in (c).
- **Calibration:** D25's correct-CDF range 0.0090–0.0330 and inert-coordinate range 0.0232–0.0703
  put a recovered prior below ~0.07 and a wrong one above 0.38; 0.05 sits inside the recovered band
  with margin against the 0.0703 upper edge of the added-coordinate case. **Limit:** toy-derived;
  P16's real failure was 0.2909 / 0.2161, far outside, so this bar discriminates that failure but
  cannot certify anything finer than the toy resolves.
- **Reserved seeds:** **17901–17905** (P17's reserved set, still unconsumed) — one per run of (c),
  registered in the run manifest before launch and never used for development.
- **Budget / alarm:** the audit script only reads arrays; 10 min under SIGALRM.
- **If it fails:** stop, retain, report the run as **NOT RECOVERED** with the numbers; do not tune
  and rerun on the same seeds.

### (b) Appended Beta(3,1) recovery judged on b³, with the wrong-Uniform contrast — DRAFT

- **Statistic:** on an appended coordinate with prior Beta(3,1), the weighted CDF distance of **b³**
  (which is Uniform(0,1) under the correct prior) — and, as the positive contrast, the same distance
  computed against the **wrong** Uniform(0,1) CDF of b.
- **Threshold (DRAFT):** correct-CDF distance **≤ 0.05**; wrong-CDF distance **≥ 0.30**; both must
  hold. The contrast is what shows the instrument can *see* a non-uniform prior.
- **Calibration:** D25 exactly — 0.0090–0.0330 correct against 0.3826–0.4153 wrong. **Limit:** on
  the real path P17 D38's Beta chains gave 0.42–0.63 *correct* distances from short correlated
  chains, so a pass here on a nested run is not a certificate that a short-chain follow-up would
  pass; and the toy tells nothing about real cliffs.
- **Seeds / budget / failure:** as (a).

### (c) Consistency of all active distributions and covariance directions across independent initialisations — DRAFT

- **Statistic:** **five** independent runs on the reserved seeds. For every active parameter, the
  weighted median and 5/95 interval; for the posterior covariance **in the unit cube**, the
  eigendecomposition (P16 D4's convention, prior sd 1/√12 along any direction). Agreement measured
  as: (i) every median within **2 bootstrap Monte-Carlo errors** across all pairs (P11's rule,
  unchanged); (ii) the leading three eigenvectors' pairwise |cos| **≥ 0.9** across runs; (iii) the
  posterior/prior width ratio of every direction agreeing within **0.1** across runs.
- **Threshold (DRAFT):** all three, on all five runs.
- **Calibration:** (i) is the historical rule and is retained unchanged (RIGOUR 2); (ii) and (iii)
  have **no P17 calibration source** — they are proposed from P16 D5's finding that live-point
  correlations reversed sign between a crashed run and its posterior, so direction agreement is
  the property that failure lacked. **Limit:** un-calibrated; the PI may tighten or reject; five
  runs cost ~5 × 10 h at P16's measured rate.
- **Failure:** DISAGREED, with the same table P11 produced, retained; no averaging across runs.

### (d) Preregistered region occupancy with ancestry-aware uncertainty — DRAFT

- **Regions:** defined **before** launch in the manifest, in the unit cube, by rule and not by
  looking at any posterior: at minimum the *living* region (peak predicted growth ≥ 50 % of the
  measured 2.0761 /h, the P12/P13 criterion) and its complement.
- **Statistic:** each run's importance-weighted region mass, with an uncertainty from the
  **number of distinct ancestral roots** feeding the region's final live points (P17's
  ancestry count, D13–D38) rather than from weight ESS.
- **Threshold (DRAFT):** region masses agreeing across the five runs to within **0.05**, *and* no
  region with fewer than **20** distinct roots.
- **Calibration:** D40/D47 recover a known region mass to within ~0.02 with supplied geometry;
  0.05 allows for the real surface having none. The 20-root floor comes from P17's traces, where
  29–32 initial roots accompanied restricted movement and 634–800 complementary slots — i.e. below
  ~30 roots the mass estimate was visibly ancestry-limited. **Limit:** both numbers are borrowed
  from toys and traces, not derived for this target.

### (e) Feasibility-aware posterior predictive checks at every observed temperature, including the unresolved-evaluation rate — DRAFT

- **Statistic:** at every one of the 12 measured temperatures, the posterior-predictive
  distribution of growth and of the scored respiration observable over ≥ 500 weighted draws, each
  evaluated **fresh** under the registered retry ladder (T1 D0); the fraction of draws whose solve
  is **UNRESOLVED** after the ladder; and the fraction whose respiration prediction is missing.
- **Threshold (DRAFT):** unresolved-evaluation rate **≤ 1 %** of draw-temperatures; every measured
  value inside the predictive 2.5–97.5 % interval at **≥ 10 of 12** temperatures; and, under the
  approved observation model, **no positive measurement unscored** (the property T1 TASK 2's table
  demonstrates the current code lacks).
- **Calibration:** **none exists** — P17 ran no feasibility-aware predictive check. The 1 % and
  10/12 are proposed as the loosest bars that would still have caught P16's half-dead posterior
  (median predictive peak growth 0.0016 /h against 2.0761). **Limit:** un-calibrated; DRAFT in the
  strongest sense.

### (f) Evidence and final-live-point reconstruction with independent hash audits — DRAFT

- **Statistic:** an independent script (not the producer's helpers) reconstructs log Z, the
  importance weights, the final 800 live points and the prior transform from the checkpoint and
  the saved arrays, and checks every source, input and output SHA-256 against the run manifest.
- **Threshold (DRAFT):** reconstructed log Z within **1e-9** of reported; weights normalising to
  one within **1e-12**; inverse-prior cube error **≤ 1e-14**; **every** hash matching; the five
  runs' log Z agreeing within their **combined reported error** (P11's rule, unchanged).
- **Calibration:** P17's independent audit achieved 1.7e-15 cube error and <1.5e-13 weight
  normalisation on P16's arrays; the tolerances above are ten-fold looser. The log Z agreement rule
  is historical. **Limit:** agreement in log Z is explicitly **insufficient** (RIGOUR 5; P17 D26
  and D40 show it coexisting with wrong active weights and material evidence error), so (f) passing
  certifies reproduction of the arithmetic, not correctness of the posterior.

## Deliberately NOT thresholds

- **No living-fraction target.** The 80–87 % fractions belong to specified analytical toys.
- **No IID KS p-values on nested samples.** Nested samples are dependent; distances are descriptive.
- **Weight ESS is not independent N**, and is not used as a sample count anywhere above.
- **No evidence-error envelope.** D25's +0.07…+0.41 is a one-signed bias, not a calibration.

## Budget, alarm, stopping

Five runs at nlive 800, `rslice`, sequential, each under a **16 h** SIGALRM-enforced cap with
30-minute checkpoints (P16's measured 8.0–9.6 h each ⇒ ~45–50 h wall). **One job at a time.** A run
that hits its cap is STALLED, retained, and stops the programme; it is not restarted without a new
registration. All six checks are computed by audit scripts only after every run's hashes are
verified. **Any single failed check is a NOT PASSED for the programme**; the blocker is recorded
(RIGOUR 10) and nothing is averaged, tuned or re-seeded to reach a pass.

_For signature: ______________________ (PI)   date: ____________ — until signed, no revised run._
