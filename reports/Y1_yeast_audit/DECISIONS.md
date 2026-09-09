# Y1 — decisions and judgement calls

Every point at which this audit could have gone a different way, with what was chosen and why.
Kept from the first judgement call, per the prompt.

---

## 1. The deposited pickles do not load; the `.mat` files are used instead

`models/aerobic.pkl` and `models/anaerobic.pkl` are cobra 0.15.3 model objects pickled in 2020.
Unpickling under cobra 0.31 fails inside `cobra.Configuration.__setstate__` — first
`AttributeError: 'Configuration' object has no attribute 'problem'`, then, once that is shimmed,
`KeyError: 'tolerances'`. Reviving them means reconstructing a five-year-old private API.

**Decision: stop after two attempts and use the deposited `.mat` files**, which carry the same
models. The prompt caps format archaeology explicitly ("Do not spend more than a few hours on
format conversion"), and there was a working route that does not need it.

**What this costs.** The correspondence between pickle and `.mat` is inferred, not proved: the
anaerobic `.mat` is the aerobic `.mat` with oxygen uptake shut (`r_1992_REV` ub 0 against ∞) and
the same protein pool (0.17866), which is exactly the aerobic/anaerobic distinction their code
draws. Recorded as an inference in `task_a_load.md`.

## 2. The `.mat` load needs a trim, and the trim is verified rather than asserted

Several GECKO fields in the deposit are sized to a subset of the model (909 `genes` against 764
`geneNames`; `rxnECnumbers` and `rxnUniprots` shorter than `rxns`), and cobra zips them against
the full lists and overruns.

**Decision: keep only the fields that define the linear program** plus the identifiers needed to
read it, and drop GECKO's annotation extras — then check what the trim could have broken against
the raw MATLAB struct. `verify_fidelity` compares S, lb, ub, c and the reaction and metabolite id
lists. All three deposited models come back exact: ids identical, `lb`/`ub`/`c` max abs diff 0.0,
`S` non-zeros equal on both sides. See `task_a_load.json`.

## 3. Our own audit was blind to their naming convention — found and fixed before any conclusion

The first run of `audit_coupling_ion` on the yeast model returned `ion: None`, "no ATP synthase
moving a coupling ion was found", and classes A–D returned **zero hits on 6743 reactions**. Both
were wrong. `r_0226No1` is mitochondrial ATP synthase, it carries flux, and the model respires.

The cause is in `src/etcgem/sink_audit.py`, not in their model. Every pattern in that module is
anchored at `^`, and it searched the metabolite id and the joined string `f"{id} {name}"`. BiGG
and ModelSEED put the chemistry in the id (`atp_c`, `cpd00002_c0`), so that works. Yeast7 puts an
opaque id beside a plain chemical name (`s_0437` / `ATP`), and an anchored pattern cannot match
`"s_0437 ATP"` from the left. The audit therefore recognised no ATP, no NADH, no O2 — and read a
model with an intact respiratory chain as perfectly clean.

**Decision: fix the matcher (search the name as its own string) and prove the fix inert on the
seven strains before using it.** Had this not been caught, Y1 would have reported "no defect
found" for the wrong reason — the least useful possible outcome, and one that would have looked
like a result.

**Regression evidence.** `reports/K5_respire/task1_coupling_audit.py` re-run on all seven
strains: **every numeric cell identical, max abs difference 0.0** across the whole class-E
budget, the 354 translocator rows and their `kind` classification
(`task0_k5_budget_recheck.csv`). Classes A–D re-run on all seven: A/B/C/D counts identical to
the committed `reports/candida_thermal_limit/sink_audit_table.csv`
(`task0_classes_AD_recheck.json`).

## 4. A second, incidental fix: the group representative was nondeterministic

While checking (3) the eciML1515 ATP-synthase label moved between runs — `ATPS4rpp_REVNo1` one
run, `ATPS4rpp_REVNo2` the next. `_gecko_groups` keyed each contracted group by union-find's own
representative, which comes from `met.reactions`, a set of objects hashed by identity, so it
varies between processes. Membership, and every number, was identical either way.

**Decision: key each group by its lexicographically smallest member.** A report should not change
its labels when re-run. Verified: three consecutive runs now give the same label; all numbers
unchanged.

## 5. Which state the coupling budget is measured at

The batch states are FERMENTATIVE. On unlimited glucose under a protein-pool cap the model does
what the Crabtree effect says it should, and ATP synthase carries **no flux at all** — so the
proton budget is 0/0 and undefined there. Reporting "nan" would be true and useless.

**Decision: audit five states, and read the budget at the respiratory ones.** The pristine
`ecYeast7_v1.0_batch.mat` (glucose capped at 1) respires, and so does the chemostat, which is
where the paper's respiratory conclusions come from (Fig. 4). The fermentative states are
reported too, with the reason their budget is undefined.

## 6. Their chemostat routine had to be called in place, and the inlining is checked

`etc.simulate_chomostat` runs inside `with model:` blocks and returns only a `Solution`, so the
state it audits cannot be reached from outside. `chemostat_state` performs their own calls, in
their order, in place.

**Decision: call their functions, never re-implement them, and check the equivalence.** The
inlined version reproduces `etc.simulate_chomostat`'s objective to |diff| = 0.000e+00.

## 7. One compatibility shim in their code, and it changes no number

`etc.set_NGAMT` sets `NGAM.lower_bound` then `NGAM.upper_bound`; cobra 0.15.3 tolerated the
intermediate `lb > ub`, cobra 0.31 raises. The shim sets both at once to the value **their**
`etc.getNGAMT` computes. Nothing else in `etcpy` is touched.

## 8. K5's reversibility criterion needs restating for GECKO models

K5 established that the separating feature is reversibility, not uncostedness. But GECKO writes
every reaction irreversibly and supplies a `_REV` twin where the reconstruction allowed both
directions, so `lb < 0 < ub` is **false by construction** in any GECKO model — eciML1515
included. Applied literally, the criterion is vacuous here and would return a clean bill for a
structural reason rather than an evidential one.

**Decision: apply the criterion as "uncosted, with an uncosted `_REV` twin".** That is what
"reversible and free" means in a GECKO model. The census in `task_b2_mito_proton_census.csv`
reports both readings.

## 9. The counterfactual had to be re-posed

Blocking the chain in the chemostat state can only return `infeasible`, because the chemostat
pins growth at the dilution rate. True, but blunt.

**Decision: add two sharper tests.** (i) With growth free, maximise ATP synthase flux with the
costed chain blocked — how much can anything else support? (ii) The energy-generating-cycle test:
shut every exchange except the protein pool and ask the model to make ATP from nothing. Both are
reported.
