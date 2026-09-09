# Y1 PART B — the coupling-ion audit on the published yeast etcGEM

**The defect class does not fire.** The proton circuit in Li et al.'s ecYeast7 is closed through
the respiratory chain, and there is no free route back into the energised compartment — not in one
step, and not in any number of steps. Four independent checks agree, and the negative is stated
below with the evidence beneath it rather than as an absence of hits.

Before any of this could be trusted, a fault in **our own audit** had to be found and fixed: it
was blind to the Yeast7 naming convention and returned a clean bill of health for the wrong
reason. That is `DECISIONS.md` §3, and the regression evidence is in
`task0_k5_budget_recheck.csv` and `task0_classes_AD_recheck.json`.

Scripts: `task_b_coupling_audit.py`, `task_b2_verifications.py`, `task_b3_free_proton_path.py`,
`task_b4_what_etcpy_constrains.py`.

---

## 1. The coupling ion and the energised compartment, inferred rather than assumed

Inferred from the model's own ATP synthase, as K5 did for the methanogen (which turned out to be
sodium-driven):

* **Ion: H⁺.** **Energised compartment: the cytosol (`c`).** **De-energised: the mitochondrion
  (`m`).**
* **ATP synthase: `r_0226No1`** — `ADP[m] + 3 H⁺[c] + Pi[m] → ATP[m] + 2 H⁺[m] + H₂O[m]`, enzyme-
  costed against seventeen `prot_*` subunits. Not arm-split, so both halves of the reaction are
  in one row.

Note the orientation. In a mitochondrial model the energised side is the *cytosol*, which is also
where bulk metabolism happens, so protons appearing there chemically are ordinary chemistry rather
than the chain. The budget below is therefore read as the **translocated** fraction, which is the
quantity K5 measured for the seven strains and the one that is comparable across them.

A name-based search would not have found this reaction: searching for "ATP synthase" in this model
returns only the cytosolic V-ATPases (`arm_r_0227`, `r_0227No1/2`, `r_1085No1`, `r_1086No1`).

## 2. The proton budget, at the states where ATP synthase actually runs

| state | µ (h⁻¹) | ATP synthase draw | chain, translocated | carriers | **chain supplies** |
|---|---|---|---|---|---|
| `batch_pristine` (deposited `ecYeast7_v1.0_batch.mat`) | 0.097023 | 19.753 | 18.320 | 0.021 | **92.74 %** |
| `aerobic_chemostat` (their `simulate_chomostat`, D = 0.1, 30 °C, σ = 0.5) | 0.1 (fixed) | 22.599 | 21.051 | 0.022 | **93.15 %** |
| `aerobic_pristine` (glucose unlimited) | 0.865388 | **0** | 32.006 | 0.188 | undefined |
| `aerobic_etcpy_30C` (σ = 0.5) | 0.377602 | **0** | 13.966 | 0.082 | undefined |
| `anaerobic_etcpy_30C` | 0.330907 | **0** | 0 | 0.072 | undefined |

The three undefined rows are not a failure of the audit. On unlimited glucose under a protein-pool
cap the model **ferments** — which is the Crabtree effect their paper is largely about — and ATP
synthase carries no flux at all, so the budget is 0/0. The two respiratory states are the ones
that bear on the question, and both put the chain at **93 %**.

The ~7 % remainder is protons released by cytosolic chemistry, which on the mitochondrial
orientation is metabolism rather than a shortcut (`redox_in_compartment` 7.02 at the chemostat
state). Carriers supply **0.1 %**.

**Against K5's seven strains** (`task0_k5_budget_recheck.csv`), where the same quantity reads:
E. coli 123.7 %, *M. maripaludis* 104.7 %, *C. parapsilosis* 112.0 %, *Synechocystis* 18.6 %
translocated but 100 % once in-lumen chemistry is counted, and the three Candida models that K4
found broken: **0.05 %, 0.05 %, 0.04 %**. Yeast at 93 % sits with the healthy models, four orders
of magnitude away from the broken ones.

## 3. The costed / reversible classification, applied as K5's criterion requires

K5 established that the separating feature is **reversibility, not uncostedness**: E. coli has
twelve uncosted proton-movers and is fine because none of them is reversible.

That criterion needs restating for a GECKO model. GECKO writes every reaction irreversibly and
supplies a `_REV` twin where the reconstruction allowed both directions, so `lb < 0 < ub` is
**false by construction** — in ecYeast7, in eciML1515, in any of them. Applied literally the
criterion would return "clean" for a structural reason. The meaningful form is: **uncosted, with
an uncosted `_REV` twin**. Both readings are reported.

Every reaction that moves a proton across the mitochondrial membrane (`task_b2_mito_proton_census.csv`):

| | count |
|---|---|
| reactions moving H⁺ between `m` and `c` | **15** |
| of those, **uncosted** | **12** |
| uncosted ones that deliver H⁺ **to** the energised side | **0** |
| uncosted ones with an uncosted `_REV` twin | **0** |
| costed ones delivering H⁺ to the energised side | **2** (`r_0438No1`, `r_0439No1` — the chain) |

All twelve uncosted ones run the **dissipative** way, cytosol → mitochondrion: the proton leak
(`r_2129`), phosphate/H⁺ symport (`r_1245`, flux 5.88), pyruvate/H⁺ (`r_2034`, 0.36),
ornithine/H⁺ (`r_1237`, 0.02), oxaloacetate/H⁺, CTP, UTP, GTP, D-lactate and arginine carriers.
None of them has a reverse twin. **Nothing free returns a proton to the cytosol.**

The model does contain free reversible proton movers — 98 of them, 49 forward/`_REV` pairs
(`task_b2_free_proton_pairs.csv`): the amino-acid and nucleotide H⁺ symporters at the plasma
membrane, and "H⁺ diffusion" between the cytosol and the ER, Golgi, peroxisome, nucleus, vacuole
and lipid particle. **Not one of them touches the mitochondrial membrane.** They move protons
between compartments neither of which is energised, so they cannot substitute for the chain.

## 4. There is no free path, of any length

A pairwise census is not sufficient on this model, because it has a separate `mm` (mitochondrial
membrane) compartment and an uncosted reversible pair `r_3957`/`r_3957_REV` moving protons between
`m` and `mm`. Two such steps in series would be a free bypass that no pairwise test would see.

So the question was asked as reachability (`task_b3_free_proton_path.py`): build a directed graph
on compartments whose edges are uncosted proton-moving reactions, ATP synthase excluded, and look
for a path from `m` to `c`.

* 153 proton-moving edges, **149 of them uncosted**.
* Path `m → c` using **uncosted edges only: NONE**, at any length.
* Path `m → c` using every edge but ATP synthase: `r_0438No1` — the costed chain, and only that.
* Path `c → m` using uncosted edges only: exists (e.g. `r_1130`), as it should — dissipation is
  free, energisation is not.

## 5. The three verifications the prompt requires, reported although the audit did not fire

**(1) Reproduced from the pristine downloaded model.** `batch_pristine` and `aerobic_pristine` are
the deposited `.mat` files with nothing altered — no medium change, no closure, no pinning. The
load shim is verified exact against the raw MATLAB struct (`task_a_load.md` §2). The result is the
same in the pristine states as in the treated ones.

**(2) The reactions carry meaningful flux — and the ones that would matter carry none.** At the
chemostat state ATP synthase carries 7.53, the chain carries 11.09 and 5.54, oxygen uptake is
2.78. The uncosted proton movers that carry flux all run dissipatively (5.88, 0.36, 0.02). The
free reversible H⁺ diffusions carry 0.06 (`r_1825_REV`, cytosol↔ER) and 3×10⁻⁵ — and they are not
on the energised membrane in any case. **There is no latent hazard to describe either**, because
§4 shows no free route exists even unused.

**(3) Their own code does not constrain anything our loading path misses — and does not need to.**
Diffing the model against itself across `map_fNT`, `map_kcatT`, `set_NGAMT` and `set_sigma` at
30 °C, σ = 0.5 (`task_b4_etcpy_diff.csv`): their layer changes **3925 of 6743 reactions**, but
**only two bounds** — `NGAM` (0.7 → 1.683834, pinned) and `prot_pool_exchange` (0.17866 →
0.08933). Everything else is a stoichiometric coefficient on `prot_pool`, which is how GECKO
expresses enzyme cost. **No transporter is bounded by their thermal layer.** The one uncosted
proton-moving reaction it touches is NGAM itself.

## 6. Two stress tests, because a negative should be pushed on

**The counterfactual** (`task_b2_counterfactual.csv`). Block the two costed chain translocators and
re-solve. At the chemostat state, where growth is pinned at the dilution rate, the model goes
**infeasible** — the circuit cannot be closed any other way. With growth free, maximum ATP synthase
flux falls from 35.411 to 13.623; auditing that forced state shows the residue is supplied by
**costed** cytosolic chemistry (GAPDH, pyruvate carboxylase, hexokinase, all paid for out of the
protein pool), with `redox_translocated` and `carrier_translocated` both **exactly 0**. Nothing
uncosted supplies the energised compartment even when the LP is told to try.

**The energy-generating-cycle test.** Shut every exchange except the protein pool — no glucose, no
oxygen, no secretion, maintenance released — and ask the model to make ATP from nothing:

* maximum ATP synthase flux: **0**
* maximum ATP hydrolysis through NGAM: **0**

Both exactly zero. The model cannot generate free energy from nothing.

## 7. Classes A–D, for completeness

`task_b_classes_AD.csv`, identical across all four states (they differ only in bounds and
coefficients, not in structure): 6743 reactions, 4003 costed, 2740 uncosted; **A = 53** uncosted
reactions that can produce ATP/NAD(P)H/quinol/ferredoxin, **B = 0** reversible maintenance,
**C = 1** hard-pinned uncosted drain (NGAM, which is maintenance and is meant to be pinned),
**D = 13** uncosted consumers of a terminal electron acceptor.

For scale: the three Candida models K4 found broken report **44–47** class-A hits, and E. coli
reports 10. Yeast's 53 is the largest count in the family — and it is exactly the point K5 made
when it wrote class E: **the class-A count says nothing about whether the coupling circuit is
intact.** Here the count is high and the circuit is sound.

## 8. What this does and does not say

It says: the specific defect this project found — an uncosted, reversible route that lets the ion
gradient close around the respiratory chain — **is not present in the published yeast etcGEM**,
under four independent tests, in the pristine deposit and under their own thermal layer.

It does not say their reconstruction is free of every modelling artefact; nothing here looked for
any other kind. And it does not touch their conclusions, which this audit has no bearing on either
way.
