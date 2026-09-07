#!/usr/bin/env python3
"""gate_table.py -- K1's gate: every locked number of the standalone Candida etcGEM
against the port's value, with the tolerance and a PASS/FAIL.

The comparison is made against the standalone AS IT STANDS, in the Candidas repository at
the commit recorded in each strain.yaml. It reads that repository read-only; it changes
nothing on either side. Run from the project root, after

    etcgem transfer --experiment transfer_candida
    etcgem transfer --experiment transfer_candida_pinned_maint
    etcgem fba --strain cauris_iRV973 --experiment candida_pool_unconstrained --temp 30
    etcgem fba --strain cauris_iRV973 --experiment candida_pool_binding --temp 30

    python3 reports/candida_thermal_limit/gate_table.py [--candidas-root PATH]

Writes gate_table.csv beside this file and prints the table. Exit status 0 if every row
passes, 1 otherwise -- so a later change that breaks the agreement is visible.

TOLERANCES, stated before the comparison was run (prompts/K1_candida_port_and_verify_prompt.md):
    fitted globals            within 2%
    predicted mu              within 1e-3 /h or 1%, whichever is larger
    thermal limits            within 0.2 C
    pool-binding growth rates within 1e-3 /h or 1% (same rule as mu)
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import pandas as pd

STRAIN_OF = {"auris": "cauris_iRV973", "haemulonii": "chaemulonii_draft",
             "duobushaemulonii": "cduobushaemulonii_draft",
             "parapsilosis": "cparapsilosis_iDC1003"}

TOL_GLOBAL_REL = 0.02        # fitted globals: 2%
TOL_MU_ABS = 1e-3            # mu: 1e-3 /h ...
TOL_MU_REL = 0.01            # ... or 1%, whichever is larger
TOL_LIMIT_C = 0.2            # thermal limits: 0.2 C

rows = []


def add(quantity, source, locked, port, tol_text, ok, note=""):
    rows.append(dict(quantity=quantity, locked_source=source, locked=locked, port=port,
                     tolerance=tol_text, verdict="PASS" if ok else "FAIL", note=note))


def _close_rel(a, b, rel):
    return abs(a - b) <= rel * abs(b) if b else abs(a - b) <= rel


def _close_mu(a, b):
    return abs(a - b) <= max(TOL_MU_ABS, TOL_MU_REL * abs(b))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--candidas-root", default=os.environ.get("CANDIDAS_ROOT"))
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                  "gate_table.csv"))
    a = ap.parse_args(argv)
    if not a.candidas_root:
        ap.error("--candidas-root (or $CANDIDAS_ROOT) is required")
    G = os.path.join(a.candidas_root, "gem")

    # ---------------------------------------------------------------- 1. fitted globals
    locked = json.load(open(os.path.join(G, "tables", "etcgem_calib.json")))
    port = json.load(open("outputs/transfer_candida/calibration.json"))
    f = port["fitted"]
    for name, key, label in (("pheno_sigma", "sig", "fitted sigma (Gaussian peak width, C)"),
                             ("pheno_w", "w", "fitted w (denaturation width, C)"),
                             ("pool_budget", "P", "fitted P (pool budget, g enzyme/gDW)")):
        add(label, "gem/tables/etcgem_calib.json (18_build_etcgem_tpc.py)",
            round(locked[key], 6), round(f[name], 6), "2%",
            _close_rel(f[name], locked[key], TOL_GLOBAL_REL))
    add("growth scale SCALE (peak match on C. auris)",
        "gem/tables/etcgem_calib.json (18_build_etcgem_tpc.py)",
        round(locked["SCALE"], 6), round(port["scale"], 6), "2%",
        _close_rel(port["scale"], locked["SCALE"], TOL_GLOBAL_REL))
    add("C. auris calibration MSE",
        "gem/tables/etcgem_calib.json (18_build_etcgem_tpc.py)",
        round(locked["auris_fit_mse"], 8), round(port["mse"], 8), "2%",
        _close_rel(port["mse"], locked["auris_fit_mse"], TOL_GLOBAL_REL))

    # -------------------------------------------------- 2. predicted mu at every T, x4 sp
    lp = pd.read_csv(os.path.join(G, "tables", "etcgem_tpc_pred.csv"))
    for sp, strain in STRAIN_OF.items():
        p = pd.read_csv(f"strains/{strain}/outputs/transfer_candida/tpc.csv")
        pm = dict(zip(p.temp_C.round(6), p.mu_pred))
        l = lp[lp.species == sp]
        worst, worst_T = 0.0, None
        for _, r in l.iterrows():
            v = pm.get(round(float(r["T"]), 6))
            if v is None:
                add(f"predicted mu, {sp} at {r['T']:g} C", "gem/tables/etcgem_tpc_pred.csv",
                    r["pred_mu"], None, "1e-3 /h or 1%", False, "temperature missing from the port grid")
                continue
            d = abs(round(v, 4) - r["pred_mu"])
            if d > worst:
                worst, worst_T = d, float(r["T"])
            add(f"predicted mu, {sp} at {r['T']:g} C", "gem/tables/etcgem_tpc_pred.csv",
                r["pred_mu"], round(v, 4), "1e-3 /h or 1%", _close_mu(round(v, 4), r["pred_mu"]))
        print(f"[mu] {sp:18s} {len(l)} temperatures, largest |difference| "
              f"{worst:.6f} /h" + (f" (at {worst_T:g} C)" if worst_T is not None else ""))

    # ------------------------------------------------------------- 3. thermal limits
    # FIG4_LOCKED.md states the RANGE across the four species; the producing script,
    # 22_thermal_sensitivity.py, pins the maintenance reaction, so the matching port run
    # is transfer_candida_pinned_maint.
    s = pd.read_csv("outputs/transfer_candida_pinned_maint/summary.csv")
    lim = s.thermal_limit_C
    add("model-predicted thermal limit, lowest of the four species (C)",
        "gem/FIG4_LOCKED.md (22_thermal_sensitivity.py)", 52.7, round(float(lim.min()), 2),
        "0.2 C", abs(float(lim.min()) - 52.7) <= TOL_LIMIT_C,
        "transfer_candida_pinned_maint: 22 pins maintenance, 18 does not")
    add("model-predicted thermal limit, highest of the four species (C)",
        "gem/FIG4_LOCKED.md (22_thermal_sensitivity.py)", 54.5, round(float(lim.max()), 2),
        "0.2 C", abs(float(lim.max()) - 54.5) <= TOL_LIMIT_C,
        "transfer_candida_pinned_maint: 22 pins maintenance, 18 does not")

    # per-species reference values, if a read-only re-run of 22 was captured
    ref = os.path.join(os.path.dirname(os.path.abspath(__file__)), "standalone_22_limits.csv")
    if os.path.exists(ref):
        r22 = pd.read_csv(ref).set_index("species").limit_C
        byname = dict(zip(s.strain, s.thermal_limit_C))
        for sp, strain in STRAIN_OF.items():
            if sp in r22.index:
                add(f"thermal limit, {sp} (C)", "gem/22_thermal_sensitivity.py (re-run, read-only)",
                    round(float(r22[sp]), 2), round(float(byname[strain]), 2), "0.2 C",
                    abs(float(byname[strain]) - float(r22[sp])) <= TOL_LIMIT_C)

    # ------------------------------------------------- 4. the pool-binding precondition
    for label, exp, locked_v in (
            ("C. auris maximum, pool removed (plain GEM) /h", "candida_pool_unconstrained", 2.045),
            ("C. auris maximum, pool at P=0.25 with EC-class kcats /h", "candida_pool_binding", 0.758)):
        v = json.load(open(f"strains/cauris_iRV973/outputs/fba_{exp}/fba_result.json"))["growth"]
        add(label, "gem/notes/POOL_BINDING_RESULT.md (16_pool_binding_test.py)",
            locked_v, round(v, 4), "1e-3 /h or 1%", _close_mu(round(v, 3), locked_v))

    df = pd.DataFrame(rows)
    df.to_csv(a.out, index=False)
    n_fail = int((df.verdict == "FAIL").sum())
    with pd.option_context("display.width", 200, "display.max_colwidth", 60):
        print(df[~df.quantity.str.startswith("predicted mu")].to_string(index=False))
    print(f"\n{len(df)} comparisons, {len(df) - n_fail} PASS, {n_fail} FAIL "
          f"({(df.quantity.str.startswith('predicted mu')).sum()} of them the "
          f"per-temperature mu table)")
    print("wrote", a.out)
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())
