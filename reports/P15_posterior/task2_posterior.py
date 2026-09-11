#!/usr/bin/env python3
"""P15 TASK 2 -- the posterior, the agreement verdict, and the two predictions.

Resampling, stated: dynesty's importance weights w_i = exp(logwt_i - logz) are used directly for
weighted quantiles (no multinomial resampling), so no Monte-Carlo noise is added beyond the run's
own. Monte-Carlo error on a median is estimated by the standard bootstrap over the weighted sample.
"""
import argparse, json, os, sys
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
for p in (os.path.join(ROOT, "reports", "P13_support"), os.path.join(ROOT, "reports", "P6_convergence")):
    if p not in sys.path: sys.path.insert(0, p)
from common13 import NAMES, SPECS, build, decompose, to_natural, _MASK_G, P4DIR   # noqa: E402

OUT15 = os.path.join(ROOT, "strains", "eciML1515", "outputs", "calibration_configD_NLDM_recipe_P15_nested")
OUT11 = os.path.join(ROOT, "strains", "eciML1515", "outputs", "calibration_configD_NLDM_recipe_P11_nested")
NEAR = 0.01


def load(d, tag):
    s = np.load(os.path.join(d, f"samples_{tag}.npy")); lw = np.load(os.path.join(d, f"logwt_{tag}.npy"))
    w = np.exp(lw - lw.max()); w /= w.sum()
    return s, w


def wq(x, w, q):
    i = np.argsort(x); x, w = x[i], w[i]
    c = np.cumsum(w) - 0.5 * w; c /= w.sum()
    return np.interp(q, c, x)


def mc_err(x, w, nboot=200, seed=0):
    rng = np.random.default_rng(seed); n = len(x)
    idx = rng.choice(n, size=(nboot, n), p=w / w.sum())
    return float(np.std([np.median(x[i]) for i in idx]))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--tags", default="run1,run2"); a = ap.parse_args()
    tags = a.tags.split(",")
    S = {t: load(OUT15, t) for t in tags}
    summ = {t: json.load(open(os.path.join(OUT15, f"summary_{t}.json"))) for t in tags}

    # ---- agreement rule ----
    lz = {t: (summ[t]["logz"], summ[t]["logzerr"]) for t in tags}
    print("=== the runs ===")
    for t in tags:
        s = summ[t]
        print(f"  {t}: iters {s['iters']}, evals {s['ncall']}, wall {s['wall_h']:.2f} h, "
              f"dlogz {s['dlogz_final']:.4f}, logZ {s['logz']:.3f} +/- {s['logzerr']:.3f}, "
              f"n_eff {s['n_eff']:.0f}, converged_on_dlogz {s['converged_on_dlogz']}")
    rows = []
    if len(tags) == 2:
        a_, b_ = tags
        comb = float(np.hypot(lz[a_][1], lz[b_][1])); d = abs(lz[a_][0] - lz[b_][0])
        print(f"\n=== agreement ===\n  |log Z difference| {d:.3f}  combined error {comb:.3f}  "
              f"= {d/comb:.2f} sigma  -> {'within' if d <= comb else 'OUTSIDE'}")
        for i, n in enumerate(NAMES):
            xa, wa = S[a_][0][:, i], S[a_][1]; xb, wb = S[b_][0][:, i], S[b_][1]
            ma, mb = wq(xa, wa, 0.5), wq(xb, wb, 0.5)
            ea, eb = mc_err(xa, wa), mc_err(xb, wb)
            e = float(np.hypot(ea, eb))
            rows.append(dict(param=n, median_a=ma, median_b=mb, diff=mb - ma, mc_error=e,
                             sigma=abs(mb - ma) / e if e > 0 else np.nan,
                             lo5_a=wq(xa, wa, 0.05), hi95_a=wq(xa, wa, 0.95),
                             lo5_b=wq(xb, wb, 0.05), hi95_b=wq(xb, wb, 0.95)))
        A = pd.DataFrame(rows); A.to_csv(os.path.join(HERE, "task2_agreement.csv"), index=False)
        pd.set_option("display.width", 220)
        print(A[["param", "median_a", "median_b", "diff", "mc_error", "sigma"]].round(4).to_string(index=False))
        worst = A.loc[A.sigma.idxmax()]
        agreed = bool(d <= comb and (A.sigma <= 2).all())
        print(f"\n  worst median: {worst.param} at {worst.sigma:.2f} MC errors")
        print(f"  VERDICT: {'AGREED' if agreed else 'DISAGREED'}")
        json.dump(dict(logz_diff=d, combined_err=comb, sigma=d / comb,
                       worst_param=str(worst.param), worst_sigma=float(worst.sigma),
                       agreed=agreed), open(os.path.join(HERE, "task2_agreement.json"), "w"), indent=1)

    # ---- the two predictions ----
    ctx, sp = build()
    def frac_near_mask(samples, w, n=400, seed=0):
        rng = np.random.default_rng(seed)
        idx = rng.choice(len(samples), size=min(n, len(samples)), p=w / w.sum())
        hit, g15 = 0, []
        for k in idx:
            d = decompose(samples[k], ctx, SPECS)
            g = np.asarray(d["growth"], float)
            if np.any(np.abs(g - _MASK_G) <= NEAR * _MASK_G): hit += 1
            g15.append(float(g[0]))
        return hit / len(idx), float(np.mean(g15)), float(np.std(g15))
    pred = {}
    for lbl, (s, w) in [("P15_" + tags[0], S[tags[0]])] + ([("P11_main", load(OUT11, "main"))]):
        f, m15, s15 = frac_near_mask(s, w)
        pred[lbl] = dict(frac_within_1pct_of_mask=f, growth15_mean=m15, growth15_sd=s15)
        print(f"\n[pred] {lbl}: fraction of posterior samples with a temperature within 1 % of "
              f"_MASK_G = {f:.4f}; posterior-predictive growth at 15 C = {m15:.5f} +/- {s15:.5f} /h")
    json.dump(pred, open(os.path.join(HERE, "task2_predictions.json"), "w"), indent=1)
    print("\n[t2] done")


if __name__ == "__main__":
    main()
