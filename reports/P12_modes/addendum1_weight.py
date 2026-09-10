#!/usr/bin/env python3
"""P12 addendum 1 -- characterise the support weight. CHANGES NOTHING.

One flux_tpc solve per fixed point; all schemes are re-scored from that same solve, so the
comparison is exact arithmetic on identical LP solutions, not three separate fits.

Schemes (the report explains why the addendum's (ii)/(iii) had to be restated):
  (i)    as is                -- hard mask g >= 1e-4 & o2 > 0, then w = min(1, g/g_s), g_s = 0.01
  (ii)   as the addendum      -- growth predictions floored at 1e-3 before the log. The growth
                                term is LINEAR, so this is a no-op; computed and reported anyway.
  (ii')  no discount          -- hard mask kept, w == 1. The respiration penalty is paid in full
                                wherever it is scored. This is the counterfactual that answers
                                "does the weight keep B alive?"
  (iii') no support handling  -- no growth mask, w == 1, every temperature scored. Where the model
                                consumes no O2 this is log(0) -> -inf, which is the reason some
                                handling exists at all.
"""
import os, sys, json
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from common import (fixed_points, build, SPECS, NAMES, NEST, decompose, _MASK_G,   # noqa: E402
                    to_natural, to_pert, flux_tpc, add_total_carbon_constraint, _prov)

EPS_ADDENDUM = 1e-3


def schemes(th, ctx, sp):
    resp = ctx.get("respiration") or {}
    nat = to_natural(th, sp); pert = to_pert(th, sp); pm = ctx["pm"]
    if "clearance_mult" in nat:
        r = ctx["recipe"]
        _prov.set_medium_recipe(pm, r["recipe_csv"], clearance_L_per_gDW_h=r["clearance"] * float(nat["clearance_mult"]),
                                uptake_ub=r.get("uptake_ub", 1000.0), verbose=False)
        if ctx.get("c_max") is not None:
            add_total_carbon_constraint(pm, float(ctx["c_max"]))
    df = flux_tpc(pm, ctx["T"], pert, metabolites=("o2",), tiebreak=str(resp.get("tiebreak", "none")),
                  growth_tol=float(resp.get("growth_tol", 1e-6)), tiebreak_tol=float(resp.get("tiebreak_tol", 1e-9)))
    g = df["growth"].to_numpy(float); o2 = df["o2_uptake"].to_numpy(float)
    dg = float(nat["disc_growth"]); var = ctx["growth_sd"] ** 2 + dg ** 2
    gterm = float(np.sum(-0.5 * ((ctx["growth_obs"] - g) ** 2 / var + np.log(2 * np.pi * var))))
    # the addendum's (ii): floor the growth PREDICTION before "the log" -- the term is linear,
    # so this can only move predictions that are below the floor, and only linearly.
    gfl = np.maximum(g, EPS_ADDENDUM)
    gterm_fl = float(np.sum(-0.5 * ((ctx["growth_obs"] - gfl) ** 2 / var + np.log(2 * np.pi * var))))
    dr = float(nat["disc_resp"]); rs = float(nat["resp_scale"])
    floor = float(resp.get("log_o2_floor", 0.0)); gs = float(resp.get("alive_soft_growth") or 0.0)

    def rterm(mask, weighted):
        if not mask.any():
            return 0.0
        pred = np.log(o2[mask] * ctx["o2_conv"] * rs); obsl = np.log(ctx["resp_obs"][mask])
        rel = ctx["resp_sd"][mask] / ctx["resp_obs"][mask]; varr = rel ** 2 + dr ** 2 + floor ** 2
        w = np.minimum(1.0, g[mask] / gs) if (weighted and gs) else np.ones(int(mask.sum()))
        return float(np.sum(-0.5 * w * ((obsl - pred) ** 2 / varr + np.log(2 * np.pi * varr))))

    keep = (g >= _MASK_G) & (o2 > 0)
    allT = np.ones_like(g, bool)
    r_i = rterm(keep, True); r_nod = rterm(keep, False)
    # (iii'): scoring EVERY temperature. Where the model is dead, flux_tpc returns NaN for O2 --
    # there is no prediction to score at all, so the term is UNDEFINED, not merely bad. That is a
    # stronger reason for support handling than "the log of zero" and is recorded as such.
    n_nan = int((~np.isfinite(o2)).sum()); n_nonpos = int((o2[np.isfinite(o2)] <= 0).sum())
    with np.errstate(divide="ignore", invalid="ignore"):
        r_iii = float("nan") if (n_nan or n_nonpos) else rterm(allT, False)
    return dict(growth_term=gterm, growth_term_floored=gterm_fl,
                resp_i=r_i, resp_nodiscount=r_nod, resp_nosupport=r_iii,
                total_i=gterm + r_i, total_ii_addendum=gterm_fl + r_i,
                total_iiprime=gterm + r_nod, total_iiiprime=gterm + r_iii,
                peak_growth=float(g.max()), peak_obs=float(ctx["growth_obs"].max()),
                n_scored=int(keep.sum()), n_T=int(len(g)), mean_w=float(np.minimum(1.0, g[keep] / gs).mean()) if keep.any() and gs else float("nan"),
                n_o2_nan=n_nan, n_o2_nonpos=n_nonpos, undefined_iiiprime=bool(n_nan or n_nonpos))


def main():
    ctx, _sp = build(); fp = fixed_points()
    s2 = np.load(os.path.join(NEST, "samples_seed2.npy")); l2 = np.load(os.path.join(NEST, "logl_seed2.npy"))
    fp["Bstar"] = s2[int(np.nanargmax(l2))]
    rows = {}
    for k in ("A", "B", "Bstar", "P4"):
        rows[k] = schemes(fp[k], ctx, SPECS)
        print(f"[a1] {k:6s} done", flush=True)
    df = pd.DataFrame(rows).T
    df.to_csv(os.path.join(HERE, "addendum1_schemes.csv"))
    pd.set_option("display.width", 200)
    print("\n[a1] per-scheme TOTAL log-likelihood")
    print(df[["growth_term", "resp_i", "resp_nodiscount", "total_i", "total_ii_addendum",
              "total_iiprime", "total_iiiprime"]].round(3).to_string())
    print("\n[a1] support and deadness")
    print(df[["peak_growth", "peak_obs", "n_scored", "n_T", "mean_w", "n_o2_nan", "n_o2_nonpos"]].round(4).to_string())
    for lo, hi in (("A", "B"), ("A", "Bstar")):
        print(f"\n[a1] gap {lo} - {hi}:")
        for s, lab in (("total_i", "(i)   as is          "), ("total_ii_addendum", "(ii)  addendum floor "),
                       ("total_iiprime", "(ii') no discount   "), ("total_iiiprime", "(iii')no support    ")):
            print(f"[a1]    {lab} {df.loc[lo, s] - df.loc[hi, s]:+9.3f}   "
                  f"({lo} {df.loc[lo, s]:+9.3f}, {hi} {df.loc[hi, s]:+9.3f})")
    json.dump({k: {kk: (None if not np.isfinite(vv) else float(vv)) for kk, vv in v.items()} for k, v in rows.items()},
              open(os.path.join(HERE, "addendum1_schemes.json"), "w"), indent=1)
    print("\n[a1] done")


if __name__ == "__main__":
    main()
