#!/usr/bin/env python3
"""P5 TASK 1d -- the cap alone, at fixed parameters, for all three LB configurations.

P3's gate machinery (reports/P3_gate/gate_def.py) reads one point out of each of Parsa's LB
chains and recomputes his prediction in our model, with the cap taken from his fitted
C_max_LB_mult x nominal. This script keeps everything about that point fixed and changes ONE
number -- the multiplier, so that the cap is 120 (P4's canonical), 257, 350, 450 (his E/F
nominal) or his own fitted value -- and reports growth and respiration R2 at each. No sampler,
no optimisation: the same parameter vector, five caps, three configurations.

Reads his chains under $PARSA_ROOT (READ ONLY). Writes cap_sweep_fixed_point.csv beside this
file.
"""
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "reports", "P3_gate"))
os.chdir(ROOT)

import gate_def as G                                                                    # noqa: E402

PARSA = os.environ.get("PARSA_ROOT", "/Users/g.yvon-durocher/Downloads/etcGEMs-main_3")
CHAINS = os.path.join(PARSA, "strains", "eciML1515", "outputs")
RUNS = [("D", "calibration_configD_LB_full"),
        ("E", "calibration_configE_LB_freecmax"),
        ("F", "calibration_configF_LB")]
CAPS = (120.0, 257.0, 350.0, 450.0, "his")
MEASURED_PEAK = None


def main():
    gdw = float(G.gas_exchange()["gdw_per_cell"])
    etc_e = os.path.join(ROOT, "strains/eciML1515/etc/complexes_szenk_merged_bd.csv")
    etc_f = os.path.join(ROOT, "strains/eciML1515/etc/complexes_configF_as_fitted.csv")
    csv = os.path.join(G.RESP, "derived_R2A_LB_current.csv")
    Tg, og = G.load_obs(csv, 2, "growth_C_per_C_h")
    Tr, orr = G.load_obs(csv, 2, "R_O2_mg_cell_min")
    print(f"[sweep] measured LB growth peak {og.max():.3f} h^-1 at {Tg[int(np.argmax(og))]:g} C", flush=True)
    rows = []
    for conf, run in RUNS:
        cdir = os.path.join(CHAINS, run)
        cfg = json.load(open(os.path.join(cdir, "meta.json"))).get("cfg") or {}
        specs = G.build_specs("LB", cfg)
        names = [s.name for s in specs]
        th_map, _, it, nw = G.read_points(cdir)
        k = names.index("C_max_LB_mult")
        nom = G.CAP_NOM_E["LB"] if cfg.get("use_etc") else G.CAP_NOM["LB"]
        his_cap = nom * float(np.exp(th_map[k]))
        table = etc_f if cfg.get("use_configf") else etc_e
        for cap in CAPS:
            c = his_cap if cap == "his" else float(cap)
            th = th_map.copy()
            th[k] = np.log(c / nom)           # the ONE number that changes
            g, r, nat = G.predict("LB", "LB", cfg, th, specs, gdw, table, True)
            gr2, _ = G.r2(og, Tg, g, G.DENSE)
            rr2, _ = G.r2(orr, Tr, r, G.DENSE)
            rows.append(dict(config=conf, run=run, point="MAP", c_max=round(c, 1),
                             is_his_fitted=(cap == "his"), growth_R2=round(gr2, 4), resp_R2=round(rr2, 4),
                             rmax=round(float(np.nanmax(g)), 3), Topt_C=float(G.DENSE[int(np.nanargmax(g))]),
                             measured_peak=round(float(og.max()), 3)))
            print(f"[sweep] {conf} LB  cap {c:6.1f}{' (his)' if cap == 'his' else '      '}  "
                  f"growth R2 {gr2:7.3f}  resp R2 {rr2:7.3f}  rmax {np.nanmax(g):.3f}", flush=True)
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(HERE, "cap_sweep_fixed_point.csv"), index=False)
    pd.set_option("display.width", 200)
    print(df.to_string(index=False))
    print("[sweep] done", flush=True)


if __name__ == "__main__":
    main()
