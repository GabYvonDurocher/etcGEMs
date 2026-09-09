#!/usr/bin/env python3
"""task3_enzymes.py -- Y2 TASK 3: what the calibration moved, enzyme by enzyme, and which
enzymes carry the thermal limit at the posterior.

    python3 reports/Y2_regime_posterior/task3_enzymes.py --bayesiangem <clone> --results <extracted>

Y1 PART D could only report what the paper says about the prior -> posterior move, because the
paper gives counts, correlations and average widths but no signed shift, and Y1 had no posterior
file. With the posterior in hand the shift is measurable, so this reports it: the signed,
per-enzyme change in Tm and Topt, and the list of enzymes whose posterior mean Tm falls below
42 C -- the set the paper names in Supplementary Fig. 8 and the set its thermal-limit mechanism
rests on.

Reproducing that named list from the file is also a check on the file, independent of the SD
cross-check in TASK 1.

Writes task3_enzyme_shifts.csv (all 764) and task3_low_tm.csv.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from posterior import import_their_code, load_populations, per_enzyme      # noqa: E402

# The nine the paper names: "in the Posterior etcGEMs, only 9 enzymes (1%) with a mean melting
# temperature below 42 C were present (ERG1, ATP1, ALA1, KRS1, SER1, HEM1, PDB1, ADH1, and TRP3)
# (Supplementary Fig. 8)".
PAPER_NINE = ["ERG1", "ATP1", "ALA1", "KRS1", "SER1", "HEM1", "PDB1", "ADH1", "TRP3"]


def gene_map(bg):
    out = {}
    with open(os.path.join(bg, "data", "enzyme_uniprot_gene_name.csv")) as fh:
        for line in fh:
            parts = line.strip().split(",")
            if len(parts) > 1:
                out[parts[0]] = ",".join(parts[1:])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bayesiangem", required=True)
    ap.add_argument("--results", required=True)
    args = ap.parse_args()
    bg = os.path.abspath(args.bayesiangem)
    prior, post, _ = load_populations(args.results, bg)
    _, GEMS = import_their_code(bg)
    pri_table = GEMS.params
    genes = gene_map(bg)

    rows = []
    tm_pri_p, tm_post = per_enzyme(prior, "Tm"), per_enzyme(post, "Tm")
    to_pri_p, to_post = per_enzyme(prior, "Topt"), per_enzyme(post, "Topt")
    for u in tm_post.columns:
        rows.append(dict(
            uniprot=u, gene=genes.get(u, ""),
            Tm_prior_file_C=float(pri_table.loc[u, "Tm"]) - 273.15,
            Tm_prior_measured=bool(pri_table.loc[u, "Tm_std"] < 5),
            Tm_prior_particles_mean_C=float(tm_pri_p[u].mean()) - 273.15,
            Tm_post_mean_C=float(tm_post[u].mean()) - 273.15,
            Tm_post_sd_C=float(tm_post[u].std(ddof=1)),
            Tm_shift_C=float(tm_post[u].mean() - pri_table.loc[u, "Tm"]),
            Topt_prior_file_C=float(pri_table.loc[u, "Topt"]) - 273.15,
            Topt_prior_particles_mean_C=float(to_pri_p[u].mean()) - 273.15,
            Topt_post_mean_C=float(to_post[u].mean()) - 273.15,
            Topt_post_sd_C=float(to_post[u].std(ddof=1)),
            Topt_shift_C=float(to_post[u].mean() - pri_table.loc[u, "Topt"])))
    d = pd.DataFrame(rows).sort_values("Tm_post_mean_C")
    d.to_csv(os.path.join(HERE, "task3_enzyme_shifts.csv"), index=False)

    for f in ("Tm", "Topt"):
        s = d[f + "_shift_C"]
        print(f"[y2t3] {f:5s} shift, posterior mean - prior file, over 764 enzymes: "
              f"mean {s.mean():+6.3f} C  median {s.median():+6.3f}  sd {s.std():5.3f}  "
              f"range [{s.min():+6.2f}, {s.max():+6.2f}]  |  moved down: "
              f"{int((s < 0).sum())}, up: {int((s > 0).sum())}", flush=True)

    lo_post = d[d.Tm_post_mean_C < 42.0]
    lo_pri = d[d.Tm_prior_file_C < 42.0]
    lo_post.to_csv(os.path.join(HERE, "task3_low_tm.csv"), index=False)
    print(f"[y2t3] posterior mean Tm < 42 C: {len(lo_post)} enzymes "
          f"({sorted(lo_post.gene.tolist())})", flush=True)
    print(f"[y2t3] prior file  Tm < 42 C: {len(lo_pri)} enzymes "
          f"({sorted(lo_pri.gene.tolist())})", flush=True)
    got, want = set(lo_post.gene), set(PAPER_NINE)
    print(f"[y2t3] against the paper's nine (Supp. Fig. 8): matched {sorted(got & want)}; "
          f"here but not named {sorted(got - want)}; named but not here {sorted(want - got)}",
          flush=True)
    named = d[d.gene.isin(PAPER_NINE)][
        ["gene", "Tm_prior_file_C", "Tm_prior_measured", "Tm_post_mean_C", "Tm_post_sd_C",
         "Tm_shift_C", "Topt_prior_file_C", "Topt_post_mean_C", "Topt_shift_C"]]
    print("[y2t3] the paper's nine, prior file -> posterior mean:")
    print(named.to_string(index=False))
    json.dump(dict(n_low_posterior=len(lo_post), n_low_prior=len(lo_pri),
                   paper_nine=PAPER_NINE,
                   matched=sorted(got & want), extra=sorted(got - want),
                   missing=sorted(want - got),
                   Tm_shift_mean=float(d.Tm_shift_C.mean()),
                   Tm_shift_median=float(d.Tm_shift_C.median()),
                   Topt_shift_mean=float(d.Topt_shift_C.mean()),
                   Topt_shift_median=float(d.Topt_shift_C.median())),
              open(os.path.join(HERE, "task3_enzymes.json"), "w"), indent=2)
    print("[y2t3] wrote task3_enzyme_shifts.csv, task3_low_tm.csv, task3_enzymes.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
