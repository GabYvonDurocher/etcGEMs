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

## D2 — the audit had to infer the coupling ion, not assume the proton

**Where:** TASK 1.

*M. maripaludis*' ATP synthase in this project is **sodium**-driven, four Na⁺ per ATP. An audit
written for protons would have scored it "no ATP synthase" or, worse, scored a proton budget
that has nothing to do with how the organism conserves energy.

**Decided:** infer the ion from each strain's own ATP synthase. The class is named for the
coupling ion rather than the proton for that reason.

Two further things had to be right, each of which changes an organism's answer. **Ions enter the
energised compartment by chemistry as well as by translocation** — counting translocation alone
scores *Synechocystis* at 19 % when its chain supplies all of it, through water splitting and
cytochrome *b*₆*f* into the lumen — so both are reported and the caller reads the cell that
matters. And **GECKO splits a reaction into an arm and its isozymes**, putting the two halves of
ATP synthase in different reactions, so a test wanting both in one finds no ATP synthase in
eciML1515 at all; the audit contracts those groups first.

## D3 — the fix is an experiment overlay, never a strain default

**Where:** TASK 2.

The natural home for `forbid_ion_export` looks like `strain.yaml`, beside `pin_at_ub`. It cannot
go there. Doing so would change the `resolved_config.yaml` of every committed run of these
strains and move K1's locked numbers, which the gate checks — the P1 DECISIONS D3 concern.

**Decided:** `configs/experiments/candida_B5_respire.yaml`, as rung B5 of the K2 ladder. The
unrepaired model stays the default and both are runnable side by side. **The gate still passes
79/79, exit 0**, precisely because nothing runs the repair by default.

## D4 — the general rule, not the discovered list

**Where:** TASK 2.

Two versions of fix (b) were available: constrain the 5–8 carriers the solver was actually
caught using, or apply the general rule to every uncosted reversible carrier (134 reactions).
The first is less invasive; the second does not depend on which carrier the solver happened to
pick at one temperature.

**Decided:** the general rule, on the evidence that it costs nothing. The two give **identical
growth to six decimal places** (*C. auris* 0.065380 either way), so the 129 extra constraints
bind on nothing. Had they differed, the minimal list would have been the right answer and the
difference would have been the finding.

## D5 — complex III is reported and NOT corrected

**Where:** TASK 2, TASK 3.

The repair reveals that complex III, encoded with its protons running cytosol→matrix, eats
exactly half the proton-motive force cytochrome *c* oxidase pumps. Correcting it moves
respiration per unit growth from 1.8–2.4× measured to 0.9–1.3×, i.e. onto the measurement. It is
tempting to adopt.

**Decided:** report it, carry it through TASK 3 as a **labelled sensitivity**, adopt nothing. It
is a second, independent change to the reconstruction, and making two at once would leave the
before-and-after unattributable — which is the whole point of TASK 3. Recorded as
`OPEN_ITEMS` 3.13 with the evidence, for a human to decide.

## D6 — the carbon cap is grounded in the model's own requirement, and shared across species

**Where:** TASK 3b.

A cap had to be chosen. Two temptations: pick it per species, or tune it. Per species would
encode an interspecies difference that nothing measured supports, in a task whose whole subject
is whether an interspecies difference exists.

**Decided:** one shared value, `c_max = 12.0 mmol C/gDW/h`, the carbon the calibration strain
consumes at 40 °C with no area constraint — the tightest cap that does not itself reduce base
growth, which is P4's criterion for M9. Swept at 8, 12 and 20 so the choice is visible rather
than load-bearing.

## D7 — the core's carbon cap was silently a no-op on these models

**Where:** TASK 3b.

`gasflux.add_total_carbon_constraint` matched only GECKO-split `EX_*_e_REV` reactions. The
Candida and methanogen models keep one reversible exchange with a negative lower bound, so the
function matched nothing and returned None — a cap that reported success and constrained
nothing.

**Decided:** add a plain-exchange branch, as a **fallback** used only when the GECKO pattern
matches nothing, so no eciML1515 run can change behaviour while P4 is running there.
