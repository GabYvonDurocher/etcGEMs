"""Bounded P17 conditional continuation; NEVER a fresh posterior/evidence estimate."""
import independent_audit as a
import premise as p
import numpy as np,json,time,signal,argparse,warnings
from multiprocessing import get_context
from dynesty.internal_samplers import RSliceSampler
from dynesty.sampler import Sampler
from test_bound_history import preserve_history,original
class ParentSlice(RSliceSampler):
    @staticmethod
    def sample(args):
        ret=RSliceSampler.sample(args)
        ret.proposal_stats.update(parent_u=np.asarray(args.u).tolist(),child_u=np.asarray(ret.u).tolist())
        return ret

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--seed',type=int,default=17511);ap.add_argument('--seconds',type=int,default=7200);ap.add_argument('--iterations',type=int,default=2500);ap.add_argument('--resume',action='store_true');args=ap.parse_args()
    summary=json.loads((a.HERE/'validate_live_set_summary.json').read_text());assert summary['ordering_validation_passed']
    inp=np.load(a.HERE/'validated_live_input.npz');u=inp['u'].copy();u[:,7]=np.random.default_rng(args.seed-10).random(800)
    pt=a.transform_factory(a.reduced.FREE_SPECS);v=np.array([pt(x) for x in u]);lookup={x['index']:x['logl'] for x in json.loads((a.HERE/'validate_live_set.json').read_text())};ll=np.array([lookup[int(i)] for i in inp['indices']])
    roots={x.tobytes():x.tobytes() for x in u};root_value={x.tobytes():float(x[7]) for x in u};unknown=set();processed=0;history=[]
    folder=a.HERE/f'conditional_{args.seed}'
    if args.resume:
        status=json.loads((folder/'status.json').read_text());assert status['status']=='timed out; last safe checkpoint preserved'
        initial=np.load(folder/'initial.npz');assert np.array_equal(initial['u'],u) and np.array_equal(initial['v'],v)
        with (folder/'status_before_resume.json').open('x') as out:json.dump(status,out,indent=2)
        history=json.loads((folder/'history.json').read_text())
        (folder/'status.json').write_text(json.dumps(dict(status='bounded continuation running',seed=args.seed)))
    else:
        folder.mkdir(exist_ok=False);np.savez_compressed(folder/'initial.npz',u=u,v=v,logl=ll)
    t=time.monotonic();s=None
    def expiry(*unused):raise TimeoutError('Conditional diagnostic hard deadline reached')
    signal.signal(signal.SIGALRM,expiry);signal.alarm(args.seconds);Sampler.update_bound_if_needed=preserve_history
    def record():
        nonlocal processed
        r=s.results
        for st in r.proposal_stats[processed:]:
            if not st or 'parent_u' not in st:continue
            parent=np.array(st['parent_u']).tobytes();child=np.array(st['child_u']).tobytes()
            if parent not in roots:roots[parent]=parent;root_value[parent]=float(st['parent_u'][7]);unknown.add(parent)
            roots[child]=roots[parent]
        processed=len(r.proposal_stats);counts={}
        for point in s.live_u:
            key=point.tobytes()
            if key not in roots:roots[key]=key;root_value[key]=float(point[7]);unknown.add(key)
            ancestor=roots[key];counts[ancestor]=counts.get(ancestor,0)+1
        ancestor_mean=sum(n*root_value[k] for k,n in counts.items())/800
        mean=float(s.live_u[:,7].mean());row=dict(iterations=int(r.niter),live_fmean=mean,live_ks=a.ecdf(s.live_u[:,7],np.ones(800)/800),ancestor_contribution=ancestor_mean,movement_contribution=mean-ancestor_mean,distinct_ancestors=len(counts),largest_ancestor_fraction=max(counts.values())/800,unknown_independent_phase_roots=len(unknown),min_logl=float(s.live_logl.min()),wall_s=time.monotonic()-t,ncall=int(s.ncall))
        history.append(row);(folder/'history.json').write_text(json.dumps(history,indent=2));np.savez_compressed(folder/'live.npz',u=s.live_u,v=s.live_v,logl=s.live_logl);print(json.dumps(row),flush=True)
    try:
        with get_context('spawn').Pool(8,initializer=p.cm._gwinit,initargs=(dict(p.PAYLOAD,solver='gurobi'),)) as pool:
            if args.resume:
                s=a.dynesty.NestedSampler.restore(str(folder/'checkpoint.save'),pool=pool)
                assert s.results.niter<args.iterations and s.nlive==800
            else:
                s=a.dynesty.NestedSampler(p.loglike15,pt,15,nlive=800,live_points=(u,v,ll),sample=ParentSlice(ndim=15,slices=3),bound='multi',pool=pool,queue_size=8,first_update={'min_ncall':0,'min_eff':101},rstate=np.random.default_rng(args.seed))
                s.update_bound_if_needed(float(ll.min()),force=True)
            assert not s.unit_cube_sampling
            s.save(str(folder/'checkpoint.save'));record()
            while s.results.niter<args.iterations:
                remaining=min(250,args.iterations-s.results.niter)
                with warnings.catch_warnings():
                    warnings.simplefilter('ignore');s.run_nested(maxiter=remaining-1,dlogz=0,add_live=False,print_progress=False,checkpoint_file=str(folder/'checkpoint.save'),checkpoint_every=600)
                s.save(str(folder/'checkpoint.save'));previous=history[-1]['iterations'];record()
                if s.results.niter==previous:raise RuntimeError('Sampler stopped before registered replacement count')
            r=s.results;np.savez_compressed(folder/'dead.npz',u=r.samples_u,logl=r.logl,ids=r.samples_id)
            (folder/'proposal_parents.json').write_text(json.dumps(list(r.proposal_stats),default=lambda x:x.tolist() if isinstance(x,np.ndarray) else float(x)))
        status='completed diagnostic iterations'
    except TimeoutError:status='timed out; last safe checkpoint preserved'
    finally:signal.alarm(0);Sampler.update_bound_if_needed=original
    (folder/'status.json').write_text(json.dumps(dict(status=status,wall_s=time.monotonic()-t,seed=args.seed,resumed=args.resume,scope='Conditional diagnostic from biased archived active set, not a posterior or evidence estimate'),indent=2))
if __name__=='__main__':main()
