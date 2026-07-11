"""Re-base the E. coli Ea dissection from the window-dependent Arrhenius slope to the
window-independent Sharpe-Schoolfield E. Reuses the saved per-enzyme control coefficients
C_i + per-enzyme kcat(T) Arrhenius E (the multi-hour part), and only regenerates the
organism-level TPCs (tuned / growth-law-off / NGAM-flat) to get the SS-E terms.

  python strains/eciML1515/run_ea_rebase_ss.py

Writes strains/eciML1515/outputs/ea_dissection_ss/{decomposition_ss.json, per_enzyme_*.csv}.
Keeps the slope-version outputs untouched.
"""
import json
import logging
import os
import sys
import warnings

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
logging.getLogger("cobra").setLevel(logging.CRITICAL)
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd


def main():
    import cobra
    cobra.Configuration().solver = "gurobi"
    from src.etcgem import ea_dissection as EA
    from src.etcgem.enzyme_cost import Perturbation

    STRAIN = "eciML1515"
    OUT = os.path.join("strains", STRAIN, "outputs", "ea_dissection_ss")
    SLOPE = os.path.join("strains", STRAIN, "outputs", "ea_dissection")
    os.makedirs(OUT, exist_ok=True)
    grid = np.linspace(5, 52, 48)
    pert, med = EA.tuned_pert()

    def cw(df):
        """control-weighted means from a saved per-enzyme frame."""
        sC = float(df["C_i"].sum())
        return {"sum_C": sC,
                "cw_kcat": float((df["C_i"] * df["Ea_kcat_eV"]).sum()) / sC,
                "cw_fN": float((df["C_i"] * df["Ea_fN_eV"]).sum()) / sC,
                "cw_kcat_fN": float((df["C_i"] * df["Ea_i_eV"]).sum()) / sC,
                "unweighted_kcat": float(df["Ea_kcat_eV"].mean())}

    results = {}
    for medium, csv in [("BHI", "ea_per_enzyme_BHI.csv"), ("glucose_minimal", "ea_per_enzyme_glucose.csv")]:
        df = pd.read_csv(os.path.join(SLOPE, csv))
        c = cw(df)
        # tuned provider at this medium (growth law ON) -> SS-E + windowed-slope cross-check
        pm, _ = EA.build_pm(STRAIN, medium, growth_law=True, close_o2=True)
        SS_tuned, ssfit, _ = EA.ea_org_ss(pm, pert, grid)
        slope_tuned, _, _ = EA.ea_org(pm, pert, grid)
        # maintenance: flatten NGAM(T) on the SAME provider -> Delta SS-E
        saved = pm.ec.ngam_temperature
        pm.ec.ngam_temperature = False
        SS_ngamflat, _, _ = EA.ea_org_ss(pm, pert, grid)
        pm.ec.ngam_temperature = saved
        d_maint = SS_tuned - SS_ngamflat
        # allocation: growth-law-off provider -> Delta SS-E
        pm_gl, _ = EA.build_pm(STRAIN, medium, growth_law=False, close_o2=True)
        SS_GLoff, _, _ = EA.ea_org_ss(pm_gl, pert, grid)
        d_alloc = SS_tuned - SS_GLoff
        residual = SS_tuned - (c["cw_kcat"] + d_alloc + d_maint)
        results[medium] = {
            "Ea_org_SS_E": round(SS_tuned, 4), "SS_fit_r2": round(ssfit.r2, 4),
            "SS_Eh_eV": round(ssfit.E_h, 3), "SS_Th_C": round(ssfit.T_h_C, 2),
            "windowed_slope_crosscheck": round(slope_tuned, 4),
            "control_weighted_mean_kcat_E": round(c["cw_kcat"], 4),
            "  of_which_native_fraction_fN": round(c["cw_fN"], 4),
            "  control_weighted_kcat_fN": round(c["cw_kcat_fN"], 4),
            "unweighted_mean_kcat_E": round(c["unweighted_kcat"], 4),
            "sum_C_i": round(c["sum_C"], 3),
            "allocation_growth_law_SS": round(d_alloc, 4),
            "maintenance_NGAM_SS": round(d_maint, 4),
            "residual_nonlinear_SS": round(residual, 4),
            "SS_growth_law_off": round(SS_GLoff, 4), "SS_ngam_flat": round(SS_ngamflat, 4),
            "closure_check": round(c["cw_kcat"] + d_alloc + d_maint + residual, 4),
        }
        print(f"[{medium}] SS-E={SS_tuned:.4f} (slope {slope_tuned:.4f}); cw_kcat={c['cw_kcat']:.4f} "
              f"fN={c['cw_fN']:+.4f}; alloc={d_alloc:+.4f} maint={d_maint:+.4f} resid={residual:+.4f}")

    # emergent BHI SS-E (structural check) + observed VdL SS-E cross-check
    pm_em, _ = EA.build_pm(STRAIN, "BHI", growth_law=True, close_o2=True)
    SS_em, emfit, _ = EA.ea_org_ss(pm_em, Perturbation(f_metab=0.280, f_maint=0.360), grid)
    from src.etcgem.sharpe_schoolfield import fit_sharpe_schoolfield
    ze = np.load(os.path.join(SLOPE.replace("ea_dissection", "calibration_vanderlinden"),
                              "posterior_predictive.npz"))
    obs_fit = fit_sharpe_schoolfield(ze["obs_T"], ze["obs"], T_ref_C=20.0)
    results["emergent_BHI_SS_E"] = round(SS_em, 4)
    results["observed_VdL_SS_E"] = round(obs_fit.E, 4)
    results["meta"] = {"convention": "Sharpe-Schoolfield E (Schoolfield 1981), T_ref=20C; "
                       "per-enzyme E_i = kcat(T) rising-limb Arrhenius E (f_N separated to "
                       "the deactivation side, contribution ~-0.008 eV, negligible)",
                       "tuned_medians": med}
    print(f"[emergent BHI] SS-E={SS_em:.4f}; observed VdL SS-E={obs_fit.E:.4f}")
    json.dump(results, open(os.path.join(OUT, "decomposition_ss.json"), "w"), indent=2, default=str)
    print("wrote", os.path.join(OUT, "decomposition_ss.json"))


if __name__ == "__main__":
    main()
