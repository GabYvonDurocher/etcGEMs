# P4 — decisions

Standing rules carry over. `$PARSA_ROOT`, `$CANDIDAS_ROOT`, `$ECOLI_R2A`, `$ECOLI_M9` are READ
ONLY. **`strains/c*/` belongs to K4, running in parallel: nothing here touched it, and every
commit staged an explicit path rather than `git add -A`.**

---

## D0 — the RQ stop band was widened, because the prompt's own text contradicts it

**Where:** TASK 1.

The prompt asks for RQ "physiological", cites Parsa's recipe-medium value of **0.46**, and calls
a value "far outside ~0.6–1.3" a stop condition. 0.46 is outside 0.6–1.3. Taken literally the
check would stop on the very number the prompt quotes as the expected result.

**Decided:** stop outside **0.40–1.40**, flag between 0.40 and 0.60. The pre-flight's NLDM values
(0.474) then reproduce Parsa's 0.46 and are reported as a result; a fermentative RQ ≈ 0.02, which
is configuration A's failure mode, still stops.

## D1 — the behavioural pre-flight was re-run at a fitted point, because at the prior centre it says nothing

**Where:** TASK 1.

At `Perturbation()` — no perturbation at all — NLDM looked fermentative (RQ 0.47–0.50) and LB
acetate was zero. The sampler does not stay at the prior centre, so those readings are not
evidence about the configuration. Re-run at the MAP of Parsa's own fit for the same
configuration, every NLDM/LB fit is physiological: RQ 1.11–1.40, acetate 7.1–27.6.

**Decided:** report both points and enforce the checks at the fitted one.

## D2 — M9 carries the carbon cap on configurations E and F, where their NLDM counterparts do not

**Where:** TASK 1, found by the pre-flight.

On NLDM the recipe ceilings limit carbon; on LB the component list does; on `glucose_minimal`
**nothing does** — glucose is open at ub 1000. Without a cap the ETC area budget alone left the
model fermenting: configuration F on M9 gave RQ 0.026 with zero acetate, configuration E gave
growth 3.7e-5.

**Decided:** all three M9 fits carry `c_max = 120`. Recorded because it makes the M9 fits
structurally different from their NLDM counterparts, and because the reason is a property of the
medium mapping rather than of the configurations.

For M9 on E and F the behavioural check itself is **reported but not enforced**: the only
parameter point available is a borrowed NLDM MAP, which is not sensible on glucose-minimal, and
no fitted point exists because fitting M9 is the request. **Samplability was checked instead** —
40 of 40 prior draws give a finite log-likelihood for all three M9 fits (best −5.4, median −65
to −76), so the sampler has a well-defined surface.

## D3 — the warm start failed silently in all nine fits; fixed, not re-run

**Where:** TASK 2.

`_warm_start` calls the module-level `_wnegpost`/`_wlogprob`, which read the globals the
`run()`-family worker initialiser sets. A pool initialised for the gas-flux entry point has
different globals, so every worker raised and scipy surfaced it as an opaque *"map-like callable
must be of the form f(func, iterable)"*. `_warm_start` caught it and fell back to the
emergent-point ball — correct behaviour, but it means **none of the nine chains was warm-started**
and each spent its burn-in walking to the mode.

**Decided:** fix the wiring (`_warm_start` now takes the worker callables; `_gwnegpost` added) so
any future run benefits, and **do not re-run on the strength of it**. Re-running all nine is ~10 h
and would not change the governing conclusion, which is that the chains are too short by a factor
of four regardless of where they start (D4). The fix is committed and untested at scale, and that
is said rather than implied.

## D4 — nothing is quoted from a non-converged chain, including his

**Where:** TASK 3, and it governs the whole report.

All nine refits are non-converged: τ_max 146–245 against 1500–2000 steps, chain/τ ≈ 6–12 against
the ≥40 criterion. Measured with the same estimator, **all six of Parsa's committed chains are
non-converged too** (τ 160–214, chain/τ 8.2–9.4, n_eff 148–170).

**Decided:** report every R² as indicative and quote none as a result — which, applied evenly,
also means the ten values P3 gated and the ones his report prints are point estimates from
unconverged chains. Stated neutrally: it is a sampling-budget property, and the arithmetic fix is
40·τ ≈ 8 000 steps, four times the chain, ≈ 40 h for all nine on this machine. Not run, and the
cost is given so the decision to spend it is a human's.

## D5 — the LB collapse is reported with its candidate cause, and the single run that would settle it is named

**Where:** TASK 3.

All three LB growth R² fall by 0.65–0.72 under the canonical settings, to 0.16–0.20. The LB
medium did not change, so the medium cannot be the cause; `c_max` did, from his fitted values to
120 — and **his own LB fits chose 256.7, 459.3 and 509.9**, all 2–4× higher.

**c_max = 120 is a glucose/NLDM recommendation and P4 over-applied it to LB**: his sweep and the
P2/P3 sensitivity that supported adopting it are computed on glucose-minimal and NLDM only, and
no LB sensitivity was ever run. **Decided:** report it, do not change `c_max` on the strength of
one non-converged fit, and name the run that would settle it — configuration D on LB at
c_max ≈ 260, one fit, ~45 min.

The NLDM movements are **not separable** — medium and cap both changed — and that is said rather
than guessed. The single-change run that would separate them is configuration D on NLDM under the
blanket medium at c_max 120, one fit, ~70 min.
