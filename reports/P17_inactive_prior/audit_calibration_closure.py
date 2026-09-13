"""Read-only reconstruction of D50 outputs; writes a separate closure audit only.

Does not import the sampler, target implementation or its summary helpers.
"""
import hashlib
import json
from pathlib import Path
import numpy as np
from scipy.special import logsumexp, ndtr
from scipy.stats import truncnorm, t

HERE = Path(__file__).resolve().parent / 'stratified_calibration'
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
def smooth(x):
    return truncnorm.cdf(x, -0.5/.15, 0.5/.15, loc=.5, scale=.15)
def spike(x):
    return .3*truncnorm.cdf(x, -400, 1600, loc=.2, scale=.0005) + .7*truncnorm.cdf(x, -7.5, 2.5, loc=.75, scale=.1)
def ks(x, w):
    ii = np.argsort(x); x = x[ii]; w = w[ii]; cs = np.cumsum(w)
    return float(max(np.max(cs-x), np.max(x-(cs-w))))
def close(a, b):
    assert np.allclose(a, b, atol=2e-11, rtol=0), (a, b)

z1 = .15*np.sqrt(2*np.pi)*(ndtr(.5/.15)-ndtr(-.5/.15))
out = {'scope': 'Independent raw-array and analytical-truth audit; no sampler certification.', 'targets': {}}
for kind in ('smooth', 'spike'):
    cdf = smooth if kind == 'smooth' else spike
    truth = (14 if kind == 'smooth' else 13)*np.log(z1)
    core_mass = float(cdf(.203)-cdf(.197)); rows = []
    for p in sorted((HERE/kind).glob('*/result.json')):
        r = json.loads(p.read_text()); folder = p.parent
        u, lw, errors = [], [], []
        for part in r['parts']:
            raw = np.load(folder/f"{part['core']}.npz")
            active_u = np.delete(raw['u'], 7, axis=1)
            if kind == 'smooth':
                expected_ll = -.5*np.sum(((active_u-.5)/.15)**2, axis=1)
            else:
                expected_ll = np.logaddexp(
                    np.log(.3)+truncnorm.logpdf(active_u[:,0],-400,1600,loc=.2,scale=.0005),
                    np.log(.7)+truncnorm.logpdf(active_u[:,0],-7.5,2.5,loc=.75,scale=.1)
                )-.5*np.sum(((active_u[:,1:]-.5)/.15)**2,axis=1)
            close(expected_ll, raw['logl'])
            volume = .006 if part['core'] else .994
            close(volume, part['volume'])
            assert np.all((np.abs(raw['u'][:, 0]-.2)<.003) == part['core'])
            zpart = float(logsumexp(raw['logwt'])); close(zpart, part['logz'])
            expected = truth + np.log(core_mass if part['core'] else 1-core_mass) - np.log(volume)
            errors.append(zpart-expected)
            u.append(raw['u']); lw.append(raw['logwt']+np.log(volume))
        u = np.concatenate(u); lw = np.concatenate(lw)
        combined = np.load(folder/'combined.npz')
        assert np.array_equal(u, combined['u']) and np.array_equal(lw, combined['logwt'])
        z = float(logsumexp(lw)); w = np.exp(lw-z)
        active = [ks(cdf(u[:, j]) if j == 0 else smooth(u[:, j]), w) for j in range(15) if j != 7]
        inactive = ks(u[:, 7], w); region = float(w[u[:, 0]<.5].sum())
        close([z, truth, z-truth, region, float(cdf(.5)), inactive, max(active)],
              [r[k] for k in ('logz','truth_logz','logz_error','region_mass','truth_region_mass','inactive_ks','max_active_ks')])
        close(active, r['all_active_ks'])
        score = max(inactive/.02, max(active)/.05, abs(region-cdf(.5))/.05, abs(z-truth)/.15)
        rows.append(dict(seed=r['seed'],logz_error=z-truth,region_mass=region,inactive_ks=inactive,
                         max_active_ks=max(active),score=score,conditional_logz_errors=errors,
                         hashes={f.name:sha(f) for f in folder.iterdir() if f.is_file()}))
    summary_path = HERE/f'{kind}_calibration.json'
    summary = None
    if summary_path.exists():
        summary = json.loads(summary_path.read_text())
        assert len(rows) == 100 and [r['seed'] for r in rows] == list(range(18101,18201))
        for r in rows: assert summary['result_hashes'][str(r['seed'])] == r['hashes']['result.json']
        ratios = np.exp([r['logz_error'] for r in rows]); margin = t.ppf(.995,99)*ratios.std(ddof=1)/10
        close(summary['score_envelope'], max(r['score'] for r in rows))
        close(summary['mean_evidence_ratio'], ratios.mean())
        close(summary['approximate_99pct_t_interval'], [ratios.mean()-margin, ratios.mean()+margin])
    out['targets'][kind] = dict(completed=len(rows),summary=summary,rows=rows)
out['status'] = json.loads((HERE/'status.json').read_text())
assert out['status']['status'] != 'running', 'Audit final batch only after completion or recorded stop'
(HERE/'closure_audit.json').write_text(json.dumps(out, indent=2))
print(json.dumps({k:v['completed'] for k,v in out['targets'].items()}))
