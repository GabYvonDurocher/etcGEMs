# Claude Code prompt — feasibility scoping for a cyanobacterium (phototroph) etcGEM: the readiness gates for the low-Ea third point of the Yvon-Durocher 2014 ordering, BEFORE committing to a build (autonomous, research + light analysis only)

Run from the project root (`.../MICROADAPT/etcGEMs`). SCOPING ONLY — do NOT build the model. Mirror the
methanogen readiness approach (docs/METHANOGEN_ETCGEM_PLAN.md, the "three feasibility gates" table): decide
whether a cyanobacterium etcGEM is tractable as the LOW-Ea third point (CH4 > respiration > photosynthesis,
Yvon-Durocher 2014), and surface the ONE gate that is genuinely new and could sink it: whether our
enzyme-/temperature-constrained framework can represent a phototroph's temperature-INSENSITIVE energy input
(the light reactions) well enough that a low growth-Ea can emerge for the RIGHT mechanistic reason. Output a
readiness plan + an explicit GO / NO-GO / GO-WITH-CAVEATS recommendation. No src/etcgem changes, no strain
dir, no model runs.

NOTE TO USER: launch in an auto-approving mode. Web research (GEMs, TPC data, thermal params, photophysiology).
Produces docs/PHOTOTROPH_ETCGEM_PLAN.md. No heavy compute.

WHY THIS GATE MATTERS (state it up front in the doc): in the two-organism paper, the mechanism setting Ea is
(i) control-weighting on the enzyme backbone and (ii) the allocation buffer — both operating on kcat(T)-limited
enzymatic steps. A phototroph's low Ea may arise from a DIFFERENT route the current etcGEM does not natively
carry: photochemistry / light harvesting is close to temperature-independent, so if light capture (not a
Calvin-cycle enzyme) sets the rate, growth-Ea is low because the rate-limiting input is not kcat-limited at all.
The scoping must decide whether we can represent this (and therefore whether the phototroph tests or breaks the
framework).

---

```
Work AUTONOMOUSLY; commit at the end; print a summary + the GO/NO-GO. Read first: docs/METHANOGEN_ETCGEM_PLAN.md
(the gate structure + house style to mirror), reports/activation_energy/report.qmd (the mechanism the phototroph
must test, and the 2014 framing), src/etcgem/{providers.py, enzyme_cost.py, sectors.py, tpc.py} (to judge what
the framework CAN and CANNOT represent — esp. how growth is bounded and whether a temperature-independent energy
input can be encoded), and strains/mmaripaludis/outputs/M1_audit_and_readiness.md (the readiness-note format).
Web-research the gates below; cite every source (GEM papers, TPC papers, thermal data).

GATE 1 - Base GEM (does a well-curated cyanobacterium GEM exist, ideally with a GECKO ecModel?)
- Survey candidate organisms + GEMs: Synechocystis sp. PCC 6803 (e.g. iJN678 Nogales 2012, iSynCJ816 Joshi 2020,
  and later reconstructions), Synechococcus elongatus PCC 7942 / UTEX 2973 (fast-grower), Synechococcus sp. PCC
  7002, Prochlorococcus. Report: reactions/genes/coverage, photosynthesis + Calvin-cycle + photorespiration
  representation, light-uptake handling, whether a GECKO/enzyme-constrained version exists (or how hard sMOMENT
  would be, as we did for iMR539). Recommend a primary + fallback. Note model size (smaller is fine/helpful for
  clean Ea attribution). GREEN/AMBER/RED.

GATE 2 - Thermal parameters (Topt / Tm)
- Topt: the Li-Engqvist sequence predictor works from any proteome (portable) — confirm applicability to a
  cyanobacterial proteome. Tm: is the chosen organism in the Meltome Atlas (Jarzab 2020) or any meltome? If not,
  a mesophile Tm prior (as for the methanogen) is the fallback for a mesophilic cyanobacterium (Synechocystis
  ~30-35 C; note thermophilic options like Thermosynechococcus if a higher-Topt anchor helps). GREEN/AMBER/RED.

GATE 3 - Calibration/validation TPC (a measured growth-rate-vs-temperature curve for the chosen strain)
- Find a published growth-rate TPC (mu vs T) for the candidate organism (analogous to Jones 1983 / Van Derlinden):
  Topt, range, CTmax, and an approximate rising-limb Ea. Cyanobacterial growth TPCs exist (report specific
  papers + figures to digitise). ALSO note what rate the 2014 paper's photosynthesis Ea refers to (gross/net
  photosynthesis, O2 evolution, or carbon fixation) and whether a GROWTH TPC is the right comparison or whether
  we should target a photosynthesis-flux TPC — this choice matters for the claim. GREEN/AMBER/RED.

GATE 4 - THE DECISIVE ONE: can the etcGEM represent the light reactions / temperature-independent energy input?
- This is the new, potentially sinking gate. Determine, from the GEM structure + our framework:
  * How is phototrophic growth BOUNDED in a cyanobacterium GEM — a light/photon exchange reaction with a set
    uptake bound, feeding ATP/NADPH via the photosystems? Is that bound temperature-independent (photochemistry)
    while the Calvin-cycle + downstream enzymes ARE kcat(T)-limited?
  * If light-limited: growth-Ea would be low because the energy input is T-insensitive — a DIFFERENT mechanism
    from respiration/methanogenesis (a genuinely enriching third route, IF we can encode it: e.g. a
    temperature-independent photon-supply constraint alongside the enzyme pool). If Calvin-cycle-limited (e.g.
    RuBisCO carboxylation): growth-Ea reflects RuBisCO's kcat(T) + photorespiration T-dependence — which the
    current kcat(T) framework CAN represent, and RuBisCO is famously a low-turnover, T-sensitive enzyme (so this
    could go either way on Ea). Report which regime the literature + GEM imply under the growth conditions of the
    TPC, and therefore which mechanism sets the phototroph Ea.
  * State clearly: does representing the phototroph require a NEW model layer (a temperature-independent
    light/energy-supply constraint, photorespiration T-dependence, photoinhibition at high T)? Is that a modest
    addition (like the sector layer) or a substantial reframe? This determines the build cost + risk.
  GREEN (framework handles it) / AMBER (needs a documented new layer, tractable) / RED (needs a reframe that
  breaks the shared framework).

SYNTHESIS + RECOMMENDATION
- Fill a gates table (Gate | Status | Detail | Sources) exactly like the methanogen plan. Then give the honest
  bottom line: is a cyanobacterium the right low-Ea third point, what would the build cost (a full M1-M6-style
  cycle + any new light layer), and does it TEST the mechanism (does the framework predict low Ea for the right
  reason?) or RISK it (low Ea only reproducible via a non-enzymatic light constraint the paper's mechanism does
  not cover). Give a GO / NO-GO / GO-WITH-CAVEATS with the reasoning, and — if GO — a phased plan mirroring the
  methanogen (phase 0 data-gather + go/no-go, then base->ecModel->thermal->calibration->sector), plus whether it
  belongs in THIS paper or a follow-up. If NO-GO or GO-WITH-CAVEATS, state exactly what would need to be true
  (e.g. a specific GEM, a specific TPC, a workable light-constraint encoding) to flip it.

OUTPUT
- Write docs/PHOTOTROPH_ETCGEM_PLAN.md (mirror METHANOGEN_ETCGEM_PLAN.md: rationale, the four gates table, the
  portable-vs-new layer analysis with the light-reaction question foregrounded, the phased plan, the risks, and
  the recommendation). All sources cited. This is a decision document, not a build.

VERIFY (report all)
1. Four gates researched + statuses (Base GEM; Topt/Tm; TPC; the light-reaction/temperature-independence gate),
   each with cited sources; a candidate organism + GEM recommended.
2. Gate 4 explicitly resolves whether the phototroph's low Ea would arise from a mechanism the current framework
   represents (kcat(T)-limited Calvin cycle) or one it does not (T-independent light supply), and what new layer
   (if any) is needed.
3. docs/PHOTOTROPH_ETCGEM_PLAN.md written, mirroring the methanogen plan; explicit GO / NO-GO / GO-WITH-CAVEATS
   + phased plan (if GO) + this-paper-vs-follow-up recommendation.
4. NO model built, no strain dir, no src/etcgem changes, no runs.

CONSTRAINTS
- Scoping + research + decision doc only. Do NOT build the model or add a strain. Mirror the methanogen gate
  house style. Cite every GEM/TPC/thermal/photophysiology source.
- Autonomous; single commit: "docs: phototroph (cyanobacterium) etcGEM feasibility scoping + gates + go/no-go".
```
