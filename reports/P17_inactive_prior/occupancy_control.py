"""D29 asymmetric occupancy test; unchanged biological model, analytic toy only."""
import argparse
import json
import signal
import time
import warnings
import numpy as np
from scipy.special import ndtr, logsumexp
from scipy.stats import truncnorm
import controls as c
from conditional_trace import ParentSlice


class Target:
    def __init__(self, shape, offset):
        self.shape, self.offset = shape, offset

    def __call__(self, u):
        if u[0] > .95:
            return float(11-.5*np.sum(((u[c.ACTIVE[1:]]-.5)/.25)**2))
        return float(self.offset-(.5*((u[14]-.5)/.25)**2 if self.shape == 'smooth' else 0))


def truth(shape, offset):
    z = .25*np.sqrt(2*np.pi)*(ndtr(2)-ndtr(-2))
    terms = [np.log(.95)+offset+(np.log(z) if shape == 'smooth' else 0),
             np.log(.05)+11+13*np.log(z)]
    logz = float(logsumexp(terms))
    return dict(logz=logz, high_mass=float(np.exp(terms[1]-logz)))


def run(shape, offset, seed):
    folder = c.HERE / f'occupancy_{shape}_{offset:g}_{seed}'
    folder.mkdir(exist_ok=False)
    expected = truth(shape, offset)
    (folder/'truth.json').write_text(json.dumps(expected, indent=2))
    start = time.monotonic()
    sampler = c.dynesty.NestedSampler(Target(shape, offset), c.identity, 15,
        nlive=800, sample=ParentSlice(ndim=15, slices=3), bound='multi',
        first_update={'min_eff': 30}, rstate=np.random.default_rng(seed))
    initial = sampler.live_u.copy()
    roots = {u.tobytes(): u.tobytes() for u in initial}
    processed = 0
    starts, ends, history = [], [], []

    def record():
        nonlocal processed
        r = sampler.results
        for st in r.proposal_stats[processed:]:
            if not st or 'parent_u' not in st:
                continue  # Independent unit-cube phase is explicitly untraced.
            p, child = np.array(st['parent_u']), np.array(st['child_u'])
            pk, ck = p.tobytes(), child.tobytes()
            if pk not in roots:
                roots[pk] = pk
            roots[ck] = roots[pk]
            starts.append(p)
            ends.append(child)
        processed = len(r.proposal_stats)
        live = sampler.live_u
        counts = {}
        for u in live[live[:, 0] > .95]:
            key = u.tobytes()
            root = roots.get(key, key)
            counts[root] = counts.get(root, 0)+1
        n = int((live[:, 0] > .95).sum())
        history.append(dict(iteration=int(r.niter), cut=float(sampler.live_logl.min()),
                            high_live=n, high_roots=len(counts),
                            max_high_root_fraction=max(counts.values())/n if n else None,
                            live_nuisance_mean=float(live[:, 7].mean())))
        (folder/'history.json').write_text(json.dumps(history, indent=2))

    sampler.save(str(folder/'checkpoint.save'))
    record()
    while True:
        before = sampler.results.niter
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            sampler.run_nested(maxiter=249, add_live=False, dlogz=.1, print_progress=False)
        sampler.save(str(folder/'checkpoint.save'))
        record()
        if sampler.results.niter == before:
            break
    sampler.add_final_live(print_progress=False)
    r = sampler.results
    w = np.exp(r.logwt-logsumexp(r.logwt))
    u = r.samples_u
    mass = expected['high_mass']
    cdf0 = (1-mass)*np.clip(u[:, 0]/.95, 0, 1)+mass*np.clip((u[:, 0]-.95)/.05, 0, 1)
    cdf1 = (1-mass)*u[:, 1]+mass*truncnorm.cdf(u[:, 1], -2, 2, loc=.5, scale=.25)
    starts, ends = np.asarray(starts), np.asarray(ends)
    ps, pe = starts[:, 0] > .95, ends[:, 0] > .95
    high = ps & pe
    row = dict(shape=shape, offset=offset, seed=seed, wall_s=time.monotonic()-start,
               initial_high=int((initial[:, 0]>.95).sum()),
               high_entry=int((~ps & pe).sum()), high_exit=int((ps & ~pe).sum()),
               high_to_high=int(high.sum()),
               high_nuisance_rms=float(np.sqrt(np.mean((ends[high, 7]-starts[high, 7])**2))) if high.any() else None,
               nuisance_mean=float(w@u[:, 7]), nuisance_ks=c.ecdf(u[:, 7], w),
               region_mass=float(w[u[:, 0]>.95].sum()), truth=expected,
               region_coordinate_ks=c.ecdf(cdf0, w), active_coordinate_ks=c.ecdf(cdf1, w),
               logz=float(r.logz[-1]), logzerr=float(r.logzerr[-1]),
               ncall=int(sampler.ncall), final_live_diagnostic=history[-1],
               scope='Toy intervention changes only low score; roots are descriptive, not statistical ESS. Independent cube-phase proposals are not counted as traced crossings.')
    np.savez_compressed(folder/'weighted_trace.npz', u=u, logwt=r.logwt, logl=r.logl,
                        initial=initial, starts=starts, ends=ends)
    (folder/'result.json').write_text(json.dumps(row, indent=2))
    print(json.dumps(row), flush=True)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--benchmark', action='store_true')
    args = ap.parse_args()
    def expiry(*unused):
        raise TimeoutError('D29 hard run/batch deadline; checkpoint retained')
    signal.signal(signal.SIGALRM, expiry)
    batch_start = time.monotonic()
    for shape in ['flat', 'smooth']:
        for offset in [0., -13.5]:
            for seed in range(17701, 17706):
                if not args.benchmark and (shape, offset, seed) == ('flat', 0., 17701):
                    result = json.loads((c.HERE/'occupancy_flat_0_17701/result.json').read_text())
                    assert result['wall_s'] < 120
                    continue
                remaining = 900-(time.monotonic()-batch_start)
                if remaining <= 0:
                    raise TimeoutError('D29 batch deadline')
                signal.alarm(max(1, int(min(120, remaining))))
                run(shape, offset, seed)
                signal.alarm(0)
                if args.benchmark:
                    raise SystemExit(0)
