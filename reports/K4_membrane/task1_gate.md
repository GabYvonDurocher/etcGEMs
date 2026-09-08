# K4 TASK 1 — the gate: can the four *Candida* models express an ETC membrane-area constraint?

**Answer: in one of the four, and it is the wrong one.** The mechanism is expressible and
load-bearing in *C. parapsilosis*, whose iDC1003 is an independently curated reconstruction.
In the three *Candidozyma* species — *C. auris* and the two relatives whose thermal divergence
is the whole question — the respiratory chain is present, is functional, and carries
**0.03 % of the respiratory load**, because the proton circuit is closed through eleven
uncosted amino-acid/H⁺ symporters instead of through the chain.

Reproduce with `python3 reports/K4_membrane/task1_etc_complement.py` (exit 0). Tables:
`task1_inventory.csv`, `task1_coupling.csv`, `task1_fva.csv`, `task1_proton_carriers.csv`,
`task1_uncoupling.csv`. Configuration: `candida_B3_ngamT`, the K2 rung (unfolding thermal
form, grounded budget, NGAM(T)), at 30 °C and 40 °C.

---

## 1. The complement: every complex is present

| complex | *C. auris* | *C. haemulonii* | *C. duobushaemulonii* | *C. parapsilosis* |
|---|---|---|---|---|
| I — NADH dehydrogenase | `R11945__mito`, `R11945__cyto` | same | same | `R11945__mito` |
| II — succinate dehydrogenase | `R02164__mito` | same | same | `R02164__mito` **uncosted** |
| III — cytochrome *bc*₁ | `R02161__mito` | same | same | `T02161__mito` |
| IV — cytochrome *c* oxidase | `R00081__mito` **uncosted** | same | same | `R00081__mito` **uncosted** |
| V — ATP synthase | `T_ATP_synthase__mito` | same | same | `T00485__cyto` |
| alternative oxidase (AOX) | **absent** | **absent** | **absent** | **absent** |
| plasma-membrane chain | absent | absent | absent | `TI6900005/7_CYTMEM__plas` |

**AOX: A3's finding is confirmed, and by a second method.** A3 established by alignment that
alternative oxidase is present in all four *proteomes* and in no model. Searching the four
SBMLs directly — by EC number (1.10.3.\*), by reaction name and by ubiquinol-oxidase chemistry
— returns nothing in any of them. The same holds for the GRX5-family glutaredoxins. So the
one ETC component that is genuinely fungal, that is the obvious candidate for a
thermally-relevant respiratory difference, and that Xiao et al. propose as a mechanism, cannot
be given a membrane footprint here because it has no reaction to attach one to.

Two encoding defects, both in the **published** iRV973 and not introduced by the K1 port
(checked directly against `$CANDIDAS_ROOT/gem/models/auris_iRV973.xml`):

* **Complex I is non-electrogenic as encoded.** `R11945` is written
  `NADH + ubiquinone + H⁺ → NAD⁺ + ubiquinol` with the proton taken from, and returned to, a
  single compartment. It carries EC 7.1.1.2, the proton-pumping complex I. Either the EC
  number or the stoichiometry is wrong. *C. parapsilosis* encodes the same step
  electrogenically (5 H⁺ in from the matrix, 4 H⁺ out to the cytosol).
* **Complex III pumps the wrong way.** `R02161__mito` consumes 1.5 cytosolic H⁺ and releases
  1.5 into the matrix — it *consumes* the proton-motive force rather than building it.
  *C. parapsilosis*' `T02161__mito` has the same 1.5 H⁺ in the correct direction.

## 2. The gate: presence is not the binding question

The area constraint is `Σᵢ (Aᵢ / kcatᵢ) · vᵢ ≤ A_ETC`, a bound on **flux variables**. A complex
that carries no flux contributes nothing to the left-hand side and cannot be constrained
however its footprint is parameterised. (It need not be enzyme-costed: cytochrome *c* oxidase
is uncosted in all four models and is still reachable by the constraint.)

**The fraction of ATP synthase's protons that the respiratory chain actually delivers:**

| species | 30 °C | 40 °C |
|---|---|---|
| *C. auris* | 0.003 % | **0.03 %** |
| *C. haemulonii* | 0.003 % | 0.02 % |
| *C. duobushaemulonii* | 0.02 % | 0.02 % |
| *C. parapsilosis* | **92.6 %** | **112.0 %** |

Three independent measurements agree.

**Knockouts.** In the three *Candidozyma* models, deleting complex I, II, III or IV changes
growth by less than 0.006 %. Deleting ATP synthase halves it. In *C. parapsilosis*, deleting
complex III or IV costs 37 % of growth at 30 °C and 52 % at 40 °C, and complex I costs 24 % at
40 °C.

**Flux.** At 40 °C in *C. auris*, ATP synthase runs at 10.35 while complex III runs at 0.0054
and cytochrome *c* oxidase at 0.0027 — a ratio of about 2000. In *C. parapsilosis* the same
three are 10.01, 5.81 and 2.91.

**Variability.** This is not an artefact of one optimum among many. At 99 % of optimal growth
the chain's flux range in the three *Candidozyma* models tops out at 0.18–0.51, against ATP
synthase's tightly determined 7.0–11.3. The chain *may* carry a little flux; it is never
required to carry much.

## 3. Why: the proton circuit is closed outside the chain

Tracing the mitochondrial proton budget of *C. auris* at 40 °C: ATP synthase delivers 31.04
H⁺/gDW/h into the matrix, and the single largest counter-flow is
`L_Aspartate_c00049_CytoMito__mito` at 32.52 — an aspartate/H⁺ symporter, reversible,
unbounded, and **uncosted**, whose own name mentions only aspartate. The model runs a futile
aspartate cycle to return protons to the cytosol, and ATP synthase runs on that.

There are **eleven** such uncosted, reversible metabolite/H⁺ carriers in each of the three
*Candidozyma* models (aspartate, pyruvate, guanosine, serine, threonine, tyrosine, valine,
lysine, tryptophan, asparagine, and an ATP/ADP antiporter). *C. parapsilosis* has three, and
its phosphate carrier — the fourth — is enzyme-costed.

**This is a class the existing sink audit cannot see.** `etcgem audit-sinks` looks for
uncosted reactions that move ATP, NAD(P)H, FADH₂, quinol, reduced ferredoxin, or a terminal
electron acceptor. These carriers move **protons**, which is none of those, so all eleven pass
the audit. The audit's classes A–D found 44–47 class-A hits in these same models and missed
this. A fifth class — uncosted transport of the coupling ion across an energy-transducing
membrane — is a framework-level gap, recorded in `docs/OPEN_ITEMS.md`.

## 4. Functional and bypassed, not broken

Two labelled diagnostics, neither adopted (`DECISIONS.md` D3).

**Close the carriers outright** and growth goes to zero in all three *Candidozyma* models —
they are the only route across the membrane for aspartate, pyruvate and five amino acids, so
this is too blunt to be a repair. But the chain lights up on the way down: complex III to 8.3,
cytochrome *c* oxidase to 4.1.

**Strip only the proton coupling**, keeping the metabolite transport, and the chain takes over
the whole load while the cell still grows:

| *C. auris*, 40 °C | as encoded | proton coupling removed |
|---|---|---|
| growth µ (model units) | 0.1022 | **0.0659** |
| complex I | 0.000 | 9.25 |
| complex III | 0.0054 | 9.25 |
| cytochrome *c* oxidase | 0.0027 | 4.63 |
| ATP synthase | 10.35 | 4.63 |

So the chain is **functional and bypassed**. The reconstruction is not missing an ETC; it is
missing the accounting that would force flux through it. Under the repair, respiration costs
the cell a third of its growth, which is the order of magnitude one expects when a free ATP
route is removed.

## 5. What this licenses

**It licenses building the mechanism and applying it, and it does not license using it to
compare the three *Candidozyma* species.** The one model in which an ETC area budget can bind
on a real respiratory chain is *C. parapsilosis* — the outgroup, 8.5–11.2 % apart in gene
content from the other three and the species whose thermal behaviour is not the puzzle. The
three species whose divergence K2 quantified share the *auris* scaffold, and in all three the
chain is inert.

That is a **structural** limit, and it is worth separating from the parameter limit TASK 2
guards against. Seq2Tm failed because its species differences were too small to matter. This
fails earlier: the reactions a membrane-area constraint would act on carry no load in three of
the four models, so no parameterisation of the table — however well sourced, however
differentiated between species — could make the constraint bind on respiration in them.

TASK 2 and TASK 3 proceed on that basis: build the table, apply it, and report what a
constraint does in models where it can only reach ATP synthase. The result is characterisation
of a mechanism that has been **made available and not tested**, and TASK 5 says what would
make it testable.
