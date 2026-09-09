# P10 — fix the respiration likelihood: a tie-break for the faces, a variance the model can honour for the kinks

@@STATUS@@

Detail: [DECISIONS.md](DECISIONS.md) (D0–@@DLAST@@). Scripts beside this file: `task1_check.py`,
`task1_d3a.py` (→ `task1_d3a.csv`, `task1_elb_face.csv`, `task1_cost.csv`), `lines.py`
(→ `lines_<tag>.csv`, `lines_<tag>_summary.csv` for `baseline`, `tiebreak`, `variance`, `both`),
`task2_floor.py` (→ `task2_floor.json`, `task2_jumps.csv`), `task4_regate.py`
(→ `task4_regate.csv`), `task4_candida_pfba.py` (→ `task4_candida_pfba.csv`), `run_fit.py`,
`task5_table.py`.

---

## TASK 0 — the term as it is (D0)

PR #24 merged → `4bdaf18`; `p10/respiration-likelihood`; `../etcGEMs-venv`; **baseline gates
79/79 and 60/60**, seven strains byte-identical.

**The term, from the code** (D0, in full there). Per temperature, the model's O2 uptake at the
growth optimum, converted to a per-cell rate through `gdw_per_cell × 32/60 × resp_scale`,
against the measured per-cell rate, **on a log scale**, over the temperatures where the model
is alive (growth ≥ 1e-4 and O2 > 0), with variance `rel_T² + disc_resp²` — `rel_T` the measured
replicate sd over mean (0.057 at 20 °C, 0.087 at 25 °C, up to 0.38), `disc_resp` one fitted
scale shared by all temperatures, prior half-normal(0.5) on [1e-3, 3]. O2 is read off the vertex
of a single growth-objective solve, Gurobi primal simplex at 1e-7.

**Why `disc_resp` did not absorb the cliffs.** Not the scale (log, right) and not the prior (a
half-normal(0.5) costs 2 units at 1.0). Three things multiply at P9's cliffs: a standing cold
residual of +1.8 to +2.3 in log (the model respires 6–10× less than measured at 20–25 °C, where
it is nearly dead and the culture is not); the measurement's smallest relative sd (0.06–0.09),
so the variance there is `disc_resp` alone; and an O2 vertex switch of 0.6–1.4 in log across one
0.05 sd step. ½(2rΔ + Δ²)/var with r ≈ 2, Δ ≈ 1.4, var ≈ 0.056 is 70. `disc_resp` is set to 0.22
where the chain sits, where the cold residuals are small; it is the moves away from the MAP that
meet both a large residual and a vertex jump, and a fitted scale cannot know the model's
granularity where the chain would go. So the minimal change is a **floor at the model's own
granularity, in quadrature** — not a second discrepancy term, not a new prior.

## TASK 1 — the tie-break

`flux_tpc(..., tiebreak="none" | "pfba" | "min_o2" | "max_o2", growth_tol=1e-6, tiebreak_tol=1e-9)`,
default `none`; the likelihood reads the option from `gas_exchange.respiration`; every other
caller (the `etcgem gasflux` outputs, the P1/P3 gate scripts) keeps the default. **Seven-strain
gate with the option OFF: 79/79, byte-identical** (only the two stale FBA dumps §4 records).
Turned ON for eciML1515 only.

Two things the sketch needed (D1): the parsimonious objective is built directly rather than
through cobra's `add_pfba`, whose exact re-pin of growth is basis-fragile on the LB models; and
every solve in a tie-broken call runs at **1e-9** optimality/feasibility, because at 1e-7 the
parsimonious optimum on the LB models is flat enough in O2 that vertices within tolerance differ
two- to four-fold (with growth and total flux both pinned, the O2 is a point; successive
tolerance-level solves returned 8.9, 10.0, 12.8 at 30 °C on E LB).

**The D3a instrument under pfba** (`task1_d3a.csv`; one reused model θ, θ; θ, θ′, θ; models
rebuilt fresh):

| fit | none: reuse θ,θ / θ,θ′,θ | **pfba** | s per evaluation, none → pfba |
|---|---|---|---|
| D NLDM | 0.0000 / 0.0000 | **0.0000 / 0.0000** | 0.43 → 1.87 |
| D LB | 0.0000 / 0.0000 | **0.0000 / 0.0000** | 0.26 → 1.81 |
| E NLDM | 0.5153 / 0.5153 | **0.0000 / 0.0000** | 0.67 → 2.22 |
| E LB | 2.4978 / 2.4992 | **0.0000 / 0.0000** | 0.39 → 2.34 |
| F NLDM | 0.0000 / 0.0000 | **0.0000 / 0.0000** | 0.50 → 2.24 |
| **F LB** | 2.3530 / 2.3530 | **0.0525 / 0.5055** | 0.48 → 2.33 |

Five of six cells are 0.0000. **F LB is not, and TASK 1 STOPS on that cell** as the prompt
requires: on that model the parsimonious optimum at 1e-9 still leaves a residual freedom in
O2 (0.05–0.5 units between calls, down from 2.35). F LB stays held.

**Where pfba lands on the E LB face at Parsa's θ**, O2 at 37 / 40 / 45 / 50 °C: none 38.12 /
46.66 / 40.71 / 28.49; **pfba 38.07 / 46.60 / 40.71 / 28.49**; min_o2 38.07 / 46.60 / 40.70 /
28.48; max_o2 38.24 / 46.66 / 40.74 / 28.49 — at *his* θ the face is 0.17 wide and pfba sits at
its low end; the [0, 190] face of P6 D3a is at P4's MAP θ. **Cost:** 0.45 → 2.0 s per likelihood
evaluation, single process (×4.5; the prompt estimated ×2).

## TASK 2 — the variance

**The cliffs have two mechanisms** (D2; `task2_jumps.csv`, from a re-run of P9's twelve ROUGH
lines with per-temperature O2 recorded — P9 reproduced line for line): of 33 steps with
|ΔlogL| > 5, **17 are O2 vertex jumps** (|Δ log O2| median 0.47, max 1.42; 14 of them at 20 °C,
3 at 25 °C) and **13 are flips of the term's own support** — a temperature entering or leaving
the hard mask `growth ≥ 1e-4 & O2 > 0` at 15 or 47–50 °C, taking its whole residual and
log-variance with it at ±16–18 units (f_maint, ngam_scale and clearance_mult's cliffs are all
this) — and 3 are growth-term steps. P9's instrument recorded only the log-likelihood and saw
the first mechanism.

**The two minimal changes**, both options default OFF, ON for eciML1515 (`gas_exchange.respiration`):

* **`log_o2_floor` = 0.76**, in quadrature: `var_T = rel_T² + disc_resp² + 0.76²`. Rule fixed
  before the number was read: the largest |Δ log O2| across a 0.05 sd step among the O2-carried
  cliffs at the temperature carrying most of them — 20 °C, 14 of 17, where the median is 0.44
  and the maximum **0.759** (`task2_floor.json`, source `lines_baseline.csv`). The one larger
  jump (1.42 at 25 °C, dCp_scale at +0.9 sd) is left to cost what it costs.
* **`alive_soft_growth` = 0.01 h⁻¹**: a temperature's contribution weighted by min(1, g/0.01),
  continuous, equal to 1 wherever the model grows faster than 0.01 (the peak is 1.6), instead
  of the switch at 1e-4.

**The prior on `disc_resp` is unchanged** — half-normal(0.5) on [1e-3, 3] before and after —
for D0's reason. **The arithmetic on P9's three decomposed jumps, same θ, old → new:**
dCp_scale at 25 °C **−70.2 → −6.2**; random1 at 20 °C **−31.6 → −2.6**; PC2 at 20 °C
**+23.1 → +1.9**. Single digits. Gate with the change OFF: 79/79 (the same run as TASK 1's;
both options are in the same block and both default off).

## TASK 3 — is the surface smooth now?

@@TASK3@@

## TASK 4 — the gate, re-read

**The P3 gate at Parsa's θ, O2 at the pfba vertex** (`task4_regate.csv`; his construction, his
media and caps, P3's points):

| config, medium (point) | growth R², none → pfba | respiration R², none → pfba | Δ resp |
|---|---|---|---|
| D NLDM (posterior median) | 0.7066 → 0.7066 | 0.7246 → 0.7246 | -0.0001 |
| D LB (MAP) | 0.8964 → 0.8964 | 0.7931 → 0.7931 | -0.0000 |
| E NLDM (MAP) | 0.8492 → 0.8492 | 0.7214 → 0.7215 | +0.0001 |
| E LB (MAP) | 0.8284 → 0.8284 | 0.8014 → 0.7749 | -0.0265 |
| F NLDM (MAP) | 0.9051 → 0.9051 | 0.9636 → 0.9635 | -0.0001 |
| F LB (MAP) | 0.8809 → 0.8809 | 0.8524 → 0.8518 | -0.0005 |

**Growth R²: unchanged to four decimals, all ten values** — neither half touches the growth
solve. **D respiration: unchanged** (D's O2 was unique). **E and F: the difference is the width
of the face at his θ** — E LB 0.8014 → 0.7749, the others within 0.001 — not a regression; the
old number was one arbitrary point of the face, which at his θ is narrow (0.17 on E LB) and at
P4's MAP is [0, 190]. F LB's row carries D1's caveat (its tie-break is not exact). The restated
criterion is written into `reports/P3_gate/README.md` as a dated note; the gate's history is
not rewritten, and the gate is not re-opened against his numbers.

**The Candida strains, as information only** (`task4_candida_pfba.csv`; K5's construction,
`candida_B5_respire` at 40 °C, the coupling-ion audit run on the plain optimum and on cobra's
pfba solution at the same growth):

| strain | chain_supplies_fraction, plain → pfba | including in-compartment chemistry, plain → pfba |
|---|---|---|
| cauris_iRV973 | 2.000 → 2.000 | 2.789 → 2.787 |
| cduobushaemulonii_draft | 2.133 → 2.133 | 2.682 → 3.231 |
| chaemulonii_draft | 2.722 → 2.722 | 3.246 → 3.529 |
| cparapsilosis_iDC1003 | 1.120 → 1.120 | 1.395 → 1.395 |

The translocation-only fraction is unchanged to three decimals in all four; the "including
chemistry" figure moves for two (*C. haemulonii* 3.25 → 3.53, *C. duobushaemulonii* 2.68 → 3.23),
so pfba does redistribute in-compartment proton chemistry there. Not adopted for any Candida
strain — a K-series decision (OPEN_ITEMS, new PI item). (The audit's `growth` field under pfba
reads the parsimonious objective value, not growth; growth is held at its optimum by
construction.)

## TASK 5 — one fit

@@TASK5@@

## TASK 6 — the record

@@TASK6@@

## Verification

@@VERIFY@@
