# K4 — decisions

Standing rules carry over. `$CANDIDAS_ROOT` is READ ONLY. This run owns `strains/c*/` and
`reports/candida_*` / `reports/K4_membrane/`; P4 owns `strains/eciML1515/` and
`reports/ecoli_gasflux/` and nothing here writes there.

Branched from `main` at **ed56d4d** ("Merge P3: configurations D, E and F gated against
experiment; c_max adopted from Parsa's own sweep"), which is where `main` stood at the start
of this run. P4's work sits on `p4/refit` and is not in this branch.

---

## D0 — the run is done in a separate worktree, because P4 is live in the primary checkout

**Where:** TASK 0.

P4 is running in the primary working copy on branch `p4/refit` with uncommitted work in
`strains/eciML1515/` and `reports/P4_refit/`. Checking out a K4 branch there would have moved
P4's files under it.

**Decided:** `git worktree add ../etcGEMs-k4 -b k4/membrane-candida main`. The two runs share
one object store and never share a working tree. Nothing in this run touches P4's half, which
`git diff main --stat` confirms at the end.

## D1 — TASK 1 is answered on flux, not on presence, because presence is not the binding question

**Where:** TASK 1.

The prompt frames the gate as "which complexes are in the model". Reading the SBML answers
that quickly and the answer is encouraging: complexes I–V are all present in all four models.
Taken alone it would have licensed building the table and applying the constraint.

It would also have been wrong. The area constraint is
`sum_i (A_i / kcat_i) * v_i <= A_ETC` — a bound on **flux variables**. A complex that is
present but carries no flux contributes nothing to the left-hand side, so the constraint
cannot bind on it however the table is parameterised. Presence is necessary and nowhere near
sufficient.

**Decided:** the gate is decided on whether the modelled chain is **load-bearing**, measured
three ways that agree — per-complex knockout, flux variability at 99 % of optimal growth (so
that "carries no flux at the optimum" and "cannot carry flux" are separated), and the
mitochondrial proton budget. The headline quantity is the fraction of the protons ATP
synthase consumes that the respiratory chain actually delivers.

Note that the constraint reaches uncosted reactions too, since it is written on flux and not
on enzyme mass. Cytochrome c oxidase is uncosted in all four models and is still constrainable.
Cost membership is reported because it decides whether a complex responds to temperature
through the enzyme layer, not whether the area constraint can see it.

## D2 — the three *Candidozyma* models fail the gate, and the reason is a proton shunt, not a missing complex

**Where:** TASK 1. Numbers in `task1_gate.md`; tables beside it.

In *C. auris*, *C. haemulonii* and *C. duobushaemulonii* the respiratory chain supplies
**0.00–0.03 %** of the protons ATP synthase consumes. Knocking out complex I, II, III or IV
changes growth by less than 0.006 %. ATP synthase runs at flux 6–10 while the whole chain runs
at 0.000–0.005.

The cause is identified rather than assumed: **eleven uncosted, reversible metabolite/H+
symporters** carry protons across the inner membrane, and one of them,
`L_Aspartate_c00049_CytoMito__mito`, carries 32.5 of the 31.0 protons per hour that ATP
synthase needs at 40 °C. The proton circuit is closed through a free amino-acid cycle instead
of through the chain.

**Decided:** report this as the TASK 1 result and treat the three *Candidozyma* models as
**not able to express the mechanism in a way that means anything**, while stating precisely
that the complexes are present and functional and that it is the proton accounting that
defeats it. "The ETC is not in the model" would have been the wrong sentence; the ETC is in
the model and is bypassed.

## D3 — the surgical uncoupling is a diagnostic and is NOT adopted

**Where:** TASK 1.

Stripping the proton coupling from the eleven uncosted carriers, while keeping the metabolite
transport they exist to provide, makes the chain carry the whole load: complex III goes from
0.005 to 9.25, cytochrome c oxidase from 0.003 to 4.63, and growth falls from 0.1022 to 0.0659
at 40 °C. So the chain is **functional and bypassed**, not broken.

That is a reconstruction repair. It changes predicted growth by a third, it is not in the
published iRV973, and adopting it inside a prompt about membrane area would change two things
at once and make every downstream number unattributable.

**Decided:** run it, report it, label it a diagnostic, adopt nothing. It goes to
`docs/OPEN_ITEMS.md` as work in its own right, and TASK 3 reports the area constraint against
the models **as they stand**, with the uncoupled variant as a labelled sensitivity so a reader
can see what the mechanism would do in a repaired model.

## D4 — the defect is in the published reconstruction, checked, not inferred

**Where:** TASK 1.

Read directly from `$CANDIDAS_ROOT/gem/models/auris_iRV973.xml` (read-only), the published
iRV973 before any re-keying: the same eleven carriers, the same
`R02161__mito` proton direction and the same non-electrogenic `R11945`. So this is a property
of the published reconstruction and not something the K1 port or the RefSeq re-keying
introduced. Stated that way in the report, because "the model we built has a defect" and "the
model we were given has a defect" are different claims and only the second is true.
