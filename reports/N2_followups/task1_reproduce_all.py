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
            # transfer.run_tag: the output folder is transfer_<exp>, de-doubled when the
            # experiment name already starts with "transfer"
            tag = exp if exp.startswith("transfer") else f"transfer_{exp}"
            J.append((s, tag, [ETC, "transfer", "--experiment", exp]))
        J.append((s, "audit_sinks", [ETC, "audit-sinks", "--strain", s]))
        J.append((s, "audit_sinks_raw", [ETC, "audit-sinks", "--strain", s, "--raw"]))
    for exp in ["candida_pool_unconstrained", "candida_pool_binding"]:
        J.append(("cauris_iRV973", f"fba_{exp}",
                  [ETC, "fba", "--strain", "cauris_iRV973", "--experiment", exp,
                   "--temp", "30"]))
    return J


def numerically_equal(a_bytes, b_path, rtol=1e-9):
    """Do two CSV/JSON files agree to floating-point rounding?

    A byte difference in the last significant digit is rounding, not staleness -- the toy
    strain's rmax comes back as 0.0889448438683759 or ...99 depending on the BLAS build.
    Reporting that as "does not reproduce" would bury a real signal in noise, so exact and
    numeric agreement are reported as separate columns."""
    import math
    import re
    try:
        A = re.findall(r"-?\d+\.?\d*(?:[eE][-+]?\d+)?", a_bytes.decode())
        B = re.findall(r"-?\d+\.?\d*(?:[eE][-+]?\d+)?", open(b_path, "rb").read().decode())
    except Exception:
        return False
    if len(A) != len(B):
        return False
    for x, y in zip(A, B):
        try:
            fx, fy = float(x), float(y)
        except ValueError:
            if x != y:
                return False
            continue
        if math.isnan(fx) and math.isnan(fy):
            continue
        if not math.isclose(fx, fy, rel_tol=rtol, abs_tol=1e-12):
            return False
    return True


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
        diff, numeric_only = [], []
        for f in files:
            if f.endswith(".png"):
                continue        # matplotlib PNGs carry a non-deterministic creation date
            p = os.path.join(ROOT, f)
            if not os.path.exists(p):
                diff.append(os.path.basename(f) + "(missing)")
            elif open(p, "rb").read() != watch.get(f):
                if numerically_equal(watch.get(f, b""), p):
                    numeric_only.append(os.path.basename(f))
                else:
                    diff.append(os.path.basename(f))
        n_cmp = len([f for f in files if not f.endswith(".png")])
        rows.append(dict(strain=s, output=d, n_tracked=len(files), n_compared=n_cmp,
                         reproduces_exact=(len(diff) == 0 and len(numeric_only) == 0),
                         reproduces_numeric=(len(diff) == 0),
                         rounding_only=";".join(sorted(numeric_only)),
                         differing=";".join(sorted(diff))))
        status = ("OK" if not diff and not numeric_only else
                  ("OK (rounding: " + ";".join(numeric_only) + ")" if not diff else
                   "DIFFERS: " + ";".join(diff)))
        print(f"  {s:24s} {d:30s} {status}", flush=True)

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
    n_bad = int((T.reproduces_numeric == False).sum())
    print(f"\n{len(T)} committed output directories checked; "
          f"{int((T.reproduces_exact == True).sum())} reproduce byte-for-byte, "
          f"{int((T.reproduces_numeric == True).sum())} reproduce to floating-point "
          f"rounding, {n_bad} do not reproduce")
    print("wrote", os.path.join(HERE, "task1_reproduction_table.csv"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
