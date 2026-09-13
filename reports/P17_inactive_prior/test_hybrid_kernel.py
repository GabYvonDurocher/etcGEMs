"""D47 IID exact-start stationarity control, not a mixing certificate."""
import json
from pathlib import Path
from types import SimpleNamespace
import numpy as np
from hybrid_kernel import HybridSampler
from independence_kernel import Mixture
from dynesty.internal_samplers import SamplerArgument

rng=np.random.default_rng(17841);n=2000
mixture=Mixture([[.1,.1]],[[[.01,0],[0,.01]]])
def ll(u):
    return 0. if np.all((u>=0)&(u<=.2)) or np.all((u>=.6)&(u<=1)) else -100.
def identity(u):return u
rows=[]
for i in range(n):
    u=rng.random(2)*.2 if rng.random()<.2 else .6+rng.random(2)*.4
    result=HybridSampler.sample(SamplerArgument(u=u,rseed=rng,prior_transform=identity,
        loglikelihood=ll,loglstar=-1.,axes=np.eye(2),scale=1.,kwargs={'mixture':mixture,'steps':32}))
    assert ll(result.u)==0;rows.append(result.u)
rows=np.array(rows)
def ks(x):
    x=np.sort(x);return float(max(np.max(np.arange(1,n+1)/n-x),np.max(x-np.arange(n)/n)))
cdf=np.where(rows<=.2,rows,.2+2*(rows-.6))
distances=[ks(cdf[:,j]) for j in range(2)]
mass_error=abs(float(np.mean(rows[:,0]<.2))-.2)
bound=float(np.sqrt(np.log(2/(.001/3))/(2*n)))
assert max(distances+[mass_error])<bound
out=dict(seed=17841,n=n,marginal_ks=distances,region_mass_error=mass_error,
         simultaneous_bound=bound,total_alpha=.001,scope='Independent exact-start endpoints only; not nested-sampling certification.')
Path(__file__).with_suffix('.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
