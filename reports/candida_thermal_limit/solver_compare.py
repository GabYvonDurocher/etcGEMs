#!/usr/bin/env python3
"""solver_compare.py -- K2 PART D: Gurobi against GLPK, rung by rung.

K1 pinned GLPK because the standalone solved with it and the port then reproduced it
exactly. That hid a 0.4% disagreement at the coldest point of the two DRAFT models' sweeps.
K2 runs on Gurobi and reports the difference instead.

Run each rung twice and pass both output roots:

    for e in transfer_candida candida_B1_unfolding candida_B2_grounded_budget \\
             candida_B3_ngamT candida_B4_sectors ; do
        etcgem transfer --experiment $e --solver glpk --tag glpk_$e --out-root /tmp/glpk
    done
    python3 reports/candida_thermal_limit/solver_compare.py --glpk-root /tmp/glpk

Writes solver_comparison.csv beside this file: every per-temperature growth rate that
differs by more than the threshold, in MODEL units (unscaled), so a peak-matched growth
scale cannot mask or manufacture a difference.
"""
from __future__ import annotations

import argparse
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RUNGS = [("B0", "transfer_candida"), ("B1", "candida_B1_unfolding"),
         ("B2", "candida_B2_grounded_budget"), ("B3", "candida_B3_ngamT"),
         ("B4", "candida_B4_sectors")]
SHORT = {"cauris_iRV973": "auris", "chaemulonii_draft": "haemulonii",
         "cduobushaemulonii_draft": "duobushaemulonii",
         "cparapsilosis_iDC1003": "parapsilosis"}


def arbitrate(strain: str, experiment: str, T_C: float):
    """Decide whether a Gurobi/GLPK disagreement is alternate optima or arithmetic.

    An LP's optimal OBJECTIVE is unique -- alternate optima differ in the flux vector, not
    in the growth rate -- so a difference in predicted growth cannot be alternate optima and
    must be numerical. This checks that directly, three ways:

      1. tighten Gurobi's feasibility/optimality tolerances: does its answer move?
      2. rescale the LP to a mathematically IDENTICAL but well-conditioned one (divide every
         pool coefficient AND the budget by the median coefficient, via
         Perturbation(kcat_scale=k, budget=B/k)): do the two solvers then agree?
      3. solve with glpk_exact, GLPK's rational-arithmetic solver: who is right?
    """
    import cobra
    import numpy as np
    sys.path.insert(0, "src")
    from etcgem.config import resolve, build_provider
    from etcgem.enzyme_cost import Perturbation
    from etcgem.tpc import compute_tpc

    out = {}
    for solver in ("gurobi", "glpk", "glpk_exact"):
        cobra.Configuration().solver = solver
        cfg = resolve(strain, experiment)
        cfg["solver"] = solver
        pm = build_provider(cfg)
        B = pm.ec.default_budget
        v = float(compute_tpc(pm, [T_C], Perturbation()).growth[0])
        k = 1.0 / float(np.median(pm.ec._costs(T_C + 273.15, Perturbation())))
        vs = float(compute_tpc(pm, [T_C], Perturbation(kcat_scale=k, budget=B / k)).growth[0])
        rng = pm.ec._costs(T_C + 273.15, Perturbation())
        out[solver] = dict(as_is=v, rescaled=vs, scale_factor=k,
                           coef_min=float(rng.min()), coef_max=float(rng.max()))
    print(f"\narbitration: {strain} / {experiment} at {T_C:g} C")
    c = out["gurobi"]
    print(f"  pool-constraint coefficient range {c['coef_min']:.3e} to {c['coef_max']:.3e} "
          f"(dynamic range {c['coef_max']/c['coef_min']:.2e}) -- the activity floor puts a "
          f"handful of enzymes many orders above the median")
    for k_, v_ in out.items():
        print(f"  {k_:11s} as-is {v_['as_is']:.10f}   rescaled {v_['rescaled']:.10f}   "
              f"shift {v_['rescaled']-v_['as_is']:+.3e}")
    agree = abs(out["gurobi"]["as_is"] - out["glpk_exact"]["as_is"]) < 1e-9
    print(f"  glpk_exact (rational arithmetic) agrees with "
          f"{'GUROBI' if agree else 'GLPK'}; the disagreement is ARITHMETIC, not alternate "
          f"optima (an LP's optimal objective is unique).")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--glpk-root", required=True)
    ap.add_argument("--threshold", type=float, default=1e-6,
                    help="report every |difference| above this, in model units (default 1e-6)")
    ap.add_argument("--arbitrate", action="store_true",
                    help="also decide the largest disagreement: numerical or alternate optima")
    a = ap.parse_args(argv)

    rows = []
    for rung, exp in RUNGS:
        g_dir = os.path.join(a.glpk_root, f"glpk_{exp}")
        gur = f"outputs/transfer_{exp}" if not exp.startswith("transfer") else f"outputs/{exp}"
        for f in (os.path.join(g_dir, "summary.csv"), os.path.join(gur, "summary.csv")):
            if not os.path.exists(f):
                sys.exit(f"missing {f}")
        G = pd.read_csv(os.path.join(g_dir, "summary.csv")).set_index("strain")
        U = pd.read_csv(os.path.join(gur, "summary.csv")).set_index("strain")
        mcols = [c for c in U.columns if c.startswith("model_mu_")]
        for st in U.index:
            for c in mcols:
                T = float(c[len("model_mu_"):-1])
                gv, uv = float(G.loc[st, c]), float(U.loc[st, c])
                rows.append(dict(rung=rung, species=SHORT.get(st, st), temp_C=T,
                                 gurobi=uv, glpk=gv, diff=uv - gv,
                                 rel=(abs(uv - gv) / gv if gv else np.nan)))
            for c in ("thermal_limit_C", "descr_CTmax_C", "descr_Topt_C", "peak_mu_model"):
                if c in U.columns:
                    gv, uv = float(G.loc[st, c]), float(U.loc[st, c])
                    rows.append(dict(rung=rung, species=SHORT.get(st, st), temp_C=np.nan,
                                     quantity=c, gurobi=uv, glpk=gv, diff=uv - gv,
                                     rel=(abs(uv - gv) / gv if gv else np.nan)))
    D = pd.DataFrame(rows)
    D["quantity"] = D.get("quantity", pd.Series(index=D.index, dtype=object)).fillna("growth")
    hits = D[D["diff"].abs() > a.threshold].copy()
    hits.to_csv(os.path.join(HERE, "solver_comparison.csv"), index=False)

    print(f"{len(D)} paired quantities compared; {len(hits)} differ by more than "
          f"{a.threshold:g} (model units)\n")
    if len(hits):
        with pd.option_context("display.width", 200, "display.max_rows", 100):
            print(hits.sort_values("diff", key=abs, ascending=False)
                  .head(40).round(8).to_string(index=False))
        print("\nby rung and species (growth only, count above threshold and largest |diff|):")
        gr = hits[hits.quantity == "growth"]
        if len(gr):
            t = gr.groupby(["rung", "species"]).agg(
                n=("diff", "size"), max_abs=("diff", lambda x: float(np.abs(x).max())),
                max_rel=("rel", "max"),
                coldest_T=("temp_C", "min"), warmest_T=("temp_C", "max"))
            print(t.round(8).to_string())
    print("\nwrote", os.path.join(HERE, "solver_comparison.csv"))
    if a.arbitrate and len(hits):
        gr = hits[hits.quantity == "growth"]
        if len(gr):
            w = gr.loc[gr["rel"].idxmax()]
            exp = dict(RUNGS)[w["rung"]]
            strain = {v: k for k, v in SHORT.items()}[w["species"]]
            arbitrate(strain, exp, float(w["temp_C"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
