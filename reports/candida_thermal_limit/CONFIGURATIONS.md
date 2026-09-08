# The two configurations, and which one you are in

_N2 TASK 2. One sentence if you read nothing else: **fidelity to the original implementation
and numerical correctness are now different things, and K1's gate tests the first while
everything else uses the second.**_

## Why there are two

The proteome-pool constraint is badly scaled at the cold end. The 1e-6 activity floor puts a
handful of enzymes many orders of magnitude above the median cost, so at 22 °C the row's
coefficients span up to **7.7 × 10¹¹** (N1 TASK 3, `reports/N1_overnight/TASK3_pool_conditioning.md`).

On a row that badly conditioned, GLPK returns a wrong answer — up to **8.7% wrong** at the
worst point. That is established rather than asserted: **Gurobi and GLPK's own exact rational
solver (`glpk_exact`) agree**, GLPK's floating-point answer does not, and tightening Gurobi's
tolerances moves it by 4 × 10⁻¹³.

Dividing every pool coefficient **and the pool bound** by the same constant gives a
mathematically identical, well-conditioned LP. It changes no optimum, only the arithmetic
used to find it — Gurobi's answers move by at most 1.5 × 10⁻¹⁴.

**But K1's gate must not have it.** The gate's job is to reproduce the standalone Candida
etcGEM *exactly*, and the standalone's numbers at the cold end of the two draft models
contain that ~0.4% GLPK error. A better-conditioned port does not reproduce the error, and so
cannot reproduce those numbers. That job is historical and finished — the standalone's values
are frozen in `standalone_expected.json` — so it gets its own configuration rather than
holding back everything else.

## The two configurations

| | `rescale_pool_row` | used by | what it is for |
|---|---|---|---|
| **normal use** (the default) | **true** | everything: `etcgem tpc`, `etcgem transfer`, ladder rungs B1–B4, any new work | the correct answer |
| **legacy fidelity** | **false** | `transfer_candida`, `transfer_candida_unpinned`, `candida_pool_unconstrained`, `candida_pool_binding` — i.e. the four experiments K1's gate reads, which are also ladder rung B0 | reproducing the standalone, error included |

Each of those four experiment files carries the key with the reason written beside it.

### One automatic exception

Rescaling is **not supported with proteome sectors wired**: the sector layer writes the pool
bound in `set_allocation` and, under the growth law, adds a `v_bio` coefficient to the pool
row, neither of which the rescaling reaches. Since the default is now on, a *default* must
not break a configuration that was working — so with sectors enabled it reverts to off and
says so on stdout. An **explicit** `rescale_pool_row: true` with sectors still raises, because
that is a request the code cannot honour.

In practice this affects ladder rung B4 and *M. maripaludis*. *E. coli* and *Synechocystis*
are unaffected for a different reason: they build through `from_gecko`, which does not carry
this option at all.

## What flipping the default actually changed

Every numeric quantity in every Candida `transfer` run, before and after
(`reports/N2_followups/task2_what_moves.csv`):

| rung | quantities that moved | largest absolute change | largest relative change |
|---|---|---|---|
| B0, B0-uncorrected | **0** | — | — (legacy fidelity: unchanged by construction) |
| B1 | 137 | 1.06 × 10⁻¹¹ | 2.2 × 10⁻¹² |
| B1s (sensitivity) | 138 | 8.16 × 10⁻¹² | 1.4 × 10⁻¹² |
| B2 | 125 | 1.99 × 10⁻¹² | 2.9 × 10⁻¹³ |
| B3 | 128 | 2.98 × 10⁻¹³ | 2.3 × 10⁻¹³ |
| B4 | **0** | — | — (sectors: rescaling auto-off) |

**Nothing moved by more than 2 × 10⁻¹² in relative terms.** These runs are on Gurobi, which
was already returning the right answer; the rescaling only removes the *reason* GLPK could
not.

**So no number quoted in any report or in the discussion notes changes at any reported
precision, and no prose needs updating.** That is a result, not an assumption: the comparison
covered every numeric column of every strain in every summary, the fitted globals, the growth
scale, the calibration MSE, and every required separation, and the largest movement anywhere
is in the twelfth decimal place.

The value of the change is therefore not in the current numbers. It is that **the next person
to run this on GLPK, or on a machine without a Gurobi licence, gets the right answer** —
which, before this, they did not.

## Verified

* K1's gate under legacy fidelity, with `$CANDIDAS_ROOT` **unset**: **79/79 PASS, exit 0**.
* *E. coli*, *M. maripaludis* and *Synechocystis* nominal TPCs: **byte-identical** under the
  new default (confirmed by re-running, not assumed).
