"""D45 fresh-model reverse-order repeat of all saved D44 evaluations."""
import json
import signal
import time
import numpy as np
import independent_audit as a
import premise as p

FOLDER=a.HERE/'real_curvature_repeat'

def main():
    FOLDER.mkdir(exist_ok=False);start=time.monotonic();rows=[]
    def expired(*unused):raise TimeoutError('D45 300s deadline')
    signal.signal(signal.SIGALRM,expired);signal.alarm(300)
    try:
        source=json.loads((a.HERE/'real_curvature_probe/evaluations.json').read_text())
        assert len(source)==58
        transform=a.transform_factory(a.reduced.FREE_SPECS)
        p.cm._gwinit(dict(p.PAYLOAD,solver='gurobi'));p.gasflux.flux_tpc=p.flux
        for saved in reversed(source):
            if len(rows)>=80:raise RuntimeError('D45 call cap')
            p.capture.clear();value=float(p.loglike15(transform(np.array(saved['u']))))
            rows.append(dict(label=saved['label'],logl=value,original_logl=saved['logl'],
                             absolute_difference=abs(value-saved['logl']),flux=p.capture.get('flux',{})))
            (FOLDER/'evaluations.json').write_text(json.dumps(rows,indent=2))
        delta=max(r['absolute_difference'] for r in rows)
        by={r['label']:r for r in rows};base=by['baseline_start']['logl'];curves=[]
        for name in a.reduced.FREE_NAMES:
            if name=='f_metab':continue
            k=[-(by[f'{name}_minus_{h}']['logl']-2*base+by[f'{name}_plus_{h}']['logl'])/h**2 for h in [.02,.04]]
            curves.append(dict(parameter=name,curvatures=k,relative_difference=abs(k[0]-k[1])/max(1,abs(k[0]),abs(k[1]))))
        (FOLDER/'curvatures.json').write_text(json.dumps(curves,indent=2))
        status=dict(status='completed',repeatability_passed=delta<=1e-6,max_likelihood_difference=delta,
                    unstable_axes=[r['parameter'] for r in curves if r['relative_difference']>.001],
                    calls=len(rows),wall_s=time.monotonic()-start)
    except Exception as error:
        (FOLDER/'status.json').write_text(json.dumps(dict(status='stopped for review',error=repr(error),calls=len(rows),wall_s=time.monotonic()-start),indent=2));raise
    finally:signal.alarm(0)
    (FOLDER/'status.json').write_text(json.dumps(status,indent=2));print(json.dumps(status))

if __name__=='__main__':main()
