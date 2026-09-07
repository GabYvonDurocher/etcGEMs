# N1 — decision log

_One entry per judgement call the prompt did not answer. Each records what was decided, why,
what the alternatives were, whether it is reversible, and who should look at it. An
over-long log is the intended failure mode._

## D0 — branch point

**Decided.** Branch `n1/overnight` from `main` at `295cedc`, as the prompt specifies. K1, K2
and A1 are all merged there; `git status` was clean apart from the pre-existing untracked
`strains/{mmaripaludis,syn6803}/outputs/`, which TASK 5 is about.

**Reversible:** yes. **Review:** nobody.

## D1 — a dirty working tree at the start of the night, reverted not committed

**Observed.** `strains/eciML1515/outputs/tpc/` (4 files) was MODIFIED in the working tree at
branch time — the output of an `etcgem tpc` verification run left behind, not a committed
change. Reverting it shows the same pre-existing drift the K1 report already records: the
committed eciML1515 `outputs/tpc/` does not match what the current code produces
(committed Topt 37.0 °C, rmax 0.341; current code 31.0 °C, rmax 0.543).

**Decided.** Reverted with `git checkout --`. N1 does not touch it.

**Why.** Committing it would change a committed result of a strain other than the Candida
four, which the standing rules forbid outright, and it is not N1's question.

**Alternatives.** Commit the refreshed output (forbidden); investigate the drift (a separate
piece of work — it predates the whole Candida merge and is already documented at the end of
`reports/candida_thermal_limit/K1_port_verification.md`).

**Reversible:** yes, trivially. **Review:** worth someone deciding whether the committed
eciML1515 TPC should be regenerated; it is stale, and TASK 5 is adjacent to it but does not
resolve it.

## D2 — TASK 1: absence is graded by alignment threshold, not by RBH

**Decided.** Report presence/absence at three nested criteria (`no_rbh`, `no_hit_e10`,
`no_hit_e3`) rather than the single RBH criterion the rest of the project uses.

**Why.** RBH-absence conflates "the gene is not there" with "reciprocity was broken by
paralogy". It over-states absence by more than threefold here: 569 versus 172 genes for
*C. auris* against *C. haemulonii*.

**Alternatives.** RBH only (what `07_rbh_orthologs.py` does) — simpler and consistent with
the rest of the project, but it would have reported ~3x too many absences.

**Reversible:** yes; all three columns are in the committed CSV. **Review:** nobody, but
anyone reusing `ortholog_pairs.csv` for presence/absence should read this.

## D3 — TASK 1: each species taken in the namespace its own model uses

**Decided.** RefSeq `XP_` for the three *Candidozyma*; UniProt/CGD `CPAR2_`
(`gem/inputs/parap_uniprot.tsv`) for *C. parapsilosis*, because that is what iDC1003's GPRs
are keyed on. All cross-species statements by alignment, never by identifier.

**Why.** Level (b) asks which genes reached a model, which is a direct lookup only if the
proteome is in the model's namespace. Using `phylo/proteomes/parapsilosis.faa` (RefSeq)
would have made every *C. parapsilosis* model-membership test fail silently.

**Alternatives.** Use RefSeq throughout and map to CPAR2_ by sequence — more steps, same
answer.

**Reversible:** yes. **Review:** nobody.

## D4 — TASK 1: the candidate screen decides by alignment, after finding by description

**Decided.** Find candidates by keyword in the RefSeq proteomes (which carry descriptions),
then decide presence in each species by aligning those sequences against every proteome.

**Why.** A description search alone gets it wrong twice over. It reports no alternative
oxidase in *C. haemulonii* when alignment finds one at 86.4% identity, and it reports zero
of everything in *C. parapsilosis*, whose model namespace has no description field — which
would have been read as absence when it is a missing annotation column.

**Alternatives.** Fetch annotations for the UniProt proteome — explicitly forbidden by the
task ("Do NOT fetch new annotations").

**Reversible:** yes. **Review:** someone should confirm the keyword list is the right reading
of the Xiao et al. candidates; FTR1 and SIT1 matched nothing in any proteome and are reported
as unanswerable rather than absent.

## D5 — TASK 2: the fixture holds every expected value, including the two prose-sourced ones

**Decided.** `standalone_expected.json` carries the calibration, the 48-value mu table and
the counterfactual results read from the standalone's tables, **and also** the two numbers
that were hard-coded in the script: the 52.7–54.5 °C thermal-limit range (from the prose of
`gem/FIG4_LOCKED.md`) and the 2.045 / 0.758 pool-binding pair (from
`gem/notes/POOL_BINDING_RESULT.md`). Each carries its `source` string.

**Why.** Otherwise the gate would have two kinds of expected value with two kinds of
provenance, one of them invisible. Now every expected number has one home and one recorded
origin, and the fixture is the complete statement of what the port is being held to.

**Alternatives.** Leave the two transcribed numbers as constants — simpler, but it would
mean `--refresh-fixture` silently does not refresh them.

**Reversible:** yes. **Review:** the two transcribed values are still transcriptions; if
anyone re-runs `22_thermal_sensitivity.py` or `16_pool_binding_test.py` and gets different
numbers, the fixture will not notice, because the standalone does not write them to a file.

## D6 — TASK 2: with --candidas-root, the LIVE values are used and drift is reported

**Decided.** When `--candidas-root` is given, the gate reads the standalone, prints any
difference from the committed fixture, and then evaluates against the **live** values.

**Why.** The alternative — evaluating against the fixture and only warning — would let the
gate pass while the thing it claims to reproduce had moved. Reporting drift and using the
live values means a changed standalone shows up as a changed verdict, which is the point of
a gate.

**Alternatives.** Always use the fixture and treat drift as a separate check; or fail on any
drift. The second is too brittle for a file that will legitimately change if the standalone
is ever re-run.

**Reversible:** yes. **Review:** nobody, unless the standalone is re-run — then someone
should look at the drift report before `--refresh-fixture`.

## D7 — TASK 3: rescaling refuses to run with proteome sectors, rather than half-working

**Decided.** `rescale_pool_row` raises a `RuntimeError` when `_sectors` is wired.

**Why.** The sector layer writes the pool bound in `set_allocation` and, under the growth
law, adds a `v_bio` coefficient to the pool row. Neither is reached by a rescaling applied in
`set_temperature`/`set_budget`, so with sectors on the row and its bound would be scaled by
different factors — a different LP, silently. An explicit refusal is a smaller problem than a
wrong answer.

**Alternatives.** Extend `set_allocation` to carry the factor — more code, and it would touch
the path eciML1515 and mmaripaludis run on, which is exactly what this task must not do.

**Reversible:** yes. **Review:** whoever wants the rescaling on a sector-enabled strain; the
extension is small but must not be done without re-verifying the other strains.

## D8 — TASK 3: default OFF, and the tension is recorded rather than resolved  *(NEEDS REVIEW)*

**Decided.** `rescale_pool_row` defaults to `false`, so the gate is unaffected and every
committed output is unchanged. The rescaled result is a separate labelled run.

**Why.** K1's gate reproduces the standalone exactly, INCLUDING the ~0.4% error the
standalone's solver made at the cold end of the two draft models. A better-conditioned port
does not reproduce that error and cannot pass the gate on those points. The standing rules
forbid loosening a test to make it pass and forbid editing a number in a report to match a
new result, so the only honest options were: leave the default off and document, or change
the canonical configuration and re-baseline the gate. The second is a decision about what
this project's reference numbers ARE, which is not a decision this prompt has the standing
to make.

**Alternatives.** (i) Default ON and re-baseline the affected gate rows against the correct
values — defensible, and arguably right, but it changes numbers people have quoted.
(ii) Default ON and loosen the tolerance — forbidden. (iii) Do not implement it — the task
asked for it.

**Reversible:** yes, one YAML key.

**Who should look at this:** the project owner. The question is whether fidelity to the
standalone or numerical correctness should be the canonical Candida configuration. Evidence
for correctness: Gurobi and GLPK's own exact rational solver agree, and GLPK does not — by
8.7% at the worst point. Evidence for fidelity: exact reproduction is the whole of K1's
claim, and a gate should be re-baselined deliberately and once, not as a side effect.

## D9 — TASK 3: the two fba resolved_config files are refreshed, and why that is not a result change

**Decided.** Commit the refreshed `resolved_config.yaml` of
`strains/cauris_iRV973/outputs/fba_candida_pool_{binding,unconstrained}/`.

**Why.** Those two folders were last written before K2 PART A added `ngam_reaction` and
`ngam_base_scale` to the strain files, so their recorded config no longer matched the
`strain.yaml` the run used. Both keys are inert in those runs (`ngam_temperature` is off) and
`fba_result.json` is byte-identical — no number moves. A resolved-config file exists to record
what was run; leaving it stale is a small untruth in a provenance record.

**Alternatives.** Revert them and leave the mismatch — keeps the diff smaller at the cost of
a provenance file that misstates the configuration.

**Reversible:** yes. **Review:** nobody, but it is the one place N1 touches a committed
output file, so it is recorded here deliberately.

## D10 — TASK 4: the flatness is recorded in a NEW file, not added to descriptors.json

**Decided.** `sector_flatness.json` is written into the run's output folder when the risk
applies, rather than adding a `plateau_width` field to `TPCDescriptors`.

**Why.** Adding a field to `TPCDescriptors` would change every `descriptors.json` in the
repository, including `strains/eciML1515/outputs/tpc/descriptors.json`, which is a committed
output of a strain other than the Candida four. The standing rules forbid that outright. A
new file, written only when the risk applies, records the same information and changes
nothing.

**Alternatives.** Add the field (forbidden); print it only (then it cannot be checked after
the fact, which is the point of the task).

**Reversible:** yes. **Review:** nobody. But see TASK4_sector_cap.md's closing paragraph:
making `descriptors()` itself refuse to report a T_opt read off a tie is the natural
follow-up and does change `descriptors.json`, so it needs a human.

## D11 — TASK 4: the guard fires for mmaripaludis too, and that is intended

**Observed, not decided.** *M. maripaludis* has sectors on with a fixed `translation_coeff`
and no `allocation_from_data`, so it is in the at-risk class and the guard fires for it. Its
plateau is reported as `NaN` because its bare TPC is identically zero at the a-priori
`kcat_scale` — the maintenance-crushed state its own `strain.yaml` documents.

**Why left as is.** The guard is correct: the configuration IS at risk. Reporting NaN rather
than a fabricated width is the right behaviour for a zero curve. Nothing about how
mmaripaludis runs changed, and its committed outputs are byte-identical.

**Reversible:** n/a. **Review:** whoever owns mmaripaludis may want to know that its
translation cap is temperature-independent; it has not mattered so far because its analyses
run at a calibrated `kcat_scale` where the metabolic pool binds.

## D12 — TASK 5: every strain commits its nominal TPC; scratch is everything a report does not read

**Decided.** The rule is "every strain commits `outputs/tpc/`; beyond that an output
directory is committed when a committed report, README or verification script reads it".
Applied to all seven strains (eight folders including `_toy`); documented in `README.md`.

**Why this and not the opposite rule.** Treating the nominal TPC as scratch and gitignoring
it everywhere is cleaner in one respect — nothing committed can go stale — but applying it
would mean removing `eciML1515`'s and `_toy`'s committed copies, and the standing rules for
this night forbid deleting committed evidence. The chosen rule adds files and deletes none,
and it has a property the other lacks: a committed nominal TPC that stops reproducing is a
signal. `eciML1515`'s already is one.

**Alternatives.** (i) gitignore everywhere — forbidden by the deletion rule. (ii) Leave the
inconsistency — the task exists because that is not acceptable.

**Reversible:** yes, entirely; these are new files. **Review:** the rule itself is worth a
sentence of agreement or disagreement from the project owner, since it now sits in README.md.

## D13 — TASK 5: `etcgem tpc` gains an optional `--experiment`, so syn6803 can be included

**Decided.** Add `--experiment` to `etcgem tpc`, mirroring `etcgem fba`, which has had it
since K1. `syn6803`'s nominal TPC is then produced through the shared command via the K2
overlay and lands in `outputs/tpc_syn6803_ecmodel/`.

**Why.** `syn6803`'s `strain.yaml` carries `provider.type: fba` as a P1 placeholder, so the
plain command cannot build its real model and the strain could not be brought under the rule
at all. The alternative was to declare syn6803 an exception, which is the inconsistency the
task exists to remove.

**Alternatives.** Fix `syn6803/strain.yaml` to describe its real provider — the right long-term
answer, but it changes how another strain is configured and could change its committed
results, which the standing rules put out of bounds tonight.

**Reversible:** yes. Verified that with no `--experiment` the command is byte-for-byte
unchanged (eciML1515 and mmaripaludis, all three files each).

**Review:** whoever owns syn6803 should decide whether `strain.yaml` ought to describe the
enzyme-constrained model directly instead of relying on an overlay.

## D14 — TASK 5: three further inconsistencies listed, not fixed

**Decided.** Record rather than act on: (i) `eciML1515/outputs/tpc/` no longer reproduces;
(ii) six `*_quick` / `*_v2` directories are committed under `eciML1515/outputs/`; (iii) sixteen
Python files live in strain folders against the project's own rule.

**Why.** Each would change or remove a committed artefact of a strain other than the Candida
four. (iii) in particular is load-bearing — `syn6803/run_p2_thermal.py` is the only way that
strain's real model gets built — and moving it is its own piece of work.

**Reversible:** n/a, nothing was done. **Review:** all three; (i) is the one that matters,
because a committed result that does not reproduce is either a stale file or a regression and
nobody currently knows which.

## D15 — TASK 6: the patch carries the path fixes and the README, not the move

**Decided.** `K3_candidas_archive.patch` contains the three path fixes
(`scripts/19_fig4.R`, `scripts/run_all.sh`, `.gitignore`) and the new
`archive/gem_standalone/README.md`. The `git mv` itself is given as commands in
`K3_readiness.md`, not as a diff.

**Why.** A rename of a 56 MB directory is not a text patch, and a patch that tried to be one
would be unusable. Verified instead that the textual half applies cleanly:
`git apply --check` in `$CANDIDAS_ROOT` exits 0 and writes nothing.

**Alternatives.** Generate a full `git format-patch` including renames — would require
committing in `$CANDIDAS_ROOT`, which is forbidden.

**Reversible:** n/a, nothing applied. **Review:** whoever applies it. The acceptance test
(`Rscript scripts/19_fig4.R` after the move) has NOT been run, because running it means
modifying `$CANDIDAS_ROOT`.

## D16 — TASK 6: the archive README's content is mine, and it makes claims

**Decided.** `archive/gem_standalone/README.md` states that the port is verified at 79/79,
names the two findings about the standalone that came out of porting it (the reversible
maintenance reaction and the Seq2Tm truncation bug), and tells readers to take etcGEM outputs
from a pinned etcGEMs commit by path rather than vendoring them back.

**Why.** An archive README that only said "moved" would lose the reason and the evidence. The
two findings are already in the K1 and A1 reports and in the draft message to Ilgaz, so the
README repeats rather than introduces them.

**Alternatives.** A three-line pointer — smaller, and it would leave the next reader to
rediscover why.

**Reversible:** yes, nothing applied. **Review:** ILGAZ SHOULD READ IT BEFORE IT IS APPLIED.
It is a README in his repository describing findings about his code; he should agree with the
wording, and the message drafted for him raises the same two points directly.
