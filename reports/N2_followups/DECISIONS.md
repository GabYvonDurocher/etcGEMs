# N2 — decision log

_Continues N1's. One entry per judgement call the prompt did not answer._

## D0 — TASK 0: `$CANDIDAS_ROOT` is not literally clean, and the merge proceeded anyway

**Observed.** The prompt's pre-merge check is "`git -C "$CANDIDAS_ROOT" status --short` is
empty". It is not: it shows `?? runs/`.

**Decided.** Proceed with the merge.

**Why.** `runs/` is untracked, contains the Candidas project's own C-series R pipeline
outputs (`C1_reproduction/`, `C2_arm_current/`, `C2_arm_nobp/`, `C2_arm_ramp/` — oxygen
tables and figures), and was already present at the first `git status` of that repository in
the K1 session, before any of this work began. No tracked file there is modified. The check's
intent is "we have not written into the Candidas repository", and that holds.

**Alternatives.** Stop the whole prompt over a pre-existing untracked directory in someone
else's repository.

**Reversible:** n/a. **Review:** nobody, but recorded because it is a documented check that
did not literally pass.

## D1 — TASK 0: the merge verification flagged two mmaripaludis files, and it was a file mode

**Observed.** After the merge, re-running `etcgem tpc` for mmaripaludis left
`descriptors.json` and `nominal_tpc.csv` flagged by `git status`. That is a stop condition as
written.

**Decided.** Not a stop condition: the diff is `old mode 100644 / new mode 100755` and
nothing else. All eight mmaripaludis and syn6803 output files are byte-identical in CONTENT,
checked with `cmp` against `git show HEAD:<path>`.

**Why.** This checkout is on a OneDrive-backed filesystem that flips the executable bit on
rewrite. `git status` reports mode changes; the content is what the verification is about.

**Alternatives.** Set `core.fileMode=false` — a repository configuration change affecting the
user's environment, for a cosmetic problem, and not this prompt's business.

**Reversible:** n/a, nothing changed. **Review:** worth knowing that on this machine
`git status` can flag a file whose content has not moved; content checks should use `cmp`
against `git show`, which is what N2 does throughout.

## D2 — TASK 1: the reproduction check reports exact AND numeric agreement separately

**Decided.** `task1_reproduce_all.py` reports `reproduces_exact` (byte-for-byte) and
`reproduces_numeric` (every number equal to a relative tolerance of 1e-9) as two columns.

**Why.** The toy strain's TPC differs from its committed copy by a maximum **relative**
difference of 6.2e-15 — floating-point rounding between BLAS builds, on a model whose
numbers are otherwise deterministic (two consecutive runs are byte-identical). Reporting that
as "does not reproduce" would bury the one real finding in noise.

**Alternatives.** Byte comparison only — would have flagged `_toy`'s numbers as stale when
they are not. Numeric only — would have hidden `_toy`'s genuinely stale `resolved_config.yaml`.

**Reversible:** yes. **Review:** nobody.

## D3 — TASK 1: `_toy`'s stale resolved_config is listed, not fixed

**Decided.** `strains/_toy/outputs/tpc/resolved_config.yaml` is structurally stale — it
predates `close_free_o2_sinks` in `configs/defaults.yaml` and the `proteome_sectors` block in
the merged config — and is **left alone**.

**Why.** The task's constraint is explicit: do not bulk-overwrite other stale outputs, list
them. It is also the least consequential possible case (a synthetic smoke-test strain whose
numbers are correct and whose provenance file is out of date), so there is no urgency that
would justify overriding the constraint.

**Alternatives.** Regenerate it — one command, and it would have been consistent with what
TASK 1 did for eciML1515, but eciML1515 was diagnosed first and this was not.

**Reversible:** n/a, nothing done. **Review:** whoever wants it regenerated; it is a
one-liner and should be done deliberately.

## D4 — TASK 1: the check covers what one quick deterministic command produces, and says so

**Decided.** The reproduction check covers the nominal TPCs, the Candida `transfer_*`,
`audit_sinks*` and `fba_*` outputs — 46 directories, 132 files. It does **not** cover
`eciML1515`'s sweeps and Bayesian calibrations, `mmaripaludis`' M2–M6, `syn6803`'s P1–P4, or
the cross-organism `outputs/ea_*`.

**Why.** Those take hours to days and several are stochastic (emcee chains), so "does it
reproduce" is a different question needing a seed policy and a tolerance rather than a byte
comparison. Attempting it inside an under-an-hour prompt would have produced a table of
false failures.

**Alternatives.** Run everything — not feasible in the time and would answer the wrong
question for the stochastic runs.

**Reversible:** n/a. **Review:** somebody should decide whether the stochastic outputs need a
reproducibility policy at all; at present nothing checks them.

## D5 — TASK 2: with sectors wired, the default reverts to off instead of raising

**Decided.** `config._rescale_choice` distinguishes an EXPLICIT `rescale_pool_row: true` from
the new default. With proteome sectors enabled, an explicit request still raises (N1 D7's
reasoning is unchanged); the default silently reverts to off and prints why.

**Why.** N1 implemented the sector case as a hard error, correctly, when the option was
opt-in. Once it is the default, that error would break ladder rung B4 and *M. maripaludis*
without either configuration having asked for anything. A default must not break a
configuration that was working.

**Alternatives.** Set `rescale_pool_row: false` explicitly in B4 and in mmaripaludis'
strain.yaml — works, but leaves every future sector strain to trip over the same error.
Extend the rescaling into `set_allocation` — the right long-term answer, and it touches the
path eciML1515 and mmaripaludis run on, which N2 is not the place for.

**Reversible:** yes. **Review:** whoever wants rescaling to work with sectors; the extension
is small but must be verified against the other strains.

## D6 — TASK 2: legacy fidelity is the four gate experiments, which includes ladder rung B0

**Decided.** `rescale_pool_row: false` goes in `transfer_candida`,
`transfer_candida_unpinned`, `candida_pool_unconstrained` and `candida_pool_binding` — the
four experiments K1's gate reads. `transfer_candida` is also K2 ladder rung B0.

**Why.** B0 is by definition the standalone's configuration — it is what the gate compares
its limits and counterfactual rows against — so it belongs on the fidelity side. It also
means K2's published B0 row does not move, which is the right outcome for a rung whose job
is to be the reference point.

**Alternatives.** Put only `transfer_candida_unpinned` (the one that runs GLPK) in legacy
fidelity. Under Gurobi the other three move by <1.5e-14, so it would work — but it would
leave the gate reading a mixture of configurations, which is the thing this task exists to
end.

**Reversible:** yes, four YAML keys. **Review:** nobody, but it is worth knowing that "ladder
rung B0" and "legacy fidelity" now name the same configuration.

## D7 — TASK 4: the "2–5%" framing is stated as a range with the arithmetic visible

**Decided.** §5 says "the models see about 2–5% of the gene-content difference" and gives the
two numbers it comes from (0–15 in a model, 122–647 in the proteome) plus a worked example
(4 of 209 for *C. auris* against *C. haemulonii*).

**Why.** 0/122 to 15/647 spans 0% to 2.3%, and the per-comparison ratios cluster around
1.5–2.5%; the prompt's "roughly 2–5%" is the right order but the honest thing is to show the
ratio rather than assert a single figure, because the numerator is small enough that a single
gene moves it several percent.

**Alternatives.** Quote a single percentage — cleaner to read, and it would overstate the
precision of a count that ranges from zero to fifteen.

**Reversible:** yes, it is prose. **Review:** worth a glance from whoever quotes it next; the
underlying table is `reports/N1_overnight/A3_model_level_counts.csv`.

## D8 — TASK 4: §6(e) is written as a scope limit, and says explicitly what it does not claim

**Decided.** §6(e) says the Xiao et al. mechanism is "untestable in this framework as it
stands, on two separate grounds", names both, and then states in the same paragraph that this
is a scope limit of these reconstructions and **not** a refutation — because a gene being
present says nothing about expression, and the mechanism proposed is regulatory rather than
combinatorial.

**Why.** The prompt asks for exactly this framing, and it is the one place in N2 where a
measurement could easily be read as adjudicating a mechanism. Writing the disclaimer in the
same paragraph rather than a footnote is deliberate.

**Reversible:** yes. **Review:** this is the sentence most likely to be quoted out of
context; worth a human reading it once.
