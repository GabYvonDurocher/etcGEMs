# Quoting thermal descriptors: which are regime-free and which are not

*A short standing rule, written because the same thing has now been measured three times in
three different places.*

## The rule

* **$T_\text{opt}$ is quoted with its binding constraint named.** "T_opt = 31 °C" is not a
  property of the model; "T_opt = 31 °C on glucose-minimal, where the translation cap binds
  from 31 °C" is. A T_opt without its regime cannot be compared with another T_opt.
* **$CT_\text{max}$ may be quoted plainly.** It has been insensitive to every constraint tried.
* **$r_\text{max}$ is quoted with the constraint too**, for a different reason: it responds
  *continuously* to every capacity constraint, so there is no regime in which it is unaffected.
* **$E_a$ and the cold-limb descriptors follow $T_\text{opt}$**: they move when it does.

## The evidence

Three constraints have each been shown to relocate the optimum, in three separate pieces of
work, on the same organism and model:

| constraint | what it did to $T_\text{opt}$ | what it did to $CT_\text{max}$ | where |
|---|---|---|---|
| **the sector re-grounding** (`a416fd1`: $f_\text{metab}$ 0.285 → 0.483, medium-matched allocation wired) | **37 → 30 °C**, then 31 °C after the growth law | 46.856 → 46.881 °C (+0.05 %) | `reports/N2_followups/TASK1_stale_eciML1515_tpc.md` |
| **the translation cap**, where it binds | T_opt is the crossover at which the cap starts to bind; where the cap ceiling peaks instead, T_opt is that peak | unmoved | `reports/N3_output_audit/TASK2_cap_regime.md` |
| **a total-carbon cap** (Parsa's configuration D) | flat from uncapped to $c_\text{max}\approx150$, then **39.0 → 32.5 °C** between 80 and 60 on NLDM | ≤0.66 % at $c_\text{max}=60$, ≤0.91 % at 40 | `reports/P2_settle/TASK3_cmax.md` |

The pattern is consistent and mechanical rather than coincidental. $CT_\text{max}$ is where the
**unfolding envelope** takes growth to zero, and no capacity constraint moves that: a constraint
can only lower the curve, and the temperature at which the curve reaches zero is set by where
the enzymes denature. $T_\text{opt}$, by contrast, is wherever the *binding* constraint's
ceiling peaks or crosses the rising envelope-limited branch — so it moves whenever which
constraint binds changes, without the envelope changing at all.

## What this means for an attribution

A variance decomposition or elasticity that reports "$T_\text{opt}$ is owned by protein
stability" is a statement **about one operating point**, and it is measured with local
perturbations that do not cross a regime boundary. It is not wrong; it is conditional, and the
condition is the set of constraints that bind at that point. State the condition. The same
analysis for $CT_\text{max}$ needs no such caveat.

## In practice

* Every reported $T_\text{opt}$ names its medium and which of the pool / translation cap /
  carbon cap binds at the optimum.
* A T_opt compared across two model versions is checked for a change of binding constraint
  before it is read as a change of biology.
* A run whose configuration makes a cap bind hard records that fact beside the descriptors.
