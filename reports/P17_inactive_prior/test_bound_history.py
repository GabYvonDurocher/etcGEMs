"""Regression: dynesty 3.1.0 aliases mutable bound history; local recording-only fix."""
import numpy as np,json,copy,inspect,hashlib
from pathlib import Path
import dynesty
from dynesty.sampler import Sampler
H=Path(__file__).resolve().parent
original=Sampler.update_bound_if_needed

def preserve_history(self,*args,**kwargs):
    before=len(self.bound_list)
    result=original(self,*args,**kwargs)
    if len(self.bound_list)>before:self.bound_list[-1]=copy.deepcopy(self.bound_list[-1])
    return result

def ll(x):return -.5*np.sum(((x-.5)/.1)**2)
def pt(x):return x

def run(patched):
    Sampler.update_bound_if_needed=preserve_history if patched else original
    try:
        s=dynesty.NestedSampler(ll,pt,3,nlive=100,sample='rslice',slices=3,bound='multi',rstate=np.random.default_rng(17300),first_update={'min_eff':30})
        s.run_nested(dlogz=.1,print_progress=False)
        return s.results
    finally:Sampler.update_bound_if_needed=original

if __name__=='__main__':
    assert dynesty.__version__=='3.1.0'
    baseline=run(False);fixed=run(True)
    nbase=len({id(b) for b in baseline.bound[1:]});nfix=len({id(b) for b in fixed.bound[1:]})
    assert len(baseline.bound)>2 and nbase==1
    assert nfix==len(fixed.bound)-1
    assert np.array_equal(baseline.samples,fixed.samples) and np.array_equal(baseline.logwt,fixed.logwt)
    out=dict(version=dynesty.__version__,source_sha256=hashlib.sha256(inspect.getsource(original).encode()).hexdigest(),recorded_bounds=len(baseline.bound),baseline_distinct_non_cube=nbase,patched_distinct_non_cube=nfix,trajectory_and_weights_identical=True,scope='Recording defect only; does not explain biased posterior or recover P16 historical geometry')
    (H/'test_bound_history.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
