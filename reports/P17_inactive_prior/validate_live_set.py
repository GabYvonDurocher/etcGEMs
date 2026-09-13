"""Full live-set likelihood repeatability, before any conditional sampler replay."""
import independent_audit as a
import premise as p
import numpy as np,json,time,signal
from multiprocessing import get_context
LAST=None
ORIGINAL=p.gasflux.flux_tpc
def capture(*args,**kwargs):
    global LAST
    LAST=ORIGINAL(*args,**kwargs);return LAST

def init():
    p.cm._gwinit(dict(p.PAYLOAD,solver='gurobi'));p.gasflux.flux_tpc=capture

def worker(item):
    index,theta,old=item;t=time.monotonic();value=p.loglike15(theta)
    return dict(index=int(index),logl=float(value),stored_logl=float(old),difference=float(value-old),peak_growth=float(LAST['growth'].max()),finite_o2=int(np.isfinite(LAST['o2_uptake']).sum()),statuses=LAST['status'].tolist(),wall_s=time.monotonic()-t)

def main():
    def timeout(*args):raise TimeoutError('P17 live-set validation exceeded 900s')
    signal.signal(signal.SIGALRM,timeout);signal.alarm(900);t=time.monotonic()
    s=a.dynesty.NestedSampler.restore(str(a.BASE/'dynesty_red2.save'));s.add_final_live(print_progress=False);r=s.results;it=6800
    ix=np.array([np.flatnonzero((r.samples_id==k)&(np.arange(len(r.logl))>=it))[0] for k in range(800)])
    u=r.samples_u[ix].copy();u[:,7]=np.random.default_rng(17501).random(800);pt=a.transform_factory(a.reduced.FREE_SPECS);theta=np.array([pt(v) for v in u])
    np.savez_compressed(a.HERE/'validated_live_input.npz',u=u,theta=theta,indices=ix,stored_logl=r.logl[ix])
    rows=[]
    try:
        with get_context('spawn').Pool(8,initializer=init) as pool:
            for row in pool.imap_unordered(worker,[(i,x,ll) for i,x,ll in zip(ix,theta,r.logl[ix])]):
                rows.append(row)
                (a.HERE/'validate_live_set.json').write_text(json.dumps(rows,indent=2))
                if len(rows)%100==0:print('completed',len(rows),'max difference',max(abs(x['difference']) for x in rows),flush=True)
    finally:signal.alarm(0)
    worst=max(abs(v['difference']) for v in rows);out=dict(n=len(rows),max_abs_difference=worst,threshold=1e-6,ordering_validation_passed=bool(len(rows)==800 and worst<=1e-6),wall_s=time.monotonic()-t,source='red2 live active population at6800; independent f_metab prior redraw seed17501; NOT a posterior fit')
    (a.HERE/'validate_live_set_summary.json').write_text(json.dumps(out,indent=2));print(json.dumps(out),flush=True)
if __name__=='__main__':main()
