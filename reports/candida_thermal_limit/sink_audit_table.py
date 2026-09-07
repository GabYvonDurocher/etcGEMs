#!/usr/bin/env python3
"""sink_audit_table.py -- K2 PART E: the uncosted-energy-sink audit across all seven strains.

Reads the JSON each `etcgem audit-sinks` run wrote and assembles one table. Run first:

    for s in eciML1515 mmaripaludis cauris_iRV973 chaemulonii_draft \\
             cduobushaemulonii_draft cparapsilosis_iDC1003 ; do
        etcgem audit-sinks --strain $s ; etcgem audit-sinks --strain $s --raw
    done
    etcgem audit-sinks --strain syn6803 --experiment syn6803_ecmodel
    etcgem audit-sinks --strain syn6803 --experiment syn6803_ecmodel --raw

`configured` is the model as that strain actually runs, after whatever correction its
strain.yaml applies; `raw` is the reconstruction as published, with close_free_sinks,
relax_pinned and pin_at_ub all switched off. The difference between the two columns is what
each strain's bespoke fix was doing -- which is the check that this audit would have found
all three by itself.
"""
from __future__ import annotations

import json
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
STRAINS = [("eciML1515", "audit_sinks", "Escherichia coli K-12"),
           ("mmaripaludis", "audit_sinks", "Methanococcus maripaludis"),
           ("syn6803", "audit_sinks_syn6803_ecmodel", "Synechocystis sp. PCC 6803"),
           ("cauris_iRV973", "audit_sinks", "Candidozyma auris"),
           ("chaemulonii_draft", "audit_sinks", "C. haemulonii (DRAFT)"),
           ("cduobushaemulonii_draft", "audit_sinks", "C. duobushaemulonii (DRAFT)"),
           ("cparapsilosis_iDC1003", "audit_sinks", "Candida parapsilosis")]
CLASSES = [("A", "class_A_count", "uncosted, can produce ATP/NAD(P)H/Fd_red"),
           ("B", "class_B_count", "reversible maintenance/ATPM"),
           ("C", "class_C_count", "hard-pinned uncosted drain"),
           ("D", "class_D_count", "uncosted consumer of a terminal e- acceptor")]


def main():
    rows, notes = [], []
    for strain, tag, organism in STRAINS:
        for mode, suffix in (("configured", ""), ("raw", "_raw")):
            f = f"strains/{strain}/outputs/{tag}{suffix}/sink_audit.json"
            if not os.path.exists(f):
                print(f"  (missing {f})", file=sys.stderr)
                continue
            d = json.load(open(f))
            row = dict(strain=strain, organism=organism, mode=mode,
                       reactions=d["n_reactions"], costed=d["n_costed"],
                       uncosted=d["n_uncosted"],
                       uncosted_frac=round(d["n_uncosted"] / d["n_reactions"], 3))
            for c, key, _ in CLASSES:
                row[c] = d[key]
            rows.append(row)
            for r in d["class_B_reversible_maintenance"]:
                notes.append(dict(strain=strain, mode=mode, cls="B", reaction=r["reaction"],
                                  bounds=f"[{r['lower_bound']:g}, {r['upper_bound']:g}]",
                                  detail=r.get("name") or ""))
            for r in d["class_C_pinned_uncosted"]:
                notes.append(dict(strain=strain, mode=mode, cls="C", reaction=r["reaction"],
                                  bounds=f"[{r['lower_bound']:g}, {r['upper_bound']:g}]",
                                  detail=("FIXED" if r.get("fixed") else "forced >= lb")
                                         + " " + (r.get("name") or "")))
    T = pd.DataFrame(rows)
    T.to_csv(os.path.join(HERE, "sink_audit_table.csv"), index=False)
    N = pd.DataFrame(notes)
    if len(N):
        N.to_csv(os.path.join(HERE, "sink_audit_hits.csv"), index=False)
    with pd.option_context("display.width", 220):
        print(T.to_string(index=False))
        print("\nclass definitions:")
        for c, _, desc in CLASSES:
            print(f"  {c}  {desc}")
        if len(N):
            print("\nevery class B and C hit, in full:")
            print(N.to_string(index=False))
    print("\nwrote", os.path.join(HERE, "sink_audit_table.csv"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
