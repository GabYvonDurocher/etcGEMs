"""SINGLE SOURCE OF TRUTH for the two canonical Sharpe-Schoolfield activation energies per
organism used everywhere in the paper:

  E_a(observed) := SS-E fit to the OBSERVED CALIBRATION data points (methanogen Jones; E. coli
                   Van Derlinden; phototroph ZAVREL GROWTH), with a +/-5% resampling 90% CI.
  E_a(model)    := SS-E of the CALIBRATED (sectored, posterior-median) model TPC = the value the
                   control-weighted decomposition sums to (methanogen 1.06; respiration 0.68;
                   photosynthesis 0.57). This is the CANONICAL quoted model number.

Also records, for context: the Fig-1 SS-E POSTERIOR median + 90% CI (the spread shown by the
violins; its median differs from E_a(model) because the SS-E posterior is right-skewed — for the
phototroph most, being the widest parameter posterior), and the phototroph INOUE light-saturated
FLUX SS-E as an independent cross-check (kept DISTINCT from the Zavrel-growth observed value).

Reuses saved calibration data / posterior draws + the decomposition outputs; no model re-runs,
no re-calibration.  Writes outputs/ea_cross_organism/ss_e_canonical.{csv,json}.

  python reports/activation_energy/gen_ss_e_canonical.py
"""
import json, logging, os, sys, warnings
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
logging.getLogger("cobra").setLevel(logging.CRITICAL); warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from src.etcgem.sharpe_schoolfield import fit_sharpe_schoolfield as ssf

OUT = "outputs/ea_cross_organism"
PP = {"methanogen": "strains/mmaripaludis/outputs/calibration_jones/posterior_predictive.npz",
      "ecoli": "strains/eciML1515/outputs/calibration_vanderlinden/posterior_predictive.npz",
      "phototroph": "strains/syn6803/outputs/calibration_zavrel/posterior_predictive.npz"}
# E_a(model): the decomposition targets (SS-E of the calibrated sectored model at posterior-median
# params). Read from the dissection JSONs where available; E. coli from the two-way comparison.
DECOMP = {"methanogen": "strains/mmaripaludis/outputs/ea_dissection_ss/decomposition_ss.json",
          "phototroph": "strains/syn6803/outputs/ea_dissection_ss/decomposition_ss.json"}
POST = "reports/activation_energy/assets/fig1/ss_e_posteriors.json"
STUDY = {"methanogen": "Jones 1983 (H2/CO2 growth)", "ecoli": "Van Derlinden 2012 (BHI growth)",
         "phototroph": "Zavrel 2015 (light-saturated growth)"}


def boot_ci(T, r, n=400, noise=0.05, seed=0):
    rng = np.random.default_rng(seed)
    E0 = ssf(T, r, T_ref_C=20.0)
    Es = [f.E for f in (ssf(T, np.asarray(r) * (1 + noise * rng.standard_normal(len(r))), T_ref_C=20.0)
                        for _ in range(n)) if f.ok and np.isfinite(f.E)]
    Es = np.array(Es)
    return float(E0.E), [float(np.percentile(Es, 5)), float(np.percentile(Es, 95))], float(E0.r2)


def main():
    post = json.load(open(POST))
    ea_model = {"methanogen": json.load(open(DECOMP["methanogen"]))["Ea_org_SS_E"],
                "ecoli": 0.6784,   # two-way comparison.json (E. coli BHI decomposition)
                "phototroph": json.load(open(DECOMP["phototroph"]))["Ea_org_SS_E"]}
    rows = []
    for k in ("methanogen", "ecoli", "phototroph"):
        d = np.load(PP[k]); Eo, ci, r2 = boot_ci(d["obs_T"], d["obs"])
        row = {"organism": k, "study_observed": STUDY[k],
               "E_a_observed": round(Eo, 3), "E_a_observed_CI90_lo": round(ci[0], 3),
               "E_a_observed_CI90_hi": round(ci[1], 3), "observed_fit_R2": round(r2, 3),
               "n_observed_points": int(len(d["obs"])),
               "E_a_model": round(float(ea_model[k]), 3),
               "E_a_model_posterior_median": round(post[k]["median"], 3),
               "E_a_model_posterior_CI90_lo": round(post[k]["ci90"][0], 3),
               "E_a_model_posterior_CI90_hi": round(post[k]["ci90"][1], 3),
               "model_inside_observed_CI": bool(ci[0] <= float(ea_model[k]) <= ci[1])}
        rows.append(row)
    # phototroph Inoue light-saturated FLUX cross-check (kept distinct)
    io = pd.read_csv("strains/syn6803/thermal/Inoue2001_O2evol.csv").sort_values("temperature_c")
    Ef, cif, r2f = boot_ci(io["temperature_c"].to_numpy(float), io["O2evol_umolO2_mgChla_h"].to_numpy(float))
    for row in rows:
        if row["organism"] == "phototroph":
            row["E_a_Inoue_flux_crosscheck"] = round(Ef, 3)
            row["E_a_Inoue_flux_CI90"] = [round(cif[0], 3), round(cif[1], 3)]
            row["model_carbon_fixation_flux_SS_E"] = 0.563   # P4 dissection (matches Inoue 0.52)

    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(OUT, "ss_e_canonical.csv"), index=False)
    meta = {"note": ("E_a(observed): SS-E fit to the calibration data points (+/-5% resample 90% CI). "
                     "E_a(model): SS-E of the calibrated sectored model at posterior-median params = "
                     "the control-weighted decomposition target (the CANONICAL model number). The Fig-1 "
                     "posterior median differs from E_a(model) because the SS-E posterior is right-skewed "
                     "(largest for the phototroph, the widest parameter posterior); mark the POINT E_a(model) "
                     "on the violin and report the posterior median/CI as spread. Phototroph Zavrel-growth "
                     "observed SS-E is fragile (6 points, CI [0.34,0.92]) so it must always appear WITH its "
                     "CI; the model 0.57 sits well inside it. Inoue flux (0.52) is an independent cross-check, "
                     "NOT the observed value."),
            "rows": rows}
    json.dump(meta, open(os.path.join(OUT, "ss_e_canonical.json"), "w"), indent=2)
    print(df.to_string(index=False))
    print("\nwrote", os.path.join(OUT, "ss_e_canonical.{csv,json}"))


if __name__ == "__main__":
    main()
