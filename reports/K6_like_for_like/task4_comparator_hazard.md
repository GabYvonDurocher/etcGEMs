# K6 TASK 4 — the comparator hazard, and where else it lurks

Recorded as a standing hazard in `docs/OPEN_ITEMS.md` §4. **This is the second time a comparison
in this project has been made against the wrong version of a measured quantity**; the first was
Parsa's NLDM CSV predating its own medium change.

**The rule.** When comparing a model to data, fit both sides over the same window with the same
functional form, and state in the report which measured source was used.

---

## The quantities that have more than one measured value

Every one of these is legitimately multi-valued. The hazard is not that the data are wrong; it
is that two numbers with the same name answer different questions.

| quantity | spread | why they differ |
|---|---|---|
| **E_growth** | **4.6×** — 0.194, 0.732, 0.901 eV for *C. auris* clade I | straight Arrhenius over all temperatures; the same fit on the rising limb; hierarchical Sharpe-Schoolfield with the collapse modelled. The first is **negative for three isolates**, which is the tell. |
| **E_resp** | 1.45× — 0.518, 0.454, 0.654, 0.545 eV for the same clade | published Bayesian Arrhenius (and the OLS, which agrees); equilibration-corrected; term-free; Sharpe-Schoolfield with `Eh` at its bound. Three of them are in `bayes_resp_arr_E_three_treatments.csv`. |
| **the measured growth TPC** | 0.000 vs 0.66–0.83 /h at 40–44 °C | `measured_tpc_honest.csv` counts a dead well as an **observed zero**; `derived_N0_R_results_with_carbon.csv` keeps only valid fits, i.e. the survivors. |
| **T_opt** | up to 2 °C | `strain.yaml`'s `measured_Topt_C`, the argmax of `measured_tpc.csv`, and the Bayesian `growth_Topt_C`. |
| **per-cell respiration** | ~6× | the cell-mass constants (`OPEN_ITEMS` 1.9). |

## The one that matters most, and is not the one K5 tripped on

**The measured growth TPC has two conventions, and every *Candida* strain in this repository
calibrates against one of them while every activation-energy analysis uses the other.**

`gem/17_build_measured_tpc.py` states the choice explicitly and gives a good reason for it: a
dead well produces a flat oxygen trace that cannot be fitted, and the file it replaced silently
dropped temperatures where everything died, so a dead well is recorded as an **observed zero**.
That is the right convention for "the relatives stop growing at 40 °C", which is the phenomenon
this whole line of work exists to explain.

It is the wrong convention for anything fitted on a log scale, because zeros cannot be logged —
which is why the Arrhenius and Bayesian fits use the survivors-only table instead.

So at 40 °C, *C. haemulonii* grows at **0.000 /h** by the calibration target and at
**0.66 /h** by the fitting table. Both are correct. **Mixing them in one comparison is the
trap**, and it is a larger one than the E_growth case because the two files are used routinely,
side by side, throughout the project.

*K6's own comparisons use the survivors table on both sides, as the manuscript does, and the
zeros table is never used for a slope.*

## What was checked and found clean

* **Growth rate units.** `measured_tpc.csv`'s `mu` and the derived table's `r` differ by a
  constant 59.5× across every temperature where both are non-zero — they are the same quantity
  per hour and per minute. Not a discrepancy.
* **CUE** has five tables but they are a posterior, a by-isolate summary, a by-clade summary, a
  quadratic fit and an uncertainty band, i.e. one analysis at five levels. No competing values
  were found, and CUE is not used in any model-data comparison in this repository.

## Nothing was fixed

Per the prompt, this task reports. No measured file was edited, no strain configuration changed,
and the multi-valued quantities remain multi-valued, which is correct: each version answers its
own question.
