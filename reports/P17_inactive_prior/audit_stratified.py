"""Independent D48 partition-weight and conditional-evidence audit."""
import hashlib
import argparse
import json
from pathlib import Path
import numpy as np
from scipy.special import logsumexp,ndtr
from scipy.stats import truncnorm

HERE=Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--uniform',action='store_true');args=parser.parse_args()
BATCH='stratified_uniform' if args.uniform else 'stratified_controls'
z1=.15*np.sqrt(2*np.pi)*(ndtr(.5/.15)-ndtr(-.5/.15));truth=13*np.log(z1)
def cdf(x):
    return .3*truncnorm.cdf(x,-400,1600,loc=.2,scale=.0005)+.7*truncnorm.cdf(x,-7.5,2.5,loc=.75,scale=.1)
mass=float(cdf(.203)-cdf(.197));rows=[]
for result in sorted((HERE/BATCH).glob('*/result.json')):
    row=json.loads(result.read_text());folder=result.parent;combined=np.load(folder/'combined.npz')
    us=[];weights=[];errors=[]
    for part in row['parts']:
        raw=np.load(folder/f"{part['core']}.npz");us.append(raw['u']);weights.append(raw['logwt']+np.log(part['volume']))
        true_conditional=float(truth+np.log(mass if part['core'] else 1-mass)-np.log(part['volume']))
        errors.append(dict(core=part['core'],truth_logz=true_conditional,error=part['logz']-true_conditional,reported_error=part['logzerr']))
    assert np.array_equal(np.concatenate(us),combined['u'])
    assert np.array_equal(np.concatenate(weights),combined['logwt'])
    z=float(logsumexp(combined['logwt']));w=np.exp(combined['logwt']-z)
    assert abs(z-row['logz'])<1e-12
    assert abs(float(w[combined['u'][:,0]<.5].sum())-row['region_mass'])<1e-12
    rows.append(dict(seed=row['seed'],conditional_evidence=errors,logz_error=z-truth,
        region_mass=row['region_mass'],inactive_ks=row['inactive_ks'],max_active_ks=row['max_active_ks'],
        combined_sha256=hashlib.sha256((folder/'combined.npz').read_bytes()).hexdigest()))
out=dict(exact_core_posterior_mass=mass,rows=rows,scope='Independent partition recombination and truth audit; no posterior certificate.')
(HERE/('stratified_uniform_audit.json' if args.uniform else 'stratified_audit.json')).write_text(json.dumps(out,indent=2));print(json.dumps(out))
