"""Bounded local diagnostic from archived geometry, never a new posterior run."""
import independent_audit as a
import premise as p
import numpy as np,json,time
from types import SimpleNamespace
from dynesty.internal_samplers import RSliceSampler

def main():
    batch_start=time.monotonic()
    s=a.dynesty.NestedSampler.restore(str(a.BASE/'dynesty_red1.save'));s.add_final_live(print_progress=False);r=s.results
    p.cm._gwinit(dict(p.PAYLOAD,solver='gurobi'));pt=a.transform_factory(a.reduced.FREE_SPECS)
    rows=[]
    for it in [4800,9600]:
        indices=np.array([np.flatnonzero((r.samples_id==j)&(np.arange(len(r.logl))>=it))[0] for j in range(800)])
        # Prespecified maximum-likelihood live point, not a posterior representative.
        ix=indices[np.argmax(r.logl[indices])];cut=float(r.logl[it-1]);bound=r.bound[r.bound_iter[it]]
        for seed in [17201,17202,17203]:
            if time.monotonic()-batch_start>1800:return
            rng=np.random.default_rng(seed);u=r.samples_u[ix].copy();u[7]=rng.random()
            axes=bound.get_random_axes(rng);scale=float(r.scale[it]);t=time.monotonic();calls=0
            def ll(theta):
                nonlocal calls
                if calls>=200 or time.monotonic()-t>600 or time.monotonic()-batch_start>1800:raise RuntimeError('Probe diagnostic budget exceeded; no sample accepted')
                calls+=1;return p.loglike15(theta)
            initial=ll(pt(u));assert initial>cut,(initial,cut)
            record=dict(iteration=it,seed=seed,stored_index=int(ix),cut=cut,initial_logl=initial,stored_logl=float(r.logl[ix]),start=u.tolist(),scale=scale,axes_row_norm=np.linalg.norm(axes,axis=1).tolist(),scope='Reconstructed historical bound and scale, current rslice3 with default stepping-out. Not an exact historical RNG replay or an unbiased posterior.')
            try:
                args=SimpleNamespace(u=u,loglstar=cut,axes=axes,scale=scale,prior_transform=pt,loglikelihood=ll,rseed=rng,kwargs={'slices':3})
                ret=RSliceSampler.sample(args);record.update(end=ret.u.tolist(),logl=float(ret.logl),nuisance_displacement=float(ret.u[7]-u[7]),active_rms=float(np.sqrt(np.mean(np.delete(ret.u-u,7)**2))),status='complete')
            except Exception as exc:record.update(status='failed',error=repr(exc))
            record.update(calls=calls,wall_s=time.monotonic()-t);rows.append(record)
            (a.HERE/'real_kernel_probe.json').write_text(json.dumps(rows,indent=2));print(json.dumps(record),flush=True)
if __name__=='__main__':main()
