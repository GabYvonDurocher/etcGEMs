"""Known-target P17 control; all truths analytic, no metabolic model solve."""
import sys,json,time,argparse,warnings,signal
from pathlib import Path
import numpy as np
from scipy.special import ndtr,logsumexp
from scipy.stats import truncnorm
import dynesty
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
for p in ['src','reports/P16_reduced','reports/P11_nested','reports/P6_convergence']:sys.path.insert(0,str(ROOT/p))
from reduced import FREE_SPECS
from prior_transform import transform_factory
from independent_audit import cdf,ecdf
D=15;NUIS=7;ACTIVE=np.array([j for j in range(D) if j!=NUIS]);PT=transform_factory(FREE_SPECS)

def identity(u):return u
class Target:
    def __init__(self,kind,transformed=False):self.kind=kind;self.transformed=transformed
    def __call__(self,x):
        if self.transformed:
            v=np.where(PT.take_log,np.exp(x),x)
            x=(ndtr((v-PT.loc)/PT.scale)-PT.Pa)/(PT.Pb-PT.Pa)
        a=x[ACTIVE]
        if self.kind=='stratum':
            z=.15*np.sqrt(2*np.pi)*(ndtr(.5/.15)-ndtr(-.5/.15))
            if a[0]<.5:return float(-.5*((a[-1]-.5)/.15)**2-np.log(z))
            z0=.08*np.sqrt(2*np.pi)*(ndtr(.25/.08)-ndtr(-.25/.08))
            return float(np.log(.5)-.5*((a[0]-.75)/.08)**2-np.log(z0)-.5*np.sum(((a[1:]-.5)/.15)**2)-13*np.log(z))
        if self.kind=='smooth':return float(-.5*np.sum(((a-.5)/.15)**2))
        # Exact separable truncated Gaussian mixture; unequal region widths and weights.
        # First active coordinate identifies the two regions; 13 remaining active coordinates
        # have the same smooth density. Integrated component masses are 0.3 and 0.7.
        mus=np.array([.2,.75]);sig=np.array([.0005 if self.kind=='spike' else .035,.10]); mass=ndtr((1-mus)/sig)-ndtr(-mus/sig)
        lp=np.log([.3,.7])-.5*((a[0]-mus)/sig)**2-np.log(sig*np.sqrt(2*np.pi)*mass)
        return float(logsumexp(lp)-.5*np.sum(((a[1:]-.5)/.15)**2))

def truth(kind):
    if kind=='stratum':return 0.
    z1=.15*np.sqrt(2*np.pi)*(ndtr(.5/.15)-ndtr(-.5/.15))
    return 14*np.log(z1) if kind=='smooth' else 13*np.log(z1)
def active_cdf(x,kind):
    if kind=='stratum':return np.where(np.asarray(x)<.5,x,.5+.5*truncnorm.cdf(x,-.25/.08,.25/.08,loc=.75,scale=.08))
    if kind=='smooth':return truncnorm.cdf(x,-.5/.15,.5/.15,loc=.5,scale=.15)
    small=.0005 if kind=='spike' else .035
    return .3*truncnorm.cdf(x,-.2/small,.8/small,loc=.2,scale=small)+.7*truncnorm.cdf(x,-.75/.1,.25/.1,loc=.75,scale=.1)
def _run(a,seed,pool):
    label=f'{a.kind}_{a.path}_p{a.nproc}_t{int(a.transformed)}_s{a.slices}_{seed}'
    if a.bound!='multi':label+='_'+a.bound
    if a.kernel!='rslice':label+='_'+a.kernel
    from global_coordinate import GlobalCoordinate
    kernel=a.kernel if a.kernel in ['rslice','unif'] else GlobalCoordinate(ndim=D)
    t=time.monotonic();sampler=dynesty.NestedSampler(Target(a.kind,a.transformed),PT if a.transformed else identity,D,nlive=800,bound=a.bound,sample=kernel,slices=a.slices,pool=pool,queue_size=a.nproc,first_update={'min_eff':30},rstate=np.random.default_rng(seed))
    bound_update=str(sampler.bound_update_interval)
    initial=sampler.live_u.copy();checkpoint=str(HERE/(label+'.save'))
    sampler.save(checkpoint)  # safe initial state, retained if a hard deadline interrupts
    if a.path=='plain':sampler.run_nested(dlogz=.1,print_progress=False,checkpoint_file=checkpoint,checkpoint_every=min(1800,max(1,a.seconds/4)))
    else:
        prev=sampler.it
        while True:
            with warnings.catch_warnings():
                warnings.simplefilter('ignore');sampler.run_nested(maxiter=250,dlogz=.1,add_live=False,print_progress=False,checkpoint_file=checkpoint,checkpoint_every=min(1800,max(1,a.seconds/4)))
            if sampler.it==prev:break
            prev=sampler.it
        sampler.add_final_live(print_progress=False)
    r=sampler.results;w=np.exp(r.logwt-logsumexp(r.logwt));u=r.samples_u
    out=dict(label=label,bound_update_interval=bound_update,kernel=a.kernel,bound=a.bound,seed=seed,kind=a.kind,path=a.path,nproc=a.nproc,transformed=a.transformed,slices=a.slices,wall_s=time.monotonic()-t,ncall=int(sum(r.ncall)),niter=r.niter,logz=float(r.logz[-1]),logzerr=float(r.logzerr[-1]),truth_logz=float(truth(a.kind)),nuisance_mean=float(w@u[:,NUIS]),nuisance_ks=ecdf(u[:,NUIS],w),active_ks=ecdf(active_cdf(u[:,0],a.kind),w),region_mass=float(w[u[:,0]<.5].sum()),truth_region_mass=float(active_cdf(.5,a.kind)),initial_nuisance_mean=float(initial[:,NUIS].mean()))
    np.savez_compressed(HERE/(label+'.npz'),u=u,logwt=r.logwt,logl=r.logl,ids=r.samples_id,iteration=r.samples_it,initial=initial)
    (HERE/(label+'.json')).write_text(json.dumps(out,indent=2));print(json.dumps(out),flush=True)
    # Analytic runs are reproducible from compact arrays and configuration; avoid redundant pickles.
    Path(checkpoint).unlink(missing_ok=True)
def run(a,seed,pool):
    def expired(signum,frame):raise TimeoutError('P17 enforced per-run wall-clock budget reached')
    previous=signal.signal(signal.SIGALRM,expired);signal.alarm(a.seconds)
    try:return _run(a,seed,pool)
    except TimeoutError as exc:
        (HERE/f'timeout_{a.kind}_{a.kernel}_{seed}.json').write_text(json.dumps(dict(seed=seed,kind=a.kind,kernel=a.kernel,status='timed out',seconds=a.seconds,error=str(exc),checkpoint='Last safely written periodic checkpoint only; interrupted proposal not saved'),indent=2))
        raise
    finally:signal.alarm(0);signal.signal(signal.SIGALRM,previous)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--seconds',type=int,default=1800);p.add_argument('--kind',choices=['smooth','mixture','spike','stratum'],default='smooth');p.add_argument('--path',choices=['plain','chunk'],default='plain');p.add_argument('--nproc',type=int,default=1);p.add_argument('--transformed',action='store_true');p.add_argument('--kernel',choices=['rslice','global-coordinate','unif'],default='rslice');p.add_argument('--bound',choices=['multi','single'],default='multi');p.add_argument('--slices',type=int,default=3);p.add_argument('--seeds',type=int,nargs='+',default=list(range(17001,17006)));a=p.parse_args()
    if a.nproc>1:
        from multiprocessing import Pool
        with Pool(a.nproc) as pool:
            for seed in a.seeds:run(a,seed,pool)
    else:
        for seed in a.seeds:run(a,seed,None)
