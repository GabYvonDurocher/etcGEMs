# P10 — decisions

Standing rules carry over. Branch `p10/respiration-likelihood` from `main` after the P9 merge; no
push to `main`; end in a PR that is not merged. Interpreter `../etcGEMs-venv`. Both changes are
core options, default OFF; nothing else about the model, the other priors, the data or `c_max`
changes. Exit codes checked explicitly.

---

## D0 — TASK 0: what the respiration term is today, read from the code, and why `disc_resp` did not absorb the cliffs

PR #24 merged server-side clean → `4bdaf18`; `p10/respiration-likelihood`; baseline gates on
the venv recorded in the report.

**The term, from `gasflux_log_likelihood` (calibration_multi.py):**

* *Quantity.* Per temperature, the model's **O2 uptake** at the growth optimum, converted to a
  per-cell rate — `o2_uptake × gdw_per_cell × 32/60 × resp_scale` — against the measured
  `R_O2_mg_cell_min` averaged over replicates. Not RQ, not CO2.
* *Scale.* **Logarithmic**: `(log obs − log pred)²`. Already log.
* *Mask.* Only temperatures where the model is alive (growth ≥ 1e-4) and consuming O2 (> 0)
  are scored; dead temperatures contribute nothing to this term.
* *Variance, per temperature.* `var_T = rel_T² + disc_resp²`, where `rel_T` is the measured
  replicate sd divided by the mean (30 % where the sd is missing, `load_respirometry`) and
  `disc_resp` is one fitted scale shared by all temperatures, prior half-normal(0.5) on the
  natural value, bounds [1e-3, 3], sampled in log space. Both rel and disc_resp are relative,
  i.e. sds of log respiration. The term is `−½ Σ_T [(log obs − log pred)² / var_T + log 2π var_T]`.
* *At P4's MAP*: `disc_resp` = **0.220**, `resp_scale` = 3.63; the measured relative sds are
  **0.057 at 20 °C and 0.087 at 25 °C** (0.06–0.38 elsewhere), so `var` at the cold points is
  ≈ 0.05.

**How O2 is obtained:** one LP per temperature, growth as the objective (`slim_optimize`), O2
read off the returned vertex (`EX_o2_e_REV − EX_o2_e`), Gurobi with cobra's settings —
**Method 0, primal simplex**, FeasibilityTol/OptimalityTol 1e-7 (P9 read them back). No
tie-break of any kind.

**Why the existing discrepancy did not absorb the cliffs.** It is on the right scale (log) and
its prior is not too narrow — a half-normal(0.5) costs only 2 units at `disc_resp` = 1. The
arithmetic of P9's three decomposed jumps says what actually happens
(`reports/P9_surface/task2_attribution.csv`, recomputed here with the term's own formula):

| jump | T | log residual before → after | Δ log O2 | var at the MAP's disc_resp 0.22 | term step | step if disc_resp were 0.5 / 0.7 / 1.0 |
|---|---|---|---|---|---|---|
| dCp_scale +0.90→+0.95 sd | 25 °C | +2.05 → +3.47 | 1.42 | 0.056 | **−70.2** | −15.2 / −7.9 / −3.9 |
| random1 +0.95→+1.00 sd | 20 °C | +1.77 → +2.53 | 0.76 | 0.052 | **−31.6** | −6.4 / −3.3 / −1.6 |
| PC2 −1.00→−0.95 sd | 20 °C | +2.32 → +1.73 | 0.59 | 0.052 | **+23.1** | +4.7 / +2.4 / +1.2 |

Three things multiply. (1) At the cliffs the cold points already carry a **standing residual
of +1.8 to +2.3 in log** — at those θ the model respires 6–10× less than measured at 20–25 °C,
where the model is nearly dead (growth 0.01–0.13) and the measurement is not. (2) The
measurement's relative sd there is **0.06–0.09**, the smallest of any temperature, so the
term's variance is set almost entirely by `disc_resp`. (3) The LP's optimal O2 at those
temperatures moves by a **factor 1.8–4.1 (0.6–1.4 in log) across one 0.05 sd step** — a vertex
switch, unique at each end (P9). The step in a quadratic term is ½(2rΔ + Δ²)/var: with r ≈ 2,
Δ ≈ 1.4 and var ≈ 0.056 that is 70. `disc_resp` cannot rescue it: it is one scale shared by
twelve temperatures, ten of which the model fits within their own `rel`, and at the MAP itself
the cold residuals are small — the chain sets it to 0.22 where the MAP is, and it is the moves
*away* from the MAP that meet both a large residual and a vertex jump. A fitted scale describes
the residuals where the chain sits; it cannot know about the model's granularity where the
chain would go, and it is that granularity — how far O2 jumps between adjacent LP vertices —
that the term's variance must honour if a 0.05 sd move is not to cost 70 units.

**So the minimal change that follows from this reading is not a second discrepancy term and not
a new prior: it is a floor on the log-O2 sd, added in quadrature, set to the model's own vertex
granularity** — `var_T = rel_T² + disc_resp² + floor²` — with the floor derived from the
distribution of |Δ log O2| across the 0.05 sd steps at P9's cliffs (TASK 2), fixed, not fitted,
and default 0 so that nothing moves with it off. The prior on `disc_resp` stays as it is: the
reading says it was never the problem, and TASK 2 reports it before and after unchanged, with
this reason. The tie-break (TASK 1) is the other half: it makes E/F's O2 a function of θ at all,
and on D it does not remove vertex switches — a pFBA solution is piecewise too — which is why
the floor is needed as well.
