"""Separate f_metab from same-vector solver-history effects; canonical LP comparison."""
import premise as p
import numpy as np,json,time
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import get_context
REF={};CURRENT=[];RESET=False

def state(ecm,T,pert):
    p.original_state(ecm,T,pert)
    gp=ecm.model.solver.problem;gp.update();A=gp.getA().tocoo()
    vn=gp.getAttr('VarName');cn=gp.getAttr('ConstrName')
    # Canonical names eliminate harmless row/column reordering by the solver interface.
    vals={('a',cn[i],vn[j]):float(v) for i,j,v in zip(A.row,A.col,A.data)}
    for attr,names in [('LB',vn),('UB',vn),('Obj',vn),('RHS',cn)]:vals.update({(attr,n):float(v) for n,v in zip(names,gp.getAttr(attr))})
    if T not in REF:REF[T]=vals
    ref=REF[T];keys=set(ref)|set(vals)
    delta=[abs(vals.get(k,0)-ref.get(k,0)) for k in keys]
    CURRENT.append(dict(T=T,max_abs=max(delta),changed=sum(d!=0 for d in delta)))
    if RESET:gp.reset()

def init(reset):
    global RESET
    RESET=reset;p.gasflux.apply_state=state;p.gasflux.flux_tpc=p.flux
    p.cm._gwinit(dict(p.PAYLOAD,solver='gurobi'))
def call(arg):
    theta,label=arg;CURRENT.clear();row=p.evaluate(np.asarray(theta),label);row['lp_diff']=list(CURRENT);return row

def main():
    source=json.loads((p.HERE/'premise_results.json').read_text());theta=np.array(next(v['theta'] for v in source if v['label']=='red1_median_fresh'))
    j=p.FREE_NAMES.index('f_metab'); rows=[]
    init(False)
    # 12 exact repeats isolate numerical history without changing a parameter.
    for k in range(12):
        rows.append(call((theta,f'repeat_{k}')));print(rows[-1]['label'],rows[-1]['logl'],flush=True)
    # Independently initialized workers, two orders, plus resetting basis only.
    for reset in [False,True]:
        with ProcessPoolExecutor(max_workers=2,mp_context=get_context('spawn'),initializer=init,initargs=(reset,)) as pool:
            tasks=[]
            for k,fm in enumerate([.15,.28,.45,.45,.28,.15,.28,.28]):
                th=theta.copy();th[j]=fm;tasks.append((th,f'worker_reset{reset}_{k}'))
            rows.extend(pool.map(call,tasks))
        (p.HERE/'state_repeatability.json').write_text(json.dumps(rows,indent=2))
    print('complete',flush=True)
if __name__=='__main__':main()
