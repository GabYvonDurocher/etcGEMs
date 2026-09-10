#!/usr/bin/env python3
"""P11 TASK 2 -- the second-seed reproducibility check: the two converged runs against each
other. log Z with its combined error, and every posterior median with the Monte-Carlo error on
that median (the equal-weight sample's own sd / sqrt(n_eff)). Writes task2_seed_compare.csv."""
import json, os, sys
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src")); sys.path.insert(0, HERE); os.chdir(ROOT)
import dynesty                                                        # noqa: E402
from etcgem.calibration_multi import build_gasflux_specs              # noqa: E402
from task3_posterior import equal_weight                             # noqa: E402
OUT = os.path.join(ROOT, "strains", "eciML1515", "outputs", "calibration_configD_NLDM_recipe_P11_nested")


def main():
    specs = build_gasflux_specs({"use_etc": False, "fit_clearance": True})
    A, sA, _ = equal_weight("main"); B, sB, _ = equal_weight("seed2")
    dz = sA["logz"] - sB["logz"]; err = float(np.hypot(sA["logzerr"], sB["logzerr"]))
    hs = {}
    for tag in ("main", "seed2"):
        s = dynesty.NestedSampler.restore(os.path.join(OUT, f"dynesty_{tag}.save"))
        hs[tag] = float(np.array(s.saved_run["h"])[-1])
    print(f"[cmp] main : nlive 400  it {sA['iters']:5d}  evals {sA['ncall']:6d}  logZ {sA['logz']:.3f} +/- {sA['logzerr']:.3f}  n_eff {sA['n_eff']:.0f}  H {hs['main']:.2f}", flush=True)
    print(f"[cmp] seed2: nlive 250  it {sB['iters']:5d}  evals {sB['ncall']:6d}  logZ {sB['logz']:.3f} +/- {sB['logzerr']:.3f}  n_eff {sB['n_eff']:.0f}  H {hs['seed2']:.2f}", flush=True)
    print(f"[cmp] log Z difference {dz:+.3f} against a combined error of {err:.3f} -> {abs(dz)/err:.1f} sigma  "
          f"=> {'AGREE' if abs(dz) < 2*err else 'DISAGREE'}", flush=True)
    rows = []
    for j, sp in enumerate(specs):
        a = np.exp(A[:, j]) if sp.space == "log" else A[:, j]
        b = np.exp(B[:, j]) if sp.space == "log" else B[:, j]
        # MC error on a median ~ 1.253 * sd / sqrt(n_eff)
        sea = 1.253 * a.std() / np.sqrt(sA["n_eff"]); seb = 1.253 * b.std() / np.sqrt(sB["n_eff"])
        se = float(np.hypot(sea, seb)); d = float(np.median(a) - np.median(b))
        rows.append(dict(param=sp.name, main_median=float(np.median(a)), seed2_median=float(np.median(b)),
                         diff=d, mc_error=se, sigma=abs(d) / se if se else np.nan,
                         main_w90=float(np.percentile(a, 95) - np.percentile(a, 5)),
                         seed2_w90=float(np.percentile(b, 95) - np.percentile(b, 5)),
                         agree_2sigma=bool(abs(d) < 2 * se)))
    df = pd.DataFrame(rows); df.to_csv(os.path.join(HERE, "task2_seed_compare.csv"), index=False)
    pd.set_option("display.width", 220)
    print(df[["param", "main_median", "seed2_median", "diff", "mc_error", "sigma", "agree_2sigma"]].round(4).to_string(index=False), flush=True)
    print(f"\n[cmp] medians agreeing within 2 MC errors: {int(df.agree_2sigma.sum())} of {len(df)}; "
          f"largest discrepancy {df.sigma.max():.1f} sigma on {df.loc[df.sigma.idxmax(),'param']}", flush=True)
    json.dump(dict(logz_main=sA["logz"], logzerr_main=sA["logzerr"], logz_seed2=sB["logz"], logzerr_seed2=sB["logzerr"],
                   logz_diff=dz, logz_combined_err=err, logz_sigma=abs(dz)/err, logz_agree=bool(abs(dz) < 2*err),
                   H_main=hs["main"], H_seed2=hs["seed2"], medians_agreeing=int(df.agree_2sigma.sum()), n_params=len(df),
                   max_median_sigma=float(df.sigma.max())), open(os.path.join(HERE, "task2_seed_compare.json"), "w"), indent=1)
    print("[cmp] done", flush=True)


if __name__ == "__main__":
    main()
