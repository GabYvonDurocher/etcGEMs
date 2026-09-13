"""Check original bounds along a proven inactive prior direction, without solves."""
import independent_audit as a
import numpy as np,json
out=[]
for tag in ['red1','red2']:
    s=a.dynesty.NestedSampler.restore(str(a.BASE/f'dynesty_{tag}.save'));s.add_final_live(print_progress=False);r=s.results
    for it in [4800,8000,9600]:
        ix=np.array([np.flatnonzero((r.samples_id==k)&(np.arange(len(r.logl))>=it))[0] for k in range(800)])
        b=r.bound[r.bound_iter[it]];u=r.samples_u[ix].copy();coverage=[]
        for v in [0.,.25,.5,.75,1.]:
            test=u.copy();test[:,7]=v;coverage.append([bool(b.contains(x)) for x in test])
        mask=np.array(coverage);row=dict(tag=tag,iteration=it,f_cdf=[0,.25,.5,.75,1],fraction_in_bound=mask.mean(axis=1).tolist(),fraction_all_five_in_bound=float(mask.all(axis=0).mean()),actual_live_containment=float(np.mean([b.contains(x) for x in u])))
        out.append(row);print(json.dumps(row),flush=True)
(a.HERE/'bound_coverage.json').write_text(json.dumps(out,indent=2))
