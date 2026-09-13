"""D26: exact conditional nuisance refresh cannot repair biased active samples."""
import hashlib
import json
import time
import numpy as np
from scipy.special import logsumexp
import independent_audit as a
import controls as c


def main():
    started = time.monotonic()
    result = {}
    for name in ['red1', 'red2'] + [f'spike_{seed}' for seed in range(17001, 17006)]:
        if name.startswith('red'):
            sources = [a.BASE/f'samples_{name}.npy', a.BASE/f'logwt_{name}.npy']
            u = a.cdf(np.load(sources[0]))
            lw = np.load(sources[1])
        else:
            seed = int(name.split('_')[1])
            sources = [a.HERE/f'spike_plain_p1_t0_s3_{seed}.npz']
            data = np.load(sources[0])
            u, lw = data['u'], data['logwt']
        w = np.exp(lw-logsumexp(lw))
        row = dict(source_sha256={str(p.relative_to(a.ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
                   original_mean=float(w@u[:, 7]), original_ks=a.ecdf(u[:, 7], w),
                   refresh=[])
        active = np.delete(u, 7, axis=1)
        for seed in range(17651, 17656):
            copy = u.copy()
            copy[:, 7] = np.random.default_rng(seed).random(len(copy))
            assert np.array_equal(np.delete(copy, 7, axis=1), active)
            entry = dict(seed=seed, mean=float(w@copy[:, 7]), ks=a.ecdf(copy[:, 7], w),
                         active_coordinates_and_weights_unchanged=True)
            if name.startswith('spike'):
                entry.update(region_mass=float(w[copy[:, 0]<.5].sum()),
                             truth_region_mass=float(c.active_cdf(.5, 'spike')))
                assert entry['region_mass'] == float(w[u[:, 0]<.5].sum())
            row['refresh'].append(entry)
        result[name] = row
    with (a.HERE/'nuisance_only_refresh.json').open('x') as out:
        json.dump(dict(results=result, wall_s=time.monotonic()-started,
                       scope='Diagnostic copies only; no changed P16 posterior saved. '
                             'Conditional nuisance recovery cannot validate active inference.'), out, indent=2)
    for name, row in result.items():
        print(name, 'original KS', row['original_ks'], 'refreshed KS',
              [round(x['ks'], 5) for x in row['refresh']],
              'active region', row['refresh'][0].get('region_mass'))


if __name__ == '__main__':
    main()
