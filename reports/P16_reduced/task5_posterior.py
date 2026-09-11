#!/usr/bin/env python3
"""P16 TASK 5 -- the reduced posterior, with D4's pre-registered reporting.

Resampling, stated: dynesty's importance weights w = exp(logwt - logz) are used directly for
weighted quantiles and for the weighted covariance; no multinomial resampling, so no Monte-Carlo
noise is added beyond the run's own. Median Monte-Carlo error is a weighted bootstrap.

EVERY summary carries the hidden uncertainty fixed in D2:
  this posterior assumes the meltome's MEAN is exactly right; any uniform error in the measured
  melting temperatures is absorbed by tm_scale and the catalytic parameters.
"""
import argparse, json, os, sys
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
for p in (HERE, os.path.join(ROOT, "reports", "P13_support"), os.path.join(ROOT, "reports", "P11_nested"),
          os.path.join(ROOT, "reports", "P6_convergence"), os.path.join(ROOT, "src")):
    if p not in sys.path: sys.path.insert(0, p)
from reduced import FREE_NAMES, FREE_SPECS, FIXED_NAME, FIXED_SAMPLED, expand   # noqa: E402
from common13 import build, SPECS, NAMES, decompose, P4DIR                       # noqa: E402
from etcgem.calibration_multi import to_natural                                  # noqa: E402
OUT = os.path.join(ROOT, "strains", "eciML1515", "outputs", "calibration_configD_NLDM_recipe_P16_reduced")
OUT11 = os.path.join(ROOT, "strains", "eciML1515", "outputs", "calibration_configD_NLDM_recipe_P11_nested")
PRIOR_SD_CUBE = 1.0 / np.sqrt(12.0)          # uniform prior on the unit cube (D4)
CONSTRAINED, PRIOR_DOM = 0.5, 0.8            # D4's classification, fixed in advance
TM_BOUND = (0.4, 2.2)
HIDDEN = ("this posterior assumes the meltome's MEAN is exactly right; any uniform error in the "
          "measured melting temperatures is absorbed by tm_scale and the catalytic parameters")


def load(tag):
    """samples (parameter space), importance weights, and samples_u (unit cube), all CONSISTENT.

    The committed .npy files were written after `add_final_live`, so they carry the final 800 live
    points; the periodic checkpoint was written before it and is 800 rows shorter. Restoring and
    folding the final live points in reproduces the same set -- it costs no likelihood evaluations,
    since those points already carry their logl -- and is verified row-for-row against the .npy.
    """
    s = np.load(os.path.join(OUT, f"samples_{tag}.npy"))
    lw = np.load(os.path.join(OUT, f"logwt_{tag}.npy"))
    w = np.exp(lw - lw.max()); w /= w.sum()
    import dynesty
    smp = dynesty.NestedSampler.restore(os.path.join(OUT, f"dynesty_{tag}.save"))
    if len(np.asarray(smp.results["samples"])) < len(s):
        smp.add_final_live(print_progress=False)
    r = smp.results
    u = np.asarray(r["samples_u"], float)
    assert len(u) == len(s), (len(u), len(s))
    d = float(np.max(np.abs(np.asarray(r["samples"], float) - s)))
    assert d < 1e-9, f"restored samples differ from the committed .npy by {d:.3e}"
    return s, w, u


def wq(x, w, q):
    i = np.argsort(x); x, w = x[i], w[i]
    c = np.cumsum(w) - 0.5 * w; c /= w.sum()
    return float(np.interp(q, c, x))


def mc(x, w, nb=200, seed=0):
    rng = np.random.default_rng(seed); n = len(x)
    idx = rng.choice(n, size=(nb, n), p=w / w.sum())
    return float(np.std([np.median(x[i]) for i in idx]))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--tags", default="red1,red2"); a = ap.parse_args()
    tags = [t for t in a.tags.split(",") if os.path.exists(os.path.join(OUT, f"samples_{t}.npy"))]
    print(f"[t5] runs available: {tags}")
    print(f"[t5] FIXED: {FIXED_NAME} = {FIXED_SAMPLED} -- {HIDDEN}\n")
    S = {t: load(t) for t in tags}
    summ = {t: json.load(open(os.path.join(OUT, f"summary_{t}.json"))) for t in tags}
    for t in tags:
        s = summ[t]
        print(f"[t5] {t}: iters {s['iters']}, evals {s['ncall']}, wall {s['wall_h']:.2f} h, "
              f"dlogz {s['dlogz_final']:.4f}, logZ {s['logz']:.4f} +/- {s['logzerr']:.4f}, "
              f"n_eff {s['n_eff']:.0f}, converged {s['converged_on_dlogz']}")

    # ---------- agreement ----------
    verdict = None
    if len(tags) == 2:
        A, B = tags
        d = abs(summ[A]["logz"] - summ[B]["logz"]); comb = float(np.hypot(summ[A]["logzerr"], summ[B]["logzerr"]))
        rows = []
        for i, n in enumerate(FREE_NAMES):
            xa, wa = S[A][0][:, i], S[A][1]; xb, wb = S[B][0][:, i], S[B][1]
            ma, mb = wq(xa, wa, .5), wq(xb, wb, .5); e = float(np.hypot(mc(xa, wa), mc(xb, wb)))
            rows.append(dict(param=n, median_a=ma, median_b=mb, diff=mb - ma, mc_error=e,
                             sigma=abs(mb - ma) / e if e > 0 else np.nan))
        AG = pd.DataFrame(rows); AG.to_csv(os.path.join(HERE, "task5_agreement.csv"), index=False)
        pd.set_option("display.width", 230)
        print(f"\n[t5] === AGREEMENT ===\n[t5] |log Z difference| {d:.4f}, combined error {comb:.4f} "
              f"= {d/comb:.2f} sigma -> {'within' if d <= comb else 'OUTSIDE'}")
        print(AG.round(4).to_string(index=False))
        worst = AG.loc[AG.sigma.idxmax()]
        verdict = bool(d <= comb and (AG.sigma <= 2).all())
        print(f"[t5] worst median: {worst.param} at {worst.sigma:.2f} MC errors")
        print(f"[t5] VERDICT: {'AGREED' if verdict else 'DISAGREED'}")

    # ---------- marginals, beside P4 ----------
    tag = tags[0]; s, w, u = S[tag]
    ch = np.load(os.path.join(P4DIR, "chain.npy")); burn = int(2 * 244.7)
    p4 = np.median(ch[burn:].reshape(-1, ch.shape[2]), axis=0)
    p4n = to_natural(p4, SPECS)
    rows = []
    for i, n in enumerate(FREE_NAMES):
        x = s[:, i]; sp = FREE_SPECS[i]
        lo, med, hi = wq(x, w, .05), wq(x, w, .5), wq(x, w, .95)
        # natural-space median, via the spec's own space
        base = float(sp.emergent) if sp.emergent is not None else 1.0   # halfnormal discrepancies have no nominal
        natmed = med if sp.space == "add" else float(np.exp(med) * base)
        rows.append(dict(param=n, median_sampled=med, lo5=lo, hi95=hi, width=hi - lo,
                         natural_median=natmed, prior_sd=float(sp.scale),
                         width_over_prior=(hi - lo) / (2 * 1.645 * float(sp.scale)),
                         p4_median_natural=float(p4n.get(n, np.nan))))
    M = pd.DataFrame(rows); M.to_csv(os.path.join(HERE, "task5_marginals.csv"), index=False)
    print(f"\n[t5] === MARGINALS ({tag}) -- {FIXED_NAME} FIXED AT {FIXED_SAMPLED}; {HIDDEN} ===")
    print(M[["param", "natural_median", "median_sampled", "lo5", "hi95", "width_over_prior",
             "p4_median_natural"]].round(4).to_string(index=False))

    # ---------- D4 item 1: the eigendecomposition ----------
    mu = (u * w[:, None]).sum(0)
    X = u - mu
    C = (X * w[:, None]).T @ X / (1 - np.sum(w ** 2))
    ev, evec = np.linalg.eigh(C); o = np.argsort(ev); ev, evec = ev[o], evec[:, o]
    erows = []
    for k in range(len(ev)):
        v = evec[:, k]; ratio = float(np.sqrt(max(ev[k], 0)) / PRIOR_SD_CUBE)
        cls = "CONSTRAINED" if ratio < CONSTRAINED else ("PRIOR-DOMINATED" if ratio > PRIOR_DOM else "INTERMEDIATE")
        top = np.argsort(np.abs(v))[::-1][:3]
        erows.append(dict(rank=k + 1, eigenvalue=float(ev[k]), post_over_prior=ratio, classification=cls,
                          loadings=", ".join(f"{FREE_NAMES[i]} {v[i]:+.3f}" for i in top)))
    E = pd.DataFrame(erows)
    full = pd.DataFrame(evec, index=FREE_NAMES, columns=[f"dir{k+1}" for k in range(len(ev))])
    E.to_csv(os.path.join(HERE, "task5_eigen.csv"), index=False)
    full.to_csv(os.path.join(HERE, "task5_eigenvectors.csv"))
    print(f"\n[t5] === POSTERIOR EIGENDECOMPOSITION (unit cube; prior sd along any direction = "
          f"{PRIOR_SD_CUBE:.4f}) ===")
    print(E.round(4).to_string(index=False))
    nc = int((E.classification == "CONSTRAINED").sum()); npd = int((E.classification == "PRIOR-DOMINATED").sum())
    print(f"[t5] the data CONSTRAIN {nc} of {len(ev)} directions; {npd} are PRIOR-DOMINATED; "
          f"{len(ev)-nc-npd} intermediate")

    # ---------- D4 item 2: the prediction ----------
    R = np.corrcoef((u * 1.0), rowvar=False)
    pairs = [("sigma", "kcat_scale"), ("dCp_scale", "dTopt"), ("kappa_scale", "tm_scale")]
    print("\n[t5] === D4 PREDICTION: the three pairs stronger than the fixed one ===")
    prow = []
    for x, y in pairs:
        i, j = FREE_NAMES.index(x), FREE_NAMES.index(y)
        r = float(R[i, j])
        # the direction most loaded on this pair
        pair_load = np.abs(evec[i, :]) + np.abs(evec[j, :])
        kbest = int(np.argmax(pair_load))
        prow.append(dict(pair=f"{x}~{y}", corr_posterior=r,
                         top_direction=kbest + 1, its_ratio=float(np.sqrt(max(ev[kbest], 0)) / PRIOR_SD_CUBE),
                         its_class=E.classification.iloc[kbest]))
        print(f"[t5]   {x}~{y}: posterior corr {r:+.3f}; most-loaded direction #{kbest+1} "
              f"(ratio {prow[-1]['its_ratio']:.3f}, {prow[-1]['its_class']})")
    pd.DataFrame(prow).to_csv(os.path.join(HERE, "task5_prediction.csv"), index=False)

    # ---------- D4 item 3: tm_scale railing ----------
    it = FREE_NAMES.index("tm_scale"); spt = FREE_SPECS[it]
    xs = s[:, it]; nat = np.exp(xs) * (float(spt.emergent) if spt.emergent is not None else 1.0)
    q = [wq(nat, w, z) for z in (.05, .5, .95)]
    near = float(w[nat >= 0.95 * TM_BOUND[1]].sum())
    print(f"\n[t5] === tm_scale, with its bound beside it (D4 item 3) ===")
    print(f"[t5]   posterior median {q[1]:.4f}, 5/95 [{q[0]:.4f}, {q[2]:.4f}]; prior bound {TM_BOUND}")
    print(f"[t5]   posterior mass within 5 % of the upper bound 2.2: {100*near:.2f} %")
    print(f"[t5]   TASK 2 said Y3's 4-6 K tail needs 1.32-1.62 -> "
          f"{'INSIDE the posterior 5/95' if q[0] <= 1.32 <= q[2] or q[0] <= 1.62 <= q[2] else 'OUTSIDE the posterior 5/95'}")
    railing = bool(near > 0.05)
    print(f"[t5]   RAILING: {'YES -- the reduction RELOCATED the degeneracy' if railing else 'no'}")

    # ---------- the tail (Y3's invariant) ----------
    ctx, sp2 = build()
    def _find_Tm(pm):
        """_Tm lives on the EnzymeConstrainedModel the provider wraps, not on the provider."""
        for holder in (pm, getattr(pm, "ec", None), getattr(pm, "thermal", None)):
            if holder is not None and hasattr(holder, "_Tm"):
                return np.asarray(getattr(holder, "_Tm"), float)
        for o in vars(pm).values():
            if hasattr(o, "_Tm"):
                return np.asarray(o._Tm, float)
        raise AttributeError("could not locate the enzyme Tm vector")
    Tm = _find_Tm(ctx["pm"]); Tm = Tm[np.isfinite(Tm)]; mT = float(Tm.mean())
    print(f"\n[t5] === THE TAIL (Y3's invariant), at the posterior median tm_scale = {q[1]:.4f} ===")
    trow = []
    for pc in (1, 2, 5):
        d = mT - float(np.quantile(Tm, pc / 100))
        shift = (q[1] - 1.0) * (-d)
        # tm_scale's 5th percentile gives the LEAST negative shift, so order the interval
        a_, b_ = sorted(((q[0] - 1.0) * (-d), (q[2] - 1.0) * (-d)))
        covers = bool(a_ <= -4.0 <= b_ or a_ <= -6.0 <= b_ or (-6.0 >= a_ and -4.0 <= b_))
        trow.append(dict(percentile=pc, delta_below_mean_K=d, Tm_shift_K=shift, lo=a_, hi=b_,
                         covers_Y3_invariant=covers))
        print(f"[t5]   {pc}th pct enzyme ({d:.2f} K below the mean): effective Tm shift "
              f"{shift:+.2f} K  [5/95 {a_:+.2f} to {b_:+.2f}]  "
              f"(Y3's invariant: -4 to -6 K -> {'covered by the interval' if covers else 'NOT covered'})")
    pd.DataFrame(trow).to_csv(os.path.join(HERE, "task5_tail.csv"), index=False)

    # ---------- R2 at the posterior median ----------
    med15 = np.array([wq(s[:, i], w, .5) for i in range(len(FREE_NAMES))])
    d_ = decompose(expand(med15), ctx, SPECS)
    g = np.asarray(d_["growth"], float); go = np.asarray(d_["growth_obs"], float)
    o2 = np.asarray(d_["o2"], float); ro = np.asarray(d_["resp_obs"], float)
    natmed = to_natural(expand(med15), SPECS)
    pred_r = o2 * ctx["o2_conv"] * float(natmed["resp_scale"])
    def r2(obs, pred):
        m = np.isfinite(obs) & np.isfinite(pred)
        if m.sum() < 2: return float("nan")
        ss = np.sum((obs[m] - pred[m]) ** 2); st = np.sum((obs[m] - obs[m].mean()) ** 2)
        return float(1 - ss / st)
    r2g, r2r = r2(go, g), r2(np.log(ro), np.log(np.where(pred_r > 0, pred_r, np.nan)))
    print(f"\n[t5] === R2 AT THE POSTERIOR MEDIAN (log_o2_floor 1.42, support clamp) ===")
    print(f"[t5]   growth R2 {r2g:.4f}   respiration R2 (log scale) {r2r:.4f}")
    print(f"[t5]   peak predicted growth {np.nanmax(g):.4f} /h against a measured {np.nanmax(go):.4f}")
    print(f"[t5]   NOTE: {HIDDEN}")
    pd.DataFrame([dict(growth_R2=r2g, resp_R2_log=r2r, peak_growth=float(np.nanmax(g)),
                       peak_obs=float(np.nanmax(go)))]).to_csv(os.path.join(HERE, "task5_r2.csv"), index=False)

    json.dump(dict(tags=tags, agreed=verdict, n_constrained=nc, n_prior_dominated=npd,
                   growth_R2=r2g, resp_R2_log=r2r,
                   tm_scale_median=q[1], tm_scale_5_95=[q[0], q[2]], tm_mass_near_bound=near,
                   railing=railing, fixed=FIXED_NAME, hidden_uncertainty=HIDDEN),
              open(os.path.join(HERE, "task5_summary.json"), "w"), indent=1, default=float)
    print("\n[t5] done")


if __name__ == "__main__":
    main()
