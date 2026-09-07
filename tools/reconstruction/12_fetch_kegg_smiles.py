#!/usr/bin/env python3
"""12_fetch_kegg_smiles.py - get SMILES for the KEGG compounds the DLKcat run needs.
Run on the Mac (internet):  python3 tools/reconstruction/12_fetch_kegg_smiles.py
Reads <work>/inputs/kegg_compounds_needed.txt, writes <work>/inputs/kegg_smiles.tsv (kegg<TAB>SMILES).
Needs rdkit (conda install -c conda-forge rdkit) + requests. ~1000 compounds, ~10 min.

PORTED from the standalone Candida etcGEM (Candidas repository, `gem/`) into
tools/reconstruction/ by K1. The ONLY change is that the layout and the taxon map now
come from a reconstruction config (paths.py / reconstruction.yaml) instead of the
standalone's fixed gempaths.py, so this step can build the inputs for any taxon. The
method is unchanged; nothing here implements the model.
"""
import time, requests
from pathlib import Path
from rdkit import Chem
from paths import *  # PROJECT, WORK, INPUTS, MODELS, TABLES, EXTERNAL, NOTES,
                    # PROTEOMES, PROTEOME, SP, STRAIN_OUT, load_proteome
cli_configure()     # --config/--work/--external/--proteomes/--out-strain (paths.py)
cids=[l.strip() for l in open(INPUTS / "kegg_compounds_needed.txt") if l.strip()]
out=open(INPUTS / "kegg_smiles.tsv","w"); ok=miss=0
for i,c in enumerate(cids,1):
    try:
        mol=requests.get(f"https://rest.kegg.jp/get/cpd:{c}/mol",timeout=30).text
        m=Chem.MolFromMolBlock(mol)
        if m: out.write(f"{c}\t{Chem.MolToSmiles(m)}\n"); ok+=1
        else: miss+=1
    except Exception: miss+=1
    if i%100==0: print(f"  {i}/{len(cids)}  ok={ok} miss={miss}",flush=True); out.flush()
    time.sleep(0.15)
out.close(); print(f"done: {ok} SMILES, {miss} missing -> <work>/inputs/kegg_smiles.tsv")
