"""P17 numerical replay of prespecified archived points, preserving original likelihood."""
import premise as p
import json,numpy as np

def main():
    p.gasflux.flux_tpc=p.flux
    rows=[]; j=p.FREE_NAMES.index('f_metab')
    for seed in ['red1','red2']:
        samples=np.load(p.BASE/f'samples_{seed}.npy');lw=np.load(p.BASE/f'logwt_{seed}.npy');ll=np.load(p.BASE/f'logl_{seed}.npy')
        for name,ix in [('maxweight',int(np.argmax(lw))),('transition',8000)]:
            th=samples[ix].copy();p.cm._gwinit(dict(p.PAYLOAD,solver='gurobi'))
            for k,fm in enumerate([th[j]]*4+[.15,.45]):
                x=th.copy();x[j]=fm;row=p.evaluate(x,f'{seed}_{name}_{k}');row['stored_logl']=float(ll[ix]);row['stored_index']=ix;rows.append(row)
                (p.HERE/'weighted_replay.json').write_text(json.dumps(rows,indent=2));print(row['label'],row['logl'],row['stored_logl'],flush=True)
            p.cm._gwinit(dict(p.PAYLOAD,solver='gurobi'));row=p.evaluate(th,f'{seed}_{name}_fresh');row['stored_logl']=float(ll[ix]);row['stored_index']=ix;rows.append(row)
            (p.HERE/'weighted_replay.json').write_text(json.dumps(rows,indent=2))
if __name__=='__main__':main()
