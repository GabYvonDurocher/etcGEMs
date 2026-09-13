"""Independent saved-array audit and complete active-marginal summaries."""
import hashlib
import json
from pathlib import Path
import numpy as np
from scipy.special import logsumexp, ndtr

HERE = Path(__file__).resolve().parent
rows = []
def ecdf(x, w):
    order = np.argsort(x); x=x[order]; w=w[order]; upper=np.cumsum(w)
    return float(max(np.max(upper-x), np.max(x-(upper-w))))
def normal_cdf(x, mean, sd):
    return (ndtr((x-mean)/sd)-ndtr(-mean/sd))/(ndtr((1-mean)/sd)-ndtr(-mean/sd))
for batch in ['independence_controls', 'independence_oracle', 'independence_diagonal', 'independence_laplace', 'hybrid_controls']:
    for path in sorted((HERE/batch).glob('*/result.json')):
        row=json.loads(path.read_text()); source=path.parent/'samples.npz'
        data=np.load(source);u=data['u'];w=np.exp(data['logwt']-logsumexp(data['logwt']))
        assert np.isfinite(u).all() and np.isfinite(w).all()
        assert abs(w.sum()-1)<1e-12
        first=normal_cdf(u[:,0],.5,.15) if row['kind']=='smooth' else .3*normal_cdf(u[:,0],.2,.0005)+.7*normal_cdf(u[:,0],.75,.1)
        active={str(j):ecdf(first if j==0 else normal_cdf(u[:,j],.5,.15),w) for j in range(15) if j!=7}
        assert abs(active['0']-row['active_ks'])<1e-12
        assert abs(ecdf(u[:,7],w)-row['nuisance_ks'])<1e-12
        assert abs(w[u[:,0]<.5].sum()-row['region_mass'])<1e-12
        rows.append(dict(batch=batch,**row,all_active_ks=active,max_active_ks=max(active.values()),
                         logz_error=row['logz']-row['truth_logz'],
                         arrays_sha256=hashlib.sha256(source.read_bytes()).hexdigest()))
out=dict(rows=rows,scope='Weighted CDF effect sizes; no IID KS significance or weight-ESS certification.')
(HERE/'independence_audit.json').write_text(json.dumps(out,indent=2))
for batch in ['independence_controls','independence_oracle','independence_diagonal','independence_laplace','hybrid_controls']:
    for kind in ['smooth','spike']:
        subset=[r for r in rows if r['batch']==batch and r['kind']==kind]
        if subset:
            print(json.dumps(dict(batch=batch,kind=kind,n=len(subset),
                region_mass=[r['region_mass'] for r in subset],
                max_active_ks=[r['max_active_ks'] for r in subset],
                inactive_ks=[r['nuisance_ks'] for r in subset],
                logz_error=[r['logz_error'] for r in subset])))
