"""P17 independent reconstruction; no imports from P16 audit/posterior helpers."""
import sys, json, hashlib, platform, importlib.metadata as md
from pathlib import Path
import numpy as np
from scipy.special import logsumexp
from scipy.stats import truncnorm
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[1]
for p in ['src','reports/P16_reduced','reports/P11_nested','reports/P6_convergence']:
    sys.path.insert(0,str(ROOT/p))
import reduced
from prior_transform import transform_factory
import dynesty
BASE=ROOT/'strains/eciML1515/outputs/calibration_configD_NLDM_recipe_P16_reduced'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def cdf(samples):
    out=np.empty_like(samples)
    for j,s in enumerate(reduced.FREE_SPECS):
        if s.prior=='normal': x=samples[:,j]; lo,hi,mu,sd=s.lo,s.hi,s.loc,s.scale
        elif s.prior=='lognormal': x=samples[:,j];lo,hi,mu,sd=np.log(s.lo),np.log(s.hi),s.log_center,s.scale
        else: x=np.exp(samples[:,j]);lo,hi,mu,sd=s.lo,s.hi,0.,s.scale
        out[:,j]=truncnorm.cdf(x,(lo-mu)/sd,(hi-mu)/sd,loc=mu,scale=sd)
    return out

def ecdf(x,w):
    ii=np.argsort(x); xs=x[ii]; cs=np.cumsum(w[ii])
    return float(max(np.max(cs-xs),np.max(xs-(cs-w[ii]))))

if __name__=='__main__':
    manifest={};result={};saved={}
    for tag in ['red1','red2']:
        for p in list(BASE.glob('*'+tag+'*'))+[ROOT/f'reports/P16_reduced/trace_{tag}.json']:
            manifest[str(p.relative_to(ROOT))]=sha(p)
        s=np.load(BASE/f'samples_{tag}.npy');lw=np.load(BASE/f'logwt_{tag}.npy');ll=np.load(BASE/f'logl_{tag}.npy')
        w=np.exp(lw-logsumexp(lw));u=cdf(s)
        checkpoint=dynesty.NestedSampler.restore(str(BASE/f'dynesty_{tag}.save'))
        before=len(checkpoint.results.samples);checkpoint.add_final_live(print_progress=False);r=checkpoint.results
        assert before+r.nlive==len(s)
        assert np.array_equal(r.samples,s) and np.array_equal(r.logl,ll)
        assert np.allclose(r.logwt,lw,rtol=0,atol=1e-12)
        j=reduced.FREE_NAMES.index('f_metab')
        roundtrip=np.array([transform_factory(reduced.FREE_SPECS)(v) for v in u])
        summary=json.loads((BASE/f'summary_{tag}.json').read_text())
        row=dict(samples=len(s),dead_before_final=before,nlive=r.nlive,
          weight_sum_using_reported_logz=float(np.exp(lw-summary['logz']).sum()),
          cube_error=float(np.max(abs(u-r.samples_u))),roundtrip_error=float(np.max(abs(roundtrip-s))),
          mean=float(w@u[:,j]),ks=ecdf(u[:,j],w),duplicates=len(s)-len(np.unique(s,axis=0)),
          logz=float(logsumexp(lw)),logzerr=float(r.logzerr[-1]),
          actual_dlogz=json.loads((ROOT/f'reports/P16_reduced/trace_{tag}.json').read_text())[-1]['dlogz'])
        row['medians']={n:float(np.interp(.5,np.cumsum(w[np.argsort(s[:,k])])-.5*w[np.argsort(s[:,k])],np.sort(s[:,k]))) for k,n in enumerate(reduced.FREE_NAMES)}
        result[tag]=row;saved[tag]=(s,w);print(tag,json.dumps(row),flush=True)
    # Independently reproduce the historical conditional-bootstrap rule, without
    # endorsing it as a calibrated nested-sampling uncertainty estimate.
    se={}
    for tag,(s,w) in saved.items():
        rng=np.random.default_rng(0)
        meds=[np.median(s[rng.choice(len(s),len(s),p=w)],axis=0) for _ in range(200)]
        se[tag]=np.std(meds,axis=0)
    result['historical_rule_failures']=[n for j,n in enumerate(reduced.FREE_NAMES) if abs(result['red1']['medians'][n]-result['red2']['medians'][n])>2*np.hypot(se['red1'][j],se['red2'][j])]
    for folder in ['src/etcgem','configs/experiments','reports/P16_reduced','reports/P11_nested']:
        for p in (ROOT/folder).rglob('*'):
            if p.is_file() and p.suffix in ['.py','.json','.yaml','.csv','.md']:manifest[str(p.relative_to(ROOT))]=sha(p)
    versions={n:md.version(n) for n in ['dynesty','numpy','scipy','cobra','gurobipy']}
    (HERE/'environment.json').write_text(json.dumps(dict(python=sys.executable,platform=platform.platform(),versions=versions),indent=2))
    (HERE/'input_manifest.json').write_text(json.dumps(manifest,indent=2))
    (HERE/'independent_audit.json').write_text(json.dumps(result,indent=2))
