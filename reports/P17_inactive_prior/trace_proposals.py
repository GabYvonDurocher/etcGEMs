"""Instrument original dynesty rslice in-process, without changing its outputs."""
import controls as c
from dynesty.internal_samplers import RSliceSampler
import numpy as np,json,time,argparse
from scipy.special import logsumexp
TRACE=[]
class TracedSlice(RSliceSampler):
    @staticmethod
    def sample(args):
        r=RSliceSampler.sample(args)
        TRACE.append((np.array(args.u,copy=True),np.array(r.u,copy=True),float(args.loglstar),int(r.ncalls)))
        return r

def run(seed):
    TRACE.clear();t=time.monotonic()
    s=c.dynesty.NestedSampler(c.Target('spike'),c.identity,15,nlive=800,bound='multi',sample=TracedSlice(ndim=15,slices=3),first_update={'min_eff':30},rstate=np.random.default_rng(seed))
    initial=s.live_u.copy();s.run_nested(dlogz=.1,print_progress=False);r=s.results
    baseline=np.load(c.HERE/f'spike_plain_p1_t0_s3_{seed}.npz')
    same=np.array_equal(r.samples_u,baseline['u']) and np.array_equal(r.logl,baseline['logl'])
    assert same,'Instrumentation changed sample stream; do not interpret until reconciled'
    starts=np.array([v[0] for v in TRACE]);ends=np.array([v[1] for v in TRACE]);cut=np.array([v[2] for v in TRACE]);calls=np.array([v[3] for v in TRACE])
    w=np.exp(r.logwt-logsumexp(r.logwt));core=lambda v:abs(v[:,0]-.2)<.003
    si,ei=core(starts),core(ends)
    # Reconstruct proposal ancestry by exact cube-coordinate bytes. Unknown start
    # roots include points drawn in the initial independent uniform stage.
    root={x.tobytes():x.tobytes() for x in initial};parents={};unknown=set()
    for st,en in zip(starts,ends):
        key=st.tobytes()
        if key not in root:root[key]=key;unknown.add(key)
        root[en.tobytes()]=root[key];parents[en.tobytes()]=key
    masses={}
    for x,wt in zip(r.samples_u,w):
        key=x.tobytes();ancestor=root.get(key,key);masses[ancestor]=masses.get(ancestor,0.)+float(wt)
    ms=np.array(list(masses.values()))
    def stats(mask):
        z=(ends-starts)[mask,7]
        return dict(n=int(mask.sum()),nuisance_rms=float(np.sqrt(np.mean(z*z))) if len(z) else None,nuisance_parent_child_corr=float(np.corrcoef(starts[mask,7],ends[mask,7])[0,1]) if len(z)>1 else None)
    summary=dict(seed=seed,baseline_identical=bool(same),wall_s=time.monotonic()-t,nproposal=len(TRACE),initial_core=int(core(initial).sum()),core_entry=int((~si&ei).sum()),core_exit=int((si&~ei).sum()),core_to_core=stats(si&ei),outside_to_outside=stats(~si&~ei),unknown_start_roots=len(unknown),largest_root_weight=float(ms.max()),root_mass_ess=float(1/(ms@ms)),nuisance_ks=c.ecdf(r.samples_u[:,7],w),region_mass=float(w[r.samples_u[:,0]<.5].sum()))
    np.savez_compressed(c.HERE/f'trace_spike_{seed}.npz',start=starts,end=ends,cut=cut,calls=calls,initial=initial)
    (c.HERE/f'trace_spike_{seed}.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary),flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--seeds',type=int,nargs='+',default=[17001]);a=p.parse_args()
    for seed in a.seeds:run(seed)
