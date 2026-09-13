"""D44 saved-parent curvature readiness, unchanged biological likelihood."""
import json
import pickle
import signal
import sys
import time
import numpy as np
import independent_audit as a
import premise as p
from conditional_trace import ParentSlice

FOLDER=a.HERE/'real_curvature_probe'

def main():
    FOLDER.mkdir(exist_ok=False);started=time.monotonic();rows=[]
    def expired(*unused):raise TimeoutError('D44 300s deadline')
    signal.signal(signal.SIGALRM,expired);signal.alarm(300)
    try:
        plan=json.loads((a.HERE/'beta_path_chains/plan.json').read_text())[0]
        sys.modules['__main__'].ParentSlice=ParentSlice
        sampler=pickle.loads((a.HERE/'conditional_17511/audit_checkpoint_2000.save').read_bytes())['sampler']
        _,obs,err,_,_,_=p.cm.load_respirometry(p.PAYLOAD['strain'],p.PAYLOAD['table'],p.PAYLOAD['otu'])
        j=a.reduced.FREE_NAMES.index('disc_growth')
        var=np.asarray(err)**2+np.exp(2*sampler.live_v[:,j,None])
        curve=-.5*np.sum(np.asarray(obs)**2/var+np.log(2*np.pi*var),axis=1)
        group=abs(sampler.live_logl-curve)>=1e-6
        scale=np.std(sampler.live_u[group],axis=0,ddof=1);u=np.array(plan['parent'][:15])
        transform=a.transform_factory(a.reduced.FREE_SPECS)
        (FOLDER/'plan.json').write_text(json.dumps(dict(parent=u.tolist(),scale=scale.tolist(),source=plan),indent=2))
        p.cm._gwinit(dict(p.PAYLOAD,solver='gurobi'));p.gasflux.flux_tpc=p.flux
        def evaluate(v,label):
            if len(rows)>=80:raise RuntimeError('D44 call cap')
            p.capture.clear();value=float(p.loglike15(transform(v)))
            rows.append(dict(label=label,u=v.tolist(),logl=value,flux=p.capture.get('flux',{})))
            (FOLDER/'evaluations.json').write_text(json.dumps(rows,indent=2))
            return value
        base=evaluate(u,'baseline_start')
        if abs(base-plan['parent_logl'])>1e-6:raise RuntimeError('D44 parent repeatability')
        results=[]
        for j,name in enumerate(a.reduced.FREE_NAMES):
            if name=='f_metab':continue
            k=[]
            for fraction in [.02,.04]:
                delta=np.zeros(15);delta[j]=fraction*scale[j]
                if np.any(u-delta<0) or np.any(u+delta>1):break
                minus=evaluate(u-delta,f'{name}_minus_{fraction}')
                plus=evaluate(u+delta,f'{name}_plus_{fraction}')
                k.append(float(-(minus-2*base+plus)/fraction**2))
            results.append(dict(parameter=name,curvatures=k,
                relative_difference=abs(k[0]-k[1])/max(1,abs(k[0]),abs(k[1])) if len(k)==2 else None))
            (FOLDER/'curvatures.json').write_text(json.dumps(results,indent=2))
        end=evaluate(u,'baseline_end')
        if abs(end-base)>1e-6:raise RuntimeError('D44 final baseline repeatability')
        ready=all(r['relative_difference'] is not None and r['relative_difference']<=1e-3 for r in results)
        status=dict(status='completed',local_diagonal_readiness=ready,calls=len(rows),wall_s=time.monotonic()-started,
                    baseline_difference=abs(end-base),scope='Necessary local stencil check only; not full Hessian or posterior confirmation.')
    except Exception as error:
        (FOLDER/'status.json').write_text(json.dumps(dict(status='stopped for review',error=repr(error),calls=len(rows),wall_s=time.monotonic()-started),indent=2))
        raise
    finally:signal.alarm(0)
    (FOLDER/'status.json').write_text(json.dumps(status,indent=2));print(json.dumps(status))

if __name__=='__main__':main()
