"""Assemble the final per-enzyme kcat+MW+source table for the M. maripaludis sMOMENT
ecModel (M2): measured core (priority) -> DLTKcat prediction -> dataset-mean fallback.
Run from project root:  python strains/mmaripaludis/dltkcat/assemble_kcat_table.py"""
import json, os, re
import numpy as np, pandas as pd
import logging, warnings
logging.getLogger("cobra").setLevel(logging.CRITICAL); warnings.filterwarnings("ignore")
import cobra

HERE = "strains/mmaripaludis"
MODEL = f"{HERE}/model/iMR539_curated.xml"
MWJSON = f"{HERE}/dltkcat/enzyme_mw.json"
CORE = f"{HERE}/dltkcat/kcat_measured_core.csv"
PRED = f"{HERE}/dltkcat/predicted.csv"          # DLTKcat output (pred_log10kcat), may be absent
OUT = f"{HERE}/dltkcat/kcat_table.csv"

def full_id(model, base):
    if base in model.reactions: return base
    for r in model.reactions:
        if r.id == base or r.id.startswith(base + "_LSQBKT"): return r.id
    return None

def main():
    cobra.Configuration().solver = "glpk"
    m = cobra.io.read_sbml_model(MODEL)
    mw = json.load(open(MWJSON))                       # rxn_id -> {mw_kDa, n_genes}

    # measured core: rxn_base -> kcat
    core = pd.read_csv(CORE)
    core_kcat = {}
    for _, r in core.iterrows():
        fid = full_id(m, r.rxn_base)
        if fid: core_kcat[fid] = float(r.kcat_s)

    # M2b literature/BRENDA overrides for the flagged high-pool offenders (PFOR, OGOR...)
    OVR = f"{HERE}/dltkcat/kcat_overrides.csv"
    override_kcat = {}
    if os.path.exists(OVR):
        for _, r in pd.read_csv(OVR).iterrows():
            fid = full_id(m, r.rxn_base)
            if fid: override_kcat[fid] = float(r.kcat_s)

    # DLTKcat predictions: rxn_id -> kcat (10^pred_log10kcat), averaged if duplicates
    dlt = {}
    if os.path.exists(PRED):
        pr = pd.read_csv(PRED)
        pr["kcat"] = 10.0 ** pr["pred_log10kcat"]
        dlt = pr.groupby("rxn_id")["kcat"].median().to_dict()
    dlt_vals = [v for v in dlt.values() if np.isfinite(v) and v > 0]
    fallback = float(np.median(dlt_vals)) if dlt_vals else 25.0

    # M2b (PART C) documented floor for the untrustworthy DLTKcat archaeal-underprediction
    # tail: 1.0/s = the lower bound of physiologically-plausible central-metabolic turnover
    # (the measured methanogen core spans 9-290/s; BRENDA central-C kcats rarely < 1/s).
    # Applied ONLY to DLTKcat predictions (not to measured/literature/fallback), so genuine
    # slow measured values (e.g. Mcr, Fwd) are never floored.
    FLOOR = 1.0

    rows, n_core = [], 0
    n_dlt = n_fb = n_ovr = n_floored = 0
    for rid, info in mw.items():
        if info.get("mw_kDa") is None:
            continue
        mwk = float(info["mw_kDa"])
        grp = _subsys(m, rid)
        if rid in core_kcat:
            kcat, src = core_kcat[rid], "measured_core"; n_core += 1
        elif rid in override_kcat:
            kcat, src = override_kcat[rid], "literature_override"; n_ovr += 1
        elif rid in dlt and np.isfinite(dlt[rid]) and dlt[rid] > 0:
            kcat = float(dlt[rid])
            if kcat < FLOOR:
                kcat, src = FLOOR, "dltkcat_floored"; n_floored += 1
            else:
                src = "dltkcat"
            n_dlt += 1
        else:
            kcat, src = fallback, "fallback_mean"; n_fb += 1
        rows.append(dict(rxn_id=rid, mw_kDa=round(mwk, 3), kcat_s=round(kcat, 4),
                         source=src, group=grp))
    df = pd.DataFrame(rows)
    df.to_csv(OUT, index=False)
    print(f"kcat table: {len(df)} enzymatic reactions -> {OUT}")
    print(f"  measured_core       : {n_core}")
    print(f"  literature_override : {n_ovr}")
    print(f"  dltkcat             : {n_dlt}  (of which {n_floored} floored to {FLOOR}/s)")
    print(f"  fallback_mean       : {n_fb}  (median DLTKcat kcat = {fallback:.2f} 1/s)")
    print(f"  kcat 1/s: median={df.kcat_s.median():.2f} "
          f"p10={df.kcat_s.quantile(.1):.2f} p90={df.kcat_s.quantile(.9):.2f}")

def _subsys(m, rid):
    s = getattr(m.reactions.get_by_id(rid), "subsystem", None)
    return s if s else "default"

if __name__ == "__main__":
    main()
