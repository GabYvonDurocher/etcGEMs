#!/usr/bin/env python3
"""T2 TASK 5 -- ALL live points of every checkpoint (run 3 at its last checkpoint; runs 1-2 final) re-evaluated
fresh in a 16-process pool; how many stored log L exceed the re-evaluated value, by how much. FILE with a
__main__ guard. Development seed: none needed (exhaustive)."""
import os, sys, json, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
for p in (os.path.join(ROOT, "src"), os.path.join(ROOT, "reports", "P6_convergence"), HERE):
    if p not in sys.path: sys.path.insert(0, p)
os.chdir(ROOT)
from t2_target import build, Target, payload            # noqa: E402
from t2_prior import transform_factory                  # noqa: E402
from etcgem import calibration_multi as CM              # noqa: E402
from etcgem.calibration_multi import _gwinit, _set_default_solver, gasflux_log_likelihood   # noqa: E402
OUT = os.path.join(ROOT, "strains", "eciML1515", "outputs", "calibration_configD_NLDM_recipe_T2_validated")
_TG = None; _PT = None


def _eval(u):
    global _TG, _PT
    if _TG is None: _TG = Target(CM._GSPECS); _PT = transform_factory(_TG.sampled)
    return float(gasflux_log_likelihood(_TG.expand(_PT(np.asarray(u, float))), CM._GCTX, CM._GSPECS))


def main():
    import dynesty
    from multiprocessing import Pool
    solver = _set_default_solver("gurobi"); out = {}
    with Pool(16, initializer=_gwinit, initargs=(dict(payload(True), solver=solver),)) as pool:
        for k, seed in ((3, 17903), (1, 17901), (2, 17902)):
            s = dynesty.NestedSampler.restore(os.path.join(OUT, f"run{k}_seed{seed}", "dynesty.save")); U = np.asarray(s.live_u); L = np.asarray(s.live_logl)
            fresh = np.array(pool.map(_eval, list(U), chunksize=10)); d = fresh - L; ad = np.abs(d)
            bad = np.where(d < -1e-3)[0]
            out[k] = dict(it=int(s.it), n=len(U), max_abs=float(ad.max()), n_gt_1e6=int((ad > 1e-6).sum()), n_gt_1e3=int((ad > 1e-3).sum()), n_stored_above_fresh_1e3=int(len(bad)),
                          n_stored_above_by_gt_0p1=int((d < -0.1).sum()), n_fresh_below_loglstar=int((fresh < L.min()).sum()), loglstar=float(L.min()),
                          worst=[dict(i=int(i), stored=float(L[i]), fresh=float(fresh[i]), diff=float(d[i]), u=np.round(U[i], 4).tolist()) for i in np.argsort(d)[:5]])
            print(f"[lp] run {k} it {s.it}: {len(U)} live points; max|diff| {ad.max():.3e}; >1e-6: {out[k]['n_gt_1e6']}; stored above fresh by >1e-3: {len(bad)}; by >0.1: {out[k]['n_stored_above_by_gt_0p1']}; fresh below current loglstar: {out[k]['n_fresh_below_loglstar']}", flush=True)
            for w in out[k]["worst"][:3]: print("    ", {a: b for a, b in w.items() if a != "u"}, flush=True)
    json.dump(out, open(os.path.join(HERE, "task5_livepoints_all.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
