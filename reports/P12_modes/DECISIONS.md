# P12 — decisions

Standing rules carry over. Branch `p12/modes` from `main` after the P11 merge; no push to `main`;
end in a PR that is not merged. Interpreter `../etcGEMs-venv`. The likelihood is P10's with both
options ON for eciML1515 (tie-break pfba at 1e-9, log-O2 floor 1.42, continuous support 0.01),
read from the strain config; **nothing about the likelihood or the priors changes here**. No
sampler is run. Exit codes checked explicitly.

---

## D0 — which of R1–R4 this run can move, and the first thing the decomposition says

PR #26 merged server-side → `9af3184`; `p12/modes` branched; gates with the options OFF
recorded in the report. **The user's uncommitted edit to `docs/OPEN_ITEMS.md` — sections 0a
(R1–R4), 0b (the sequence) and 0c (the reconciliation rule) — was present in the working tree and
is committed as this branch's first commit, untouched**, before any analysis. This run appends
to those sections; it does not rewrite them.

**Against R1–R4, read from 0a before running anything:**

* **R1 (statistically reliable)** — this run **moves it**, and only in the sense 0a already
  allows: it supplies the basin map that decides *what kind* of sampling is needed. It cannot by
  itself produce a posterior two runs agree on, because it runs no sampler. Its deliverable is
  the licence for the next run, with a cost.
* **R3 (right for the right reason)** — this run **informs it** and cannot close it. If the
  basins are what 0a suspects — "shift enzyme optima **or** shift stability, differently
  compensated" — then the map states the alternatives in the model's own parameters and says how
  far apart they are. Discriminating them needs the per-enzyme data 0a names (temperature-dependent
  kcat on the Topt side; the meltome is already held on the Tm side). A basin with `dTm` near zero
  would bear directly on 0b's step 2, the dTm decision, and that is the single most valuable thing
  this map could contain.
* **R2 (identified)** — **untouched.** The five flat parameters are flat because the data do not
  constrain them; a basin map does not add data. If a parameter that P11 called flat turns out to
  separate basins, that is a statement about the *surface*, not about identifiability, and will be
  said that way.
* **R4 (predictively reliable)** — **untouched.** No holdout is involved.

## D1 — theta_B is the seed-2 *median*, and at that point the model is nearly dead; the seed-2 MAP is carried alongside it

**Where:** TASK 0, on reading the decomposition.

The prompt defines theta_B as P11's seed-2 posterior median, and that is what is used. But the
decomposition shows what that point is: **at theta_B the model barely grows at any temperature**
— predicted growth 0.000–0.163 h⁻¹ against measured 0.094–2.076 — and its log-likelihood is
−34.96 against theta_A's −10.42. The seed-2 run's *best* sample is −9.11 (P11), so its posterior
contains good points; its **median** does not sit near them. A median is a coordinate-wise
summary and in a spread or skewed posterior it need not lie in a region of high density at all.

That matters for TASK 1: a line from A to B may be a line from a good point to a poor one rather
than a line between two basins, and a valley on it would prove nothing about mode structure.
**Decided:** report the prompt's A→B line as specified, and carry **theta_B\*, the seed-2 run's
maximum-likelihood sample**, as a second representative of that run, with the same three profiles.
The basin map in TASK 2 is what actually settles the question, and it includes A, B, B\* and P4 as
starts.

Recorded also because it qualifies P11's own comparison: the fifteen-of-sixteen median
disagreement is real, but "the medians differ" and "the modes differ" are not the same statement,
and TASK 2 is what distinguishes them.

## D2 — the evaluation profile inverts Pettersen & Almaas's, so their 8.5× route does not apply here

**Where:** TASK 0.

One evaluation of this likelihood is **2.06 s**, split **92 % LP solve / 8 % model preparation**
(growth LP 1.07 s, tie-break LP 0.81 s, `apply_state` 0.16 s, medium 0.003 s, carbon cap 0.007 s,
flux reads 0.001 s). Pettersen & Almaas measured the reverse — 0.8 % of their time in
optimisation, the rest in COBRApy model preparation — and got 8.5× by moving to ReFramed
(their Table 1). **That lever is worth at most 8 % here and is not recommended.** The lever that
exists is the LP itself: the pfba tie-break is a second LP costing 0.81 s, 39 % of the total, and
it is the price of a likelihood that is a function of its parameters (P10). Recommendations,
not acted on: warm-start the tie-break LP from the growth solve's basis rather than re-solving
from scratch; or solve the two objectives lexicographically in one Gurobi call, which is exactly
what Pettersen & Almaas propose for their chemostat instability. Both are changes to the
evaluation path and belong in their own run with their own verification.

## D3 — the line profiles say A and B are separated by a valley, but A and B* are not

TASK 1's six line scans (`task1_profiles.csv`, `task1_valleys.json`) put a genuine barrier between
theta_A and theta_B: the log-likelihood dips to -35.58 at t=0.88, +0.62 below the lower endpoint,
and P4->B dips +1.10 below its lower end. Those are VALLEYS by the rule written before the scan
(a dip strictly below the lower endpoint by more than the 0.02 evaluation jitter P5 measured).

But A -> B* — the second seed's MAP rather than its median — is MONOTONE, with no dip at all, and
B* is *better* than A (-9.11 against -10.42; -9.07 at t=0.93 on the extended line). So along this
one line the two seeds' best points are not separated by anything.

Judgement: this does not settle whether the seeds found different modes, and TASK 1 is not the
instrument that can settle it. A single straight line finding no barrier is weak evidence of a
shared basin: two basins can be connected along one chord and separated along another, and a
monotone chord is exactly what a long curved ridge would also produce. The claim "seed 2's mode
lies inside seed 1's basin" therefore waits for TASK 2, whose local optimisations follow the
surface rather than a chord, and whose clustering is the actual test. What TASK 1 establishes is
narrower and still worth having: the seed-2 MEDIAN sits in a region separated from A by a real
barrier, which is why the two runs' medians disagreed on 15 of 16 parameters, and the seed-2
MEDIAN is not a good point of the posterior at all (-34.96, nearly dead). A median between two
modes is a point in neither.

Consequence for the report: the 6.8-sigma log Z disagreement in P11 is not necessarily two
different modes. It may be one mode explored to different depths. TASK 2 decides.
