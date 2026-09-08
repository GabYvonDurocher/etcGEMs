# K6 — decisions

Standing rules carry over. `$CANDIDAS_ROOT` is READ ONLY. Branched from `main` at **b23cb44**,
the K5 merge. **P4 was still running** (see D1), so `strains/eciML1515/` and `reports/ecoli_*`
are never written.

---

## D0 — TASK 0: the K5 merge verified

PR #8 merged as `b23cb44`, branch deleted local and remote. Exit codes checked explicitly and
never chained:

| check | result |
|---|---|
| Candida gate, `$CANDIDAS_ROOT` unset | **79/79 PASS, exit 0** |
| `stamp_reports.py --check` | **exit 0** (K5 refreshed its own stamp before merging) |
| `transfer_candida`, `candida_B5_respire` re-run | exit 0, no numerical output changed |
| working tree | clean |

Only `resolved_config.yaml` files moved on re-run, and only in their absolute
`provider.model_path`, which is the worktree artefact K5 recorded as `OPEN_ITEMS` 3.15.

## D1 — P4 was still running; nothing under its half was touched

Checked, not assumed. `p4/refit` stood at `b115791` ("P4 TASK 2: refit E_NLDM under the
canonical settings"), four commits ahead of `main` and unmerged, with files written under
`strains/eciML1515/outputs/` within the previous ninety minutes.

## D2 — the prompt's framing was verified before it was used, and it holds

**Where:** TASK 1. The prompt asserts that K5's measured comparator is contaminated. It is not
taken on trust; the fitting code was read and the diagnosis tested empirically.

`scripts/07_oxygen_fits.R`, `fit_arr_lm`: `lm(ln y ~ boltz)` over **every** temperature with
y > 0, no deactivation term, no rising-limb restriction, `EXCLUDE_TEMPS_PLOT` empty.
`scripts/09_bayesian_models.R`, `fit_ss_hier`: hierarchical **Sharpe-Schoolfield**, in which the
high-temperature collapse is carried by its own `Eh` and `Th` so that `E` is the **rising-limb**
activation energy. `fit_arr_hier`, used for respiration: hierarchical **Arrhenius**, no
deactivation term.

**So the two E_growth are not two estimates of one quantity.** One is the slope of a straight
line through a peaked curve; the other is the rising-limb parameter of a peaked model. The test:
refitting the OLS to growth on the rising limb alone moves it from 0.01–0.35 eV to 0.21–0.93 eV,
toward the Bayesian 0.62–1.15, while E_resp is left alone — for *C. duobushaemulonii*, 0.008 →
0.627 against a Bayesian 0.622. **The diagnosis holds.**

## D3 — the rising-limb cut uses the Bayesian optimum, not the raw argmax

**Where:** TASK 1, TASK 2.

A rising-limb fit needs a cut, and the obvious one — the argmax of the measured mean curve — is
unreliable where the hot end is noisy. *C. haemulonii*'s raw argmax lands at 42 °C, above its
own thermal limit, on a mean taken over the few wells still alive; cutting there leaves the
turnover inside the "rising limb" and returns 0.205 eV. Cutting at that group's Bayesian
`growth_Topt_C` of 32.0 °C returns 0.601 eV.

**Decided:** cut at the Bayesian `growth_Topt_C`, which is estimated with the collapse modelled
rather than read off noise, and report the raw-argmax cut beside it so the choice is visible.

## D4 — which measured comparator is appropriate, and why it is not one number

**Where:** TASK 1, TASK 2.

Neither table is "the" measured value. The appropriate comparator depends on the quantity:

* **E_growth** — the rising-limb value, whether from the Bayesian Sharpe-Schoolfield fit or an
  OLS restricted to the rising limb. The full-range OLS is a different quantity and is not
  comparable to a model whose curve turns over elsewhere.
* **E_resp** — the full-range Arrhenius value. Respiration does not turn over, the two sources
  agree on it to three decimals for *C. auris* clade I (0.518 both), and truncating it to the
  growth optimum throws away the hot end where the signal is.

That asymmetry is not a fudge; it is what the manuscript itself does, and
`bayes_E_resp_minus_growth.csv` is the difference of exactly those two.
