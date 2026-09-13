"""D31: live-group geometry, not posterior covariance or causal certification."""
import hashlib
import json
import pickle
import numpy as np
from scipy.linalg import eigh
import independent_audit as a
from conditional_trace import ParentSlice
from premise import cm, PAYLOAD


def main():
    _, obs, err, _, _, _ = cm.load_respirometry(PAYLOAD['strain'], PAYLOAD['table'], PAYLOAD['otu'])
    j = a.reduced.FREE_NAMES.index('disc_growth')
    rows = []
    for seed in [17511, 17512]:
        path = a.HERE/f'conditional_{seed}/audit_checkpoint_2000.save'
        raw = path.read_bytes()
        s = pickle.loads(raw)['sampler']
        assert s.results.niter == 2000
        u, v, ll = s.live_u, s.live_v, s.live_logl
        variance = np.asarray(err)**2+np.exp(2*v[:, j, None])
        curve = -.5*np.sum(np.asarray(obs)**2/variance+np.log(2*np.pi*variance), axis=1)
        hi = abs(ll-curve) >= 1e-6
        assert hi.sum() > 15 and (~hi).sum() > 15
        all_cov = np.cov(u, rowvar=False)
        hi_cov = np.cov(u[hi], rowvar=False)
        eigenvalues, vectors = eigh(hi_cov, all_cov)
        assert np.all(eigenvalues > 0), 'Singular group geometry; no ridge permitted'
        directions = []
        for eigenvalue, vector in zip(eigenvalues, vectors.T):
            # Unit Euclidean loading norm for readability; width ratio unchanged.
            vector = vector/np.linalg.norm(vector)
            if vector[np.argmax(abs(vector))] < 0:
                vector = -vector
            ratio = np.sqrt((vector@hi_cov@vector)/(vector@all_cov@vector))
            assert np.isclose(ratio, np.sqrt(eigenvalue), rtol=1e-8, atol=1e-12)
            directions.append(dict(width_ratio=float(ratio), loadings=dict(zip(a.reduced.FREE_NAMES, vector.tolist()))))
        row = dict(seed=seed, iteration=2000, checkpoint_sha256=hashlib.sha256(raw).hexdigest(),
                   complementary_count=int(hi.sum()), compatible_count=int((~hi).sum()),
                   all_cov_condition=float(np.linalg.cond(all_cov)),
                   complementary_cov_condition=float(np.linalg.cond(hi_cov)),
                   all_f_sd=float(np.std(u[:, 7], ddof=1)),
                   complementary_f_sd=float(np.std(u[hi, 7], ddof=1)),
                   compatible_f_sd=float(np.std(u[~hi, 7], ddof=1)),
                   directions=directions)
        rows.append(row)
        print(seed, 'width ratios', [round(d['width_ratio'], 6) for d in directions],
              'tightest', sorted(directions[0]['loadings'].items(), key=lambda x:-abs(x[1]))[:4], flush=True)
    with (a.HERE/'group_geometry.json').open('x') as out:
        json.dump(dict(rows=rows, scope='Unweighted live geometry of conditional diagnostics, not posterior/prior widths. Covariance comparison is not proof of proposal-axis use or causality.'), out, indent=2)


if __name__ == '__main__':
    main()
