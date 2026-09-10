#!/usr/bin/env python3
"""P12 TASK 3 -- what each basin IS: its curves, its O2 face, its terms, its dTm.

Per basin, at its best-log-likelihood endpoint:
  * predicted growth and O2 over the twelve temperatures, against the measured points;
  * the O2 FACE at optimal growth -- min_o2 and max_o2 through P10's own tie-break options, which
    is Pettersen & Almaas's cytochrome-oxidase observation reproduced here: at a fixed optimal
    growth the LP does not pin O2, and the width of that face is how much of the respiration
    prediction is arbitrary rather than determined;
  * the growth-term and respiration-term log-likelihoods separately;
  * the sixteen parameters, with dTm called out -- a basin with dTm near zero is one that fits
    WITHOUT contradicting the measured meltome, which is the R3 question (OPEN_ITEMS 0a/0b step 2).
"""
import os, sys, json
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from common import build, SPECS, NAMES, decompose, to_natural, to_pert, flux_tpc, _prov   # noqa: E402
from common import add_total_carbon_constraint                                            # noqa: E402
DTM_NEAR_ZERO = 1.0     # |dTm| below this K is "near zero" -- reported prominently either way


def o2_face(th, ctx, sp):
    """min and max O2 uptake at the growth optimum, per temperature: the width of the LP face."""
    resp = ctx.get("respiration") or {}
    nat = to_natural(th, sp); pert = to_pert(th, sp); pm = ctx["pm"]
    if "clearance_mult" in nat:
        r = ctx["recipe"]
        _prov.set_medium_recipe(pm, r["recipe_csv"], clearance_L_per_gDW_h=r["clearance"] * float(nat["clearance_mult"]),
                                uptake_ub=r.get("uptake_ub", 1000.0), verbose=False)
        if ctx.get("c_max") is not None:
            add_total_carbon_constraint(pm, float(ctx["c_max"]))
    out = {}
    for tb in ("pfba", "min_o2", "max_o2"):
        df = flux_tpc(pm, ctx["T"], pert, metabolites=("o2",), tiebreak=tb,
                      growth_tol=float(resp.get("growth_tol", 1e-6)),
                      tiebreak_tol=float(resp.get("tiebreak_tol", 1e-9)))
        out[tb] = df["o2_uptake"].to_numpy(float)
        out["growth"] = df["growth"].to_numpy(float)
    return out


def main():
    ctx, _sp = build()
    good = pd.read_csv(os.path.join(HERE, "task2_endpoints_clustered.csv"))
    xcols = [f"x_{n}" for n in NAMES]
    T = np.asarray(ctx["T"], float)
    rows, curves = [], {"T": T.tolist(), "growth_obs": np.asarray(ctx["growth_obs"], float).tolist(),
                        "resp_obs": np.asarray(ctx["resp_obs"], float).tolist()}
    for b in sorted(good.basin.unique()):
        g = good[good.basin == b]
        th = g.loc[g.logl.idxmax(), xcols].to_numpy(float)
        d = decompose(th, ctx, SPECS)
        f = o2_face(th, ctx, SPECS)
        nat = to_natural(th, SPECS)
        width = f["max_o2"] - f["min_o2"]
        alive = np.asarray(d["growth"], float) > 1e-4
        rows.append(dict(basin=int(b), n=len(g), n_from_prior=int((g.kind == "prior").sum()),
                         holds=",".join(sorted(set(g.kind) - {"prior"})),
                         logl=float(d["logl"]), growth_term=float(np.sum(d["growth_term"])),
                         resp_term=float(np.sum(d["resp_term"])),
                         peak_growth=float(np.max(d["growth"])),
                         face_width_mean=float(np.nanmean(width[alive])) if alive.any() else float("nan"),
                         face_width_max=float(np.nanmax(width[alive])) if alive.any() else float("nan"),
                         **{n: float(nat[n]) for n in NAMES if n in nat}))
        curves[f"basin{b}"] = dict(growth=np.asarray(d["growth"], float).tolist(),
                                   o2_pfba=f["pfba"].tolist(), o2_min=f["min_o2"].tolist(),
                                   o2_max=f["max_o2"].tolist(), weight=np.asarray(d["weight"], float).tolist())
        print(f"[t3] basin {b} done", flush=True)
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(HERE, "task3_per_basin.csv"), index=False)
    json.dump(curves, open(os.path.join(HERE, "task3_curves.json"), "w"), indent=1)
    pd.set_option("display.width", 260)
    print("\n[t3] per basin (at its best endpoint)")
    print(df[["basin", "n", "n_from_prior", "holds", "logl", "growth_term", "resp_term",
              "peak_growth", "face_width_mean", "face_width_max", "dTm", "dTopt"]].round(3).to_string(index=False))
    near = df[df.dTm.abs() < DTM_NEAR_ZERO]
    print(f"\n[t3] *** basins with |dTm| < {DTM_NEAR_ZERO} K (fit WITHOUT contradicting the measured "
          f"meltome): {sorted(near.basin.tolist()) if len(near) else 'NONE'} ***")
    if len(near):
        print(near[["basin", "dTm", "dTopt", "logl", "peak_growth"]].round(3).to_string(index=False))
    print("[t3] done")


if __name__ == "__main__":
    main()
