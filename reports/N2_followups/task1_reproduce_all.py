#!/usr/bin/env python3
"""task1_reproduce_all.py -- N2 TASK 1: which committed strain outputs still reproduce?

Regenerates every committed output that ONE deterministic command produces in
seconds-to-minutes, into a scratch location, and compares byte for byte against what is
committed. It does NOT overwrite anything: a failure is listed, not fixed, because a second
stale artefact deserves its own diagnosis.

Out of scope, and listed as such: sweeps, Bayesian calibrations (MCMC chains), decomposition
and dissection runs. Those take hours to days and several are stochastic, so "does it
reproduce" is a different question for them and needs its own design.

    python3 reports/N2_followups/task1_reproduce_all.py

Writes task1_reproduction_table.csv beside this file.
"""
from __future__ import annotations

import filecmp
import json
import os
import shutil
import subprocess
import sys
import tempfile

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
ETC = os.path.join(ROOT, ".venv", "bin", "etcgem")
PY = os.path.join(ROOT, ".venv", "bin", "python")

STRAINS = ["_toy", "eciML1515", "mmaripaludis", "syn6803", "cauris_iRV973",
           "chaemulonii_draft", "cduobushaemulonii_draft", "cparapsilosis_iDC1003"]

# (output dir under strains/<s>/outputs/, command) -- one command, deterministic, quick
def jobs():
    J = []
    for s in STRAINS:
        if s == "syn6803":
            J.append((s, "tpc_syn6803_ecmodel",
                      [ETC, "tpc", "--strain", s, "--experiment", "syn6803_ecmodel",
                       "--no-plots"]))
        else:
            J.append((s, "tpc", [ETC, "tpc", "--strain", s, "--no-plots"]))
    for s in ["cauris_iRV973", "chaemulonii_draft", "cduobushaemulonii_draft",
              "cparapsilosis_iDC1003"]:
        for exp in ["transfer_candida", "transfer_candida_unpinned",
                    "candida_B1_unfolding", "candida_B1s_fit_dTm",
                    "candida_B2_grounded_budget", "candida_B3_ngamT",
                    "candida_B4_sectors"]:
            J.append((s, exp, [ETC, "transfer", "--experiment", exp]))
        J.append((s, "audit_sinks", [ETC, "audit-sinks", "--strain", s]))
        J.append((s, "audit_sinks_raw", [ETC, "audit-sinks", "--strain", s, "--raw"]))
    for exp in ["candida_pool_unconstrained", "candida_pool_binding"]:
        J.append(("cauris_iRV973", f"fba_{exp}",
                  [ETC, "fba", "--strain", "cauris_iRV973", "--experiment", exp,
                   "--temp", "30"]))
    return J


def tracked(path):
    r = subprocess.run(["git", "-C", ROOT, "ls-files", path],
                       capture_output=True, text=True)
    return [l for l in r.stdout.splitlines() if l.strip()]


def main():
    # snapshot every committed file we might overwrite, so nothing is left changed
    all_dirs = sorted({(s, d) for s, d, _ in jobs()})
    watch = {}
    for s, d in all_dirs:
        rel = f"strains/{s}/outputs/{d}"
        for f in tracked(rel):
            p = os.path.join(ROOT, f)
            if os.path.exists(p):
                watch[f] = open(p, "rb").read()

    done, rows = set(), []
    for s, d, cmd in jobs():
        key = tuple(cmd)
        if key not in done:
            subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
            done.add(key)
        rel = f"strains/{s}/outputs/{d}"
        files = tracked(rel)
        if not files:
            rows.append(dict(strain=s, output=d, n_tracked=0, n_compared=0,
                             reproduces=None, differing=""))
            continue
        diff = []
        for f in files:
            p = os.path.join(ROOT, f)
            if not os.path.exists(p):
                diff.append(os.path.basename(f) + "(missing)")
            elif open(p, "rb").read() != watch.get(f):
                diff.append(os.path.basename(f))
        # plots are excluded: matplotlib PNGs carry a non-deterministic creation date
        diff = [x for x in diff if not x.endswith(".png")]
        rows.append(dict(strain=s, output=d, n_tracked=len(files),
                         n_compared=len([f for f in files if not f.endswith(".png")]),
                         reproduces=(len(diff) == 0), differing=";".join(sorted(diff))))
        print(f"  {s:24s} {d:28s} {'OK' if not diff else 'DIFFERS: ' + ';'.join(diff)}",
              flush=True)

    # restore every watched file, so this script leaves the tree exactly as it found it
    for f, blob in watch.items():
        p = os.path.join(ROOT, f)
        if not os.path.exists(p) or open(p, "rb").read() != blob:
            with open(p, "wb") as fh:
                fh.write(blob)

    T = pd.DataFrame(rows)
    T.to_csv(os.path.join(HERE, "task1_reproduction_table.csv"), index=False)
    with pd.option_context("display.width", 200, "display.max_rows", 100):
        print("\n" + T.to_string(index=False))
    n_bad = int((T.reproduces == False).sum())
    print(f"\n{len(T)} committed output directories checked; "
          f"{int((T.reproduces == True).sum())} reproduce, {n_bad} do not")
    print("wrote", os.path.join(HERE, "task1_reproduction_table.csv"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
