"""Read-only sampling audit; writes separate audit_* results, never overwrites run outputs.
All summaries condition on dTm=0: mean meltome error is excluded and must be absorbed
by tm_scale and catalytic parameters. No likelihood evaluations or new sampling.
"""
import sys,json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import norm
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from task5_posterior import load,wq,FREE_NAMES,FREE_SPECS,HIDDEN
from prior_transform import transform_factory
BASE=HERE.parents[1]/'strains/eciML1515/outputs/calibration_configD_NLDM_recipe_P16_reduced'
allm=[];alle=[];allp=[];runs={}; saved={}; boots={}
pt=transform_factory(FREE_SPECS)
for tag in ['red1','red2']:
 print('Loading',tag,flush=True)
 s,w,u=load(tag); ll=np.load(BASE/f'logl_{tag}.npy'); summary=json.loads((BASE/f'summary_{tag}.json').read_text()); trace=json.loads((HERE/f'trace_{tag}.json').read_text())
 assert s.shape==(len(w),15) and len(ll)==len(w)
 # Independently invert the prior transform, matching stored unit-cube coordinates.
 x=np.where(pt.take_log,np.exp(s),s)
 ui=(norm.cdf((x-pt.loc)/pt.scale)-pt.Pa)/(pt.Pb-pt.Pa)
 assert np.max(np.abs(ui-u))<1e-8
 mu=np.sum(w[:,None]*u,axis=0); X=u-mu
 C=np.einsum('ni,n,nj->ij',X,w,X)/(1-np.sum(w*w)); ev,V=np.linalg.eigh(C)
 for k in range(15):
  if V[np.argmax(np.abs(V[:,k])),k]<0: V[:,k]*=-1
  ratio=np.sqrt(12*ev[k]); cl='CONSTRAINED' if ratio<.5 else ('PRIOR-DOMINATED' if ratio>.8 else 'INTERMEDIATE')
  row=dict(seed=tag,direction=k+1,eigenvalue=ev[k],width_ratio=ratio,classification=cl)
  row.update({n:V[j,k] for j,n in enumerate(FREE_NAMES)});alle.append(row)
 pd.DataFrame(C,index=FREE_NAMES,columns=FREE_NAMES).to_csv(HERE/f'audit_covariance_{tag}.csv')
 rng=np.random.default_rng(0); idx=rng.choice(len(s),size=(200,len(s)),p=w/w.sum())
 mc=np.std(np.median(s[idx],axis=1),axis=0); boots[tag]=mc
 priorq=np.array([pt(np.full(15,q)) for q in [.05,.5,.95]])
 for j,sp in enumerate(FREE_SPECS):
  natural=s[:,j] if sp.space=='add' else np.exp(s[:,j])*(sp.emergent if sp.emergent is not None else 1.)
  pq=priorq[:,j] if sp.space=='add' else np.exp(priorq[:,j])*(sp.emergent if sp.emergent is not None else 1.)
  q=[wq(natural,w,z) for z in [.05,.5,.95]]
  allm.append(dict(seed=tag,parameter=sp.name,lo5=q[0],median=q[1],hi95=q[2],prior_lo5=pq[0],prior_hi95=pq[2],interval_width_ratio=(q[2]-q[0])/(pq[2]-pq[0]),cube_sd_ratio=np.sqrt(12*C[j,j]),median_sampled=wq(s[:,j],w,.5),bootstrap_mc_sampled=mc[j]))
 R=C/np.sqrt(np.outer(np.diag(C),np.diag(C)))
 for a,b,old in [('sigma','kcat_scale',-.857),('dCp_scale','dTopt',-.853),('kappa_scale','tm_scale',.804)]:
  i,j=FREE_NAMES.index(a),FREE_NAMES.index(b); pair=C[np.ix_([i,j],[i,j])]; pe,pv=np.linalg.eigh(pair)
  k=int(np.argmax(np.abs(V[i])+np.abs(V[j])))
  allp.append(dict(seed=tag,pair=a+'~'+b,P15_correlation=old,weighted_correlation=R[i,j],unweighted_correlation=np.corrcoef(u[:,i],u[:,j])[0,1],narrow_pair_width=np.sqrt(12*pe[0]),broad_pair_width=np.sqrt(12*pe[1]),dominant_global_direction=k+1,global_width_ratio=np.sqrt(12*ev[k]),first_marginal_width=np.sqrt(12*C[i,i]),second_marginal_width=np.sqrt(12*C[j,j])))
 ti=FREE_NAMES.index('tm_scale'); tm=np.exp(s[:,ti]); near=float(w[tm>=.95*2.2].sum())
 runs[tag]=dict(summary=summary,actual_final_dlogz=trace[-1]['dlogz'],weight_sum=float(np.exp(np.load(BASE/f'logwt_{tag}.npy')-summary['logz']).sum()),n_eff_check=float(1/np.sum(w*w)),inverse_transform_max_error=float(np.max(abs(ui-u))),best_logl=float(ll.max()),tm_q=[wq(tm,w,q) for q in [.05,.5,.95]],tm_prior=[.4,2.2],tm_mass_near_upper=near,counts=pd.Series([r['classification'] for r in alle if r['seed']==tag]).value_counts().to_dict())
 saved[tag]=(s,w,u)
 print(tag,runs[tag]['counts'],'tm',runs[tag]['tm_q'],flush=True)
M=pd.DataFrame(allm);E=pd.DataFrame(alle);P=pd.DataFrame(allp)
M.to_csv(HERE/'audit_marginals.csv',index=False);E.to_csv(HERE/'audit_eigendecomposition.csv',index=False);P.to_csv(HERE/'audit_pairs.csv',index=False)
A=M[M.seed=='red1'].set_index('parameter');B=M[M.seed=='red2'].set_index('parameter');ag=[]
for n in FREE_NAMES:
 err=np.hypot(A.loc[n,'bootstrap_mc_sampled'],B.loc[n,'bootstrap_mc_sampled']);diff=B.loc[n,'median_sampled']-A.loc[n,'median_sampled']
 ag.append(dict(parameter=n,median_seed1=A.loc[n,'median'],median_seed2=B.loc[n,'median'],difference_sampled=diff,combined_bootstrap_mc=err,mc_errors=abs(diff)/err,passes=bool(abs(diff)<=2*err)))
AG=pd.DataFrame(ag);AG.to_csv(HERE/'audit_agreement.csv',index=False)
z1=runs['red1']['summary'];z2=runs['red2']['summary']; dz=abs(z1['logz']-z2['logz']);ze=np.hypot(z1['logzerr'],z2['logzerr'])
result=dict(hidden_uncertainty=HIDDEN,runs=runs,agreement=dict(logz_difference=dz,combined_logz_error=ze,logz_sigma=dz/ze,evidence_pass=bool(dz<=ze),median_failures=AG.loc[~AG.passes,'parameter'].tolist(),agreed=bool(dz<=ze and AG.passes.all())),mc_method='Existing P16 recipe: 200 iid weighted resamples, each of length equal to stored nested sample count, seed 0. This is resampling error conditional on saved weights, not full nested-sampling uncertainty.')
(HERE/'audit_summary.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result['agreement'],indent=2));print(AG.to_string(index=False));print(P.to_string(index=False))
# Tail shifts use the previously recorded mean-to-quantile distances; no model build.
tail_reference=pd.read_csv(HERE/'task5_tail.csv'); tails=[]
for seed,r in runs.items():
 lo,m,hi=r['tm_q']
 for _,v in tail_reference.iterrows():
  d=v.delta_below_mean_K
  tails.append(dict(seed=seed,percentile=int(v.percentile),median_shift_K=-(m-1)*d,lo5_shift_K=-(hi-1)*d,hi95_shift_K=-(lo-1)*d))
pd.DataFrame(tails).to_csv(HERE/'audit_tail.csv',index=False)
