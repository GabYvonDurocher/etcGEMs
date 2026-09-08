# Claude Code prompt — P1: bring Parsa's gas-flux and overflow work (Configs A–F) into the core, split mechanism from E. coli specifics, and reproduce his numbers as the gate (autonomous)

Run from the project root (`.../MICROADAPT/etcGEMs`). Parsa has built six configurations exploring
gas exchange and overflow metabolism on top of a July snapshot of this repository. They are novel
work destined for a new E. coli paper, together with the temperature-dependent proteome allocation
already in the core. This prompt brings them in **under the project's own rule**: one core model,
strain folders carrying only data and configuration.

His folder is at `$PARSA_ROOT` (default: `/Users/g.yvon-durocher/Downloads/etcGEMs-main_3`). It is
**READ ONLY** throughout — a plain directory, not a git repository.

NOTE TO USER: launch in an auto-approving mode. No emcee, no overnight recomputation: this prompt
ports code and reproduces cheap deterministic quantities. Where reproducing something would need a
calibration, it STOPS and costs it rather than spending the night.

## What Parsa's snapshot is, established rather than assumed

He recalls downloading on 7 July; the content says otherwise and the content is authoritative. Every
shared module in his `src/etcgem` is an EXACT ancestor of ours, so he modified nothing in the core.
Matching commits: `config.py`, `enzyme_cost.py`, `sectors.py` → `2b6e8b4`; `calibration_multi.py` →
`4620c9f`; `providers.py` → `7ec248f`; `cli.py` → `e67b4c0`. The newest is **`e67b4c0`, 9 July
21:00** — his fork point. `main` is now ~140 commits ahead.

**Three things changed under him, and each is a reconciliation, not a port:**
  * `99eab16` (10 Jul) consolidated configs under `configs/` and dropped the per-strain
    `config.yaml` — the layout his scripts expect no longer exists.
  * `8e6b703` (10 Jul) renamed canonical output directories (`validation_trusted` → `validation`,
    `calibration_vanderlinden_v3` → `calibration_vanderlinden`) and archived superseded runs.
  * `8085036` (11 Jul) closed the four uncosted O2 sinks BY DEFAULT, credited as Parsa's own audit.
    His `gasflux.py` still carries `block_free_o2_sinks` with an identical `FREE_O2_SINKS` list, so
    the same thing is now done twice. His committed gas-flux numbers were produced with HIS closure,
    not the core's.

## The split this prompt enforces

His configs are currently structured as parallel implementations with E. coli specifics hard-coded
in module constants — `configE.py` holds Szenk-2017 complex footprints, `configF.py` holds
`BDII_RXNS = ["CYTBDppNo1", "CYTBD2ppNo1"]`, and `configF` imports `configE` rather than varying it.
Nothing appears in `strain.yaml`. That is the same drift the K-series corrected for Ilgaz.

The test for every line: **would another organism ever want this?**

| | core (`src/etcgem`) | `strains/eciML1515/` |
|---|---|---|
| A MMRT-costed transport | the costing mechanism | which reactions are transport |
| B total-carbon cap | `add_total_carbon_constraint` | `c_max` |
| C Basan acetate line | the comparison machinery | Basan data, acetate reaction ID |
| D emergent overflow | calibration OPTIONS, not parallel calibrators | cap parameters |
| E ETC membrane area | area constraint keyed on a complex table | Szenk footprints, reaction IDs, `A_ETC` |
| F bd-II electrogenicity | an electrogenicity column in that SAME table | which reactions are bd-II |

**E and F must collapse into one mechanism.** An ETC complex table with area and electrogenicity
columns is smaller and more general than a module plus its fork, and it is what would let the
Candida strains ever test a membrane-area limit — the one open axis neither codebase can express.

Follow the precedent already in this repository: `proteome_alloc.py` is generic in the core, the
Wang 2026 measurements sit in `strains/eciML1515/proteomics/`, and `strain.yaml` wires them with
`allocation_from_data:`. Every config should end up looking like that.

REFERENCE, read first: `$PARSA_ROOT/ADDED_FILES_MANIFEST.txt`, his `src/etcgem/{gasflux,configE,
configF,calibration_configD,calibration_configD_full}.py`, `$PARSA_ROOT/README.md`, and
`$PARSA_ROOT/outputs_reports/etcgem3_configuration_summary*.pdf` for what each config claims. Then
`prompts/K1_candida_port_and_verify_prompt.md` (the same job, done for Ilgaz) and
`docs/CANDIDA_ETCGEM_PLAN.md` §2 (the structural rule).

---

```
Work AUTONOMOUSLY; commit in parts; print a summary. Branch: `git switch -c p1/parsa-configs main`.
Maintain reports/P1_parsa_port/DECISIONS.md from the first judgement call. $PARSA_ROOT and
$CANDIDAS_ROOT are READ ONLY. Do not push to main. Do not run emcee.

PART A - inventory and fork-point confirmation
- Verify the fork point above rather than trusting it: confirm each shared module matches the stated
  commit, and report any that do not.
- Enumerate what he adds: the five new source modules, every `scripts_*.py` and `scripts/add_*.py`,
  and what each config's outputs contain. Classify each script: PORT (belongs in the framework),
  SCRATCH (his `scratchpad_*.py`, one-off diagnostics), or REPORT-BUILDER.
- List, per config, the numbers his own reports print — these become the PART E gate. Take them from
  his outputs and reports, and say where each came from.

PART B - the core mechanisms
Implement in src/etcgem, generic, with NO E. coli reaction IDs, footprints or values in the code:
- `gasflux.py`: exchange-flux TPCs and `add_total_carbon_constraint`. REMOVE `block_free_o2_sinks`
  and its `FREE_O2_SINKS` constant — the core already closes those by default (`8085036`). If
  anything in his path depends on closing them at a different point, say so and handle it through
  the existing provider option rather than reinstating a second mechanism.
- One ETC-complex mechanism replacing configE + configF: a constraint driven by a per-strain TABLE
  with columns for reaction ID, area footprint, turnover and electrogenicity. E's area budget and
  F's non-electrogenic bd-II become rows and a column, not two modules.
- ConfigA's transport costing and ConfigB's carbon cap as core options.
- ConfigD: fold into the EXISTING calibration machinery as configurations. Do not carry
  `calibration_configD.py` / `calibration_configD_full.py` across as parallel calibrators — three
  calibration code paths cannot be kept in step. If folding proves genuinely impossible, STOP and
  explain why rather than duplicating.
- Everything opt-in and OFF by default. No existing strain's behaviour may change: verify
  eciML1515, mmaripaludis, syn6803 and the four Candida strains produce byte-identical committed
  outputs, and that the Candida gate still passes 79/79 with $CANDIDAS_ROOT unset.

PART C - the E. coli specifics
Into `strains/eciML1515/`, referenced from `strain.yaml`:
- `etc/complexes.csv` (or similar): the Szenk-2017 footprints, turnovers, reaction IDs and the
  electrogenicity flag, with provenance in a header comment.
- `A_ETC`, `c_max`, the transport reaction set, the acetate reaction ID, ConfigD's cap parameters,
  and the Basan reference data.
- Each config selectable per run, in the `configs/experiments/` style, NOT as a bespoke script.

PART D - port his scripts
- PORT-classified scripts move into `scripts/` adapted to the current API and the new config layout
  (his per-strain `config.yaml` no longer exists — `99eab16`).
- SCRATCH stays out. Say what you dropped and why, in one line each.
- Report builders: adapt to write into `reports/ecoli_gasflux/` (a new deliverable directory in the
  house convention), not into his `outputs_reports/`.

PART E - THE GATE: reproduce his numbers, and be honest about which cannot be checked cheaply
- For every quantity listed in PART A, reproduce it under the port and tabulate his value, the port
  value, the tolerance and PASS/FAIL.
- EXPECT SOME TO MOVE, for a stated reason: his runs used his own O2-sink closure rather than the
  core's default, his baseline predates `a416fd1` (the sector re-grounding that moved E. coli's
  nominal T_opt 37 → 30 C) and `8085036`. Where a number moves, say WHICH of those explains it, with
  evidence. A movement you cannot attribute is a FAIL, not a footnote.
- Anything requiring a calibration to check: do NOT run it. List it, estimate the cost, stop.
- Write reports/P1_parsa_port/gate.md with the table and the attributions.

PART F - the one cheap science check, before anyone writes anything up
Does ConfigD's overflow move the THERMAL descriptors, or only the carbon ones? Run the nominal TPC
with ConfigD off and on and report T_opt, rmax, CT_max, E_a and niche width side by side, plus the
carbon quantities (acetate flux, O2, CO2, RQ). This is a handful of solves, not a calibration.
- If the thermal envelope is unmoved, the thermal work and the overflow work compose cleanly and can
  be written up side by side.
- If T_opt or CT_max move, they cannot, and that must be flagged prominently — it would mean the
  existing thermal results were obtained in a regime where a real mechanism was missing.
- Report the numbers. Do not adjudicate what should be done about it.

PART G - do NOT import his outputs
His `strains/eciML1515/outputs/` is 295 MB over 114 directories and contains his own copies of
`calibration_vanderlinden`, `validation_trusted`, `control_tuned`, `decompose_tuned`,
`elasticity_tuned`, `sweep_calibrated`, `proteome_sectors` and `anatomy` — the same directories the
N3 audit flagged, from a different model state. Importing them would give two unattributable sets of
outputs for the same analyses.
- Import NOTHING from his outputs tree except small text tables needed as INPUT (e.g. the Basan
  data), each with its provenance recorded.
- His `outputs_reports/` (including 16 `.bak` Word files) stays out entirely.
- Record in the report where his outputs are, so they can be consulted rather than lost.

VERIFY (report all)
1. Fork point confirmed or corrected, per module.
2. The script classification: PORT / SCRATCH / REPORT-BUILDER, with counts.
3. Core mechanisms implemented, with confirmation that no E. coli identifier or measured value
   appears in src/etcgem; E and F collapsed into one mechanism.
4. `strain.yaml` and the E. coli data files; each config runnable via configs/experiments/.
5. All seven existing strains byte-identical; Candida gate 79/79 with $CANDIDAS_ROOT unset.
6. THE GATE TABLE: his value, port value, PASS/FAIL, and for every movement the attribution
   (his O2 closure / pre-a416fd1 / pre-8085036 / unexplained).
7. PART F: thermal descriptors with ConfigD off and on, and the carbon quantities.
8. What was NOT checked because it needs a calibration, with costs.
9. `git diff main --stat`; nothing from his outputs tree imported except named inputs.

CONSTRAINTS
- The rule outranks convenience: mechanisms in the core, E. coli specifics in the strain folder, no
  strain folder containing code that implements the method.
- E and F collapse. If that turns out to be wrong, STOP and explain — do not port two modules
  quietly.
- Everything opt-in, default off, existing strains untouched. Verified, not asserted.
- An unattributable change in one of his numbers is a FAIL. Do not explain movements you have not
  demonstrated.
- No emcee. No overnight recomputation. Stop and cost instead.
- Autonomous; commit in parts:
  "P1: inventory of Parsa's snapshot and fork point",
  "P1: core mechanisms - gas flux, carbon cap, ETC complex table",
  "P1: E. coli specifics into strains/eciML1515 + experiment configs",
  "P1: ported scripts and report builder",
  "P1: gate against Parsa's numbers",
  "P1: ConfigD thermal-vs-carbon check".
```
