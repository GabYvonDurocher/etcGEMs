"""N3 TASK 3: replay a committed resolved_config.yaml through TODAY's code and compare the
nominal TPC it produces with the one committed beside it.

Writes NOTHING into the repository. This is the same test N2 used on _toy: is the committed
output still what the current code produces from the config the run recorded?
"""
import json, os, sys
import numpy as np, pandas as pd, yaml
sys.path.insert(0, os.path.join(os.getcwd(), "src"))
from etcgem.config import build_provider, temperature_grid
from etcgem.tpc import compute_tpc
from etcgem.enzyme_cost import Perturbation

d = sys.argv[1]                       # e.g. strains/eciML1515/outputs/sweep_default
cfg = yaml.safe_load(open(os.path.join(d, "resolved_config.yaml")))
ref = os.path.join(d, "nominal_tpc.csv")
pm = build_provider(cfg)
temps = temperature_grid(cfg)
tpc = compute_tpc(pm, temps, Perturbation())
desc = tpc.descriptors(cfg.get("crit_frac", 0.05)).as_dict()
print(f"\n=== {d}")
print("  replayed descriptors:", {k: (round(v, 6) if isinstance(v, float) else v) for k, v in desc.items()})
if os.path.exists(ref):
    old = pd.read_csv(ref)
    if len(old) == len(tpc.growth) and np.allclose(old.temp_C.values, temps):
        dd = np.abs(old.growth.values - tpc.growth)
        rel = dd / np.where(old.growth.values != 0, np.abs(old.growth.values), np.nan)
        print(f"  vs committed nominal_tpc.csv: max abs {dd.max():.3e}  max rel {np.nanmax(rel):.3e}"
              f"  identical={bool((dd == 0).all())}")
    else:
        print(f"  GRID MISMATCH: committed n={len(old)} [{old.temp_C.min()}-{old.temp_C.max()}], "
              f"replay n={len(temps)} [{temps[0]}-{temps[-1]}]")
sj = os.path.join(d, "summary.json")
if os.path.exists(sj):
    s = json.load(open(sj))
    if "nominal" in s:
        print("  committed summary.json nominal:", {k: round(v, 6) for k, v in s["nominal"].items()})
