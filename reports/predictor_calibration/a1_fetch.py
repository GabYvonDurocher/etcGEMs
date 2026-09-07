#!/usr/bin/env python3
"""a1_fetch.py -- A1 PART 0: acquire the measured benchmark and the two yeast proteomes.

Every species-specific input the Candida etcGEM has comes from a sequence predictor, and
Figure 4's conclusion rests on one number one of them produced. To ask whether that
predictor can resolve a difference of that size, it has to be scored against MEASUREMENT.
This fetches the measurement.

    python3 reports/predictor_calibration/a1_fetch.py [--data-dir DIR]

Downloads into DIR (default tools/reconstruction/external/a1_data/, gitignored) and writes
reports/predictor_calibration/DATA_PROVENANCE.md. Nothing is substituted: if a source is
unavailable the script says which file it wanted and stops.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import zipfile
from datetime import date

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DATA = os.path.join("tools", "reconstruction", "external", "a1_data")

MELTOME_URL = ("https://raw.githubusercontent.com/J-SNACKKB/FLIP/main/splits/meltome/"
               "full_dataset.json.zip")
UNIPROT_FIELDS = "accession,id,protein_name,gene_names,organism_name,length,sequence"
PROTEOMES = {
    "scerevisiae": dict(upid="UP000002311", label="Saccharomyces cerevisiae S288c"),
    "suvarum": dict(upid="UP001162085", label="Saccharomyces uvarum (S. bayanus var. uvarum)"),
}
MELTOME_RUN = "Saccharomyces cerevisiae lysate"


def sh(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"FAILED: {cmd}\n{r.stderr[:2000]}")
    return r.stdout


def md5(path, chunk=1 << 20):
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for b in iter(lambda: fh.read(chunk), b""):
            h.update(b)
    return h.hexdigest()


def fetch(url, dest):
    if os.path.exists(dest):
        print(f"  have {os.path.basename(dest)}")
        return dest
    print(f"  GET {url}")
    sh(f'curl -sfL --retry 3 -o "{dest}" "{url}"')
    if not os.path.exists(dest) or os.path.getsize(dest) == 0:
        sys.exit(f"download produced nothing: {url}")
    return dest


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data-dir", default=DEFAULT_DATA)
    a = ap.parse_args(argv)
    D = os.path.abspath(a.data_dir)
    os.makedirs(D, exist_ok=True)
    prov = []

    # --- 1. the measured meltome -------------------------------------------------
    print("[1] Meltome Atlas (Jarzab 2020), via the FLIP benchmark's redistribution")
    z = fetch(MELTOME_URL, os.path.join(D, "full_dataset.json.zip"))
    j = os.path.join(D, "full_dataset.json")
    if not os.path.exists(j):
        with zipfile.ZipFile(z) as zf:
            zf.extractall(D)
    rows = json.load(open(j))
    # NB: the JSON encodes some melting points as the literal NaN, which json.load returns
    # as float('nan') and which `is not None` does not catch. Filter on finite instead.
    import math
    sub = [r for r in rows if r.get("runName") == MELTOME_RUN
           and r.get("meltingPoint") is not None
           and isinstance(r["meltingPoint"], (int, float))
           and math.isfinite(r["meltingPoint"])]
    mt = pd.DataFrame([dict(proteinId=r["proteinId"],
                            uniprotAccession=r.get("uniprotAccession"),
                            meltingPoint=r["meltingPoint"]) for r in sub])
    mt.to_csv(os.path.join(D, "meltome_scerevisiae.csv"), index=False)
    print(f"    {len(rows)} entries; run '{MELTOME_RUN}' -> {len(mt)} proteins with a Tm")
    prov.append(dict(
        file="full_dataset.json.zip -> meltome_scerevisiae.csv",
        what=f"Meltome Atlas melting points, run '{MELTOME_RUN}'",
        source=MELTOME_URL,
        upstream="Jarzab et al. 2020, Nat Methods 17:495-503, doi:10.1038/s41592-020-0801-4; "
                 "PRIDE PXD011929. Redistributed by the FLIP benchmark (J-SNACKKB/FLIP, "
                 "splits/meltome), which obtained it from "
                 "http://meltomeatlas.proteomics.wzw.tum.de:5003",
        entries=f"{len(rows)} total, {len(mt)} S. cerevisiae proteins with a melting point",
        namespace="UniProt accession (uniprotAccession field)", md5=md5(z)))

    # --- 2. the two proteomes ----------------------------------------------------
    for key, meta in PROTEOMES.items():
        print(f"[2] UniProt reference proteome {meta['upid']} ({meta['label']})")
        url = (f"https://rest.uniprot.org/uniprotkb/stream?query=proteome:{meta['upid']}"
               f"&format=tsv&fields={UNIPROT_FIELDS}")
        dest = os.path.join(D, f"proteome_{key}.tsv")
        fetch(url, dest)
        df = pd.read_csv(dest, sep="\t")
        print(f"    {len(df)} entries")
        prov.append(dict(
            file=os.path.basename(dest), what=f"{meta['label']} reference proteome",
            source=url, upstream=f"UniProt proteome {meta['upid']}",
            entries=f"{len(df)} proteins", namespace="UniProt accession", md5=md5(dest)))

    # --- 3. the C. auris clade proteomes (PART D's noise floor) -------------------
    croot = os.environ.get("CANDIDAS_ROOT")
    clades = []
    if croot:
        for c in ("I", "II", "III", "IV"):
            p = os.path.join(croot, "phylo", "proteomes", f"auris_clade{c}.faa")
            if os.path.exists(p):
                n = sum(1 for line in open(p) if line.startswith(">"))
                clades.append((f"auris_clade{c}.faa", n, md5(p)))
    if clades:
        print(f"[3] C. auris clade proteomes: {', '.join(f'{n} ({c})' for c, n, _ in clades)}")
        prov.append(dict(
            file=", ".join(c for c, _, _ in clades),
            what="the four C. auris clade proteomes (PART D, the same-species noise floor)",
            source="$CANDIDAS_ROOT/phylo/proteomes/ (read-only; not copied)",
            upstream="NCBI RefSeq, as assembled by the Candidas project",
            entries="; ".join(f"{c}: {n} proteins" for c, n, _ in clades),
            namespace="RefSeq XP_ accession", md5="; ".join(h[:8] for _, _, h in clades)))
    else:
        print("[3] WARNING: $CANDIDAS_ROOT clade proteomes not found; PART D cannot run")

    # --- 4. the measured interspecies benchmark ----------------------------------
    prov.append(dict(
        file="(none -- summary statistic only)",
        what="measured S. cerevisiae vs S. uvarum proteome-wide mean ortholog dTm",
        source="NOT OBTAINED AS PER-PROTEIN DATA",
        upstream="Walunjkar et al. 2025, Mol Biol Evol 42:msaf137, 'Pervasive Divergence in "
                 "Protein Thermostability is Mediated by Both Structural Changes and Cellular "
                 "Environments'. The value used throughout Figure 4 and here is the "
                 "PARENTAL-CONTEXT mean: 1.6 C over 827 ortholog pairs, 85% of S. cerevisiae "
                 "proteins more thermostable, alongside an 8 C difference in growth thermal "
                 "limit (IT50). Provenance taken from $CANDIDAS_ROOT/gem/FIG4_etcgem_caption.md "
                 "lines 72-75 and 250-257.",
        entries="summary statistic only: mean 1.6 C, n = 827 pairs",
        namespace="n/a", md5="n/a"))

    with open(os.path.join(HERE, "DATA_PROVENANCE.md"), "w") as fh:
        fh.write(f"# A1 — data provenance\n\n_Fetched {date.today().isoformat()} by "
                 f"`reports/predictor_calibration/a1_fetch.py`. Raw files live in "
                 f"`{a.data_dir}`, which is gitignored._\n\n")
        fh.write("**Nothing here is substituted.** Where a source publishes only a summary "
                 "statistic, that is recorded as such and the analysis that depends on it is "
                 "marked weaker in the report.\n\n")
        for p in prov:
            fh.write(f"## {p['what']}\n\n")
            fh.write(f"| | |\n|---|---|\n")
            fh.write(f"| file | `{p['file']}` |\n")
            fh.write(f"| retrieved from | {p['source']} |\n")
            fh.write(f"| original source | {p['upstream']} |\n")
            fh.write(f"| entries | {p['entries']} |\n")
            fh.write(f"| identifier namespace | {p['namespace']} |\n")
            fh.write(f"| md5 | `{p['md5']}` |\n\n")
    print("\nwrote", os.path.join(HERE, "DATA_PROVENANCE.md"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
