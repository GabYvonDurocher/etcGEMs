#!/usr/bin/env python3
"""P11 TASK 2 -- the internal reproducibility check dynesty provides: the prior-volume shrinkage
at each iteration is a random variable (Beta(1, nlive)), and `dynesty.utils.jitter_run` resamples
it to give the statistical spread of log Z and of the posterior that follows from the same
likelihood calls. 200 realisations. This is not an independent second seed -- it re-rolls the
volumes, not the sampling -- and is reported as what it is. Writes task2_jitter.json beside
this file."""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src")); sys.path.insert(0, HERE); os.chdir(ROOT)
import dynesty
from dynesty.utils import jitter_run, resample_equal        # noqa: E402
from etcgem.calibration_multi import build_gasflux_specs    # noqa: E402
OUT = os.path.join(ROOT, "strains", "eciML1515", "outputs", "calibration_configD_NLDM_recipe_P11_nested")


def main(tag="main"):
    s = dynesty.NestedSampler.restore(os.path.join(OUT, f"dynesty_{tag}.save"))
    res = s.results
    specs = build_gasflux_specs({"use_etc": False, "fit_clearance": True}); names = [x.name for x in specs]
    rng = np.random.default_rng(5)
    logzs, meds = [], []
    for k in range(200):
        r = jitter_run(res, rstate=np.random.default_rng(1000 + k))
        logzs.append(float(r.logz[-1]))
        w = np.exp(r.logwt - r.logz[-1]); w = w / w.sum()
        eq = resample_equal(r.samples, w, rstate=np.random.default_rng(2000 + k))
        meds.append(np.median(eq, axis=0))
    logzs = np.array(logzs); meds = np.array(meds)
    nat_sd = []
    for j, sp in enumerate(specs):
        col = np.exp(meds[:, j]) if sp.space == "log" else meds[:, j]
        nat_sd.append(dict(param=sp.name, median_of_medians=float(np.median(col)), sd_of_medians=float(col.std())))
    out = dict(tag=tag, n_realisations=200, logz_mean=float(logzs.mean()), logz_sd=float(logzs.std()),
               logz_reported=float(res.logz[-1]), logzerr_reported=float(res.logzerr[-1]), medians=nat_sd)
    json.dump(out, open(os.path.join(HERE, "task2_jitter.json"), "w"), indent=1)
    print(f"[jitter] log Z over 200 volume realisations: {logzs.mean():.3f} +/- {logzs.std():.3f} "
          f"(the run reports {res.logz[-1]:.3f} +/- {res.logzerr[-1]:.3f})", flush=True)
    for r in nat_sd:
        print(f"[jitter] {r['param']:16s} median {r['median_of_medians']:10.4f}  sd over realisations {r['sd_of_medians']:.4f}", flush=True)
    print("[jitter] done", flush=True)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "main")
