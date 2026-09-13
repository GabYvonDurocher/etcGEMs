"""Diagnostic exact conditional coordinate kernel; no change to target or prior.
Uniform rejection on the WHOLE prior interval samples all permitted disconnected
pieces proportional to length. A sweep is invariant but need not mix adequately.
"""
import numpy as np
from dynesty.internal_samplers import InternalSampler,SamplerReturn,RSliceSampler
from dynesty.utils import get_random_generator
class GlobalCoordinate(InternalSampler):
    @property
    def update_bound_interval_ratio(self):
        return RSliceSampler(ndim=self.ndim,slices=3).update_bound_interval_ratio
    @staticmethod
    def sample(args):
        rng=get_random_generator(args.rseed);u=np.array(args.u,copy=True);nc=0
        for j in rng.permutation(len(u)):
            for tries in range(1000000):
                candidate=u.copy();candidate[j]=rng.random();v=args.prior_transform(candidate)
                ll=args.loglikelihood(v);nc+=1
                if ll>args.loglstar:u=candidate;break
            else:raise RuntimeError(f'GlobalCoordinate exceeded evaluation cap at coordinate {j}, cutoff {args.loglstar}')
        return SamplerReturn(u=u,v=v,logl=ll,ncalls=nc,tuning_info={},evaluation_history=[],proposal_stats={'ncalls':nc})
