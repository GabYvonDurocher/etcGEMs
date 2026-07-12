#!/usr/bin/env python
"""P2 — thermal envelope + emergent light-saturated growth TPC for Synechocystis 6803.

Attaches the temperature-dependent enzyme envelope (kcat(T) MMRT + two-state unfolding
f_N(T) + NGAM(T)) to the pre-built AUTOPACMEN sMOMENT ecModel iSynCJ816_STAR, reusing the
E. coli / methanogen thermal machinery (providers.from_gecko route-B + enzyme_cost +
unfolding). EMERGENT: nothing is fit to the Zavrel 2015 data. Operated under the P1
light-SATURATED autotrophic medium (photon non-limiting, CO2 available, organic-C closed).

Outputs under outputs/P2_thermal/: emergent growth TPC + carbon-fixation-flux TPC, SS-E and
TPC descriptors, the Zavrel-2015 a-priori overlay figure.
Run from repo root with the venv + Gurobi.
"""
import logging, warnings, os, json, sys
logging.getLogger("cobra").setLevel(logging.CRITICAL)
warnings.filterwarnings("ignore")
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)
import cobra
cobra.Configuration().solver = "gurobi"

from src.etcgem.providers import from_gecko
from src.etcgem.enzyme_cost import Perturbation
from src.etcgem import unfolding as U
from src.etcgem.sharpe_schoolfield import fit_sharpe_schoolfield

STRAIN = os.path.join(REPO, "strains", "syn6803")
STAR = os.path.join(STRAIN, "model", "ecmodel_iSynCJ816_STAR", "iSynCJ816_STAR.xml")
PARAMS = os.path.join(STRAIN, "thermal", "enzyme_thermal_params.csv")
OUTDIR = os.path.join(STRAIN, "outputs", "P2_thermal")
os.makedirs(OUTDIR, exist_ok=True)

T0_C = 35.0                     # reference (Zavrel optimum)
POOL_BUDGET = 0.26              # STAR grounded sMOMENT enzyme budget (emergent P_metab)
NGAM_TARGET_35C = 3.12          # mmol ATP/gDW/h ~ Touloupakis 2015 maintenance 3.12 mmol photon/gDW/h
BIOMASS = "BIOMASS_Ec_SynAuto_1"
RUBISCO = "RBPC_1"
PHOTON = "EX_photon_e"


def light_saturated_autotrophic(model):
    """P1 medium: photon non-limiting, inorganic C available, organic C closed."""
    if "EX_glc__D_e" in [r.id for r in model.reactions]:
        model.reactions.get_by_id("EX_glc__D_e").lower_bound = 0.0
    for oc in ("EX_ac_e", "EX_pyr_e", "EX_succ_e", "EX_glcglyc_e"):
        if oc in [r.id for r in model.reactions]:
            model.reactions.get_by_id(oc).lower_bound = 0.0
    model.reactions.get_by_id("EX_co2_e").lower_bound = -1000.0
    model.reactions.get_by_id(PHOTON).lower_bound = -999999.0
    model.objective = BIOMASS


def main():
    # NGAM amplitude anchor: NGAM(35 C) = 3.12 mmol ATP/gDW/h (Touloupakis 2015).
    ngam_base_scale = NGAM_TARGET_35C / U.ngam_T(273.15 + 35.0, scale=1.0)
    print(f"[P2] NGAM(T) anchor: base_scale={ngam_base_scale:.4f} "
          f"-> NGAM(35C)={U.ngam_T(273.15+35.0, scale=ngam_base_scale):.2f}, "
          f"NGAM(25C)={U.ngam_T(273.15+25.0, scale=ngam_base_scale):.2f}, "
          f"NGAM(44C)={U.ngam_T(273.15+44.0, scale=ngam_base_scale):.2f} mmol ATP/gDW/h")

    pm = from_gecko(
        STAR, T0=273.15 + T0_C,
        thermal_model="unfolding",
        enzyme_params=PARAMS, enzyme_params_key="rxn_id",
        budget_override=POOL_BUDGET,
        ngam_temperature=True, ngam_rxn="ATPM", ngam_base_scale=ngam_base_scale,
        dcp_prior_kJ=-4.0,
        close_free_o2_sinks=False,     # cyano: no E. coli O2-sink curation
        prot_prefix="prot_", pool_id="prot_pool", biomass_rxn=BIOMASS,
    )
    ecm = pm.ec
    light_saturated_autotrophic(ecm.model)

    # --- sweep temperature: emergent growth TPC + carbon-fixation-flux TPC ---
    temps = np.arange(5.0, 50.0 + 0.1, 1.0)
    pert = Perturbation()
    growth, cfix, photon_used, photon_shadow, pool_draw = [], [], [], [], []
    for Tc in temps:
        ecm.set_temperature(Tc + 273.15, pert)
        sol = ecm.model.optimize()
        g = sol.objective_value if (sol.status == "optimal") else 0.0
        g = 0.0 if (g is None or not np.isfinite(g) or g < 1e-6) else g
        growth.append(g)
        cfix.append(sol.fluxes.get(RUBISCO, 0.0) if g > 0 else 0.0)
        photon_used.append(-sol.fluxes.get(PHOTON, 0.0) if g > 0 else 0.0)
        try:
            photon_shadow.append(sol.reduced_costs.get(PHOTON, np.nan) if g > 0 else np.nan)
        except Exception:
            photon_shadow.append(np.nan)
        pool_draw.append(ecm._pool.primal if hasattr(ecm._pool, "primal") else np.nan)
    growth = np.array(growth); cfix = np.array(cfix)
    photon_used = np.array(photon_used); photon_shadow = np.array(photon_shadow)

    # --- descriptors ---
    from src.etcgem.tpc import TPC
    tpc = TPC(temps, growth)
    d = tpc.descriptors()
    ss_growth = fit_sharpe_schoolfield(temps, growth, T_ref_C=20.0)
    ss_cfix = fit_sharpe_schoolfield(temps, cfix, T_ref_C=20.0)

    i_pk = int(np.argmax(growth))
    Topt_C = float(temps[i_pk]); rmax = float(growth[i_pk])
    # photon non-binding check at the emergent optimum (and across the growing range)
    grow_mask = growth > 0.05 * rmax
    nonbind = np.nanmax(np.abs(photon_shadow[grow_mask])) if grow_mask.any() else np.nan

    print(f"\n[P2] EMERGENT growth TPC: Topt={Topt_C:.1f} C  rmax={rmax:.4f} /h  "
          f"CTmax={d.CTmax_C:.1f} C  niche={d.niche_width_C:.1f} C")
    print(f"     SS-E (growth)  = {ss_growth.E:.3f} eV (R2={ss_growth.r2:.3f}, ok={ss_growth.ok})")
    print(f"     SS-E (C-fix)   = {ss_cfix.E:.3f} eV (R2={ss_cfix.r2:.3f}, ok={ss_cfix.ok})")
    print(f"     photon |shadow price| max over growing range = {nonbind:.2e} "
          f"(~0 => photon NON-binding across the sweep; light-saturated holds)")
    print(f"     Zavrel 2015: Topt~35 C, SS-E~0.42 eV (Q10 1.70), CTmax~44 C")

    # --- save TPC csv ---
    import csv as _csv
    tpc_csv = os.path.join(OUTDIR, "emergent_tpc.csv")
    with open(tpc_csv, "w", newline="") as fh:
        w = _csv.writer(fh)
        w.writerow(["T_C", "growth_per_h", "carbon_fixation_RBPC_1", "photon_used", "photon_shadow_price"])
        for i in range(len(temps)):
            w.writerow([f"{temps[i]:.1f}", f"{growth[i]:.6f}", f"{cfix[i]:.4f}",
                        f"{photon_used[i]:.3f}", f"{photon_shadow[i]:.3e}"])

    desc = {
        "emergent_growth": {**d.as_dict(), "Topt_C": Topt_C, "rmax_per_h": rmax,
                            "SS_E_eV": ss_growth.E, "SS_E_R2": ss_growth.r2, "SS_ok": ss_growth.ok,
                            "SS_Th_C": ss_growth.T_h_C},
        "emergent_carbon_fixation": {"SS_E_eV": ss_cfix.E, "SS_E_R2": ss_cfix.r2, "SS_ok": ss_cfix.ok,
                                     "Topt_C": float(temps[int(np.argmax(cfix))]) if cfix.max() > 0 else None},
        "zavrel2015": {"Topt_C": 35.0, "SS_E_eV": 0.420, "Q10_rising": 1.70, "CTmax_C": 44.0,
                       "light_umol_m2_s": "220-360 (saturating)"},
        "photon_nonbinding_maxabs_shadow": float(nonbind),
        "ngam_base_scale": float(ngam_base_scale), "pool_budget_gDW": POOL_BUDGET,
        "n_thermal_enzymes": len(ecm.table),
    }
    with open(os.path.join(OUTDIR, "descriptors.json"), "w") as fh:
        json.dump(desc, fh, indent=2)

    # --- figure: emergent TPC (raw + normalised) vs Zavrel 2015 descriptors ---
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.3))
    ax[0].plot(temps, growth, "-o", ms=3, color="#1b7837", label="emergent growth TPC")
    ax[0].axvline(35, ls=":", color="#762a83", label="Zavrel Topt 35 C")
    ax[0].axvline(44, ls="--", color="#b35806", alpha=0.7, label="Zavrel CTmax ~44 C")
    ax[0].set_xlabel("temperature (C)"); ax[0].set_ylabel("growth rate (1/h)")
    ax[0].set_title(f"emergent (a-priori) growth TPC\nTopt={Topt_C:.0f}C  SS-E={ss_growth.E:.2f}eV")
    ax[0].legend(fontsize=7); ax[0].grid(alpha=0.3)
    # normalised shape + Zavrel rising-limb slope reference (E=0.42 eV)
    gn = growth / growth.max() if growth.max() > 0 else growth
    ax[1].plot(temps, gn, "-o", ms=3, color="#1b7837", label="emergent (norm.)")
    kB = 8.617333e-5
    rl = (temps >= 15) & (temps <= 35)
    Tk = temps[rl] + 273.15
    zav = np.exp((0.420 / kB) * (1.0 / (35 + 273.15) - 1.0 / Tk))
    ax[1].plot(temps[rl], zav, "--", color="#762a83", label="Zavrel rising limb (E=0.42 eV)")
    ax[1].set_xlabel("temperature (C)"); ax[1].set_ylabel("growth / max")
    ax[1].set_title("normalised shape vs Zavrel rising-limb Ea")
    ax[1].legend(fontsize=7); ax[1].grid(alpha=0.3)
    fig.tight_layout()
    figpath = os.path.join(OUTDIR, "emergent_tpc_vs_zavrel.png")
    fig.savefig(figpath, dpi=140); plt.close(fig)
    print(f"\n[P2] wrote {tpc_csv}\n     {os.path.join(OUTDIR,'descriptors.json')}\n     {figpath}")


if __name__ == "__main__":
    main()
