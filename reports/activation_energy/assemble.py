"""Collect the finalised cross-organism comparison assets into reports/activation_energy/
assets/ under stable names, so report.qmd + supplementary.qmd render without touching the
analysis outputs. Run from the project root:  python reports/activation_energy/assemble.py

This is the CROSS-ORGANISM COMPARISON PAPER (E. coli respiration vs M. maripaludis
methanogenesis), Sharpe-Schoolfield E throughout. Sources: outputs/ea_cross_organism/ (the
final comparison), outputs/ea_definition_audit/ (window-sensitivity + SS fits), the two
strains' outputs/ (decompositions, Mcr sweep, methanogen calibration/audit figures). Figure 1
(assets/fig1/) is built in place by gen_fig1_ss_posteriors.py + the fig1 assembler."""
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
XORG = os.path.join(ROOT, "outputs", "ea_cross_organism")
AUDIT = os.path.join(ROOT, "outputs", "ea_definition_audit")
MM = os.path.join(ROOT, "strains", "mmaripaludis", "outputs")
FIG_DIR = os.path.join(HERE, "assets", "figures")
TBL_DIR = os.path.join(HERE, "assets", "tables")

SY = os.path.join(ROOT, "strains", "syn6803", "outputs")

# (source_path, dest_dir, dest_name)
COPIES = [
    # main-paper figures (three-way)
    (os.path.join(XORG, "cross_organism_signed_contributions_3way.png"), FIG_DIR, "cross_organism_signed_contributions_3way.png"),
    # supplement figures
    (os.path.join(MM, "calibration_jones", "prior_vs_posterior_tpc.png"), FIG_DIR, "methanogen_calibration_jones.png"),
    (os.path.join(MM, "calibration_jones", "corner.png"), FIG_DIR, "methanogen_corner.png"),
    (os.path.join(MM, "M3_thermal", "emergent_tpc_vs_jones.png"), FIG_DIR, "methanogen_emergent_tpc.png"),
    (os.path.join(ROOT, "strains", "eciML1515", "outputs", "calibration_vanderlinden", "prior_vs_posterior_tpc.png"), FIG_DIR, "ecoli_calibration_vdl.png"),
    (os.path.join(ROOT, "strains", "eciML1515", "outputs", "calibration_vanderlinden", "corner.png"), FIG_DIR, "ecoli_corner.png"),
    (os.path.join(AUDIT, "ss_fits_overlay.png"), FIG_DIR, "ss_fits_overlay.png"),
    # phototroph supplement figures
    (os.path.join(SY, "P2_thermal", "emergent_tpc_vs_zavrel.png"), FIG_DIR, "phototroph_emergent_tpc.png"),
    (os.path.join(SY, "calibration_zavrel", "prior_vs_posterior_tpc.png"), FIG_DIR, "phototroph_calibration_zavrel.png"),
    (os.path.join(SY, "calibration_zavrel", "corner.png"), FIG_DIR, "phototroph_corner.png"),
    (os.path.join(SY, "calibration_zavrel", "inoue_crosschecks.png"), FIG_DIR, "phototroph_inoue_crosschecks.png"),
    (os.path.join(SY, "P3b_sectors", "sectored_vs_singlepool_tpc.png"), FIG_DIR, "phototroph_sectored_tpc.png"),
    (os.path.join(SY, "ea_dissection_ss", "robustness_sweep.png"), FIG_DIR, "phototroph_robustness_sweep.png"),
    # main-paper tables (three-way)
    (os.path.join(XORG, "comparison_table_3way.csv"), TBL_DIR, "comparison_table_3way.csv"),
    (os.path.join(AUDIT, "window_sensitivity.csv"), TBL_DIR, "window_sensitivity.csv"),
    (os.path.join(AUDIT, "sharpe_schoolfield_fits.csv"), TBL_DIR, "sharpe_schoolfield_fits.csv"),
    (os.path.join(MM, "ea_dissection_ss", "mcr_sweep.csv"), TBL_DIR, "mcr_sweep.csv"),
]


def main():
    copied, missing = [], []
    for src, dest_dir, dest_name in COPIES:
        if not os.path.exists(src):
            missing.append(src)
            continue
        os.makedirs(dest_dir, exist_ok=True)
        shutil.copy2(src, os.path.join(dest_dir, dest_name))
        copied.append(f"{dest_name}  <- {os.path.relpath(src, ROOT)}")
    # Figure 1 is built in place under assets/fig1/ (gen_fig1_ss_posteriors.py)
    fig1 = os.path.join(HERE, "assets", "fig1", "fig1_scene_setter.png")
    fig1_ok = os.path.exists(fig1)
    print("=" * 64)
    print(f"COPIED ({len(copied)}):")
    for c in copied:
        print("  +", c)
    print(f"Figure 1 (assets/fig1/fig1_scene_setter.png): {'present' if fig1_ok else 'MISSING - run gen_fig1_ss_posteriors.py'}")
    if missing:
        print(f"MISSING ({len(missing)}):")
        for m in missing:
            print("  -", os.path.relpath(m, ROOT))
    print("=" * 64)


if __name__ == "__main__":
    main()
