#!/usr/bin/env python3
"""task1_posterior.py -- Y2 TASK 1: obtain the posterior, and establish it is the right one.

    python3 reports/Y2_regime_posterior/task1_posterior.py \
        --bayesiangem /path/to/BayesianGEM --results /path/to/extracted --archive /path/results.tar.gz

Three things are established here, in order, and the last is a STOP condition.

1. WHAT WAS OBTAINED. DOI, version, file name, size, the md5 Zenodo publishes and the md5 and
   sha256 of what actually landed on disk.

2. THE MAPPING FROM PRIOR TO POSTERIOR IS A FIELD RENAME. Their particles are dicts keyed
   `"<uniprot>_<Tm|Topt|dCpt>"` in the same units as `data/model_enzyme_params.csv`, and their own
   `GEMS.format_input` is what turns one into a thermal-parameter table. Two checks: the identity
   check -- `format_input` given the prior table's OWN values must reproduce
   `etc.calculate_thermal_params(prior)` exactly -- and then one enzyme printed by hand, prior file
   against prior particle against posterior median, before anything is applied to 764.

3. THE SD CROSS-CHECK, WHICH IS THE STOP CONDITION. The paper reports average per-enzyme standard
   deviations, prior -> posterior, of Topt 10.9 -> 7.1 C, Tm 4.9 -> 4.0 C and dCp 2.0 -> 1.8
   kJ/mol/K (Supplementary Fig. 7, quoted in the Results). If the populations in this file do not
   reproduce those, the file or the transform is wrong and Y2 must not proceed.

Writes task1_provenance.json and task1_sd_crosscheck.csv.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tarfile

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from posterior import (FIELDS, PICKLE, import_their_code, load_populations,   # noqa: E402
                       median_particle, per_enzyme)

# What the paper reports (Supplementary Fig. 7, quoted in Results): average per-enzyme SD.
PAPER_SD = {"Topt": (10.9, 7.1), "Tm": (4.9, 4.0), "dCpt": (2.0, 1.8)}   # (prior, posterior)
PAPER_SD_UNITS = {"Topt": "C", "Tm": "C", "dCpt": "kJ/mol/K"}
TOL = {"Topt": 0.6, "Tm": 0.4, "dCpt": 0.3}     # the paper quotes one decimal place


def digest(path):
    md5, sha = hashlib.md5(), hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 22), b""):
            md5.update(chunk)
            sha.update(chunk)
    return md5.hexdigest(), sha.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bayesiangem", required=True)
    ap.add_argument("--results", required=True, help="directory the archive was extracted into")
    ap.add_argument("--archive", default=None, help="results.tar.gz, for its checksums")
    args = ap.parse_args()
    bg = os.path.abspath(args.bayesiangem)
    out = {"zenodo": {"doi": "10.5281/zenodo.3996543",
                      "concept_doi": "10.5281/zenodo.3686995",
                      "record": 3996543, "version": "2.0",
                      "published": "2020-02-25",
                      "title": "Computed results for Bayesian genome scale modelling "
                               "temperature effect on yeast metabolism",
                      "file": "results.tar.gz",
                      "zenodo_md5": "9367d7edcea41ecd50d9fb399f064582"}}

    if args.archive:
        md5, sha = digest(args.archive)
        out["zenodo"].update(bytes=os.path.getsize(args.archive), md5=md5, sha256=sha,
                             md5_matches_zenodo=(md5 == out["zenodo"]["zenodo_md5"]))
        print(f"[y2t1] archive {os.path.getsize(args.archive)} bytes  md5={md5}  "
              f"matches Zenodo: {out['zenodo']['md5_matches_zenodo']}", flush=True)
        with tarfile.open(args.archive, "r:gz") as tf:
            members = [(m.name, m.size) for m in tf if m.isfile()]
        out["archive_members"] = [{"name": n, "bytes": s} for n, s in sorted(members)]
        print(f"[y2t1] archive holds {len(members)} files", flush=True)

    p = os.path.join(args.results, PICKLE)
    md5, sha = digest(p)
    out["posterior_file"] = dict(path=PICKLE, bytes=os.path.getsize(p), md5=md5, sha256=sha)

    prior, post, smc = load_populations(args.results, bg)
    etc, GEMS = import_their_code(bg)
    keys = sorted(prior[0].keys())
    out["populations"] = dict(prior_n=len(prior), posterior_n=len(post),
                              n_parameters=len(keys),
                              n_enzymes=len(keys) // len(FIELDS),
                              fields=list(FIELDS),
                              generations=len(getattr(smc, "epsilons", [])) - 1,
                              final_epsilon=float(smc.epsilons[-1]),
                              simulations=int(getattr(smc, "simulations", -1)))
    print(f"[y2t1] prior n={len(prior)}  posterior n={len(post)}  "
          f"{len(keys)} parameters over {len(keys)//len(FIELDS)} enzymes; "
          f"final epsilon {smc.epsilons[-1]:.6f}", flush=True)

    # --- 2. the mapping -----------------------------------------------------------------
    prior_table = GEMS.params
    identity = {k: float(prior_table.loc[k.rsplit("_", 1)[0], k.rsplit("_", 1)[1]])
                for k in keys}
    df_id, _ = GEMS.format_input(identity)
    df_ref = etc.calculate_thermal_params(prior_table)
    cols = [c for c in df_ref.columns if c in df_id.columns]
    ident_diff = float(np.max(np.abs(df_id[cols].values - df_ref.loc[df_id.index, cols].values)))
    out["identity_check_max_abs_diff"] = ident_diff
    print(f"[y2t1] identity check -- format_input(prior values) vs "
          f"calculate_thermal_params(prior): max abs diff {ident_diff:.3e}", flush=True)

    med = median_particle(post)
    ez = "P32476"                       # ERG1, the paper's headline enzyme
    row = {}
    for f in FIELDS:
        k = f"{ez}_{f}"
        pri_particles = np.array([pp[k] for pp in prior], float)
        post_particles = np.array([pp[k] for pp in post], float)
        row[f] = dict(prior_file=float(prior_table.loc[ez, f]),
                      prior_file_std=float(prior_table.loc[ez, f + "_std"]),
                      prior_particles_mean=float(pri_particles.mean()),
                      prior_particles_sd=float(pri_particles.std(ddof=1)),
                      posterior_median=float(med[k]),
                      posterior_particles_mean=float(post_particles.mean()),
                      posterior_particles_sd=float(post_particles.std(ddof=1)))
    out["one_enzyme"] = {"uniprot": ez, "gene": "ERG1", "values": row}
    print(f"[y2t1] mapping shown on {ez} (ERG1):")
    for f in FIELDS:
        v = row[f]
        u = "K" if f != "dCpt" else "J/mol/K"
        print(f"        {f:5s} prior file {v['prior_file']:9.3f} +/- {v['prior_file_std']:.2f} {u} "
              f"| prior particles {v['prior_particles_mean']:9.3f} +/- {v['prior_particles_sd']:.2f} "
              f"| posterior median {v['posterior_median']:9.3f} "
              f"(mean {v['posterior_particles_mean']:9.3f} +/- {v['posterior_particles_sd']:.2f})",
              flush=True)

    # --- 3. the SD cross-check ----------------------------------------------------------
    rows, ok = [], True
    for f in FIELDS:
        a, b = per_enzyme(prior, f), per_enzyme(post, f)
        scale = 1e-3 if f == "dCpt" else 1.0        # J/mol/K -> kJ/mol/K for the comparison
        sd_prior = float(np.mean(a.std(ddof=1).values)) * scale
        sd_post = float(np.mean(b.std(ddof=1).values)) * scale
        pp, qq = PAPER_SD[f]
        good = abs(sd_prior - pp) <= TOL[f] and abs(sd_post - qq) <= TOL[f]
        ok = ok and good
        rows.append(dict(field=f, units=PAPER_SD_UNITS[f],
                         sd_prior_here=sd_prior, sd_prior_paper=pp,
                         sd_posterior_here=sd_post, sd_posterior_paper=qq,
                         tolerance=TOL[f], matches=good))
        print(f"[y2t1] SD {f:5s} ({PAPER_SD_UNITS[f]:9s}) prior {sd_prior:6.2f} vs paper {pp:5.1f} | "
              f"posterior {sd_post:6.2f} vs paper {qq:5.1f} | {'OK' if good else 'MISMATCH'}",
              flush=True)
    pd.DataFrame(rows).to_csv(os.path.join(HERE, "task1_sd_crosscheck.csv"), index=False)
    out["sd_crosscheck_passes"] = bool(ok)

    with open(os.path.join(HERE, "task1_provenance.json"), "w") as fh:
        json.dump(out, fh, indent=2)
    print(f"[y2t1] wrote task1_provenance.json and task1_sd_crosscheck.csv; "
          f"SD cross-check {'PASSES' if ok else 'FAILS -- STOP'}")
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
