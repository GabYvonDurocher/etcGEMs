#!/usr/bin/env python3
"""P11 TASK 1 -- the dynesty toy: a 16-dimensional correlated Gaussian likelihood (P8's
covariance: random SPD, condition number 50, seed 0) under a uniform prior on a box wide enough
to hold the mass. log Z is then analytic: with a NORMALISED Gaussian likelihood integrating to
1 over R^16 and a uniform prior of density 1/V, log Z = -log V (to the mass outside the box,
which is < 1e-12 here). dynesty must recover it within its own reported error, and the
posterior mean and covariance within Monte Carlo error.

Module-level definitions only: the loglikelihood and the transform must be picklable for the
process pool (a function defined in __main__ is re-imported by every spawned worker).
Writes toy.json beside this file.
"""
import json, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
D = 16
_rng = np.random.default_rng(0)
_A = _rng.standard_normal((D, D)); COV = _A @ _A.T + 0.5 * np.eye(D)
_w, _V = np.linalg.eigh(COV); COV = (_V * np.clip(_w, _w.max() / 50, None)) @ _V.T
MU = _rng.standard_normal(D) * 3
PREC = np.linalg.inv(COV)
_SD = np.sqrt(np.diag(COV))
LO, HI = MU - 12 * _SD, MU + 12 * _SD          # the box; 12 sd per axis
LOGZ_TRUE = float(-np.sum(np.log(HI - LO)))
_NORM = float(-0.5 * D * np.log(2 * np.pi) - 0.5 * np.linalg.slogdet(COV)[1])


def loglike(x):
    d = np.asarray(x) - MU
    return _NORM - 0.5 * float(d @ PREC @ d)


def ptform(u):
    return LO + np.asarray(u) * (HI - LO)


def main():
    import dynesty
    from dynesty.utils import resample_equal
    from multiprocessing import Pool
    t0 = time.time()
    with Pool(8) as pool:
        s = dynesty.NestedSampler(loglike, ptform, D, nlive=500, sample="rslice", bound="multi",
                                  pool=pool, queue_size=8, rstate=np.random.default_rng(7))
        s.run_nested(dlogz=0.1, print_progress=False)
    r = s.results; wall = time.time() - t0
    logz, logzerr = float(r.logz[-1]), float(r.logzerr[-1])
    w = np.exp(r.logwt - r.logz[-1]); post = resample_equal(r.samples, w / w.sum())
    mean = post.mean(0); cov = np.cov(post, rowvar=False)
    n_eff = float(w.sum() ** 2 / np.sum(w ** 2))
    se = _SD / np.sqrt(n_eff); z = (mean - MU) / se
    cov_rel = np.abs(cov - COV)[np.triu_indices(D)] / np.abs(COV)[np.triu_indices(D)]
    out = dict(dim=D, nlive=500, sample="rslice", niter=int(r.niter), ncall=int(sum(r.ncall)), wall_min=round(wall / 60, 2),
               logz=logz, logzerr=logzerr, logz_true=LOGZ_TRUE, logz_error_in_sigma=float(abs(logz - LOGZ_TRUE) / logzerr),
               n_eff=n_eff, max_abs_z_mean=float(np.abs(z).max()), median_rel_cov_error=float(np.median(cov_rel)),
               passed=bool(abs(logz - LOGZ_TRUE) < 3 * logzerr and np.abs(z).max() < 4))
    json.dump(out, open(os.path.join(HERE, "toy.json"), "w"), indent=1)
    print(f"[toy] log Z {logz:.3f} +/- {logzerr:.3f} against analytic {LOGZ_TRUE:.3f} "
          f"({abs(logz-LOGZ_TRUE)/logzerr:.2f} sigma); n_eff {n_eff:.0f}; max |z| of the means {np.abs(z).max():.2f}; "
          f"median relative covariance error {np.median(cov_rel):.3f}; {int(r.niter)} iters, {int(sum(r.ncall))} calls, {wall/60:.1f} min", flush=True)
    print(f"[toy] PASSED: {out['passed']}", flush=True)


if __name__ == "__main__":
    main()
