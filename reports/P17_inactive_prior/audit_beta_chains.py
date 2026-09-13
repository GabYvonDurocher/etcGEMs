"""Read-only independent audit of the six D37 chain artifacts."""
import hashlib
import json
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent / 'beta_path_chains'
rows = []
for plan in json.loads((HERE / 'plan.json').read_text()):
    for kind in ['original', 'local']:
        folder = HERE / f'{plan["seed"]}_{kind}'
        trace = np.load(folder / 'trace.npz')
        u, logl, calls = trace['u'], trace['logl'], trace['calls']
        result = json.loads((folder / 'result.json').read_text())
        verified = json.loads((folder / 'verified.json').read_text())
        assert u.shape == (33, 16) and logl.shape == (33,)
        assert np.array_equal(u[0], plan['parent'])
        assert np.isfinite(u).all() and ((u >= 0) & (u <= 1)).all()
        assert np.all(logl > plan['cut']) and np.all(np.diff(calls) > 0)
        assert [v['step'] for v in verified] == [8, 16, 24, 32]
        errors = [abs(v['rechecked_logl'] - logl[v['step']]) for v in verified]
        assert max(errors) <= 1e-6
        def ks(values):
            x = np.sort(values)
            return float(max(np.max(np.arange(1, 33) / 32 - x),
                             np.max(x - np.arange(32) / 32)))
        beta_ks, inactive_ks = ks(u[1:, 15]), ks(u[1:, 7])
        assert abs(beta_ks - result['beta_cdf_ks']) < 1e-12
        assert abs(inactive_ks - result['original_inactive_ks']) < 1e-12
        assert abs(u[1:, 15].mean() - result['beta_cdf_mean']) < 1e-12
        assert result['calls'] == int(calls[-1]) + 1 <= 1000
        rows.append(dict(seed=plan['seed'], kind=kind, states=33,
                         beta_cdf_ks=beta_ks, inactive_ks=inactive_ks,
                         max_recheck_error=max(errors),
                         trace_sha256=hashlib.sha256((folder/'trace.npz').read_bytes()).hexdigest()))
out = dict(status='six traces independently audited', chains=rows,
           scope='Descriptive correlated-chain coverage; no IID test or posterior certification.')
(HERE / 'audit.json').write_text(json.dumps(out, indent=2))
print(json.dumps(out))
