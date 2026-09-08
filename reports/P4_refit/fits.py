"""The scoped list of P4 refits, in one place, imported by the pre-flight, the runner and the
comparison so they cannot disagree about what is being fitted.

SCOPE. The nine fits below are exactly those behind a number quoted in
reports/ecoli_gasflux/ -- the ten R2 values P3 gated, plus M9 for each configuration, which has
never been fitted by anyone. Parsa's tree holds ~25 calibration directories (`freebd`,
`wideenv`, `nocap`, `_test`, `_resume`, `_olddata`, `_kfit`, `_combined`, `_growthonly` ...);
none of the rest produces a quoted number and none is refitted.

CANONICAL SETTINGS, applied to every fit here:
  medium            recipe ceilings, with the clearance K SAMPLED (prior 2-10 L gDW^-1 h^-1)
  c_max             120 mmol C gDW^-1 h^-1, FIXED -- adopted from his own sweep, not fitted,
                    and applied only where the configuration used a cap at all
  transporter kcat  300 s^-1 (in the strain data since P2; configuration A only)
  configuration F   configuration E's areas and turnovers + non-electrogenic bd-II
"""
E_TABLE = "etc/complexes_szenk_merged_bd.csv"
F_TABLE = "etc/complexes_configF_as_fitted.csv"
R2A_LB = "respirometry/derived_R2A_LB_current.csv"
M9 = "respirometry/derived_M9_current.csv"
C_MAX = 120.0

# label, config, model medium, data table, OTU, c_max, etc table, apply protons, fit K
FITS = [
    # 1. configuration D -- the medium change bites hardest here
    ("D_NLDM", "D", "NLDM",            R2A_LB, 1, C_MAX, None,    False, True),
    ("D_LB",   "D", "LB",              R2A_LB, 2, C_MAX, None,    False, False),
    # 2. configuration E -- membrane area; his NLDM fit had no cap, his LB fit did
    ("E_NLDM", "E", "NLDM",            R2A_LB, 1, None,  E_TABLE, False, True),
    ("E_LB",   "E", "LB",              R2A_LB, 2, C_MAX, E_TABLE, False, False),
    # 3. configuration F -- E's table plus a non-electrogenic bd-II
    ("F_NLDM", "F", "NLDM",            R2A_LB, 1, None,  F_TABLE, True,  True),
    ("F_LB",   "F", "LB",              R2A_LB, 2, C_MAX, F_TABLE, True,  False),
    # 4. M9 -- first light. Mapped to the model's glucose_minimal (M9 is glucose + salts), so
    #    there is no recipe and no clearance to sample; the carbon cap does the limiting.
    #    ALL THREE carry the carbon cap, including E and F whose NLDM counterparts do not.
    #    Reason, found by the pre-flight: on NLDM the recipe ceilings limit carbon and on LB the
    #    component list does; on glucose_minimal NOTHING does -- glucose is open at ub 1000 --
    #    so without a cap the ETC area budget alone leaves the cell fermenting (configuration
    #    F on M9 gave RQ 0.026 with zero acetate; configuration E gave growth 3.6e-5). The cap
    #    is the only carbon limitation available on this medium. Recorded as DECISIONS D2.
    ("D_M9",   "D", "glucose_minimal", M9,     1, C_MAX, None,    False, False),
    ("E_M9",   "E", "glucose_minimal", M9,     1, C_MAX, E_TABLE, False, False),
    ("F_M9",   "F", "glucose_minimal", M9,     1, C_MAX, F_TABLE, True,  False),
]

OUT_TMPL = "calibration_config{cfg}_{med}_recipe_cmax120"


def out_dir_for(label, cfg, medium):
    med = {"NLDM": "NLDM", "LB": "LB", "glucose_minimal": "M9"}[medium]
    return OUT_TMPL.format(cfg=cfg, med=med)
