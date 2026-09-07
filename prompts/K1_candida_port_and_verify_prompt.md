# Claude Code prompt — K1 (Candida into the framework, phase 1): port the four Candida species as `strains/` entries on the common core, add the three generic pieces the core lacks, and verify the port reproduces the standalone implementation's locked numbers (autonomous)

Run from the project root (`.../MICROADAPT/etcGEMs`). PORT phase. This makes the four Candida
species strains of this repository, using `src/etcgem` as their only implementation. It decides
NOTHING scientific: the gate is that the core, configured to match the standalone implementation,
reproduces that implementation's locked numbers. K2 (the same strains under the core's own thermal
form) is a separate prompt and must not be started here.

NOTE TO USER: launch in an auto-approving mode. Needs the Candidas repository checked out beside this
one — set `CANDIDAS_ROOT` to its path (default:
`/Users/g.yvon-durocher/Library/CloudStorage/OneDrive-UniversityofExeter/Documents/work/Candidas TPC/Candidas`)
at commit `f123bc7` or later. The Candidas repository is READ ONLY for this prompt. Python, cobra and
a solver as for the other strains. Nothing here runs DLKcat, KOfam or Seq2*: their OUTPUTS are ported;
the TOOLS are ported and wired but not re-executed (fetching their external weights is out of scope).

REFERENCE: docs/CANDIDA_ETCGEM_PLAN.md (read it first; §2 is the target structure, §3 the mapping, §4
the three additions). The standalone implementation is `$CANDIDAS_ROOT/gem/` — read its `README.md`,
`gempaths.py`, `18_build_etcgem_tpc.py` (the whole model is in this one 140-line file) and
`FIG4_LOCKED.md` (every number the port must reproduce, each pinned to its producing script).

THE STANDALONE MODEL, so there is no ambiguity about what is being matched. Per reaction r with
DLKcat kcat_r tied to best gene g, for which Topt_g and Tm_g are sequence-predicted:

    peak_g(T)  = exp(-(T - Topt_g)^2 / (2 sigma^2))
    death_g(T) = 1 / (1 + exp((T - Tm_g)/w))
    act_g(T)   = peak_g(T) * death_g(T), floored at 1e-6
    kcat_r(T)  = kcat_r * act_g(T)
    pool:        sum_r  MW_r / (kcat_r(T) * 3600)  *  v_r  <=  P        (sMOMENT, one pool)

Three globals {sigma, w, P} fitted by multi-start Nelder-Mead to the C. auris measured curve only,
then frozen; fitted values approx sigma = 10.2, w = 8.8, P = 0.36. Reactions without a kcat use a
default (13.7 s^-1); genes without a prediction use the species median Topt/Tm. Temperature sweep
22-44 C; detection floor 0.05 h^-1. Medium: YMS as glucose + a pooled amino-acid budget, biotin
auxotrophy retained. This is the `phenomenological` thermal form the core gains in PART C.

---

```
Work AUTONOMOUSLY; commit in parts; print a summary. Read first: docs/CANDIDA_ETCGEM_PLAN.md;
strains/mmaripaludis/ (the smoment_gem strain layout and strain.yaml to mirror — this is the closest
precedent, NOT eciML1515); src/etcgem/{providers.py (from_gem_smoment), config.py (build_provider),
enzyme_cost.py (the thermal_model dispatch at the "unfolding" branches), cli.py (how verbs are
registered), calibration_multi.py}; prompts/README.md; then $CANDIDAS_ROOT/gem/{README.md,
gempaths.py, 18_build_etcgem_tpc.py, 17_build_measured_tpc.py, FIG4_LOCKED.md, requirements.txt}.
Branch: `git switch -c k1/candida-port main`.

PART A - the four strain folders (data only; no code in a strain folder)
- Create strains/cauris_iRV973/, strains/cparapsilosis_iDC1003/, strains/chaemulonii_draft/,
  strains/cduobushaemulonii_draft/, each with model/, media/, thermal/, dltkcat/, outputs/ and a
  strain.yaml, mirroring strains/mmaripaludis/.
- model/: copy the species' SBML from $CANDIDAS_ROOT/gem/models/ (the rekeyed iRV973, iDC1003, and
  the two KOfam drafts). Record the source path and Candidas commit in strain.yaml. The two drafts'
  strain.yaml must say they are draft reconstructions, not curated models.
- Write ONE converter, tools/reconstruction/to_strain_inputs.py, that produces from gem/tables/:
    dltkcat/kcat_table.csv         (rxn_id, mw_kDa, kcat_s, source, group)
                                    from kcat_reaction_<sp>.csv joined to enzyme_mw_<sp>.csv on
                                    best_gene; source = "dlkcat" or "default_13.7"; group = the
                                    model subsystem if present, else "".
    thermal/enzyme_thermal_params.csv  keyed rxn_id: Topt, Tm, Length, dCpt
                                    Topt/Tm from thermal_topt.csv / thermal_tm.csv via best_gene;
                                    Length from the proteome; dCpt from the shared prior
                                    (dcp_prior_kJ in strain.yaml, as the methanogen does) — the
                                    phenomenological form ignores dCpt; it is written now so K2 needs
                                    no new inputs. Rows for reactions whose gene has no prediction
                                    carry the species-median Topt/Tm with a `source=median` column.
  The converter takes --species and --candidas-root; run it four times; commit its outputs. State
  per species: reactions in the model, reactions with a kcat, with a predicted Topt, with a Tm, and
  how many fell to defaults/medians. These counts must match the standalone's (its README and
  FIG4_LOCKED.md state them); any difference is a finding, report it.
- media/YMS.md documenting the medium exactly as the standalone encodes it (glucose + pooled amino
  acids, biotin), and whatever set_medium needs to apply it; copy the standalone's medium csv into
  media/ as the source of truth.
- thermal/measured_tpc.csv: the measured growth TPC the standalone fits and validates against, taken
  from the output of $CANDIDAS_ROOT/gem/17_build_measured_tpc.py (NOT recomputed), with the Candidas
  commit recorded. Same for measured respiration where it exists, in a second file — copied, unused
  here.
- strain.yaml per species: provider type smoment_gem; model_file; kcat_csv; enzyme_params +
  enzyme_params_key rxn_id; thermal_model: phenomenological; the organism block; T0_C; a
  temperature_grid matching the standalone's sweep (22-44 C); medium name. Proteome-sector block
  DISABLED (the standalone has none; K2 decides). Every value that comes from the standalone carries a
  comment saying so.

PART B - tools/reconstruction/
- Create tools/reconstruction/ and move a COPY of $CANDIDAS_ROOT/gem/01_ … 15_ into it, paths
  generalised: no gempaths.py; every script takes --proteome / --out-strain / --external arguments
  or reads a small reconstruction.yaml; output is a populated strains/<name>/ skeleton. Include its
  own requirements.txt (from the standalone's) and a fetch_external.sh for DLKcat, Seq2Topt/Seq2Tm
  weights and the KOfam database, all gitignored under tools/reconstruction/external/ — same
  convention as DLTKcat/.
- Do NOT run them. Do write tools/reconstruction/README.md: what each step does, its inputs and
  outputs, what it needs fetched, and the order — so that adding a taxon from a proteome is a
  documented procedure. Note explicitly that these tools produce inputs; nothing in them implements
  the model.

PART C - the core: three additions
C1  thermal_model: phenomenological
- Add the third option beside mmrt and unfolding in enzyme_cost.py at each thermal_model dispatch
  point, and thread it through providers.from_gem_smoment / config.build_provider like the others.
  Per-enzyme parameters: Topt, Tm (from enzyme_params). Global parameters: sigma, w (new provider
  keys `pheno_sigma`, `pheno_w`), exposed as calibratable knobs the way the existing globals are.
  act(T) exactly as defined above, floor 1e-6.
- The pool constraint under this form must be the sMOMENT form the standalone uses. Check that the
  core's smoment_gem cost (MW/(kcat*3600) per unit flux from one pool) is the same expression; if
  the core applies any additional factor (sigma saturation, f_metab, a T-dependent pool) that the
  standalone does not, it must be switchable OFF for the K1 match and the strain.yaml must switch it
  off, with a comment. Report exactly what was switched off.
- Existing strains must be untouched: `etcgem tpc --strain eciML1515` and `--strain mmaripaludis`
  produce byte-identical tables before and after this change (verify, do not assert).
C2  etcgem transfer
- New experiment kind in configs/experiments/transfer_candida.yaml:
      kind: transfer
      calibrate_on: cauris_iRV973
      predict: [chaemulonii_draft, cduobushaemulonii_draft, cparapsilosis_iDC1003]
      globals: [pheno_sigma, pheno_w, pool_budget]      # what is fitted on calibrate_on, then frozen
      objective: measured_tpc                           # the strain's thermal/measured_tpc.csv
      optimizer: {method: nelder-mead, multistart: N}   # match the standalone's; state N
      detection_floor_h: 0.05
- New CLI verb `etcgem transfer --experiment transfer_candida`: fit the listed globals on the
  calibrate_on strain against its measured curve, freeze, sweep every strain in predict, write per
  strain outputs/transfer_<exp>/{tpc.csv, resolved_config.yaml} and a top-level
  outputs/transfer_<exp>/summary.csv (per strain: fitted globals, predicted mu at each T, predicted
  thermal limit at the detection floor). Reuse the existing tpc engine; do not write a second solver
  loop.
C3  registration
- README.md: the four strains in the layout tree; `transfer` in the CLI table; `phenomenological` in
  the thermal-model description; tools/reconstruction/ in the layout. prompts/README.md: a K-series
  section with this prompt.

PART D - THE GATE: reproduce the standalone's locked numbers
- Run `etcgem transfer --experiment transfer_candida`.
- Compare against $CANDIDAS_ROOT/gem/FIG4_LOCKED.md, number by number: the fitted (sigma, w, P);
  predicted mu at every temperature for each of the four species; the predicted thermal limit per
  species; the unconstrained-vs-constrained C. auris maximum (2.05 vs 0.76 h^-1 in the standalone).
  State a tolerance BEFORE running (suggest: fitted globals within 2%, mu within 1e-3 h^-1 or 1%
  whichever is larger, limits within 0.2 C) and report every comparison in a table with PASS/FAIL.
- If a number fails: diagnose whether the port differs (a default, a medium bound, a floor, an
  optimizer start, a T grid) and fix the PORT, never the standalone or the tolerance. If it cannot
  be closed, the prompt ends with the mismatch documented, not with a claim of success.
- Write reports/candida_thermal_limit/K1_port_verification.md: the table, the tolerance, what was
  switched off in the core to match, and the exact commands. This file is the evidence that the two
  implementations agree at this one point.

PART E - do NOT
- Do not run K2. Do not enable unfolding/mmrt on the Candida strains. Do not enable proteome sectors.
  Do not re-run DLKcat/Seq2*/KOfam. Do not move gem/audits or gem/notes (that is K3). Do not alter
  any file in $CANDIDAS_ROOT. Do not change any existing strain, experiment or output.

VERIFY (report all)
1. Four strain folders, each listing its files; per-species input counts vs the standalone's.
2. Converter run four times; its outputs committed; the join on best_gene has no unmatched rows
   (or the unmatched rows listed).
3. tools/reconstruction/ present, paths generalised, README written, nothing executed.
4. enzyme_cost.py phenomenological branch: the act(T) expression quoted from the code; what was
   switched off to match sMOMENT; eciML1515 and mmaripaludis tpc tables byte-identical pre/post.
5. `etcgem transfer` runs; the summary.csv; resolved_config.yaml present per strain.
6. THE GATE TABLE: every locked number, port value, tolerance, PASS/FAIL. Overall PASS or the
   documented mismatch.
7. README.md and prompts/README.md updated.
8. `git diff main --stat`: only strains/c*/, tools/reconstruction/, src/etcgem/{enzyme_cost,
   providers, config, cli, transfer}.py, configs/experiments/transfer_candida.yaml,
   reports/candida_thermal_limit/, README.md, prompts/. Nothing else.

CONSTRAINTS
- Port, do not redesign. Where the standalone made a choice (default kcat 13.7, median fill, floor
  1e-6, 22-44 C grid), the port makes the same choice and comments it. K2 is where choices change.
- No code in a strain folder. Anything that implements the method goes in src/etcgem; anything that
  builds inputs goes in tools/reconstruction.
- Existing strains byte-identical. This is checked, not assumed.
- The gate is against FIG4_LOCKED.md as it stands. If the standalone's numbers look wrong, report
  it; do not "fix" them on either side.
- Autonomous; commit in parts:
  "K1: four Candida strain folders + converter (data only)",
  "K1: tools/reconstruction from the standalone gem/ pipeline (not executed)",
  "K1: thermal_model phenomenological; existing strains unchanged",
  "K1: etcgem transfer experiment kind",
  "K1: port verification against FIG4_LOCKED.md",
  "K1: README + prompts index".
```
