#!/usr/bin/env python3
"""P3 TASK 3 -- the gate: configurations D, E and F against experiment.

No emcee. His six committed chains hold the fits; this reads the MAP out of each one and
recomputes the prediction and the R2 in THIS repository's core, exactly as his figure script
does (`scripts_configE_fig.py`):

  * parameters: the MAP, argmax of the whole log-probability array (not the median);
  * grid: np.arange(8.0, 55.01, 1.5);
  * prediction: flux_tpc -> growth, and o2_uptake * O2_CONV * resp_scale for per-cell respiration;
  * R2: interpolate the model curve onto the observed temperatures, then 1 - SS_res/SS_tot,
    linear for both growth and respiration.

Every comparison is run against BOTH versions of the measured data (pre-boundaryfix, which is
what his figures used, and current) and -- for NLDM -- BOTH medium constructions (blanket, which
his fits used, and the recipe ceilings that are now canonical). Writes gate_def_table.csv.

    python reports/P3_gate/gate_def.py [--chains DIR]
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
os.chdir(ROOT)

from etcgem.calibration_multi import (PSpec, build_vdl_specs, WIDE_ENVELOPE_SPECS,   # noqa: E402
                                      to_natural, to_pert, build_pm_medium)
from etcgem.config import resolve                                                     # noqa: E402
import yaml                                                                           # noqa: E402
from etcgem import etc_area as EA                                                     # noqa: E402
from etcgem.gasflux import flux_tpc, add_total_carbon_constraint                       # noqa: E402

RESP = os.path.join(ROOT, "strains", "eciML1515", "respirometry")
DENSE = np.arange(8.0, 55.01, 1.5)
CAP_NOM = {"NLDM": 230.0, "LB": 230.0}      # config D
CAP_NOM_E = {"NLDM": 450.0, "LB": 450.0}    # config E/F: the lighter bound
F_ETC_NOM = 0.316
OTU = {"NLDM": 1, "LB": 2}
MW_O2 = 32.0

# His committed fits. The cfg is NOT hard-coded here: each run's own meta.json is authoritative
# (it records use_cap / use_etc / use_configf / cmax_fixed, and they are not what the config
# names suggest -- configuration E on LB pins C_max at 459 rather than fitting it, and there is
# a second configuration-F NLDM run made under the recipe medium).
FITS = [
    ("D", "NLDM", "calibration_configD_NLDM_full"),
    ("D", "LB",   "calibration_configD_LB_full"),
    ("E", "NLDM", "calibration_configE_NLDM"),
    ("E", "LB",   "calibration_configE_LB"),
    ("E", "LB",   "calibration_configE_LB_freecmax"),
    ("F", "NLDM", "calibration_configF_NLDM"),
    ("F", "NLDM", "calibration_configF_NLDM_recipe"),
    ("F", "NLDM", "calibration_configF_NLDM_cap"),
    ("F", "LB",   "calibration_configF_LB_combined"),
    ("F", "LB",   "calibration_configF_LB"),
]
# What his reports print, for the comparison.
HIS = {("D", "NLDM"): dict(growth_r2=0.71), ("D", "LB"): dict(growth_r2=0.90),
       ("E", "NLDM"): dict(growth_r2=0.85, resp_r2=0.72, f_etc=0.32),
       ("E", "LB"):   dict(growth_r2=0.83, resp_r2=0.81, f_etc=0.32),
       ("F", "NLDM"): dict(growth_r2=0.91, resp_r2=0.96),
       ("F", "LB"):   dict(growth_r2=0.88, resp_r2=0.85, c_max=510.0)}


def gas_exchange():
    """The strain's measured gas-exchange constants. Loaded straight from the strain file:
    config.apply_gasflux reads it lazily during build_provider, so resolve() alone does not
    carry it."""
    p = os.path.join(ROOT, "strains", "eciML1515", "gas_exchange.yaml")
    return (yaml.safe_load(open(p)) or {}).get("gas_exchange", {})


def build_specs(medium, cfg):
    """His build_specs_full(cfg), rebuilt from this repository's own PSpec set."""
    base = build_vdl_specs()
    phys = [WIDE_ENVELOPE_SPECS.get(s.name, s) for s in base if s.name != "sigma_disc"]
    extra = []
    if cfg.get("use_etc"):
        extra += [PSpec(f"F_ETC_{medium}_mult", "log", "lognormal", 0.35, 0.0, 0.3, 2.0, None, 1.0)]
    if cfg.get("fit_clearance") and medium == "NLDM":
        extra += [PSpec("nldm_clear_mult", "log", "lognormal", 0.35, 0.0, 0.4, 2.0, None, 1.0)]
    if cfg.get("use_cap") and medium not in (cfg.get("cmax_fixed") or {}):
        lo, hi = (0.2, 2.2) if cfg.get("use_etc") else (0.25, 3.0)
        extra += [PSpec(f"C_max_{medium}_mult", "log", "lognormal", 0.40, 0.0, lo, hi, None, 1.0)]
    extra += [PSpec("resp_scale", "log", "lognormal", 1.00, 0.0, 0.02, 50.0, None, 1.0),
              PSpec("disc_resp", "log", "halfnormal", 0.50, 0.0, 1e-3, 3.0, None, None),
              PSpec("disc_growth", "log", "halfnormal", 0.50, 0.0, 1e-4, 5.0, None, None)]
    return phys + extra


def read_points(chain_dir):
    """(MAP, posterior median, iterations, walkers) from a committed chain.

    Both are needed: his configuration-E and -F figures quote the MAP, and his configuration-D
    numbers turn out to be the posterior median. Reading a chain is not sampling.
    """
    import h5py
    with h5py.File(os.path.join(chain_dir, "chain.h5"), "r") as f:
        g = f[list(f.keys())[0]]
        it = int(g.attrs["iteration"])
        ch = g["chain"][:it]
        lp = g["log_prob"][:it]
    i, j = np.unravel_index(np.nanargmax(lp), lp.shape)
    burn = it // 2
    med = np.median(ch[burn:].reshape(-1, ch.shape[2]), axis=0)
    return ch[i, j], med, int(it), ch.shape[1]


def load_obs(data_csv, otu, col):
    d = pd.read_csv(data_csv)
    d = d[d["OTU"] == otu]
    g = d.groupby("T")[col].agg(["mean", "std", "count"]).reset_index()
    return g["T"].to_numpy(float), g["mean"].to_numpy(float)


def r2(obs, Tobs, pred, Tpred):
    p = np.interp(Tobs, Tpred, pred)
    k = np.isfinite(p) & np.isfinite(obs)
    o, pp = obs[k], p[k]
    ss = float(np.sum((o - pp) ** 2))
    return 1.0 - ss / float(np.sum((o - o.mean()) ** 2)), float(np.sqrt(ss / k.sum()))


def build_pm_for_fit(medium_key, his_order):
    """The provider his fits used: growth law ON, static sectors, the medium set, O2 sinks
    closed -- and NOTHING else. The gasflux_configD overlay is used only for the medium
    plumbing, with its carbon cap switched OFF: what the fit applies is whatever that fit's own
    meta.json says, and applying the overlay's cap on top silently added a 230 mmol C cap to
    every configuration-E and -F run.

    ``his_order`` closes the four O2 sinks AFTER the provider is built, as his scripts do,
    instead of inside from_gecko. For configurations A-C that made no difference (P1); with an
    ETC area constraint it does, because the sector layer's translation_coeff is calibrated
    before the closure in his order and after it in ours.
    """
    from etcgem.config import build_provider
    cfg = resolve("eciML1515", "gasflux_configD")
    if his_order:
        cfg["close_free_o2_sinks"] = False
    cfg.setdefault("proteome_sectors", {})["biosynthesis_growth_law"] = True
    cfg["allocation_from_data"] = None
    cfg.setdefault("gasflux", {})["enabled"] = True
    cfg["gasflux"]["medium"] = medium_key
    cfg["gasflux"]["total_carbon_cap"]["enabled"] = False
    pm = build_provider(cfg)
    if his_order:
        m = pm.ec.model
        for rid in ("QMO2No1", "QMO3No1", "MOX", "CU1Opp"):
            if rid in m.reactions:
                m.reactions.get_by_id(rid).upper_bound = 0.0
        m.solver.update()
    pm.ec._alloc_from_data = None
    try:
        pm.ec.model.solver.configuration.timeout = 30
    except Exception:
        pass
    return pm


def predict(medium, medium_key, cfg, theta, specs, gdw_per_cell, etc_table_path, his_order):
    nat = to_natural(theta, specs)
    pert = to_pert(theta, specs)
    pm = build_pm_for_fit(medium_key, his_order)
    if cfg.get("use_etc"):
        table = EA.load_etc_table(etc_table_path)
        if cfg.get("use_configf"):
            EA.set_proton_stoichiometry(pm, table, verbose=False)
        gx = gas_exchange()
        mem = gx.get("membrane") or {}
        a_mem = EA.membrane_area_per_gdw(mem["sv_um2_per_fL"], mem["dcw_pg_per_fL"])
        f_etc = F_ETC_NOM * float(nat[f"F_ETC_{medium}_mult"])
        EA.add_etc_area_constraint(pm, table, EA.budget_from_fraction(a_mem, f_etc))
    if cfg.get("use_cap"):
        fixed = (cfg.get("cmax_fixed") or {}).get(medium)
        if fixed is not None:
            cap = float(fixed)
        else:
            nom = CAP_NOM_E[medium] if cfg.get("use_etc") else CAP_NOM[medium]
            cap = nom * float(nat[f"C_max_{medium}_mult"])
        add_total_carbon_constraint(pm, cap)
    df = flux_tpc(pm, DENSE, pert, metabolites=("o2",))
    o2_conv = float(gdw_per_cell) * MW_O2 / 60.0
    g = df["growth"].to_numpy(float)
    r = df["o2_uptake"].to_numpy(float) * o2_conv * float(nat["resp_scale"])
    return g, r, nat


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chains", default=os.environ.get(
        "PARSA_ROOT", "/Users/g.yvon-durocher/Downloads/etcGEMs-main_3")
        + "/strains/eciML1515/outputs")
    args = ap.parse_args()
    gdw = float(gas_exchange()["gdw_per_cell"])
    etc_e = os.path.join(ROOT, "strains/eciML1515/etc/complexes_szenk_merged_bd.csv")
    etc_f = os.path.join(ROOT, "strains/eciML1515/etc/complexes_configF_as_fitted.csv")

    rows = []
    for conf, medium, run in FITS:
        cdir = os.path.join(args.chains, run)
        if not os.path.exists(os.path.join(cdir, "chain.h5")):
            print(f"[gate] MISSING chain: {cdir}")
            continue
        cfg = json.load(open(os.path.join(cdir, "meta.json"))).get("cfg") or {}
        specs = build_specs(medium, cfg)
        th_map, th_med, it, nw = read_points(cdir)
        theta = th_map
        if len(theta) != len(specs):
            print(f"[gate] {conf}/{medium} [{run}]: chain has {len(theta)} params, "
                  f"specs {len(specs)} -- SKIP")
            continue
        table = etc_f if cfg.get("use_configf") else etc_e
        # NLDM: his fits predate the recipe medium, so both constructions are tried
        med_keys = ["NLDM_blanket", "NLDM"] if medium == "NLDM" else ["LB"]
        for mk in med_keys:
          for point, theta in (("MAP", th_map), ("posterior median", th_med)):
           for his_order in (True, False):
            g, r, nat = predict(medium, mk, cfg, theta, specs, gdw, table, his_order)
            for data_ver, fname in (("pre-fix", "derived_R2A_LB_20260907_prefix.csv"),
                                    ("current", "derived_R2A_LB_current.csv")):
                csv = os.path.join(RESP, fname)
                Tg, og = load_obs(csv, OTU[medium], "growth_C_per_C_h")
                Tr, orr = load_obs(csv, OTU[medium], "R_O2_mg_cell_min")
                gr2, grm = r2(og, Tg, g, DENSE)
                rr2, rrm = r2(orr, Tr, r, DENSE)
                rows.append({"config": conf, "medium": medium, "run": run, "model_medium": mk,
                             "point": point,
                             "o2_closure": "his (after build)" if his_order else "core (in provider)",
                             "data": data_ver, "growth_R2": gr2, "growth_RMSE": grm,
                             "resp_R2": rr2, "resp_RMSE": rrm,
                             "resp_scale": float(nat["resp_scale"]),
                             "F_ETC": (F_ETC_NOM * float(nat[f"F_ETC_{medium}_mult"])
                                       if cfg.get("use_etc") else np.nan),
                             "C_max": (float((cfg.get("cmax_fixed") or {}).get(medium))
                                       if (cfg.get("use_cap")
                                           and (cfg.get("cmax_fixed") or {}).get(medium) is not None)
                                       else ((CAP_NOM_E[medium] if cfg.get("use_etc")
                                              else CAP_NOM[medium])
                                             * float(nat.get(f"C_max_{medium}_mult", np.nan))
                                             if cfg.get("use_cap") else np.nan)),
                             "his_growth_R2": HIS[(conf, medium)].get("growth_r2", np.nan),
                             "his_resp_R2": HIS[(conf, medium)].get("resp_r2", np.nan),
                             "chain_steps": it, "walkers": nw})
                print(f"[gate] {conf}/{medium:4s} [{run[20:]:22s}] {point:16s} model={mk:13s} "
                      f"O2={'his ' if his_order else 'core'} data={data_ver:8s} "
                      f"growth R2={gr2:7.3f} (his {HIS[(conf,medium)].get('growth_r2', float('nan'))})"
                      f"   resp R2={rr2:8.3f} (his {HIS[(conf,medium)].get('resp_r2', float('nan'))})")
    out = pd.DataFrame(rows)
    out.to_csv(os.path.join(HERE, "gate_def_table.csv"), index=False)
    print(f"\nwrote {os.path.relpath(os.path.join(HERE, 'gate_def_table.csv'), ROOT)}")


if __name__ == "__main__":
    main()
