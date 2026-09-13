"""D50 fixed calibration schedule, guarded and restartable by completed seed."""
import hashlib
import json
import signal
import time
from pathlib import Path
import numpy as np
from scipy.stats import t
import stratified_controls as s

HERE=s.c.HERE/'stratified_calibration'
def score(row):
    return max(row['inactive_ks']/.02,row['max_active_ks']/.05,
               abs(row['region_mass']-row['truth_region_mass'])/.05,abs(row['logz_error'])/.15)

def main():
    HERE.mkdir(exist_ok=True)
    with (HERE/'running.claim').open('x') as out:out.write('D50 single sequential coordinator; inspect process before removing claim.\n')
    def expired(*unused):raise TimeoutError('D50 per-stratum deadline; checkpoint retained')
    signal.signal(signal.SIGALRM,expired);start=time.monotonic()
    try:
        rng=np.random.default_rng(17842);reference={}
        for kind in ['smooth','spike']:
            scores=[];prob=float(s.c.active_cdf(.5,kind))
            for _ in range(2000):
                u=rng.random((400,15));x=np.sort(u,axis=0)
                ks=np.maximum(np.max(np.arange(1,401)[:,None]/400-x,axis=0),np.max(x-np.arange(400)[:,None]/400,axis=0))
                scores.append(max(ks[7]/.02,np.max(np.delete(ks,7))/.05,abs(np.mean(u[:,0]<prob)-prob)/.05))
            reference[kind]=dict(n=400,datasets=2000,cdf_only_score_99th=float(np.quantile(scores,.99)))
        (HERE/'iid_reference.json').write_text(json.dumps(reference,indent=2))
        for kind in ['smooth','spike']:
            stage=time.monotonic();s.KIND=kind;s.METHOD='unif';s.HERE=HERE/kind;s.HERE.mkdir(exist_ok=True)
            for seed in range(18101,18201):
                path=s.HERE/str(seed)/'result.json'
                if path.exists():continue
                if time.monotonic()-stage>1440:raise TimeoutError('D50 target budget leaves no full pair allowance')
                s.run(seed)
                (HERE/'status.json').write_text(json.dumps(dict(status='running',kind=kind,last_completed_seed=seed,wall_s=time.monotonic()-start),indent=2))
            rows=[json.loads((s.HERE/str(seed)/'result.json').read_text()) for seed in range(18101,18201)]
            ratios=np.exp([r['logz_error'] for r in rows]);margin=float(t.ppf(.995,99)*ratios.std(ddof=1)/10)
            summary=dict(kind=kind,seeds=[18101,18200],n=100,score_envelope=max(map(score,rows)),
                mean_evidence_ratio=float(ratios.mean()),approximate_99pct_t_interval=[float(ratios.mean()-margin),float(ratios.mean()+margin)],
                scope='Known-partition control; ~99% pointwise exchangeable-run envelope, not simultaneous five-run certification or real-model confirmation.',
                result_hashes={str(r['seed']):hashlib.sha256((s.HERE/str(r['seed'])/'result.json').read_bytes()).hexdigest() for r in rows})
            (HERE/f'{kind}_calibration.json').write_text(json.dumps(summary,indent=2))
        status=dict(status='completed calibration; inspect before reserved confirmation',wall_s=time.monotonic()-start)
    except Exception as error:
        (HERE/'status.json').write_text(json.dumps(dict(status='stopped for review',error=repr(error),wall_s=time.monotonic()-start),indent=2));raise
    finally:signal.alarm(0)
    (HERE/'status.json').write_text(json.dumps(status,indent=2))

if __name__=='__main__':main()
