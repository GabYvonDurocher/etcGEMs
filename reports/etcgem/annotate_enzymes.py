"""Augment the tuned control / identifiability tables with local enzyme identities.

Adds a gene symbol, a short enzyme/protein name and (where available) an EC number to
each rxn_id/enzyme_id row, sourced ENTIRELY from local files — no web fetch:

* enzyme/protein NAME  <- the ecModel reaction .name (GECKO isozyme suffixes stripped);
* gene SYMBOL          <- the measured proteomics table (b-number -> genename), joined
                          through the model's reaction->gene (b-number) map;
* UniProt accession     <- the enzyme_id already in the table;
* EC number             <- the ecModel reaction annotation if present (it is not stored
                          in this GECKO build, so left blank rather than invented).

Writes *_annotated.csv next to the source tables. Idempotent; re-run any time.
"""
from __future__ import annotations

import os
import re
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
MODEL = os.path.join(ROOT, "strains", "eciML1515", "model", "eciML1515_batch.xml")
PROT = os.path.join(ROOT, "strains", "eciML1515", "proteomics", "tem_proteomic.csv")
CTRL = os.path.join(ROOT, "strains", "eciML1515", "outputs", "control_tuned")


def _clean_name(name: str) -> str:
    s = re.sub(r"\s*\(No\d+\)\s*$", "", str(name))          # drop GECKO isozyme tag
    s = s.replace(" (reversible)", "")
    return s.strip()


def _rxn_base(rid: str) -> str:
    return re.sub(r"(No\d+)?(_REV)?$", "", str(rid))


def build_maps():
    sys.path.insert(0, os.path.join(ROOT, "src"))
    from etcgem.providers import _load_any
    m = _load_any(MODEL)
    prot = pd.read_csv(PROT)
    bgene = {a: str(g) for a, g in zip(prot["Accession"], prot["genename"]) if isinstance(g, str)}

    def annot(rid):
        r = None
        for cand in (rid, _rxn_base(rid)):
            if cand in m.reactions:
                r = m.reactions.get_by_id(cand)
                break
        if r is None:
            return "", "", ""
        bs = [g.id for g in r.genes]
        gene = ";".join(sorted({bgene[b] for b in bs if b in bgene}))
        ec = r.annotation.get("ec-code", "")
        if isinstance(ec, list):
            ec = ";".join(ec)
        return gene, _clean_name(r.name), (ec or "")
    return annot


def augment(path_in, path_out, annot, front_cols):
    df = pd.read_csv(path_in)
    ann = df["rxn_id"].map(lambda r: annot(r))
    df.insert(df.columns.get_loc("rxn_id") + 1, "gene", [a[0] for a in ann])
    df.insert(df.columns.get_loc("gene") + 1, "enzyme_name", [a[1] for a in ann])
    df["EC"] = [a[2] for a in ann]
    # bring the identity columns to the front for readability
    cols = [c for c in front_cols if c in df.columns] + \
           [c for c in df.columns if c not in front_cols]
    df[cols].to_csv(path_out, index=False)
    return len(df), int((df["gene"] != "").sum())


def main():
    annot = build_maps()
    n1, g1 = augment(os.path.join(CTRL, "thermal_control.csv"),
                     os.path.join(CTRL, "thermal_control_annotated.csv"), annot,
                     ["rank", "gene", "enzyme_name", "enzyme_id", "rxn_id", "EC", "thermal_screen"])
    n2, g2 = augment(os.path.join(CTRL, "identifiability.csv"),
                     os.path.join(CTRL, "identifiability_annotated.csv"), annot,
                     ["gene", "enzyme_name", "enzyme_id", "rxn_id", "EC", "parameter",
                      "ident", "identifiable_from_growth", "refined"])
    print(f"[annotate] thermal_control: {n1} rows, {g1} with a gene symbol")
    print(f"[annotate] identifiability: {n2} rows, {g2} with a gene symbol")


if __name__ == "__main__":
    main()
