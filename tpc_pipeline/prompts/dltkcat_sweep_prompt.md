# Claude Code prompt — DLTKcat thermal params → eciML1515 TPC sweep

Paste the block below into Claude Code (run from the `tpc_pipeline` folder).

---

```
You are working in an existing Python project that computes enzyme- and
temperature-constrained genome-scale metabolic TPC (thermal performance curve)
sensitivity sweeps. Your job: obtain REAL per-enzyme thermal parameters
(Topt, dCp) from DLTKcat for the E. coli model eciML1515, apply them to the
model, and run the sweep. Work carefully and verify each step before moving on.

KEY PATHS
- Pipeline package folder (run pipeline commands from here):
  /Users/g.yvon-durocher/Library/CloudStorage/OneDrive-UniversityofExeter/Documents/work/MICROADAPT/etcGEMs/tpc_pipeline
- Model file:
  /Users/g.yvon-durocher/Library/CloudStorage/OneDrive-UniversityofExeter/Documents/work/MICROADAPT/etcGEMs/eciML1515_batch.xml
- Read RUNBOOK.md and README.md in the pipeline folder first — they explain the
  pipeline, the DLTKcat integration, and the CLI subcommands.

ENVIRONMENTS (keep them separate — DLTKcat's torch/rdkit will clash with the
pipeline deps)
- Pipeline: a venv at ./.venv with requirements.txt installed.
- DLTKcat: its own conda/venv with pytorch, rdkit, scikit-learn, pandas.

STEP 1 — Pipeline env + sanity check
- cd into the pipeline folder. Create/activate .venv, pip install -r requirements.txt.
- Run: python -m tpc_pipeline --config configs/example_toy.yaml
- Confirm outputs/toy_run/ figures are produced. Stop and fix if not.

STEP 2 — Generate DLTKcat input from the model
- Run: python -m tpc_pipeline.dltkcat prep --model "<MODEL PATH ABOVE>" \
       --out dltkcat_input.csv --tmin 5 --tmax 55 --n 11
- Confirm dltkcat_input.csv has columns rxn_id, enz, sub, bigg, mnx, Temp_C,
  Temp_K and ~2300 reactions. The rxn_id column MUST be preserved through every
  later DLTKcat step so predictions can be mapped back.

STEP 3 — Set up DLTKcat
- git clone https://github.com/SizheQiu/DLTKcat.git (outside the pipeline folder).
- Create its environment and install pytorch, rdkit, scikit-learn, pandas.
- READ its README, code/feature_functions.py, and especially code/GEMs.ipynb —
  that notebook is the worked example for feeding GEM reactions to DLTKcat at
  multiple temperatures. Do NOT guess the temperature normalization; use exactly
  what their code does (they produce columns 'smiles','seq','Temp_K_norm',
  'Inv_Temp_norm').

STEP 4 — Resolve inputs + predict (DLTKcat env)
- Use their convert_input(path, enz_col='enz', sub_col='sub') on dltkcat_input.csv
  to add 'smiles' and 'seq'. This needs internet (PubChem/UniProt). Log how many
  rows resolve; drop or fix unresolved substrate names, but KEEP rxn_id + Temp_C.
- Apply their temperature normalization, then run:
  python predict.py --input <converted.csv> --output dltkcat_output.csv
  (uses the default pretrained --model_path / --param_dict_pkl). Output is
  log10(kcat) per row. Ensure dltkcat_output.csv still carries rxn_id and Temp_C.
- If you hit the "Index out of range" error at the amino embedding, apply the fix
  noted in their README (+1 to n_atom/n_amino) or retrain per their instructions.

STEP 5 — Fit MMRT + run the sweep (pipeline env)
- python -m tpc_pipeline.dltkcat parse --pred <path>/dltkcat_output.csv \
       --key rxn_id --temp-col Temp_C --out fits.csv
  (log10 assumed; add --no-log10 if the output is raw kcat. If the kcat column
  isn't named 'kcat', pass --kcat-col <name>.)
- Report how many enzymes fit ok (ok/r2 columns) vs fell back to defaults.
- python run_with_fits.py --config configs/eciML1515.yaml --fits fits.csv
- This applies the DLTKcat Topt/dCp to eciML1515 (keeping its calibrated enzyme
  costs) and writes outputs/eciML1515_run_dltkcat/.

STEP 6 — Report
- Print the nominal descriptors (Topt, rmax, CTmax) from
  outputs/eciML1515_run_dltkcat/summary.json and compare them to the
  default-parameter run in outputs/eciML1515_run/summary.json.
- Point me to the new tpc_ensemble.png and sensitivity_heatmap.png, and briefly
  describe how the DLTKcat-derived TPC differs from the default-parameter one
  (peak temperature, breadth, CTmax).

CONSTRAINTS
- Verify the output of each step before proceeding; if a step fails, diagnose and
  report rather than pushing ahead.
- The join key between DLTKcat output and our fitter is rxn_id + Temp_C; if
  convert_input reorders/drops rows, re-join on (enz, sub, Temp_C) to restore rxn_id.
- Don't modify the pipeline's scientific code; only adapt the DLTKcat glue and
  CLI flags as needed.
```
