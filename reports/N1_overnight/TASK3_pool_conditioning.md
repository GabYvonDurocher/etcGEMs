# TASK 3 — the pool row's conditioning

_N1 TASK 3. K2 PART D established that the pool constraint is badly scaled at the cold end,
that GLPK returns a wrong growth rate there, and that rescaling makes GLPK agree with
Gurobi. This measures the conditioning per strain, implements the rescaling behind an
option that is **off by default**, and reports what does and does not change._

Produced by `reports/N1_overnight/task3_conditioning.py` →
`task3_conditioning.csv`, `task3_rescaled_comparison.csv`.

## What was implemented

`provider.rescale_pool_row` (default `false`). When on, `set_temperature` divides every pool
coefficient **and the pool bound** by the same constant — the median coefficient at that
temperature, recomputed per solve because the conditioning is temperature-dependent. That is
a mathematically identical LP with a well-conditioned row: it changes no optimum, only the
arithmetic used to find it.

`set_temperature` also now records the row's condition number (`ec._row_cond`) on every
solve, whether or not rescaling is on, so the diagnostic is available for free.

**It refuses to run with proteome sectors wired**, raising a clear error rather than
silently doing half the job: the sector layer writes the pool bound in `set_allocation` and,
under the growth law, adds a v_bio coefficient to the pool row, neither of which this
rescaling reaches. That is why the demonstration below uses ladder rungs B0 and B3, the two
without sectors.

## Condition number of the pool row (max/min coefficient)

| experiment | strain | 22 °C | 26 °C | 30 °C | 34 °C | 38 °C | 44 °C |
|---|---|---|---|---|---|---|---|
| B0 `transfer_candida` | *C. auris* | 2.15e10 | 2.55e10 | 2.22e10 | 2.79e09 | 3.50e08 | 2.20e07 |
| | *C. haemulonii* | 2.55e09 | 7.42e08 | 2.16e08 | 6.22e07 | 1.78e07 | 2.67e06 |
| | *C. duobushaemulonii* | **7.74e11** | 1.90e11 | 2.92e10 | 4.50e09 | 6.95e08 | 4.25e07 |
| | *C. parapsilosis* | 2.92e10 | 6.12e09 | 1.27e09 | 2.64e08 | 5.40e07 | 4.88e06 |
| B3 `candida_B3_ngamT` | *C. auris* | 1.28e09 | 2.85e08 | 6.63e07 | 1.60e07 | 4.00e06 | 5.33e05 |
| | *C. haemulonii* | 1.38e08 | 4.94e07 | 1.82e07 | 6.87e06 | 2.66e06 | 1.60e06 |
| | *C. duobushaemulonii* | 8.18e08 | 2.41e08 | 7.34e07 | 2.30e07 | 7.46e06 | 2.65e06 |
| | *C. parapsilosis* | 6.65e09 | 1.75e09 | 4.77e08 | 1.35e08 | 3.92e07 | 6.53e06 |

The conditioning is worst at the cold end and worst under the phenomenological form, peaking
at **7.7 × 10¹¹** for *C. duobushaemulonii* at 22 °C. It improves by 3–5 orders of magnitude
across the sweep, which is why the disagreements are all at the bottom of the temperature
range: the 1e-6 activity floor puts a handful of enzymes that far above the median cost, and
it does so most when every enzyme is far from its optimum.

## What moves

48 (experiment, strain, temperature) points, growth in model units:

| comparison | max \|difference\| | n > 1e-9 |
|---|---|---|
| GLPK − Gurobi, as-is | 1.117e-03 | **10** |
| GLPK − Gurobi, both rescaled | 1.106e-03 | **1** |
| **Gurobi rescaled − Gurobi as-is** | **1.499e-14** | **0** |

Two things follow. **Gurobi does not move**: 1.5e-14 over 24 points confirms that the
rescaled LP really is the same LP, so the option is safe. And **rescaling fixes 9 of GLPK's
10 errors**, all of them at 22–30 °C.

### The one that survives, arbitrated

`candida_B3_ngamT` / *C. auris* / 22 °C:

| | µ (model units) | error against exact |
|---|---|---|
| Gurobi | 0.0128335203 | −3.8e-13 |
| Gurobi, rescaled | 0.0128335203 | −3.8e-13 |
| **GLPK** | **0.0139506667** | **+1.117e-03 (+8.7%)** |
| **GLPK, rescaled** | **0.0139392658** | **+1.106e-03 (+8.6%)** |
| `glpk_exact` (rational arithmetic) | 0.0128335203 | 0 |

GLPK's own exact rational solver agrees with Gurobi, so **Gurobi is right and GLPK is wrong
by 8.7% at this point** — and rescaling barely helps. Rescaling is therefore a *partial
mitigation for GLPK*, not a cure; the fix that works everywhere tested is using Gurobi,
which is what the Candida strains have defaulted to since K2. Note also that this point is
much worse than the ~0.5% K2 measured: K2 compared at the ladder's own grid, and this is a
colder, harder point on a rung K2 did not sample there.

## Why the default is OFF, and the tension that creates

**K1's gate reproduces the standalone exactly, including the ~0.4% error the standalone's own
solver made** at the cold end of the two draft models. A better-conditioned port does not
reproduce that error, and so cannot pass the gate on those points.

The gate was not loosened and the numbers were not edited. Instead the option is off by
default, so:

* every committed output is unchanged — verified below;
* the gate still passes 79/79;
* the rescaled result exists as a separate, labelled run
  (`task3_rescaled_comparison.csv`).

**Fidelity to the standalone and numerical correctness are now different configurations of
the same code.** Which should eventually be canonical is a decision for a human, not for
this prompt. Recorded in `DECISIONS.md` as **D8, needing review**.

## Confirmation that default-OFF changes nothing

| check | result |
|---|---|
| `etcgem tpc --strain eciML1515`, all three files vs the pre-K1 baseline | **IDENTICAL** |
| `etcgem tpc --strain mmaripaludis`, all three files vs the pre-K1 baseline | **IDENTICAL** |
| all seven Candida `transfer` experiments re-run | no content change |
| both `fba` pool-binding runs re-run | growth unchanged; see note |
| K1's gate, from the fixture | **79/79 PASS, exit 0** |

*Note.* Re-running the two `fba` experiments refreshed their recorded
`resolved_config.yaml` with `ngam_reaction` and `ngam_base_scale` — two keys added to the
strain files in K2 PART A, after those two output folders were last written. Both are inert
in those runs (`ngam_temperature` is off), `fba_result.json` is byte-identical, and no
number moves. The refresh is committed so the recorded config matches the `strain.yaml` it
was run from; see `DECISIONS.md` D9.

## What a human should decide

Whether the canonical Candida configuration should be
`rescale_pool_row: true` with the gate's affected points re-baselined against the *correct*
values, or `false` as now with exact fidelity to the standalone. The evidence for the first
is that Gurobi and `glpk_exact` agree and GLPK does not; the evidence for the second is that
K1's whole claim is exact reproduction, and re-baselining a gate is a thing that should
happen deliberately and once. **This prompt does not have the standing to choose.**
