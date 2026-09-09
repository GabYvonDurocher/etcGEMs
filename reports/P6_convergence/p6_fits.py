"""The nine P6 fits: P4's scoped list (reports/P4_refit/fits.py), unchanged except LB's c_max,
which is read from the strain data P5 settled (carbon_cap.by_medium.LB), and the order, which is
the prompt's: D NLDM, D LB, E NLDM, E LB, F NLDM, F LB, then M9 x 3.

Nothing else differs from P4: same data tables, OTUs, ETC tables, proton stoichiometry, clearance
sampling, and the same scalar c_max (120) wherever P4 used it on NLDM / M9.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
import importlib.util as _ilu
_spec = _ilu.spec_from_file_location("p4_fits", os.path.join(ROOT, "reports", "P4_refit", "fits.py"))
_p4 = _ilu.module_from_spec(_spec); _spec.loader.exec_module(_p4)
P4_FITS, E_TABLE, F_TABLE, R2A_LB, M9, C_MAX = _p4.FITS, _p4.E_TABLE, _p4.F_TABLE, _p4.R2A_LB, _p4.M9, _p4.C_MAX


def lb_cmax_from_strain_data():
    """P5's canonical LB cap, read from the strain file -- not assumed."""
    import yaml
    p = os.path.join(ROOT, "strains", "eciML1515", "gas_exchange.yaml")
    gx = (yaml.safe_load(open(p)) or {}).get("gas_exchange", {})
    v = ((gx.get("carbon_cap") or {}).get("by_medium") or {}).get("LB")
    if v is None:
        raise SystemExit("[fits] gas_exchange.carbon_cap.by_medium.LB is not set: P5 left LB "
                         "unsettled; do not run LB at the scalar 120 (P6 TASK 0).")
    return float(v)


LB_CMAX = lb_cmax_from_strain_data()
ORDER = ["D_NLDM", "D_LB", "E_NLDM", "E_LB", "F_NLDM", "F_LB", "D_M9", "E_M9", "F_M9"]
_by = {f[0]: f for f in P4_FITS}
FITS = []
for lab in ORDER:
    label, cfg, medium, table, otu, c_max, etc_table, protons, fit_k = _by[lab]
    if medium == "LB":
        c_max = LB_CMAX
    FITS.append((label, cfg, medium, table, otu, c_max, etc_table, protons, fit_k))

OUT_TMPL = "calibration_config{cfg}_{med}_recipe_P6"
P4_TMPL = "calibration_config{cfg}_{med}_recipe_cmax120"
MED = {"NLDM": "NLDM", "LB": "LB", "glucose_minimal": "M9"}


def out_dir_for(cfg, medium):
    return OUT_TMPL.format(cfg=cfg, med=MED[medium])


def p4_dir_for(cfg, medium):
    return P4_TMPL.format(cfg=cfg, med=MED[medium])


# P6 DECISIONS D3: configurations E and F are NOT run -- their likelihood re-applies the ETC
# area constraint on every call and the model's O2 uptake at optimal growth is not unique, so
# the respiration term depends on solver history (jitter 0.5-7.5 in log-likelihood at a fixed
# parameter vector, against <= 0.0004 for every configuration-D fit). See preflight_jitter.csv
# and jitter_diagnosis.json. RUN is what TASK 1 samples, in the prompt's order restricted to D.
STOPPED = {"E_NLDM": "likelihood not a function of theta (D3)", "E_LB": "same", "F_NLDM": "same",
           "F_LB": "same", "E_M9": "same", "F_M9": "same"}
RUN = [f for f in FITS if f[0] not in STOPPED]
