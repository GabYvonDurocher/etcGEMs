#!/usr/bin/env python3
"""a1_orthologs.py -- reciprocal-best-hit ortholog pairs for A1's PARTs C, D and E.

Two pairings are needed and they are the same operation:

  PART C  S. cerevisiae <-> S. uvarum, the interspecies test against a MEASURED benchmark.
  PART D  all six pairs of the four C. auris clades, the same-species noise floor. Their
          proteomes are 99.4-100% identical, so their true pairwise Tm difference is ~0 and
          whatever the predictor returns for them is its floor on this kind of comparison.

Uses tools/reconstruction/07_rbh_orthologs.py's rbh_pairs (DIAMOND blastp, --sensitive,
e < 1e-10, reciprocity required) -- the same procedure the Candida pipeline uses, so the
noise floor is measured through the same pairing machinery as the estimate it calibrates.

    python3 reports/predictor_calibration/a1_orthologs.py

Writes <data>/orthologs/*.tsv (id_a, id_b, percent identity).
"""
from __future__ import annotations

import argparse
import os
import statistics
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools", "reconstruction"))
DEFAULT_DATA = os.path.join(ROOT, "tools", "reconstruction", "external", "a1_data")
CLADES = ["I", "II", "III", "IV"]


def tsv_to_fasta(tsv, fasta):
    if os.path.exists(fasta):
        return fasta
    t = pd.read_csv(tsv, sep="\t").dropna(subset=["Sequence"])
    with open(fasta, "w") as fh:
        for _, r in t.iterrows():
            fh.write(f">{r['Entry']}\n{r['Sequence']}\n")
    return fasta


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data-dir", default=DEFAULT_DATA)
    ap.add_argument("--candidas-root", default=os.environ.get("CANDIDAS_ROOT"))
    a = ap.parse_args(argv)
    D = os.path.abspath(a.data_dir)
    out = os.path.join(D, "orthologs")
    os.makedirs(out, exist_ok=True)

    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "rbh07", os.path.join(ROOT, "tools", "reconstruction", "07_rbh_orthologs.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    jobs = []
    sc = tsv_to_fasta(os.path.join(D, "proteome_scerevisiae.tsv"),
                      os.path.join(D, "proteome_scerevisiae.faa"))
    su = tsv_to_fasta(os.path.join(D, "proteome_suvarum.tsv"),
                      os.path.join(D, "proteome_suvarum.faa"))
    jobs.append(("scerevisiae__suvarum", sc, su))
    if a.candidas_root:
        pr = os.path.join(a.candidas_root, "phylo", "proteomes")
        for i, ci in enumerate(CLADES):
            for cj in CLADES[i + 1:]:
                jobs.append((f"auris_clade{ci}__clade{cj}",
                             os.path.join(pr, f"auris_clade{ci}.faa"),
                             os.path.join(pr, f"auris_clade{cj}.faa")))
        # C. auris clade I against each relative: the interspecies difference Figure 4 rests
        # on, measured PROTEOME-WIDE here rather than over the standalone's model-enzyme
        # subset, so it sits on the same footing as the S. cerevisiae / S. uvarum benchmark
        # and the clade noise floor -- same pairing, same predictor run, same protocol.
        for rel in ("haemulonii", "duobushaemulonii", "parapsilosis"):
            jobs.append((f"auris_cladeI__{rel}",
                         os.path.join(pr, "auris_cladeI.faa"),
                         os.path.join(pr, f"{rel}.faa")))
    else:
        print("WARNING: no $CANDIDAS_ROOT; the PART D clade pairs are skipped",
              file=sys.stderr)

    rows = []
    for tag, fa, fb in jobs:
        dest = os.path.join(out, f"{tag}.tsv")
        if os.path.exists(dest):
            pairs = [tuple(l.rstrip("\n").split("\t")) for l in open(dest)]
            pairs = [(a_, b_, float(p)) for a_, b_, p in pairs]
        else:
            print(f"[rbh] {tag}", flush=True)
            pairs = mod.rbh_pairs(fa, fb, tag=tag)
            with open(dest, "w") as fh:
                for a_, b_, p in pairs:
                    fh.write(f"{a_}\t{b_}\t{p:.1f}\n")
        med = statistics.median(p for _, _, p in pairs) if pairs else float("nan")
        rows.append(dict(pair=tag, n_pairs=len(pairs), median_identity_pct=round(med, 2)))
        print(f"  {tag:34s} {len(pairs):5d} pairs, median identity {med:.1f}%")
    pd.DataFrame(rows).to_csv(os.path.join(HERE, "ortholog_pairs.csv"), index=False)
    print("\nwrote", os.path.join(HERE, "ortholog_pairs.csv"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
