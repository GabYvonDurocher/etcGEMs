# K3 readiness — retiring the standalone fork

_N1 TASK 6. The etcGEMs-side work only. **Nothing in `$CANDIDAS_ROOT` was cloned, branched,
modified or pushed**; it was read, and `git status` there is unchanged (`?? runs/`, which
predates this night)._

## 1. Does anything here still need `$CANDIDAS_ROOT` at run time?

**No.** Verified with the variable unset:

| | with `$CANDIDAS_ROOT` unset |
|---|---|
| `etcgem tpc --strain cauris_iRV973` | Topt 34.0 °C, rmax 0.385 /h — **runs** |
| `etcgem transfer --experiment transfer_candida` | fitted σ 10.231397, w 8.788455, P 0.356974 — **runs** |
| `etcgem audit-sinks --strain cauris_iRV973` | 1314 costed of 2863; A=44 B=0 C=1 D=26 — **runs** |
| `reports/candida_thermal_limit/gate_table.py` | **79/79 PASS, exit 0** |
| `ladder_table.py`, `ceiling_table.py`, `sink_audit_table.py` | **run** |

TASK 2 removed the last run-time dependency: the gate reads a committed fixture
(`standalone_expected.json`) carrying the Candidas commit hash and the md5 of each source
file, and `--candidas-root` is now an optional drift check.

### What still references it, and what that means

Six files, none of them needed to *run* anything — each is a **regeneration** tool whose
outputs are already committed:

| file | needs `$CANDIDAS_ROOT` to | outputs already committed? |
|---|---|---|
| `tools/reconstruction/to_strain_inputs.py` | rebuild the four strains' input tables from the standalone's `gem/tables/` | yes — `strains/c*/{dltkcat,thermal,media,model}/` |
| `reports/predictor_calibration/a1_{fetch,orthologs,predict,analyse}.py` | re-run A1 (needs the four *C. auris* clade proteomes from `phylo/proteomes/`) | yes — `reports/predictor_calibration/*.csv,*.json,*.png` |
| `reports/N1_overnight/a3_gene_content.py` | re-run A3 (same proteomes) | yes — `reports/N1_overnight/A3_*.csv` |

So after archiving, all three keep working if pointed at the archive
(`--candidas-root .../Candidas`, unchanged, since `gem/` moves whole and every script in it
resolves paths from its own location). **What they cannot survive is the proteomes moving**,
which the archive plan does not touch: `phylo/proteomes/` stays where it is.

**One dependency is not on `gem/` but on `phylo/`.** A1 and A3 both read
`$CANDIDAS_ROOT/phylo/proteomes/*.faa`. If the intent is for etcGEMs to be able to regenerate
its own analyses without Candidas at all, those nine FASTA files (≈31 MB) would have to be
vendored or fetched from RefSeq. **This is not resolved and should be a decision.**

## 2. What would have to change in the Candidas repository

`gem/` is 56 MB (31 MB models, 11 MB tables). Thirty-four files outside `gem/` mention it.
Only two of them are load-bearing:

| file | what breaks | fix |
|---|---|---|
| `scripts/19_fig4.R` | `GT <- file.path(root, "gem", "tables")` — Figure 4 is drawn from those tables | one line, plus the header's input list |
| `scripts/run_all.sh` | the optional `RUN_GEM=1` stage runs `$ROOT/gem/$s.py` | one line, plus prose |
| `.gitignore` | seven `/gem/...` ignore rules stop matching | seven lines |

The other thirty-one are **prose**: `README.md` (8 mentions), `SETUP.md` (11),
`reports/{REPRODUCTION,RUNBOOK,N0_SENSITIVITY,MANUSCRIPT_FIGURE_LINKAGE}.md`,
`manuscript/{v3.qmd,grant_case_for_support.md}`, `docs/prompts/*`, `reports/tools/*.py` and
`reports/tools/*.json` (recorded paths in comparison fixtures), and two files already under
`archive/`. They should be updated for accuracy but nothing stops working if they are not —
except `reports/tools/*.json`, which record paths inside committed comparison fixtures and
should be checked by whoever owns those tools.

**Nothing inside `gem/` needs changing.** Every script there resolves its own location
(`gempaths.py`: `GEM = Path(__file__).resolve().parent`), so the directory moves whole.

### What could not be moved

* **The models.** `gem/models/*.xml` (31 MB) are also the strains' models in etcGEMs, where
  they are already committed. The archive keeps its copies; they are the same files.
* **`gem/tables/fig4/*.csv`.** Figure 4 of the manuscript is drawn from them, so they must
  stay reachable from `scripts/19_fig4.R` whatever else happens. They are outputs of the
  standalone and etcGEMs does not produce them (it produces the model, not the figure's
  flattened tables), so **they cannot be replaced by a pointer to etcGEMs.**
* **`gem/audits/` and `gem/notes/`.** The plan (`docs/CANDIDA_ETCGEM_PLAN.md` §5) has these
  moving to `reports/candida_thermal_limit/` as `audits/` and `notes/`. That is a move
  *into* etcGEMs and is **not** drafted here: it duplicates 25 audit scripts whose inputs are
  the standalone's own tables, and deciding which of them generalise into experiment overlays
  is a scientific judgement, not an implementation one.

## 3. The drafted patch, **not applied**

`reports/N1_overnight/K3_candidas_archive.patch` — verified with `git apply --check` in
`$CANDIDAS_ROOT`, **exit 0, nothing written**:

```
 .gitignore                       |  14 ++++----
 archive/gem_standalone/README.md |  64 ++++++++++++++++++++++++++++++
 scripts/19_fig4.R                |  22 +++++++------
 scripts/run_all.sh               |  15 +++++----
 4 files changed, 91 insertions(+), 24 deletions(-)
```

It contains the three path fixes and the new `archive/gem_standalone/README.md`, which points
at etcGEMs, states that the port is verified (79/79, with the fixture that makes the check
work with `gem/` archived), and records the two findings about the standalone that came out
of the porting.

**The patch does not contain the move itself**, because a rename of 56 MB is not a text diff.
Apply it after the move:

```bash
cd "$CANDIDAS_ROOT"
git switch -c k3/archive-gem-standalone
mkdir -p archive
git mv gem archive/gem_standalone
git apply /path/to/K3_candidas_archive.patch
git add -A && git commit -m "K3: retire the standalone etcGEM to archive/gem_standalone/"
# then check Figure 4 still draws:
Rscript scripts/19_fig4.R
```

**The last line is the acceptance test and it has not been run**, because running it would
require modifying `$CANDIDAS_ROOT`. Whoever applies this should run it before pushing.

## 4. What is left before K3 can be called done

1. **Decide the `phylo/proteomes/` question** above — whether etcGEMs vendors the nine
   proteomes so A1 and A3 can be regenerated without Candidas.
2. **Apply the patch and run `Rscript scripts/19_fig4.R`** to confirm the figure still draws.
3. **Decide about `gem/audits/` and `gem/notes/`** — the plan says they move into
   `reports/candida_thermal_limit/`; that is 25 audit scripts and a scientific judgement about
   which generalise.
4. Update the thirty-one prose references, and check `reports/tools/*.json`.
5. Ilgaz should see this first. `reports/N1_overnight/message_to_ilgaz.md` is the draft.
