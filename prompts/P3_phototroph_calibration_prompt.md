# Claude Code prompt — P3 (phototroph build): Bayesian calibration of the Synechocystis 6803 etcGEM to the Zavrel 2015 light-saturated growth TPC (shape-first: bring the rising-limb SS-E down honestly), reusing the E. coli/methanogen emcee machinery (autonomous)

Run from the project root (`.../MICROADAPT/etcGEMs`). Calibrates the P2 thermal ecModel to the digitised Zavrel
2015 growth TPC, reusing src/etcgem/calibration.py (emcee, provenance priors, discrepancy likelihood) — the same
additive-inverse approach as the E. coli and methanogen calibrations. SS-E (Sharpe-Schoolfield) throughout. Keep
the GROUNDED single-pool structure with the growth-law/allocation coupling OFF (the cyanobacterial allocation
layer is the NEXT step, P3b — the analog of the methanogen M6; the allocation contribution to Ea is a P4 finding,
not something baked in here). NO Ea dissection (P4).

NOTE TO USER: launch in an auto-approving mode, from the venv with Gurobi + emcee. Multi-hour run.

CONTEXT (P2): the emergent light-saturated model matches SHAPE and MAGNITUDE a-priori — Topt 36.0 C (Zavrel ~35),
CTmax 45.7 C (Zavrel ~44), rmax 0.067/h (Zavrel ~0.05-0.09). The one clear residual is the RISING-LIMB Ea: emergent
SS-E 0.771 eV vs Zavrel ~0.42 eV (~1.8x too steep). Photon shadow price = 0 at every temperature (light saturation /
in-mechanism holds thermally). So unlike the methanogen (which needed MAGNITUDE-first because mu~=0), the phototroph
needs SHAPE-first: magnitude is already realistic, and the job is to bring the rising-limb SS-E DOWN honestly and to
identify WHICH knob does it — the diagnostic that sets up P4 (is the low Ea genuinely shallow Calvin kcat(T), or does
it need the allocation buffer?). Target: the digitised Zavrel 2015 growth TPC in thermal/ (light-saturated, Topt ~35).
Cross-check curves also in thermal/: Inoue Fig 1 (light-LIMITED growth, broad range) + Inoue Fig 2A (light-saturated
photosynthesis flux) + Inoue Fig 6 (PSII denaturation) — for validation/overlays, NOT fit targets.

---

```
Work AUTONOMOUSLY end to end; commit in parts; print a summary. Read first: src/etcgem/{calibration.py (emcee,
PARAM_NAMES, priors, log_likelihood_sd, trusted-curve loader, warm-start/early-stop/solver guards), enzyme_cost.py,
providers.py (the route-B from_gecko phototroph path + set_temperature/NGAM(T)), sectors.py, tpc.py,
sharpe_schoolfield.py, validation.py}, strains/syn6803/{strain.yaml, thermal/ (the digitised Zavrel 2015 growth TPC
CSV + the Inoue cross-check CSVs), outputs/P2_thermal.md}, strains/mmaripaludis/outputs/{M4_calibration.md} (the
calibration precedent to mirror), and docs/PHOTOTROPH_ETCGEM_PLAN.md. Gurobi with a GLPK-abort guard + one-solve
pre-flight (STOP if not Gurobi unless ALLOW_GLPK); autocorr early-stop; warm-start — as in the other calibrations.

PART A - load the Zavrel curve + confirm the operating point
- Load the digitised Zavrel 2015 growth TPC via the trusted-curve loader; fit on RAW ABSOLUTE growth rate (1/h).
  Confirm the model is the P2 thermal ecModel under the LIGHT-SATURATED autotrophic medium (photon bound non-limiting;
  re-confirm the photon shadow price stays 0 across the fitted range so calibration stays in-mechanism), with NGAM(T)
  on and the growth-law/allocation coupling OFF (single sMOMENT pool).
- Also fit/record the OBSERVED SS-E of the Zavrel cloud WITH its uncertainty (the rising-limb coverage is thinnish —
  report the SS-E CI so we know how tightly 0.42 is actually pinned; this bounds how hard P3 should push).

PART B - free-parameter set + SHAPE-FIRST + provenance priors
- Free the unified set (the E. coli/methanogen analogue): magnitude {kcat_scale, sigma} + envelope/stability
  {dTopt, topt_scale, dCp_scale, dTm, tm_scale} + pool {f_metab, f_maint} + maintenance {ngam_scale, ngam_steepness}
  + sigma_disc. Hold P_total fixed.
- SHAPE-FIRST (the opposite of the methanogen): magnitude is already realistic, so keep it near-1 and let the
  ENVELOPE knobs do the work of lowering the rising-limb SS-E 0.77 -> ~0.42:
  * kcat_scale: LogNormal centred on 1 (NOT the Davidi 4x — the ecModel ships real kcats and rmax is already right).
    This doubles as the "borrowed ecModel pool budget" check flagged in P1: report whether the data demand any pool
    magnitude move. sigma bounded (0,1), prior ~0.45.
  * dCp_scale: BROAD LogNormal about 1 — this is the PRIME Ea lever (flatter MMRT curvature -> shallower rising-limb
    Ea). Report how far it must move and whether the DEMANDED per-enzyme curvature is plausible (vs the -4 kJ/mol/K
    prior): a modest shallowing is "genuinely shallow Calvin kcat(T)"; an implausibly flat dCp means the envelope
    ALONE cannot explain the low Ea and it likely needs the allocation buffer (-> motivates P3b). This judgement is
    the key P3 diagnostic; do NOT just tune to hit 0.42 and move on.
  * dTopt ~N(0, ~4 K) (Topt 36 -> ~35, tiny); topt_scale (per-enzyme Topt spread -> heterogeneity flattening, a
    legitimate aggregation route to lower SS-E — report if it moves); dTm ~N(0, ~4 K) (CTmax 45.7 vs ~44, small;
    we hold Inoue Fig 6 PSII denaturation in reserve to sanity-check Tm later).
  * f_metab/f_maint: moderate priors (single-pool partition); NOTE these become real allocation levers only when the
    P3b sector layer is added. ngam_scale/ngam_steepness LogNormal about 1 (Touloupakis 2015 anchored). sigma_disc
    HalfNormal (use the Zavrel replicate scatter as obs_sd if present).

PART C - fit (emcee) on raw absolute rates
- emcee, gradient-free, parallel, warm-started at the posterior mode (short optimiser first), autocorr early-stop at
  n_eff>=400. Fit the Zavrel curve (absolute 1/h) with the Gaussian discrepancy likelihood. Report solver, acceptance,
  n_eff, stopping reason, wall-time.

PART D - outputs (calibration only; NO Ea dissection) + honest diagnostic + cross-checks
- Save strains/syn6803/outputs/calibration_zavrel/: chain + summary.json (per-param posterior median/90% CI,
  convergence, medium=light-saturated autotrophy), the PRIOR-vs-POSTERIOR TPC on raw absolute rate (emergent +
  posterior band + Zavrel points, 5-50 C), demanded_corrections.csv (prior vs posterior + interpretable correction),
  and the corner plot.
- HEADLINE for the summary:
  * Does the posterior reach Zavrel (rmax, Topt ~35, CTmax ~44) and — the crux — does the calibrated rising-limb SS-E
    reach ~0.42 (within the observed SS-E CI from PART A)?
  * WHICH knob lowers the Ea, and is it plausible? Foreground the dCp_scale (and topt_scale) verdict: modest/plausible
    shallowing -> the low phototroph Ea is genuinely shallow Calvin-cycle kcat(T) (an in-mechanism, enzyme-kinetic
    result); implausibly flat -> the envelope cannot do it alone and the allocation buffer (P3b) is likely needed.
    State this explicitly as the P4 setup.
  * Secondary (light-saturated FLUX cross-check for the 2014 comparison): report the calibrated CARBON-FIXATION-flux
    SS-E and compare to the Inoue Fig 2A photosynthesis-flux Ea (~0.5 eV, light-saturated) — an INDEPENDENT curve the
    model was not fit to.
  * Validation overlays (not fit targets): the calibrated growth TPC over Inoue Fig 1 (light-LIMITED; expect the model
    to sit steeper/higher on the rising limb — illustrating the light-limitation gap, the Discussion point) and the
    calibrated flux TPC over Inoue Fig 2A (light-saturated; should track).
- Keep emergent vs calibrated distinct; nothing relabelled as prediction.

VERIFY (report all)
0. solver=gurobi (pre-flight passed). Fit under the light-saturated medium (photon shadow price 0 across the range),
   NGAM(T) on, growth-law/allocation OFF (single pool).
1. Unified free set + SHAPE-FIRST (magnitude near-1; envelope knobs lower the Ea); provenance priors as above;
   P_total fixed. Observed Zavrel SS-E + its CI reported.
2. Posterior reaches (or how close to) Zavrel rmax/Topt/CTmax; calibrated rising-limb SS-E vs the observed ~0.42
   (within CI?); convergence (n_eff>=400).
3. Ea-lever DIAGNOSTIC: which knob lowers the SS-E, whether the demanded dCp/topt_scale is plausible, and the explicit
   verdict (shallow-Calvin-kinetics vs needs-allocation) as the P4/P3b setup.
4. Secondary flux SS-E vs Inoue Fig 2A (~0.5) reported; Inoue Fig 1 + Fig 2A overlays saved as validation cross-checks;
   calibration_zavrel outputs written; emergent vs calibrated distinct; GO/NO-GO for P3b (cyanobacterial allocation
   layer) then P4 (Ea dissection + three-way comparison).

CONSTRAINTS
- Additive inverse calibration only; reuse calibration.py (emcee, not ABC/Stan); exact likelihood. SS-E throughout.
- Grounded single-pool structure; growth-law/allocation OFF (the cyanobacterial allocation layer is P3b, and its Ea
  contribution is a P4 finding — do NOT bake it in here). NGAM(T) amplitude stays anchored on Touloupakis 2015
  (ngam_scale near 1 unless data demand). Do NOT force the Ea down by an implausible curvature just to hit 0.42 —
  the honest diagnostic (which knob, is it plausible) is the deliverable.
- Fit RAW ABSOLUTE rates; single Zavrel curve; Inoue curves are cross-checks only. Keep emergent vs calibrated distinct.
- Autonomous; commit in parts: "phototroph P3: calibration setup (unified params + shape-first envelope priors; magnitude near-1)",
  "phototroph P3: emcee fit to Zavrel 2015 (light-saturated growth)",
  "phototroph P3: calibration_zavrel outputs (prior-vs-posterior TPC, corrections, corner) + Inoue cross-checks + P3 note".
```
