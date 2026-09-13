"""D46 bit-identical replay check and conditional movement summaries."""
import hashlib
import json
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
output=[]
for variant,original in [('pilot','independence_controls'),('oracle','independence_oracle')]:
    folder=HERE/f'independence_trace_{variant}'/'spike_17752'
    baseline=HERE/original/'spike_17752'/'samples.npz'
    saved=np.load(baseline);replay=np.load(folder/'samples.npz')
    for name in ['u','logl','logwt']:assert np.array_equal(saved[name],replay[name]),(variant,name)
    trace=json.loads((folder/'proposal_trace.json').read_text())
    cut=np.array([r['cut'] for r in trace]);assert np.all(np.diff(cut)>=0)
    groups=[]
    for stage,indices in enumerate(np.array_split(np.arange(len(trace)),5),1):
        for core in [False,True]:
            rows=[trace[i] for i in indices if (abs(trace[i]['parent_active']-.2)<.003)==core]
            if not rows:continue
            stalled=np.array([r['accepted']==0 for r in rows])
            step=np.array([r['child_inactive']-r['parent_inactive'] for r in rows])
            groups.append(dict(stage=stage,parent_core=core,n=len(rows),cut_range=[float(cut[indices[0]]),float(cut[indices[-1]])],
                stalled_fraction=float(stalled.mean()),nuisance_rms_step=float(np.sqrt(np.mean(step**2))),
                region_exchanges=sum((abs(r['child_active']-.2)<.003)!=core for r in rows),
                mean_accepted=float(np.mean([r['accepted'] for r in rows])),
                mean_density_rejections=float(np.mean([r['density_rejected'] for r in rows]))))
    result=dict(variant=variant,bit_identical=True,kernels=len(trace),groups=groups,
        trace_sha256=hashlib.sha256((folder/'proposal_trace.json').read_bytes()).hexdigest(),
        baseline_sha256=hashlib.sha256(baseline.read_bytes()).hexdigest())
    output.append(result)
(HERE/'global_trace_audit.json').write_text(json.dumps(output,indent=2))
for result in output:
    print(json.dumps(result))
