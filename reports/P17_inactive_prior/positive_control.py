"""D25: deliberately informative f coordinate, plus separate independent extra axis."""
import json
import signal
import time
import numpy as np
from scipy.special import logsumexp
import controls as c


def target(u):
    return c.Target('smooth')(u[:15]) + 2*np.log(u[7])


def main():
    def timeout(*unused):
        raise TimeoutError('D25 per-run 120 second deadline')
    signal.signal(signal.SIGALRM, timeout)
    outcomes = []
    for ndim in [15, 16]:
        for seed in range(17601, 17606):
            dest = c.HERE / f'positive_d{ndim}_{seed}.json'
            if dest.exists():
                raise FileExistsError(dest)
            signal.alarm(120)
            t = time.monotonic()
            s = c.dynesty.NestedSampler(
                target, c.identity, ndim, nlive=800, sample='rslice', slices=3,
                bound='multi', first_update={'min_eff': 30},
                rstate=np.random.default_rng(seed))
            s.run_nested(dlogz=.1, print_progress=False)
            r = s.results
            w = np.exp(r.logwt-logsumexp(r.logwt))
            u = r.samples_u
            row = dict(seed=seed, ndim=ndim, wall_s=time.monotonic()-t,
                       logz=float(r.logz[-1]), logzerr=float(r.logzerr[-1]),
                       truth_logz=float(c.truth('smooth')-np.log(3)),
                       informed_mean=float(w@u[:, 7]), truth_informed_mean=.75,
                       informed_correct_cdf_ks=c.ecdf(u[:, 7]**3, w),
                       informed_wrong_uniform_ks=c.ecdf(u[:, 7], w),
                       active_ks=c.ecdf(c.active_cdf(u[:, 0], 'smooth'), w),
                       ncall=int(sum(r.ncall)))
            if ndim == 16:
                row.update(extra_inactive_mean=float(w@u[:, 15]),
                           extra_inactive_ks=c.ecdf(u[:, 15], w))
            row['correct_cdf_closer'] = row['informed_correct_cdf_ks'] < row['informed_wrong_uniform_ks']
            np.savez_compressed(c.HERE/f'positive_d{ndim}_{seed}.npz', u=u, logwt=r.logwt, logl=r.logl)
            with dest.open('x') as out:
                json.dump(row, out, indent=2)
            signal.alarm(0)
            outcomes.append(row)
            print(json.dumps(row), flush=True)
    with (c.HERE/'positive_control_summary.json').open('x') as out:
        json.dump(dict(outcomes=outcomes, all_correct_cdf_closer=all(
            r['correct_cdf_closer'] for r in outcomes),
            scope='Known dependency discriminator; not remedy confirmation or calibrated error limits'), out, indent=2)


if __name__ == '__main__':
    main()
