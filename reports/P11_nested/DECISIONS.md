# P11 — decisions

Standing rules carry over. Branch `p11/nested` from `main` after the P10 merge; no push to
`main`; end in a PR that is not merged. Interpreter `../etcGEMs-venv`. Two decisions are
**executed, not revisited**: the respiration floor moves to the largest measured vertex jump,
and the growth term is not floored. Exit codes checked explicitly.

---

## D0 — TASK 0: the floor moves 0.76 → 1.42, and the absolute smoothness rule, both written before the re-scan

PR #25 merged server-side clean → `97411f1`; `p11/nested` branched; gates on
`../etcGEMs-venv` with the options OFF recorded in the report.

**The floor.** P10 set `log_o2_floor` = **0.76** by a rule that took the largest |Δ log O2| at
the *modal* cliff temperature (20 °C, 14 of the 17 O2-carried cliff steps; largest there 0.759).
The largest measured vertex jump **anywhere** in that scan is **1.4216**, on the `axis:dCp_scale`
line between +0.90 and +0.95 sd, carried by **25 °C**, and it is the step that still cost 7.8
units under the 0.76 floor and left the surface ROUGH (P10 D5, `task2_jumps.csv`). The prompt's
first decision is to move the floor to that number: **`log_o2_floor` 0.76 → 1.42**. One value,
one commit. Its cost is stated rather than hidden: the respiration term's sd at every temperature
is now at least 1.42 in log, i.e. the model is granted a factor-4 band on O2 everywhere, which is
a real loss of information about respiration and is the price of a sampleable surface. The three
temperatures whose measured relative sd is 0.06–0.09 are the ones that lose most.

**The growth term is untouched** (the prompt's second decision, executed): its 1–3 unit kinks are
the growth LP's piecewise-linear response to θ, present in every enzyme-constrained model.
Flooring the primary data's variance to make a sampler comfortable would trade information for
convenience. They will appear in the re-scan and are **reported, not fixed**.

**The absolute smoothness rule, written now, before the re-scan exists:**

> A line is **SAMPLEABLE** if no single 0.05 sd step along it exceeds **5 log-likelihood units**.
> The surface is **SAMPLEABLE** if every one of P9's twelve lines is.

Why absolute rather than P9's relative rule: what decides whether a sampler can cross a step is
the likelihood ratio across it, e^{−Δ}. e^{−30} is a wall no random-walk proposal crosses;
e^{−2} is a kink any sampler steps over and a nested sampler does not even notice, since it uses
only the ordering of likelihood values. A relative rule (step > 20 % of the line's range) was the
right instrument while the cliffs were 13–72 units and the ranges 15–137; once the floor shrinks
the cliffs it shrinks the ranges with them, and the rule then flags kinks that are not obstacles.
Both readings are reported side by side. Five units is chosen as the threshold because it is the
same cliff threshold P10 used to *identify* the steps it fixed (`task2_floor.py`, CLIFF = 5.0),
so the rule and the diagnosis that produced the fix use one number; a step of 5 is a likelihood
ratio of 150 across 0.05 sd, which is a kink and not a wall.

If any line still exceeds 5 units after the floor move, TASK 0 STOPS and reports which.
