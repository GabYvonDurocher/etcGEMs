#!/usr/bin/env python3
"""P16 TASK 1 -- the WHOLE eigenspectrum of P15's run-1 live points. No solving.

Covariance of the 800 live points in the UNIT CUBE (live_u), per D0: that is the space rslice
samples in, and the prior transform already maps each prior onto [0,1] so no external scale is
imported. Reports all sixteen eigenvalues ascending with full loadings, the dominant pairwise
correlations of each near-degenerate direction, and the count of NEAR-DEGENERATE directions under
D0's rule (eigenvalue below 1e-3 of the largest; also at 1e-2 and 1e-4).
"""
import json, os, sys
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
for p in (os.path.join(ROOT, "src"), os.path.join(ROOT, "reports", "P6_convergence"),
          os.path.join(ROOT, "reports", "P11_nested")):
    if p not in sys.path: sys.path.insert(0, p)
os.chdir(ROOT)
from etcgem.calibration_multi import build_gasflux_specs   # noqa: E402
from p6_fits import FITS                                   # noqa: E402
OUT15 = os.path.join(ROOT, "strains", "eciML1515", "outputs", "calibration_configD_NLDM_recipe_P15_nested")
FIT = [f for f in FITS if f[0] == "D_NLDM"][0]
NAMES = [s.name for s in build_gasflux_specs({"use_etc": FIT[6] is not None, "fit_clearance": FIT[8]})]
THRESHOLDS = (1e-2, 1e-3, 1e-4)
HEADLINE = 1e-3


def main():
    import dynesty
    s = dynesty.NestedSampler.restore(os.path.join(OUT15, "dynesty_run1.save"))
    U = np.asarray(s.live_u, float)
    n, D = U.shape
    print(f"[t1] checkpoint iteration {s.it}; {n} live points, {D} dimensions (unit cube)", flush=True)
    C = np.cov(U, rowvar=False)
    ev, evec = np.linalg.eigh(C)
    o = np.argsort(ev); ev, evec = ev[o], evec[:, o]
    R = np.corrcoef(U, rowvar=False)
    lam_max = float(ev[-1])
    rows = []
    for k in range(D):
        v = evec[:, k]
        top = np.argsort(np.abs(v))[::-1][:3]
        # the pairwise correlation that dominates this direction: among its top loadings
        best, bestr = "", 0.0
        for i in range(len(top)):
            for j in range(i + 1, len(top)):
                a, b = int(top[i]), int(top[j])
                if abs(R[a, b]) > abs(bestr):
                    bestr = float(R[a, b]); best = f"{NAMES[a]}~{NAMES[b]}"
        rows.append(dict(rank=k + 1, eigenvalue=float(ev[k]), sqrt=float(np.sqrt(max(ev[k], 0))),
                         ratio_to_largest=float(ev[k] / lam_max),
                         loadings=", ".join(f"{NAMES[i]} {v[i]:+.3f}" for i in top),
                         dominant_pair=best, pair_corr=bestr))
    T = pd.DataFrame(rows)
    T.to_csv(os.path.join(HERE, "task1_spectrum.csv"), index=False)
    pd.set_option("display.width", 260); pd.set_option("display.max_colwidth", 70)
    print("\n[t1] ALL SIXTEEN EIGENVALUES, ascending")
    print(T[["rank", "eigenvalue", "sqrt", "ratio_to_largest", "loadings", "dominant_pair", "pair_corr"]]
          .to_string(index=False, float_format=lambda x: f"{x:.4e}" if abs(x) < 1e-2 else f"{x:.4f}"))
    cond = lam_max / max(float(ev[0]), 1e-300)
    print(f"\n[t1] condition number (largest/smallest) = {cond:.4e}")
    counts = {}
    for th in THRESHOLDS:
        q = T[T.ratio_to_largest < th]
        counts[th] = len(q)
        print(f"[t1] threshold {th:.0e}: {len(q)} NEAR-DEGENERATE direction(s)"
              + (" -> " + "; ".join(f"#{int(r['rank'])} ({r.dominant_pair}, r={r.pair_corr:+.3f})"
                                    for _, r in q.iterrows()) if len(q) else ""))
    nh = counts[HEADLINE]
    print(f"\n[t1] HEADLINE (threshold {HEADLINE:.0e}): {nh} qualifying direction(s) -> "
          + ("fixing ONE parameter suffices; proceed to TASK 2" if nh == 1
             else ("*** TWO OR MORE -- TASK 4 MUST NOT START ***" if nh >= 2
                   else "*** NONE qualify -- the rule does not identify the crash direction ***")))
    # the full loading matrix for the qualifying directions
    print("\n[t1] full loadings of the near-degenerate direction(s) at the headline threshold")
    for _, r in T[T.ratio_to_largest < HEADLINE].iterrows():
        v = evec[:, int(r["rank"]) - 1]
        print(f"[t1]   direction #{int(r['rank'])} (lambda {r.eigenvalue:.4e}):")
        for i in np.argsort(np.abs(v))[::-1]:
            print(f"[t1]       {NAMES[i]:16s} {v[i]:+.4f}")
    json.dump(dict(iteration=int(s.it), n_live=n, dim=D, eigenvalues=[float(x) for x in ev],
                   ratio_to_largest=[float(x / lam_max) for x in ev], condition_number=cond,
                   thresholds={f"{k:.0e}": int(v) for k, v in counts.items()},
                   headline_threshold=HEADLINE, n_near_degenerate=int(nh),
                   loadings={f"dir{k+1}": {NAMES[i]: float(evec[i, k]) for i in range(D)} for k in range(D)}),
              open(os.path.join(HERE, "task1_spectrum.json"), "w"), indent=1)
    print("\n[t1] done")


if __name__ == "__main__":
    main()
