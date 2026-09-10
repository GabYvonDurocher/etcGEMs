#!/usr/bin/env python3
"""P12 TASK 2, addendum-1 item 4 -- score every basin for deadness and under the no-discount
scheme. CHANGES NOTHING; this is scoring, not fitting.

For each basin found by task2_basins.py, at BOTH its best-log-likelihood endpoint and its median
centre:
  * the predicted growth curve over the twelve temperatures, and its peak against the observed
    peak (2.076 /h);
  * DEAD-MODEL if the peak predicted growth is below half the observed peak (addendum 1 item 4) --
    such a basin is not an alternative explanation of the thermal curve;
  * the log-likelihood under (i) as is and under (ii') no discount (w == 1 on the respiration
    term, hard mask kept), so the reader sees which basins survive a full-strength penalty.
"""
import os, sys, json
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from common import build, SPECS, NAMES, decompose                      # noqa: E402
from addendum1_weight import schemes                                   # noqa: E402

HALF_DEAD = 0.5


def main():
    ctx, _sp = build()
    good = pd.read_csv(os.path.join(HERE, "task2_endpoints_clustered.csv"))
    xcols = [f"x_{n}" for n in NAMES]
    obs = np.asarray(ctx["growth_obs"], float); peak_obs = float(obs.max())
    rows, curves = [], {}
    for b in sorted(good.basin.unique()):
        g = good[good.basin == b]
        reps = {"best": g.loc[g.logl.idxmax(), xcols].to_numpy(float),
                "centre": g[xcols].median().to_numpy(float)}
        for tag, th in reps.items():
            sc = schemes(th, ctx, SPECS)
            d = decompose(th, ctx, SPECS)
            gp = np.asarray(d["growth"], float)
            frac = float(gp.max()) / peak_obs
            rows.append(dict(basin=int(b), rep=tag, n=len(g),
                             n_from_prior=int((g.kind == "prior").sum()),
                             holds=",".join(sorted(set(g.kind) - {"prior"})),
                             logl_i=sc["total_i"], logl_nodiscount=sc["total_iiprime"],
                             growth_term=sc["growth_term"], resp_i=sc["resp_i"],
                             discount_credit=sc["resp_i"] - sc["resp_nodiscount"],
                             peak_growth=float(gp.max()), peak_obs=peak_obs, peak_frac=frac,
                             dead_model=bool(frac < HALF_DEAD), mean_w=sc["mean_w"],
                             n_scored=sc["n_scored"]))
            curves[f"basin{b}_{tag}"] = gp.tolist()
        print(f"[t2s] basin {b} scored", flush=True)
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(HERE, "task2_basin_scores.csv"), index=False)
    json.dump(dict(T=list(map(float, ctx["T"])), growth_obs=obs.tolist(), curves=curves),
              open(os.path.join(HERE, "task2_basin_curves.json"), "w"), indent=1)
    pd.set_option("display.width", 240)
    print("\n[t2s] basins: deadness and the no-discount rescore")
    print(df[["basin", "rep", "n", "n_from_prior", "holds", "logl_i", "logl_nodiscount",
              "discount_credit", "peak_growth", "peak_frac", "dead_model"]].round(3).to_string(index=False))
    dead = sorted(df[(df.rep == "best") & df.dead_model].basin.unique())
    print(f"\n[t2s] DEAD-MODEL basins (peak predicted growth < {HALF_DEAD:.0%} of {peak_obs:.3f} /h): "
          f"{dead if dead else 'none'}")
    print("[t2s] done")


if __name__ == "__main__":
    main()
