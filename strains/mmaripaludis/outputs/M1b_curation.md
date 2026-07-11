# iMR539 → iMR539_curated: carbon-honest H2/CO2 autotroph (M1b)

Model curation on the M. maripaludis base GEM. **Plain FBA only** — no ecModel/thermal/
calibration (M2+). Goal: a clean autotroph on H2/CO2 whose biomass carbon derives from CO2,
so the M2 enzyme-constrained rates are meaningful. Solver: **Gurobi** (WLS academic).
Original `model/iMR539.xml` kept; edits on `model/iMR539_curated.xml`.

The mu overshoot (~0.55/h vs measured ~0.23/h) is **expected** for plain FBA (no enzyme/
maintenance ceiling, unpinned uptake) and is **not** addressed here — M2's enzyme constraint
sets the physiological rate.

## PART A — the four missing biomass precursors

The M1 audit found four biomass precursors with no biosynthesis: the published model could
not grow unless each was supplied by a free exchange (mu=0 if any closed). Tracing the
network showed they feed just **two** tiny (0.0031 stoich) biomass components:

### Membrane_lipid, NAC, Flagellin → **remove archaellin from biomass** (one edit, three fixed)
All three feed *only* the archaellin (archaeal flagellum) N-glycosylation branch, which is
otherwise a dead-end terminating at the biomass component ARCN:

```
MEMLIP + UDP-gal --GALgt--> LIP1SUG --...--> LIP3SUG + NAC --2NACgt--> LIP4SUG
LIP4SUG + Thr --TSot--> LIP4SUGT --TSf--> LIP4SUGT[e] ;  FLGN + LIP4SUGT[e] --TSost--> ARCN --> biomass
```
- **MEMLIP** ("Membrane_lipid") is the glycan-*carrier* lipid (dolichol/undecaprenyl-P
  analogue), **not** the bulk membrane phospholipid.
- **NAC** is an NDP cell-wall sugar for the glycan chain.
- **FLGN** is the apo-archaellin protein.

**Decision: remove ARCN (archaellin) from the biomass reaction; close all three exchanges.**
Justification: the archaellum is a dispensable motility appendage — standard practice to
exclude non-essential surface structures from a *growth* objective. The genuine bulk archaeal
ether membrane lipids, **SATARCHL** (saturated CDP-archaeol) and **SATARCHLS** (saturated
archaetidylserine), remain in biomass and are synthesised from CO2-derived CDP-archaeol
(CDPDGGR/ASDGGR, 8 H2 + CDP-archaeol, MMP0388) — the real membrane lipid was already
carbon-honest. This is the least-invasive fix: one biomass edit resolves three precursors,
versus gap-filling a speculative glycan-carrier-lipid + NDP-sugar biosynthesis.
*Scope note:* the model represents protein N-glycosylation only via archaellin; no other
glycoprotein depends on this branch.

### tRNA(SeCys) → **restore tRNA recycling** (gap-fill; keep the essential selenoprotein)
The selenocysteine pathway is otherwise complete and gene-annotated:
```
tRNA(Sec) + Ser + ATP --rxn09249/MMP0879--> Ser-tRNA(Sec)
Ser-tRNA(Sec) + ATP --rxn11751/MMP1490(PSTK)--> O-Pseryl-tRNA(Sec)
O-Pseryl-tRNA(Sec) + selenophosphate --rxn11752/MMP0595(SepSecS)--> SeCys-tRNA(Sec)
SeCys-tRNA(Sec) --rxn11950--> Selenoprotein          (** did NOT release free tRNA **)
```
The incorporation step `rxn11950` consumed the charged tRNA but never regenerated the free
tRNA(Sec), so every selenoprotein permanently consumed one tRNA that only the exchange could
supply — a **recycling gap**, not a real biomass requirement.

**Decision: make rxn11950 also produce free tRNA(Sec)** (`SeCys-tRNA(Sec) → Selenoprotein +
tRNA(Sec)`); close the tRNA exchange. Justification: tRNA is a catalytic macromolecule
released after aminoacyl transfer. Selenoproteins are **essential** in M. maripaludis (the
Fru/Vhu/Fdh hydrogenases/formate-DH are selenoenzymes), so the selenoprotein stays in
biomass. Selenium is supplied as a medium trace (**selenate**, cpd03396); selenophosphate is
synthesised internally (rxn02569 from selenide). Net inputs to the branch — serine (from
CO2), selenophosphate (from medium Se), ATP — are all honest.

## PART B — organic-C leaks + CH4
- **Closed** the free organic-carbon uptakes: **acetate** (cpd00029) and **octadecenoate**
  (cpd15269) — spurious organic-C on an autotrophic medium. Left as products only (lb=0).
- **Unpinned CH4:** the shipped model fixed the CH4 exchange at (50, 50); reset to (0, 1000)
  so methane is an emergent output.
- Defined medium kept open (availability, not pinned): H2, CO2, NH3, phosphate, H2S,
  selenate (Se trace), mineral salts.

## Two vitamin cofactors supplied as a documented medium trace (honest residual)
Investigating carbon-honesty surfaced two further gaps beyond the flagged four: **thiamin
(B1, cpd00305)** and **NMN (cpd00355, NAD precursor)** have **no de novo biosynthesis** in
iMR539 (thiamin: only uptake→phosphorylation→TPP; NMN: only feeder to NAD, de novo NaAD
route gapped) — closing either zeros growth. Gap-filling would require adding whole
speculative pathways (violating least-invasive), and methanogen defined media routinely
include a vitamin supplement (Balch vitamins). **Decision: supply thiamin + NMN as documented
defined-medium traces.** Carbon impact is negligible — together 0.058 mmol C/gDW/h vs 257.2
from CO2, i.e. **0.022%** of biomass carbon. Flag for optional gap-fill in M2 if a
vitamin-free defined medium is wanted.

## PART C — carbon-honest autotrophy (verified; `outputs/curated_validation.json`)
- Grows on H2/CO2 with **all four precursor exchanges closed (bounds (0,0), zero flux)**:
  **mu = 0.548 /h**.
- **Carbon balance: 99.978% of carbon uptake is CO2** (257.22 of 257.28 mmol C/gDW/h); the
  remaining 0.022% is the two documented vitamin traces. CO2 in (257.2) − CH4 out (242.7) =
  ~14.5 mmol C fixed into biomass, all CO2-derived.
- Methanogenesis stoichiometry preserved: **H2 : CO2 : CH4 = 4.12 : 1.06 : 1** (theory 4:1:1).
- Sanity re-checks: no growth without electron donor (no-H2 mu=0) or carbon (no-CO2 mu=0).

## PART D — GO / NO-GO for M2 (ecModel)

**GO.** M2 inherits a **carbon-honest H2/CO2 autotroph**: biomass carbon from CO2, correct
methanogenesis stoichiometry, no free biomass-precursor uptake, no organic-C leaks, CH4 an
emergent product, and (from M1) no thermodynamic energy loops + 85% metabolic GPR coverage.

**Residual caveats carried into M2 (honest):**
1. Two vitamin cofactors (thiamin, NMN) are defined-medium traces (0.022% of C) — gapped
   biosynthesis; optional gap-fill only if a vitamin-free medium is required.
2. Archaellin/N-glycosylation is folded out of biomass (motility structure); if archaellum
   cost ever matters, restore it with a proper glycan-carrier + NDP-sugar biosynthesis.
3. mu overshoots the measured value — expected; the M2 enzyme/maintenance layer sets the rate.
4. Formatotrophic growth still unsupported by the base GEM (only relevant if formate TPCs are
   needed).
