"""D37 fixed-cut real-likelihood chains with an appended inactive Beta(3,1)."""
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

FOLDER = a.HERE/'beta_path_chains'
PT15 = a.transform_factory(a.reduced.FREE_SPECS)


def transform(u):
    return np.r_[PT15(u[:15]), u[15]**(1/3)]


def prepare():
    sys.modules['__main__'].ParentSlice = ParentSlice
    _, obs, err, _, _, _ = p.cm.load_respirometry(p.PAYLOAD['strain'], p.PAYLOAD['table'], p.PAYLOAD['otu'])
    j = a.reduced.FREE_NAMES.index('disc_growth')
    plans = []
    for seed, source, iteration in [(17821,17511,2000), (17822,17512,2000), (17823,17513,2397)]:
        raw = (a.HERE/f'conditional_{source}/audit_checkpoint_{iteration}.save').read_bytes()
        s = pickle.loads(raw)['sampler']
        assert s.results.niter == iteration
        var = np.asarray(err)**2+np.exp(2*s.live_v[:, j, None])
        curve = -.5*np.sum(np.asarray(obs)**2/var+np.log(2*np.pi*var), axis=1)
        group = np.flatnonzero(abs(s.live_logl-curve)>=1e-6)
        index = int(group[np.argsort(s.live_logl[group])[len(group)//2]])
        rng = np.random.default_rng(seed)
        original = s.bound.get_random_axes(rng)
        local = np.linalg.cholesky(np.cov(s.live_u[group], rowvar=False))
        local *= np.linalg.norm(original)/np.linalg.norm(local)
        axes = {}
        for label, base in [('original',original), ('local',local)]:
            value = np.zeros((16,16)); value[:15,:15] = base
            value[15,15] = np.linalg.norm(original)/np.sqrt(15)
            axes[label] = value.tolist()
        parent = np.r_[s.live_u[index],rng.random()]
        plans.append(dict(seed=seed, source=source, iteration=iteration, parent=parent.tolist(),
                          parent_logl=float(s.live_logl[index]), cut=float(s.live_logl.min()),
                          scale=float(s.internal_sampler.scale), axes=axes,
                          rng_state=copy.deepcopy(rng.bit_generator.state),
                          source_sha256=hashlib.sha256(raw).hexdigest()))
    return plans


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--prepare-only', action='store_true'); args=ap.parse_args()
    FOLDER.mkdir(exist_ok=True)
    plans = prepare()
    if (FOLDER/'plan.json').exists():
        assert json.loads((FOLDER/'plan.json').read_text()) == plans
    else:
        (FOLDER/'plan.json').write_text(json.dumps(plans,indent=2))
    if args.prepare_only:
        print('Six paired real-path chains prepared; no model solves.'); return
    with (FOLDER/'status.json').open('x') as out:
        json.dump({'status':'running'},out)
    batch_start = time.monotonic()
    def expiry(*unused):
        raise TimeoutError('D37 enforced chain/batch deadline')
    signal.signal(signal.SIGALRM,expiry)
    summary = []
    try:
        for plan in plans:
            for kind in ['original','local']:
                remaining = 10800-(time.monotonic()-batch_start)
                if remaining<=0: raise TimeoutError('D37 total deadline')
                signal.alarm(max(1,int(min(1800,remaining))))
                folder = FOLDER/f'{plan["seed"]}_{kind}'; folder.mkdir(exist_ok=False)
                started=time.monotonic(); calls=0
                p.cm._gwinit(dict(p.PAYLOAD,solver='gurobi')); p.gasflux.flux_tpc=p.flux
                def ll(theta):
                    nonlocal calls
                    if calls>=1000: raise RuntimeError('D37 chain call cap')
                    calls+=1; p.capture.clear()
                    return p.loglike15(np.asarray(theta[:15]))
                u=np.array(plan['parent']); value=ll(transform(u))
                if abs(value-plan['parent_logl'])>1e-6 or value<=plan['cut']:
                    raise RuntimeError('D37 parent repeatability/order failure')
                rng=np.random.default_rng(); rng.bit_generator.state=copy.deepcopy(plan['rng_state'])
                states=[u.copy()]; values=[float(value)]; counts=[calls]; verified=[]
                for step in range(1,33):
                    ret=RSliceSampler.sample(SimpleNamespace(u=u.copy(),loglstar=plan['cut'],
                        axes=np.array(plan['axes'][kind]),scale=plan['scale'],prior_transform=transform,
                        loglikelihood=ll,rseed=rng,kwargs={'slices':3,'nonbounded':None,'periodic':None,'reflective':None}))
                    u=np.asarray(ret.u); value=float(ret.logl)
                    states.append(u.copy()); values.append(value); counts.append(calls)
                    np.savez_compressed(folder/'trace.npz',u=np.asarray(states),logl=values,calls=counts)
                    if step%8==0:
                        again=ll(transform(u))
                        checked=dict(step=step,reported_logl=value,rechecked_logl=again,
                                     flux=p.capture.get('flux',{}))
                        verified.append(checked); (folder/'verified.json').write_text(json.dumps(verified,indent=2))
                        if abs(again-value)>1e-6: raise RuntimeError('D37 endpoint repeatability failure')
                        print(json.dumps(dict(seed=plan['seed'],kind=kind,step=step,calls=calls,
                            wall_s=time.monotonic()-started,beta_cdf=float(u[15]))),flush=True)
                trace=np.asarray(states); samples=trace[1:]; weights=np.ones(32)/32
                row=dict(seed=plan['seed'],kind=kind,steps=32,calls=calls,wall_s=time.monotonic()-started,
                         beta_cdf_mean=float(samples[:,15].mean()),beta_cdf_ks=a.ecdf(samples[:,15],weights),
                         beta_cdf_range=[float(samples[:,15].min()),float(samples[:,15].max())],
                         original_inactive_mean=float(samples[:,7].mean()),original_inactive_ks=a.ecdf(samples[:,7],weights),
                         beta_lag1=float(np.corrcoef(trace[:-1,15],trace[1:,15])[0,1]),
                         coordinate_rms_step=dict(zip(a.reduced.FREE_NAMES+['beta_cdf'],np.sqrt(np.mean(np.diff(trace,axis=0)**2,axis=0)).tolist())),
                         scope='32 correlated transitions from biased active parent; no burn-in removal, IID significance, or posterior certification.')
                (folder/'result.json').write_text(json.dumps(row,indent=2)); summary.append(row)
                (FOLDER/'summary.json').write_text(json.dumps(summary,indent=2)); signal.alarm(0)
        status=dict(status='completed six chains',wall_s=time.monotonic()-batch_start)
    except Exception as error:
        status=dict(status='stopped for review',error=repr(error),wall_s=time.monotonic()-batch_start)
        (FOLDER/'status.json').write_text(json.dumps(status,indent=2)); raise
    finally:
        signal.alarm(0)
    (FOLDER/'status.json').write_text(json.dumps(status,indent=2))


if __name__=='__main__': main()
