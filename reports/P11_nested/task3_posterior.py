#!/usr/bin/env python3
"""P11 TASK 3 -- the nested posterior, and what it says about P4's.

Weights: dynesty's importance weights w = exp(logwt - logz); the posterior is summarised by
RESAMPLING to equal weight (dynesty.utils.resample_equal) with a fixed seed, so medians and
5/95 intervals are ordinary sample quantiles of an equally weighted draw.

Beside them: P4's under-converged medians and the intervals P4 would have quoted (its own
summary.json posterior block, post-burn 5/50/95). Writes task3_posterior.csv and
task3_posterior.json beside this file.
"""
import json, os, sys
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src")); sys.path.insert(0, HERE); os.chdir(ROOT)
from etcgem.calibration_multi import build_gasflux_specs, to_natural      # noqa: E402
OUT = os.path.join(ROOT, "strains", "eciML1515", "outputs", "calibration_configD_NLDM_recipe_P11_nested")
P4 = os.path.join(ROOT, "strains", "eciML1515", "outputs", "calibration_configD_NLDM_recipe_cmax120")


def equal_weight(tag="main"):
    from dynesty.utils import resample_equal
    s = np.load(os.path.join(OUT, f"samples_{tag}.npy")); lw = np.load(os.path.join(OUT, f"logwt_{tag}.npy"))
    summ = json.load(open(os.path.join(OUT, f"summary_{tag}.json")))
    w = np.exp(lw - summ["logz"]); w = w / w.sum()
    return resample_equal(s, w, rstate=np.random.default_rng(42)), summ, w


def main(tag="main"):
    specs = build_gasflux_specs({"use_etc": False, "fit_clearance": True}); names = [s.name for s in specs]
    post, summ, w = equal_weight(tag)
    nat = np.array([[np.exp(post[i, j]) if s.space == "log" else post[i, j] for j, s in enumerate(specs)] for i in range(len(post))])
    p4 = json.load(open(os.path.join(P4, "summary.json")))["posterior"]
    rows = []
    for j, s in enumerate(specs):
        lo, med, hi = np.percentile(nat[:, j], [5, 50, 95]); prior_w = s.hi - s.lo
        a = p4[s.name]; p4lo, p4hi = a["ci90"]
        rows.append(dict(param=s.name, new_median=med, new_lo5=lo, new_hi95=hi, new_width=hi - lo,
                         new_width_over_prior=(hi - lo) / prior_w, p4_median=a["posterior_median"],
                         p4_lo5=p4lo, p4_hi95=p4hi, p4_width=p4hi - p4lo, p4_width_over_prior=a["width_ratio_vs_prior"],
                         median_shift=med - a["posterior_median"],
                         moved_outside_p4_interval=bool(med < p4lo or med > p4hi),
                         width_ratio_new_over_p4=(hi - lo) / (p4hi - p4lo) if (p4hi - p4lo) else np.nan,
                         prior_lo=s.lo, prior_hi=s.hi))
    df = pd.DataFrame(rows); df.to_csv(os.path.join(HERE, "task3_posterior.csv"), index=False)
    pd.set_option("display.width", 250)
    print(df[["param", "p4_median", "new_median", "median_shift", "moved_outside_p4_interval", "p4_width", "new_width", "width_ratio_new_over_p4", "new_width_over_prior"]].round(4).to_string(index=False), flush=True)
    n_out = int(df.moved_outside_p4_interval.sum())
    print(f"\n[post] medians outside P4's (invalid) 90 % interval: {n_out} of {len(df)}; "
          f"intervals wider than P4's: {int((df.width_ratio_new_over_p4 > 1).sum())}, narrower: {int((df.width_ratio_new_over_p4 < 1).sum())}", flush=True)
    json.dump(dict(tag=tag, n_equal_weight=int(len(post)), medians_outside_p4=n_out,
                   n_eff=summ["n_eff"], logz=summ["logz"], logzerr=summ["logzerr"],
                   theta_median=[float(np.median(post[:, j])) for j in range(len(specs))], names=names),
              open(os.path.join(HERE, "task3_posterior.json"), "w"), indent=1)
    print("[post] done", flush=True)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "main")
