# Y2 — decisions and judgement calls

Kept from the first judgement call, per the prompt.

---

## 1. Three files in the BayesianGEM clone look modified, and nothing modified them

TASK 0 asks for `git status` clean in Y1's clone. It is not:

```
 M validate_smc_abc/figures/Case2_ga.pdf
 M validate_smc_abc/figures/Case2_smc_abc_classic.pdf
 M validate_smc_abc/figures/Case2_smc_abc_this_work.pdf
```

**The cause is the deposit, not us.** The repository contains three pairs of files whose names
differ only in case — `case2_ga.pdf` and `Case2_ga.pdf`, and likewise for the other two. macOS's
filesystem is case-insensitive, so it can hold only one of each pair; git checks out both, the
second overwrites the first, and git then reports a difference it cannot resolve.
`git ls-files | tr A-Z a-z | sort | uniq -d` returns exactly those three names and nothing else.

**Decision: proceed, and record why.** The clone is at `a68307e`, the right commit. Everything Y2
reads is untouched — `git status models data code` is empty — and the three affected files are
validation figures for the SMC-ABC toy models, which Y2 does not read. Checksums of the three files
Y2 does read are in `SOURCE.md`.

## 2. Their `GEMS.py` needs sklearn, which this environment does not have

`GEMS.format_input` is the function that turns a posterior particle into a thermal-parameter
table, and it is theirs. Importing `GEMS` to get it pulls in `sklearn.metrics` at module level.

**Decision: stub `sklearn.metrics` with the two functions GEMS imports, rather than copy
`format_input` into our own file.** `mean_squared_error` and `r2_score` are used only to print fit
statistics inside `aerobic()`, `anaerobic()` and `chemostat()`, none of which Y2 calls; the stub
implements them correctly anyway so that if anything ever does call them the numbers are right.
Copying `format_input` would have been re-implementation by another name, and it is exactly the
function whose fidelity matters most here.

## 3. The sweep is amortised across the four settings, and the amortisation is verified

Y1 called `etc.simulate_growth` once per (setting, temperature). The expensive part — `map_fNT`
and `map_kcatT` over 764 enzymes — is identical across settings that differ only in a bound, and
Y2 repeats the whole test at a hundred parameter sets.

**Decision: apply their four calls once per temperature and solve once per glucose cap inside a
nested `with model:` block — and refuse to use any number until the amortisation is shown exact.**
`verify_against_simulate_growth` compares it with `etc.simulate_growth` over the full 61-point
grid; `task2_regime.py` aborts with exit 2 unless the difference is **0.0**. The readouts
(`refine_topt`, `crossing`) are *imported* from Y1's script rather than copied, so the 99 %
plateau and the 1 %-of-maximum CT_max cannot drift between the two reports.

## 4. Which objects are "the prior" and "the posterior"

Their `abc_etc.SMCABC` object carries several populations. `population_t0` is the first generation
(n = 128) and `population` is the final one (n = 100) — matching the paper's own "n = 128 for
Prior and n = 100 for Posterior" (Fig. 2a–c caption), and `visualization.ipynb` uses exactly that
pair to draw the prior/posterior comparisons.

**Decision: use those two, and prove it with the SD cross-check rather than by argument.** The
paper reports average per-enzyme SDs prior → posterior of Topt 10.9 → 7.1 °C, Tm 4.9 → 4.0 °C,
ΔCp‡ 2.0 → 1.8 kJ/mol/K (Supplementary Fig. 7). These populations give **10.92 → 7.16**,
**4.90 → 4.01** and **2.00 → 1.79**. Three parameters, six numbers, all inside a rounding step of
the published values. That is the file.

## 5. Y1's "prior" is a third object again, so all three are run

Y1 PART C ran at `data/model_enzyme_params.csv` — the **point** prior table, one value per
enzyme — not at a draw from the prior distribution. The posterior analogue of that is the
enzyme-by-enzyme median of the 100 particles.

**Decision: run all of `prior_file`, `prior_median`, `posterior_median`, and draws from both
populations.** Comparing Y1's point prior directly against posterior draws would confound the
prior→posterior move with the point→distribution move. Drawing from the prior as well makes the
comparison like for like, and it is the only way to say whether the posterior *narrows* the effect.

## 6. The glucose lever only, for the draws

Y1 used two levers and was explicit that only one is a regime change: σ scales the enzyme budget
without altering which constraint binds, and Y1 reported that it moves T_opt about as little as it
moves CT_max. The quotable figures — 10.09 °C and 0.81 °C — are the across-setting ranges of the
**glucose** lever.

**Decision: the draws use the four glucose settings, unchanged from Y1.** The σ lever is
reproduced in full by the `prior_file` re-run (TASK 2a), so nothing is lost; repeating a lever
that was already shown not to be a regime change, a hundred times, would only buy wall-clock.

## 7. `${PIPESTATUS[0]}` is empty in zsh, and nearly cost an exit-code check

A verification wrote `cmd | grep ...; echo "EXIT=${PIPESTATUS[0]}"` and printed `EXIT=` — zsh
spells it `$pipestatus[1]`, and the check silently reported nothing at all. This is the same class
of defect as the `cmd && check` rule already in the standing rules: a verification that cannot
fail is not a verification.

**Decision: no pipes in exit-code checks.** Redirect to a file, capture `$?` on the bare command,
then read the file. Every exit code in this report is captured that way.
