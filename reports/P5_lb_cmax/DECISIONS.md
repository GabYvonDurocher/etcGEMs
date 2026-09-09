# P5 — decisions

Standing rules carry over. `$PARSA_ROOT` and `$CANDIDAS_ROOT` are READ ONLY; TASK 0 is the only
write to `main`; branch `p5/lb-cmax`, ending in a PR that is not merged. Exit codes checked
explicitly throughout.

---

## D0 — the stamps were refreshed on `main` inside TASK 0, and the primary checkout's stray stamp was discarded

**Where:** TASK 0, before the first gate ran.

`p4/refit` was one commit stale against its own stamps at its HEAD: `stamp_reports.py --check`
on the committed `1c39f79` reported `P4_refit` and `ecoli_gasflux` stale, because "P4: summary"
was committed after the last stamp run. The primary checkout also held an **uncommitted**
regeneration of `reports/ecoli_gasflux/PROVENANCE.md` (stamped at `d73370f`), which is the
same lag one step earlier. After the merge a third stamp, `K5_respire`, went stale too, because
that report reads an *E. coli* output P4 touched.

**Decided:** treat the refresh as TASK 0 bookkeeping — one commit on `main` (`4863d61`)
regenerating the three stamps, made before any gate ran, so that the "stamps pass" verification
is of the merged tree and not of a tree that had just been patched by hand. The stray working
copy was saved to the scratchpad and discarded (`git stash`, then dropped) rather than committed,
because it was generated at the wrong commit. Precedent: every K-run since K5 has needed a
stamp-refresh commit for the same reason.

## D1 — two stale FBA config dumps found by the byte-identity check; recorded, not regenerated

**Where:** TASK 0, both batteries.

Re-running the K1 gate's two `etcgem fba` commands changes
`strains/cauris_iRV973/outputs/fba_candida_pool_{binding,unconstrained}/resolved_config.yaml`
by exactly one line each: `rescale_pool_row: false` appears. Every numeric output in both
directories reproduces byte-identically; the gate passes 79/79. The key was added to the
config dump by N2's hotfix (`a467d23`), and those two directories were last written at N1 TASK 3
(`217581e`), before it — so they have been stale on `main` since the N2 merge, through K4–K9,
and every TASK 0 that reported "seven strains byte-identical" was true of the transfer and TPC
outputs it re-ran and silent about these two, which the batteries did not re-run. It is the
hazard this prompt's TASK 3 asks to record, met on the way: a field added to a record, and a
check that does not read that field. It is also the second instance of OPEN_ITEMS 3.15's
family (a `resolved_config.yaml` diff that is not a numeric change), and 3.15's absolute-path
artefact is exactly what would have hidden it from a worktree.

**Decided:** do NOT regenerate the two files. VERIFY 6 forbids committed-output changes beyond
the new LB fit directory, the numbers are unchanged, and a one-key config-dump refresh belongs
in a housekeeping commit that says so. Recorded in `docs/OPEN_ITEMS.md` §4 under the new
hazard, with the two paths, so the next byte-identity run knows to expect it and the next
housekeeping run knows to clear it. The working tree was restored before each merge.

The same battery also caught, transiently, the exact regression TASK 3 describes: at
`main + P4` (before K9 landed) the two Candida transfers rewrote
`outputs/transfer_candida*/calibration.json` with `"fixed": {}` — K8's unconditional field, which
K9 TASK 0 fixed. After the K9 merge the same commands leave `outputs/` clean. So the fix is
verified on `main` by the second battery, not assumed from K9's report.

## D2 — the fit runs at c_max = 257, not 260

**Where:** TASK 1, before the sampler started.

The prompt asks for "≈ 260, justified from his own fits". Read at source from his chains
(`task1_parsa_lb_cmax.py`), configuration D on LB is `230 × C_max_LB_mult`: **256.7 at the MAP**,
267.0 at the posterior median. The MAP is the point P3's gate reproduced his 0.90 at, and it is
the point P4 scored its D_LB refit at. **Decided: 257.** It makes the fit differ from P4's D_LB in
one number (the cap, 120 → 257) and from his D_LB in the medium convention and in the cap being
fixed rather than sampled — nothing else. 260 or 267 would have been defensible and would not
change the conclusion; 257 is the one that is *his*.

Two things read at source that the P4 report did not say, recorded here so the value is not
over-read:

* his three LB caps are **fitted multipliers of 1.02–1.13 on his own nominal** (230 for D, 450
  for E and F; lognormal prior sd 0.40 centred on 1). The posterior barely moved from the prior
  centre. So "his LB fits chose 257 / 459 / 510" is true and weak: the data did not pull the cap
  away from wherever he centred it, and D's 257 differs from E's 459 mainly because he centred
  them differently;
* the E LB value his figure quotes comes from `configE_LB_freecmax` (459.3 at the MAP, **353.9**
  at the median); the sibling run `configE_LB` then **pins** it at 459.0. F's `configF_LB`
  gives 509.9 at the MAP and 391.6 at the median.

The one fit is therefore a test of *whether the cap is the cause of the LB collapse*, and if it
is, of whether a cap in the region of his nominal recovers his fit. It is not an LB sensitivity
and will not be presented as one.

## D3 — the chain was trapped in a dead mode by the warm start, so the question is answered at fixed points instead

**Where:** TASK 1, on reading the fit's scores.

The fit ran to completion (2000 × 40, 156 min — three times P4's 46 min for the same settings,
because one worker's slow solves serialised the ensemble) and scored **growth R² −2.19, r_max
0.0002, T_opt 54.5 °C, acetate and RQ undefined**: the MAP predicts zero growth at every
temperature. That is not a statement about `c_max`. Evaluating the chain: 97 % of walkers sit at
`disc_growth` > 1 in the **first** 250-step block and 100 % thereafter; the median log-posterior
is −40.8 → −38.7 over the run, against −27.4 for P4's D_LB at c_max 120; `dTopt` sits at 13
against a prior edge of 15. The walkers were seeded there: P4's warm-start repair worked as
wired this time (P4 D3 said it was untested at scale), and its short differential evolution
(`maxiter=12, popsize=4` — 12 generations of 60) returned the **dead mode** (−logpost 37.6), a
local optimum where growth ≡ 0 and the growth discrepancy term absorbs the data. Every walker
started in a tight ball around it and none crossed to the growing region in 2000 steps. P4's
nine chains, whose warm start silently failed, started from the emergent-point ball instead and
found growing solutions. So the repair has now been tested once at scale and, on this
likelihood, it did harm.

Meanwhile P3's gate already contains the deterministic version of the run this prompt asked
for: **Parsa's D_LB MAP, scored in OUR configuration-D LB model at his cap 256.7, gives growth
R² 0.896** (`reports/P3_gate/gate_def_headline.csv`). A growing high-R² solution therefore
exists at c_max ≈ 257 in this model; the sampler failed to find it, not the model.

**Decided:**

* keep the chain as a record (`calibration_configD_LB_recipe_cmax257/`, `lb_cmax_comparison.csv`)
  and quote nothing from it except that it is trapped — it is not re-run, because a second
  2.5 h chain would test the warm start, not `c_max`, and TASK 1 is about `c_max`;
* answer the question **at fixed parameter points, without a sampler** (`task1c_fixed_point.py`):
  his D_LB MAP and P4's D_LB MAP, each scored identically at c_max 120 and 257, plus a local
  optimisation of the log-posterior from each start at each cap so that "the best growing-mode
  fit at each cap" is compared like for like. Fixed points are exact and cheap; a chain at ~9 τ
  is neither, and P4's own D_LB value is itself a single chain's MAP;
* record the warm-start failure as a new open item with a trigger, because P6 is about to spend
  ~40 h on nine chains with this warm start switched on.

## D4 — the canonical LB cap is set, at 450 rather than 257, from the fixed-point evidence

**Where:** TASK 1, after task1c–1e.

The prompt allows "set nothing" if one fit cannot choose. One fit could not (D3). But the
deterministic checks can, and they say more than the fit would have:

| cap | D growth / resp R² | E | F | best of the caps tried? |
|---|---|---|---|---|
| 120 (P4) | 0.64 / 0.40 at his point; best posterior found 0.26 / 0.94 | 0.05 / 0.50 | −0.10 / 0.41 | no |
| 257 (his D value; the prompt's ≈ 260) | 0.89 / 0.83 re-optimised | 0.77 / 0.42 | 0.89 / 0.63 | D only |
| 450 (his E/F nominal) | 0.90 / 0.78, log-posterior −7.7 (best) | 0.83 / 0.86 fixed, 0.89 / 0.40 re-opt | 0.90 / 0.85, −11.4 (best) | all three |

**`c_max` is confirmed as the cause** of the LB collapse: the same parameter vector, scored the
same way, changes only with the cap, and the mechanism is visible — the measured LB peak is
2.94 h⁻¹ and a 120 mmol C gDW⁻¹ h⁻¹ cap holds r_max at 1.1–1.8 whatever the parameters, so on
LB the cap binds where on NLDM (peak ≈ 1.6) it does not.

**Decided: `by_medium.LB = 450`** in `strains/eciML1515/gas_exchange.yaml`, with the provenance
and the scope of the 120 written beside both numbers. Reasons, in order: it is *his* number
(the nominal his E and F LB fits were centred on, and within 13 % of all three fitted values);
D's growth is on its plateau there (0.895 at 257, 0.898 at 450) and its log-posterior is the
best of the caps tried; E and F reach their gated values there and do not at 257; and P6 is
about to run all three on LB, so a value that serves one configuration and starves two would
be a worse decision than 450 even though 257 is the one this prompt anticipated. Scope, stated
in the file: above 450 nothing has been tested (r_max 2.4–2.7 against 2.94 measured) and no LB
sensitivity to an unbounded cap has been run by anyone — that is the trigger to revisit.

Two things about how it is recorded. It is a **new key** (`carbon_cap.by_medium`), consumed by
the fit runners' explicit `c_max=` arguments and not by `config.apply_gasflux`, which reads the
scalar — so no committed `gasflux_*` output changes, and that is verified by regenerating
`gasflux_configB` and `outputs/tpc` after the edit (the hazard TASK 3 records: re-run the
byte-identity check AFTER the last change). Wiring `apply_gasflux` to read it would move every
committed configuration-B/D LB curve and is not this prompt's to do. And 120 stays as the
scalar because that is what NLDM and glucose-minimal were established on; its comment now says
so.

Caveat carried into the report: for E and F the likelihood re-applies the ETC area constraint
on every evaluation, and Powell returned a worse log-posterior than its start for E at 450
(−17.5 from −14.9), which an optimiser cannot do on a pure function. Checked directly in
`stateful_check` (see the report); the fixed-point R² are what they are, but E/F values are
reproducible only to the extent that check says.
