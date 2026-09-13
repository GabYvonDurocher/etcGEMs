"""D47 composition of frozen global MH and coordinate slice kernels."""
from types import SimpleNamespace
import numpy as np
from dynesty.internal_samplers import generic_slice_step, SamplerReturn
from dynesty.utils import get_random_generator
from independence_kernel import IndependenceSampler

class HybridSampler(IndependenceSampler):
    @staticmethod
    def sample(args):
        rng=get_random_generator(args.rseed)
        forwarded=SimpleNamespace(u=args.u,loglstar=args.loglstar,prior_transform=args.prior_transform,
                                  loglikelihood=args.loglikelihood,rseed=rng,kwargs=args.kwargs)
        result=IndependenceSampler.sample(forwarded)
        u,v,ll=result.u,result.v,result.logl;nc=result.ncalls;history=[]
        for j in rng.permutation(len(u)):
            direction=np.zeros(len(u));direction[j]=1
            u,v,ll,calls,_,_,_=generic_slice_step(u,direction,None,args.loglstar,
                args.loglikelihood,args.prior_transform,False,history,rng)
            nc+=calls
        stats=dict(result.proposal_stats);stats['coordinate_sweeps']=1
        return SamplerReturn(u=u,v=v,logl=ll,ncalls=nc,tuning_info={},
            evaluation_history=history,proposal_stats=stats)
