"""D39 frozen mixture independence MH on the uniform constrained prior."""
import numpy as np
from scipy.special import logsumexp
from dynesty.internal_samplers import InternalSampler, RSliceSampler, SamplerReturn
from dynesty.utils import get_random_generator


class Mixture:
    def __init__(self, means, covariances, uniform_weight=.1):
        self.means=np.asarray(means); self.covariances=np.asarray(covariances)
        self.ndim=self.means.shape[1]
        self.chol=np.linalg.cholesky(self.covariances)
        self.whiten=np.linalg.inv(self.chol)
        self.lognorm=-.5*self.ndim*np.log(2*np.pi)-np.log(np.diagonal(self.chol,axis1=1,axis2=2)).sum(axis=1)
        self.weights=np.r_[uniform_weight,np.full(len(self.means),(1-uniform_weight)/len(self.means))]
        self.logweights=np.log(self.weights)

    def draw(self,rng):
        k=rng.choice(len(self.weights),p=self.weights)
        if k==0: return rng.random(self.ndim)
        return self.means[k-1]+self.chol[k-1]@rng.normal(size=self.ndim)

    def logpdf(self,u):
        delta=np.einsum('kij,kj->ki',self.whiten,u-self.means)
        uniform=self.logweights[0] if np.all((u>=0)&(u<=1)) else -np.inf
        return float(logsumexp(np.r_[uniform,self.logweights[1:]+self.lognorm-.5*np.sum(delta*delta,axis=1)]))


class IndependenceSampler(InternalSampler):
    def __init__(self, mixture, steps=32, **kwargs):
        super().__init__(mixture=mixture,steps=steps,**kwargs)
        self.sampler_kwargs.update(mixture=Mixture(**mixture),steps=steps)

    @property
    def update_bound_interval_ratio(self):
        return RSliceSampler(ndim=self.ndim,slices=3).update_bound_interval_ratio

    @staticmethod
    def sample(args):
        rng=get_random_generator(args.rseed); q=args.kwargs['mixture']
        u=np.array(args.u,copy=True); v=args.prior_transform(u); ll=args.loglikelihood(v)
        if not ll>args.loglstar: raise RuntimeError('Independence kernel parent below cut')
        logq=q.logpdf(u); nc=1; accepted=0; outside=0; density_rejected=0
        for _ in range(args.kwargs['steps']):
            candidate=q.draw(rng)
            if np.any((candidate<0)|(candidate>1)):
                outside+=1; continue
            proposed_logq=q.logpdf(candidate)
            if np.log(rng.random())>min(0.,logq-proposed_logq):
                density_rejected+=1; continue
            proposed_v=args.prior_transform(candidate); proposed_ll=args.loglikelihood(proposed_v); nc+=1
            if proposed_ll>args.loglstar:
                u,v,ll,logq=candidate,proposed_v,proposed_ll,proposed_logq; accepted+=1
        return SamplerReturn(u=u,v=v,logl=ll,ncalls=nc,tuning_info={},evaluation_history=[],
            proposal_stats=dict(accepted=accepted,outside=outside,density_rejected=density_rejected))
