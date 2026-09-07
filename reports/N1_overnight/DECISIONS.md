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
