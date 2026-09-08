# K5 — decisions

Standing rules carry over. `$CANDIDAS_ROOT` is READ ONLY. This run owns `strains/c*/` and
`reports/K5_respire/`. **P4 was still running when this started** (see D1), so
`strains/eciML1515/` and `reports/ecoli_*` are audited read-only and never written.

Branched from `main` at **c094bf0**, which is the K4 merge plus its stamp refresh.

---

## D0 — TASK 0: the merge verified, with one artefact that is not a difference

**Where:** TASK 0.

PR #7 merged with a merge commit (`0a42c2f`), remote and local branches deleted. Verification,
exit codes checked explicitly and never chained:

| check | result |
|---|---|
| Candida gate, `$CANDIDAS_ROOT` unset | **79/79 PASS, exit 0** |
| `stamp_reports.py --check` | exit 1 → regenerated → **exit 0** |
| `etcgem transfer --experiment transfer_candida` | exit 0, outputs byte-identical |
| `etcgem transfer --experiment candida_B3_ngamT` | exit 0, outputs byte-identical |
| working tree after all of it | clean |

The stamp failure was expected and is not a defect: a stamp records the commit its report was
last written at, so merging K4 made K4's own stamp stale. P3 refreshed its stamps after its
merge for the same reason. Regenerated and pushed to `main`, which is the one push to `main`
TASK 0 permits.

**The artefact.** Re-running the two transfer experiments left every `tpc.csv`, `summary.csv`,
`counterfactual.csv` and `calibration.json` byte-identical, but changed eight
`resolved_config.yaml` files. The whole diff is one line each: `provider.model_path`, which is
recorded as an **absolute** path and therefore encodes the directory the run was made from.
This run is in a git worktree at `etcGEMs-k5/`, so the path differs from the committed one made
in `etcGEMs/`. Reverted; no numerical output moved. Recorded in `docs/OPEN_ITEMS.md` because it
means "byte-identical on re-run" is only checkable from the same directory, which is a
reproducibility wart rather than a result.

## D1 — P4 had NOT landed; E. coli is audited, never written

**Where:** TASK 0, TASK 1.

Checked rather than assumed. At the start of this run `p4/refit` sat at `32cc234`
("P4 TASK 2: refit D_NLDM under the canonical settings"), two commits ahead of `main` and not
merged, and `strains/eciML1515/outputs/calibration_configD_NLDM_recipe_cmax120/` was being
written to within the previous ninety minutes.

**Decided:** TASK 1 audits all seven strains, but builds *eciML1515* read-only and writes
nothing under `strains/eciML1515/` or `reports/ecoli_*`. Any proton defect found there is
reported and left for P4, as the prompt requires.
