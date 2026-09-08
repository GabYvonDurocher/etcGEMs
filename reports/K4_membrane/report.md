# K4 — the ETC membrane-area constraint carried to the four *Candida* strains

_2026-09-08. Branched from `main` at **ed56d4d**. Runs in parallel with P4, which owns
`strains/eciML1515/` and `reports/ecoli_gasflux/`; nothing here writes there._

P1 collapsed Parsa's configurations E and F into one table-driven ETC membrane-area mechanism
in the core, and P3 gated it against measured *E. coli* respirometry (configuration E
respiration R² 0.72, configuration F 0.96). K4 carries that validated mechanism to a new
organism. It is the first mechanism in either codebase whose species-specificity need not come
from a sequence predictor, which is why §6a of the discussion notes calls it the leading open
candidate.

**The short version.** The mechanism has been built, applied and reported. It cannot carry the
interspecies comparison, for two independent reasons — one structural, one parametric — and
neither is the reason the prompt anticipated. It is **available and not tested**, and §5 says
exactly what that licenses.

Reproduce everything with:

```bash
python3 reports/K4_membrane/task1_etc_complement.py    # the gate
python3 reports/K4_membrane/task2_build_tables.py      # the tables + sourcing
python3 reports/K4_membrane/task3_sweep.py             # the A_ETC sweep
python3 reports/candida_thermal_limit/gate_table.py    # K1's gate, still 79/79
```

---

## 1. Is the mechanism expressible in these models at all?

**Every complex is present. In three of the four models the chain carries no load, so the
constraint has nothing to bind on.** Detail and method: `task1_gate.md`.

Complexes I–V are encoded in all four models. Alternative oxidase is in none of them —
confirming A3 by a second method, searching the SBML by EC number, name and chemistry — while
being present in all four proteomes. The one genuinely fungal branch of the ETC, and the one
Xiao et al. propose as a mechanism, has no reaction to attach a footprint to.

The area constraint is `Σᵢ (Aᵢ / kcatᵢ) · vᵢ ≤ A_ETC`, a bound on **flux variables**. Presence
is therefore not the binding question; flux is. The fraction of the protons ATP synthase
consumes that the respiratory chain actually delivers:

| species | 30 °C | 40 °C |
|---|---|---|
| *C. auris* | 0.003 % | **0.03 %** |
| *C. haemulonii* | 0.003 % | 0.02 % |
| *C. duobushaemulonii* | 0.02 % | 0.02 % |
| *C. parapsilosis* | **92.6 %** | **112.0 %** |

Three measurements agree. Deleting complex I, II, III or IV moves growth by less than 0.006 %
in the three *Candidozyma* and costs *C. parapsilosis* 37–52 %. At 40 °C in *C. auris*, ATP
synthase runs at 10.35 while complex III runs at 0.0054. Flux variability at 99 % of optimal
growth shows this is structural, not one optimum among many.

**The cause is identified, not assumed.** Eleven uncosted, reversible metabolite/H⁺ symporters
close the proton circuit outside the chain; one of them, an aspartate/H⁺ carrier, supplies 32.5
of the 31.0 protons per hour ATP synthase needs at 40 °C. Stripping only their proton coupling
makes the chain carry the whole load and costs a third of predicted growth — so the chain is
**functional and bypassed**, not broken. The defect is in the published iRV973, checked
read-only; it is not a porting artefact.

**What the chain is for, in these models, is pyrimidines.** Ubiquinol has exactly one producer
— dihydroorotate dehydrogenase, itself essential — and two sinks, complex III and complex II
run backwards. Delete both sinks and the cell cannot make RNA. The chain's flux is set by
nucleotide demand, not energy demand, which is why it sits at 0.005 while ATP synthase sits at
10.

**Verdict.** Expressible and load-bearing in *C. parapsilosis*. In the three *Candidozyma* the
constraint can be applied but can only reach ATP synthase. Those three are the species whose
divergence is the question; *C. parapsilosis* is the outgroup.

## 2. What the complex tables are actually made of

Built by `task2_build_tables.py`; per-value provenance in `task2_sourcing.csv`.

| column | provenance | count |
|---|---|---|
| `area_nm2` | **derived from solved structures of fungi** | **20 / 20 (100 %)** |
| `kcat_s` | **taken from *E. coli*** | **20 / 20 (100 %)** |
| `reactions` | read off each model | 20 / 20 |
| `h_p_target` | left blank, deliberately | — |
| **measured in a *Candida* species** | — | **0 / 20, area and turnover alike** |

The areas came out better than expected. Rather than transferring *E. coli* footprints, they
are membrane-plane cross-sections of the complexes oriented in the bilayer, from fungal
structures: complex I from *Yarrowia lipolytica* (PDB 6RFR, 137.4 nm²) and complexes II, III,
IV and V from *S. cerevisiae* (9KPS 15.4; 6HU9 68.2 for the bc₁ dimer and 45.0 for cytochrome
*c* oxidase; 6B2Z 57.9 for the ATP synthase monomer). Two independent derivations agree to
0.2–4 %, and six values cross-check against dimensions stated in the source papers.

The turnovers had no such rescue: **no kcat has been measured for any ETC complex of any
*Candida* species**, so every one is *E. coli*'s.

**The decisive point, stated before any result is interpreted. Every footprint and every
turnover is identical across the four species.** A constraint whose parameters do not differ
between species cannot explain a difference between them. This is the same failure mode as
Seq2Tm's overlapping distributions, and it is better found here than by a referee.

Three things were considered and rejected as ways to make the table species-specific:

* **The models' own DLKcat turnovers** do differ — 61.3 / 37.3 / 50.7 s⁻¹ for complex I across
  the three *Candidozyma*, a 1.6× spread. They come from the predictor family A1 found has no
  demonstrated per-protein validity in this regime, and for complex III and ATP synthase the
  "prediction" is the parse default 13.7 s⁻¹ in all four species. Using them would import the
  exact channel this whole line of work exists to get away from.
* **Molecular weight** differs by 3.6 % across the three *Candidozyma*. It is also the wrong
  quantity: Carlson et al. (2024) show membrane footprint does not scale with enzyme mass.
* **Complex-level identity.** In all three iRV973-derived models, complexes I, III and ATP
  synthase share **one identical set of seven genes** and therefore one molecular weight. The
  models do not distinguish these three complexes, so a table that gives them different
  footprints and turnovers is more specific than the models it describes.

**The budget itself, A_ETC, is a free knob, and the prompt's premise about it is wrong in a
useful way.** There is no published mitochondrial inner-membrane area for any *Candida*, and no
inner:outer membrane area ratio for **any fungus**. Building one from *S. cerevisiae*
stereology gives ≈ 6 × 10¹⁸ nm²/gDW, of which ~40 % is occupied by redox complexes and ATP
synthase (Schwerzmann et al. 1986, rat liver — the measured counterpart of Szenk's 0.316 for
*E. coli*), so ≈ 2.4 × 10¹⁸ nm²/gDW of ETC-capable membrane. *E. coli*'s figure is
4.3 × 10¹⁸. **Per gram dry weight the mitochondrion buys yeast no expansion of bioenergetic
membrane at all — it is within a factor of two, and on the low side.** Cristae amplify area per
cell *volume*, which is not the denominator this constraint uses.

## 3. What happens when it is applied

`task3_sweep.py`, under the K2 configuration (`candida_B3_ngamT`: unfolding thermal form,
grounded budget, NGAM(T)). Nothing is fitted. A_ETC is swept as a multiple of **A\*** = the
area the unconstrained *C. auris* model uses at 30 °C = **2.62 × 10¹⁷ nm²/gDW**.

**Where the area goes.** ATP synthase takes **99.6–99.99 %** of the area used in the three
*Candidozyma* and **11–16 %** in *C. parapsilosis*. In three of four species this is
arithmetically a constraint on ATP synthase.

**The chain-only sweep is the cleanest statement.** Constraining complexes I–IV alone, all the
way to zero, changes growth at 40 °C by:

| species | unconstrained | A_ETC = 0 | change |
|---|---|---|---|
| *C. auris* | 0.7836 | 0.7836 | **0.0000** |
| *C. haemulonii* | 0.6840 | 0.6839 | 0.0001 |
| *C. duobushaemulonii* | 0.5353 | 0.5353 | 0.0000 |
| *C. parapsilosis* | 0.6368 | 0.3087 | **−52 %** |

**Descriptors under the full table** (µ in model units, so the peak-matched scale cannot mask a
magnitude change):

| A_ETC | peak µ *auris* | peak µ *haem* | peak µ *duo* | peak µ *parap* | T_opt *auris* | CT_max *auris* | R² *auris* |
|---|---|---|---|---|---|---|---|
| unconstrained | 0.1041 | 0.0894 | 0.0738 | 0.0860 | 38.0 | 53.58 | 0.254 |
| 2 × A\* | 0.1041 | 0.0894 | 0.0738 | 0.0617 | 38.0 | 53.58 | 0.254 |
| 1 × A\* | 0.0887 | 0.0848 | 0.0717 | 0.0551 | 36.5 | 53.66 | 0.473 |
| 0.5 × A\* | 0.0632 | 0.0628 | 0.0573 | 0.0515 | 35.5 | 53.02 | 0.733 |
| 0.1 × A\* | 0.0402 | 0.0457 | 0.0446 | 0.0473 | 34.5 | 48.53 | **0.908** |
| 0 | 0.0346 | 0.0415 | 0.0415 | 0.0454 | 34.0 | 47.00 | 0.890 |

E_a moves little (1.15–1.46 eV throughout). The three *Candidozyma* are **completely unmoved
down to 2 × A\*** while *C. parapsilosis* responds at 3 × A\* — the constraint reaches the one
species with a working chain first, which is the gate showing up again.

**Two things worth noticing, in opposite directions.**

*In favour:* the constraint substantially improves the calibration strain's fit. *C. auris*'
R² rises 0.254 → **0.908** and its CT_max falls 53.6 → 48.5 °C, against an observed limit near
45. A membrane budget pulls the over-predicted ceiling down, which is the direction §4 of the
discussion notes says something must.

*Against, and decisive:* **it acts in the wrong direction across species.** Tightening the
budget from non-binding to zero costs *C. auris* **3.0×** of its peak growth and the relatives
only 1.8–2.2×. The thermotolerant species is the *most* membrane-limited of the four. And the
relatives' fits get worse, not better (*C. haemulonii* R² −2.03 → −2.87). To reproduce the
observed divergence the mechanism would have to hurt the relatives more; it does the opposite.

**Flatness, per N1's guard.** The core's own guard does not fire in this configuration
(proteome sectors are off), so the same quantity is computed directly with the same function
and written to `task3_flatness.json`. The 1 %-of-peak plateau is **1.5–3.0 °C on a 60 °C grid**
at every A_ETC level and for every species. These are genuine peaks: unlike K2's rung B4, the
area constraint does not flatten the curve, so T_opt is meaningful here.

## 4. The required difference, beside K2's 13.8 °C

K2 asked what uniform Tm separation would push a relative below the 0.05 h⁻¹ detection floor at
40 °C, and got **13.8 °C** against 0.411 °C predicted and 1.6 °C measured — a shortfall of 26×
and 8.6×.

**The A_ETC analogue has no answer.** No membrane budget puts any relative below the floor at
40 °C — not a small one, not zero:

| species | µ(40 °C) unconstrained | at A_ETC = 0 | detection floor |
|---|---|---|---|
| *C. haemulonii* | 0.684 | **0.283** | 0.05 |
| *C. duobushaemulonii* | 0.535 | **0.261** | 0.05 |
| *C. parapsilosis* | 0.637 | **0.290** | 0.05 |

With oxidative phosphorylation shut off entirely the relatives still grow at 5–6× the
detection floor, because the models can ferment. Measured, all three are at exactly 0.000 h⁻¹
at 40 °C while *C. auris* is at 0.664.

| mechanism | required interspecies difference | available | shortfall |
|---|---|---|---|
| enzyme Tm (K2) | 13.8 °C | 0.411 °C predicted; 1.6 °C measured | 26× ; 8.6× |
| **ETC membrane area (K4)** | **no finite value; the mechanism cannot produce the phenotype at any budget** | no measurement exists for any *Candida*; nearest fungal proxy 7× | **not expressible as a ratio** |

The two failures are different in kind, and the difference matters. The Tm route fails
*quantitatively* — the mechanism works, and the available difference is 26× too small. The
membrane-area route fails *structurally*: there is no value of the parameter that produces the
observed phenotype, so no measurement could rescue it in these models as they stand.

For completeness, the comparator the prompt asks for. No study has measured mitochondrial
membrane area comparatively across fungal species. The largest documented biological variation
is **3–6× within *S. cerevisiae* across carbon source**, and the nearest cross-species fungal
proxy is Arthur & Watson (1976), who measured cytochrome *aa*₃ per mg dry weight across seven
yeasts including *C. parapsilosis* and found **7×** (and >20× including a respiratory-deficient
thermophile). Against a requirement that does not exist as a finite number, none of these can
be compared — which is itself the honest answer.

**And a literature-grounded budget does not bind at all.** The first-principles yeast figure,
≈ 2.4 × 10¹⁸ nm²/gDW, sits at **9 × A\***. Even its lower bound is above A\*. Physical membrane
area is not a limiting resource in these models at any defensible parameterisation.

## 5. What this licenses, and what it does not

**It licenses these statements.**

* The core's ETC membrane-area mechanism now runs on a eukaryote and on four new strains, from
  per-strain data files, with no code change. That was the capability P1 was built for and it
  transfers.
* In *C. parapsilosis*, whose reconstruction encodes a coupled respiratory chain, the
  constraint binds on respiration and behaves sensibly: it reduces growth, lowers CT_max and
  improves fit at intermediate budgets.
* An ETC area budget applied to the three *Candidozyma* models is a constraint on ATP synthase,
  not on respiration — measured, at 99.6–99.99 % of the area used.
* A first-principles yeast membrane budget is ~9× too generous to bind on these models.
* Per gram dry weight, mitochondrial cristae give yeast no more bioenergetic membrane than
  *E. coli* has.
* Within these models, no membrane-area budget reproduces the observed collapse of the
  relatives at 40 °C, and tightening the budget hurts *C. auris* most.

**It does not license these.**

* **Any claim that membrane area does or does not explain the *Candida* thermal divergence.**
  The mechanism has been **made available and NOT tested as an explanation**. It was not tested
  because it could not be: the parameters that would carry species signal do not exist for any
  *Candida*, and in three of the four models there is no respiratory load for them to act on.
  That is the honest statement the prompt asks for, and it is the one to quote.
* **Any interspecies comparison from these tables.** Every footprint and turnover is identical
  across the four species. Any difference the sweep shows between species comes from network
  and reconstruction differences, not from membrane parameters.
* **Any conclusion about *C. auris* versus the relatives from the *C. parapsilosis* result.**
  The one species where the mechanism binds properly is the outgroup, 8.5–11.2 % apart in gene
  content, and it is not the species whose thermal behaviour is the puzzle.
* **Any reading of the improved *C. auris* fit (R² 0.254 → 0.908) as support for the
  hypothesis.** It is a one-parameter constraint tightened until a curve fits, on the strain the
  configuration is calibrated on, while the same constraint makes all three relatives worse. It
  is what over-fitting looks like, and it is reported because hiding it would be worse.
* **Anything about membrane lipids.** This constraint has no lipid term. Lipidomics would bear
  on fluidity and proton leak, which are a different mechanism needing the extension A8 scopes.

**One thing that would have made the result different, and did not.** The prompt anticipated
the failure mode where footprints cannot be differentiated between species — the Seq2Tm trap —
and that trap did close exactly as predicted. But it was not the binding constraint. Even with
perfectly measured, strongly differentiated per-species footprints, the mechanism would still
do nothing in three of the four models, because the reactions it acts on carry no load. The
structural obstacle sits in front of the parametric one, and it is cheaper to fix: it needs a
reconstruction repair, not a measurement campaign.

---

## Files

| what | where |
|---|---|
| the gate, in full | `task1_gate.md` |
| ETC inventory, coupling, FVA, essentiality, quinol balance, proton carriers | `task1_*.csv` |
| the complex tables | `strains/*/etc/complexes.csv` |
| per-value sourcing | `task2_sourcing.csv` |
| the A_ETC sweep, binding per temperature, counterfactual, flatness | `task3_*.csv`, `task3_flatness.json` |
| what would make this a real test | `task5_what_would_test_it.md` |
| decisions | `DECISIONS.md` |
