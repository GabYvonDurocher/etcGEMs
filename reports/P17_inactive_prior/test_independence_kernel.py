"""D39 independent density, balance, and exact-start stationarity checks."""
import json
from pathlib import Path
from types import SimpleNamespace
import numpy as np
from scipy.stats import norm
from independence_kernel import Mixture, IndependenceSampler
from independent_audit import ecdf


def main():
    q=Mixture([[.05]],[[[.03**2]]]); rng=np.random.default_rng(17740)
    grid=np.linspace(.001,.999,100)
    actual=np.array([np.exp(q.logpdf(np.array([x]))) for x in grid])
    expected=.1+.9*norm.pdf(grid,.05,.03)
    assert np.allclose(actual,expected,rtol=1e-12,atol=1e-12)
    # Unnormalised constrained-uniform target has symmetric accepted flux.
    forward=actual[:,None]*np.minimum(1,actual[None,:]/actual[:,None])
    assert np.allclose(forward,forward.T,rtol=1e-12,atol=1e-12)
    def ll(u): return 0. if u[0]<.2 or u[0]>.6 else -100.
    corrected=[]; uncorrected=[]
    for _ in range(2000):
        x=rng.random()*.6; x=x if x<.2 else x+.4
        args=SimpleNamespace(u=np.array([x]),prior_transform=lambda u:u,loglikelihood=ll,
                             loglstar=-1.,rseed=rng,kwargs={'mixture':q,'steps':32})
        corrected.append(IndependenceSampler.sample(args).u[0])
        bad=np.array([x])
        for __ in range(32):
            proposal=q.draw(rng)
            if np.all((proposal>=0)&(proposal<=1)) and ll(proposal)>-1:
                bad=proposal
        uncorrected.append(bad[0])
    def cdf(x):
        x=np.asarray(x); return np.where(x<.2,x/.6,(x-.4)/.6)
    ks=ecdf(cdf(corrected),np.ones(2000)/2000); badks=ecdf(cdf(uncorrected),np.ones(2000)/2000)
    limit=float(np.sqrt(np.log(2/.001)/(2*2000)))
    assert ks<limit and badks>limit
    result=dict(seed=17740,independent_exact_starts=2000,corrected_ks=ks,
                uncorrected_ks=badks,dkw_alpha=.001,dkw_limit=limit,
                density_and_balance_passed=True,
                scope='Independent exact-start endpoint test only; not IID testing of nested output.')
    (Path(__file__).parent/'test_independence_kernel.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result))


if __name__=='__main__':main()
