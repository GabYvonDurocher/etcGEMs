"""D39 frozen imperfect-pilot proposal, known-target nested controls."""
import argparse
import hashlib
import json
import signal
import time
import warnings
import numpy as np
from scipy.special import logsumexp
import controls as c
from independence_kernel import IndependenceSampler

HERE=c.HERE/'independence_controls'
TRACE=False


def pilot(kind):
    source=c.HERE/f'{kind}_plain_p1_t0_s3_17001.npz'
    data=np.load(source); u=data['u']; w=np.exp(data['logwt']-logsumexp(data['logwt']))
    masks=[np.ones(len(u),dtype=bool)] if kind=='smooth' else [abs(u[:,0]-.2)<.003,abs(u[:,0]-.2)>=.003]
    means=[]; covariances=[]
    for mask in masks:
        v=u[mask]; weights=w[mask]/w[mask].sum(); mean=weights@v
        delta=v-mean; covariance=(delta*weights[:,None]).T@delta
        np.linalg.cholesky(covariance)  # No ridge or fit tuning.
        means.append(mean.tolist());covariances.append(covariance.tolist())
    result=dict(means=means,covariances=covariances,uniform_weight=.1)
    dest=HERE/f'{kind}_pilot.json'
    record=dict(mixture=result,source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                scope='Frozen weighted baseline17001 fit; not true target component parameters.')
    if dest.exists():assert json.loads(dest.read_text())==record
    else:dest.write_text(json.dumps(record,indent=2))
    return result


def run(kind,seed):
    folder=HERE/f'{kind}_{seed}';folder.mkdir(exist_ok=False);start=time.monotonic()
    s=c.dynesty.NestedSampler(c.Target(kind),c.identity,15,nlive=800,bound='multi',
        sample=IndependenceSampler(mixture=pilot(kind),steps=32,ndim=15),
        first_update={'min_eff':30},rstate=np.random.default_rng(seed))
    s.save(str(folder/'checkpoint.save'))
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        s.run_nested(dlogz=.1,print_progress=False,checkpoint_file=str(folder/'checkpoint.save'),checkpoint_every=30)
    r=s.results; w=np.exp(r.logwt-logsumexp(r.logwt));u=r.samples_u
    stats=[st for st in r.proposal_stats if st and 'accepted' in st]
    if TRACE:
        (folder/'proposal_trace.json').write_text(json.dumps(stats))
    row=dict(kind=kind,seed=seed,wall_s=time.monotonic()-start,steps=32,ncall=int(s.ncall),
             logz=float(r.logz[-1]),logzerr=float(r.logzerr[-1]),truth_logz=float(c.truth(kind)),
             nuisance_ks=c.ecdf(u[:,7],w),nuisance_mean=float(w@u[:,7]),
             active_ks=c.ecdf(c.active_cdf(u[:,0],kind),w),region_mass=float(w[u[:,0]<.5].sum()),
             truth_region_mass=float(c.active_cdf(.5,kind)),
             stalled_fraction=float(np.mean([st['accepted']==0 for st in stats])),
             mean_accepted_per_kernel=float(np.mean([st['accepted'] for st in stats])),
             duplicate_vectors=len(u)-len(np.unique(u,axis=0)))
    np.savez_compressed(folder/'samples.npz',u=u,logwt=r.logwt,logl=r.logl)
    (folder/'result.json').write_text(json.dumps(row,indent=2));print(json.dumps(row),flush=True)


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--benchmark',action='store_true');ap.add_argument('--oracle',action='store_true');ap.add_argument('--diagonal',action='store_true');ap.add_argument('--laplace',action='store_true');ap.add_argument('--trace',action='store_true');args=ap.parse_args()
    assert sum([args.oracle,args.diagonal,args.laplace])<=1
    if args.laplace:
        HERE=c.HERE/'independence_laplace'
        def pilot(kind):
            assert kind=='spike'
            return json.loads((HERE/'fitted_proposal.json').read_text())['mixture']
    if args.diagonal:
        HERE=c.HERE/'independence_diagonal'
        def pilot(kind):
            source=c.HERE/'independence_controls'/f'{kind}_pilot.json'
            record=json.loads(source.read_text());result=record['mixture']
            result['covariances']=[np.diag(np.diag(v)).tolist() for v in result['covariances']]
            (HERE/'diagonal_proposal.json').write_text(json.dumps(dict(mixture=result,source_sha256=hashlib.sha256(source.read_bytes()).hexdigest()),indent=2))
            return result
    if args.oracle:
        HERE=c.HERE/'independence_oracle'
        def pilot(kind):
            assert kind=='spike'
            means=np.full((2,15),.5);means[:,0]=[.2,.75]
            variances=np.full((2,15),.15**2);variances[:,0]=np.square([.0005,.1]);variances[:,7]=1/12
            result=dict(means=means.tolist(),covariances=[np.diag(v).tolist() for v in variances],uniform_weight=.1)
            (HERE/'oracle_proposal.json').write_text(json.dumps(result,indent=2))
            return result
    if args.trace:
        assert not args.diagonal and not args.laplace and not args.benchmark
        TRACE=True;HERE=c.HERE/('independence_trace_oracle' if args.oracle else 'independence_trace_pilot')
        original_sample=IndependenceSampler.sample
        def traced_sample(args):
            ret=original_sample(args);q=args.kwargs['mixture']
            ret.proposal_stats.update(cut=float(args.loglstar),parent_active=float(args.u[0]),child_active=float(ret.u[0]),
                parent_inactive=float(args.u[7]),child_inactive=float(ret.u[7]),
                parent_logq=q.logpdf(args.u),child_logq=q.logpdf(ret.u))
            return ret
        IndependenceSampler.sample=staticmethod(traced_sample)
    HERE.mkdir(exist_ok=True);start=time.monotonic()
    def expiry(*unused):raise TimeoutError('D39 control deadline; checkpoint preserved')
    signal.signal(signal.SIGALRM,expiry)
    for kind in (['spike'] if args.oracle or args.diagonal or args.laplace or args.trace else ['smooth','spike']):
        for seed in ([17752] if args.trace else range(17751,17756)):
            if not args.benchmark and kind=='smooth' and seed==17751:
                assert json.loads((HERE/'smooth_17751/result.json').read_text())['wall_s']<180
                continue
            remaining=(900 if args.oracle or args.diagonal or args.laplace else 1800)-(time.monotonic()-start)
            if remaining<=0:raise TimeoutError('D39 batch deadline')
            signal.alarm(max(1,int(min(180,remaining))));run(kind,seed);signal.alarm(0)
            if args.benchmark:raise SystemExit(0)
