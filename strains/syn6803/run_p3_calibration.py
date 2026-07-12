#!/usr/bin/env python
"""P3 — Bayesian calibration of the Synechocystis 6803 thermal etc-GEM to the Zavrel 2015
light-saturated growth TPC (shape-first), reusing calibration_multi.py (emcee).

Runs the emcee fit (run_syn6803) then computes the P3 diagnostics:
- observed Zavrel SS-E + CI (PART A),
- calibrated vs emergent rising-limb SS-E over the Zavrel window (the crux),
- the Ea-lever diagnostic (which knob; is the demanded dCp/topt plausible),
- the calibrated CARBON-FIXATION-flux SS-E vs Inoue 2001 O2-evolution (~0.52, not fit),
- Inoue light-limited growth + Inoue O2 flux cross-check overlays.
Writes strains/syn6803/outputs/calibration_zavrel/p3_diagnostics.json + cross-check figure.

Run from repo root with venv + Gurobi + emcee.  Env: N_STEPS (default 4000), N_WALKERS (48).
"""
import os, sys, json, time
import numpy as np
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)
os.chdir(REPO)

import logging, warnings
logging.getLogger("cobra").setLevel(logging.CRITICAL); warnings.filterwarnings("ignore")
import pandas as pd
from src.etcgem import calibration_multi as C
from src.etcgem.enzyme_cost import Perturbation
from src.etcgem.tpc import compute_tpc
from src.etcgem.sharpe_schoolfield import fit_sharpe_schoolfield

STRAIN = "syn6803"
OUTDIR = os.path.join("strains", STRAIN, "outputs", "calibration_zavrel")
THERMAL = os.path.join("strains", STRAIN, "thermal")
RUBISCO = "RBPC_1"


def ss_over(pm, temps, pert):
    """SS-E of the growth TPC over a temperature grid at a parameter point."""
    g = compute_tpc(pm, temps, pert).growth
    return fit_sharpe_schoolfield(temps, g, T_ref_C=20.0), g


def carbon_fixation_ssE(pm, temps, pert):
    """SS-E of the RuBisCO carboxylase-flux TPC (secondary descriptor)."""
    ecm = pm.ec; flux = []
    for Tc in temps:
        ecm.set_temperature(Tc + 273.15, pert)
        ecm.set_budget(ecm.default_budget)
        sol = ecm.model.optimize()
        flux.append(sol.fluxes.get(RUBISCO, 0.0) if sol.status == "optimal" else 0.0)
    flux = np.array(flux)
    return fit_sharpe_schoolfield(temps, flux, T_ref_C=20.0), flux


def main():
    n_steps = int(os.environ.get("N_STEPS", 4000))
    n_walk = int(os.environ.get("N_WALKERS", 48))
    t0 = time.time()
    res = C.run_syn6803(STRAIN, OUTDIR, n_walkers=n_walk, n_steps_max=n_steps,
                        target_neff=400, seed=1, progress=False)
    print(f"[P3] emcee done in {time.time()-t0:.0f}s; n_eff={res['sampler']['n_eff']} "
          f"stop={res['sampler']['stop_reason']}")

    # rebuild provider (parent process) for diagnostics
    pm = C._build_pm_syn6803(STRAIN)
    specs = C.build_syn6803_specs()
    T_obs, obs, meta = C.load_zavrel(STRAIN)
    flat = np.load(os.path.join(OUTDIR, "chain_flat.npy"))
    med_theta = np.array([np.median(flat[:, j]) for j in range(len(specs))])
    emergent_theta = np.array([np.log(s.emergent) if s.space == "log" else s.emergent
                               for s in specs[:-1]] + [np.log(0.3)])

    # --- PART A: observed Zavrel SS-E + CI ---
    ss_obs = fit_sharpe_schoolfield(T_obs, obs, T_ref_C=20.0)
    obs_ci = [ss_obs.E - 1.96 * ss_obs.E_sd, ss_obs.E + 1.96 * ss_obs.E_sd]

    # --- crux: SS-E over the Zavrel window, emergent vs posterior-median ---
    win = np.linspace(23, 38, 16)
    ss_em, _ = ss_over(pm, win, C.to_pert(emergent_theta, specs))
    ss_po, g_po = ss_over(pm, win, C.to_pert(med_theta, specs))
    # full-range posterior TPC descriptors
    full = np.arange(5.0, 50.0 + 0.1, 1.0)
    _, g_full = ss_over(pm, full, C.to_pert(med_theta, specs))
    from src.etcgem.tpc import TPC
    d_full = TPC(full, g_full).descriptors()

    # --- carbon-fixation-flux SS-E (posterior) vs Inoue O2-evolution (light-saturated) ---
    ss_cfix, cfix_flux = carbon_fixation_ssE(pm, full, C.to_pert(med_theta, specs))
    inoue_o2 = pd.read_csv(os.path.join(THERMAL, "Inoue2001_O2evol.csv")).sort_values("temperature_c")
    ss_inoue_o2 = fit_sharpe_schoolfield(inoue_o2["temperature_c"].to_numpy(float),
                                         inoue_o2["O2evol_umolO2_mgChla_h"].to_numpy(float), T_ref_C=20.0)
    inoue_gr = pd.read_csv(os.path.join(THERMAL, "Inoue2001_tpc.csv")).sort_values("temperature_c")

    # posterior median natural params
    nat_med = {s.name: (float(np.exp(med_theta[j])) if s.space == "log" else float(med_theta[j]))
               for j, s in enumerate(specs)}
    dcp_med = nat_med["dCp_scale"]
    dcp_curv = -4.0 * dcp_med   # effective per-enzyme MMRT curvature (kJ/mol/K)

    diag = {
        "observed_zavrel": {"SS_E_eV": round(ss_obs.E, 3), "SS_E_sd": round(ss_obs.E_sd, 3),
                            "SS_E_95CI": [round(obs_ci[0], 3), round(obs_ci[1], 3)],
                            "R2": round(ss_obs.r2, 3), "n": meta["n"], "rmax": meta["obs_rmax"],
                            "Topt_C": meta["obs_Topt_C"], "window_C": [23, 38]},
        "rising_limb_SS_E_window23_38": {
            "emergent": round(ss_em.E, 3), "posterior_median": round(ss_po.E, 3),
            "observed": round(ss_obs.E, 3),
            "reaches_observed_within_CI": bool(obs_ci[0] <= ss_po.E <= obs_ci[1])},
        "posterior_full_range_descriptors": {
            "Topt_C": round(d_full.Topt_C, 2), "rmax": round(d_full.rmax, 4),
            "CTmax_C": round(d_full.CTmax_C, 2)},
        "Ea_lever_diagnostic": {
            "dCp_scale_median": round(dcp_med, 3),
            "dCp_scale_90CI": [round(float(np.percentile(np.exp(flat[:, 3]), 5)), 3),
                               round(float(np.percentile(np.exp(flat[:, 3]), 95)), 3)],
            "effective_curvature_kJ_per_mol_K": round(dcp_curv, 2),
            "prior_curvature_kJ_per_mol_K": -4.0,
            "kcat_scale_median": round(nat_med["kcat_scale"], 3),
            "topt_scale_median": round(nat_med["topt_scale"], 3),
            "rails_dCp_floor": bool(dcp_med < 0.28)},
        "carbon_fixation_flux": {
            "posterior_SS_E_eV": round(ss_cfix.E, 3), "posterior_Topt_C": round(float(full[int(np.argmax(cfix_flux))]), 1),
            "inoue2001_O2evol_SS_E_eV": round(ss_inoue_o2.E, 3), "inoue2001_O2evol_SS_E_sd": round(ss_inoue_o2.E_sd, 3)},
        "posterior_median_params": {k: round(v, 4) for k, v in nat_med.items()},
    }
    with open(os.path.join(OUTDIR, "p3_diagnostics.json"), "w") as fh:
        json.dump(diag, fh, indent=2)
    print("[P3] diagnostics:\n" + json.dumps(diag, indent=2))

    # --- cross-check figure: calibrated growth vs Inoue light-limited; flux vs Inoue O2 ---
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.4))
    ax[0].plot(full, g_full, "-", color="#d95f02", lw=2, label="calibrated growth TPC (light-sat)")
    ax[0].plot(T_obs, obs, "o", color="k", ms=6, label="Zavrel 2015 (fit target)")
    ax[0].plot(inoue_gr["temperature_c"], inoue_gr["doublings_d"] / inoue_gr["doublings_d"].max() * g_full.max(),
               "s--", color="#7570b3", ms=4, alpha=0.8, label="Inoue light-LIMITED growth (norm., x-check)")
    ax[0].set_xlabel("temperature (C)"); ax[0].set_ylabel("growth rate (1/h)")
    ax[0].set_title(f"calibrated growth vs data\nSS-E: calib {ss_po.E:.2f} / Zavrel {ss_obs.E:.2f} eV")
    ax[0].legend(fontsize=7); ax[0].grid(alpha=0.3)
    axb = ax[1]; axb.plot(full, cfix_flux / cfix_flux.max(), "-", color="#1b9e77", lw=2,
                          label=f"calibrated C-fixation flux (SS-E {ss_cfix.E:.2f})")
    o2 = inoue_o2["O2evol_umolO2_mgChla_h"].to_numpy(float)
    axb.plot(inoue_o2["temperature_c"], o2 / o2.max(), "^--", color="#e7298a", ms=5,
             label=f"Inoue O2-evol flux (SS-E {ss_inoue_o2.E:.2f}, x-check)")
    axb.set_xlabel("temperature (C)"); axb.set_ylabel("flux / max")
    axb.set_title("light-saturated FLUX cross-check (Yvon-Durocher 2014 comparison)")
    axb.legend(fontsize=7); axb.grid(alpha=0.3)
    fig.tight_layout(); fig.savefig(os.path.join(OUTDIR, "inoue_crosschecks.png"), dpi=140); plt.close(fig)
    print(f"[P3] wrote {OUTDIR}/p3_diagnostics.json + inoue_crosschecks.png")


if __name__ == "__main__":
    main()
