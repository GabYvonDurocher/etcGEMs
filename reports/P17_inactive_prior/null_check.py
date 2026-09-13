"""Standing weighted inactive-CDF diagnostic. No model solves or IID p-values."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from scipy.special import logsumexp
from scipy.stats import truncnorm

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--samples', type=Path, required=True)
    p.add_argument('--logwt', type=Path, required=True)
    p.add_argument('--column', type=int, required=True)
    p.add_argument('--prior', choices=['p16-f-metab','beta31','uniform'], required=True)
    p.add_argument('--expected-samples-sha256', required=True)
    p.add_argument('--expected-logwt-sha256', required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    hashes = {k:hashlib.sha256(getattr(a,k).read_bytes()).hexdigest() for k in ('samples','logwt')}
    assert hashes['samples'] == a.expected_samples_sha256
    assert hashes['logwt'] == a.expected_logwt_sha256
    s = np.load(a.samples); lw = np.load(a.logwt)
    assert s.ndim == 2 and lw.shape == (len(s),) and np.isfinite(s).all()
    assert np.isfinite(logsumexp(lw)) and not np.isnan(lw).any()
    x = s[:,a.column]
    if a.prior == 'p16-f-metab':
        assert np.all((x >= .15) & (x <= .45))
        u = truncnorm.cdf(x, (.15-.28)/.03, (.45-.28)/.03, loc=.28, scale=.03)
    else:
        assert np.all((x >= 0) & (x <= 1))
        u = x**3 if a.prior == 'beta31' else x
    w = np.exp(lw-logsumexp(lw)); ii = np.argsort(u); cs = np.cumsum(w[ii])
    result = dict(n=len(s),prior=a.prior,column=a.column,hashes=hashes,
        cdf_mean=float(np.sum(w*u)),cdf_ks=float(max(np.max(cs-u[ii]),np.max(u[ii]-(cs-w[ii])))),
        weight_ess=float(1/np.sum(w*w)),
        scope='Target CDF is Uniform(0,1) only after independent prior and inactivity are proved. Descriptive weighted discrepancy; weight ESS is not independent N. No automatic pass or IID p-value.')
    assert not a.output.exists(), 'Use a new audit filename; preserve existing evidence'
    a.output.write_text(json.dumps(result,indent=2)); print(json.dumps(result,indent=2))
if __name__ == '__main__': main()
