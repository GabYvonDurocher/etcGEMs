"""Copy the Ea-dissection outputs into reports/activation_energy/assets/ under stable
names, so report.qmd renders without touching the analysis outputs. Run from the project
root:  python reports/activation_energy/assemble.py

Mirrors reports/ecoli_tpc/assemble.py; reads only strains/eciML1515/outputs/ea_dissection/
(produced by `etcgem ea`)."""
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
EA = os.path.join(ROOT, "strains", "eciML1515", "outputs", "ea_dissection")
FIG_DIR = os.path.join(HERE, "assets", "figures")
TBL_DIR = os.path.join(HERE, "assets", "tables")

# (source_filename, stable_dest_name)
FIGURES = [
    ("ea_signed_contributions.png", "ea_signed_contributions.png"),
    ("ea_departure.png",            "ea_departure.png"),
    ("ea_top_enzymes_no_carrier.png", "ea_top_enzymes.png"),   # acpP-excluded (robust) version
    ("ea_by_cog.png",               "ea_by_cog.png"),
    ("ea_robustness.png",           "ea_robustness.png"),
]
TABLES = [
    ("summary.json",                "ea_summary.json"),
    ("ea_by_cog_BHI_no_carrier.csv", "ea_by_cog_BHI.csv"),
    ("ea_by_cog_glucose_no_carrier.csv", "ea_by_cog_glucose.csv"),
    ("ea_per_enzyme_BHI.csv",       "ea_per_enzyme_BHI.csv"),
    ("ea_per_enzyme_glucose.csv",   "ea_per_enzyme_glucose.csv"),
]


def _copy(src_name, dest_dir, dest_name, copied, missing):
    src = os.path.join(EA, src_name)
    if not os.path.exists(src):
        missing.append(f"{src_name}  ({src})")
        return False
    os.makedirs(dest_dir, exist_ok=True)
    shutil.copy2(src, os.path.join(dest_dir, dest_name))
    copied.append(f"{dest_name}  <- ea_dissection/{src_name}")
    return True


def main():
    copied, missing = [], []
    for s, d in FIGURES:
        _copy(s, FIG_DIR, d, copied, missing)
    for s, d in TABLES:
        _copy(s, TBL_DIR, d, copied, missing)
    print("=" * 60)
    print(f"COPIED ({len(copied)}):")
    for c in copied:
        print("  +", c)
    if missing:
        print(f"MISSING ({len(missing)}):")
        for m in missing:
            print("  -", m)
    print("=" * 60)
    print(f"assets -> {os.path.relpath(os.path.join(HERE, 'assets'), ROOT)}")


if __name__ == "__main__":
    main()
