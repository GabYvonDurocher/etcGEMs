"""Instrument original likelihood without changing its mathematical operations."""
import sys,json,time,hashlib
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[1]
for p in ['src','reports/P16_reduced','reports/P11_nested','reports/P6_convergence']:
    sys.path.insert(0,str(ROOT/p))
from reduced import FREE_NAMES,FULL_NAMES,expand,loglike15
from run_reduced import PAYLOAD
from etcgem import calibration_multi as cm, gasflux
BASE=ROOT/'strains/eciML1515/outputs/calibration_configD_NLDM_recipe_P16_reduced'
# Instrument apply_state used by the actual original flux_tpc, before every solve.
original_state=gasflux.apply_state; original_flux=gasflux.flux_tpc
capture={}
def state(ecm,T,pert):
    original_state(ecm,T,pert)
    gp=ecm.model.solver.problem;gp.update(); A=gp.getA().tocsr()
    h=hashlib.sha256()
    for v in [A.indptr,A.indices,A.data,np.asarray(gp.getAttr('LB')),np.asarray(gp.getAttr('UB')),np.asarray(gp.getAttr('RHS')),np.asarray(gp.getAttr('Obj'))]:h.update(v.tobytes())
    h.update(str(gp.getAttr('Sense')).encode())
    capture.setdefault('fingerprints',[]).append(h.hexdigest())
def flux(*args,**kwargs):
    frame=original_flux(*args,**kwargs)
    capture['flux']=frame.to_dict(orient='list'); return frame

def evaluate(theta,label):
    capture.clear(); t=time.monotonic(); ll=loglike15(theta)
    return dict(label=label,theta=theta.tolist(),logl=ll,wall_s=time.monotonic()-t,**capture)

def main():
    gasflux.apply_state=state;gasflux.flux_tpc=flux
    # Independent by-name check of the insertion, before any model evaluation.
    dummy=np.arange(15.)
    assert dict(zip(FULL_NAMES,expand(dummy)))==dict(dict(zip(FREE_NAMES,dummy)),dTm=0.)
    points={}
    for tag in ['red1','red2']:
        x=np.load(BASE/f'samples_{tag}.npy'); ll=np.load(BASE/f'logl_{tag}.npy')
        points[tag+'_best']=x[np.argmax(ll)]
        lw=np.load(BASE/f'logwt_{tag}.npy');w=np.exp(lw-lw.max());w/=w.sum()
        points[tag+'_median']=np.array([np.interp(.5,np.cumsum(w[np.argsort(x[:,j])]),np.sort(x[:,j])) for j in range(15)])
    records=[];j=FREE_NAMES.index('f_metab')
    cm._gwinit(dict(PAYLOAD,solver='gurobi'))
    for key,theta in points.items():
        for i,fm in enumerate([.15,.28,.45,.45,.28,.15]):
            th=theta.copy();th[j]=fm
            row=evaluate(th,key+'_reused_'+str(i));records.append(row)
            (HERE/'premise_results.json').write_text(json.dumps(records,indent=2))
            print(row['label'],row['logl'],round(row['wall_s'],2),row.get('flux',{}).get('status'),flush=True)
        cm._gwinit(dict(PAYLOAD,solver='gurobi'))
        th=theta.copy();th[j]=.28; records.append(evaluate(th,key+'_fresh'))
        (HERE/'premise_results.json').write_text(json.dumps(records,indent=2))
if __name__=='__main__':main()
