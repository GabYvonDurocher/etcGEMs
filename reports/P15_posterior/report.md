# P15 — the criterion resolved, and the posterior still not earned

_Run 2026-09-10/11 on `../etcGEMs-venv`, branch `p15/posterior`, from main after PR #30 (P14)
merged._

**Outcome: the sampleability question is closed and the run failed for a different reason.** Run 1
**crashed** after 9.9 h at iteration 11,547 with dlogz 2.168, deterministically, on a degenerate
direction that turns out to be **Y3's non-identified `dTm`/`tm_scale` pair**. Run 2 was not started.
No posterior is quoted.

---

## TASK 0 — the 1.23 resolution, recorded before anything ran

PR #30 merged **cleanly** — no conflicts. Verified rather than assumed: `support: clamp` is set in
`strains/eciML1515/gas_exchange.yaml` **and in no other strain config**; the core default is
`current`; gates **79/79** and **60/60**; ten fresh-model evaluations at p38 give **−9.9893897954
ten times, spread 0.0000000000**. **D0 was committed alone**, before any sampler was launched.

### Why lifting the discontinuity conjunct is a correction, not an accommodation

The criterion required no-jumps **and** no-plateaus. The argument that separates them needed no
data. Nested sampling estimates **Z = ∫ L dX**, with **X(λ)** the prior volume where L > λ. Its one
structural requirement is that **L have no atoms under the prior**: an atom makes X(λ) jump and
voids **X_i ≈ exp(−i/nlive)**, which assumes live points uniform in X. **A plateau creates that
atom. A jump does not** — it leaves a *gap* in L's support, X flat over an interval of λ carrying no
prior mass, no live point ever there, and **Z = Σ L_i w_i remains a valid Riemann sum in X**.

Then the measurements: **0 of 480** adjacent evaluations exactly equal, so no atoms; the four real
jumps are **0.145–0.885 units**, against the **1–3 unit** growth-term kinks P11 accepted as
irreducible and which no respiration change touches. So even 1.22 would leave larger discontinuities
in place from another term — it is a **cost optimisation for the remaining eight fits, not a
correctness fix**.

**P14 was right to refuse to lift this itself.** The criterion was its own and its data had been
seen; a run that moves its own goalposts after a failing result is worth nothing whether or not the
new position is defensible.

## TASK 1 — the proofs, and then the crash

**All three proofs pass.** Prior transform: deferred to P11's own script, which compares 10,000
draws per parameter against **analytic** means and quantiles — density consistent for every
parameter (max spread 3.55e-14), largest deviation 1.58 MC se, regenerating its committed output
byte-identically. Pool vs single-process at p38: **max |difference| 0.000e+00**. Checkpoint restore:
stopped at iteration 62, restored at 62.

*(My own first version of the transform check was wrong — it built a "reference" quantile from the
transform of a constant vector, which is not a quantile of anything, and reported a spurious
1.274e-01. Corrected in the script.)*

### Run 1: CRASHED — not converged, and not capped

| | |
|---|---|
| settings | nlive **800**, `rslice` (3 slices), `multi`, dlogz 0.1, seed 1, 16 processes, `first_update={'min_eff':30}` |
| launched | 2026-09-10 22:07 |
| died | 2026-09-11 08:04, **~9.9 h** |
| reached | iteration **11,547**, **180,257** evaluations, eff 6.4 % |
| at failure | **dlogz 2.168**, log Z **−25.730** |
| written | **nothing** — no samples, weights or summary; only the 07:15 checkpoint |

```
RuntimeError: Slice sampler has failed to find a valid point.
nstep_left: -5.4e-323   nstep_right: 5e-323   nstep_hat: 1.04e-322
u_prop == u  (bit-identical)      loglstar: -14.169843617724203
```

Those steps are **denormal doubles — numerically zero**. **This is reported as CRASHED, not
STALLED**: D1's rule covers hitting the 16 h cap, and this did neither that nor converge. The three
outcomes license different next steps and are not interchangeable.

### The cause, from the checkpoint's own live points

Covariance of the 800 live points **in the unit cube**, which is where `rslice` works:

| smallest eigenvalues | λ | √λ | dominant loadings |
|---|---|---|---|
| 1 | **1.947e-04** | 1.395e-02 | **`dTm` +0.903**, `sigma` +0.274, **`tm_scale` −0.217** |
| 2 | 6.305e-04 | 2.511e-02 | `dTopt` −0.625, `resp_scale` −0.560 |
| 3 | 7.880e-04 | 2.807e-02 | `sigma` −0.816, `kcat_scale` −0.313 |

Largest eigenvalue 0.2835; **condition number 1,457**. **`corr(dTm, tm_scale) = +0.831`** among live
points, that 2×2 block conditioned at 49.3.

**This is Y3's non-identified pair, confirmed by a wholly independent route.** Y3 found it by
profiling the likelihood; here the *sampler's own live points* collapse onto the same correlation as
the constraint tightens. It also explains the **1,124 divide-by-zero warnings** from
`bounding.py:273` (`1./l1` with a zero eigenvalue) — the bounding ellipsoid was singular for hours
before the slice sampler finally failed.

**What it is not:** `dTm` is the **most tightly constrained** parameter (live sd 0.0506 against the
prior's 0.289). This is a thin **correlated ridge**, not a plateau — consistent with P14's census
finding no plateaus at all. The sampleability verdict stands; the geometry defeated the sampler.

**R2 surfacing, as D1 said it would:** `f_metab` 0.273, `dCp_scale` 0.266 and `f_maint` 0.265 sit
essentially **at their priors** (0.289) among the live points.

### The resume, and a correction to my own record

Run 1 was resumed from its checkpoint **with identical settings**, to test whether the failure was
deterministic. I reported at the time that it was not, because the resume started and kept running.
**That was wrong.** It died after 50 minutes with **bit-identical** state — same `u`, same
`loglstar` −14.169843617724203, same denormal steps — having completed **zero** progress chunks.
dynesty restores its `rstate`, so the resume replays the same draws and fails the same way. **Run 1
is terminal at iteration 11,547.** The correction is recorded in D3 rather than edited away.

## TASKS 2 and 3 — NOT RUN

Run 2 was not started, per D1 and the prompt. **No posterior, log Z with error, agreement verdict,
`dTm` interval, R² table or 1.17 costing is quoted, because none was computed.** The two predictions
D1 fixed in advance — that the clamp posterior moves away from the `_MASK_G` knife-edge, and that
posterior-predictive growth at 15 °C rises — **remain unevaluated for a third run**, and stand as
written.

## The decision this leaves — the PI's, with a recommendation

The settings were not changed. `rslice` → `rwalk`, fewer `slices`, or a different `bound` would very
probably get past this, but they are **D1 settings fixed before the run**, `rslice` is what **P11**
used so changing it forfeits the comparability that makes an agreement verdict mean anything, and D2
committed in advance that a second crash is reported with the choice left to the PI.

**The recommendation follows from the diagnosis rather than from the traceback.** This is not a
dynesty bug to be worked around; it is the geometry telling the truth. Two redundant knobs on one
axis — `dTm` and `tm_scale`, which Y3 showed are not jointly identified — produce a ridge of
ever-shrinking width, and any sampler that brackets along a direction will eventually fail on it.
`rwalk` would not fail the same way, but it would still be exploring a **degeneracy** rather than a
posterior.

- **(a) Fix `tm_scale` (or `dTm`) at nominal and re-run.** Removes the degenerate direction at
  source, drops to 15 dimensions, and converts an unidentifiability into a stated limitation. This
  is **§0b step 3** and item **1.20**, and it is the recommended route. Same cost as this run.
- **(b) Change the sampler and re-run otherwise unchanged.** Cheapest in thought; samples a known
  degeneracy and forfeits comparability with P11.
- **(c) Both** — (a) as the scientific run, (b) as a robustness check.

## Reconciliation against §0c

- **Which of R1–R4 moved: none closed.** R1's *criterion* is settled and its obstacle is now named
  and measured, but no posterior exists. **R2 moved as a matter of evidence**, in the wrong
  direction and usefully: the degeneracy that killed the run is a *measurement* of
  non-identifiability from the sampler's own live points, independent of Y3's profiling. R3 and R4
  untouched.
- **Retracted or qualified, numbers unedited:** **D2's claim that the crash was stochastic is
  retracted by D3** — it was a weak inference from a 50-minute window. **P14's discontinuity
  conjunct is retired** with the argument that predates its data.
- **What this does NOT license:** quoting any posterior or log Z; unblocking 1.17; or concluding
  that the likelihood is unsampleable — it has **no plateaus**, and the failure was a
  sampler-geometry interaction, not an atom.
