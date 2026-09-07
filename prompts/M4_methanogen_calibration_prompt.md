# Claude Code prompt — M4 (methanogen build): Bayesian calibration of the M. maripaludis etcGEM to the Jones 1983 TPC (magnitude-first, then shape), reusing the E. coli emcee machinery (autonomous)

Run from the project root (`.../MICROADAPT/etcGEMs`). Calibrates the M3 thermal ecModel to the
digitised Jones 1983 growth TPC, reusing src/etcgem/calibration.py (emcee, provenance priors,
discrepancy likelihood) — the same additive-inverse approach as the E. coli P2. NO Ea dissection (M5).
Keep the GROUNDED single-pool structure (NO forced Scott growth law — the slow methanogen uses a
different allocation; the allocation comparison is an M5 finding).

NOTE TO USER: launch in an auto-approving mode, from the venv with Gurobi + emcee. Multi-hour run.

CONTEXT (M3): emergent shape is right (CTmax 46.8 matches Jones ~47-48; single-peaked; correct range)
but (a) a-priori mu ~= 0 because grounded kcats + MEASURED maintenance (Goyal 2015 NGAM 7.836
mmol ATP/gDW/h) leave no energy for growth — so MAGNITUDE must be calibrated FIRST so growth clears
maintenance; (b) Topt +5 C warm, rising-limb Ea 1.72 eV too steep (Topt is a mesophile prior; dCp
generic). Mcr kcat 58.9/s, uncertainty 3-294/s (carry to M5). Target: the digitised Jones 1983 Fig 2
TPC (type strain JJ, H2/CO2, peak ~0.181/h at ~37-38 C, range 18-47 C).

---

```
Work AUTONOMOUSLY end to end; commit in parts; print a summary. Read first: src/etcgem/{calibration.py
(emcee, PARAM_NAMES, priors, log_likelihood_sd, trusted-curve loader, warm-start/early-stop/solver
guards), enzyme_cost.py, providers.py (from_gem_smoment + set_temperature/NGAM(T)), sectors.py, tpc.py,
validation.py}, strains/mmaripaludis/{strain.yaml, thermal/ (the digitised Jones 1983 TPC CSV),
outputs/{M2b_kcat_refinement.md, M3_thermal.md}}, and docs/METHANOGEN_ETCGEM_PLAN.md. Gurobi with a
GLPK-abort guard + one-solve pre-flight (STOP if not Gurobi unless ALLOW_GLPK); autocorr early-stop;
warm-start — as in the E. coli P2.

PART A - load the Jones curve + confirm the operating point
- Load the digitised Jones 1983 TPC (H2/CO2 defined medium) via the trusted-curve loader; fit on RAW
  ABSOLUTE growth rate (1/h). Confirm the model is the M3 thermal ecModel at the H2/CO2 operating point
  with NGAM(T) on and the growth-law/allocation coupling OFF (single sMOMENT pool).

PART B - free-parameter set + MAGNITUDE-FIRST + provenance priors
- Free the unified set (the E. coli analogue): magnitude {kcat_scale, sigma} + envelope/stability
  {dTopt, topt_scale, dCp_scale, dTm, tm_scale} + allocation/pool {f_metab (the metabolic mass
  fraction of the pool), f_maint} + maintenance {ngam_scale, ngam_steepness} + sigma_disc. Hold
  P_total fixed.
- MAGNITUDE-FIRST: because a-priori mu ~= 0, the chain MUST start where the model grows. Give kcat_scale
  a LogNormal prior centred on the Davidi in-vitro->in-vivo ~4x (broad; it also absorbs the residual
  archaeal-kcat underprediction), and INITIALISE the walkers where growth clears maintenance
  (kcat_scale ~4, sigma ~0.45). Ensure the likelihood is finite/non-degenerate there (guard the
  zero-growth region). sigma bounded (0,1), prior ~0.45.
- PROVENANCE priors: f_metab TIGHT on the measured Xia proteome enzyme-mass fraction (measurement
  wiggle only); dCp_scale broad (to correct the too-steep a-priori Ea 1.72); dTopt ~N(0, ~5 K) (to pull
  Topt 42 -> ~38); dTm ~N(0, ~4 K) (CTmax already ~right, small); ngam_scale/ngam_steepness LogNormal
  about 1 (the Goyal 2015 amplitude is measured, so keep ngam_scale near 1 unless the data demand
  otherwise); sigma_disc HalfNormal (no measured SD on the Jones curve).

PART C - fit (emcee) on raw absolute rates
- emcee, gradient-free, parallel, warm-started at the posterior mode (short optimiser first), autocorr
  early-stop at n_eff>=400. Fit the Jones curve (absolute 1/h) with the Gaussian discrepancy likelihood.
  Report solver, acceptance, n_eff, stopping reason, wall-time.

PART D - outputs (calibration only; NO Ea dissection)
- Save strains/mmaripaludis/outputs/calibration_jones/: chain + summary.json (per-param posterior
  median/90% CI, convergence, medium=H2/CO2), the PRIOR-vs-POSTERIOR TPC on raw absolute rate (emergent
  + posterior band + Jones points, 5-50 C), demanded_corrections.csv (prior vs posterior + interpretable
  correction), and the corner plot.
- HEADLINE for the summary: does the posterior reach the Jones peak (~0.18/h)? What kcat_scale + sigma
  are demanded (is the magnitude correction a plausible few-fold in-vivo/in-vitro gap + the archaeal-
  kcat residual, or implausibly large)? The CALIBRATED descriptors — Topt (should land ~38), CTmax
  (~47), and especially the rising-limb Ea (does the steep a-priori 1.72 calibrate DOWN, and where does
  it land relative to E. coli's ~0.9?). Note that the calibrated Ea is the number the eventual E. coli
  comparison hinges on, and carry the Mcr 3-294/s sensitivity as a caveat.
- Keep emergent vs calibrated distinct; nothing relabelled as prediction.

VERIFY (report all)
0. solver=gurobi (pre-flight passed). Fit at H2/CO2, NGAM(T) on, growth-law OFF (single pool).
1. Unified free set + magnitude-first init (walkers start where growth clears maintenance; kcat_scale
   Davidi prior); provenance priors as above; P_total fixed.
2. Posterior reaches (or how close to) the Jones peak; demanded kcat_scale + sigma reported and judged
   plausible/implausible; f_metab stayed near the Xia value; convergence (n_eff>=400).
3. Calibrated descriptors: Topt ~38, CTmax ~47, and the calibrated rising-limb Ea (vs the a-priori 1.72
   and vs E. coli's ~0.9); prior-vs-posterior TPC + corner saved.
4. calibration_jones outputs written; emergent vs calibrated distinct; Mcr-sensitivity caveat carried;
   GO/NO-GO for M5 (Ea dissection + E. coli comparison).

CONSTRAINTS
- Additive inverse calibration only; reuse calibration.py (emcee, not ABC/Stan); exact likelihood.
- Grounded single-pool structure; NO forced Scott growth law (allocation comparison is M5). NGAM(T)
  amplitude stays anchored on Goyal 2015 (ngam_scale near 1 unless data demand).
- Fit RAW ABSOLUTE rates; single Jones curve. Keep emergent vs calibrated distinct.
- Autonomous; commit in parts: "methanogen M4: magnitude-first calibration setup (unified params + Davidi kcat prior + Xia f_metab)",
  "methanogen M4: emcee fit to Jones 1983 (H2/CO2)",
  "methanogen M4: calibration_jones outputs (prior-vs-posterior TPC, corrections, corner) + M4 note".
```
