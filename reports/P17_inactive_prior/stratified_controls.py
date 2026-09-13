"""D48 exact conditional-prior partition and evidence recombination."""
import argparse
import json
import signal
import time
import warnings
import numpy as np
from scipy.special import logsumexp
import controls as c

HERE=c.HERE/'stratified_controls'
METHOD='rslice'
KIND='spike'
class Prior:
    def __init__(self,core):self.core=core
    def __call__(self,u):
        x=np.array(u,copy=True)
        if self.core:x[0]=.197+.006*u[0]
        else:
            v=.994*u[0];x[0]=v if v<.197 else v+.006
        return x

def run(seed):
    folder=HERE/str(seed);folder.mkdir(exist_ok=False);start=time.monotonic();parts=[]
    for core,stream in zip([True,False],np.random.SeedSequence(seed).spawn(2)):
        signal.alarm(180)
        sampler=c.dynesty.NestedSampler(c.Target(KIND),Prior(core),15,nlive=400,
            bound='multi',sample=METHOD,**({'slices':3} if METHOD=='rslice' else {}),first_update={'min_eff':30},rstate=np.random.default_rng(stream))
        checkpoint=folder/f'{core}.save';sampler.save(str(checkpoint))
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            sampler.run_nested(dlogz=.1,print_progress=False,checkpoint_file=str(checkpoint),checkpoint_every=30)
        r=sampler.results;volume=.006 if core else .994
        np.savez_compressed(folder/f'{core}.npz',u=r.samples,logwt=r.logwt,logl=r.logl)
        parts.append(dict(u=r.samples,logwt=r.logwt+np.log(volume),logz=float(r.logz[-1]),
                          logzerr=float(r.logzerr[-1]),core=core,volume=volume,ncall=int(sampler.ncall)))
        signal.alarm(0)
    u=np.concatenate([p['u'] for p in parts]);logwt=np.concatenate([p['logwt'] for p in parts]);logz=float(logsumexp(logwt));w=np.exp(logwt-logz)
    active=[c.ecdf(c.active_cdf(u[:,j],KIND) if j==0 else c.active_cdf(u[:,j],'smooth'),w) for j in range(15) if j!=7]
    row=dict(seed=seed,kind=KIND,logz=logz,truth_logz=float(c.truth(KIND)),logz_error=logz-c.truth(KIND),
        region_mass=float(w[u[:,0]<.5].sum()),truth_region_mass=float(c.active_cdf(.5,KIND)),
        inactive_ks=c.ecdf(u[:,7],w),all_active_ks=active,max_active_ks=max(active),wall_s=time.monotonic()-start,
        parts=[{k:v for k,v in p.items() if k not in ['u','logwt']} for p in parts])
    np.savez_compressed(folder/'combined.npz',u=u,logwt=logwt)
    (folder/'result.json').write_text(json.dumps(row,indent=2));print(json.dumps(row),flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--benchmark',action='store_true');parser.add_argument('--uniform',action='store_true');args=parser.parse_args()
    if args.uniform:METHOD='unif';HERE=c.HERE/'stratified_uniform'
    HERE.mkdir(exist_ok=True)
    def expired(*unused):raise TimeoutError('D48 per-stratum deadline; checkpoint retained')
    signal.signal(signal.SIGALRM,expired)
    grid=(np.arange(10000)+.5)/10000
    for core in [True,False]:
        transformed=np.array([Prior(core)(np.r_[v,np.zeros(14)])[0] for v in grid])
        assert np.all((abs(transformed-.2)<.003)==core)
    assert np.isclose(np.exp(logsumexp(np.log([.006,.994]))),1.)
    (HERE/'transform_check.json').write_text(json.dumps(dict(grid_per_region=10000,volumes=[.006,.994],passed=True)))
    if not args.benchmark:assert json.loads((HERE/'17751/result.json').read_text())['wall_s']<360
    start=time.monotonic()
    for seed in ([17751] if args.benchmark else [17752,17753,17754,17755]):
        if time.monotonic()-start>=1440:raise TimeoutError('D48 batch budget leaves no room for another pair')
        run(seed)
