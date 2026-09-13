"""Supplementary strand bootstrap; does not replace P16's specified agreement recipe.
All diagnostics condition on dTm=0 and an exact measured meltome mean.
No model evaluation; original samples/checkpoints remain unchanged.
"""
import sys,json
from pathlib import Path
import numpy as np,pandas as pd,dynesty
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from task5_posterior import FREE_NAMES,wq,HIDDEN
BASE=HERE.parents[1]/'strains/eciML1515/outputs/calibration_configD_NLDM_recipe_P16_reduced'
meds={}; errs={};rows=[]; null=[]
for tag in ['red1','red2']:
 sm=dynesty.NestedSampler.restore(str(BASE/f'dynesty_{tag}.save'));s=np.load(BASE/f'samples_{tag}.npy')
 if len(sm.results.samples)<len(s):sm.add_final_live(print_progress=False)
 r=sm.results;assert np.max(abs(r.samples-s))<1e-9
 rng=np.random.default_rng(91602); q=[]; zs=[]
 for b in range(100):
  br=dynesty.utils.resample_run(r,rstate=rng);w=np.exp(br.logwt-br.logwt.max());w/=w.sum()
  q.append([wq(br.samples[:,j],w,.5) for j in range(15)]);zs.append(br.logz[-1])
 errs[tag]=np.std(q,axis=0,ddof=1)
 w=np.exp(r.logwt-r.logwt.max());w/=w.sum();meds[tag]=np.array([wq(s[:,j],w,.5) for j in range(15)])
 j=FREE_NAMES.index('f_metab');u=r.samples_u[:,j];order=np.argsort(u);cu=np.cumsum(w[order]);ks=max(np.max(abs(cu-u[order])),np.max(abs(cu-w[order]-u[order])))
 null.append(dict(seed=tag,f_metab_unit_mean=float(w@u),expected_mean=.5,f_metab_unit_sd=float(np.sqrt(np.sum(w*(u-np.sum(w*u))**2))),expected_sd=float(1/np.sqrt(12)),weighted_KS_to_uniform=float(ks),logz_strand_sd=float(np.std(zs,ddof=1))))
 print(tag,'strand bootstrap done',flush=True)
for j,n in enumerate(FREE_NAMES):
 e=np.hypot(errs['red1'][j],errs['red2'][j]);d=abs(meds['red1'][j]-meds['red2'][j]);rows.append(dict(parameter=n,combined_strand_mc=e,mc_errors=d/e,passes=bool(d<=2*e)))
pd.DataFrame(rows).to_csv(HERE/'audit_strand_agreement.csv',index=False);pd.DataFrame(null).to_csv(HERE/'audit_inactive_parameter.csv',index=False)
print(pd.DataFrame(rows).to_string(index=False));print(pd.DataFrame(null).to_string(index=False))
