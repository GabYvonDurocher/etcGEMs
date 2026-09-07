#!/usr/bin/env python3
"""gate_table.py -- K1's gate: every locked number of the standalone Candida etcGEM
against the port's value, with the tolerance and a PASS/FAIL.

The comparison is made against the standalone AS IT STANDS, in the Candidas repository at
the commit recorded in each strain.yaml.

SELF-CONTAINED BY DEFAULT (N1 TASK 2). Every expected value is frozen in the committed
fixture `standalone_expected.json` beside this file, with the Candidas commit hash and the
md5 of each source file inside it, so the gate keeps working on a machine that has never
seen the Candidas repository -- and keeps working after the fork is archived, which is what
K3 needs. Pass `--candidas-root PATH` to read the standalone directly instead: the gate then
compares the live values with the fixture and REPORTS ANY DRIFT before running, and
`--refresh-fixture` rewrites it. It reads that repository read-only; it changes nothing on
either side.

Run from the project root, after

    etcgem transfer --experiment transfer_candida_unpinned
    etcgem transfer --experiment transfer_candida
    etcgem fba --strain cauris_iRV973 --experiment candida_pool_unconstrained --temp 30
    etcgem fba --strain cauris_iRV973 --experiment candida_pool_binding --temp 30

    python3 reports/candida_thermal_limit/gate_table.py                    # from the fixture
    python3 reports/candida_thermal_limit/gate_table.py --candidas-root P  # + drift check

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


HERE = os.path.dirname(os.path.abspath(__file__))
FIXTURE = os.path.join(HERE, "standalone_expected.json")

# Values transcribed from the standalone's prose records rather than from a table it writes.
# They live in the fixture like everything else, so every expected number has one home.
FIG4_LOCKED_LIMITS = dict(low_C=52.7, high_C=54.5,
                          source="gem/FIG4_LOCKED.md, 'model-predicted thermal limit "
                                 "52.7-54.5 C across the four species', produced by "
                                 "22_thermal_sensitivity.py")
POOL_BINDING = dict(unconstrained=2.045, constrained_P025_ecclass=0.758,
                    source="gem/notes/POOL_BINDING_RESULT.md, produced by "
                           "16_pool_binding_test.py")


def _md5(path):
    import hashlib
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def build_expected(candidas_root):
    """Read every expected value out of the standalone. Read-only."""
    import subprocess
    G = os.path.join(candidas_root, "gem")
    files = {}
    for rel in ("gem/tables/etcgem_calib.json", "gem/tables/etcgem_tpc_pred.csv",
                "gem/tables/counterfactual_results.json"):
        q = os.path.join(candidas_root, rel)
        files[rel] = _md5(q) if os.path.exists(q) else None
    try:
        commit = subprocess.run(["git", "-C", candidas_root, "rev-parse", "HEAD"],
                                capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        commit = "unknown"
    exp = dict(
        candidas_repo=os.path.basename(os.path.normpath(candidas_root)),
        candidas_commit=commit, source_file_md5=files,
        calib=json.load(open(os.path.join(G, "tables", "etcgem_calib.json"))),
        tpc_pred=pd.read_csv(os.path.join(G, "tables", "etcgem_tpc_pred.csv"))
                   .to_dict(orient="records"),
        fig4_locked_limits=FIG4_LOCKED_LIMITS, pool_binding=POOL_BINDING)
    cfj = os.path.join(G, "tables", "counterfactual_results.json")
    if os.path.exists(cfj):
        raw = json.load(open(cfj))
        exp["counterfactual"] = dict(baseline=raw["baseline"],
                                     required=raw["mechanisms"]["thr=0.05"])
    return exp


def load_expected(path=FIXTURE):
    if not os.path.exists(path):
        sys.exit(f"no fixture at {path}; regenerate it with "
                 f"--candidas-root PATH --refresh-fixture")
    return json.load(open(path))


def drift(fixture, live):
    """Every place the live standalone disagrees with the committed fixture."""
    out = []
    if fixture.get("candidas_commit") != live.get("candidas_commit"):
        out.append(f"candidas_commit: fixture {fixture.get('candidas_commit')} "
                   f"-> live {live.get('candidas_commit')}")
    for k, v in (live.get("source_file_md5") or {}).items():
        fv = (fixture.get("source_file_md5") or {}).get(k)
        if fv != v:
            out.append(f"md5 {k}: fixture {fv} -> live {v}")
    for k, v in live["calib"].items():
        fv = fixture["calib"].get(k)
        if fv is None or abs(float(v) - float(fv)) > 1e-12:
            out.append(f"calib.{k}: fixture {fv} -> live {v}")
    fp = {(r["species"], float(r["T"])): float(r["pred_mu"]) for r in fixture["tpc_pred"]}
    for r in live["tpc_pred"]:
        key = (r["species"], float(r["T"]))
        if key not in fp or abs(fp[key] - float(r["pred_mu"])) > 1e-12:
            out.append(f"tpc_pred {key}: fixture {fp.get(key)} -> live {r['pred_mu']}")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--candidas-root", default=None,
                    help="read the standalone directly and report drift from the fixture; "
                         "without it the committed fixture is the reference and no external "
                         "repository is needed")
    ap.add_argument("--refresh-fixture", action="store_true",
                    help="rewrite standalone_expected.json from --candidas-root")
    ap.add_argument("--fixture", default=FIXTURE)
    ap.add_argument("--out", default=os.path.join(HERE, "gate_table.csv"))
    a = ap.parse_args(argv)

    fixture = load_expected(a.fixture) if os.path.exists(a.fixture) else None
    if a.candidas_root:
        live = build_expected(a.candidas_root)
        if a.refresh_fixture:
            with open(a.fixture, "w") as fh:
                json.dump(live, fh, indent=2)
            print(f"[fixture] rewrote {a.fixture} from {a.candidas_root} "
                  f"(commit {live['candidas_commit'][:7]})")
            fixture = live
        elif fixture is not None:
            d = drift(fixture, live)
            print(f"[fixture] committed fixture is Candidas commit "
                  f"{fixture['candidas_commit'][:7]}; live copy is "
                  f"{live['candidas_commit'][:7]}")
            if d:
                print(f"[fixture] DRIFT in {len(d)} place(s):")
                for line in d[:20]:
                    print(f"    {line}")
                print("[fixture] using the LIVE values; --refresh-fixture to adopt them")
            else:
                print("[fixture] no drift: every expected value matches")
        exp = live
        src = f"live standalone at {a.candidas_root}"
    else:
        if fixture is None:
            ap.error(f"no fixture at {a.fixture} and no --candidas-root")
        exp = fixture
        src = (f"committed fixture {os.path.basename(a.fixture)} "
               f"(Candidas commit {exp['candidas_commit'][:7]})")
    print(f"[gate] expected values from: {src}\n")

    # Which port run each locked number is compared against. The standalone is not internally
# consistent about the maintenance reaction (K1 finding 1), so the numbers from 18 are
# compared against the UNCORRECTED run and those from 19/22 against the corrected one --
# which is the strain default since K2 PART A.
#   transfer_candida_unpinned  == gem/18_build_etcgem_tpc.py   (calibration + mu table)
#   transfer_candida           == gem/19 and gem/22            (limits, counterfactual)

    # ---------------------------------------------------------------- 1. fitted globals
    locked = exp["calib"]
    port = json.load(open("outputs/transfer_candida_unpinned/calibration.json"))
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
    lp = pd.DataFrame(exp["tpc_pred"])
    for sp, strain in STRAIN_OF.items():
        p = pd.read_csv(f"strains/{strain}/outputs/transfer_candida_unpinned/tpc.csv")
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
    s = pd.read_csv("outputs/transfer_candida/summary.csv")
    lim = s.thermal_limit_C
    add("model-predicted thermal limit, lowest of the four species (C)",
        "gem/FIG4_LOCKED.md (22_thermal_sensitivity.py)",
        exp["fig4_locked_limits"]["low_C"], round(float(lim.min()), 2),
        "0.2 C",
        abs(float(lim.min()) - exp["fig4_locked_limits"]["low_C"]) <= TOL_LIMIT_C,
        "transfer_candida (maintenance corrected, as 22 does); 18 does not")
    add("model-predicted thermal limit, highest of the four species (C)",
        "gem/FIG4_LOCKED.md (22_thermal_sensitivity.py)",
        exp["fig4_locked_limits"]["high_C"], round(float(lim.max()), 2),
        "0.2 C",
        abs(float(lim.max()) - exp["fig4_locked_limits"]["high_C"]) <= TOL_LIMIT_C,
        "transfer_candida (maintenance corrected, as 22 does); 18 does not")

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

    # ------------------- 5. the corrected-maintenance run against 19_etcgem_counterfactual
    # 19 applies the maintenance correction that 18 omits, and records both its baseline mu
    # and the required separations. Added in K2, when that correction became the default.
    if exp.get("counterfactual"):
        c19 = exp["counterfactual"]
        for sp, strain in STRAIN_OF.items():
            p = pd.read_csv(f"strains/{strain}/outputs/transfer_candida/tpc.csv")
            pm = dict(zip(p.temp_C.round(6), p.mu_pred))
            for T, locked_v in c19["baseline"][sp].items():
                v = pm.get(round(float(T), 6))
                add(f"corrected-maintenance mu, {sp} at {T} C",
                    "gem/tables/counterfactual_results.json (19_etcgem_counterfactual.py)",
                    locked_v, (round(v, 4) if v is not None else None),
                    "1e-3 /h or 1%",
                    v is not None and _close_mu(round(v, 4), locked_v))
        cfp = "outputs/transfer_candida/counterfactual.csv"
        if os.path.exists(cfp):
            port_cf = pd.read_csv(cfp)
            m19 = c19["required"]
            for mech, param in (("Tm", "dTm"), ("Topt", "dTopt")):
                for sp, locked_v in m19[mech]["per_rel"].items():
                    strain = STRAIN_OF[sp]
                    r = port_cf[(port_cf.strain == strain) & (port_cf.param == param)]
                    got = (None if r.empty or pd.isna(r.iloc[0]["required"])
                           else float(r.iloc[0]["required"]))
                    want = locked_v.get("required")
                    ok = (got is None and want is None) or (
                        got is not None and want is not None and abs(got - want) <= 0.2)
                    add(f"required {mech} separation, {sp} (C)",
                        "gem/tables/counterfactual_results.json (19_etcgem_counterfactual.py)",
                        want, got, "0.2 C", ok,
                        "both None = neither can be pushed below detection at 40 C"
                        if want is None else "")

    # ------------------------------------------------- 4. the pool-binding precondition
    for label, exp, locked_v in (
            ("C. auris maximum, pool removed (plain GEM) /h", "candida_pool_unconstrained",
             exp["pool_binding"]["unconstrained"]),
            ("C. auris maximum, pool at P=0.25 with EC-class kcats /h", "candida_pool_binding",
             exp["pool_binding"]["constrained_P025_ecclass"])):
        v = json.load(open(f"strains/cauris_iRV973/outputs/fba_{exp}/fba_result.json"))["growth"]
        add(label, "gem/notes/POOL_BINDING_RESULT.md (16_pool_binding_test.py)",
            locked_v, round(v, 4), "1e-3 /h or 1%", _close_mu(round(v, 3), locked_v))

    df = pd.DataFrame(rows)
    df.to_csv(a.out, index=False)
    n_fail = int((df.verdict == "FAIL").sum())
    with pd.option_context("display.width", 200, "display.max_colwidth", 60):
        hide = df.quantity.str.startswith(("predicted mu", "corrected-maintenance mu"))
        print(df[~hide].to_string(index=False))
    print(f"\n{len(df)} comparisons, {len(df) - n_fail} PASS, {n_fail} FAIL "
          f"({int(hide.sum())} of them per-temperature mu values, elided above)")
    print("wrote", a.out)
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())
