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
