#!/usr/bin/env python3
"""task3_tables.py -- Y2 TASK 3: turn the raw sweeps into the tables the report quotes.

    python3 reports/Y2_regime_posterior/task3_tables.py

Reads task2_ranges.csv and task2_summary.csv; writes task3_headline.csv, task3_draw_spread.csv,
task3_headline.json and the two per-draw tables.

THE THING THIS HAS TO GET RIGHT, and the first version of it got wrong.

Under a tight glucose cap the model's growth rises with temperature until the SUBSTRATE limit
binds and then goes exactly flat at the ceiling the cap allows -- 0.0968 h^-1 at cap 1, reached by
about 15 C and held to about 38 C. The top of the curve is therefore not a peak but a ceiling, and
`argmax` over a 20-50 C grid returns the FIRST point of an exact tie, which is the grid's own lower
bound. 44 of 100 posterior draws report `T_opt` at 20.0 C for that reason.

That is not degeneracy. It is the effect itself, in its clearest form -- and a filter that drops
those draws throws away exactly the evidence and biases the T_opt range downward. So they are
treated as CENSORED (`T_opt <= 20 C`, the range a lower bound) and counted, never discarded.

Extending the grid downward would not help: growth is still rising at 5-13 C and the ceiling is
already reached by 15 C, so the tie -- and the censoring -- would simply move with the grid. The
descriptor that survives is the PLATEAU, which is what Y1 reported and what this reports.

Genuinely degenerate, and excluded: a parameter set whose curve never falls back through 1 % of
its own maximum inside the grid, or whose maximum growth is zero. Both are rare.
"""
from __future__ import annotations

import json
import os

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
GRID_LO = 20.0
LOOSE, TIGHT = "glucose_cap=10.0", "glucose_cap=1.0"


def load():
    r = pd.read_csv(os.path.join(HERE, "task2_ranges.csv"))
    s = pd.read_csv(os.path.join(HERE, "task2_summary.csv"))
    g = s.groupby(["kind", "index"])
    add = pd.concat([
        g["T_opt_at_edge"].any().rename("T_opt_censored"),
        g["mu_max"].min().rename("min_mu_max"),
        s.assign(_n=s.CT_max_rel_1pct.isna()).groupby(["kind", "index"])["_n"].any()
         .rename("no_CT_max_crossing"),
    ], axis=1).reset_index()
    r = r.merge(add, on=["kind", "index"])
    r["degenerate"] = r.no_CT_max_crossing | (r.min_mu_max <= 1e-9)
    for lab, tag in ((LOOSE, "loose"), (TIGHT, "tight")):
        sub = s[s.setting == lab][["kind", "index", "plateau99_width", "CT_max_rel_1pct", "T_opt"]]
        sub = sub.rename(columns={"plateau99_width": f"plateau_{tag}",
                                  "CT_max_rel_1pct": f"CT_max_{tag}", "T_opt": f"T_opt_{tag}"})
        r = r.merge(sub, on=["kind", "index"])
    return r, s


def spread(v):
    v = np.asarray(v, float)
    v = v[np.isfinite(v)]
    if not len(v):
        return dict(n=0)
    q = lambda p: float(np.percentile(v, p))                    # noqa: E731
    return dict(n=int(len(v)), median=float(np.median(v)), p05=q(5), p25=q(25),
                p75=q(75), p95=q(95), min=float(v.min()), max=float(v.max()))


def main():
    r, s = load()
    out = {"point_estimates": {}, "draws": {}}
    rows = []
    for kind in ("prior_file", "prior_median", "posterior_median"):
        x = r[r.kind == kind]
        if not len(x):
            continue
        x = x.iloc[0]
        d = dict(T_opt_range=float(x.T_opt_range), CT_max_range=float(x.CT_max_range),
                 asymmetry=float(x.asymmetry),
                 T_opt_loose=float(x.T_opt_loose), T_opt_tight=float(x.T_opt_tight),
                 CT_max_loose=float(x.CT_max_loose), CT_max_tight=float(x.CT_max_tight),
                 plateau_loose=float(x.plateau_loose), plateau_tight=float(x.plateau_tight),
                 mu_max_ratio=float(x.mu_max_ratio),
                 T_opt_censored=bool(x.T_opt_censored))
        out["point_estimates"][kind] = d
        rows.append(dict(parameter_set=kind, n=1, **d))
        print(f"[y2t3] {kind:17s} T_opt {d['T_opt_loose']:5.2f} -> {d['T_opt_tight']:5.2f} "
              f"(range {d['T_opt_range']:5.2f}{'*' if d['T_opt_censored'] else ' '})   "
              f"CT_max {d['CT_max_loose']:5.2f} -> {d['CT_max_tight']:5.2f} "
              f"(range {d['CT_max_range']:5.2f})   asymmetry {d['asymmetry']:5.1f}x   "
              f"plateau {d['plateau_loose']:.1f} -> {d['plateau_tight']:.1f} C")

    for kind in ("prior_draw", "posterior_draw"):
        sub = r[r.kind == kind]
        good = sub[~sub.degenerate]
        d = dict(n_total=int(len(sub)), n_degenerate=int(sub.degenerate.sum()),
                 n_used=int(len(good)),
                 n_T_opt_censored=int(good.T_opt_censored.sum()),
                 T_opt_range=spread(good.T_opt_range), CT_max_range=spread(good.CT_max_range),
                 T_opt_range_uncensored=spread(good[~good.T_opt_censored].T_opt_range),
                 CT_max_range_uncensored=spread(good[~good.T_opt_censored].CT_max_range),
                 plateau_loose=spread(good.plateau_loose),
                 plateau_tight=spread(good.plateau_tight),
                 CT_max_loose=spread(good.CT_max_loose),
                 CT_max_tight=spread(good.CT_max_tight),
                 frac_T_opt_beats_CT_max=float((good.T_opt_range > good.CT_max_range).mean()),
                 frac_plateau_widens=float((good.plateau_tight > good.plateau_loose).mean()))
        out["draws"][kind] = d
        rows.append(dict(parameter_set=kind, n=d["n_used"],
                         T_opt_range=d["T_opt_range"]["median"],
                         T_opt_range_p05=d["T_opt_range"]["p05"],
                         T_opt_range_p95=d["T_opt_range"]["p95"],
                         CT_max_range=d["CT_max_range"]["median"],
                         CT_max_range_p05=d["CT_max_range"]["p05"],
                         CT_max_range_p95=d["CT_max_range"]["p95"],
                         plateau_loose=d["plateau_loose"]["median"],
                         plateau_tight=d["plateau_tight"]["median"],
                         T_opt_censored=d["n_T_opt_censored"],
                         degenerate=d["n_degenerate"]))
        print(f"[y2t3] {kind:17s} n={d['n_used']}/{d['n_total']} "
              f"({d['n_degenerate']} degenerate, {d['n_T_opt_censored']} T_opt censored at "
              f"{GRID_LO:.0f} C)")
        for nm in ("T_opt_range", "CT_max_range", "plateau_loose", "plateau_tight"):
            v = d[nm]
            print(f"        {nm:16s} median {v['median']:6.2f}  "
                  f"[{v['p05']:.2f}, {v['p95']:.2f}]  n={v['n']}")
        print(f"        T_opt range > CT_max range in {100*d['frac_T_opt_beats_CT_max']:.0f} % of "
              f"draws; plateau widens under the cap in "
              f"{100*d['frac_plateau_widens']:.0f} %")

    pd.DataFrame(rows).to_csv(os.path.join(HERE, "task3_headline.csv"), index=False)
    for kind in ("prior_draw", "posterior_draw"):
        r[r.kind == kind].to_csv(os.path.join(HERE, f"task3_{kind}s.csv"), index=False)
    json.dump(out, open(os.path.join(HERE, "task3_headline.json"), "w"), indent=2)
    print("[y2t3] wrote task3_headline.csv, task3_headline.json, task3_*_draws.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
