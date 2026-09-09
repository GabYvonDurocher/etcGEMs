#!/usr/bin/env python3
"""P10 TASK 4 -- the P3 gate re-read under the tie-break: every one of the ten gated R2 values
recomputed at Parsa's own theta (P3's points, P3's construction, his blanket/LB media and his
caps) with O2 read at the pfba vertex instead of the solver's. Growth R2 must be unchanged
(the tie-break never touches growth); respiration R2 for D unchanged (its O2 was unique);
for E and F the difference is the width of the face. Writes task4_regate.csv beside this file.
"""
import json, os, sys
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src")); sys.path.insert(0, os.path.join(ROOT, "reports", "P3_gate")); os.chdir(ROOT)
import gate_def as G                                                               # noqa: E402
from etcgem.calibration_multi import to_natural, to_pert                           # noqa: E402
from etcgem.gasflux import flux_tpc, add_total_carbon_constraint                   # noqa: E402
from etcgem import etc_area as EA                                                  # noqa: E402

CHAINS = os.path.join(os.environ.get("PARSA_ROOT", "/Users/g.yvon-durocher/Downloads/etcGEMs-main_3"), "strains", "eciML1515", "outputs")
HEADLINE = pd.read_csv(os.path.join(ROOT, "reports", "P3_gate", "gate_def_headline.csv"))


def predict_tb(medium, medium_key, cfg, theta, specs, gdw, table, his_order, tiebreak):
    """gate_def.predict with the tie-break threaded into flux_tpc; everything else identical"""
    nat = to_natural(theta, specs); pert = to_pert(theta, specs)
    pm = G.build_pm_for_fit(medium_key, his_order)
    if cfg.get("use_etc"):
        tab = EA.load_etc_table(table)
        if cfg.get("use_configf"): EA.set_proton_stoichiometry(pm, tab, verbose=False)
        gx = G.gas_exchange(); mem = gx.get("membrane") or {}
        a_mem = EA.membrane_area_per_gdw(mem["sv_um2_per_fL"], mem["dcw_pg_per_fL"])
        EA.add_etc_area_constraint(pm, tab, EA.budget_from_fraction(a_mem, G.F_ETC_NOM * float(nat[f"F_ETC_{medium}_mult"])))
    if cfg.get("use_cap"):
        fixed = (cfg.get("cmax_fixed") or {}).get(medium)
        cap = float(fixed) if fixed is not None else (G.CAP_NOM_E[medium] if cfg.get("use_etc") else G.CAP_NOM[medium]) * float(nat[f"C_max_{medium}_mult"])
        add_total_carbon_constraint(pm, cap)
    df = flux_tpc(pm, G.DENSE, pert, metabolites=("o2",), tiebreak=tiebreak)
    g = df["growth"].to_numpy(float); r = df["o2_uptake"].to_numpy(float) * (gdw * G.MW_O2 / 60.0) * float(nat["resp_scale"])
    return g, r


def main():
    gdw = float(G.gas_exchange()["gdw_per_cell"])
    etc_e = os.path.join(ROOT, "strains/eciML1515/etc/complexes_szenk_merged_bd.csv"); etc_f = os.path.join(ROOT, "strains/eciML1515/etc/complexes_configF_as_fitted.csv")
    rows = []
    for _, h in HEADLINE.iterrows():
        conf, medium, run, point = h["config"], h["medium"], "calibration_" + h["run"].replace("D_", "configD_").replace("E_", "configE_").replace("F_", "configF_"), h["point"]
        cdir = os.path.join(CHAINS, run); cfg = json.load(open(os.path.join(cdir, "meta.json"))).get("cfg") or {}
        specs = G.build_specs(medium, cfg); th_map, th_med, it, nw = G.read_points(cdir); theta = th_map if point == "MAP" else th_med
        table = etc_f if cfg.get("use_configf") else etc_e
        mk = "NLDM_blanket" if medium == "NLDM" else "LB"
        csv = os.path.join(G.RESP, "derived_R2A_LB_20260907_prefix.csv")
        Tg, og = G.load_obs(csv, G.OTU[medium], "growth_C_per_C_h"); Tr, orr = G.load_obs(csv, G.OTU[medium], "R_O2_mg_cell_min")
        out = dict(config=conf, medium=medium, run=run, point=point, his_growth_R2=h["his_g"], his_resp_R2=h["his_r"], p3_growth_R2=h["pre_g"], p3_resp_R2=h["pre_r"])
        for tb in ("none", "pfba"):
            g, r = predict_tb(medium, mk, cfg, theta, specs, gdw, table, True, tb)
            gr2, _ = G.r2(og, Tg, g, G.DENSE); rr2, _ = G.r2(orr, Tr, r, G.DENSE)
            out[f"growth_R2_{tb}"] = gr2; out[f"resp_R2_{tb}"] = rr2
        out["d_growth_R2"] = out["growth_R2_pfba"] - out["growth_R2_none"]; out["d_resp_R2"] = out["resp_R2_pfba"] - out["resp_R2_none"]
        rows.append(out)
        print(f"[regate] {conf} {medium:4s} {point:16s} growth R2 none {out['growth_R2_none']:.4f} pfba {out['growth_R2_pfba']:.4f} (P3 {h['pre_g']:.4f}, his {h['his_g']})  resp R2 none {out['resp_R2_none']:.4f} pfba {out['resp_R2_pfba']:.4f} (P3 {h['pre_r']}, his {h['his_r']})", flush=True)
    pd.DataFrame(rows).to_csv(os.path.join(HERE, "task4_regate.csv"), index=False); print("[regate] done", flush=True)


if __name__ == "__main__":
    main()
