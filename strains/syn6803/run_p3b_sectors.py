#!/usr/bin/env python
"""P3b — cyanobacterial proteome-sector / allocation layer forward-check.

Attaches the Synechocystis-6803-specific sector + coupled growth-law layer (Jahn 2018 fractions
+ RIB slope; Zavrel 2019 P_total; reuse sectors.py) to the P3 thermal ecModel, then checks
whether the P3 Zavrel fit still holds at the P3 posterior-median parameters, and MEASURES the
allocation buffer = SS-E(sectored, growth law) - SS-E(single-pool P3). Re-calibration is only
needed if the fit shifts materially (expected NOT to, given the small absolute RIB slope over
the phototroph's tiny mu range).

Run from repo root with venv + Gurobi.
"""
import os, sys, json
import numpy as np
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO); os.chdir(REPO)
import logging, warnings
logging.getLogger("cobra").setLevel(logging.CRITICAL); warnings.filterwarnings("ignore")
from src.etcgem import calibration_multi as C
from src.etcgem.enzyme_cost import Perturbation
from src.etcgem.tpc import compute_tpc, TPC
from src.etcgem.sharpe_schoolfield import fit_sharpe_schoolfield as ssf

OUTDIR = os.path.join("strains", "syn6803", "outputs", "P3b_sectors")
os.makedirs(OUTDIR, exist_ok=True)
STRAIN = "syn6803"
PHOTON = "EX_photon_e"; RUBISCO = "RBPC_1"


def p3_median_pert(specs, extra=None):
    flat = np.load("strains/syn6803/outputs/calibration_zavrel/chain_flat.npy")
    med = np.array([np.median(flat[:, j]) for j in range(len(specs))])
    nat = {s.name: (float(np.exp(med[j])) if s.space == "log" else float(med[j]))
           for j, s in enumerate(specs)}
    kw = {s.pert: nat[s.name] for s in specs if s.pert is not None}
    if extra:
        kw.update(extra)
    return Perturbation(**kw), nat


def sweep(pm, temps, pert, want_flux=False):
    ecm = pm.ec; g = []; flux = []; shadow = []
    for Tc in temps:
        ecm.set_temperature(Tc + 273.15, pert)
        if pert.uses_allocation():
            ecm.set_allocation(pert.f_metab, pert.f_maint, kappa_scale=pert.kappa_scale,
                               sigma_sat=pert.sigma_sat)
        else:
            ecm.set_budget(ecm.default_budget)
        sol = ecm.model.optimize()
        gv = sol.objective_value if sol.status == "optimal" else 0.0
        gv = 0.0 if (gv is None or not np.isfinite(gv) or gv < 1e-6) else gv
        g.append(gv)
        flux.append(sol.fluxes.get(RUBISCO, 0.0) if (want_flux and gv > 0) else 0.0)
        shadow.append(abs(sol.reduced_costs.get(PHOTON, 0.0)) if gv > 0 else 0.0)
    return np.array(g), np.array(flux), np.array(shadow)


def main():
    specs = C.build_syn6803_specs()
    T_obs, obs, meta = C.load_zavrel(STRAIN)
    full = np.arange(5.0, 50.0 + 0.1, 1.0)

    # --- single-pool P3 baseline ---
    pm0 = C._build_pm_syn6803(STRAIN)
    pert0, nat = p3_median_pert(specs)
    g0, _, sh0 = sweep(pm0, full, pert0)
    d0 = TPC(full, g0).descriptors(); ss0 = ssf(full, g0)

    # --- sectored (growth law ON) at the SAME P3 params + nominal sector split ---
    pm1 = C._build_pm_syn6803_sectored(STRAIN)
    s = pm1.ec._sectors
    pert1, _ = p3_median_pert(specs, extra={"f_metab": s["f_metab_nom"], "f_maint": s["f_maint_nom"]})
    g1, cfix1, sh1 = sweep(pm1, full, pert1, want_flux=True)
    d1 = TPC(full, g1).descriptors(); ss1 = ssf(full, g1); ssf1_flux = ssf(full, cfix1)

    # --- sectored with slope forced to 0 (isolates the buffer, like M6) ---
    cfg0 = dict(C.SYN6803_SECTOR_CFG); cfg0["growth_law_slope"] = 0.0; cfg0["growth_law_f_bio0"] = s["f_bio_nom"]
    pm2 = C._build_pm_syn6803_sectored(STRAIN, cfg0)
    pert2, _ = p3_median_pert(specs, extra={"f_metab": s["f_metab_nom"], "f_maint": s["f_maint_nom"]})
    g2, _, _ = sweep(pm2, full, pert2)
    ss2 = ssf(full, g2)

    # buffer = SS-E(growth law ON) - SS-E(growth law OFF, slope 0)
    buffer = ss1.E - ss2.E
    # fit deltas vs P3 single pool
    at_obs1, _, _ = sweep(pm1, T_obs, pert1)
    resid = 100 * (at_obs1 - obs) / obs

    out = {
        "sector_fractions": {"f_metab": s["f_metab_nom"], "f_bio": s["f_bio_nom"], "f_maint": s["f_maint_nom"],
                             "P_total_backed_out": round(s["P_total"], 4),
                             "growth_law_slope": s["growth_law_slope"], "f_bio_0": s["f_bio_0"],
                             "translation_coeff": round(s["translation_coeff"], 4), "mu_nominal": round(s["mu_nominal"], 4)},
        "single_pool_P3": {"rmax": round(d0.rmax, 4), "Topt_C": round(d0.Topt_C, 2), "CTmax_C": round(d0.CTmax_C, 2),
                           "SS_E_eV": round(ss0.E, 3)},
        "sectored_growth_law_ON": {"rmax": round(d1.rmax, 4), "Topt_C": round(d1.Topt_C, 2), "CTmax_C": round(d1.CTmax_C, 2),
                                   "SS_E_eV": round(ss1.E, 3), "carbon_fixation_SS_E": round(ssf1_flux.E, 3)},
        "sectored_growth_law_OFF_slope0": {"SS_E_eV": round(ss2.E, 3)},
        "allocation_buffer_eV": round(buffer, 4),
        "deltas_vs_single_pool": {"d_rmax": round(d1.rmax - d0.rmax, 4), "d_Topt_C": round(d1.Topt_C - d0.Topt_C, 2),
                                  "d_CTmax_C": round(d1.CTmax_C - d0.CTmax_C, 2), "d_SS_E": round(ss1.E - ss0.E, 4),
                                  "max_abs_dmu": round(float(np.max(np.abs(g1 - g0))), 5)},
        "zavrel_refit_residual_pct": [round(float(x), 1) for x in resid],
        "photon_shadow_max": round(float(max(sh0.max(), sh1.max())), 6),
        "recalibration_needed": bool(abs(ss1.E - ss0.E) > 0.05 or abs(d1.rmax - d0.rmax) / max(d0.rmax, 1e-9) > 0.10),
        "cross_org_allocation_buffer": {"E_coli": -0.130, "methanogen": 0.000, "phototroph": round(buffer, 4)},
    }
    with open(os.path.join(OUTDIR, "p3b_forward_check.json"), "w") as fh:
        json.dump(out, fh, indent=2)
    print(json.dumps(out, indent=2))

    # figure: single-pool vs sectored TPC + Zavrel
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(full, g0, "-", color="#1f78b4", lw=2, label=f"single-pool P3 (SS-E {ss0.E:.3f})")
    ax.plot(full, g1, "--", color="#e31a1c", lw=2, label=f"sectored + growth law (SS-E {ss1.E:.3f})")
    ax.plot(T_obs, obs, "o", color="k", ms=6, label="Zavrel 2015")
    ax.set_xlabel("temperature (C)"); ax.set_ylabel("growth rate (1/h)")
    ax.set_title(f"P3b sector layer: allocation buffer = {buffer:+.3f} eV\n"
                 f"(E.coli -0.13 | methanogen 0.00 | phototroph {buffer:+.3f})")
    ax.legend(fontsize=8); ax.grid(alpha=0.3)
    fig.tight_layout(); fig.savefig(os.path.join(OUTDIR, "sectored_vs_singlepool_tpc.png"), dpi=140); plt.close(fig)
    print(f"\n[P3b] wrote {OUTDIR}/p3b_forward_check.json + sectored_vs_singlepool_tpc.png")


if __name__ == "__main__":
    main()
