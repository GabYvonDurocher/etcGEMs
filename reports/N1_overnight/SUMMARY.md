# N1 — overnight summary

Branch `n1/overnight`, from `main` at `295cedc`. Seven tasks, all attempted, **all DONE**.
Every judgement call is in `DECISIONS.md` (D0–D16).

## Status

| task | status | one line |
|---|---|---|
| **1 — A3 gene-content screen** | **DONE** | Gene content differs by 2.4–3.8% within the *Candidozyma* clade and 8.5–11.2% against *C. parapsilosis*, but **0–15 genes per comparison are inside a metabolic model**; all four locatable Xiao et al. candidates are present in all four species and AOX and the glutaredoxins are in no model. |
| **2 — self-contained gate** | **DONE** | Every expected value frozen in `standalone_expected.json` with the Candidas commit and per-file md5. **79/79 PASS, exit 0, with `$CANDIDAS_ROOT` unset**; `--candidas-root` now reports drift. |
| **3 — pool-row conditioning** | **DONE** | `provider.rescale_pool_row`, **default off**. Row spans 1.4e8–7.7e11; rescaling leaves Gurobi at 1.5e-14 and fixes 9 of GLPK's 10 errors. The tension with K1's gate is recorded, not resolved — **D8 needs review**. |
| **4 — sector translation cap** | **DONE** | Hypothesis confirmed: eciML1515's plateau goes 2.0 °C → **14.0 °C** with `allocation_from_data` off. Guard added (warning + `sector_flatness.json`); the cap was **not** made temperature-dependent. |
| **5 — repository consistency** | **DONE** | One rule chosen and applied to all seven strains: every strain commits its nominal TPC. `etcgem tpc` gained `--experiment` so syn6803 could be included. Three further inconsistencies listed, not fixed. |
| **6 — K3 groundwork** | **DONE** | **Nothing in this repository needs `$CANDIDAS_ROOT` at run time**, verified. Patch drafted and `git apply --check`ed (exit 0), **not applied**. `$CANDIDAS_ROOT` unmodified. |
| **7 — message to Ilgaz** | **DONE** | Drafted, plain text, pasteable. |

## What every task produced

**TASK 1** `A3_gene_content.md` + six CSVs, from `a3_gene_content.py`. Absence graded at
three alignment thresholds because RBH-absence over-states no-hit absence more than threefold
(569 vs 172 genes for *C. auris* against *C. haemulonii*). The model-level trap is stated
before the numbers: the two draft models are the *C. auris* network with genes reassigned, so
their model-level gene content is near-identical by construction. FTR1 and SIT1 matched no
description in any proteome and are reported as unanswerable, not absent.

**TASK 2** `standalone_expected.json` (Candidas `f123bc7`, md5 per source file) + a rewritten
`gate_table.py`. The two values previously hard-coded from prose (`FIG4_LOCKED.md`'s
52.7–54.5 °C, `POOL_BINDING_RESULT.md`'s 2.045/0.758) are in the fixture too, each with its
source string. `K1_port_verification.md` updated.

**TASK 3** `TASK3_pool_conditioning.md` + two CSVs. The one GLPK error that survives rescaling
was arbitrated with `glpk_exact`: Gurobi and the exact rational solver agree (0.0128335203)
and GLPK is 8.7% wrong. Default-OFF verified to change nothing.

**TASK 4** `TASK4_sector_cap.md`, `configs/experiments/eci_sectors_no_alloc_data.yaml`,
`strains/eciML1515/outputs/n1_task4_sectors_no_alloc/`, and the guard in `sectors.py` wired
into `etcgem tpc` and `etcgem transfer`.

**TASK 5** `TASK5_repository_consistency.md`, the rule in `README.md`, nominal TPCs committed
for all seven strains, `--experiment` on `etcgem tpc`.

**TASK 6** `K3_readiness.md` + `K3_candidas_archive.patch` (4 files, 91 insertions, `git apply
--check` exit 0, not applied).

**TASK 7** `message_to_ilgaz.md`.

## Nothing broke

| check | result |
|---|---|
| `etcgem tpc --strain eciML1515`, three files vs the pre-K1 baseline | **IDENTICAL** |
| `etcgem tpc --strain mmaripaludis`, three files | **IDENTICAL** |
| K1's gate, `$CANDIDAS_ROOT` unset | **79/79 PASS, exit 0** |
| `git diff main HEAD` for existing strains | **additions only** — eciML1515 gained the TASK 4 diagnostic directory; mmaripaludis and syn6803 gained their nominal TPC under TASK 5's rule. No committed output modified. |
| `$CANDIDAS_ROOT` | **unmodified** (`git status` there: `?? runs/`, which predates tonight) |

## What needs a human, and why

Ordered by how much it matters.

1. **D8 — should the canonical Candida configuration be `rescale_pool_row: true`?**
   *The question:* fidelity to the standalone, or numerical correctness. K1's gate reproduces
   the standalone exactly **including a ~0.4% error its solver made**; a better-conditioned
   port does not reproduce that error and cannot pass the gate on those points. Left off, so
   nothing changed. *Evidence for switching:* Gurobi and GLPK's own exact rational solver
   agree and GLPK does not, by 8.7% at the worst point. *Evidence against:* exact reproduction
   is the whole of K1's claim, and a gate should be re-baselined deliberately and once.

2. **D16 — Ilgaz should read the archive README before it is applied.** It is a README in his
   repository describing findings about his code. The message drafted for him raises the same
   two points directly, and he should see both before either lands.

3. **TASK 5 finding — `strains/eciML1515/outputs/tpc/` does not reproduce.** Committed
   Topt 37.0 °C / rmax 0.341; current code 31.0 °C / 0.543. It predates the Candida merge.
   Under the rule adopted tonight this is a signal, and **nobody currently knows whether it is
   a stale file or a regression.**

4. **TASK 6 — the `phylo/proteomes/` question.** A1 and A3 read the proteomes from
   `$CANDIDAS_ROOT`. Archiving `gem/` does not touch them, but if etcGEMs is meant to
   regenerate its own analyses without Candidas at all, those nine FASTA files (~31 MB) must
   be vendored or fetched. Not resolved.

5. **TASK 4 — the translation cap.** Not made temperature-dependent; that is a modelling
   decision with implications for every strain. `TASK4_sector_cap.md` proposes making the
   *absence* of temperature dependence a declared choice rather than the default that arises
   from omitting a key, notes that grounding it for yeast is blocked on data, and argues
   against a generic literature ribosome response.

6. **TASK 5 findings 2 and 3** — six `*_quick`/`*_v2` directories committed under
   `eciML1515/outputs/`, and sixteen Python files in strain folders against the project's own
   rule. Both are their own piece of work.

7. **D13 — syn6803's `strain.yaml` describes a placeholder provider.** Tonight's workaround
   is the `syn6803_ecmodel` overlay. Whether the strain file should describe the real model
   directly is for whoever owns that strain.

## The decision log

`DECISIONS.md`, D0–D16, in full. Two are marked as needing review (**D8**, **D16**); the
others record choices that are reversible and confined to new files.
