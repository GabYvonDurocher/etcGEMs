# Running the TPC pipeline on your Mac — step by step

All commands are for the macOS Terminal. Copy-paste as-is (paths are quoted
because the folder name has spaces).

---

## Part A — Set up and run the pipeline

### 1. Open Terminal and go to the package folder

```bash
cd "/Users/g.yvon-durocher/Library/CloudStorage/OneDrive-UniversityofExeter/Documents/work/MICROADAPT/etcGEMs/tpc_pipeline"
```

### 2. Create a virtual environment and install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

This installs cobrapy, numpy, scipy, pandas, matplotlib, pyyaml. The GLPK LP
solver ships with cobrapy — nothing else to install. (Re-activate later with
`source .venv/bin/activate` whenever you open a new Terminal.)

### 3. Smoke-test offline (no model file needed)

```bash
python -m tpc_pipeline --config configs/example_toy.yaml
```

Writes `outputs/toy_run/` with `tpc_ensemble.png`, `sensitivity_heatmap.png`,
`descriptors.csv`, etc. If those appear, the install works.

### 4. Run the real E. coli sweep (eciML1515)

The config already points at `../eciML1515_batch.xml`. Just run:

```bash
python -m tpc_pipeline --config configs/eciML1515.yaml
```

Takes a few minutes (120 samples x 53 temperatures). Outputs land in
`outputs/eciML1515_run/`: the TPC ensemble, sensitivity heatmap, descriptor
distributions, and `summary.json`. Edit `configs/eciML1515.yaml` to change the
temperature grid, sample count, parameter ranges, `pool_scale`, or `default_dCp`.

That is the whole forward pipeline. Part B adds real per-enzyme thermal data.

---

## Part B — Add DLTKcat thermal parameters (optional, advanced)

DLTKcat is a separate deep-learning repo with heavy dependencies (PyTorch,
RDKit). Keep it in its **own environment** so it doesn't clash with the pipeline.

### 1. Generate DLTKcat's input from your model

Back in the `tpc_pipeline` folder with `.venv` active:

```bash
python -m tpc_pipeline.dltkcat prep \
  --model "/Users/g.yvon-durocher/Library/CloudStorage/OneDrive-UniversityofExeter/Documents/work/MICROADAPT/etcGEMs/eciML1515_batch.xml" \
  --out dltkcat_input.csv --tmin 5 --tmax 55 --n 11
```

Produces `dltkcat_input.csv` with columns `rxn_id, enz, sub, bigg, mnx, Temp_C,
Temp_K` (~2340 reactions x 11 temps). Keep the `rxn_id` column through the next
steps so predictions map back.

### 2. Set up DLTKcat and predict

```bash
cd ..                       # leave tpc_pipeline
git clone https://github.com/SizheQiu/DLTKcat.git
cd DLTKcat
# create its environment (conda recommended), then install:
#   pytorch, scikit-learn, rdkit, pandas
```

Then follow DLTKcat's own workflow — its **`/code/GEMs.ipynb` notebook is the
worked example for exactly this** (feeding GEM reactions in at different
temperatures). In short (per its README):

1. `convert_input("dltkcat_input.csv", enz_col='enz', sub_col='sub')` — adds
   `smiles` and `seq` columns (resolved from the UniProt id + substrate name).
2. Normalise temperature to `Temp_K_norm` and `Inv_Temp_norm` (the notebook /
   `code/feature_functions.py` show the exact normalisation used in training).
3. Predict:
   ```bash
   python predict.py --input dltkcat_input_converted.csv --output dltkcat_output.csv
   ```
   (uses the default pretrained `--model_path` / `--param_dict_pkl`.) Output is
   log10(kcat) per row. Make sure `rxn_id` and `Temp_C` are carried into the
   output file.

### 3. Fit MMRT and run the sweep with real thermal params

Back in `tpc_pipeline` with `.venv` active:

```bash
python -m tpc_pipeline.dltkcat parse \
  --pred /path/to/dltkcat_output.csv --key rxn_id --temp-col Temp_C --out fits.csv

python run_with_fits.py --config configs/eciML1515.yaml --fits fits.csv
```

`parse` fits Topt/dCp per reaction (log10 input by default; add `--no-log10` if
your output is raw kcat). `run_with_fits.py` applies those parameters to the
model — keeping its calibrated enzyme costs — and runs the sweep into
`outputs/eciML1515_run_dltkcat/`.

Check the `ok`/`r2` columns in `fits.csv`: DLTKcat is noisy (R²≈0.6), so
reactions with a poor or non-peaked fit are flagged and fall back to the default
thermal knobs instead of injecting garbage.

---

## Troubleshooting

- **`ModuleNotFoundError: tpc_pipeline`** — you must run from inside the
  `tpc_pipeline` folder (the one containing the `tpc_pipeline/` package and
  `configs/`), with `.venv` active.
- **Model file not found** — confirm `eciML1515_batch.xml` is fully downloaded
  from OneDrive (not a cloud-only placeholder) and the path in
  `configs/eciML1515.yaml` matches its location.
- **Sweep feels slow** — lower `n_samples` or the temperature-grid `n` in the
  config; `solver_timeout` (seconds) caps any single hard LP.
- **Want faster solves** — optional: install the `gurobipy` or CPLEX solver;
  cobrapy will pick it up automatically. Not required.
