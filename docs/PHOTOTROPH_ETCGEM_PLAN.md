# Phototroph (cyanobacterium) etc-GEM — feasibility scoping and go/no-go

**Scope.** A decision document, not a build. It asks whether a cyanobacterium etc-GEM is
tractable as the **low-Ea third point** of the Yvon-Durocher et al. 2014 ordering (methanogenesis
> respiration > photosynthesis) and surfaces the one gate that is genuinely new and could sink it:
whether our enzyme- and temperature-constrained framework can represent a phototroph's
temperature-*insensitive* energy input (the light reactions) well enough that a low growth-Ea
emerges for the **right mechanistic reason**. Mirrors `docs/METHANOGEN_ETCGEM_PLAN.md`. No model
built, no strain directory, no `src/etcgem` changes.

## 1. Why this matters, and the gate that could sink it

The two-organism paper (`reports/activation_energy/`) explains the higher thermal sensitivity of
methanogenesis versus respiration by two mechanisms, **both operating on kcat(T)-limited enzymatic
steps**: (i) growth control concentrating on a high-$E_a$ enzyme backbone, and (ii) the
proteome-allocation buffer. A phototroph is the natural third test because its thermal sensitivity
is *lower* than respiration's — but its low $E_a$ may arise from a **different route the framework
does not natively carry**. Photochemistry and light harvesting are close to temperature-independent;
if **light capture** (not a Calvin-cycle enzyme) sets the rate, then growth-$E_a$ is low because the
rate-limiting input is not kcat-limited at all. Whether we can represent this decides whether the
phototroph **tests** the framework (predicts low $E_a$ for a reason the framework carries) or
**breaks/extends** it (low $E_a$ only via a non-enzymatic light constraint the paper's mechanism does
not cover). This is Gate 4, and it is the crux.

## 2. The four feasibility gates

| Gate | Status | Detail | Sources |
|---|---|---|---|
| **1. Base GEM (+ ecModel)** | **GREEN** | Well-curated GEMs exist for *Synechocystis* sp. PCC 6803: iJN678 (Nogales 2012) and the updated **iSynCJ816** (816 genes, 1045 reactions; Joshi et al.). An **enzyme-constrained** cyanobacterial model already exists ("Upgrading a cyanobacterial GEM by inclusion of enzymatic constraints", 2024), and GECKO 2.0 provides a route from any GEM; sMOMENT (as built here for iMR539) is the fallback. Model size (~1000 reactions) is comparable to iMR539 — small enough for clean $E_a$ attribution. *Synechococcus elongatus* PCC 7942 / UTEX 2973 (fast grower) and PCC 7002 are alternatives if a faster grower or a specific TPC is preferred. | Nogales 2012; Joshi et al. (iSynCJ816); enzyme-constrained cyanobacterial GEM (Sci. rep./ScienceDirect 2024); GECKO 2.0 (Chen 2022) |
| **2. Topt / Tm** | **AMBER** | **Topt**: the Li–Engqvist sequence predictor is proteome-portable and applies to a cyanobacterial proteome — same status as E. coli/methanogen. **Tm**: the Meltome Atlas (Jarzab 2020, 13 species archaea→human) does **not** include a cyanobacterium, so — exactly as for the methanogen — Tm is a **mesophile prior** for a mesophilic strain (*Synechocystis* Topt ~30–35 °C). A thermophilic anchor (*Thermosynechococcus*) exists if a higher-Topt reference helps. Precedent (methanogen) makes this tractable, not a blocker. | Jarzab 2020 (Nat. Methods 17:495); Li–Engqvist 2019 |
| **3. Calibration/validation TPC** | **AMBER** | Cyanobacterial growth TPCs are published: marine *Synechococcus* thermal ecotypes give Topt ~25–33 °C with digitisable µ-vs-T curves; hot-spring *Synechococcus* extend the range. **Caveat that matters for the claim**: the 2014 photosynthesis $E_a$ refers to a **photosynthesis flux** (gross production / O₂ evolution / C-fixation), *not* growth. For a hydrogenotroph growth ≈ CH₄ so a growth TPC sufficed; for a phototroph, growth-$E_a$ and photosynthesis-$E_a$ can differ, so we must decide whether to target a **growth TPC** (what the framework predicts) or a **photosynthesis-flux TPC** (what 2014 measured) — and ideally use a strain with both. | *Synechococcus* thermal ecotypes (bioRxiv 2020; PMC5029218); marine *Synechococcus* warming (PMC12976987); Yvon-Durocher 2014 |
| **4. Light reactions / T-independent energy input (DECISIVE)** | **AMBER** | The framework **can** represent both regimes, but which one sets $E_a$ — and whether it is the framework's mechanism — depends on the light regime (see §3). Not RED (no reframe that breaks the shared framework), not GREEN (needs a documented new light-supply layer + a target-rate decision). | Farquhar/von Caemmerer Vcmax/Jmax T-dependence; RuBisCO/electron-transport co-limitation (PMC10192301); carboxysome CO₂-concentrating (bioRxiv 2020) |

## 3. Gate 4 in depth — can we represent the temperature-independent energy input?

**How phototrophic growth is bounded in a cyanobacterium GEM.** Light enters as a **photon
exchange reaction** with an uptake bound; the photosystems convert photons to ATP/NADPH, which
drive the Calvin cycle (RuBisCO carboxylation) and downstream biosynthesis. In our framework the
photon exchange is a **medium-availability constraint** (an exchange bound set as *availability*,
never pinned — exactly how H₂/CO₂ availability is handled for the methanogen), while the Calvin-cycle
and biosynthetic enzymes sit in the **kcat(T)-limited enzyme pool**. So the framework already carries
the two ingredients: a temperature-independent energy-supply bound *and* a temperature-dependent
enzyme budget.

**Which one limits — and therefore which mechanism sets $E_a$ — depends on the light regime.**
The Farquhar–von Caemmerer picture (and its cyanobacterial analogue) says photosynthesis is limited
by RuBisCO carboxylation ($V_\text{cmax}$) at high light / low CO₂ and by electron transport
($J_\text{max}$) at high CO₂, with *different* temperature dependencies. Cyanobacteria concentrate
CO₂ around RuBisCO in carboxysomes, favouring carboxylation and suppressing photorespiration.

- **Light-limited regime (sub-saturating light).** The rate tracks the photon supply, which is
  temperature-independent (photochemistry), so growth-$E_a$ is **low** — but this is a **different
  mechanism** from the paper's control-weighting/allocation story. It is representable (a fixed,
  T-independent photon exchange bound that binds instead of the enzyme pool), but then the enzyme
  pool is *not* the binding constraint, so the etc-GEM's kcat(T) machinery does not set the rate.
  The phototroph would then demonstrate a **third, genuinely distinct route to a thermal sensitivity**
  (a T-insensitive energy input) — enriching, but an *extension* of the framework, not a test of the
  same mechanism.
- **Calvin/RuBisCO-limited regime (saturating light).** The rate tracks RuBisCO's carboxylation
  capacity, which **is** kcat(T)-limited — the framework represents this natively. But RuBisCO
  carboxylation is not an especially low-$E_a$ enzyme (its $E_a$ is moderate, ~0.5–0.7 eV, and rises
  with photorespiration T-dependence), so in this regime the framework would predict a **moderate**
  growth-$E_a$, not necessarily the low value 2014 reports for photosynthesis.

**The honest resolution.** The framework does **not** break (Gate 4 is not RED): a T-independent
photon-supply constraint is a native medium exchange, and the Calvin cycle is native kcat(T). But a
low growth-$E_a$ "for the right reason" is *not* guaranteed to emerge from the enzyme mechanism — it
most plausibly emerges from the **light-supply** route, which is a new, documented layer (modest, on
the scale of the sector layer) rather than the paper's control-weighting/allocation mechanism.
Representing the phototroph faithfully therefore needs: (a) a **temperature-independent
light/energy-supply constraint** (small — a photon exchange bound, natively supported); optionally
(b) **photorespiration T-dependence** (a T-dependent RuBisCO carboxylase/oxygenase branching ratio —
a kcat(T)-like refinement) and (c) **photoinhibition at high T** (a falling-limb term). (a) is a
modest addition; (b)/(c) are optional refinements, not a reframe.

## 4. Does it test the mechanism, or risk it?

- It **tests** the framework *if* the growth TPC is measured under Calvin/RuBisCO-limited (saturating
  light) conditions and the framework then predicts the observed (moderate-to-low) $E_a$ via RuBisCO
  kcat(T) + photorespiration — a clean, in-mechanism prediction.
- It **extends** the framework *if* the low $E_a$ is a light-limited (T-independent supply) phenomenon
  — a valuable *third mechanism* (energy-supply-set thermal sensitivity) but not the paper's
  control-weighting/allocation mechanism.
- It would only **break** the framework if a low $E_a$ could be reproduced *neither* by RuBisCO
  kcat(T) *nor* by a documentable light-supply constraint — which the physiology does not suggest.

So the phototroph is scientifically the **most interesting** of the three (it can distinguish
"enzyme-set" from "energy-supply-set" thermal sensitivity), but it is also the one that most likely
requires a **new (if modest) model layer** and a careful **rate-target decision**.

## 5. Recommendation — GO WITH CAVEATS, as a follow-up

**GO WITH CAVEATS**, as a **separate follow-up study**, not part of the current two-organism paper
(which already frames the cyanobacterium as future work). Reasoning: all three technical gates
(base GEM, thermal params, TPC) are GREEN/AMBER with clear precedents from the methanogen build; the
decisive Gate 4 is AMBER, not RED — the framework can represent the light input — but a faithful
phototroph needs a **new light/energy-supply layer** and a **resolution of the growth- vs
photosynthesis-$E_a$ target**, both of which are real work and real interpretive risk. Bundling that
into the current paper would dilute a clean two-organism result; done properly as its own cycle it
becomes a strong third paper that either confirms the mechanism (Calvin-limited) or adds a genuinely
new one (light-supply-limited).

**What would flip Gate 4 to GREEN (do these in phase 0):** (1) confirm, from the chosen strain's TPC
conditions, whether growth was **light-saturated** (→ Calvin/RuBisCO-limited → in-mechanism test) or
**light-limited** (→ energy-supply route → new layer); (2) settle the **target rate** (growth TPC vs
photosynthesis-flux TPC) to match the 2014 comparison; (3) confirm the photon-exchange encoding of a
T-independent supply behaves as intended in a small pilot (the only place a "light layer" is needed).

**Phased plan (if pursued), mirroring the methanogen:**
- **Phase 0 — data + go/no-go.** Pick strain (primary *Synechocystis* PCC 6803 with iSynCJ816 /
  the enzyme-constrained version; fallback *S. elongatus* UTEX 2973 for a faster grower); digitise a
  growth (and, if available, a photosynthesis-flux) TPC; resolve the light-regime and rate-target
  questions above; decide the Tm route (mesophile prior). Resolve Gate 4 to GREEN/AMBER before building.
- **Phase 1 — base → ecModel.** Reuse the ecModel or build sMOMENT on iSynCJ816 (as for iMR539);
  set the photoautotrophic medium (CO₂, light, minerals) with light as a **T-independent photon
  exchange**; validate photosynthetic growth + the correct C-fixation stoichiometry.
- **Phase 2 — thermal layer.** kcat(T)/unfolding with Li–Engqvist Topt + a mesophile Tm prior;
  **the new bit**: a documented temperature-independent light-supply constraint, plus (optional)
  photorespiration T-dependence and photoinhibition.
- **Phase 3 — allocation.** A cyanobacterial proteome-sector layer + its own allocation law
  (photosynthetic proteome is large and light-acclimating — its own "departure").
- **Phase 4 — calibrate** (emcee, to the digitised TPC) and **Phase 5 — Ea dissection** (SS-E;
  the control-weighted decomposition, now with the light-supply term as a candidate driver) and the
  three-organism comparison.

**Bottom line.** A cyanobacterium is the right low-$E_a$ third point and the most mechanistically
revealing, but it carries the one new layer (a temperature-independent light supply) and one
interpretive decision (growth vs photosynthesis $E_a$) that the two enzyme-limited organisms did not.
Recommend pursuing it as a dedicated follow-up, with a phase-0 gate that resolves the light-regime
question before committing to the build.

## Sources

- Yvon-Durocher et al. 2014, *Nature* 507:488–491 — the methanogenesis > respiration > photosynthesis $E_a$ ordering.
- Nogales et al. 2012 (iJN678); Joshi et al. (iSynCJ816, 816 genes / 1045 reactions); enzyme-constrained cyanobacterial GEM (ScienceDirect/Sci. rep. 2024); Chen et al. 2022 (GECKO 2.0 catalogue).
- Jarzab et al. 2020, *Nat. Methods* 17:495–503 (Meltome Atlas; no cyanobacterium among the 13 species); Li & Engqvist 2019 (sequence Topt predictor).
- *Synechococcus* thermal-ecotype growth TPCs (bioRxiv 2020; PMC5029218; marine warming PMC12976987); hot-spring *Synechococcus* thermotolerance (PMC92289).
- Farquhar–von Caemmerer photosynthesis model ($V_\text{cmax}$/$J_\text{max}$ T-dependence); RuBisCO deactivation / electron-transport co-limitation (PMC10192301); carboxysome CO₂-concentrating mechanism (bioRxiv 2020).
