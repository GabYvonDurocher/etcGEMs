"""Read-only P16 live-set reconstruction and numerical-library warning audit."""
import independent_audit as a
import numpy as np,json,hashlib,inspect
from scipy.special import logsumexp
from dynesty import bounding,internal_samplers,sampler
H=a.HERE
out={}
for tag in ['red1','red2']:
    s=a.dynesty.NestedSampler.restore(str(a.BASE/f'dynesty_{tag}.save'));s.add_final_live(print_progress=False);r=s.results
    u=r.samples_u;j=a.reduced.FREE_NAMES.index('f_metab');w=np.exp(r.logwt-logsumexp(r.logwt));ids=r.samples_id
    # Each slot's successive death records give the point occupying that slot
    # before its next replacement. Reconstruct live set before each dead iteration.
    byslot=[np.flatnonzero(ids==k) for k in range(r.nlive)];pos=np.zeros(r.nlive,dtype=int)
    rows=[]
    for it in range(r.niter+1):
        if it%800==0 or it==r.niter:
            ix=np.array([seq[pos[k]] for k,seq in enumerate(byslot)])
            live=u[ix];v=live[:,j];C=np.cov(live,rowvar=False);eig=np.linalg.eigvalsh(C)
            rows.append(dict(iteration=it,min_logl=float(np.min(r.logl[ix])),mean=float(v.mean()),sd=float(v.std()),ks=a.ecdf(v,np.ones(len(v))/len(v)),min_eigen=float(eig[0]),max_eigen=float(eig[-1]),unique_coordinates=len(np.unique(v))))
        if it<r.niter:pos[ids[it]]+=1
    masses=np.bincount(ids,weights=w,minlength=r.nlive)
    out[tag]=dict(live_history=rows,posterior_mean=float(w@u[:,j]),slot_mass_max=float(masses.max()),slot_mass_ess=float(1/(masses@masses)),caveat='Slot IDs are replacement strands, not proposal-parent genealogy. Slot-mass ESS does not measure independent posterior information.')
    print(tag,[(d['iteration'],round(d['mean'],3),round(d['ks'],3)) for d in rows],flush=True)
(H/'drift.json').write_text(json.dumps(out,indent=2))
versions={}
for mod in [bounding,internal_samplers,sampler]:
    p=a.Path(mod.__file__);versions[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
(H/'installed_source_hashes.json').write_text(json.dumps(versions,indent=2))
# Well-conditioned covariance stress: warning flags versus actual numerical error.
import warnings
rng=np.random.default_rng(17101);tests=[]
for k in range(100):
    X=rng.random((800,15));C=np.cov(X,rowvar=False)
    with warnings.catch_warnings(record=True) as msgs:
        warnings.simplefilter('always'); good,c,inv,axes=bounding.improve_covar_mat(C)
    tests.append(dict(seed_index=k,warnings=[str(m.message) for m in msgs],inverse_residual=float(np.max(abs(C@inv-np.eye(15)))),axes_residual=float(np.max(abs(axes@axes.T-C))),condition=float(np.linalg.cond(C))))
(H/'bounding_numeric_checks.json').write_text(json.dumps(tests,indent=2))
print('numerical checks',len(tests),'warnings',sum(len(x['warnings']) for x in tests),'worst residual',max(x['inverse_residual'] for x in tests))
