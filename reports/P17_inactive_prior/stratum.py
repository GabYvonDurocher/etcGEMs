"""Algebraic diagnostic of the unchanged zero-growth/no-respiration likelihood."""
import independent_audit as a
from premise import cm,PAYLOAD
import numpy as np,json
from scipy.optimize import minimize_scalar
from scipy.special import logsumexp
_,og,sg,_,_,_=cm.load_respirometry(PAYLOAD['strain'],PAYLOAD['table'],PAYLOAD['otu'])
def zero_curve(d):
    var=sg**2+np.asarray(d)[...,None]**2
    return -.5*np.sum(og**2/var+np.log(2*np.pi*var),axis=-1)
j=a.reduced.FREE_NAMES.index('disc_growth');sp=a.reduced.FREE_SPECS[j]
opt=minimize_scalar(lambda d:-float(zero_curve(d)),bounds=(sp.lo,sp.hi),method='bounded',options={'xatol':1e-12})
out=dict(curve_max=float(-opt.fun),disc_growth_at_max=float(opt.x),scope='Algebraic compatibility only; not solver-status classification',runs={})
for tag in ['red1','red2']:
    s=a.dynesty.NestedSampler.restore(str(a.BASE/f'dynesty_{tag}.save'));s.add_final_live(print_progress=False);r=s.results
    w=np.exp(r.logwt-logsumexp(r.logwt));curve=zero_curve(np.exp(r.samples[:,j]));error=abs(r.logl-curve);f=r.samples_u[:,7];rows=[]
    for tol in [1e-12,1e-8,1e-4]:
        m=error<tol;rows.append(dict(tol=tol,count=int(m.sum()),weight=float(w[m].sum()),fmean=float(w[m]@f[m]/w[m].sum())))
    hist=[]
    for it in range(0,r.niter+1,400):
        ix=np.array([np.flatnonzero((r.samples_id==k)&(np.arange(len(r.logl))>=it))[0] for k in range(800)])
        m=error[ix]<1e-8
        hist.append(dict(iteration=it,cut=float(r.logl[max(it-1,0)]),compatible_count=int(m.sum()),compatible_fmean=float(f[ix][m].mean()) if m.any() else None,other_fmean=float(f[ix][~m].mean()) if (~m).any() else None,median_index=int(ix[np.argsort(r.logl[ix])[400]])))
    out['runs'][tag]=dict(tolerances=rows,live_history=hist)
    print(tag,rows,flush=True)
(a.HERE/'stratum.json').write_text(json.dumps(out,indent=2));print('Maximum',out['curve_max'],out['disc_growth_at_max'])
