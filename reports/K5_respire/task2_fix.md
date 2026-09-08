# K5 TASK 2 — the repair: which fix worked, and what it cost

**Costing the transport does not work. Constraining the direction does.** The adopted fix is a
direction constraint on uncosted, reversible proton carriers, applied as an experiment overlay
(`configs/experiments/candida_B5_respire.yaml`) rather than as a strain default.

Reproduce with `python3 reports/K5_respire/task2_fix.py` (exit 0). Tables:
`task2_fix_comparison.csv`, `task2_reaction_justification.csv`.

---

## The three candidates, tried in order

### (a) Cost the transport — **fails**

Config A's mechanism, MMRT-costed membrane carriers, gated on *E. coli* by P3. It was tried
first because it is a mechanism this project already has, it adds no assumption about
direction, and if free proton pumping stopped being free the solver might prefer the chain on
its own.

It costs 78 mitochondrial carriers in the three *Candidozyma* and 33 in *C. parapsilosis*.
The chain still supplies **0.04–0.05 %**.

The reason is an arithmetic mismatch. At a generic carrier's cost — 35 kDa, 300 s⁻¹ — the
aspartate cycle running at 32.5 mmol/gDW/h consumes about 1 % of a 0.0923 g/gDW proteome
budget, while the free gradient it manufactures buys roughly ten times the ATP the chain would
have to pay for. Making the leak slightly expensive does not close it.

### (b) Constrain the direction — **works, and is adopted**

For each uncosted, reversible carrier, the direction that pumps protons **into** the cytosol is
bounded to zero. The physiological direction, protons flowing down the gradient into the
matrix, is left completely open.

**The justification, per reaction and identical for all of them:** a proton-coupled symporter
is driven *by* the electrochemical gradient. It cannot build the gradient that drives it. Run
in the export direction it is a free proton pump, which is not a property of the carrier but an
artefact of a model that prices metabolites and not the ion. Nothing is deleted, no numerical
bound is invented, and the reaction remains available in the direction biology uses it.

**Iteration turned out to be required, and that is itself a finding.** Constraining only the
one carrier that leaks is not enough: in *C. duobushaemulonii* the solver answers by routing
the same free export through a different carrier, and it took four rounds to close. The loop
closes a *route*, not a reaction.

| species | rounds | carriers the solver actually used |
|---|---|---|
| *C. auris* | 3 | 5 |
| *C. haemulonii* | 5 | 7 |
| *C. duobushaemulonii* | 4 | 8 |
| *C. parapsilosis* | 0 | 0 |

The adopted overlay applies the **general rule** rather than that discovered list — no uncosted
reversible carrier may export protons into the cytosol — which touches 134 reactions in the
three *Candidozyma* and 2 in *C. parapsilosis*. **The two give identical growth to six decimal
places** (*C. auris* 0.065380 either way), so the 129 extra constraints bind on nothing. The
general rule is preferred only because it does not depend on which carrier the solver happened
to pick at one temperature.

### (c) Explicit bounds — **not needed, not used**

## The proton budget, before and after

Chain supplies, as a fraction of what ATP synthase draws, at 40 °C:

| species | before | after |
|---|---|---|
| *C. auris* | 0.05 % | **200 %** |
| *C. haemulonii* | 0.05 % | **272 %** |
| *C. duobushaemulonii* | 0.04 % | **213 %** |
| *C. parapsilosis* | 112 % | 112 % (nothing to constrain) |

## What it cost

Predicted growth in model units at 40 °C:

| species | before | after | cost |
|---|---|---|---|
| *C. auris* | 0.1022 | 0.0654 | **−36 %** |
| *C. haemulonii* | 0.0892 | 0.0559 | **−37 %** |
| *C. duobushaemulonii* | 0.0698 | 0.0432 | **−38 %** |
| *C. parapsilosis* | 0.0830 | 0.0830 | 0 % |

K4 measured about one third for stripping the proton coupling by hand. This is the same
quantity, arrived at by a constraint rather than by editing stoichiometry.

## The over-supply is not a new leak: complex III is wired backwards

A repaired chain should supply close to 100 %. It supplies 200–272 %, and the reason is the
second reconstruction defect K4 reported, now quantified. Tracing *C. auris* at 40 °C after the
repair:

| flux (mmol gDW⁻¹ h⁻¹) | reaction | |
|---|---|---|
| **+28.95** | `R00081__mito` cytochrome *c* oxidase | pumps protons out to the cytosol |
| −14.47 | `R02161__mito` complex III | **consumes** cytosolic protons |
| −14.47 | `T_ATP_synthase__mito` ATP synthase | consumes cytosolic protons |

Complex III in the *iRV973* models is encoded with its 1.5 protons moving cytosol→matrix, the
opposite direction to a mitochondrion. So it spends proton-motive force instead of making it,
and it eats **exactly half** of what cytochrome *c* oxidase pumps. That is where the factor of
two comes from, and it means the repaired model still wastes half its respiratory gradient.

**Not fixed here.** It is a second, independent change to the reconstruction, and making two at
once would leave TASK 3's before-and-after unattributable. TASK 3 therefore reports the adopted
repair and carries the complex III correction as a separate labelled sensitivity.

## Where the fix lives, and why not in `strain.yaml`

`configs/experiments/candida_B5_respire.yaml`, as rung B5 of the K2 ladder. Putting it in
`strain.yaml` would change the `resolved_config.yaml` of every committed run of these strains
and move K1's locked numbers, which the gate checks. The unrepaired model stays the default and
both are runnable side by side.

The core gained one function, `providers.forbid_free_ion_export`, and one config key,
`provider.forbid_ion_export`, naming the energised compartment and the ion. **K1's gate still
passes 79/79, exit 0**, because nothing runs it by default.
