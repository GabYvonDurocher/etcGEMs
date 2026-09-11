#!/usr/bin/env python3
"""P15 -- why run 1 crashed: is the live-point cloud degenerate, and in which direction?

The slice sampler failed with bracket steps of ~1e-323 (denormal), i.e. the likelihood-constrained
region is numerically zero-width along the sampled direction. dynesty's bounding had already been
emitting 1,124 divide-by-zero warnings from `1./l1` -- a zero eigenvalue. This loads the last
checkpoint and asks which direction is degenerate, in NATURAL parameter terms.
"""
import json, os, sys
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
for p in (os.path.join(ROOT, "src"), os.path.join(ROOT, "reports", "P6_convergence"),
          os.path.join(ROOT, "reports", "P11_nested")):
    if p not in sys.path: sys.path.insert(0, p)
os.chdir(ROOT)
from etcgem.calibration_multi import build_gasflux_specs                     # noqa: E402
from p6_fits import FITS                                                     # noqa: E402
OUT = os.path.join(ROOT, "strains", "eciML1515", "outputs", "calibration_configD_NLDM_recipe_P15_nested")
FIT = [f for f in FITS if f[0] == "D_NLDM"][0]
ETC, FIT_K = FIT[6], FIT[8]
NAMES = [s.name for s in build_gasflux_specs({"use_etc": ETC is not None, "fit_clearance": FIT_K})]


def main():
    import dynesty
    s = dynesty.NestedSampler.restore(os.path.join(OUT, "dynesty_run1.save"))
    U = np.asarray(s.live_u, float)          # live points in the UNIT CUBE, which is what rslice works in
    print(f"[cd] checkpoint at iteration {s.it}, {U.shape[0]} live points in {U.shape[1]} dimensions")
    C = np.cov(U, rowvar=False)
    ev, evec = np.linalg.eigh(C)
    order = np.argsort(ev)                    # smallest first -- the degenerate directions
    print(f"[cd] live-point covariance eigenvalues (unit cube), smallest 6:")
    for k in order[:6]:
        v = evec[:, k]
        top = np.argsort(np.abs(v))[::-1][:3]
        print(f"[cd]   lambda {ev[k]:.3e}  sqrt {np.sqrt(max(ev[k],0)):.3e}  loading: "
              + ", ".join(f"{NAMES[i]} {v[i]:+.3f}" for i in top))
    print(f"[cd] largest eigenvalue {ev[order[-1]]:.3e}; CONDITION NUMBER "
          f"{ev[order[-1]]/max(ev[order[0]],1e-300):.3e}")
    sd = U.std(axis=0)
    w = pd.DataFrame(dict(param=NAMES, live_sd_unit_cube=sd)).sort_values("live_sd_unit_cube")
    print("\n[cd] per-parameter spread of the live points in the unit cube (1.0/sqrt(12)=0.289 is the prior):")
    print(w.round(6).to_string(index=False))
    # the dTm / tm_scale plane specifically -- Y3's non-identified pair
    i, j = NAMES.index("dTm"), NAMES.index("tm_scale")
    r = float(np.corrcoef(U[:, i], U[:, j])[0, 1])
    sub = np.cov(U[:, [i, j]], rowvar=False); e2 = np.linalg.eigvalsh(sub)
    print(f"\n[cd] Y3's pair: corr(dTm, tm_scale) among live points = {r:+.4f}; "
          f"2x2 eigenvalues {e2[0]:.3e} / {e2[1]:.3e}, condition {e2[1]/max(e2[0],1e-300):.1f}")
    worst = int(order[0])
    v = evec[:, worst]
    json.dump(dict(iteration=int(s.it), n_live=int(U.shape[0]),
                   eigenvalues_smallest=[float(ev[k]) for k in order[:6]],
                   condition_number=float(ev[order[-1]] / max(ev[order[0]], 1e-300)),
                   degenerate_direction={NAMES[k]: float(v[k]) for k in np.argsort(np.abs(v))[::-1][:5]},
                   corr_dTm_tm_scale=r,
                   live_sd={n: float(x) for n, x in zip(NAMES, sd)}),
              open(os.path.join(HERE, "task1_crash_diag.json"), "w"), indent=1)
    print("\n[cd] done")


if __name__ == "__main__":
    main()
