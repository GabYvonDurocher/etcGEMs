#!/usr/bin/env python3
"""P6 TASK 2 -- what converging changed. For each fit P6 ran: the P6 chain against P4's
under-converged one -- R2 (from fits_table.csv and P4's refit_comparison.csv), and for every
shared parameter the posterior median and the 90 % credible-interval width, both chains
post-burn (2 tau, each chain's own tau). Also K's posterior/prior width ratio (NLDM: K = 5 x
clearance_mult against the prior [2, 10]) and sigma on M9 against the rich media.

Writes compare_posteriors.csv and compare_summary.csv beside this file.
"""
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, HERE)
os.chdir(ROOT)

import emcee                                                              # noqa: E402
from etcgem.calibration_multi import build_gasflux_specs, to_natural       # noqa: E402
from p6_fits import RUN, out_dir_for, p4_dir_for                          # noqa: E402

OUTS = os.path.join(ROOT, "strains", "eciML1515", "outputs")


def post(d, specs):
    ch = np.load(os.path.join(d, "chain.npy"))
    tau = float(np.max(emcee.autocorr.integrated_time(ch, tol=0)))
    burn = min(int(2 * tau), ch.shape[0] - 10)
    flat = ch[burn:].reshape(-1, ch.shape[2])
    sub = flat[::max(1, len(flat) // 4000)]
    rows = {}
    for k, s in enumerate(specs):
        col = np.array([to_natural(t, specs)[s.name] for t in sub])
        lo, md, hi = np.percentile(col, [5, 50, 95])
        rows[s.name] = dict(median=md, lo=lo, hi=hi, width=hi - lo, prior_width=s.hi - s.lo)
    return rows, tau, ch.shape[0]


def main():
    ft = pd.read_csv(os.path.join(HERE, "fits_table.csv")).set_index("fit")
    p4t = pd.read_csv(os.path.join(ROOT, "reports", "P4_refit", "refit_comparison.csv")).set_index("fit")
    rows, summ = [], []
    for label, cfg, medium, table, otu, c_max, etc, protons, fit_k in RUN:
        if label not in ft.index:
            continue
        specs = build_gasflux_specs({"use_etc": etc is not None, "fit_clearance": fit_k})
        p6, tau6, n6 = post(os.path.join(OUTS, out_dir_for(cfg, medium)), specs)
        p4, tau4, n4 = post(os.path.join(OUTS, p4_dir_for(cfg, medium)), specs)
        for name in p6:
            a, b = p4[name], p6[name]
            rows.append(dict(fit=label, param=name, p4_median=a["median"], p6_median=b["median"],
                             median_shift_in_p6_widths=(b["median"] - a["median"]) / b["width"] if b["width"] else np.nan,
                             p4_width90=a["width"], p6_width90=b["width"],
                             width_ratio_p6_over_p4=b["width"] / a["width"] if a["width"] else np.nan,
                             p6_width_over_prior=b["width"] / b["prior_width"]))
        s = dict(fit=label, p4_steps=n4, p4_tau=round(tau4, 1), p6_steps=n6, p6_tau=round(tau6, 1),
                 p4_growth_R2=p4t.loc[label, "growth_R2_refit"], p6_growth_R2=ft.loc[label, "growth_R2"],
                 p4_resp_R2=p4t.loc[label, "resp_R2_refit"], p6_resp_R2=ft.loc[label, "resp_R2"],
                 p4_c_max=p4t.loc[label, "config"] and (120.0 if medium != "LB" else 120.0), p6_c_max=c_max,
                 sigma_p4=p4["sigma"]["median"], sigma_p6=p6["sigma"]["median"],
                 sigma_ci90_p6=f"[{p6['sigma']['lo']:.3f}, {p6['sigma']['hi']:.3f}]")
        if "clearance_mult" in p6:
            for tag, pp in (("p4", p4), ("p6", p6)):
                K = 5.0 * np.array([pp["clearance_mult"]["lo"], pp["clearance_mult"]["median"], pp["clearance_mult"]["hi"]])
                s[f"K_median_{tag}"] = K[1]; s[f"K_ci90_{tag}"] = f"[{K[0]:.2f}, {K[2]:.2f}]"
                s[f"K_width_over_prior_{tag}"] = (K[2] - K[0]) / 8.0
        summ.append(s)
    pd.DataFrame(rows).to_csv(os.path.join(HERE, "compare_posteriors.csv"), index=False)
    pd.DataFrame(summ).to_csv(os.path.join(HERE, "compare_summary.csv"), index=False)
    pd.set_option("display.width", 250)
    print(pd.DataFrame(summ).round(3).T.to_string())
    df = pd.DataFrame(rows)
    print(df.round(3).to_string(index=False))
    print("[compare] done")


if __name__ == "__main__":
    main()
