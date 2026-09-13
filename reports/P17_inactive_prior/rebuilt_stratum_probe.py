"""Newly rebuilt local-bound diagnostic; NOT recovered historical geometry."""
import independent_audit as a
import premise as p
import numpy as np,json,time
from types import SimpleNamespace
from dynesty.internal_samplers import RSliceSampler
from dynesty.bounding import MultiEllipsoid

def main():
    start=time.monotonic();p.cm._gwinit(dict(p.PAYLOAD,solver='gurobi'));p.gasflux.flux_tpc=p.flux
    _,og,sg,_,_,_=p.cm.load_respirometry(p.PAYLOAD['strain'],p.PAYLOAD['table'],p.PAYLOAD['otu'])
    pt=a.transform_factory(a.reduced.FREE_SPECS);rows=[];j=a.reduced.FREE_NAMES.index('disc_growth')
    for tag,it in [('red1',8000),('red2',8800)]:
        s=a.dynesty.NestedSampler.restore(str(a.BASE/f'dynesty_{tag}.save'));s.add_final_live(print_progress=False);r=s.results
        ix=np.array([np.flatnonzero((r.samples_id==k)&(np.arange(len(r.logl))>=it))[0] for k in range(800)])
        var=sg**2+np.exp(2*r.samples[ix,j,None]);curve=-.5*np.sum(og**2/var+np.log(2*np.pi*var),axis=1)
        group=ix[abs(r.logl[ix]-curve)<1e-8];chosen=int(group[np.argsort(r.logl[group])[len(group)//2]])
        for seed in [17201,17202,17203]:
            if time.monotonic()-start>1800:return
            rng=np.random.default_rng(seed);u=r.samples_u[chosen].copy();u[7]=rng.random();bound=MultiEllipsoid(15);bound.update(r.samples_u[ix],rstate=np.random.default_rng(17400+it),bootstrap=s.bound_bootstrap);bound.scale_to_logvol(bound.logvol+np.log(s.bound_enlarge));containment=int(sum(bound.contains(z) for z in r.samples_u[ix]));assert containment==800,containment;axes=bound.get_random_axes(rng);scale=float(r.scale[it]);cut=float(r.logl[it-1]);t=time.monotonic();calls=0
            def ll(theta):
                nonlocal calls
                if calls>=200 or time.monotonic()-t>600 or time.monotonic()-start>1800:raise RuntimeError('Stratum probe budget exceeded')
                calls+=1;return p.loglike15(theta)
            initial=ll(pt(u));initial_flux=p.capture['flux'];assert initial>cut
            record=dict(bound_source='New bound fitted to reconstructed live set; historical bound snapshots unavailable',live_containment=containment,tag=tag,iteration=it,seed=seed,stored_index=chosen,group_count=len(group),cut=cut,initial_logl=initial,stored_logl=float(r.logl[chosen]),initial_flux=initial_flux,start=u.tolist(),scale=scale,axes_row_norm=np.linalg.norm(axes,axis=1).tolist())
            try:
                args=SimpleNamespace(u=u,loglstar=cut,axes=axes,scale=scale,prior_transform=pt,loglikelihood=ll,rseed=rng,kwargs={'slices':3})
                ret=RSliceSampler.sample(args);record.update(end=ret.u.tolist(),logl=float(ret.logl),nuisance_displacement=float(ret.u[7]-u[7]),active_rms=float(np.sqrt(np.mean(np.delete(ret.u-u,7)**2))),status='complete')
            except Exception as exc:record.update(status='failed',error=repr(exc))
            record.update(calls=calls,wall_s=time.monotonic()-t);rows.append(record);(a.HERE/'rebuilt_stratum_probe.json').write_text(json.dumps(rows,indent=2));print(json.dumps({k:v for k,v in record.items() if k not in ['initial_flux','axes_row_norm','start','end']}),flush=True)
if __name__=='__main__':main()
