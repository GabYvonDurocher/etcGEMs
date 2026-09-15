# T2 — the approved target revision implemented, validated against the signed protocol: R1 stays open, and the blocker has a name

_2026-09-13 → 2026-09-15, branch `t2/validated-posterior` from main `fe35aac` (the merge of T1's #40),
worktree `../etcGEMs-t2`. Decisions D0–D11 in `DECISIONS.md`; state in `status.json`; the
detached driver's route in `launch_status.md`. **Verdict: R1 OPEN — NOT PASSED for the programme.
No posterior is quoted.** The approved revision itself is implemented, gated and verified and is
not the cause._

## The decisions executed (D0)

1.29 f_metab removal — ON for eciML1515 (`calibration.remove_inactive: [f_metab]`); 1.30 −∞ for
structural infeasibility — ON (`respiration.infeasible: zero_lik`); 1.31 curvature — nothing
applied; 1.32 protocol — signed with the (d) amendment, frozen as `docs/VALIDATION_PROTOCOL.md`.
Both options are core options, default OFF (`gasflux.py`: `UnresolvedSolve`, `_ladder`,
`flux_tpc(stop_on_infeasible, retry_ladder)`; `calibration_multi.py`: the option and the
strain-config `calibration` block). Registered before anything ran: coldest-first short-circuit
order, the three-rung retry ladder (rung 2 corrected to the solver's floor, D3), the 876-point
audit set at 1e-6, seeds 17901–17905 to runs 1–5, 16 h / 72 h alarms, P16's sampler settings,
dynesty's −∞ accounting.

## Gates and instruments (D1, D2, D4, D6)

- Seven-strain gate with both options OFF, on the patched code: **79/79, 60/60, byte-identical**
  (path-only `resolved_config.yaml` diffs). P3 gate with both ON: `gate_def_table.csv`
  **byte-identical**; Parsa's D NLDM θ `optimal` at all twelve measured temperatures.
- Invariant at all 876 T1 audit points: **13 feasible unchanged to 9.6e-08 (tolerance 1e-6); 863
  at −∞; 0 unresolved** — exactly as predicted in D0. Datum table: 7 rows −∞ with all 73 formerly
  unscored measurements accounted for; 6 feasible rows within 1.85e-9 (four miss the 1e-9 bar by
  ≤ 0.85e-9; reported, not moved). Short-circuit: 50/50 identical verdicts, 77 of 600 solves saved.
- **Prior rejection rate — item 1.33: 16.45 %, Wilson 95 % [14.9 %, 18.1 %]**, firing at 15 °C in
  326 of 329 cases (47 °C once, 50 °C twice); 636 of 1,671 feasible draws living (~32 % of the
  prior). The prompt's "~96 %" described P16's live points at iteration 6800, not the prior: the
  dead stratum held 81.5 % of posterior weight from ~16 % of prior volume.
- Diagnostic coordinates: the `Perturbation` the model receives is **identical at 100/100 points**
  with and without them (the exact test, D5/D6; config hashes `85da50e9…` / `fe223870…`). The
  log L residuals (median 4e-11; one 0.028 event) are same-instance solver history — the first
  sighting of the blocker below.

## The driver and its runs (D7, D8, D9, D-driver)

`run_protocol.py`: idempotent, sequential, self-auditing, self-stopping, checkpointed (30 min),
detachable, alarmed. Dry run on P17's smooth toy: audits PASS; a run killed at iteration 1810
resumed from its checkpoint and finished **bit-identical** to an uninterrupted control. Launched
2026-09-13 22:42:33 (pid 83007), ten-minute check passed.

| run | seed | iterations | evaluations | wall | evals s⁻¹ | log Z | n_eff | audit | rejection (d) |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 17901 | 15,277 | 235,542 | 11.22 h | 5.83 | −27.707 ± 0.110 | 10,400 | PASS | 16.10 % |
| 2 | 17902 | 13,465 | 206,277 | 13.39 h | 4.28 | −28.047 ± 0.100 | 7,899 | PASS | 14.50 % |
| 3 | 17903 | 9,288 at the last checkpoint | 136,647 | 7.07 h | — | (−28.33 running) | — | **CRASH** at 07:45 on the 15th | 13.70 % |
| 4, 5 | 17904, 17905 | not started | | | | | | | |

The driver's run-1 projection (finish 2026-09-16 06:55) was already behind at D9: 11–13.4 h per
run against P16's 8–9.6 h (4.3–5.8 evals s⁻¹, not 6.4–6.9).

## The crash, diagnosed (D10, D11)

dynesty: *"Slice sampler has failed to find a valid point"* with the bracket collapsed to 1e-323.
The failing `u` **is live point 654 of run 3's checkpoint**, stored at log L −18.480 above loglstar
−19.163; re-evaluated **fresh on three model instances it is −19.760854009581777 every time**
(warm, three calls: the same to 5e-8) — **1.281 units below its stored value and 0.6 below the
threshold**. All 800 live points of each checkpoint re-evaluated fresh in a pool: run 3 carries
**four** such points at +1.279 to +1.281 (one warm-worker evaluation and its slice descendants),
all with true values below the current loglstar; run 1 one point at +4.8e-3; run 2 none above
1e-3. The crash is mechanical and deterministic: no slice step from a point whose true value is
below the threshold can succeed. No solve was UNRESOLVED; no −∞ point was involved; the ladder
and the approved revision are not implicated. P15's crash (dlogz 2.17) has the same signature.

Live-point geometry (P15's treatment, for the record): runs 1 and 2 end with tm_scale widths
0.0069 and 0.0175 — **the posterior rails tm_scale against the upper edge of its prior mass**
(median u 0.994, tm_scale ≈ 1.46; the 2.2 truncation is not reached). A finding for the PI (Y3's
tail question), not a T2 decision.

## The six checks on the two complete runs — information only (D11, `task5_checks.json`)

(f) audits re-derived PASS (log Z to 0.0, weights ≤ 1e-13, cube 5.6e-16); **log Z disagree** (Δ 0.340
vs combined 0.149). (a) run 1 PASS (0.044), run 2 **FAIL** (0.088). (b) **FAIL both**: b³ distance
0.259 / 0.119 against ≤ 0.05 — the Beta(3,1) positive control on a provably inert coordinate is
not recovered. (c) **14 of 14 physical medians disagree** beyond 2 MC errors (dTopt 0.33 vs −1.62 K;
disc_growth 65 MC errors); leading eigenvectors min |cos| 0.013 **FAIL**; widths PASS. (d) **PASS
both** (16.10 %, 14.50 % within 2 SE of 16.45 %; 0 posterior samples infeasible anywhere; living
0.986 / 0.976 by construction — the dead stratum is excluded, not occupied). (e) unresolved 0,
unscored 0, respiration 11/12, **growth 8/12 FAIL both** — at 35–43 °C the measured peak (2.076 /h
at 40 °C) lies above the predictive 97.5 % (≈ 1.62 /h): the model under-predicts the warm-side
peak by ~25 % calibrated (E5: 2.3× uncalibrated), a scientific finding distinct from the sampling
failure.

## Verdict, and what it licenses

**R1 OPEN.** The blocker: *the gas-flux likelihood as evaluated in a persistent pool worker is not
a deterministic function of θ — the tie-broken LP returns path-dependent vertices at the 1e-3 to
1.3 log-likelihood level at posterior points — so nested sampling's ordering is violated; one run
crashed on it and the two that finished do not agree.* Not fixed here (RIGOUR 9/10): candidate
remedies for the PI — a fresh model per evaluation (measured 6.7 s per build against ~1.9 s per
evaluation, i.e. a ~4–5× cost), a solver-state reset per call, or a tie-break proven
state-independent at every temperature (P10 D1 already found F LB's was not) — are each a new
registration. A validated D NLDM posterior would license nothing about E, F, M9 or another
organism; an unvalidated one licenses nothing at all. The reserved seeds 17901–17903 are consumed;
17904–17905 are not.

## Corrections made by dated addition

D3: rung 2's "1e-12" is unsettable (Gurobi floor 1e-9); T1's ladder ran rung 2 at the model's
existing tolerances, its classification unaffected. D5: the first diagnostics instrument compared
two model instances; replaced by the exact test. D9: the run-1 projection was behind by run 2.
