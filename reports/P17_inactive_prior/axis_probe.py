"""D32 paired real-path proposal geometry test; local diagnostic, not a posterior."""
import argparse
import copy
import hashlib
import json
import pickle
import signal
import sys
import time
from types import SimpleNamespace
import numpy as np
from dynesty.internal_samplers import RSliceSampler
import independent_audit as a
import premise as p
from conditional_trace import ParentSlice


def prepare(source_seed=17511, seed_start=17801):
    sys.modules['__main__'].ParentSlice = ParentSlice
    path = a.HERE/f'conditional_{source_seed}/audit_checkpoint_2000.save'
    raw = path.read_bytes()
    s = pickle.loads(raw)['sampler']
    assert s.results.niter == 2000 and not s.unit_cube_sampling
    _, obs, err, _, _, _ = p.cm.load_respirometry(p.PAYLOAD['strain'], p.PAYLOAD['table'], p.PAYLOAD['otu'])
    j = a.reduced.FREE_NAMES.index('disc_growth')
    var = np.asarray(err)**2+np.exp(2*s.live_v[:, j, None])
    curve = -.5*np.sum(np.asarray(obs)**2/var+np.log(2*np.pi*var), axis=1)
    group = np.flatnonzero(abs(s.live_logl-curve)>=1e-6)
    index = int(group[np.argsort(s.live_logl[group])[len(group)//2]])
    covariance = np.cov(s.live_u[group], rowvar=False)
    local = np.linalg.cholesky(covariance)
    assert np.allclose(local@local.T, covariance, rtol=1e-10, atol=1e-14)
    pairs = []
    for seed in range(seed_start, seed_start+3):
        rng = np.random.default_rng(seed)
        original = s.bound.get_random_axes(rng)
        axes = local*np.linalg.norm(original)/np.linalg.norm(local)
        assert np.isclose(np.linalg.norm(axes), np.linalg.norm(original), rtol=1e-12)
        pairs.append(dict(seed=seed, rng_state=copy.deepcopy(rng.bit_generator.state),
                          original_axes=original.tolist(), local_axes=axes.tolist()))
    return dict(checkpoint_sha256=hashlib.sha256(raw).hexdigest(), index=index,
                group_count=len(group), parent=s.live_u[index].tolist(),
                stored_logl=float(s.live_logl[index]), cut=float(s.live_logl.min()),
                scale=float(s.internal_sampler.scale),
                covariance_eigenvalues=np.linalg.eigvalsh(covariance).tolist(),
                kwargs=s.internal_sampler.sampler_kwargs, pairs=pairs)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--prepare-only', action='store_true')
    ap.add_argument('--source-seed', type=int, default=17511)
    ap.add_argument('--seed-start', type=int, default=17801)
    ap.add_argument('--output-name', default='axis_probe')
    args = ap.parse_args()
    folder = a.HERE/args.output_name
    folder.mkdir(exist_ok=True)
    plan = prepare(args.source_seed, args.seed_start)
    if (folder/'plan.json').exists():
        assert json.loads((folder/'plan.json').read_text()) == plan
    else:
        (folder/'plan.json').write_text(json.dumps(plan, indent=2))
    if args.prepare_only:
        print('Prepared six fixed paired proposals; no model initialisation or evaluation.')
        return
    if (folder/'status.json').exists():
        raise FileExistsError('Probe batch already attempted; preserve and review')
    (folder/'status.json').write_text(json.dumps({'status': 'running'}))
    started = time.monotonic()
    def timeout(*unused):
        raise TimeoutError('D32 enforced probe/batch deadline')
    signal.signal(signal.SIGALRM, timeout)
    pt = a.transform_factory(a.reduced.FREE_SPECS)
    _, obs, err, _, _, _ = p.cm.load_respirometry(p.PAYLOAD['strain'], p.PAYLOAD['table'], p.PAYLOAD['otu'])
    j = a.reduced.FREE_NAMES.index('disc_growth')
    u = np.array(plan['parent'])
    rows = []
    try:
        for pair in plan['pairs']:
            for kind in ['original', 'local']:
                remaining = 1800-(time.monotonic()-started)
                if remaining <= 0:
                    raise TimeoutError('D32 batch deadline')
                signal.alarm(max(1, int(min(600, remaining))))
                t = time.monotonic()
                calls = 0
                # Fresh evaluator for each side of the pair avoids asymmetric history.
                p.cm._gwinit(dict(p.PAYLOAD, solver='gurobi'))
                p.gasflux.flux_tpc = p.flux
                def ll(theta):
                    nonlocal calls
                    if calls >= 200:
                        raise RuntimeError('D32 200-call cap reached')
                    calls += 1
                    p.capture.clear()
                    return p.loglike15(theta)
                parent_ll = ll(pt(u))
                if abs(parent_ll-plan['stored_logl']) > 1e-6 or parent_ll <= plan['cut']:
                    raise RuntimeError(f'Parent reproducibility/order failed: {parent_ll} vs {plan["stored_logl"]}')
                rng = np.random.default_rng()
                rng.bit_generator.state = copy.deepcopy(pair['rng_state'])
                ret = RSliceSampler.sample(SimpleNamespace(
                    u=u.copy(), loglstar=plan['cut'], axes=np.array(pair[kind+'_axes']),
                    scale=plan['scale'], prior_transform=pt, loglikelihood=ll,
                    rseed=rng, kwargs=copy.deepcopy(plan['kwargs'])))
                endpoint_ll = ll(pt(ret.u))
                if abs(endpoint_ll-float(ret.logl)) > 1e-6:
                    raise RuntimeError('Endpoint reproducibility failed; do not report stale solver status')
                delta = ret.u-u
                flux = p.capture.get('flux', {})
                var = np.asarray(err)**2+np.exp(2*pt(ret.u)[j])
                curve = float(-.5*np.sum(np.asarray(obs)**2/var+np.log(2*np.pi*var)))
                row = dict(seed=pair['seed'], axes_kind=kind, parent_logl=parent_ll,
                           endpoint_logl=endpoint_ll, cut=plan['cut'], calls=calls,
                           wall_s=time.monotonic()-t, end=np.asarray(ret.u).tolist(),
                           displacement=dict(zip(a.reduced.FREE_NAMES, delta.tolist())),
                           nuisance_displacement=float(delta[7]),
                           active_rms=float(np.sqrt(np.mean(np.delete(delta, 7)**2))),
                           compatible_with_zero_growth_curve=abs(endpoint_ll-curve)<1e-6,
                           axes_covariance_eigenvalues=np.linalg.eigvalsh(np.array(pair[kind+'_axes'])@np.array(pair[kind+'_axes']).T).tolist(),
                           endpoint_flux=flux)
                rows.append(row)
                (folder/'results.json').write_text(json.dumps(rows, indent=2))
                print(json.dumps({k:v for k,v in row.items() if k not in ['endpoint_flux', 'displacement', 'end']}), flush=True)
                signal.alarm(0)
        status = {'status': 'completed six proposals', 'wall_s': time.monotonic()-started}
    except Exception as error:
        status = {'status': 'stopped for review', 'error': repr(error), 'wall_s': time.monotonic()-started}
        (folder/'status.json').write_text(json.dumps(status, indent=2))
        raise
    finally:
        signal.alarm(0)
    (folder/'status.json').write_text(json.dumps(status, indent=2))


if __name__ == '__main__':
    main()
