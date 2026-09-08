# K5 TASK 1 — the coupling-ion audit, on all seven strains

**Only the three *Candidozyma* models have the defect. *E. coli* does not, and neither do
*C. parapsilosis*, *M. maripaludis* or *Synechocystis*.** That is the answer to the question
the prompt flags as the significant one: Parsa's configuration E and F respiration R² values,
0.72 and 0.96, do not rest on a leaking proton circuit.

Reproduce with `python3 reports/K5_respire/task1_coupling_audit.py` (exit 0), or per strain
with `etcgem audit-sinks --strain S --coupling-ion`. Tables: `task1_budget.csv`,
`task1_translocators.csv`.

---

## Why classes A–D could not see this

`etcgem audit-sinks` watches **chemical** free-energy carriers — ATP, NAD(P)H, FADH₂, quinol,
reduced ferredoxin — and terminal electron acceptors. It does not watch the **ion** that ATP
synthase runs on. So a model can close its proton circuit through free metabolite/H⁺ symporters
and every one of those reactions passes clean. The three *Candidozyma* models report 44–47
class-A hits each while this went unnoticed.

Class E is a **budget**, not a list, and it needs a solved state: a free proton carrier that
exists but carries nothing is not a defect.

## Two things the audit has to get right, or it mis-reads whole organisms

**The coupling ion is not always the proton.** *M. maripaludis*' ATP synthase in this project
is **sodium**-driven, four Na⁺ per ATP. The ion is therefore inferred from each strain's own
ATP synthase rather than assumed, which is what the name of the class refers to.

**The ion enters the energised compartment two ways.** It can be *translocated* across the
membrane, which is the mitochondrial and bacterial case, or *released chemically inside* that
compartment, which is what photosynthetic water splitting and cytochrome *b*₆*f* do into a
thylakoid lumen. Counting translocation alone scores *Synechocystis* at 19 % when its chain in
fact supplies all of it. Both are reported.

A third had to be handled to get *E. coli* at all: **GECKO splits a reaction into an arm and
its isozymes**, joined by a pseudo-metabolite, so the two halves of ATP synthase live in
different reactions — `arm_ATPS4rpp` consumes four periplasmic protons while `ATPS4rppNo1`
produces the ATP and three cytosolic ones. A test wanting both in one reaction finds no ATP
synthase in eciML1515 at all. The audit contracts those groups first.

## The budget, all seven strains

Ions delivered to the energised side, against those ATP synthase draws from it.

| strain | ion | membrane | µ | ATP synthase draws | chain, translocated | chain, in-compartment | carriers | **chain supplies** |
|---|---|---|---|---|---|---|---|---|
| *C. auris* | H⁺ | mito→cyto | 0.1022 | 31.04 | 0.016 | 4.94 | 32.60 | **0.05 %** |
| *C. haemulonii* | H⁺ | mito→cyto | 0.0892 | 29.06 | 0.014 | 4.36 | 29.39 | **0.05 %** |
| *C. duobushaemulonii* | H⁺ | mito→cyto | 0.0698 | 26.30 | 0.011 | 3.01 | 28.97 | **0.04 %** |
| *C. parapsilosis* | H⁺ | mito→cyto | 0.0830 | 30.02 | 33.63 | 8.24 | 11.60 | 112 % |
| *E. coli* | H⁺ | c→p | 0.5248 | 144.00 | 178.10 | 0.00 | 48.50 | **124 %** |
| *M. maripaludis* | **Na⁺** | c0→e0 | 0.1040 | 111.97 | 117.22 | 0.00 | 0.00 | 105 % |
| *Synechocystis* | H⁺ | c→lumen | 0.0489 | 58.38 | 10.84 | 47.54 | 0.00 | 19 % / **100 %** |

*Synechocystis* is given both readings because its supply is chemical: cytochrome *b*₆*f*
releases 31.8 and the oxygen-evolving complex 15.7 protons into the lumen, both costed, plus
10.8 translocated by cytochrome *c* oxidase. That sums to 58.4, exactly ATP synthase's draw.

*M. maripaludis* is audited at its **calibrated** operating point (`kcat_scale` 7.223, its own
`nominal_kcat_scale`). At the a-priori point its LP is infeasible — the maintenance-crushed
state K2 documented — so an audit there would read fluxes off a failed solve. The status is
recorded either way.

## Uncosted and reversible, per strain

| strain | ion reactions carrying flux | uncosted | of those, reversible |
|---|---|---|---|
| *C. auris* | 80 | 17 | **9** |
| *C. haemulonii* | 75 | 15 | **11** |
| *C. duobushaemulonii* | 84 | 22 | **15** |
| *C. parapsilosis* | 87 | 8 | 3 |
| *E. coli* | 16 | 12 | **0** |
| *M. maripaludis* | 4 | 0 | 0 |
| *Synechocystis* | 8 | 1 | 0 |

**The pattern that separates the broken models from the healthy ones is reversibility, not
uncostedness.** *E. coli* has twelve uncosted proton-moving reactions and none of them is
reversible, so none can be run backwards to manufacture a gradient. The three *Candidozyma*
have nine to fifteen uncosted **reversible** carriers, and the solver uses one of them —
`L_Aspartate_c00049_CytoMito__mito`, delivering 32.5 of the 31.0 protons per hour ATP synthase
needs in *C. auris*.

## One honest secondary observation about *E. coli*

*E. coli* is not clean in the sense of having no free proton delivery. `PYRt2rpp_REV`, an
uncosted pyruvate/proton symporter running in reverse, delivers **48.5** protons per hour to
the periplasm, 34 % of what ATP synthase draws, and `Htex_REV` removes 53.3. Those are
uncosted, and in a model where the chain were weaker they could matter. They do not matter
here because the chain over-supplies: 178.1 against a draw of 144.0. **Reported, not fixed —
P4 owns eciML1515**, and nothing in this run writes there.

## What this licenses

The defect is specific to the three *Candidozyma* models, which share the *iRV973* scaffold.
*C. parapsilosis*, built from an independently curated reconstruction, is healthy on the same
metric under the same configuration. So this is a property of one reconstruction, not of the
model class, not of the framework, and not of fungi.
