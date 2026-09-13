"""Independent 1D conditional-draw regression; DKW does not apply to nested samples."""
from global_coordinate import GlobalCoordinate
from types import SimpleNamespace
import numpy as np,json
from pathlib import Path
n=10000;rng=np.random.default_rng(17250);limit=float(np.sqrt(np.log(2000)/(2*n)));out={}
for target in ['disjoint','positive_gaussian']:
    ll=(lambda x:1. if (.1<x[0]<.2 or .6<x[0]<.9) else 0.) if target=='disjoint' else (lambda x:-.5*((x[0]-.7)/.1)**2)
    cutoff=.5 if target=='disjoint' else -.5
    x=[]
    for k in range(n):
        args=SimpleNamespace(u=np.array([.15 if target=='disjoint' else .7]),rseed=rng,prior_transform=lambda u:u,loglikelihood=ll,loglstar=cutoff)
        x.append(GlobalCoordinate.sample(args).u[0])
    x=np.array(x)
    u=np.where(x<.2,(x-.1)/.4,.25+(x-.6)/.4) if target=='disjoint' else (x-.6)/.2
    u.sort();ks=float(max(np.max(np.arange(1,n+1)/n-u),np.max(u-np.arange(n)/n)))
    assert ks<limit,(target,ks,limit)
    out[target]=dict(n=n,ks=ks,dkw_bound=limit,alpha=.001,passes=True,first_interval_mass=float(np.mean(x<.2)))
Path(__file__).with_name('test_global_coordinate.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
