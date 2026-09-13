"""Read-only independent ancestry and stratum audit of a P17 checkpoint snapshot."""
import argparse
import hashlib
import json
import pickle
import sys
from pathlib import Path

import numpy as np
import independent_audit as a
from conditional_trace import ParentSlice
from premise import cm, PAYLOAD


def audit(folder):
    # Load a single immutable byte snapshot. Never resume or modify the sampler.
    # CLI checkpoints pickle the tracing class under __main__.
    sys.modules['__main__'].ParentSlice = ParentSlice
    raw = (folder / 'checkpoint.save').read_bytes()
    saved = pickle.loads(raw)
    s = saved['sampler']
    r = s.results
    snapshot = folder / f'audit_checkpoint_{r.niter}.save'
    if snapshot.exists():
        assert snapshot.read_bytes() == raw
    else:
        with snapshot.open('xb') as out:
            out.write(raw)
    initial = np.load(folder / 'initial.npz')
    _, obs, err, _, _, _ = cm.load_respirometry(
        PAYLOAD['strain'], PAYLOAD['table'], PAYLOAD['otu'])
    j = a.reduced.FREE_NAMES.index('disc_growth')

    def curve(theta):
        variance = np.asarray(err)**2 + np.exp(theta[j])**2
        return float(-.5 * np.sum(np.asarray(obs)**2 / variance + np.log(2*np.pi*variance)))

    # Every accepted child must be either discarded later or still alive.
    points = {}
    for us, vs, ls in [(initial['u'], initial['v'], initial['logl']),
                       (r.samples_u, r.samples, r.logl),
                       (s.live_u, s.live_v, s.live_logl)]:
        for u, v, ll in zip(us, vs, ls):
            key = u.tobytes()
            if key in points:
                assert np.array_equal(points[key][0], v) and points[key][1] == ll
            points[key] = (v, float(ll))
    parent_of = {}
    pairs = []
    for stats in r.proposal_stats:
        assert stats and 'parent_u' in stats and 'child_u' in stats
        parent = np.asarray(stats['parent_u'], dtype=np.float64)
        child = np.asarray(stats['child_u'], dtype=np.float64)
        pk, ck = parent.tobytes(), child.tobytes()
        assert pk in points and ck in points
        assert ck not in parent_of and ck != pk
        parent_of[ck] = pk
        pairs.append((parent, child))
    roots = {x.tobytes(): x for x in initial['u']}

    def root(key):
        visited = set()
        while key not in roots:
            assert key not in visited, 'Cycle in proposal genealogy'
            visited.add(key)
            key = parent_of[key]
        return key

    def group_stats(us):
        counts = {}
        for u in us:
            k = root(u.tobytes())
            counts[k] = counts.get(k, 0) + 1
        n = len(us)
        if not n:
            return {'count': 0}
        f = us[:, 7]
        ancestor_mean = sum(roots[k][7]*nroot for k, nroot in counts.items()) / n
        return dict(count=n, fmean=float(f.mean()),
                    ks=a.ecdf(f, np.ones(n)/n),
                    ancestor_mean=float(ancestor_mean),
                    movement_mean=float(f.mean()-ancestor_mean),
                    root_count=len(counts), max_root_fraction=max(counts.values())/n)

    errors = {key: abs(ll - curve(v)) for key, (v, ll) in points.items()}
    strata = {}
    for tol in [1e-8, 1e-6]:
        compatible = lambda u: errors[u.tobytes()] < tol
        live_mask = np.array([compatible(u) for u in s.live_u])
        transitions = {}
        for source in [False, True]:
            for dest in [False, True]:
                selected = [(p, c) for p, c in pairs
                            if compatible(p) == source and compatible(c) == dest]
                row = {'count': len(selected)}
                if selected:
                    starts, ends = map(np.asarray, zip(*selected))
                    movement = ends-starts
                    active = np.delete(movement, 7, axis=1)
                    row.update(nuisance_rms=float(np.sqrt(np.mean(movement[:, 7]**2))),
                               active_rms=float(np.sqrt(np.mean(active**2))),
                               nuisance_mean_step=float(movement[:, 7].mean()))
                    if len(selected) > 1:
                        row['nuisance_parent_child_correlation'] = float(
                            np.corrcoef(starts[:, 7], ends[:, 7])[0, 1])
                transitions[f'{int(source)}_to_{int(dest)}'] = row
        strata[str(tol)] = dict(
            compatible_live=group_stats(s.live_u[live_mask]),
            complementary_live=group_stats(s.live_u[~live_mask]),
            transitions=transitions)
    return dict(checkpoint_sha256=hashlib.sha256(raw).hexdigest(),
                iterations=int(r.niter), accepted_traced=len(pairs),
                all_parents_and_children_accounted_for=True,
                all_live=group_stats(s.live_u), strata=strata,
                scope='Conditional diagnostic from biased archived active set; '
                      'algebraic curve compatibility is not a solver-status classification; '
                      'ancestry counts are descriptive, not statistical ESS; '
                      'no evidence or posterior estimate.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', type=int, required=True)
    args = parser.parse_args()
    folder = a.HERE / f'conditional_{args.seed}'
    result = audit(folder)
    dest = folder / f"audit_{result['iterations']}.json"
    with dest.open('x') as out:
        json.dump(result, out, indent=2)
    print(json.dumps(result, indent=2))
